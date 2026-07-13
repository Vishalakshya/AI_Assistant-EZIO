import os
import psutil
import subprocess
import win32gui
import win32con
import win32process
from typing import List, Dict, Any
from app.core.interfaces.base import AppControllerInterface, WindowManagerInterface

class WindowsWindowManager(WindowManagerInterface):
    def _find_window(self, window_title: str) -> int:
        hwnd_list = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                hwnd_list.append(hwnd)
        win32gui.EnumWindows(callback, None)
        return hwnd_list[0] if hwnd_list else 0

    def focus_window(self, window_title: str) -> bool:
        hwnd = self._find_window(window_title)
        if hwnd:
            try:
                # Sometimes needs to attach thread input
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
            except Exception:
                return False
        return False

    def minimize_window(self, window_title: str) -> bool:
        hwnd = self._find_window(window_title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        return False

    def maximize_window(self, window_title: str) -> bool:
        hwnd = self._find_window(window_title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        return False

class WindowsAppController(AppControllerInterface):
    # Common Windows shortcuts / execution names
    APP_ALIASES = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "vs code": "code",
        "cursor": "cursor",
        "discord": "Update.exe --processStart Discord.exe", # Typical discord launch
        "spotify": "spotify.exe",
        "notepad": "notepad.exe",
        "terminal": "wt.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
    }

    def open_application(self, app_name: str) -> bool:
        command = self.APP_ALIASES.get(app_name.lower(), app_name)
        try:
            # Use start to utilize Windows path resolution
            subprocess.Popen(f"start {command}", shell=True)
            return True
        except Exception:
            return False

    def close_application(self, app_name: str, force: bool = False) -> bool:
        target_name = self.APP_ALIASES.get(app_name.lower(), app_name)
        if target_name.endswith(".exe"):
            proc_name = target_name
        else:
            proc_name = f"{target_name}.exe"
            
        closed_any = False
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] and proc.info['name'].lower() == proc_name.lower():
                try:
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    closed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return closed_any

    def get_running_processes(self) -> List[Dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            if proc.info['name']: # Filter out empty
                processes.append(proc.info)
        # Sort by memory usage
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        return processes[:50] # Return top 50 to avoid massive payloads

    def get_installed_apps(self) -> List[str]:
        # Typically requires querying HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
        # Simplified for brevity here via PowerShell or pre-compiled list
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-AppxPackage | Select-Object -ExpandProperty Name"],
                capture_output=True, text=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except Exception:
            return []
