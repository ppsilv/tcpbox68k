#!/usr/bin/python3
import os
import sys

def split_16bit_binary(input_file):
    """Divide um arquivo binário em partes low e high byte para sistemas 16-bit"""
    
    # Verifica se o arquivo existe
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado!")
        sys.exit(1)
    
    # Gera nomes dos arquivos de saída
    base_name = os.path.splitext(input_file)[0]
    low_file = f"{base_name}_low.bin"
    high_file = f"{base_name}_high.bin"
    
    # Lê o arquivo original
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Verifica tamanho e adiciona padding se necessário
    if len(data) % 2 != 0:
        print(f"Aviso: Arquivo com tamanho ímpar ({len(data)} bytes), adicionando padding 0xFF")
        data += b'\xff'
    
    # Processa os bytes
    low_bytes = bytearray()
    high_bytes = bytearray()
    
    for i in range(0, len(data), 2):
        low_bytes.append(data[i])
        high_bytes.append(data[i+1] if i+1 < len(data) else 0xff)
    
    # Escreve os arquivos de saída
    with open(low_file, 'wb') as f_low, open(high_file, 'wb') as f_high:
        f_low.write(low_bytes)
        f_high.write(high_bytes)
    
    print(f"Arquivos gerados com sucesso:")
    print(f"- Low bytes (D0-D7):  {low_file}")
    print(f"- High bytes (D8-D15): {high_file}")
    print(f"Tamanho original: {len(data)} bytes | Low: {len(low_bytes)} bytes | High: {len(high_bytes)} bytes")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: split.py <arquivo_binario>")
        print("Exemplo: split.py firmware.bin")
        sys.exit(1)
    
    split_16bit_binary(sys.argv[1])

