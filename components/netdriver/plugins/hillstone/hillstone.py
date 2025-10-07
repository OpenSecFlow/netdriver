#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class HillstoneBase(Base):
    """ Hillstone Base Plugin """

    info = PluginInfo(
        vendor="hillstone",
        model="base",
        version="base",
        description="Hillstone Base Plugin"
    )

    _CMD_CONFIG = "configure"
    _CMD_EXIT_CONFIG = "end"
    _CMD_CANCEL_MORE = "terminal length 0"
    _SUPPORTED_MODES = [Mode.CONFIG, Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return HillstoneBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return HillstoneBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return HillstoneBase.PatternHelper.get_ignore_error_patterns()
    
    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: HillstoneBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: HillstoneBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_auto_confirm_patterns(self) -> dict[re.Pattern, str]:
        return HillstoneBase.PatternHelper.get_auto_confirm_patterns()
    
    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (HillstoneBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    async def _decide_init_state(self) -> str:
        """ Decide init state
        @override
        @throws DetectCurrentModeFailed
        """
        # in case of previoius cmd failed and left in config mode
        if self._mode == Mode.CONFIG:
            await self.write_channel(self._CMD_EXIT_CONFIG)
        prompt = await self._get_prompt()
        self.decide_current_mode(prompt)
        self.decide_current_vsys(prompt)
        return prompt

    async def save(self, command: str) -> str:
        """ Handle save command """
        self._logger.info(f"Exec [{command}] by save func.")
        await self.write_channel(command)
        return await self._handle_auto_confirms(cmd=command, auto_enter=False) 

    class PatternHelper:
        """ Inner class for patterns """
        # hostname# 
        _PATTERN_ENABLE = r"^\r{0,1}.+#\s\r{0,1}$"
        # hostname(config)# 
        _PATTERN_CONFIG = r"^\r{0,1}.+\(config.*\)#\s\r{0,1}$"
        #  --More-- 
        _PATTERN_MORE = r" --More-- "

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(HillstoneBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile(HillstoneBase.PatternHelper._PATTERN_CONFIG, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<config>{})".format(
                HillstoneBase.PatternHelper._PATTERN_ENABLE,
                HillstoneBase.PatternHelper._PATTERN_CONFIG
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"\s+\^-+.+",
                r"Error:.+",
                r"错误：.+"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs =  [
                r"Error: Schedule entity (.+) is not found",
                r"错误：没有找到时间表(.+)",
                r"Error: Failed to find this service",
                r"错误: 无法找到服务",
                r"Error: Rule (\d+) is not found$",
                r"错误：规则(\d+)不存在",
                r"Error: This service already exists",
                r"错误：该服务已经添加",
                r"Error: Rule is already configured with schedule (.+)",
                r"错误：此规则已经配置了时间表\"(.+)\"",
                r"Error: Rule is not configured with schedule (.+)",
                r"错误：此规则没有配置时间表\"(.+)\"",
                r"Error: This entity is already added",
                r"错误：该项已经添加",
                r"Error: This entity already exists",
                r"错误: 该成员已经存在",
                r"Error: Cannot find this service entity",
                r"错误：查找该服务条目失败!",
                r"Error: Address entry (.+) has no member (.+)",
                r"错误：地址条目(.+)没有成员(.+)",
                r"Error: Address (?!.*as\b)(.+) is not found",
                r"错误：地址簿(.+)没有找到",
                r"Error: Deleting a service not configured",
                r"错误：尝试删除一个没有配置的服务"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]
        
        @staticmethod
        def get_auto_confirm_patterns() -> dict[re.Pattern, str]:
            return {
                re.compile(r"Save configuration, are you sure\? \[y\]\/n: ", re.MULTILINE): "y",
                re.compile(r"Save configuration for all VSYS, are you sure\? \[y\]\/n: ", re.MULTILINE): "y",
                re.compile(r"Backup start configuration file, are you sure\? y\/\[n\]: ", re.MULTILINE): "y",
                re.compile(r"Backup all start configuration files, are you sure\? y\/\[n\]: ", re.MULTILINE): "y",
                re.compile(r"保存配置，请确认 \[y\]\/n: ", re.MULTILINE): "y",
                re.compile(r"备份启动配置文件，请确认 y\/\[n\]: ", re.MULTILINE): "y",
                re.compile(r"保存所有VSYS的配置，请确认 \[y\]\/n: ", re.MULTILINE): "y",
                re.compile(r"备份所有启动配置文件，请确认 y\/\[n\]: ", re.MULTILINE): "y"
            }

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(HillstoneBase.PatternHelper._PATTERN_MORE, re.MULTILINE)
 