#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import log
from netdriver.client.mode import Mode
from netdriver.exception.errors import DetectCurrentModeFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.leadsec import LeadsecBase


class LeadsecPowerV(LeadsecBase):
    """ Leadsec PowerV Session """
    info = PluginInfo(
        vendor="leadsec",
        model="powerv",
        version="base",
        description="Leadsec PowerV Plugin"
    )

    def decide_current_mode(self, prompt):
        self._logger.info(f"Deciding mode with: {prompt}")
        mode: Mode = None
        login_pattern = self.get_login_prompt_pattern()

        if login_pattern and login_pattern.search(prompt):
            mode = Mode.LOGIN
        else:
            raise DetectCurrentModeFailed(f"Unknown mode, prompt: {prompt}")

        self._logger.info(f"Got mode: {self._mode} with lastline: {prompt}")
    

    def decide_current_vsys(self, prompt: str):
        # PowerV does not have vsys, return default
        self._vsys = self._DEFAULT_VSYS
        self._logger.info(f"Set vsys to: {self._vsys}")

    async def switch_vsys(self, vsys: str) -> str:
        if vsys != LeadsecBase._DEFAULT_VSYS:
            self._logger.warning("Leadsec PowerV not support vsys, ignore")
        self._vsys = vsys
        return ""

    async def disable_pagging(self):
        self._logger.warning("Leadsec PowerV not support pagination command")