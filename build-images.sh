#!/bin/bash
set -e

# Repository name for Docker images (GitHub Container Registry)
REPO_NAME="${DOCKER_REPO:-ghcr.io/rotarymars/clang}"

# Read clang versions from versions.txt (filter out empty lines)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mapfile -t VERSIONS < <(grep -v '^[[:space:]]*$' "${SCRIPT_DIR}/versions.txt")

echo "Building Docker images for clang versions: ${VERSIONS[@]}"

for version in "${VERSIONS[@]}"; do
    echo "Building clang-${version}..."
    docker build -f "dockerfiles/Dockerfile.clang-${version}" -t "${REPO_NAME}:${version}" .
    echo "Successfully built ${REPO_NAME}:${version}"
done

# Tag the latest version (POSIX-safe array index)
LATEST_VERSION="${VERSIONS[${#VERSIONS[@]}-1]}"
docker tag "${REPO_NAME}:${LATEST_VERSION}" "${REPO_NAME}:latest"
echo "Tagged ${REPO_NAME}:${LATEST_VERSION} as ${REPO_NAME}:latest"

echo "All images built successfully!"
echo "To push images, run: ./push-images.sh"
