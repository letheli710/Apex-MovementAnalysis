"""Scan a client exe's .data for setfile key descriptors.

Layout found in N1 (dx12 client): +0x0 int32 index, -1 in the file and filled
at runtime; +0x4 int32 type; +0x8 pointer to the key name in a read-only
section. Prints one TSV row per descriptor: address, type, key.

Usage: scan_setfile_desc.py <exe> > descriptors.tsv
"""
import re
import struct
import sys

IMAGE_BASE = 0x140000000
NAME = re.compile(rb'[A-Za-z_][A-Za-z0-9_]{1,63}\Z')


def sections(b):
    pe = struct.unpack_from('<I', b, 0x3c)[0]
    n = struct.unpack_from('<H', b, pe + 6)[0]
    opt = struct.unpack_from('<H', b, pe + 20)[0]
    out, o = {}, pe + 24 + opt
    for _ in range(n):
        name = b[o:o + 8].rstrip(b'\0').decode(errors='replace')
        vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 8)
        out[name] = (va, vs, rp, rs)
        o += 40
    return out


def main(path):
    b = open(path, 'rb').read()
    secs = sections(b)
    rva, _, rp, rs = secs['.rdata']

    def rdata_string(va):
        r = va - IMAGE_BASE
        if not rva <= r < rva + rs:
            return None
        off = rp + r - rva
        end = b.find(b'\0', off, off + 65)
        if end < 0:
            return None
        s = b[off:end]
        return s.decode() if NAME.match(s) else None

    dva, _, drp, drs = secs['.data']
    print('descriptor\ttype\tkey')
    for off in range(drp, drp + drs - 16, 8):
        idx, typ = struct.unpack_from('<iI', b, off)
        if idx != -1 or typ > 16:
            continue
        ptr = struct.unpack_from('<Q', b, off + 8)[0]
        key = rdata_string(ptr)
        if key:
            print(f'{IMAGE_BASE + dva + off - drp:x}\t{typ}\t{key}')


if __name__ == '__main__':
    main(sys.argv[1])
