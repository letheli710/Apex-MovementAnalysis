"""Turn DumpConVarRegistrations.java output from TF2 DLLs into a ConVar default table.

TF2 registers a ConVar with one call (seen in server.dll and client.dll):
    FUN_reg(&DAT_obj, "name", &DAT_default | "default", flags [, "help", ...]);
The default is the third argument. This script finds that call for each name in the
decompiled context and reads the default string from the PE file itself.

Usage: python -I parse_convar_dump.py <out.tsv> <dll> <dump.txt> [<dll> <dump.txt> ...]
Output columns: convar, default, dll, function, register_call, flags, help, object
"""
import csv
import re
import struct
import sys
from pathlib import Path

CALL = re.compile(
    r'(FUN_[0-9a-f]+)\(&?(?:DAT|PTR)_(?P<obj>[0-9a-f]+),\s*"(?P<name>[^"]+)",\s*'
    r'(?:&?(?:DAT|s_[A-Za-z0-9_]*?)_(?P<addr>[0-9a-f]{9,16})|"(?P<lit>[^"]*)"),\s*'
    r'(?P<flags>[^,)]+)(?:,\s*(?:"(?P<help>(?:[^"\\]|\\.)*)"|(?P<helpref>[^,)]+)))?', re.S)


class PE:
    def __init__(self, path):
        self.b = Path(path).read_bytes()
        b = self.b
        pe = struct.unpack_from("<I", b, 0x3C)[0]
        self.base = struct.unpack_from("<Q", b, pe + 24 + 24)[0]
        n = struct.unpack_from("<H", b, pe + 6)[0]
        opt = struct.unpack_from("<H", b, pe + 20)[0]
        self.secs = []
        o = pe + 24 + opt
        for _ in range(n):
            vs, va, rs, rp = struct.unpack_from("<IIII", b, o + 8)
            self.secs.append((va, rs, rp))
            o += 40
        self.sha = __import__("hashlib").sha256(b).hexdigest()

    def cstr(self, va):
        r = va - self.base
        for sva, rs, rp in self.secs:
            if sva <= r < sva + rs:
                off = rp + r - sva
                end = self.b.find(b"\0", off, off + 256)
                return self.b[off:end].decode("latin1") if end >= 0 else None
        return None


def parse(dll, dump):
    pe = PE(dll)
    text = Path(dump).read_text(encoding="utf-8", errors="replace")
    head = re.search(r"^sha256: (\w+)", text, re.M)
    if head and head.group(1) != pe.sha:
        raise SystemExit(f"{dump}: sha256 does not match {dll}")
    rows = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        name = block.split("\n", 1)[0].strip()
        fn = re.search(r"^ref: \S+ \(\w+\) in (\S+) @ (\w+)", block, re.M)
        for m in CALL.finditer(block):
            if m.group("name") != name:
                continue
            default = m.group("lit") if m.group("lit") is not None else pe.cstr(int(m.group("addr"), 16))
            rows.append([name, default, Path(dll).name, fn.group(2) if fn else "", m.group(1),
                         m.group("flags").strip(), (m.group("help") or "").replace("\t", " "), m.group("obj")])
            break
    return rows


def main():
    out = sys.argv[1]
    rows = []
    args = sys.argv[2:]
    for dll, dump in zip(args[::2], args[1::2]):
        rows += parse(dll, dump)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["convar", "default", "dll", "function", "register_call", "flags", "help", "object"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
