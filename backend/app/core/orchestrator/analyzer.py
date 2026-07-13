import json
import logging
import re
from app.core.orchestrator.intent import Intent
from app.core.llm.base import LLMProvider
from app.core.tools.manager import ToolManager

logger = logging.getLogger(__name__)

class IntentAnalyzer:
    """
    Layer 1 - Intent Extractor
    Converts natural language into a structured intent.
    """
    def __init__(self, llm_provider: LLMProvider, tool_manager: ToolManager):
        self.llm = llm_provider
        self.tools = tool_manager

    async def analyze(self, message: str, request_class: str) -> Intent:
        tool_schemas = self.tools.get_available_schemas()
        
        # Compress tool schemas to drastically reduce token count
        simplified_tools = []
        for schema in tool_schemas:
            func = schema.get("function", {})
            params = list(func.get("parameters", {}).get("properties", {}).keys())
            simplified_tools.append(f"{func.get('name')}({', '.join(params)}) - {func.get('description')}")
        
        tools_list_str = "\n".join(simplified_tools)
        
        prompt = (
            "You are the Layer 1 Intent Extractor.\n"
            f"The request has been classified as: {request_class}\n"
            "Extract the intent, parameters, and requirements into JSON.\n"
            "You MUST output valid JSON and NOTHING else.\n\n"
            "Available tools:\n"
            f"{tools_list_str}\n\n"
            "JSON Format exactly as follows:\n"
            "{\n"
            '  "intent": "Short description",\n'
            '  "parameters": {"param1": "value1"}, // or null\n'
            '  "confidence": 0.95,\n'
            '  "tool": "tool_name", // or null\n'
            '  "security_level": "safe", // safe, moderate, or dangerous\n'
            '  "requires_memory": false,\n'
            '  "requires_reasoning": false,\n'
            '  "requires_confirmation": false\n'
            "}\n\n"
            f"User Request: {message}\n"
        )

        try:
            response = await self.llm.generate_response(messages=[{"role": "system", "content": prompt}])
            content = response.get("content", "").strip()
            
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                intent_obj = Intent(**data)
                
                # Format intent name properly
                intent_name = intent_obj.tool if intent_obj.tool else intent_obj.intent
                logger.info(f"[Layer1] Intent\n{intent_name}")
                
                return intent_obj
        except Exception as e:
            logger.error(f"[Layer1] Error: {e}")

        logger.info("[Layer1] Intent\nunknown")
        return Intent(intent="unknown", requires_reasoning=True, requires_memory=True)
