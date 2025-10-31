#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 <project> <version>

Create a release for NetDriver projects.

Arguments:
  project     Project to release: agent or simunet
  version     Version number (e.g., 0.3.5)

Examples:
  $0 agent 0.3.5
  $0 simunet 0.4.0

This script will:
  1. Update version in pyproject.toml using poetry
  2. Commit version changes
  3. Create a git tag (agent-X.X.X or simunet-X.X.X)
  4. Push changes and tag to trigger the release workflow
EOF
    exit 1
}

# Check arguments
if [ $# -ne 2 ]; then
    print_error "Invalid number of arguments"
    usage
fi

PROJECT=$1
VERSION=$2

# Validate project
if [[ "$PROJECT" != "agent" && "$PROJECT" != "simunet" ]]; then
    print_error "Invalid project: $PROJECT"
    print_error "Project must be 'agent' or 'simunet'"
    exit 1
fi

# Validate version format (X.X.X)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format: $VERSION"
    print_error "Version must be in format X.X.X (e.g., 0.3.5)"
    exit 1
fi

TAG_NAME="${PROJECT}-${VERSION}"

print_info "Release Configuration"
echo "  Project: $PROJECT"
echo "  Version: $VERSION"
echo "  Tag:     $TAG_NAME"
echo

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    print_error "Poetry is not installed"
    print_error "Install it from: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory has uncommitted changes"
    print_error "Please commit or stash your changes before creating a release"
    exit 1
fi

# Check if tag already exists
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    print_error "Tag $TAG_NAME already exists"
    echo
    print_info "To delete the tag locally and remotely, run:"
    echo "  git tag -d $TAG_NAME"
    echo "  git push origin :refs/tags/$TAG_NAME"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"

# Confirm release
echo
print_warning "This will update version, commit, create tag, and push to remote"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Aborted"
    exit 1
fi

# Update version in pyproject.toml
echo
print_info "Updating version in projects/${PROJECT}/pyproject.toml to ${VERSION}..."
poetry version "$VERSION" -C "projects/${PROJECT}"
print_success "Version updated"

# Commit version changes
print_info "Committing version changes..."
git add "projects/${PROJECT}/pyproject.toml"
git commit -m "chore: bump ${PROJECT} version to ${VERSION}"
print_success "Version changes committed"

# Create tag
print_info "Creating tag $TAG_NAME..."
git tag -a "$TAG_NAME" -m "Release $PROJECT $VERSION"
print_success "Tag created"

# Push changes and tag
print_info "Pushing changes and tag to remote..."
git push origin "$CURRENT_BRANCH"
git push origin "$TAG_NAME"
print_success "Changes and tag pushed"

echo
print_success "Release initiated successfully!"
echo
print_info "Monitor the release workflow at:"
echo "  https://github.com/OpenSecFlow/netdriver/actions"
echo
print_info "Once the workflow completes, the release will be available at:"
echo "  https://github.com/OpenSecFlow/netdriver/releases/tag/$TAG_NAME"
echo
print_info "The package will be published to PyPI as:"
echo "  pip install netdriver-${PROJECT}==${VERSION}"
