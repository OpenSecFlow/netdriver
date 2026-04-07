#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
import pytest

from netdriver_agent.route import LoggingApiRoute


@pytest.mark.unit
def test_logging_route_allows_empty_get_body() -> None:
    app = FastAPI()
    router = APIRouter(route_class=LoggingApiRoute)

    @router.get("/discovery")
    async def list_discovery_tasks() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(router)

    client = TestClient(app)
    response = client.get("/discovery")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.unit
def test_logging_route_allows_non_json_body() -> None:
    app = FastAPI()
    router = APIRouter(route_class=LoggingApiRoute)

    @router.post("/echo")
    async def echo() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(router)

    client = TestClient(app)
    response = client.post(
        "/echo",
        content="plain text payload",
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
