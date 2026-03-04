#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from netdriver_core.dev.mode import Mode
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.base import Base


class LeadsecBase(Base):
    """ Leadsec Base Session """

    info = PluginInfo(
        vendor="leadsec",
        model="base",
        version="base",
        description="Leadsec Base Plugin"
    )

    _SUPPORTED_MODES = [Mode.LOGIN]
    
    def get_union_pattern(self):
        return LeadsecBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return LeadsecBase.PatternHelper.get_error_patterns()
    
    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return LeadsecBase.PatternHelper.get_ignore_error_patterns()
    
    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return LeadsecBase.PatternHelper.get_more_pattern()
    
    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: LeadsecBase.PatternHelper.get_login_prompt_pattern()
        }

    async def disable_pagging(self):
        self._logger.warning("Leadsec not support pagination command")

    class PatternHelper:
        """ Inner class for patterns """
        # hostname# or hostname%
        _PATRTERN_LOGIN = r"^\r{0,1}[a-zA-Z0-9]+>$"

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            """ Get login prompt pattern """
            return re.compile(LeadsecBase.PatternHelper._PATRTERN_LOGIN, re.MULTILINE)
        
        @staticmethod
        def get_union_pattern() -> re.Pattern:
            """ Get union pattern """
            return re.compile("(?P<login>{})".format(
                LeadsecBase.PatternHelper._PATRTERN_LOGIN
            ), re.MULTILINE)
        
        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"^\^\s.*",
                r"错误：?:?\s?.*",
                r"unknown keyword",
                r"\S*存在",
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            return []

        @staticmethod
        def get_auto_confirm_patterns() -> dict[re.Pattern, str]:
            return {}

        @staticmethod
        def get_more_pattern() -> tuple[re.Pattern, str]:
            return (None, ' ')
