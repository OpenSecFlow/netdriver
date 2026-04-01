#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-

from pathlib import Path
from asyncssh import SSHServerProcess
from netdriver_core.dev.mode import Mode
from netdriver_core.exception.server import ClientExit
from netdriver_simunet.server.handlers.command_handler import CommandHandler
from netdriver_simunet.server.models import DeviceBaseInfo


class FortinetFortigateHandler(CommandHandler):
    """ Fortinet fortigate Command Handler """

    info = DeviceBaseInfo(
        vendor="fortinet",
        model="fortigate",
        version="*",
        description="Fortinet fortigate Command Handler"
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
            conf_path = f"{cwd_path}/fortinet_fortigate.yml"
        self.conf_path = conf_path
        super().__init__(process)
        self.level = []
        self.level_type = []

    @property
    def prompt(self) -> str:
        prompt = self.config.hostname
        if self.level:
            prompt = f'{prompt} ({self.level[-1]})'
        return prompt + self.config.modes[self._mode].prompt

    def switch_level(self, command: str) -> bool:
        if command.startswith('config'):
            commands = command.split(' ')
            self.level_type.append(commands[0])
            self.level.append(commands[-1])
        elif command.startswith('edit'):
            if self.level_type and self.level_type[-1] == 'config':
                commands = command.split(' ')
                self.level_type.append(commands[0])
                self.level.append(commands[-1])
            else:
                return False
        elif command == 'end':
            if self.level_type:
                is_edit = False
                if self.level_type[-1] == 'edit':
                    is_edit = True
                self.level.pop()
                self.level_type.pop()
                if is_edit:
                    self.level.pop()
                    self.level_type.pop()
            else:
                return False   
        elif command == 'next':
            if self.level_type and self.level_type[-1] == 'edit':
                self.level.pop()
                self.level_type.pop()    
            else:
                return False
        elif command == 'exit' and self.level:
            return False
        return True

    def exec_cmd_in_mode(self, command: str) -> str:
        """ Execute command in current mode """
        self._logger.info(f"Exec [{command} in {self._mode}]")
        if command in self.config.modes[self._mode].cmd_map:
            if not self.switch_level(command):
                return self.config.invalid_cmd_error
            return self.config.modes[self._mode].cmd_map[command]
        elif command in self.config.common_cmd_map:
            if not self.switch_level(command):
                return self.config.invalid_cmd_error
            return self.config.common_cmd_map[command]
        else:
            return self.config.invalid_cmd_error

    async def switch_vsys(self, command: str) -> bool:
        return False

    async def switch_mode(self, command: str) -> bool:
        match self._mode:
            case Mode.ENABLE:
                if command == "exit" and not self.level:
                    # logout
                    raise ClientExit
            case _:
                return False
        return False