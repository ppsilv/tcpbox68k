# Makefile para desenvolvimento MC68000
# Versão otimizada para gerar binários compactos

# Configurações
ASM := vasmm68k_mot
ASSEMBLER := vasmm68k_mot
LINKER := m68k-elf-ld
ASM_ELF := vasmm68k_mot
OBJCOPY := m68k-elf-objcopy
#ASMFLAGS := -quiet -L
ELF_FLAGS := -Felf -quiet
SPLITTER := python3 split68k.py
FILLER := python3 fill.py
PROGRAMMER := minipro
CHIP_TYPE := 28C64A  # Altere para o seu chip Flash

# Nomes de arquivos
SOURCE := test_ram2.asm
TARGET := $(basename $(SOURCE))
TARGET_OBJ := $(TARGET).o
TARGET_ELF := $(TARGET).elf
TARGET_BIN := $(TARGET).bin
TARGET_LOW := $(TARGET)_low.bin
TARGET_HIGH := $(TARGET)_high.bin
LAYOUT_FILE := layout.ld

# Tamanhos (ajuste conforme sua memória)
FLASH_SIZE := 8192  # 8KB (tamanho da 28C64A)
ROM_SIZE := 8192     # 8KB usados

#.PHONY: all compile compile_compact split fill program clean
.PHONY: all compile split fill program clean

all: split

# Compilação tradicional (pode gerar binário grande)
compile:
	@echo "Compilando $(SOURCE) para $(TARGET_BIN)..."
	@$(ASM) -Fbin $(ASMFLAGS) -L $(TARGET).lst -o $(TARGET_BIN) $(SOURCE)
	@echo "Tamanho do binário: $$(stat -c%s $(TARGET_BIN)) bytes"
	@echo "╔════════════════════════════════╗"
	@echo "║  Compilação Concluída!         ║"
	@echo "╠════════════════════════════════╣"
	@echo "║ Binário: $(TARGET_BIN)         ║"
	@echo "║ Tamanho: $$(stat -c%s $(TARGET_BIN)) bytes          ║"
	@echo "║ Listagem: $(TARGET).lst        ║"
	@echo "╚════════════════════════════════╝"


# Compilação segura que detecta TODOS os erros
compile_linker:
	@echo "Compiler..."
	#vasmm68k_mot -Felf -quiet -L listing.txt -o test_ram2.o test_ram2.asm
	@$(ASSEMBLER) $(ELF_FLAGS) -L $(TARGET).lst -o $(TARGET_OBJ) $(SOURCE)
	@echo "Linker..."
	#m68k-elf-ld -T layout.ld test_ram2.o -o test_ram2.elf
	@$(LINKER) -T $(LAYOUT_FILE) $(TARGET_OBJ) -o $(TARGET_ELF)
	@echo "Objcopy..."
	#m68k-elf-objcopy -O binary test_ram2.elf test_ram2.bin
	@$(OBJCOPY) -O binary $(TARGET_ELF) $(TARGET_BIN)

	@echo "╔══════════════════════════╗"
	@echo "║  SEÇÕES CARREGADAS:      ║"
	@echo "╠══════════════════════════╣"
	@echo "║ CODE: $$(m68k-elf-objdump -h $(TARGET_ELF) | grep CODIGO | awk '{print "0x"$$3}') bytes ║"
	@echo "║ DATA: $$(m68k-elf-objdump -h $(TARGET_ELF) | grep DADOS | awk '{print "0x"$$3}') bytes ║"
	@echo "║ BSS:  $$(m68k-elf-objdump -h $(TARGET_ELF) | grep RAM | awk '{print "0x"$$3}') bytes (RAM) ║"sp
	@echo "╚══════════════════════════╝"

antigo:
	@echo "Compilando $(SOURCE) para binário compacto..."
	@# Primeiro: compilação com verificação rigorosa de símbolos
	@if ! $(ASM_ELF) $(ELF_FLAGS) -L $(TARGET).lst -o $(TARGET_ELF) $(SOURCE) 2> errors.txt; then \
		echo "\nERROS DE COMPILAÇÃO:"; \
		cat errors.txt; \
		rm -f $(TARGET_ELF) errors.txt; \
		exit 1; \
	fi

	@# Segundo: verificação explícita de símbolos não resolvidos
	@if m68k-elf-nm $(TARGET_ELF) | grep ' U ' > unresolved.txt; then \
		echo "\nERROS DE SÍMBOLOS NÃO RESOLVIDOS:"; \
		cat unresolved.txt; \
		rm -f $(TARGET_ELF) unresolved.txt errors.txt; \
		exit 1; \
	fi

	@# Terceiro: conversão para binário
	@$(OBJCOPY) -O binary $(TARGET_ELF) $(TARGET_BIN)
	@echo "Tamanho do binário compacto: $$(stat -c%s $(TARGET_BIN)) bytes"
	@rm -f errors.txt unresolved.txt
	@echo "╔══════════════════════════╗"
	@echo "║  Compilação Concluída!   ║"
	@echo "╠══════════════════════════╣"
	@echo "║ Binário: $(TARGET_BIN)   ║"
	@echo "║ Tamanho: $$(stat -c%s $(TARGET_BIN)) bytes       ║"
	@echo "║ Listagem: $(TARGET).lst  ║"
	@echo "╚══════════════════════════╝"

split: compile_linker
	@echo "Dividindo $(TARGET_BIN) em words 16-bit..."
	@$(SPLITTER) $(TARGET_BIN)
	@echo "Arquivos gerados: $(TARGET_LOW) e $(TARGET_HIGH)"

fill: split
	@echo "Preenchendo arquivos para $(FLASH_SIZE) bytes..."
	@$(FILLER) $(TARGET_LOW) $(FLASH_SIZE)
	@$(FILLER) $(TARGET_HIGH) $(FLASH_SIZE)
	@echo "Preenchimento completo."

programL: fill
	@echo "Gravando parte LOW na Flash..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(TARGET_LOW) -s
	@echo "Gravação concluída!"

programH: fill
	@echo "Gravando parte HIGH na Flash..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(TARGET_HIGH) -s
	@echo "Gravação concluída!"

program: programL programH

clean:
	@rm -f *.bin *.o *.txt *.lst *.elf
	@echo "Arquivos temporários removidos."

help:
	@echo "Makefile para desenvolvimento MC68000 (versão compacta)"
	@echo "Opções:"
	@echo "  make compile        - Compila tradicional (pode gerar binário grande)"
	@echo "  make compile_linker - Compila gerando binário com sessões code,data e bss (recomendado)"
	@echo "  make split          - Compila (compacto) e divide o binário"
	@echo "  make fill           - Compila, divide e preenche os arquivos"
	@echo "  make program        - Executa todo o fluxo e grava nas Flash ROMs"
	@echo "  make programL       - Grava apenas a parte LOW"
	@echo "  make programH       - Grava apenas a parte HIGH"
	@echo "  make clean          - Remove arquivos gerados"
	@echo "  make help           - Mostra esta ajuda"
