#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from netdriver_agent.models.common import CommonResponse
from netdriver_agent.models.conn import ConnectRequest
from netdriver_agent.client.pool import SessionPool
from netdriver_agent.client.session import Session
from netdriver_core.exception.errors import ConnectFailed


class ConnectRequestHandler:

    async def handle(self, request: ConnectRequest) -> CommonResponse:
        """ Handle connect request """
        if not request:
            raise ValueError("ConnectRequest is empty")

        session: Session = await SessionPool().get_session(**vars(request))
        is_alive: bool = await session.is_alive()
        if is_alive:
            return CommonResponse.ok(msg="Connection is alive")
        else:
            raise ConnectFailed
