#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class SnmpCredential:
    """SNMP credential for authentication."""
    # SNMPv2c
    community: str | None = None
    version: str = "v2c"
    # SNMPv3
    username: str | None = None
    auth_protocol: str | None = None
    auth_password: str | None = None
    priv_protocol: str | None = None
    priv_password: str | None = None


@dataclass
class SnmpResult:
    """Result of an SNMP GET/WALK operation."""
    success: bool
    data: dict[str, str] | None = None
    error: str | None = None
