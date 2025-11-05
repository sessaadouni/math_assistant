"""
FallbackLLMProvider - LLM provider with automatic fallback
"""

from typing import Optional, List, Dict

from ...application.interfaces.llm_provider import ILLMProvider


class FallbackLLMProvider(ILLMProvider):
    """
    LLM provider that falls back to a secondary model on failure.
    
    Use cases:
    - Primary: Large cloud model (deepseek-v3)
    - Fallback: Smaller local model (qwen2.5:7b-math)
    
    This ensures reliability even if the primary model is unavailable.
    """
    
    def __init__(
        self,
        primary: ILLMProvider,
        fallback: ILLMProvider,
    ):
        """
        Initialize fallback provider.
        
        Args:
            primary: Primary LLM provider
            fallback: Fallback LLM provider (used if primary fails)
        """
        self._primary = primary
        self._fallback = fallback
        self._using_fallback = False
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """Generate with fallback"""
        # Try primary
        try:
            result = self._primary.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=stop_sequences,
            )
            self._using_fallback = False
            return result
        except Exception as primary_error:
            # Log primary error (could use logging)
            print(f"⚠️  Primary LLM failed: {primary_error}")
            
            # Try fallback
            try:
                result = self._fallback.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop_sequences=stop_sequences,
                )
                self._using_fallback = True
                print(f"✅ Fallback LLM succeeded: {self._fallback.get_model_name()}")
                return result
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both LLMs failed. Primary: {primary_error}. Fallback: {fallback_error}"
                )
    
    def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate with history and fallback"""
        # Try primary
        try:
            result = self._primary.generate_with_history(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            self._using_fallback = False
            return result
        except Exception as primary_error:
            print(f"⚠️  Primary LLM failed: {primary_error}")
            
            # Try fallback
            try:
                result = self._fallback.generate_with_history(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                self._using_fallback = True
                print(f"✅ Fallback LLM succeeded: {self._fallback.get_model_name()}")
                return result
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both LLMs failed. Primary: {primary_error}. Fallback: {fallback_error}"
                )
    
    def get_model_name(self) -> str:
        """Get current model name"""
        if self._using_fallback:
            return f"{self._fallback.get_model_name()} (fallback)"
        return self._primary.get_model_name()
    
    def is_available(self) -> bool:
        """Check if at least one provider is available"""
        return self._primary.is_available() or self._fallback.is_available()
    
    def is_using_fallback(self) -> bool:
        """Check if currently using fallback"""
        return self._using_fallback
