#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pull_config(test_client: TestClient, fortinet_fortigate_dev: dict):
    trace_id = uuid4().hex
    response = test_client.post("/api/v1/cmd", headers={"x-correlation-id": trace_id}, json={
        "protocol": fortinet_fortigate_dev.get("protocol"),
        "ip": fortinet_fortigate_dev.get("ip"),
        "port": fortinet_fortigate_dev.get("port"),
        "username": fortinet_fortigate_dev.get("username"),
        "password": fortinet_fortigate_dev.get("password"),
        "enable_password": fortinet_fortigate_dev.get("enable_password"),
        "vendor": "fortinet",
        "model": "fortigate",
        "version": "7.2",
        "encode": "utf-8",
        "vsys": "default",
        "commands": [
            {
                "type": "raw",
                "mode": "enable",
                "command": "show full-configuration",
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
