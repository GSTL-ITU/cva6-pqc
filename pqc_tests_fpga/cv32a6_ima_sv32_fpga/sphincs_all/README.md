# CVA6 Bare-Metal SPHINCS+ Performance Profiling (Nexys Video)

This repository contains the hardware-in-the-loop testing pipeline for running, validating, and benchmarking bare-metal Post-Quantum Cryptography (SPHINCS+) C applications on a CVA6 (Ariane) 32-bit RISC-V soft core flashed onto a Xilinx Artix-7 Nexys Video FPGA.

This specific test implements cycle-accurate performance profiling using the RISC-V `mcycle` Control and Status Register (CSR) to measure the exact hardware clock cycles required for SPHINCS+ Keypair Generation, Signing, and Verification.

Host-to-FPGA communication is handled via the onboard FTDI chip, which provides both the JTAG interface for programming/debugging and a UART interface for I/O. The test utilizes a host-device synchronization protocol to ensure no UART data is lost during the initialization phase.

## Repository Structure
*   `main.c`: Bare-metal C code running the SPHINCS+ signature validation and `mcycle` cycle counting.
*   `host_test.py`: Python host script that synchronizes with the FPGA and logs the test output.
*   `load.elf`: Compiled RISC-V binary.
*   `Makefile`: Build instructions for the bare-metal environment.

## Hardware & System Configuration
*   **Target:** CVA6 RISC-V Core on Nexys Video (Artix-7)
*   **System Clock:** 25 MHz
*   **UART Port:** `/dev/ttyUSB0` (Mapped by FTDI Channel B while OpenOCD holds Channel A)
*   **Baud Rate:** 57600 (Derived from 25MHz clock with a UART divisor of `27` / `0x1B`)

## Prerequisites
Ensure the following tools are installed and in your PATH:
*   `openocd`
*   `riscv32-unknown-elf-gdb`
*   `python3` (with `pyserial` installed)

## Execution Workflow

> **⚠️ SYNCHRONIZATION NOTE:** 
> The C code is designed to block execution until it receives a `'c'` trigger character from the host. While this prevents desynchronization, it is still highly recommended to start the Python listener *before* resuming the FPGA to ensure the initialization string is caught perfectly.
> **Follow the exact order below.**

### Step 1: Start OpenOCD
In **Terminal 1**, start the OpenOCD JTAG connection:

    openocd -f corev_apu/fpga/ariane_nexys_video.cfg

### Step 2: Connect GDB & Load Binary
In **Terminal 2**, start GDB, connect to OpenOCD, and load the executable into the FPGA's memory:

    riscv32-unknown-elf-gdb load.elf

Inside the GDB prompt:

    (gdb) target extended-remote localhost:3333
    (gdb) load

*(Do **not** type `continue` yet. Leave the GDB prompt open.)*

### Step 3: Start the Python Host Script
In **Terminal 3**, launch the host listener. This script will connect to the UART, wait for the initialization string, and automatically send the trigger character.

    sudo python3 host_test.py

*Expected output:*

    Opening /dev/ttyUSB0 at 57600 baud...
    Waiting for FPGA to initialize...

### Step 4: Execute the Code
Return to **Terminal 2** (GDB) and start the RISC-V core:

    (gdb) continue

### Expected Result
Once `continue` is executed, **Terminal 3** should instantly print the clean initialization string, send the trigger, run the SPHINCS+ tests (including cycle profiling), and gracefully close the connection:

    FPGA: CVA6 UART INITIALIZED. Waiting for trigger...

    Triggering SHPHINCS+ test on FPGA...

    --- Test Output ---
    ==================================
    SPHINCS+ FPGA Hardware Test
    ==================================
    Generating keypair...
    -> Cycles: 2870229957
    Keypair generation successful.
    Testing 1 signatures..
    - iteration #0:
    Signing message...
    -> Cycles: 3102258972
    smlen as expected.
    Verifying message...
    -> Cycles: 204513860
    Verification succeeded.
    mlen as expected.
    Output message as expected.
    In-place verification succeeded.
    Flipping a bit of m invalidates signature.
    ALL TESTS PASSED

    Serial connection closed.

### Hardware Performance Summary

The following table details the cycle counts for the SPHINCS+ cryptographic operations running on the FPGA. Due to the extensive runtime of this algorithm, results are provided only for the optimized build (`-O3`).

| Operation | Optimized (`-O3`) Cycles |
| :--- | ---: |
| **Keypair Generation** | 2,870,229,957 |
| **Signing Message** | 3,102,258,972 |
| **Verifying Message** | 204,513,860 |

## Troubleshooting
* **Garbage characters:** This is a baud rate mismatch or a framing error. Ensure `host_test.py` is set to `57600` baud and that you are using a 25MHz system clock on the FPGA.
* **Cannot open `/dev/ttyUSB0`:** Ensure you are using `sudo` to run the Python script, or add your user to the `dialout` group. Check your serial port name via `bash pyserial-ports` on any terminal. You can change the port parameter inside `host_test.py` to match your system.