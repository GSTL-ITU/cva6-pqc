# CVA6 FPGA area: core vs SoC

Device xc7a200tsbg484-1, RTL at commit `f4eea742`, target `cv32a6_ima_sv32_fpga`, 25 MHz core clock. Whole design after place and route (the bitstream flow, `make fpga`); core alone after place and route.

Setup WNS: whole design +0.154 ns, core alone +14.121 ns.

## Summary

| Block | LUTs | LUT as logic | LUTRAM | SRL | FFs | BRAM (36 Kb) | DSPs | share of device LUTs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Whole design** (`ariane_xilinx`) | 31,900 | 30,659 | 982 | 259 | 30,905 | 23.5 | 4 | 23.7% |
| **Core** in the SoC (`i_ariane`) | 8,914 | 8,698 | 216 | 0 | 4,685 | 16.5 | 4 | 6.6% |
| **Core** alone (out of context) | 8,273 | 8,057 | 216 | 0 | 4,642 | 16.5 | 4 | 6.1% |
| **SoC without core** | 22,986 | 21,961 | 766 | 259 | 26,220 | 7 | 0 | 17.1% |
| **SoC without core and DDR3 controller** | 16,527 | 16,172 | 316 | 39 | 20,610 | 7 | 0 | 12.3% |

Device usage of the whole design: LUTs 23.7% (of 134,600), LUTRAM 2.1% (of 46,200), FFs 11.5% (of 269,200), BRAM (36 Kb) 6.4% (of 365), DSPs 0.5% (of 740).

## Core breakdown

`ariane_xilinx/i_ariane` in the SoC, largest blocks first; "share" is the part of the core's LUTs.

| Block | LUTs | LUT as logic | LUTRAM | SRL | FFs | BRAM (36 Kb) | DSPs | share of LUTs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Core** (ariane) | 8,914 | 8,698 | 216 | 0 | 4,685 | 16.5 | 4 | 100.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;ex_stage_i (ex_stage) | 3,156 | 3,156 | 0 | 0 | 1,834 | 4 | 4 | 35.4% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lsu_i (load_store_unit) | 2,318 | 2,318 | 0 | 0 | 1,632 | 4 | 0 | 26.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;csr_buffer_i (csr_buffer) | 497 | 497 | 0 | 0 | 13 | 0 | 0 | 5.6% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_mult (mult) | 271 | 271 | 0 | 0 | 155 | 0 | 4 | 3.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;branch_unit_i (branch_unit) | 62 | 62 | 0 | 0 | 0 | 0 | 0 | 0.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other ex_stage_i logic* | 8 | 8 | 0 | 0 | 34 | 0 | 0 | 0.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;gen_cache_wt.i_cache_subsystem (wt_cache_subsystem) | 2,332 | 2,246 | 86 | 0 | 848 | 12 | 0 | 26.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_wt_dcache (wt_dcache) | 1,188 | 1,188 | 0 | 0 | 453 | 6 | 0 | 13.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_adapter (wt_axi_adapter) | 691 | 607 | 84 | 0 | 315 | 0 | 0 | 7.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_cva6_icache (cva6_icache) | 170 | 170 | 0 | 0 | 80 | 6 | 0 | 1.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other gen_cache_wt.i_cache_subsystem logic* | 283 | 281 | 2 | 0 | 0 | 0 | 0 | 3.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;issue_stage_i (issue_stage) | 2,198 | 2,154 | 44 | 0 | 834 | 0 | 0 | 24.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_issue_read_operands (issue_read_operands) | 1,206 | 1,162 | 44 | 0 | 182 | 0 | 0 | 13.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_scoreboard (scoreboard) | 992 | 992 | 0 | 0 | 652 | 0 | 0 | 11.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_frontend (frontend) | 577 | 555 | 22 | 0 | 295 | 0.5 | 0 | 6.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_instr_realign (instr_realign) | 418 | 418 | 0 | 0 | 49 | 0 | 0 | 4.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_instr_queue (instr_queue) | 141 | 119 | 22 | 0 | 44 | 0 | 0 | 1.6% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ras_gen.i_ras (ras) | 2 | 2 | 0 | 0 | 66 | 0 | 0 | 0.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other i_frontend logic* | 16 | 16 | 0 | 0 | 136 | 0.5 | 0 | 0.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;id_stage_i (id_stage) | 332 | 332 | 0 | 0 | 167 | 0 | 0 | 3.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;csr_regfile_i (csr_regfile) | 269 | 269 | 0 | 0 | 707 | 0 | 0 | 3.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;*other i_cva6 logic* | 50 | -14 | 64 | 0 | 0 | 0 | 0 | 0.6% |

## SoC breakdown

"share" is the part of the whole design's LUTs.

| Block | LUTs | LUT as logic | LUTRAM | SRL | FFs | BRAM (36 Kb) | DSPs | share of LUTs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Whole design** (ariane_xilinx) | 31,900 | 30,659 | 982 | 259 | 30,905 | 23.5 | 4 | 100.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_ariane (ariane) | 8,914 | 8,698 | 216 | 0 | 4,685 | 16.5 | 4 | 27.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_ddr (xlnx_mig_7_ddr3) | 6,459 | 5,789 | 450 | 220 | 5,610 | 0 | 0 | 20.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_axi_xbar (axi_xbar_intf) | 5,198 | 5,198 | 0 | 0 | 4,574 | 0 | 0 | 16.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_ariane_peripherals (ariane_peripherals) | 4,292 | 4,212 | 80 | 0 | 5,115 | 1 | 0 | 13.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_fifo_encap (fifo_v3__parameterized6) | 1,659 | 1,659 | 0 | 0 | 5,161 | 0 | 0 | 5.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_axi_riscv_atomics (axi_riscv_atomics_wrap) | 1,171 | 1,171 | 0 | 0 | 593 | 0 | 0 | 3.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_encoder (rv_tracer) | 730 | 730 | 0 | 0 | 474 | 0 | 0 | 2.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_cva6_rvfi (cva6_rvfi) | 595 | 595 | 0 | 0 | 1,120 | 0 | 0 | 1.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_axi_dwidth_converter_dm_slave (xlnx_axi_dwidth_converter_dm_slave) | 545 | 505 | 40 | 0 | 509 | 0 | 0 | 1.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_dm_top (dm_top) | 499 | 499 | 0 | 0 | 677 | 0 | 0 | 1.6% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_dmi_jtag (dmi_jtag) | 494 | 494 | 0 | 0 | 340 | 0 | 0 | 1.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_xlnx_axi_clock_converter_ddr (xlnx_axi_clock_converter) | 418 | 222 | 196 | 0 | 994 | 0 | 0 | 1.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_axi_dwidth_converter_dm_master (xlnx_axi_dwidth_converter_dm_master) | 380 | 341 | 0 | 39 | 397 | 0 | 0 | 1.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_dm_axi2mem (axi2mem) | 268 | 268 | 0 | 0 | 44 | 0 | 0 | 0.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_clint (clint) | 182 | 182 | 0 | 0 | 153 | 0 | 0 | 0.6% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_encapsulator (encapsulator) | 160 | 160 | 0 | 0 | 0 | 0 | 0 | 0.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_axi2rom (axi2mem__parameterized0) | 87 | 87 | 0 | 0 | 44 | 0 | 0 | 0.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_iti (cva6_iti) | 75 | 75 | 0 | 0 | 0 | 0 | 0 | 0.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_dm_axi_master (axi_adapter) | 65 | 65 | 0 | 0 | 40 | 0 | 0 | 0.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_slicer (slicer_DPTI) | 8 | 8 | 0 | 0 | 327 | 0 | 0 | 0.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;*flattened into the top: boot ROM, DPTI controller and FIFOs, clock and reset* | -299 | -299 | 0 | 0 | 48 | 6 | 0 | -0.9% |

## Core alone (out of context)

Numbers after place and route. `area/cva6_ooc_top.sv`: the same `ariane` instance and configuration as in `ariane_xilinx`, synthesized as the top with `-mode out_of_context` (no I/O buffers; nothing outside the core can optimize or absorb its logic). The RVFI trace port is left open, as it only feeds SoC-side tracing blocks.

| Block | LUTs | LUT as logic | LUTRAM | SRL | FFs | BRAM (36 Kb) | DSPs | share of LUTs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Core** (ariane) | 8,273 | 8,057 | 216 | 0 | 4,642 | 16.5 | 4 | 100.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;ex_stage_i (ex_stage) | 3,117 | 3,117 | 0 | 0 | 1,829 | 4 | 4 | 37.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lsu_i (load_store_unit) | 2,135 | 2,135 | 0 | 0 | 1,627 | 4 | 0 | 25.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;csr_buffer_i (csr_buffer) | 482 | 482 | 0 | 0 | 13 | 0 | 0 | 5.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_mult (mult) | 423 | 423 | 0 | 0 | 155 | 0 | 4 | 5.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;branch_unit_i (branch_unit) | 69 | 69 | 0 | 0 | 0 | 0 | 0 | 0.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other ex_stage_i logic* | 8 | 8 | 0 | 0 | 34 | 0 | 0 | 0.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;issue_stage_i (issue_stage) | 2,044 | 2,000 | 44 | 0 | 795 | 0 | 0 | 24.7% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_issue_read_operands (issue_read_operands) | 1,143 | 1,099 | 44 | 0 | 183 | 0 | 0 | 13.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_scoreboard (scoreboard) | 901 | 901 | 0 | 0 | 612 | 0 | 0 | 10.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;gen_cache_wt.i_cache_subsystem (wt_cache_subsystem) | 1,976 | 1,890 | 86 | 0 | 847 | 12 | 0 | 23.9% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_wt_dcache (wt_dcache) | 1,222 | 1,222 | 0 | 0 | 452 | 6 | 0 | 14.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_adapter (wt_axi_adapter) | 347 | 263 | 84 | 0 | 315 | 0 | 0 | 4.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_cva6_icache (cva6_icache) | 172 | 172 | 0 | 0 | 80 | 6 | 0 | 2.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other gen_cache_wt.i_cache_subsystem logic* | 235 | 233 | 2 | 0 | 0 | 0 | 0 | 2.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;i_frontend (frontend) | 480 | 458 | 22 | 0 | 297 | 0.5 | 0 | 5.8% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_instr_realign (instr_realign) | 372 | 372 | 0 | 0 | 49 | 0 | 0 | 4.5% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;i_instr_queue (instr_queue) | 105 | 83 | 22 | 0 | 44 | 0 | 0 | 1.3% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ras_gen.i_ras (ras) | 3 | 3 | 0 | 0 | 66 | 0 | 0 | 0.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*other i_frontend logic* | 0 | 0 | 0 | 0 | 138 | 0.5 | 0 | 0.0% |
| &nbsp;&nbsp;&nbsp;&nbsp;id_stage_i (id_stage) | 346 | 346 | 0 | 0 | 167 | 0 | 0 | 4.2% |
| &nbsp;&nbsp;&nbsp;&nbsp;csr_regfile_i (csr_regfile) | 255 | 255 | 0 | 0 | 707 | 0 | 0 | 3.1% |
| &nbsp;&nbsp;&nbsp;&nbsp;*other i_cva6 logic* | 55 | -9 | 64 | 0 | 0 | 0 | 0 | 0.7% |

BRAM counts 36 Kb blocks (a RAMB18 is half). "LUTs" is LUT as logic + LUTRAM + SRL.
Small modules that Vivado flattens into their parent show up in the "other" rows.
After place and route these rows can be slightly negative: phys_opt_design moves
and replicates logic across hierarchy boundaries.
