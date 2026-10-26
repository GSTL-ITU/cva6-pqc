// CVA6 (cv32a6_ima_sv32_fpga, Nexys Video, 25 MHz) backend of the shared PQC
// harnesses in common-pqc-lib-riscv (hornet/bench.h, -DBENCH_PLATFORM='"bench_cva6.h"').
// printf goes to the UART through _write in bench_cva6.c.
#ifndef BENCH_CVA6_H
#define BENCH_CVA6_H

#include <stdint.h>

#define CVA6_CLK_HZ 25000000u

#define BENCH_CSR64(lo, hi) ({                                   \
        uint32_t h_, l_, h2_;                                    \
        do {                                                     \
            __asm__ volatile ("csrr %0, " #hi : "=r"(h_));       \
            __asm__ volatile ("csrr %0, " #lo : "=r"(l_));       \
            __asm__ volatile ("csrr %0, " #hi : "=r"(h2_));      \
        } while (h_ != h2_);                                     \
        ((uint64_t)h_ << 32) | l_; })

static inline uint64_t bench_cycles(void) { return BENCH_CSR64(mcycle, mcycleh); }
static inline uint64_t bench_instret(void) { return BENCH_CSR64(minstret, minstreth); }
static inline uint32_t bench_clk_hz(void) { return CVA6_CLK_HZ; }

#endif
