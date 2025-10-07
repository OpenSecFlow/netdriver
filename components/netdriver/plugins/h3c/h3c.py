#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class H3CBase(Base):
    """ H3C Base Plugin """

    info = PluginInfo(
        vendor="h3c",
        model="base",
        version="base",
        description="H3C Base Plugin"
    )

    _CMD_CONFIG = "system-view"
    _CMD_EXIT_CONFIG = "return"
    _CMD_CANCEL_MORE = "screen-length disable"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return H3CBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return H3CBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return H3CBase.PatternHelper.get_ignore_error_patterns()

    def get_auto_confirm_patterns(self) -> dict[str, re.Pattern]:
        return H3CBase.PatternHelper.get_auto_confirm_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: H3CBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: H3CBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (H3CBase.PatternHelper.get_more_pattern(), self._CMD_MORE)
    
    async def _decide_init_state(self) -> str:
        """ Decide init state
        @override
        @throws DetectCurrentModeFailed
        """
        if self._mode == Mode.CONFIG:
            await self.write_channel(self._CMD_EXIT_CONFIG)
        prompt = await self._get_prompt()
        self.decide_current_mode(prompt)
        self.decide_current_vsys(prompt)
        return prompt

    class PatternHelper:
        """ Inner class for patterns """
        # <hostname>
        _PATTERN_ENABLE = r"^\r{0,1}(RBM_P|RBM_S)?<.+>\s*$"
        # [hostname]
        _PATTERN_CONFIG = r"^\r{0,1}(RBM_P|RBM_S)?\[.+\]\s*$"
        # ---- More ----
        _PATTERN_MORE = r"---- More ----"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(H3CBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(H3CBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                H3CBase.PatternHelper._PATTERN_ENABLE,
                H3CBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r".+\^.+",
                r".+%.+",
                r".+doesn't exist.+",
                r".+does not exist.+",
                r"Object group with given name exists with different type."
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
        
        @staticmethod
        def get_auto_confirm_patterns() -> dict[str, re.Pattern]:
            return {
                re.compile(r"The current configuration will be written to the device. Are you sure? \[Y\/N\]:", re.MULTILINE): "Y",
                re.compile(r"\(To leave the existing filename unchanged, press the enter key\):", re.MULTILINE): "",
                re.compile(r"flash:/startup.cfg exists, overwrite? \[Y\/N\]:", re.MULTILINE): "Y",
                re.compile(r"Are you sure you want to continue the save operation? \[Y\/N\]:", re.MULTILINE): "Y"
            }

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(H3CBase.PatternHelper._PATTERN_MORE, re.MULTILINE)
