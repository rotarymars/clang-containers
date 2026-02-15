#!/bin/bash
set -e

# Repository name for Docker images (GitHub Container Registry)
REPO_NAME="${DOCKER_REPO:-ghcr.io/rotarymars/clang}"

# List of clang versions to build (full version numbers)
VERSIONS=(10.0.1 11.1.0 12.0.1 13.0.1 14.0.6 15.0.7 16.0.6 17.0.6 18.1.8)

echo "Building Docker images for clang versions: ${VERSIONS[@]}"

for version in "${VERSIONS[@]}"; do
    echo "Building clang-${version}..."
    docker build -f "dockerfiles/Dockerfile.clang-${version}" -t "${REPO_NAME}:${version}" .
    echo "Successfully built ${REPO_NAME}:${version}"
done

# Tag the latest version
LATEST_VERSION="${VERSIONS[-1]}"
docker tag "${REPO_NAME}:${LATEST_VERSION}" "${REPO_NAME}:latest"
echo "Tagged ${REPO_NAME}:${LATEST_VERSION} as ${REPO_NAME}:latest"

echo "All images built successfully!"
echo "To push images, run: ./push-images.sh"
