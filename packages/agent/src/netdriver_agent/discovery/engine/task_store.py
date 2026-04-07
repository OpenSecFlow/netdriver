#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQLite-based persistent task store for discovery tasks."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from netdriver_core.log import logman
from netdriver_agent.discovery.engine.models import (
    DiscoveredDevice,
    DiscoveryTask,
    TaskStatus,
)

log = logman.logger

_CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS discovery_tasks (
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

_CREATE_DEVICES_TABLE = """
CREATE TABLE IF NOT EXISTS discovered_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES discovery_tasks(id) ON DELETE CASCADE,
    ip TEXT NOT NULL,
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

_CREATE_DEVICES_INDEX = """
CREATE INDEX IF NOT EXISTS idx_devices_task_id ON discovered_devices(task_id)
"""


class TaskStore:
    """SQLite-backed persistent store for discovery tasks and results."""

    def __init__(self, db_path: str = "data/discovery.db"):
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init_db(self) -> None:
        """Initialize database and create tables if needed."""
        db_path = Path(self._db_path)
        if db_path.parent != Path():
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA journal_mode=WAL")
        await self._db.execute("PRAGMA foreign_keys=ON")
        await self._db.execute(_CREATE_TASKS_TABLE)
        await self._db.execute(_CREATE_DEVICES_TABLE)
        await self._db.execute(_CREATE_DEVICES_INDEX)
        await self._db.commit()
        log.info(f"TaskStore initialized: {self._db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    async def create_task(self, targets: list[str]) -> str:
        """Create a new discovery task.

        Args:
            targets: List of CIDR/IP range strings.

        Returns:
            Generated task_id (UUID).
        """
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        targets_json = json.dumps(targets)

        await self._db.execute(
            "INSERT INTO discovery_tasks (id, status, targets, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (task_id, TaskStatus.PENDING, targets_json, now, now),
        )
        await self._db.commit()
        log.info(f"Created discovery task: {task_id}")
        return task_id

    async def get_task(self, task_id: str) -> DiscoveryTask | None:
        """Get task by ID with all discovered devices.

        Args:
            task_id: Task UUID.

        Returns:
            DiscoveryTask or None if not found.
        """
        async with self._db.execute(
            "SELECT * FROM discovery_tasks WHERE id = ?", (task_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None

        task = self._row_to_task(row)

        # Fetch discovered devices
        async with self._db.execute(
            "SELECT * FROM discovered_devices WHERE task_id = ? ORDER BY discovered_at",
            (task_id,),
        ) as cursor:
            async for device_row in cursor:
                task.devices.append(self._row_to_device(device_row))

        return task

    async def list_tasks(self) -> list[DiscoveryTask]:
        """List all tasks (without devices for efficiency).

        Returns:
            List of DiscoveryTask (devices list will be empty).
        """
        tasks = []
        async with self._db.execute(
            "SELECT * FROM discovery_tasks ORDER BY created_at DESC"
        ) as cursor:
            async for row in cursor:
                tasks.append(self._row_to_task(row))
        return tasks

    async def set_status(self, task_id: str, status: TaskStatus, error_message: str = "") -> None:
        """Update task status.

        Args:
            task_id: Task UUID.
            status: New status.
            error_message: Error message (for FAILED status).
        """
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE discovery_tasks SET status = ?, error_message = ?, updated_at = ? WHERE id = ?",
            (status, error_message, now, task_id),
        )
        await self._db.commit()

    async def update_progress(self, task_id: str, completed: int, total: int) -> None:
        """Update task progress counters.

        Args:
            task_id: Task UUID.
            completed: Number of completed hosts.
            total: Total number of hosts.
        """
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE discovery_tasks SET completed_hosts = ?, total_hosts = ?, updated_at = ? WHERE id = ?",
            (completed, total, now, task_id),
        )
        await self._db.commit()

    async def add_device(self, task_id: str, device: DiscoveredDevice) -> None:
        """Add a discovered device to the task results.

        Args:
            task_id: Task UUID.
            device: Discovered device data.
        """
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            """INSERT INTO discovered_devices
            (task_id, ip, vendor, model, version, hostname, method, ssh_username, snmp_community, raw_data, discovered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task_id,
                device.ip,
                device.vendor,
                device.model,
                device.version,
                device.hostname,
                device.method,
                device.ssh_username,
                device.snmp_community,
                device.raw_data,
                now,
            ),
        )
        await self._db.commit()

    async def count_running_tasks(self) -> int:
        """Count currently running tasks."""
        async with self._db.execute(
            "SELECT COUNT(*) FROM discovery_tasks WHERE status IN (?, ?)",
            (TaskStatus.PENDING, TaskStatus.RUNNING),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def cleanup_expired(self, retention_seconds: int) -> int:
        """Delete completed/failed tasks older than retention period.

        Args:
            retention_seconds: Maximum age in seconds.

        Returns:
            Number of tasks deleted.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - retention_seconds
        cutoff_iso = datetime.fromtimestamp(cutoff, timezone.utc).isoformat()

        async with self._db.execute(
            "SELECT COUNT(*) FROM discovery_tasks WHERE status IN (?, ?, ?) AND updated_at < ?",
            (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, cutoff_iso),
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0

        if count > 0:
            await self._db.execute(
                "DELETE FROM discovery_tasks WHERE status IN (?, ?, ?) AND updated_at < ?",
                (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, cutoff_iso),
            )
            await self._db.commit()
            log.info(f"Cleaned up {count} expired discovery task(s)")

        return count

    @staticmethod
    def _row_to_task(row) -> DiscoveryTask:
        """Convert database row to DiscoveryTask."""
        targets = json.loads(row["targets"]) if row["targets"] else []
        return DiscoveryTask(
            id=row["id"],
            status=TaskStatus(row["status"]),
            targets=targets,
            total_hosts=row["total_hosts"] or 0,
            completed_hosts=row["completed_hosts"] or 0,
            error_message=row["error_message"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_device(row) -> DiscoveredDevice:
        """Convert database row to DiscoveredDevice."""
        return DiscoveredDevice(
            ip=row["ip"],
            vendor=row["vendor"] or "",
            model=row["model"] or "",
            version=row["version"] or "",
            hostname=row["hostname"] or "",
            method=row["method"] or "",
            ssh_username=row["ssh_username"],
            snmp_community=row["snmp_community"],
            raw_data=row["raw_data"] or "",
            discovered_at=row["discovered_at"],
        )
