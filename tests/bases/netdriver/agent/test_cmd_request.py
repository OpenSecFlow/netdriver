#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from netdriver.exception.error_code import ErrorCode

_base_body = {
    "protocol": "ssh",
    "ip": "172.21.1.170",
    "port": 22,
    "username": "array",
    "password": "admin",
    "enable_password": "",
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
        }
    ],
    "timeout": 10
}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_protocol(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["protocol"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_ip(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["ip"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_port(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["port"] = 65536
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_vendor(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["vendor"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_model(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["model"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_vendor_and_model_combination(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["vendor"] = "cisco"
    _body["model"] = "ag"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_encode(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["encode"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_cmd_type(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["commands"][0]["type"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_cmd_mode(test_client: TestClient):
    trace_id = uuid4().hex
    _body = _base_body.copy()
    _body["commands"][0]["mode"] = "invalid"
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json=_body)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == ErrorCode.CLIENT_PARAM_ERROR
