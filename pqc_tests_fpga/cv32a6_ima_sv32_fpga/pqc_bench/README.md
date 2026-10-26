# Shared PQC harnesses on CVA6 (Nexys Video)

The same harness and crypto sources as on the HORNET core, taken from
[common-pqc-lib-riscv](https://github.com/GSTL-ITU/common-pqc-lib-riscv) (`dev`
branch), built for `cv32a6_ima_sv32_fpga`. Only the platform layer is CVA6
specific:

* `bench_cva6.h`: 64-bit `mcycle`/`mcycleh` and `minstret`/`minstreth`, 25 MHz
* `bench_cva6.c`: `printf` on the NS16550 UART (57600 baud), constructor sets the divisor

Every operation (KeyGen, Encaps/Sign, Decaps/Verify) is timed with the 64-bit
counter, and every output (keys, ciphertexts, signatures) is printed as a
64-bit FNV digest. The digests must equal those of a native build of the same
harness (`make host` in common-pqc-lib-riscv), and of the HORNET runs.

## Build

```sh
make [RUNS=100] [COMMON_PQC=../../../../common-pqc-lib-riscv]
#   build/r<RUNS>/{kyber3,dilithium2,falcon9,sphincs}.elf
```

`RUNS` operations per scheme, each with fresh randomness from the scheme's
deterministic RNG; run 0 uses the same seed as the single-run programs.
The libraries are the `rv32im/ilp32` multilib (`-march=rv32im_zicsr`):
toolchains such as xPack GCC 15 have no `rv32ima` multilib and would pick one
without M; the code has no A instructions either way.

## Run on the board without touching it

```sh
BIT=../../../corev_apu/fpga/work-fpga/ariane_xilinx.bit \
./run_fpga.sh build/r1/dilithium2.elf logs/dilithium2-r1.log "result "
./run_fpga.sh ../dilithium_all/load_O3.elf logs/old-dilithium.log "ALL TESTS PASSED" --trigger
```

`run_fpga.sh` programs the bitstream with Vivado when `BIT` is set, stops
Vivado's `hw_server` (it holds the FTDI), starts the UART logger
(`uart_log.py`, 57600 baud; `--trigger` answers the "Waiting for trigger" of
the older programs with `c`), starts OpenOCD with `nexys_video.cfg`, loads the
ELF with GDB (`load`, `monitor resume`, `detach`; OpenOCD stays connected while
the program runs) and waits for the stop text. OpenOCD, GDB and pyserial come
from a Docker image (`IMAGE`, default `hornet-dev:latest` from HORNET-RV32IMF,
which has OpenOCD in its OSS CAD Suite); no host installation is needed.

`nexys_video.cfg` is `corev_apu/fpga/ariane_nexys_video.cfg` with the command
names of released OpenOCD versions (`ftdi vid_pid`, `gdb_report_*`).

## Bitstream in batch mode

Vivado does not see the board store (XHub) in batch mode; the IP and project
scripts take extra board paths from `BOARD_REPO_PATHS`:

```sh
export BOARD_REPO_PATHS=~/.Xilinx/Vivado/2025.2/xhub/board_store/xilinx_board_store/XilinxBoardStore/Vivado/2025.2/boards
make fpga target=cv32a6_ima_sv32_fpga BOARD=nexys_video XILINX_BOARD=digilentinc.com:nexys_video:part0:1.2 RISCV=<toolchain>
```

The bootrom (`corev_apu/fpga/src/bootrom/bootrom_32.sv`) has to exist; with
GCC 15 its SD-card driver needs `-Wno-error=int-conversion -Wno-error=incompatible-pointer-types`
(pass `CC=` and `OBJCOPY=` to `make -C corev_apu/fpga/src/bootrom bootrom_32.sv`).
