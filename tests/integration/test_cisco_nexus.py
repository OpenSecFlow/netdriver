#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_connect(test_client: TestClient, cisco_nexus_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/connect", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_nexus_dev.get("protocol"),
        "ip": cisco_nexus_dev.get("ip"),
        "port": cisco_nexus_dev.get("port"),
        "username": cisco_nexus_dev.get("username"),
        "password": cisco_nexus_dev.get("password"),
        "enable_password": cisco_nexus_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "nexus",
        "version": "9.8",
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
async def test_switch_mode(test_client: TestClient, cisco_nexus_dev: dict):
    trace_id = uuid4().hex
    request_json = {
        "protocol": cisco_nexus_dev.get("protocol"),
        "ip": cisco_nexus_dev.get("ip"),
        "port": cisco_nexus_dev.get("port"),
        "username": cisco_nexus_dev.get("username"),
        "password": cisco_nexus_dev.get("password"),
        "enable_password": cisco_nexus_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "nexus",
        "version": "9.8",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show version",
                "template": ""
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "hostname nxos\ncopy running-config startup-config",
                "template": ""
            },
            {
                "type": "raw",
                "mode": "enable",
                "command": "show version",
                "template": ""
            }
        ],
        "timeout": 10
    }

    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id},
                                    json=request_json)
    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 3
    for res in response.json().get("result"):
        assert len(res.get("ret")) > 100
