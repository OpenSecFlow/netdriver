#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.array import ArrayBase


# pylint: disable=abstract-method
class ArrayAPV(ArrayBase):
    """ Array APV Plugin """

    info = PluginInfo(
        vendor="array",
        model="apv",
        version="base",
        description="Array APV Plugin"
    )