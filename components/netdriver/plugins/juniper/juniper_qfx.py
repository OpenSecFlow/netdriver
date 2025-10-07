#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.juniper import JuniperBase


class JuniperQFX(JuniperBase):
    """ Juniper QFX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="qfx.*",
        version="base",
        description="Juniper QFX Plugin"
    )