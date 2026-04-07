#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver_core.dev.mode import Mode
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult
from netdriver_agent.plugins.base import Base
from netdriver_textfsm import TextFSMParser


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
    _CMD_END = "end"
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
                await self.write_channel(self._CMD_END)
                prompt = await self._get_prompt(write_return=False)
        # keep decide vsys before decide mode
        self.decide_current_vsys(prompt)
        self.decide_current_mode(prompt)
        return prompt

    class PatternHelper:
        """ Inner class for patterns """
        # hostname # or hostname $
        _PATTERN_ENABLE = r"^\r{0,1}\S+\s*(\(\S+\))?\s*(#|\$)\s*$"
        # hostname (root) # or hostname (root) $
        _PATTERN_VSYS= r"^\r{0,1}\S+\s*\((\S+)\)\s*(#|\$)\s*$"
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

    @classmethod
    def get_probe_command(cls) -> str:
        return "get system status"

    @classmethod
    def parse_probe_output(cls, output: str) -> ProbeResult:
        rows = TextFSMParser(cls._PROBE_TEMPLATE).parse(output)
        row = rows[0] if rows else {}
        model = row.get("MODEL", "")
        if not model and "fortigate" in output.lower():
            model = "FortiGate"
        return ProbeResult(
            vendor="fortinet",
            model=model,
            version=row.get("VERSION", ""),
            hostname=row.get("HOSTNAME", ""),
            serial_number=row.get("SERIAL", ""),
        )

    _PROBE_TEMPLATE = """\
Value HOSTNAME (\\S+)
Value MODEL (\\S+)
Value VERSION ([0-9.]+)
Value SERIAL (\\S+)

Start
  ^[Hh]ostname\\s*:\\s*${HOSTNAME} -> Continue
  ^[Pp]latform\\s+\\S+\\s+[Nn]ame\\s*:\\s*${MODEL} -> Continue
  ^v${VERSION}\\s -> Continue
  ^[Ff]irmware\\s+[Vv]ersion\\s*:\\s*v?${VERSION} -> Continue
  ^[Ss]erial-[Nn]umber\\s*:\\s*${SERIAL} -> Continue
  ^[Ss]erial\\s+[Nn]umber\\s*:\\s*${SERIAL} -> Continue
"""