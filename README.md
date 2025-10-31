# NetDriver

<a name="top"></a>

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-1.8.3-60A5FA.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](./LICENSE)
[![Build & Test](https://github.com/OpenSecFlow/netdriver/actions/workflows/build.yml/badge.svg)](https://github.com/OpenSecFlow/netdriver/actions/workflows/build.yml)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](./CONTRIBUTING.md)
[![Last Commit](https://img.shields.io/github/last-commit/OpenSecFlow/netdriver)](https://github.com/OpenSecFlow/netdriver/commits/master)
[![Release](https://img.shields.io/github/v/release/OpenSecFlow/netdriver)](https://github.com/OpenSecFlow/netdriver/releases)
[![Release Date](https://img.shields.io/github/release-date/OpenSecFlow/netdriver)](https://github.com/OpenSecFlow/netdriver/releases)
[![Discord](https://img.shields.io/badge/Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/BGZuQQ5g)

⭐ Star us on GitHub — your support motivates us a lot! 🙏😊

[![Share](https://img.shields.io/badge/share-000000?logo=x&logoColor=white)](https://x.com/intent/tweet?text=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/OpenSecFlow/netdriver%20%23NetworkAutomation%20%23NetDriver%20%23DevOps)
[![Share](https://img.shields.io/badge/share-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/OpenSecFlow/netdriver)
[![Share](https://img.shields.io/badge/share-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/OpenSecFlow/netdriver)
[![Share](https://img.shields.io/badge/share-FF4500?logo=reddit&logoColor=white)](https://www.reddit.com/submit?title=Check%20out%20this%20project%20on%20GitHub:%20https://github.com/OpenSecFlow/netdriver)
[![Share](https://img.shields.io/badge/share-0088CC?logo=telegram&logoColor=white)](https://t.me/share/url?url=https://github.com/OpenSecFlow/netdriver&text=Check%20out%20this%20project%20on%20GitHub)

## Table of Contents

- [About](#about)
- [Comparison](#comparison)
- [Architecture](#architecture)
- [Support Devices](#support-devices)
  - [Supported Vendors and Models](#supported-vendors-and-models)
  - [Plugin Architecture](#plugin-architecture)
  - [Adding Device Support](#adding-device-support)
- [Quick Start](#quick-start)
- [Contributions and Requests](#contributions-and-requests)
- [License](#license)
- [Contacts](#contacts)

## About

Everyone loves netmiko cause it's the best at what it can do, so instead of reinventing the wheel we decided to add couple of sticks in to it by implementing some Quality-of-life features.
NetDriver is a network device automation framework that enables CLI command execution through HTTP RESTful APIs.
With features like session persistence for efficiency a command queue to avoid configuration conflicts and an HTTP RESTful API for simple third-party integration. With its plugin architecture which combines automation scalability and contemporary network management in a single framework it offers high concurrency and is built on top of AsyncSSH
for your convinience.

NetDriver adopts a Monorepo architecture consisting of multiple sub-projects:

- **netdriver-agent** - Provides REST APIs for device connectivity testing and command execution
- **netdriver-simunet** - Simulates network device terminals for automated testing and other scenarios requiring device emulation

Features:

- 🌐 **HTTP RESTful API** : Easy integration with third-party platforms
- 🔄 **Session Management** : Customizable session persistence for improved efficiency, eliminating repeated connections per command
- 📋 **Command Queue** : Ensures sequential command execution on devices, preventing configuration errors and failures caused by concurrent modifications
- ⚡ **AsyncSSH Foundation** : Superior concurrency capabilities through asynchronous SSH implementation
- 🔌 **Plugin Architecture** : Simplified and accelerated development of new vendor support

## Comparison

|     Feature       | NetDriver | Netmiko |
|------------|:--------:|:----:|
| **HTTP RESTful API for third-party integration** | ✅       | ❌    |
| **Session persistence with customizable duration** | ✅       | ❌    |
|  **Python-based implementation**    | ✅       | ✅    |
|  **Command execution queue to prevent concurrent conflicts**    | ✅       | ❌    |
|  **Plugin architecture for easier device support development**    | ✅       | ❌    |
|  **Standard CLI automation**    | ✅       | ✅    |
|  **Open source**    | ✅       | ✅    |
|   **AsyncSSH-based architecture for high concurrency**    | ✅       | ❌    |

## Architecture

```text
┌─────────────────┐
│  Your App/Tool  │
└────────┬────────┘
         │ HTTP API
         ▼
┌─────────────────┐
│ NetDriver Agent │
└────────┬────────┘
         │ SSH
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│SimuNet │ │ Real   │
│Devices │ │Devices │
└────────┘ └────────┘
```

## Support Devices

NetDriver currently supports a wide range of network devices from major vendors. The plugin architecture makes it easy to add support for new devices.

### Supported Vendors and Models

| Vendor | Model | Device Type | Description |
|--------|-------|-------------|-------------|
| **Cisco** | ASA | Firewall | Cisco Adaptive Security Appliance |
| | ASR | Router | Cisco Aggregation Services Router |
| | Catalyst | Switch | Cisco Catalyst Series Switches |
| | ISR | Router | Cisco Integrated Services Router |
| | Nexus | Switch | Cisco Nexus Data Center Switches |
| **Huawei** | CE | Switch | Huawei CloudEngine Series Switches |
| | USG | Firewall | Huawei Unified Security Gateway |
| **Juniper** | EX | Switch | Juniper EX Series Ethernet Switches |
| | MX | Router | Juniper MX Series Universal Routing Platforms |
| | QFX | Switch | Juniper QFX Series Data Center Switches |
| | SRX | Firewall | Juniper SRX Series Services Gateways |
| **Fortinet** | FortiGate | Firewall | Fortinet FortiGate Next-Generation Firewalls |
| **Palo Alto** | PA | Firewall | Palo Alto Networks Next-Generation Firewalls |
| **Arista** | EOS | Switch | Arista Networks EOS-based Switches |
| **H3C** | SecPath | Firewall | H3C SecPath Series Firewalls |
| | VSR | Router | H3C Virtual Services Router |
| **Check Point** | Security Gateway | Firewall | Check Point Security Gateway |
| **Hillstone** | SG | Firewall | Hillstone StoneOS-based Security Gateways |
| **DPTech** | FW | Firewall | DPTech Firewall Series |
| **Topsec** | NGFW | Firewall | Topsec Next-Generation Firewalls |
| **Venustech** | USG | Firewall | Venustech Unified Security Gateway |
| **Maipu** | NSS | Switch | Maipu Network Security Switch |
| **Array** | AG | Gateway | Array Application Gateway |
| **Chaitin** | CTD-SG | Gateway | Chaitin SafeLine Security Gateway |
| **Qianxin** | NSG | Gateway | Qianxin Next-Generation Security Gateway |
| **Leadsec** | PowerV | Firewall | Leadsec PowerV Series |

### Plugin Architecture

The plugin system allows for easy extension and customization:

- **Vendor Base Plugins**: Common functionality shared across device models from the same vendor
- **Model-Specific Plugins**: Device-specific implementations for unique features and behaviors
- **Pattern Matching**: Automatic plugin selection based on vendor/model/version detection
- **Extensible**: Add new device support by creating a new plugin class

### Adding Device Support

To add support for a new device, create a plugin in `components/netdriver/plugins/{vendor}/` that inherits from the vendor base class or `Base` plugin. See [Development Guidelines](./CONTRIBUTING.md) for more information.

## Quick Start

We can first run the Simunet service to obtain simulated network devices for testing, then use the Agent to connect and execute commands. Of course, if you have real devices that are on the [support devices](#support-devices), you can skip the Simunet guide and start using the Agent service directly.

- [Simunet Guide](./docs/quick-start-simunet.md)
- [Agent Guide](./docs/quick-start-agent.md)

## Contributions and Requests

Your contributions matter!Our project can always be better so we would be happy to recive your help!Please take a look at [contributing](./CONTRIBUTING.md) guide before submiting a pull request!
For questions, issues, or feature requests, please open an issue on the project repository.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Contacts

We look forward to assisting you and ensuring your experience with our products is successful and enjoyable!

[![Discord](https://img.shields.io/badge/Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/BGZuQQ5g)

[Back to top](#top)
