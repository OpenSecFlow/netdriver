#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Utilities for Plugin and Template Management

Provides async file operations for loading TextFSM templates and discovering
plugin directories. Optimized for non-blocking I/O to prevent performance
degradation during bulk template loading operations.
"""
import os
import sys
from typing import Dict

from aiofiles import os as aio_os, open as aio_open

async def load_templates(directory: str, prefix: str) -> Dict[str, str]:
    """
    Bulk load TextFSM parsing templates with async I/O optimization.
    
    TextFSM templates convert unstructured command output into structured data.
    Async loading prevents blocking when processing large template collections,
    maintaining system responsiveness during plugin initialization.
    """
    templates = {}

    entries = await aio_os.scandir(directory)
    for entry in entries:
        # Filter by prefix to support vendor-specific template organization
        if entry.name.startswith(prefix) and entry.name.endswith(".textfsm"):
            async with aio_open(entry.path, "r") as f:
                templates[entry.name] = await f.read()

    return templates


def get_plugin_dir(plugin: object) -> str:
    """
    Resolve plugin's filesystem location for resource discovery.
    
    Enables plugins to locate their associated template files and configuration
    resources regardless of installation method or package structure. Critical
    for proper plugin resource loading in different deployment scenarios.
    """
    module = sys.modules[plugin.__module__]
    directory = os.path.dirname(os.path.abspath(module.__file__))
    return directory
