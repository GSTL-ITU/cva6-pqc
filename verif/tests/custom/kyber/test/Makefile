CC32=riscv32-unknown-elf
TARGET=sim_kyber

# Changed include path from -I./src to -I../ to point to the parent directory
CCFLAGS=-march=rv32imf -mabi=ilp32f -ffp-contract=off -mstrict-align -malign-data=xlen -O2 -fno-math-errno -T ./linksc.ld -nostartfiles -ffunction-sections -fdata-sections -Wl,--gc-sections -I../

# All Kyber core submodules located one directory up
KYBER_SRC = ../cbd.c ../fips202.c ../indcpa.c ../kem.c ../ntt.c ../poly.c ../polyvec.c ../randombytes.c ../reduce.c ../symmetric-shake.c ../verify.c

build:
	# Note: Verify the path to crt0.s and rom_generator based on your repo structure
	$(CC32)-gcc hornet_kyber.c $(KYBER_SRC) ../../../../rom_gen/crt0.s $(CCFLAGS) -o $(TARGET).elf
	$(CC32)-objcopy -O binary -j .init -j .text -j .rodata -j .sdata $(TARGET).elf $(TARGET).bin
	../../../../rom_gen/rom_generator $(TARGET).bin
	cp $(TARGET).data memory_init_tb.mem

clean:
	rm -f *.elf *.bin *.data memory_init_tb.mem