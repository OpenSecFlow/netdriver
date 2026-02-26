#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.juniper import JuniperBase


class JuniperQFX(JuniperBase):
    """ Juniper QFX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="qfx.*",
        version="base",
        description="Juniper QFX Plugin"
    )