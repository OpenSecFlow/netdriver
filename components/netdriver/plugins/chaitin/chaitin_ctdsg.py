#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.chaitin import ChaiTinBase


# pylint: disable=abstract-method
class ChaiTinCTDSG(ChaiTinBase):
    """ ChaiTin CTDSG Plugin """

    info = PluginInfo(
            vendor="chaitin",
            model="ctdsg.*",
            version="base",
            description="ChaiTin CTDSG Plugin"
        )