import asyncio
from typing import Any, Callable


async def run_in_thread(sync_call: Callable) -> Any:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_call)
