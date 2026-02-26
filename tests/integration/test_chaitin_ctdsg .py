#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_route(test_client: TestClient, chaitin_ctdsg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": chaitin_ctdsg_dev.get("protocol"),
        "ip": chaitin_ctdsg_dev.get("ip"),
        "port": chaitin_ctdsg_dev.get("port"),
        "username": chaitin_ctdsg_dev.get("username"),
        "password": chaitin_ctdsg_dev.get("password"),
        "enable_password": chaitin_ctdsg_dev.get("enable_password"),
        "vendor": "chaitin",
        "model": "ctdsg",
        "version": "v3.0",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show ip route",
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
async def test_pull_config(test_client: TestClient, chaitin_ctdsg_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": chaitin_ctdsg_dev.get("protocol"),
        "ip": chaitin_ctdsg_dev.get("ip"),
        "port": chaitin_ctdsg_dev.get("port"),
        "username": chaitin_ctdsg_dev.get("username"),
        "password": chaitin_ctdsg_dev.get("password"),
        "enable_password": chaitin_ctdsg_dev.get("enable_password"),
        "vendor": "chaitin",
        "model": "ctdsg",
        "version": "v3.0",
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
