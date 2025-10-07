#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class FortinetBase(Base):
    """ Fortinet Base Plugin """

    info = PluginInfo(
        vendor="fortinet",
        model="base",
        version="base",
        description="Fortinet Base Plugin"
    )

    _CMD_CANCEL_MORE = "config system console\nset output standard\nend"
    _SUPPORTED_MODES = [Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return FortinetBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return FortinetBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return FortinetBase.PatternHelper.get_ignore_error_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: FortinetBase.PatternHelper.get_enable_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (FortinetBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    async def _decide_init_state(self) -> str:
        """ Decide init state """
        prompt = await self._get_prompt()
        vsys_pattern = FortinetBase.PatternHelper.get_vsys_pattern()
        vsys_match = None
        # prevent the last execution error from not exiting
        if vsys_pattern:
            vsys_match = vsys_pattern.search(prompt)
            if vsys_match and vsys_match.group(1) != self._vsys:
                self.write_channel("end")
                prompt = await self._get_prompt()
        # keep decide vsys before decide mode
        self.decide_current_vsys(prompt)
        self.decide_current_mode(prompt)
        return prompt

    class PatternHelper:
        """ Inner class for patterns """
        # hostname # 
        _PATTERN_ENABLE = r"^\r{0,1}\S+\s*#\s*$"
        # hostname (root) #
        _PATTERN_VSYS= r"^\r{0,1}\S+\s*\((\S+)\)\s*#\s*$"
        # --More--
        _PATTERN_MORE = r"--More--"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(FortinetBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_vsys_pattern() -> re.Pattern:
            return re.compile(FortinetBase.PatternHelper._PATTERN_VSYS, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<vsys>{})".format(
                FortinetBase.PatternHelper._PATTERN_ENABLE,
                FortinetBase.PatternHelper._PATTERN_VSYS
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"Unknown action.*",
                r"Command fail.*"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"delete table entry .+ unset oper error.*"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(FortinetBase.PatternHelper._PATTERN_MORE, re.MULTILINE)