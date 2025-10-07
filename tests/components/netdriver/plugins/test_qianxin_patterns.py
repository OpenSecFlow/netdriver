#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.qianxin import QiAnXinBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = QiAnXinBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("hostname>")
    assert enable_pattern.search("hostname> ")
    assert enable_pattern.search("hostname> \n")
    assert enable_pattern.search("hostname> \r\n")
    assert enable_pattern.search("\nhostname> \n")
    assert enable_pattern.search("\r\nhostname> \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = QiAnXinBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("hostname-config]")
    assert config_pattern.search("hostname-config] ")
    assert config_pattern.search("hostname-config] \n")
    assert config_pattern.search("hostname-config] \r\n")
    assert config_pattern.search("\nhostname-config] \n")
    assert config_pattern.search("\r\nhostname-config] \r\n")
    assert config_pattern.search("hostname-config-network-test]")
    assert config_pattern.search("hostname-config-object-service-test] ")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = QiAnXinBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("hostname>")
    assert union_pattern.search("hostname> ")
    assert union_pattern.search("hostname> \n")
    assert union_pattern.search("hostname> \r\n")
    assert union_pattern.search("\nhostname> \n")
    assert union_pattern.search("\r\nhostname> \r\n")
    assert union_pattern.search("hostname-config]")
    assert union_pattern.search("hostname-config] ")
    assert union_pattern.search("hostname-config] \n")
    assert union_pattern.search("hostname-config] \r\n")
    assert union_pattern.search("\nhostname-config] \n")
    assert union_pattern.search("\r\nhostname-config] \r\n")
    assert union_pattern.search("hostname-config-network-test]")
    assert union_pattern.search("hostname-config-object-service-test] ")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("% Unknown command."),
    ("                    ^\n% Invalid parameter detected at '^' marker."),
    ("% Command incomplete."),
    ("		Object address name not exist"),
    ("		Valid name can only support alpha, digit, chinese and \"_-.@\", and the name must start with a letter, number or Chinese"),
    ("		Object address not exist"),
    ('		Object address group name not exist'),
    ("		Object address and address group name exist"),
    ("		Object address referenced by other module"),
    ("		Object address group referenced by other module"),
    ("		Object service name not exist"),
    ("		Invalid parameters"),
    ("		Object service group name not exist"),
    ('		Repetitions with Object custom service'),
    ("		Object service has been referenced"),
    ('		Schedule [xxx] not exist'),
    ('		Start larger than end'),
    ('		Name can not repeat'),
    ('		Object [time_5] is quoted'),
    ("		Rule [111] not exist"),
    ('		Source zone [xxx] not exist'),
    ('		Destination zone [yyy] not exist'),
    ('		Schedule not exist')
])
async def test_error_catch(output: str):
    error_patterns = QiAnXinBase.PatternHelper.get_error_patterns()
    ignore_patterns = QiAnXinBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
