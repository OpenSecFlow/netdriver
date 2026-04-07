#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field


@dataclass
class HostInfo:
    """Discovered host from Nmap host discovery."""
    ip: str
    vendor_hint: str | None = None
    hostname: str | None = None


@dataclass
class ScanResult:
    """Port scan result for a single host."""
    ip: str
    vendor_hint: str | None = None
    hostname: str | None = None
    has_ssh: bool = False
    has_snmp: bool = False
    open_ports: list[int] = field(default_factory=list)
    ssh_ports: list[int] = field(default_factory=list)
    snmp_ports: list[int] = field(default_factory=list)
