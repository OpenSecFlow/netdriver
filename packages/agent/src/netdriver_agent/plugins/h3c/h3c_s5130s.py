#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.h3c import H3CBase


class H3CS5130S(H3CBase):
    """ H3C S5130S Plugin """

    info = PluginInfo(
        vendor="h3c",
        model="s5130s.*",
        version="base",
        description="H3C S5130S Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("save", self.save)