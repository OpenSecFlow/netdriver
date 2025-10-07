#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class VenustechBase(Base):
    """ Venustech Base Plugin """

    info = PluginInfo(
        vendor="venustech",
        model="base",
        version="base",
        description="Venustech Base Plugin"
    )

    def get_union_pattern(self) -> re.Pattern:
        return VenustechBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return VenustechBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return VenustechBase.PatternHelper.get_ignore_error_patterns()

    def get_enable_password_pattern(self) -> re.Pattern:
        return VenustechBase.PatternHelper.get_enable_password_prompt_pattern()

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (VenustechBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    async def disable_pagging(self):
        self._logger.warning("Venustech not support pagination command")

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: VenustechBase.PatternHelper.get_login_prompt_pattern(),
            Mode.ENABLE: VenustechBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: VenustechBase.PatternHelper.get_config_prompt_pattern()
        }

    class PatternHelper:
        """ Inner class for patterns """
        # hostname>
        _PATTERN_LOGIN = r"^\r{0,1}[^\s<]+>\s*$"
        # hostname#
        _PATTERN_ENABLE = r"^\r{0,1}[^\s#]+#\s*$"
        # hostname(config)#
        _PATTERN_CONFIG = r"^\r{0,1}\S+\(\S+\)#\s*$"
        # --More-- (7% of 13459 bytes)
        _PATTERN_MORE = r"--More-- \(\d+% of \d+ bytes\)"
        _PATTERN_ENABLE_PASSWORD = r"(Enable )?Password:"

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            return re.compile(VenustechBase.PatternHelper._PATTERN_LOGIN, re.MULTILINE)

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(VenustechBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(VenustechBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile(
                "(?P<login>{})|(?P<config>{})|(?P<enable>{})".format(
                    VenustechBase.PatternHelper._PATTERN_LOGIN,
                    VenustechBase.PatternHelper._PATTERN_CONFIG,
                    VenustechBase.PatternHelper._PATTERN_ENABLE
                ),
                re.MULTILINE
            )

        @staticmethod
        def get_enable_password_prompt_pattern() -> re.Pattern:
            return re.compile(VenustechBase.PatternHelper._PATTERN_ENABLE_PASSWORD, re.MULTILINE)
        
        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(VenustechBase.PatternHelper._PATTERN_MORE, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"^%.+",
                r".+not exist!"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_sts = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_sts]
