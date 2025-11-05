"""
Settings - Configuration centralisée (backward compatible with core/config.py)
"""

# Re-export existing config for backward compatibility
from ..core.config import RAGConfig, UIConfig, rag_config, ui_config

__all__ = [
    "RAGConfig",
    "UIConfig",
    "Settings",
    "rag_config",
    "ui_config",
]


class Settings:
    """
    Unified settings class for the application.
    
    This wraps the existing RAGConfig and UIConfig for backward compatibility
    while providing a cleaner interface for new code.
    """
    
    def __init__(
        self,
        rag_config: RAGConfig = rag_config,
        ui_config: UIConfig = ui_config,
    ):
        self.rag = rag_config
        self.ui = ui_config
    
    # Convenience properties for common settings
    
    @property
    def ollama_host(self) -> str:
        """Get Ollama host URL"""
        return self.rag.ollama_host
    
    @property
    def ollama_api_key(self) -> str:
        """Get Ollama API key"""
        return self.rag.ollama_api_key
    
    @property
    def llm_model(self) -> str:
        """Get primary LLM model"""
        return self.rag.llm_model
    
    @property
    def llm_fallback_model(self) -> str:
        """Get fallback LLM model"""
        return self.rag.llm_local_fallback or self.rag.llm_model_local
    
    @property
    def embed_model(self) -> str:
        """Get embedding model"""
        return self.rag.embed_model_primary
    
    @property
    def reranker_model(self) -> str:
        """Get reranker model"""
        return self.rag.reranker_model
    
    @property
    def use_reranker(self) -> bool:
        """Check if reranker is enabled"""
        return self.rag.use_reranker
    
    @property
    def db_path(self) -> str:
        """Get database path"""
        return str(self.rag.db_dir)
    
    @property
    def collection_name(self) -> str:
        """Get collection name"""
        return self.rag.collection_name
