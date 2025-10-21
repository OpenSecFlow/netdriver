#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_mode(test_client: TestClient, juniper_ex_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": juniper_ex_dev.get("protocol"),
        "ip": juniper_ex_dev.get("ip"),
        "port": juniper_ex_dev.get("port"),
        "username": juniper_ex_dev.get("username"),
        "password": juniper_ex_dev.get("password"),
        "enable_password": juniper_ex_dev.get("enable_password"),
        "vendor": "juniper",
        "model": "ex4200",
        "version": "junos 15",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show version | no-more"
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "set system host-name juniper-ex",
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
async def test_pull_config(test_client: TestClient, juniper_ex_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": juniper_ex_dev.get("protocol"),
        "ip": juniper_ex_dev.get("ip"),
        "port": juniper_ex_dev.get("port"),
        "username": juniper_ex_dev.get("username"),
        "password": juniper_ex_dev.get("password"),
        "enable_password": juniper_ex_dev.get("enable_password"),
        "vendor": "juniper",
        "model": "ex4200",
        "version": "junos 15",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show configuration | display set | no-more",
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