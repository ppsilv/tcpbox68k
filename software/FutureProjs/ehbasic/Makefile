all: basic68k.bin

basic68k.bin: basic68k.inc basic68k.asm
	@vasmm68k_mot -nowarn=2028 -nowarn=2030 -nowarn=2048 -m68000 -Fbin -L basic68k.lst -o basic68k.bin basic68k.asm
	@echo "Compilação terminada"

basic68k_even.run: basic68k.run
	srec_cat basic68k.run -split 2 0 -offset 0x6000 -o basic68k_even.run

basic68k_odd.run: basic68k.run
	srec_cat basic68k.run -split 2 1 -offset 0x6000 -o basic68k_odd.run

upload: basic68k.run
	/bin/echo -e "LO1\r\n" >/dev/ttyUSB0
	sleep 1
	ascii-xfr -s -l 50 basic68k.run | sed  's/S5/S9/' > /dev/ttyUSB0
	/bin/echo -e "GO 800\r\n" >/dev/ttyUSB0

basic68k_odd.bin: basic68k_odd.run
	srec2bin -o 0xC001 basic68k_odd.run basic68k_odd.bin

basic68k_even.bin: basic68k_even.run
	srec2bin -o 0xC000 basic68k_even.run basic68k_even.bin

# Program EEPROMS using Minipro programmer.
# Adjust device type below to match your actual device.
program_odd: basic68k_odd.bin
	minipro -S --write=basic68k_odd.bin --device=AT28HC64

program_even: basic68k_even.bin
	minipro -S --write=basic68k_even.bin --device=AT28HC64

clean:
	$(RM) *.bin *.lst *.run *.hex
distclean:
	$(RM) basic68k.run basic68k_even.run basic68k_odd.run basic68k.lst basic68k.hex
	$(RM) basic68k_even.bin basic68k_odd.bin
