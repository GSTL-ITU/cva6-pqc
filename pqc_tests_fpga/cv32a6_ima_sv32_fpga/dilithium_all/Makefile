CC = riscv32-unknown-elf-gcc
OBJCOPY = riscv32-unknown-elf-objcopy

ARCH = -march=rv32ima_zicsr -mabi=ilp32 -mcmodel=medany

# Dilithium parameter set (2, 3, or 5)
DILITHIUM_MODE ?= 2

CFLAGS_BASE = $(ARCH) -Wall --specs=nosys.specs -DDILITHIUM_MODE=$(DILITHIUM_MODE) -I../../../verif/tests/custom/dilithium
LDFLAGS = -T ../link.ld -nostartfiles

SRCS = ../../../verif/bsp/crt0.S \
       ./main.c \
       ../../../verif/tests/custom/dilithium/sign.c \
       ../../../verif/tests/custom/dilithium/packing.c \
       ../../../verif/tests/custom/dilithium/polyvec.c \
       ../../../verif/tests/custom/dilithium/poly.c \
       ../../../verif/tests/custom/dilithium/ntt.c \
       ../../../verif/tests/custom/dilithium/reduce.c \
       ../../../verif/tests/custom/dilithium/rounding.c \
       ../../../verif/tests/custom/dilithium/fips202.c \
       ../../../verif/tests/custom/dilithium/symmetric-shake.c \
       ../../../verif/tests/custom/dilithium/randombytes.c

TARGET_O0 = load_O0.elf
TARGET_O3 = load_O3.elf

# Build both targets by default
all: $(TARGET_O0) $(TARGET_O3)

# Rule for O0
$(TARGET_O0): $(SRCS)
	$(CC) $(CFLAGS_BASE) -O0 $(LDFLAGS) -o $@ $^

# Rule for O3
$(TARGET_O3): $(SRCS)
	$(CC) $(CFLAGS_BASE) -O3 $(LDFLAGS) -o $@ $^

clean:
	rm -f $(TARGET_O0) $(TARGET_O3)