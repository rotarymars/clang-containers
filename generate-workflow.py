#!/usr/bin/env python3
"""
Generate GitHub Actions workflow from versions.txt

The workflow builds each clang version as its own job, but only for versions
whose Dockerfile actually changed (or, on demand, the ones missing from the
registry). Builds are layer-cached in the registry so an unchanged builder
stage is never recompiled.
"""

import os
import sys

def read_versions(filename='versions.txt'):
    """Read versions from versions.txt file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Error: {filename} not found. Please create it with version numbers.")

    with open(filename, 'r') as f:
        versions = [line.strip() for line in f if line.strip()]

    if not versions:
        raise ValueError(f"Error: {filename} is empty. Please add at least one version.")

    return versions

# The build matrix is resolved at run time from versions.txt, so this template
# does not need regenerating whenever a version is added.
WORKFLOW = r'''name: Build and Push Clang Container Images

on:
  push:
    branches:
      - main
    paths:
      - 'dockerfiles/**'
      - 'versions.txt'
  workflow_dispatch:
    inputs:
      versions:
        description: 'changed | missing | all | explicit space separated list'
        required: false
        default: 'missing'

env:
  IMAGE: ghcr.io/${{ github.repository_owner }}/clang

jobs:
  plan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: read
    outputs:
      versions: ${{ steps.plan.outputs.versions }}
      count: ${{ steps.plan.outputs.count }}
      build_latest: ${{ steps.plan.outputs.build_latest }}
      latest: ${{ steps.plan.outputs.latest }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Decide which versions to build
        id: plan
        env:
          MODE: ${{ github.event.inputs.versions || 'changed' }}
          BEFORE: ${{ github.event.before }}
        run: |
          set -euo pipefail
          all_versions() { grep -v '^[[:space:]]*$' versions.txt; }

          # A push with no usable base (new branch, force push) cannot be
          # diffed, so fall back to building whatever the registry lacks.
          if [ "$MODE" = changed ] && { [ -z "$BEFORE" ] || [ "$BEFORE" = "0000000000000000000000000000000000000000" ] || ! git cat-file -e "$BEFORE^{commit}" 2>/dev/null; }; then
            echo "No diffable base commit, falling back to 'missing'"
            MODE=missing
          fi

          case "$MODE" in
            all)
              LIST=$(all_versions)
              ;;
            changed)
              LIST=$(git diff --name-only --diff-filter=d "$BEFORE" "${{ github.sha }}" -- dockerfiles/ \
                     | sed -n 's#^dockerfiles/Dockerfile\.clang-##p')
              ;;
            missing)
              LIST=""
              for v in $(all_versions); do
                if docker buildx imagetools inspect "$IMAGE:$v" >/dev/null 2>&1; then
                  echo "Already published: $v"
                else
                  LIST="$LIST$v"$'\n'
                fi
              done
              ;;
            *)
              LIST=$(printf '%s\n' $MODE)
              ;;
          esac

          # Drop anything that is not a known version with a Dockerfile.
          SELECTED=""
          for v in $LIST; do
            if grep -qxF "$v" versions.txt && [ -f "dockerfiles/Dockerfile.clang-$v" ]; then
              SELECTED="$SELECTED$v"$'\n'
            else
              echo "Skipping unknown version: $v"
            fi
          done

          # Single jq pass so an empty selection yields [] instead of failing.
          JSON=$(printf '%s' "$SELECTED" | jq -R -s -c 'split("\n") | map(select(length > 0))')
          COUNT=$(printf '%s' "$JSON" | jq length)
          LATEST=$(all_versions | tail -n1)

          echo "versions=$JSON" >> "$GITHUB_OUTPUT"
          echo "count=$COUNT" >> "$GITHUB_OUTPUT"
          echo "latest=$LATEST" >> "$GITHUB_OUTPUT"
          echo "build_latest=$(printf '%s' "$JSON" | jq --arg l "$LATEST" 'any(. == $l)')" >> "$GITHUB_OUTPUT"

          echo "Building $COUNT version(s) (mode: $MODE): $JSON" >> "$GITHUB_STEP_SUMMARY"

  build-and-push:
    needs: plan
    if: needs.plan.outputs.count != '0'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    strategy:
      fail-fast: false
      matrix:
        version: ${{ fromJSON(needs.plan.outputs.versions) }}
    # A newer push for the same version supersedes this build; unrelated
    # versions keep running.
    concurrency:
      group: build-clang-${{ matrix.version }}
      cancel-in-progress: true

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push clang-${{ matrix.version }}
        uses: docker/build-push-action@v6
        with:
          context: .
          file: dockerfiles/Dockerfile.clang-${{ matrix.version }}
          platforms: linux/amd64
          tags: ${{ env.IMAGE }}:${{ matrix.version }}
          push: true
          provenance: false
          # Registry cache, not type=gha: the GitHub Actions cache is capped at
          # 10 GB per repository, which a single LLVM build tree can exhaust.
          cache-from: type=registry,ref=${{ env.IMAGE }}:buildcache-${{ matrix.version }}
          cache-to: type=registry,ref=${{ env.IMAGE }}:buildcache-${{ matrix.version }},mode=max,image-manifest=true,oci-mediatypes=true

  tag-latest:
    needs: [plan, build-and-push]
    if: needs.plan.outputs.build_latest == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Tag latest version
        # imagetools retags server side, so no multi-GB pull is needed.
        run: |
          docker buildx imagetools create \
            --tag "$IMAGE:latest" \
            "$IMAGE:${{ needs.plan.outputs.latest }}"
'''

def generate_workflow():
    """Generate GitHub Actions workflow YAML."""
    # Validated so a broken versions.txt fails here rather than in CI.
    read_versions()
    return WORKFLOW

if __name__ == '__main__':
    try:
        print(generate_workflow())
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
