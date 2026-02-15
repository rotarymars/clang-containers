#!/bin/bash
set -e

# Repository name for Docker images (GitHub Container Registry)
REPO_NAME="${DOCKER_REPO:-ghcr.io/rotarymars/clang}"

# Read clang versions from versions.txt
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mapfile -t VERSIONS < "${SCRIPT_DIR}/versions.txt"

echo "Pushing Docker images for clang versions: ${VERSIONS[@]}"

for version in "${VERSIONS[@]}"; do
    echo "Pushing ${REPO_NAME}:${version}..."
    docker push "${REPO_NAME}:${version}"
    echo "Successfully pushed ${REPO_NAME}:${version}"
done

# Ensure the latest tag exists locally; if not, tag the last version as latest
LATEST_TAG="${REPO_NAME}:latest"
if ! docker image inspect "${LATEST_TAG}" >/dev/null 2>&1; then
    LAST_VERSION="${VERSIONS[${#VERSIONS[@]}-1]}"
    echo "\"latest\" tag not found locally; tagging ${REPO_NAME}:${LAST_VERSION} as ${LATEST_TAG}..."
    docker tag "${REPO_NAME}:${LAST_VERSION}" "${LATEST_TAG}"
fi

# Push the latest tag
echo "Pushing ${LATEST_TAG}..."
docker push "${LATEST_TAG}"
echo "Successfully pushed ${LATEST_TAG}"

echo "All images pushed successfully!"
