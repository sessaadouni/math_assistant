"""
Adapters for backward compatibility

This module provides adapters to connect the new SOLID architecture
with legacy code (CLI, GUI, API) without requiring full rewrites.
"""

from .legacy_assistant_adapter import LegacyAssistantAdapter

__all__ = ["LegacyAssistantAdapter"]
