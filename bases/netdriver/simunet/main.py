#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
import asyncio
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from netdriver.log import logman
from netdriver.server.device import MockSSHDevice
from netdriver.simunet.containers import container


log = logman.logger
app = FastAPI()


async def start_servers(config: dict) -> AsyncGenerator[MockSSHDevice, None]:
    # Start all SSH services
    for dev in config["devices"]:
        host = dev.get("host", None)
        port = dev["port"]
        vendor = dev["vendor"]
        model = dev["model"]
        version = dev["version"]
        log.info(f"Starting SSH server {vendor}-{model}-{version} on \
                 {host if host else '0.0.0.0'}:{port}...")
        yield MockSSHDevice.create_device(vendor=vendor, model=model, version=version, host=host,
                                          port=port)


async def on_startup() -> None:
    """ put all post up logic here """
    log.info("Starting up the application...")
    app.state.servers = []
    async for server in start_servers(container.config()):
        app.state.servers.append(server)
        asyncio.create_task(server.start())


async def on_shutdown() -> None:
    """ put all clean logic here """
    log.info("Shutting down the application...")
    for server in app.state.servers:
        await server.stop()


# Register event handlers on simunet_app instance
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def start():
    uvicorn.run("netdriver.simunet.main:app", host="0.0.0.0", port=8001, reload=True)
