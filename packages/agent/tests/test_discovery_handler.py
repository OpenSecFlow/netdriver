#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass

import pytest

from netdriver_agent.discovery.engine.models import DiscoveredDevice, DiscoveryTask, TaskStatus

from netdriver_agent.handlers.discovery_handler import DiscoveryRequestHandler
from netdriver_agent.models.discovery import (
    DiscoveryPortsModel,
    DiscoveryRequest,
    SnmpCredentialModel,
    SshCredentialModel,
)


@dataclass
class _FakeEngine:
    captured: dict[str, object]

    def __init__(self) -> None:
        self.captured = {}

    async def start_discovery(self, **kwargs: object) -> str:
        self.captured = kwargs
        return "task-123"

    async def cancel_task(self, task_id: str) -> bool:
        return task_id == "task-123"


@dataclass
class _FakeTaskStore:
    task: DiscoveryTask | None = None

    async def count_running_tasks(self) -> int:
        return 0

    async def get_task(self, task_id: str) -> DiscoveryTask | None:
        if self.task and self.task.id == task_id:
            return self.task
        return None

    async def list_tasks(self) -> list[DiscoveryTask]:
        return [self.task] if self.task else []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_discovery_passes_request_overrides_to_engine() -> None:
    engine = _FakeEngine()
    task_store = _FakeTaskStore()
    handler = DiscoveryRequestHandler(engine=engine, task_store=task_store)

    response = await handler.start_discovery(
        DiscoveryRequest(
            targets=["10.0.0.0/24"],
            ports=DiscoveryPortsModel(ssh=[22], snmp=[161]),
            ssh_credentials=[
                SshCredentialModel(username="admin", password="secret")
            ],
            snmp_credentials=[SnmpCredentialModel(community="public")],
            max_concurrent_probes=88,
            probe_timeout=9.5,
        )
    )

    assert response.task_id == "task-123"
    assert engine.captured["targets"] == ["10.0.0.0/24"]
    assert engine.captured["ssh_ports"] == [22]
    assert engine.captured["snmp_ports"] == [161]
    assert engine.captured["max_concurrent_probes"] == 88
    assert engine.captured["probe_timeout"] == 9.5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_status_does_not_include_mac_field() -> None:
    engine = _FakeEngine()
    task_store = _FakeTaskStore(
        task=DiscoveryTask(
            id="task-123",
            status=TaskStatus.COMPLETED,
            targets=["10.0.0.0/24"],
            total_hosts=1,
            completed_hosts=1,
            devices=[
                DiscoveredDevice(
                    ip="10.0.0.1",
                    vendor="Cisco",
                    model="N9K",
                    method="ssh",
                )
            ],
        )
    )
    handler = DiscoveryRequestHandler(engine=engine, task_store=task_store)

    response = await handler.get_task_status("task-123")

    payload = response.model_dump()
    assert payload["devices"][0]["ip"] == "10.0.0.1"
    assert payload["devices"][0]["vendor"] == "Cisco"
    assert "serial_number" in payload["devices"][0]
    assert "mac" not in payload["devices"][0]
