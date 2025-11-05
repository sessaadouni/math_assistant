"""
Use Case: Build Course Content

Constructs comprehensive course content on a topic with structure and rigor.
"""

from dataclasses import dataclass
from typing import Optional, List, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Answer, Document
from ...domain.value_objects import Filters, SessionContext


@dataclass
class BuildCourseRequest:
    """Request to build course content."""
    topic: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class BuildCourseUseCase:
    """
    Use case for building complete course content.
    
    Generates structured course content with:
    - Clear structure (definitions, theorems, properties)
    - Rigorous mathematical treatment
    - Examples and applications
    - Exercises references
    """
    
    def __init__(
        self,
        retriever: IRetriever,
        llm_provider: ILLMProvider,
        router: IRouter,
        prompt_provider: Any,
    ):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: BuildCourseRequest) -> Answer:
        """Execute course building."""
        filters_dict = self._build_filters(request.filters)
        
        docs = self.retriever.retrieve(
            query=request.topic,
            filters=filters_dict,
            k=12  # More docs for comprehensive course
        )
        
        if not docs:
            return Answer(
                text=f"Aucun document trouvé pour : {request.topic}",
                sources=[],
                metadata={"error": "no_documents"}
            )
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("course_build")
        
        variables = {
            "topic": request.topic,
            "level": request.level,
            "context": context,
        }
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables=variables
        )
        
        return Answer(
            text=result_text,
            sources=self._extract_sources(docs),
            metadata={"task": "course_build", "topic": request.topic}
        )
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        """Build filters dictionary."""
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter,
            'block_kind': filters.block_kind,
            'block_id': filters.block_id,
            'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        """Format documents into context."""
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            page = meta.get("page", "?")
            chapter = meta.get("chapter", "?")
            chunks.append(f"[Doc {i} – p.{page}, ch.{chapter}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        """Extract sources from documents."""
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")} 
                for d in docs if d.metadata]
