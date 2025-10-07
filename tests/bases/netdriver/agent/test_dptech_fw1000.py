#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_mode(test_client: TestClient, dptech_fw_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": dptech_fw_dev.get("protocol"),
        "ip": dptech_fw_dev.get("ip"),
        "port": dptech_fw_dev.get("port"),
        "username": dptech_fw_dev.get("username"),
        "password": dptech_fw_dev.get("password"),
        "enable_password": dptech_fw_dev.get("enable_password"),
        "vendor": "dptech",
        "model": "fw1000",
        "version": "S511C013D001",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show running-config"
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "show address-object *",
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
async def test_pull_config(test_client: TestClient, dptech_fw_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": dptech_fw_dev.get("protocol"),
        "ip": dptech_fw_dev.get("ip"),
        "port": dptech_fw_dev.get("port"),
        "username": dptech_fw_dev.get("username"),
        "password": dptech_fw_dev.get("password"),
        "enable_password": dptech_fw_dev.get("enable_password"),
        "vendor": "dptech",
        "model": "fw1000",
        "version": "S511C013D001",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show running-config",
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