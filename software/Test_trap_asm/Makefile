# Makefile para programa de demonstração do TRAP #1

AS = vasmm68k_mot
LD = m68k-elf-ld
OBJCOPY = m68k-elf-objcopy

ASFLAGS = -m68000 -Felf -quiet -opt-allbra -opt-lsl
#-opt-cc
LDFLAGS = -nostdlib -T trap1_demo.ld

OBJS = trap1_demo.o

all: trap1_demo.bin trap1_demo.lst

# Compilar assembly para objeto
%.o: %.s
	$(AS) $(ASFLAGS) $< -o $@

# Gerar listing
%.lst: %.s
	$(AS) $(ASFLAGS) -L $@ $< -o /dev/null

# Linker
trap1_demo.elf: $(OBJS)
	$(LD) $(LDFLAGS) $^ -o $@

# Binário final
trap1_demo.bin: trap1_demo.elf
	$(OBJCOPY) -O binary $< $@

# Limpar
clean:
	rm -f *.o *.elf *.bin *.lst

.PHONY: all clean
