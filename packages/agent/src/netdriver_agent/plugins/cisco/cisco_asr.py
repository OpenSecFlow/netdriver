#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoASR(CiscoBase):
    """ Cisco ASR Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="asr.*",
            version="base",
            description="Cisco ASR Plugin"
        )