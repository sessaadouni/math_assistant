"""
Additional Use Cases for Math Assistant
"""

from dataclasses import dataclass
from typing import Optional, List, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Answer, Document
from ...domain.value_objects import Filters, SessionContext


# ============================================================================
# SHEETS USE CASES
# ============================================================================

@dataclass
class CreateSheetRequest:
    """Request to create revision sheet."""
    topic: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class CreateSheetUseCase:
    """Create clear and useful revision sheets."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider, 
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: CreateSheetRequest) -> Answer:
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=request.topic, filters=filters_dict, k=8)
        
        if not docs:
            return Answer(text=f"Aucun document trouvé pour : {request.topic}",
                        sources=[], metadata={"error": "no_documents"})
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("sheet_create")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={"topic": request.topic, "level": request.level, "context": context}
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "sheet_create", "topic": request.topic})
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter, 'block_kind': filters.block_kind,
            'block_id': filters.block_id, 'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            chunks.append(f"[Doc {i} – p.{meta.get('page', '?')}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")} 
                for d in docs if d.metadata]


@dataclass
class ReviewSheetRequest:
    """Request to review student revision sheet."""
    sheet_text: str
    topic: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class ReviewSheetUseCase:
    """Review and provide feedback on student revision sheets."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: ReviewSheetRequest) -> Answer:
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=request.topic, filters=filters_dict, k=6)
        
        context = self._format_context(docs) if docs else "Pas de contexte de cours disponible."
        prompt_template = self.prompts.get("sheet_review")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "sheet_text": request.sheet_text,
                "topic": request.topic,
                "level": request.level,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "sheet_review", "topic": request.topic})
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter, 'block_kind': filters.block_kind,
            'block_id': filters.block_id, 'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            chunks.append(f"[Doc {i} – p.{meta.get('page', '?')}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")}
                for d in docs if d.metadata]


# ============================================================================
# EXERCISE USE CASES
# ============================================================================

@dataclass
class SolveExerciseRequest:
    """Request to solve an exercise step by step."""
    statement: str
    topic: Optional[str] = None
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class SolveExerciseUseCase:
    """Solve exercises step by step with detailed explanations."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: SolveExerciseRequest) -> Answer:
        query = request.topic if request.topic else request.statement[:200]
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=query, filters=filters_dict, k=8)
        
        context = self._format_context(docs) if docs else "Pas de contexte disponible."
        prompt_template = self.prompts.get("solver")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "statement": request.statement,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "solver", "statement": request.statement[:100]})
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter, 'block_kind': filters.block_kind,
            'block_id': filters.block_id, 'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            chunks.append(f"[Doc {i} – p.{meta.get('page', '?')}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")}
                for d in docs if d.metadata]


@dataclass
class CorrectExerciseRequest:
    """Request to correct student exercise answer."""
    statement: str
    student_answer: str
    points: int = 10
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class CorrectExerciseUseCase:
    """Correct student exercise answers with detailed feedback."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: CorrectExerciseRequest) -> Answer:
        query = request.statement[:200]
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=query, filters=filters_dict, k=6)
        
        context = self._format_context(docs) if docs else "Pas de contexte disponible."
        prompt_template = self.prompts.get("exo_corrector")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "statement": request.statement,
                "student_answer": request.student_answer,
                "points": request.points,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "exo_corrector", "points": request.points})
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter, 'block_kind': filters.block_kind,
            'block_id': filters.block_id, 'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            chunks.append(f"[Doc {i} – p.{meta.get('page', '?')}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")}
                for d in docs if d.metadata]
