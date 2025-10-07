#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.juniper import JuniperBase


class JuniperSRX(JuniperBase):
    """ Juniper SRX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="srx.*",
        version="base",
        description="Juniper SRX Plugin"
    )