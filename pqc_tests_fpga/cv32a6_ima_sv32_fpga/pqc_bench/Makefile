# The PQC harnesses of common-pqc-lib-riscv on CVA6 (cv32a6_ima_sv32_fpga, Nexys Video):
# the same harness and crypto sources as on HORNET, timed with the 64-bit mcycle.
#
#   make [RUNS=100]            build/r<RUNS>/{kyber3,dilithium2,falcon9,sphincs}.elf
#   ./run_fpga.sh <elf> <log>  load with OpenOCD/GDB, log the UART until "result "
#
# COMMON_PQC: checkout of common-pqc-lib-riscv (default: next to this repository)
CC   ?= riscv32-unknown-elf-gcc
ifeq ($(origin CC),default)
CC    = riscv32-unknown-elf-gcc
endif
COMMON_PQC ?= $(abspath ../../../../common-pqc-lib-riscv)
RUNS ?= 1
OPT  ?= -O3
OUT  ?= build/r$(RUNS)

# rv32im libraries (the toolchains' rv32ima multilib lacks M); the code itself has no A instructions
ARCH    = -march=rv32im_zicsr -mabi=ilp32 -mcmodel=medany
CFLAGS  = $(ARCH) $(OPT) -Wall --specs=nosys.specs -I. -I$(COMMON_PQC)/hornet \
          -DBENCH_PLATFORM='"bench_cva6.h"' -DRUNS=$(RUNS)
LDFLAGS = -T ../link.ld -nostartfiles
COMMON  = ../../../verif/bsp/crt0.S bench_cva6.c

K  = $(COMMON_PQC)/c-ml-kem-kyber/riscv-hornet
D  = $(COMMON_PQC)/c-ml-dsa-dilithium/risc-v/hornet
F  = $(COMMON_PQC)/c-fn-dsa-falcon/risc-v/hornet
S  = $(COMMON_PQC)/c-slh-dsa-sphincs/risc-v/hornet/sphincs-shake256-128s-simple

KYBER_SRCS = $(K)/test/hornet_kyber.c $(addprefix $(K)/,cbd.c fips202.c indcpa.c kem.c ntt.c poly.c \
             polyvec.c randombytes.c reduce.c symmetric-shake.c verify.c)
DILITHIUM_SRCS = $(D)/test/hornet_dilithium.c $(addprefix $(D)/,sign.c packing.c polyvec.c poly.c ntt.c \
             reduce.c rounding.c randombytes.c fips202.c symmetric-shake.c)
FALCON_SRCS = $(F)/test/hornet_falcon.c $(addprefix $(F)/src/,codec.c common.c falcon.c fft.c fpr.c \
             keygen.c rng.c shake.c sign.c vrfy.c)
SPHINCS_SRCS = $(S)/test/hornet_sphincs.c $(addprefix $(S)/,address.c randombytes.c wots.c utils.c fors.c \
             sign.c hash_shake256.c thash_shake256_simple.c fips202.c)

all: $(OUT)/kyber3.elf $(OUT)/dilithium2.elf $(OUT)/falcon9.elf $(OUT)/sphincs.elf

$(OUT)/kyber3.elf: $(KYBER_SRCS) $(COMMON) bench_cva6.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -DKYBER_K=3 $(LDFLAGS) -o $@ $(COMMON) $(KYBER_SRCS)
$(OUT)/dilithium2.elf: $(DILITHIUM_SRCS) $(COMMON) bench_cva6.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -DDILITHIUM_MODE=2 $(LDFLAGS) -o $@ $(COMMON) $(DILITHIUM_SRCS)
$(OUT)/falcon9.elf: $(FALCON_SRCS) $(COMMON) bench_cva6.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -DLOGN=9 $(LDFLAGS) -o $@ $(COMMON) $(FALCON_SRCS)
$(OUT)/sphincs.elf: $(SPHINCS_SRCS) $(COMMON) bench_cva6.h
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(COMMON) $(SPHINCS_SRCS)

clean:
	rm -rf build
.PHONY: all clean
