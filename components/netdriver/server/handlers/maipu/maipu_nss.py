#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-

from pathlib import Path
from asyncssh import SSHServerProcess
from netdriver.client.mode import Mode
from netdriver.exception.server import ClientExit
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.models import DeviceBaseInfo


class MaiPuNSSHandler(CommandHandler):
    """ MaiPu NSS Command Handler """

    info = DeviceBaseInfo(
        vendor="maipu",
        model="nss",
        version="*",
        description="MaiPu NSS Command Handler"
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
            conf_path = f"{cwd_path}/maipu_nss.yml"
        self.conf_path = conf_path
        super().__init__(process)

    async def switch_vsys(self, command: str) -> bool:
        return False

    async def switch_mode(self, command: str) -> bool:
        if command not in self.config.modes[self._mode].switch_mode_cmds:
            return False

        match self._mode:
            case Mode.LOGIN:
                if command == "exit":
                    # logout
                    raise ClientExit
                if command == "enable":
                    self._mode = Mode.ENABLE
                    return True
            case Mode.ENABLE:
                if command == "exit":
                    # logout
                    raise ClientExit
                elif command == "configure terminal":
                    # switch to config mode
                    self._mode = Mode.CONFIG
                    return True
                elif command == "disable":
                    self._mode = Mode.LOGIN
                    return True
            case Mode.CONFIG:
                if command == "exit" or command == "end":
                    # exit config mode
                    self._mode = Mode.ENABLE
                    return True
                elif command == "disable":
                    # login mode
                    self._mode = Mode.LOGIN
                    return True
            case _:
                return False
        return False
