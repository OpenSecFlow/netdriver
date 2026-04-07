#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe result model for device identification."""

from dataclasses import dataclass


@dataclass
class ProbeResult:
    """Result of a device probe command."""

    vendor: str = ""
    model: str = ""
    version: str = ""
    hostname: str = ""
    serial_number: str = ""
