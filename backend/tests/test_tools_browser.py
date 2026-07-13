import pytest
from app.tools.browser.tools import browser_controller as playwright_controller

@pytest.mark.asyncio
async def test_browser_search(mocker):
    # We don't want to actually launch Chromium in CI unit tests
    mock_page = mocker.AsyncMock()
    mock_page.title.return_value = "Test Results"
    mock_page.evaluate.return_value = "Search Results Data"
    mock_page.content.return_value = "<html><body>Search Results Data</body></html>"
    
    mock_context = mocker.AsyncMock()
    mock_context.new_page.return_value = mock_page
    
    mock_browser = mocker.AsyncMock()
    mock_browser.new_context.return_value = mock_context
    
    # Mock the internal initialization
    mocker.patch.object(playwright_controller, '_ensure_started', new_callable=mocker.AsyncMock)
    playwright_controller._browser = mock_browser
    playwright_controller._page = mock_page

    # Test
    await playwright_controller.navigate("https://example.com")
    html_content = await playwright_controller.extract_text()
    
    assert "Search Results Data" in html_content
    mock_page.goto.assert_called_once_with("https://example.com", wait_until="domcontentloaded", timeout=15000)
