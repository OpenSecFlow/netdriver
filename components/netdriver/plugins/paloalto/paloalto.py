#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class PaloaltoBase(Base):
    """ Paloalto Base Plugin """

    info = PluginInfo(
        vendor="paloalto",
        model="base",
        version="base",
        description="Paloalto Base Plugin"
    )

    _CMD_CONFIG = "configure"
    _CMD_EXIT_CONFIG = "exit"
    _CMD_CANCEL_MORE = "set cli pager off"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return PaloaltoBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return PaloaltoBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return PaloaltoBase.PatternHelper.get_ignore_error_patterns()

    def get_auto_confirm_patterns(self) -> dict[str, re.Pattern]:
        return PaloaltoBase.PatternHelper.get_auto_confirm_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: PaloaltoBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: PaloaltoBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (PaloaltoBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # user@hostname>
        _PATTERN_ENABLE = r"^\r{0,1}\S+@\S+>\s*$"
        # user@hostname#
        _PATTERN_CONFIG = r"^\r{0,1}\S+@\S+#\s*$"
        # --more--,lines 43-84 
        _PATTERN_MORE = r"(--more--)|(lines \d+-\d+ )"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(PaloaltoBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(PaloaltoBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                PaloaltoBase.PatternHelper._PATTERN_ENABLE,
                PaloaltoBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"Unknown command:.*",
                r"Invalid syntax.",
                r"Server error:.*",
                r"Validation Error:.*",
                r"Commit failed"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
        
        @staticmethod
        def get_auto_confirm_patterns() -> dict[re.Pattern, str]:
            return {
                re.compile(r"Would you like to proceed with commit\? \(y or n\) Please type \"y\" for yes or \"n\" for no\.", re.MULTILINE): "y",
            }

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(PaloaltoBase.PatternHelper._PATTERN_MORE, re.MULTILINE)
