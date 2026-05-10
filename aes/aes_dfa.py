#!/usr/bin/env python3
from itertools import product
from helpers import AES_DFA

def candidates_for_fault(ref_ct, faulty_ct, positions, faulted_row):
    c  = [ref_ct[p]    for p in positions]
    cs = [faulty_ct[p] for p in positions]
    pat = AES_DFA.PATTERNS[faulted_row]

    diff_to_keys = []
    for r in range(4):
        m = {}
        for k in range(256):
            d = AES_DFA.INV_SBOX[c[r] ^ k] ^ AES_DFA.INV_SBOX[cs[r] ^ k]
            m.setdefault(d, []).append(k)
        diff_to_keys.append(m)

    cands = set()
    for f in range(1, 256):
        row_keys = []
        ok = True
        for r in range(4):
            ks = diff_to_keys[r].get(AES_DFA.gmul(pat[r], f))
            if not ks:
                ok = False
                break
            row_keys.append(ks)
        if ok:
            for combo in product(*row_keys):
                cands.add(combo)
    return cands


def recover_round10_key(ref_ct_hex, faulty_groups):
    ref_ct = bytes.fromhex(ref_ct_hex)
    k10 = [None] * 16

    for col in range(4):
        positions = AES_DFA.CT_POSITIONS[col]
        intersect = None

        for faulted_row, fct_hex in enumerate(faulty_groups[col]):
            fct = bytes.fromhex(fct_hex)
            c = candidates_for_fault(ref_ct, fct, positions, faulted_row)
            intersect = c if intersect is None else (intersect & c)
            if len(intersect) == 1:
                break

        if not intersect:
            raise RuntimeError(f"Column {col}: no consistent key candidates.")
        if len(intersect) > 1:
            print(f"[!] Column {col}: {len(intersect)} candidates remain:")
            for cand in sorted(intersect):
                print("    ", " ".join(f"{b:02x}" for b in cand))
            raise RuntimeError(f"Column {col}: ambiguous result.")

        key_tuple = next(iter(intersect))
        for i, p in enumerate(positions):
            k10[p] = key_tuple[i]
        print(f"[+] Column {col} -> CT positions {positions} = "
              + " ".join(f"{b:02x}" for b in key_tuple))

    return bytes(k10)


REF_CT = "29c3505f571420f6402299b31a02d73a" # Reference, unfaulted, ciphertext.

FAULTS = {
    0: [
        "80c3505f571420924022c8b31acdd73a", # Col 0 byte 0 faulted ciphertext.
        "5bc3505f571420474022c7b31a4ed73a",
        "fac3505f571420e1402221b31a81d73a",
        "8dc3505f5714204d40224db31a6bd73a",
    ],
    1: [
        "2930505f0e1420f64022996e1a02703a",
        "2959505f5d1420f6402299851a02df3a",
        "294c505ff31420f6402299531a02bf3a",
        "29e7505f691420f6402299401a02f53a",
    ],
    2: [
        "29c3055f573320f6bb2299b31a02d7a2",
        "29c3275f573d20f6162299b31a02d795",
        "29c32f5f57f320f6632299b31a02d733",
        "29c3345f571620f6ef2299b31a02d71f",
    ],
    3: [
        "29c350705714a4f6400799b39302d73a",
        "29c350b6571452f640ae99b3bb02d73a",
        "29c3506257147ff6405899b39d02d73a",
        "29c350585714caf6408a99b3a702d73a",
    ],
}

k10 = recover_round10_key(REF_CT, FAULTS)
found = k10.hex().upper()
print("Round 10 Key: " + found)