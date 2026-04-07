#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Device identifier using existing plugin patterns and SNMP OID mapping."""

import re

from netdriver_core.log import logman
from netdriver_core.plugin.core import IPluginRegistry

from netdriver_agent.discovery.oid.vendor_oid_map import identify_vendor_by_oid

log = logman.logger


class DeviceIdentifier:
    """Identifies network devices using SSH prompt patterns and SNMP OID mapping.

    SSH identification leverages existing plugin PatternHelper.get_union_pattern()
    static methods from all registered vendor plugins.
    """

    def __init__(self):
        self._prompt_patterns: dict[str, list] = {}
        self._load_plugin_patterns()

    def _load_plugin_patterns(self) -> None:
        """Load prompt patterns from all registered plugins."""
        for key, plugin_list in IPluginRegistry.plugin_registries.items():
            vendor = key.split("/")[0]
            if vendor in self._prompt_patterns:
                continue

            for plugin_cls in plugin_list:
                try:
                    pattern = plugin_cls.PatternHelper.get_union_pattern()
                    if vendor not in self._prompt_patterns:
                        self._prompt_patterns[vendor] = []
                    self._prompt_patterns[vendor].append(pattern)
                    log.debug(f"Loaded prompt pattern for vendor '{vendor}' from {plugin_cls.__name__}")
                    break  # One pattern per vendor is sufficient
                except AttributeError:
                    continue

        log.info(f"Loaded prompt patterns for {len(self._prompt_patterns)} vendor(s)")

    def identify_by_prompt(self, prompt: str) -> list[str]:
        """Identify vendors by matching SSH prompt against plugin patterns.

        Iterates over all registered plugin PatternHelper.get_union_pattern()
        static methods and collects all matching vendors.

        Args:
            prompt: The SSH prompt/banner text from the device.

        Returns:
            List of matching vendor names (e.g. ["cisco", "arista"]), or empty list.
        """
        if not prompt:
            return []

        matched_vendors = []
        for vendor, patterns in self._prompt_patterns.items():
            for pattern in patterns:
                if pattern and pattern.search(prompt):
                    log.debug(f"Prompt matched vendor '{vendor}'")
                    matched_vendors.append(vendor)
                    break

        return matched_vendors

    def identify_by_oid(self, sys_object_id: str) -> str | None:
        """Identify vendor by sysObjectID prefix match.

        Args:
            sys_object_id: The SNMP sysObjectID value.

        Returns:
            Vendor name or None.
        """
        return identify_vendor_by_oid(sys_object_id)

    @staticmethod
    def get_probe_plugin(
        vendor: str,
        model: str = "",
        version: str = "",
    ) -> type | None:
        """Get the best-matching plugin class for a device profile.

        Resolution order: exact vendor/model match → regex model match →
        vendor/base fallback.

        Args:
            vendor: Vendor name (required).
            model: Model name (optional).
            version: Version string (optional).

        Returns:
            Plugin class with get_probe_command/parse_probe_output, or None.
        """
        if not vendor:
            return None

        vendor = vendor.strip().lower()
        model = model.strip().lower() if model else ""
        version = version.strip().lower() if version else ""

        # 1. Try exact vendor/model key
        if model:
            key = f"{vendor}/{model}"
            model_plugins = IPluginRegistry.plugin_registries.get(key, [])
            result = DeviceIdentifier._select_version(model_plugins, version)
            if result is not None:
                return result

            # 2. Try regex model match
            for plugin_key, plugins in IPluginRegistry.plugin_registries.items():
                plugin_vendor, plugin_model = plugin_key.split("/", maxsplit=1)
                if plugin_vendor != vendor or plugin_model == "base":
                    continue
                if re.match(plugin_model, model, re.IGNORECASE):
                    result = DeviceIdentifier._select_version(plugins, version)
                    if result is not None:
                        return result

        # 3. Fall back to vendor/base
        base_plugins = IPluginRegistry.plugin_registries.get(f"{vendor}/base", [])
        return DeviceIdentifier._select_version(base_plugins, version)

    @staticmethod
    def _select_version(plugins: list[type], version: str) -> type | None:
        """Select exact version or fall back to base."""
        if version:
            for plugin_cls in plugins:
                if hasattr(plugin_cls, 'info') and plugin_cls.info.version == version:
                    return plugin_cls
        for plugin_cls in plugins:
            if hasattr(plugin_cls, 'info') and plugin_cls.info.version == "base":
                return plugin_cls
        return None
