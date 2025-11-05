"""
ILLMProvider - Abstract interface for LLM text generation
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class ILLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    
    Implementations can use:
    - Ollama (local)
    - OpenAI API
    - Anthropic Claude
    - Custom fine-tuned models
    - etc.
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """
        Generate text completion for a prompt.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens to generate
            stop_sequences: List of sequences that stop generation
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name/identifier of the current model.
        
        Returns:
            Model name
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available and healthy.
        
        Returns:
            True if available, False otherwise
        """
        pass
