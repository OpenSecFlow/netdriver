#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from netdriver.client.mode import Mode
from netdriver.plugin.plugin_info import PluginInfo
from netdriver.plugins.base import Base


# pylint: disable=abstract-method
class ArrayBase(Base):
    """ Array Base Plugin """

    info = PluginInfo(
        vendor="array",
        model="base",
        version="base",
        description="Array Base Plugin"
    )

    _CMD_CANCEL_MORE = "no page"

    def get_union_pattern(self) -> re.Pattern:
        return ArrayBase.PatternHelper.get_union_pattern()

    def get_error_patterns(self) -> list[re.Pattern]:
        return ArrayBase.PatternHelper.get_error_patterns()

    def get_ignore_error_patterns(self) -> list[re.Pattern]:
        return ArrayBase.PatternHelper.get_ignore_error_patterns()

    def get_enable_password_prompt_pattern(self) -> re.Pattern:
        return ArrayBase.PatternHelper.get_enable_password_prompt_pattern()

    def get_mode_prompt_patterns(self) -> dict[Mode, re.Pattern]:
        return {
            Mode.LOGIN: ArrayBase.PatternHelper.get_login_prompt_pattern(),
            Mode.ENABLE: ArrayBase.PatternHelper.get_enable_prompt_pattern(),
            Mode.CONFIG: ArrayBase.PatternHelper.get_config_prompt_pattern()
        }

    def get_more_pattern(self) -> tuple[re.Pattern, str]:
        return (ArrayBase.PatternHelper.get_more_pattern(), self._CMD_MORE)

    class PatternHelper:
        """ Inner class for patterns """
        # hostname> $
        _PATTERN_LOGIN = r"^\r{0,1}[^\s<]+>\s*$"
        # hostname# $
        _PATTERN_ENABLE = r"^\r{0,1}[^\s#]+#\s*$"
        # hostname(config)# $
        _PATTERN_CONFIG = r"^\r{0,1}\S+\(\S+\)#\s*$"
        # vsite_namer$ $
        _PATTERN_VSITE_ENABLE = r"^\r{0,1}\S+\$\s*$"
        # vsite_name(config)$ $
        _PATTERN_VSITE_CONFIG = r"^\r{0,1}\S+\(\S+\)\$\s*$"
        _PATTERN_ENABLE_PASSWORD = r"Enable password:"
        #  --More-- 
        _PATTERN_MORE = r" --More-- "

        @staticmethod
        def get_login_prompt_pattern() -> re.Pattern:
            return re.compile(ArrayBase.PatternHelper._PATTERN_LOGIN, re.MULTILINE)

        @staticmethod
        def get_enable_prompt_pattern() -> re.Pattern:
            return re.compile("(?P<enable>{})|(?P<vsite_enable>{})".format(
                ArrayBase.PatternHelper._PATTERN_ENABLE,
                ArrayBase.PatternHelper._PATTERN_VSITE_ENABLE
            ), re.MULTILINE)

        @staticmethod
        def get_config_prompt_pattern() -> re.Pattern:
            return re.compile("(?P<config>{})|(?P<vsite_config>{})".format(
                ArrayBase.PatternHelper._PATTERN_CONFIG,
                ArrayBase.PatternHelper._PATTERN_VSITE_CONFIG,
            ), re.MULTILINE)

        @staticmethod
        def get_union_pattern() -> re.Pattern:
            # config before enable, because config is a subset of enable
            # vsite_config before vsite_enable, because vsite_config is a subset of vsite_enable
            return re.compile(
                "(?P<login>{})|(?P<vsite_config>{})|(?P<config>{})|(?P<enable>{})|(?P<vsite_enable>{})".format(
                    ArrayBase.PatternHelper._PATTERN_LOGIN,
                    ArrayBase.PatternHelper._PATTERN_VSITE_CONFIG,
                    ArrayBase.PatternHelper._PATTERN_CONFIG,
                    ArrayBase.PatternHelper._PATTERN_ENABLE,
                    ArrayBase.PatternHelper._PATTERN_VSITE_ENABLE
            ), re.MULTILINE)

        @staticmethod
        def get_enable_password_prompt_pattern() -> re.Pattern:
            return re.compile(ArrayBase.PatternHelper._PATTERN_ENABLE_PASSWORD, re.MULTILINE)

        @staticmethod
        def get_error_patterns() -> list[re.Pattern]:
            regex_strs = [
                r"Virtual site .+ is not configured",
                r"Cannot find the group name '.+'\.",
                r"No such group map configured: \".+\" to \".+\"\.",
                r"Internal group \".+\" not found, please configure the group at localdb\.",
                r"Already has a group map for external group \".+\"\.",
                r"role \".+\" doesn't exist",
                r"qualification \".+\" doesn't exist",
                r"the condition \"GROUPNAME IS '.+'\" doesn't exist in qualification \".+\", role \".+\"",
                r"The resource \".+\" has not been assigned to this role",
                r"Netpool .+ does not exist",
                r"Resource group .+ does not exist",
                r"The resource \".+\" has not been assigned to this role",
                r"Cannot find the resource group '.+'\.",
                r"This resource group name has been used, please give another one\.",
                r"This resource .+ doesn't exist or hasn't assigned to target .+",
                r"Parse network resource failed: Invalid port format\.",
                r"Parse network resource failed: Invalid ACL format\.",
                r"Parse network resource failed: ICMP protocol resources MUST NOT with port information\.",
                r"Cannot find the resource group '.+'\.",
                r"The resource \".+\" does not exsit under resource group \".+\"",
                r"\^$",
            ]
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_ignore_error_patterns() -> list[re.Pattern]:
            regex_strs = []
            return [re.compile(regex_str, re.MULTILINE) for regex_str in regex_strs]

        @staticmethod
        def get_more_pattern() -> re.Pattern:
            return re.compile(ArrayBase.PatternHelper._PATTERN_MORE, re.MULTILINE)