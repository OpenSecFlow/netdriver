# netdriver-agent

NetDriver Agent is a FastAPI-based REST API service that provides:

- **Device Connectivity Testing**: Verify SSH connectivity to network devices
- **Command Execution**: Execute CLI commands on network devices via HTTP API
- **Session Management**: Maintain persistent SSH sessions with customizable timeouts
- **Command Queue**: Ensure sequential command execution to prevent configuration conflicts

## Key Features

- **HTTP RESTful API**: Easy integration with third-party platforms and automation tools
- **Session Persistence**: Reuse SSH connections for improved efficiency and reduced latency
- **Command Queue**: Sequential command execution prevents configuration conflicts
- **Flexible Configuration**: Customize timeouts and behavior per device, vendor, or globally
- **High Performance**: AsyncSSH-based architecture for handling multiple concurrent requests
