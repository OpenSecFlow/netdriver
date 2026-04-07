#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pydantic models for discovery API request/response."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from netdriver_agent.models.common import CommonResponse


class SshCredentialModel(BaseModel):
    """SSH credential in API request."""
    username: str
    password: str
    enable_password: str = ""


class SnmpCredentialModel(BaseModel):
    """SNMP credential in API request."""
    community: str | None = None
    version: str = "v2c"
    username: str | None = None
    auth_protocol: str | None = None
    auth_password: str | None = None
    priv_protocol: str | None = None
    priv_password: str | None = None


class DiscoveryPortsModel(BaseModel):
    """Protocol-scoped ports for discovery scan."""

    ssh: list[int] = Field(
        default_factory=lambda: [22],
        description="TCP ports to scan for SSH",
        examples=[[22]],
    )
    snmp: list[int] = Field(
        default_factory=lambda: [161],
        description="UDP ports to scan for SNMP",
        examples=[[161]],
    )

    @field_validator("ssh", "snmp")
    @classmethod
    def validate_ports(cls, ports: list[int]) -> list[int]:
        """Ensure ports are valid and deduplicated."""
        normalized_ports: list[int] = []
        for port in ports:
            if not 1 <= port <= 65535:
                raise ValueError("port must be between 1 and 65535")
            if port not in normalized_ports:
                normalized_ports.append(port)
        return normalized_ports

    @model_validator(mode="after")
    def ensure_ports_configured(self) -> Self:
        """Require at least one protocol port to scan."""
        if not self.ssh and not self.snmp:
            raise ValueError("at least one SSH or SNMP port must be configured")
        return self


class DiscoveryRequest(BaseModel):
    """Request body for POST /api/v1/discovery."""
    targets: list[str] = Field(
        ...,
        description="CIDR or IP ranges to scan",
        examples=[["192.168.1.0/24", "10.0.0.1-10"]],
    )
    ports: DiscoveryPortsModel = Field(
        default_factory=DiscoveryPortsModel,
        description="Protocol-scoped ports to scan",
        examples=[{"ssh": [22], "snmp": [161]}],
    )
    ssh_credentials: list[SshCredentialModel] = Field(
        default_factory=list,
        description="SSH credentials to try",
    )
    snmp_credentials: list[SnmpCredentialModel] = Field(
        default_factory=list,
        description="SNMP credentials to try",
    )
    max_concurrent_probes: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum concurrent probes",
    )
    probe_timeout: float = Field(
        default=30.0,
        gt=0,
        description="Per-probe timeout in seconds",
    )


class DiscoveredDeviceModel(BaseModel):
    """A discovered device in API response."""
    ip: str
    vendor: str = ""
    model: str = ""
    version: str = ""
    hostname: str = ""
    serial_number: str = ""
    method: str = ""
    ssh_username: str | None = None
    snmp_community: str | None = None
    discovered_at: str | None = None


class DiscoveryResponse(CommonResponse):
    """Response for POST /api/v1/discovery (task created)."""
    task_id: str = Field(description="Discovery task ID for polling")


class DiscoveryStatusResponse(CommonResponse):
    """Response for GET /api/v1/discovery/{task_id}."""
    task_id: str
    status: str
    progress: float = Field(description="0.0 ~ 1.0")
    total_hosts: int = 0
    completed_hosts: int = 0
    devices: list[DiscoveredDeviceModel] = Field(default_factory=list)
    error_message: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class DiscoveryTaskSummary(BaseModel):
    """Summary of a discovery task for list endpoint."""
    task_id: str
    status: str
    targets: list[str] = Field(default_factory=list)
    progress: float = 0.0
    total_hosts: int = 0
    completed_hosts: int = 0
    created_at: str | None = None
    updated_at: str | None = None
