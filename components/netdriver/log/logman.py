#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" A wrapper of loguru
"""
import inspect
from pprint import pformat
import logging
from typing import List

from asgi_correlation_id import correlation_id
from loguru import logger


def set_log_extras(record: dict):
    """set_log_extras [summary].
    [extended_summary]
    Args:
        record ([type]): [description]
    """
    # Log datetime in UTC time zone, even if server is using another timezone
    record["extra"]["correlation_id"] = correlation_id.get() or '-'


def format_record(record: dict) -> str:
    """Return a custom format for loguru loggers.
    Uses pformat for log any data like request/response body
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</green> | "
    format_string += "<level>{level}</level> | "
    # format_string += "<green>{process}-{thread}</green> | "
    if record["name"] == "asyncssh.logging" and record["extra"].get("session_key"):
        format_string += "<green>{extra[session_key]}</green> | "
    else:
        format_string += "<green>{extra[correlation_id]}</green> | "
    format_string += "<cyan>{name}</cyan>:"
    format_string += "<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    format_string += "<level>{message}</level>"

    # This is to nice print data, like:
    # logger.bind(payload=dataobject).info("Received data")
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=2, compact=True, width=100
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"

    return format_string


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    """

    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# Track if logger has been initialized
_logger_initialized = False

def configure_logman(level: str = "INFO", intercept_loggers: List[str] = [], log_file: str = "logs/netdriver_agent.log",
                     module_filter: str = None, exclude_filter: str = None):
    """ Config loguru

    Args:
        level: Log level (INFO, DEBUG, TRACE)
        intercept_loggers: List of logger names to intercept
        log_file: Path to log file
        module_filter: Module name pattern to filter (e.g., "netdriver.agent", "netdriver.server")
                       If None, all logs are written to the file
        exclude_filter: Module name pattern to exclude (e.g., "netdriver.server")
                       Logs from modules starting with this pattern will be excluded

    Note: This function can be called multiple times to add multiple log files with different filters.
    On first call, it removes all existing handlers and sets up base configuration.
    On subsequent calls, it only adds new handlers without removing existing ones.
    """
    global _logger_initialized

    # Only remove handlers on first call
    if not _logger_initialized:
        logger.remove()
        _logger_initialized = True

    intercept_handler = InterceptHandler()

    _all_loggers = logging.root.manager.loggerDict
    for name, _logger in _all_loggers.items():
        if name in intercept_loggers:
            if intercept_handler not in _logger.handlers:
                _logger.handlers = [intercept_handler]

    # Create filter function based on module_filter and exclude_filter
    def log_filter(record):
        # First check exclude filter
        if exclude_filter and record["name"].startswith(exclude_filter):
            return False
        # Then check include filter
        if module_filter is None:
            return True
        # Filter based on module name
        return record["name"].startswith(module_filter)

    # Add log file handler with optional module filter
    handler_id = logger.add(
        log_file,
        rotation="1 days",
        retention="60 days",
        colorize=False,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level=level,
        format=format_record,
        filter=log_filter
    )

    # Configure standard logging only once
    if not logging.root.handlers or all(isinstance(h, InterceptHandler) for h in logging.root.handlers):
        # because the logging dose not support TRACE level, we use DEBUG instead
        if level == "TRACE":
            logging.basicConfig(handlers=[intercept_handler], level="DEBUG", force=True)
        else:
            logging.basicConfig(handlers=[intercept_handler], level=level, force=True)

    logger.configure(patcher=set_log_extras)

    return handler_id


def create_session_logger(session_key: str, level: str = "INFO"):
    """Create a logger for a specific session."""
    return logger.bind(session_key=session_key)
