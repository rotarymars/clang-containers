# clang-containers

[![Build and Push Clang Container Images](https://github.com/rotarymars/clang-containers/actions/workflows/build-push.yml/badge.svg)](https://github.com/rotarymars/clang-containers/actions/workflows/build-push.yml)

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
- The matching `libc++`, `libc++abi` and `libunwind`, built from the same LLVM source tree
- CMake and Ninja build tools
- Standard C/C++ library headers (libstdc++ remains the default)
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

### Using libc++

Every image ships the `libc++` that matches its Clang version. libstdc++ stays
the default standard library; opt into libc++ per compilation:

```bash
clang++ -stdlib=libc++ -std=c++20 main.cpp -o main
```

With CMake:

```bash
cmake -DCMAKE_CXX_FLAGS=-stdlib=libc++ ..
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

### What gets built

A `plan` job decides the build matrix at run time, so a push does not rebuild
every version:

- **push to main** — builds only the versions whose `dockerfiles/Dockerfile.clang-*`
  changed in that push.
- **manual run** — the `versions` input accepts `missing` (default; builds only
  what is absent from ghcr.io), `changed`, `all`, or an explicit space separated
  list such as `20.1.8 21.1.8`.

### Caching

Each version keeps a `mode=max` registry layer cache at
`ghcr.io/<owner>/clang:buildcache-<version>`. An unchanged builder stage is
restored from there instead of recompiling LLVM, so edits to the runtime stage
are cheap. Registry cache is used rather than `type=gha` because the GitHub
Actions cache is capped at 10 GB per repository, which a single LLVM build tree
can exhaust.

Each build is scoped to a per-version concurrency group, so a newer push for the
same version cancels the superseded run while unrelated versions continue.

The workflow resolves versions from `versions.txt` at run time, so it only needs
regenerating when `generate-workflow.py` itself changes.

## Adding New Versions

To add a new Clang version:

1. Add the version number to `versions.txt` (e.g., `19.0.0-rc1`)
2. Generate Dockerfiles: `./generate-dockerfiles.py`
3. Commit and push the changes

The workflow reads `versions.txt` at run time and builds the new version's
Dockerfile because it is new in the push.

### Generating Dockerfiles

The `generate-dockerfiles.py` script reads `versions.txt` and generates all Dockerfiles automatically:

```bash
./generate-dockerfiles.py
```

This ensures consistency across all Dockerfiles and automatically:
- Selects the appropriate Ubuntu version (20.04 for LLVM 10-12, 22.04 for LLVM 13+)
- Configures the correct libstdc++ version for each Ubuntu release
- Builds `libc++`/`libc++abi`/`libunwind` from the same source tree, via
  `LLVM_ENABLE_RUNTIMES` for LLVM 13+ and `LLVM_ENABLE_PROJECTS` for earlier
  releases, which predate the runtimes build
- Uses `ln -sf` to safely create compiler symlinks (avoiding failures if they already exist)

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
├── generate-dockerfiles.py
├── generate-workflow.py
├── versions.txt
└── README.md
```

## License

See the LLVM project license at https://llvm.org/LICENSE.txt
