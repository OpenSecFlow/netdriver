# Quick Start Guide: Publishing to PyPI

This guide will help you quickly set up and publish your packages to PyPI.

## Prerequisites

- GitHub repository with the workflows
- PyPI account (https://pypi.org/account/register/)
- TestPyPI account (https://test.pypi.org/account/register/) - optional but recommended

## Step 1: Get PyPI Tokens

### For PyPI

1. Visit https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Fill in:
   - Token name: `GitHub Actions - NetDriver`
   - Scope: `Entire account` (or select specific project after first upload)
4. Click "Add token"
5. **Copy the token** (starts with `pypi-...`) - you won't see it again!

### For TestPyPI (Recommended for testing)

1. Visit https://test.pypi.org/manage/account/token/
2. Follow same steps as above
3. Copy the token

## Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click "New repository secret"
4. Add two secrets:

   **Secret 1:**
   - Name: `PYPI_API_TOKEN`
   - Secret: Paste your PyPI token

   **Secret 2:**
   - Name: `TEST_PYPI_API_TOKEN`
   - Secret: Paste your TestPyPI token

## Step 3: Choose Your Workflow

### Option A: Standard Workflow (Recommended for first-time)

Use `publish-pypi.yml` - installs everything on-the-fly

**No additional setup needed!**

### Option B: Docker-based Workflow (Faster)

Use `publish-pypi-docker.yml` - uses pre-built image

**Additional setup:**

1. Build the CI image first:
   ```bash
   # Go to Actions → "Build CI Image" → Run workflow
   # Or build locally and push
   docker build -t ghcr.io/opensecflow/netdriver/ci:latest -f .github/Dockerfile.ci .
   docker push ghcr.io/opensecflow/netdriver/ci:latest
   ```

2. Update your workflow to use the image (already configured in `publish-pypi-docker.yml`)

## Step 4: Test Publishing (Recommended)

Before publishing to production PyPI, test with TestPyPI:

### Manual Test

1. Go to **Actions** → **"Publish to PyPI"**
2. Click **"Run workflow"**
3. Select:
   - Branch: `master`
   - Environment: **`testpypi`**
   - Projects: **`all`**
4. Click **"Run workflow"**

### Verify on TestPyPI

1. Check your packages:
   - https://test.pypi.org/project/netdriver-agent/
   - https://test.pypi.org/project/netdriver-simunet/

2. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ netdriver-agent
   ```

## Step 5: Publish to Production

### Option 1: Manual Publishing

1. Go to **Actions** → **"Publish to PyPI"**
2. Click **"Run workflow"**
3. Select:
   - Branch: `master`
   - Environment: **`pypi`** (NOT testpypi!)
   - Projects: **`all`**
4. Click **"Run workflow"**

### Option 2: Automatic Publishing (via Git Tags)

```bash
# 1. Update version numbers
poetry version -P projects/agent 0.3.1
poetry version -P projects/simunet 0.3.1

# 2. Commit changes
git add projects/*/pyproject.toml
git commit -m "chore: bump version to 0.3.1"
git push

# 3. Create and push tag
git tag v0.3.1
git push origin v0.3.1
```

The `release.yml` workflow will automatically:
- ✅ Create a GitHub Release
- ✅ Build both packages
- ✅ Publish to PyPI
- ✅ Attach wheel files to the release

## Step 6: Verify Publication

1. Check on PyPI:
   - https://pypi.org/project/netdriver-agent/
   - https://pypi.org/project/netdriver-simunet/

2. Test installation:
   ```bash
   pip install netdriver-agent
   pip install netdriver-simunet
   ```

## Common Issues

### "HTTP Error 403: Authentication failed"

**Solution:** Check that GitHub secrets are correctly configured

```bash
# Verify secrets exist in: Settings → Secrets and variables → Actions
# Should see:
# - PYPI_API_TOKEN
# - TEST_PYPI_API_TOKEN
```

### "HTTP Error 400: Bad Request - duplicate keys"

**Solution:** Version already exists on PyPI. Bump the version:

```bash
poetry version -P projects/agent patch
poetry version -P projects/simunet patch
# Then rebuild and publish
```

### Workflow fails with "Poetry not found"

**Solution:**
- If using standard workflow: Check Poetry installation step
- If using Docker workflow: Build the CI image first

### Package shows as "0 B" or malformed

**Solution:** Check build output - Polylith path warnings are normal, verify wheel contents:

```bash
unzip -l projects/agent/dist/netdriver_agent-*.whl
```

## Best Practices

### Version Management

✅ **DO:**
- Keep version numbers in sync across `projects/agent/pyproject.toml` and `projects/simunet/pyproject.toml`
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Test on TestPyPI before production

❌ **DON'T:**
- Publish the same version twice
- Skip testing on TestPyPI
- Use local version identifiers for production (e.g., `0.3.0+local`)

### Release Process

1. Develop features on branches
2. Test locally: `poetry build -P projects/agent`
3. Create PR and verify build test passes
4. Merge to master
5. Test on TestPyPI
6. Tag and release to production PyPI

### Security

- 🔒 Never commit tokens to repository
- 🔒 Use scoped tokens when possible
- 🔒 Rotate tokens regularly
- 🔒 Use GitHub environments for additional approval gates

## Next Steps

- Set up automated testing before publishing
- Configure GitHub environments for approval workflows
- Set up branch protection rules
- Consider using PyPI Trusted Publishers (no tokens needed!)

## Need Help?

- 📖 Full documentation: `.github/workflows/README.md`
- 🐛 Report issues: https://github.com/OpenSecFlow/netdriver/issues
- 📝 PyPI Help: https://pypi.org/help/
- 🎯 GitHub Actions: https://docs.github.com/en/actions
