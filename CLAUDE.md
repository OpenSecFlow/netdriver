# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetDriver is a network device automation framework built on AsyncSSH that provides HTTP RESTful APIs for CLI command execution on network devices. It's organized as a monorepo with a Polylith architecture, consisting of:

- **netdriver-agent**: FastAPI-based REST API service for device connectivity testing and command execution
- **netdriver-simunet**: SSH server simulation for testing network device terminals

## Key Architecture Patterns

### Polylith Architecture

The project uses a Polylith-inspired structure with `bases/` (applications) and `components/` (shared libraries):

```Text
bases/netdriver/
├── agent/          # REST API application
└── simunet/        # Simulation network application

components/netdriver/
├── client/         # SSH client with async session management
├── exception/      # Centralized error handling and error codes
├── log/            # Logging utilities (Loguru-based)
├── plugin/         # Plugin system core and engine
├── plugins/        # Device-specific plugins (Cisco, Huawei, Juniper, etc.)
├── server/         # SSH server for simulated devices
├── textfsm/        # Enhanced TextFSM for output parsing
└── utils/          # Utility functions
```

### Session Management

The `SessionPool` (in `components/netdriver/client/pool.py`) is a singleton that:

- Maintains persistent SSH sessions with devices (identified by `protocol:username@ip:port`)
- Automatically monitors session health and removes closed/expired/idle sessions
- Implements a command queue per session to prevent concurrent configuration conflicts
- Uses asyncio locks to ensure thread-safe session operations

### Plugin System

The plugin engine (`components/netdriver/plugin/engine.py`) dynamically loads device plugins at startup:

- Plugins are organized by vendor directory under `components/netdriver/plugins/`
- Each plugin inherits from `Base` (in `components/netdriver/plugins/base.py`) and implements device-specific behavior
- Plugins define mode patterns (LOGIN, ENABLE, CONFIG), error patterns, and command handling
- Plugin resolution: `vendor/model/version` → `vendor/model/base` → `vendor/base/base`

### Device Modes and State Management

Sessions track device state including:

- **Mode**: LOGIN, ENABLE, or CONFIG (defined in `client/mode.py`)
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
# Default: auto-detects CPU cores and uses (cores - 2) workers, minimum 1
uv run simunet

# Specify custom number of workers
NUM_WORKERS=4 uv run simunet
# or
uv run simunet --workers 4

# Force single worker mode (enables auto-reload for development)
NUM_WORKERS=1 uv run simunet

# Auto-cleanup occupied ports before starting
uv run simunet --force
```

### Testing

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest -m unit

# Run integration tests only
uv run pytest -m integration

# Run specific test file
uv run pytest tests/bases/netdriver/agent/test_cisco_nexus.py
```

### Configuration

Configuration files in `config/`:

- `config/agent/agent.yml` - Agent service settings (logging, session timeouts, SSH parameters, profiles)
 - Logs are written to `logs/netdriver_agent.log`
- `config/simunet/simunet.yml` - Simulated device definitions and logging settings
 - Logs are written to `logs/netdriver_simunet.log`
 - In multi-worker mode: `logs/netdriver_simunet_worker_0.log`, `logs/netdriver_simunet_worker_1.log`, etc.

### Multi-Process Mode

Simunet **automatically** uses multi-process mode for improved performance:

**Default Behavior:**
- Automatically detects CPU cores: `workers = max(1, cpu_cores - 2)`
- Example: 8-core system → 6 workers, 4-core → 2 workers, 2-core → 1 worker
- Reserves 2 cores for system and other processes
- **Smart adjustment**: If worker count exceeds device count, automatically adjusts to match device count

**Override Default:**
```bash
# Specify custom number of workers
NUM_WORKERS=4 uv run simunet
# or
uv run simunet --workers 4

# Force single worker (enables auto-reload)
NUM_WORKERS=1 uv run simunet
```

**Performance Guidelines:**
- Small scale (< 10 devices): 1-2 workers
- Medium scale (10-30 devices): 2-4 workers
- Large scale (> 30 devices): 4-8 workers

**Notes:**
- Multi-worker mode (workers > 1) does not support auto-reload
- Single worker mode supports auto-reload for development
- Each worker handles a portion of devices automatically
- Separate log files are created for each worker: `logs/simunet_worker_N.log`

## Development Guidelines

### Adding a New Device Plugin

1. Create vendor directory under `components/netdriver/plugins/` if it doesn't exist
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
from netdriver_agent.plugin.plugin_info import PluginInfo
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

Integration tests are in `tests/bases/netdriver/agent/` and typically:

1. Start the simunet service with test fixtures in `conftest.py`
2. Use httpx client to make API calls to the agent
3. Verify command execution and error handling

### Error Handling

All custom exceptions are in `components/netdriver/exception/errors.py` and inherit from `BaseError`:

- Include HTTP status code and error code
- For command execution errors, include output
- Examples: `LoginFailed`, `PluginNotFound`, `ExecCmdTimeout`, `EnableFailed`

### Dependency Injection

The agent uses `dependency-injector` (see `bases/netdriver/agent/containers.py`) to wire:

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
