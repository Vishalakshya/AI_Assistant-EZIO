from app.core.tools.registry import registry
from app.core.tools.schemas import ToolMetadata, ToolPermissions, ToolContext
from app.tools.browser.controller import PlaywrightBrowserController

browser_controller = PlaywrightBrowserController()

@registry.register(ToolMetadata(
    name="browser_search",
    description="Searches Google and returns the top 5 URLs and titles.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    },
    permissions=ToolPermissions(tier=2) # Moderate: invokes web traffic
))
async def browser_search(query: str, context: ToolContext) -> str:
    results = await browser_controller.search_google(query)
    if not results:
        return f"No results found for '{query}'."
    
    formatted = []
    for r in results:
        formatted.append(f"- [{r['title']}]({r['url']})")
    return "Top Results:\n" + "\n".join(formatted)

@registry.register(ToolMetadata(
    name="browser_read_page",
    description="Navigates to a URL and extracts the main text content for reading.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    },
    permissions=ToolPermissions(tier=2)
))
async def browser_read_page(url: str, context: ToolContext) -> str:
    success = await browser_controller.navigate(url)
    if not success:
        return f"Failed to navigate to {url}."
        
    text = await browser_controller.extract_text()
    return text
