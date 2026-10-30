"""Dump TF2's built-in playersettings (.set) schema from a DLL.

Record layout found in server.dll v2.0.11 (0x30 bytes, in .data):
  +0x00 char* key name        +0x08 char* default value (string)
  +0x10 char* help text        +0x18 int32 type, int32 struct offset
  +0x20 qword flags            +0x28 int32 min, int32 max (0x80000001 / 0x7fffffff = none)
A record is accepted when name and help point at printable strings, the default is a
printable string or NULL (written as <none>: the .set file must supply the key), and
min/max is the "none" sentinel or a plausible range. Keys outside this table (e.g. wallrunAccelerateHorizontal,
speed, sprintspeed) sit in a second table without defaults and are not listed here.

Usage: python -I scan_set_schema.py <dll> <out.tsv>
"""
import csv
import hashlib
import struct
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))


def main(path, out):
    b = open(path, "rb").read()
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    base = struct.unpack_from("<Q", b, pe + 48)[0]
    n = struct.unpack_from("<H", b, pe + 6)[0]
    opt = struct.unpack_from("<H", b, pe + 20)[0]
    secs = {}
    o = pe + 24 + opt
    for _ in range(n):
        name = b[o:o + 8].rstrip(b"\0").decode()
        vs, va, rs, rp = struct.unpack_from("<IIII", b, o + 8)
        secs[name] = (va, rs, rp)
        o += 40

    def cstr(v):
        r = v - base
        for va, rs, rp in secs.values():
            if va <= r < va + rs:
                off = rp + r - va
                end = b.find(b"\0", off, off + 400)
                s = b[off:end] if end >= 0 else None
                if s is not None and all(32 <= c < 127 or c in (9, 10) for c in s):
                    return s.decode()
        return None

    va, rs, rp = secs[".data"]
    rows = []
    for off in range(rp, rp + rs - 0x30, 8):
        name_p, def_p, help_p, typ, field_off, flags, mn, mx = struct.unpack_from("<QQQiiQii", b, off)
        sane_range = (mn, mx) == (-0x7FFFFFFF, 0x7FFFFFFF) or (mn <= mx and abs(mn) < 10**6 and abs(mx) < 10**6)
        if not (0 <= typ < 16 and 0 <= field_off < 0x10000 and sane_range):
            continue
        name = cstr(name_p)
        if not name or not name.replace("_", "").isalnum():
            continue
        default = "<none>" if def_p == 0 else cstr(def_p)
        helptext = cstr(help_p)
        if default is None or helptext is None or not helptext:
            continue
        rows.append([f"{base + va + off - rp:x}", name, default, typ, f"{field_off:#x}", flags,
                     "" if mn == -0x7FFFFFFF else mn, "" if mx == 0x7FFFFFFF else mx,
                     helptext.replace("\t", " ").replace("\n", " ")])
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(f"# {path} sha256 {hashlib.sha256(b).hexdigest()}\n")
        w = csv.writer(f, delimiter="\t")
        w.writerow(["record", "key", "default", "type", "offset", "flags", "min", "max", "help"])
        w.writerows(rows)
    print(len(rows), "records")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
