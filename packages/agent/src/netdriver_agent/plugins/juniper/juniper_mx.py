#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.juniper import JuniperBase


class JuniperMX(JuniperBase):
    """ Juniper MX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="mx.*",
        version="base",
        description="Juniper MX Plugin"
    )