"""
ISessionStore - Abstract interface for session persistence
"""

from abc import ABC, abstractmethod
from typing import Optional

from ...domain.value_objects import SessionContext
from ...domain.entities import Question, Answer


class ISessionStore(ABC):
    """
    Abstract interface for session storage.
    
    Implementations can use:
    - In-memory dictionaries (development)
    - SQLite (simple persistence)
    - Redis (production, distributed)
    - PostgreSQL (full relational)
    """
    
    @abstractmethod
    def get_context(self, chat_id: str) -> SessionContext:
        """
        Get session context for a chat.
        
        Args:
            chat_id: Unique chat identifier
            
        Returns:
            SessionContext (creates new if doesn't exist)
        """
        pass
    
    @abstractmethod
    def update_context(
        self,
        chat_id: str,
        question: Question,
        answer: Answer,
    ) -> None:
        """
        Update session context with new Q&A exchange.
        
        Args:
            chat_id: Unique chat identifier
            question: Question entity
            answer: Answer entity
        """
        pass
    
    @abstractmethod
    def clear_context(self, chat_id: str) -> None:
        """
        Clear session context for a chat.
        
        Args:
            chat_id: Unique chat identifier
        """
        pass
    
    @abstractmethod
    def exists(self, chat_id: str) -> bool:
        """
        Check if session exists.
        
        Args:
            chat_id: Unique chat identifier
            
        Returns:
            True if session exists
        """
        pass
    
    @abstractmethod
    def get_all_chat_ids(self) -> list[str]:
        """
        Get list of all active chat IDs.
        
        Returns:
            List of chat IDs
        """
        pass
