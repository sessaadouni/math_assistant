"""
Domain Entities - Core business objects with identity
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4


@dataclass
class Source:
    """Source document reference with metadata"""
    
    page: int
    doc_id: str
    doc_type: str
    file_name: str
    score: Optional[float] = None
    excerpt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "page": self.page,
            "doc_id": self.doc_id,
            "doc_type": self.doc_type,
            "file_name": self.file_name,
            "score": self.score,
            "excerpt": self.excerpt,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Source":
        """Create from dictionary"""
        return cls(
            page=data["page"],
            doc_id=data["doc_id"],
            doc_type=data["doc_type"],
            file_name=data["file_name"],
            score=data.get("score"),
            excerpt=data.get("excerpt"),
        )


@dataclass
class Document:
    """Retrieved document with content and metadata"""
    
    id: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
    
    def to_source(self) -> Source:
        """Convert document to source reference"""
        return Source(
            page=self.metadata.get("page", 0),
            doc_id=self.id,
            doc_type=self.metadata.get("doc_type", "cours"),
            file_name=self.metadata.get("file_name", "unknown"),
            score=self.score,
            excerpt=self.content[:200] if self.content else None,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
        }


@dataclass
class Context:
    """Context for RAG with documents and formatted text"""
    
    documents: List[Document]
    formatted_text: str
    num_sources: int
    
    @property
    def sources(self) -> List[Source]:
        """Get list of source references"""
        # Source is defined in this same file, no need to import
        result = []
        for doc in self.documents:
            if isinstance(doc, Source):
                result.append(doc)
            elif hasattr(doc, 'to_source'):
                result.append(doc.to_source())
            else:
                # Fallback: treat as Document-like object
                result.append(doc)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "documents": [doc.to_dict() for doc in self.documents],
            "formatted_text": self.formatted_text,
            "num_sources": self.num_sources,
        }


@dataclass
class Question:
    """User question entity"""
    
    id: str
    text: str
    chat_id: str
    created_at: datetime = field(default_factory=datetime.now)
    rewritten_text: Optional[str] = None
    
    @classmethod
    def create(cls, text: str, chat_id: str) -> "Question":
        """Create new question with generated ID"""
        return cls(
            id=str(uuid4()),
            text=text,
            chat_id=chat_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "text": self.text,
            "chat_id": self.chat_id,
            "created_at": self.created_at.isoformat(),
            "rewritten_text": self.rewritten_text,
        }


@dataclass
class Answer:
    """
    Generated answer entity.
    
    Supports both old-style (with sources) and new-style (with context) initialization:
    - Old: Answer(text="...", sources=[...], metadata={...})
    - New: Answer(id="...", question_id="...", text="...", context=Context(...))
    """
    
    text: str
    sources: Optional[List[Source]] = None  # For backward compatibility
    id: str = field(default_factory=lambda: str(uuid4()))
    question_id: str = ""
    chat_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    context: Optional[Context] = None
    task_type: Optional[str] = None
    model_used: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization to handle sources parameter"""
        # If sources were passed but context wasn't, use sources directly
        if self.sources is None and self.context:
            self.sources = self.context.sources
        elif self.sources is None:
            self.sources = []
    
    @classmethod
    def create(
        cls,
        question_id: str,
        text: str,
        chat_id: str,
        context: Optional[Context] = None,
        task_type: Optional[str] = None,
        model_used: Optional[str] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        sources: Optional[List[Source]] = None,
    ) -> "Answer":
        """Create new answer with generated ID"""
        return cls(
            id=str(uuid4()),
            question_id=question_id,
            text=text,
            chat_id=chat_id,
            context=context,
            task_type=task_type,
            model_used=model_used,
            execution_time=execution_time,
            metadata=metadata,
            sources=sources,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "text": self.text,
            "chat_id": self.chat_id,
            "created_at": self.created_at.isoformat(),
            "context": self.context.to_dict() if self.context else None,
            "task_type": self.task_type,
            "model_used": self.model_used,
            "execution_time": self.execution_time,
            "sources": [s.to_dict() for s in self.sources],
        }
