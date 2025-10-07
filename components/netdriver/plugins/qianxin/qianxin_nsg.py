#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.qianxin import QiAnXinBase


class QiAnXinNSG(QiAnXinBase):
    """ QiAnXin NSG Plugin """

    info = PluginInfo(
        vendor="qianxin",
        model="nsg.*",
        version="base",
        description="QiAnXin NSG Plugin"
    )

    async def pull_running_config(self, vsys: str = QiAnXinBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show running config", vsys=vsys, mode=Mode.ENABLE)

    async def pull_hitcounts(self, vsys: str = QiAnXinBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show security policy", vsys=vsys, mode=Mode.ENABLE)

    async def pull_routes(self, vsys: str = QiAnXinBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show ip route\nshow ipv6 route", vsys=vsys, mode=Mode.ENABLE)