# Makefile para desenvolvimento MC68000
# Inclui: compilação, split, fill e gravação com minipro

# Configurações
ASM := vasmm68k_mot
ASMFLAGS := -Fbin -quiet -L listing.txt
SPLITTER := python3 split68k.py
FILLER := python3 fill.py
PROGRAMMER := minipro
CHIP_TYPE := 28C64A  # Altere para o seu chip Flash

# Nomes de arquivos
SOURCE := test_ram2.asm
TARGET := $(basename $(SOURCE))
TARGET_LOW := $(TARGET)_low.bin
TARGET_HIGH := $(TARGET)_high.bin

# Tamanhos (ajuste conforme sua memória)
FLASH_SIZE := 8192  # 32KB (tamanho típico de uma 27C256)
ROM_SIZE := 8192     # 8KB usados

.PHONY: all compile split fill program clean

all: split

compile:
	@echo "Compilando $(SOURCE) para $(TARGET).bin..."
	@$(ASM) $(ASMFLAGS) -o $(TARGET).bin $(SOURCE)
	@echo "Compilação concluída. Tamanho: $$(stat -c%s $(TARGET).bin) bytes"

split: compile
	@echo "Dividindo $(TARGET).bin em words 16-bit..."
	@$(SPLITTER) $(TARGET).bin
	@echo "Arquivos gerados: $(TARGET_LOW) e $(TARGET_HIGH)"

fill: split
	@echo "Preenchendo arquivos para $(FLASH_SIZE) bytes..."
	@$(FILLER) $(TARGET_LOW) $(FLASH_SIZE)
	@$(FILLER) $(TARGET_HIGH) $(FLASH_SIZE)
	@echo "Preenchimento completo."

programL: fill
	@echo "Gravando na Flash com minipro..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(TARGET_LOW) -s
	@echo "Gravação concluída com sucesso!"

programH: fill
	@echo "Gravando na Flash com minipro..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(TARGET_HIGH) -s
	@echo "Gravação concluída com sucesso!"

clean:
	@rm -f *.bin *.txt
	@echo "Arquivos temporários removidos."

help:
	@echo "Makefile para desenvolvimento MC68000"
	@echo "Opções:"
	@echo "  make compile    - Compila o código assembly"
	@echo "  make split      - Compila e divide o binário (16-bit)"
	@echo "  make fill       - Compila, divide e preenche os arquivos"
	@echo "  make program    - Executa todo o fluxo e grava nas Flash ROMs"
	@echo "  make clean      - Remove arquivos gerados"
	@echo "  make help       - Mostra esta ajuda"

