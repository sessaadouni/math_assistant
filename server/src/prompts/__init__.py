"""
Prompts Module - Organized by domain

This module contains all prompt templates organized by functional domain.
Each domain has its own subdirectory with related prompts.
"""

from .registry import PromptRegistry, get_default_registry

__all__ = [
    "PromptRegistry",
    "get_default_registry",
]
