import re
from typing import Dict, Any, Optional, Tuple

class FastRouter:
    """
    Pure Python router for sub-millisecond classification and deterministic routing.
    Bypasses LLM classification and planning for common operating system operations.
    """
    def __init__(self):
        # Compiled regex patterns for speed
        self.open_app_pattern = re.compile(
            r"^\s*(?:open|launch|start|run)\s+(.+)$", re.IGNORECASE
        )
        self.close_app_pattern = re.compile(
            r"^\s*(?:close|exit|kill|terminate|stop)\s+(.+)$", re.IGNORECASE
        )
        self.volume_pattern = re.compile(
            r"^\s*(?:set\s+)?volume\s+(?:to\s+)?(\d+)\s*%?\s*$", re.IGNORECASE
        )
        self.volume_mute_pattern = re.compile(
            r"^\s*(?:mute|unmute|silence)\s*$", re.IGNORECASE
        )
        self.volume_direction_pattern = re.compile(
            r"^\s*(?:sound|speaker|volume)\s+(up|down)\s*$", re.IGNORECASE
        )
        self.system_stats_pattern = re.compile(
            r"\b(system\s*(stats|statistics|info|status)|cpu|ram|memory\s*usage|disk|battery)\b", re.IGNORECASE
        )
        self.camera_pattern = re.compile(
            r"\b(camera|webcam|take\s+(a\s+)?(photo|picture)|capture\s+(camera|photo|picture))\b", re.IGNORECASE
        )
        self.time_pattern = re.compile(
            r"\b(what\s+time\s+is\s+it|current\s+time|time\s+now|what\s+is\s+the\s+time)\b", re.IGNORECASE
        )
        self.search_files_pattern = re.compile(
            r"^\s*(?:search|find)\s+(?:for\s+)?files?\s*(?:named|called|with)?\s+(.+)$", re.IGNORECASE
        )
        self.search_downloads_pattern = re.compile(
            r"^\s*(?:search|find)\s+(?:in\s+)?downloads\s*(?:for)?\s*(.+)?$", re.IGNORECASE
        )
        self.browser_search_pattern = re.compile(
            r"^\s*(?:search\s+google\s+for|search\s+web\s+for|google\s+search\s+for|google\s+search|browser\s+search|search\s+for|google)\s+(.+)$", re.IGNORECASE
        )
        self.browser_read_pattern = re.compile(
            r"^\s*(?:read\s+page|goto|go\s+to|open\s+website|open\s+page)\s+(https?://[^\s]+)$", re.IGNORECASE
        )
        self.processes_pattern = re.compile(
            r"\b(running\s+processes|show\s+processes|list\s+processes|active\s+processes)\b", re.IGNORECASE
        )

        # Single word exact matches (common apps/commands)
        self.exact_apps = {
            "calculator": "Calculator",
            "calc": "Calculator",
            "notepad": "Notepad",
            "chrome": "Chrome",
            "edge": "Edge",
            "firefox": "Firefox",
            "terminal": "Terminal",
            "cmd": "cmd.exe",
            "powershell": "PowerShell",
        }

    def route(self, message: str) -> Optional[Tuple[str, Dict[str, Any], bool]]:
        """
        Routes the message to a tool if deterministic match is found.
        Returns:
            Tuple[tool_name, arguments, requires_llm_formatting] or None
        """
        cleaned = message.strip().lower()

        # 1. Exact single-word app matches
        if cleaned in self.exact_apps:
            return "open_application", {"app_name": self.exact_apps[cleaned]}, False

        # 2. Open Application
        m = self.open_app_pattern.match(message)
        if m:
            app_name = m.group(1).strip()
            # Normalize common apps
            app_lower = app_name.lower()
            if app_lower in ["calc", "calculator"]:
                app_name = "Calculator"
            elif app_lower == "notepad":
                app_name = "Notepad"
            elif app_lower == "chrome":
                app_name = "Chrome"
            elif app_lower == "edge":
                app_name = "Edge"
            return "open_application", {"app_name": app_name}, False

        # 3. Close Application
        m = self.close_app_pattern.match(message)
        if m:
            app_name = m.group(1).strip()
            return "close_application", {"app_name": app_name}, False

        # 4. Volume Control
        m = self.volume_pattern.match(message)
        if m:
            level = int(m.group(1))
            return "set_volume", {"level": level}, False

        if self.volume_mute_pattern.match(message):
            return "set_volume", {"level": 0}, False

        m = self.volume_direction_pattern.match(message)
        if m:
            direction = m.group(1).lower()
            # Let's map up to 50% / down to 10% or just standard levels
            level = 50 if direction == "up" else 10
            return "set_volume", {"level": level}, False

        # 5. System Stats
        if self.system_stats_pattern.search(message):
            return "get_system_stats", {}, False

        # 6. Capture Camera
        if self.camera_pattern.search(message):
            return "capture_camera", {}, False

        # 7. Time/Clock
        if self.time_pattern.search(message):
            return "clock", {}, False

        # 8. Running Processes
        if self.processes_pattern.search(message):
            return "get_running_processes", {}, False

        # 9. Search Files
        m = self.search_files_pattern.match(message)
        if m:
            query = m.group(1).strip()
            return "search_files", {"query": query}, True

        m = self.search_downloads_pattern.match(message)
        if m:
            query = m.group(1).strip() if m.group(1) else ""
            return "search_files", {"query": query}, True

        # 10. Browser Search
        m = self.browser_search_pattern.match(message)
        if m:
            query = m.group(1).strip()
            return "browser_search", {"query": query}, True

        # 11. Browser Read Page
        m = self.browser_read_pattern.match(message)
        if m:
            url = m.group(1).strip()
            return "browser_read_page", {"url": url}, True

        return None
