"""Resolve ConVar default strings from a Ghidra registration dump + the game dll.

Usage: py -3 cv_defaults.py <convar-all-*.txt> <dll> [regex]
Reads only names and default strings (research numbers), writes nothing.
"""
import re, struct, sys

def sections(b):
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    n = struct.unpack_from("<H", b, pe + 6)[0]
    opt = struct.unpack_from("<H", b, pe + 20)[0]
    base = struct.unpack_from("<Q", b, pe + 24 + 24)[0]
    s = pe + 24 + opt
    out = []
    for k in range(n):
        o = s + 40 * k
        vs, va, rs, ra = struct.unpack_from("<IIII", b, o + 8)
        out.append((va, max(vs, rs), ra))
    return base, out

def read_str(b, base, secs, va):
    rva = va - base
    for sva, size, raw in secs:
        if sva <= rva < sva + size:
            o = raw + rva - sva
            e = b.find(b"\0", o)
            return b[o:e].decode("latin1")
    return None

dump, dll = sys.argv[1], sys.argv[2]
pat = re.compile(sys.argv[3] if len(sys.argv) > 3 else ".")
b = open(dll, "rb").read()
base, secs = sections(b)
txt = open(dump, encoding="utf-8", errors="replace").read()
seen = set()
for m in re.finditer(r'FUN_[0-9a-f]+\(&DAT_[0-9a-f]+,\s*"([^"]+)",\s*&DAT_([0-9a-f]+)', txt):
    name, va = m.group(1), int(m.group(2), 16)
    if name in seen or not pat.search(name):
        continue
    seen.add(name)
    print(f"{name}\t{read_str(b, base, secs, va)!r}")
