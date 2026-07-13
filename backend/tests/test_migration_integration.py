import pytest
from fastapi.testclient import TestClient
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.main import app
from app.db.session import DATABASE_URL

async def mock_stream_response(*args, **kwargs):
    yield {"content": "I have successfully processed your request."}

@pytest.mark.asyncio
async def test_clean_clone_answers_first_request(mocker):
    """
    Verify that the application can start up and serve a chat request
    without crashing due to missing database tables.
    The database is created wherever session.py configures it (APPDATA).
    """
    # Patch the stream_response method on the dependency injected LLM provider
    mock_stream = mocker.patch("app.api.dependencies._orchestrator.llm.stream_response")
    mock_stream.side_effect = mock_stream_response

    # Use TestClient to trigger the FastAPI lifespan
    with TestClient(app) as client:
        response = client.post("/api/v1/chat/message", json={"message": "Hello, my name is Alice."})

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert mock_stream.called

    # Verify tables exist by querying the real database
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        from sqlalchemy import text
        result = await conn.execute(text("SELECT count(*) FROM memories"))
        count = result.scalar()
        assert count is not None

    await engine.dispose()
