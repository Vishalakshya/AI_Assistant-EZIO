import httpx
import asyncio

async def run_tests():
    url = "http://127.0.0.1:8000/api/v1/chat/message"
    
    commands = [
        "Open notepad",
        "Search for test files in the current folder",
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for cmd in commands:
            print(f"\nSending command: {cmd}")
            try:
                response = await client.post(url, json={"message": cmd})
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
