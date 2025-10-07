#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import abstractmethod
from dependency_injector.providers import Configuration
from pydantic import IPvAnyAddress
from re import Match, Pattern
from typing import Optional, Tuple, List
import asyncssh

from netdriver.exception.errors import ChannelError, ChannelReadTimeout
from netdriver.log import logman
from netdriver.utils.asyncu import async_timeout


log = logman.logger


DEFAULT_SESSION_PROFILE = {
    "read_timeout": 10,
}

_DEFAUTL_SSH_CONFIG = {
    "config": None,
    "known_hosts": None,
    "connect_timeout": 10.0,
    "login_timeout": 3.0,
    "keepalive_interval": 60,
    "keepalive_count_max": 3,
    # Key exchange algorithms
    "kex_algs": set([
      "gss-curve25519-sha256",
      "gss-curve448-sha512",
      "gss-nistp521-sha512",
      "gss-nistp384-sha384",
      "gss-nistp256-sha256",
      "gss-1.3.132.0.10-sha256",
      "gss-gex-sha256",
      "gss-group14-sha256",
      "gss-group15-sha512",
      "gss-group16-sha512",
      "gss-group17-sha512",
      "gss-group18-sha512",
      "gss-group14-sha1",
      "curve25519-sha256",
      "curve25519-sha256@libssh.org",
      "curve448-sha512",
      "ecdh-sha2-nistp521",
      "ecdh-sha2-nistp384",
      "ecdh-sha2-nistp256",
      "ecdh-sha2-1.3.132.0.10",
      "diffie-hellman-group-exchange-sha256",
      "diffie-hellman-group14-sha256",
      "diffie-hellman-group15-sha512",
      "diffie-hellman-group16-sha512",
      "diffie-hellman-group17-sha512",
      "diffie-hellman-group18-sha512",
      "diffie-hellman-group14-sha256@ssh.com",
      "diffie-hellman-group14-sha1",
      "rsa2048-sha256",
      "gss-gex-sha1",
      "gss-group1-sha1",
      "diffie-hellman-group-exchange-sha224@ssh.com",
      "diffie-hellman-group-exchange-sha384@ssh.com",
      "diffie-hellman-group-exchange-sha512@ssh.com",
      "diffie-hellman-group-exchange-sha1",
      "diffie-hellman-group14-sha224@ssh.com",
      "diffie-hellman-group15-sha256@ssh.com",
      "diffie-hellman-group15-sha384@ssh.com",
      "diffie-hellman-group16-sha384@ssh.com",
      "diffie-hellman-group16-sha512@ssh.com",
      "diffie-hellman-group18-sha512@ssh.com",
      "diffie-hellman-group1-sha1",
      "rsa1024-sha1",
    ]),
    # Encryption algorithms
    "encryption_algs": set([
      "chacha20-poly1305@openssh.com",
      "aes256-gcm@openssh.com",
      "aes128-gcm@openssh.com",
      "aes256-ctr",
      "aes192-ctr",
      "aes128-ctr",
      "aes256-cbc",
      "aes192-cbc",
      "aes128-cbc",
      "3des-cbc",
      "blowfish-cbc",
      "cast128-cbc",
      "seed-cbc@ssh.com",
      "arcfour256",
      "arcfour128",
      "arcfour",
    ]),
}
_DEFAULT_READ_BUFFER_SIZE = 8192


def update_ssh_config(kwargs: dict, config: Configuration) -> dict:
    """ Update SSH configuration with defaults and provided parameters """
    extra_kex_algs = set(config.session.ssh.kex_algs() or [])
    extra_encryption_algs = (config.session.ssh.encryption_algs() or [])
    ssh_config = _DEFAUTL_SSH_CONFIG.copy()
    ssh_config["kex_algs"] = list(ssh_config["kex_algs"].union(extra_kex_algs))
    ssh_config["encryption_algs"] = list(ssh_config["encryption_algs"].union(extra_encryption_algs))
    ssh_config["login_timeout"] = config.session.ssh.login_timeout() or ssh_config["login_timeout"]
    ssh_config["connect_timeout"] = config.session.ssh.connect_timeout() or ssh_config["connect_timeout"]
    ssh_config["keepalive_interval"] = config.session.ssh.keepalive_interval() or ssh_config["keepalive_interval"]
    ssh_config["keepalive_count_max"] = config.session.ssh.keepalive_count_max() or ssh_config["keepalive_count_max"]
    kwargs.update(ssh_config)
    return kwargs


class Channel:
    """ Channel interface """
    _logger = None
    _read_buffer_size: int 
    _line_break: str
    _read_channel_until_timeout: float

    @classmethod
    async def create(cls,
                 ip: Optional[IPvAnyAddress] = None,
                 port: int = 22,
                 protocol: str = "ssh",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 encode: str = "utf-8",
                 term_size: Tuple = None,
                 logger: object = None,
                 profile: dict = {},
                 config: Configuration = None,
                 **kwargs: dict) -> "Channel":
        """ Factory method to create channel """

        cls._read_buffer_size = config.session.read_buffer_size() or _DEFAULT_READ_BUFFER_SIZE
        cls._read_channel_until_timeout = profile.get("read_timeout", DEFAULT_SESSION_PROFILE.get("read_timeout", 10))

        if protocol == "ssh":
            kwargs = update_ssh_config(kwargs, config)
            conn = await asyncssh.connect(
                host=str(ip), port=port, username=username, password=password,
                encoding=encode, **kwargs)
            terminal = await conn.create_process(term_type="ansi", term_size=term_size)
            terminal.stdout.channel.set_encoding(encoding=encode, errors='replace')
            return SSHChannel(conn, terminal, logger=logger)
        else:
            raise ValueError(f"protocol {protocol} not supported.")

    @abstractmethod
    async def read_channel(self, buffer_size: int = None) -> str:
        """ read the available data of buff size
        :param buffer_size: int, default is 8192, if None, use the read_buffer_size from config
        """

    @abstractmethod
    async def read_channel_until(
        self,
        cmd: str,
        union_pattern: Pattern,
        more_pattern: Pattern,
        more_cmd: str,
        timeout: float = 10) -> str:

        """
        read data until pattern or timeout
        :param cmd: str, the command last writed
        :param union_pattern: Pattern
        :param handle_more: bool
        :param more_pattern: Pattern
        :param more_cmd: str
        :param timeout: float
        """

    @abstractmethod
    async def write_channel(self, data: str) -> None:
        """ write data to channel """

    @abstractmethod
    async def close(self) -> None:
        """ close channel """

    @abstractmethod
    def is_alive(self) -> bool:
        """ check if channel is alive """

    @abstractmethod
    def read_at_eof(self) -> bool:
        """ check if channel is read eof """


class SSHChannel(Channel):
    """ AsyncSSH Channel """
    _conn: asyncssh.SSHClientConnection
    _terminal: asyncssh.SSHClientProcess

    def __init__(self, conn: asyncssh.SSHClientConnection,
                 terminal: asyncssh.SSHClientProcess,
                 logger: object = None) -> None:
        """ SSH Channel """
        self._conn = conn
        self._terminal = terminal
        self._logger = logger

    def _check_channel(self):
        if not self._conn:
            raise ChannelError("Connection not established")
        if not self.is_alive():
            raise ChannelError("Connection closed")
    
    async def read_channel(self, buffer_size: int = None) -> str:
        self._check_channel()
        buf_size = buffer_size if buffer_size else self._read_buffer_size
        ret = await self._terminal.stdout.read(buf_size)
        self._logger.debug(f"Read:\n<<<{ret}<<<\n")
        return ret

    def _get_lastline(self, chunk: str = "") -> str:
        """ Get the last line from the chunk """
        lines = chunk.splitlines()
        if lines and len(lines) > 0:
            return lines[-1]
        return chunk


    @async_timeout()
    async def read_channel_until(
        self, cmd, union_pattern: Pattern, more_pattern: Pattern, more_cmd: str = '',
        timeout: float = 10) -> str:
        """ Read data until pattern or timeout
        :param union_pattern: Pattern, the pattern to match
        :param handle_more: bool, whether to handle more data
        :param more_pattern: Pattern, the pattern to match for more data
        :param more_cmd: str, the command to send for more data
        :param timeout: float, the timeout for the read operation
        :return: str, the data read from the channel
        """
        self._check_channel()
        output = ReadBuffer(cmd=cmd)
        while not self.read_at_eof():
            chunk = await self.read_channel(self._read_buffer_size)
            output.append(chunk)
            if output.check_pattern(union_pattern, False):
                self._logger.debug(f"Found prompt, stop reading")
                break
            if more_pattern and output.check_pattern(more_pattern):
                self._logger.debug(f"More data detected, sending command: {more_cmd}")
                self._terminal.stdin.write(more_cmd)
                continue
        return output.get_data()

    async def write_channel(self, data: str) -> None:
        self._check_channel()
        self._logger.debug(f"Write:\n>>>{data}<<<\n")
        self._terminal.stdin.write(data)

    async def close(self) -> None:
        self._terminal.close()
        self._conn.close()

    def is_alive(self) -> bool:
        return not self._conn.is_closed() and not self._terminal.is_closing()
    
    def read_at_eof(self) -> bool:
        """ Check if the read end of the channel is at EOF """
        return self._terminal.stdout.at_eof() if self._terminal.stdout else True


class ReadBuffer:
    """ Read buffer for streaming data from stdout and check whether the pattern matched """
    _buffer: List[str]
    # record the last checked line position in the buffer
    _last_line_pos: Tuple[int, int]
    _line_break: str
    # the previous command that used to make sure the prompt is correct
    # because the echo "prompt: {cmd}" may be checked as a matched pattern
    _cmd: str
    _is_cmd_displayed: bool = False

    def __init__(self, cmd: str = '', line_break: str = '\n') -> None:
        """ Initialize read buffer """
        self._buffer = []
        self._last_line_pos = (0, 0)
        self._line_break = line_break
        self._cmd = cmd
        self._is_cmd_displayed = False

    def _check_cmd_displayed(self, line: str = '') -> bool:
        if not self._is_cmd_displayed and self._cmd and line:
            # check if the command is displayed in the line
            if self._cmd in line:
                self._is_cmd_displayed = True
                log.trace(f"Command '{self._cmd}' is displayed in the line: {line}")
    
    def _is_real_prompt(self) -> bool:
        if self._cmd:
            return self._is_cmd_displayed
        return True

    def __str__(self) -> str:
        return self.get_data()

    def append(self, data: str) -> None:
        """ Append data to the buffer """
        if data:
            self._buffer.append(data)
    
    def get_data(self) -> str:
        """ Get the joined data from the buffer """
        return ''.join(self._buffer)

    def check_pattern(self, pattern: Pattern, is_update_checkpos: bool = True) -> Match:
        """
        Check if the pattern is matched with the unchecked buffer
        Start from the last checked position, and check each line in the buffer

        :param pattern: Pattern, the pattern to match
        :param is_update_checkpos: bool, whether to update the last checked position. Set it to False, when you check
            multiple patterns in the same buffer, such as cisco enable with password prompt
        :return: Match object if matched, otherwise None
        """
        if not self._buffer or len(self._buffer) == 0:
            return None

        start_index = self._last_line_pos[0]
        buffer_size = len(self._buffer)
        line = ''
        log.trace(f"Checking start from [{self._last_line_pos[0]}][{self._last_line_pos[1]}]")
        for i in range(start_index, buffer_size):
            line_start_pos = self._last_line_pos[1] if i == start_index else 0
            # concat the fist line in current buffer item
            lb_pos = self._buffer[i].find(self._line_break, line_start_pos)
            while lb_pos != -1:
                # found a line break, concat the line
                line = ''.join([line, self._buffer[i][line_start_pos:lb_pos], self._line_break])
                self._check_cmd_displayed(line)
                line_start_pos = lb_pos + len(self._line_break)
                log.trace(f"Checking buffer[{i}][:{line_start_pos}]: {line}")
                matched = pattern.search(line)
                if matched and self._is_real_prompt():
                    # if matched, update the last line position
                    self._last_line_pos = (i, line_start_pos)
                    return matched
                else:
                    # update the last line position if is_update_checkpos is True
                    if is_update_checkpos:
                        self._last_line_pos = (i, line_start_pos)
                # next line start position
                lb_pos = self._buffer[i].find(self._line_break, line_start_pos)
                line = ''
            
            # no line break found, check the rest of buffer item
            line = ''.join([line, self._buffer[i][line_start_pos:]])
            self._check_cmd_displayed(line)
            line_start_pos += len(line)
            if i == buffer_size - 1:
                # if no line break found and no more buffer, check the last line
                log.trace(f"Checking buffer[{i}][:{line_start_pos}]: {line}")
                matched = pattern.search(line)
                if matched and self._is_real_prompt():
                    # if matched, update the last line position
                    self._last_line_pos = (i, line_start_pos)
                    return matched
        
        return None