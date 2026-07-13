from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ToolPermissions(BaseModel):
    tier: int = Field(default=1, description="1=Safe, 2=Moderate, 3=Dangerous")
    requires_confirmation: bool = Field(default=False)

class ToolMetadata(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] # JSON Schema dict for function args
    permissions: ToolPermissions = Field(default_factory=ToolPermissions)

class ToolContext(BaseModel):
    user_id: str
    session_id: str
    background_task: bool = False

class ToolResult(BaseModel):
    tool_name: str
    status: str = Field(description="'success', 'error', 'denied', 'pending'")
    output: Optional[Any] = None
    error_message: Optional[str] = None
