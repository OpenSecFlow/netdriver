#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time

from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute

from netdriver.agent.containers import container
from netdriver.log import logman


class LoggingApiRoute(APIRoute):
    """ Custom APIRouter that logs all incoming requests. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_level = container.config.api.request_log_level()
        # only record cmd
        if container.config.record.enable():
            protocol = container.config.record.protocol()
            host = container.config.record.host()
            port = container.config.record.port()
            uri = container.config.record.uri()
            self.record_url = f"{protocol}://{host}:{port}/{uri}"
            self.intercept_urls = container.config.record.intercept_urls()
        else:
            self.record_url = None
        self._logger = logman.logger

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            # before request
            start_time = time.time()
            req_body = json.loads(await request.body())
            if self.log_level and self.log_level.upper() == "DEBUG":
                payload = {
                    "headers": dict(request.headers),
                    "body": req_body,
                }
                self._logger.bind(payload=payload).info(
                    f"=== Start Request {request.method} | {request.url} ===")
            else:
                self._logger.info(f"=== Start Request {request.method} | {request.url} ===")

            # handle request
            response = await original_route_handler(request)

            # after request
            duration = time.time() - start_time
            response.headers["X-Response-Time"] = str(duration)
            self._logger.info(
                f"=== End Request {request.method} | {request.url} | {response.status_code} | {duration:.3f}s ===")

            return response

        return logging_route_handler
