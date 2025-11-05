"""
Use Case: Explain Course Topic

Provides pedagogical explanation of course topics with examples and FAQ.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Question, Answer, Document
from ...domain.value_objects import Filters, SessionContext


@dataclass
class ExplainCourseRequest:
    """
    Request to explain a course topic.
    
    Attributes
    ----------
    topic : str
        The course topic to explain (e.g., "convergence uniforme")
    level : str
        Education level (default: "prépa/terminale+")
    filters : Optional[Filters]
        Metadata filters (chapter, block_kind, etc.)
    session_context : Optional[SessionContext]
        Session state for context
    """
    topic: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class ExplainCourseUseCase:
    """
    Use case for explaining course topics.
    
    Flow:
    -----
    1. Retrieve relevant course documents based on topic
    2. Get CourseExplainPrompt from registry
    3. Generate pedagogical explanation with:
       - Vulgarisation → rigorous explanation
       - Concrete examples and analogies
       - Text-based visualizations (axes, tables)
       - Mini FAQ (3-5 common questions)
       - Page references [p.X]
    
    Example:
    --------
    >>> use_case = ExplainCourseUseCase(retriever, llm, router, prompt_provider)
    >>> request = ExplainCourseRequest(
    ...     topic="convergence uniforme",
    ...     level="prépa",
    ...     filters=Filters(chapter="5")
    ... )
    >>> response = use_case.execute(request)
    >>> print(response.answer.text)
    """
    
    def __init__(
        self,
        retriever: IRetriever,
        llm_provider: ILLMProvider,
        router: IRouter,
        prompt_provider: Any,  # PromptRegistry
    ):
        """
        Initialize use case with dependencies.
        
        Parameters
        ----------
        retriever : IRetriever
            Document retrieval service
        llm_provider : ILLMProvider
            LLM service for generation
        router : IRouter
            Router for intent detection (unused in this use case, kept for consistency)
        prompt_provider : PromptRegistry
            Registry for accessing prompts
        """
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: ExplainCourseRequest) -> Answer:
        """
        Execute the course explanation use case.
        
        Parameters
        ----------
        request : ExplainCourseRequest
            Request containing topic, level, and filters
            
        Returns
        -------
        Answer
            Answer entity with explanation text and source documents
            
        Raises
        ------
        ValueError
            If no documents found for the topic
        """
        # Step 1: Retrieve relevant documents
        filters_dict = {}
        if request.filters:
            if request.filters.chapter:
                filters_dict['chapter'] = request.filters.chapter
            if request.filters.block_kind:
                filters_dict['block_kind'] = request.filters.block_kind
            if request.filters.block_id:
                filters_dict['block_id'] = request.filters.block_id
            if request.filters.type:
                filters_dict['type'] = request.filters.type
        
        docs = self.retriever.retrieve(
            query=request.topic,
            filters=filters_dict,
            k=8
        )
        
        if not docs:
            return Answer(
                text=f"Aucun document trouvé pour le sujet : {request.topic}. "
                     f"Veuillez préciser le chapitre ou reformuler.",
                sources=[],
                metadata={"error": "no_documents"}
            )
        
        # Step 2: Format context from documents
        context = self._format_context(docs)
        
        # Step 3: Get prompt from registry
        prompt_template = self.prompts.get_prompt("course_explain")
        
        # Step 4: Prepare variables
        variables = {
            "topic": request.topic,
            "level": request.level,
            "context": context,
        }
        
        # Step 5: Generate explanation
        explanation_text = self.llm.generate(
            prompt_template=prompt_template,
            variables=variables
        )
        
        # Step 6: Create Answer entity
        answer = Answer(
            text=explanation_text,
            sources=self._extract_sources(docs),
            metadata={
                "task": "course_explain",
                "topic": request.topic,
                "level": request.level,
                "docs_count": len(docs),
            }
        )
        
        return answer
    
    def _format_context(self, docs: List[Document]) -> str:
        """
        Format documents into context string.
        
        Parameters
        ----------
        docs : List[Document]
            Retrieved documents
            
        Returns
        -------
        str
            Formatted context with page references
        """
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            
            page = meta.get("page", "?")
            chapter = meta.get("chapter", "?")
            block_kind = meta.get("block_kind", "")
            
            header = f"[Doc {i} – p.{page}, ch.{chapter}"
            if block_kind:
                header += f", {block_kind}"
            header += "]"
            
            chunks.append(f"{header}\n{content}")
        
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        """
        Extract source information from documents.
        
        Parameters
        ----------
        docs : List[Document]
            Retrieved documents
            
        Returns
        -------
        List[Source]
            List of source entities (simplified for now)
        """
        # For now, return metadata dicts
        # TODO: Create proper Source entities in domain layer
        sources = []
        for doc in docs:
            meta = doc.metadata or {}
            sources.append({
                "page": meta.get("page"),
                "chapter": meta.get("chapter"),
                "block_kind": meta.get("block_kind"),
                "block_id": meta.get("block_id"),
            })
        return sources
