#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class ChaiTinBase(Base):
    """ ChaiTin Base Plugin """

    info = PluginInfo(
        vendor="chaitin",
        model="base",
        version="base",
        description="ChaiTin Base Plugin"
    )

    def get_union_pattern(self) -> re.Pattern:
        return ChaiTinBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return ChaiTinBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return ChaiTinBase.PatternHelper.get_ignore_error_patterns()

    def get_enable_password_prompt_pattern(self) -> re.Pattern:
        return ChaiTinBase.PatternHelper.get_enable_password_prompt_pattern()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: ChaiTinBase.PatternHelper.get_login_prompt_pattern(),
            Mode.ENABLE: ChaiTinBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: ChaiTinBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (ChaiTinBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # hostname>
        _PATTERN_LOGIN = r"^\r{0,1}[^\s<]+>\s*$"
        # hostname#
        _PATTERN_ENABLE = r"^\r{0,1}[^\s#]+#\s*$"
        # hostname(config)#
        _PATTERN_CONFIG = r"^\r{0,1}\S+\(\S+\)#\s*$"
        _PATTERN_ENABLE_PASSWORD = r"(Enable )?Password:"

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            return re.compile(ChaiTinBase.PatternHelper._PATTERN_LOGIN, re.MULTILINE)

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(ChaiTinBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(ChaiTinBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile(
                "(?P<login>{})|(?P<config>{})|(?P<enable>{})".format(
                    ChaiTinBase.PatternHelper._PATTERN_LOGIN,
                    ChaiTinBase.PatternHelper._PATTERN_CONFIG,
                    ChaiTinBase.PatternHelper._PATTERN_ENABLE
                ),
                re.MULTILINE
            )

        @staticmethod
        def get_enable_password_prompt_pattern() -> re.Pattern:
            return re.compile(ChaiTinBase.PatternHelper._PATTERN_ENABLE_PASSWORD, re.MULTILINE)

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return None

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"% Command incomplete",
                r"% Unknown command",
                r"Error:.*"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_sts = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_sts]