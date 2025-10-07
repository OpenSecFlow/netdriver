#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_mode(test_client: TestClient, array_ag_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": array_ag_dev.get("protocol"),
        "ip": array_ag_dev.get("ip"),
        "port": array_ag_dev.get("port"),
        "username": array_ag_dev.get("username"),
        "password": array_ag_dev.get("password"),
        "enable_password": array_ag_dev.get("enable_password"),
        "vendor": "array",
        "model": "ag",
        "version": "xyz",
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
                "command": "hostname array-ag\nwrite memory all",
            },
            {
                "type": "raw",
                "mode": "login",
                "command": "show version",
            }
        ],
        "timeout": 1000
    })
    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_switch_vsys(test_client: TestClient, array_ag_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": array_ag_dev.get("protocol"),
        "ip": array_ag_dev.get("ip"),
        "port": array_ag_dev.get("port"),
        "username": array_ag_dev.get("username"),
        "password": array_ag_dev.get("password"),
        "enable_password": array_ag_dev.get("enable_password"),
        "vendor": "array",
        "model": "ag",
        "version": "xyz",
        "encode": "utf-8",
        "vsys": "vpndg",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show vpn active",
                "template": ""
            },
            {
                "type": "raw",
                "mode": "config",
                "command": "show version",
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

    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": array_ag_dev.get("protocol"),
        "ip": array_ag_dev.get("ip"),
        "port": array_ag_dev.get("port"),
        "username": array_ag_dev.get("username"),
        "password": array_ag_dev.get("password"),
        "enable_password": array_ag_dev.get("enable_password"),
        "vendor": "array",
        "model": "ag",
        "version": "xyz",
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
                "command": "show version",
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, array_ag_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": array_ag_dev.get("protocol"),
        "ip": array_ag_dev.get("ip"),
        "port": array_ag_dev.get("port"),
        "username": array_ag_dev.get("username"),
        "password": array_ag_dev.get("password"),
        "enable_password": array_ag_dev.get("enable_password"),
        "vendor": "array",
        "model": "ag",
        "version": "xyz",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show running all",
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
