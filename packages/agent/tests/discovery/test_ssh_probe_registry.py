#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import pytest

from netdriver_core.plugin.core import IPluginRegistry, PluginCore
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_core.plugin.probe import ProbeResult
from netdriver_agent.discovery.probe.base_ssh_probe import SshProbe
from netdriver_agent.discovery.probe.identifier import DeviceIdentifier
from netdriver_agent.discovery.probe.models import DeviceInfo, DeviceProfile, SshCredential, SshProbeResult


class _FakeProcessStdin:
    def __init__(self) -> None:
        self.writes: list[str] = []

    def write(self, data: str) -> None:
        self.writes.append(data)


class _FakeProcess:
    def __init__(self) -> None:
        self.stdin = _FakeProcessStdin()


class _FakeConn:
    def __init__(self, process: _FakeProcess) -> None:
        self._process = process

    async def create_process(
        self,
        term_type: str,
        term_size: tuple[int, int],
    ) -> _FakeProcess:
        assert term_type == "ansi"
        assert term_size == (1000, 100)
        return self._process


# --- DeviceIdentifier.identify_by_prompt tests ---


@pytest.mark.unit
def test_identify_by_prompt_returns_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """identify_by_prompt should return a list of matching vendors."""
    saved = dict(IPluginRegistry.plugin_registries)

    class _FakePlugin:
        class PatternHelper:
            @staticmethod
            def get_union_pattern():
                import re
                return re.compile(r"^\S+#\s*$", re.MULTILINE)

    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {"testvendor/base": [_FakePlugin]})

    try:
        identifier = DeviceIdentifier()
        result = identifier.identify_by_prompt("switch-a#")
        assert isinstance(result, list)
        assert "testvendor" in result
    finally:
        IPluginRegistry.plugin_registries = saved


@pytest.mark.unit
def test_identify_by_prompt_returns_empty_for_no_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """identify_by_prompt should return empty list when no patterns match."""
    saved = dict(IPluginRegistry.plugin_registries)
    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {})

    try:
        identifier = DeviceIdentifier()
        result = identifier.identify_by_prompt("unknown-prompt>>>")
        assert result == []
    finally:
        IPluginRegistry.plugin_registries = saved


@pytest.mark.unit
def test_identify_by_prompt_returns_empty_for_empty_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    saved = dict(IPluginRegistry.plugin_registries)
    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {})

    try:
        identifier = DeviceIdentifier()
        result = identifier.identify_by_prompt("")
        assert result == []
    finally:
        IPluginRegistry.plugin_registries = saved


# --- DeviceIdentifier.get_probe_plugin tests ---


@pytest.mark.unit
def test_get_probe_plugin_exact_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_probe_plugin should find exact vendor/model match."""
    saved = dict(IPluginRegistry.plugin_registries)

    class _AcmeEdge(PluginCore):
        info = PluginInfo(vendor="acme", model="edge5000", version="base", description="test")

    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {"acme/edge5000": [_AcmeEdge]})

    try:
        result = DeviceIdentifier.get_probe_plugin("acme", "edge5000")
        assert result is _AcmeEdge
    finally:
        IPluginRegistry.plugin_registries = saved


@pytest.mark.unit
def test_get_probe_plugin_falls_back_to_vendor_base(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_probe_plugin should fall back to vendor/base when model not found."""
    saved = dict(IPluginRegistry.plugin_registries)

    class _AcmeBase(PluginCore):
        info = PluginInfo(vendor="acme", model="base", version="base", description="test")

    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {"acme/base": [_AcmeBase]})

    try:
        result = DeviceIdentifier.get_probe_plugin("acme", "unknown-device")
        assert result is _AcmeBase
    finally:
        IPluginRegistry.plugin_registries = saved


@pytest.mark.unit
def test_get_probe_plugin_returns_none_for_unknown_vendor(monkeypatch: pytest.MonkeyPatch) -> None:
    saved = dict(IPluginRegistry.plugin_registries)
    monkeypatch.setattr(IPluginRegistry, "plugin_registries", {})

    try:
        result = DeviceIdentifier.get_probe_plugin("nonexistent")
        assert result is None
    finally:
        IPluginRegistry.plugin_registries = saved


# --- SshProbe._identify_device tests ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_identify_device_uses_plugin_when_vendor_known() -> None:
    """When vendor is known, should use plugin's probe command."""
    probe = SshProbe()
    process = _FakeProcess()
    outputs = iter(["switch-a#", "Cisco IOS Software, Version 15.2(4)M7"])

    async def fake_read_until_prompt(process: _FakeProcess) -> str:
        return next(outputs)

    probe._read_until_prompt = fake_read_until_prompt  # type: ignore[method-assign]

    class _Identifier:
        def identify_by_prompt(self, prompt: str) -> list[str]:
            raise AssertionError("identify_by_prompt should not be called")

        @staticmethod
        def get_probe_plugin(vendor, model="", version=""):
            class _CiscoPlugin:
                @classmethod
                def get_probe_command(cls):
                    return "show version"

                @classmethod
                def parse_probe_output(cls, output):
                    return ProbeResult(vendor="cisco", model="ISR4451", version="15.2(4)M7")

                __name__ = "_CiscoPlugin"

            return _CiscoPlugin

    result = await probe._identify_device(
        conn=_FakeConn(process),
        host="10.0.0.1",
        port=22,
        credential=SshCredential(username="ops", password="secret"),
        identifier=_Identifier(),
        read_timeout=1.0,
        selection_profile=DeviceProfile(vendor="cisco", model="isr", version=""),
    )

    assert result.device_info is not None
    assert result.device_info.vendor == "cisco"
    assert result.device_info.model == "ISR4451"
    assert process.stdin.writes == ["show version\n"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_identify_device_tries_prompt_matching_when_vendor_unknown() -> None:
    """When vendor is unknown, should match prompt and try candidate plugins."""
    probe = SshProbe()
    process = _FakeProcess()
    outputs = iter(["<huawei-switch>", "Huawei CE6857 Version V200R021"])

    async def fake_read_until_prompt(process: _FakeProcess) -> str:
        return next(outputs)

    probe._read_until_prompt = fake_read_until_prompt  # type: ignore[method-assign]

    class _Identifier:
        def identify_by_prompt(self, prompt: str) -> list[str]:
            assert prompt == "<huawei-switch>"
            return ["huawei"]

        @staticmethod
        def get_probe_plugin(vendor, model="", version=""):
            class _HuaweiPlugin:
                @classmethod
                def get_probe_command(cls):
                    return "display version"

                @classmethod
                def parse_probe_output(cls, output):
                    return ProbeResult(vendor="huawei", model="CE6857", version="V200R021")

                __name__ = "_HuaweiPlugin"

            return _HuaweiPlugin

    result = await probe._identify_device(
        conn=_FakeConn(process),
        host="10.0.0.2",
        port=22,
        credential=SshCredential(username="ops", password="secret"),
        identifier=_Identifier(),
        read_timeout=1.0,
        selection_profile=DeviceProfile(),
    )

    assert result.device_info is not None
    assert result.device_info.vendor == "huawei"
    assert result.device_info.model == "CE6857"
    assert process.stdin.writes == ["display version\n"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_identify_device_falls_back_to_default_probe() -> None:
    """When no candidate plugins match, should fall back to PluginCore default."""
    probe = SshProbe()
    process = _FakeProcess()
    outputs = iter(["unknown-prompt$", "Cisco IOS Version 17.9.4"])

    async def fake_read_until_prompt(process: _FakeProcess) -> str:
        return next(outputs)

    probe._read_until_prompt = fake_read_until_prompt  # type: ignore[method-assign]

    class _Identifier:
        def identify_by_prompt(self, prompt: str) -> list[str]:
            return []

        @staticmethod
        def get_probe_plugin(vendor, model="", version=""):
            return None

    result = await probe._identify_device(
        conn=_FakeConn(process),
        host="10.0.0.3",
        port=22,
        credential=SshCredential(username="ops", password="secret"),
        identifier=_Identifier(),
        read_timeout=1.0,
        selection_profile=DeviceProfile(),
    )

    assert result.device_info is not None
    # PluginCore default detects "cisco" from output
    assert result.device_info.vendor == "cisco"
    # Fallback probe command is "show version"
    assert process.stdin.writes == ["show version\n"]
