# bin2vmem.py
import sys


inject = [0x00a30313, 0x00a30313, 0x00a30313, 0x00a30313, 0x00a30313, 0x00a30313, 0x00a30313]
space_index = 0
target = len(inject)
position = 0

with open(sys.argv[1], 'rb') as f:
    data = f.read()

# Pad data to multiple of 4 bytes
while len(data) % 4 != 0:
    data += b'\x00'

words = []

for i in range(0, len(data), 4):
    word = data[i:i+4]

    words.append(word)

    if (word == 0):
        space_index += 1
    else:
        space_index = 0

    if (space_index == target):
        position = space_index


        
for j in range(len(words)):

    if ((j >= (position - target)) and (j <= (position))):
        words[j] = inject[position - target + j]

    # Reverse for little endian
    print(f"{int.from_bytes(words[j], byteorder='little'):08x}")