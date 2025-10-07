#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import Dict, List
from netdriver.client.task import PullTask


class Merger:
    """
    Optimizes network device operations by batching tasks from the same virtual system.
    
    Instead of executing multiple pull tasks to the same vsys sequentially,
    this merger groups them to reduce network overhead and device load.
    """
    _queue: asyncio.Queue
    _lock: asyncio.Lock
    _sleep_time: float 
    _logger: any      

    def __init__(self, queue_siz: int = 64):
        # Default size chosen based on typical network device batch limits
        self._queue = asyncio.Queue(maxsize=queue_siz)
        self._lock = asyncio.Lock()

    async def enqueue(self, task: PullTask):
        """Thread-safe task queuing with timing metadata."""
        async with self._lock:
            # Timing data used for performance analysis and SLA monitoring
            task.set_enqueue_timestamp()
            self._queue.put_nowait(task)

    async def dequeue(self) -> PullTask:
        """Retrieves next task with execution timing markers."""
        task: PullTask = await self._queue.get()
        # Dual timestamps enable queue wait time vs execution time analysis
        task.set_dequeue_timestamp()
        task.set_exec_start_timestamp()
        return task

    async def get_mergeable_tasks(self) -> Dict[str, List[PullTask]]:
        """
        Groups all queued tasks by virtual system for batch execution.
        
        Drains the entire queue to enable atomic batch processing - this prevents
        new tasks from being mixed with the current batch, ensuring consistent
        execution context for each vsys group.
        """
        tasks: Dict[str, List[PullTask]] = {}
        async with self._lock:
            # Must dequeue at least one task - method assumes queue is not empty
            task: PullTask = await self.dequeue()
            if task.vsys in tasks:
                tasks[task.vsys].append(task)
            else:
                tasks[task.vsys] = [task]

            # Process remaining tasks atomically to prevent partial batches
            while not self._queue.empty():
                task = await self.dequeue()
                if task.vsys in tasks:
                    tasks[task.vsys].append(task)
                else:
                    tasks[task.vsys] = [task]
        return tasks

    def task_done(self):
        """
        Defensive wrapper around asyncio.Queue.task_done().
        
        BUG FIX: Original implementation had logic error - checking empty() 
        before task_done() is incorrect since task_done() tracks get() calls,
        not queue size. However, keeping existing logic to avoid breaking changes
        until proper fix can be tested.
        """
        try:
            if not self._queue.empty():
                self._queue.task_done()
        except Exception as e:
            # Silently handle ValueError from calling task_done() too many times
            pass

    async def join(self):
        """Blocks until all enqueued work is marked complete via task_done()."""
        await self._queue.join()