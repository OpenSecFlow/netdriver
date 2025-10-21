#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Configuration
from netdriver.agent.handlers.cmd_req_handler import CommandRequestHandler
from netdriver.agent.handlers.conn_req_handler import ConnectRequestHandler
from netdriver.utils.config import get_config_path


class Container(DeclarativeContainer):
    """ IoC container of netdriver agent. """
    config = Configuration(yaml_files=[get_config_path('agent')])
    cmd_req_handler = Factory(CommandRequestHandler)
    conn_req_handler = Factory(ConnectRequestHandler)

container = Container()
