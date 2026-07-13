import json
import logging
from typing import Any, Dict, Union
from app.core.tools.registry import registry
from app.core.tools.schemas import ToolResult, ToolContext

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Executes a registered tool securely.
    """
    async def execute(self, tool_name: str, arguments: Union[str, Dict[str, Any]], context: ToolContext) -> ToolResult:
        try:
            # Parse arguments
            if isinstance(arguments, str):
                kwargs: Dict[str, Any] = json.loads(arguments)
            elif isinstance(arguments, dict):
                kwargs: Dict[str, Any] = arguments
            else:
                kwargs = {}
            
            # Fetch tool
            func = registry.get_tool(tool_name)
            
            # Execute
            # In a real async system, check if func is a coroutine
            result = await func(**kwargs, context=context)
            
            return ToolResult(
                tool_name=tool_name,
                status="success",
                output=result
            )
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse arguments for tool {tool_name}")
            return ToolResult(
                tool_name=tool_name,
                status="error",
                error_message="Invalid JSON arguments provided by LLM."
            )
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}")
            return ToolResult(
                tool_name=tool_name,
                status="error",
                error_message=str(e)
            )
