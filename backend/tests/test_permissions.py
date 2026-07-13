import pytest
import asyncio
from app.core.security.confirmation import ConfirmationManager

@pytest.mark.asyncio
async def test_confirmation_manager_approval():
    manager = ConfirmationManager()
    
    # Run the confirmation request in a background task
    request_task = asyncio.create_task(manager.request_confirmation("user_123", "delete_file", {"path": "C:\\test.txt"}))
    
    # Give it a tiny moment to register the pending action
    await asyncio.sleep(0.01)
    
    # Resolve the pending action
    pending_actions = list(manager.store.pending_actions.keys())
    token = pending_actions[0] if pending_actions else None
    manager.store.resolve_action(token, True)
    
    result = await request_task
    assert result is True
    assert len(manager.store.pending_actions) == 0

@pytest.mark.asyncio
async def test_confirmation_manager_denial():
    manager = ConfirmationManager()
    
    request_task = asyncio.create_task(manager.request_confirmation("user_123", "shutdown_system", "{}"))
    await asyncio.sleep(0.01)
    
    pending_actions = list(manager.store.pending_actions.keys())
    token = pending_actions[0] if pending_actions else None
    manager.store.resolve_action(token, False)
    
    approved = await request_task
    assert approved is False
