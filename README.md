# clang-containers

A collection of Docker containers, each containing a specific version of the Clang compiler built from the LLVM project source.

## Available Versions

This repository provides Docker images for the following Clang versions:
- Clang 10 (`llvmorg-10.0.1`)
- Clang 11 (`llvmorg-11.1.0`)
- Clang 12 (`llvmorg-12.0.1`)
- Clang 13 (`llvmorg-13.0.1`)
- Clang 14 (`llvmorg-14.0.6`)
- Clang 15 (`llvmorg-15.0.7`)
- Clang 16 (`llvmorg-16.0.6`)
- Clang 17 (`llvmorg-17.0.6`)
- Clang 18 (`llvmorg-18.1.8`)

## Usage

Each container comes with:
- The Clang compiler built from source
- CMake and Ninja build tools
- A `/workspace` directory with a pre-created `build` subdirectory

### Pull and Run

```bash
# Pull a specific version
docker pull rotarymars/clang:18

# Run the container and check the clang version
docker run --rm rotarymars/clang:18

# Run with an interactive shell
docker run -it --rm rotarymars/clang:18 /bin/bash

# Mount your project and build it
docker run -it --rm -v $(pwd):/workspace rotarymars/clang:18 /bin/bash
```

### Example: Building a C++ Project

```bash
# Start the container with your source code mounted
docker run -it --rm -v $(pwd):/workspace rotarymars/clang:18 /bin/bash

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
docker build -f dockerfiles/Dockerfile.clang-18 -t rotarymars/clang:18 .
```

## Pushing Images

To push images to Docker Hub (requires authentication):

```bash
# Login to Docker Hub
docker login

# Push all images
./push-images.sh
```

## GitHub Actions

This repository includes a GitHub Actions workflow that automatically builds and pushes images to Docker Hub when changes are pushed to the main branch or when manually triggered.

Required secrets:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

## Structure

```
.
├── dockerfiles/
│   ├── Dockerfile.clang-10
│   ├── Dockerfile.clang-11
│   ├── Dockerfile.clang-12
│   ├── Dockerfile.clang-13
│   ├── Dockerfile.clang-14
│   ├── Dockerfile.clang-15
│   ├── Dockerfile.clang-16
│   ├── Dockerfile.clang-17
│   └── Dockerfile.clang-18
├── .github/
│   └── workflows/
│       └── build-push.yml
├── build-images.sh
├── push-images.sh
└── README.md
```

## License

See the LLVM project license at https://llvm.org/LICENSE.txt
