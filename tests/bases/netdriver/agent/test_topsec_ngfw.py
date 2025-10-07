#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_route(test_client: TestClient, topsec_ngfw_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": topsec_ngfw_dev.get("protocol"),
        "ip": topsec_ngfw_dev.get("ip"),
        "port": topsec_ngfw_dev.get("port"),
        "username": topsec_ngfw_dev.get("username"),
        "password": topsec_ngfw_dev.get("password"),
        "enable_password": topsec_ngfw_dev.get("enable_password"),
        "vendor": "topsec",
        "model": "ngfw",
        "version": "v3",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "network route show",
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
async def test_pull_config(test_client: TestClient, topsec_ngfw_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": topsec_ngfw_dev.get("protocol"),
        "ip": topsec_ngfw_dev.get("ip"),
        "port": topsec_ngfw_dev.get("port"),
        "username": topsec_ngfw_dev.get("username"),
        "password": topsec_ngfw_dev.get("password"),
        "enable_password": topsec_ngfw_dev.get("enable_password"),
        "vendor": "topsec",
        "model": "ngfw",
        "version": "v3",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show",
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
