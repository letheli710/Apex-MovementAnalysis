"""Read 32-bit floats / ints at virtual addresses of a PE image (no dependencies).
Usage: pe_floats.py <exe> <hexVA> [<hexVA> ...]"""
import struct
import sys


def sections(data):
    pe = struct.unpack_from('<I', data, 0x3C)[0]
    nsec = struct.unpack_from('<H', data, pe + 6)[0]
    optsz = struct.unpack_from('<H', data, pe + 20)[0]
    base = struct.unpack_from('<Q', data, pe + 24 + 24)[0]
    out = []
    o = pe + 24 + optsz
    for i in range(nsec):
        name = data[o:o + 8].rstrip(b'\0').decode('ascii', 'replace')
        vsize, va, rawsize, rawptr = struct.unpack_from('<IIII', data, o + 8)
        out.append((name, base + va, max(vsize, rawsize), rawptr, rawsize))
        o += 40
    return out


def main():
    exe = sys.argv[1]
    data = open(exe, 'rb').read()
    secs = sections(data)
    for a in sys.argv[2:]:
        va = int(a, 16)
        for name, sva, size, rawptr, rawsize in secs:
            if sva <= va < sva + size:
                off = va - sva
                if off + 4 > rawsize:
                    print('%x %s (bss, no file data)' % (va, name))
                else:
                    f, = struct.unpack_from('<f', data, rawptr + off)
                    i, = struct.unpack_from('<I', data, rawptr + off)
                    print('%x %s float=%r u32=0x%08x' % (va, name, f, i))
                break
        else:
            print('%x not in any section' % va)


main()
