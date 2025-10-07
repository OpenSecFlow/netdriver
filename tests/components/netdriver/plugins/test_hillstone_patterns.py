#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.utils import regex
from netdriver.plugins.hillstone import HillstoneBase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = HillstoneBase.PatternHelper.get_enable_prompt_pattern()
    assert not enable_pattern.search("hostname#")
    assert enable_pattern.search("hostname# ")
    assert enable_pattern.search("hostname# \n")
    assert enable_pattern.search("hostname# \r\n")
    assert enable_pattern.search("\nhostname# \n")
    assert enable_pattern.search("\r\nhostname# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = HillstoneBase.PatternHelper.get_config_prompt_pattern()
    assert not config_pattern.search("hostname(config)#")
    assert config_pattern.search("hostname(config)# ")
    assert config_pattern.search("hostname(config)# \n")
    assert config_pattern.search("hostname(config)# \r\n")
    assert config_pattern.search("\nhostname(config)# \n")
    assert config_pattern.search("\r\nhostname(config)# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = HillstoneBase.PatternHelper.get_union_pattern()
    assert not union_pattern.search("hostname#")
    assert union_pattern.search("hostname# ")
    assert union_pattern.search("hostname# \n")
    assert union_pattern.search("hostname# \r\n")
    assert union_pattern.search("\nhostname# \n")
    assert union_pattern.search("\r\nhostname# \r\n")
    assert not union_pattern.search("hostname(config)#")
    assert union_pattern.search("hostname(config)# ")
    assert union_pattern.search("hostname(config)# \n")
    assert union_pattern.search("hostname(config)# \r\n")
    assert union_pattern.search("\nhostname(config)# \n")
    assert union_pattern.search("\r\nhostname(config)# \r\n")
    assert not union_pattern.search("hostname(config-policy-rule)#")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("\n           ^-----unrecognized keyword aa"),
    ("\n           ^-----incomplete command aas"),
    ("Error: Address as is not found"),
    ("Error: This name is used by another policy rule"),
    ("Error: Rule 9 is not found in this context"),
    ("Error: Maximum is smaller than minimum"),
    ('Error: This address entry is used by policy "5" and cannot be deleted'),
    ('Error: Service entity UDP-232 is used by Policy rule id 5'),
    ('Error:Start time is greater than end time!'),
    ('Error: Schedule Schedule_e796e021750334cb is in use by Policy id 5'),
    ("         ^-----无法识别的关键字: skdjf"),
    ("                   ^-----不完整的命令"),
    ("错误：此名称已经被其他的策略规则使用")
])
async def test_error_catch(output: str):
    error_patterns = HillstoneBase.PatternHelper.get_error_patterns()
    ignore_patterns = HillstoneBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
