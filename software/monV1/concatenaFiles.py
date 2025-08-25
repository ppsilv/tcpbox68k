#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PGORDÃO FILE CONCATENATOR - Alinhamento PAR com estilo retrô!
# Uso: python3 concat_files.py <arquivo1> <arquivo2> <saida>
#

import sys

def align_even(data):
    """Garante que os dados tenham tamanho PAR (adiciona 0xFF se ímpar)."""
    if len(data) % 2 != 0:
        return data + b'\xFF'  # Padding retrô!
    return data

def concatenate_files(file1, file2, output_file):
    """Concatena file2 após file1, com alinhamento PAR."""
    try:
        # Lê os arquivos em modo binário
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()

        # Aplica alinhamento PAR ao primeiro arquivo
        aligned_data1 = align_even(data1)

        # Concatena os dados
        final_data = aligned_data1 + data2

        # Salva o resultado
        with open(output_file, 'wb') as out:
            out.write(final_data)

        print(f"✅ Concluído! Arquivo '{output_file}' gerado com:")
        print(f" - Tamanho de '{file1}' (alinhado): {len(aligned_data1)} bytes")
        print(f" - Tamanho de '{file2}': {len(data2)} bytes")
        print(f" - Tamanho total: {len(final_data)} bytes")

    except Exception as e:
        print(f"❌ ERRO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 concat_files.py <arquivo1> <arquivo2> <saida>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output = sys.argv[3]

    print("⚡ PGORDÃO FILE CONCATENATOR (Alinhamento PAR + Padding 0xFF)!")
    concatenate_files(file1, file2, output)
