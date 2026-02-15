#!/bin/bash
set -e

# Repository name for Docker images (GitHub Container Registry)
REPO_NAME="${DOCKER_REPO:-ghcr.io/rotarymars/clang}"

# List of clang versions to push (full version numbers)
VERSIONS=(10.0.1 11.1.0 12.0.1 13.0.1 14.0.6 15.0.7 16.0.6 17.0.6 18.1.8)

echo "Pushing Docker images for clang versions: ${VERSIONS[@]}"

# Check if logged in to GitHub Container Registry
if ! docker info | grep -q "ghcr.io"; then
    echo "Please login to GitHub Container Registry first:"
    echo "  echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin"
    exit 1
fi

for version in "${VERSIONS[@]}"; do
    echo "Pushing ${REPO_NAME}:${version}..."
    docker push "${REPO_NAME}:${version}"
    echo "Successfully pushed ${REPO_NAME}:${version}"
done

# Push the latest tag
echo "Pushing ${REPO_NAME}:latest..."
docker push "${REPO_NAME}:latest"
echo "Successfully pushed ${REPO_NAME}:latest"

echo "All images pushed successfully!"
