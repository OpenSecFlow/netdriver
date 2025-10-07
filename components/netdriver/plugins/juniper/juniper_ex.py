#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.juniper import JuniperBase


class JuniperEX(JuniperBase):
    """ Juniper EX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="ex.*",
        version="base",
        description="Juniper EX Plugin"
    )
