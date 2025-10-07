#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from netdriver.utils.terminal import simulate_output

@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("output, expected", [
    ("array-ag>enable\r\n\rEnable password:\r\n\r\n\rarray-ag#switch vpndg\r\n\r\r\n\rvpndg$configure terminal\r\n\r\r\n\rvpndg(config)$aaa map group \"                                                               \r                                                                                \rvpndg(config)$aaa map group \"杭                                                            \r                                                                                \rvpndg(config)$aaa map group \"杭州                                                         \r                                                                                \rvpndg(config)$aaa map group \"杭州橡                                                      \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木                                                   \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木资                                                \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木资产_                                            \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木资产_泰                                         \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木资产_泰九VPN                                   \r                                                                                \rvpndg(config)$aaa map group \"杭州橡木资产_泰九VPN组\" \"g-HZXMZC-TaiJiu\"\b\b\b\b\r\n\rAlready has a group map for external group \"杭州橡木资产_泰九VPN组\". \r\n\rvpndg(config)$",
     "array-ag>enable\nEnable password:\n\narray-ag#switch vpndg\n\nvpndg$configure terminal\n\nvpndg(config)$aaa map group \"杭州橡木资产_泰九VPN组\" \"g-HZXMZC-TaiJiu\"\b\b\b\b\nAlready has a group map for external group \"杭州橡木资产_泰九VPN组\". \nvpndg(config)$"),
])
async def test_compress_output(output: str, expected: str):
    compressed_output = simulate_output(output)
    assert compressed_output == expected
