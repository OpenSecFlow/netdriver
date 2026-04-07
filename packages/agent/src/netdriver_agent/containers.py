#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton, Configuration
from netdriver_agent.handlers.cmd_req_handler import CommandRequestHandler
from netdriver_agent.handlers.conn_req_handler import ConnectRequestHandler
from netdriver_agent.handlers.discovery_handler import DiscoveryRequestHandler
from netdriver_agent.discovery.engine.discovery_engine import DiscoveryEngine
from netdriver_agent.discovery.engine.task_store import TaskStore


class Container(DeclarativeContainer):
    """ IoC container of netdriver agent. """
    config = Configuration()
    cmd_req_handler = Factory(CommandRequestHandler)
    conn_req_handler = Factory(ConnectRequestHandler)
    task_store = Singleton(
        TaskStore,
        db_path=config.discovery.db_path,
    )
    discovery_engine = Singleton(
        DiscoveryEngine,
        task_store=task_store,
        db_path=config.discovery.db_path,
        nmap_path=config.discovery.nmap_path,
        max_concurrent_probes=config.discovery.max_concurrent_probes,
        probe_timeout=config.discovery.probe_timeout,
        ssh_connect_timeout=config.discovery.ssh.connect_timeout,
        ssh_read_timeout=config.discovery.ssh.read_timeout,
        snmp_timeout=config.discovery.snmp.timeout,
        snmp_retries=config.discovery.snmp.retries,
        plugin_modules=["netdriver_agent.plugins"],
    )
    discovery_handler = Factory(
        DiscoveryRequestHandler,
        engine=discovery_engine,
        task_store=task_store,
    )


def get_config_file() -> str:
    """Get config file path from environment variable or use default."""
    return os.getenv("NETDRIVER_AGENT_CONFIG", "config/agent/agent.yml")


def configure_discovery_vendor_map() -> None:
    """Export discovery vendor map config for subprocess workers."""
    vendor_map_file = container.config.discovery.vendor_map_file()
    if vendor_map_file:
        os.environ["NETDRIVER_DISCOVERY_VENDOR_MAP"] = vendor_map_file
        return

    os.environ.pop("NETDRIVER_DISCOVERY_VENDOR_MAP", None)


container = Container()
container.config.from_yaml(get_config_file())
configure_discovery_vendor_map()
