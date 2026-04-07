#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver_core.dev.mode import Mode
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult
from netdriver_agent.plugins.base import Base
from netdriver_textfsm import TextFSMParser


# pylint: disable=abstract-method
class CheckPointBase(Base):
    """ CheckPoint Base Plugin """

    info = PluginInfo(
        vendor="check point",
        model="base",
        version="base",
        description="CheckPoint Base Plugin"
    )

    _CMD_CANCEL_MORE = "set clienv rows 0"
    _SUPPORTED_MODES = [Mode.ENABLE]

    def get_union_pattern(self) -> re.Pattern:
        return CheckPointBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return CheckPointBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return CheckPointBase.PatternHelper.get_ignore_error_patterns()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.ENABLE: CheckPointBase.PatternHelper.get_enable_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (CheckPointBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # hostname> or [Global] hostname> or [WARNING! Local Member] hostname>
        _PATTERN_ENABLE = r"^\r{0,1}(\[.+\])?\s*\S+\s*>\s*$"
        # -- More --
        _PATTERN_MORE = r"-- More --"

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile(CheckPointBase.PatternHelper._PATTERN_ENABLE, re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})".format(
                CheckPointBase.PatternHelper._PATTERN_ENABLE
            ), re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r".+Incomplete command\.",
                r".+Invalid command:.+"
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(CheckPointBase.PatternHelper._PATTERN_MORE, re.MULTILINE)

    @classmethod
    def get_probe_command(cls) -> str:
        return "show version all\nshow hostname"

    @classmethod
    def parse_probe_output(cls, output: str) -> ProbeResult:
        rows = TextFSMParser(cls._PROBE_TEMPLATE).parse(output)
        row = rows[0] if rows else {}
        return ProbeResult(
            vendor="check point",
            model=row.get("MODEL", ""),
            version=row.get("VERSION", ""),
            hostname=row.get("HOSTNAME", ""),
            serial_number=row.get("SERIAL", ""),
        )

    _PROBE_TEMPLATE = """\
Value HOSTNAME (\\S+)
Value MODEL (Check\\s+Point\\s+\\S+|Gaia\\s*\\S*)
Value VERSION ([0-9A-Za-z.]+)
Value SERIAL (\\S+)

Start
  ^${HOSTNAME}\\s*$ -> Continue
  ^[Pp]roduct\\s+[Vv]ersion\\s+(?:Check\\s+Point\\s+)?[Rr]?${VERSION} -> Continue
  ^\\s*[Vv]ersion\\s+${VERSION} -> Continue
  ^\\s*[Ss]erial\\s+[Nn]umber\\s*:\\s*${SERIAL} -> Continue
"""