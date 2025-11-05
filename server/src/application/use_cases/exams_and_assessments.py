"""
Exam and Assessment Use Cases
"""

from dataclasses import dataclass
from typing import Optional, List, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Answer, Document
from ...domain.value_objects import Filters, SessionContext


# ============================================================================
# EXAM USE CASES
# ============================================================================

@dataclass
class GenerateExamRequest:
    """Request to generate an exam."""
    chapters: str
    duration: str = "2h"
    total_points: int = 20
    level: str = "prépa"
    difficulty: str = "mixte"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class GenerateExamUseCase:
    """Generate complete exams with multiple exercises."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: GenerateExamRequest) -> Answer:
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=request.chapters, filters=filters_dict, k=12)
        
        if not docs:
            return Answer(text=f"Aucun document trouvé pour : {request.chapters}",
                        sources=[], metadata={"error": "no_documents"})
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("exam")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "chapters": request.chapters,
                "duration": request.duration,
                "total_points": request.total_points,
                "level": request.level,
                "difficulty": request.difficulty,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "exam", "chapters": request.chapters})
    
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
class CorrectExamRequest:
    """Request to correct an exam."""
    student_answer: str
    exam_statement: str
    points: int = 20
    level: str = "prépa"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class CorrectExamUseCase:
    """Correct complete exams with detailed grading."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: CorrectExamRequest) -> Answer:
        query = request.exam_statement[:300]
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=query, filters=filters_dict, k=8)
        
        context = self._format_context(docs) if docs else "Pas de contexte disponible."
        prompt_template = self.prompts.get("exam_corrector")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "student_answer": request.student_answer,
                "exam_statement": request.exam_statement,
                "points": request.points,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "exam_corrector", "points": request.points})
    
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
# QCM AND KHOLLE USE CASES
# ============================================================================

@dataclass
class GenerateQCMRequest:
    """Request to generate QCM (multiple choice questions)."""
    topic: str
    num_questions: int = 12
    level: str = "prépa"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class GenerateQCMUseCase:
    """Generate QCM with multiple choice questions."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: GenerateQCMRequest) -> Answer:
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=request.topic, filters=filters_dict, k=10)
        
        if not docs:
            return Answer(text=f"Aucun document trouvé pour : {request.topic}",
                        sources=[], metadata={"error": "no_documents"})
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("qcm")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "topic": request.topic,
                "num_questions": request.num_questions,
                "level": request.level,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "qcm", "topic": request.topic})
    
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
class GenerateKholleRequest:
    """Request to generate kholle (oral exam)."""
    topic: str
    duration: str = "20min"
    level: str = "prépa"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class GenerateKholleUseCase:
    """Generate kholle (oral exam) questions."""
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: GenerateKholleRequest) -> Answer:
        filters_dict = self._build_filters(request.filters)
        docs = self.retriever.retrieve(query=request.topic, filters=filters_dict, k=8)
        
        if not docs:
            return Answer(text=f"Aucun document trouvé pour : {request.topic}",
                        sources=[], metadata={"error": "no_documents"})
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("kholle")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "topic": request.topic,
                "duration": request.duration,
                "level": request.level,
                "context": context
            }
        )
        
        return Answer(text=result_text, sources=self._extract_sources(docs),
                     metadata={"task": "kholle", "topic": request.topic})
    
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
