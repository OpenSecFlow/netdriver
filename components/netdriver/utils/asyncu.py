#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import functools
from typing import Callable, Optional


class AsyncTimeoutError(Exception):
    """ Custom exception for async function timeout """
    def __init__(self, func_name: str, timeout: float):
        self.func_name = func_name
        self.timeout = timeout
        super().__init__(f"Function '{func_name}' timed out after {timeout} seconds")


def async_timeout(
    timeout: Optional[float] = None,
    timeout_param: str = "timeout"):
    """
    Decorator to apply a timeout to an asynchronous function.
    If `timeout` is provided, it will be used as the timeout value.
    If `timeout_param` is provided, it will look for this parameter in the function arguments
    to determine the timeout value dynamically.
    If neither is provided, the function will run without a timeout.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            actual_timeout = kwargs.pop(timeout_param, timeout)
            
            if not actual_timeout and args:
                instance = args[0]
                if hasattr(instance, f"_{func.__name__}_timeout"):
                    actual_timeout = getattr(instance, f"_{func.__name__}_timeout")
                elif hasattr(instance, "default_timeout"):
                    actual_timeout = getattr(instance, "default_timeout")
            
            if actual_timeout is None:
                return await func(*args, **kwargs)
            
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=actual_timeout)
            except asyncio.TimeoutError:
                raise AsyncTimeoutError(func.__name__, actual_timeout)
                
        return wrapper
    return decorator
