#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.topsec import TopSecBase


class TopSecNGFW(TopSecBase):
    """ TopSec NGFW Plugin """

    info = PluginInfo(
        vendor="topsec",
        model="ngfw.*",
        version="base",
        description="TopSec NGFW Plugin"
    )