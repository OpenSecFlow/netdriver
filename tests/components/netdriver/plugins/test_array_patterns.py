#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.utils import regex
from netdriver.plugins.array import ArrayBase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_pattern():
    login_pattern = ArrayBase.PatternHelper.get_login_prompt_pattern()
    assert login_pattern.search("\rhostname>")
    assert login_pattern.search("\rhostname> ")
    assert login_pattern.search("\rhostname> \n")
    assert login_pattern.search("\rhostname> \r\n")
    assert not login_pattern.search('system mail from "%h<alert@log.domain>')

@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = ArrayBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("hostname#")
    assert enable_pattern.search("hostname# ")
    assert enable_pattern.search("hostname# \n")
    assert enable_pattern.search("hostname# \r\n")
    assert enable_pattern.search("\nhostname# \n")
    assert enable_pattern.search("\r\nhostname# \r\n")
    assert enable_pattern.search("vsite_name$")
    assert enable_pattern.search("vsite_name$ ")
    assert enable_pattern.search("vsite_name$ \n")
    assert enable_pattern.search("vsite_name$ \r\n")
    assert enable_pattern.search("\nvsite_name$ \n")
    assert enable_pattern.search("\r\nvsite_name$ \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = ArrayBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("hostname(config)#")
    assert config_pattern.search("hostname(config)# ")
    assert config_pattern.search("hostname(config)# \n")
    assert config_pattern.search("hostname(config)# \r\n")
    assert config_pattern.search("\nhostname(config)# \n")
    assert config_pattern.search("\r\nhostname(config)# \r\n")
    assert config_pattern.search("vsite_name(config)$")
    assert config_pattern.search("vsite_name(config)$ ")
    assert config_pattern.search("vsite_name(config)$ \n")
    assert config_pattern.search("vsite_name(config)$ \r\n")
    assert config_pattern.search("\nvsite_name(config)$ \n")
    assert config_pattern.search("\r\nvsite_name(config)$ \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = ArrayBase.PatternHelper.get_union_pattern()
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
    assert union_pattern.search("vsite_name$")
    assert union_pattern.search("vsite_name$ ")
    assert union_pattern.search("vsite_name$ \n")
    assert union_pattern.search("vsite_name$ \r\n")
    assert union_pattern.search("\nvsite_name$ \n")
    assert union_pattern.search("\r\nvsite_name$ \r\n")
    assert union_pattern.search("vsite_name(config)$")
    assert union_pattern.search("vsite_name(config)$ ")
    assert union_pattern.search("vsite_name(config)$ \n")
    assert union_pattern.search("vsite_name(config)$ \r\n")
    assert union_pattern.search("\nvsite_name(config)$ \n")
    assert union_pattern.search("\r\nvsite_name(config)$ \r\n")
    assert not union_pattern.search("\n#\n")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_password_pattern():
    epw_pattern = ArrayBase.PatternHelper.get_enable_password_prompt_pattern()
    assert epw_pattern.search("Enable password:")
    assert epw_pattern.search("Enable password: ")
    assert epw_pattern.search("Enable password: \n")
    assert epw_pattern.search("Enable password: \r\n")
    assert epw_pattern.search("\nEnable password: \n")
    assert epw_pattern.search("\r\nEnable password: \r\n")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    # test r"Virtual site .+ is not configured"
    ("\nVirtual site .+ is not configured \n"),
    ("\r\nVirtual site .+ is not configured \r\n"),
    # r"^Cannot find the group name '.+'\.$"
    ("Cannot find the group name 'g-202'."),
    ("\nCannot find the group name 'g-202'.\n"),
    ("\r\nCannot find the group name 'g-202'.\r\n"),
    # r"^No such group map configured: \".+\" to \".+\"\.$"
    ('No such group map configured: "ad" to "g".'),
    ('\nNo such group map configured: "ad" to "g".\n'),
    ('\r\nNo such group map configured: "ad" to "g".\r\n'),
    # r"^Internal group \".+\" not found, please configure the group at localdb\.$"
    ('Internal group "g" not found, please configure the group at localdb.'),
    ('\nInternal group "g" not found, please configure the group at localdb.\n'),
    ('\r\nInternal group "g" not found, please configure the group at localdb.\r\n'),
    # r"Already has a group map for external group \".+\"\."
    ('Already has a group map for external group "AD组-重庆外汇投资运维".'),
    ('\nAlready has a group map for external group "AD组-重庆外汇投资运维".\n'),
    ('\r\nAlready has a group map for external group "AD组-重庆外汇投资运维".\r\n'),
    # r"role \".+\" doesn't exist",
    ("role \"r-K\" doesn't exist"),
    ("\nrole \"r-K\" doesn't exist\n"),
    ("\r\nrole \"r-K\" doesn't exist\r\n"),
    # r"qualification \".+\" doesn't exist",
    ("qualification \"q-2024_09-30\" doesn't exist"),
    ("\nqualification \"q-2024_09-30\" doesn't exist\n"),
    ("\r\nqualification \"q-2024_09-30\" doesn't exist\r\n"),
    # r"the condition \"GROUPNAME IS '.+'\" doesn't exist in qualification \".+\", role \".+\""
    ("the condition \"GROUPNAME IS 'g-2024_09-30'\" doesn't exist in qualification \"q-2024_09-30\", role \"r-2024_09-30\"\n"),
    ("\nthe condition \"GROUPNAME IS 'g-2024_09-30'\" doesn't exist in qualification \"q-2024_09-30\", role \"r-2024_09-30\"\n"),
    ("\r\nthe condition \"GROUPNAME IS 'g-2024_09-30'\" doesn't exist in qualification \"q-2024_09-30\", role \"r-2024_09-30\"\r\n"),
    # r"The resource \".+\" has not been assigned to this role"
    ("The resource \"netpools\" has not been assigned to this role"),
    ("\nThe resource \"netpools\" has not been assigned to this role\n"),
    ("\r\nThe resource \"netpools\" has not been assigned to this role\r\n"),
    # r"Netpool .+ does not exist"
    ("Netpool netpool does not exist"),
    ("\nNetpool netpool does not exist\n"),
    ("\r\nNetpool netpool does not exist\r\n"),
    # r"Resource group .+ does not exist"
    ("Resource group vpn-resources does not exist"),
    ("\nResource group vpn-resources does not exist\n"),
    ("\r\nResource group vpn-resources does not exist\r\n"),
    # r"The resource \".+\" has not been assigned to this role"
    ("The resource \"vpn-resources\" has not been assigned to this role"),
    ("\nThe resource \"vpn-resources\" has not been assigned to this role\n"),
    ("\r\nThe resource \"vpn-resources\" has not been assigned to this role\r\n"),
    # r"Cannot find the resource group '.+'\."
    ("Cannot find the resource group 's-2024_09-30'."),
    ("\nCannot find the resource group 's-2024_09-30'.\n"),
    ("\r\nCannot find the resource group 's-2024_09-30'.\r\n"),
    # r"This resource group name has been used, please give another one\."
    ("This resource group name has been used, please give another one."),
    ("\nThis resource group name has been used, please give another one.\n"),
    ("\r\nThis resource group name has been used, please give another one.\r\n"),
    # r"This resource .+ doesn't exist or hasn't assigned to target .+"
    ("This resource s-2024_09-30 doesn't exist or hasn't assigned to target r-2024_09-30"),
    ("\nThis resource s-2024_09-30 doesn't exist or hasn't assigned to target r-2024_09-30\n"),
    ("\r\nThis resource s-2024_09-30 doesn't exist or hasn't assigned to target r-2024_09-30\r\n"),
    # r"Parse network resource failed: Invalid port format\."
    ("Parse network resource failed: Invalid port format."),
    ("\nParse network resource failed: Invalid port format.\n"),
    ("\r\nParse network resource failed: Invalid port format.\r\n"),
    # r"Parse network resource failed: Invalid ACL format\."
    ("Parse network resource failed: Invalid ACL format."),
    ("\nParse network resource failed: Invalid ACL format.\n"),
    ("\r\nParse network resource failed: Invalid ACL format.\r\n"),
    # r"Parse network resource failed: ICMP protocol resources MUST NOT with port information\."
    ("Parse network resource failed: ICMP protocol resources MUST NOT with port information."),
    ("\nParse network resource failed: ICMP protocol resources MUST NOT with port information.\n"),
    ("\r\nParse network resource failed: ICMP protocol resources MUST NOT with port information.\r\n"),
    # r"Cannot find the resource group '.+'\."
    ("Cannot find the resource group 's-2024_09-30_1'."),
    ("\nCannot find the resource group 's-2024_09-30_1'.\n"),
    ("\r\nCannot find the resource group 's-2024_09-30_1'.\r\n"),
    # r"The resource \".+\" does not exsit under resource group \".+\""
    ("The resource \"12://2.3.3.3:100\" does not exsit under resource group \"s-2024_09-30\""),
    ("\nThe resource \"12://2.3.3.3:100\" does not exsit under resource group \"s-2024_09-30\"\n"),
    ("\r\nThe resource \"12://2.3.3.3:100\" does not exsit under resource group \"s-2024_09-30\"\r\n"),
    # test r"\^$
    ("show date ?\n\n         ^\n"),
    ('localdb group "g-HeFuTouZi-Users"\r\n\rlocaldb group "g-HeFuTouZi-Users" \r\n\r\n^\r\n \r\n\rvpndg$')
])
async def test_error_catch(output: str):
    error_patterns = ArrayBase.PatternHelper.get_error_patterns()
    ignore_patterns = ArrayBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str
