from app.core.tools.registry import registry
from app.core.tools.schemas import ToolMetadata, ToolPermissions, ToolContext
from app.tools.files.controller import WindowsFileSystem

fs_controller = WindowsFileSystem()

@registry.register(ToolMetadata(
    name="search_files",
    description="Searches for a file by name or extension.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Filename or extension to search for."},
            "path": {"type": "string", "description": "Specific folder to search in (optional)."},
            "recursive": {"type": "boolean", "default": True}
        },
        "required": ["query"]
    },
    permissions=ToolPermissions(tier=1) # Safe read-only
))
async def search_files(query: str, context: ToolContext, path: str = None, recursive: bool = True) -> str:
    files = fs_controller.search_files(query, path, recursive)
    if not files:
        return f"No files found matching '{query}'."
    return "Found files:\n" + "\n".join(files)

@registry.register(ToolMetadata(
    name="read_document",
    description="Reads the text content of a PDF, DOCX, or TXT file.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to the document."}
        },
        "required": ["file_path"]
    },
    permissions=ToolPermissions(tier=1) # Safe read-only
))
async def read_document(file_path: str, context: ToolContext) -> str:
    if file_path.lower().endswith(".pdf"):
        return fs_controller.read_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return fs_controller.read_docx(file_path)
    elif file_path.lower().endswith(".txt") or file_path.lower().endswith(".py") or file_path.lower().endswith(".js"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read up to 10k chars to prevent token overflow
                return f.read(10000) 
        except Exception as e:
            return f"Error reading text file: {e}"
    else:
        return "Unsupported file format. Please use PDF, DOCX, or plain text."

@registry.register(ToolMetadata(
    name="delete_file",
    description="Deletes a file or directory permanently.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Absolute path to the file."}
        },
        "required": ["file_path"]
    },
    permissions=ToolPermissions(tier=3, requires_confirmation=True) # Dangerous action
))
async def delete_file(file_path: str, context: ToolContext) -> str:
    success = fs_controller.delete_file(file_path)
    if success:
        return f"Successfully deleted {file_path}."
    return f"Failed to delete {file_path}. It may not exist or is in use."
