import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websocket.manager import confirm_manager
from app.core.security.confirmation import confirmation_manager

router = APIRouter()

@router.websocket("/ws/confirmations")
async def websocket_confirmation_endpoint(websocket: WebSocket, client_id: str = "local_user_001"):
    await confirm_manager.connect(websocket, client_id)
    try:
        while True:
            # 1. Listen for Approval/Rejection payloads from React UI
            data = await websocket.receive_json()
            
            token = data.get("token")
            approved = data.get("approved", False)
            
            if token:
                # 2. Unpause the Orchestrator's PendingActionStore
                confirmation_manager.store.resolve_action(token, approved)
                
                await confirm_manager.send_personal_message({
                    "type": "ACTION_RESOLVED",
                    "token": token,
                    "status": "APPROVED" if approved else "REJECTED"
                }, client_id)

    except WebSocketDisconnect:
        confirm_manager.disconnect(client_id)
