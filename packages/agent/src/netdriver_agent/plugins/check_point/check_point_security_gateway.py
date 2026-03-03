#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.check_point import CheckPointBase


class CheckPointSecurityGateway(CheckPointBase):
    """ CheckPoint SecurityGateway Plugin """

    info = PluginInfo(
        vendor="check point",
        model="security gateway",
        version="base",
        description="CheckPoint SecurityGateway Plugin"
    )