#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from netdriver.client.channel import ReadBuffer
from netdriver.client.mode import Mode
from netdriver.exception.errors import EnableFailed
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base
from netdriver.utils.asyncu import async_timeout


# pylint: disable=abstract-method
class CiscoBase(Base):
    """ Cisco Base Plugin """

    info = PluginInfo(
        vendor="cisco",
        model="base",
        version="base",
        description="Cisco Base Plugin"
    )

    def get_union_pattern(self) -> re.Pattern:
        return CiscoBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return CiscoBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return CiscoBase.PatternHelper.get_ignore_error_patterns()

    def get_enable_password_prompt_pattern(self) -> re.Pattern:
        return CiscoBase.PatternHelper.get_enable_password_prompt_pattern()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: CiscoBase.PatternHelper.get_login_prompt_pattern(),
            Mode.ENABLE: CiscoBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: CiscoBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (CiscoBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    @async_timeout(5)
    async def enable(self) -> str:
        """ Enter enable mode """

        self._logger.info("Enabling")
        pattern_enable_password = CiscoBase.PatternHelper.get_enable_password_prompt_pattern()
        pattern_login = CiscoBase.PatternHelper.get_login_prompt_pattern()
        pattern_enable = CiscoBase.PatternHelper.get_enable_prompt_pattern()

        await self.write_channel(self._CMD_ENABLE)
        output = ReadBuffer(self._CMD_ENABLE)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_enable and output.check_pattern(pattern_enable, False):
                    self._mode = Mode.ENABLE
                    self._logger.info("Enable success")
                    # disable page, because after existing enable mode
                    # page will be enabled again
                    await self.disable_pagging()
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

    class PatternHelper:
        """ Inner class for patterns """
        # ^hostname> $
        _PATTERN_LOGIN = r"^\r{0,1}[^\s<]+>\s*$"
        # ^hostname# $
        _PATTERN_ENABLE = r"^\r{0,1}[^\s#]+#\s*$"
        # ^hostname(config)# $
        _PATTERN_CONFIG = r"^\r{0,1}\S+\(\S+\)#\s*$"
        _PATTERN_ENABLE_PASSWORD = r"(Enable )?Password:"
        # <--- More --->
        _PATTERN_MORE = r"<--- More --->"

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            return re.compile(CiscoBase.PatternHelper._PATTERN_LOGIN, re.MULTILINE)

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(CiscoBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(CiscoBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile(
                "(?P<login>{})|(?P<config>{})|(?P<enable>{})".format(
                    CiscoBase.PatternHelper._PATTERN_LOGIN,
                    CiscoBase.PatternHelper._PATTERN_CONFIG,
                    CiscoBase.PatternHelper._PATTERN_ENABLE
                ),
                re.MULTILINE
            )

        @staticmethod
        def get_enable_password_prompt_pattern() -> re.Pattern:
            return re.compile(CiscoBase.PatternHelper._PATTERN_ENABLE_PASSWORD, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"% Invalid command at '\^' marker\.",
                r"% Invalid parameter detected at '\^' marker\.",
                r"invalid vlan \(reserved value\) at '\^' marker\.",
                r"ERROR: VLAN \d+ is not a primary vlan",
                r"\^$",
                r"^%.+",
                r"^Command authorization failed.*",
                r"^Command rejected:.*"
                r"ERROR:.+",
                r"Invalid password",
                r"Access denied.",
                r"End address less than start address"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_sts = [
                r"ERROR: object \(.+\) does not exist."
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_sts]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(CiscoBase.PatternHelper._PATTERN_MORE, re.MULTILINE)