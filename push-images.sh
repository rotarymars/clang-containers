#!/bin/bash
set -e

# Repository name for Docker images
REPO_NAME="${DOCKER_REPO:-rotarymars/clang}"

# List of clang versions to push
VERSIONS=(10 11 12 13 14 15 16 17 18)

echo "Pushing Docker images for clang versions: ${VERSIONS[@]}"

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo "Please login to Docker Hub first: docker login"
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
