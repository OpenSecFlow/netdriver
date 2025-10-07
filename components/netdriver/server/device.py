#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
import socket
from typing import List, Optional

import asyncssh

from netdriver.log import logman
from netdriver.exception.server import ClientExit
from netdriver.server.handlers import CommandHandler, CommandHandlerFactory
from netdriver.server.user_repo import UserRepo


class MockSSHDevice(asyncssh.SSHServer):
    """ Create mock SSH-device """
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
        """ Create a mock SSH-device

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
        if host_keys is None:
            host_keys = [asyncssh.generate_private_key('ssh-rsa')]
        self.host_keys = host_keys
        if user_repo is None:
            user_repo = UserRepo()
        self.user_repo = user_repo
        self._handlers = []

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        """ Hook after connection established """
        peer_name = conn.get_extra_info('peername')
        client_ip, client_port = peer_name[0], peer_name[1]
        self._logger.info(f"SSH connection received from {client_ip}:{client_port}")

    def connection_lost(self, exc: Optional[Exception]):
        """ Hook after connection lost """
        if exc:
            self._logger.error(f"SSH connection error: {exc}")
        else:
            self._logger.info('SSH connection closed')

    def password_auth_supported(self) -> bool:
        """ Configure to use password authentication """
        return True

    def begin_auth(self, username: str) -> bool:
        """ Begin user authentication """
        return True

    async def validate_password(self, username: str, password: str) -> bool:
        """ Validate user password """
        self._logger.info(f"Validating user {username} with password {password}")
        return await self.user_repo.auth(username, password)

    async def handle_process(self, process: asyncssh.SSHServerProcess):
        """ Handle process created by SSH client """
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
            self._logger.info(f"Client exited: {e}")
            process.exit(0)
        except Exception as e:
            _msg = f"An unexpected error occurred: {e}"
            self._logger.error(_msg)
            process.stdout.write(_msg)
            process.exit(1)
        finally:
            try:
                process.exit(0)
            except Exception as e:
                self._logger.error(f"Error during process cleanup: {e}")

    async def start(self):
        """ Start mock SSH-device """
        self._server = await asyncssh.create_server(
            MockSSHDevice,
            host=self.host,
            port=self.port,
            family=self.family,
            server_host_keys=self.host_keys,
            trust_client_host=True,
            process_factory=self.handle_process,
        )
        self._logger.info(f"SSH server started at: {self._server.get_addresses()}")

    def stop(self):
        """ Stop mock SSH-device """
        self._server.close()
        self._logger.info("SSH server stopped")

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
