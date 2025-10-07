#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from netdriver.agent.models.cmd import CommandRequest, CommandResponse, CommandRet
from netdriver.client.channel import ReadBuffer
from netdriver.client.pool import SessionPool
from netdriver.client.session import Session
from netdriver.client.task import CmdTaskResult
from netdriver.exception.error_code import ErrorCode
from netdriver.exception.errors import ExecError
from netdriver.textfsm import TextFSMParser
from netdriver import utils


class CommandRequestHandler:

    async def handle(self, command: CommandRequest) -> CommandResponse:
        """ Handle command request """
        if not command:
            raise ValueError("CommandRequest is empty")

        result: List[CommandRet] = []
        total_time: float = 0.0
        output = ReadBuffer()

        try:
            session: Session = await SessionPool().get_session(**vars(command))
            cmd_total: int = len(command.commands)
            cmd_exec_except: int = 0
            cmd_exec_success: int = 0
            for cmd in command.commands:
                task_ret: CmdTaskResult = await session.send_cmd(
                    cmd.command, command.vsys, cmd.mode, timeout=command.timeout, detail_output=cmd.detail_output)
                output.append(f"\n===== start exec cmd: [{cmd.command}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} =====\n")
                output.append(task_ret.output)
                output.append(f"\n===== end exec cmd: [{cmd.command}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} =====\n")
                # If catch_error is False, the error will be raised
                if task_ret.exception:
                    cmd_exec_except += 1
                    # if is ExecError, append output
                    if isinstance(task_ret.exception, ExecError):
                        result.append(CommandRet(ret_code=task_ret.exception.code, command=cmd.command,
                                                 ret=utils.terminal.simulate_output(task_ret.output)))
                        task_ret.exception.output = output.get_data()
                    if not command.continue_on_error or cmd_total < 2:
                        raise task_ret.exception
                else:
                    cmd_exec_success += 1
                    # raw
                    if cmd.type == "raw":
                        result.append(CommandRet(ret_code="OK", command=cmd.command,
                                                 ret=utils.terminal.simulate_output(task_ret.output)))
                    # textfsm
                    elif cmd.type == "textfsm":
                        parsed_objs = TextFSMParser(cmd.template).parse(task_ret.output)
                        result.append(CommandRet(ret_code="OK", command=cmd.command, ret=parsed_objs))
                    else:
                        raise ValueError(f"Unsupported command type: {cmd.type}")
                total_time += task_ret.get_total_time()

            handled_output = utils.terminal.simulate_output(output.get_data())
            if cmd_total > 1 and cmd_exec_except > 0 :
                msg = f"Batch exec: {cmd_exec_success}/{cmd_total} succeeded, {cmd_exec_except} failures!"
                return CommandResponse.from_error(code=ErrorCode.EXEC_CMD_PARTIAL_ERROR, msg=msg, output=handled_output,
                                                  result=result, time=total_time)
            return CommandResponse.ok(time=total_time, result=result, output=handled_output)
        except ExecError as exec:
            handled_output = utils.terminal.simulate_output(exec.output)
            return CommandResponse.from_error(
                code=exec.code, msg=exec.message, output=handled_output, result=result, time=total_time)
