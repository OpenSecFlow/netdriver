#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SNMP client for basic GET/WALK operations using pysnmp-lextudio."""

from pysnmp.hlapi.asyncio import (  # type: ignore[import]
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    UsmUserData,
    getCmd,
    bulkCmd,
    usmHMACMD5AuthProtocol,
    usmHMACSHAAuthProtocol,
    usmDESPrivProtocol,
    usmAesCfb128Protocol,
)

from netdriver_core.log import logman
from netdriver_core.snmp.models import SnmpCredential, SnmpResult

log = logman.logger

# Standard MIB-II OIDs
SNMP_OIDS = {
    "sysDescr": "1.3.6.1.2.1.1.1.0",
    "sysObjectID": "1.3.6.1.2.1.1.2.0",
    "sysUpTime": "1.3.6.1.2.1.1.3.0",
    "sysContact": "1.3.6.1.2.1.1.4.0",
    "sysName": "1.3.6.1.2.1.1.5.0",
    "sysLocation": "1.3.6.1.2.1.1.6.0",
    "sysServices": "1.3.6.1.2.1.1.7.0",
}

# Auth protocol mapping
_AUTH_PROTOCOLS = {
    "md5": usmHMACMD5AuthProtocol,
    "sha": usmHMACSHAAuthProtocol,
}

# Priv protocol mapping
_PRIV_PROTOCOLS = {
    "des": usmDESPrivProtocol,
    "aes": usmAesCfb128Protocol,
    "aes128": usmAesCfb128Protocol,
}


class SnmpClient:
    """Async SNMP client wrapping pysnmp-lextudio."""

    def __init__(self, timeout: float = 5.0, retries: int = 1, port: int = 161):
        self._timeout = timeout
        self._retries = retries
        self._port = port

    async def get(
        self,
        host: str,
        credential: SnmpCredential,
        oids: list[str],
        port: int | None = None,
    ) -> SnmpResult:
        """SNMP GET operation.

        Args:
            host: Target IP address.
            credential: SNMP credential (v2c community or v3 user).
            oids: List of OID strings to query.

        Returns:
            SnmpResult with {oid: value} data on success.
        """
        auth_data = self._build_auth_data(credential)
        transport = UdpTransportTarget(
            (host, port or self._port),
            timeout=self._timeout,
            retries=self._retries,
        )

        object_types = [ObjectType(ObjectIdentity(oid)) for oid in oids]

        try:
            error_indication, error_status, error_index, var_binds = await getCmd(
                SnmpEngine(),
                auth_data,
                transport,
                ContextData(),
                *object_types,
            )
        except Exception as e:
            log.debug(f"SNMP GET failed for {host}: {e}")
            return SnmpResult(success=False, error=str(e))

        if error_indication:
            return SnmpResult(success=False, error=str(error_indication))

        if error_status:
            error_msg = f"{error_status.prettyPrint()} at {var_binds[int(error_index) - 1][0] if error_index else '?'}"
            return SnmpResult(success=False, error=error_msg)

        data = {}
        for var_bind in var_binds:
            oid_str = str(var_bind[0])
            value_str = str(var_bind[1])
            data[oid_str] = value_str

        return SnmpResult(success=True, data=data)

    async def walk(
        self,
        host: str,
        credential: SnmpCredential,
        oid: str,
        port: int | None = None,
    ) -> SnmpResult:
        """SNMP WALK (GETBULK) operation.

        Args:
            host: Target IP address.
            credential: SNMP credential.
            oid: Root OID to walk.

        Returns:
            SnmpResult with {oid: value} data on success.
        """
        auth_data = self._build_auth_data(credential)
        transport = UdpTransportTarget(
            (host, port or self._port),
            timeout=self._timeout,
            retries=self._retries,
        )

        data = {}
        try:
            error_indication, error_status, error_index, var_bind_table = await bulkCmd(
                SnmpEngine(),
                auth_data,
                transport,
                ContextData(),
                0, 25,  # non-repeaters, max-repetitions
                ObjectType(ObjectIdentity(oid)),
            )

            if error_indication:
                return SnmpResult(success=False, error=str(error_indication))

            if error_status:
                return SnmpResult(success=False, error=str(error_status.prettyPrint()))

            for var_bind in var_bind_table:
                oid_str = str(var_bind[0])
                if not oid_str.startswith(oid):
                    break
                data[oid_str] = str(var_bind[1])

        except Exception as e:
            log.debug(f"SNMP WALK failed for {host}: {e}")
            return SnmpResult(success=False, error=str(e))

        return SnmpResult(success=True, data=data)

    async def get_system_info(
        self,
        host: str,
        credential: SnmpCredential,
        port: int | None = None,
    ) -> SnmpResult:
        """Convenience method to get standard system info (sysDescr, sysObjectID, sysName).

        Args:
            host: Target IP address.
            credential: SNMP credential.

        Returns:
            SnmpResult with system info.
        """
        oids = [
            SNMP_OIDS["sysDescr"],
            SNMP_OIDS["sysObjectID"],
            SNMP_OIDS["sysName"],
        ]
        return await self.get(host, credential, oids, port=port)

    @staticmethod
    def _build_auth_data(credential: SnmpCredential):
        """Build pysnmp auth data from credential."""
        if credential.version == "v2c":
            return CommunityData(credential.community or "public", mpModel=1)

        # SNMPv3
        auth_proto = _AUTH_PROTOCOLS.get(
            (credential.auth_protocol or "").lower()
        )
        priv_proto = _PRIV_PROTOCOLS.get(
            (credential.priv_protocol or "").lower()
        )

        return UsmUserData(
            userName=credential.username or "",
            authKey=credential.auth_password,
            privKey=credential.priv_password,
            authProtocol=auth_proto,
            privProtocol=priv_proto,
        )
