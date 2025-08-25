import binascii

# Lê o binário temporário
with open("monitor.bin", "rb") as f:
    data = bytearray(f.read())

f.close
# Calcula CRC32 (excluindo os últimos 4 bytes)
checksum = binascii.crc32(data[:-4]) & 0xFFFFFFFF

# Insere o checksum nos últimos 4 bytes
data[-4:] = checksum.to_bytes(4, byteorder='big')  # Big-endian para 68000

# Salva o binário final
with open("monitor.bin", "wb") as f:
    f.write(data)

print(f"Checksum calculado: 0x{checksum:08X}")
