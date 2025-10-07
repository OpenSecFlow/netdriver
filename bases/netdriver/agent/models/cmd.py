#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Any
from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field

from netdriver.agent.models.common import CommonRequest, CommonResponse
from netdriver.client.mode import Mode


class CommandRet(BaseModel):
    ret_code: str = Field(description="Status Code. 'OK' or error code.", examples=["OK"])
    command: str = Field("", description="Command", examples=["show version"])
    ret: Any = Field("", description="Return value, raw type returns string, textfsm returns list",
                     examples=["1.1.1"])


class CommandResponse(CommonResponse):
    time: float = Field(0.0, description="Execution time (seconds)", examples=[0])
    result: List[CommandRet] | None = Field(None, description="Command execution result")
    output: str | None = Field(None, description="Device CLI output")

    @classmethod
    def from_error(cls, code: str, msg: str, cor_id: str = None, time: float=0.0, result:
                   list = None, output: str = None) -> "CommandResponse":
        """ Create a CommandResponse object with error """
        _cor_id = cor_id if cor_id else correlation_id.get()
        return cls(code=code, msg=msg, correlation_id=_cor_id, time=time, result=result,
                   output=output)

    @classmethod
    def ok(cls, time: float, result: List[CommandRet], output: str,
           cor_id: str = None) -> "CommandResponse":
        """ Create a CommandResponse object with ok """
        _cor_id = cor_id if cor_id else correlation_id.get()
        return cls(code="OK", msg="", correlation_id=_cor_id, time=time, result=result,
                   output=output)


class Command(BaseModel):
    type: str = Field(description="Type", pattern="raw|textfsm")
    mode: Mode = Field(description="Execution mode", pattern="login|enable|config",
                       examples=["enable"])
    command: str = Field(description="Command", examples=["show version"])
    template: str = Field("", description="Template content, can be empty when type is raw",
                          examples=[""])
    detail_output: bool = Field(
        True, description="Whether to show detailed output, such as auto switch mode and vsys log.",
        examples=[True, False]
    )


class CommandRequest(CommonRequest):
    """ Command Request Model """
    continue_on_error: bool = Field(False, description="continue on error", examples=[True, False])
    commands: List[Command]
