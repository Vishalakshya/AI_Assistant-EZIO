import pytest
from unittest.mock import MagicMock
from app.core.orchestrator.agent import AgentOrchestrator
from app.core.tools.schemas import ToolResult

async def mock_stream_response(*args, **kwargs):
    yield {"content": "Notepad has been opened."}

@pytest.mark.asyncio
async def test_orchestrator_fast_path(mocker):
    """Verify that deterministic commands (like open calculator) bypass the LLM completely."""
    mock_llm = mocker.AsyncMock()
    mock_tools = MagicMock()
    
    mock_tools.execute_tool_call = mocker.AsyncMock(return_value=ToolResult(
        tool_name="open_application",
        status="success",
        output="Opened notepad"
    ))

    orchestrator = AgentOrchestrator(llm_provider=mock_llm, tool_manager=mock_tools)

    # "Open Notepad" should go through FastRouter, execute the tool, and format response in Python
    response = await orchestrator.process_message("user_123", "sess_1", "Open Notepad")

    assert "opened" in response.lower()
    assert "notepad" in response.lower()
    # LLM is never called
    assert mock_llm.stream_response.call_count == 0
    mock_tools.execute_tool_call.assert_called_once_with("open_application", {"app_name": "Notepad"}, mocker.ANY)

@pytest.mark.asyncio
async def test_orchestrator_llm_synthesis_path(mocker):
    """Verify that tools requiring LLM formatting execute the tool, then call LLM once."""
    mock_llm = mocker.Mock()
    mock_llm.stream_response = mock_stream_response
    mock_tools = MagicMock()
    
    mock_tools.execute_tool_call = mocker.AsyncMock(return_value=ToolResult(
        tool_name="browser_search",
        status="success",
        output="Search results for OpenAI"
    ))

    orchestrator = AgentOrchestrator(llm_provider=mock_llm, tool_manager=mock_tools)

    # "Search Google for OpenAI" matches browser_search (requires LLM formatting)
    response = await orchestrator.process_message("user_123", "sess_1", "Search Google for OpenAI")

    assert response == "Notepad has been opened."
    mock_tools.execute_tool_call.assert_called_once_with("browser_search", {"query": "OpenAI"}, mocker.ANY)
