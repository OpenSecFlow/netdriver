#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import StrEnum


class ConfigType(StrEnum):
    """ Config Type Enum """

    RUNNING = "running"
    ROUTE = "route"
    HIT_COUNT = "hit_count"
