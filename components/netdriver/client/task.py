#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from asyncio import Future
from typing import List

from netdriver.client.mode import Mode
from netdriver.exception.errors import BaseError
from netdriver.plugin.types import ConfigType


class TaskResult:
    """ Task result of session exec """
    queue_time: float
    exec_time: float
    total_time: float
    output: str
    exception: BaseError

    def get_total_time(self):
        return self.queue_time + self.exec_time


class Task:
    """ Exec Task of sesssion exec """
    enqueue_timestamp: float
    dequeue_timestamp: float
    exec_start_timestamp: float
    exec_end_timestamp: float
    timeout: float
    catch_error: bool
    vsys: str
    exception: BaseError
    future: Future

    def __init__(self, vsys: str = None, timeout: float = 10, catch_error: bool = True,
                 future: Future = None):
        self.vsys = vsys
        self.timeout = timeout
        self.catch_error = catch_error
        self.future = future

    def set_enqueue_timestamp(self):
        self.enqueue_timestamp = time.time()

    def set_dequeue_timestamp(self):
        self.dequeue_timestamp = time.time()

    def set_exec_start_timestamp(self):
        self.exec_start_timestamp = time.time()

    def set_exec_end_timestamp(self):
        self.exec_end_timestamp = time.time()

    def cacnel(self):
        if self.future and not self.future.done():
            self.future.cancel()


class CmdTaskResult(TaskResult):
    """ Command Task Result """


class CmdTask(Task):
    """ Command Task """
    mode: Mode
    command: str
    detail_output: bool

    def __init__(self, command: str, vsys: str = None, mode: Mode = None,
                 timeout: float = 10, catch_error: bool = True, 
                 detail_output: bool = True, future: Future = None):
        super().__init__(vsys, timeout, catch_error, future)
        self.command = command.strip()
        self.mode = mode
        self.detail_output = detail_output

    def __str__(self):
        return f"[{self.command}|{self.vsys}|{self.mode}|{self.timeout}]"

    def set_result(self, output: str = None, exception: BaseError = None):
        self.set_exec_end_timestamp()
        self.exception = exception
        if self.future and not self.future.done():
            self.future.set_result(output)

    async def get_result(self) -> CmdTaskResult:
        output = await self.future
        result = CmdTaskResult()
        # If dequeue_timestamp is None, it not dequeued
        if not self.dequeue_timestamp:
            result.queue_time = 0.0
        else:
            result.queue_time = self.dequeue_timestamp - self.enqueue_timestamp
        # If exec_start_timestamp is None, it not dequeued
        if not self.exec_start_timestamp:
            result.exec_time = 0.0
        else:
            result.exec_time = self.exec_end_timestamp - self.exec_start_timestamp
        result.exception = self.exception
        result.output = output
        return result


class PullTaskResult(TaskResult):
    """ Pull Task Result """


class PullTask(Task):
    """ Pull Task """
    type: ConfigType

    def __init__(self, type: ConfigType, vsys: str = None,
                 timeout: float = 10, catch_error: bool = True,
                 future: Future = None):
        super().__init__(vsys, timeout, catch_error, future)
        self.type = type

    def __str__(self):
        return f"[{self.type}|{self.vsys}|{self.timeout}]"

    def set_result(self, output: str = None, exception: BaseError = None):
        self.set_exec_end_timestamp()
        self.exception = exception
        if self.future and not self.future.done():
            self.future.set_result(output)

    async def get_result(self) -> PullTaskResult:
        ouput = await self.future
        result = PullTaskResult()
        # If dequeue_timestamp is None, it not dequeued
        if not self.dequeue_timestamp:
            result.queue_time = 0.0
        else:
            result.queue_time = self.dequeue_timestamp - self.enqueue_timestamp
        # If exec_start_timestamp is None, it not dequeued
        if not self.exec_start_timestamp:
            result.exec_time = 0.0
        else:
            result.exec_time = self.exec_end_timestamp - self.exec_start_timestamp
        result.exception = self.exception
        result.output = ouput
        return result
