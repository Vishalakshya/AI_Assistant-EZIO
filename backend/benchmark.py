import asyncio
import time
import httpx

async def test_endpoint(prompt: str):
    print(f"\n==============================================")
    print(f"Testing Prompt: '{prompt}'")
    print(f"==============================================")
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/chat/message",
                json={"content": prompt}
            )
            data = response.json()
            end_time = time.time()
            latency = end_time - start_time
            print(f"Latency: {latency:.2f} seconds")
            print(f"Response: {data.get('response', 'No response field')}")
            return latency
        except Exception as e:
            print(f"Error: {e}")
            return None

async def run_benchmarks():
    print("Waiting for server to start...")
    await asyncio.sleep(5)
    
    # 1. System Request (Should bypass LLM Layer 2)
    t1 = await test_endpoint("What are my system stats?")
    
    # 2. Web Search Request (Should trigger Playwright browser)
    t2 = await test_endpoint("Search the web for the latest python version.")
    
    # 3. Simple Chat (Should bypass Tool Execution)
    t3 = await test_endpoint("Hello! Who are you?")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
