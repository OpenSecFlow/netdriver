#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discovery API endpoints."""

from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.routing import APIRouter

from netdriver_agent.containers import Container
from netdriver_agent.handlers.discovery_handler import DiscoveryRequestHandler
from netdriver_agent.models.common import CommonResponse
from netdriver_agent.models.discovery import (
    DiscoveryRequest,
    DiscoveryResponse,
    DiscoveryStatusResponse,
    DiscoveryTaskSummary,
)
from netdriver_agent.route import LoggingApiRoute


router = APIRouter(prefix="/discovery", route_class=LoggingApiRoute, tags=["discovery"])


@router.post("", summary="Start a discovery task")
@inject
async def start_discovery(
    request: DiscoveryRequest,
    handler: DiscoveryRequestHandler = Depends(Provide[Container.discovery_handler]),
) -> DiscoveryResponse:
    """Start a network device auto-discovery task."""
    return await handler.start_discovery(request)


@router.get("", summary="List all discovery tasks")
@inject
async def list_tasks(
    handler: DiscoveryRequestHandler = Depends(Provide[Container.discovery_handler]),
) -> list[DiscoveryTaskSummary]:
    """List all discovery tasks."""
    return await handler.list_tasks()


@router.get("/{task_id}", summary="Get discovery task status")
@inject
async def get_task_status(
    task_id: str,
    handler: DiscoveryRequestHandler = Depends(Provide[Container.discovery_handler]),
) -> DiscoveryStatusResponse:
    """Get discovery task status and results."""
    return await handler.get_task_status(task_id)


@router.delete("/{task_id}", summary="Cancel a discovery task")
@inject
async def cancel_task(
    task_id: str,
    handler: DiscoveryRequestHandler = Depends(Provide[Container.discovery_handler]),
) -> CommonResponse:
    """Cancel a running discovery task."""
    await handler.cancel_task(task_id)
    return CommonResponse.ok(msg=f"Task {task_id} cancelled")
