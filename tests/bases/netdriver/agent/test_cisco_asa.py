#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_connect(test_client: TestClient, cisco_asa_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/connect", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_asa_dev.get("protocol"),
        "ip": cisco_asa_dev.get("ip"),
        "port": cisco_asa_dev.get("port"),
        "username": cisco_asa_dev.get("username"),
        "password": cisco_asa_dev.get("password"),
        "enable_password": cisco_asa_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "asa",
        "version": "xyz",
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
async def test_switch_mode(test_client: TestClient, cisco_asa_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_asa_dev.get("protocol"),
        "ip": cisco_asa_dev.get("ip"),
        "port": cisco_asa_dev.get("port"),
        "username": cisco_asa_dev.get("username"),
        "password": cisco_asa_dev.get("password"),
        "enable_password": cisco_asa_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "asa",
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
                "command": "hostname cisco-asa\nwrite memory",
            },
            {
                "type": "raw",
                "mode": "login",
                "command": "show version",
            }
        ],
        "timeout": 10
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
async def test_pull_config(test_client: TestClient, cisco_asa_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_asa_dev.get("protocol"),
        "ip": cisco_asa_dev.get("ip"),
        "port": cisco_asa_dev.get("port"),
        "username": cisco_asa_dev.get("username"),
        "password": cisco_asa_dev.get("password"),
        "enable_password": cisco_asa_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "asa",
        "version": "xyz",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show running-config\nshow access-list"
            },
        ],
        "timeout": 10
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 1
    assert len(response.json().get("output")) > 100


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_route(test_client: TestClient, cisco_asa_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_asa_dev.get("protocol"),
        "ip": cisco_asa_dev.get("ip"),
        "port": cisco_asa_dev.get("port"),
        "username": cisco_asa_dev.get("username"),
        "password": cisco_asa_dev.get("password"),
        "enable_password": cisco_asa_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "asa",
        "version": "xyz",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show route"
            },
        ],
        "timeout": 10
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")
    assert len(response.json().get("result")) == 1
    assert len(response.json().get("output")) > 100


@pytest.mark.skip(reason="Update config need repo")
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_running_config(test_client: TestClient, cisco_asa_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/update", headers={"x-correlation-id": trace_id}, json={
        "protocol": cisco_asa_dev.get("protocol"),
        "ip": cisco_asa_dev.get("ip"),
        "port": cisco_asa_dev.get("port"),
        "username": cisco_asa_dev.get("username"),
        "password": cisco_asa_dev.get("password"),
        "enable_password": cisco_asa_dev.get("enable_password"),
        "vendor": "cisco",
        "model": "asa",
        "version": "xyz",
        "encode": "utf-8",
        "vsys": "default",
        "type": "running",
        "device": "ae38eda4-3fbf-4fc7-a8eb-b2f23db45d39",
        "checksum": "",
        "timeout": 60
    })

    assert response.status_code == 200
    assert response.json().get("code") == "OK"
    assert response.headers.get("x-correlation-id") == trace_id
    assert not response.json().get("err_msg")