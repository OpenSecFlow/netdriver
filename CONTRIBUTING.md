# Contributing to NetDriver

Thank you for your interest in contributing to NetDriver! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Contributing to NetDriver](#contributing-to-netdriver)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
    - [Our Pledge](#our-pledge)
    - [Our Standards](#our-standards)
    - [Enforcement](#enforcement)
  - [Getting Started](#getting-started)
  - [Development Environment Setup](#development-environment-setup)
    - [Prerequisites](#prerequisites)
    - [Setup Steps](#setup-steps)
  - [How to Contribute](#how-to-contribute)
  - [Development Guidelines](#development-guidelines)
    - [Code Style](#code-style)
    - [Example Code Style](#example-code-style)
    - [Commit Messages](#commit-messages)
    - [Branch Naming](#branch-naming)
  - [Adding a New Device Plugin](#adding-a-new-device-plugin)
    - [1. Create Plugin File](#1-create-plugin-file)
    - [2. Implement Plugin Class](#2-implement-plugin-class)
    - [3. Add Tests](#3-add-tests)
    - [4. Update Documentation](#4-update-documentation)
  - [Testing](#testing)
    - [Running Tests](#running-tests)
    - [Writing Tests](#writing-tests)
  - [Pull Request Process](#pull-request-process)
  - [Reporting Bugs](#reporting-bugs)
  - [Screenshots](#screenshots)
  - [Feature Requests](#feature-requests)
  - [Project Structure](#project-structure)
  - [Questions or Need Help?](#questions-or-need-help)
  - [Recognition](#recognition)

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to make participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information, such as a physical or electronic address, without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated and will result in a response that is deemed necessary and appropriate to the circumstances. The project team is obligated to maintain confidentiality with regard to the reporter of an incident.

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org/), version 1.4.

## Getting Started

Before you start contributing, please:

1. Read this contribution guide thoroughly
2. Check the [existing issues](https://github.com/OpenSecFlow/netdriver/issues) to see if your concern is already being addressed
3. For major changes, open an issue first to discuss what you would like to change
4. Fork the repository and create your branch from `master`

## Development Environment Setup

### Prerequisites

- Python 3.12 or higher
- uv 0.9.26 or higher (https://docs.astral.sh/uv/)
- Git

### Setup Steps

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/netdriver.git
   cd netdriver
   ```

2. **Install Python (using pyenv)**

   ```bash
   # Install pyenv if not already installed
   curl -fsSL https://pyenv.run | bash

   # Install Python 3.12.7
   pyenv install 3.12.7
   pyenv local 3.12.7
   ```

3. **Install uv**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Install Dependencies**

   ```bash
   uv sync
   ```

5. **Verify Installation**

   ```bash
   # Run tests to ensure everything is working
   uv run pytest
   ```

## How to Contribute

There are many ways to contribute to NetDriver:

- **Report bugs** - Help us identify and fix issues
- **Suggest features** - Share ideas for new functionality
- **Write documentation** - Improve or expand our docs
- **Add device plugins** - Extend support for more network devices
- **Fix bugs** - Submit pull requests for known issues
- **Improve code quality** - Refactoring, optimization, and code cleanup

## Development Guidelines

### Code Style

1. **Follow PEP 8** - Python code should adhere to [PEP 8](https://pep8.org/) style guidelines
2. **Use Type Hints** - Add type annotations to function signatures
3. **Write Docstrings** - Document modules, classes, and functions using Google-style docstrings
4. **Keep It Simple** - Write clear, readable code; avoid unnecessary complexity

### Example Code Style

```python
from typing import List, Optional

async def execute_command(
    device_ip: str,
    command: str,
    timeout: int = 30
) -> dict:
    """Execute a command on a network device.

    Args:
        device_ip: IP address of the target device
        command: CLI command to execute
        timeout: Command execution timeout in seconds

    Returns:
        Dictionary containing command output and execution status

    Raises:
        ExecCmdTimeout: If command execution exceeds timeout
        LoginFailed: If authentication fails
    """
    # Implementation here
    pass
```

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update", "Refactor")
- Keep the first line under 72 characters
- Add detailed description in the body if needed

**Good examples:**

```text
Add Cisco ASA plugin support

Fix session timeout handling in SessionPool
- Properly handle expired sessions
- Add reconnection logic
- Update tests

Update documentation for plugin development
```

**Bad examples:**

```text
fixed stuff
update
changes
```

### Branch Naming

Use descriptive branch names that reflect the work:

- `feature/add-cisco-asa-plugin`
- `fix/session-timeout-handling`
- `docs/update-plugin-guide`
- `refactor/improve-error-handling`

## Adding a New Device Plugin

NetDriver uses a plugin architecture to support different network devices. Here's how to add a new plugin:

### 1. Create Plugin File

Create a new file under `packages/agent/src/netdriver_agent/plugins/[vendor]/`:

```bash
packages/agent/src/netdriver_agent/plugins/cisco/cisco_asa.py
```

### 2. Implement Plugin Class

```python
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.cisco import CiscoBase

class CiscoASA(CiscoBase):
    """Cisco ASA Firewall Plugin."""

    info = PluginInfo(
        vendor="cisco",
        model="asa",
        version="base",
        description="Cisco ASA Firewall Plugin"
    )

    def get_mode_prompt_patterns(self) -> dict:
        """Define prompt patterns for each mode."""
        return {
            "LOGIN": r"[\r\n][\w\-\.]+>\s*$",
            "ENABLE": r"[\r\n][\w\-\.]+#\s*$",
            "CONFIG": r"[\r\n][\w\-\.]+\(config[^\)]*\)#\s*$",
        }

    def get_more_pattern(self) -> str:
        """Pattern for pagination prompts."""
        return r"<--- More --->"

    def get_error_patterns(self) -> list:
        """Patterns that indicate command errors."""
        return [
            r"% Invalid",
            r"% Incomplete",
            r"% Unknown",
        ]
```

### 3. Add Tests

Create an integration test file under `tests/integration/`:

```bash
tests/integration/test_cisco_asa.py
```

If you add new prompt parsing or vendor detection logic, also extend the focused unit tests under `packages/agent/tests/plugins/`.

### 4. Update Documentation

Add the new plugin to the supported devices list in the README.

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/integration/test_cisco_nexus.py

# Run unit tests only
uv run pytest -m unit

# Run integration tests only
uv run pytest --mock-dev -m integration
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Test both success and failure cases
- Use meaningful test names

**Example test:**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_execute_command_success(client: AsyncClient):
    """Test successful command execution."""
    response = await client.post(
        "/api/v1/exec",
        json={
            "ip": "192.168.1.1",
            "username": "admin",
            "password": "password",
            "commands": ["show version"]
        }
    )
    assert response.status_code == 200
    assert "output" in response.json()
```

## Pull Request Process

1. **Update Your Fork**

   ```bash
   git checkout master
   git pull upstream master
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**

   - Write your code
   - Add tests
   - Update documentation
   - Ensure all tests pass

3. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add clear description of your changes"
   ```

4. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**

   - Go to the [NetDriver repository](https://github.com/OpenSecFlow/netdriver)
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Description of changes
     - Related issue numbers
     - Testing performed
     - Screenshots (if applicable)

6. **PR Review Requirements**

   - All tests must pass
   - Code coverage should not decrease
   - At least one maintainer approval required
   - Address all review comments
   - Resolve merge conflicts if any

7. **After Approval**

   - A maintainer will merge your PR
   - Delete your feature branch
   - Pull the latest changes to your fork

## Reporting Bugs

When reporting bugs, please include:

1. **Description** - Clear description of the issue
2. **Steps to Reproduce** - Detailed steps to reproduce the bug
3. **Expected Behavior** - What you expected to happen
4. **Actual Behavior** - What actually happened
5. **Environment**:
   - NetDriver version
   - Python version
   - Operating system
   - Device type/model (if relevant)
6. **Logs** - Relevant log output or error messages
7. **Screenshots** - If applicable

**Use this template:**

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- NetDriver version: 0.3.10
- Python version: 3.12.7
- OS: Ubuntu 22.04
- Device: Cisco Nexus 9000

## Logs

```text
Paste relevant logs here
```

## Screenshots

[Attach screenshots if applicable]

## Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** - Your idea might already be proposed
2. **Be specific** - Clearly describe the feature and use case
3. **Explain the value** - Why would this benefit users?
4. **Consider implementation** - Any thoughts on how it could work?

**Template:**

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Implementation
Any ideas on how this could be implemented?

## Alternatives Considered
What other approaches have you considered?

## Additional Context
Any other relevant information
```

## Project Structure

Understanding the project structure will help you contribute effectively:

```text
netdriver/
├── packages/
│   ├── agent/               # FastAPI agent package
│   ├── core/                # Shared device, logging, plugin primitives
│   ├── discovery/           # Device discovery helpers
│   ├── simunet/             # Simulated SSH device service
│   └── textfsm/             # TextFSM parsing support
├── config/
│   ├── agent/               # Agent runtime configuration
│   └── simunet/             # Simulated device configuration
├── tests/
│   └── integration/         # Cross-package integration tests
├── docs/                    # Project documentation
└── scripts/                 # Development helper scripts
```

## Questions or Need Help?

- Open an [issue](https://github.com/OpenSecFlow/netdriver/issues) for questions
- Check existing [documentation](https://github.com/OpenSecFlow/netdriver/blob/master/README.md)
- Contact the maintainers:
  - <vincent@byntra.se>
  - <bobby@byntra.se>
  - <sam@byntra.se>
  - <mark@byntra.se>

## Recognition

We value all contributions! Contributors will be:

- Listed in our contributors list
- Mentioned in release notes for significant contributions
- Part of a growing community of network automation enthusiasts

Thank you for contributing to NetDriver!
