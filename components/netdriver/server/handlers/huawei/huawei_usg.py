#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import StrEnum
from pathlib import Path
import re
from asyncssh import SSHServerProcess
from netdriver.client.mode import Mode
from netdriver.exception.server import ClientExit
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.models import DeviceBaseInfo

_RE_RULE = re.compile(r"rule name (\S+)")


class HuaweiUSGHandler(CommandHandler):
    """ Huawei USG Command Handler """

    class HrpRole(StrEnum):
        MASTER: str = "master"
        SLAVE: str = "slave"
        NONE: str = "none"

    info = DeviceBaseInfo(
        vendor="huawei",
        model="usg",
        version="*",
        description="Huawei USG Command Handler"
    )
    _vsys: str # current vsys
    _hrp_role: HrpRole # current HRP role
    _config_level: list

    @classmethod
    def is_selectable(cls, vendor: str, model: str, version: str) -> bool:
        # only check vendor and model, check version in the future
        if cls.info.vendor == vendor and cls.info.model == model:
            return True

    def __init__(self, process: SSHServerProcess, conf_path: str = None):
        # current file path
        if conf_path is None:
            cwd_path = Path(__file__).parent
            conf_path = f"{cwd_path}/huawei_usg.yml"
        self.conf_path = conf_path
        self._vsys = "default"
        super().__init__(process)
        self._hrp_role = HuaweiUSGHandler.HrpRole(
            self.config.vendor_options.get("huawei.usg.hrp_role", "none"))
        self._reset_config_level()

    @property
    def prompt(self) -> str:
        hrp_prefix: str
        prompt_template: str = self.config.modes[self._mode].prompt
        match self._hrp_role:
            case self.HrpRole.MASTER:
                hrp_prefix = "HRP_M"
            case self.HrpRole.SLAVE:
                hrp_prefix = "HRP_S"
            case _:
                hrp_prefix = ""
        prompt = self.config.hostname
        if self._vsys != "default":
            prompt += f"-{self._vsys}"
        for level in self._config_level:
            if level:
                prompt += f"-{level}"
        return prompt_template.format(hrp_prefix, prompt)

    def _reset_config_level(self):
        self._config_level = [""]

    def _push_config_level(self, cfg: str):
        self._config_level.append(cfg)

    def _pop_config_level(self):
        if len(self._config_level) > 1:
            self._config_level.pop()

    def _get_current_config_level(self) -> str:
        return self._config_level[-1]

    async def switch_vsys(self, command: str) -> bool:
        cmds = command.split(" ")
        cmd_len = len(cmds)

        # return to user view
        if cmd_len == 1 and cmds[0] == "return":
            self._vsys = "default"
            self._reset_config_level()
            self._mode = Mode.ENABLE
            return True

        match self._vsys:
            case "default":
                # public
                if cmd_len != 3:
                    return False
                if cmds[0] == "switch" and cmds[1] == "vsys" and cmds[2] \
                    and self._mode == Mode.CONFIG:
                    self._vsys = cmds[2]
                    self._reset_config_level()
                    self._mode = Mode.ENABLE
                    self._logger.info(f"Switched vssy [default -> {self._vsys}]")
                    return True
            case _:
                # $vsys
                if cmd_len == 1 and cmds[0] == "quit" and self._mode == Mode.ENABLE:
                    self._vsys = "default"
                    self._reset_config_level()
                    self._logger.info(f"Switched vsys [{self._vsys} -> default]")
                    return True
        return False

    async def switch_mode(self, command: str) -> bool:
        # only switch mode at first level
        if len(self._config_level) != 1:
            return False
        if command not in self.config.modes[self._mode].switch_mode_cmds:
            return False
        match self._mode:
            case Mode.ENABLE:
                if command == "quit":
                    self._logger.info("Logout")
                    # logout
                    raise ClientExit
                elif command == "system-view" or command == "sys":
                    # switch to config mode
                    self._logger.info("Switched mode [enable -> config]")
                    self._mode = Mode.CONFIG
                    return True
            case Mode.CONFIG:
                if command == "quit":
                    # exit config mode
                    self._logger.info("Switched mode [config -> enable]")
                    self._mode = Mode.ENABLE
                    return True
        return False

    def exec_cmd_in_mode(self, command: str) -> str:
        self._logger.info(f"Exec [{command} in {self._mode}]")
        # handle common command
        if command in self.config.common_cmd_map:
            return self.config.common_cmd_map.get(command, "")
        # handle sub level command
        current_mode_cmd_map = self.config.modes[self._mode]
        match self._mode:
            case Mode.ENABLE:
                return current_mode_cmd_map.cmd_map.get(command, self.config.invalid_cmd_error)
            case Mode.CONFIG:
                # handle sub level command
                if command == "user-interface current":
                    self._push_config_level("ui-vty0")
                if command == "security-policy":
                    self._push_config_level("policy-security")
                # handle rule command
                matched = _RE_RULE.match(command)
                if matched:
                    rule_name = matched.group(1)
                    self._push_config_level(f"rule-{rule_name}")
                elif command == "quit" and self._get_current_config_level():
                    self._pop_config_level()
                # handle normal command
                return current_mode_cmd_map.cmd_map.get(command, self.config.invalid_cmd_error)
