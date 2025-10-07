#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from netdriver.utils import files


@pytest.mark.skip
@pytest.mark.asyncio
async def test_load_runconf_templates():
    templates = await files.load_templates(
        directory="components/netdriver/plugins/cisco/cisco_asa", prefix="runconf")
    assert templates
