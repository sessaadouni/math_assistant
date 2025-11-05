"""
AnswerQuestionUseCase - Main use case for answering user questions

This use case orchestrates the entire flow:
1. Route decision (Router)
2. Query rewriting (if needed)
3. Document retrieval (Retriever)
4. Answer generation (LLM)
5. Session update (SessionStore)
"""

from typing import Optional, Dict, Any
import time
from datetime import datetime

from ...domain.entities import Question, Answer, Document, Context
from ...domain.value_objects import Filters, TaskType, SessionContext
from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ..interfaces.session_store import ISessionStore


class AnswerQuestionUseCase:
    """
    Use case for answering user questions.
    
    This is the main orchestration point that coordinates:
    - Intent detection and routing
    - Context retrieval
    - LLM generation
    - Session management
    
    Following Single Responsibility Principle:
    - This class ONLY orchestrates
    - Actual work is delegated to injected services
    """
    
    def __init__(
        self,
        retriever: IRetriever,
        llm_provider: ILLMProvider,
        router: IRouter,
        session_store: ISessionStore,
        prompt_provider: Any,  # Will be PromptRegistry after prompts refactoring
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            retriever: Document retrieval service
            llm_provider: LLM generation service
            router: Intent detection and routing service
            session_store: Session persistence service
            prompt_provider: Prompt template provider
        """
        self._retriever = retriever
        self._llm = llm_provider
        self._router = router
        self._session = session_store
        self._prompts = prompt_provider
    
    def execute(
        self,
        question_text: str,
        chat_id: str,
        filters: Optional[Filters] = None,
        auto_link: bool = True,
        debug: bool = False,
        force_router_mode: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> Answer:
        """
        Execute the use case: answer a user question.
        
        Args:
            question_text: The user's question
            chat_id: Unique chat/session identifier
            filters: Optional explicit filters (doc_type, bloc_name, etc.)
            auto_link: Whether to auto-link to previous context
            debug: Enable debug information
            
        Returns:
            Answer entity with text, sources, and metadata
        """
        start_time = time.time()
        
        def _notify(step: str, detail: str = ""):
            """Helper to notify progress if callback provided"""
            if progress_callback:
                progress_callback(step, detail)
        
        # 1. Create question entity
        question = Question.create(
            text=question_text,
            chat_id=chat_id,
        )
        
        # 2. Get session context
        session_context = self._session.get_context(chat_id)
        
        # 3. Routing decision
        _notify("Router", f"Mode: {force_router_mode or 'auto'}")
        decision = self._router.decide(
            question=question_text,
            session_context=session_context if auto_link else None,
            explicit_filters=filters,
        )
        
        # Enrich question with history if follow-up detected
        enriched_question = question_text
        if "référence au contexte précédent" in decision.reason:
            _notify("Router", "✅ Follow-up détecté → Recherche RAG forcée")
            # Add conversation history to help LLM understand the reference
            if session_context and session_context.history:
                # Get last exchange for context
                last_q, last_a = session_context.history[-1]
                # Create enriched question with context
                enriched_question = (
                    f"[Contexte: L'utilisateur a précédemment demandé \"{last_q}\"]\n\n"
                    f"Question actuelle: {question_text}"
                )
        
        # Override router decision if force_router_mode is set
        if force_router_mode:
            from dataclasses import replace
            if force_router_mode == "llm":
                # Force LLM-only mode (no RAG)
                decision = replace(decision, decision="llm_only")
                _notify("Router", "Mode LLM pur (pas de RAG)")
            elif force_router_mode == "rag":
                # Force RAG mode
                decision = replace(decision, decision="rag_first")
                _notify("Router", "Mode RAG prioritaire")
            elif force_router_mode == "hybrid":
                # Force hybrid mode
                decision = replace(decision, decision="rag_to_llm")
                _notify("Router", "Mode hybride (RAG + LLM)")
        
        # Apply session filters if auto_link
        effective_filters = filters or decision.filters
        if auto_link and not effective_filters.is_empty():
            effective_filters = session_context.last_filters.merge(effective_filters)
        
        # Update question with rewritten query
        if decision.rewritten_query:
            question.rewritten_text = decision.rewritten_query
        
        # 4. Retrieve context if needed
        context: Optional[Context] = None
        if decision.use_rag:
            _notify("RAG", "Recherche dans la base vectorielle...")
            docs = self._retriever.retrieve(
                query=decision.rewritten_query or question_text,
                filters=effective_filters,
                k=8,
            )
            
            if docs:
                _notify("RAG", f"✅ {len(docs)} documents trouvés")
                # Format context for prompt
                formatted_text = self._format_context_for_prompt(docs)
                context = Context(
                    documents=docs,
                    formatted_text=formatted_text,
                    num_sources=len(docs),
                )
            else:
                _notify("RAG", "⚠️  Aucun document trouvé")
        else:
            _notify("RAG", "Mode LLM pur - Pas de recherche RAG")
        
        # 5. Get appropriate prompt for task
        prompt_template = self._get_prompt_for_task(decision.task)
        
        # 6. Generate answer with LLM
        _notify("LLM", f"Génération de la réponse ({decision.task})...")
        answer_text = self._generate_answer(
            question=enriched_question,  # Use enriched question with history context
            context=context,
            prompt_template=prompt_template,
            task=decision.task,
        )
        _notify("LLM", "✅ Réponse générée")
        
        # 7. Create answer entity
        execution_time = time.time() - start_time
        answer = Answer.create(
            question_id=question.id,
            text=answer_text,
            chat_id=chat_id,
            context=context,
            task_type=decision.task.value,
            model_used=self._llm.get_model_name(),
            execution_time=execution_time,
        )
        
        # 8. Update session
        self._session.update_context(chat_id, question, answer)
        
        return answer
    
    def _format_context_for_prompt(self, docs: list[Document]) -> str:
        """
        Format retrieved documents for prompt injection.
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        parts = []
        for i, doc in enumerate(docs, 1):
            page = doc.metadata.get("page", "?")
            doc_type = doc.metadata.get("doc_type", "cours")
            bloc_name = doc.metadata.get("bloc_name", "")
            
            # Build header
            header_parts = [f"Document {i}"]
            if bloc_name:
                header_parts.append(f"[{bloc_name}]")
            header_parts.append(f"(page {page})")
            
            header = " ".join(header_parts)
            
            # Add content (LangChain Document uses 'page_content')
            content = doc.page_content.strip()
            parts.append(f"{header}\n{content}")
        
        return "\n\n---\n\n".join(parts)
    
    def _get_prompt_for_task(self, task: TaskType) -> Any:
        """
        Get appropriate prompt template for task.
        
        Args:
            task: Task type enum
            
        Returns:
            Prompt template (BasePrompt instance)
        """
        # Use PromptRegistry
        return self._prompts.get(task.value)
    
    def _generate_answer(
        self,
        question: str,
        context: Optional[Context],
        prompt_template: Any,
        task: TaskType,
    ) -> str:
        """
        Generate answer using LLM.
        
        Args:
            question: User's question
            context: Retrieved context (if any)
            prompt_template: Prompt template to use (BasePrompt instance)
            task: Task type
            
        Returns:
            Generated answer text
        """
        # Prepare variables for prompt
        variables = {"question": question}
        
        if context:
            variables["context"] = context.formatted_text
        else:
            # For non-RAG tasks, provide empty context or placeholder
            variables["context"] = "(Aucun contexte spécifique fourni)"
        
        # Add default values for other common variables
        # Some prompts may need these
        variables.setdefault("notion", question)
        variables.setdefault("topic", question)
        variables.setdefault("level", "Licence 3 / Master 1")
        
        # Format prompt using BasePrompt's format method
        try:
            formatted_prompt = prompt_template.format(**variables)
        except Exception as e:
            # Fallback: use only required variables
            required_vars = prompt_template.get_required_variables()
            filtered_vars = {k: v for k, v in variables.items() if k in required_vars}
            formatted_prompt = prompt_template.format(**filtered_vars)
        
        # Generate with LLM
        answer = self._llm.generate(
            prompt=formatted_prompt,
            temperature=0.1,
        )
        
        return answer.strip()
    
    def execute_stream(
        self,
        question_text: str,
        chat_id: str,
        filters: Optional[Filters] = None,
        auto_link: bool = True,
    ):
        """
        Execute use case with streaming response.
        
        TODO: Implement streaming support
        
        Args:
            question_text: The user's question
            chat_id: Unique chat/session identifier
            filters: Optional explicit filters
            auto_link: Whether to auto-link to previous context
            
        Yields:
            Answer chunks
        """
        raise NotImplementedError("Streaming not yet implemented")
