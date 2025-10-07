#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoNexus(CiscoBase):
    """ Cisco Nexus Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="nexus",
            version="base",
            description="Cisco Nexus Plugin"
        )