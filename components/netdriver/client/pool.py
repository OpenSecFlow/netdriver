#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from typing import Dict, Optional
from pydantic import IPvAnyAddress
from tabulate import tabulate
from dependency_injector.providers import Configuration
from netdriver.client.session import Session, gen_session_key
from netdriver.exception.errors import PluginNotFound, SessionInitFailed
from netdriver.log import logman
from netdriver.plugin.engine import PluginEngine


log = logman.logger


class SessionPool:
    """ Session Manager Singleton Class """
    _instance = None
    _pool:Dict[str, Session] = {}
    _pool_lock: asyncio.Lock
    _check_interval: float
    _config: Configuration

    def __new__(cls, config: Configuration = None) -> "SessionPool":

        if not cls._instance:
            log.info("Creating SessionManager instance")
            cls._instance = super(SessionPool, cls).__new__(cls)
            cls._instance._pool = {}
            cls._instance._pool_lock = asyncio.Lock()
            cls._instance._config = config
            cls._instance._check_interval = config.session.check_interval() or 30
            asyncio.create_task(cls._instance.monitor_sessions(), name="SessionPoolMonitor")
        return cls._instance

    async def _get_session_by_key(self, session_key: str) -> Optional[Session]:
        """
        Get session by key, if session is not exist or not same, return None.
        This method is used to check whether session is alive or not.
        """

        session = None
        log.info(f"Try to acquire _pool_lock for getting session: {session_key}")
        async with self._pool_lock:
            log.info(f"acquired lock for session {session_key}")
            session = self._pool.get(session_key)
        log.info(f"_pool_lock released")
        if session:
            close_reason  = None
            if not await session.is_alive():
                close_reason = "not alive"
            elif session.check_expiration_time():
                close_reason = "expired"
            elif session.check_idle_time():
                close_reason = "idle timeout"
            if close_reason:
                await self._handle_closed_session(session)
                log.info(f"Session {session_key} is {close_reason}, removed from pool.")
                return None
            log.info(f"Got alived session by key: {session_key}")
            return session            
        else:
            log.info(f"Got no session by key: {session_key}")
            return None

    async def _remove_session_by_key(self, session_key: str) -> None:
        """
        Remove session by key, if session is not exist, do nothing.
        This method is used to remove session from pool.
        """
        log.info(f"Try to acquire _pool_lock and remove session: {session_key}")
        async with self._pool_lock:
            if session_key in self._pool:
                del self._pool[session_key]
                log.info(f"Session {session_key} removed from pool.")
            else:
                log.warning(f"Session {session_key} not found in pool.")
        log.info(f"_pool_lock released")

    async def get_session(self,
                          ip: Optional[IPvAnyAddress] = None,
                          username: Optional[str] = "",
                          password: Optional[str] = "",
                          vendor: Optional[str] = "",
                          model: Optional[str] = "",
                          port: int = 22,
                          protocol: str = "ssh",
                          enable_password: Optional[str] = "",
                          version: str = "base",
                          encode: str = "utf-8",
                          **kwargs: dict
        ) -> Optional[Session]:
        """
        To get a session by key, if session is not exist or not same, create a new session.

        :param protocol: protocol, default is ssh
        :param ip: ipv4 or ipv6 address
        :param port: port, default is 22
        :param username: username login to device
        :param password: password login to device
        :param enable_password: enable password, only for cisco, arista..
        :param vendor: vendor of device, e.g. cisco, huawei
        :param model: model of device, e.g. asa, ios
        :param args: other args
        :param kwargs: other kwargs

        :raises ValueError: client side parameter error
        :raises PluginNotFound: plugin not found for vendor/model/protocol/version
        :raises LoginFailed: login failed
        :raises SessionInitFailed: session init failed
        """

        if not ip:
            raise ValueError("ip is required.")
        if not username:
            raise ValueError("username is required.")
        if not password:
            password = ""
        if not enable_password:
            enable_password = ""
        if not vendor:
            raise ValueError("vendor is required.")
        if not model:
            raise ValueError("type is required.")

        session_key = gen_session_key(protocol, username, ip, port)
        _session = await self._get_session_by_key(session_key)

        # Check whether session is same
        if _session and not _session.is_same(
            vendor, model, version, password, enable_password, encode):
            log.warning(f"Session {session_key} is not same, try to remove it.")
            if _session.is_idle is True:
                 log.warning(f"Session {session_key} is idle, close and regenerate it.")
                 await self._handle_closed_session(_session)
                 _session = None
            else:
                log.warning(f"Session {session_key} is not idle, raise SessionInitFailed.")
                raise SessionInitFailed(
                    f"A session with same key [{session_key}] is still running, " + \
                    "to make sure the execuation safety, please check your request " + \
                    "parameters and try again!")

        # Return session if exist
        if _session:
            log.info(f"Got session by key: {session_key}")
            return _session

        session_clz: Session = PluginEngine().get_plugin(vendor, model, version)
        if not session_clz:
            raise PluginNotFound(
                f"Plugin not found for {vendor}/{model}/{protocol}/{version}")
        
        log.info(f"Try to acquire _pool_lock and add session: {session_key}")
        async with self._pool_lock:
            _session = await session_clz.create(
                ip=ip, port=port, protocol=protocol,
                username=username, password=password, enable_password=enable_password,
                vendor=vendor, model=model, version=version, encode=encode, config=self._config,
                **kwargs)
            self._pool[_session.session_key] = _session
        log.info(f"_pool_lock released, session {_session.session_key} added to pool.")

        # Wait for session initialization to complete
        log.info(f"Waiting for session {_session.session_key} initialization to complete.")
        await _session._init_task_done
        if _session._init_task.exception():
            log.error(f"Session initialization failed: {_session._init_task.exception()}")
            await self._remove_session_by_key(_session.session_key)
            raise _session._init_task.exception()

        log.info(f"Created new session for: {_session.session_key}")
        return _session

    async def _handle_closed_session(self, session: Session):
        log.debug(f"Try to acquire _pool_lock and remove {session.session_key} from pool and close it.")
        try:
            async with self._pool_lock:
                self._pool.pop(session.session_key)
            await asyncio.wait_for(session.close(), timeout=1)
        except Exception as e:
            log.error(f"Error closing session {session.session_key}: {e}")

    async def close_all(self):
        await asyncio.gather(
            *[self._handle_closed_session(session) for session in self._pool.values()])

    async def _display_sessions_info(self):
        """Display session information in a table."""
        table = []
        for session in self._pool.values():
            table.append(await session.get_display_info())
        log.info("\n########## Session Pool Status ########## \n" + tabulate(
            table,
            headers=Session.get_info_headers(),
        ))

    async def _remove_closed_sessions(self):
        # list() is used to avoid RuntimeError: dictionary changed size during iteration
        log.info("Start removing closed sessions from pool.")
        for session_key in list(self._pool):
            session = self._pool.get(session_key)
            if session and not await session.is_alive():
                await self._handle_closed_session(session)
        log.info("Finished removing closed sessions from pool.")

    async def monitor_sessions(self) -> None:
        while True:
            await asyncio.sleep(self._check_interval)
            await self._display_sessions_info()
            await self._remove_closed_sessions()
