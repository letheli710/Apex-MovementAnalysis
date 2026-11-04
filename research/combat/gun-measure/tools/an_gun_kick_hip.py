"""Per-gun hip fit on taps + hold together: vmaP, vmaY = g * (camera - L), L a spring lag of the camera punch; vmF, vmU = a * vmaP, vmR = b * vmaY; vmaR + s2R = g2 * lag of yaw/pitch. The source of the hip motion is not known: this is a fit, not a rule (RECOIL-VIEW section 11.3). D-GUNKICK.tsv is its output.
  py -3 an_gun_kick_hip.py <s3 run dir of HSD-RawData gun-measure> <out tsv>"""
import bisect, csv, gzip, math, os, statistics as st, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guns as GUNS
R, OUT = sys.argv[1], sys.argv[2]


def float_or(s):
    try: return float(s)
    except ValueError: return s


def rows(p):
    op = gzip.open if p.endswith('.gz') else open
    with op(p, 'rt', encoding='utf-8', newline='') as f:
        r = csv.reader(f); k = next(r)
        for l in r:
            if len(l) == len(k): yield dict(zip(k, map(float_or, l)))


F = [r for r in rows(R + '/frames.csv.gz') if isinstance(r.get('vmF'), float)]
Sh = list(rows(R + '/shots.csv'))
wall0 = int(open(R + '/wall.txt').read()) / 1000
M = {}
for l in open(R + '/marks.tsv', encoding='utf-8'):
    a = l.rstrip('\n').split('\t')
    if len(a) >= 3: M.setdefault(a[0], []).append((float(a[1]) - wall0, a[2]))
FT = [r['t'] for r in F]; ST = [r['t'] for r in Sh]
def cutF(a, b): return F[bisect.bisect_left(FT, a):bisect.bisect_right(FT, b)]
def cutS(a, b): return Sh[bisect.bisect_left(ST, a):bisect.bisect_right(ST, b)]


def solve(x, v, k, d, dt):
    disc = d * d - 4 * k
    if disc > 1e-9:
        r = math.sqrt(disc); r1 = (-d + r) / 2; r2 = (-d - r) / 2
        A = (v - r2 * x) / (r1 - r2); B = x - A; e1 = A * math.exp(r1 * dt); e2 = B * math.exp(r2 * dt)
        return e1 + e2, r1 * e1 + r2 * e2
    if disc < -1e-9:
        w = math.sqrt(-disc) / 2; s = -d / 2; b = (v - s * x) / w; e = math.exp(s * dt); c = math.cos(w * dt); n = math.sin(w * dt)
        return e * (x * c + b * n), e * (s * (x * c + b * n) + w * (b * c - x * n))
    s = -d / 2; b = v - s * x; e = math.exp(s * dt)
    return e * (x + b * dt), e * (s * (x + b * dt) + b)


def lag(fr, c, k, d):
    L = c[0]; v = 0.0; out = []
    for i, r in enumerate(fr):
        x, v = solve(L - c[i], v, k, d, r['ft']); L = x + c[i]; out.append(c[i] - L)
    return out


def segs(g):
    out = []
    for tag in (f'fr_{g}_taps', f'fr_{g}_hold'):
        if tag not in M: continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        sh = cutS(a, b)
        if not sh: continue
        t0 = sh[0]['t']; fr = cutF(t0 - 0.15, sh[-1]['t'] + 0.2)
        fr = [r for r in fr if r['ws'] != 1 or True]
        if len(fr) < 15 or any(r['zf'] > 0 for r in fr): continue
        n = len([r for r in fr if r['t'] < t0])
        if not n: continue
        out.append((tag, fr, n))
    return out


KS = (20, 40, 60, 80, 100, 150, 200, 300, 400, 600); DS = (4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 70)
def fit(ss, ch, cam, off=None):
    """off: extra added to the measured channel per frame"""
    Y, C = [], []
    for tag, fr, n in ss:
        b0 = st.mean(r[ch] + (r[off] if off else 0) for r in fr[:n])
        Y.append([r[ch] + (r[off] if off else 0) - b0 for r in fr]); C.append([r[cam] for r in fr])
    best = None
    for k in KS:
        for d in DS:
            M_ = [lag(s[1], c, k, d) for s, c in zip(ss, C)]
            sxy = sum(x * y for m, yy in zip(M_, Y) for x, y in zip(m, yy)); sxx = sum(x * x for m in M_ for x in m)
            if sxx < 1e-9: continue
            g = sxy / sxx
            n = sum(len(m) for m in M_)
            e = math.sqrt(sum((y - g * x) ** 2 for m, yy in zip(M_, Y) for x, y in zip(m, yy)) / n)
            if best is None or e < best[0]: best = (e, k, d, g)
    n = sum(len(y) for y in Y); sz = math.sqrt(sum(y * y for yy in Y for y in yy) / n)
    return best, sz


out = open(OUT, 'w', encoding='utf-8', newline='\n')
out.write('gun\tkP\tdP\tgP\trmsP\tsizeP\tkY\tdY\tgY\trmsY\tsizeY\tkR\tdR\tgR\trmsR\tsizeR\trollFromPitch\taF\tbU\tcR\trmsF\tsizeF\trmsU\tsizeU\trmsV\tsizeV\n')
for g in GUNS.GUNS:
    ss = segs(g)
    if not ss: print(g, 'none'); continue
    (eP, kP, dP, gP), szP = fit(ss, 'vmaP', 'puP')
    (eY, kY, dY, gY), szY = fit(ss, 'vmaY', 'puY')
    # roll beyond the -punch roll: which camera axis drives it
    (eR1, kR1, dR1, gR1), szR = fit(ss, 'vmaR', 'puY', 's2R')
    (eR2, kR2, dR2, gR2), _ = fit(ss, 'vmaR', 'puP', 's2R')
    fromP = eR2 < eR1
    eR, kR, dR, gR = (eR2, kR2, dR2, gR2) if fromP else (eR1, kR1, dR1, gR1)
    # position is a fixed share of the angles?
    xs = {k: [] for k in ('vmaP', 'vmaY', 'vmF', 'vmU', 'vmR')}
    for tag, fr, n in ss:
        base = {k: st.mean(r[k] for r in fr[:n]) for k in xs}
        for r in fr:
            for k in xs: xs[k].append(r[k] - base[k])
    slope = lambda a, b: sum(x * y for x, y in zip(xs[a], xs[b])) / max(sum(x * x for x in xs[a]), 1e-9)
    aF, bU, cR = slope('vmaP', 'vmF'), slope('vmaP', 'vmU'), slope('vmaY', 'vmR')
    rs = lambda a, b, s: math.sqrt(st.mean((y - s * x) ** 2 for x, y in zip(xs[a], xs[b])))
    size = lambda a: math.sqrt(st.mean(y * y for y in xs[a]))
    out.write(f"{g}\t{kP}\t{dP}\t{gP:.3f}\t{eP:.3f}\t{szP:.3f}\t{kY}\t{dY}\t{gY:.3f}\t{eY:.3f}\t{szY:.3f}\t{kR}\t{dR}\t{gR:.3f}\t{eR:.3f}\t{szR:.3f}\t{int(fromP)}\t{aF:.4f}\t{bU:.4f}\t{cR:.4f}\t{rs('vmaP','vmF',aF):.3f}\t{size('vmF'):.3f}\t{rs('vmaP','vmU',bU):.3f}\t{size('vmU'):.3f}\t{rs('vmaY','vmR',cR):.3f}\t{size('vmR'):.3f}\n")
    print(f"{g:11s} P k{kP} d{dP} g{gP:+.2f} rms {eP:.3f}/{szP:.3f} | Y k{kY} d{dY} g{gY:+.2f} {eY:.3f}/{szY:.3f} | R k{kR} d{dR} g{gR:+.2f} {'P' if fromP else 'Y'} {eR:.3f}/{szR:.3f} | F {aF:+.3f} {rs('vmaP','vmF',aF):.3f}/{size('vmF'):.3f} U {bU:+.3f} {rs('vmaP','vmU',bU):.3f}/{size('vmU'):.3f} V {cR:+.3f} {rs('vmaY','vmR',cR):.3f}/{size('vmR'):.3f}", flush=True)
