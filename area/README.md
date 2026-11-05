# FPGA area: core vs SoC

LUT, FF, BRAM and DSP usage of CVA6 on the Nexys Video, split into the core
(`i_ariane`: the cva6 pipeline, register file, MMU/TLBs, multiplier/divider,
L1 instruction and data caches, AXI adapter) and the rest of the SoC (DDR3
controller (MIG), AXI crossbar, width and clock converters, AXI atomics,
debug module and JTAG, boot ROM, CLINT, PLIC, UART, SPI, GPIO, timer, DPTI,
instruction tracer, clock generation and reset). Vivado runs on the host.

## Results

Nexys Video (XC7A200T-1SBG484), Vivado 2026.1, after place and route,
RTL at commit `f4eea742`, target `cv32a6_ima_sv32_fpga`, 25 MHz core clock.
The whole design is the bitstream of `make fpga` (the same flow and
options as `corev_apu/fpga/scripts/run.tcl`). Setup WNS: whole design
+0.154 ns, core alone +14.121 ns.

| | LUTs | LUT as logic | LUTRAM | SRL | FFs | BRAM (36 Kb) | DSPs |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Whole design** (`ariane_xilinx`) | 31,900 | 30,659 | 982 | 259 | 30,905 | 23.5 | 4 |
| **Core** in the SoC (`i_ariane`) | 8,914 | 8,698 | 216 | 0 | 4,685 | 16.5 | 4 |
| **Core** alone (out of context) | 8,273 | 8,057 | 216 | 0 | 4,642 | 16.5 | 4 |
| **SoC without core** | 22,986 | 21,961 | 766 | 259 | 26,220 | 7 | 0 |
| **SoC without core and DDR3 controller** | 16,527 | 16,172 | 316 | 39 | 20,610 | 7 | 0 |

The whole design uses 23.7% of the device's LUTs, 11.5% of its FFs, 6.4% of
its BRAMs and 0.5% of its DSPs. The core alone uses 6.1% of the LUTs.

Core in the SoC, by block:

| Block | LUTs | FFs | BRAM (36 Kb) | DSPs | share of core LUTs |
|---|---:|---:|---:|---:|---:|
| EX stage (ex_stage) | 3,156 | 1,834 | 4 | 4 | 35.4% |
| &nbsp;&nbsp;&nbsp;&nbsp;load/store unit with MMU and TLBs | 2,318 | 1,632 | 4 | 0 | 26.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;CSR buffer | 497 | 13 | 0 | 0 | 5.6% |
| &nbsp;&nbsp;&nbsp;&nbsp;multiplier and divider (mult) | 271 | 155 | 0 | 4 | 3.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;ALU, branch unit and the rest of EX | 70 | 34 | 0 | 0 | 0.8% |
| Cache subsystem (wt_cache_subsystem) | 2,332 | 848 | 12 | 0 | 26.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;data cache (wt_dcache, 8 KiB) | 1,188 | 453 | 6 | 0 | 13.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;AXI adapter (wt_axi_adapter) | 691 | 315 | 0 | 0 | 7.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;instruction cache (cva6_icache, 8 KiB) | 170 | 80 | 6 | 0 | 1.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;arbitration and the rest | 283 | 0 | 0 | 0 | 3.2% |
| Issue stage (scoreboard, read operands) | 2,198 | 834 | 0 | 0 | 24.7% |
| Frontend (fetch, realign, instruction queue, RAS) | 577 | 295 | 0.5 | 0 | 6.5% |
| ID stage (decoder) | 332 | 167 | 0 | 0 | 3.7% |
| CSR file (csr_regfile) | 269 | 707 | 0 | 0 | 3.0% |
| Register file (LUTRAM) and the rest of cva6 | 50 | 0 | 0 | 0 | 0.6% |

SoC without core, by block:

| Block | LUTs | FFs | BRAM (36 Kb) |
|---|---:|---:|---:|
| DDR3 controller (xlnx_mig_7_ddr3) | 6,459 | 5,610 | 0 |
| AXI crossbar (axi_xbar_intf) | 5,198 | 4,574 | 0 |
| Peripherals: PLIC, UART, SPI, GPIO, timer (ariane_peripherals) | 4,292 | 5,115 | 1 |
| DPTI encapsulation FIFO (fifo_encap) | 1,659 | 5,161 | 0 |
| AXI atomics (axi_riscv_atomics) | 1,171 | 593 | 0 |
| Instruction trace: rv_tracer, cva6_rvfi, cva6_iti, encapsulator, slicer | 1,568 | 1,921 | 0 |
| Debug module and JTAG (dm_top, dmi_jtag, axi2mem, axi_adapter) | 1,326 | 1,101 | 0 |
| AXI width and clock converters (Xilinx IP) | 1,343 | 1,900 | 0 |
| CLINT | 182 | 153 | 0 |
| Boot ROM bus (axi2rom) | 87 | 44 | 0 |
| Flattened into the top: boot ROM, DPTI controller and FIFOs, clock and reset | -299 | 48 | 6 |

The 7 SoC BRAMs: boot ROM 4, DPTI FIFOs 2 (FIFO36), SPI FIFOs 1 (two RAMB18).
The 16.5 BRAMs of the core: I-cache 6, D-cache 6, shared TLB 4, frontend 0.5.
The negative LUT count of the last row: the blocks above add up to 299 LUTs
more than the whole design, because `phys_opt_design` and LUT packing move
and merge logic across hierarchy boundaries.

The full tables are in [area.md](area.md), a copy of the generated
`build/area/nexys_video/area.md`.

## Other core configurations

The core alone (out of context, after place and route, 25 MHz constraint) for
the other CVA6 targets in `core/include/`, with `make -C area configs`. Each
is built as it would be in `ariane_xilinx` (its `build_fpga_config`), with two
more settings for the FPGA: `FpgaEn` on (only the board's target sets it; the
register files, FIFOs and branch predictors then use LUTRAM/BRAM instead of
flip-flops) and `TechnoCut` off (`cv32a60x`/`cv32a65x` otherwise expect an
ASIC SRAM macro and leave a black box). The board's target is unchanged by
both.

| Configuration | Features | LUTs | LUTRAM | FFs | BRAM (36 Kb) | DSPs | % XC7A200T LUTs |
|---|---|---:|---:|---:|---:|---:|---:|
| `cv32a6_ima_sv32_fpga` (board) | RV32IMA, MMU, I$/D$ 8/8 KiB WT, 1 commit | 8,273 | 216 | 4,642 | 16.5 | 4 | 6.2% |
| `cv32a60x` | RV32IMCB, no MMU, I$/D$ 2/2 KiB HPDcache, CV-X-IF coprocessor | 9,094 | 134 | 4,899 | 9 | 4 | 6.8% |
| `cv32a65x` | as cv32a60x, superscalar, 8-entry scoreboard | 15,907 | 334 | 5,958 | 9 | 4 | 11.9% |
| `cv32a6_imac_sv32` | RV32IMACB, MMU, I$/D$ 16/32 KiB HPDcache, 2 commit | 16,817 | 270 | 8,122 | 28 | 4 | 12.6% |
| `cv64a6_imafdc_sv39` | RV64IMAFDCB, MMU, I$/D$ 16/32 KiB WT, 2 commit | 46,224 | 816 | 15,800 | 38 | 27 | 34.5% |
| `cv64a6_imafdch_sv39` | + hypervisor | 49,398 | 916 | 19,742 | 38 | 27 | 36.9% |
| `cv64a6_imafdc_sv39_wb` | write-back D$ | 41,899 | 638 | 15,059 | 39 | 27 | 31.3% |
| `cv64a6_imafdc_sv39_hpdcache` | HPDcache write-through | 46,006 | 636 | 18,665 | 30 | 27 | 34.4% |
| `cv64a6_imafdc_sv39_hpdcache_wb` | HPDcache write-back | 45,851 | 636 | 19,054 | 30 | 27 | 34.3% |

- The 64-bit cores are 5–6× the board's core. The FPU alone is about 11.6k
  LUTs, 2.3k FFs and 11 DSPs (the 64-bit multiplier takes the other 16), and
  the issue stage (with the FP register file) grows to 10.6–13.6k LUTs.
- The hypervisor extension adds about 3.2k LUTs and 3.9k FFs, mostly in the
  MMU (two-stage translation) and the CSRs.
- In these runs, HPDcache uses fewer BRAMs (28 vs 36 in the caches) but about 3k more
  FFs than the write-through cache. The write-back D$ config comes out 4.3k
  LUTs smaller than write-through, but most of that difference is in the issue
  stage, which the cache type should not affect. Block-level numbers move by a
  few thousand LUTs between configs through cross-boundary optimization.
  Compare totals rather than single blocks.
- All of them would fit the XC7A200T; the largest uses 37% of its LUTs.
  Timing at 25 MHz is met with 1.4 to 14 ns to spare. That slack is margin
  at this constraint, not an Fmax.

Not included: `cv64a60ax` (its config package does not set the `RVZiCbom`
field that `config_pkg` now has, so it does not compile in this repository),
`cv64a6_imafdcv_sv39` (needs the Ara vector unit) and
`cv64a6_imafdc_sv39_openpiton` (OpenPiton NoC interface).

The full comparison, with LUTs, FFs and BRAMs per block (frontend, ID, issue,
EX, FPU, MMU, caches, CSR), is in [configs.md](configs.md), a copy of the
generated `build/area/nexys_video/configs.md`.

## Running

```
make -C area                     # copy, make fpga on the copy, area reports
make -C area IMPL=0              # core alone only synthesized, not routed
make -C area reports             # rerun area.tcl on an existing build
make -C area summary DEPTH=3     # rebuild area.md only, deeper breakdown
make -C area configs             # the core alone for each of CONFIGS, configs.md
make -C area configs CONFIGS="cv32a6_imac_sv32"   # a chosen set
```

`make -C area configs` needs the build of `make -C area` (it reuses its
source copy and `add_sources.tcl`) and takes 10–15 minutes per configuration.
Run it without `-j`: a 64-bit core peaks at about 10.5 GB during synthesis,
and three in parallel exhausted 31 GB. Each run is capped at `MEMMAX` (20G)
in a `systemd-run` scope, so running out kills that Vivado, not the desktop.

`make -C area` takes about 45 minutes (8 threads). It

1. copies the repository (without `.git`, `build/`, `area/`) to
   `build/area/nexys_video/src` and records the commit in `commit.txt`;
2. downloads the Nexys Video board files (Digilent `vivado-boards`) to
   `build/area/nexys_video/boards` and points `BOARD_REPO_PATHS` at them;
3. runs `make fpga target=cv32a6_ima_sv32_fpga BOARD=nexys_video` on the copy
   (log in `make_fpga.log`), which writes the bitstream to
   `src/corev_apu/fpga/work-fpga/`;
4. runs `area.tcl`: the SoC reports from the `opt` and `routed` checkpoints of
   that build, then the core alone (synthesis, place and route);
5. writes `area.md` with `area_summary.py`.

The flow runs on a copy because `make fpga` writes into the source tree (IPs
under `corev_apu/fpga/xilinx`, the boot ROM, `add_sources.tcl`, the Vivado
project). Two settings differ from a plain `make fpga`, both passed on the
command line and both outside the RTL:

- the bootrom is compiled with `-Wno-error=int-conversion`: its C code passes
  pointers as integers, which GCC 14 and later reject (here GCC 16.1,
  `~/riscv32`, `RISCV=` and `CROSS=` override it);
- board part `digilentinc.com:nexys_video:part0:1.2`, as in
  `pqc_tests_fpga/cv32a6_ima_sv32_fpga/pqc_bench/README.md` (`XBOARD=` overrides it).

Output in `build/area/nexys_video/`:

| File | Content |
|---|---|
| `area.md` | summary: whole design, core, SoC without core; core and SoC breakdown |
| `soc_util_<stage>.rpt`, `soc_util_hier_<stage>.rpt` | `ariane_xilinx` from the bitstream flow |
| `soc_timing_route.rpt` | its timing summary |
| `core_util_<stage>.rpt`, `core_util_hier_<stage>.rpt` | the core alone, out of context |
| `core_timing_route.rpt` | its timing summary at 25 MHz (`IMPL=1`) |
| `src/corev_apu/fpga/work-fpga/ariane_xilinx.bit` | the bitstream itself |

`<stage>` is `opt` (synthesis + `opt_design`) or `route`; the summary uses the
route reports when they exist.

The core is given two ways:

- **in the SoC**: the `i_ariane` instance in the hierarchical report of the
  whole design. Together with "SoC without core" this adds up to the total.
- **alone**: `cva6_ooc_top.sv` instantiates `ariane` with the same
  configuration as `ariane_xilinx` (`cv32a6_ima_sv32_fpga` through its
  `build_fpga_config`) and is synthesized with `-mode out_of_context` (no I/O
  buffers) and the same retiming option. The RVFI trace port is left open:
  in the SoC it only feeds the tracing blocks, which are counted in the SoC.
  The core alone is 641 LUTs smaller than in the SoC, about half of it in the
  AXI adapter (347 vs 691 LUTs, the same 84 LUTRAM: the difference is logic
  LUTs around its data FIFO), the rest spread over the pipeline. FFs, LUTRAM,
  BRAM and DSPs match within 1%. The in-SoC number is the cost of the core as
  it is on the board.

Rerunning the flow only rewrites the files in `build/`; copy `area.md` and
`configs.md` here again to update the versions in this folder.

Files: `area.tcl` (Vivado: SoC reports, then the core alone),
`area_core.tcl` (Vivado: the core alone for any target), `area_summary.py`
(core vs SoC report), `area_configs.py` (configuration comparison),
`cva6_ooc_top.sv` (top for the core alone), `Makefile`. Nothing outside
this folder is changed.
