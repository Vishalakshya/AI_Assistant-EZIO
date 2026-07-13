from fastapi import Depends
from app.db.session import AsyncSessionLocal
from app.core.orchestrator.agent import AgentOrchestrator
from app.core.llm.factory import LLMProviderFactory
from app.core.tools.manager import ToolManager

# Global singletons for the orchestrator
_tool_manager = ToolManager()
_llm_provider = LLMProviderFactory.get_provider()
_orchestrator = AgentOrchestrator(llm_provider=_llm_provider, tool_manager=_tool_manager)

async def get_db():
    """Yields a SQLAlchemy async session."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_orchestrator() -> AgentOrchestrator:
    """Dependency injection for the central intelligence agent."""
    return _orchestrator

async def get_current_user_id() -> str:
    """
    Mock Dependency.
    In v1 (Single User Desktop), we return a hardcoded 'local_user' ID.
    In v2, this will extract and decode JWT/OAuth tokens from the request headers.
    """
    return "local_user_001"
