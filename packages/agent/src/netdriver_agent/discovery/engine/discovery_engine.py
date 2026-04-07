#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discovery engine subprocess scheduler."""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
from dataclasses import asdict

from netdriver_core.log import logman
from netdriver_core.nmap.scanner import DEFAULT_SNMP_PORTS, DEFAULT_SSH_PORTS
from netdriver_core.snmp.models import SnmpCredential

from netdriver_agent.discovery.engine.models import TaskStatus
from netdriver_agent.discovery.engine.task_store import TaskStore
from netdriver_agent.discovery.engine.worker import DiscoveryWorkerPayload
from netdriver_agent.discovery.probe.models import SshCredential

log = logman.logger


class DiscoveryEngine:
    """Schedules discovery tasks into isolated subprocess workers."""

    def __init__(
        self,
        task_store: TaskStore,
        db_path: str = "data/discovery.db",
        nmap_path: str = "nmap",
        max_concurrent_probes: int = 50,
        probe_timeout: float = 30.0,
        ssh_connect_timeout: float = 10.0,
        ssh_read_timeout: float = 5.0,
        snmp_timeout: float = 5.0,
        snmp_retries: int = 1,
        plugin_modules: list[str] | None = None,
    ) -> None:
        self._task_store = task_store
        self._db_path = db_path
        self._nmap_path = nmap_path
        self._max_concurrent = max_concurrent_probes
        self._probe_timeout = probe_timeout
        self._ssh_connect_timeout = ssh_connect_timeout
        self._ssh_read_timeout = ssh_read_timeout
        self._snmp_timeout = snmp_timeout
        self._snmp_retries = snmp_retries
        self._plugin_modules = plugin_modules or []
        self._running_tasks: dict[str, subprocess.Popen] = {}

    async def start_discovery(
        self,
        targets: list[str],
        ssh_ports: list[int] | None = None,
        snmp_ports: list[int] | None = None,
        ssh_credentials: list[SshCredential] | None = None,
        snmp_credentials: list[SnmpCredential] | None = None,
        max_concurrent_probes: int | None = None,
        probe_timeout: float | None = None,
    ) -> str:
        """Create a task record and launch a subprocess worker."""
        self._cleanup_finished_processes()

        task_id = await self._task_store.create_task(targets)
        payload = DiscoveryWorkerPayload(
            task_id=task_id,
            db_path=self._db_path,
            nmap_path=self._nmap_path,
            targets=targets,
            ssh_ports=(
                ssh_ports if ssh_ports is not None else DEFAULT_SSH_PORTS
            ),
            snmp_ports=(
                snmp_ports if snmp_ports is not None else DEFAULT_SNMP_PORTS
            ),
            ssh_credentials=[
                asdict(credential) for credential in (ssh_credentials or [])
            ],
            snmp_credentials=[
                asdict(credential) for credential in (snmp_credentials or [])
            ],
            max_concurrent_probes=(
                max_concurrent_probes
                if max_concurrent_probes is not None else self._max_concurrent
            ),
            probe_timeout=(
                probe_timeout if probe_timeout is not None else self._probe_timeout
            ),
            ssh_connect_timeout=self._ssh_connect_timeout,
            ssh_read_timeout=self._ssh_read_timeout,
            snmp_timeout=self._snmp_timeout,
            snmp_retries=self._snmp_retries,
            plugin_modules=self._plugin_modules,
        )

        command = [
            sys.executable,
            "-m",
            "netdriver_agent.discovery.engine.worker",
            payload.to_json(),
        ]

        try:
            process = subprocess.Popen(
                command,
                start_new_session=True,
            )
        except OSError as exc:
            log.error(f"Failed to start discovery worker for task {task_id}: {exc}")
            await self._task_store.set_status(task_id, TaskStatus.FAILED, str(exc))
            return task_id

        self._running_tasks[task_id] = process
        log.info(f"Started discovery subprocess {process.pid} for task {task_id}")
        return task_id

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running discovery task by terminating its subprocess."""
        process = self._running_tasks.get(task_id)
        if process is None:
            self._cleanup_finished_processes()
            return False

        if process.poll() is not None:
            self._cleanup_finished_processes()
            return False

        self._terminate_process(process)

        try:
            await asyncio.to_thread(process.wait, 5)
        except subprocess.TimeoutExpired:
            self._kill_process(process)
            await asyncio.to_thread(process.wait, 5)

        await self._task_store.set_status(task_id, TaskStatus.CANCELLED)
        log.info(f"Cancelled discovery task {task_id}")
        self._cleanup_finished_processes()
        return True

    def _cleanup_finished_processes(self) -> None:
        """Drop completed subprocess handles from memory."""
        finished_task_ids = [
            task_id
            for task_id, process in self._running_tasks.items()
            if process.poll() is not None
        ]
        for task_id in finished_task_ids:
            self._running_tasks.pop(task_id)

    @staticmethod
    def _terminate_process(process: subprocess.Popen) -> None:
        """Terminate the subprocess, preferring its whole process group."""
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGTERM)
            return
        process.terminate()

    @staticmethod
    def _kill_process(process: subprocess.Popen) -> None:
        """Force kill the subprocess, preferring its whole process group."""
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGKILL)
            return
        process.kill()
