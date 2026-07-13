import asyncio
from typing import List, Dict
from playwright.async_api import async_playwright, Page, BrowserContext
from app.core.interfaces.base import BrowserControllerInterface

class PlaywrightBrowserController(BrowserControllerInterface):
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context: BrowserContext = None
        self._page: Page = None
        self._lock = asyncio.Lock()

    async def _ensure_started(self):
        async with self._lock:
            if not self._playwright:
                self._playwright = await async_playwright().start()
                # Run headful for desktop assistant visibility, but could be headless
                self._browser = await self._playwright.chromium.launch(headless=False)
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()

    async def navigate(self, url: str) -> bool:
        await self._ensure_started()
        try:
            # Ensure URL is fully formed
            if not url.startswith("http"):
                url = "https://" + url
            await self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            return True
        except Exception:
            return False

    async def extract_text(self) -> str:
        await self._ensure_started()
        try:
            # Extract main readable text from the body, stripping out scripts/styles
            text = await self._page.evaluate('''() => {
                const elements = document.body.querySelectorAll('script, style, noscript');
                for (const el of elements) el.remove();
                return document.body.innerText;
            }''')
            # Truncate to avoid LLM context overflow
            return text[:8000] if text else "No text found on page."
        except Exception as e:
            return f"Failed to extract text: {e}"

    async def search_google(self, query: str) -> List[Dict[str, str]]:
        await self._ensure_started()
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            await self._page.goto(search_url, wait_until="domcontentloaded")
            
            # Simple heuristic to grab top search results
            results = await self._page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('.yuRUbf a'));
                return links.slice(0, 5).map(a => ({
                    title: a.querySelector('h3') ? a.querySelector('h3').innerText : 'No Title',
                    url: a.href
                }));
            }''')
            return results
        except Exception:
            return []

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
