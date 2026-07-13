from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# --- Application Interfaces ---

class WindowManagerInterface(ABC):
    @abstractmethod
    def focus_window(self, window_title: str) -> bool: pass
    
    @abstractmethod
    def minimize_window(self, window_title: str) -> bool: pass
    
    @abstractmethod
    def maximize_window(self, window_title: str) -> bool: pass

class AppControllerInterface(ABC):
    @abstractmethod
    def open_application(self, app_name: str) -> bool: pass
    
    @abstractmethod
    def close_application(self, app_name: str, force: bool = False) -> bool: pass
    
    @abstractmethod
    def get_running_processes(self) -> List[Dict[str, Any]]: pass
    
    @abstractmethod
    def get_installed_apps(self) -> List[str]: pass

# --- File Interfaces ---

class FileSystemInterface(ABC):
    @abstractmethod
    def search_files(self, query: str, path: str = None, recursive: bool = True) -> List[str]: pass
    
    @abstractmethod
    def move_file(self, source: str, destination: str) -> bool: pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> bool: pass

# --- System Interfaces ---

class SystemControllerInterface(ABC):
    @abstractmethod
    def set_volume(self, level: int) -> bool: pass
    
    @abstractmethod
    def set_brightness(self, level: int) -> bool: pass
    
    @abstractmethod
    def get_system_stats(self) -> Dict[str, Any]: pass
    
    @abstractmethod
    def toggle_wifi(self, enable: bool) -> bool: pass

# --- Browser Interfaces ---

class BrowserControllerInterface(ABC):
    @abstractmethod
    async def navigate(self, url: str) -> bool: pass
    
    @abstractmethod
    async def extract_text(self) -> str: pass
    
    @abstractmethod
    async def search_google(self, query: str) -> List[Dict[str, str]]: pass
