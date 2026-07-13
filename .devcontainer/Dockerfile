# Set the OS
FROM ubuntu:22.04

# Prevent Ubuntu from asking interactive "Yes/No" questions
ENV DEBIAN_FRONTEND=noninteractive

# Install all Ubuntu package dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    build-essential \
    gcc-11 \
    g++-11 \
    python3 \
    python3-pip \
    python3-venv \
    make \
    cmake \
    git \
    curl \
    wget \
    flex \
    bison \
    device-tree-compiler \
    autoconf \
    help2man \
    libfl-dev \
    verilator \
    locales \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Lock GCC to version 11
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100

# Install the RISC-V Toolchain
ENV RISCV="/opt/riscv"
RUN mkdir -p ${RISCV} && chmod 777 ${RISCV}
RUN wget https://buildbot.embecosm.com/job/riscv32-gcc-ubuntu2204-release/10/artifact/riscv32-embecosm-ubuntu2204-gcc13.2.0.tar.gz --no-check-certificate && \
    tar -x -f riscv32-embecosm-ubuntu2204-gcc13.2.0.tar.gz --strip-components=1 -C ${RISCV} && \
    rm riscv32-embecosm-ubuntu2204-gcc13.2.0.tar.gz


# Global Toolchain & Compiler Paths
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PATH="${RISCV}/bin:${PATH}"
ENV LIBRARY_PATH="${RISCV}/lib"
ENV LD_LIBRARY_PATH="${RISCV}/lib"
ENV C_INCLUDE_PATH="${RISCV}/include"
ENV CPLUS_INCLUDE_PATH="${RISCV}/include"
ENV CXX="g++-11"
ENV CC="gcc-11"
ENV NUM_JOBS=8

# CVA6 Specific Simulation Environment Variables
# These point to the workspace that VS Code mounts automatically.
ENV ROOT_PROJECT="/workspaces/cva6-pqc"
ENV RTL_PATH="${ROOT_PROJECT}/"
ENV TB_PATH="${ROOT_PROJECT}/verif/tb/core"
ENV TESTS_PATH="${ROOT_PROJECT}/verif/tests"
ENV RISCV_DV_ROOT="${ROOT_PROJECT}/verif/sim/dv"
ENV CVA6_DV_ROOT="${ROOT_PROJECT}/verif/env/corev-dv"

# Verilator & Spike Installation Paths
ENV VERILATOR_INSTALL_DIR="${ROOT_PROJECT}/tools/verilator-v5.008"
ENV SPIKE_INSTALL_DIR="${ROOT_PROJECT}/tools/spike"
ENV SPIKE_SRC_DIR="${ROOT_PROJECT}/verif/core-v-verif/vendor/riscv/riscv-isa-sim"
ENV SPIKE_PATH="${SPIKE_INSTALL_DIR}/bin"

# Update PATH again to include Verilator and Spike
ENV PATH="/home/cva6user/.local/bin:${VERILATOR_INSTALL_DIR}/bin:${SPIKE_PATH}:${PATH}"

# RISC-V Compiler Auto-Detection Variables
# The setup.sh tries to auto-detect this, but we know exactly what we downloaded:
ENV CV_SW_PREFIX="riscv32-unknown-elf-"
ENV RISCV_CC="${RISCV}/bin/${CV_SW_PREFIX}gcc"
ENV RISCV_OBJCOPY="${RISCV}/bin/${CV_SW_PREFIX}objcopy"

# Default Simulation Target Settings
ENV DV_SIMULATORS="veri-testharness,spike"
ENV DV_TARGET="cv64a6_imafdc_sv39"
ENV UVM_VERBOSITY="UVM_NONE"

# Create non-root user and grant sudo
RUN groupadd cva6user && \
    useradd -m -g cva6user -s /bin/bash cva6user && \
    echo "cva6user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to our dedicated user
USER cva6user