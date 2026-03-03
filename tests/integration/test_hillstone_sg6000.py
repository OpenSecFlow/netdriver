#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_connect(test_client: TestClient, hillstone_SG6000_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/connect", headers={"x-correlation-id": trace_id}, json={
        "protocol": hillstone_SG6000_dev.get("protocol"),
        "ip": hillstone_SG6000_dev.get("ip"),
        "port": hillstone_SG6000_dev.get("port"),
        "username": hillstone_SG6000_dev.get("username"),
        "password": hillstone_SG6000_dev.get("password"),
        "enable_password": hillstone_SG6000_dev.get("enable_password"),
        "vendor": "hillstone",
        "model": "sg6000",
        "version": "5.5",
        "encode": "utf-8",
        "vsys": "default",
        "timeout": 10
    })
    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert response.json().get("msg") == "Connection is alive"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_mode(test_client: TestClient, hillstone_SG6000_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": hillstone_SG6000_dev.get("protocol"),
        "ip": hillstone_SG6000_dev.get("ip"),
        "port": hillstone_SG6000_dev.get("port"),
        "username": hillstone_SG6000_dev.get("username"),
        "password": hillstone_SG6000_dev.get("password"),
        "enable_password": hillstone_SG6000_dev.get("enable_password"),
        "vendor": "hillstone",
        "model": "sg6000",
        "version": "5.5",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show version"
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "hostname hillstone\nsave",
            },
            {
                "type": "raw",
                "mode": "enable",
                "command": "show version"
            }
        ],
        "timeout": 60
    })
    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 3
    for res in response.json().get("result"):
        assert len(res.get("ret")) > 100


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, hillstone_SG6000_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": hillstone_SG6000_dev.get("protocol"),
        "ip": hillstone_SG6000_dev.get("ip"),
        "port": hillstone_SG6000_dev.get("port"),
        "username": hillstone_SG6000_dev.get("username"),
        "password": hillstone_SG6000_dev.get("password"),
        "enable_password": hillstone_SG6000_dev.get("enable_password"),
        "vendor": "hillstone",
        "model": "sg6000",
        "version": "5.5",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show configuration",
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
    assert len(response.json().get("result")[0].get("ret")) > 100
