#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from asyncssh import SSHServerProcess
from netdriver.client.mode import Mode
from netdriver.exception.server import ClientExit
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.models import DeviceBaseInfo


class HuaweiCEHandler(CommandHandler):
    """ Huawei CE Command Handler """

    info = DeviceBaseInfo(
        vendor="huawei",
        model="ce",
        version="*",
        description="Huawei CE Command Handler"
    )

    @classmethod
    def is_selectable(cls, vendor: str, model: str, version: str) -> bool:
        # only check vendor and model, check version in the future
        if cls.info.vendor == vendor and cls.info.model == model:
            return True

    def __init__(self, process: SSHServerProcess, conf_path: str = None):
        # current file path
        if conf_path is None:
            cwd_path = Path(__file__).parent
            conf_path = f"{cwd_path}/huawei_ce.yml"
        self.conf_path = conf_path
        super().__init__(process)

    @property
    def prompt(self) -> str:
        """ Get current prompt """
        prompt_template: str = self.config.modes[self._mode].prompt
        return prompt_template.format(self.config.hostname)

    async def switch_vsys(self, command: str) -> bool:
        return False

    async def switch_mode(self, command: str) -> bool:
        if command not in self.config.modes[self._mode].switch_mode_cmds:
            return False

        match self._mode:
            case Mode.ENABLE:
                if command == "quit":
                    # logout
                    raise ClientExit
                elif command == "system-view":
                    # switch to config mode
                    self._mode = Mode.CONFIG
                    return True
            case Mode.CONFIG:
                if command == "quit" or command == "return":
                    # exit config mode
                    self._mode = Mode.ENABLE
                    return True
            case _:
                return False
        return False