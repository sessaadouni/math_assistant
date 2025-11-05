"""
Utility Use Cases - Formulas and Proofs
"""

from dataclasses import dataclass
from typing import Optional, List, Any

from ..interfaces.retriever import IRetriever
from ..interfaces.llm_provider import ILLMProvider
from ..interfaces.router import IRouter
from ...domain.entities import Answer, Document
from ...domain.value_objects import Filters, SessionContext


# ============================================================================
# FORMULA USE CASE
# ============================================================================

@dataclass
class ExplainFormulaRequest:
    """Request to explain a mathematical formula."""
    query: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class ExplainFormulaUseCase:
    """
    Explain mathematical formulas with conditions and applications.
    
    Provides:
    - Formula statement in LaTeX $$…$$
    - When and why to use it
    - Necessary conditions
    - Intuitive meaning
    - Practical example
    - Common errors
    """
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: ExplainFormulaRequest) -> Answer:
        # Boost retrieval for formulas
        query = f"{request.query} formula formule"
        filters_dict = self._build_filters(request.filters)
        
        docs = self.retriever.retrieve(query=query, filters=filters_dict, k=8)
        
        if not docs:
            return Answer(
                text=f"Aucun document trouvé pour la formule : {request.query}",
                sources=[],
                metadata={"error": "no_documents"}
            )
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("formula")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "query": request.query,
                "level": request.level,
                "context": context
            }
        )
        
        return Answer(
            text=result_text,
            sources=self._extract_sources(docs),
            metadata={"task": "formula", "query": request.query}
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


# ============================================================================
# PROOF USE CASE
# ============================================================================

@dataclass
class ProveStatementRequest:
    """Request to prove a mathematical statement."""
    statement: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class ProveStatementUseCase:
    """
    Provide rigorous mathematical proofs.
    
    Structure:
    - Recall of statement (hypotheses, conclusion)
    - Proof strategy (1-2 lines: method used)
    - Detailed, rigorous, progressive demonstration
    - Key steps highlighted
    - Verification / limit cases
    - References [p.X]
    """
    
    def __init__(self, retriever: IRetriever, llm_provider: ILLMProvider,
                 router: IRouter, prompt_provider: Any):
        self.retriever = retriever
        self.llm = llm_provider
        self.router = router
        self.prompts = prompt_provider
    
    def execute(self, request: ProveStatementRequest) -> Answer:
        # Boost retrieval for proofs
        query = f"{request.statement} proof démonstration preuve"
        filters_dict = self._build_filters(request.filters)
        
        # Prioritize theorem/proposition blocks if no filter specified
        if not request.filters or not request.filters.block_kind:
            filters_dict['block_kind'] = 'theorem'
        
        docs = self.retriever.retrieve(query=query, filters=filters_dict, k=8)
        
        # Fallback without block_kind filter
        if not docs:
            docs = self.retriever.retrieve(
                query=query,
                filters={k: v for k, v in filters_dict.items() if k != 'block_kind'},
                k=8
            )
        
        if not docs:
            return Answer(
                text=f"Aucun document trouvé pour : {request.statement}",
                sources=[],
                metadata={"error": "no_documents"}
            )
        
        context = self._format_context(docs)
        prompt_template = self.prompts.get("proof")
        
        result_text = self.llm.generate(
            prompt_template=prompt_template,
            variables={
                "statement": request.statement,
                "level": request.level,
                "context": context
            }
        )
        
        return Answer(
            text=result_text,
            sources=self._extract_sources(docs),
            metadata={"task": "proof", "statement": request.statement[:100]}
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
            block_kind = meta.get("block_kind", "")
            
            header = f"[Doc {i} – p.{page}, ch.{chapter}"
            if block_kind:
                header += f", {block_kind}"
            header += "]"
            
            chunks.append(f"{header}\n{content}")
        return "\n\n".join(chunks)
    
    def _extract_sources(self, docs: List[Document]) -> List[Any]:
        return [{"page": d.metadata.get("page"), "chapter": d.metadata.get("chapter"),
                 "block_kind": d.metadata.get("block_kind")}
                for d in docs if d.metadata]
