from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    Ensures the AgentOrchestrator remains model-agnostic.
    """
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Generates a response from the LLM.
        
        Args:
            messages: A list of message dictionaries (e.g., role, content).
            tools: Optional list of JSON schemas for function calling.
            temperature: Sampling temperature.
            max_tokens: Max output tokens.
            
        Returns:
            A standardized dictionary containing 'content', 'tool_calls', and 'finish_reason'.
        """
        pass

    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ):
        """
        Streams a response from the LLM.
        Yields chunks of text or tool calls.
        """
        pass

    @abstractmethod
    async def supports_tools(self) -> bool:
        """
        Returns True if the provider/model supports native tool calling.
        """
        pass
