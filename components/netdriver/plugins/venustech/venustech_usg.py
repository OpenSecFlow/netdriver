#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.venustech import VenustechBase


# pylint: disable=abstract-method
class VenustechUSG(VenustechBase):
    """ Venustech USG Plugin """

    info = PluginInfo(
            vendor="venustech",
            model="usg.*",
            version="base",
            description="Venustech USG Plugin"
        )