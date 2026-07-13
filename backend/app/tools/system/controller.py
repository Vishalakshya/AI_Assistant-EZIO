import subprocess
import psutil
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from typing import Dict, Any
from app.core.interfaces.base import SystemControllerInterface

class WindowsSystemController(SystemControllerInterface):
    def set_volume(self, level: int) -> bool:
        if not 0 <= level <= 100:
            return False
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            # Level is 0 to 100, pycaw expects a scalar 0.0 to 1.0
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return True
        except Exception:
            return False

    def set_brightness(self, level: int) -> bool:
        if not 0 <= level <= 100:
            return False
        try:
            sbc.set_brightness(level)
            return True
        except Exception:
            return False

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "Desktop/Unknown"
        }

    def toggle_wifi(self, enable: bool) -> bool:
        # Note: Toggling wifi via netsh requires Admin privileges on modern Windows
        # We simulate the call structure here.
        state = "enable" if enable else "disable"
        try:
            # We assume Wi-Fi interface name is 'Wi-Fi'
            subprocess.run(
                ["netsh", "interface", "set", "interface", "name=Wi-Fi", f"admin={state}"],
                capture_output=True, check=True
            )
            return True
        except Exception:
            return False

class CameraPermissionManager:
    """
    Tier 2 Specific Manager handling privacy requirements for webcam access.
    """
    def __init__(self):
        # In-memory mock. In production, this queries SQLite `tool_permissions`
        self._approved_users = set()

    def has_permission(self, user_id: str) -> bool:
        return user_id in self._approved_users

    def grant_permission(self, user_id: str):
        self._approved_users.add(user_id)
        # TODO: Write to audit log

    def revoke_permission(self, user_id: str):
        self._approved_users.discard(user_id)

camera_permissions = CameraPermissionManager()
sys_controller = WindowsSystemController()
