#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.chaitin import ChaiTinBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_pattern():
    login_pattern = ChaiTinBase.PatternHelper.get_login_prompt_pattern()
    assert login_pattern.search("\rhostname>")
    assert login_pattern.search("\r\nhostname>")
    assert login_pattern.search("hostname> ")
    assert login_pattern.search("hostname> \n")
    assert login_pattern.search("hostname> \r\n")
    assert not login_pattern.search('<not_hostname>')


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = ChaiTinBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("hostname#")
    assert enable_pattern.search("hostname# ")
    assert enable_pattern.search("hostname# \n")
    assert enable_pattern.search("hostname# \r\n")
    assert enable_pattern.search("\nhostname# \n")
    assert enable_pattern.search("\r\nhostname# \r\n")
    assert not enable_pattern.search("###")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = ChaiTinBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("hostname(config)#")
    assert config_pattern.search("hostname(config)# ")
    assert config_pattern.search("hostname(config)# \n")
    assert config_pattern.search("hostname(config)# \r\n")
    assert config_pattern.search("\nhostname(config)# \n")
    assert config_pattern.search("\r\nhostname(config)# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = ChaiTinBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("hostname>")
    assert union_pattern.search("hostname> ")
    assert union_pattern.search("hostname> \n")
    assert union_pattern.search("hostname> \r\n")
    assert union_pattern.search("\nhostname> \n")
    assert union_pattern.search("\r\nhostname> \r\n")
    assert union_pattern.search("hostname#")
    assert union_pattern.search("hostname# ")
    assert union_pattern.search("hostname# \n")
    assert union_pattern.search("hostname# \r\n")
    assert union_pattern.search("\nhostname# \n")
    assert union_pattern.search("\r\nhostname# \r\n")
    assert union_pattern.search("hostname(config)#")
    assert union_pattern.search("hostname(config)# ")
    assert union_pattern.search("hostname(config)# \n")
    assert union_pattern.search("hostname(config)# \r\n")
    assert union_pattern.search("\nhostname(config)# \n")
    assert union_pattern.search("\r\nhostname(config)# \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("% Unknown command."),
    ("% Command incomplete.")
])
async def test_error_catch(output: str):
    error_patterns = ChaiTinBase.PatternHelper.get_error_patterns()
    ignore_patterns = ChaiTinBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
