#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration utilities for finding config files.
Prioritizes local config directory, then falls back to system-wide config.
"""
import os
from pathlib import Path
from typing import Optional


def find_config_file(config_name: str) -> Optional[str]:
    """
    Find configuration file with priority order:
    1. Current directory: ./config/{config_name}/{config_name}.yml
    2. System directory: /etc/netdriver/{config_name}.yml
    
    Args:
        config_name: Name of the config ('agent' or 'simunet')
    
    Returns:
        Absolute path to config file if found, None otherwise
    """
    # Method 1: Try current working directory first (./config/)
    local_config_path = Path.cwd() / "config"  / f"{config_name}.yml"
    if local_config_path.exists():
        return str(local_config_path)
    
    # Method 2: Try system-wide config directory (/etc/netdriver/)
    system_config_path = Path.cwd()/"netdriver" / f"{config_name}.yml"
    if system_config_path.exists():
        return str(system_config_path)
    
    return None


def get_config_path(config_name: str) -> str:
    """
    Get the path to a specific config file.
    
    Args:
        config_name: Name of the config ('agent' or 'simunet')
    
    Returns:
        Path to the config file
        
    Raises:
        FileNotFoundError: If config file cannot be found
    """
    if config_name not in ['agent', 'simunet']:
        raise ValueError(f"Unknown config name: {config_name}. Must be 'agent' or 'simunet'")
    
    config_path = find_config_file(config_name)
    if config_path is None:
        # Provide detailed error information
        local_path = Path.cwd() / "config" / f"{config_name}.yml"
        system_path = Path.cwd() / "netdriver" / f"{config_name}.yml"
        
        error_msg = f"Could not find config file for '{config_name}'\n"
        error_msg += "Searched in:\n"
        error_msg += f"  - Local config: {local_path}\n"
        error_msg += f"  - System config: {system_path}\n"
        error_msg += "\nPlease ensure the config file exists in one of these locations."
        
        raise FileNotFoundError(error_msg)
    
    return config_path