#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from netdriver_core.utils import files


@pytest.mark.skip
@pytest.mark.asyncio
async def test_load_runconf_templates():
    templates = await files.load_templates(
        directory="packages/agent/src/netdriver_agent/plugins/cisco", prefix="runconf")
    assert templates
