#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.juniper import JuniperBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = JuniperBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("user@hostname>")
    assert enable_pattern.search("user@hostname> ")
    assert enable_pattern.search("user@hostname> \n")
    assert enable_pattern.search("user@hostname> \r\n")
    assert enable_pattern.search("\nuser@hostname> \n")
    assert enable_pattern.search("\r\nuser@hostname> \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = JuniperBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("user@hostname#")
    assert config_pattern.search("user@hostname# ")
    assert config_pattern.search("user@hostname# \n")
    assert config_pattern.search("user@hostname# \r\n")
    assert config_pattern.search("\nuser@hostname# \n")
    assert config_pattern.search("\r\nuser@hostname# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = JuniperBase.PatternHelper.get_union_pattern()
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
    ("                  ^\nunknown command."),
    ("                       ^\nsyntax error, expecting <command>."),
    ("                                   ^syntax error."),
    ("error: device xfds not found"),
    ("error: could not resolve name: 100.1.1.-1: 100.1.1.-1"),
    ("invalid value '256' in ip address: '100.1.1.256' at '100.1.1.256'"),
    ("missing or invalid prefix length '-1' in address '100.1.1.0/-1' at '100.1.1.0/-1'"),
    ("prefix length '33' is larger than 32 in address '100.1.1.0/33' at '100.1.1.0/33'"),
    ("invalid ip address or hostname: ::-1 at '::-1'"),
    ("number: '256': Value must be a number from 0 to 255 at '256'")
])
async def test_error_catch(output: str):
    error_patterns = JuniperBase.PatternHelper.get_error_patterns()
    ignore_patterns = JuniperBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
