#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver import utils
from netdriver.client.mode import Mode
from netdriver.exception.errors import SwitchVsysFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.huawei import HuaweiBase


class HuaweiUSG(HuaweiBase):
    """ Huawei USG Plugin """

    info = PluginInfo(
        vendor="huawei",
        model="usg.*",
        version="base",
        description="Huawei USG Plugin"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_hooks()

    def register_hooks(self):
        """ Register hooks for specific commands """
        self.register_hook("save", self.save)
        self.register_hook("save all", self.save)

    def decide_current_vsys(self, prompt: str):
        """ Decide current vsys
        Because of Huawei is hard to retrive vsys from prompt, we just set it to default
        """
        self._vsys = self._DEFAULT_VSYS
        self._logger.info(f"Set vsys to: {self._vsys}")

    async def switch_vsys(self, vsys: str) -> str:
        self._logger.info(f"Switching vsys: {self._vsys} -> {vsys}")

        output = ""
        # Already in the target vsys
        if vsys == self._vsys:
            return output

        ret: str
        if vsys == self._DEFAULT_VSYS:
            ret = await self.exec_cmd_in_vsys_and_mode("quit", mode=Mode.ENABLE)
            output += ret
        else:
            ret = await self.exec_cmd_in_vsys_and_mode(f"switch vsys {vsys}", mode=Mode.CONFIG)
            output += ret

        # check errors
        err = utils.regex.catch_error_of_output(ret,
                                                self.get_error_patterns(),
                                                self.get_ignore_error_patterns())
        if err:
            self._logger.error(f"Switch vsys failed: {err}")
            raise SwitchVsysFailed(err, output=output)

        self._vsys = vsys
        self._logger.info(f"Switched vsys to: {self._vsys}")
        return output
