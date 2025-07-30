#python3 converthex2bin.py "303CFF0031C02400263C0007A120538366FC303C000031C024006000FF7E303CAA0031C02400263C0007A120538366FC303C000031C024004E75" piscaled.bin

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# HEX68K_TO_BIN.PY - Conversor de HEX para binário (PDSILVA/PGORDÃO Protocol)
# Uso: python3 hex68k_to_bin.py <hex_string> <output.bin>
#
# Exemplo: python3 hex68k_to_bin.py "303CFF00..." piscaled.bin
#

import sys
import re

def hex_to_bin(hex_str, output_file):
    """Converte string HEX (sem espaços/formatação) para arquivo binário."""
    try:
        # Remove espaços, quebras de linha e caracteres não-HEX
        clean_hex = re.sub(r'[^0-9A-Fa-f]', '', hex_str)

        # Verifica se o comprimento é par (bytes completos)
        if len(clean_hex) % 2 != 0:
            raise ValueError("String HEX deve ter número par de caracteres!")

        # Converte para bytes
        binary_data = bytes.fromhex(clean_hex)

        # Salva em arquivo
        with open(output_file, 'wb') as f:
            f.write(binary_data)

        print(f"✅ Conversão concluída! Arquivo '{output_file}' gerado com:")
        print(f" - Tamanho: {len(binary_data)} bytes")
        print(f" - Primeiros bytes: {binary_data[:4].hex().upper()}...")

    except Exception as e:
        print(f"❌ ERRO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 hex68k_to_bin.py <hex_string> <output.bin>")
        print("Exemplo: python3 hex68k_to_bin.py '303CFF00...' piscaled.bin")
        sys.exit(1)

    hex_input = sys.argv[1]
    output_file = sys.argv[2]

    print("⚡ HEX68K_TO_BIN - Conversor para o Protocolo PDSILVA-3000!")
    hex_to_bin(hex_input, output_file)
