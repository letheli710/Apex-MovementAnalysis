"""Print float/double/int values at VAs in a PE (constants referenced by decompiled code).
Usage: python -I read_consts.py <pe> <va_hex> [...]"""
import struct, sys
b = open(sys.argv[1], 'rb').read()
pe = struct.unpack_from('<I', b, 0x3c)[0]
base = struct.unpack_from('<Q', b, pe + 48)[0]
n = struct.unpack_from('<H', b, pe + 6)[0]; opt = struct.unpack_from('<H', b, pe + 20)[0]
secs = []
o = pe + 24 + opt
for _ in range(n):
    vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 8); secs.append((va, rs, rp)); o += 40
for a in sys.argv[2:]:
    r = int(a, 16) - base
    off = next((rp + r - va for va, rs, rp in secs if va <= r < va + rs), None)
    if off is None:
        print(a, 'not in file (bss)'); continue
    f, = struct.unpack_from('<f', b, off); d, = struct.unpack_from('<d', b, off); i, = struct.unpack_from('<i', b, off)
    print(f'{a}  float={f:.7g}  double={d:.10g}  int={i}  hex={b[off:off+8].hex()}')
