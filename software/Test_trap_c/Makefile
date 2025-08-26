# Makefile para endereço 0x82000

CC = m68k-elf-gcc
LD = m68k-elf-ld
OBJCOPY = m68k-elf-objcopy

CFLAGS = -m68000 -O0 -Wall -fno-builtin -ffreestanding -nostdlib
LDFLAGS = -nostdlib -T readwrite.ld

all: readwrite.bin

readwrite.o: readwrite.c
	$(CC) $(CFLAGS) -c $< -o $@

readwrite.elf: readwrite.o
	$(LD) $(LDFLAGS) $^ -o $@

readwrite.bin: readwrite.elf
	$(OBJCOPY) -O binary $< $@

# Verificar o endereço de entrada
verify:
	m68k-elf-objdump -f readwrite.elf | grep "start address"
	m68k-elf-nm readwrite.elf | grep "_start"

clean:
	rm -f *.o *.elf *.bin

.PHONY: all clean verify
