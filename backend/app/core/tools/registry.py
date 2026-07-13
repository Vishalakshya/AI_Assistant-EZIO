from typing import Callable, Dict, List
from app.core.tools.schemas import ToolMetadata

class ToolRegistry:
    """
    Holds all available tools and their metadata.
    Model-agnostic.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata):
        """Decorator to register a tool."""
        def decorator(func: Callable):
            self._tools[metadata.name] = func
            self._metadata[metadata.name] = metadata
            return func
        return decorator

    def get_tool(self, name: str) -> Callable:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found in registry.")
        return self._tools[name]

    def get_metadata(self, name: str) -> ToolMetadata:
        return self._metadata[name]

    def get_all_schemas(self) -> List[Dict]:
        """Returns schemas formatted for OpenAI function calling."""
        schemas = []
        for meta in self._metadata.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": meta.name,
                    "description": meta.description,
                    "parameters": meta.parameters
                }
            })
        return schemas

# Global Registry Instance
registry = ToolRegistry()
