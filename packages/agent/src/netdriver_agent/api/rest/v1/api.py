#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated
from dependency_injector.wiring import inject, Provide
from fastapi import Depends, Header
from fastapi.routing import APIRouter
from netdriver_agent.containers import Container
from netdriver_agent.handlers.cmd_req_handler import CommandRequestHandler
from netdriver_agent.handlers.conn_req_handler import ConnectRequestHandler
from netdriver_agent.models.cmd import CommandRequest, CommandResponse
from netdriver_agent.models.common import CommonResponse
from netdriver_agent.models.conn import ConnectRequest
from netdriver_agent.models.header import CommonHeaders
from netdriver_agent.route import LoggingApiRoute


router = APIRouter(route_class=LoggingApiRoute)


@router.post("/cmd", summary="Execute command on device")
@inject
async def cmd(
    command: CommandRequest,
    headers: Annotated[CommonHeaders, Header()],
    handler: CommandRequestHandler = Depends(Provide[Container.cmd_req_handler])
) -> CommandResponse:
    """ Execute command on device. """
    return await handler.handle(command)


@router.post("/connect", summary="Check the connection between agent and device")
@inject
async def connect(
    request: ConnectRequest,
    headers: Annotated[CommonHeaders, Header()],
    handler: ConnectRequestHandler = Depends(Provide[Container.conn_req_handler])
) -> CommonResponse:
    """ Check the connection to the device. """
    return await handler.handle(request)
