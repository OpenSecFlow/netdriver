#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
"""
Mock SSH Device Simulator

Creates realistic network device simulations for testing and development.
Enables safe testing of network automation scripts without requiring physical
hardware or risking configuration changes on production devices.
"""
import socket
from typing import List, Optional

import asyncssh

from netdriver.log import logman
from netdriver.exception.server import ClientExit
from netdriver.server.handlers import CommandHandler, CommandHandlerFactory
from netdriver.server.user_repo import UserRepo


class MockSSHDevice(asyncssh.SSHServer):
    """
    Programmable SSH server that mimics real network device behavior.
    
    Enables safe testing by simulating device responses without requiring
    physical hardware. Supports vendor-specific command handlers to replicate
    authentic device interactions and CLI behaviors.
    """
    _server: asyncssh.SSHAcceptor
    _logger = logman.logger
    _handlers = List[CommandHandler]

    vendor: str
    model: str
    version: str
    host : str
    port : int
    family : int
    host_keys : list
    user_repo: UserRepo

    @classmethod
    def create_device(cls, vendor: str, model: str, version: str, host: str = None,
                      port: int = 8022, family: int = socket.AF_INET, host_keys: list = None,
                      user_repo: UserRepo = None) -> "MockSSHDevice":
        """
        Factory method for vendor-specific device simulation.
        
        Creates a configured mock device that behaves like the specified vendor/model.
        Enables testing against multiple device types without hardware dependencies.
        Create a mock SSH-device

        @param vendor: Vendor name of the device
        @param model: Model name of the device
        @param version: Version of the device
        @param host: Hostname or IP address to listen on, default is all interfaces
        @param port: Port number to listen on, default is 8022
        @param family: Address family to listen on, default is AF_INET
        @param host_keys: List of host key files, default is ['config/simunet/keys/host_key']
        @param user_repo: user repository for authentication
        """
        device = cls(host, port, family, host_keys, user_repo)
        device.vendor = vendor
        device.model = model
        device.version = version
        return device

    def __init__(self, host: str = None, port: int = 8022,
                 family: int = socket.AF_INET, host_keys: list = None, user_repo: UserRepo = None):
        self.host = host
        self.port = port
        self.family = family
        # Generate ephemeral keys for testing to avoid key management complexity
        if host_keys is None:
            host_keys = [asyncssh.generate_private_key('ssh-rsa')]
        self.host_keys = host_keys
        if user_repo is None:
            user_repo = UserRepo()
        self.user_repo = user_repo
        self._handlers = []

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        """Connection logging for debugging and audit trails."""
        peer_name = conn.get_extra_info('peername')
        client_ip, client_port = peer_name[0], peer_name[1]
        self._logger.info(f"SSH connection received from {client_ip}:{client_port}")

    def connection_lost(self, exc: Optional[Exception]):
        """Connection cleanup with error diagnosis."""
        if exc:
            self._logger.error(f"SSH connection error: {exc}")
        else:
            self._logger.info('SSH connection closed')

    def password_auth_supported(self) -> bool:
        """Enables password authentication for testing simplicity."""
        return True

    def begin_auth(self, username: str) -> bool:
        """Always allow auth attempts to reach validation stage."""
        return True

    async def validate_password(self, username: str, password: str) -> bool:
        """Delegate authentication to configurable user repository."""
        self._logger.info(f"Validating user {username} with password {password}")
        return await self.user_repo.auth(username, password)

    async def handle_process(self, process: asyncssh.SSHServerProcess):
        """
        Main command processing loop with vendor-specific behavior simulation.
        
        Creates appropriate command handler based on device type to provide
        realistic CLI interactions and responses for testing automation scripts.
        """
        width, height, pixwidth, pixheight = process.term_size
        self._logger.info(f"Process started with size [{width}x{height}] pixels \
                          [{pixwidth}x{pixheight}]")

        try:
            _handler = CommandHandlerFactory.create_handler(process, self.vendor, self.model,
                                                            self.version)
            self._handlers.append(_handler)
            await _handler.run()
        except ValueError as e:
            self._logger.error(e)
            process.stdout.write(str(e))
            process.exit(1)
        except ClientExit as e:
            # Normal client disconnection - not an error condition
            self._logger.info(f"Client exited: {e}")
            process.exit(0)
        except Exception as e:
            _msg = f"An unexpected error occurred: {e}"
            self._logger.error(_msg)
            process.stdout.write(_msg)
            process.exit(1)
        finally:
            # Defensive cleanup to prevent resource leaks
            try:
                process.exit(0)
            except Exception as e:
                self._logger.error(f"Error during process cleanup: {e}")

    async def start(self):
        """Initialize SSH server with realistic device configuration."""
        self._server = await asyncssh.create_server(
            MockSSHDevice,
            host=self.host,
            port=self.port,
            family=self.family,
            server_host_keys=self.host_keys,
            trust_client_host=True,  # Testing convenience - don't verify client hosts
            process_factory=self.handle_process,
        )
        self._logger.info(f"SSH server started at: {self._server.get_addresses()}")

    def stop(self):
        """Graceful server shutdown."""
        self._server.close()
        self._logger.info("SSH server stopped")

    async def __aenter__(self):
        """Async context manager support for clean resource management."""
        await self.start()

    async def __aexit__(self, exc_type, exc, tb):
        """Ensure server cleanup even if exceptions occur."""
        await self.stop()
