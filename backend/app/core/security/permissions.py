from typing import Tuple

class PermissionManager:
    """
    Manages Tiered Permissions for Tool Execution.
    """
    async def check_permission(self, user_id: str, tool_name: str, tier: int) -> Tuple[bool, str]:
        """
        Checks if a user is allowed to execute a tool.
        Returns: (is_approved, reason_or_status)
        """
        # In a real app, we'd query the SQLite DB: SELECT confirmation_required FROM tool_permissions
        # For now, we enforce hardcoded tiers
        if tier == 1:
            return True, "Safe action."
            
        elif tier == 2:
            # Check global 'ALLOW_MODERATE_ACTIONS' setting
            return True, "Moderate action allowed."
            
        elif tier == 3:
            # Tier 3 MUST invoke the WebSocket confirmation loop
            return False, "CONFIRMATION_REQUIRED"
            
        return False, "Unknown tier."

permission_manager = PermissionManager()
