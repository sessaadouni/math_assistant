"""
Configuration module
"""

from .settings import RAGConfig, UIConfig, Settings

# Keep backward compatibility with existing code
from .settings import rag_config, ui_config

__all__ = [
    "RAGConfig",
    "UIConfig",
    "Settings",
    "rag_config",
    "ui_config",
]
