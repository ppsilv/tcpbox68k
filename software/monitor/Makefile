# Makefile para desenvolvimento MC68000
# Agora com split.py inteligente e fluxo completo

# Ferramentas
ASM := vasmm68k_mot
ASMFLAGS := -Fbin -quiet -L listing.txt
SPLITTER := python3 split.py
FILLER := python3 fill.py
PROGRAMMER := minipro
CHIP_TYPE := 28C64B  # Altere para seu chip (28C64A/28C64B)

# Arquivos
SOURCE := monitor.asm
AUX_SOURCE := flash-util.asm
TARGET := monitor.bin
AUX_TARGET := flash-util.bin
SPLIT_LOW := monitor_low.bin
SPLIT_HIGH := monitor_high.bin
ROM_SIZE := 8129

# Tamanhos (ajuste conforme necessário)
SPLIT_SIZE := 4096  # 4KB por chip (para 28C64)

.PHONY: all compile aux split fill programH programL clean help

# Fluxo completo
all: program

# Compilação principal
compile: aux
	@echo "🔨 Compilando $(SOURCE)..."
	@$(ASM) $(ASMFLAGS) -o $(TARGET) $(SOURCE)
	@echo "✅ $(TARGET) gerado ($$(stat -c%s $(TARGET)) bytes)"

# Compilação do utilitário
aux:
	@echo "🔧 Compilando $(AUX_SOURCE)..."
	@$(ASM) $(ASMFLAGS) -o $(AUX_TARGET) $(AUX_SOURCE)

# Divisão inteligente com split.py
split: compile aux
	@echo "✂️ Dividindo $(TARGET) em partes de $(SPLIT_SIZE) bytes..."
	@$(SPLITTER) $(TARGET)
	@echo "✅ Partes prontas: $(SPLIT_LOW) e $(SPLIT_HIGH)"

fill: compile aux split
	@echo "✂️ Preenchendo $(TARGET) com $(ROM_SIZE) bytes..."
	@$(FILLER) $(SPLIT_LOW) $(ROM_SIZE)
	@$(FILLER) $(SPLIT_HIGH) $(ROM_SIZE)
	@echo "✅ Partes prontas: $(SPLIT_LOW) e $(SPLIT_HIGH)"

# Gravação em chips separados (cada um começa em 0x0000)
programL: split
	@echo "🔥 Gravando $(SPLIT_LOW) na Flash #1..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(SPLIT_LOW)
	@echo "🎉 Gravação concluída Flash Low!"
programH: split
	@echo "🔥 Gravando $(SPLIT_HIGH) na Flash #2..."
	@$(PROGRAMMER) -p $(CHIP_TYPE) -w $(SPLIT_HIGH)
	@echo "🎉 Gravação concluída na Flash High!"

# Limpeza radical
clean:
	@rm -f *.bin *.txt
	@echo "🧹 Arquivos temporários removidos."

# Ajuda estilizada
help:
	@echo "⚡ Makefile Turbo para MC68000 ⚡"
	@echo "Comandos úteis:"
	@echo "  make all      - Compila, divide e grava (fluxo completo)"
	@echo "  make compile  - Só compila o monitor.asm"
	@echo "  make aux      - Compila o flash-util.asm"
	@echo "  make split    - Divide o binário usando split.py"
	@echo "  make program  - Grava nas duas memórias"
	@echo "  make clean    - Limpeza geral"
	@echo "  make help     - Mostra esta ajuda"
