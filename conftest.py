#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

_ARG_MOCK_DEV = "--mock-dev"

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(_ARG_MOCK_DEV, action="store_true", help="use mock device")
