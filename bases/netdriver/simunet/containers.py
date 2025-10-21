#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration

from netdriver.utils.config import get_config_path


class Container(DeclarativeContainer):
    """ IoC container of simunet. """
    config = Configuration()


container = Container()
config_path = get_config_path('simunet')
container.config.from_yaml(config_path, required=True)
