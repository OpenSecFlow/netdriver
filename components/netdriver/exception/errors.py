#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .error_code import ErrorCode


class BaseError(Exception):
    # http status code
    status_code: int
    # error code
    code: str
    # error message
    message: str

    def __init__(self, msg: str) -> None:
        if not isinstance(msg, str):
            msg = str(msg)
        self.message = msg
        self.status_code = 500
        self.code = ErrorCode.SERVER_ERROR

    def __str__(self) -> str:
        return self.message


class LoginFailed(BaseError):
    def __init__(self, msg: str = "Login failed, please check your username and passwrod.") -> None:
        super().__init__(msg)
        self.status_code = 401 # Unauthorized
        self.code = ErrorCode.LOGIN_FAILED


class PluginNotFound(BaseError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.status_code = 501 # Not Implemented
        self.code = ErrorCode.PLUGIN_NOT_FOUND


class QueueFullError(BaseError):
    def __init__(self, msg: str = "Queue is full, please try again later.") -> None:
        super().__init__(msg)
        self.status_code = 429 # Too Many Requests
        self.code = ErrorCode.QUEUE_FULL


class ConnectTimeout(BaseError):
    def __init__(self,
                 msg: str = "Connect timeout, please check the connectivity between netdriver-agent and device.") -> None:
        super().__init__(msg)
        self.status_code = 504 # Gateway Timeout
        self.code = ErrorCode.CONNECT_TIMEOUT


class ConnectFailed(BaseError):
    def __init__(self, msg: str = "Connect failed, please check the device status.") -> None:
        super().__init__(msg)
        self.status_code = 502 # Bad Gateway
        self.code = ErrorCode.CONNECT_FAILED


class SessionInitFailed(BaseError):
    def __init__(self,
                 msg: str = "Session init failed, please check the device and credentioals.") -> None:
        super().__init__(msg)
        self.status_code = 502 # Bad Gateway
        self.code = ErrorCode.SESSION_INIT_FAILED


class UnsupportedConfigType(BaseError):
    def __init__(self, msg: str = "Config type only supports: running, routes, hit_counts.") -> None:
        super().__init__(msg)
        self.status_code = 400
        self.code = ErrorCode.UNSUPPORTED_CONFIG_TYPE


class ExecError(BaseError):
    """ Base class for execute command error """
    output: str

    def __init__(self, msg: str, output: str = "") -> None:
        super().__init__(msg)
        self.status_code = 500
        self.code = ErrorCode.EXEC_CMD_ERROR
        self.output = output


class ExecCmdError(ExecError):
    """ Execute command error """


class ExecCmdTimeout(ExecError):
    """ Execute command timeout """
    def __init__(self, msg, output = ""):
        super().__init__(msg, output)
        self.code = ErrorCode.EXEC_CMD_TIMEOUT


class ChannelError(ExecError):
    def __init__(self, msg: str, output: str="") -> None:
        super().__init__(msg, output)
        self.code = ErrorCode.CHANNEL_ERROR


class ChannelReadTimeout(ExecError):
    def __init__(self,
                 msg: str = "Read channel timeout, please check the device status.",
                 output: str = "") -> None:
        super().__init__(msg, output)
        self.status_code = 504
        self.code = ErrorCode.CHANNEL_READ_TIMEOUT


class DetectCurrentModeFailed(ExecError):
    def __init__(self, msg: str = "Detect current mode failed.", output="") -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.DETECT_CURRENT_MODE_FAILED

class DetectCurrentVsysFailed(ExecError):
    def __init__(self, msg: str = "Detect current vsys failed.", output="") -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.DETECT_CURRENT_VSYS_FAILED


class SwitchVsysFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.SWITCH_VSYS_FAILED


class UnsupportedMode(ExecError):
    def __init__(self, msg: str, output: str = "") -> None:
        super().__init__(msg, output)
        self.status_code = 400
        self.code = ErrorCode.UNSUPPORTED_MODE


class EnableFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.ENABLE_FAILED


class DisableFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.DISABLE_FAILED


class ConfigFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.CONFIG_FAILED


class ExitConfigFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.EXIT_CONFIG_FAILED


class GetPromptFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.GET_PROMPT_FAILED


class PullConfigFailed(ExecError):
    def __init__(self, msg: str, output: str) -> None:
        super().__init__(msg, output)
        self.status_code = 500
        self.code = ErrorCode.PULL_CONFIG_ERROR


class UpdateTimeout(ExecError):
    def __init__(self, msg: str, output: str = "") -> None:
        super().__init__(msg, output)
        self.status_code = 504
        self.code = ErrorCode.UPDATE_CONFIG_TIMEOUT


class TextFsmTemplateError(BaseError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.status_code = 500
        self.code = ErrorCode.TEXTFSM_TEMPLATE_ERROR


class TextFsmParseError(BaseError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.status_code = 500
        self.code = ErrorCode.TEXTFSM_PARSE_ERROR


class SaveRepoError(BaseError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.status_code = 500
        self.code = ErrorCode.SAVE_REPO_ERROR
