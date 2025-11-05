"""
Assistant module - Entry point for Math Assistant

NEW (Phase 4 - SOLID):
----------------------
Use get_assistant() to get the NEW SOLID architecture with:
- DI Container (automatic dependency injection)
- 16 Use Cases
- MathAssistantFacade (unified API)
- Backward-compatible API via LegacyAssistantAdapter

OLD (Legacy):
-------------
Use get_legacy_assistant() to get the old monolithic MathAssistant.

MIGRATION:
----------
1. Import stays the same:
   from src.assistant import get_assistant

2. Code works unchanged:
   assistant = get_assistant()
   result = assistant.route_and_execute(question)
   result = assistant.run_task("qcm", topic)

3. Under the hood:
   - OLD: Returns MathAssistant (1036 lines monolith)
   - NEW: Returns LegacyAssistantAdapter wrapping MathAssistantFacade
   
4. Toggle with environment variable:
   USE_LEGACY_ASSISTANT=1  → Old monolith
   USE_LEGACY_ASSISTANT=0  → New SOLID (default)
"""

import os

# Check which assistant to use
USE_LEGACY = os.getenv("USE_LEGACY_ASSISTANT", "0") == "1"

if USE_LEGACY:
    # Use old monolithic assistant
    from .assistant import MathAssistant as _LegacyAssistant
    
    def get_assistant():
        """Get legacy monolithic assistant."""
        return _LegacyAssistant()
    
    def get_legacy_assistant():
        """Get legacy monolithic assistant (explicit)."""
        return _LegacyAssistant()

else:
    # Use NEW SOLID architecture with adapter
    from ..application.adapters import LegacyAssistantAdapter
    
    def get_assistant():
        """
        Get Math Assistant (NEW SOLID architecture).
        
        Returns LegacyAssistantAdapter wrapping MathAssistantFacade.
        Provides backward-compatible API while using SOLID architecture.
        
        Returns
        -------
        LegacyAssistantAdapter
            Adapter providing old API with new architecture
            
        Examples
        --------
        >>> assistant = get_assistant()
        >>> result = assistant.route_and_execute("Question?")
        >>> result = assistant.run_task("qcm", "séries", num_questions=5)
        """
        return LegacyAssistantAdapter()
    
    def get_legacy_assistant():
        """Get legacy monolithic assistant (if needed for comparison)."""
        from .assistant import MathAssistant
        return MathAssistant()


__all__ = ["get_assistant", "get_legacy_assistant"]