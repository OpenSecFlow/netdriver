#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class DptechBase(Base):
    """ Dptech Base Plugin """

    info = PluginInfo(
        vendor="dptech",
        model="base",
        version="base",
        description="Dptech Base Plugin"
    )

    _CMD_CONFIG = "conf-mode"
    _CMD_EXIT_CONFIG = "end"
    _CMD_CANCEL_MORE = "language-mode chinese\nterminal line 0"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return DptechBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return DptechBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return DptechBase.PatternHelper.get_ignore_error_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: DptechBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: DptechBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        """ Get more pattern """
        return (DptechBase.PatternHelper.get_more_pattern(), self._CMD_MORE)
    
    class PatternHelper:
        """ Inner class for patterns """
        # <hostname>
        _PATTERN_ENABLE = r"^\r{0,1}<.+>\s*$"
        # [hostname]
        _PATTERN_CONFIG = r"^\r{0,1}\[.+\]\s*$"
        # --More(CTRL+C break)-- 
        _PATTERN_MORE = r" --More(CTRL+C break)-- "

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(DptechBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(DptechBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                DptechBase.PatternHelper._PATTERN_ENABLE,
                DptechBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"% Unknown command.*",
                r"Can't find the .+ object",
                r".*not exist.*",
                r".*item is longer.*",
                r"Failed.*",
                r"Undefined error.*",
                r"% Command can not contain:.+",
                r"Invalid parameter.*",
                r"% Ambiguous command."
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs =  []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(DptechBase.PatternHelper._PATTERN_MORE, re.MULTILINE)