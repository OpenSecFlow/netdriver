# netdriver-simunet

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
