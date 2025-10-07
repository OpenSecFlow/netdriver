#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import threading
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from netdriver.agent.main import app
from netdriver.server.device import MockSSHDevice


_ARG_MOCK_DEV = "--mock-dev"


@pytest.fixture(scope="module")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app=app) as client:
        yield client


class AsyncRunner:
    """ Run async function in a separate thread """

    def __init__(self, dev):
        self.dev = dev
        self.loop = None

    def __call__(self, *args, **kwargs):
        self.loop = asyncio.new_event_loop()
        self.loop.create_task(self.dev.start())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.dev.stop()



@pytest.fixture(scope="module")
def cisco_nexus_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.132",
            "port": 22,
            "username": "admin",
            "password": "Juniper@123",
            "enable_password": "",
        }
    else:
        port = 18020
        dev = MockSSHDevice.create_device(vendor="cisco", model="nexus", version="xyz", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Cisco@123",
            "enable_password": "",
        }
        runner.stop()



@pytest.fixture(scope="module")
def array_ag_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.170",
            "port": 22,
            "username": "array",
            "password": "admin",
            "enable_password": "123456",
        }
    else:
        port = 18021
        dev = MockSSHDevice.create_device(vendor="array", model="ag", version="xyz", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "array",
            "password": "admin",
            "enable_password": "",
        }
        runner.stop()


@pytest.fixture(scope="module")
def huawei_usg_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.84",
            "port": 22,
            "username": "admin",
            "password": "Admin@12345",
            "enable_password": "",
        }
    else:
        port = 18022
        dev = MockSSHDevice.create_device(vendor="huawei", model="usg", version="xyz", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def hillstone_SG6000_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.123",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18023
        dev = MockSSHDevice.create_device(vendor="hillstone", model="sg6000", version="5.5", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def h3c_secpath_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.33",
            "port": 22,
            "username": "admin",
            "password": "h3c@123456",
            "enable_password": "",
        }
    else:
        port = 18024
        dev = MockSSHDevice.create_device(vendor="h3c", model="secpath", version="7.1", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def juniper_ex_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.135",
            "port": 22,
            "username": "admin",
            "password": "Juniper@123",
            "enable_password": "",
        }
    else:
        port = 18025
        dev = MockSSHDevice.create_device(vendor="juniper", model="ex4200", version="junos 15", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def paloalto_pa_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.66",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18026
        dev = MockSSHDevice.create_device(vendor="paloalto", model="pa", version="8.1", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def fortinet_fortigate_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.88",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18027
        dev = MockSSHDevice.create_device(vendor="fortinet", model="fortigate", version="7.2", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def cisco_asa_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.198",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "r00tme"
        }
    else:
        port = 18024
        dev = MockSSHDevice.create_device(vendor="cisco", model="asa", version="9.6.0", port=port)
        runner = AsyncRunner(dev)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
        runner.stop()


@pytest.fixture(scope="module")
def juniper_srx_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.68",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18028
        dev = MockSSHDevice.create_device(vendor="juniper", model="srx", version="junos 12.0", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def huawei_ce_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.122",
            "port": 22,
            "username": "huawei",
            "password": "Ce@123456",
            "enable_password": "",
        }
    else:
        port = 18029
        dev = MockSSHDevice.create_device(vendor="huawei", model="ce6800", version="8.18", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def arista_eos_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.92",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "12345",
        }
    else:
        port = 18030
        dev = MockSSHDevice.create_device(vendor="arista", model="eos-lab", version="4.31.2F", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def check_point_security_gateway_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.140",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18031
        dev = MockSSHDevice.create_device(vendor="check point", model="Gaia", version="R80.40", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()


@pytest.fixture(scope="module")
def h3c_vsr_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.33",
            "port": 22,
            "username": "admin",
            "password": "h3c@123456",
            "enable_password": "",
        }
    else:
        port = 18032
        dev = MockSSHDevice.create_device(vendor="h3c", model="vsr", version="7.1", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def dptech_fw_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "192.168.60.92",
            "port": 22,
            "username": "admin",
            "password": "root@r00tme",
            "enable_password": "",
        }
    else:
        port = 18033
        dev = MockSSHDevice.create_device(vendor="dptech", model="fw1000", version="S511C013D001", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def maipu_nss_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.5.199",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18034
        dev = MockSSHDevice.create_device(vendor="maipu", model="nss", version="9.7.40.8", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def qianxin_nsg_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.177",
            "port": 22,
            "username": "admin",
            "password": "Lablab@123",
            "enable_password": "",
        }
    else:
        port = 18035
        dev = MockSSHDevice.create_device(vendor="qianxin", model="nsg", version="6.1.13", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def venustech_usg_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.1.133",
            "port": 22,
            "username": "admin",
            "password": "byntra@123",
            "enable_password": "",
        }
    else:
        port = 18036
        dev = MockSSHDevice.create_device(vendor="venustech", model="usg", version="v2.6", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def chaitin_ctdsg_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "1172.21.6.101",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18037
        dev = MockSSHDevice.create_device(vendor="chaitin", model="ctdsg", version="v3.0", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()

@pytest.fixture(scope="module")
def topsec_ngfw_dev(request: pytest.FixtureRequest) -> Generator[dict, None, None]:
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)
    if not mock_dev:
        yield {
            "protocol": "ssh",
            "ip": "172.21.6.208",
            "port": 22,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }
    else:
        port = 18038
        dev = MockSSHDevice.create_device(vendor="topsec", model="ngfw", version="v3", port=port)
        runner = AsyncRunner(dev.start)
        thread = threading.Thread(target=runner)
        thread.daemon = True
        thread.start()
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": port,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }
        runner.stop()