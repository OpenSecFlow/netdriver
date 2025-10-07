#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import enum


class Mode(enum.StrEnum):
    """
    Network device session privilege levels for command execution.
    
    Different commands require different privilege levels on network devices.
    This enum standardizes access levels across various device types and vendors.
    """
    # Basic user-level access - read-only operations, show commands
    LOGIN = "login"
    
    # Administrative access - system configuration viewing, advanced diagnostics  
    ENABLE = "enable"
    
    # Configuration mode - device settings modification, write operations
    CONFIG = "config"
    
    # Meta-mode representing all privilege levels for bulk operations
    # Used when command compatibility spans multiple modes
    UNION = "union"
