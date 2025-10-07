#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from netdriver.plugins.check_point import CheckPointBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = CheckPointBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("hostname>")
    assert enable_pattern.search("hostname> ")
    assert enable_pattern.search("hostname> \n")
    assert enable_pattern.search("hostname> \r\n")
    assert enable_pattern.search("\nhostname> \n")
    assert enable_pattern.search("\r\nhostname> \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = CheckPointBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("hostname>")
    assert union_pattern.search("hostname> ")
    assert union_pattern.search("hostname> \n")
    assert union_pattern.search("hostname> \r\n")
    assert union_pattern.search("\nhostname> \n")
    assert union_pattern.search("\r\nhostname> \r\n")



@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("CLINFR0329  Invalid command:'xxxx'."),
    ("CLINFR0339  Incomplete command.")
])
async def test_error_catch(output: str):
    error_patterns = CheckPointBase.PatternHelper.get_error_patterns()
    ignore_patterns = CheckPointBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str