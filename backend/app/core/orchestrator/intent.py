from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Intent(BaseModel):
    intent: str = Field(description="A short string describing what the user wants to do")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="The exact arguments extracted from the request")
    confidence: float = Field(default=0.0, description="Confidence score between 0 and 1")
    tool: Optional[str] = Field(default=None, description="The exact name of the primary tool to use, if any")
    security_level: str = Field(default="safe", description="Security level: safe, moderate, or dangerous")
    requires_memory: bool = Field(default=False, description="True if memory/context is needed")
    requires_reasoning: bool = Field(default=False, description="True if complex thinking is needed")
