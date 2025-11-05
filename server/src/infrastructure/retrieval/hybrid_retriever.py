# -*- coding: utf-8 -*-
"""
Hybrid Retriever for Math RAG Assistant (SOLID Architecture).

This module implements a hybrid retrieval strategy combining:
- BM25 (lexical search)
- Vector search (semantic search)  
- Cross-encoder reranking (optional)

Migrated from src/core/rag_engine.py to follow SOLID principles.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from collections import defaultdict
import os
import unicodedata

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

from src.application.interfaces.retriever import IRetriever
from src.domain.value_objects import Filters
from src.config.settings import Settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    """
    Normalize accents/case/whitespace for metadata comparison.
    
    Args:
        s: Value to normalize
        
    Returns:
        Normalized string (lowercase, no accents, collapsed whitespace)
    """
    s = "" if s is None else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.strip().lower().split())


def strip_accents(text: str) -> str:
    """Remove accents from text for BM25 normalization."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def _map_reranker_name(name: str) -> str:
    """
    Map Ollama-like aliases to HuggingFace model IDs.
    
    Args:
        name: Reranker model name (may include ':latest' suffix)
        
    Returns:
        HuggingFace model ID for SentenceTransformers
    """
    n = (name or "").strip()
    # Remove ':latest' suffix
    n = n.split(":")[0]
    
    # Common mappings
    if n.endswith("bge-reranker-v2-m3") or "bge-reranker-v2-m3" in n:
        return "BAAI/bge-reranker-v2-m3"
    if "jina-reranker" in n:
        return "jinaai/jina-reranker-v2-base-multilingual"
    if n.lower() in {"bge-small-en-v1.5", "bge-base-en-v1.5"}:
        return f"BAAI/{n}"
    
    # Default: return as-is (assume already HF ID)
    return n


# ---------------------------------------------------------------------------
# Hybrid Retriever
# ---------------------------------------------------------------------------

class HybridRetriever(IRetriever):
    """
    Hybrid retrieval combining BM25, vector search, and reranking.
    
    Implements IRetriever interface with:
    - retrieve(): Main retrieval with fusion and reranking
    - get_available_blocs(): List available block kinds
    - get_available_doc_types(): List available document types
    
    Responsibilities (Single Responsibility Principle):
    - Coordinate BM25 and vector retrievers
    - Apply metadata filters
    - Fuse results with reciprocal rank fusion
    - Apply cross-encoder reranking (optional)
    - Provide metadata discovery (blocs, doc types)
    
    Dependencies (Dependency Inversion):
    - Chroma: Vector store
    - BM25Retriever: Lexical search
    - CrossEncoder: Reranking (optional)
    - Settings: Configuration
    """
    
    def __init__(
        self,
        store: Optional[Chroma],
        all_docs: List[Document],
        settings: Settings,
    ) -> None:
        """
        Initialize HybridRetriever.
        
        Args:
            store: Chroma vector store (None for BM25-only mode)
            all_docs: All documents (for BM25 and metadata discovery)
            settings: Configuration settings
        """
        self._store = store
        self._all_docs = all_docs
        self._settings = settings
        self._config = settings.rag
        
        # Reranker (lazy init)
        self._cross_encoder: Optional[Any] = None
        self._reranker_initialized = False
        self._rr_maxlen = 256
        self._rr_batch = 16
        
        # BM25-only flag
        self._bm25_only = (store is None)
        
    def retrieve(
        self,
        query: str,
        filters: Optional[Filters] = None,
        k: int = 8,
    ) -> List[Document]:
        """
        Retrieve documents using hybrid strategy.
        
        Args:
            query: Search query
            filters: Metadata filters (optional)
            k: Number of documents to return
            
        Returns:
            List of retrieved documents (ranked by relevance)
            
        Strategy:
        1. Fast path: exact metadata match (if filters provided)
        2. BM25 retrieval (if enabled)
        3. Vector retrieval (if store available)
        4. Fusion: reciprocal rank fusion with weights
        5. Reranking: cross-encoder scoring (if enabled)
        6. Return k documents
        """
        filters = filters or Filters()
        k = max(k, 8)
        filters_dict = self._filters_to_dict(filters)
        
        # 1. Fast path: exact metadata match
        fast_docs = self._fast_path_retrieve(filters_dict, k)
        
        # 2. BM25 retrieval
        bm25_docs = self._bm25_retrieve(query, filters_dict, k)
        
        # 3. Vector retrieval
        vector_docs = self._vector_retrieve(query, filters_dict, k)
        
        # 4. Fusion: reciprocal rank fusion
        merged = self._fuse_results(
            fast=fast_docs,
            bm25=bm25_docs,
            vector=vector_docs,
            k=k,
        )
        
        # Select top candidates for reranking
        candidates = merged[: max(k * 2, 12)]
        
        # 5. Reranking (optional)
        if self._config.use_reranker and candidates:
            candidates = self._rerank(query, candidates)
        
        # 6. Return top_k
        return candidates[:k]
    
    def get_available_blocs(self) -> List[str]:
        """
        Get all available block kinds.
        
        Returns:
            Sorted list of unique block kinds
        """
        blocs = set()
        for doc in self._all_docs:
            block_kind = doc.metadata.get("block_kind")
            if block_kind:
                blocs.add(str(block_kind))
        return sorted(blocs)
    
    def get_available_doc_types(self) -> List[str]:
        """
        Get all available document types.
        
        Returns:
            Sorted list of unique document types
        """
        types = set()
        for doc in self._all_docs:
            doc_type = doc.metadata.get("type")
            if doc_type:
                types.add(str(doc_type))
        return sorted(types)
    
    # -------------------------
    # Private retrieval methods
    # -------------------------
    
    def _fast_path_retrieve(
        self,
        filters: Dict[str, Any],
        k: int,
    ) -> List[Document]:
        """
        Fast path: exact metadata match.
        
        Returns documents matching ALL filters exactly.
        Used for highly specific queries (chapter + block_id + block_kind).
        """
        if not filters:
            return []
        
        # Normalize filters
        wanted = {}
        for key in ("chapter", "block_kind", "block_id", "type", "doc_type"):
            value = filters.get(key)
            if value is not None:
                wanted[key] = _norm(value)
        
        if not wanted:
            return []
        
        # Match documents
        matches = []
        for doc in self._all_docs:
            if all(
                _norm(doc.metadata.get(k)) == v
                for k, v in wanted.items()
            ):
                matches.append(doc)
        
        return matches[: max(k, 10)]
    
    def _bm25_retrieve(
        self,
        query: str,
        filters: Dict[str, Any],
        k: int,
    ) -> List[Document]:
        """
        BM25 lexical retrieval.
        
        Returns documents using BM25 scoring (TF-IDF variant).
        Applied after metadata filtering.
        """
        # BM25 needed if: no vector store OR explicitly enabled
        bm25_needed = (
            self._store is None or
            bool(getattr(self._config, "use_bm25_with_vector", False))
        )
        
        if not bm25_needed or not self._all_docs:
            return []
        
        # Apply filters
        filtered_docs = self._apply_filters(self._all_docs, filters)
        
        if not filtered_docs:
            return []
        
        # Normalize documents (accent removal for better BM25 matching)
        normalized_docs = [
            Document(
                page_content=strip_accents(doc.page_content),
                metadata=doc.metadata,
            )
            for doc in filtered_docs
        ]
        
        # Create BM25 retriever
        try:
            bm25 = BM25Retriever.from_documents(normalized_docs, k=k * 2)
            return bm25.invoke(query)
        except Exception:
            return []
    
    def _vector_retrieve(
        self,
        query: str,
        filters: Dict[str, Any],
        k: int,
    ) -> List[Document]:
        """
        Vector semantic retrieval.
        
        Returns documents using embedding similarity.
        Applies soft filtering (chapter OR type OR block_kind) to avoid low recall.
        """
        if self._store is None:
            return []
        
        # Build soft filter (avoid over-filtering)
        vector_filter = None
        if filters:
            # Priority: chapter > type > block_kind
            # NOTE: block_id NOT included (too restrictive)
            if filters.get("chapter"):
                vector_filter = {"chapter": {"$eq": str(filters["chapter"])}}
            elif filters.get("type"):
                vector_filter = {"type": {"$eq": _norm(filters["type"])}}
            elif filters.get("block_kind"):
                vector_filter = {"block_kind": {"$eq": _norm(filters["block_kind"])}}
        
        # Create retriever
        try:
            kwargs = {"k": k * 2}
            if vector_filter:
                # Use 'filter', not 'where' (Chroma API)
                kwargs["filter"] = vector_filter
            
            retriever = self._store.as_retriever(search_kwargs=kwargs)
            return retriever.invoke(query)
        except Exception:
            return []
    
    def _fuse_results(
        self,
        *,
        fast: List[Document],
        bm25: List[Document],
        vector: List[Document],
        k: int,
    ) -> List[Document]:
        """
        Fuse results using reciprocal rank fusion.
        
        Formula: score(doc) = Σ weight_i / (k0 + rank_i + 1)
        
        Weights:
        - Fast path: 2.0 (exact match)
        - BM25: 1.0 (lexical)
        - Vector: 1.0 (semantic)
        
        Args:
            fast: Fast path documents
            bm25: BM25 documents
            vector: Vector documents
            k: Number of documents to return
            
        Returns:
            Fused and ranked documents
        """
        rank_scores = defaultdict(float)
        doc_index = {}
        
        def add_results(docs: List[Document], weight: float, k0: int = 60):
            for rank, doc in enumerate(docs):
                doc_id = id(doc)
                doc_index[doc_id] = doc
                rank_scores[doc_id] += weight * (1.0 / (k0 + rank + 1))
        
        # Apply weights
        add_results(fast, weight=2.0)
        add_results(bm25, weight=1.0)
        add_results(vector, weight=1.0)
        
        # Sort by score
        sorted_docs = sorted(
            doc_index.values(),
            key=lambda d: rank_scores[id(d)],
            reverse=True,
        )
        
        return sorted_docs
    
    def _rerank(
        self,
        query: str,
        candidates: List[Document],
    ) -> List[Document]:
        """
        Rerank candidates using cross-encoder.
        
        Args:
            query: Search query
            candidates: Candidate documents
            
        Returns:
            Reranked documents
        """
        if not candidates:
            return candidates
        
        # Lazy init reranker
        if not self._reranker_initialized:
            self._init_reranker()
            self._reranker_initialized = True
        
        if self._cross_encoder is None:
            return candidates
        
        try:
            # Clip text to max length (~4 chars/token)
            def clip_text(text: str, max_tokens: int) -> str:
                return text[: max_tokens * 4]
            
            # Create query-document pairs
            pairs = [
                (query, clip_text(doc.page_content, self._rr_maxlen))
                for doc in candidates
            ]
            
            # Score in batches
            scores = []
            for i in range(0, len(pairs), self._rr_batch):
                batch = pairs[i:i + self._rr_batch]
                batch_scores = self._cross_encoder.predict(
                    batch,
                    show_progress_bar=False,
                )
                scores.extend(batch_scores)
            
            # Sort by score
            ranked = sorted(
                zip(candidates, scores),
                key=lambda x: x[1],
                reverse=True,
            )
            
            return [doc for doc, _ in ranked]
        
        except Exception:
            # Fallback: return candidates as-is
            return candidates
    
    # -------------------------
    # Private helpers
    # -------------------------
    
    def _init_reranker(self) -> None:
        """Initialize cross-encoder reranker (lazy)."""
        try:
            from sentence_transformers import CrossEncoder
            
            hf_id = _map_reranker_name(self._config.reranker_model)
            
            # Device/batch/seq_len configurable via env
            device = os.getenv("RERANKER_DEVICE", None)  # "cpu" | "cuda" | "mps" | None
            self._cross_encoder = CrossEncoder(hf_id, device=device)
            
            self._rr_maxlen = int(os.getenv("RERANK_MAX_LEN", "256"))
            self._rr_batch = int(os.getenv("RERANK_BATCH", "16"))
        
        except Exception:
            self._cross_encoder = None
    
    @staticmethod
    def _apply_filters(
        docs: List[Document],
        filters: Dict[str, Any],
    ) -> List[Document]:
        """
        Apply metadata filters to documents.
        
        Args:
            docs: Documents to filter
            filters: Metadata filters
            
        Returns:
            Filtered documents
        """
        if not filters:
            return docs
        
        # Normalize filters
        wanted = {
            k: _norm(v)
            for k, v in filters.items()
            if v is not None
        }
        
        # Match documents
        matches = []
        for doc in docs:
            if all(
                _norm(doc.metadata.get(k)) == v
                for k, v in wanted.items()
            ):
                matches.append(doc)
        
        return matches
    
    @staticmethod
    def _filters_to_dict(filters: Filters) -> Dict[str, Any]:
        """Convert Filters to dict."""
        result = {}
        if filters.chapter:
            result["chapter"] = filters.chapter
        if filters.block_kind:
            result["block_kind"] = filters.block_kind
        if filters.block_id:
            result["block_id"] = filters.block_id
        if filters.type:
            result["type"] = filters.type
        if filters.doc_type:
            result["doc_type"] = filters.doc_type
        return result
