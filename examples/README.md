# Example Usage

This directory contains a simple example to test the Clang container.

## Building the Example

```bash
# Run the container with this example mounted
docker run -it --rm -v $(pwd):/workspace rotarymars/clang:18 /bin/bash

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
