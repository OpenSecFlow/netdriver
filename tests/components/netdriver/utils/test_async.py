#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import pytest

from netdriver.utils.asyncu import AsyncTimeoutError, async_timeout


# 使用示例
class APIClient:
    def __init__(self):
        self.default_timeout = 10.0
        self._fetch_data_timeout = 5.0  # 为特定方法设置超时
    
    @async_timeout()
    async def fetch_data(self, url: str):
        await asyncio.sleep(3)
        return f"数据来自 {url}"
    
    @async_timeout(timeout=2.0)
    async def quick_check(self):
        await asyncio.sleep(3)
        return "检查完成"

@pytest.mark.skip
@pytest.mark.asyncio
async def test_correct():
    client = APIClient()
    print(await client.fetch_data("http://api.example.com"))
    print(await client.fetch_data("http://api.example.com", timeout=8.0))


@pytest.mark.skip
@pytest.mark.asyncio
async def test_timeout():
    client = APIClient()
    with pytest.raises(AsyncTimeoutError) as exc_info:
        await client.quick_check()