import logging
import json
import re
from typing import Any
from app.core.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class RequestClassifier:
    """
    Layer 0 - Request Classifier
    Perform only lightweight request classification.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def classify(self, message: str) -> str:
        prompt = (
            "You are the Layer 0 Request Classifier.\n"
            "Classify the following request into exactly ONE of these categories:\n"
            "- conversation\n"
            "- single_tool\n"
            "- tool_with_parameters\n"
            "- multi_step\n"
            "- knowledge\n"
            "- memory\n"
            "- vision\n"
            "- voice\n"
            "- developer\n"
            "- system\n\n"
            "Output ONLY a JSON object exactly like this:\n"
            "{\"class\": \"<class_name>\"}\n\n"
            f"User Request: {message}\n"
        )
        
        try:
            response = await self.llm.generate_response(messages=[{"role": "system", "content": prompt}], max_tokens=100)
            content = response.get("content", "").strip()
            
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                category = data.get("class", "conversation")
                logger.info(f"[Layer0] Classification\n{category}")
                return category
        except Exception as e:
            logger.error(f"[Layer0] Error: {e}")
            
        logger.info("[Layer0] Classification\nconversation")
        return "conversation"
