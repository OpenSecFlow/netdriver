#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest

from netdriver.utils import regex
from netdriver.plugins.huawei import HuaweiBase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enable_pattern():
    enable_pattern = HuaweiBase.PatternHelper.get_enable_prompt_pattern()
    assert enable_pattern.search("<USG6000v>")
    assert enable_pattern.search("<USG6000v>\n")
    assert enable_pattern.search("<USG6000v>\r\n")
    assert enable_pattern.search("<USG6000v> ")
    assert enable_pattern.search("<USG6000v> \n")
    assert enable_pattern.search("<USG6000v> \r\n")

    assert enable_pattern.search("\r<USG6000v>")
    assert enable_pattern.search("\n<USG6000v>")

    assert enable_pattern.search("<USG6000v-vsys>")
    assert enable_pattern.search("<USG6000v-vsys-policy-security>")
    assert enable_pattern.search("HRP_M<USG6000v>")
    assert enable_pattern.search("HRP_S<USG6000v>")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_config_pattern():
    config_pattern = HuaweiBase.PatternHelper.get_config_prompt_pattern()
    assert config_pattern.search("[USG6000v]")
    assert config_pattern.search("[USG6000v]\n")
    assert config_pattern.search("[USG6000v]\r\n")
    assert config_pattern.search("[USG6000v] ")
    assert config_pattern.search("[USG6000v] \n")
    assert config_pattern.search("[USG6000v] \r\n")

    assert config_pattern.search("\r[USG6000v]")
    assert config_pattern.search("\n[USG6000v]")

    assert config_pattern.search("[USG6000v-vsys]")
    assert config_pattern.search("[USG6000v-vsys-policy-security]")
    assert config_pattern.search("HRP_M[USG6000v]")
    assert config_pattern.search("HRP_S[USG6000v]")
    assert config_pattern.search("HRP_S[USG6000V2-object-address-set-test obj]")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_union_pattern():
    union_pattern = HuaweiBase.PatternHelper.get_union_pattern()

    assert union_pattern.search("<USG6000v>")
    assert union_pattern.search("<USG6000v>\n")
    assert union_pattern.search("<USG6000v>\r\n")
    assert union_pattern.search("<USG6000v> ")
    assert union_pattern.search("<USG6000v> \n")
    assert union_pattern.search("<USG6000v> \r\n")
    assert union_pattern.search("\r<USG6000v>")
    assert union_pattern.search("\n<USG6000v>")
    assert union_pattern.search("<USG6000v-vsys>")
    assert union_pattern.search("<USG6000v-vsys-policy-security>")
    assert union_pattern.search("HRP_M<USG6000v>")
    assert union_pattern.search("HRP_S<USG6000v>")

    assert union_pattern.search("[USG6000v]")
    assert union_pattern.search("[USG6000v]\n")
    assert union_pattern.search("[USG6000v]\r\n")
    assert union_pattern.search("[USG6000v] ")
    assert union_pattern.search("[USG6000v] \n")
    assert union_pattern.search("[USG6000v] \r\n")
    assert union_pattern.search("\r[USG6000v]")
    assert union_pattern.search("\n[USG6000v]")
    assert union_pattern.search("[USG6000v-vsys]")
    assert union_pattern.search("[USG6000v-vsys-policy-security]")
    assert union_pattern.search("HRP_M[USG6000v]")
    assert union_pattern.search("HRP_S[USG6000v]")
    assert union_pattern.search("HRP_S[USG6000V2-object-address-set-test obj]")


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    # r"Error: .+$",
    ("HRP_S<USG6000V2>s\ns\n                ^\nError:Ambiguous command found at '^' position."),
    ("switch vsys vsys1\n Error: The specified virtual system does not exist.\nHRP_S[hw-usg-h-o-s-t-n-m-e]"),
    (" Error: The description length can not exceed 127."),
    ("HRP_S[USG6000V2]ip address-set test2\nip address-set test2 (+B)\n Error: The address or address set is not created(Please specify type when create it)!"),
    ("HRP_S[USG6000V2-group-address-set-test]address range 10.1.1.10 10.1.1.9\naddress range 10.1.1.10 10.1.1.9 (+B)\n Error: Illegal address range!\nHRP_S[USG6000V2-group-address-set-test]"),
    ("HRP_S[USG6000V2-group-address-set-test]address address-set 1\naddress address-set 1 (+B)\n Error: Specify address or address set does not existed yet!\nHRP_S[USG6000V2-group-address-set-test]"),
    # r"\^$",
    ("invalid_cmd\n                ^\nError:Ambiguous command found at '^' position.")
])
async def test_error_catch(output: str):
    error_patterns = HuaweiBase.PatternHelper.get_error_patterns()
    ignore_patterns = HuaweiBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert error_str


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output", [
    ("HRP_S[USG6000V2-group-address-set-test]address 1.1.1.1 mask 32\naddress 1.1.1.1 mask 32 (+B)\n Error: Address item conflicts!"),
    ("HRP_S[USG6000V2-group-address-set-test]undo address 3\nundo address 3 (+B)\n Error: The address item does not exist!\nHRP_S[USG6000V2-group-address-set-test]"),
    ("HRP_S[USG6000V2-domain-set-test]undo add domain byntra\nundo add domain byntra (+B)\n Error: The delete configuration does not exist.\nHRP_S[USG6000V2-domain-set-test]"),
    ("HRP_S[USG6000V2]undo ip address-set 123\nundo ip address-set 123 (+B)\n Error: The address or address set is not created!\nHRP_S[USG6000V2]"),
    ("HRP_S[USG6000V2-group-service-set-svc_test]service service-set ssh\nservice service-set ssh (+B)\n Error: Cannot add! Service item conflicts or illegal reference!\nHRP_S[USG6000V2-group-service-set-svc_test]"),
    ("HRP_S[USG6000V2-group-service-set-svc_test]undo service 3\nundo service 3 (+B)\n Error: The service item does not exist!\nHRP_S[USG6000V2-group-service-set-svc_test]"),
    ("HRP_S[USG6000V2-object-service-set-test_1]service protocol 85\nservice protocol 85 (+B)\n Error: Service item conflicts!\nHRP_S[USG6000V2-object-service-set-test_1]"),
    ("HRP_S[USG6000V2-object-service-set-test_1]undo service 7\nundo service 7 (+B)\n Error: The service item does not exist!\nHRP_S[USG6000V2-object-service-set-test_1]"),
    ("HRP_S[USG6000V2]undo ip service-set xyz\nundo ip service-set xyz (+B)\n Error: The service set is not created(Please specify service set type when creat it)!\nHRP_S[USG6000V2]"),
    ("HRP_S[USG6000V2]undo time-range 123\nundo time-range 123 (+B)\n Error: No such a time-range.\nHRP_S[USG6000V2]"),
    ("HRP_S[USG6000V2]undo nat address-group test\nundo nat address-group test (+B)\n Error: The specified address-group does not exist."),
    ("HRP_S[USG6000V2-policy-nat]undo rule name 123\nundo rule name 123 (+B)\n Error: The specified rule does not exist yet."),
    ("This condition has already been configured"),
])
async def test_error_ignore(output: str):
    error_patterns = HuaweiBase.PatternHelper.get_error_patterns()
    ignore_patterns = HuaweiBase.PatternHelper.get_ignore_error_patterns()
    error_str = regex.catch_error_of_output(output, error_patterns, ignore_patterns)
    assert not error_str
