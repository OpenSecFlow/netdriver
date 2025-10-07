#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoCatalyst(CiscoBase):
    """ Cisco Catalyst Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="catalyst",
            version="base",
            description="Cisco Catalyst Plugin"
        )