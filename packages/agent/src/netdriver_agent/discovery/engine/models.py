#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class DiscoveredDevice:
    """A device discovered during a discovery task."""
    ip: str
    vendor: str = ""
    model: str = ""
    version: str = ""
    hostname: str = ""
    method: str = ""
    serial_number: str = ""
    ssh_username: str | None = None
    snmp_community: str | None = None
    raw_data: str = ""
    discovered_at: datetime | None = None


@dataclass
class DiscoveryTask:
    """State of a discovery task."""
    id: str
    status: TaskStatus = TaskStatus.PENDING
    targets: list[str] = field(default_factory=list)
    total_hosts: int = 0
    completed_hosts: int = 0
    devices: list[DiscoveredDevice] = field(default_factory=list)
    error_message: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def progress(self) -> float:
        if self.total_hosts == 0:
            return 0.0
        return self.completed_hosts / self.total_hosts
