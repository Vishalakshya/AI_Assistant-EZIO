import os
import logging
from app.core.llm.base import LLMProvider
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

class LLMProviderFactory:
    @staticmethod
    def get_provider() -> LLMProvider:
        provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider_name == "ollama":
            logger.info("Initializing Ollama Provider...")
            return OllamaProvider()
        elif provider_name == "openai":
            logger.info("Initializing OpenAI Provider...")
            return OpenAIProvider()
        else:
            logger.warning(f"Unknown LLM provider '{provider_name}'. Falling back to Ollama.")
            return OllamaProvider()
