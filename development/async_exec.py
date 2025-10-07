#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Execution Pattern Prototype

Explores producer-consumer patterns with Future-based result handling.
Demonstrates non-blocking task submission with async result retrieval,
useful for network operations where response timing is unpredictable.
"""
import asyncio
from asyncio import Queue, Future, get_event_loop


class Wrapper:
    """
    Task container with Future-based result coordination.
    
    Enables async submission of work items while maintaining result correlation.
    The Future pattern allows callers to await results without blocking the
    producer-consumer pipeline.
    """
    val: int
    future: Future

    def __init__(self, val) -> None:
        self.val = val
        # Future enables async result retrieval after processing
        self.future = get_event_loop().create_future()


class Node:
    """
    Async task processor with queue-based work distribution.
    
    Demonstrates decoupling of task submission from execution timing.
    Useful pattern for network operations where processing speed varies
    and backpressure management is critical.
    """
    _queue: Queue

    def __init__(self, buffer_size: int = 64):
        # Buffer size controls backpressure - prevents memory exhaustion
        self._queue = Queue(buffer_size)

    async def start(self):
        print("Start")
        # Background consumer prevents blocking the submission path
        asyncio.create_task(self.consume())

    def stop(self):
       
        pass

    async def consume(self):
        """
        Background worker that processes queued tasks sequentially.
        
        Simulates slow operations (network calls, device responses) while
        maintaining async coordination with callers via Futures.
        """
        print("Consume")
        while True:
            val = await self._queue.get()
            print(f"Received: {val}")
            print(f"Queue size: {self._queue.qsize()}")
            # Simulate processing and return result via Future
            val.future.set_result(val.val + 1)
            await asyncio.sleep(1)  # Simulates slow network operation

    # EXPERIMENTAL: Direct queue access - removed in favor of exec pattern
    # async def send(self, value: int):
        # print(f"Send: {value}")
        # await self._queue.put(value)

    async def exec(self, value: int) -> int:
        """Blocking submission - waits for result before returning."""
        print(f"Exec: {value}")
        wrapper = Wrapper(value)
        self._queue.put_nowait(wrapper)  # May raise QueueFull if buffer exceeded
        return await wrapper.future

    async def exec_nowait(self, value: int) -> Future:
        """
        Non-blocking submission pattern for concurrent operations.
        
        Returns Future immediately, allowing caller to manage timing and
        coordination. Useful for batch operations where results can be
        collected asynchronously.
        """
        print(f"Aexec: {value}")
        wrapper = Wrapper(value)
        await self._queue.put(wrapper)  # Respects backpressure
        return wrapper.future


async def main():
    """
    Demonstration of concurrent task submission with async result collection.
    
    Shows how multiple operations can be submitted rapidly while results
    are processed at their own pace - critical for network automation
    where device response times vary significantly.
    """
    node = Node()

    await node.start()

    # Submit all tasks quickly without waiting for individual results
    futures = []
    for i in range(3):
        futures.append(await node.exec_nowait(i))

    # Simulate other work while background processing continues
    await asyncio.sleep(10)

    # Collect results when ready - demonstrates flexible timing control
    for future in futures:
        print(f"Result: {await future}")


# Development prototype - demonstrates async patterns for network operations
asyncio.run(main())
