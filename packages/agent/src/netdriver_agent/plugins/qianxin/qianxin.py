#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver_core.dev.mode import Mode
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult
from netdriver_agent.plugins.base import Base
from netdriver_textfsm import TextFSMParser


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
            await self.write_channel(self._CMD_EXIT_CONFIG)
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

    @classmethod
    def get_probe_command(cls) -> str:
        return "show version\nshow hostname"

    @classmethod
    def parse_probe_output(cls, output: str) -> ProbeResult:
        rows = TextFSMParser(cls._PROBE_TEMPLATE).parse(output)
        row = rows[0] if rows else {}
        return ProbeResult(
            vendor="qianxin",
            model=row.get("MODEL", ""),
            version=row.get("VERSION", ""),
            hostname=row.get("HOSTNAME", ""),
            serial_number=row.get("SERIAL", ""),
        )

    _PROBE_TEMPLATE = """\
Value HOSTNAME (\\S+)
Value MODEL (NSG\\d+\\S*)
Value VERSION ([0-9A-Za-z.]+)
Value SERIAL (\\S+)

Start
  ^[Hh]ostname\\s*:\\s*${HOSTNAME} -> Continue
  ^${HOSTNAME}\\s*$ -> Continue
  ^\\s*${MODEL}\\s -> Continue
  ^\\s*[Vv]ersion\\s+${VERSION} -> Continue
  ^\\s*[Ss]erial\\s+[Nn]umber\\s*:\\s*${SERIAL} -> Continue
"""