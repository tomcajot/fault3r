# bin2vmem.py
import sys

with open(sys.argv[1], 'rb') as f:
    data = f.read()

# Pad data to multiple of 4 bytes
while len(data) % 4 != 0:
    data += b'\x00'

for i in range(0, len(data), 4):
    word = data[i:i+4]
    # Reverse for little endian
    print(f"{int.from_bytes(word, byteorder='little'):08x}")
