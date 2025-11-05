"""
OllamaLLMProvider - LLM provider using Ollama
"""

from typing import Optional, List, Dict, Any
import requests
from langchain_ollama import ChatOllama

from ...application.interfaces.llm_provider import ILLMProvider


class OllamaLLMProvider(ILLMProvider):
    """
    LLM provider using Ollama for local inference.
    
    Supports:
    - Local Ollama server
    - Remote Ollama endpoints (e.g., groq/deepseek cloud)
    - Fallback to smaller models
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "deepseek-v3:671b-cloud",
        api_key: Optional[str] = None,
        timeout: int = 300,
    ):
        """
        Initialize Ollama LLM provider.
        
        Args:
            base_url: Ollama server URL
            model: Model name (e.g., "deepseek-v3:671b-cloud", "qwen2.5:7b-math")
            api_key: Optional API key for cloud endpoints
            timeout: Request timeout in seconds
        """
        self._base_url = base_url
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        
        # Initialize LangChain ChatOllama
        self._chat_model = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.1,
            timeout=timeout,
        )
        
        # Set API key if provided
        if api_key:
            self._chat_model.api_key = api_key
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """Generate text completion"""
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Update temperature
        self._chat_model.temperature = temperature
        
        # Generate
        try:
            response = self._chat_model.invoke(messages)
            return response.content
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
    
    def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate with conversation history"""
        # Update temperature
        self._chat_model.temperature = temperature
        
        # Generate
        try:
            response = self._chat_model.invoke(messages)
            return response.content
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
    
    def get_model_name(self) -> str:
        """Get model name"""
        return self._model
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def list_available_models(self) -> List[str]:
        """List available models on Ollama server"""
        try:
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception:
            return []
