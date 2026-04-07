#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver_core.dev.mode import Mode
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult
from netdriver_agent.plugins.base import Base
from netdriver_textfsm import TextFSMParser


# pylint: disable=abstract-method
class TopSecBase(Base):
    """ TopSec Base Plugin """

    info = PluginInfo(
        vendor="topsec",
        model="base",
        version="base",
        description="TopSec Base Plugin"
    )

    _SUPPORTED_MODES = [Mode.ENABLE]

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

    @classmethod
    def get_probe_command(cls) -> str:
        return "show version\nshow hostname"

    @classmethod
    def parse_probe_output(cls, output: str) -> ProbeResult:
        rows = TextFSMParser(cls._PROBE_TEMPLATE).parse(output)
        row = rows[0] if rows else {}
        return ProbeResult(
            vendor="topsec",
            model=row.get("MODEL", ""),
            version=row.get("VERSION", ""),
            hostname=row.get("HOSTNAME", ""),
            serial_number=row.get("SERIAL", ""),
        )

    _PROBE_TEMPLATE = """\
Value HOSTNAME (\\S+)
Value MODEL (NGFW\\d+\\S*|TOS\\s*\\S+)
Value VERSION ([0-9A-Za-z.]+)
Value SERIAL (\\S+)

Start
  ^[Hh]ostname\\s*:\\s*${HOSTNAME} -> Continue
  ^${HOSTNAME}\\s*$ -> Continue
  ^\\s*${MODEL}\\s -> Continue
  ^\\s*[Vv]ersion\\s+${VERSION} -> Continue
  ^\\s*[Ss]erial\\s+[Nn]umber\\s*:\\s*${SERIAL} -> Continue
"""
