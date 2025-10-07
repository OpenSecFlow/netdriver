#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import re
from netdriver.client.channel import ReadBuffer
from netdriver.client.mode import Mode
from netdriver.client.session import Session
from netdriver.exception.errors import ConfigFailed, DetectCurrentModeFailed, DisableFailed, EnableFailed, ExitConfigFailed, UnsupportedMode
from netdriver.plugin.core import PluginCore
from netdriver.utils.asyncu import async_timeout


# pylint: disable=abstract-method
class Base(Session, PluginCore):
    """ Base Plugin """

    _CMD_ENABLE = "enable"
    _CMD_DISABLE = "disable"
    _CMD_CONFIG = "configure terminal"
    _CMD_EXIT_CONFIG = "exit"
    _CMD_MORE = " "
    _CMD_CANCEL_MORE = "terminal length 0"
    _DEFAULT_RETURN = '\n'
    _DEFAULT_VSYS = "default"
    _CANCEL_MORE_VSYS = _DEFAULT_VSYS
    _CANCEL_MORE_MODE = Mode.ENABLE
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE, Mode.LOGIN]

    @abc.abstractmethod
    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        """ Implementations, defined by Plugin """
        raise NotImplementedError("Method get_mode_prompt_patterns not implemented")

    @abc.abstractmethod
    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        """ Implementations, defined by Plugin """
        raise NotImplementedError("Method get_more_pattern not implemented")

    @abc.abstractmethod
    def get_union_pattern(self) -> re.Pattern:
        """ Implementations, defined by Plugin """
        raise NotImplementedError("Method get_union_pattern not implemented")

    @abc.abstractmethod
    def get_error_patterns(self) -> list[re.Pattern]:
        """ Implementations, defined by Plugin """
        raise NotImplementedError("Method get_error_patterns not implemented")

    @abc.abstractmethod
    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        """ Implementations, defined by Plugin """
        raise NotImplementedError("Method get_ignore_error_patterns not implemented")

    def decide_current_mode(self, prompt: str):
        self._logger.info(f"Deciding [{prompt}] mode")
        pattern_modes = self.get_mode_prompt_patterns()
        for mode in self._SUPPORTED_MODES:
            mode_pattern = pattern_modes.get(mode)
            if mode_pattern and mode_pattern.search(prompt):
                self._mode = mode
                self._logger.info(f"Got mode: {mode} with lastline: {prompt}")
                return
        raise DetectCurrentModeFailed(f"Unknown mode, prompt: {prompt}")

    def decide_current_vsys(self, prompt: str):
        self._vsys = self._DEFAULT_VSYS
        self._logger.info(f"Got vsys: {self._vsys}")

    def get_default_return(self) -> str:
        return self._DEFAULT_RETURN

    def get_enable_password_prompt_pattern(self) -> re.Pattern:
        return None

    def get_auto_confirm_patterns(self) -> dict[re.Pattern, str]:
        return {}

    async def switch_mode(self, mode: Mode) -> str:
        """
        Switch to the target mode

        @param mode: target mode
        @raise UnsupportedMode: unsupported mode
        @raise EnableFailed: enable failed
        @raise DisableFailed: disable failed
        @raise ConfigFailed: config failed
        @raise ExitConfigFailed: exit config failed
        """
        self._logger.info(f"Switching mode: {self._mode} -> {mode}")
        output = ReadBuffer()
        if mode not in self._SUPPORTED_MODES:
            raise UnsupportedMode(f"Unsupported mode: {mode}")
        if not self._mode:
            raise UnsupportedMode("Current mode is None")

        while self._mode != mode:
            match self._mode:
                case Mode.LOGIN:
                    # login -> enable
                    output.append(await self.enable())
                case Mode.ENABLE:
                    if mode == Mode.LOGIN:
                        # enable -> login
                        output.append(await self.disable())
                    elif mode == Mode.CONFIG:
                        # enable -> config
                        output.append(await self.config())
                case Mode.CONFIG:
                    # config -> enable
                    output.append(await self.exit_config())
        self._logger.info(f"Switched mode to {self._mode}")
        return output.get_data()

    async def switch_vsys(self, vsys: str) -> str:
        if vsys != self._DEFAULT_VSYS:
            self._logger.warning("Not support vsys, ignore")
        self._vsys = vsys
        return ""

    @async_timeout(5)
    async def enable(self) -> str:
        """ Enter enable mode """

        self._logger.info("Enabling")
        pattern_enable_password = self.get_enable_password_prompt_pattern()
        pattern_modes = self.get_mode_prompt_patterns()
        pattern_login = pattern_modes.get(Mode.LOGIN)
        pattern_enable = pattern_modes.get(Mode.ENABLE)

        await self.write_channel(self._CMD_ENABLE)
        output = ReadBuffer(self._CMD_ENABLE)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_enable and output.check_pattern(pattern_enable, False):
                    self._mode = Mode.ENABLE
                    self._logger.info("Enable success")
                    break
                if pattern_login and output.check_pattern(pattern_login, False):
                    self._logger.info("enable failed, got login prompt")
                    raise EnableFailed("Enable failed, got login prompt", output=output.get_data())
                if pattern_enable_password and output.check_pattern(pattern_enable_password):
                    self._logger.info("Got enable password prompt, sending password")
                    await self.write_channel(self.enable_password or '')
        except EnableFailed as e:
            raise e
        except Exception as e:
            raise EnableFailed(msg=str(e), output=output.get_data()) from e
        return output.get_data()

    @async_timeout(5)
    async def disable(self) -> str:
        """ Exit enable mode

        @raise DisableFailed: disable failed
        """
        self._logger.info("Disabling")
        pattern_modes = self.get_mode_prompt_patterns()
        pattern_login = pattern_modes.get(Mode.LOGIN)
        pattern_enable = pattern_modes.get(Mode.ENABLE)

        await self.write_channel(self._CMD_DISABLE)
        output = ReadBuffer(self._CMD_DISABLE)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_login and output.check_pattern(pattern_login, False):
                    self._mode = Mode.LOGIN
                    self._logger.info("Disable success")
                    break
                if pattern_enable and output.check_pattern(pattern_enable):
                    self._logger.info("Disable failed, got enable prompt")
                    raise DisableFailed("Disable failed, got enable prompt", output=output.get_data())
        except DisableFailed as e:
            raise e
        except Exception as e:
            raise DisableFailed(msg=str(e), output=output.get_data()) from e
        return output.get_data()

    @async_timeout(5)
    async def config(self) -> str:
        """ Enter config mode

        @raise ConfigFailed: config failed
        """
        self._logger.info("Entering config mode")
        pattern_modes = self.get_mode_prompt_patterns()
        pattern_config = pattern_modes.get(Mode.CONFIG)
        pattern_enable = pattern_modes.get(Mode.ENABLE)

        await self.write_channel(self._CMD_CONFIG)
        output = ReadBuffer(cmd=self._CMD_CONFIG)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_config and output.check_pattern(pattern_config, False):
                    self._mode = Mode.CONFIG
                    self._logger.info("Entered config mode")
                    break
                if pattern_enable and output.check_pattern(pattern_enable):
                    self._logger.info("Config failed, got enable prompt")
                    raise ConfigFailed("Config failed, got enable prompt", output=output.get_data())
        except ConfigFailed as e:
            raise e
        except Exception as e:
            raise ConfigFailed(msg=str(e), output=output.get_data()) from e
        return output.get_data()

    @async_timeout(5)
    async def exit_config(self) -> str:
        """ Exit config mode

        @raise ExitConfigFailed: exit config failed
        """
        self._logger.info("Exiting config mode")
        pattern_modes = self.get_mode_prompt_patterns()
        pattern_enable = pattern_modes.get(Mode.ENABLE)
        pattern_config = pattern_modes.get(Mode.CONFIG)

        await self.write_channel(self._CMD_EXIT_CONFIG)
        output = ReadBuffer(cmd=self._CMD_EXIT_CONFIG)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_enable and output.check_pattern(pattern_enable, False):
                    self._mode = Mode.ENABLE
                    self._logger.info("Exited config mode")
                    break
                if pattern_config and output.check_pattern(pattern_config):
                    self._logger.info("Exit config failed, got config prompt")
                    raise ExitConfigFailed("Exit config failed, got config prompt", output=output.get_data())
        except ExitConfigFailed as e:
            raise e
        except Exception as e:
            raise ExitConfigFailed(msg=str(e), output=output) from e
        return output.get_data()

    async def disable_pagging(self):
        self._logger.info("Disabling paging")
        await self.exec_cmd_in_vsys_and_mode(self._CMD_CANCEL_MORE, vsys=self._CANCEL_MORE_VSYS,
                                             mode=self._CANCEL_MORE_MODE)

    async def save(self, command: str) -> str:
        """ Handle save command """
        self._logger.info(f"Exec [{command}] by save func.")
        await self.write_channel(command)
        return await self._handle_auto_confirms(cmd=command)