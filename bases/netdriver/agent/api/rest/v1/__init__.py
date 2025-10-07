#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi.routing import APIRouter
from netdriver.agent.api.rest.v1.api import router as cmd_router

router = APIRouter(prefix='/v1', tags=['v1'])
router.include_router(cmd_router)
