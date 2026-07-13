from typing import List, Dict
from app.core.tools.registry import registry
from app.core.tools.executor import ToolExecutor
from app.core.tools.schemas import ToolResult, ToolContext
from app.core.security.permissions import permission_manager # We will build this next

class ToolManager:
    """
    Coordinates Registry, Executor, and Permission checking.
    """
    def __init__(self):
        self.executor = ToolExecutor()

    def get_available_schemas(self) -> List[Dict]:
        return registry.get_all_schemas()

    async def execute_tool_call(self, tool_name: str, arguments: str, context: ToolContext) -> ToolResult:
        """
        Main entry point for Orchestrator to execute a tool.
        """
        # 1. Check Permissions
        metadata = registry.get_metadata(tool_name)
        is_approved, reason = await permission_manager.check_permission(
            user_id=context.user_id, 
            tool_name=tool_name, 
            tier=metadata.permissions.tier
        )
        
        if not is_approved:
            # If Tier 3, this triggers the confirmation flow which pauses execution
            if reason == "CONFIRMATION_REQUIRED":
                return ToolResult(tool_name=tool_name, status="pending", error_message="Waiting for user confirmation.")
            
            return ToolResult(tool_name=tool_name, status="denied", error_message=reason)

        # 2. Execute
        result = await self.executor.execute(tool_name, arguments, context)
        
        # 3. Log (Implementation of ActionLogger omitted for brevity)
        
        return result
