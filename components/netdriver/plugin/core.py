#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Registry and Discovery System

Automatic plugin registration using metaclass patterns to enable dynamic loading
of device-specific drivers without manual configuration. Supports runtime discovery
of available plugins by vendor/model combinations.
"""
from typing import List, Dict

from netdriver.log import logman
from netdriver.plugin.plugin_info import PluginInfo


log = logman.logger


class IPluginRegistry(type):
    """
    Metaclass for automatic plugin registration during class definition.
    
    Uses Python's metaclass mechanism to automatically register plugins when
    their classes are defined, eliminating need for manual registration calls.
    See: https://docs.python.org/3/reference/datamodel.html#metaclasses
    """

    plugin_registries: Dict[str, List[type]] = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(cls)
        # Exclude base classes from registration to avoid circular dependencies
        if name != 'PluginCore' and name != 'Base':
            key = f"{cls.info.vendor}/{cls.info.model}"
            model_plugins = IPluginRegistry.plugin_registries.get(key, [])
            model_plugins.append(cls)
            IPluginRegistry.plugin_registries[key] = model_plugins
            log.info(f"registered plugin: {key} -> {cls}")


class PluginCore(object, metaclass=IPluginRegistry):
    """
    Base class for all network device plugins with automatic registration.
    
    Inheriting from this class automatically registers the plugin in the global
    registry, making it discoverable by the plugin engine at runtime.
    """

    def get_plugin_info(self) -> PluginInfo:
        """Provides metadata for plugin discovery and compatibility checking."""
        return self.info
