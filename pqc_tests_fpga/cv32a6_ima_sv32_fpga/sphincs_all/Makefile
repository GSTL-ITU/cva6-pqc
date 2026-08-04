CC = riscv32-unknown-elf-gcc
OBJCOPY = riscv32-unknown-elf-objcopy

ARCH = -march=rv32ima_zicsr -mabi=ilp32 -mcmodel=medany

CFLAGS_BASE = $(ARCH) -Wall --specs=nosys.specs -I../../../verif/tests/custom/sphincs
LDFLAGS = -T ../link.ld -nostartfiles

SRCS = ../../../verif/bsp/crt0.S \
       ./main.c \
       ../../../verif/tests/custom/sphincs/test/test_syscalls.c \
       ../../../verif/tests/custom/sphincs/address.c \
       ../../../verif/tests/custom/sphincs/fips202.c \
       ../../../verif/tests/custom/sphincs/fors.c \
       ../../../verif/tests/custom/sphincs/hash_shake256.c \
       ../../../verif/tests/custom/sphincs/randombytes.c \
       ../../../verif/tests/custom/sphincs/sign.c \
       ../../../verif/tests/custom/sphincs/thash_shake256_simple.c \
       ../../../verif/tests/custom/sphincs/utils.c \
       ../../../verif/tests/custom/sphincs/wots.c

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