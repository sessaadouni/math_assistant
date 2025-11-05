# -*- coding: utf-8 -*-
"""
Intent Router for Math RAG Assistant (SOLID Architecture).

This module implements routing logic to decide RAG vs LLM strategies.
Migrated from src/assistant/router.py to follow SOLID principles.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List
import time
import uuid
import re

from langchain_core.documents import Document
from rapidfuzz import fuzz

from src.application.interfaces.router import IRouter
from src.application.interfaces.retriever import IRetriever
from src.domain.value_objects import RouterDecision, Filters
from src.config.settings import Settings
from src.utils import normalize_whitespace, normalize_query_for_retrieval

from .intent_detector import IntentDetector


class IntentRouter(IRouter):
    """
    Routing engine that decides between RAG and LLM strategies.
    
    Implements IRouter interface with:
    - decide(): Main routing decision (rag_first, llm_first, llm_only, rag_to_llm)
    - calculate_rag_signal(): Quick RAG signal calculation
    
    Responsibilities (Single Responsibility Principle):
    - Coordinate intent detection (via IntentDetector)
    - Calculate RAG confidence signal
    - Apply routing thresholds and penalties
    - Build decision passport with metadata
    
    Dependencies (Dependency Inversion):
    - IRetriever: For quick document retrieval
    - IntentDetector: For intent classification
    - Settings: For thresholds and weights
    """
    
    def __init__(
        self, 
        retriever: IRetriever, 
        settings: Settings,
        intent_detector: Optional[IntentDetector] = None
    ) -> None:
        """
        Initialize IntentRouter.
        
        Args:
            retriever: Document retriever for RAG signal calculation
            settings: Configuration settings (thresholds, weights, penalties)
            intent_detector: Intent detector (created if not provided)
        """
        self._retriever = retriever
        self._settings = settings
        self._intent_detector = intent_detector or IntentDetector()
        
        # Cache config values for performance
        self._config = settings.rag
    
    # -------------------------
    # Public API (IRouter-compatible)
    # -------------------------
    
    def decide(
        self,
        question: str,
        session_context: Optional[Any] = None,
        explicit_filters: Optional[Filters] = None,
    ) -> RouterDecision:
        """
        IRouter-compatible decide method (wrapper).
        
        This is the main interface method called by use cases.
        It wraps the internal _decide_internal() method.
        
        Args:
            question: User's question text
            session_context: Optional session context with conversation history
            explicit_filters: Optional explicit filters
            
        Returns:
            RouterDecision
        """
        chat_id = session_context.chat_id if session_context else "unknown"
        filters = explicit_filters or Filters()
        
        # Get last decision for continuity
        last_decision = None
        if session_context and hasattr(session_context, 'last_decision'):
            last_decision = session_context.last_decision
        
        # Build enriched query with conversation context if available
        enriched_query = question
        force_rag_for_followup = False
        
        if session_context and hasattr(session_context, 'history') and session_context.history:
            # Detect anaphoric references using IntentDetector
            has_anaphora = self._intent_detector.has_anaphoric_reference(question)
            
            # If anaphora detected, force RAG (user needs doc search for previous topic)
            if has_anaphora:
                force_rag_for_followup = True
            
            # Get last 2 exchanges for context (avoid too much token usage)
            recent_history = session_context.history[-2:]
            context_parts = []
            for prev_q, prev_a in recent_history:
                # Only include question (answer is too long)
                context_parts.append(f"Question précédente: {prev_q}")
            
            if context_parts:
                history_context = "\n".join(context_parts)
                enriched_query = f"{history_context}\n\nQuestion actuelle: {question}"
        
        return self._decide_internal(
            chat_id=chat_id,
            raw_query=enriched_query,  # Use enriched query with history
            rewritten_query=enriched_query,
            filters=filters,
            pinned_bias=bool(session_context),
            last_decision=last_decision,
            force_rag_for_followup=force_rag_for_followup,
        )
    
    def calculate_rag_signal(
        self,
        question: str,
        filters: Optional[Filters] = None,
    ) -> float:
        """
        IRouter-compatible calculate_rag_signal (simple version).
        
        Returns just the confidence score (0..1).
        """
        filters = filters or Filters()
        signal = self._calculate_rag_signal_internal(
            query=question,
            filters=filters,
        )
        return signal["rag_conf"]
    
    # -------------------------
    # Internal implementation
    # -------------------------
    
    def _decide_internal(
        self,
        *,
        chat_id: str,
        raw_query: str,
        rewritten_query: str,
        filters: Filters,
        pinned_bias: bool = False,
        last_decision: Optional[str] = None,
        force_rag_for_followup: bool = False,
    ) -> RouterDecision:
        """
        Main routing decision logic.
        
        Args:
            chat_id: Conversation ID
            raw_query: Original user query
            rewritten_query: Query rewritten by QueryRewriter
            filters: Document filters
            pinned_bias: Whether to apply pinning bias
            last_decision: Previous routing decision (for continuity)
            
        Returns:
            RouterDecision with decision, confidence, task, filters, passport
            
        Decision logic:
        1. Detect intent (task type + special intents)
        2. Calculate RAG signal (sim, struct, kw, pin)
        3. Apply penalties if weak context
        4. Compare to thresholds → decision
        5. Override for special intents (book/out-of-syllabus)
        6. Build passport with metadata
        """
        # Normalize queries
        raw_norm = IntentDetector._normalize(raw_query)
        rew_norm = IntentDetector._normalize(rewritten_query or raw_query)
        
        # 1. Intent detection
        task_main, intent_scores = self._intent_detector.detect_intent(raw_norm)
        special_task = self._intent_detector.detect_special_intent(raw_norm)
        task = special_task or task_main
        
        # 2. RAG signal calculation
        rag_signal = self._calculate_rag_signal_internal(
            query=rew_norm,
            filters=filters,
            pinned_bias=pinned_bias,
            last_decision=last_decision,
        )
        
        # Extract signal components
        rag_conf = rag_signal["rag_conf"]
        rag_stats = rag_signal["rag_stats"]
        
        # 3. Thresholds
        t_rag = self._get_threshold("router_threshold_rag_first", 0.55)
        t_llm = self._get_threshold("router_threshold_llm_first", 0.35)
        
        # 4. Decision logic
        weak_ctx = rag_signal["weak_context"]
        
        # Force RAG if anaphoric reference detected (follow-up question)
        if force_rag_for_followup:
            decision = "rag_first"
            reason = "référence au contexte précédent détectée (follow-up)"
        elif task in {"book_exercises", "book_demo", "course_extension"}:
            decision = "rag_to_llm"
            reason = "intent livre/hors programme détecté"
        else:
            if rag_conf >= t_rag and not weak_ctx:
                decision, reason = "rag_first", "signal RAG fort"
            elif rag_conf >= t_llm:
                decision, reason = "llm_first", "signal RAG moyen"
            else:
                decision, reason = "llm_only", "signal RAG faible"
        
        # 5. Build passport
        passport = self._build_passport(
            chat_id=chat_id,
            raw_query=raw_query,
            rewritten_query=rewritten_query or raw_query,
            filters=filters,
            decision=decision,
            rag_conf=rag_conf,
            task=task,
            intent_scores=intent_scores,
            rag_stats=rag_stats,
            reason=reason,
            matched_special=special_task,
        )
        
        # Convert Filters to dict for backward compatibility
        filters_dict = {
            "chapter": filters.chapter,
            "block_kind": filters.block_kind,
            "block_id": filters.block_id,
            "type": filters.type,
            "doc_type": filters.doc_type,
        }
        
        return RouterDecision(
            decision=decision,
            rag_confidence=rag_conf,
            task_type=task,
            reason=reason,
            filters=filters,
            metadata=passport,
        )
    
    def _calculate_rag_signal_internal(
        self,
        *,
        query: str,
        filters: Filters,
        pinned_bias: bool = False,
        last_decision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate RAG confidence signal (quick retrieval).
        
        Args:
            query: Normalized query text
            filters: Document filters
            pinned_bias: Whether to apply pinning bias
            last_decision: Previous routing decision
            
        Returns:
            Dict with:
            - rag_conf: Final confidence (0..1)
            - sim: Fuzzy similarity (0..1)
            - struct_bonus: Structural match bonus (0..0.2)
            - kw_signal: Math keyword signal (0/1)
            - pin_signal: Pinning signal (0..1+)
            - weak_context: Whether context is weak
            - rag_stats: Retrieval metadata
            
        Signal composition:
        - Base = w_sim*sim + w_struct*struct + w_kw*kw + w_pin*pin
        - Penalties applied if weak context
        - Clamped to [0, 1]
        """
        # Convert Filters to dict for retriever
        filters_dict = self._filters_to_dict(filters)
        
        # Calculate dynamic k (more docs if fewer filters)
        filter_count = sum(
            1 for k in ("chapter", "block_kind", "block_id", "type", "doc_type")
            if filters_dict.get(k)
        )
        k = 5 + (0 if filter_count >= 2 else 3)
        
        # Normalize query for retrieval (LaTeX → Unicode)
        query_normalized = normalize_query_for_retrieval(query)
        
        # Quick retrieval
        t0 = time.time()
        try:
            docs = self._retriever.retrieve(query_normalized, filters, top_k=k)
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            return self._error_signal(k, latency_ms, str(e))
        
        latency_ms = int((time.time() - t0) * 1000)
        
        if not docs:
            return self._empty_signal(k, latency_ms)
        
        # Calculate similarity signal
        sim, struct_bonus, struct_hits = self._calculate_similarity(
            query=query,
            docs=docs,
            filters=filters_dict,
        )
        
        # Calculate discrete signals
        kw_signal = 1.0 if self._intent_detector.looks_like_math(query) else 0.0
        pin_signal = self._calculate_pin_signal(pinned_bias, last_decision)
        
        # Weighted combination
        base = (
            self._config.router_w_sim * float(sim) +
            self._config.router_w_struct * float(struct_bonus) +
            self._config.router_w_kw * float(kw_signal) +
            self._config.router_w_pin * float(pin_signal)
        )
        
        # Penalties for weak context
        weak_ctx = (len(docs) < 3) or (sim < 0.25)
        if weak_ctx:
            base -= self._config.router_weak_penalty
        
        rag_conf = self._clamp(base)
        
        # Extra penalty if filters specified but context still weak
        if weak_ctx and (filters.chapter or filters.block_id or filters.block_kind):
            rag_conf = self._clamp(rag_conf - self._config.router_weak_penalty_focus)
        
        # Build stats
        rag_stats = {
            "k": k,
            "hits": len(docs),
            "sim_max": sim,
            "struct_hits": struct_hits,
            "latency_ms": latency_ms,
            "weights": {
                "sim": self._config.router_w_sim,
                "struct": self._config.router_w_struct,
                "kw": self._config.router_w_kw,
                "pin": self._config.router_w_pin,
            },
            "signals": {
                "sim": float(sim),
                "struct": float(struct_bonus),
                "kw_signal": float(kw_signal),
                "pin_signal": float(pin_signal),
                "weak_ctx": bool(weak_ctx),
            },
            "penalties": {
                "weak_penalty": self._config.router_weak_penalty,
                "weak_penalty_focus": self._config.router_weak_penalty_focus,
            },
        }
        
        return {
            "rag_conf": rag_conf,
            "sim": sim,
            "struct_bonus": struct_bonus,
            "kw_signal": kw_signal,
            "pin_signal": pin_signal,
            "weak_context": weak_ctx,
            "rag_stats": rag_stats,
        }
    
    # -------------------------
    # Private helpers
    # -------------------------
    
    def _calculate_similarity(
        self,
        query: str,
        docs: List[Document],
        filters: Dict[str, Any],
    ) -> tuple[float, float, int]:
        """
        Calculate fuzzy similarity and structural bonus.
        
        Returns:
            Tuple of (max_sim, struct_bonus, struct_hits)
        """
        sims = []
        for doc in docs:
            snippet = normalize_whitespace(doc.page_content or "")[:700]
            partial = fuzz.partial_ratio(query, snippet) / 100.0
            token_sort = fuzz.token_sort_ratio(query, snippet) / 100.0
            sims.append(0.6 * partial + 0.4 * token_sort)
        
        sim_max = max(sims) if sims else 0.0
        
        # Structural bonus: filters match metadata
        struct_hits = 0
        for doc in docs:
            meta = doc.metadata
            if filters.get("chapter") and str(meta.get("chapter")) == str(filters["chapter"]):
                struct_hits += 1
            if filters.get("block_kind") and str(meta.get("block_kind")).lower() == str(filters["block_kind"]).lower():
                struct_hits += 1
            if filters.get("block_id") and str(meta.get("block_id")) == str(filters["block_id"]):
                struct_hits += 1
        
        struct_bonus = 0.2 if struct_hits >= 2 else (0.1 if struct_hits == 1 else 0.0)
        
        return sim_max, struct_bonus, struct_hits
    
    def _calculate_pin_signal(
        self,
        pinned_bias: bool,
        last_decision: Optional[str],
    ) -> float:
        """Calculate pinning signal with continuity bonus."""
        if not pinned_bias:
            return 0.0
        
        pin_signal = 1.0
        
        # Continuity bonus (preserve synergy effect from original code)
        if last_decision in {"rag_first", "rag_to_llm"} and self._config.router_w_pin > 0:
            # Original: +0.025 synergy, converted to relative gain on pin weight
            pin_signal += (0.025 / self._config.router_w_pin)
        
        return pin_signal
    
    def _build_passport(
        self,
        *,
        chat_id: str,
        raw_query: str,
        rewritten_query: str,
        filters: Filters,
        decision: str,
        rag_conf: float,
        task: str,
        intent_scores: Dict[str, float],
        rag_stats: Dict[str, Any],
        reason: str,
        matched_special: Optional[str],
    ) -> Dict[str, Any]:
        """Build context passport with all routing metadata."""
        filters_dict = self._filters_to_dict(filters)
        
        return {
            "chat_id": chat_id,
            "turn_id": uuid.uuid4().hex[:8],
            "user_query_raw": raw_query,
            "user_query_rewritten": rewritten_query,
            "filters": {k: v for k, v in filters_dict.items() if v},
            "routing": {
                "decision": decision,
                "rag_conf": round(float(rag_conf), 3),
                "thresholds": {
                    "rag_first": self._get_threshold("router_threshold_rag_first", 0.55),
                    "llm_first": self._get_threshold("router_threshold_llm_first", 0.35),
                },
                "weights": {
                    "sim": self._config.router_w_sim,
                    "struct": self._config.router_w_struct,
                    "kw": self._config.router_w_kw,
                    "pin": self._config.router_w_pin,
                },
                "rag_stats": rag_stats,
                "reason": reason,
                "matched_special": matched_special,
            },
            "task": task,
            "intent_scores": {k: round(v, 3) for k, v in intent_scores.items()},
            "safety": {"math_only": True},
            "ts": int(time.time()),
        }
    
    def _get_threshold(self, name: str, default: float) -> float:
        """Get threshold value from config."""
        return float(getattr(self._config, name, default))
    
    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        """Clamp value to [lo, hi]."""
        return max(lo, min(hi, value))
    
    @staticmethod
    def _filters_to_dict(filters: Filters) -> Dict[str, Any]:
        """Convert Filters to dict."""
        return {
            "chapter": filters.chapter,
            "block_kind": filters.block_kind,
            "block_id": filters.block_id,
            "type": filters.type,
            "doc_type": filters.doc_type,
        }
    
    def _error_signal(self, k: int, latency_ms: int, error: str) -> Dict[str, Any]:
        """Return error signal with zero confidence."""
        return {
            "rag_conf": 0.0,
            "sim": 0.0,
            "struct_bonus": 0.0,
            "kw_signal": 0.0,
            "pin_signal": 0.0,
            "weak_context": True,
            "rag_stats": {
                "k": k,
                "hits": 0,
                "sim_max": 0.0,
                "struct_hits": 0,
                "latency_ms": latency_ms,
                "error": error,
            },
        }
    
    def _empty_signal(self, k: int, latency_ms: int) -> Dict[str, Any]:
        """Return empty signal with zero confidence."""
        return {
            "rag_conf": 0.0,
            "sim": 0.0,
            "struct_bonus": 0.0,
            "kw_signal": 0.0,
            "pin_signal": 0.0,
            "weak_context": True,
            "rag_stats": {
                "k": k,
                "hits": 0,
                "sim_max": 0.0,
                "struct_hits": 0,
                "latency_ms": latency_ms,
            },
        }
