#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from netdriver.agent.models.cmd import CommandResponse
from netdriver.agent.models.common import CommonResponse
from netdriver.exception.error_code import ErrorCode
from netdriver.exception.errors import BaseError, ExecError
from netdriver.log import logman
from netdriver.utils.terminal import simulate_output


log = logman.logger

async def request_validation_error_handler(
        request: Request, exc: RequestValidationError) -> JSONResponse:
    log.warning(f"Request validation error: {exc}")
    error_msg = ""
    for error in exc.errors():
        loc = '->'.join(map(str, error['loc']))
        error_msg += f"[{loc}] {error['msg']}\n"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            CommonResponse.from_error(ErrorCode.CLIENT_PARAM_ERROR, msg=error_msg))
    )


async def value_error_handler(request: Request, exc: ValueError):
    log.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            CommonResponse.from_error(ErrorCode.CLIENT_PARAM_ERROR, msg=str(exc)))
    )


async def exec_error_handler(request: Request, exc: ExecError):
    log.error(f"Execute command error: {exc}")
    handled_output = simulate_output(exc.output)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            CommandResponse.from_error(code=exc.code, msg=exc.message, output=handled_output))
    )


async def netdriver_errors_handler(request: Request, exc: BaseError):
    log.error(f"NetDriver error: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            CommonResponse.from_error(exc.code, msg=exc.message))
    )


async def default_exception_handler(request: Request, exc: Exception):
    log.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            CommonResponse.from_error(ErrorCode.SERVER_ERROR, msg=str(exc)))
    )


global_exception_handlers = {
    ValueError: value_error_handler,
    RequestValidationError: request_validation_error_handler,
    ExecError: exec_error_handler,
    BaseError: netdriver_errors_handler,
    Exception: default_exception_handler
}
