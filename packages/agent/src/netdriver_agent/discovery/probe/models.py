#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from netdriver_core.snmp.models import SnmpCredential


@dataclass
class SshCredential:
    """SSH credential for authentication."""
    username: str
    password: str
    enable_password: str = ""


@dataclass
class DeviceInfo:
    """Identified device information."""
    vendor: str = ""
    model: str = ""
    version: str = ""
    hostname: str = ""
    serial_number: str = ""


@dataclass(slots=True)
class DeviceProfile:
    """Normalized device profile used to select SSH probes."""

    vendor: str = ""
    model: str = ""
    version: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, str] | None) -> "DeviceProfile":
        """Build a normalized profile from a mapping."""
        if data is None:
            return cls()

        return cls(
            vendor=cls._normalize_value(data.get("vendor", "")),
            model=cls._normalize_value(data.get("model", "")),
            version=cls._normalize_value(data.get("version", "")),
        )

    @classmethod
    def from_device_info(cls, device_info: DeviceInfo | None) -> "DeviceProfile":
        """Build a normalized profile from SSH/SNMP device info."""
        if device_info is None:
            return cls()

        return cls(
            vendor=cls._normalize_value(device_info.vendor),
            model=cls._normalize_value(device_info.model),
            version=cls._normalize_value(device_info.version),
        )

    @staticmethod
    def _normalize_value(value: str | None) -> str:
        """Normalize a profile field for matching."""
        return value.strip().lower() if value else ""

    def is_empty(self) -> bool:
        """Return whether all matching fields are empty."""
        return not any((self.vendor, self.model, self.version))

    def normalized(self) -> "DeviceProfile":
        """Return a normalized copy of the profile."""
        return DeviceProfile(
            vendor=self._normalize_value(self.vendor),
            model=self._normalize_value(self.model),
            version=self._normalize_value(self.version),
        )


@dataclass
class SshProbeResult:
    """Result of an SSH probe."""
    success: bool
    host: str
    port: int = 22
    credential: SshCredential | None = None
    device_info: DeviceInfo | None = None
    raw_output: str = ""
    error: str = ""


@dataclass
class SnmpProbeResult:
    """Result of an SNMP probe."""
    success: bool
    host: str
    community: str = ""
    credential: SnmpCredential | None = None
    device_info: DeviceInfo | None = None
    sys_object_id: str = ""
    sys_descr: str = ""
    sys_name: str = ""
    error: str = ""


@dataclass
class ProbeResult:
    """Combined probe result for a single host."""
    ip: str
    identified: bool = False
    method: str = ""
    device_info: DeviceInfo | None = None
    ssh_result: SshProbeResult | None = None
    snmp_result: SnmpProbeResult | None = None
