#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import asyncio
from datetime import datetime
from re import Pattern
from typing import Dict, Optional, List, Any, Tuple

from asyncio import CancelledError, Queue, QueueFull, get_event_loop
from asyncssh import PermissionDenied
from dependency_injector.providers import Configuration
from pydantic import IPvAnyAddress

from netdriver import utils
from netdriver.client.channel import DEFAULT_SESSION_PROFILE, Channel, ReadBuffer
from netdriver.client.merger import Merger
from netdriver.client.mode import Mode
from netdriver.client.task import CmdTask, CmdTaskResult, PullTask, PullTaskResult
from netdriver.exception.errors import (ConnectTimeout, ExecCmdError, ExecCmdTimeout, ExecError, GetPromptFailed,
    LoginFailed, PullConfigFailed, QueueFullError, SessionInitFailed, UnsupportedConfigType)
from netdriver.log.logman import create_session_logger
from netdriver.plugin.types import ConfigType
from netdriver.utils.asyncu import AsyncTimeoutError, async_timeout


def gen_session_key(
        protocol: str, username: str, ip: IPvAnyAddress, port: int) -> str:
    """ Generate session key """
    return f"{protocol}://{username}@{ip}:{port}"


class Session:
    """ Session Class for all CLI Session """
    ip: IPvAnyAddress
    port: int
    protocol: str
    username: str
    password: str
    enable_password: str
    encode: str
    vendor: str
    model: str
    version: str

    _logger = None
    _config: Configuration
    _cmd_queue: Queue
    _cmd_task_consumer: asyncio.Task
    _runconf_req_merger: Merger
    _runconf_req_consumer: asyncio.Task
    _route_req_merger: Merger
    _route_req_consumer: asyncio.Task
    _hitcount_req_merger: Merger
    _route_req_consumer: asyncio.Task
    _channel: Channel
    # current mode
    _mode: Mode
    # current vsys
    _vsys: str = "default"
    _create_time: float
    _last_use: float
    _idle: bool = True
    _is_closing: bool = False
    # cmd hook map
    _cmd_hooks: dict
    _handle_more: bool = False
    _init_task: asyncio.Task
    _init_task_done: asyncio.Future

    @abc.abstractmethod
    def decide_current_mode(self, prompt: str):
        """
        Decide current mode
        """
        raise NotImplementedError("Method decide_current_mode not implemented")

    @abc.abstractmethod
    def decide_current_vsys(self, prompt: str):
        """ Decide current vsys """
        raise NotImplementedError("Method decide_current_vsys not implemented")

    @abc.abstractmethod
    async def disable_pagging(self) -> None:
        """ Disable pagging """
        raise NotImplementedError("Method disable_pagging not implemented")

    @abc.abstractmethod
    async def switch_vsys(self, vsys: str) -> str:
        """ Switch vsys """
        raise NotImplementedError("Method switch_vsys not implemented")

    @abc.abstractmethod
    async def switch_mode(self, mode: Mode) -> str:
        """ Switch mode to target mode """
        raise NotImplementedError("Method switch_mode not implemented")

    @abc.abstractmethod
    def get_default_return(self) -> str:
        """ Get default return """
        raise NotImplementedError("Method get_default_return not implemented")

    @abc.abstractmethod
    def get_union_pattern(self) -> Pattern:
        """ Get union pattern for all mode prompts """
        raise NotImplementedError("Method get_union_pattern not implemented")

    @abc.abstractmethod
    def get_error_patterns(self) -> List[Pattern]:
        """ Get pattern of all mode error prompts """
        raise NotImplementedError("Method get_error_patterns not implemented")

    @abc.abstractmethod
    def get_ignore_error_patterns(self) -> List[Pattern]:
        """ Get pattern of all mode ignore error prompts """
        raise NotImplementedError("Method get_ignore_error_patterns not implemented")

    @abc.abstractmethod
    def get_auto_confirm_patterns(self) -> Dict[Pattern, str]:
        """ Get auto confirm patterns and cmds"""
        raise NotImplementedError("Method get_auto_confirm_patterns not implemented")

    @abc.abstractmethod
    def get_more_pattern(self) -> Tuple[Pattern, str]:
        """ Get more pattern and more command """
        raise NotImplementedError("Method get_more_pattern not implemented")

    @abc.abstractmethod
    async def pull_running_config(self, vsys: str = None) -> str:
        """ Pull running config """
        raise NotImplementedError("Method pull_running_config not implemented")

    @abc.abstractmethod
    async def pull_routes(self, vsys: str = None) -> str:
        """ Pull routes """
        raise NotImplementedError("Method pull_routes not implemented")

    @abc.abstractmethod
    async def pull_hitcounts(self, vsys: str = None) -> str:
        """ Pull hit counts """
        raise NotImplementedError("Method pull_hit_counts not implemented")


    @classmethod
    async def create(cls, *args, **kwargs) -> "Session":
        """ Create session

        :raises ConnectTimeout: if connect timeout
        :raises LoginFailed: if login failed
        :raises SessionInitFailed: if session init failed
        """
        session = cls(*args, **kwargs)
        session._init_task_done = asyncio.Future()
        session._init_task = asyncio.create_task(session._async_init(),
                                                 name=f"{session.session_key}_async_init")
        return session


    def __init__(self,
                 ip: Optional[IPvAnyAddress] = None,
                 port: int = 22,
                 protocol: str = "ssh",
                 username: Optional[str] = "",
                 password: Optional[str] = "",
                 enable_password: Optional[str] = "",
                 vendor: Optional[str] = "",
                 model: Optional[str] = "",
                 version: Optional[str] = "",
                 encode: str = "utf-8",
                 queue_size: int = 64,
                 **kwargs) -> None:
        if not ip:
            raise ValueError("ip is required.")
        if not username:
            raise ValueError("username is required.")
        if not password:
            raise ValueError("password is required.")
        if not vendor:
            raise ValueError("vendor is required.")
        if not model:
            raise ValueError("model is required.")
        if not version:
            raise ValueError("version is required.")

        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.encode = encode
        self.vendor = vendor
        self.model = model
        self.version = version
        self._logger = create_session_logger(self.session_key)
        self._config = kwargs.get("config", Configuration())
        profiles = self._config.session.profiles() if self._config else {}
        self._session_profile = self.load_session_profile(profiles)
        self._cmd_queue = Queue(queue_size)
        self._runconf_req_merger = Merger()
        self._route_req_merger = Merger()
        self._hitcount_req_merger = Merger()
        self._create_time = datetime.now().timestamp()
        self._last_use = None
        self._cmd_hooks = {}
        self._mode = None
        self._init_task = None
        self._channel = None

    @property
    def session_key(self) -> str:
        return gen_session_key(self.protocol, self.username, self.ip,
                               self.port)

    @property
    def is_idle(self) -> bool:
        """ Check if session is idle """
        return self._cmd_queue.empty() and self._idle

    def load_session_profile(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """ Load session profile
        Load session profile from config, priority:
        1. profile from matched ip address
        2. profile from matched vendor/model/version
        3. profile from matched vendor/model/base
        4. profile from matched global
        5. default profile
        """
        if not profiles:
            self._logger.debug(f"No session profiles found, using default profile: {DEFAULT_SESSION_PROFILE}")
            return DEFAULT_SESSION_PROFILE

        # IP specific profile is the #1 priority
        ip_profiles = profiles.get(("ip"), {})
        if str(self.ip) in ip_profiles:
            profile = ip_profiles[str(self.ip)]
            if profile:
                self._logger.debug(f"Load session profile from ip: {self.ip}, profile: {profile}")
                return profile

        model_profile = profiles.get("vendor", {}).get(self.vendor, {}).get(self.model, {})
        if model_profile:
            version_profile = model_profile.get(self.version, {})
            base_profile = model_profile.get("base", {})
            # version specific profile is the #2 priority
            if version_profile:
                self._logger.debug(
                    f"Load session profile from: {self.vendor}/{self.model}/{self.version}, profile: {version_profile}")
                return version_profile
            # base profile is the #3 priority
            if base_profile:
                self._logger.debug(
                    f"Load session profile from: {self.vendor}/{self.model}/base, profile: {base_profile}")
                return base_profile

        global_profile = profiles.get("global", {})
        if global_profile:
            # Global profile is the #4 priority
            self._logger.debug(f"Load session profile from global, profile: {global_profile}")
            return global_profile
        else:
            # Default profile is the #5 priority
            self._logger.debug(f"Load session profile from default, profile: {DEFAULT_SESSION_PROFILE}")
            return DEFAULT_SESSION_PROFILE

    async def _async_init(self):
        try:
            await self._create_channel()
            await self._init_session()
            self._cmd_task_consumer = asyncio.create_task(self._consume_cmd_queue(),
                                                          name=f"{self.session_key}_cmd_consumer")
            self._runconf_req_consumer = asyncio.create_task(self._consume_runconf_queue(),
                                                             name=f"{self.session_key}_runconf_req_consumer")
            self._route_req_consumer = asyncio.create_task(self._consume_routes_queue(),
                                                           name=f"{self.session_key}_route_req_consumer")
            self._hitcount_req_consumer = asyncio.create_task(self._consume_hitcounts_queue(),
                                                              name=f"{self.session_key}_hitcount_req_consumer")
        except ConnectTimeout as e:
            raise e
        except ExecError as e:
            raise e
        except asyncio.TimeoutError as e:
            raise ConnectTimeout() from e
        except PermissionDenied as e:
            raise LoginFailed(f"{e}, please check your username and password.") from e
        except NotImplementedError as e:
            raise SessionInitFailed(
                f"{e}, please check your vendor/model/version parameters.") from e
        except Exception as e:
            raise SessionInitFailed(e) from e       # TODO: Session Log
        finally:
            self._init_task_done.set_result(True)

    async def _create_channel(self) -> None:
        self._channel = await Channel.create(
            ip=self.ip, port=self.port, protocol=self.protocol, username=self.username, password=self.password,
            encode=self.encode, logger=self._logger, profile=self._session_profile,
            config=self._config)

    async def _decide_init_state(self) -> str:
        prompt = await self._get_prompt()
        self.decide_current_mode(prompt)
        self.decide_current_vsys(prompt)
        return prompt

    async def _init_session(self) -> None:
        self._logger.info(f"Init session")
        await self._decide_init_state()
        await self.disable_pagging()
        self._logger.info(f"Session init done")

    def is_same(self, vendor: str, model: str, version: str, password: str, enable_password: str,
                encode: str) -> bool:
        """ Check if session is same """
        return self.vendor == vendor and self.model == model and self.version == version and \
            self.password == password and self.enable_password == enable_password and \
            self.encode == encode

    def _enqueue(self, task: CmdTask):
        """
        Enqueue task
        :param task: task to enqueue
        :raises asyncio.QueueFull: if queue is full
        """
        task.set_enqueue_timestamp()
        self._cmd_queue.put_nowait(task)

    async def _dequeue(self) -> CmdTask:
        """ Dequeue task """
        try:
            task: CmdTask = await self._cmd_queue.get()
            task.set_dequeue_timestamp()
            task.set_exec_start_timestamp()
            return task
        except CancelledError as e:
            self._logger.debug("Session cancelled during dequeue operation.")
            return None

    async def _exec_cmd_task(self, task: CmdTask) -> str:
        self._logger.info(f"Start exec cmd task: {task} in session: {self.session_key}")
        start_time = asyncio.get_event_loop().time()
        output = ""
        err_msg = ""
        has_error = False
        try:
            # decide mode and vsys before exec cmd
            output += await self._decide_init_state()
            output += await self._switch_vsys_and_mode(vsys=task.vsys, mode=task.mode)
            # if no need detail output, use last line of output as detail output
            if not task.detail_output and output:
                output = output.splitlines()[-1]

            # exec cmd line-by-line, check error line-by-line, stop on error
            lines = task.command.splitlines()
            line_size = len(lines)
            i = 0
            while not has_error and i < line_size:
                line = lines[i]
                self._logger.info((f"Exec cmd[{i}]: {line}"))
                output += await self.exec_cmd(line)
                if task.catch_error:
                    error = utils.regex.catch_error_of_output(output,
                                                              self.get_error_patterns(),
                                                              self.get_ignore_error_patterns())
                    if error:
                        err_msg = error
                        has_error = True
                        self._logger.error(f"Exec cmd[{i}]: {line}, error: {error}")
                self._logger.info(f"Finished exec cmd[{i}]: {line}")
                i += 1
            time_consumed: float = asyncio.get_event_loop().time() - start_time
            self._logger.info(f"Finished exec cmd task: {task}, cost: {time_consumed:.3f}s")
            task.set_result(output=output,
                            exception=ExecCmdError(err_msg, output=output) if has_error else None)
        except AsyncTimeoutError as e:
            task.set_result(output=output, exception=e)
        except ExecError as e:
            output += e.output
            e.output = output
            task.set_result(output=output, exception=e)
        except BaseException as e:
            # catch all exception
            task.set_result(output=output, exception=ExecError(e, output=output))
        return output

    async def _consume_cmd_queue(self):
        self._logger.info(f"Start consuming cmd queue")
        while not self._is_closing:
            output = ""
            task = await self._dequeue()
            if task is None:
                continue
            self._idle = False
            try:
                # run task withtimeout
                output = await asyncio.wait_for(self._exec_cmd_task(task), timeout=task.timeout)
            except asyncio.CancelledError as e:
                self._logger.warning(f"_consume_cmd_queue cancelled: {e}", exc_info=True)
                break
            except asyncio.TimeoutError as e:
                task.set_result(output=output, exception=ExecCmdTimeout(e, output=output))
            except BaseException as e:
                self._logger.exception(e)
                task.set_result(output=output, exception=ExecCmdError(e, output=output))
            finally:
                self._idle = True
                try:
                    self._cmd_queue.task_done()
                except Exception as e:
                    self._logger.warning("Called task_done too many times.")

    async def _consume_runconf_queue(self):
        self._logger.info(f"Start consuming runconf queue")
        output: str = ""
        while not self._is_closing:
            task_dict = await self._runconf_req_merger.get_mergable_tasks()
            if not task_dict:
                continue
            for vsys, tasks in task_dict.items():
                output = None
                exception = None
                try:
                    self._logger.info(f"Get [{len(tasks)}] pull_running_config tasks of {vsys}.")
                    self._logger.info(f"Pulling running config.")
                    output = await self.pull_running_config(vsys)
                    self._logger.info(f"Pulled running config, length: [{len(output)}].")
                except asyncio.CancelledError as e:
                    self._logger.warning(f"_consume_runconf_queue cancelled: {e}", exc_info=True)
                    break
                except ExecError as exec_e:
                    exec_e.output = output
                    exception = exception
                except BaseException as e:
                    exception = PullConfigFailed(e, output=output)
                finally:
                    self._runconf_req_merger.set_mergable_tasks_result(tasks=tasks, output=output, exception=exception)
            
    async def _consume_routes_queue(self):
        self._logger.info(f"Start consuming routes queue")
        output: str = ""
        while not self._is_closing:
            task_dict = await self._route_req_merger.get_mergable_tasks()
            if not task_dict:
                continue
            for vsys, tasks in task_dict.items():
                output = None
                exception = None
                try:
                    self._logger.info(f"Get [{len(tasks)}] pull_routes tasks of {vsys}.")
                    self._logger.info(f"Pulling routes.")
                    output = await self.pull_routes(vsys)
                    self._logger.info(f"Pulled routes, length: [{len(output)}].")
                except asyncio.CancelledError as e:
                    self._logger.warning(f"_consume_routes_queue cancelled: {e}", exc_info=True)
                    break
                except ExecError as exec_e:
                    exec_e.output = output
                    exception = exec_e
                except BaseException as e:
                    exception = PullConfigFailed(e, output=output)
                finally:
                    self._route_req_merger.set_mergable_tasks_result(tasks=tasks, output=output, exception=exception)

    async def _consume_hitcounts_queue(self):
        self._logger.info(f"Start cosuming hitcountrs queue")
        while not self._is_closing:
            task_dict = await self._hitcount_req_merger.get_mergable_tasks()
            if not task_dict:
                continue
            output = None
            exception = None
            for vsys, tasks in task_dict.items():
                output = None
                exception = None
                try:
                    self._logger.info(f"Get [{len(tasks)}] pull_hitcounts tasks of {vsys}.")
                    self._logger.info(f"Pulling hit_counts.")
                    output = await self.pull_hitcounts(vsys)
                    self._logger.info(f"Pulled hit_counts, length: [{len(output)}].")
                except asyncio.CancelledError as e:
                    self._logger.warning(f"_consume_hitcounts_queue cancelled: {e}", exc_info=True)
                    break
                except ExecError as exec_e:
                    exec_e.output = output
                    exception = exec_e
                except BaseException as e:
                    exception = PullConfigFailed(e, output=output)
                finally:
                     self._hitcount_req_merger.set_mergable_tasks_result(tasks=tasks, output=output, exception=exception)

    async def _get_prompt(self, write_return: bool = True) -> str:
        """ Get current prompt """
        if write_return:
            await self.write_channel("")
        union_pattern = self.get_union_pattern()
        ret = await self.read_channel_util_prompt()

        # from lastline to fist union pattern match
        if not ret:
            raise GetPromptFailed("Get prompt failed, no data returned from channel.", ret)
        lines = ret.splitlines()
        # check last two lines for union pattern
        for line in lines[-2:]:
            if union_pattern.search(line):
                return line
        raise GetPromptFailed("Get prompt failed, no union pattern matched in the output.", ret)

    async def is_alive(self) -> bool:
        """ Check if session is alive """
        await self._init_task_done
        return not self._channel or self._channel.is_alive()

    async def close(self) -> None:
        """ Close session """
        try:
            self._is_closing = True
            self._cmd_task_consumer.cancel()
            await self._cmd_queue.join()
            self._runconf_req_consumer.cancel()
            await self._runconf_req_merger.join()
            self._route_req_consumer.cancel()
            await self._route_req_merger.join()
            self._hitcount_req_consumer.cancel()
            await self._hitcount_req_merger.join()
        except Exception as e:
            self._logger.error(f"Error closing session {self.session_key}: {e}")   
        finally:
            if self._channel:
                await self._channel.close()

    async def read_channel(self) -> str:
        """ Read the available data of default buff size """
        self._last_use = datetime.now().timestamp()
        return await self._channel.read_channel()

    async def read_channel_util_prompt(self, cmd: str = '') -> str:
        """ read channel util prompt """
        self._last_use = datetime.now().timestamp()
        return await self._channel.read_channel_until(
            cmd=cmd,
            union_pattern=self.get_union_pattern(),
            more_pattern=self.get_more_pattern()[0],
            more_cmd=self.get_more_pattern()[1])

    async def write_channel(self, data: str, auto_enter: bool = True) -> None:
        """ Write data to channel"""
        if auto_enter and not data.endswith(self.get_default_return()):
            data += self.get_default_return()
        await self._channel.write_channel(data)
        self._last_use = datetime.now().timestamp()

    async def _switch_vsys_and_mode(self, vsys: str = None, mode: Mode = None) -> str:
        """ Execute command in specific mode without output """
        # Switch mode and vsys if needed
        output = ReadBuffer()
        if vsys and self._vsys != vsys:
            output.append(await self.switch_vsys(vsys))
        # Switch mode if needed
        if mode and self._mode != mode:
            output.append(await self.switch_mode(mode))
        return output.get_data()

    async def exec_cmd_hooks(self, command: str) -> str:
        """ Execute command hooks """
        if command in self._cmd_hooks:
            self._logger.info(f"Exec command hook for command: {command}")
            return await self._cmd_hooks[command](command)

    async def exec_cmd(self, command: str) -> str:
        """
        Execute command with output
        @raise ChannelReadTimeout: if read channel timeout
        """
        output = ReadBuffer()
        if command in self._cmd_hooks:
            output.append(await self.exec_cmd_hooks(command))
        else:
            await self.write_channel(command)
            output.append(await self.read_channel_util_prompt(cmd=command))
        return output.get_data()

    async def exec_cmd_in_vsys_and_mode(self, command: str, vsys: str = None, mode: Mode = None) -> str:
        """
        Execute command in specific vsys and mode with output
        """
        output = ""
        output += await self._decide_init_state()
        output += await self._switch_vsys_and_mode(vsys=vsys, mode=mode)
        lines = command.splitlines()
        line_size = len(lines)
        i = 0
        while i < line_size:
            line = lines[i]
            output += await self.exec_cmd(line)
            i += 1
        return output 

    async def send_cmd(self, command: str, vsys: str = None, mode: Mode = None,
                       timeout: float = 10, catch_error: bool = True, detail_output: bool = True) -> CmdTaskResult:
        """
        Execute command in specific mode with output
        :param command: command to execute, supoort multi-line command
        :param vsys: vsys to execute, if not set, use current vsys
        :param mode: mode to execute, if not set, use current mode
        :param detail_output: is the detailed output
        :return: Future, result of command, need to await to get result
        """
        task: CmdTask= CmdTask(command, vsys=vsys, mode=mode, timeout=timeout,
                          catch_error=catch_error, detail_output=detail_output,
                          future=get_event_loop().create_future())
        try:
            if self._is_closing:
                _msg = f"Session is closing, please try again later. Session: {self.session_key}"
                self._logger.warning(_msg)
                raise ExecCmdError(_msg)
            self._enqueue(task)
            self._logger.info(f"Send task: {task} to session queue: {self.session_key}")
        except QueueFull:
            _msg = f"Send cmd failed! Session: {self.session_key} Cmd: [{ task }]; \
                Reason: Queue is full, please retry or check the agent."
            self._logger.error(_msg)
            task.set_result(exception=QueueFullError(_msg))

        return await task.get_result()

    async def send_cmd_only(self, command: str, vsys: str, mode: Mode):
        """
        Execute command in specific mode without output
        :param command: command to execute, supoort multi-line command
        :param vsys: vsys to execute, if not set, use current vsys
        :param mode: mode to execute, if not set, use current mode

        """
        task: CmdTask = CmdTask(command, vsys=vsys, mode=mode)
        try:
            self._enqueue(task)
        except QueueFull:
            _msg = f"Send cmd failed! Session: {self.session_key} Cmd: [{ task }]; \
                Reason: Queue is full, please retry or check the agent."
            self._logger.error(_msg)
        finally:
            task.cacnel()
            # del task

    async def pull(self, type: ConfigType, vsys: str, timeout: float = 10.0) -> PullTaskResult:
        """ Send request to pull queue
        :param task: PullTask
        :return: PullTaskResult
        """
        task: PullTask = PullTask(type=type, vsys=vsys, timeout=timeout,
                        future=get_event_loop().create_future())
        match task.type:
            case ConfigType.RUNNING:
                await self._runconf_req_merger.enqueue(task)
            case ConfigType.ROUTE:
                await self._route_req_merger.enqueue(task)
            case ConfigType.HIT_COUNT:
                await self._hitcount_req_merger.enqueue(task)
            case _:
                self._logger.warning(f"Unsupported config type: {task.type}")
                task.set_result(exception=UnsupportedConfigType())
        return await task.get_result()

    async def get_display_info(self) -> List[Any]:
        """Return session information."""
        await self._init_task_done
        create_time = datetime.fromtimestamp(self._create_time).strftime('%Y-%m-%d %H:%M:%S')
        last_use = "N/A"
        if self._last_use:
            last_use = datetime.fromtimestamp(self._last_use).strftime('%Y-%m-%d %H:%M:%S')
        return [self.session_key, self._mode, self._vsys, await self.is_alive(), self._idle,
            self._cmd_queue.qsize(), create_time, last_use]

    @classmethod
    def get_info_headers(cls) -> List[str]:
        """ Return session information headers """
        return ["Session", "Mode", "Vsys", "Alive", "Idle", "Queue Size", "Create Time",
                "Last Use"]

    def register_hook(self, command: str, handler):
        """ Register a hook for a specific command """
        self._cmd_hooks[command] = handler

    @async_timeout()
    async def _handle_auto_confirms(self, cmd, timeout: float = 10.0, auto_enter: bool = True) -> str:
        """ Automatically confirm prompts based on patterns """

        union_pattern = self.get_union_pattern()
        auto_confirm_patterns = self.get_auto_confirm_patterns()
        output = ReadBuffer(cmd=cmd)
        pattern_count = len(auto_confirm_patterns) + 1 # + 1 for union pattern

        while not self._channel.read_at_eof():
            chunk = await self.read_channel()
            output.append(chunk)
            # make sure the last check should update the position
            i = 1
            is_update_pos = True if i == pattern_count else False

            i += 1
            if union_pattern and output.check_pattern(union_pattern, is_update_pos):
                self._logger.info("Finished save")
                break

            for pattern, confirm_cmd in auto_confirm_patterns.items():
                is_update_pos = True if i == pattern_count else False
                i += 1
                if output.check_pattern(pattern, is_update_pos):
                    self._logger.info(f"Matched confirm pattern: {pattern}, send confirm cmd: {confirm_cmd}")
                    await self.write_channel(confirm_cmd, auto_enter=auto_enter)

        return output.get_data()

    async def get_runconf_templates(self) -> Dict[str, str]:
        """ Get running config tempaltes
        using aiofiles to load templates from ./{vendor}_{model} directory:
        load all files which ends with .textfsm, and the filename should be runconf_{key}.textfsm,
        content as value
        :return: Dict[str, str]
        """
        directory = utils.files.get_plugin_dir(self)
        return await utils.files.load_templates(
            directory= f"{directory}/{self.info.vendor}_{self.info.model}", prefix="runconf")

    async def get_hitcounts_templates(self) -> Dict[str, str]:
        """ Get hit counts tempaltes
        using aiofiles to load templates from ./{vendor}_{model} directory:
        load all files which ends with .textfsm, and the filename should be hitcounts_{key}.textfsm,
        content as value
        :return: Dict[str, str]
        """
        directory = utils.files.get_plugin_dir(self)
        return await utils.files.load_templates(
            directory= f"{directory}/{self.info.vendor}_{self.info.model}", prefix="hitcount")

    async def get_routes_templates(self) -> Dict[str, str]:
        """ Get routes tempaltes
        using aiofiles to load templates from ./{vendor}_{model} directory:
        load all files which ends with .textfsm, and the filename should be routes_{key}.textfsm,
        content as value
        :return: Dict[str, str]
        """
        directory = utils.files.get_plugin_dir(self)
        return await utils.files.load_templates(
            directory= f"{directory}/{self.info.vendor}_{self.info.model}", prefix="route")

    def check_idle_time(self) -> bool:
        """Check whether the session needs to be closed due to prolonged idle time"""
        max_idle_time = self._session_profile.get("max_idle_time")
        if max_idle_time is None:
            return False
        now = datetime.now().timestamp()
        idle_time = now - self._last_use
        if idle_time > max_idle_time:
            self._logger.info(f"Session idle time {idle_time:.1f}s exceeds maximum allowed {max_idle_time}s")
            return True
        return False

    def check_expiration_time(self) -> bool:
        """Check if the session was created before today's expiration time"""
        expiration_time_str = self._session_profile.get("expiration_time")
        if expiration_time_str is None:
            return False
        try:
            expiration_time = datetime.strptime(expiration_time_str, "%H:%M").time()
        except Exception:
            return False
        now = datetime.now().timestamp()
        today_expiration = datetime.combine(datetime.now().date(), expiration_time).timestamp()
        if today_expiration <= now and self._create_time < today_expiration:
            create_time_strf = datetime.fromtimestamp(self._create_time).strftime('%Y-%m-%d %H:%M:%S')
            today_expiration_strf = datetime.fromtimestamp(today_expiration).strftime('%Y-%m-%d %H:%M:%S')
            self._logger.info(f"Session create time: {create_time_strf}, expiration time: {today_expiration_strf}")
            return True
        return False
