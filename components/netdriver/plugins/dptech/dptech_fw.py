#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.dptech import DptechBase


class DptechFWPath(DptechBase):
    """ Dptech FW Plugin """

    info = PluginInfo(
        vendor="dptech",
        model="fw.*",
        version="base",
        description="Dptech FW Plugin"
    )
