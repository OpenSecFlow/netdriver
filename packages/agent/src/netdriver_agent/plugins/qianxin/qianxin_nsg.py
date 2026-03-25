#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.qianxin import QiAnXinBase


class QiAnXinNSG(QiAnXinBase):
    """ QiAnXin NSG Plugin """

    info = PluginInfo(
        vendor="qianxin",
        model="nsg.*",
        version="base",
        description="QiAnXin NSG Plugin"
    )