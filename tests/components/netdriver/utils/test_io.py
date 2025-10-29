#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from netdriver.utils.terminal import simulate_output

@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output, expected", [
    ("array-ag>enable\r\n\rEnable password:\r\n\r\n\rarray-ag#switch vpndg\r\n\r\r\n\rvpndg$configure terminal\r\n\r\r\n\rvpndg(config)$aaa map group \"                                                               \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_T                                                            \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Ta                                                         \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Tai                                                      \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taij                                                   \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taiji                                                \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taijiu_                                            \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taijiu_V                                         \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taijiu_VP                                   \r                                                                                \rvpndg(config)$aaa map group \"Hangzhou_Oak_Taijiu_VPN\" \"g-HZXMZC-TaiJiu\"\b\b\b\b\r\n\rAlready has a group map for external group \"Hangzhou_Oak_Taijiu_VPN\". \r\n\rvpndg(config)$",
     "array-ag>enable\nEnable password:\n\narray-ag#switch vpndg\n\nvpndg$configure terminal\n\nvpndg(config)$aaa map group \"Hangzhou_Oak_Taijiu_VPN\" \"g-HZXMZC-TaiJiu\"\b\b\b\b\nAlready has a group map for external group \"Hangzhou_Oak_Taijiu_VPN\". \nvpndg(config)$"),
])
async def test_compress_output(output: str, expected: str):
    compressed_output = simulate_output(output)
    assert compressed_output == expected
