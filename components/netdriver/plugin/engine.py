#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Plugin Engine '''
import os
import importlib
import re
from typing import List, Optional
from netdriver.plugin.core import IPluginRegistry, PluginCore
from netdriver.log import logman


log = logman.logger


class PluginEngine:
    """ Plugin Engine Singleton Class """
    _instance = None
    # relative path to the plugins directory
    # get upper dir/plugins
    _plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

    def __new__(cls) -> "PluginEngine":
        if not cls._instance:
            log.info("Creating PluginEngine instance")
            cls._instance = super(PluginEngine, cls).__new__(cls)
            cls._instance._load_plugins()
        return cls._instance

    def _load_plugins(self) -> None:
        log.info("Loading plugins...")
        IPluginRegistry.plugin_registries.clear()
        # walk through the plugins directory

        for root, _, files in os.walk(self._plugins_dir):
            level = root.replace(self._plugins_dir, '').count(os.sep)
            if level < 1:
                continue
            dir_name = root.split(os.sep)[-1]
            for file in files:
                if file.endswith(".py") and file != "__init__.py" and not file.startswith("test_"):
                    plugin_name = file[:-3]
                    importlib.import_module(
                        f"netdriver.plugins.{dir_name}.{plugin_name}")
            plugin_count = len(IPluginRegistry.plugin_registries)
        log.info(f"Loaded {plugin_count} plugins.")

    def get_plugins(self) -> List:
        return IPluginRegistry.plugin_registries

    def get_plugin(self, vendor: str, model: str="base",
                   version:str="base") -> Optional[type]:
        """
        Get plugin by vendor, model, protocol and version

        :param vendor: vendor name
        :param model: model name
        :param version: version name, default is base
        """
        if not vendor:
            return ValueError("Vendor is required!")
        log.info(f"get plugin for: {vendor}/{model}/{version}")

        key = f"{vendor}/{model}"
        model_plugins = IPluginRegistry.plugin_registries.get(key, [])
        res: PluginCore = None
        if not model_plugins:
            log.debug(f"model plugins are empty for {key}, try to find {model} re match")
            for plugin_key in IPluginRegistry.plugin_registries.keys():
                plugin_vendor, plugin_model = plugin_key.split("/")
                if plugin_vendor == vendor and re.match(plugin_model, model):
                    model_plugins = IPluginRegistry.plugin_registries.get(plugin_key, [])
                    break
            if not model_plugins:
                log.debug(f"model plugins are empty for {key}, try to find {model}/base")
                key = f"{vendor}/base"
                model_plugins = IPluginRegistry.plugin_registries.get(key, [])

            for plugin in model_plugins:
                if plugin.info.version == 'base':
                    res = plugin
                    break
        else:
            for plugin in model_plugins:
                if plugin.info.version == version:
                    res = plugin
                    break
            if not res:
                log.debug(
                    f"try found model base plugin for {vendor}/{model}")
                for plugin in model_plugins:
                    if plugin.info.version == 'base':
                        res = plugin
                        break
            else:
                log.debug(
                    f"no plugin found for {vendor}/{model}/{version}")

        if res:
            info: str = res.info
            log.info(f"found plugin: {info} for {vendor}/{model}/{version}")
            return res
        else:
            log.warning(f"no plugin found for {vendor}/{model}/{version}")
            return None
