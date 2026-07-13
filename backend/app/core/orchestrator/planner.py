import logging
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.llm.base import LLMProvider
from app.core.tools.manager import ToolManager
from app.core.orchestrator.intent import Intent

logger = logging.getLogger(__name__)

class Step(BaseModel):
    tool: str
    arguments: Dict[str, Any]
    description: str

class Plan(BaseModel):
    steps: List[Step]

class Planner:
    """
    Layer 2 - Deterministic Planner
    Decides HOW to solve the request using Python logic first.
    """
    def __init__(self, llm_provider: LLMProvider, tool_manager: ToolManager):
        self.llm = llm_provider
        self.tools = tool_manager

    async def create_plan(self, message: str, request_class: str, intent: Intent) -> Plan:
        # Deterministic Python-logic planning first
        if request_class in ["single_tool", "tool_with_parameters"] and intent.tool:
            plan = Plan(steps=[Step(tool=intent.tool, arguments=intent.parameters or {}, description=intent.intent)])
            logger.info(f"[Layer2] Plan\n{len(plan.steps)} Step")
            return plan
            
        if request_class in ["conversation", "knowledge", "memory", "voice"]:
            if not intent.tool:
                # No tools needed
                plan = Plan(steps=[])
                logger.info(f"[Layer2] Plan\n0 Steps")
                return plan

        # Complex reasoning / Multi-step task path requires LLM
        tool_schemas = self.tools.get_available_schemas()
        
        # Compress tool schemas to drastically reduce token count
        simplified_tools = []
        for schema in tool_schemas:
            func = schema.get("function", {})
            params = list(func.get("parameters", {}).get("properties", {}).keys())
            simplified_tools.append(f"{func.get('name')}({', '.join(params)}) - {func.get('description')}")
        
        tools_list_str = "\n".join(simplified_tools)
        
        prompt = (
            "You are the Layer 2 Deterministic Planner.\n"
            "Generate a sequential execution plan of tools to fulfill the request.\n"
            f"User Request: {message}\n"
            f"Intent: {intent.intent}\n\n"
            "Available tools:\n"
            f"{tools_list_str}\n\n"
            "Output ONLY a JSON list of steps. Format exactly:\n"
            "{\n"
            '  "steps": [\n'
            '    {"tool": "tool_name", "arguments": {"arg": "value"}, "description": "What this step does"}\n'
            "  ]\n"
            "}\n"
        )
        
        try:
            response = await self.llm.generate_response(messages=[{"role": "system", "content": prompt}])
            content = response.get("content", "").strip()
            
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                plan = Plan(**data)
                
                step_word = "Step" if len(plan.steps) == 1 else "Steps"
                logger.info(f"[Layer2] Plan\n{len(plan.steps)} {step_word}")
                return plan
        except Exception as e:
            logger.error(f"[Layer2] Error: {e}")
            
        plan = Plan(steps=[])
        logger.info(f"[Layer2] Plan\n0 Steps")
        return plan
