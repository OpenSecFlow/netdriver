#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver import utils
from netdriver.client.mode import Mode
from netdriver.exception.errors import SwitchVsysFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.array import ArrayBase


# pylint: disable=abstract-method
class ArrayAG(ArrayBase):
    """ Array AG Plugin """

    info = PluginInfo(
        vendor="array",
        model="ag",
        version="base",
        description="Array AG Plugin"
    )

    def decide_current_vsys(self, prompt: str):
        self._logger.info(f"Deciding [{prompt}] vsys")
        if self._mode == Mode.LOGIN:
            self._vsys = ArrayBase._DEFAULT_VSYS
        elif prompt.endswith(")$"):
            # vsite_name(config)$ -> vsite_name
            self._vsys = prompt.split("(")[0]
        elif prompt.endswith("$"):
            # vsite_name$ -> vsite_name
            self._vsys = prompt.split("$")[0]
        else:
            self._vsys = ArrayBase._DEFAULT_VSYS
        self._logger.info(f"Got vsys: {self._vsys}")

    async def switch_vsys(self, vsys: str) -> str:
        self._logger.info(f"Switching vsys: {self._vsys} -> {vsys}")

        output = ""
        # Already in the target vsys
        if vsys == self._vsys:
            return output

        ret : str
        if vsys == ArrayBase._DEFAULT_VSYS:
            # Switch to default vsys
            ret = await self.exec_cmd_in_vsys_and_mode("exit", mode=Mode.ENABLE)
            output += ret
        else:
            # Switch to target vsys
            ret = await self.exec_cmd_in_vsys_and_mode(f"switch {vsys}", mode=Mode.ENABLE)
            output += ret

        # Check if there is any error
        err = utils.regex.catch_error_of_output(ret,
                                                self.get_error_patterns(),
                                                self.get_ignore_error_patterns())
        if err:
            self._logger.error(f"Switch vsys failed: {err}")
            raise SwitchVsysFailed(err, output=output)

        self._vsys = vsys
        self._logger.info(f"Switched vsys to: {self._vsys}")
        return output