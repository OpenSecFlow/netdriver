#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, model_validator

from netdriver.client.mode import Mode


@dataclass
class DeviceBaseInfo:
    """ Device base Info """
    vendor: str
    model: str
    version: str
    description: str


class CmdOutput(BaseModel):
    """ Command Output """
    cmd: str
    output: str


class ModeConfig(BaseModel):
    """ Mode Configuration """
    prompt: str
    switch_mode_cmds: List[str]
    cmds: List[CmdOutput]
    cmd_map: Dict[str, str] = {}

    @model_validator(mode="after")
    def gen_cmd_map(self):
        for cmd in self.cmds:
            self.cmd_map[cmd.cmd] = cmd.output
        return self


class DeviceConfig(BaseModel):
    """ Device Configuration """
    start_mode: Mode
    hostname: str
    line_feed: str
    enable_password: str = ""
    modes: Dict[Mode, ModeConfig]
    common: List[CmdOutput]
    welcome: str
    invalid_cmd_error: str
    vendor_options: Dict[str, str] = {}
    common_cmd_map: Dict[str, str] = {}

    @model_validator(mode="after")
    def gen_common_cmd_map(self):
        for cmd in self.common:
            self.common_cmd_map[cmd.cmd] = cmd.output
        return self
