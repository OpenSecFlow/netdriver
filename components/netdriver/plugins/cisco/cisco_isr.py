#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoISR(CiscoBase):
    """ Cisco ISR Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="isr.*",
            version="base",
            description="Cisco ISR Plugin"
        )