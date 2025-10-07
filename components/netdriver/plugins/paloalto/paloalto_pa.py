#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.client.mode import Mode
from netdriver.exception.errors import DetectCurrentModeFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.paloalto import PaloaltoBase


class PaloaltoPa(PaloaltoBase):
    """ Palolalto PA Plugin """

    info = PluginInfo(
        vendor="paloalto",
        model="pa.*",
        version="base",
        description="Paloalto PA Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("commit", self.save)