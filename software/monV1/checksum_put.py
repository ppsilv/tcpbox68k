import binascii

with open("monitor.bin", "rb") as f:
    data = bytearray(f.read())

size=len(data)
print(f"Tamanho do arquivo{size} ")

checksum = 0
for i in range(0, len(data)-4, 4):
    word = int.from_bytes(data[i:i+4], 'big')
    checksum_antes = checksum
    checksum = (checksum + word) & 0xFFFFFFFF
    #print(f"+{word:08X} (pos {i:04X}) → {checksum:08X}")

#checksum -= 0x400

# Escreve em BIG-ENDIAN (igual ao 68000)
data[-4:] = [
    (checksum >> 24) & 0xFF,
    (checksum >> 16) & 0xFF,
    (checksum >> 8) & 0xFF,
    checksum & 0xFF
]

with open("monitor.bin", "wb") as f:
    f.write(data)

print(f"Checksum: 0x{checksum:08X}")

print(f"Checksum calculado: 0x{checksum:08X}")
