#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from netdriver_agent.discovery.engine.models import DiscoveredDevice
from netdriver_agent.discovery.engine.task_store import TaskStore


@pytest.mark.unit
@pytest.mark.asyncio
async def test_init_db_creates_device_table_without_mac_column(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "discovery.db"
    task_store = TaskStore(db_path=str(db_path))

    await task_store.init_db()
    await task_store.close()

    with sqlite3.connect(db_path) as connection:
        columns = [
            row[1]
            for row in connection.execute("PRAGMA table_info(discovered_devices)")
        ]

    assert "mac" not in columns


@pytest.mark.unit
@pytest.mark.asyncio
async def test_existing_schema_with_mac_column_remains_compatible(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE discovery_tasks (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'PENDING',
                targets TEXT NOT NULL,
                total_hosts INTEGER DEFAULT 0,
                completed_hosts INTEGER DEFAULT 0,
                error_message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE discovered_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                ip TEXT NOT NULL,
                mac TEXT,
                vendor TEXT DEFAULT '',
                model TEXT DEFAULT '',
                version TEXT DEFAULT '',
                hostname TEXT DEFAULT '',
                method TEXT DEFAULT '',
                ssh_username TEXT,
                snmp_community TEXT,
                raw_data TEXT DEFAULT '',
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()

    task_store = TaskStore(db_path=str(db_path))
    await task_store.init_db()

    task_id = await task_store.create_task(["10.0.0.0/24"])
    await task_store.add_device(
        task_id,
        DiscoveredDevice(
            ip="10.0.0.1",
            vendor="Cisco",
            model="N9K",
            method="ssh",
        ),
    )

    task = await task_store.get_task(task_id)
    await task_store.close()

    assert task is not None
    assert len(task.devices) == 1
    assert task.devices[0].ip == "10.0.0.1"
    assert task.devices[0].vendor == "Cisco"
