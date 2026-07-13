import pytest
from app.core.memory.context_builder import memory_builder

@pytest.mark.asyncio
async def test_memory_context_builder(mocker):
    # Mock the database retrieval
    mock_crud = mocker.patch("app.core.memory.context_builder.crud_memory")
    
    # Mock returning some fake memories
    # The return should be a mock model with a .content attribute
    class MockMemory:
        def __init__(self, content):
            self.content = content
            
    mock_crud.search = mocker.AsyncMock(return_value=[
        MockMemory("User likes dark mode"),
        MockMemory("User works as a software engineer")
    ])
    
    context = await memory_builder.build_context("user_123", "What do I like?")
    
    assert "User likes dark mode" in context
    assert "User works as a software engineer" in context
    mock_crud.search.assert_called_once()
