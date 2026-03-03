#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_switch_mode(test_client: TestClient, huawei_usg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_usg_dev.get("protocol"),
        "ip": huawei_usg_dev.get("ip"),
        "port": huawei_usg_dev.get("port"),
        "username": huawei_usg_dev.get("username"),
        "password": huawei_usg_dev.get("password"),
        "enable_password": huawei_usg_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "usg",
        "version": "xyz",
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_switch_vsys(test_client: TestClient, huawei_usg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_usg_dev.get("protocol"),
        "ip": huawei_usg_dev.get("ip"),
        "port": huawei_usg_dev.get("port"),
        "username": huawei_usg_dev.get("username"),
        "password": huawei_usg_dev.get("password"),
        "enable_password": huawei_usg_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "usg",
        "version": "xyz",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
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
    assert len(response.json().get("result")) == 1

    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_usg_dev.get("protocol"),
        "ip": huawei_usg_dev.get("ip"),
        "port": huawei_usg_dev.get("port"),
        "username": huawei_usg_dev.get("username"),
        "password": huawei_usg_dev.get("password"),
        "enable_password": huawei_usg_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "usg",
        "version": "xyz",
        "encode": "gb18030",
        "vsys": "test",
        "commands": [
            {
                "type": "raw",
                "mode": "config",
                "command": "display current-configuration",
                "template": ""
            }
        ],
        "timeout": 10
    })
    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, huawei_usg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_usg_dev.get("protocol"),
        "ip": huawei_usg_dev.get("ip"),
        "port": huawei_usg_dev.get("port"),
        "username": huawei_usg_dev.get("username"),
        "password": huawei_usg_dev.get("password"),
        "enable_password": huawei_usg_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "usg",
        "version": "xyz",
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
async def test_set_and_save(test_client: TestClient, huawei_usg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": huawei_usg_dev.get("protocol"),
        "ip": huawei_usg_dev.get("ip"),
        "port": huawei_usg_dev.get("port"),
        "username": huawei_usg_dev.get("username"),
        "password": huawei_usg_dev.get("password"),
        "enable_password": huawei_usg_dev.get("enable_password"),
        "vendor": "huawei",
        "model": "usg",
        "version": "xyz",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "config",
                "command": "sysname usg6000v"
            },
            {
                "type": "raw",
                "mode": "enable",
                "command": "save"
            }
        ],
        "timeout": 30
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    # print(response.json().get('output'))
