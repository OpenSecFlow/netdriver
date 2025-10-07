#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class HuaweiBase(Base):
    """ Huawei Base Plugin """

    info = PluginInfo(
        vendor="huawei",
        model="base",
        version="base",
        description="Huawei Base Plugin"
    )

    _CMD_CONFIG = "system-view"
    _CMD_EXIT_CONFIG = "return"
    _CMD_CANCEL_MORE = "screen-length 0 temporary"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return HuaweiBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return HuaweiBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return HuaweiBase.PatternHelper.get_ignore_error_patterns()
    
    def get_auto_confirm_patterns(self) -> dict[str, re.Pattern]:
        return HuaweiBase.PatternHelper.get_auto_confirm_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: HuaweiBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: HuaweiBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (HuaweiBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    async def _decide_init_state(self) -> str:
        """ Decide init state
        @override
        @throws DetectCurrentModeFailed
        """
        # prevent the last execution error from not exiting
        await self.write_channel(self._CMD_EXIT_CONFIG)
        prompt = await self._get_prompt()

        # keep decide vsys before decide mode
        self.decide_current_vsys(prompt)
        self.decide_current_mode(prompt)
        return prompt

    class PatternHelper:
        """ Inner class for patterns """
        # HRP_M<hostname-vsys>
        _PATTERN_ENABLE = r"^\r{0,1}(HRP_M|HRP_S){0,1}<.+>\s*$"
        # HRP_S[hostname-vsys-config-config]
        _PATTERN_CONFIG = r"^\r{0,1}(HRP_M|HRP_S){0,1}\[.+\]\s*$"
        #   ---- More ----
        _PATTERN_MORE = r"  ---- More ----"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(HuaweiBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(HuaweiBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                HuaweiBase.PatternHelper._PATTERN_ENABLE,
                HuaweiBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"Error: .+$",
                r"\^$",
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                # Address
                r"Error: Address item conflicts!",
                r"Error: The address item does not exist!",
                r"Error: The delete configuration does not exist.",
                r"Error: The address or address set is not created!",
                # Service
                r"Error: Cannot add! Service item conflicts or illegal reference!",
                r"Error: The service item does not exist!",
                r"Error: Service item conflicts!",
                r"Error: The service item does not exist!",
                r"Error: The service set is not created(.+)!",
                # Schedule
                r"Error: No such a time-range.",
                # NAT
                r"Error: The specified address-group does not exist.",
                r"Error: The specified rule does not exist yet.",
                # NetD
                r"This condition has already been configured",
                r"[a-zA-Z]* (item conflicts|Service item exists\.)",
                r"Error: Worng parameter found at.*"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
        
        @staticmethod
        def get_auto_confirm_patterns() -> dict[re.Pattern, str]:
            return {
                re.compile(r"Are you sure to continue\?\[Y\/N\]: ", re.MULTILINE): "Y",
                re.compile(r"startup saved-configuration file on peer device\?\[Y\/N\]: ", re.MULTILINE): "Y",
                re.compile(r"Warning: The current configuration will be written to the device. Continue? \[Y\/N\]: ", re.MULTILINE): "Y",
            }
        
        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(HuaweiBase.PatternHelper._PATTERN_MORE, re.MULTILINE)
