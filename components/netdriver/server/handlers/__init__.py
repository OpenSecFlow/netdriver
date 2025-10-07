#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
from asyncssh import SSHServerProcess

from netdriver.server.handlers.array.array_ag import ArrayAGHandler
from netdriver.server.handlers.chaitin.chaitin_ctdsg import ChaiTinCTDSGHandler
from netdriver.server.handlers.cisco.cisco_asa import CiscoASAHandler
from netdriver.server.handlers.cisco.cisco_nexus import CiscoNexusHandler
from netdriver.server.handlers.command_handler import CommandHandler
from netdriver.server.handlers.dptech.dptech_fw1000 import DptechFW1000Handler
from netdriver.server.handlers.huawei.huawei_usg import HuaweiUSGHandler
from netdriver.server.handlers.hillstone.hillstone_sg6000 import HillstoneSG6000Handler
from netdriver.server.handlers.h3c.h3c_secpath import H3CSecPathHandler
from netdriver.server.handlers.h3c.h3c_vsr import H3CVsrHandler
from netdriver.server.handlers.juniper.juniper_srx import JuniperSRXHandler
from netdriver.server.handlers.juniper.juniper_ex import JuniperEXHandler
from netdriver.server.handlers.maipu.maipu_nss import MaiPuNSSHandler
from netdriver.server.handlers.qianxin.qianxin_nsg import QiAnXinNSGHandler
from netdriver.server.handlers.topsec.topsec_ngfw import TopSecNGFWHandler
from netdriver.server.handlers.venustech.venustech_usg import VenustechUSGHandler
class CommandHandlerFactory:

    @staticmethod
    def create_handler(process: SSHServerProcess,
                             vendor: str,
                             model: str,
                             version: str,
                             conf_path: str = None) -> CommandHandler:
        if CiscoNexusHandler.is_selectable(vendor, model, version):
            return CiscoNexusHandler(process, conf_path)
        elif ArrayAGHandler.is_selectable(vendor, model, version):
            return ArrayAGHandler(process, conf_path)
        elif HuaweiUSGHandler.is_selectable(vendor, model, version):
            return HuaweiUSGHandler(process, conf_path)
        elif HillstoneSG6000Handler.is_selectable(vendor, model, version):
            return HillstoneSG6000Handler(process, conf_path)
        elif CiscoASAHandler.is_selectable(vendor, model, version):
            return CiscoASAHandler(process, conf_path)
        elif H3CSecPathHandler.is_selectable(vendor, model, version):
            return H3CSecPathHandler(process, conf_path)
        elif H3CVsrHandler.is_selectable(vendor, model, version):
            return H3CVsrHandler(process, conf_path)
        elif DptechFW1000Handler.is_selectable(vendor, model, version):
            return DptechFW1000Handler(process, conf_path)
        elif JuniperSRXHandler.is_selectable(vendor, model, version):
            return JuniperSRXHandler(process, conf_path)
        elif JuniperEXHandler.is_selectable(vendor, model, version):
            return JuniperEXHandler(process, conf_path)
        elif MaiPuNSSHandler.is_selectable(vendor, model, version):
            return MaiPuNSSHandler(process, conf_path)
        elif QiAnXinNSGHandler.is_selectable(vendor, model, version):
            return QiAnXinNSGHandler(process, conf_path)
        elif VenustechUSGHandler.is_selectable(vendor, model, version):
            return VenustechUSGHandler(process, conf_path)
        elif ChaiTinCTDSGHandler.is_selectable(vendor, model, version):
            return ChaiTinCTDSGHandler(process, conf_path)
        elif TopSecNGFWHandler.is_selectable(vendor, model, version):
            return TopSecNGFWHandler(process, conf_path)
        else:
            raise ValueError(f"Unsupported device: {vendor}:{model}:{version}")
