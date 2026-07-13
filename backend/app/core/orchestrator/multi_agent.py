from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Base Interface for Future Multi-Agent Support.
    """
    @abstractmethod
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class CoordinatorAgent(BaseAgent):
    """
    Future router agent to dispatch tasks to specialized sub-agents.
    """
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Future Implementation")

class BrowserAgent(BaseAgent):
    """
    Specialized agent handling complex Playwright navigation.
    """
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Future Implementation")
