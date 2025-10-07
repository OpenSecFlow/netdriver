#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class JuniperBase(Base):
    """ Juniper Base Plugin """

    info = PluginInfo(
        vendor="juniper",
        model="base",
        version="base",
        description="Juniper Base Plugin"
    )

    _CMD_CONFIG = "configure private"
    _CMD_EXIT_CONFIG = "exit"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return JuniperBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return JuniperBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return JuniperBase.PatternHelper.get_ignore_error_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: JuniperBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: JuniperBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_auto_confirm_patterns(self) -> dict[re.Pattern, str]:
        return JuniperBase.PatternHelper.get_auto_confirm_patterns()

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (JuniperBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    async def disable_pagging(self):
        self._logger.warning("Juniper not support pagination command")

    class PatternHelper:
        """ Inner class for patterns """
        # user@hostname>
        _PATTERN_ENABLE = r"^\r{0,1}\S+@\S+>\s*$"
        # user@hostname#
        _PATTERN_CONFIG = r"^\r{0,1}\S+@\S+#\s*$"
        # ---(more)---,---(more 23%)---
        _PATTERN_MORE = r"---\(more( \d+%)?\)---"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(JuniperBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(JuniperBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                JuniperBase.PatternHelper._PATTERN_ENABLE,
                JuniperBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r".*unknown command.*",
                r"syntax error.*",
                r"error:.+",
                r".+not found.*",
                r"invalid value .+",
                r"invalid ip address .+",
                r".*invalid prefix length .+",
                r"prefix length \S+ is larger than \d+ .+",
                r"number: \S+: Value must be a number from 0 to 255 at \S+",
                r"\s+\^$"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"warning: statement not found",
                r"warning: element \S+ not found"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_auto_confirm_patterns() -> dict[re.Pattern, str]:
            return {
                re.compile(r"Exit with uncommitted changes? [yes,no] (yes) ", re.MULTILINE): "yes"
            }
        
        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(JuniperBase.PatternHelper._PATTERN_MORE, re.MULTILINE)