#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.check_point import CheckPointBase


class CheckPointSecurityGateway(CheckPointBase):
    """ CheckPoint SecurityGateway Plugin """

    info = PluginInfo(
        vendor="check point",
        model="security gateway",
        version="base",
        description="CheckPoint SecurityGateway Plugin"
    )