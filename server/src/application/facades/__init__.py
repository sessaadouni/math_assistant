"""
Application Facades - Simplified API layer

Facades provide simplified, unified APIs that orchestrate multiple use cases.
"""

from .math_assistant_facade import MathAssistantFacade, get_assistant, reset_assistant

__all__ = [
    "MathAssistantFacade",
    "get_assistant",
    "reset_assistant",
]
