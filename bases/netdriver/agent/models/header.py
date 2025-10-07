#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field


class CommonHeaders(BaseModel):
    """ Common headers """
    x_correlation_id: str = Field(
        "",
        alias="X-Correlation-Id",
        description="Passed by upstream caller to track the call chain. If empty, " \
            "it will be automatically generated."
    )
