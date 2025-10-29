#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the main module for the agent.
It is responsible for starting the FastAPI server.
"""
import os
import sys
import argparse
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from netdriver.agent.api import rest
from netdriver.agent.containers import container
from netdriver.agent.handlers.error_handlers import global_exception_handlers
from netdriver.client.pool import SessionPool
from netdriver.plugin.engine import PluginEngine
from netdriver.log import logman


logman.configure_logman(level=container.config.logging.level(),
                        intercept_loggers=container.config.logging.intercept_loggers(),
                        log_file=container.config.logging.log_file())
log = logman.logger
container.wire(modules=[
    rest.v1.api,
])


async def on_startup() -> None:
    """ put all post up logic here """
    log.info("Post-startup of NetDriver Agent")
    # load plugins
    PluginEngine()
    # load session manager
    SessionPool(config=container.config)


async def on_shutdown() -> None:
    """ put all clean logic here """
    log.info("Pre-shutdown of NetDriver Agent")
    await SessionPool().close_all()


@asynccontextmanager
async def lifespan(api: FastAPI):
    await on_startup()
    yield
    await on_shutdown()


app: FastAPI = FastAPI(
    title='NetworkDriver Agent',
    lifespan=lifespan,
    container=container,
    exception_handlers=global_exception_handlers
)
app.add_middleware(CorrelationIdMiddleware, header_name="X-Correlation-Id", validator=None)
app.include_router(rest.router)


@app.get("/")
async def root() -> dict:
    """ root endpoint """
    return {
        "message": "Welcome to the NetDriver Agent",
    }


def start():
    """Start the agent server with optional configuration file parameter."""
    parser = argparse.ArgumentParser(description="NetDriver Agent Server")
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: config/agent/agent.yml or NETDRIVER_AGENT_CONFIG env var)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Port to bind (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="Enable auto-reload (default: True)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload"
    )

    args = parser.parse_args()

    # Set config file path via environment variable if specified
    if args.config:
        os.environ["NETDRIVER_AGENT_CONFIG"] = args.config
        # Reload container configuration with new config file
        container.config.from_yaml(args.config)
        # Reconfigure logging with new config
        logman.configure_logman(
            level=container.config.logging.level(),
            intercept_loggers=container.config.logging.intercept_loggers(),
            log_file=container.config.logging.log_file()
        )

    # Handle reload flag
    reload = args.reload and not args.no_reload

    uvicorn.run(
        "netdriver.agent.main:app",
        host=args.host,
        port=args.port,
        reload=reload
    )
