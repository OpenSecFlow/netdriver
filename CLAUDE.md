# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetDriver is a network device automation framework built on AsyncSSH that provides HTTP RESTful APIs for CLI command execution on network devices. It's organized as a monorepo with a Polylith architecture, consisting of:

- **netdriver-agent**: FastAPI-based REST API service for device connectivity testing and command execution
- **netdriver-simunet**: SSH server simulation for testing network device terminals

## Key Architecture Patterns

### Workspace Architecture

The project uses a `uv` workspace monorepo with package-local `src/` trees:

```Text
packages/
├── agent/src/netdriver_agent/          # REST API, session handling, plugins
├── core/src/netdriver_core/            # Shared errors, logging, plugin primitives
├── discovery/src/netdriver_discovery/  # Device discovery logic
├── simunet/src/netdriver_simunet/      # Simulation network service
└── textfsm/src/netdriver_textfsm/      # Enhanced TextFSM parser
```

### Session Management

The `SessionPool` (in `packages/agent/src/netdriver_agent/client/pool.py`) is a singleton that:

- Maintains persistent SSH sessions with devices (identified by `protocol:username@ip:port`)
- Automatically monitors session health and removes closed/expired/idle sessions
- Implements a command queue per session to prevent concurrent configuration conflicts
- Uses asyncio locks to ensure thread-safe session operations

### Plugin System

The plugin engine (`packages/agent/src/netdriver_agent/plugins/engine.py`) dynamically loads device plugins at startup:

- Plugins are organized by vendor directory under `packages/agent/src/netdriver_agent/plugins/`
- Each plugin inherits from `Base` (in `packages/agent/src/netdriver_agent/plugins/base.py`) and implements device-specific behavior
- Plugins define mode patterns (LOGIN, ENABLE, CONFIG), error patterns, and command handling
- Plugin resolution: `vendor/model/version` → `vendor/model/base` → `vendor/base/base`

### Device Modes and State Management

Sessions track device state including:

- **Mode**: LOGIN, ENABLE, or CONFIG (defined in `packages/core/src/netdriver_core/dev/mode.py`)
- **Vsys**: Virtual system context (for multi-context devices like firewalls)
- Mode switching is handled automatically by the base plugin via `switch_mode()`

## Commands

### Development Environment

```bash
# Install dependencies
uv sync
```

### Running Services

```bash
# Start agent service (REST API on http://localhost:8000)
uv run agent

# Start simulation network service (SSH servers on configured ports)
uv run simunet
```

### Testing

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest -m unit

# Run integration tests only
uv run pytest --mock-dev -m integration

# Run specific test file
uv run pytest tests/integration/test_cisco_nexus.py
```

### Configuration

Configuration files in `config/`:

- `config/agent/agent.yml` - Agent service settings (logging, session timeouts, SSH parameters, profiles)
  - Logs are written to `logs/netdriver_agent.log`
- `config/simunet/simunet.yml` - Simulated device definitions and logging settings
  - Logs are written to `logs/netdriver_simunet.log`

## Development Guidelines

### Adding a New Device Plugin

1. Create vendor directory under `packages/agent/src/netdriver_agent/plugins/` if it doesn't exist
2. Create plugin file named `{vendor}_{model}.py` (e.g., `cisco_nexus.py`)
3. Inherit from vendor base class or `Base` plugin
4. Define `PluginInfo` with vendor, model, version, and description
5. Implement required abstract methods:
   - `get_mode_prompt_patterns()` - Regex patterns for each mode's prompt
   - `get_more_pattern()` - Pattern for pagination prompts
   - `get_union_pattern()` - Combined pattern for all prompts
   - `get_error_patterns()` - Patterns that indicate command errors
   - `get_ignore_error_patterns()` - Error patterns to ignore

Example:

```python
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.cisco import CiscoBase

class CiscoNexus(CiscoBase):
    info = PluginInfo(
        vendor="cisco",
        model="nexus",
        version="base",
        description="Cisco Nexus Plugin"
    )
```

### Testing Plugins

Integration tests are in `tests/integration/` and typically:

1. Start the simunet service with test fixtures in `conftest.py`
2. Use httpx client to make API calls to the agent
3. Verify command execution and error handling

### Error Handling

All custom exceptions are in `packages/core/src/netdriver_core/exception/errors.py` and inherit from `BaseError`:

- Include HTTP status code and error code
- For command execution errors, include output
- Examples: `LoginFailed`, `PluginNotFound`, `ExecCmdTimeout`, `EnableFailed`

### Dependency Injection

The agent uses `dependency-injector` (see `packages/agent/src/netdriver_agent/containers.py`) to wire:

- Configuration providers
- Request handlers
- The container is wired to API modules in `main.py`

### Logging

Uses Loguru configured via `netdriver_core.log.logman`:

- Correlation ID middleware tracks requests (agent only)
- Log levels configurable in respective config files
- Log files are separated by service:
  - Agent: `logs/agent.log` (excludes `netdriver_simunet.server` modules in test environment)
  - Simunet: `logs/simunet.log` (only `netdriver_simunet.server` modules)
- Intercepts uvicorn logs for unified output
- Log rotation: 1 day, retention: 60 days
- Module filtering: Uses `logger.patch()` in `netdriver_simunet.server.device` to ensure correct module identification
- In test environment: Both handlers are configured to prevent log duplication

## Important Notes

- Python 3.12+ required
- Uses uv for dependency management
- All SSH operations are async (AsyncSSH-based)
- Session keys format: `{protocol}:{username}@{ip}:{port}`
- The agent runs with auto-reload enabled by default (suitable for development)
- Simulated devices use the plugin system to emulate vendor-specific behavior
- Configuration profiles support device-specific settings by vendor/model/version or IP address
