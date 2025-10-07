#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.huawei import HuaweiBase


class HuaweiCE(HuaweiBase):
    """ Huawei CE Plugin """
    info = PluginInfo(
        vendor="huawei",
        model="ce.*",
        version="base",
        description="Huawei CE Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("save", self.save)