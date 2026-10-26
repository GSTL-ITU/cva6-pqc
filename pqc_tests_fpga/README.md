# FPGA Tests

## PQC Hardware Cycle Analysis (`cv32a6_ima_sv32_fpga`)

| Algorithm | Operation | Unoptimized (`-O0`) Cycles | Optimized (`-O3`) Cycles |
| :--- | :--- | ---: | ---: |
| **Kyber** <br>*(ML-KEM)* | Keypair Generation | 18,862,487 | 4,870,962 |
| | Encapsulation | 20,469,834 | 5,132,604 |
| | Decapsulation | 21,835,714 | 5,375,795 |
| **Dilithium** <br>*(ML-DSA)* | Keypair Generation | 39,713,233 | 10,698,993 |
| | Signing | 319,767,109 | 84,220,016 |
| | Verification | 40,686,421 | 10,940,832 |
| **SPHINCS+** <br>*(SLH-DSA)* | Keypair Generation | 611,929,855 | 2,870,229,957 |
| | Signing | 625,469,793 | 3,102,258,972 |
| | Verification | 771,250,149 | 204,513,860 |
| **Falcon** <br>*(FN-DSA)* | Keypair Generation | 2,723,650,597 | 196,182,819 |
| | Signing | 1,344,415,413 | 80,656,349 |
| | Verification | 6,973,136 | 1,144,339 |

## Re-run with GCC 15.2 and the shared harness (October 2026)

Same core and bitstream flow as above (Nexys Video, 25 MHz), built with xPack
GCC 15.2 at `-O3`:

* **Old test**: the `*_all/load_O3.elf` programs of this folder, unchanged.
* **Shared harness**: [`pqc_bench`](cv32a6_ima_sv32_fpga/pqc_bench/README.md), the same harness and crypto
  files as on the HORNET core (common-pqc-lib-riscv), 64-bit `mcycle`, outputs
  checked against a native build. Seed 0 is the same seed as the old tests; the
  median is over 100 seeds (Falcon: 25), each run with fresh randomness.

| Algorithm | Operation | Old test, GCC 15.2 | Shared harness, seed 0 | Median (seeds) |
| :--- | :--- | ---: | ---: | ---: |
| **Kyber** <br>*(ML-KEM)* | Keypair Generation | 3,086,896 | 3,088,479 | 3,078,144 (100) |
|  | Encapsulation | 3,323,788 | 3,323,645 | 3,327,446 (100) |
|  | Decapsulation | 3,613,505 | 3,615,412 | 3,615,900 (100) |
| **Dilithium** <br>*(ML-DSA)* | Keypair Generation | 6,560,732 | 6,555,112 | 6,651,464 (100) |
|  | Signing | 59,982,875 | 59,935,646 | 15,143,069 (100) |
|  | Verification | 6,811,420 | 6,816,171 | 6,813,650 (100) |
| **Falcon** <br>*(FN-DSA)* | Keypair Generation | 166,531,093 | 166,486,014 | 292,037,681 (25) |
|  | Signing | 69,691,296 | 69,828,009 | 69,790,061 (25) |
|  | Verification | 845,697 | 887,572 | 886,922 (25) |
| **SPHINCS+** <br>*(SLH-DSA)* | Keypair Generation | overnight run | overnight run | overnight run |
|  | Signing | overnight run | overnight run | overnight run |
|  | Verification | overnight run | overnight run | overnight run |

The newer compiler alone needs 15-40 % fewer cycles than the August numbers
above. CVA6 counts vary by a few thousand cycles between runs of the same
program (DDR3 and cache timing).

---

## Project Status & To-Do

| Task / Objective | Associated Folder | Status |
| :--- | :--- | :--- |
| JTAG Bring-up & GDB Execution | `kyber_gdb` | ✅ **Done** |
| Basic UART pipeline (Receive `a`, `b`, transmit `c = a+b` with "Result:") | `uart_rx_tx` | ✅ **Done** |
| Fully run Kyber over UART | `kyber_uart` | ✅ **Done** |
| Fully run Kyber, count clock cycles, and print cycles to host | `kyber_all` | ✅ **Done** |
| Fully run Dilithium, count clock cycles, and print cycles to host | `dilithium_all` | ✅ **Done** |
| Fully run Falcon, count clock cycles, and print cycles to host | `falcon_all` | ✅ **Done** |
| Shared harness (same code as HORNET), 64-bit mcycle, digests, many seeds | `pqc_bench` | ✅ **Done** |
| Fully run SPHINCS+, count clock cycles, and print cycles to host | `sphincs_all` | ✅ **Done** | 


Eventhough Every test folder has its own READMEs, the general concept of usign OpenOCD and GDB (GNU Debugger) is explained below.

---

## Step 1: Establish the OpenOCD Connection

Before you can load code or debug, you must open a connection to the FPGA and halt the CPU. This exposes a port that GDB can connect to.

> **Warning:** Do not install OpenOCD inside the Docker environment. It must reach the localhost ports, which may cause a problem for some users. 

Open a terminal and run OpenOCD using the provided configuration file:

```bash
openocd -f corev_apu/fpga/ariane_nexys_video.cfg
```

If successful, OpenOCD will halt the core and begin listening for GDB connections on port `3333`. Your output should look similar to this:

```text
Open On-Chip Debugger 0.12.0+dev-02603-gfc566d740 (2026-07-24-09:53)
Licensed under GNU GPL v2
For bug reports, read
	[http://openocd.org/doc/doxygen/bugs.html](http://openocd.org/doc/doxygen/bugs.html)
DEPRECATED! use 'riscv virt2phys_mode' not 'riscv set_enable_virtual'
Warning: This version of OpenOCD does not support address translation. To debug on virtual addresses, please update to the latest version.
Info : clock speed 1000 kHz
Info : JTAG tap: riscv.cpu tap/device found: 0x00000001 (mfg: 0x000 (<invalid>), part: 0x0000, ver: 0x0)
Info : [riscv.cpu] datacount=2 progbufsize=8
Info : [riscv.cpu] Examined RISC-V core
Info : [riscv.cpu]  XLEN=32, misa=0x40141101
Info : [riscv.cpu] Examination succeed
Info : [riscv.cpu] starting gdb server on 3333
Info : Listening on port 3333 for gdb connections
riscv.cpu halted due to debug-request.
Ready for Remote Connections
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
```

**Leave this terminal running in the background.** 

---

## Step 2: Choose Your Execution Method

Depending on your goal, you can either step through your code interactively using GDB, or you can push the code directly to the board and let it run continuously.

### Method A: Interactive Debugging with GDB

Open a **new terminal** (or your Docker container) and launch the RISC-V GDB tool, passing it your compiled binary:

```bash
riscv32-unknown-elf-gdb <your_compiled_test>.elf
```

Once inside the `(gdb)` prompt, connect to the OpenOCD server you started in Step 1, load the code into the FPGA's memory, and start debugging:

```gdb
# Connect to OpenOCD (Use host.docker.internal:3333 if running GDB from a Docker container)
(gdb) target extended-remote localhost:3333

# Flash the binary into the FPGA's memory (You can do this if you want to reset the program as well)
(gdb) load

# Set a breakpoint at the start of your program (This is optional)
(gdb) break main

# Execute
(gdb) continue
```

From here, you can use standard GDB commands like `step` (step by line), `stepi` (step by instruction), or `info registers` to inspect the CPU state.

### Method B: Run Without Debugging

If you simply want to load a test program and let it run continuously (for example, to interact with it via a UART serial terminal) without keeping GDB open, you can pass a single command string directly to OpenOCD. 

#### Step 1: Connect GDB & Load Binary
In **Terminal 2**, start GDB, connect to OpenOCD, and load the executable into the FPGA's memory:

    riscv32-unknown-elf-gdb load.elf

Inside the GDB prompt:

    (gdb) target extended-remote localhost:3333
    (gdb) load

*(Do **not** type `continue` yet. Leave the GDB prompt open.)*

#### Step 2: Start the Python Host Script
In **Terminal 3**, launch the host listener. This script will connect to the UART, wait for the initialization string, and automatically send the trigger character.

    sudo python3 host_test.py

*Expected output:*

    Opening /dev/ttyUSB0 at 57600 baud...
    Waiting for FPGA to initialize...

#### Step 3: Execute the Code
Return to **Terminal 2** (GDB) and start the RISC-V core:

    (gdb) continue

#### Expected Result
Once `continue` is executed, **Terminal 3** should instantly print the clean initialization string, send the trigger, run the according test.

#### Troubleshooting
* **Garbage characters:** This is a baud rate mismatch or a framing error. Ensure `host_test.py` is set to `57600` baud and that you are using a 25MHz system clock on the FPGA.
* **Cannot open `/dev/ttyUSB0`:** Ensure you are using `sudo` to run the Python script, or add your user to the `dialout` group. Check your serial port name via `bash pyserial-ports` on any terminal. You can change the port parameter inside `host_test.py` to match your system.
