#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import Dict, List
from netdriver.client.task import PullTask


class Merger:
    """ To merge same type pull task into one """
    _queue: asyncio.Queue
    _lock: asyncio.Lock
    _sleep_time: float
    _logger: any

    def __init__(self, queue_siz: int = 64):
        self._queue = asyncio.Queue(maxsize=queue_siz)
        self._lock = asyncio.Lock()

    async def enqueue(self, task: PullTask):
        """ Enqueue task
        :param task: PullTask
        """
        async with self._lock:
            task.set_enqueue_timestamp()
            self._queue.put_nowait(task)

    async def dequeue(self) -> PullTask:
        """ Dequeue task
        :return: PullTask
        """
        task: PullTask = await self._queue.get()
        task.set_dequeue_timestamp()
        task.set_exec_start_timestamp()
        return task

    async def get_mergable_tasks(self) -> Dict[str, List[PullTask]]:
        """ Get merged tasks
        Merge same vsys tasks into one, vsys as key
        :return: Dict[PullTask]
        """
        tasks: Dict[str, List[PullTask]] = {}
        async with self._lock:
            # read all tasks in queue
            task: PullTask = await self.dequeue()
            if task.vsys in tasks:
                tasks[task.vsys].append(task)
            else:
                tasks[task.vsys] = [task]

            while not self._queue.empty():
                task = await self.dequeue()
                if task.vsys in tasks:
                    tasks[task.vsys].append(task)
                else:
                    tasks[task.vsys] = [task]
        return tasks

    def task_done(self):
        try:
            if not self._queue.empty():
                self._queue.task_done()
        except Exception as e:
            pass

    async def join(self):
        await self._queue.join()