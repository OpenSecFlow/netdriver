#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
import os
import multiprocessing
import argparse
import asyncio
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from netdriver_core.log import logman
from netdriver_simunet.server.device import MockSSHDevice
from netdriver_simunet.containers import container


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
    """
    Start the application, allocate device port ranges based on WORKER_ID and NUM_WORKERS environment variables
    Support multi-worker mode to avoid port conflicts
    """
    log.info("Starting up the application...")
    
    # Get worker configuration from environment variables
    worker_id = int(os.getenv("WORKER_ID", "0"))
    num_workers = int(os.getenv("NUM_WORKERS", "1"))
    
    # Get all device configurations
    all_devices = container.config()["devices"]
    total_devices = len(all_devices)
    
    # Single worker mode: start all devices
    if num_workers == 1:
        log.info(f"Single worker mode: starting all {total_devices} devices")
        app.state.servers = []
        async for server in start_servers(container.config()):
            app.state.servers.append(server)
            asyncio.create_task(server.start())
        return
    
    # Multi-worker mode: allocate devices based on worker_id
    devices_per_worker = total_devices // num_workers
    
    # Calculate device range for current worker
    start_idx = worker_id * devices_per_worker
    end_idx = start_idx + devices_per_worker
    
    # Last worker handles all remaining devices
    if worker_id == num_workers - 1:
        end_idx = total_devices
    
    # Get device list for current worker
    my_devices = all_devices[start_idx:end_idx]
    
    # Log port range
    if my_devices:
        port_range = f"{my_devices[0]['port']}-{my_devices[-1]['port']}"
        log.info(f"Worker {worker_id}/{num_workers} (PID: {os.getpid()}) "
                 f"handling {len(my_devices)} devices, ports: {port_range}")
    else:
        log.warning(f"Worker {worker_id}/{num_workers} has no devices to handle")
        return
    
    # Start devices assigned to current worker
    app.state.servers = []
    for dev in my_devices:
        host = dev.get("host", None)
        port = dev["port"]
        vendor = dev["vendor"]
        model = dev["model"]
        version = dev["version"]
        
        log.info(f"Worker {worker_id}: Starting SSH server {vendor}-{model}-{version} on "
                 f"{host if host else '0.0.0.0'}:{port}")
        
        server = MockSSHDevice.create_device(
            vendor=vendor,
            model=model,
            version=version,
            host=host,
            port=port
        )
        app.state.servers.append(server)
        asyncio.create_task(server.start())


async def on_shutdown() -> None:
    """ put all clean logic here """
    log.info("Shutting down the application...")
    if hasattr(app.state, 'servers'):
        for server in app.state.servers:
            try:
                if hasattr(server, '_server'):
                    server.stop()
            except Exception as e:
                log.error(f"Error stopping server: {e}")


# Register event handlers on simunet_app instance
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


async def _start_devices_for_worker(worker_id: int, num_workers: int):
    """
    Start allocated devices in worker process
    
    :param worker_id: Worker ID (0-based)
    :param num_workers: Total number of workers
    """
    # Get all device configurations
    all_devices = container.config()["devices"]
    total_devices = len(all_devices)
    
    # Calculate device allocation
    devices_per_worker = total_devices // num_workers
    start_idx = worker_id * devices_per_worker
    end_idx = start_idx + devices_per_worker
    
    # Last worker handles all remaining devices
    if worker_id == num_workers - 1:
        end_idx = total_devices
    
    # Get device list for current worker
    my_devices = all_devices[start_idx:end_idx]
    
    if not my_devices:
        log.warning(f"Worker {worker_id}/{num_workers} has no devices to handle")
        return
    
    port_range = f"{my_devices[0]['port']}-{my_devices[-1]['port']}"
    log.info(f"Worker {worker_id}/{num_workers} (PID: {os.getpid()}) "
             f"handling {len(my_devices)} devices, ports: {port_range}")
    
    # Start devices assigned to current worker
    servers = []
    for dev in my_devices:
        host = dev.get("host", None)
        port = dev["port"]
        vendor = dev["vendor"]
        model = dev["model"]
        version = dev["version"]
        
        log.info(f"Worker {worker_id}: Starting SSH server {vendor}-{model}-{version} on "
                 f"{host if host else '0.0.0.0'}:{port}")
        
        server = MockSSHDevice.create_device(
            vendor=vendor,
            model=model,
            version=version,
            host=host,
            port=port
        )
        servers.append(server)
        await server.start()
    
    # Keep process running
    log.info(f"Worker {worker_id} started {len(servers)} devices successfully")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        log.info(f"Worker {worker_id} shutting down...")
        for server in servers:
            server.stop()


def _start_worker(worker_id: int, num_workers: int, config_file: str = None):
    """
    Start single worker process (process entry point)
    
    :param worker_id: Worker ID (0-based)
    :param num_workers: Total number of workers
    :param config_file: Configuration file path
    """
    # Set environment variables for current process
    os.environ["WORKER_ID"] = str(worker_id)
    os.environ["NUM_WORKERS"] = str(num_workers)
    
    # Reload configuration if config file is specified
    if config_file:
        os.environ["NETDRIVER_SIMUNET_CONFIG"] = config_file
        container.config.from_yaml(config_file, required=True)
    
    # Reconfigure logging for subprocess (avoid log conflicts)
    log_file = container.config.logging.log_file()
    # Use separate log file for each worker
    if log_file and num_workers > 1:
        log_file_base = log_file.rsplit('.', 1)
        if len(log_file_base) == 2:
            log_file = f"{log_file_base[0]}_worker_{worker_id}.{log_file_base[1]}"
        else:
            log_file = f"{log_file}_worker_{worker_id}"
    
    logman.configure_logman(
        level=container.config.logging.level(),
        intercept_loggers=container.config.logging.intercept_loggers(),
        log_file=log_file
    )
    
    # Run async device startup logic
    asyncio.run(_start_devices_for_worker(worker_id, num_workers))


@app.get("/")
async def root() -> dict:
    """ root endpoint """
    return {
        "message": "Welcome to the NetDriver SimuNet",
    }


@app.get("/health")
async def health() -> dict:
    """ health check endpoint for docker """
    return {
        "status": "healthy",
        "service": "netdriver-simunet"
    }


def start():
    """
    Start simunet service
    
    Usage:
    
    1. Default mode (auto-detect workers based on CPU cores):
        simunet  # Auto uses (CPU cores - 2) workers (minimum 1)
    
    2. Specify worker count (using environment variable):
        NUM_WORKERS=4 simunet
    
    3. Specify worker count (using command-line argument):
        simunet --workers 4
        
    Note: 
    - Default auto-detect: max(1, cpu_count - 2)
    - Multi-worker mode does not support reload
    - Single-worker mode supports reload
    """
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
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: auto-detect based on CPU cores, or NUM_WORKERS env var)"
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

    # Determine worker count: command-line arg > env var > auto-detect (CPU cores - 2, min 1)
    num_workers = args.workers
    if num_workers is None:
        num_workers_env = os.getenv("NUM_WORKERS")
        if num_workers_env:
            num_workers = int(num_workers_env)
        else:
            # Auto-detect: CPU cores - 2, minimum 1
            cpu_count = os.cpu_count() or 1
            num_workers = max(1, cpu_count - 2)
            auto_msg = f"Auto-detected {cpu_count} CPU cores, using {num_workers} workers"
            print(auto_msg)
            log.info(auto_msg)
    
    # Get total devices, limit worker count to not exceed device count
    all_devices = container.config()["devices"]
    total_devices = len(all_devices)
    if num_workers > total_devices:
        adjust_msg = (f"Worker count ({num_workers}) exceeds device count ({total_devices}), "
                     f"adjusting to {total_devices} workers")
        print(adjust_msg)
        log.warning(adjust_msg)
        num_workers = total_devices
    
    if num_workers > 1:
        # Multi-worker mode: auto-start multiple processes
        startup_msg = [
            "=" * 60,
            f"Starting Simunet with {num_workers} workers (multi-process mode)",
            f"Note: Auto-reload is disabled in multi-worker mode",
            "=" * 60
        ]
        for msg in startup_msg:
            print(msg)
            log.info(msg)
        
        # Create and start multiple processes
        processes = []
        for worker_id in range(num_workers):
            p = multiprocessing.Process(
                target=_start_worker,
                args=(worker_id, num_workers, args.config),
                name=f"simunet-worker-{worker_id}"
            )
            p.start()
            worker_msg = f"✓ Worker {worker_id}/{num_workers} started (PID: {p.pid})"
            print(worker_msg)
            log.info(worker_msg)
            processes.append(p)
        
        completion_msg = [
            "=" * 60,
            "All workers started successfully!",
            f"Press Ctrl+C to stop all workers",
            "=" * 60
        ]
        for msg in completion_msg:
            print(msg)
            log.info(msg)
        
        # Wait for all processes
        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            shutdown_msg = [
                "\n" + "=" * 60,
                "Stopping all workers...",
                "=" * 60
            ]
            for msg in shutdown_msg:
                print(msg)
                log.info(msg)
            
            for p in processes:
                p.terminate()
            for p in processes:
                p.join()
            
            stop_msg = "✓ All workers stopped"
            print(stop_msg)
            log.info(stop_msg)
    else:
        # Single-worker mode: start all devices
        startup_msg = f"Starting in single-worker mode (all {total_devices} devices)"
        print(startup_msg)
        log.info(startup_msg)
        
        # Handle reload flag
        reload = args.reload and not args.no_reload
        
        if reload:
            reload_msg = "Auto-reload is enabled for development"
            print(reload_msg)
            log.info(reload_msg)
        
        uvicorn.run(
            "netdriver_simunet.main:app",
            host=args.host,
            port=args.port,
            reload=reload
        )
