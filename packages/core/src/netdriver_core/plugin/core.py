#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Plugin Engine core module '''
import re
from typing import List, Dict

from netdriver_core.log import logman
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult


log = logman.logger


class IPluginRegistry(type):
    ''' Plugin Registry Interface '''

    plugin_registries: Dict[str, List[type]] = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(cls)
        if name != 'PluginCore' and name != 'Base':
            key = f"{cls.info.vendor}/{cls.info.model}"
            model_plugins = IPluginRegistry.plugin_registries.get(key, [])
            model_plugins.append(cls)
            IPluginRegistry.plugin_registries[key] = model_plugins
            log.info(f"registed plugin: {key} -> {cls}")


class PluginCore(object, metaclass=IPluginRegistry):
    ''' Plugin Core Class '''

    def get_plugin_info(self) -> PluginInfo:
        ''' Get plugin info '''
        return self.info

    @classmethod
    def get_probe_command(cls) -> str:
        '''Return the CLI command used to probe device version info.'''
        return "show version"

    @classmethod
    def parse_probe_output(cls, output: str) -> ProbeResult:
        '''Parse probe command output into device identification info.'''
        vendor = ""
        model = ""
        version = ""

        lower = output.lower()
        if "cisco" in lower:
            vendor = "cisco"
        elif "huawei" in lower:
            vendor = "huawei"
        elif "juniper" in lower or "junos" in lower:
            vendor = "juniper"

        version_match = re.search(r"[Vv]ersion\s+([0-9A-Za-z.()]+)", output)
        if version_match:
            version = version_match.group(1)

        return ProbeResult(vendor=vendor, model=model, version=version)
