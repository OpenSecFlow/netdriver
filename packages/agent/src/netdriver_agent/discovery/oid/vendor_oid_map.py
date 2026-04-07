#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Load vendor SNMP OID mappings from a single YAML configuration."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from netdriver_core.log import logman

log = logman.logger
_OID_PATTERN = re.compile(r"^\d+(?:\.\d+)*$")
_CONFIG_ENV_VAR = "NETDRIVER_DISCOVERY_VENDOR_MAP"
_AGENT_CONFIG_ENV_VAR = "NETDRIVER_AGENT_CONFIG"
_DEFAULT_MODEL_OIDS = [
    "1.3.6.1.2.1.47.1.1.1.1.13.1",
]
_DEFAULT_VERSION_OIDS = [
    "1.3.6.1.2.1.47.1.1.1.1.10.1",
]
_DEFAULT_SERIAL_OIDS = [
    "1.3.6.1.2.1.47.1.1.1.1.11.1",  # entPhysicalSerialNum
]


def _validate_oid(value: str, field_name: str) -> str:
    """Validate and normalize an OID string."""
    oid = value.strip()
    if not oid:
        raise ValueError(f"{field_name} must not be empty")
    if not _OID_PATTERN.fullmatch(oid):
        raise ValueError(f"invalid {field_name}: {oid}")
    return oid


def _merge_oids(custom_oids: list[str], default_oids: list[str]) -> list[str]:
    """Merge custom and default OIDs while preserving order and removing duplicates."""
    merged: list[str] = []
    for oid in [*custom_oids, *default_oids]:
        if oid not in merged:
            merged.append(oid)
    return merged


class VendorSnmpConfig(BaseModel):
    """SNMP mapping for a single vendor."""

    model_config = ConfigDict(extra="forbid")

    sysobjectid_prefixes: list[str] = Field(default_factory=list)
    model_oids: list[str] = Field(default_factory=list)
    version_oids: list[str] = Field(default_factory=list)
    serial_number_oids: list[str] = Field(default_factory=list)

    @field_validator("sysobjectid_prefixes")
    @classmethod
    def _validate_prefixes(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for prefix in value:
            normalized.append(_validate_oid(prefix, "sysobjectid_prefix"))
        if not normalized:
            raise ValueError("sysobjectid_prefixes must not be empty")
        return normalized

    @field_validator("model_oids", "version_oids", "serial_number_oids")
    @classmethod
    def _validate_optional_oids(
        cls,
        value: list[str],
        info: ValidationInfo,
    ) -> list[str]:
        normalized: list[str] = []
        item_field_name = info.field_name[:-1] if info.field_name and info.field_name.endswith("s") else (info.field_name or "oid")
        for oid in value:
            normalized.append(_validate_oid(oid, item_field_name))
        return normalized


class VendorOidConfig(BaseModel):
    """Vendor SNMP OID configuration."""

    model_config = ConfigDict(extra="forbid")

    vendors: dict[str, VendorSnmpConfig] = Field(default_factory=dict)

    @field_validator("vendors")
    @classmethod
    def _validate_vendors(
        cls,
        value: dict[str, VendorSnmpConfig],
    ) -> dict[str, VendorSnmpConfig]:
        normalized: dict[str, VendorSnmpConfig] = {}
        for vendor, config in value.items():
            vendor_name = vendor.strip()
            if not vendor_name:
                raise ValueError("vendor name must not be empty")
            normalized[vendor_name] = config
        return normalized


def reset_vendor_oid_map_cache() -> None:
    """Reset cached vendor OID configuration."""
    _load_vendor_oid_config.cache_clear()
    _build_vendor_prefix_index.cache_clear()


def _iter_candidate_paths() -> list[Path]:
    """Return candidate configuration paths in priority order."""
    candidates: list[Path] = []
    explicit_path = os.getenv(_CONFIG_ENV_VAR)
    if explicit_path:
        candidates.append(Path(explicit_path).expanduser())

    agent_config_path = os.getenv(_AGENT_CONFIG_ENV_VAR)
    if agent_config_path:
        candidates.append(Path(agent_config_path).expanduser().parent / "vendor_oid_map.yml")

    candidates.append(Path("config/agent/vendor_oid_map.yml"))
    return candidates


def _load_config_text() -> tuple[str, str]:
    """Load configuration text from file."""
    for candidate in _iter_candidate_paths():
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8"), str(candidate)

    explicit_path = os.getenv(_CONFIG_ENV_VAR)
    if explicit_path:
        log.warning(
            f"Vendor OID mapping file '{explicit_path}' not found, ignoring custom overrides"
        )

    return "", ""


@lru_cache(maxsize=1)
def _load_vendor_oid_config() -> VendorOidConfig:
    """Load and validate vendor OID configuration."""
    config_text, config_source = _load_config_text()
    if not config_text:
        return VendorOidConfig()

    raw_config = yaml.safe_load(config_text)
    if raw_config is None:
        raw_config = {}
    if not isinstance(raw_config, dict):
        raise ValueError(f"invalid vendor OID mapping format from {config_source}")

    config = VendorOidConfig.model_validate(raw_config)
    log.debug(
        f"Loaded vendor OID mapping from {config_source} with "
        f"{len(config.vendors)} vendor entries"
    )
    return config


@lru_cache(maxsize=1)
def _build_vendor_prefix_index() -> list[tuple[str, str]]:
    """Build a longest-prefix-first sysObjectID index."""
    prefixes: list[tuple[str, str]] = []
    for vendor, config in _load_vendor_oid_config().vendors.items():
        for prefix in config.sysobjectid_prefixes:
            prefixes.append((prefix, vendor))

    prefixes.sort(key=lambda item: len(item[0]), reverse=True)
    return prefixes


def identify_vendor_by_oid(sys_object_id: str) -> str | None:
    """Identify vendor by longest sysObjectID prefix match."""
    for prefix, vendor in _build_vendor_prefix_index():
        if sys_object_id.startswith(prefix):
            return vendor
    return None


def get_vendor_snmp_detail_oids(vendor: str) -> dict[str, list[str]]:
    """Return configured model/version OID lists for a vendor."""
    config = _load_vendor_oid_config().vendors.get(vendor)
    if config is None:
        return {}

    return {
        "model": _merge_oids(config.model_oids, _DEFAULT_MODEL_OIDS),
        "version": _merge_oids(config.version_oids, _DEFAULT_VERSION_OIDS),
        "serial_number": _merge_oids(config.serial_number_oids, _DEFAULT_SERIAL_OIDS),
    }
