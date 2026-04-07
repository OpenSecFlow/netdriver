#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discovery worker process entrypoint and runtime."""

from __future__ import annotations

import asyncio
import importlib
import json
import signal
import sys
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass
from typing import TypeVar

from netdriver_core.log import logman
from netdriver_core.nmap.models import ScanResult
from netdriver_core.nmap.scanner import NmapScanner
from netdriver_core.snmp.client import SNMP_OIDS, SnmpClient
from netdriver_core.snmp.models import SnmpCredential

from netdriver_agent.discovery.engine.models import DiscoveredDevice, TaskStatus
from netdriver_agent.discovery.engine.task_store import TaskStore
from netdriver_agent.discovery.oid.vendor_oid_map import get_vendor_snmp_detail_oids
from netdriver_agent.discovery.probe.base_ssh_probe import SshProbe
from netdriver_agent.discovery.probe.identifier import DeviceIdentifier
from netdriver_agent.discovery.probe.models import DeviceProfile, SnmpProbeResult, SshCredential

log = logman.logger
ProbeCredential = TypeVar("ProbeCredential", SnmpCredential, SshCredential)


@dataclass(slots=True)
class DiscoveryWorkerPayload:
    """Serializable worker payload for a discovery task."""

    task_id: str
    db_path: str
    nmap_path: str
    targets: list[str]
    ssh_ports: list[int]
    snmp_ports: list[int]
    ssh_credentials: list[dict[str, str]]
    snmp_credentials: list[dict[str, str | None]]
    max_concurrent_probes: int
    probe_timeout: float
    ssh_connect_timeout: float
    ssh_read_timeout: float
    snmp_timeout: float
    snmp_retries: int
    plugin_modules: list[str]

    def to_json(self) -> str:
        """Serialize the worker payload to JSON."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, payload: str) -> "DiscoveryWorkerPayload":
        """Deserialize a worker payload from JSON."""
        return cls(**json.loads(payload))


class DiscoveryTaskWorker:
    """Runs the discovery pipeline inside a dedicated subprocess."""

    def __init__(
        self,
        task_store: TaskStore,
        nmap_path: str = "nmap",
        max_concurrent_probes: int = 50,
        probe_timeout: float = 30.0,
        ssh_connect_timeout: float = 10.0,
        ssh_read_timeout: float = 5.0,
        snmp_timeout: float = 5.0,
        snmp_retries: int = 1,
        plugin_modules: list[str] | None = None,
    ) -> None:
        self._task_store = task_store
        self._nmap_scanner = NmapScanner(nmap_path=nmap_path)
        self._snmp_client = SnmpClient(timeout=snmp_timeout, retries=snmp_retries)
        self._identifier: DeviceIdentifier | None = None
        self._max_concurrent = max_concurrent_probes
        self._probe_timeout = probe_timeout
        self._ssh_connect_timeout = ssh_connect_timeout
        self._ssh_read_timeout = ssh_read_timeout
        self._plugin_modules = plugin_modules or []

        self._load_vendor_probes()

    def _load_vendor_probes(self) -> None:
        """Import plugin modules to trigger IPluginRegistry registration."""
        for module_path in self._plugin_modules:
            try:
                importlib.import_module(module_path)
            except ImportError as exc:
                log.warning(f"Failed to load plugin module {module_path}: {exc}")

    def _get_identifier(self) -> DeviceIdentifier:
        """Lazy-init DeviceIdentifier."""
        if self._identifier is None:
            self._identifier = DeviceIdentifier()
        return self._identifier

    async def _probe_with_credentials(
        self,
        host: str,
        port: int,
        credentials: list[ProbeCredential],
        identifier: DeviceIdentifier,
        probe_name: str,
        format_credential_label: Callable[[ProbeCredential], str],
        probe_func: Callable[
            ...,
            Awaitable[dict[str, str] | None],
        ],
        probe_kwargs: Mapping[str, object] | None = None,
    ) -> dict[str, str] | None:
        """Probe a host with credentials sequentially and continue after single timeouts."""
        resolved_probe_kwargs = dict(probe_kwargs or {})
        for credential in credentials:
            try:
                result = await asyncio.wait_for(
                    probe_func(
                        host,
                        port,
                        [credential],
                        identifier,
                        **resolved_probe_kwargs,
                    ),
                    timeout=self._probe_timeout,
                )
            except asyncio.TimeoutError:
                log.debug(
                    f"{probe_name} probe timeout for {host}:{port} "
                    f"with {format_credential_label(credential)}"
                )
                continue

            if result:
                return result

        return None

    async def run(
        self,
        task_id: str,
        targets: list[str],
        ssh_ports: list[int],
        snmp_ports: list[int],
        ssh_credentials: list[SshCredential],
        snmp_credentials: list[SnmpCredential],
    ) -> None:
        """Execute the full discovery pipeline."""
        try:
            await self._task_store.set_status(task_id, TaskStatus.RUNNING)
            log.info(f"Discovery task {task_id}: starting scan for targets {targets}")

            scan_results = await self._nmap_scanner.scan(
                targets,
                ssh_ports=ssh_ports,
                snmp_ports=snmp_ports,
            )
            total = len(scan_results)
            await self._task_store.update_progress(task_id, 0, total)
 
            log.info(f"Discovery task {task_id}: scan found {total} host(s)")

            if total == 0:
                await self._task_store.set_status(task_id, TaskStatus.COMPLETED)
                return

            semaphore = asyncio.Semaphore(self._max_concurrent)
            completed = 0

            async def probe_host(scan_result: ScanResult) -> None:
                nonlocal completed
                async with semaphore:
                    try:
                        await self._probe_and_store(
                            task_id=task_id,
                            scan_result=scan_result,
                            ssh_credentials=ssh_credentials,
                            snmp_credentials=snmp_credentials,
                        )
                    except asyncio.CancelledError:
                        raise
                    except (OSError, RuntimeError, ValueError) as exc:
                        log.warning(
                            f"Discovery task {task_id}: probe failed for {scan_result.ip}: {exc}"
                        )
                    finally:
                        completed += 1
                        await self._task_store.update_progress(task_id, completed, total)

            await asyncio.gather(
                *(probe_host(scan_result) for scan_result in scan_results),
                return_exceptions=False,
            )

            await self._task_store.set_status(task_id, TaskStatus.COMPLETED)
            log.info(f"Discovery task {task_id}: completed")
        except asyncio.CancelledError:
            log.info(f"Discovery task {task_id}: cancelled")
            await self._task_store.set_status(task_id, TaskStatus.CANCELLED)
            raise
        except (
            OSError,
            RuntimeError,
            ValueError,
        ) as exc:
            log.error(f"Discovery task {task_id}: failed: {exc}")
            await self._task_store.set_status(task_id, TaskStatus.FAILED, str(exc))

    async def _probe_and_store(
        self,
        task_id: str,
        scan_result: ScanResult,
        ssh_credentials: list[SshCredential],
        snmp_credentials: list[SnmpCredential],
    ) -> None:
        """Probe a single host and store result."""
        host = scan_result.ip
        identifier = self._get_identifier()
        device = DiscoveredDevice(ip=host)

        snmp_success = False
        if scan_result.has_snmp and snmp_credentials:
            for snmp_port in scan_result.snmp_ports:
                snmp_result = await self._probe_with_credentials(
                    host=host,
                    port=snmp_port,
                    credentials=snmp_credentials,
                    identifier=identifier,
                    probe_name="SNMP",
                    format_credential_label=self._format_snmp_credential_label,
                    probe_func=self._probe_snmp,
                )
                if snmp_result:
                    self._apply_snmp_result(device, snmp_result)
                    snmp_success = True
                    break


        if scan_result.has_ssh and ssh_credentials:
            for ssh_port in scan_result.ssh_ports:
                ssh_result = await self._probe_with_credentials(
                    host=host,
                    port=ssh_port,
                    credentials=ssh_credentials,
                    identifier=identifier,
                    probe_name="SSH",
                    format_credential_label=self._format_ssh_credential_label,
                    probe_func=self._probe_ssh,
                    probe_kwargs={
                        "selection_profile": DeviceProfile.from_mapping(
                            {
                                "vendor": device.vendor,
                                "model": device.model,
                                "version": device.version,
                            }
                        )
                    } if device.vendor else None,
                )
                if ssh_result:
                    self._apply_ssh_result(device, ssh_result, snmp_success=snmp_success)
                    break

        if device.vendor or device.method:
            await self._task_store.add_device(task_id, device)
            log.info(
                f"Discovered: {host} -> {device.vendor}/{device.model} "
                f"v{device.version} via {device.method}"
            )

    @staticmethod
    def _format_snmp_credential_label(credential: SnmpCredential) -> str:
        """Format a human-readable SNMP credential label for logs."""
        label = credential.community if credential.version == "v2c" else credential.username
        return f"credential '{label or '<unknown>'}'"

    @staticmethod
    def _format_ssh_credential_label(credential: SshCredential) -> str:
        """Format a human-readable SSH credential label for logs."""
        return f"user '{credential.username}'"

    @staticmethod
    def _apply_snmp_result(
        device: DiscoveredDevice,
        snmp_result: dict[str, str],
    ) -> None:
        """Apply a successful SNMP probe result to a discovered device."""
        device.vendor = snmp_result.get("vendor", "")
        device.model = snmp_result.get("model", "")
        device.version = snmp_result.get("version", "")
        device.hostname = snmp_result.get("hostname", "")
        device.serial_number = snmp_result.get("serial_number", "")
        device.snmp_community = snmp_result.get("community", "")
        device.method = "snmp"
        device.raw_data = snmp_result.get("raw_data", "")

    @staticmethod
    def _apply_ssh_result(
        device: DiscoveredDevice,
        ssh_result: dict[str, str],
        *,
        snmp_success: bool,
    ) -> None:
        """Apply a successful SSH probe result to a discovered device."""
        ssh_vendor = ssh_result.get("vendor", "")
        ssh_model = ssh_result.get("model", "")
        ssh_version = ssh_result.get("version", "")
        ssh_hostname = ssh_result.get("hostname", "")
        ssh_serial = ssh_result.get("serial_number", "")

        if not snmp_success:
            device.vendor = ssh_vendor
            device.model = ssh_model
            device.version = ssh_version
            device.hostname = ssh_hostname or device.hostname
            device.method = "ssh"
        else:
            device.method = "both"
            if not device.vendor and ssh_vendor:
                device.vendor = ssh_vendor
            elif ssh_vendor and DiscoveryTaskWorker._normalize_value(device.vendor) != DiscoveryTaskWorker._normalize_value(ssh_vendor):
                log.warning(
                    f"Discovery vendor mismatch for {device.ip}: SNMP={device.vendor!r}, SSH={ssh_vendor!r}"
                )

            if ssh_model:
                device.model = ssh_model
            if ssh_version:
                device.version = ssh_version
            if ssh_hostname:
                device.hostname = ssh_hostname

        device.ssh_username = ssh_result.get("username", "")
        if ssh_serial:
            device.serial_number = ssh_serial
        device.raw_data = DiscoveryTaskWorker._merge_raw_data(
            device.raw_data,
            ssh_result.get("raw_data", ""),
        )

    async def _probe_snmp(
        self,
        host: str,
        port: int,
        credentials: list[SnmpCredential],
        identifier: DeviceIdentifier,
    ) -> dict[str, str] | None:
        """Run SNMP probe and return parsed device info dict."""
        result = await self._probe_snmp_system_info(host, port, credentials)

        if not result.success:
            return None

        vendor = identifier.identify_by_oid(result.sys_object_id)
        model = ""
        version = ""

        if vendor and result.credential is not None:
            detail_oids = get_vendor_snmp_detail_oids(vendor)
            detail_data = await self._fetch_snmp_detail_data(
                host,
                port,
                result.credential,
                detail_oids,
            )
            model = self._extract_oid_values(detail_data, detail_oids.get("model"))
            version = self._extract_oid_values(detail_data, detail_oids.get("version"))
            serial_number = self._extract_oid_values(detail_data, detail_oids.get("serial_number"))
        else:
            serial_number = ""

        return {
            "vendor": vendor or "",
            "model": model,
            "version": version,
            "serial_number": serial_number,
            "hostname": result.sys_name,
            "community": result.community,
            "raw_data": result.sys_descr,
        }

    async def _probe_snmp_system_info(
        self,
        host: str,
        port: int,
        credentials: list[SnmpCredential],
    ) -> SnmpProbeResult:
        """Try SNMP credentials and fetch standard system OIDs."""
        oids = [
            SNMP_OIDS["sysDescr"],
            SNMP_OIDS["sysObjectID"],
            SNMP_OIDS["sysName"],
        ]

        for credential in credentials:
            label = credential.community if credential.version == "v2c" else credential.username
            log.debug(f"SNMP probe {host}: trying credential '{label}'")

            result = await self._snmp_client.get(host, credential, oids, port=port)
            if not result.success or not result.data:
                continue

            sys_descr = result.data.get(SNMP_OIDS["sysDescr"], "")
            sys_object_id = result.data.get(SNMP_OIDS["sysObjectID"], "")
            sys_name = result.data.get(SNMP_OIDS["sysName"], "")

            log.info(f"SNMP probe {host}: success with credential '{label}'")
            log.debug(f"SNMP probe {host}: sysObjectID={sys_object_id}, sysDescr={sys_descr}")

            return SnmpProbeResult(
                success=True,
                host=host,
                community=credential.community or "",
                credential=credential,
                sys_object_id=sys_object_id,
                sys_descr=sys_descr,
                sys_name=sys_name,
            )

        log.info(f"SNMP probe {host}: all credentials failed")
        return SnmpProbeResult(
            success=False,
            host=host,
            error="All SNMP credentials failed",
        )

    async def _fetch_snmp_detail_data(
        self,
        host: str,
        port: int,
        credential: SnmpCredential,
        detail_oids: dict[str, list[str]],
    ) -> dict[str, str]:
        """Fetch vendor model/version OIDs when configured."""
        oids: list[str] = []
        for oid_list in detail_oids.values():
            oids.extend(oid_list)
        if not oids:
            return {}

        result = await self._snmp_client.get(host, credential, oids, port=port)
        if not result.success or not result.data:
            return {}

        return result.data

    @staticmethod
    def _extract_oid_values(mib_data: dict[str, str], oids: list[str] | None) -> str:
        """Extract the first non-empty value from a list of OIDs."""
        if oids is None:
            return ""
        for oid in oids:
            value = mib_data.get(oid, "")
            if value:
                return value
        return ""

    async def _probe_ssh(
        self,
        host: str,
        port: int,
        credentials: list[SshCredential],
        identifier: DeviceIdentifier,
        *,
        selection_profile: DeviceProfile | None = None,
    ) -> dict[str, str] | None:
        """Run SSH probe and return parsed device info dict."""
        probe = SshProbe()
        result = await probe.probe(
            host,
            port,
            credentials,
            identifier,
            connect_timeout=self._ssh_connect_timeout,
            read_timeout=self._ssh_read_timeout,
            selection_profile=selection_profile,
        )

        if not result.success:
            return None

        return {
            "vendor": result.device_info.vendor if result.device_info else "",
            "model": result.device_info.model if result.device_info else "",
            "version": result.device_info.version if result.device_info else "",
            "hostname": result.device_info.hostname if result.device_info else "",
            "serial_number": result.device_info.serial_number if result.device_info else "",
            "username": result.credential.username if result.credential else "",
            "raw_data": result.raw_output,
        }

    @staticmethod
    def _normalize_value(value: str | None) -> str:
        """Normalize a string for comparisons."""
        return value.strip().lower() if value else ""

    @staticmethod
    def _looks_precise_model(model: str) -> bool:
        """Heuristic for distinguishing exact hardware models from generic families."""
        return any(char.isdigit() for char in model) or "-" in model or " " in model

    @staticmethod
    def _merge_raw_data(existing_raw_data: str, ssh_raw_data: str) -> str:
        """Merge SNMP and SSH raw output into a single text field."""
        if not existing_raw_data:
            return ssh_raw_data
        if not ssh_raw_data or existing_raw_data == ssh_raw_data:
            return existing_raw_data
        return f"[SNMP]\n{existing_raw_data}\n\n[SSH]\n{ssh_raw_data}"


async def _run_worker(payload: DiscoveryWorkerPayload) -> None:
    """Run a worker payload in an isolated task store connection."""
    task_store = TaskStore(db_path=payload.db_path)
    await task_store.init_db()

    try:
        worker = DiscoveryTaskWorker(
            task_store=task_store,
            nmap_path=payload.nmap_path,
            max_concurrent_probes=payload.max_concurrent_probes,
            probe_timeout=payload.probe_timeout,
            ssh_connect_timeout=payload.ssh_connect_timeout,
            ssh_read_timeout=payload.ssh_read_timeout,
            snmp_timeout=payload.snmp_timeout,
            snmp_retries=payload.snmp_retries,
            plugin_modules=payload.plugin_modules,
        )
        await worker.run(
            task_id=payload.task_id,
            targets=payload.targets,
            ssh_ports=payload.ssh_ports,
            snmp_ports=payload.snmp_ports,
            ssh_credentials=[
                SshCredential(**credential) for credential in payload.ssh_credentials
            ],
            snmp_credentials=[
                SnmpCredential(**{k: v for k, v in credential.items() if v is not None})
                for credential in payload.snmp_credentials
            ],
        )
    finally:
        await task_store.close()


def run_worker(payload: DiscoveryWorkerPayload) -> int:
    """Run the async worker with signal-aware cancellation."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(_run_worker(payload))

    def _handle_signal(_: int, __) -> None:
        if not task.done():
            task.cancel()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handle_signal)
        except ValueError:
            continue

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        return 0
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    return 0


def main() -> int:
    """CLI entrypoint for the discovery worker subprocess."""
    if len(sys.argv) != 2:
        log.error("Discovery worker expects exactly one JSON payload argument")
        return 1

    try:
        payload = DiscoveryWorkerPayload.from_json(sys.argv[1])
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        log.error(f"Failed to parse discovery worker payload: {exc}")
        return 1

    return run_worker(payload)


if __name__ == "__main__":
    raise SystemExit(main())
