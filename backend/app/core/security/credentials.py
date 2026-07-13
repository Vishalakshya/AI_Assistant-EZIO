from abc import ABC, abstractmethod
from typing import Optional

class CredentialManagerInterface(ABC):
    @abstractmethod
    def set_key(self, provider: str, user_id: str, secret_key: str) -> bool:
        """Securely store an API key."""
        pass
        
    @abstractmethod
    def get_key(self, provider: str, user_id: str) -> Optional[str]:
        """Retrieve a stored API key."""
        pass
        
    @abstractmethod
    def delete_key(self, provider: str, user_id: str) -> bool:
        """Securely delete a stored API key."""
        pass
