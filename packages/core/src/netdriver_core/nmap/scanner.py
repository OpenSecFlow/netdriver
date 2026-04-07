#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nmap scanner for network host discovery and port scanning."""

import asyncio
import os
import shutil

import nmap

from netdriver_core.exception.errors import DiscoveryNmapNotFound, DiscoveryScanFailed
from netdriver_core.log import logman
from netdriver_core.nmap.models import HostInfo, ScanResult

log = logman.logger

# Default ports to scan: SSH (22/TCP) and SNMP (161/UDP)
DEFAULT_SSH_PORTS = [22]
DEFAULT_SNMP_PORTS = [161]


class NmapScanner:
    """Wraps python-nmap to provide async host discovery and port scanning."""

    def __init__(self, nmap_path: str = "nmap"):
        self._nmap_path = nmap_path
        self._verify_nmap()

    def _verify_nmap(self) -> None:
        """Verify that nmap binary is available."""
        path = shutil.which(self._nmap_path)
        if path is None:
            raise DiscoveryNmapNotFound(
                f"Nmap binary not found at '{self._nmap_path}'. "
                "Please install nmap: brew install nmap (macOS) / apt install nmap (Linux)."
            )
        self._nmap_path = path

    async def scan(
        self,
        targets: list[str],
        ssh_ports: list[int] | None = None,
        snmp_ports: list[int] | None = None,
    ) -> list[ScanResult]:
        """Scan target ports directly and return reachable hosts.

        Args:
            targets: List of CIDR or IP ranges (e.g. ["192.168.1.0/24", "10.0.0.1-10"]).
            ssh_ports: TCP ports to scan for SSH. Defaults to [22].
            snmp_ports: UDP ports to scan for SNMP. Defaults to [161].

        Returns:
            List of ScanResult for hosts with at least one target port open.
        """
        resolved_ssh_ports = ssh_ports if ssh_ports is not None else DEFAULT_SSH_PORTS
        resolved_snmp_ports = snmp_ports if snmp_ports is not None else DEFAULT_SNMP_PORTS

        log.info(
            "Starting direct port scan for "
            f"{len(targets)} target(s), ssh_ports={resolved_ssh_ports}, "
            f"snmp_ports={resolved_snmp_ports}"
        )
        return await self.scan_ports(
            targets,
            ssh_ports=resolved_ssh_ports,
            snmp_ports=resolved_snmp_ports,
        )

    async def scan_ports(
        self,
        hosts: list[str],
        ssh_ports: list[int] | None = None,
        snmp_ports: list[int] | None = None,
    ) -> list[ScanResult]:
        """Port scan on specific targets.

        Args:
            hosts: List of IPs, CIDRs, or IP ranges to scan.
            ssh_ports: TCP ports to scan for SSH. Defaults to [22].
            snmp_ports: UDP ports to scan for SNMP. Defaults to [161].

        Returns:
            List of ScanResult with at least one open target port.
        """
        resolved_ssh_ports = self._normalize_ports(
            ssh_ports if ssh_ports is not None else DEFAULT_SSH_PORTS
        )
        resolved_snmp_ports = self._normalize_ports(
            snmp_ports if snmp_ports is not None else DEFAULT_SNMP_PORTS
        )
        if not resolved_ssh_ports and not resolved_snmp_ports:
            raise ValueError("at least one SSH or SNMP port must be configured")

        target_str = " ".join(hosts)
        log.info(
            f"Starting port scan on {len(hosts)} target(s), "
            f"ssh_ports={resolved_ssh_ports}, snmp_ports={resolved_snmp_ports}"
        )

        try:
            result = await asyncio.to_thread(
                self._run_port_scan,
                target_str,
                resolved_ssh_ports,
                resolved_snmp_ports,
            )
        except Exception as e:
            raise DiscoveryScanFailed(f"Port scan failed: {e}") from e

        results = []
        for ip, data in result.items():
            if not isinstance(data, dict):
                continue

            scan_result = ScanResult(ip=ip)

            # Extract port status
            tcp_ports = data.get("tcp", {})
            for port_num, port_data in tcp_ports.items():
                port_int = int(port_num)
                if (
                    port_data.get("state") == "open"
                    and port_int in resolved_ssh_ports
                ):
                    scan_result.open_ports.append(port_int)
                    scan_result.ssh_ports.append(port_int)
                    scan_result.has_ssh = True

            udp_ports = data.get("udp", {})
            for port_num, port_data in udp_ports.items():
                port_int = int(port_num)
                if (
                    port_data.get("state") in ("open", "open|filtered")
                    and port_int in resolved_snmp_ports
                ):
                    if port_int not in scan_result.open_ports:
                        scan_result.open_ports.append(port_int)
                    scan_result.snmp_ports.append(port_int)
                    scan_result.has_snmp = True

            if scan_result.open_ports:
                results.append(scan_result)

        log.info(f"Port scan complete: {len(results)} reachable host(s) found")
        return results

    @staticmethod
    def _normalize_ports(ports: list[int]) -> list[int]:
        """Deduplicate ports while preserving order."""
        normalized_ports: list[int] = []
        for port in ports:
            if port not in normalized_ports:
                normalized_ports.append(port)
        return normalized_ports

    @staticmethod
    def _build_port_spec(ssh_ports: list[int], snmp_ports: list[int]) -> str:
        """Build nmap protocol-aware port specification."""
        port_groups: list[str] = []
        if ssh_ports:
            port_groups.append(f"T:{','.join(str(port) for port in ssh_ports)}")
        if snmp_ports:
            port_groups.append(f"U:{','.join(str(port) for port in snmp_ports)}")
        return ",".join(port_groups)

    @staticmethod
    def _build_scan_types(ssh_ports: list[int], snmp_ports: list[int]) -> str:
        """Build nmap scan-type arguments for configured protocols."""
        scan_types: list[str] = []
        if ssh_ports:
            tcp_scan_type = "-sS"
            geteuid = getattr(os, "geteuid", None)
            if callable(geteuid) and geteuid() != 0:
                tcp_scan_type = "-sT"
            scan_types.append(tcp_scan_type)
        if snmp_ports:
            scan_types.append("-sU")
        return " ".join(scan_types)

    def _run_port_scan(
        self,
        target: str,
        ssh_ports: list[int],
        snmp_ports: list[int],
    ) -> dict:
        """Synchronous nmap port scan."""
        nm = nmap.PortScanner(nmap_search_path=(self._nmap_path,))
        port_spec = self._build_port_spec(ssh_ports, snmp_ports)
        scan_types = self._build_scan_types(ssh_ports, snmp_ports)
        arguments = (
            f"{scan_types} -sV --version-intensity 0 -T4 "
            f"-p {port_spec} --max-retries 2 --host-timeout 30s"
        )
        nm.scan(hosts=target, arguments=arguments)
        return {host: nm[host] for host in nm.all_hosts()}
