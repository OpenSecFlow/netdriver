#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.cisco import CiscoBase


# pylint: disable=abstract-method
class CiscoASA(CiscoBase):
    """ Cisco ASA Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="asa",
            version="base",
            description="Cisco ASA Plugin"
        )

    async def pull_running_config(self, vsys: str = CiscoBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show running-config\nshow access-list", vsys=vsys,
                                   mode=Mode.ENABLE)

    async def pull_hitcounts(self, vsys: str = CiscoBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show access-list", vsys=vsys, mode=Mode.ENABLE)

    async def pull_routes(self, vsys: str = CiscoBase._DEFAULT_VSYS) -> str:
        return await self.exec_cmd_in_vsys_and_mode("show route", vsys=vsys, mode=Mode.ENABLE)