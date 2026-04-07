# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.4.x   | Yes       |
| < 0.4   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in NetDriver, **please do not open a public GitHub issue**.

Instead, report it via one of the following channels:

- **Email**: Send details to the maintainers at the addresses listed in `pyproject.toml`
- **GitHub Private Advisory**: Use [GitHub Security Advisories](https://github.com/features/security-advisories) on this repository

Please include the following in your report:

- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Affected versions
- Any suggested mitigations or patches (if available)

We aim to acknowledge receipt within **3 business days** and provide an initial assessment within **7 business days**.

## Security Considerations

NetDriver interacts with network devices over SSH and exposes a REST API. When deploying this project, consider the following:

### Credentials and Secrets

- Device credentials (username/password) are passed via API requests. Use TLS/HTTPS in all deployments to prevent credential exposure in transit.
- Do not log credentials. The agent configuration should be reviewed to ensure no sensitive fields appear in log output.
- Rotate device credentials regularly and restrict API access to trusted clients.

### API Authentication

- The agent HTTP API does **not** include built-in authentication. Deploy it behind an API gateway, reverse proxy, or firewall that enforces authentication and authorization appropriate for your environment.
- Restrict network access to the agent port (default: 8000) to trusted hosts only.

### SSH Host Verification

- By default, AsyncSSH may be configured to skip host key verification for convenience. In production, enable strict host key checking to prevent man-in-the-middle attacks.

### Plugin Code Execution

- Plugins are loaded dynamically from the `packages/agent/src/netdriver_agent/plugins/` directory at startup. Ensure that only trusted code is present in the plugin directories and that the deployment environment has appropriate file system permissions.

### Simulated Devices (simunet)

- The `simunet` SSH server is intended for **testing purposes only**. Do not expose it on public networks or use it in production environments.

## Disclosure Policy

We follow a coordinated disclosure process. Once a fix is available, we will:

1. Release a patched version
2. Publish a security advisory describing the vulnerability, its impact, and the fix
3. Credit the reporter (unless they prefer to remain anonymous)
