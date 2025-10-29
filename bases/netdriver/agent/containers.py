#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Configuration
from netdriver.agent.handlers.cmd_req_handler import CommandRequestHandler
from netdriver.agent.handlers.conn_req_handler import ConnectRequestHandler


class Container(DeclarativeContainer):
    """ IoC container of netdriver agent. """
    config = Configuration()
    cmd_req_handler = Factory(CommandRequestHandler)
    conn_req_handler = Factory(ConnectRequestHandler)


def get_config_file() -> str:
    """Get config file path from environment variable or use default."""
    return os.getenv("NETDRIVER_AGENT_CONFIG", "config/agent/agent.yml")


container = Container()
container.config.from_yaml(get_config_file())
