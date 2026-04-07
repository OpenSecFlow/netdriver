#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Import all vendor base classes to trigger IPluginRegistry registration
from netdriver_agent.plugins.arista.arista import AristaBase
from netdriver_agent.plugins.array.array import ArrayBase
from netdriver_agent.plugins.chaitin.chaitin import ChaiTinBase
from netdriver_agent.plugins.check_point.check_point import CheckPointBase
from netdriver_agent.plugins.cisco.cisco import CiscoBase
from netdriver_agent.plugins.dptech.dptech import DptechBase
from netdriver_agent.plugins.fortinet.fortinet import FortinetBase
from netdriver_agent.plugins.h3c.h3c import H3CBase
from netdriver_agent.plugins.hillstone.hillstone import HillstoneBase
from netdriver_agent.plugins.huawei.huawei import HuaweiBase
from netdriver_agent.plugins.juniper.juniper import JuniperBase
from netdriver_agent.plugins.leadsec.leadsec import LeadsecBase
from netdriver_agent.plugins.maipu.maipu import MaiPuBase
from netdriver_agent.plugins.paloalto.paloalto import PaloaltoBase
from netdriver_agent.plugins.qianxin.qianxin import QiAnXinBase
from netdriver_agent.plugins.topsec.topsec import TopSecBase
from netdriver_agent.plugins.venustech.venustech import VenustechBase

__all__ = [
    "AristaBase", "ArrayBase", "ChaiTinBase", "CheckPointBase",
    "CiscoBase", "DptechBase", "FortinetBase", "H3CBase",
    "HillstoneBase", "HuaweiBase", "JuniperBase", "LeadsecBase",
    "MaiPuBase", "PaloaltoBase", "QiAnXinBase", "TopSecBase",
    "VenustechBase",
]
