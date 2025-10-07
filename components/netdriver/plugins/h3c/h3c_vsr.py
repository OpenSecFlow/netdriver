#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.h3c import H3CBase


class H3CVSR(H3CBase):
    """ H3C VSR Plugin """

    info = PluginInfo(
        vendor="h3c",
        model="vsr.*",
        version="base",
        description="H3C VSR Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("save", self.save)