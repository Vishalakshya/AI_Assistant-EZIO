import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.db.session import AsyncSessionLocal, engine, Base

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Setup test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Provide a transactional scope around a series of operations."""
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client():
    """FastAPI Test Client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
