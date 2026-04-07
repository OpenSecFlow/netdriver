#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Default SSH algorithm configurations for broad device compatibility.

These algorithm lists ensure connectivity with a wide range of legacy and
modern network devices. They are shared between the agent SSH client and
the discovery SSH probe.
"""

DEFAULT_KEX_ALGS = [
    "gss-curve25519-sha256",
    "gss-curve448-sha512",
    "gss-nistp521-sha512",
    "gss-nistp384-sha384",
    "gss-nistp256-sha256",
    "gss-1.3.132.0.10-sha256",
    "gss-gex-sha256",
    "gss-group14-sha256",
    "gss-group15-sha512",
    "gss-group16-sha512",
    "gss-group17-sha512",
    "gss-group18-sha512",
    "gss-group14-sha1",
    "curve25519-sha256",
    "curve25519-sha256@libssh.org",
    "curve448-sha512",
    "ecdh-sha2-nistp521",
    "ecdh-sha2-nistp384",
    "ecdh-sha2-nistp256",
    "ecdh-sha2-1.3.132.0.10",
    "diffie-hellman-group-exchange-sha256",
    "diffie-hellman-group14-sha256",
    "diffie-hellman-group15-sha512",
    "diffie-hellman-group16-sha512",
    "diffie-hellman-group17-sha512",
    "diffie-hellman-group18-sha512",
    "diffie-hellman-group14-sha256@ssh.com",
    "diffie-hellman-group14-sha1",
    "rsa2048-sha256",
    "gss-gex-sha1",
    "gss-group1-sha1",
    "diffie-hellman-group-exchange-sha224@ssh.com",
    "diffie-hellman-group-exchange-sha384@ssh.com",
    "diffie-hellman-group-exchange-sha512@ssh.com",
    "diffie-hellman-group-exchange-sha1",
    "diffie-hellman-group14-sha224@ssh.com",
    "diffie-hellman-group15-sha256@ssh.com",
    "diffie-hellman-group15-sha384@ssh.com",
    "diffie-hellman-group16-sha384@ssh.com",
    "diffie-hellman-group16-sha512@ssh.com",
    "diffie-hellman-group18-sha512@ssh.com",
    "diffie-hellman-group1-sha1",
    "rsa1024-sha1",
]

DEFAULT_ENCRYPTION_ALGS = [
    "chacha20-poly1305@openssh.com",
    "aes256-gcm@openssh.com",
    "aes128-gcm@openssh.com",
    "aes256-ctr",
    "aes192-ctr",
    "aes128-ctr",
    "aes256-cbc",
    "aes192-cbc",
    "aes128-cbc",
    "3des-cbc",
    "blowfish-cbc",
    "cast128-cbc",
    "seed-cbc@ssh.com",
    "arcfour256",
    "arcfour128",
    "arcfour",
]
