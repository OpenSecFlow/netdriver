#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration


class Container(DeclarativeContainer):
    """ IoC container of simunet. """
    config = Configuration()


def get_config_file() -> str:
    """Get config file path from environment variable or use default."""
    return os.getenv("NETDRIVER_SIMUNET_CONFIG", "config/simunet/simunet.yml")


container = Container()
container.config.from_yaml(get_config_file(), required=True)
