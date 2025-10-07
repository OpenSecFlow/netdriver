#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.hillstone import HillstoneBase


class HillstoneSG(HillstoneBase):
    """ Hillstone SG Plugin """

    info = PluginInfo(
        vendor="hillstone",
        model="sg.*",
        version="base",
        description="Hillstone SG Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("save", self.save)
        self.register_hook("save all", self.save)