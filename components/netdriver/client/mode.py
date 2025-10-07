#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import enum


class Mode(enum.StrEnum):
    """ Session Mode """
    LOGIN = "login"
    ENABLE = "enable"
    CONFIG = "config"
    # all the modes
    UNION = "union"
