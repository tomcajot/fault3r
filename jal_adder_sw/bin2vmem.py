import sys


def encode_jal(rd, offset):
    if offset % 2 != 0:
        raise ValueError(f"JAL offset {offset} must be even")
    if not (-(1 << 20) <= offset < (1 << 20)):
        raise ValueError(f"JAL offset {offset:#x} exceeds +-1MB range")

    imm      = offset & 0x1FFFFF
    imm20    = (imm >> 20) & 0x1
    imm10_1  = (imm >> 1)  & 0x3FF
    imm11    = (imm >> 11) & 0x1
    imm19_12 = (imm >> 12) & 0xFF

    return ((imm20    << 31) |
            (imm10_1  << 21) |
            (imm11    << 20) |
            (imm19_12 << 12) |
            ((rd & 0x1F) << 7) |
            0x6F)


def read_vmem(path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.split('//', 1)[0].split('#', 1)[0]
            for tok in line.split():
                if tok.startswith('@'):
                    continue
                out.append(int(tok, 16))
    return out


def main():
    if len(sys.argv) not in (2, 4):
        sys.exit(f"Usage: {sys.argv[0]} <bin_file> [<inject.vmem> <fault_address>]")

    bin_file  = sys.argv[1]
    injecting = len(sys.argv) == 4

    if injecting:
        inject_file   = sys.argv[2]
        fault_address = int(sys.argv[3], 0)
        inject        = read_vmem(inject_file)
        if not inject:
            sys.exit(f"Error: no instructions found in {inject_file}")
        target = len(inject) + 1

    with open(bin_file, 'rb') as f:
        data = f.read()
    while len(data) % 4 != 0:
        data += b'\x00'

    words = [int.from_bytes(data[i:i+4], 'little') for i in range(0, len(data), 4)]

    if injecting:
        space_index = 0
        end_pos = -1
        for j, w in enumerate(words):
            if w == 0:
                space_index += 1
                if space_index == target:
                    end_pos = j
                    break
            else:
                space_index = 0

        if end_pos < 0:
            sys.exit(f"Error: no run of {target} consecutive empty words in binary")

        start = end_pos - target + 1

        for k, instr in enumerate(inject):
            words[start + k] = instr

        jump_index   = start + len(inject)
        jump_address = jump_index * 4
        offset       = (fault_address + 4) - jump_address
        words[jump_index] = encode_jal(0, offset)

		# JAL from fault address to inject start (for hardware injection)
        hw_offset = (start * 4) - fault_address
        hw_jal = encode_jal(0, hw_offset)

        print(f"Injected {len(inject)} instr at word {start} (addr {start*4:#x})", file=sys.stderr)
        print(f"Jump-back at addr {jump_address:#x} -> {fault_address:#x} (offset {offset:+d})", file=sys.stderr)
        print(f"Hardware fault instruction: 32'h{hw_jal:08x}  (JAL from {fault_address:#x} -> {start*4:#x})", file=sys.stderr)

    for w in words:
        print(f"{w:08x}")


if __name__ == '__main__':
    main()
