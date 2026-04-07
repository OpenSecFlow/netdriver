#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handler for discovery API requests."""

from netdriver_core.exception.errors import (
    DiscoveryTaskLimitExceeded,
    DiscoveryTaskNotFound,
)
from netdriver_core.log import logman
from netdriver_core.snmp.models import SnmpCredential
from netdriver_agent.discovery.engine.discovery_engine import DiscoveryEngine
from netdriver_agent.discovery.engine.models import DiscoveryTask
from netdriver_agent.discovery.engine.task_store import TaskStore
from netdriver_agent.discovery.probe.models import SshCredential

from netdriver_agent.models.discovery import (
    DiscoveredDeviceModel,
    DiscoveryRequest,
    DiscoveryResponse,
    DiscoveryStatusResponse,
    DiscoveryTaskSummary,
)

log = logman.logger


class DiscoveryRequestHandler:
    """Handles discovery API logic."""

    def __init__(self, engine: DiscoveryEngine, task_store: TaskStore, max_tasks: int = 5):
        self._engine = engine
        self._task_store = task_store
        self._max_tasks = max_tasks

    async def start_discovery(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """Start a new discovery task.

        Args:
            request: DiscoveryRequest with targets and credentials.

        Returns:
            DiscoveryResponse with task_id.

        Raises:
            DiscoveryTaskLimitExceeded: If max concurrent tasks exceeded.
        """
        running = await self._task_store.count_running_tasks()
        if running >= self._max_tasks:
            raise DiscoveryTaskLimitExceeded(
                f"Maximum {self._max_tasks} concurrent discovery tasks allowed, "
                f"currently {running} running."
            )

        # Convert API models to internal models
        ssh_creds = [
            SshCredential(
                username=c.username,
                password=c.password,
                enable_password=c.enable_password,
            )
            for c in request.ssh_credentials
        ]
        snmp_creds = [
            SnmpCredential(
                community=c.community,
                version=c.version,
                username=c.username,
                auth_protocol=c.auth_protocol,
                auth_password=c.auth_password,
                priv_protocol=c.priv_protocol,
                priv_password=c.priv_password,
            )
            for c in request.snmp_credentials
        ]

        task_id = await self._engine.start_discovery(
            targets=request.targets,
            ssh_ports=request.ports.ssh,
            snmp_ports=request.ports.snmp,
            ssh_credentials=ssh_creds,
            snmp_credentials=snmp_creds,
            max_concurrent_probes=request.max_concurrent_probes,
            probe_timeout=request.probe_timeout,
        )

        log.info(f"Started discovery task {task_id} for targets {request.targets}")
        return DiscoveryResponse(code="OK", msg="", task_id=task_id)

    async def get_task_status(self, task_id: str) -> DiscoveryStatusResponse:
        """Get task status and results.

        Args:
            task_id: Task UUID.

        Returns:
            DiscoveryStatusResponse with task details and discovered devices.

        Raises:
            DiscoveryTaskNotFound: If task not found.
        """
        task = await self._task_store.get_task(task_id)
        if not task:
            raise DiscoveryTaskNotFound(f"Discovery task '{task_id}' not found.")

        return self._task_to_response(task)

    async def list_tasks(self) -> list[DiscoveryTaskSummary]:
        """List all discovery tasks.

        Returns:
            List of task summaries.
        """
        tasks = await self._task_store.list_tasks()
        return [
            DiscoveryTaskSummary(
                task_id=t.id,
                status=t.status,
                targets=t.targets,
                progress=t.progress,
                total_hosts=t.total_hosts,
                completed_hosts=t.completed_hosts,
                created_at=str(t.created_at) if t.created_at else None,
                updated_at=str(t.updated_at) if t.updated_at else None,
            )
            for t in tasks
        ]

    async def cancel_task(self, task_id: str) -> None:
        """Cancel a running task.

        Args:
            task_id: Task UUID.

        Raises:
            DiscoveryTaskNotFound: If task not found or already completed.
        """
        cancelled = await self._engine.cancel_task(task_id)
        if not cancelled:
            task = await self._task_store.get_task(task_id)
            if not task:
                raise DiscoveryTaskNotFound(f"Discovery task '{task_id}' not found.")
            # Task exists but is already done
            log.info(f"Discovery task {task_id} already in status {task.status}")

    @staticmethod
    def _task_to_response(task: DiscoveryTask) -> DiscoveryStatusResponse:
        """Convert internal task to API response."""
        devices = [
            DiscoveredDeviceModel(
                ip=d.ip,
                vendor=d.vendor,
                model=d.model,
                version=d.version,
                hostname=d.hostname,
                serial_number=d.serial_number,
                method=d.method,
                ssh_username=d.ssh_username,
                snmp_community=d.snmp_community,
                discovered_at=str(d.discovered_at) if d.discovered_at else None,
            )
            for d in task.devices
        ]

        return DiscoveryStatusResponse(
            code="OK",
            task_id=task.id,
            status=task.status,
            progress=task.progress,
            total_hosts=task.total_hosts,
            completed_hosts=task.completed_hosts,
            devices=devices,
            error_message=task.error_message,
            created_at=str(task.created_at) if task.created_at else None,
            updated_at=str(task.updated_at) if task.updated_at else None,
        )
