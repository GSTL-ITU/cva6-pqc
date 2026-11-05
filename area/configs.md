# CVA6 core configurations: FPGA area

The core alone (`ariane`, out of context) on xc7a200tsbg484-1, after place and route, clock constraint 40 ns (25 MHz, the Nexys Video core clock). Every configuration with the board build's settings (`build_fpga_config` of `ariane_xilinx`) and FpgaEn on, so register files, FIFOs and branch predictors use LUTRAM/BRAM as on the board.

## Summary

| Configuration | LUTs | LUT as logic | LUTRAM | FFs | BRAM (36 Kb) | DSPs | cva6 LUTs (without coprocessor) | % device LUTs | WNS (ns) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cv32a6_ima_sv32_fpga` | 8,273 | 8,057 | 216 | 4,642 | 16.5 | 4 | 8,273 | 6.2% | +14.121 |
| `cv32a6_imac_sv32` | 16,817 | 16,547 | 270 | 8,122 | 28 | 4 | 16,817 | 12.6% | +9.139 |
| `cv32a60x` | 9,094 | 8,960 | 134 | 4,899 | 9 | 4 | 8,997 | 6.8% | +10.087 |
| `cv32a65x` | 15,907 | 15,573 | 334 | 5,958 | 9 | 4 | 15,810 | 11.9% | +1.414 |
| `cv64a6_imafdc_sv39` | 46,224 | 45,408 | 816 | 15,800 | 38 | 27 | 46,224 | 34.5% | +2.964 |
| `cv64a6_imafdch_sv39` | 49,398 | 48,482 | 916 | 19,742 | 38 | 27 | 49,398 | 36.9% | +2.444 |
| `cv64a6_imafdc_sv39_wb` | 41,899 | 41,261 | 638 | 15,059 | 39 | 27 | 41,899 | 31.3% | +3.263 |
| `cv64a6_imafdc_sv39_hpdcache` | 46,006 | 45,370 | 636 | 18,665 | 30 | 27 | 46,006 | 34.4% | +2.871 |
| `cv64a6_imafdc_sv39_hpdcache_wb` | 45,851 | 45,215 | 636 | 19,054 | 30 | 27 | 45,851 | 34.3% | +3.350 |

## Features

| Configuration | Features |
|---|---|
| `cv32a6_ima_sv32_fpga` | RV32IMA, MMU, I$ 8 KiB, D$ 8 KiB WT, SB 4, 1 commit |
| `cv32a6_imac_sv32` | RV32IMACB, MMU, I$ 16 KiB, D$ 32 KiB HPD-WT, SB 8, 2 commit |
| `cv32a60x` | RV32IMCB, no MMU, I$ 2 KiB, D$ 2028 B HPD-WT, SB 4, 1 commit, CV-X-IF + example coprocessor |
| `cv32a65x` | RV32IMCB, no MMU, I$ 2 KiB, D$ 2028 B HPD-WT, SB 8, 1 commit, superscalar, CV-X-IF + example coprocessor |
| `cv64a6_imafdc_sv39` | RV64IMAFDCB, MMU, I$ 16 KiB, D$ 32 KiB WT, SB 8, 2 commit, CV-X-IF port |
| `cv64a6_imafdch_sv39` | RV64IMAFDCBH, MMU, I$ 16 KiB, D$ 32 KiB WT, SB 8, 2 commit, CV-X-IF port |
| `cv64a6_imafdc_sv39_wb` | RV64IMAFDCB, MMU, I$ 16 KiB, D$ 32 KiB WB, SB 8, 2 commit, CV-X-IF port |
| `cv64a6_imafdc_sv39_hpdcache` | RV64IMAFDCB, MMU, I$ 16 KiB, D$ 32 KiB HPD-WT, SB 8, 2 commit, CV-X-IF port |
| `cv64a6_imafdc_sv39_hpdcache_wb` | RV64IMAFDCB, MMU, I$ 16 KiB, D$ 32 KiB HPD-WB, SB 8, 2 commit, CV-X-IF port |

SB: scoreboard entries. D$ types: WT write-through, WB write-back, HPD HPDcache. CV-X-IF port: the coprocessor interface of cva6, with no coprocessor; + example coprocessor: `ariane` also instantiates cvxif_example_coprocessor, which is in the totals but not in the "cva6 LUTs" column.

## LUTs by block

| Configuration | Frontend | ID | Issue | EX (ALU, mul/div, LSU) | FPU | MMU | Caches | CSR | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cv32a6_ima_sv32_fpga` | 480 | 346 | 2,044 | 2,086 | - | 1,031 | 1,976 | 255 | 55 |
| `cv32a6_imac_sv32` | 886 | 678 | 4,406 | 3,685 | - | 1,552 | 4,294 | 1,459 | -143 |
| `cv32a60x` | 632 | 962 | 2,516 | 1,754 | - | - | 2,989 | 86 | 58 |
| `cv32a65x` | 1,650 | 1,548 | 6,781 | 1,977 | - | - | 3,152 | 846 | -144 |
| `cv64a6_imafdc_sv39` | 1,992 | 823 | 13,584 | 5,938 | 11,584 | 4,626 | 6,057 | 2,181 | -561 |
| `cv64a6_imafdch_sv39` | 2,176 | 909 | 11,143 | 7,308 | 11,579 | 7,987 | 6,076 | 2,845 | -625 |
| `cv64a6_imafdc_sv39_wb` | 1,960 | 796 | 10,566 | 6,090 | 11,582 | 3,495 | 5,565 | 2,435 | -590 |
| `cv64a6_imafdc_sv39_hpdcache` | 1,965 | 835 | 13,553 | 6,324 | 11,578 | 3,565 | 6,378 | 2,393 | -585 |
| `cv64a6_imafdc_sv39_hpdcache_wb` | 1,985 | 817 | 13,565 | 6,342 | 11,575 | 3,674 | 6,104 | 2,320 | -531 |

## FFs by block

| Configuration | Frontend | ID | Issue | EX (ALU, mul/div, LSU) | FPU | MMU | Caches | CSR | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cv32a6_ima_sv32_fpga` | 297 | 167 | 795 | 1,172 | - | 657 | 847 | 707 | 0 |
| `cv32a6_imac_sv32` | 373 | 172 | 1,472 | 1,253 | - | 656 | 2,763 | 1,019 | 414 |
| `cv32a60x` | 271 | 159 | 546 | 1,074 | - | - | 2,539 | 269 | 0 |
| `cv32a65x` | 322 | 318 | 1,084 | 1,086 | - | - | 2,538 | 568 | 0 |
| `cv64a6_imafdc_sv39` | 532 | 298 | 2,747 | 2,218 | 2,262 | 3,536 | 2,094 | 1,699 | 414 |
| `cv64a6_imafdch_sv39` | 577 | 370 | 3,347 | 2,346 | 2,262 | 5,917 | 2,094 | 2,415 | 414 |
| `cv64a6_imafdc_sv39_wb` | 532 | 298 | 2,745 | 2,259 | 2,262 | 3,504 | 1,342 | 1,700 | 417 |
| `cv64a6_imafdc_sv39_hpdcache` | 532 | 298 | 2,747 | 2,390 | 2,262 | 3,503 | 4,815 | 1,704 | 414 |
| `cv64a6_imafdc_sv39_hpdcache_wb` | 532 | 298 | 2,749 | 2,397 | 2,262 | 3,503 | 5,192 | 1,704 | 417 |

## BRAM (36 Kb) by block

| Configuration | Frontend | ID | Issue | EX (ALU, mul/div, LSU) | FPU | MMU | Caches | CSR | Other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `cv32a6_ima_sv32_fpga` | 0.5 | 0 | 0 | 0 | - | 4 | 12 | 0 | 0 |
| `cv32a6_imac_sv32` | 0 | 0 | 0 | 0 | - | 4 | 24 | 0 | 0 |
| `cv32a60x` | 0 | 0 | 0 | 0 | - | - | 9 | 0 | 0 |
| `cv32a65x` | 0 | 0 | 0 | 0 | - | - | 9 | 0 | 0 |
| `cv64a6_imafdc_sv39` | 2 | 0 | 0 | 0 | 0 | 0 | 36 | 0 | 0 |
| `cv64a6_imafdch_sv39` | 2 | 0 | 0 | 0 | 0 | 0 | 36 | 0 | 0 |
| `cv64a6_imafdc_sv39_wb` | 2 | 0 | 0 | 0 | 0 | 0 | 37 | 0 | 0 |
| `cv64a6_imafdc_sv39_hpdcache` | 2 | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 0 |
| `cv64a6_imafdc_sv39_hpdcache_wb` | 2 | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 0 |

Blocks of `cva6`: EX is ex_stage without the FPU and the MMU (which sit inside it); "Other" is the rest of cva6 (commit stage, controller, register files mapped to LUTRAM, performance counters, glue); it can be slightly negative because phys_opt_design moves and replicates logic across hierarchy boundaries. BRAM counts 36 Kb blocks (a RAMB18 is half). The WNS is at the 40 ns constraint, so it only shows how much margin is left; it is not an Fmax.
