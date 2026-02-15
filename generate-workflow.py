#!/usr/bin/env python3
"""
Generate GitHub Actions workflow from versions.txt
This script creates a workflow that parallelizes builds across multiple jobs
to avoid hitting the 6-hour GitHub Actions timeout.
"""

import json
import sys

def read_versions(filename='versions.txt'):
    """Read versions from versions.txt file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def chunk_versions(versions, chunk_size=3):
    """Split versions into chunks for parallel execution."""
    return [versions[i:i + chunk_size] for i in range(0, len(versions), chunk_size)]

def generate_workflow():
    """Generate GitHub Actions workflow YAML."""
    versions = read_versions()
    chunks = chunk_versions(versions)
    
    # Generate matrix includes
    matrix_includes = []
    for i, chunk in enumerate(chunks):
        matrix_includes.append({
            'group': i + 1,
            'versions': ' '.join(chunk)
        })
    
    workflow = f"""name: Build and Push Clang Container Images

on:
  push:
    branches:
      - main
    paths:
      - 'dockerfiles/**'
      - '.github/workflows/build-push.yml'
      - 'versions.txt'
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    strategy:
      fail-fast: false
      matrix:
        include:
{json.dumps(matrix_includes, indent=10)[1:-1]}
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{{{ github.repository_owner }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}
      
      - name: Build and push versions in group ${{{{ matrix.group }}}}
        run: |
          for version in ${{{{ matrix.versions }}}}; do
            echo "Building and pushing clang-$version..."
            docker buildx build \\
              --file "dockerfiles/Dockerfile.clang-$version" \\
              --tag "ghcr.io/${{{{ github.repository_owner }}}}/clang:$version" \\
              --cache-from type=gha,scope=clang-$version \\
              --cache-to type=gha,mode=max,scope=clang-$version \\
              --push \\
              .
            echo "Successfully built and pushed clang-$version"
          done
  
  tag-latest:
    needs: build-and-push
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{{{ github.repository_owner }}}}
          password: ${{{{ secrets.GITHUB_TOKEN }}}}
      
      - name: Tag latest version
        run: |
          LATEST_VERSION=$(tail -n1 versions.txt)
          docker pull ghcr.io/${{{{ github.repository_owner }}}}/clang:$LATEST_VERSION
          docker tag ghcr.io/${{{{ github.repository_owner }}}}/clang:$LATEST_VERSION ghcr.io/${{{{ github.repository_owner }}}}/clang:latest
          docker push ghcr.io/${{{{ github.repository_owner }}}}/clang:latest
"""
    
    return workflow

if __name__ == '__main__':
    print(generate_workflow())
