import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websocket.manager import voice_manager

router = APIRouter()

@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket, client_id: str = "local_user_001"):
    await voice_manager.connect(websocket, client_id)
    try:
        while True:
            # 1. Receive data (Supports both Binary PCM chunks and JSON fallback)
            message = await websocket.receive()
            
            if "bytes" in message:
                # Primary Route: Raw Binary Audio (e.g. 16kHz PCM from Microphone)
                audio_chunk = message["bytes"]
                
                # TODO: Feed chunk into Whisper streaming buffer
                # print(f"Received {len(audio_chunk)} bytes of audio.")
                
                # Mock: Stream TTS output bytes back
                # await voice_manager.send_binary(tts_audio_chunk, client_id)
                
            elif "text" in message:
                # Fallback Route: Base64 JSON
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "audio" and data.get("encoding") == "base64":
                        b64_data = data.get("data")
                        # TODO: Decode base64 and feed to Whisper
                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        voice_manager.disconnect(client_id)
