CC = riscv32-unknown-elf-gcc
OBJCOPY = riscv32-unknown-elf-objcopy

ARCH = -march=rv32ima_zicsr -mabi=ilp32 -mcmodel=medany

# Removed -O2 from the base flags.
# -ffp-contract=off and -fno-math-errno are highly recommended for Falcon 
# to ensure floating-point emulation behaves deterministically.
CFLAGS_BASE = $(ARCH) -Wall --specs=nosys.specs -ffp-contract=off -fno-math-errno -I../../../verif/tests/custom/falcon
LDFLAGS = -T ../link.ld -nostartfiles

SRCS = ../../../verif/bsp/crt0.S \
       ./main.c \
       ../../../verif/tests/custom/falcon/codec.c \
       ../../../verif/tests/custom/falcon/common.c \
       ../../../verif/tests/custom/falcon/falcon.c \
       ../../../verif/tests/custom/falcon/fft.c \
       ../../../verif/tests/custom/falcon/fpr.c \
       ../../../verif/tests/custom/falcon/keygen.c \
       ../../../verif/tests/custom/falcon/rng.c \
       ../../../verif/tests/custom/falcon/shake.c \
       ../../../verif/tests/custom/falcon/sign.c \
       ../../../verif/tests/custom/falcon/vrfy.c

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