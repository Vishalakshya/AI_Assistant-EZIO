import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_orchestrator, get_current_user_id
from app.core.orchestrator.agent import AgentOrchestrator

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Submits a message to the Agent Orchestrator.
    This is the fallback standard REST endpoint. Real-time streaming occurs via WebSockets.
    """
    session_id = str(uuid.uuid4())
    
    # The orchestrator handles intent, memory injection, tool routing, and permissions
    final_response = await orchestrator.process_message(
        user_id=user_id,
        session_id=session_id,
        message=request.message
    )
    
    return ChatResponse(response=final_response, session_id=session_id)
