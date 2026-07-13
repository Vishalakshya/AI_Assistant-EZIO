import os
import logging
from typing import Any, Dict, List, Optional
import ollama
from app.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.model_name = os.getenv("OLLAMA_MODEL", "gemma3:4b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.client = ollama.AsyncClient(host=self.base_url)

    async def _check_health(self) -> bool:
        """Ping the local Ollama server to ensure it is running."""
        try:
            # list() throws an error if connection fails
            await self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 64,
    ) -> Dict[str, Any]:
        
        if not await self._check_health():
            return {
                "content": "Ollama is not running. Start Ollama and try again.",
                "tool_calls": [],
                "finish_reason": "error"
            }

        # Cap max tokens for desktop responses as requested
        capped_tokens = min(max_tokens, 80) if max_tokens > 0 else 64

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "keep_alive": -1,
            "options": {
                "temperature": temperature,
                "num_predict": capped_tokens
            }
        }
        
        # Ollama native tool calling
        if tools:
            # Ollama expects standard OpenAI-like tool definitions
            kwargs["tools"] = tools

        try:
            response = await self.client.chat(**kwargs)
            message = response.get("message", {})
            
            # Format tool calls to match the standard schema Orchestrator expects
            formatted_tool_calls = []
            if message.get("tool_calls"):
                for tc in message["tool_calls"]:
                    formatted_tool_calls.append({
                        "id": "call_" + tc["function"]["name"], # Ollama doesn't always provide an ID, mock one
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"] # Already a dict in ollama
                    })

            return {
                "content": message.get("content", ""),
                "tool_calls": formatted_tool_calls,
                "finish_reason": "tool_calls" if formatted_tool_calls else "stop"
            }
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return {
                "content": f"Ollama encountered an error: {str(e)}",
                "tool_calls": [],
                "finish_reason": "error"
            }

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ):
        if not await self._check_health():
            yield {
                "content": "Ollama is not running. Start Ollama and try again.",
                "tool_calls": None,
                "finish_reason": "error"
            }
            return

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "keep_alive": -1,
            "options": {
                "temperature": temperature,
                "num_predict": 64
            }
        }
        
        if tools:
            kwargs["tools"] = tools
            
        try:
            async for chunk in await self.client.chat(**kwargs):
                message = chunk.get("message", {})
                
                # Format tool calls
                formatted_tool_calls = None
                if message.get("tool_calls"):
                    formatted_tool_calls = []
                    for tc in message["tool_calls"]:
                        formatted_tool_calls.append({
                            "id": "call_" + tc["function"]["name"],
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        })

                yield {
                    "content": message.get("content", ""),
                    "tool_calls": formatted_tool_calls,
                    "finish_reason": "stop" if chunk.get("done") else None
                }
        except Exception as e:
            logger.error(f"Ollama stream failed: {e}")
            yield {
                "content": f"\n\n[Ollama Error: {str(e)}]",
                "tool_calls": None,
                "finish_reason": "error"
            }

    async def supports_tools(self) -> bool:
        """
        Checks if the configured model natively supports tool calling
        by checking if 'Tools' is present in the model's template.
        """
        if not await self._check_health():
            return False
            
        # Hardcode fallback for known non-tool models like gemma3:4b
        if "gemma" in self.model_name.lower():
            return False
            
        try:
            info = await self.client.show(self.model_name)
            template = info.get("template", "")
            if "{{ .Tools }}" in template or "{{.Tools}}" in template:
                return True
            # Some models might support it without explicit template, but we assume False for safety
            return False
        except Exception as e:
            logger.error(f"Failed to check model info: {e}")
            return False
