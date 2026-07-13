import asyncio
from app.core.orchestrator.agent import AgentOrchestrator
from app.core.tools.manager import ToolManager
from app.core.llm.ollama_provider import OllamaProvider
from app.db.session import AsyncSessionLocal
import logging

logging.basicConfig(level=logging.INFO)

async def test_fallback():
    # Force use Ollama provider
    llm = OllamaProvider()
    tools = ToolManager()
    agent = AgentOrchestrator(llm_provider=llm, tool_manager=tools)
    
    # We need an application context to register the tools, so import them
    import app.tools.system.tools
    import app.tools.apps.tools
    import app.tools.browser.tools
    import app.tools.files.tools

    print("=== TEST 1: Retrieve System Statistics ===")
    response = await agent.process_message("test_user", "test_session", "What is the current system stats?")
    print("\nFINAL RESPONSE:\n", response)

if __name__ == "__main__":
    asyncio.run(test_fallback())
