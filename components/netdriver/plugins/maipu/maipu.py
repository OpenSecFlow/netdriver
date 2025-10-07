#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base

# pylint: disable=abstract-method
class MaiPuBase(Base):
    """ MaiPu Base Plugin """

    info = PluginInfo(
        vendor="maipu",
        model="base",
        version="base",
        description="MaiPu Base Plugin"
    )

    _CMD_CANCEL_MORE = "more off"

    def get_union_pattern(self) -> re.Pattern:
        return MaiPuBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return MaiPuBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return MaiPuBase.PatternHelper.get_ignore_error_patterns()

    def get_enable_password_pattern(self) -> re.Pattern:
        return MaiPuBase.PatternHelper.get_enable_password_prompt_pattern()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: MaiPuBase.PatternHelper.get_login_prompt_pattern(),
            Mode.ENABLE: MaiPuBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: MaiPuBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (MaiPuBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # hostname> $
        _PATTERN_LOGIN = r"^\r{0,1}[^\s<]+>\s*$"
        # hostname# $
        _PATTERN_ENABLE = r"^\r{0,1}[^\s#]+#\s*$"
        # hostname(config)# $
        _PATTERN_CONFIG = r"^\r{0,1}\S+\(\S+\)#\s*$"
        _PATTERN_ENABLE_PASSWORD = r"password:"

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            return re.compile(MaiPuBase.PatternHelper._PATTERN_LOGIN, re.MULTILINE)

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(MaiPuBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(MaiPuBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile(
                "(?P<login>{})|(?P<config>{})|(?P<enable>{})".format(
                    MaiPuBase.PatternHelper._PATTERN_LOGIN,
                    MaiPuBase.PatternHelper._PATTERN_CONFIG,
                    MaiPuBase.PatternHelper._PATTERN_ENABLE
                ),
                re.MULTILINE
            )

        @staticmethod
        def get_enable_password_prompt_pattern() -> re.Pattern:
            return re.compile(MaiPuBase.PatternHelper._PATTERN_ENABLE_PASSWORD, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"% Invalid input"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_sts = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_sts]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return None
