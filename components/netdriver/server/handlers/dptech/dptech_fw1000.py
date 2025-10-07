#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-

from pathlib import Path
from asyncssh import SSHServerProcess
from netdriver.client.mode import Mode
from netdriver.exception.server import ClientExit
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.models import DeviceBaseInfo


class DptechFW1000Handler(CommandHandler):
    """ Dptech FW1000 Command Handler """

    info = DeviceBaseInfo(
        vendor="dptech",
        model="fw1000",
        version="*",
        description="Dptech FW1000 Command Handler"
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
            conf_path = f"{cwd_path}/dptech_fw1000.yml"
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
                if command == "exit":
                    # logout
                    raise ClientExit
                if command == "end":
                    return True
                elif command == "conf-mode":
                    # switch to config mode
                    self._mode = Mode.CONFIG
                    return True
            case Mode.CONFIG:
                if command == "end":
                    # exit config mode
                    self._mode = Mode.ENABLE
                    return True
            case _:
                return False
        return False
