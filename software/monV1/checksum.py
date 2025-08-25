import binascii

with open("monitor.bin", "rb") as f:
    data = f.read()

# Calcula CRC32 (excluindo os últimos 4 bytes)
checksum = binascii.crc32(data[:-4]) & 0xFFFFFFFF
print(f"Checksum calculado: 0x{checksum:08X}")

# Compara com o valor no dump (big-endian)
checksum_rom = int.from_bytes(data[-4:], byteorder='big')
print(f"Checksum no arquivo: 0x{checksum_rom:08X}")

if checksum == checksum_rom:
    print("✅ Checksum válido!")
else:
    print("❌ Checksum inválido!")
