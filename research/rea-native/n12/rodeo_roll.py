"""Grapple camera roll (CAM-11) replay: the native target (Grapple_CameraRoll 0x1407fac60) fed with the logged eye, aim
and hook, gated and smoothed like the caller View_CalcRoll (0x140afc480), compared with the measured camera roll.

  py -3 <this file> [run ...]   (cwd = phase2-local/data/<session>; no run = every run with [M10-GRC] lines)

Models (rows of the output):
  N6      what n6/grapple_roll.py did: hook = first attached point, on from the first to the last attached frame,
          first-order smoothing at 6.667 /s
  gate    native gate only: on while IsGrappleActive(), hook = the logged hook entity each frame; first-order smoothing
  smooth  native smoothing only: N6 gate, SmoothCD (critically damped spring, omega 6.667)
  native  both
Standard library only. Part of rea-native N12 (n12/N12-RODEO-ROLL.md).
"""
import re, glob, math, sys, bisect

KV = re.compile(r"([A-Za-z_]+)=(\S+)")
OMEGA = 6.6666665          # 0x1417f88f0, View_CalcRoll
EPS = 0.001                # 0x1417f8380 (double): both target and state below this -> state reset to 0
DIST_MAX, VIEW_MAX, STRENGTH, ROLL_MAX = 150.0, 65.0, 1.0, 20.0   # grapple_roll* (CAMERA-REFERENCE §3.5)

fr, gr = {}, {}
for f in glob.glob('platform/logs/client/*/*.log'):
    for l in open(f, encoding='utf-8', errors='replace'):
        if 'kind=frame' in l and 'side=cl' in l and 'vv=' in l:
            k = dict(KV.findall(l)); fr.setdefault(k['run'], []).append(k)
        elif '[M10-GRC]' in l:
            k = dict(KV.findall(l)); gr.setdefault(k['run'], []).append(k)
vec = lambda s: tuple(map(float, s.split(',')))
dot = lambda a, b: sum(x * y for x, y in zip(a, b))


def basis(pitch, yaw):
    p, y = math.radians(pitch), math.radians(yaw)
    f = (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), -math.sin(p))
    r = (math.sin(y), -math.cos(y), 0.0)
    u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
    return f, u


def target(eye, hook, f, u):
    """Grapple_CameraRoll, Source sign (N6: the camera roll is minus the function output)."""
    d = [hook[i] - eye[i] for i in range(3)]; L = math.sqrt(dot(d, d))
    if L <= 0: return 0.0
    sd = min(1.0, L / DIST_MAX)
    th = math.degrees(math.acos(max(-1, min(1, dot(d, f) / L)))); sa = min(1.0, th / VIEW_MAX)
    p = [d[i] - f[i] * dot(d, f) for i in range(3)]; pl = math.sqrt(dot(p, p))
    if pl <= 0: return 0.0
    p = [x / pl for x in p]; phi = math.acos(max(-1, min(1, dot(p, u))))
    k = max(0.0, min(1.0, (phi - math.pi / 2) / (math.pi / 2)))
    cr = [p[1] * u[2] - p[2] * u[1], p[2] * u[0] - p[0] * u[2], p[0] * u[1] - p[1] * u[0]]
    if dot(cr, f) < 0: phi = -phi
    return -sd * STRENGTH * sa * (1 - k) * max(-ROLL_MAX, min(ROLL_MAX, math.degrees(phi)))


def replay(run, native_gate, native_smooth):
    G = sorted(gr[run], key=lambda k: float(k['t'])); gt = [float(g['t']) for g in G]
    att = [(float(g['t']), vec(g['hook'])) for g in G if g['att'] == 'true']
    if not att: return None
    t0, h0 = att[0]; t1 = att[-1][0]
    x = vel = 0.0; prev = None; rows = []
    for k in sorted(fr.get(run, []), key=lambda k: float(k['t'])):
        t = float(k['t'])
        if t < t0 - 0.05 or t > t0 + 1.6: continue
        g = G[min(bisect.bisect_left(gt, t - 1e-4), len(G) - 1)]
        if native_gate: on, h = g['act'] == 'true', vec(g['hook'])
        else: on, h = t0 <= t <= t1, h0
        ea = vec(k['eang']); f, u = basis(ea[0], ea[1])
        tg = target(vec(k['epos']), h, f, u) if on else 0.0
        dt = t - prev if prev else 0.0; prev = t
        if not native_smooth:
            x += (tg - x) * min(1.0, OMEGA * dt)
        elif abs(tg) < EPS and abs(x) < EPS:
            x = vel = 0.0
        else:                                   # SmoothCD as in View_CalcRoll
            X = OMEGA * dt; ex = 1 / (1 + X + 0.48 * X * X + 0.235 * X * X * X)
            c = x - tg; tmp = (vel + OMEGA * c) * dt
            vel = (vel - OMEGA * tmp) * ex; x = tg + (c + tmp) * ex
        rows.append((t - t0, tg, x, vec(k['cang'])[2], g['att'][0], g['act'][0]))
    return rows


def summary(rows):
    mm = max(rows, key=lambda r: abs(r[3])); mp = max(rows, key=lambda r: abs(r[2]))
    rms = math.sqrt(sum((r[2] - r[3]) ** 2 for r in rows) / len(rows))
    return mm[3], mm[0], mp[2], mp[0], rms


if __name__ == '__main__':
    runs = sys.argv[1:] or sorted(gr, key=int)
    print('run    model   meas_peak@s    pred_peak@s    rms')
    for run in runs:
        for name, ng, ns in (('N6', 0, 0), ('gate', 1, 0), ('smooth', 0, 1), ('native', 1, 1)):
            rows = replay(run, ng, ns)
            if not rows: break
            print('%-6s %-7s %6.2f @%.2f   %6.2f @%.2f   %.2f' % ((run, name) + summary(rows)))
