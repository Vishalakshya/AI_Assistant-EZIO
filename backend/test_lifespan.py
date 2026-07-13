import asyncio
from app.main import lifespan
import traceback

async def test():
    try:
        async with lifespan(None):
            print('lifespan ok')
    except Exception as e:
        print("ERROR IN LIFESPAN:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
