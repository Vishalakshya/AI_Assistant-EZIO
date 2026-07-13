import pytest
from unittest.mock import AsyncMock, patch
from app.tools.apps.tools import open_application, close_application

@pytest.mark.asyncio
async def test_open_application_success(mocker):
    # Mock subprocess.Popen to prevent actually opening apps during test
    mock_popen = mocker.patch("subprocess.Popen")
    mock_popen.return_value = AsyncMock()
    
    result = await open_application("notepad", context=None)
    
    assert "Successfully" in result or "opened" in result.lower()
    mock_popen.assert_called_once()

@pytest.mark.asyncio
async def test_close_application_success(mocker):
    # Mock psutil iteration
    mock_process = mocker.MagicMock()
    mock_process.info = {'name': 'notepad.exe', 'pid': 1234}
    mock_process.terminate = mocker.MagicMock()
    
    mocker.patch("psutil.process_iter", return_value=[mock_process])
    
    result = await close_application("notepad", force=False, context=None)
    
    assert "Successfully" in result or "closed" in result.lower()
    mock_process.terminate.assert_called_once()

@pytest.mark.asyncio
async def test_close_application_not_found(mocker):
    mocker.patch("psutil.process_iter", return_value=[])
    
    result = await close_application("chrome", force=False, context=None)
    
    assert "Could not" in result or "not found" in result.lower()
