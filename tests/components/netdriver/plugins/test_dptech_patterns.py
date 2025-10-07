#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.dptech import DptechBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = DptechBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("<hostname>")
    assert enable_pattern.search("<hostname> ")
    assert enable_pattern.search("<hostname> \n")
    assert enable_pattern.search("<hostname> \r\n")
    assert enable_pattern.search("\n<hostname> \n")
    assert enable_pattern.search("\r\n<hostname> \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = DptechBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("[hostname]")
    assert config_pattern.search("[hostname] ")
    assert config_pattern.search("[hostname] \n")
    assert config_pattern.search("[hostname] \r\n")
    assert config_pattern.search("\n[hostname] \n")
    assert config_pattern.search("\r\n[hostname] \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = DptechBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("<hostname>")
    assert union_pattern.search("<hostname> ")
    assert union_pattern.search("<hostname> \n")
    assert union_pattern.search("<hostname> \r\n")
    assert union_pattern.search("\n<hostname> \n")
    assert union_pattern.search("\r\n<hostname> \r\n")
    assert union_pattern.search("[hostname]")
    assert union_pattern.search("[hostname] ")
    assert union_pattern.search("[hostname] \n")
    assert union_pattern.search("[hostname] \r\n")
    assert union_pattern.search("\n[hostname] \n")
    assert union_pattern.search("\r\n[hostname] \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("% Unknown command."),
    ("Can't find the test object"),
    ("Invalid parameter."),
    ("% Command can not contain: test"),
    ("Undefined error.")
])
async def test_error_catch(output: str):
    error_patterns = DptechBase.PatternHelper.get_error_patterns()
    ignore_patterns = DptechBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
