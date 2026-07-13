import keyring
from typing import Optional
from app.core.security.credentials import CredentialManagerInterface

class WindowsCredentialManager(CredentialManagerInterface):
    """
    Leverages the native Windows Credential Manager to securely encrypt and isolate API keys.
    The service name dictates the grouping in the Windows OS vault.
    """
    SERVICE_PREFIX = "EZIO_AI_"

    def _format_service_name(self, provider: str) -> str:
        return f"{self.SERVICE_PREFIX}{provider.upper()}"

    def set_key(self, provider: str, user_id: str, secret_key: str) -> bool:
        try:
            service = self._format_service_name(provider)
            keyring.set_password(service, user_id, secret_key)
            return True
        except Exception:
            return False

    def get_key(self, provider: str, user_id: str) -> Optional[str]:
        try:
            service = self._format_service_name(provider)
            return keyring.get_password(service, user_id)
        except Exception:
            return None

    def delete_key(self, provider: str, user_id: str) -> bool:
        try:
            service = self._format_service_name(provider)
            keyring.delete_password(service, user_id)
            return True
        except Exception:
            # keytar throws exception if not found, we handle gracefully
            return False

credential_manager = WindowsCredentialManager()
