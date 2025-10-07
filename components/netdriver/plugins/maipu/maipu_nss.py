#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.maipu import MaiPuBase


# pylint: disable=abstract-method
class MaiPuNSS(MaiPuBase):
    """ MaiPu NSS Plugin """

    info = PluginInfo(
            vendor="maipu",
            model="nss.*",
            version="base",
            description="MaiPu NSS Plugin"
        )
