#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio import Queue, Future, get_event_loop


class Wrapper:
    val: int
    future: Future

    def __init__(self, val) -> None:
        self.val = val
        self.future = get_event_loop().create_future()


class Node:
    _queue: Queue

    def __init__(self, buffer_size: int = 64):
        self._queue = Queue(buffer_size)

    async def start(self):
        print("Start")
        asyncio.create_task(self.consume())

    def stop(self):
        pass

    async def consume(self):
        print("Consume")
        while True:
            val = await self._queue.get()
            print(f"Received: {val}")
            print(f"Queue size: {self._queue.qsize()}")
            val.future.set_result(val.val + 1)
            await asyncio.sleep(1)

    # async def send(self, value: int):
        # print(f"Send: {value}")
        # await self._queue.put(value)

    async def exec(self, value: int) -> int:
        print(f"Exec: {value}")
        wrapper = Wrapper(value)
        self._queue.put_nowait(wrapper)
        return await wrapper.future

    async def exec_nowait(self, value: int) -> Future:
        print(f"Aexec: {value}")
        wrapper = Wrapper(value)
        await self._queue.put(wrapper)
        return wrapper.future


async def main():
    node = Node()

    await node.start()

    futures = []
    for i in range(3):
        futures.append(await node.exec_nowait(i))

    await asyncio.sleep(10)

    for future in futures:
        print(f"Result: {await future}")


asyncio.run(main())
