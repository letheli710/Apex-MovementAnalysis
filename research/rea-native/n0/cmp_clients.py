"""Locate SDK client byte patterns in r5apex.exe and r5apex_dx12.exe and compare the
containing functions (bounds from .pdata). Usage: cmp_clients.py <sdk src> <exe a> <exe b>"""
import re, struct, sys, pathlib, json

def load(p):
    b = pathlib.Path(p).read_bytes()
    pe = struct.unpack_from('<I', b, 0x3c)[0]
    n = struct.unpack_from('<H', b, pe + 6)[0]
    opt = struct.unpack_from('<H', b, pe + 20)[0]
    secs = {}
    o = pe + 24 + opt
    for _ in range(n):
        name = b[o:o + 8].rstrip(b'\0').decode(errors='replace')
        vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 8)
        secs[name] = (va, vs, rp, rs)
        o += 40
    va, vs, rp, rs = secs['.pdata']
    funcs = [struct.unpack_from('<III', b, rp + i * 12)[:2] for i in range(min(vs, rs) // 12)]
    funcs = sorted(f for f in funcs if f[0])
    return b, secs, funcs

def rva_to_off(secs, rva):
    for va, vs, rp, rs in secs.values():
        if va <= rva < va + max(vs, rs):
            return rp + rva - va
    return None

def pat_regex(p):
    out = b''
    for t in p.split():
        out += b'.' if t.startswith('?') else re.escape(bytes([int(t, 16)]))
    return re.compile(out, re.S)

def containing(funcs, rva):
    lo, hi = 0, len(funcs) - 1
    while lo <= hi:
        m = (lo + hi) // 2
        s, e = funcs[m]
        if rva < s: hi = m - 1
        elif rva >= e: lo = m + 1
        else: return s, e
    return None

def main(src, ea, eb):
    pats = []
    for f in pathlib.Path(src, 'game', 'client').rglob('*.cpp'):
        txt = f.read_text(errors='replace')
        for m in re.finditer(r'Module_FindPattern\(\s*g_GameDll\s*,\s*((?:"[^"]*"\s*)+)\)(?:\s*\.\s*\w+\([^)]*\))*\s*\.\s*GetPtr\(\s*(\w+)', txt):
            pats.append((m.group(2), ''.join(re.findall(r'"([^"]*)"', m.group(1))), f.name))
    A, B = load(ea), load(eb)
    rows = []
    for name, p, fn in pats:
        rx = pat_regex(p)
        r = {'name': name, 'file': fn}
        for tag, (b, secs, funcs) in (('a', A), ('b', B)):
            va, vs, rp, rs = secs['.text']
            hits = [m.start() for m in rx.finditer(b, rp, rp + rs)]
            r[tag + '_hits'] = len(hits)
            if len(hits) == 1:
                rva = hits[0] - rp + va
                r[tag + '_fn'] = containing(funcs, rva)
                r[tag + '_rva'] = rva
        if r.get('a_fn') and r.get('b_fn'):
            (sa, xa), (sb, xb) = r['a_fn'], r['b_fn']
            ba = A[0][rva_to_off(A[1], sa):rva_to_off(A[1], xa)]
            bb = B[0][rva_to_off(B[1], sb):rva_to_off(B[1], xb)]
            r['len'] = (len(ba), len(bb))
            if len(ba) == len(bb):
                diff = [i for i in range(len(ba)) if ba[i] != bb[i]]
                r['diff_bytes'] = len(diff)
        rows.append(r)
    json.dump(rows, sys.stdout, indent=0, default=str)

if __name__ == '__main__':
    main(*sys.argv[1:4])
