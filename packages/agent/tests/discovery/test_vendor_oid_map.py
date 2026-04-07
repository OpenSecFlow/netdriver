#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from netdriver_agent.discovery.oid import vendor_oid_map
from netdriver_agent.discovery.oid.vendor_oid_map import (
    get_vendor_snmp_detail_oids,
    identify_vendor_by_oid,
    reset_vendor_oid_map_cache,
)


@pytest.mark.unit
def test_vendor_oid_map_loads_from_env_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "vendor_oid_map.yml"
    config_file.write_text(
        """
vendors:
  vendor_a:
    sysobjectid_prefixes:
      - 1.3.6.1.4.1.999
    model_oids:
      - 1.3.6.1.4.1.999.1.1.0
      - 1.3.6.1.4.1.999.1.1.1
  vendor_b:
    sysobjectid_prefixes:
      - 1.3.6.1.4.1.999.1
    version_oids:
      - 1.3.6.1.4.1.999.1.2.0
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("NETDRIVER_DISCOVERY_VENDOR_MAP", str(config_file))
    reset_vendor_oid_map_cache()

    assert identify_vendor_by_oid("1.3.6.1.4.1.999.1.10") == "vendor_b"
    assert identify_vendor_by_oid("1.3.6.1.4.1.999.2.10") == "vendor_a"
    assert get_vendor_snmp_detail_oids("vendor_a") == {
        "model": [
            "1.3.6.1.4.1.999.1.1.0",
            "1.3.6.1.4.1.999.1.1.1",
            "1.3.6.1.2.1.47.1.1.1.1.13.1",
        ],
        "version": [
            "1.3.6.1.2.1.47.1.1.1.1.10.1",
        ],
        "serial_number": [
            "1.3.6.1.2.1.47.1.1.1.1.11.1",
        ],
    }
    assert get_vendor_snmp_detail_oids("vendor_b") == {
        "model": ["1.3.6.1.2.1.47.1.1.1.1.13.1"],
        "version": [
            "1.3.6.1.4.1.999.1.2.0",
            "1.3.6.1.2.1.47.1.1.1.1.10.1",
        ],
        "serial_number": [
            "1.3.6.1.2.1.47.1.1.1.1.11.1",
        ],
    }


@pytest.mark.unit
def test_vendor_oid_map_uses_default_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NETDRIVER_DISCOVERY_VENDOR_MAP", raising=False)
    reset_vendor_oid_map_cache()

    config = vendor_oid_map._load_vendor_oid_config()
    assert config.vendors["cisco"].sysobjectid_prefixes == ["1.3.6.1.4.1.9"]
    assert config.vendors["qianxin"].sysobjectid_prefixes == [
        "1.3.6.1.4.1.47646",
        "1.3.6.1.4.1.62722",
    ]

    assert identify_vendor_by_oid("1.3.6.1.4.1.2011.2.23.221") == "huawei"
    assert identify_vendor_by_oid("1.3.6.1.4.1.31648.1.1") == "dptech"
    assert identify_vendor_by_oid("1.3.6.1.4.1.50737.1.1") == "chaitin"
    assert identify_vendor_by_oid("1.3.6.1.4.1.65528.1.2") is None
    assert get_vendor_snmp_detail_oids("cisco") == {
        "model": ["1.3.6.1.2.1.47.1.1.1.1.13.1"],
        "version": ["1.3.6.1.2.1.47.1.1.1.1.10.1"],
        "serial_number": ["1.3.6.1.2.1.47.1.1.1.1.11.1"],
    }


@pytest.mark.unit
def test_vendor_oid_map_uses_defaults_when_custom_oids_omitted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "vendor_oid_map.yml"
    config_file.write_text(
        """
vendors:
  vendor_a:
    sysobjectid_prefixes:
      - 1.3.6.1.4.1.999
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("NETDRIVER_DISCOVERY_VENDOR_MAP", str(config_file))
    reset_vendor_oid_map_cache()

    assert get_vendor_snmp_detail_oids("vendor_a") == {
        "model": ["1.3.6.1.2.1.47.1.1.1.1.13.1"],
        "version": ["1.3.6.1.2.1.47.1.1.1.1.10.1"],
        "serial_number": ["1.3.6.1.2.1.47.1.1.1.1.11.1"],
    }


@pytest.mark.unit
def test_vendor_oid_map_rejects_invalid_oid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "vendor_oid_map.yml"
    config_file.write_text(
        """
vendors:
  broken:
    sysobjectid_prefixes:
      - invalid.oid
    model_oids:
      - 1.3.6.1.4.1.1.1.0
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("NETDRIVER_DISCOVERY_VENDOR_MAP", str(config_file))
    reset_vendor_oid_map_cache()

    with pytest.raises(ValueError, match="invalid sysobjectid_prefix"):
        vendor_oid_map._load_vendor_oid_config()


@pytest.mark.unit
def test_vendor_oid_map_rejects_invalid_detail_oid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "vendor_oid_map.yml"
    config_file.write_text(
        """
vendors:
  broken:
    sysobjectid_prefixes:
      - 1.3.6.1.4.1.1
    version_oids:
      - broken.oid
""".strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("NETDRIVER_DISCOVERY_VENDOR_MAP", str(config_file))
    reset_vendor_oid_map_cache()

    with pytest.raises(ValueError, match="invalid version_oid"):
        vendor_oid_map._load_vendor_oid_config()
