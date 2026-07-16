#!/bin/bash
set -e

echo "Cleaning up old builds..."
rm -rf obj_dir

# Define paths
HORNET_DIR="HORNET-RV32IMF"
SRC_DIR="$HORNET_DIR/sources_1/imports/src"
SIM_DIR="$HORNET_DIR/sim_1/imports/sim_src"
MEM_DIR="$HORNET_DIR/sim_1/imports/initialize_memory"

TB_FILE="$SIM_DIR/barebones_top_tb.v"

# Stage memory files
echo "Staging memory files..."
cp "$MEM_DIR/memory_init_tb.mem" . 2>/dev/null || true
cp "$HORNET_DIR/sources_1/imports/initialize_memory/memory_init.mem" . 2>/dev/null || true

# Filter out the FPGA wrapper that contains Vivado IP
# This finds all .v files in src folder EXCEPT fpga_top.v
echo "Gathering source files..."
SRC_FILES=$(find "$SRC_DIR" -name "*.v" ! -name "fpga_top.v")

# Compile
# Added flags to suppress the strict linting warnings and define the exact top module
echo "Compiling with Verilator..."
verilator --binary --timing --trace -Wno-fatal \
    -Wno-WIDTHEXPAND \
    -Wno-WIDTHTRUNC \
    -Wno-PINMISSING \
    -Wno-MULTITOP \
    --top-module barebones_top_tb \
    -I"$SRC_DIR" \
    "$TB_FILE" \
    $SRC_FILES

# Execute the compiled binary
echo "Compilation successful! Running simulation..."
./obj_dir/Vbarebones_top_tb
