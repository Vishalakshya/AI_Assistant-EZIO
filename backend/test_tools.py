import httpx
import asyncio
import json

async def check_tools():
    url = "http://127.0.0.1:8000/api/v1/tools/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            tools = data.get("tools", [])
            print(f"Status Code: {response.status_code}")
            print(f"Total Tools Registered: {len(tools)}")
            for tool in tools:
                print(f" - {tool['function']['name']}")
        except Exception as e:
            print(f"Error fetching tools: {e}")

if __name__ == "__main__":
    asyncio.run(check_tools())
