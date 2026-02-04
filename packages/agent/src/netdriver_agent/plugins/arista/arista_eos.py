#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_agent.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.arista import AristaBase


# pylint: disable=abstract-method
class AristaEOS(AristaBase):
    """ Arista EOS Plugin """

    info = PluginInfo(
            vendor="arista",
            model="eos.*",
            version="base",
            description="Arista EOS Plugin"
        )