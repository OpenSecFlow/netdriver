#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SSH probe for device identification using the plugin system."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import asyncssh
import re

from netdriver_agent.client.channel import ReadBuffer
from netdriver_core.log import logman
from netdriver_core.ssh.algorithms import DEFAULT_ENCRYPTION_ALGS, DEFAULT_KEX_ALGS

from netdriver_agent.discovery.probe.models import DeviceInfo, DeviceProfile, SshCredential, SshProbeResult

if TYPE_CHECKING:
    from netdriver_agent.discovery.probe.identifier import DeviceIdentifier

log = logman.logger


class SshProbe:
    """SSH probe that uses the plugin system for device identification."""

    _SSH_CONFIG = {
        "known_hosts": None,
        "kex_algs": DEFAULT_KEX_ALGS,
        "encryption_algs": DEFAULT_ENCRYPTION_ALGS,
    }

    async def probe(
        self,
        host: str,
        port: int,
        credentials: list[SshCredential],
        identifier: DeviceIdentifier,
        connect_timeout: float = 10.0,
        read_timeout: float = 5.0,
        selection_profile: DeviceProfile | None = None,
    ) -> SshProbeResult:
        """Full SSH probe using plugin-based identification."""

        resolved_profile = (selection_profile or DeviceProfile()).normalized()

        for credential in credentials:
            log.debug(
                f"SSH probe {host}:{port}: trying user '{credential.username}' "
                f"with profile {resolved_profile.vendor}/{resolved_profile.model}/{resolved_profile.version}"
            )

            try:
                conn = await asyncio.wait_for(
                    asyncssh.connect(
                        host,
                        port=port,
                        username=credential.username,
                        password=credential.password,
                        **self._SSH_CONFIG,
                    ),
                    timeout=connect_timeout,
                )
            except asyncio.TimeoutError:
                log.debug(
                    f"SSH probe {host}:{port}: connect timeout for user '{credential.username}'"
                )
                continue
            except (asyncssh.DisconnectError, asyncssh.PermissionDenied, OSError) as exc:
                log.debug(
                    f"SSH probe {host}:{port}: auth failed for user '{credential.username}': {exc}"
                )
                continue
            except Exception as exc:
                log.debug(
                    f"SSH probe {host}:{port}: unexpected error for user '{credential.username}': {exc}"
                )
                continue

            log.info(f"SSH probe {host}:{port}: connected as '{credential.username}'")

            try:
                return await self._identify_device(
                    conn,
                    host,
                    port,
                    credential,
                    identifier,
                    read_timeout,
                    selection_profile=resolved_profile,
                )
            except Exception as exc:
                log.warning(f"SSH probe {host}:{port}: identification failed: {exc}")
                return SshProbeResult(
                    success=True,
                    host=host,
                    port=port,
                    credential=credential,
                    error=f"Connected but identification failed: {exc}",
                )
            finally:
                conn.close()
                await conn.wait_closed()

        log.info(f"SSH probe {host}:{port}: all credentials failed")
        return SshProbeResult(
            success=False,
            host=host,
            port=port,
            error="All SSH credentials failed",
        )

    async def _identify_device(
        self,
        conn: asyncssh.SSHClientConnection,
        host: str,
        port: int,
        credential: SshCredential,
        identifier: "DeviceIdentifier",
        read_timeout: float,
        *,
        selection_profile: DeviceProfile,
    ) -> SshProbeResult:
        """Identify device type via prompt matching and plugin probe commands."""

        process = await conn.create_process(
            term_type="ansi",
            term_size=(1000, 100),
        )

        # Step 1: Read prompt
        prompt = ""
        welcome_output = ""
        try:
            prompt, welcome_output = await asyncio.wait_for(
                self._read_prompt(process),
                timeout=read_timeout,
            )
        except asyncio.TimeoutError:
            log.debug(f"SSH probe {host}:{port}: prompt read timeout, using partial output")

        # Step 2: Determine candidate plugins
        candidates: list[type] = []
        if selection_profile.vendor:
            plugin_cls = identifier.get_probe_plugin(
                selection_profile.vendor,
                selection_profile.model,
                selection_profile.version,
            )
            if plugin_cls:
                candidates.append(plugin_cls)
        else:
            matching_vendors = identifier.identify_by_prompt(prompt)
            for vendor in matching_vendors:
                plugin_cls = identifier.get_probe_plugin(vendor)
                if plugin_cls:
                    candidates.append(plugin_cls)

        # Step 3: Try each candidate plugin
        for plugin_cls in candidates:
            probe_cmd = plugin_cls.get_probe_command()
            probe_output = ""
            union_pattern = plugin_cls.PatternHelper.get_union_pattern()
            try:
                process.stdin.write(probe_cmd + "\n")
                probe_output = await asyncio.wait_for(
                    self._read_until_prompt(process, probe_cmd, union_pattern),
                    timeout=read_timeout,
                )
            except asyncio.TimeoutError:
                log.debug(f"SSH probe {host}:{port}: probe command timeout for {plugin_cls.__name__}")

            probe_result = plugin_cls.parse_probe_output(probe_output)
            if probe_result.vendor:
                device_info = DeviceInfo(
                    vendor=probe_result.vendor,
                    model=probe_result.model,
                    version=probe_result.version,
                    hostname=probe_result.hostname,
                    serial_number=probe_result.serial_number,
                )
                log.debug(
                    f"SSH probe {host}:{port}: identified by {plugin_cls.__name__} "
                    f"as {device_info.vendor}/{device_info.model}/{device_info.version}"
                )
                return SshProbeResult(
                    success=True,
                    host=host,
                    port=port,
                    credential=credential,
                    device_info=device_info,
                    raw_output=welcome_output + "\n" + probe_output,
                )

        return SshProbeResult(
            success=True,
            host=host,
            port=port,
            credential=credential,
            device_info=None,
            raw_output=welcome_output,
        )

    async def _read_until_prompt(self, process: asyncssh.SSHClientProcess, cmd: str, union_pattern: re.Pattern) -> str:
        """Read from process stdout until no more data arrives."""
        output = ReadBuffer(cmd)
        while process.stdout and not process.stdout.at_eof():
            chunk = await asyncio.wait_for(
                process.stdout.read(4096),
                timeout=2.0,
            )
            output.append(chunk)
            if output.check_pattern(union_pattern):
                break
        return output.get_data()
    
    async def _read_prompt(self, process: asyncssh.SSHClientProcess) -> tuple[str, str]:
        """Read from process stdout until EOF."""
        output = ReadBuffer()
        try:
            while process.stdout and not process.stdout.at_eof():
                chunnk = await process.stdout.read(1024)
                output.append(chunnk)
                if output.check_pattern(re.compile(r"\r?\n?[a-zA-Z0-9._\-\(\)/<>\[\]]+[>#\]\$]\s?$")):
                    break
        except Exception as exc:
            log.debug(f"SSH probe: error while reading until EOF: {exc}")
        log.debug(f"SSH probe: raw prompt output: {output!r}")
        # get last no-blank line as prompt
        lines = output.get_data().splitlines()
        num_lines = len(lines)
        for i in range(num_lines - 1, -1, -1):
            line = lines[i]
            if line.strip():
                return line.strip(), output.get_data()
        return "", output.get_data()