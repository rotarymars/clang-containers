# clang-containers

A collection of Docker containers, each containing a specific version of the Clang compiler built from the LLVM project source.

## Available Versions

This repository provides Docker images for the following Clang versions:
- Clang 10.0.1 (`llvmorg-10.0.1`)
- Clang 11.1.0 (`llvmorg-11.1.0`)
- Clang 12.0.1 (`llvmorg-12.0.1`)
- Clang 13.0.1 (`llvmorg-13.0.1`)
- Clang 14.0.6 (`llvmorg-14.0.6`)
- Clang 15.0.7 (`llvmorg-15.0.7`)
- Clang 16.0.6 (`llvmorg-16.0.6`)
- Clang 17.0.6 (`llvmorg-17.0.6`)
- Clang 18.1.8 (`llvmorg-18.1.8`)
- Clang 19.1.0 (`llvmorg-19.1.0`)
- Clang 19.1.1 (`llvmorg-19.1.1`)
- Clang 19.1.2 (`llvmorg-19.1.2`)
- Clang 19.1.3 (`llvmorg-19.1.3`)
- Clang 19.1.4 (`llvmorg-19.1.4`)
- Clang 19.1.5 (`llvmorg-19.1.5`)
- Clang 19.1.6 (`llvmorg-19.1.6`)
- Clang 19.1.7 (`llvmorg-19.1.7`)
- Clang 20.1.0 (`llvmorg-20.1.0`)
- Clang 20.1.1 (`llvmorg-20.1.1`)
- Clang 20.1.2 (`llvmorg-20.1.2`)
- Clang 20.1.3 (`llvmorg-20.1.3`)
- Clang 20.1.4 (`llvmorg-20.1.4`)
- Clang 20.1.5 (`llvmorg-20.1.5`)
- Clang 20.1.6 (`llvmorg-20.1.6`)
- Clang 20.1.7 (`llvmorg-20.1.7`)
- Clang 20.1.8 (`llvmorg-20.1.8`)
- Clang 21.1.0 (`llvmorg-21.1.0`)
- Clang 21.1.1 (`llvmorg-21.1.1`)
- Clang 21.1.2 (`llvmorg-21.1.2`)
- Clang 21.1.3 (`llvmorg-21.1.3`)
- Clang 21.1.4 (`llvmorg-21.1.4`)
- Clang 21.1.5 (`llvmorg-21.1.5`)
- Clang 21.1.6 (`llvmorg-21.1.6`)
- Clang 21.1.7 (`llvmorg-21.1.7`)
- Clang 21.1.8 (`llvmorg-21.1.8`)

## Usage

Each container comes with:
- The Clang compiler built from source using clang (self-hosted build)
- CMake and Ninja build tools
- Standard C/C++ library headers
- A `/workspace` directory with a pre-created `build` subdirectory

### Pull and Run

```bash
# Pull a specific version
docker pull ghcr.io/rotarymars/clang:18.1.8

# Run the container and check the clang version
docker run --rm ghcr.io/rotarymars/clang:18.1.8

# Run with an interactive shell
docker run -it --rm ghcr.io/rotarymars/clang:18.1.8 /bin/bash

# Mount your project and build it
docker run -it --rm -v $(pwd):/workspace ghcr.io/rotarymars/clang:18.1.8 /bin/bash
```

### Example: Building a C++ Project

```bash
# Start the container with your source code mounted
docker run -it --rm -v $(pwd):/workspace ghcr.io/rotarymars/clang:18.1.8 /bin/bash

# Inside the container
cd /workspace/build
cmake ..
cmake --build .
```

## Building Images Locally

To build all images locally:

```bash
# Build all images
./build-images.sh

# Build a specific version
docker build -f dockerfiles/Dockerfile.clang-18.1.8 -t ghcr.io/rotarymars/clang:18.1.8 .
```

## Pushing Images

To push images to GitHub Container Registry (requires authentication):

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push all images (uses ghcr.io/rotarymars/clang by default)
./push-images.sh

# Or override the repository name with DOCKER_REPO environment variable
DOCKER_REPO=ghcr.io/your-username/clang ./push-images.sh
```

## GitHub Actions

This repository includes a GitHub Actions workflow that automatically builds and pushes images to GitHub Container Registry (ghcr.io) when changes are pushed to the main branch or when manually triggered.

The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions with the necessary permissions to push to the container registry.

### Parallelization

The workflow parallelizes builds across multiple jobs (3 versions per job) to avoid hitting GitHub Actions' 6-hour timeout limit. With 35 versions, the workflow creates 12 parallel groups. The workflow is automatically generated from `versions.txt` using `generate-workflow.py`.

## Adding New Versions

To add a new Clang version:

1. Add the version number to `versions.txt` (e.g., `19.0.0-rc1`)
2. Create a corresponding Dockerfile: `dockerfiles/Dockerfile.clang-19.0.0-rc1`
3. Regenerate the workflow: `python3 generate-workflow.py > .github/workflows/build-push.yml`
4. Commit and push the changes

The scripts and workflow will automatically pick up the new version.

## Structure

```
.
├── dockerfiles/
│   ├── Dockerfile.clang-10.0.1
│   ├── Dockerfile.clang-11.1.0
│   ├── Dockerfile.clang-12.0.1
│   ├── Dockerfile.clang-13.0.1
│   ├── Dockerfile.clang-14.0.6
│   ├── Dockerfile.clang-15.0.7
│   ├── Dockerfile.clang-16.0.6
│   ├── Dockerfile.clang-17.0.6
│   ├── Dockerfile.clang-18.1.8
│   ├── Dockerfile.clang-19.1.0 through 19.1.7 (8 versions)
│   ├── Dockerfile.clang-20.1.0 through 20.1.8 (9 versions)
│   └── Dockerfile.clang-21.1.0 through 21.1.8 (9 versions)
├── .github/
│   └── workflows/
│       └── build-push.yml
├── build-images.sh
├── push-images.sh
├── generate-workflow.py
├── versions.txt
└── README.md
```

## License

See the LLVM project license at https://llvm.org/LICENSE.txt
