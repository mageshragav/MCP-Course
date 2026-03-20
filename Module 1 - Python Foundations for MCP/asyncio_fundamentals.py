import asyncio
import os
import time

# ============== SYNCHRONOUS (Blocking) ==============
def sync_fetch_data(id, delay):
    """Synchronous - blocks execution"""
    print(f" Sync: Starting task {id}")
    time.sleep(delay)  # BLOCKS everything
    print(f" Sync: Task {id} complete")
    return f"Data-{id}"

# ============== ASYNCHRONOUS (Non-Blocking) ==============
async def async_fetch_data(id, delay):
    """Asynchronous - allows other tasks to run"""
    print(f" Async: Starting task {id}")
    await asyncio.sleep(delay)  # NON-BLOCKING
    print(f" Async: Task {id} complete")
    return f"Data-{id}"

# ============== RUNNING ASYNC CODE ==============
async def main():
    """Main async function"""
    # Run tasks sequentially
    result1 = await async_fetch_data(1, 1)
    result2 = await async_fetch_data(2, 1)
  
    # Run tasks concurrently (MCP uses this!)
    results = await asyncio.gather(
        async_fetch_data(3, 1),
        async_fetch_data(4, 1),
        async_fetch_data(5, 1)
    )
    return results

# ============== ASYNC CONTEXT MANAGERS ==============
class AsyncConnection:
    """Async context manager for connections"""
    async def __aenter__(self):
        print(" Connecting...")
        await asyncio.sleep(0.5)
        return self
  
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(" Disconnecting...")
        await asyncio.sleep(0.5)


async def use_connection():
    async with AsyncConnection() as conn:
        print(" Using connection...")

# ============== ASYNC GENERATORS ==============
async def async_data_stream():
    """Stream data asynchronously"""
    for i in range(5):
        await asyncio.sleep(0.5)
        yield f"Chunk-{i}"

async def consume_stream():
    async for chunk in async_data_stream():
        print(f" Received: {chunk}")

if __name__ == "__main__":
    print("=" * 50)
    print("ASYNCIO FUNDAMENTALS DEMO")
    print("=" * 50)
  
    print("\n1️ Sequential Async Tasks:")
    asyncio.run(main())
  
    print("\n2️ Async Context Manager:")
    asyncio.run(use_connection())
  
    print("\n3️ Async Generator:")
    asyncio.run(consume_stream())
