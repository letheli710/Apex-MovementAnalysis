"""Read C strings at virtual addresses of a PE image (ConVar defaults stored as pointers).
Usage: python -I pe_str.py <dll> <hexVA> [...]   or   pe_str.py <dll> --dump <convar-all txt> <name regex>"""
import re, struct, sys

def load(path):
    b = open(path, "rb").read()
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    opt = struct.unpack_from("<H", b, pe + 20)[0]
    base = struct.unpack_from("<Q", b, pe + 24 + 24)[0]
    secs = []
    for i in range(nsec):
        o = pe + 24 + opt + 40 * i
        vsz, va, rsz, raw = struct.unpack_from("<IIII", b, o + 8)
        secs.append((va, max(vsz, rsz), raw))
    return b, base, secs

def cstr(img, va):
    b, base, secs = img
    rva = va - base
    for sva, sz, raw in secs:
        if sva <= rva < sva + sz:
            off = raw + rva - sva
            return b[off:b.index(b"\0", off)].decode("latin-1")
    return None

if __name__ == "__main__":
    img = load(sys.argv[1])
    if sys.argv[2] == "--dump":
        txt = open(sys.argv[3], encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'FUN_\w+\(&DAT_\w+,"([^"]+)",(&DAT_([0-9a-f]+)|"([^"]*)"),[^,]*, *"(.*?)"\);', txt):
            if re.search(sys.argv[4], m.group(1)):
                val = cstr(img, int(m.group(3), 16)) if m.group(3) else m.group(4)
                print(f"{m.group(1)} = {val} | {m.group(5)}")
    else:
        for a in sys.argv[2:]:
            print(a, cstr(img, int(a, 16)))
