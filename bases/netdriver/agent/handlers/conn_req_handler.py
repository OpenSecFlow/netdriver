#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pytest import Session
from netdriver.agent.models.common import CommonResponse
from netdriver.agent.models.conn import ConnectRequest
from netdriver.client.pool import SessionPool
from netdriver.exception.errors import ConnectFailed


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
