#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import StringIO
from typing import Dict, List
from netdriver.textfsm import parser

__all__ = ["parser"]


class TextFSMParser(object):
    _parser: parser.TextFSM

    def __init__(self, template):
        self._parser = parser.TextFSM(StringIO(template))

    def parse(self, text) -> list:
        res = self._parser.ParseTextToDicts(text)
        return res
