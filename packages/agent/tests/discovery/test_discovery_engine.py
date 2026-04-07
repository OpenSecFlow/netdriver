#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

import pytest

from netdriver_core.snmp.models import SnmpCredential
from netdriver_agent.discovery.engine.discovery_engine import DiscoveryEngine
from netdriver_agent.discovery.engine.models import TaskStatus
from netdriver_agent.discovery.engine.worker import DiscoveryWorkerPayload
from netdriver_agent.discovery.probe.models import SshCredential


@dataclass
class _FakeTaskStore:
    created_targets: list[list[str]]
    statuses: list[tuple[str, TaskStatus, str]]

    def __init__(self) -> None:
        self.created_targets = []
        self.statuses = []

    async def create_task(self, targets: list[str]) -> str:
        self.created_targets.append(targets)
        return "task-123"

    async def set_status(
        self,
        task_id: str,
        status: TaskStatus,
        error_message: str = "",
    ) -> None:
        self.statuses.append((task_id, status, error_message))


class _FakePopen:
    def __init__(self, command: list[str], start_new_session: bool) -> None:
        self.command = command
        self.start_new_session = start_new_session
        self.pid = 4321
        self._returncode: int | None = None

    def poll(self) -> int | None:
        return self._returncode

    def wait(self, timeout: float | None = None) -> int:
        self._returncode = 0
        return 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_discovery_launches_worker_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_store = _FakeTaskStore()
    captured: dict[str, object] = {}

    def fake_popen(command: list[str], start_new_session: bool) -> _FakePopen:
        captured["command"] = command
        captured["start_new_session"] = start_new_session
        return _FakePopen(command, start_new_session)

    monkeypatch.setattr("subprocess.Popen", fake_popen)

    engine = DiscoveryEngine(
        task_store=task_store,
        db_path="/tmp/discovery.db",
        nmap_path="/usr/bin/nmap",
        max_concurrent_probes=20,
        probe_timeout=15.0,
        ssh_connect_timeout=8.0,
        ssh_read_timeout=4.0,
        snmp_timeout=3.0,
        snmp_retries=2,
    )

    task_id = await engine.start_discovery(
        targets=["10.0.0.0/24"],
        ssh_ports=[22],
        snmp_ports=[161],
        ssh_credentials=[SshCredential(username="admin", password="secret")],
        snmp_credentials=[SnmpCredential(community="public")],
        max_concurrent_probes=99,
        probe_timeout=7.5,
    )

    assert task_id == "task-123"
    assert task_store.created_targets == [["10.0.0.0/24"]]

    command = captured["command"]
    assert isinstance(command, list)
    assert command[1:3] == ["-m", "netdriver_agent.discovery.engine.worker"]

    payload = DiscoveryWorkerPayload.from_json(command[3])
    assert payload.task_id == "task-123"
    assert payload.db_path == "/tmp/discovery.db"
    assert payload.nmap_path == "/usr/bin/nmap"
    assert payload.targets == ["10.0.0.0/24"]
    assert payload.ssh_ports == [22]
    assert payload.snmp_ports == [161]
    assert payload.max_concurrent_probes == 99
    assert payload.probe_timeout == 7.5
    assert payload.ssh_credentials == [
        {"username": "admin", "password": "secret", "enable_password": ""}
    ]
    assert payload.snmp_credentials == [
        {
            "community": "public",
            "version": "v2c",
            "username": None,
            "auth_protocol": None,
            "auth_password": None,
            "priv_protocol": None,
            "priv_password": None,
        }
    ]
    assert captured["start_new_session"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_task_terminates_worker_and_marks_task_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_store = _FakeTaskStore()
    engine = DiscoveryEngine(task_store=task_store)
    process = _FakePopen([], True)
    engine._running_tasks["task-123"] = process

    terminated: list[int] = []
    monkeypatch.setattr(
        DiscoveryEngine,
        "_terminate_process",
        staticmethod(lambda proc: terminated.append(proc.pid)),
    )

    cancelled = await engine.cancel_task("task-123")

    assert cancelled is True
    assert terminated == [4321]
    assert task_store.statuses == [("task-123", TaskStatus.CANCELLED, "")]
    assert "task-123" not in engine._running_tasks
