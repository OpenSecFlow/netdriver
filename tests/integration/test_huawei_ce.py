#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_switch_mode(test_client: TestClient, huawei_ce_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_ce_dev.get("protocol"),
        "ip": huawei_ce_dev.get("ip"),
        "port": huawei_ce_dev.get("port"),
        "username": huawei_ce_dev.get("username"),
        "password": huawei_ce_dev.get("password"),
        "enable_password": huawei_ce_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "ce6800",
        "version": "8.18",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "display version",
                "template": ""
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "display version",
                "template": ""
            }
        ],
        "timeout": 10
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, huawei_ce_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_ce_dev.get("protocol"),
        "ip": huawei_ce_dev.get("ip"),
        "port": huawei_ce_dev.get("port"),
        "username": huawei_ce_dev.get("username"),
        "password": huawei_ce_dev.get("password"),
        "enable_password": huawei_ce_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "ce6800",
        "version": "8.18",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "display current-configuration",
                "template": ""
            }
        ],
        "timeout": 10
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    # print(response.json().get('output'))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_and_save(test_client: TestClient, huawei_ce_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_ce_dev.get("protocol"),
        "ip": huawei_ce_dev.get("ip"),
        "port": huawei_ce_dev.get("port"),
        "username": huawei_ce_dev.get("username"),
        "password": huawei_ce_dev.get("password"),
        "enable_password": huawei_ce_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "ce6800",
        "version": "8.18",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "config",
                "command": "sysname huawei_ce"
            },
            {
                "type": "raw",
                "mode": "enable",
                "command": "save"
            }
        ],
        "timeout": 10
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    # print(response.json().get('output'))
