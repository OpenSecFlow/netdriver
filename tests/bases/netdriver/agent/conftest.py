#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from netdriver.agent.main import app
from netdriver.log import logman


_ARG_MOCK_DEV = "--mock-dev"

# Configure simunet log for test environment
# This needs to be called after agent.main import to add simunet log handler
# Also need to update agent handler to exclude server logs
from netdriver.log import logman as logman_module

# Remove the default agent handler and re-add with exclude filter
if logman_module._logger_initialized:
    # Get current config from agent container
    from netdriver.agent.containers import container as agent_container

    # Remove existing handlers
    logman.logger.remove()
    logman_module._logger_initialized = False

    # Re-add agent handler with exclude filter
    logman.configure_logman(
        level=agent_container.config.logging.level(),
        intercept_loggers=agent_container.config.logging.intercept_loggers(),
        log_file=agent_container.config.logging.log_file(),
        exclude_filter="netdriver.server"
    )

    # Add simunet handler
    logman.configure_logman(
        level="INFO",
        log_file="logs/simunet.log",
        module_filter="netdriver.server"
    )


@pytest.fixture(scope="session")
def simunet_process(request: pytest.FixtureRequest):
    """
    Session-scoped fixture that starts simunet process for all integration tests.
    The process is started once at the beginning and stopped after all tests complete.
    """
    mock_dev = request.config.getoption(_ARG_MOCK_DEV, default=False)

    if not mock_dev:
        # Real device mode, no simunet needed
        yield None
        return

    # Start simunet process using uvicorn directly
    logman.logger.info("Starting simunet process for integration tests...")
    process = subprocess.Popen(
        ["poetry", "run", "simunet"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for simunet to start up (give it some time to initialize all SSH servers)
    logman.logger.info("Waiting for simunet to start up...")
    time.sleep(5)

    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        logman.logger.error(f"Simunet failed to start. stdout: {stdout}, stderr: {stderr}")
        raise RuntimeError("Failed to start simunet process")

    logman.logger.info("Simunet process started successfully")
    yield process

    # Cleanup: terminate simunet process
    logman.logger.info("Stopping simunet process...")
    process.terminate()
    try:
        process.wait(timeout=10)
        logman.logger.info("Simunet process stopped successfully")
    except subprocess.TimeoutExpired:
        logman.logger.warning("Simunet process did not terminate gracefully, killing...")
        process.kill()
        process.wait()


@pytest.fixture(scope="module")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app=app) as client:
        yield client



@pytest.fixture(scope="module")
def cisco_nexus_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18020,
            "username": "admin",
            "password": "Cisco@123",
            "enable_password": "",
        }



@pytest.fixture(scope="module")
def array_ag_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18021,
            "username": "array",
            "password": "admin",
            "enable_password": "",
        }


@pytest.fixture(scope="module")
def huawei_usg_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18022,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def hillstone_SG6000_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18023,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def h3c_secpath_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18025,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def juniper_ex_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18029,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def paloalto_pa_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18036,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def fortinet_fortigate_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18037,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def cisco_asa_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18024,
            "username": "admin",
            "password": "r00tme",
            "enable_password": "",
        }


@pytest.fixture(scope="module")
def juniper_srx_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18028,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def huawei_ce_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18038,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def arista_eos_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18039,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def check_point_security_gateway_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18040,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }


@pytest.fixture(scope="module")
def h3c_vsr_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18026,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def dptech_fw_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18027,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def maipu_nss_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18030,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def qianxin_nsg_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18031,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def venustech_usg_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18032,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def chaitin_ctdsg_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18033,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }

@pytest.fixture(scope="module")
def topsec_ngfw_dev(request: pytest.FixtureRequest, simunet_process) -> Generator[dict, None, None]:
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
        yield {
            "protocol": "ssh",
            "ip": "127.0.0.1",
            "port": 18034,
            "username": "admin",
            "password": "Admin@1234567",
            "enable_password": "",
        }