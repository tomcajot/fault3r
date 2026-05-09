#!/usr/bin/env python3
"""
AES-128 Differential Fault Analysis (Piret-Quisquater attack).

Given:
  - 1 reference ciphertext
  - 16 faulted ciphertexts (4 per column of round 9 MixColumns output)
Recovers the round-10 key.

Fault model: a single byte is flipped at the input of round 9's MixColumns.
After MC, the column containing the fault has the differential pattern
(2f, f, f, 3f) (or a rotation, depending on which row was hit). Round 10 has
SubBytes + ShiftRows + AddRoundKey (no MixColumns), so the 4 differing bytes
land at fixed ciphertext positions, which we use to solve for K10.
"""

from itertools import product

# ----------------------------------------------------------------------------
# AES tables
# ----------------------------------------------------------------------------
SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
]
INV_SBOX = [0] * 256
for i, b in enumerate(SBOX):
    INV_SBOX[b] = i


def gmul(a, b):
    """Multiplication in GF(2^8) with AES reduction polynomial x^8+x^4+x^3+x+1."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return p


# ----------------------------------------------------------------------------
# Geometry of the attack
# ----------------------------------------------------------------------------
# AES state is column-major: byte index = col*4 + row.
# A column-c fault at the input of round 9 MC produces a 4-byte differential in
# column c. SubBytes (round 10) is byte-wise; ShiftRows then scatters that
# column to 4 ciphertext positions:
#
#   col 0 (state idx 0,1,2,3)     -> CT bytes 0, 13, 10,  7
#   col 1 (state idx 4,5,6,7)     -> CT bytes 4,  1, 14, 11
#   col 2 (state idx 8,9,10,11)   -> CT bytes 8,  5,  2, 15
#   col 3 (state idx 12,13,14,15) -> CT bytes 12, 9,  6,  3
#
# Order matters: CT_POSITIONS[col][r] is the ciphertext byte that came from
# row r of the original column.
CT_POSITIONS = {
    0: [0, 13, 10, 7],
    1: [4,  1, 14, 11],
    2: [8,  5,  2, 15],
    3: [12, 9,  6,  3],
}

# After MC, a single-byte fault in row r of the input column produces these
# differential patterns (multipliers on the unknown fault value f). All four
# are tried; we don't assume which row was hit.
PATTERNS = [
    (2, 1, 1, 3),  # row 0 faulted
    (3, 2, 1, 1),  # row 1 faulted
    (1, 3, 2, 1),  # row 2 faulted
    (1, 1, 3, 2),  # row 3 faulted
]


# ----------------------------------------------------------------------------
# Core DFA logic
# ----------------------------------------------------------------------------
def candidates_for_fault(ref_ct, faulty_ct, positions):
    """
    Return the set of 4-tuples (k0,k1,k2,k3) of candidate round-10 key bytes
    at the four CT positions, consistent with a single fault.

    For every (pattern, f), the expected differential at row r is m_r * f,
    and INV_SBOX[c^k] XOR INV_SBOX[c'^k] = m_r*f typically has 0/2/4 solutions
    for k. We collect all 4-tuples arising from at least one (pattern, f).
    """
    cands = set()
    c  = [ref_ct[p]    for p in positions]
    cs = [faulty_ct[p] for p in positions]

    # Precompute, per row, a map: differential -> list of candidate keys.
    diff_to_keys = []
    for r in range(4):
        m = {}
        for k in range(256):
            d = INV_SBOX[c[r] ^ k] ^ INV_SBOX[cs[r] ^ k]
            m.setdefault(d, []).append(k)
        diff_to_keys.append(m)

    for pat in PATTERNS:
        for f in range(1, 256):
            row_keys = []
            ok = True
            for r in range(4):
                ks = diff_to_keys[r].get(gmul(pat[r], f))
                if not ks:
                    ok = False
                    break
                row_keys.append(ks)
            if ok:
                for combo in product(*row_keys):
                    cands.add(combo)
    return cands


def recover_column_keys(ref_ct, faulty_cts, col):
    """Intersect candidate sets across all faults targeting the same column."""
    positions = CT_POSITIONS[col]
    intersect = None
    for fct in faulty_cts:
        c = candidates_for_fault(ref_ct, fct, positions)
        intersect = c if intersect is None else (intersect & c)
        if len(intersect) == 1:
            break  # Already unique, no need to process more faults
    return positions, intersect


def recover_round10_key(ref_ct_hex, faulty_groups):
    """
    ref_ct_hex   : 32-char hex string of the reference ciphertext.
    faulty_groups: dict {col_index (0..3): [hex faulted ciphertexts]}.
    Returns: bytes(16) of the round-10 key.
    """
    ref_ct = bytes.fromhex(ref_ct_hex)
    k10 = [None] * 16

    for col in range(4):
        faulty_cts = [bytes.fromhex(h) for h in faulty_groups[col]]
        positions, cands = recover_column_keys(ref_ct, faulty_cts, col)

        if not cands:
            raise RuntimeError(
                f"Column {col}: no consistent key (check fault grouping).")
        if len(cands) > 1:
            print(f"[!] Column {col}: {len(cands)} candidates remain")
            for c in sorted(cands):
                print("    ", " ".join(f"{b:02x}" for b in c))
            raise RuntimeError(f"Column {col}: ambiguous result.")

        key_tuple = next(iter(cands))
        for i, p in enumerate(positions):
            k10[p] = key_tuple[i]
        print(f"[+] Column {col} -> CT positions {positions} = "
              + " ".join(f"{b:02x}" for b in key_tuple))

    return bytes(k10)


# ----------------------------------------------------------------------------
# Entry point with the provided data
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    REF_CT = "29c3505f571420f6402299b31a02d73a"

    FAULTS = {
        0: [  # Bytes 0..3, hit column 0  -> CT bytes 0,13,10,7
            "80c3505f571420924022c8b31acdd73a",
            "5bc3505f571420474022c7b31a4ed73a",
            "fac3505f571420e1402221b31a81d73a",
            "8dc3505f5714204d40224db31a6bd73a",
        ],
        1: [  # Bytes 4..7, hit column 1  -> CT bytes 4,1,14,11
            "2930505f0e1420f64022996e1a02703a",
            "2959505f5d1420f6402299851a02df3a",
            "294c505ff31420f6402299531a02bf3a",
            "29e7505f691420f6402299401a02f53a",
        ],
        2: [  # Bytes 8..11, hit column 2 -> CT bytes 8,5,2,15
            "29c3055f573320f6bb2299b31a02d7a2",
            "29c3275f573d20f6162299b31a02d795",
            "29c32f5f57f320f6632299b31a02d733",
            "29c3345f571620f6ef2299b31a02d71f",
        ],
        3: [  # Bytes 12..15, hit column 3 -> CT bytes 12,9,6,3
            "29c350705714a4f6400799b39302d73a",
            "29c350b6571452f640ae99b3bb02d73a",
            "29c3506257147ff6405899b39d02d73a",
            "29c350585714caf6408a99b3a702d73a",
        ],
    }
    
    EXPECTED = "28FDDEF86DA4244ACCC0A4FE3B316F26"

    print("Running Piret-Quisquater DFA on AES-128...\n")
    k10 = recover_round10_key(REF_CT, FAULTS)
    found = k10.hex().upper()
    print("\nRecovered Round 10 Key: " + found)
    print("Target Round 10 Key:    " + EXPECTED)
    print("Match!" if found == EXPECTED else "MISMATCH")