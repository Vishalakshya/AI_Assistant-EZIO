import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.websocket.manager import chat_manager
from app.api.dependencies import get_orchestrator, get_current_user_id

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str = "local_user_001"):
    await chat_manager.connect(websocket, client_id)
    
    # Normally we inject the orchestrator via Depends in HTTP, but WS requires manual resolution
    from app.api.dependencies import _orchestrator
    
    try:
        while True:
            # Wait for user input
            data = await websocket.receive_text()
            
            # 1. Send Thinking state
            await chat_manager.send_personal_message({"type": "THINKING", "message": "Analyzing intent..."}, client_id)
            
            try:
                # 2. Invoke Orchestrator stream generator
                async for event_type, event_data in _orchestrator.stream_message(client_id, "ws_session", data):
                    if event_type == "thinking":
                        await chat_manager.send_personal_message({
                            "type": "THINKING",
                            "message": event_data
                        }, client_id)
                    elif event_type == "stream_start":
                        await chat_manager.send_personal_message({
                            "type": "STREAM_START",
                            "message_id": event_data
                        }, client_id)
                    elif event_type == "token":
                        await chat_manager.send_personal_message({
                            "type": "TOKEN",
                            "content": event_data
                        }, client_id)
                    elif event_type == "final":
                        await chat_manager.send_personal_message({
                            "type": "FINAL_RESPONSE",
                            "content": event_data
                        }, client_id)
                
            except Exception as e:
                await chat_manager.send_personal_message({"type": "ERROR", "message": str(e)}, client_id)

    except WebSocketDisconnect:
        chat_manager.disconnect(client_id)
