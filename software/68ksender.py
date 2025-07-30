#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sender Serial - PGORDÃO PROTOCOL v1.0
# Autor: PDSILVA (aka PGORDÃO) - O Mestre dos Bytes Retrô!
#
# Descrição: Envia arquivos via serial usando o protocolo PDSILVA-3000 (ACK/NACK, checksum, retransmissão)
# Uso: python3 sender_serial.py <porta_serial> <arquivo>
#

import serial
import os
import struct
import sys
import time
# No seu script Python, antes de enviar:
import termios
import tty

def set_raw_mode(fd):
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old_settings


# ===== CONSTANTES DO PROTOCOLO (IMUTÁVEIS COMO UM REGISTRADOR Z80!) =====
BLOCK_SIZE = 256          # Tamanho do bloco (256 bytes = alinhamento perfeito)
PADDING_BYTE = b'\xFF'    # Byte de preenchimento (0xFF = padrão EPROM)
ACK = b'\x06'             # Sinal ACK (ASCII ACK)
NACK = b'\x15'            # Sinal NACK (ASCII NAK)
TIMEOUT = 3               # Timeout em segundos (igual a paciência com USB)

# ===== FUNÇÕES PRINCIPAIS (CODADAS COM AS MÃOS NUAS!) =====

def calculate_checksum(data):
    """Calcula checksum de 16 bits (o jeito PDSILVA de validar dados!)"""
    return struct.pack('>H', sum(data) & 0xFFFF)

def create_header(file_name, file_size, total_packets):
    """Cria o cabeçalho no formato:
    [NOME (64 bytes)] + [TAMANHO (4 bytes)] + [QTD PACOTES (2 bytes)]"""
    header = file_name.ljust(64, '\x00').encode('ascii')
    header += struct.pack('>I', file_size)      # 4 bytes (big-endian)
    header += struct.pack('>H', total_packets)  # 2 bytes (big-endian)
    return header

def send_with_retry(serial_port, data, max_attempts=5):
    """Envia dados e espera por ACK, com retentativas."""
    for attempt in range(max_attempts):
        serial_port.write(data)

        # Espera resposta com timeout
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if serial_port.in_waiting > 0:
                response = serial_port.read(1)
                if response == ACK:
                    return True
                elif response == NACK:
                    break  # Sai do while para retentar
        # Se chegou aqui é por timeout ou NACK
        print(f"⚠️ Tentativa {attempt + 1} falhou. Retentando...")

    return False  # Todas as tentativas falharam

def transmit_file(serial_port, file_path):
    """Função principal que gerencia toda a transmissão."""
    try:
        # Abre arquivo e calcula metadados
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_size = len(file_data)
            file_name = os.path.basename(file_path)
            total_packets = (file_size + BLOCK_SIZE - 1) // BLOCK_SIZE

        print(f"📁 Arquivo: {file_name}")
        print(f"📏 Tamanho: {file_size} bytes")
        print(f"📦 Pacotes: {total_packets}")

        # Configura porta serial
        ser = serial.Serial(serial_port, baudrate=9600, timeout=TIMEOUT)
        print(f"🔌 Conectado em {serial_port} @ 9600 bps")

        # ---- FASE 1: NEGOCIAÇÃO INICIAL ----
        print("\n⚡ Iniciando handshake...")
        if not send_with_retry(ser, b'START_HEADER'):
            print("❌ ERRO: Receiver não respondeu ao handshake!")
            ser.write(NACK * 5)
            ser.close()
            return

        # ---- FASE 2: ENVIO DO HEADER ----
        header = create_header(file_name, file_size, total_packets)
        print("\n📄 Enviando header...")
        if not send_with_retry(ser, header + calculate_checksum(header)):
            print("❌ ERRO: Falha no envio do header!")
            ser.write(NACK * 5)
            ser.close()
            return

        # ---- FASE 3: TRANSMISSÃO DOS DADOS ----
        print(f"\n🚀 Enviando {total_packets} pacotes de dados...")
        for packet_num in range(total_packets):
            start = packet_num * BLOCK_SIZE
            packet = file_data[start:start + BLOCK_SIZE]

            # Padding se necessário
            if len(packet) < BLOCK_SIZE:
                packet += PADDING_BYTE * (BLOCK_SIZE - len(packet))

            # Adiciona checksum e envia
            packet_with_checksum = packet + calculate_checksum(packet)

            print(f"📤 Pacote {packet_num + 1}/{total_packets} - {len(packet)} bytes", end='\r')

            if not send_with_retry(ser, packet_with_checksum):
                print(f"\n❌ ERRO: Falha no pacote {packet_num + 1}! Abortando...")
                ser.write(NACK * 5)
                ser.close()
                return

        print("\n✅ Transmissão concluída com sucesso!")
        print("O receiver agora deve estar tão feliz quanto um 68000 rodando a 16MHz!")

    except Exception as e:
        print(f"\n💥 ERRO FATAL: {str(e)}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

# ===== PONTO DE ENTRADA (O GRANDE FINAL!) =====
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 sender_serial.py <porta_serial> <arquivo>")
        print("Exemplo: python3 sender_serial.py /dev/ttyUSB0 firmware.bin")
        sys.exit(1)

    # Ao iniciar:
    old_settings = set_raw_mode(sys.stdin.fileno())

    serial_port = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"ERRO: Arquivo '{file_path}' não encontrado!")
        sys.exit(1)

    print("\n" + "="*50)
    print("🔥 SENDER SERIAL - PGORDÃO PROTOCOL v1.0 🔥")
    print("="*50 + "\n")

    transmit_file(serial_port, file_path)
    # Ao finalizar:
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

