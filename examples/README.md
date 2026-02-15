# Example Usage

This directory contains a simple example to test the Clang container.

## Building the Example

```bash
# From the repository root, run the container with the repo mounted
docker run -it --rm -v $(pwd):/workspace ghcr.io/rotarymars/clang:18.1.8 /bin/bash

# Inside the container
cd /workspace/examples
mkdir -p build && cd build
cmake ..
cmake --build .
./hello
```

Expected output:
```
Hello from Clang container!
```
