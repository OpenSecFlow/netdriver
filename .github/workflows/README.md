# GitHub Workflows for NetDriver

This directory contains GitHub Actions workflows for automated building, testing, and publishing of NetDriver packages.

## Workflows

### 1. Build Test (`build-test.yml`)

**Trigger**: Pull requests and pushes to master/main branch

**Purpose**: Validates that packages can be built successfully

**What it does**:

- Builds both `netdriver-agent` and `netdriver-simunet` packages
- Verifies package metadata using `twine check`
- Uploads build artifacts for inspection
- Runs on Python 3.12

**Usage**: Automatically runs on PR creation and commits

### 2. Publish to PyPI (`publish-pypi.yml` / `publish-pypi-docker.yml`)

**Trigger**:

- Automatically when a GitHub release is published
- Manually via workflow dispatch

**Purpose**: Publishes packages to PyPI or TestPyPI

**What it does**:

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

**Two versions available**:

- **`publish-pypi.yml`**: Standard workflow, installs Poetry and Python on-the-fly
- **`publish-pypi-docker.yml`**: Uses pre-built Docker container (faster)

### 3. Release and Publish (`release.yml`)

**Trigger**: When a version tag is pushed (e.g., `v0.3.0`)

**Purpose**: Creates GitHub release and publishes to PyPI

**What it does**:

- Creates a GitHub release from the tag
- Builds both packages
- Publishes to PyPI
- Attaches wheel files to the release

**Usage**:

```bash
# Bump version in pyproject.toml files
poetry version patch  # or minor, major

# Commit version changes
git add projects/*/pyproject.toml
git commit -m "chore: bump version to 0.3.1"

# Create and push tag
git tag v0.3.1
git push origin master
git push origin v0.3.1
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
2. Add publisher:
   - **Owner**: Your GitHub username/organization
   - **Repository**: `netdriver`
   - **Workflow**: `release.yml`
   - **Environment**: `pypi`

3. Update workflow to use trusted publishing (already configured with `id-token: write`)

## Release Process

### Standard Release

1. **Update version numbers**:

   ```bash
   # From repository root
   poetry version -P projects/agent 0.3.1
   poetry version -P projects/simunet 0.3.1

   # Or use Poetry's bump commands
   poetry version -P projects/agent patch  # 0.3.0 → 0.3.1
   poetry version -P projects/agent minor  # 0.3.0 → 0.4.0
   poetry version -P projects/agent major  # 0.3.0 → 1.0.0
   ```

2. **Update CHANGELOG.md** (if exists)

3. **Commit changes**:

   ```bash
   git add projects/*/pyproject.toml
   git commit -m "chore: bump version to 0.3.1"
   git push origin master
   ```

4. **Create and push tag**:

   ```bash
   git tag v0.3.1
   git push origin v0.3.1
   ```

5. **Workflow will automatically**:
   - Create GitHub release
   - Build packages
   - Publish to PyPI

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

## Using Pre-built Docker Images

### 4. Build CI Image (`build-ci-image.yml`)

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

The `publish-pypi-docker.yml` workflow demonstrates usage:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/opensecflow/netdriver/ci:latest
    steps:
      - uses: actions/checkout@v4
      # Poetry and plugins are already installed!
      - run: poetry build -P projects/agent
```

**Benefits of using Docker image**:

- ⚡ **Faster**: No need to install Poetry and plugins on every run
- 🔒 **Consistent**: Same environment across all workflows
- 💾 **Cacheable**: Image layers are cached by Docker
- 🎯 **Reproducible**: Exact same versions every time

**Image locations**:

- GitHub Container Registry: `ghcr.io/opensecflow/netdriver/ci:latest`
- Available tags: `latest`, `master`, `<branch>-<sha>`

### Workflow Comparison

| Feature | Standard (`publish-pypi.yml`) | Docker (`publish-pypi-docker.yml`) |
|---------|------------------------------|-----------------------------------|
| Setup time | ~2-3 minutes | ~30 seconds |
| Python/Poetry | Installed each run | Pre-installed in image |
| Cache | Uses GitHub Actions cache | Uses Docker layer cache |
| Flexibility | More flexible | Faster but less flexible |
| Best for | Development/testing | Production releases |

## Project Structure

```text
netdriver/
├── .github/
│   ├── Dockerfile.ci               # CI/CD Docker image
│   └── workflows/
│       ├── build-ci-image.yml      # Build Docker image
│       ├── build-test.yml          # PR/push build validation
│       ├── publish-pypi.yml        # Standard publishing
│       ├── publish-pypi-docker.yml # Docker-based publishing
│       └── release.yml             # Tag-based release
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

Edit `publish-pypi-docker.yml`:

```yaml
container:
  image: your-registry/netdriver-ci:latest
  credentials:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

### 3. Skip Poetry installation

Since Poetry is pre-installed, remove or comment out:

```yaml
# - name: Install Poetry and plugins  # Already in image
#   run: pip install poetry ...
```

## References

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Polylith Plugin](https://github.com/DavidVujic/poetry-polylith-plugin)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Actions - Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
