from typing import List, Dict, Any
from fastapi import APIRouter
from app.core.tools.registry import registry
from app.tools.system.controller import sys_controller

router = APIRouter()

@router.get("/")
async def list_tools():
    """
    Returns the complete list of available tools, their descriptions, and GPT schemas.
    """
    schemas = registry.get_all_schemas()
    return {"tools": schemas}

@router.get("/status")
async def get_system_status():
    """
    Health check and active metrics endpoint.
    """
    try:
        stats = sys_controller.get_system_stats()
        return {
            "status": "healthy",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
