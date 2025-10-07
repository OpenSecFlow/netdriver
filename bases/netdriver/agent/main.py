#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the main module for the agent.
It is responsible for starting the FastAPI server.
"""
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
                        intercept_loggers=container.config.logging.intercept_loggers())
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
    uvicorn.run("netdriver.agent.main:app", host="0.0.0.0", port=8000, reload=True)
