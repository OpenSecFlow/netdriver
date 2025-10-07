#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.juniper import JuniperBase


class JuniperMX(JuniperBase):
    """ Juniper MX Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="mx.*",
        version="base",
        description="Juniper MX Plugin"
    )