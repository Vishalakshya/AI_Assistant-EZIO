import logging
from fastapi import FastAPI
from app.api.middleware import setup_middlewares
# We will import routers here shortly as we build them out

logging.basicConfig(level=logging.INFO)

import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("LIFESPAN START")

    # Create tables if they don't exist (works inside running event loop)
    from app.db.session import engine, Base
    import app.db.models  # noqa: F401 — ensure all models are loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables ensured.")

    print("IMPORTING TOOLS")
    import app.tools.system.tools
    import app.tools.apps.tools
    import app.tools.browser.tools
    import app.tools.files.tools
    print("TOOLS IMPORTED")
    
    from app.core.tools.registry import registry
    schemas = registry.get_all_schemas()
    logging.info(f"Successfully registered {len(schemas)} tools:")
    for schema in schemas:
        logging.info(f"  - {schema['function']['name']}")
        
    print("LIFESPAN DONE")
    yield

app = FastAPI(
    title="EZIO Desktop Assistant API",
    description="The Presentation Layer for the EZIO AI Orchestrator.",
    version="1.0.0",
    lifespan=lifespan
)

setup_middlewares(app)

@app.get("/")
async def root():
    return {"message": "EZIO Backend is running."}

from app.api.v1.chat import router as chat_router
from app.api.v1.memory import router as memory_router
from app.api.v1.tools import router as tools_router
from app.api.websocket.chat_socket import router as chat_ws_router
from app.api.websocket.confirm_socket import router as confirm_ws_router
from app.api.websocket.voice_socket import router as voice_ws_router

app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(tools_router, prefix="/api/v1/tools", tags=["Tools"])
app.include_router(chat_ws_router, tags=["WebSockets"])
app.include_router(confirm_ws_router, tags=["WebSockets"])
app.include_router(voice_ws_router, tags=["WebSockets"])
