# SimuNet Quick Start Guide

This guide will help you quickly get started with NetDriver SimuNet service.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
  - [Prepare](#prepare)
  - [Configuration](#configuration)
  - [Option 1: Install via PyPI](#option-1-install-via-pypi)
  - [Option 2: Install via Docker](#option-2-install-via-docker)
- [Connecting to Simulated Devices](#connecting-to-simulated-devices)
- [Next Steps](#next-steps)

## Introduction

SimuNet is a network device simulator that emulates SSH terminal behavior of real network devices. It's designed for:

- **Automated Testing**: Test automation scripts without real hardware
- **Development and Debugging**: Develop and test new plugins safely
- **Demonstrations and Training**: Provide simulated environments for demos

### Key Features

- **Multi-Vendor Support**: Emulates devices from Cisco, Huawei, Juniper, and more
- **Easy Setup**: Simple YAML configuration for device definitions
- **Plugin-Based**: Uses the same plugin system as the Agent
- **Realistic Behavior**: Emulates device prompts, modes, and command responses
- **High Performance**: AsyncSSH-based SSH server for multiple simultaneous connections

## Installation

### Prepare

Create and enter a directory for running simunet. Then:

**1. Create Configuration Directory**

```bash
mkdir -p config/simunet logs
```

**2. Download Default Configuration File**

```bash
curl -o config/simunet/simunet.yml https://raw.githubusercontent.com/OpenSecFlow/netdriver/master/config/simunet/simunet.yml
```

### Configuration

The SimuNet configuration file is located at `config/simunet/simunet.yml`:

```yaml
logging:
  level: INFO
  log_file: logs/simunet.log

devices:
  - vendor: cisco          # Vendor
    model: nexus          # Model
    version: 9.6.0        # Version
    port: 18020           # SSH port

  - vendor: huawei
    model: usg
    version: V500R001C10
    port: 18022

  - vendor: juniper
    model: srx
    version: 12.0
    port: 18028
```

> The downloaded sample configuration includes all device types currently supported by SimuNet. You can remove devices that are not needed.

#### Configuration Explanation

1. **Device Parameters**:
   - `vendor`: Device vendor (must match plugin vendor name)
   - `model`: Device model (must match plugin model name)
   - `version`: Device version (for plugin selection)
   - `port`: SSH port for this simulated device

2. **Logging Configuration**:
   - `level`: Log level (INFO, DEBUG, TRACE)
   - `log_file`: Path to log file

**Important Notes**:

- Each device must have a unique port
- Vendor and model must match an available plugin
- Port range 18020-18100 is recommended to avoid conflicts

Choose one of the following installation methods:

### Option 1: Install via PyPI

#### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

#### Installation Steps

**1. Install NetDriver SimuNet Package**

```bash
pip install netdriver-simunet
```

**2. Verify Installation**

```bash
python -c "import netdriver.simunet; print('NetDriver Agent installed successfully')"
```

#### Run

**Basic Usage**:

```bash
# Start SimuNet service (auto-detects CPU cores and sets workers)
simunet

# Start without auto-reload (production)
simunet --no-reload

# Start with specific number of workers
simunet --workers 4 --no-reload
```

**Custom Configuration**:

```bash
# Use custom config file
simunet --config /path/to/simunet.yml --port 8001

# Set workers via environment variable
NUM_WORKERS=4 simunet --no-reload
```

### Option 2: Install via Docker

#### Prerequisites

- Docker 20.10 or higher
- Docker Compose (optional)

#### Using Docker Run

```bash
docker run -d \
  --name netdriver-simunet \
  -p 18020-18040:18020-18040 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-simunet:latest
```

> Because simunet will listen on a port for a kind of device, So the docker need mapping a range of ports.
> You can also using docker host network mode instead maping a range of ports.

Docker instance run usign host network mode

```bash
docker run -d \
  --name netdriver-simunet \
  --network host \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-simunet:latest
```

### Check log

Run `tail` command to check logs

```bash
tail -f logs/simunet.log
```

![SimLog](./imgs/sim_start.png)

## Connecting to Simulated Devices

### Using SSH Client

You can connect to simulated devices using any SSH client:

```bash
# Connect to Cisco Nexus simulated device
ssh admin@localhost -p 18020
```

> username and passowrd can be any string

![SimLogin](./imgs/sim_login.png)

After successful connection, you can execute commands as you would on a real device:

## Advanced Configuration

### Multi-Process Mode

SimuNet automatically uses multi-process mode based on your CPU cores to improve performance. Each worker process handles a portion of the devices.

#### Default Behavior

**Automatic Worker Detection:**
- SimuNet automatically detects CPU cores and uses `CPU cores - 2` workers (minimum 1)
- Example: 8-core CPU → 6 workers, 4-core CPU → 2 workers, 2-core CPU → 1 worker
- This leaves resources for the system and other processes

**Override Default:**

```bash
# Use specific number of workers via environment variable
NUM_WORKERS=4 simunet

# Use specific number of workers via command line
simunet --workers 4

# Force single worker mode
NUM_WORKERS=1 simunet
# or
simunet --workers 1
```

#### Performance Recommendations

- **Small Scale (< 10 devices)**: 1-2 workers
- **Medium Scale (10-30 devices)**: 2-4 workers  
- **Large Scale (> 30 devices)**: 4-8 workers

Each worker should ideally manage 5-10 devices for optimal performance.

**Note**: 
- Multi-worker mode (workers > 1) does not support auto-reload
- Single worker mode supports auto-reload for development

#### Docker Deployment with Multi-Process

```bash
# Default (auto-detect workers)
docker run -d \
  --name netdriver-simunet \
  --network host \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-simunet:latest

# Specify worker count
docker run -d \
  --name netdriver-simunet \
  --network host \
  -e NUM_WORKERS=4 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-simunet:latest
```

#### How Device Distribution Works

When using multi-process mode, devices are automatically distributed among workers:

- Worker 0 handles devices 0 to N/W-1
- Worker 1 handles devices N/W to 2N/W-1
- ...
- Last worker handles remaining devices

**Example 1: 21 devices, 3 workers**
- Worker 0: devices 0-6 (7 devices, ports 18020-18025)
- Worker 1: devices 7-13 (7 devices, ports 18026-18031)
- Worker 2: devices 14-20 (7 devices, ports 18032-18040)

**Example 2: 4 devices, 8 workers (auto-adjusted)**
- System: 10 CPU cores → 8 workers by default
- SimuNet automatically adjusts to 4 workers (matches device count)
- Worker 0: device 0 (1 device)
- Worker 1: device 1 (1 device)
- Worker 2: device 2 (1 device)
- Worker 3: device 3 (1 device)

**Important:** If worker count exceeds device count, it's automatically adjusted to match device count to avoid empty workers.

Each worker creates a separate log file: `logs/simunet_worker_0.log`, `logs/simunet_worker_1.log`, etc.

## Next Steps

Now that you have SimuNet running, you can set up [NetDriver Agent](./quick-start-agent.md) to connect to SimuNet
