#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class QiAnXinBase(Base):
    """ QiAnXin Base Plugin """

    info = PluginInfo(
        vendor="qianxin",
        model="base",
        version="base",
        description="QiAnXin Base Plugin"
    )

    _CMD_CONFIG = "config terminal"
    _CMD_EXIT_CONFIG = "end"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return QiAnXinBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return QiAnXinBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return QiAnXinBase.PatternHelper.get_ignore_error_patterns()

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (QiAnXinBase.PatternHelper.get_more_pattern(), QiAnXinBase._CMD_MORE)

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: QiAnXinBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: QiAnXinBase.PatternHelper.get_config_prompt_pattern()
        }

    async def disable_pagging(self):
        self._logger.warning("QiAnXin not support pagination command")

    async def _decide_init_state(self) -> str:
        """ Decide init state
        @override
        @throws DetectCurrentModeFailed
        """
        if self._mode == Mode.CONFIG:
            self.write_channel(self._CMD_EXIT_CONFIG)
        prompt = await self._get_prompt()
        self.decide_current_mode(prompt)
        self.decide_current_vsys(prompt)
        return prompt

    class PatternHelper:
        """ Inner class for patterns """
        # hostname#
        _PATTERN_ENABLE = r"^\S+>\s*$"
        # hostname(config)#
        _PATTERN_CONFIG = r"^\S+-config.*]\s*$"
        # --More--
        _PATTERN_MORE = r"--More--"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(QiAnXinBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(QiAnXinBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                QiAnXinBase.PatternHelper._PATTERN_ENABLE,
                QiAnXinBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(QiAnXinBase.PatternHelper._PATTERN_MORE, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"% Unknown command.",
                r"% Command incomplete.",
                r"%?\s+Invalid parameter.*",
                r"\s+Valid name can.*",
                r"\s+Repetitions with Object.*",
                r".+ exist",
                r"\s+Start larger than end",
                r"\s+Name can not repeat",
                r"Object .+ referenced by other module",
                r"Object service has been referenced",
                r"Object \[.+\] is quoted"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs =  []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
 