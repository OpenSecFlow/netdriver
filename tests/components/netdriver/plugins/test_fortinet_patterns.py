#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.plugins.fortinet import FortinetBase
from netdriver.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = FortinetBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("hostname #")
    assert enable_pattern.search("hostname # ")
    assert enable_pattern.search("hostname # \n")
    assert enable_pattern.search("hostname # \r\n")
    assert enable_pattern.search("\nhostname # \n")
    assert enable_pattern.search("\r\nhostname # \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_vsys_pattern():
    config_pattern = FortinetBase.PatternHelper.get_vsys_pattern()
    assert config_pattern.search("hostname (root) #")
    assert config_pattern.search("hostname (root) # ")
    assert config_pattern.search("hostname (root) # \n")
    assert config_pattern.search("hostname (root) # \r\n")
    assert config_pattern.search("\nhostname (root) # \n")
    assert config_pattern.search("\r\nhostname (root) # \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = FortinetBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("hostname #")
    assert union_pattern.search("hostname # ")
    assert union_pattern.search("hostname # \n")
    assert union_pattern.search("hostname # \r\n")
    assert union_pattern.search("\nhostname # \n")
    assert union_pattern.search("\r\nhostname # \r\n")
    assert union_pattern.search("hostname (root) #")
    assert union_pattern.search("hostname (root) # ")
    assert union_pattern.search("hostname (root) # \n")
    assert union_pattern.search("hostname (root) # \r\n")
    assert union_pattern.search("\nhostname (root) # \n")
    assert union_pattern.search("\r\nhostname (root) # \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("Unknown action 0"),
    ("command parse error before 'xjj'\nCommand fail. Return code 1"),
    ("incomplete command in the end\nCommand fail. Return code -160"),
    ("end-ip must be greater than start-ip\nobject check operator error, -45, discard the setting\nCommand fail. Return code 1"),
    ("invalid ip address\n\nvalue parse error before '1.1'\nCommand fail. Return code -8"),
    ("string value is too long. the size is 734, the limit is 255\nvalue parse error before 'sssssssssssssssssssssssssssssssssssss\nCommand fail. Return code -1"),
    ("domain name is not valid.\nnode_check_object fail! for fqdn sksjdissssssssssssssssssssss\n\nvalue parse error before 'sksjdissssssssssssssssssssssssssssss\nCommand fail. Return code -651"),
    ("entry not found in datasource\n\nvalue parse error before '201.1.1.1'\nCommand fail. Return code -3"),
    ("Name '13.1.1.1' conflict: 'address' and 'address group' cannot be the same name.\nnode_check_object fail! for name 13.1.1.1\n\nvalue parse error before '13.1.1.1'\nCommand fail. Return code -163"),
    ("TCP/UDP/SCTP portrange cannot all be empty.\nobject check operator error, -651, discard the setting\nCommand fail. Return code 1"),
    ("command parse error before 'tcp'\nCommand fail. Return code -61"),
    ("node_check_object fail! for tcp-portrange 100-10\nvalue parse error before '100-10'\nCommand fail. Return code -650"),
    ("node_check_object fail! for icmptype -1\n\nvalue parse error before '-1'Command fail. Return code -651"),
    ("The entry is used by other 1 entries\nCommand fail. Return code -23")
])
async def test_error_catch(output: str):
    error_patterns = FortinetBase.PatternHelper.get_error_patterns()
    ignore_patterns = FortinetBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str