#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
from typing import Dict
from pathlib import Path

import yaml
from asyncssh import SSHServerProcess

from netdriver.client.mode import Mode
from netdriver.log import logman
from netdriver.server.models import DeviceBaseInfo, DeviceConfig


class CommandHandler(abc.ABC):
    """Base class for command handler"""
    _process: SSHServerProcess
    _logger = logman.logger
    _mode = Mode  # current mode
    _mode_cmd_map: Dict[str, str]  # mode command dictionary
    _common_cmd_map: Dict[str, str]  # common command dictionary
    info: DeviceBaseInfo
    conf_path: str
    config: DeviceConfig

    @classmethod
    @abc.abstractmethod
    def is_selectable(cls, vendor: str, model: str, version: str) -> bool:
        """ Check if the device is the same as the handler """
        raise NotImplementedError

    @abc.abstractmethod
    async def switch_vsys(self, command: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def switch_mode(self, command) -> bool:
        raise NotImplementedError

    def __init__(self, process: SSHServerProcess):
        self._process = process
        self._load_config()
        self._mode = self.config.start_mode

    def _load_config(self):
        """ Load config from file """
        try:
            conf_dict = yaml.safe_load(Path(self.conf_path).read_text(encoding='utf-8'))
            self.config = DeviceConfig(**conf_dict)
        except Exception as e:
            self._logger.error(f"Config load failed: {e}")

    @property
    def prompt(self) -> str:
        """ Get current prompt """
        return self.config.hostname + self.config.modes[self._mode].prompt

    def exec_cmd_in_mode(self, command: str) -> str:
        """ Execute command in current mode """
        self._logger.info(f"Exec [{command} in {self._mode}]")
        if command in self.config.modes[self._mode].cmd_map:
            return self.config.modes[self._mode].cmd_map[command]
        elif command in self.config.common_cmd_map:
            return self.config.common_cmd_map[command]
        else:
            return self.config.invalid_cmd_error

    async def exec_cmd(self, command) -> str:
        """ Execute command """
        self._logger.info(f"Exec: {command}\n")
        if not command:
            return ""
        if await self.switch_vsys(command):
            return ""
        if await self.switch_mode(command):
            return ""
        return self.exec_cmd_in_mode(command)

    def writeline(self, message: str):
        """ Write message to stdout with line feed """
        self.write(message + self.config.line_feed)

    def write(self, message: str):
        """ Write message to stdout """
        if not self._process.is_closing():
            self._process.stdout.write(message)

    async def run(self):
        self.writeline(self.config.welcome)
        self.write(self.prompt)
        async for cmd in self._process.stdin:
            cmd = cmd.rstrip('\n')
            self._logger.info(f"Received <- {cmd}")
            output = await self.exec_cmd(cmd)
            self._logger.info(f"Output -> {output}")
            self.writeline(output)
            self.write(self.prompt)
