#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoCatalyst(CiscoBase):
    """ Cisco Catalyst Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="catalyst",
            version="base",
            description="Cisco Catalyst Plugin"
        )