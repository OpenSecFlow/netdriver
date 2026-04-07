#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi.routing import APIRouter
from netdriver_agent.api.rest.v1 import api  # noqa: F401
from netdriver_agent.api.rest.v1 import discovery  # noqa: F401
from netdriver_agent.api.rest.v1.api import router as cmd_router
from netdriver_agent.api.rest.v1.discovery import router as discovery_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(cmd_router)
router.include_router(discovery_router)
