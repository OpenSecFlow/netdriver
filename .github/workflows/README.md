# GitHub Workflows for NetDriver

This directory contains GitHub Actions workflows for automated building, testing, and publishing of NetDriver packages.

## Workflows

### 1. Build (`build.yml`)

**Trigger**: Pull requests and pushes to master/main branch

**Purpose**: Validates that packages can be built successfully

**What it does**:

- Builds both `netdriver-agent` and `netdriver-simunet` packages
- Verifies package metadata using `twine check`
- Uploads build artifacts for inspection
- Runs on Python 3.12

**Usage**: Automatically runs on PR creation and commits

### 2. Publish to PyPI (`publish-pypi.yml`)

**Trigger**:

- Automatically when a GitHub release is published
- Manually via workflow dispatch

**Purpose**: Publishes packages to PyPI or TestPyPI

**What it does**:

- Uses pre-built Docker container with Poetry installed
- Builds wheel packages for selected projects
- Publishes to PyPI or TestPyPI
- Uploads build artifacts

**Manual Usage**:

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select:
   - **Environment**: `testpypi` or `pypi`
   - **Projects**: `all`, `agent`, `simunet`, or `agent,simunet`
4. Click "Run workflow"

**Note**: Requires the CI Docker image to be built first (see section 5 below)

### 3. Release and Publish

The project supports independent release workflows for agent and simunet:

#### 3.1. Independent Agent Release (`release-agent.yml`)

**Trigger**: When an agent-prefixed tag is pushed (e.g., `agent-1.0.0`)

**Purpose**: Creates GitHub release and publishes ONLY agent package to PyPI

**What it does**:

- Creates a GitHub release for agent
- Builds only agent package
- Publishes to PyPI
- Builds and pushes agent Docker image to GHCR
- Attaches wheel file to the release

**Usage**:

```bash
# Update agent version in pyproject.toml (optional, will be updated by workflow)
poetry version 1.0.0 -C projects/agent

# Commit version changes (optional)
git add projects/agent/pyproject.toml
git commit -m "chore: bump agent version to 1.0.0"

# Create and push agent tag
git tag agent-1.0.0
git push origin master
git push origin agent-1.0.0
```

#### 3.2. Independent Simunet Release (`release-simunet.yml`)

**Trigger**: When a simunet-prefixed tag is pushed (e.g., `simunet-2.5.0`)

**Purpose**: Creates GitHub release and publishes ONLY simunet package to PyPI

**What it does**:

- Creates a GitHub release for simunet
- Builds only simunet package
- Publishes to PyPI
- Builds and pushes simunet Docker image to GHCR
- Attaches wheel file to the release

**Usage**:

```bash
# Update simunet version in pyproject.toml (optional, will be updated by workflow)
poetry version 2.5.0 -C projects/simunet

# Commit version changes (optional)
git add projects/simunet/pyproject.toml
git commit -m "chore: bump simunet version to 2.5.0"

# Create and push simunet tag
git tag simunet-2.5.0
git push origin master
git push origin simunet-2.5.0
```

## Setup Requirements

### 1. Configure PyPI Tokens

Add the following secrets to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Description | Get From |
|------------|-------------|----------|
| `PYPI_API_TOKEN` | PyPI API token | <https://pypi.org/manage/account/token/> |
| `TEST_PYPI_API_TOKEN` | TestPyPI API token | <https://test.pypi.org/manage/account/token/> |

**Creating PyPI Tokens**:

1. **For PyPI**:
   - Visit <https://pypi.org/manage/account/token/>
   - Click "Add API token"
   - Token name: `GitHub Actions - NetDriver`
   - Scope: `Entire account` (or specific project after first upload)
   - Copy the token (starts with `pypi-...`)

2. **For TestPyPI**:
   - Visit <https://test.pypi.org/manage/account/token/>
   - Follow same steps as above

3. **Add to GitHub**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Secret: Paste your token
   - Repeat for `TEST_PYPI_API_TOKEN`

### 2. Alternative: Trusted Publishing (Recommended)

GitHub Actions supports PyPI's trusted publishing (no token needed):

1. Go to PyPI → Your account → Publishing
2. Add publisher for each package:
   - **Owner**: Your GitHub username/organization
   - **Repository**: `netdriver`
   - **Workflow**: `release-agent.yml` (for netdriver-agent)
   - **Workflow**: `release-simunet.yml` (for netdriver-simunet)
   - **Environment**: `pypi`

3. Both workflows are already configured with `id-token: write` for trusted publishing

## Release Process

### Agent Release

Use this when you only need to release the agent:

1. **Update version number** (optional):

   ```bash
   poetry version 1.0.0 -C projects/agent
   ```

2. **Commit changes** (optional):

   ```bash
   git add projects/agent/pyproject.toml
   git commit -m "chore: bump agent version to 1.0.0"
   git push origin master
   ```

3. **Create and push tag**:

   ```bash
   git tag agent-1.0.0
   git push origin agent-1.0.0
   ```

4. **Workflow will automatically**:
   - Update agent version to 1.0.0
   - Create GitHub release for agent
   - Build agent package
   - Publish to PyPI
   - Build and push agent Docker image to GHCR

### Simunet Release

Use this when you need to release simunet:

1. **Update version number** (optional):

   ```bash
   poetry version 2.5.0 -C projects/simunet
   ```

2. **Commit changes** (optional):

   ```bash
   git add projects/simunet/pyproject.toml
   git commit -m "chore: bump simunet version to 2.5.0"
   git push origin master
   ```

3. **Create and push tag**:

   ```bash
   git tag simunet-2.5.0
   git push origin simunet-2.5.0
   ```

4. **Workflow will automatically**:
   - Update simunet version to 2.5.0
   - Create GitHub release for simunet
   - Build simunet package
   - Publish to PyPI
   - Build and push simunet Docker image to GHCR

### Test Release

To test publishing before official release:

1. **Manual workflow dispatch**:
   - Go to Actions → "Publish to PyPI"
   - Run workflow with:
     - Environment: `testpypi`
     - Projects: `all`

2. **Or use CLI**:

   ```bash
   poetry publish -P projects/agent -r testpypi
   poetry publish -P projects/simunet -r testpypi
   ```

3. **Verify on TestPyPI**:
   - <https://test.pypi.org/project/netdriver-agent/>
   - <https://test.pypi.org/project/netdriver-simunet/>

4. **Test installation**:

   ```bash
   pip install --index-url https://test.pypi.org/simple/ netdriver-agent
   ```

## Troubleshooting

### Build fails with "not in the subpath" warning

This is expected in Polylith architecture and can be ignored. The build will still succeed.

### "HTTP Error 400: Bad Request - duplicate keys"

This means the version already exists on PyPI. Solutions:

- Bump the version number
- Use `--skip-existing` flag (already in workflows)

### "HTTP Error 403: Authentication failed"

Check that:

- GitHub secrets are correctly configured
- Tokens haven't expired
- Token has correct permissions

### Package not found after publishing

- PyPI can take a few minutes to update indexes
- Check package name is correct (use underscore vs hyphen)
- Verify on PyPI website first

## Docker Image Publishing

All release workflows automatically build and publish Docker images to GitHub Container Registry (GHCR).

### Docker Image Tags

Each release creates multiple tags for flexibility:

- `latest` - Always points to the most recent release
- `<version>` - Specific version (e.g., `1.0.0`)
- `<major>.<minor>` - Minor version (e.g., `1.0`)
- `<major>` - Major version (e.g., `1`)

### Multi-Architecture Support

Docker images are built for multiple architectures:

- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

### Image Locations

| Package | Registry | Image Name |
|---------|----------|------------|
| Agent | GHCR | `ghcr.io/opensecflow/netdriver/netdriver-agent` |
| Simunet | GHCR | `ghcr.io/opensecflow/netdriver/netdriver-simunet` |

### Using Docker Images

**Agent:**
```bash
# Pull latest
docker pull ghcr.io/opensecflow/netdriver/netdriver-agent:latest

# Pull specific version
docker pull ghcr.io/opensecflow/netdriver/netdriver-agent:1.0.0

# Run agent
docker run -d -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-agent:latest
```

**Simunet:**
```bash
# Pull latest
docker pull ghcr.io/opensecflow/netdriver/netdriver-simunet:latest

# Pull specific version
docker pull ghcr.io/opensecflow/netdriver/netdriver-simunet:2.5.0

# Run simunet with host network mode (SSH ports bind directly to host)
docker run -d --network host \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/opensecflow/netdriver/netdriver-simunet:latest
```

**Note**: Simunet uses host network mode (`--network host`) to bind SSH ports (default 2201-2220) directly to the host. This is required for proper SSH server functionality.

### Docker Image Authentication

Docker images are public and can be pulled without authentication. For private repositories, authenticate first:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## Tag Naming Convention

The project uses prefixed tag patterns for independent releases:

| Tag Pattern | Workflow | Releases | Artifacts |
|------------|----------|----------|-----------|
| `agent-1.0.0` | `release-agent.yml` | Agent only | PyPI package + Docker image |
| `simunet-2.5.0` | `release-simunet.yml` | Simunet only | PyPI package + Docker image |

## Using Pre-built Docker Images

### 5. Build CI Image (`build-ci-image.yml`)

**Purpose**: Creates a Docker image with Poetry and Python pre-installed for faster CI/CD

**What it includes**:

- Python 3.12
- Poetry with multiproject and polylith plugins
- Git and essential build tools

**Building the image**:

```bash
# Build locally
docker build -t netdriver-ci -f .github/Dockerfile.ci .

# Or trigger GitHub workflow to build and push to GHCR
# Go to Actions → "Build CI Image" → Run workflow
```

**Using the custom image in workflows**:

The `publish-pypi.yml` workflow uses this approach:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/${{ github.repository }}/python-poetry:3.12
    steps:
      - uses: actions/checkout@v4
      # Poetry and plugins are already installed!
      - run: poetry build-project -C projects/agent
```

**Benefits of using Docker image**:

- ⚡ **Faster**: No need to install Poetry and plugins on every run
- 🔒 **Consistent**: Same environment across all workflows
- 💾 **Cacheable**: Image layers are cached by Docker
- 🎯 **Reproducible**: Exact same versions every time

**Image locations**:

- GitHub Container Registry: `ghcr.io/opensecflow/netdriver/python-poetry:3.12`
- Available tags: `latest`, `master`, `<branch>-<sha>`

**Benefits**:

- ⚡ **Faster**: Setup in ~30 seconds vs ~2-3 minutes
- 🔒 **Consistent**: Same environment across all workflows
- 💾 **Cacheable**: Docker layer caching
- 🎯 **Reproducible**: Exact versions every time

## Project Structure

```text
netdriver/
├── .github/
│   ├── Dockerfile.ci               # CI/CD Docker image
│   └── workflows/
│       ├── build-ci-image.yml      # Build Docker image
│       ├── build.yml               # PR/push build validation
│       ├── publish-pypi.yml        # Manual PyPI publishing
│       ├── release-agent.yml       # Agent release workflow
│       └── release-simunet.yml     # Simunet release workflow
├── bases/
│   └── netdriver/
│       ├── agent/                  # REST API service
│       └── simunet/                # Simulation network
├── components/                     # Shared components
└── projects/
    ├── agent/
    │   └── pyproject.toml
    └── simunet/
        └── pyproject.toml
```

## Advanced: Custom Docker Images

If you want to use your own Docker image:

### 1. Build and push your image

```bash
# Build
docker build -t your-registry/netdriver-ci:latest -f .github/Dockerfile.ci .

# Push to your registry
docker push your-registry/netdriver-ci:latest
```

### 2. Update workflow file

Edit `publish-pypi.yml`:

```yaml
container:
  image: your-registry/netdriver-ci:latest
  credentials:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

### 3. Verify Poetry is available

Poetry and plugins are pre-installed, so you can use them directly:

```yaml
- name: Verify Poetry installation
  run: |
    poetry --version
    poetry self show plugins
```

## References

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Polylith Plugin](https://github.com/DavidVujic/poetry-polylith-plugin)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Actions - Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
