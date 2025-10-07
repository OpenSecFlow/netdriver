#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.paloalto import PaloaltoBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = PaloaltoBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("user@hostname>")
    assert enable_pattern.search("user@hostname> ")
    assert enable_pattern.search("user@hostname> \n")
    assert enable_pattern.search("user@hostname> \r\n")
    assert enable_pattern.search("\nuser@hostname> \n")
    assert enable_pattern.search("\r\nuser@hostname> \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = PaloaltoBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("user@hostname#")
    assert config_pattern.search("user@hostname# ")
    assert config_pattern.search("user@hostname# \n")
    assert config_pattern.search("user@hostname# \r\n")
    assert config_pattern.search("\nuser@hostname# \n")
    assert config_pattern.search("\r\nuser@hostname# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = PaloaltoBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("user@hostname>")
    assert union_pattern.search("user@hostname> ")
    assert union_pattern.search("user@hostname> \n")
    assert union_pattern.search("user@hostname> \r\n")
    assert union_pattern.search("\nuser@hostname> \n")
    assert union_pattern.search("\r\nuser@hostname> \r\n")
    assert union_pattern.search("user@hostname#")
    assert union_pattern.search("user@hostname# ")
    assert union_pattern.search("user@hostname# \n")
    assert union_pattern.search("user@hostname# \r\n")
    assert union_pattern.search("\nuser@hostname# \n")
    assert union_pattern.search("\r\nuser@hostname# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("Unknown command: kskl"),
    ("Invalid syntax."),
    ("Server error: grp -> static '1' is not a valid reference\ngrp -> static is invalid"),
    ("Validation Error:\nservice -> test  is missing 'protocol'\nservice is invalid"),
    ("  Error: Fail to count address groups\n(Module: device)\nCommit failed")
])
async def test_error_catch(output: str):
    error_patterns = PaloaltoBase.PatternHelper.get_error_patterns()
    ignore_patterns = PaloaltoBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
