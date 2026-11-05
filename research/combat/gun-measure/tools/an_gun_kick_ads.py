"""Decompile rule for the gun jolt against R5's per-frame view model log (s3 fr_ runs).
  py -3 an_gun_kick_ads.py <s3 run dir of HSD-RawData gun-measure> <dir with springs.txt and the weapon .txt files of S21>
x (+0x3514): += back*hardPitch*scale, v += back*softPitch*20*scale; y (+0x3518): += dYaw*scale, v += dYawSpeed*scale.
View model: forward += x*zf, right += side.y*y*zf, roll += roll.y*y*zf - punchRoll."""
import gzip, math, os, re, statistics as st, sys, csv, json
sys.stdout.reconfigure(encoding='utf-8')
R, SRC = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guns as GUNS


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


def springs():
    T = open(SRC + '/springs.txt', encoding='utf-8', errors='replace').read()
    out = {}
    for m in re.finditer(r'"(\w+)"\s*\{([^{}]*)\}', T):
        out[m[1]] = {a: float(b) for a, b in re.findall(r'"(\w+)"\s*"([-\d.]+)"', m[2])}
    return out


def fields(cls):
    T = open(f'{SRC}/{cls}.txt', encoding='utf-8', errors='replace').read()
    T = T.split('"Mods"')[0]
    return dict(re.findall(r'"(\w+)"\s*"([^"]*)"', T))


def rows(p):
    op = gzip.open if p.endswith('.gz') else open
    with op(p, 'rt', encoding='utf-8', newline='') as f:
        r = csv.reader(f); k = next(r)
        for l in r:
            if len(l) != len(k): continue
            try: yield dict(zip(k, map(float_or, l)))
            except ValueError: pass


def float_or(s):
    try: return float(s)
    except ValueError: return s


print('loading')
F = [r for r in rows(R + '/frames.csv.gz') if isinstance(r.get('vmF'), float)]
S = list(rows(R + '/shots.csv'))
M = {}
for l in open(R + '/marks.tsv', encoding='utf-8'):
    a = l.rstrip('\n').split('\t')
    if len(a) >= 3: M.setdefault(a[0], []).append((float(a[1]), a[2]))
# wall clock to frame t: wall.txt holds the origin
W = open(R + '/wall.txt').read().strip()
print('wall', W, 'frames', len(F), 'shots', len(S))
wall0 = int(W) / 1000
SP = springs()
V = GUNS.GUNS if hasattr(GUNS, 'GUNS') else None
print(type(V), list(V)[:3] if V else dir(GUNS))
res = []
import bisect
FT = [r['t'] for r in F]; ST = [r['t'] for r in S]
for g, info in V.items():
    cls = 'mp_weapon_' + info
    try: f = fields(cls)
    except Exception as e: print('skip', g, e); continue
    back = float(f.get('viewmodel_jolt_backwardPerShot', 0)); scale = float(f.get('viewmodel_jolt_scale', 0))
    if not scale: continue
    sd = [float(x) for x in f.get('viewmodel_jolt_side', '0 0 0').split()]; rd = [float(x) for x in f.get('viewmodel_jolt_roll', '0 0 0').split()]
    sp = SP[f['viewmodel_spring_jolt']]
    hardP = float(f['viewkick_pitch_hardScale']); softP = float(f['viewkick_pitch_softScale'])
    for mode, tag in (('ads', f'fr_{g}_adshold'),):
        if tag not in M: continue
        a = M[tag][0][0] - wall0; b = M[tag][-1][0] - wall0 + 0.2
        i0, i1 = bisect.bisect_left(FT, a), bisect.bisect_right(FT, b + 1.0)
        fr = F[i0:i1]; sh = S[bisect.bisect_left(ST, a):bisect.bisect_right(ST, b)]
        if len(sh) < 2 or len(fr) < 10: continue
        t0 = sh[0]['t']; before = [r for r in fr if t0 - 0.15 <= r['t'] < t0]
        if not before: continue
        base = {k: st.mean(r[k] for r in before) for k in ('vmF', 'vmR', 'vmU', 'vmaR')}
        x = vx = y = vy = 0.0; n = 0; last_t = before[-1]['t']
        err = []; pk = [0, 0]; py = [0, 0]; pr = [0, 0]
        for r in fr:
            if r['t'] < t0 - 0.02: continue
            if r['t'] > sh[-1]['t'] + 0.2: break
            zf = r['zf']
            kx = sp['hipfire_pitch_springConstant'] + (sp['ADS_pitch_springConstant'] - sp['hipfire_pitch_springConstant']) * zf
            dx = sp['hipfire_pitch_damping'] + (sp['ADS_pitch_damping'] - sp['hipfire_pitch_damping']) * zf
            ky = sp['hipfire_yaw_springConstant'] + (sp['ADS_yaw_springConstant'] - sp['hipfire_yaw_springConstant']) * zf
            dy = sp['hipfire_yaw_damping'] + (sp['ADS_yaw_damping'] - sp['hipfire_yaw_damping']) * zf
            dt = r['ft']
            x, vx = solve(x, vx, kx, dx, dt); y, vy = solve(y, vy, ky, dy, dt)
            while n < len(sh) and sh[n]['t'] <= r['t']:
                q = sh[n]; n += 1
                x += back * hardP * scale; vx += back * softP * 20 * scale
                y += (q['s2Y1'] - q['s2Y0']) * scale; vy += (q['v2Y1'] - q['v2Y0']) * scale
            mF = x * zf; mR = sd[1] * y * zf; mRoll = rd[1] * y * zf
            aF = r['vmF'] - base['vmF']; aR = r['vmR'] - base['vmR']; aRoll = r['vmaR'] - base['vmaR'] + r['puR']
            err.append((aF - mF, aR - mR, aRoll - mRoll, aF, mF, aRoll, mRoll))
            if abs(aF) > abs(pk[0]): pk[0] = aF
            if abs(mF) > abs(pk[1]): pk[1] = mF
        rms = lambda i: math.sqrt(st.mean(e[i] ** 2 for e in err))
        print(f"{g:12s} {mode} shots {len(sh):3d} frames {len(err):4d} peak vmF {pk[0]:+.3f} model {pk[1]:+.3f} | rms F {rms(0):.3f} R {rms(1):.3f} rollNoPunch {rms(2):.3f} | sizeF {math.sqrt(st.mean(e[3]**2 for e in err)):.3f} sizeRoll {math.sqrt(st.mean(e[5]**2 for e in err)):.3f} modelRoll {math.sqrt(st.mean(e[6]**2 for e in err)):.3f}")
