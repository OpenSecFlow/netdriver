#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_mode(test_client: TestClient, h3c_secpath_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": h3c_secpath_dev.get("protocol"),
        "ip": h3c_secpath_dev.get("ip"),
        "port": h3c_secpath_dev.get("port"),
        "username": h3c_secpath_dev.get("username"),
        "password": h3c_secpath_dev.get("password"),
        "enable_password": h3c_secpath_dev.get("enable_password"),
        "vendor": "h3c",
        "model": "secpath",
        "version": "7.1",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "display version"
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "hostname H3C",
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
async def test_pull_config(test_client: TestClient, h3c_secpath_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": h3c_secpath_dev.get("protocol"),
        "ip": h3c_secpath_dev.get("ip"),
        "port": h3c_secpath_dev.get("port"),
        "username": h3c_secpath_dev.get("username"),
        "password": h3c_secpath_dev.get("password"),
        "enable_password": h3c_secpath_dev.get("enable_password"),
        "vendor": "h3c",
        "model": "secpath",
        "version": "7.1",
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
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 1

@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_and_save(test_client: TestClient, h3c_secpath_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": h3c_secpath_dev.get("protocol"),
        "ip": h3c_secpath_dev.get("ip"),
        "port": h3c_secpath_dev.get("port"),
        "username": h3c_secpath_dev.get("username"),
        "password": h3c_secpath_dev.get("password"),
        "enable_password": h3c_secpath_dev.get("enable_password"),
        "vendor": "h3c",
        "model": "secpath",
        "version": "7.1",
        "encode": "gb18030",
        "vsys": "default",
        "commands": [
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