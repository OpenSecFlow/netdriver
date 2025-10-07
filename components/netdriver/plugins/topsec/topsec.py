#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class TopSecBase(Base):
    """ TopSec Base Plugin """

    info = PluginInfo(
        vendor="topsec",
        model="base",
        version="base",
        description="TopSec Base Plugin"
    )

    SUPPORTED_MODES = [Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return TopSecBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return TopSecBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return TopSecBase.PatternHelper.get_ignore_error_patterns()

    async def disable_pagging(self):
        self._logger.warning("TopSec not support pagination command")

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (TopSecBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: TopSecBase.PatternHelper.get_enable_prompt_pattern()
        }
    
    class PatternHelper:
        """ Inner class for patterns """
        # hostname# or hostname%
        _PATTERN_ENABLE = r"^\r{0,1}\S+[#%]\s*$"
        # --More--
        _PATTERN_MORE = r"--More--"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(TopSecBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})".format(
                TopSecBase.PatternHelper._PATTERN_ENABLE
            ), re.MULTILINE)

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(TopSecBase.PatternHelper._PATTERN_MORE, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"^error"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
