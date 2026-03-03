#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, check_point_security_gateway_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": check_point_security_gateway_dev.get("protocol"),
        "ip": check_point_security_gateway_dev.get("ip"),
        "port": check_point_security_gateway_dev.get("port"),
        "username": check_point_security_gateway_dev.get("username"),
        "password": check_point_security_gateway_dev.get("password"),
        "enable_password": check_point_security_gateway_dev.get("enable_password"),
        "vendor": "check point",
        "model": "security gateway",
        "version": "R80.40",
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_route(test_client: TestClient, check_point_security_gateway_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": check_point_security_gateway_dev.get("protocol"),
        "ip": check_point_security_gateway_dev.get("ip"),
        "port": check_point_security_gateway_dev.get("port"),
        "username": check_point_security_gateway_dev.get("username"),
        "password": check_point_security_gateway_dev.get("password"),
        "enable_password": check_point_security_gateway_dev.get("enable_password"),
        "vendor": "check point",
        "model": "security gateway",
        "version": "R80.40",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show route",
                "template": ""
            },
            {
                "type": "raw",
                "mode": "enable",
                "command": "show ipv6 route",
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
