"""Find .data qwords that point at a given string in a PE and hexdump around them.
Usage: python -I peek_refs.py <pe> <string> [span]"""
import struct, sys
b = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', b, 0x3c)[0]
base = struct.unpack_from('<Q', b, pe + 24 + 24)[0]
n = struct.unpack_from('<H', b, pe + 6)[0]; opt = struct.unpack_from('<H', b, pe + 20)[0]
secs = []
o = pe + 24 + opt
for _ in range(n):
    name = b[o:o+8].rstrip(b'\0').decode(); vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 8); secs.append((name, va, vs, rp, rs)); o += 40
def off2va(off):
    for name, va, vs, rp, rs in secs:
        if rp <= off < rp + rs: return base + va + off - rp, name
def va2off(v):
    for name, va, vs, rp, rs in secs:
        if va <= v - base < va + rs: return rp + v - base - va
def cstr(v):
    o = va2off(v)
    if o is None: return None
    e = b.find(b'\0', o, o + 80)
    s = b[o:e]
    return s.decode('latin1') if e > o and all(32 <= c < 127 for c in s) else None
s = sys.argv[2].encode() + b'\0'
span = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x40
i = b.find(b'\0' + s) + 1
sva, sname = off2va(i)
print(f'string @ {sva:x} ({sname}) base {base:x}')
p = struct.pack('<Q', sva)
j = b.find(p)
while j >= 0:
    va, name = off2va(j)
    print(f'-- ptr @ {va:x} ({name})')
    for k in range(j - span, j + span, 8):
        q = struct.unpack_from('<Q', b, k)[0]
        lo, hi = struct.unpack_from('<ii', b, k)
        f1, f2 = struct.unpack_from('<ff', b, k)
        print(f'  {k - j:+4x}  {q:016x}  i=({lo},{hi})  f=({f1:.4g},{f2:.4g})  {cstr(q) or ""}')
    j = b.find(p, j + 1)
