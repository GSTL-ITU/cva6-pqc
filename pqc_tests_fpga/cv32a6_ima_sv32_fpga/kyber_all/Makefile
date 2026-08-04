CC = riscv32-unknown-elf-gcc
OBJCOPY = riscv32-unknown-elf-objcopy

ARCH = -march=rv32ima_zicsr -mabi=ilp32 -mcmodel=medany

CFLAGS_BASE = $(ARCH) -Wall --specs=nosys.specs
LDFLAGS = -T ../link.ld -nostartfiles

SRCS = ../../../verif/bsp/crt0.S \
       ./main.c \
       ../../../verif/tests/custom/kyber/cbd.c \
       ../../../verif/tests/custom/kyber/fips202.c \
       ../../../verif/tests/custom/kyber/indcpa.c \
       ../../../verif/tests/custom/kyber/kem.c \
       ../../../verif/tests/custom/kyber/ntt.c \
       ../../../verif/tests/custom/kyber/poly.c \
       ../../../verif/tests/custom/kyber/polyvec.c \
       ../../../verif/tests/custom/kyber/randombytes.c \
       ../../../verif/tests/custom/kyber/reduce.c \
       ../../../verif/tests/custom/kyber/symmetric-shake.c \
       ../../../verif/tests/custom/kyber/verify.c

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