#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Plugin Engine core module '''
from typing import List, Dict

from netdriver.log import logman
from netdriver.plugin.plugin_info import PluginInfo


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
