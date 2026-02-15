#!/bin/bash
set -e

# Repository name for Docker images
REPO_NAME="${DOCKER_REPO:-rotarymars/clang}"

# List of clang versions to build
VERSIONS=(10 11 12 13 14 15 16 17 18)

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
