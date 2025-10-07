#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver import utils
from netdriver.client.mode import Mode
from netdriver.exception.errors import DetectCurrentVsysFailed, SwitchVsysFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.fortinet import FortinetBase


class FortinetFortiGate(FortinetBase):
    """ Fortinet FortiGate Plugin """

    info = PluginInfo(
        vendor="fortinet",
        model="fortigate.*",
        version="base",
        description="Fortinet FortiGate Plugin"
    )

    _CMD_CANCEL_MORE = "config global\nconfig system console\nset output standard\nend\nend"

    def decide_current_vsys(self, prompt: str):
        """ 
        Decide current vsys
        Extract VSYS through prompt
        """

        vsys = self._DEFAULT_VSYS
        vsys_match = None
        union_pattern = self.get_union_pattern()
        vsys_pattern = FortinetBase.PatternHelper.get_vsys_pattern()
        if union_pattern and union_pattern.search(prompt):
            if vsys_pattern:
                vsys_match = vsys_pattern.search(prompt)
            if vsys_match:
               vsys = vsys_match.group(1) 
        else:
            raise DetectCurrentVsysFailed(f"Unknown vsys, prompt: {prompt}")
        self._vsys = vsys
        self._logger.info(f"Set vsys to: {self._vsys}")

    async def switch_vsys(self, vsys: str) -> str:
        self._logger.info(f"Switching vsys: {self._vsys} -> {vsys}")

        output = ""
        # Already in the target vsys
        if vsys == self._vsys:
            return output

        ret: str
        if vsys == self._DEFAULT_VSYS:
            # vsys -> default
            ret = await self.exec_cmd_in_vsys_and_mode("end", mode=Mode.ENABLE)
            output += ret
        elif self._vsys == self._DEFAULT_VSYS:
            # default -> vsys
            ret = await self.exec_cmd_in_vsys_and_mode(f"config vdom\nedit {vsys}", mode=Mode.ENABLE)
            output += ret
        else:
            # vsys1 -> vsys2
            ret = await self.exec_cmd_in_vsys_and_mode(f"next\nedit {vsys}", mode=Mode.ENABLE)
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
