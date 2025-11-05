"""
IRetriever - Abstract interface for document retrieval
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ...domain.entities import Document
from ...domain.value_objects import Filters


class IRetriever(ABC):
    """
    Abstract interface for document retrieval.
    
    Implementations can use different strategies:
    - Hybrid (BM25 + Vector + Reranker)
    - Pure vector search
    - ColBERT late interaction
    - etc.
    """
    
    @abstractmethod
    def retrieve(
        self,
        query: str,
        filters: Optional[Filters] = None,
        k: int = 5,
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query
            filters: Optional filters (doc_type, bloc_name, etc.)
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with scores
        """
        pass
    
    @abstractmethod
    def get_available_blocs(self) -> List[str]:
        """
        Get list of available bloc names in the vector store.
        
        Returns:
            List of unique bloc names
        """
        pass
    
    @abstractmethod
    def get_available_doc_types(self) -> List[str]:
        """
        Get list of available document types.
        
        Returns:
            List of unique doc types (cours, td, exam, etc.)
        """
        pass
