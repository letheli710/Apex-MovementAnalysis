"""Read Titanfall 2 MDL v53 headers: bones, attachments, pose params, sequences, includes.

Research tool only: reads numbers and names from the local game's models, writes no game data.
"""
import struct
import sys


def cstr(b, off):
    end = b.find(b"\0", off)
    return b[off:end].decode("latin1")


class Mdl:
    BONE_SIZE = 244

    def __init__(self, path):
        self.path = path
        self.b = open(path, "rb").read()
        b = self.b
        assert b[:4] == b"IDST" and struct.unpack_from("<i", b, 4)[0] == 53, path
        self.name = cstr(b, 0x10)
        i = lambda o: struct.unpack_from("<i", b, o)[0]
        self.i = i
        self.numbones, self.boneindex = i(0xA0), i(0xA4)
        self.numhitboxsets, self.hitboxsetindex = i(0xB0), i(0xB4)
        self.numlocalanim, self.localanimindex = i(0xB8), i(0xBC)
        self.numlocalseq, self.localseqindex = i(0xC0), i(0xC4)
        self.eye = struct.unpack_from("<3f", b, 0x54)
        self.hull = struct.unpack_from("<6f", b, 0x6C)
        self.bones = []
        for n in range(self.numbones):
            o = self.boneindex + n * self.BONE_SIZE
            self.bones.append(
                dict(
                    idx=n,
                    name=cstr(b, o + i(o)),
                    parent=i(o + 4),
                    pos=struct.unpack_from("<3f", b, o + 0x20),
                    quat=struct.unpack_from("<4f", b, o + 0x2C),
                    rot=struct.unpack_from("<3f", b, o + 0x3C),
                    flags=i(o + 0xB8),
                    proctype=i(o + 0xBC),
                    procindex=i(o + 0xC0),
                    physbone=i(o + 0xC4),
                    off=o,
                )
            )


def hexdump(b, off, n=64):
    for k in range(0, n, 16):
        chunk = b[off + k : off + k + 16]
        print(f"{off+k:08x}  " + " ".join(f"{x:02x}" for x in chunk))


if __name__ == "__main__":
    m = Mdl(sys.argv[1])
    print(m.name, "bones", m.numbones, "anims", m.numlocalanim, "seqs", m.numlocalseq, "eye", m.eye, "hull", m.hull)
    for x in m.bones[:40]:
        print(x["idx"], x["name"], x["parent"], [round(v, 2) for v in x["pos"]], "flags", hex(x["flags"]), "proc", x["proctype"])
    b = m.b
    # header dump as ints from 0xA0
    for o in range(0xA0, 0x1F0, 8):
        print(hex(o), m.i(o), m.i(o + 4), hex(m.i(o + 4)))
