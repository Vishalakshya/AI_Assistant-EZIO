import asyncio
from app.core.orchestrator.agent import AgentOrchestrator
from app.core.tools.manager import ToolManager
from app.core.llm.ollama_provider import OllamaProvider
import logging

logging.basicConfig(level=logging.INFO)

async def test_end_to_end():
    # Force use Ollama provider
    llm = OllamaProvider()
    tools = ToolManager()
    agent = AgentOrchestrator(llm_provider=llm, tool_manager=tools)
    
    # We need an application context to register the tools, so import them
    import app.tools.system.tools
    import app.tools.apps.tools
    import app.tools.browser.tools
    import app.tools.files.tools

    tests = [
        ("Test 1: System Stats", "What is the current system stats?"),
        ("Test 2: Open Notepad", "Can you open Notepad for me?"),
        ("Test 3: Search Files", "Search for files named 'readme' in my documents folder."),
        ("Test 4: Read Document", "Read the document at C:\\Windows\\win.ini")
    ]
    
    for name, prompt in tests:
        print(f"\n{'='*50}\n{name}\n{'='*50}")
        response = await agent.process_message("test_user", "test_session", prompt)
        print("\nFINAL RESPONSE:\n", str(response).encode('cp1252', errors='replace').decode('cp1252'))

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
