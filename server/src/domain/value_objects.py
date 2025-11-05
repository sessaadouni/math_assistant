"""
Domain Value Objects - Immutable objects without identity
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List


class TaskType(str, Enum):
    """Task type enumeration"""
    
    QA = "qa"
    TUTOR = "tutor"
    COURSE_BUILD = "course_build"
    COURSE_EXPLAIN = "course_explain"
    COURSE_SUMMARY = "course_summary"
    EXERCISE_GEN = "exercise_gen"
    SOLVER = "solver"
    EXO_CORRECTOR = "exo_corrector"
    EXAM = "exam"
    EXAM_CORRECTOR = "exam_corrector"
    COURSE_STRUCTURE = "course_structure"
    PROBLEM_SOLVER = "problem_solver"
    FORMAL_VERIFIER = "formal_verifier"
    RESEARCH_ASSISTANT = "research_assistant"
    STUDY_PLANNER = "study_planner"
    CONCEPT_EXPLAINER = "concept_explainer"
    CALCULATOR = "calculator"
    
    @classmethod
    def from_string(cls, value: str) -> "TaskType":
        """Convert string to TaskType"""
        try:
            return cls(value)
        except ValueError:
            return cls.QA  # Default


@dataclass(frozen=True)
class Filters:
    """Immutable filters for document retrieval (compatible with RAGEngine)"""
    
    # Primary fields (aligned with RAGEngine metadata)
    chapter: Optional[str] = None
    block_kind: Optional[str] = None  # théorème, définition, etc.
    block_id: Optional[str] = None     # 1.2.3, etc.
    type: Optional[str] = None          # cours, exercice, théorie, etc.
    doc_type: Optional[str] = None     # alias for 'type'
    
    # Legacy fields (for backward compatibility)
    bloc_name: Optional[str] = None
    file_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding None values)"""
        return {
            k: v for k, v in {
                "chapter": self.chapter,
                "block_kind": self.block_kind,
                "block_id": self.block_id,
                "type": self.type or self.doc_type,  # use 'type' if set, else doc_type
                "doc_type": self.doc_type or self.type,
                "bloc_name": self.bloc_name,
                "file_name": self.file_name,
            }.items() if v is not None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Filters":
        """Create from dictionary"""
        return cls(
            chapter=data.get("chapter"),
            block_kind=data.get("block_kind"),
            block_id=data.get("block_id"),
            type=data.get("type"),
            doc_type=data.get("doc_type"),
            bloc_name=data.get("bloc_name"),
            file_name=data.get("file_name"),
        )
    
    def is_empty(self) -> bool:
        """Check if all filters are None"""
        return all(v is None for v in [
            self.chapter,
            self.block_kind,
            self.block_id,
            self.type,
            self.doc_type,
            self.bloc_name,
            self.file_name,
        ])
    
    def merge(self, other: "Filters") -> "Filters":
        """Merge with another Filters, keeping non-None values"""
        return Filters(
            chapter=other.chapter or self.chapter,
            block_kind=other.block_kind or self.block_kind,
            block_id=other.block_id or self.block_id,
            type=other.type or self.type,
            doc_type=other.doc_type or self.doc_type,
            bloc_name=other.bloc_name or self.bloc_name,
            file_name=other.file_name or self.file_name,
        )


@dataclass(frozen=True)
class RouterDecision:
    """Immutable routing decision (compatible with IntentRouter)"""
    
    # Core fields
    decision: str  # "rag_first" | "llm_first" | "llm_only" | "rag_to_llm"
    task_type: str  # Task key (qa, theorem, exercise_gen, etc.)
    rag_confidence: float  # 0..1
    reason: str
    
    # Optional fields
    filters: Filters = field(default_factory=lambda: Filters())
    rewritten_query: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Legacy compatibility properties
    @property
    def task(self) -> "TaskType":
        """Legacy compatibility: task as TaskType"""
        return TaskType.from_string(self.task_type)
    
    @property
    def use_rag(self) -> bool:
        """Legacy compatibility: use_rag flag"""
        return self.decision in {"rag_first", "rag_to_llm"}
    
    @property
    def confidence(self) -> float:
        """Legacy compatibility: confidence alias"""
        return self.rag_confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision": self.decision,
            "task_type": self.task_type,
            "task": self.task_type,  # alias
            "rag_confidence": self.rag_confidence,
            "confidence": self.rag_confidence,  # alias
            "use_rag": self.use_rag,
            "reason": self.reason,
            "filters": self.filters.to_dict(),
            "rewritten_query": self.rewritten_query,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouterDecision":
        """Create from dictionary (supports both old and new formats)"""
        # Support new format (decision, task_type, rag_confidence)
        if "decision" in data:
            return cls(
                decision=data.get("decision", "llm_only"),
                task_type=data.get("task_type", "qa"),
                rag_confidence=data.get("rag_confidence", 0.0),
                reason=data.get("reason", ""),
                filters=Filters.from_dict(data.get("filters", {})),
                rewritten_query=data.get("rewritten_query"),
                metadata=data.get("metadata", {}),
            )
        # Support old format (task, use_rag, confidence)
        else:
            task_type = data.get("task", "qa")
            use_rag = data.get("use_rag", False)
            confidence = data.get("confidence", 0.0)
            
            # Convert old use_rag to new decision
            if use_rag and confidence >= 0.55:
                decision = "rag_first"
            elif use_rag:
                decision = "rag_to_llm"
            elif confidence >= 0.35:
                decision = "llm_first"
            else:
                decision = "llm_only"
            
            return cls(
                decision=decision,
                task_type=task_type,
                rag_confidence=confidence,
                reason=data.get("reason", ""),
                filters=Filters.from_dict(data.get("filters", {})),
                rewritten_query=data.get("rewritten_query"),
            )


@dataclass
class SessionContext:
    """Session context for routing decisions"""
    
    chat_id: str
    history: List[Dict[str, str]] = field(default_factory=list)
    last_task: Optional[TaskType] = None
    last_filters: Filters = field(default_factory=lambda: Filters())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_exchange(self, question: str, answer: str):
        """Add Q&A exchange to history"""
        self.history.append({
            "question": question,
            "answer": answer,
        })
        # Keep only last 5 exchanges
        if len(self.history) > 5:
            self.history = self.history[-5:]
    
    def get_recent_context(self, n: int = 3) -> str:
        """Get recent conversation context as formatted string"""
        recent = self.history[-n:] if self.history else []
        if not recent:
            return ""
        
        lines = []
        for i, exchange in enumerate(recent, 1):
            lines.append(f"Q{i}: {exchange['question']}")
            lines.append(f"A{i}: {exchange['answer'][:100]}...")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chat_id": self.chat_id,
            "history": self.history,
            "last_task": self.last_task.value if self.last_task else None,
            "last_filters": self.last_filters.to_dict(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """Create from dictionary"""
        return cls(
            chat_id=data["chat_id"],
            history=data.get("history", []),
            last_task=TaskType.from_string(data["last_task"]) if data.get("last_task") else None,
            last_filters=Filters.from_dict(data.get("last_filters", {})),
            metadata=data.get("metadata", {}),
        )
