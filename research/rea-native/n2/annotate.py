"""Annotate decompiled code with the N1 names, so it can be read.

Replaces, in the Ghidra output:
  DAT_<descriptor>      -> SF<key>          setfile key descriptor (index read)
  DAT_<convar object+0x40> -> CV<name>      ConVar value
  FUN_<entry>           -> <N1 / SDK name>  named functions
and adds the float value of each referenced read-only constant as a comment.

Usage: annotate.py <in.c> <out.c> <raw dir> <names-dx12.tsv> <seeds-dx12.tsv> <exe>
Output stays under local/ (decompiled game code).
"""
import csv
import re
import struct
import sys

IMAGE_BASE = 0x140000000


def load_exe(path):
    b = open(path, 'rb').read()
    pe = struct.unpack_from('<I', b, 0x3c)[0]
    n = struct.unpack_from('<H', b, pe + 6)[0]
    opt = struct.unpack_from('<H', b, pe + 20)[0]
    secs, o = [], pe + 24 + opt
    for _ in range(n):
        name = b[o:o + 8].rstrip(b'\0').decode(errors='replace')
        vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 8)
        secs.append((name, va, rs, rp))
        o += 40
    return b, secs


def read_float(b, secs, va):
    r = va - IMAGE_BASE
    for name, sva, rs, rp in secs:
        if name in ('.rdata', '_RDATA') and sva <= r < sva + rs - 4:
            return struct.unpack_from('<f', b, rp + r - sva)[0]
    return None


def main(src, dst, raw, names_tsv, seeds_tsv, exe):
    sub = {}
    with open(f'{raw}/setfile-descriptors.tsv', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            sub[r['descriptor'].lower()] = 'SF' + r['key']
    with open(f'{raw}/convars.tsv', encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            if r['offset'] == '0x40':
                obj = int(r['object'], 16) + 0x40
                sub[f'{obj:x}'] = 'CV' + r['convar']
    fn = {}
    for path in (seeds_tsv, names_tsv):
        for line in open(path, encoding='utf-8').read().splitlines():
            if line and not line.startswith('#'):
                t = line.split('\t')
                if path == names_tsv:
                    fn.setdefault(t[0].lower(), t[1])
                elif t[1] != 'NONE':
                    fn.setdefault(t[1].lower(), t[0])
    b, secs = load_exe(exe)
    text = open(src, encoding='utf-8').read()

    def dat(m):
        a = m.group(1).lower()
        if a in sub:
            return sub[a]
        v = read_float(b, secs, int(a, 16))
        if v is not None and v == v and 1e-6 < abs(v) < 1e7:
            return f'{m.group(0)}/*{v:g}*/'
        return m.group(0)

    text = re.sub(r'_?DAT_([0-9a-fA-F]{9})', dat, text)
    text = re.sub(r'FUN_([0-9a-fA-F]{9})', lambda m: fn.get(m.group(1).lower(), m.group(0)), text)
    open(dst, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    main(*sys.argv[1:7])
