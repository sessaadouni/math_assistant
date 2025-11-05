"""
Dependency Injection Container

This module provides a centralized container for creating and managing
application dependencies following the Dependency Inversion Principle.
"""

from typing import Dict, Any, Optional

from .settings import Settings, rag_config, ui_config
from ..application.interfaces.retriever import IRetriever
from ..application.interfaces.llm_provider import ILLMProvider
from ..application.interfaces.router import IRouter
from ..application.interfaces.session_store import ISessionStore
from ..application.interfaces.query_rewriter import IQueryRewriter

# Infrastructure implementations
from ..infrastructure.llm.ollama_provider import OllamaLLMProvider
from ..infrastructure.llm.fallback_provider import FallbackLLMProvider
from ..infrastructure.session.memory_store import InMemorySessionStore
from ..infrastructure.query.ollama_query_rewriter import OllamaQueryRewriter


class DIContainer:
    """
    Dependency Injection Container.
    
    This container manages the lifecycle of all application dependencies
    and provides factory methods to create them with proper configuration.
    
    Usage:
        container = DIContainer()
        llm = container.get_llm_provider()
        retriever = container.get_retriever()
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize DI Container.
        
        Args:
            settings: Optional settings (uses global config if not provided)
        """
        self._settings = settings or Settings(rag_config, ui_config)
        self._singletons: Dict[str, Any] = {}
    
    # ========================================================================
    # LLM Provider
    # ========================================================================
    
    def get_llm_provider(self) -> ILLMProvider:
        """
        Get LLM provider with fallback.
        
        Returns configured LLM provider with:
        - Primary: Cloud model (deepseek-v3) if available
        - Fallback: Local model (qwen2.5:7b-math)
        """
        if "llm_provider" not in self._singletons:
            # Primary LLM
            primary = OllamaLLMProvider(
                base_url=self._settings.ollama_host,
                model=self._settings.llm_model,
                api_key=self._settings.ollama_api_key,
                timeout=300,
            )
            
            # Fallback LLM (if different from primary)
            fallback_model = self._settings.llm_fallback_model
            if fallback_model and fallback_model != self._settings.llm_model:
                fallback = OllamaLLMProvider(
                    base_url=self._settings.rag.ollama_host_local,
                    model=fallback_model,
                    timeout=300,
                )
                self._singletons["llm_provider"] = FallbackLLMProvider(
                    primary=primary,
                    fallback=fallback,
                )
            else:
                self._singletons["llm_provider"] = primary
        
        return self._singletons["llm_provider"]
    
    def get_rewriter_llm(self) -> Optional[ILLMProvider]:
        """
        Get query rewriter LLM.
        
        Returns smaller/faster model for query rewriting or None if disabled.
        """
        if not self._settings.rag.use_rewriter:
            return None
        
        if "rewriter_llm" not in self._singletons:
            rewrite_model = self._settings.rag.rewrite_model
            if rewrite_model:
                self._singletons["rewriter_llm"] = OllamaLLMProvider(
                    base_url=self._settings.ollama_host,
                    model=rewrite_model,
                    timeout=60,
                )
            else:
                self._singletons["rewriter_llm"] = None
        
        return self._singletons["rewriter_llm"]
    
    # ========================================================================
    # Query Rewriter
    # ========================================================================
    
    def get_query_rewriter(self) -> IQueryRewriter:
        """
        Get query rewriter service.
        
        Returns configured query rewriter using Ollama LLM.
        Handles contextual query reformulation for better retrieval.
        """
        if "query_rewriter" not in self._singletons:
            # Note: OllamaQueryRewriter prend une instance ChatOllama (pas ILLMProvider)
            # On crée directement l'instance ici
            from langchain_ollama import ChatOllama
            
            rewrite_model = getattr(self._settings.rag, 'rewrite_model', 'llama3.2:latest')
            base_url = getattr(self._settings.rag, 'ollama_host', 'http://localhost:11434')
            
            llm = ChatOllama(
                model=rewrite_model,
                base_url=base_url,
                temperature=0.3,
                num_predict=150,
            )
            
            self._singletons["query_rewriter"] = OllamaQueryRewriter(
                settings=self._settings,
                llm=llm,
            )
        
        return self._singletons["query_rewriter"]
    
    # ========================================================================
    # Retriever
    # ========================================================================
    
    def get_retriever(self) -> IRetriever:
        """
        Get document retriever.
        
        Returns configured hybrid retriever (BM25 + Vector + Reranker).
        """
        if "retriever" not in self._singletons:
            from ..infrastructure.retrieval import HybridRetriever
            from ..core.rag_engine import get_engine
            
            # Get RAG engine (handles store/embeddings/docs)
            engine = get_engine()
            
            # Ensure store is loaded
            store = engine.store
            all_docs = engine._get_all_docs()
            
            self._singletons["retriever"] = HybridRetriever(
                store=store,
                all_docs=all_docs,
                settings=self._settings,
            )
        
        return self._singletons["retriever"]
    
    # ========================================================================
    # Router
    # ========================================================================
    
    def get_router(self) -> IRouter:
        """
        Get intent router.
        
        Returns configured router for intent detection and routing decisions.
        """
        if "router" not in self._singletons:
            from ..infrastructure.routing import IntentRouter, IntentDetector
            
            self._singletons["router"] = IntentRouter(
                retriever=self.get_retriever(),
                settings=self._settings,
                intent_detector=IntentDetector(),
            )
        
        return self._singletons["router"]
    
    # ========================================================================
    # Session Store
    # ========================================================================
    
    def get_session_store(self) -> ISessionStore:
        """
        Get session store.
        
        Returns in-memory session store (can be swapped for Redis/SQLite).
        """
        if "session_store" not in self._singletons:
            self._singletons["session_store"] = InMemorySessionStore()
        
        return self._singletons["session_store"]
    
    # ========================================================================
    # Prompts
    # ========================================================================
    
    def get_prompt_registry(self):
        """
        Get prompt registry.
        
        Returns singleton PromptRegistry with all prompts registered.
        """
        if "prompt_registry" not in self._singletons:
            from ..prompts import get_default_registry
            self._singletons["prompt_registry"] = get_default_registry()
        
        return self._singletons["prompt_registry"]
    
    # ========================================================================
    # Use Cases
    # ========================================================================
    
    def get_answer_question_use_case(self):
        """
        Get AnswerQuestion use case.
        
        Returns configured use case with all dependencies injected.
        """
        if "answer_question_use_case" not in self._singletons:
            from ..application.use_cases import AnswerQuestionUseCase
            
            self._singletons["answer_question_use_case"] = AnswerQuestionUseCase(
                retriever=self.get_retriever(),
                llm_provider=self.get_llm_provider(),
                router=self.get_router(),
                session_store=self.get_session_store(),
                prompt_provider=self.get_prompt_registry(),
            )
        
        return self._singletons["answer_question_use_case"]
    
    def get_explain_course_use_case(self):
        """
        Get ExplainCourse use case.
        
        Returns configured use case for explaining course topics.
        """
        if "explain_course_use_case" not in self._singletons:
            from ..application.use_cases import ExplainCourseUseCase
            
            self._singletons["explain_course_use_case"] = ExplainCourseUseCase(
                retriever=self.get_retriever(),
                llm_provider=self.get_llm_provider(),
                router=self.get_router(),
                prompt_provider=self.get_prompt_registry(),
            )
        
        return self._singletons["explain_course_use_case"]
    
    def get_generate_exercise_use_case(self):
        """
        Get GenerateExercise use case.
        
        Returns configured use case for generating exercises.
        """
        if "generate_exercise_use_case" not in self._singletons:
            from ..application.use_cases import GenerateExerciseUseCase
            
            self._singletons["generate_exercise_use_case"] = GenerateExerciseUseCase(
                retriever=self.get_retriever(),
                llm_provider=self.get_llm_provider(),
                router=self.get_router(),
                prompt_provider=self.get_prompt_registry(),
            )
        
        return self._singletons["generate_exercise_use_case"]
    
    def get_explain_theorem_use_case(self):
        """Get ExplainTheorem use case."""
        if "explain_theorem_use_case" not in self._singletons:
            from ..application.use_cases import ExplainTheoremUseCase
            
            self._singletons["explain_theorem_use_case"] = ExplainTheoremUseCase(
                retriever=self.get_retriever(),
                llm_provider=self.get_llm_provider(),
                router=self.get_router(),
                prompt_provider=self.get_prompt_registry(),
            )
        
        return self._singletons["explain_theorem_use_case"]
    
    def get_build_course_use_case(self):
        """Get BuildCourse use case."""
        if "build_course_use_case" not in self._singletons:
            from ..application.use_cases import BuildCourseUseCase
            self._singletons["build_course_use_case"] = BuildCourseUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["build_course_use_case"]
    
    def get_summarize_course_use_case(self):
        """Get SummarizeCourse use case."""
        if "summarize_course_use_case" not in self._singletons:
            from ..application.use_cases import SummarizeCourseUseCase
            self._singletons["summarize_course_use_case"] = SummarizeCourseUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["summarize_course_use_case"]
    
    def get_create_sheet_use_case(self):
        """Get CreateSheet use case."""
        if "create_sheet_use_case" not in self._singletons:
            from ..application.use_cases import CreateSheetUseCase
            self._singletons["create_sheet_use_case"] = CreateSheetUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["create_sheet_use_case"]
    
    def get_review_sheet_use_case(self):
        """Get ReviewSheet use case."""
        if "review_sheet_use_case" not in self._singletons:
            from ..application.use_cases import ReviewSheetUseCase
            self._singletons["review_sheet_use_case"] = ReviewSheetUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["review_sheet_use_case"]
    
    def get_solve_exercise_use_case(self):
        """Get SolveExercise use case."""
        if "solve_exercise_use_case" not in self._singletons:
            from ..application.use_cases import SolveExerciseUseCase
            self._singletons["solve_exercise_use_case"] = SolveExerciseUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["solve_exercise_use_case"]
    
    def get_correct_exercise_use_case(self):
        """Get CorrectExercise use case."""
        if "correct_exercise_use_case" not in self._singletons:
            from ..application.use_cases import CorrectExerciseUseCase
            self._singletons["correct_exercise_use_case"] = CorrectExerciseUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["correct_exercise_use_case"]
    
    def get_generate_exam_use_case(self):
        """Get GenerateExam use case."""
        if "generate_exam_use_case" not in self._singletons:
            from ..application.use_cases import GenerateExamUseCase
            self._singletons["generate_exam_use_case"] = GenerateExamUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["generate_exam_use_case"]
    
    def get_correct_exam_use_case(self):
        """Get CorrectExam use case."""
        if "correct_exam_use_case" not in self._singletons:
            from ..application.use_cases import CorrectExamUseCase
            self._singletons["correct_exam_use_case"] = CorrectExamUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["correct_exam_use_case"]
    
    def get_generate_qcm_use_case(self):
        """Get GenerateQCM use case."""
        if "generate_qcm_use_case" not in self._singletons:
            from ..application.use_cases import GenerateQCMUseCase
            self._singletons["generate_qcm_use_case"] = GenerateQCMUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["generate_qcm_use_case"]
    
    def get_generate_kholle_use_case(self):
        """Get GenerateKholle use case."""
        if "generate_kholle_use_case" not in self._singletons:
            from ..application.use_cases import GenerateKholleUseCase
            self._singletons["generate_kholle_use_case"] = GenerateKholleUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["generate_kholle_use_case"]
    
    def get_explain_formula_use_case(self):
        """Get ExplainFormula use case."""
        if "explain_formula_use_case" not in self._singletons:
            from ..application.use_cases import ExplainFormulaUseCase
            self._singletons["explain_formula_use_case"] = ExplainFormulaUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["explain_formula_use_case"]
    
    def get_prove_statement_use_case(self):
        """Get ProveStatement use case."""
        if "prove_statement_use_case" not in self._singletons:
            from ..application.use_cases import ProveStatementUseCase
            self._singletons["prove_statement_use_case"] = ProveStatementUseCase(
                self.get_retriever(), self.get_llm_provider(),
                self.get_router(), self.get_prompt_registry())
        return self._singletons["prove_statement_use_case"]
    
    # ========================================================================
    # Utilities
    # ========================================================================
    
    def clear_singletons(self):
        """Clear all singletons (useful for testing)"""
        self._singletons.clear()
    
    def register_singleton(self, key: str, instance: Any):
        """
        Manually register a singleton.
        
        Useful for testing with mocks.
        """
        self._singletons[key] = instance


# Global container instance (for backward compatibility)
_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """
    Get global DI container instance.
    
    Creates one if it doesn't exist.
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def reset_container():
    """
    Reset global container.
    
    Useful for testing.
    """
    global _global_container
    if _global_container:
        _global_container.clear_singletons()
    _global_container = None
