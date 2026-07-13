import logging
import json
from typing import Dict, Any, List
from app.core.tools.manager import ToolManager
from app.core.tools.schemas import ToolContext
from app.core.security.confirmation import confirmation_manager
from app.core.orchestrator.planner import Plan

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Layer 3 - Tool Executor
    Executes tools sequentially and collects outputs.
    """
    def __init__(self, tool_manager: ToolManager):
        self.tools = tool_manager

    async def execute_plan(self, plan: Plan, user_id: str, session_id: str, security_level: str) -> List[Dict[str, Any]]:
        results = []
        context = ToolContext(user_id=user_id, session_id=session_id)
        
        for step in plan.steps:
            args_str = json.dumps(step.arguments)
            logger.info(f"[Layer3] Executing Tool\n{step.tool}({args_str})")
            
            # Request confirmation for dangerous tasks
            if security_level == "dangerous" or step.tool.startswith("write_") or step.tool.startswith("delete_"):
                approved = await confirmation_manager.request_confirmation(user_id, step.tool, step.arguments)
                if not approved:
                    logger.warning(f"Tool {step.tool} denied by user.")
                    results.append({"tool": step.tool, "status": "denied", "result": "Denied by user."})
                    break # Stop execution if a step is denied
                    
            result = await self.tools.execute_tool_call(step.tool, step.arguments, context)
            
            # Handle pending confirmation from tool implementation itself
            if result.status == "pending":
                approved = await confirmation_manager.request_confirmation(user_id, step.tool, step.arguments)
                if not approved:
                    results.append({"tool": step.tool, "status": "denied", "result": "Denied by user."})
                    break
                else:
                    # Execute again after approval
                    result = await self.tools.execute_tool_call(step.tool, step.arguments, context)
            
            if result.status == "success":
                results.append({"tool": step.tool, "status": "success", "result": result.output})
            else:
                results.append({"tool": step.tool, "status": "error", "result": result.error_message})
                break # Stop on error
                
        return results
