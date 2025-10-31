# Release Scripts

This directory contains scripts to help with the release process.

## release.sh

A convenient script to create and push release tags.

### Usage

```bash
./scripts/release.sh <project> <version>
```

**Parameters:**

- `project`: The project to release (`agent` or `simunet`)
- `version`: Version number in format `X.X.X` (e.g., `0.3.5`)

### Examples

**Release netdriver-agent version 0.3.5:**

```bash
./scripts/release.sh agent 0.3.5
```

**Release netdriver-simunet version 0.4.0:**

```bash
./scripts/release.sh simunet 0.4.0
```

### What it does

1. Validates input parameters
2. Checks prerequisites (git repository, poetry installation)
3. Verifies working directory is clean
4. Verifies the tag doesn't already exist
5. Updates version in `projects/<project>/pyproject.toml` using `poetry version`
6. Commits the version change
7. Creates an annotated git tag (e.g., `agent-0.3.5`)
8. Pushes the commit and tag to remote
9. Triggers the GitHub Actions release workflow

### Release Workflow

Once the tag is pushed, the GitHub Actions workflow will automatically:

1. **Create GitHub Release** with release notes
2. **Run Tests** (pylint + pytest)
3. **Build and Publish to PyPI**
   - Build wheel package
   - Publish to PyPI
   - Upload wheel to GitHub release
4. **Build and Push Docker Image**
   - Build multi-platform image (linux/amd64, linux/arm64)
   - Push to GitHub Container Registry (ghcr.io)
   - Tag with version and `latest`
5. **Verify Publication**
   - Check PyPI package availability
   - Generate summary

### Troubleshooting

**Tag already exists:**

```bash
# Delete local tag
git tag -d agent-0.3.5

# Delete remote tag
git push origin :refs/tags/agent-0.3.5

# Try again
./scripts/release.sh agent 0.3.5
```

**Workflow failed:**

- Check GitHub Actions: <https://github.com/OpenSecFlow/netdriver/actions>
- Review workflow logs for specific errors
- Fix issues and delete/recreate the tag if needed

### Prerequisites

- **Poetry** installed and configured
- **Git** configured and authenticated
- Push permissions to the repository
- **Clean working directory** (no uncommitted changes)
