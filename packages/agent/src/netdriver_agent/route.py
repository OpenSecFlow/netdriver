#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time

from typing import Any, Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute

from netdriver_agent.containers import container
from netdriver_core.log import logman


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

    @staticmethod
    def _parse_request_body(body: bytes, content_type: str | None) -> Any | None:
        """Parse request body for logging without breaking empty or non-JSON requests."""
        if not body:
            return None

        normalized_content_type = (content_type or "").split(";", maxsplit=1)[0].strip().lower()
        if normalized_content_type == "application/json" or normalized_content_type.endswith("+json"):
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return body.decode("utf-8", errors="replace")

        return body.decode("utf-8", errors="replace")

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            # before request
            start_time = time.time()
            req_body = self._parse_request_body(
                await request.body(),
                request.headers.get("content-type"),
            )
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
