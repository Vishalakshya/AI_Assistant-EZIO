import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Determine AppData directory
app_data = os.getenv('APPDATA')
if app_data:
    base_dir = Path(app_data) / "EZIO"
else:
    base_dir = Path.home() / ".ezio"

data_dir = base_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)
db_path = data_dir / "ezio.db"

# Load from environment or default to AppData SQLite
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("ENVIRONMENT") == "development",
    future=True,
    # Check_same_thread is needed for SQLite
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# AsyncSession factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db():
    """FastAPI Dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session
