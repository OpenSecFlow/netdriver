#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
import os
import argparse
import asyncio
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from netdriver.log import logman
from netdriver.server.device import MockSSHDevice
from netdriver.simunet.containers import container


logman.configure_logman(level=container.config.logging.level(),
                        intercept_loggers=container.config.logging.intercept_loggers(),
                        log_file=container.config.logging.log_file())
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
        server.stop()


# Register event handlers on simunet_app instance
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def start():
    """Start the simunet server with optional configuration file parameter."""
    parser = argparse.ArgumentParser(description="NetDriver SimuNet Server")
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: config/simunet/simunet.yml or NETDRIVER_SIMUNET_CONFIG env var)"
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
        default=8001,
        help="Port to bind (default: 8001)"
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
        os.environ["NETDRIVER_SIMUNET_CONFIG"] = args.config
        # Reload container configuration with new config file
        container.config.from_yaml(args.config, required=True)
        # Reconfigure logging with new config
        logman.configure_logman(
            level=container.config.logging.level(),
            intercept_loggers=container.config.logging.intercept_loggers(),
            log_file=container.config.logging.log_file()
        )

    # Handle reload flag
    reload = args.reload and not args.no_reload

    uvicorn.run(
        "netdriver.simunet.main:app",
        host=args.host,
        port=args.port,
        reload=reload
    )
