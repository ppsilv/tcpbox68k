#!/usr/bin/env python3
# send_program.py - Script para enviar programas para o monitor MC68000
# Melhorado com: seleção de arquivo, verificação e feedback visual

import serial
import os
import time

def main():
    print("\n=== Enviador de Programas para MC68000 ===")

    # Configuração da porta serial
    port = input("Porta serial (ex: COM3, /dev/ttyUSB0): ")
    baudrate = int(input("Baud rate (ex: 9600): "))

    try:
        # Solicita o arquivo a ser enviado
        file_path = input("Caminho do arquivo binário: ").strip('"\' ')

        # Verifica se o arquivo existe
        if not os.path.isfile(file_path):
            print(f"\nErro: Arquivo '{file_path}' não encontrado!")
            return

        file_size = os.path.getsize(file_path)
        print(f"\nPreparando para enviar {file_size} bytes...")

        # Mostra informações do arquivo
        print(f"\nArquivo: {os.path.basename(file_path)}")
        print(f"Tamanho: {file_size} bytes")

        # Confirmação
        if input("\nConfirmar envio? (s/n): ").lower() != 's':
            print("Envio cancelado.")
            return

        # Conecta na serial
        with serial.Serial(port, baudrate, timeout=2) as ser:
            print("\nConectando...", end='', flush=True)
            time.sleep(1)  # Espera a conexão estabilizar

            # Envia tamanho (4 bytes, big-endian)
            ser.write(file_size.to_bytes(4, 'big'))
            print(f"\nEnviando tamanho: {file_size} bytes")

            # Barra de progresso simples
            print("[", end='', flush=True)
            progress_chars = 0

            # Envia dados do arquivo
            with open(file_path, 'rb') as f:
                bytes_sent = 0
                while chunk := f.read(128):  # Lê em blocos de 128 bytes
                    ser.write(chunk)
                    bytes_sent += len(chunk)

                    # Atualiza barra de progresso
                    new_chars = int((bytes_sent / file_size) * 50) - progress_chars
                    if new_chars > 0:
                        print("=" * new_chars, end='', flush=True)
                        progress_chars += new_chars

            print("] 100%")
            print(f"\nEnvio concluído! Total enviado: {bytes_sent} bytes")

    except serial.SerialException as e:
        print(f"\nErro na comunicação serial: {e}")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
    finally:
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
