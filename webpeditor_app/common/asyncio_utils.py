import asyncio
from typing import Awaitable


def complete[T](future: Awaitable[T]) -> T:
    return asyncio.get_event_loop().run_until_complete(future)
