#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class CheckPointBase(Base):
    """ CheckPoint Base Plugin """

    info = PluginInfo(
        vendor="check point",
        model="base",
        version="base",
        description="CheckPoint Base Plugin"
    )

    _CMD_CANCEL_MORE = "set clienv rows 0"
    _SUPPORTED_MODES = [Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return CheckPointBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return CheckPointBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return CheckPointBase.PatternHelper.get_ignore_error_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: CheckPointBase.PatternHelper.get_enable_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (CheckPointBase.PatternHelper.get_more_pattern, self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # hostname>
        _PATTERN_ENABLE = r"^\r{0,1}\S+\s*>\s*$"
        # -- More --
        _PATTERN_MORE = r"-- More --"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(CheckPointBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})".format(
                CheckPointBase.PatternHelper._PATTERN_ENABLE
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r".+Incomplete command\.",
                r".+Invalid command:.+"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(CheckPointBase.PatternHelper._PATTERN_MORE, re.MULTILINE)