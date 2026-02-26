#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_route(test_client: TestClient, maipu_nss_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": maipu_nss_dev.get("protocol"),
        "ip": maipu_nss_dev.get("ip"),
        "port": maipu_nss_dev.get("port"),
        "username": maipu_nss_dev.get("username"),
        "password": maipu_nss_dev.get("password"),
        "enable_password": maipu_nss_dev.get("enable_password"),
        "vendor": "maipu",
        "model": "nss",
        "version": "9.7.40.8",
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
async def test_pull_config(test_client: TestClient, maipu_nss_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": maipu_nss_dev.get("protocol"),
        "ip": maipu_nss_dev.get("ip"),
        "port": maipu_nss_dev.get("port"),
        "username": maipu_nss_dev.get("username"),
        "password": maipu_nss_dev.get("password"),
        "enable_password": maipu_nss_dev.get("enable_password"),
        "vendor": "maipu",
        "model": "nss",
        "version": "9.7.40.8",
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
