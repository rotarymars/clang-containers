#!/usr/bin/env python3
"""
Generate Dockerfiles from versions.txt
This script reads the versions.txt file and generates a Dockerfile for each version.
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

def get_ubuntu_version(version):
    """Determine Ubuntu version based on LLVM version."""
    # Extract major version number
    major_version = int(version.split('.')[0])
    
    # Versions 10, 11, 12 use Ubuntu 20.04
    # Versions 13 and above use Ubuntu 22.04
    if major_version <= 12:
        return '20.04', 'libstdc++-10-dev'
    else:
        return '22.04', 'libstdc++-12-dev'

def generate_dockerfile(version):
    """Generate Dockerfile content for a specific version."""
    ubuntu_version, libstdcpp = get_ubuntu_version(version)
    
    dockerfile = f"""FROM ubuntu:{ubuntu_version} AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies including pre-built clang for bootstrapping
RUN apt-get update && apt-get install -y \\
    clang \\
    cmake \\
    ninja-build \\
    git \\
    python3 \\
    && rm -rf /var/lib/apt/lists/*

# Clone LLVM project with specific version
WORKDIR /opt
RUN git clone --branch llvmorg-{version} --depth 1 https://github.com/llvm/llvm-project.git

# Build and install clang using clang as the compiler
WORKDIR /opt/llvm-project
RUN mkdir build && cd build && \\
    cmake -G Ninja \\
    -DCMAKE_BUILD_TYPE=Release \\
    -DCMAKE_INSTALL_PREFIX=/usr/local \\
    -DCMAKE_C_COMPILER=clang \\
    -DCMAKE_CXX_COMPILER=clang++ \\
    -DLLVM_ENABLE_PROJECTS=clang \\
    -DLLVM_TARGETS_TO_BUILD=X86 \\
    ../llvm && \\
    cmake --build . --target install

# Runtime image
FROM ubuntu:{ubuntu_version}

ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies (libc and libstdc++ headers without gcc)
RUN apt-get update && apt-get install -y \\
    cmake \\
    ninja-build \\
    libc6-dev \\
    {libstdcpp} \\
    && rm -rf /var/lib/apt/lists/*

# Copy clang installation from builder
COPY --from=builder /usr/local /usr/local

# Set default C/C++ compilers to clang for cmake
ENV CC=/usr/local/bin/clang
ENV CXX=/usr/local/bin/clang++

# Create symlinks for standard compiler names (use -f to force overwrite if they exist)
RUN ln -sf /usr/local/bin/clang /usr/bin/cc && \\
    ln -sf /usr/local/bin/clang++ /usr/bin/c++

# Set up default build directory
WORKDIR /workspace
RUN mkdir -p build

# Default command shows clang version
CMD ["clang", "--version"]
"""
    return dockerfile

def main():
    """Main function to generate all Dockerfiles."""
    try:
        versions = read_versions()
        output_dir = 'dockerfiles'
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Generating Dockerfiles for {len(versions)} versions...")
        
        for version in versions:
            dockerfile_path = os.path.join(output_dir, f'Dockerfile.clang-{version}')
            dockerfile_content = generate_dockerfile(version)
            
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            print(f"Generated: {dockerfile_path}")
        
        print(f"\nSuccessfully generated {len(versions)} Dockerfiles in {output_dir}/")
        
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
