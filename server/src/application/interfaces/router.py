"""
IRouter - Abstract interface for intent detection and routing
"""

from abc import ABC, abstractmethod
from typing import Optional

from ...domain.value_objects import RouterDecision, Filters, SessionContext


class IRouter(ABC):
    """
    Abstract interface for routing user queries.
    
    The router is responsible for:
    - Detecting user intent
    - Deciding which task to execute
    - Determining if RAG is needed
    - Suggesting filters
    """
    
    @abstractmethod
    def decide(
        self,
        question: str,
        session_context: Optional[SessionContext] = None,
        explicit_filters: Optional[Filters] = None,
    ) -> RouterDecision:
        """
        Analyze question and decide routing.
        
        Args:
            question: User's question
            session_context: Optional session context for continuity
            explicit_filters: Optional explicit filters from user
            
        Returns:
            RouterDecision with task, use_rag flag, filters, etc.
        """
        pass
    
    @abstractmethod
    def calculate_rag_signal(
        self,
        question: str,
        filters: Optional[Filters] = None,
    ) -> float:
        """
        Calculate confidence score for RAG usefulness.
        
        This is a quick check to see if RAG would be helpful
        based on query patterns and available documents.
        
        Args:
            question: User's question
            filters: Optional filters to narrow search
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        pass
