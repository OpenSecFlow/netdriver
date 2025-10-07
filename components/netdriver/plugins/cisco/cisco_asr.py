#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoASR(CiscoBase):
    """ Cisco ASR Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="asr.*",
            version="base",
            description="Cisco ASR Plugin"
        )