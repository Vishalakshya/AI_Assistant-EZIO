import os
from typing import Any, Dict, List, Optional
import json
import logging
from openai import AsyncOpenAI
from app.core.llm.base import LLMProvider
from app.core.security.windows_credentials import credential_manager

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        # We assume single user "local_user_001" for v1.
        secure_api_key = credential_manager.get_key("OPENAI", "local_user_001")
        
        # Development fallback
        if not secure_api_key:
            secure_api_key = os.getenv("OPENAI_API_KEY")
            
        if secure_api_key:
            self.client = AsyncOpenAI(api_key=secure_api_key)
        else:
            logger.warning("OpenAI API Key not found in Windows Credential Manager or environment variables.")
            raise ValueError("OpenAI API key not found.")

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response: ChatCompletion = await self.client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        
        formatted_tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                formatted_tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                })

        return {
            "content": message.content,
            "tool_calls": formatted_tool_calls,
            "finish_reason": response.choices[0].finish_reason
        }

    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            
        try:
            stream = await self.client.chat.completions.create(**kwargs)
            async for chunk in stream:
                # Format streaming chunks
                delta = chunk.choices[0].delta
                yield {
                    "content": delta.content,
                    "tool_calls": delta.tool_calls, # Might require careful reconstruction in the orchestrator
                    "finish_reason": chunk.choices[0].finish_reason
                }
        except Exception as e:
            logger.error(f"OpenAI stream failed: {e}")
            yield {
                "content": f"\n\n[OpenAI Error: {str(e)}]",
                "tool_calls": None,
                "finish_reason": "error"
            }

    async def supports_tools(self) -> bool:
        """
        OpenAI API natively supports tool calling for all modern chat models.
        """
        return True
