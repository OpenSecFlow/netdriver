#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from typing import Self
from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field, IPvAnyAddress, field_validator, model_validator


_VENDOR_MODELS = {
    "array": ["ag"],
    "cisco": ["nexus", "isr.*", "asr.*", "catalyst", "asa"],
    "huawei": ["usg.*", "ce.*"],
    "h3c": ["secpath", "vsr.*"],
    "hillstone": ["sg.*"],
    "juniper": ["ex.*", "qfx.*", "mx.*", "srx.*"],
    "paloalto": ["pa.*"],
    "fortinet": ["fortigate.*"],
    "arista": ["eos.*"],
    "check point": ["security gateway"],
    "dptech": ["fw.*"],
    "maipu": ["nss.*"],
    "qianxin": ["nsg.*"],
    "venustech": ["usg.*"],
    "chaitin": ["ctdsg.*"],
    "topsec": ["ngfw.*"]
}
_VENDOR_PATTERNS = "|".join(_VENDOR_MODELS.keys())
_models = set()
for models in _VENDOR_MODELS.values():
    for model in models:
        _models.add(model)
_MODEL_PATTERNS = "|".join(_models)


class CommonResponse(BaseModel):
    """ Common Response Model """

    code: str = Field(description="Status Code. 'OK' or error code.", examples=["OK"])
    msg: str = Field("", description="Detail message about the error code.", examples=[""])

    @classmethod
    def from_error(cls, code: str, msg: str = "", cor_id: str = None) -> "CommonResponse":
        """ Create a CommonResponse object with error """
        _cor_id = cor_id if cor_id else correlation_id.get()
        return cls(code=code, msg=msg, correlation_id=_cor_id)

    @classmethod
    def ok(cls, msg: str = "", cor_id: str = None) -> "CommonResponse":
        """ Create a CommonResponse object with ok """
        _cor_id = cor_id if cor_id else correlation_id.get()
        return cls(code="OK", msg=msg, correlation_id=_cor_id)


class CommonRequest(BaseModel):
    """ Common Request Model """

    protocol: str = Field(
        "ssh", description="Protocol", pattern="ssh|telnet", examples=["ssh"])
    ip: IPvAnyAddress = Field(
        description="Device IP, support IPv4 and IPv6.", examples=["192.168.60.198", "a::1"])
    port: int = Field(22, description="Port", examples=[22], ge=1, le=65535)
    username: str = Field(..., description="Username", examples=["admin"])
    password: str = Field(..., description="Password, support encrypted and plaintext.",
                          examples=["r00tme"])
    enable_password: str = Field(
        None, description="Enable password, For cisco, arista...", examples=[""])
    vendor: str = Field(description="Vendor", examples=["cisco"], pattern=_VENDOR_PATTERNS)
    model: str = Field(description="Model", examples=["asa"], pattern=_MODEL_PATTERNS)
    version: str = Field(description="Version", examples=["9.8"])
    encode: str = Field(
        "utf-8", description="The device encode. GB2312, GBK, GB18030 all use GB18030",
        examples=["utf-8"], pattern="utf-8|gb18030")
    vsys: str = Field(
        "default",
        description="Name of logical system, such as Fortinet vdom, Huawei vsys.",
        examples=["default"])
    timeout: int = Field(60, description="Timeout, unit: second.", examples=[60])

    def session_key(self) -> str:
        return f"{self.protocol}//{self.username}@{self.ip}:{self.port}"

    @model_validator(mode="after")
    def check_vendor_model(self) -> Self:
        for pattern in _VENDOR_MODELS.get(self.vendor, []):
            if re.match(pattern, self.model):
                return self
        raise ValueError(f"unsupported model {self.model} for vendor {self.vendor}.")
