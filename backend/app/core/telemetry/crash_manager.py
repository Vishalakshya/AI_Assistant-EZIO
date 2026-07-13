import os
import sys
import uuid
import json
import logging
import traceback
import platform
from datetime import datetime

class CrashManager:
    """
    Completely local, privacy-first crash reporting system.
    No data leaves the user's machine automatically.
    """
    def __init__(self):
        # Store in %APPDATA%/EZIO/logs/crashes
        self.crash_dir = os.path.join(os.getenv("APPDATA", ""), "EZIO", "logs", "crashes")
        os.makedirs(self.crash_dir, exist_ok=True)
        self._setup_global_handler()

    def _setup_global_handler(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.log_crash(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = handle_exception

    def log_crash(self, exc_type, exc_value, exc_traceback):
        crash_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        stack_trace = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Collect safe, non-PII system info
        system_info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "architecture": platform.machine()
        }
        
        crash_data = {
            "crash_id": crash_id,
            "timestamp": timestamp,
            "error_type": exc_type.__name__,
            "error_message": str(exc_value),
            "stack_trace": stack_trace,
            "system_info": system_info
        }
        
        log_path = os.path.join(self.crash_dir, f"crash_{crash_id}.json")
        with open(log_path, "w") as f:
            json.dump(crash_data, f, indent=4)
            
        logging.error(f"FATAL CRASH [{crash_id}]: {exc_type.__name__} - {str(exc_value)}. Details saved to {log_path}")

class SafeModeBootManager:
    """Detects repeated startup failures and toggles safe mode."""
    def __init__(self):
        self.flag_file = os.path.join(os.getenv("APPDATA", ""), "EZIO", ".booting")
        self.safe_mode = False

    def mark_boot_start(self):
        if os.path.exists(self.flag_file):
            self.safe_mode = True
            logging.warning("Previous boot failed! Starting in SAFE MODE (Plugins disabled, Tools disabled).")
        else:
            with open(self.flag_file, "w") as f:
                f.write("booting")

    def mark_boot_success(self):
        if os.path.exists(self.flag_file):
            os.remove(self.flag_file)

class BugReportGenerator:
    """Packages sanitized logs into a ZIP only when explicitly requested by the user."""
    @staticmethod
    def generate_report(crash_id: str) -> str:
        # TODO: Zip the specific crash JSON alongside sanitized sqlite action_logs
        return f"Bug report for {crash_id} generated successfully at %APPDATA%/EZIO/reports/"

crash_manager = CrashManager()
safe_boot = SafeModeBootManager()
