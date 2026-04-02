#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter
from netdriver_agent.api.rest import v1
from netdriver_agent.api.rest.v1 import router as _router


router = APIRouter(prefix="/api")
router.include_router(_router)
