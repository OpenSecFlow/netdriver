#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver_agent.plugins.h3c import H3CBase
from netdriver_core.utils import regex


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = H3CBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("\r<hostname>")
    assert enable_pattern.search("\r\n<hostname>")
    assert enable_pattern.search("\x00<hostname>")
    assert enable_pattern.search("<hostname> ")
    assert enable_pattern.search("<hostname> \n")
    assert enable_pattern.search("<hostname> \r\n")
    assert enable_pattern.search("RBM_P<hostname>")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = H3CBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("[hostname]")
    assert config_pattern.search("[hostname] ")
    assert config_pattern.search("[hostname] \n")
    assert config_pattern.search("[hostname] \r\n")
    assert config_pattern.search("\n[hostname] \n")
    assert config_pattern.search("\r\n[hostname] \r\n")
    assert config_pattern.search("[hostname-vlan1]")
    assert config_pattern.search("RBM_P[hostname]")
    assert not config_pattern.search("[Y/N]")
    assert not config_pattern.search("[y/n]")

@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = H3CBase.PatternHelper.get_union_pattern()
    assert union_pattern.search("<hostname>")
    assert union_pattern.search("<hostname> ")
    assert union_pattern.search("<hostname> \n")
    assert union_pattern.search("<hostname> \r\n")
    assert union_pattern.search("\n<hostname> \n")
    assert union_pattern.search("\r\n<hostname> \r\n")
    assert union_pattern.search("\x00<hostname>")
    assert union_pattern.search("[hostname]")
    assert union_pattern.search("[hostname] ")
    assert union_pattern.search("[hostname] \n")
    assert union_pattern.search("[hostname] \r\n")
    assert union_pattern.search("\n[hostname] \n")
    assert union_pattern.search("\r\n[hostname] \r\n")
    assert union_pattern.search("[hostname-vlan1]")
    assert union_pattern.search("[hostname-vlan1] ")
    assert union_pattern.search("[hostname-vlan1] \n")
    assert union_pattern.search("[hostname-vlan1] \r\n")
    assert union_pattern.search("\n[hostname-vlan1] \n")
    assert union_pattern.search("\r\n[hostname-vlan1] \r\n")
    assert union_pattern.search("RBM_P<hostname>")
    assert union_pattern.search("RBM_P[hostname]")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("     ^                 \n% Unrecognized command found at '^' position."),
    ("                            ^                          % Wrong parameter found at '^' position."),
    ("The rule does not exist."),
    ("Object group with given name exists with different type.")
])
async def test_error_catch(output: str):
    error_patterns = H3CBase.PatternHelper.get_error_patterns()
    ignore_patterns = H3CBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("The current configuration will be written to the device. Are you sure? [Y/N]:"),
    ("(To leave the existing filename unchanged, press the enter key):"),
    ("flash:/startup.cfg exists, overwrite? [Y/N]:"),
    ("Are you sure you want to continue the save operation? [Y/N]:")
])
async def test_auto_confirm(output: str):
    auto_confirm_patterns = H3CBase.PatternHelper.get_auto_confirm_patterns()
    confirm_cmd = regex.catch_auto_confirm_of_output(output, auto_confirm_patterns)
    assert confirm_cmd != None