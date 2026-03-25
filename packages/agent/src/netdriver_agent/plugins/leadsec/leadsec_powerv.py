#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.leadsec import LeadsecBase


class LeadsecPowerV(LeadsecBase):
    """ Leadsec PowerV Session """

    info = PluginInfo(
        vendor="leadsec",
        model="powerv",
        version="base",
        description="Leadsec PowerV Plugin"
    )