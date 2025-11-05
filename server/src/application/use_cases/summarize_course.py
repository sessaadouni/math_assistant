"""
Use Case: Summarize Course

Creates concise course summaries with key points, formulas, and glossary.
"""

from dataclasses import dataclass
from typing import Optional, List, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Answer, Document
from ...domain.value_objects import Filters, SessionContext


@dataclass
class SummarizeCourseRequest:
    """Request to summarize course topic."""
    topic: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class SummarizeCourseUseCase:
    """
    Use case for summarizing course topics.
    
    Generates structured summaries with:
    - Key ideas (bullet points)
    - Essential definitions and notations
    - Theorems/properties with [p.X]
    - Essential formulas in $$…$$
    - Common errors/pitfalls
    - Mini-glossary (terms → 1 line)
    - 2-3 quick exercises
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
    
    def execute(self, request: SummarizeCourseRequest) -> Answer:
        """Execute course summarization."""
        filters_dict = self._build_filters(request.filters)
        
        docs = self.retriever.retrieve(
            query=request.topic,
            filters=filters_dict,
            k=10
        )
        
        if not docs:
            return Answer(
                text=f"Aucun document trouvé pour : {request.topic}",
                sources=[],
                metadata={"error": "no_documents"}
            )
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("course_summary")
        
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
            metadata={"task": "course_summary", "topic": request.topic}
        )
    
    def _build_filters(self, filters: Optional[Filters]) -> dict:
        if not filters:
            return {}
        return {k: v for k, v in {
            'chapter': filters.chapter,
            'block_kind': filters.block_kind,
            'block_id': filters.block_id,
            'type': filters.type,
        }.items() if v is not None}
    
    def _format_context(self, docs: List[Document]) -> str:
        chunks = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content or doc.content or ""
            meta = doc.metadata or {}
            page = meta.get("page", "?")
            chapter = meta.get("chapter", "?")
            chunks.append(f"[Doc {i} – p.{page}, ch.{chapter}]\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter")} 
                for d in docs if d.metadata]
