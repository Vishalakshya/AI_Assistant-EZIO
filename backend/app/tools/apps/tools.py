from app.core.tools.registry import registry
from app.core.tools.schemas import ToolMetadata, ToolPermissions, ToolContext
from app.tools.apps.controller import WindowsAppController, WindowsWindowManager

app_controller = WindowsAppController()
window_manager = WindowsWindowManager()

@registry.register(ToolMetadata(
    name="open_application",
    description="Opens an application on the user's computer.",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Name of the app (e.g., 'chrome', 'vs code')"}
        },
        "required": ["app_name"]
    },
    permissions=ToolPermissions(tier=1)
))
async def open_application(app_name: str, context: ToolContext) -> str:
    success = app_controller.open_application(app_name)
    if success:
        return f"Successfully requested to open {app_name}."
    return f"Failed to open {app_name}."

@registry.register(ToolMetadata(
    name="close_application",
    description="Closes a running application. Use force=True only if the app is frozen or user explicitly requests force quit.",
    parameters={
        "type": "object",
        "properties": {
            "app_name": {"type": "string"},
            "force": {"type": "boolean", "default": False}
        },
        "required": ["app_name"]
    },
    permissions=ToolPermissions(tier=3, requires_confirmation=True) # Dangerous: closing work
))
async def close_application(app_name: str, force: bool, context: ToolContext) -> str:
    success = app_controller.close_application(app_name, force)
    if success:
        return f"Successfully closed {app_name}."
    return f"Could not find or close {app_name}."

@registry.register(ToolMetadata(
    name="focus_window",
    description="Brings a specific window to the foreground.",
    parameters={
        "type": "object",
        "properties": {
            "window_title": {"type": "string", "description": "Partial title of the window."}
        },
        "required": ["window_title"]
    },
    permissions=ToolPermissions(tier=2) # Moderate: interrupts user
))
async def focus_window(window_title: str, context: ToolContext) -> str:
    success = window_manager.focus_window(window_title)
    if success:
        return f"Brought '{window_title}' to the foreground."
    return f"Could not find window matching '{window_title}'."
    
@registry.register(ToolMetadata(
    name="get_running_processes",
    description="Returns a list of currently running processes and their resource usage.",
    parameters={"type": "object", "properties": {}},
    permissions=ToolPermissions(tier=1)
))
async def get_running_processes(context: ToolContext) -> str:
    processes = app_controller.get_running_processes()
    # Format to string summary to save tokens
    summary = "\n".join([f"{p['name']} (PID: {p['pid']}) - CPU: {p.get('cpu_percent', 0)}% MEM: {p.get('memory_percent', 0):.1f}%" for p in processes[:15]])
    return f"Top 15 Processes by Memory:\n{summary}"
