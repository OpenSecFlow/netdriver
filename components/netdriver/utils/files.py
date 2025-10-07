#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from typing import Dict

from aiofiles import os as aio_os, open as aio_open

async def load_templates(directory: str, prefix: str) -> Dict[str, str]:
    """ Load templates from directory """
    templates = {}

    entries = await aio_os.scandir(directory)
    for entry in entries:
        if entry.name.startswith(prefix) and entry.name.endswith(".textfsm"):
            async with aio_open(entry.path, "r") as f:
                templates[entry.name] = await f.read()

    return templates


def get_plugin_dir(plugin: object) -> str:
    """ Get plugin path """
    module = sys.modules[plugin.__module__]
    directory = os.path.dirname(os.path.abspath(module.__file__))
    return directory
