#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration


class Container(DeclarativeContainer):
    """ IoC container of simunet. """
    config = Configuration()


container = Container()
container.config.from_yaml("config/simunet/simunet.yml", required=True)
