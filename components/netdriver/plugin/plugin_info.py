#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class PluginInfo:
    ''' Plugin Info '''
    vendor: str
    model: str
    version: str
    description: str
