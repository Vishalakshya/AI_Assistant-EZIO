import cv2
import mss
from app.core.tools.registry import registry
from app.core.tools.schemas import ToolMetadata, ToolPermissions, ToolContext
from app.tools.system.controller import WindowsSystemController, camera_permissions
from app.core.security.confirmation import confirmation_manager

sys_controller = WindowsSystemController()

@registry.register(ToolMetadata(
    name="get_system_stats",
    description="Returns current CPU, RAM, Battery, and Disk usage.",
    parameters={"type": "object", "properties": {}},
    permissions=ToolPermissions(tier=1)
))
async def get_system_stats(context: ToolContext) -> str:
    stats = sys_controller.get_system_stats()
    return f"CPU: {stats['cpu_percent']}%\nRAM: {stats['ram_percent']}%\nDisk: {stats['disk_percent']}%\nBattery: {stats['battery']}%"

@registry.register(ToolMetadata(
    name="set_volume",
    description="Sets the master volume (0-100).",
    parameters={
        "type": "object",
        "properties": {
            "level": {"type": "integer", "description": "Volume level from 0 to 100."}
        },
        "required": ["level"]
    },
    permissions=ToolPermissions(tier=2) # Moderate
))
async def set_volume(level: int, context: ToolContext) -> str:
    if sys_controller.set_volume(level):
        return f"Volume set to {level}%."
    return "Failed to set volume."

@registry.register(ToolMetadata(
    name="capture_camera",
    description="Takes a photo using the webcam. Used when user asks 'what do I look like' or 'take a picture'.",
    parameters={"type": "object", "properties": {}},
    permissions=ToolPermissions(tier=2) # Explicitly mapped to Tier 2 by user
))
async def capture_camera(context: ToolContext) -> str:
    # 1. Check Privacy Audit Log / Permissions
    if not camera_permissions.has_permission(context.user_id):
        # We manually invoke the confirmation manager for Tier 2 Privacy Escalation
        approved = await confirmation_manager.request_confirmation(
            context.user_id, "capture_camera", "First-time Camera Access Request"
        )
        if not approved:
            return "Camera access denied by user."
        camera_permissions.grant_permission(context.user_id)
        
    # 2. Execute via OpenCV
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            file_path = "latest_snapshot.jpg"
            cv2.imwrite(file_path, frame)
            return f"Photo captured successfully and saved to {file_path}."
        return "Failed to read from camera."
    except Exception as e:
        return f"Camera error: {e}"
