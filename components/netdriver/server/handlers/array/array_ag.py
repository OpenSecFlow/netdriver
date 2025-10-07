#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
from pathlib import Path
from asyncssh import SSHServerProcess
from netdriver.client.mode import Mode
from netdriver.exception.server import ClientExit
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.models import DeviceBaseInfo


class ArrayAGHandler(CommandHandler):
    """ Array AG Command Handler """
    info = DeviceBaseInfo(
        vendor="array",
        model="ag",
        version="*",
        description="Array AG Command Handler"
    )
    _vsys: str # current vsys

    @classmethod
    def is_selectable(cls, vendor: str, model: str, version: str) -> bool:
        # only check vendor and model, check version in the future
        if cls.info.vendor == vendor and cls.info.model == model:
            return True

    def __init__(self, process: SSHServerProcess, conf_path: str = None):
        if conf_path is None:
            cwd_path = Path(__file__).parent
            conf_path = f"{cwd_path}/array_ag.yml"
        self.conf_path = conf_path
        self._vsys = "default"
        super().__init__(process)

    @property
    def prompt(self) -> str:
        if self._vsys == "default":
            return self.config.hostname + self.config.modes[self._mode].prompt
        else:
            if self._mode == Mode.ENABLE:
                return f"{self._vsys}$"
            elif self._mode == Mode.CONFIG:
                return f"{self._vsys}(config)$"
            else:
                raise ValueError("Login mode does not support in virtual site!")

    async def switch_vsys(self, command: str) -> bool:
        """ Switch vsys
        command to handle:
        - <vsys>$ exit
        - switch <vsys>
        """
        res = command.split(" ")
        param_len = len(res)
        cmd = res[0]

        if self._mode == Mode.LOGIN:
            return False

        if param_len == 1 and cmd == "exit" and self._mode == Mode.ENABLE and \
            self._vsys != "default":
            # handle: <vsys>$ exit
            self._logger.info(f"Switched vsys [{self._vsys} -> default]")
            self._vsys = "default"
            return True

        if param_len != 2:
            return False

        vsys = res[1]
        match self._vsys:
            case "default":
                # default to virtual site
                if cmd == "switch" and vsys:
                    self._logger.info(f"Switched vsys [default -> {vsys}]")
                    self._vsys = vsys
                    return True
            case _:
                # virtual site to virtual site
                if cmd == "switch" and vsys:
                    self._logger.info(f"Switched vsys [{self._vsys} -> {vsys}]")
                    self._vsys = vsys
                    return True
                else:
                    return False
        return False


    async def switch_mode(self, command) -> bool:
        if command not in self.config.modes[self._mode].switch_mode_cmds:
            return False

        match self._mode:
            case Mode.LOGIN:
                if command == "enable":
                    self._logger.info("Switching mode [login -> enable]")
                    self.write("Enable password:")
                    passwd = await self._process.stdin.readline()
                    passwd = passwd.rstrip("\n")
                    if passwd != self.config.enable_password:
                        self.writeline("Access denied!")
                        return True
                    else:
                        self._mode = Mode.ENABLE
                        return True
                elif command == "exit":
                    # logout
                    self._logger.info("Logout")
                    raise ClientExit
            case Mode.ENABLE:
                if command == "disable":
                    # to loging
                    self._logger.info("Switching mode [enable -> login]")
                    self._mode = Mode.LOGIN
                    return True
                elif command == "exit":
                    # logout
                    self._logger.info("Logout")
                    raise ClientExit
                elif command == "configure terminal":
                    # switch to config mode
                    self._logger.info("Switching mode [enable -> config]")
                    self._mode = Mode.CONFIG
                    return True
            case Mode.CONFIG:
                if command == "exit":
                    # to enable
                    self._logger.info("Switching mode [config -> enable]")
                    self._mode = Mode.ENABLE
                    return True
                elif command == "disable" and self._vsys == "default":
                    # to login, only works in default vsys
                    self._logger.info("Switching mode [config -> login]")
                    self._mode = Mode.LOGIN
                    return True
            case _:
                return False
        return False
