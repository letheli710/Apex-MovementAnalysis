"""N13: proximity detach and wall hit of the straight wall pulls (m10_g_d400) with the logged hook entity.

  py -3 <this file> [run ...]   (cwd = phase2-local/data/20261023_234226_N6_grapple_frida2; runs 20318 20319)

Per client frame from 90 u out: the pre-move distances of the two rules to the hook entity ([M10-GRC] hook),
  dmin = min(|P - origin|, |P - (origin + 70)|)   native pull step 0x14066fb60 (origin and EyePosition)
  dseg = distance to the segment [origin, origin + 72]   HSD-Unity GrappleAbility.SegmentDistance
the velocity change of the frame (pull: dvx > 0; no pull: dvz = -6.25 = gravity only) and the client att flag.
Then the wall hit: one frame takes vx from ~575 to ~6.5 and adds vz. Solving v' = v - (v.n) n for a wall normal
n = (-cos a, 0, sin a) from the vx left over gives a, and the vz it predicts is printed next to the measured one.
Standard library only. Part of rea-native N13 (N13-GRAPPLE-DETACH.md).
"""
import csv, math, sys, bisect, re, glob

KV = re.compile(r"([A-Za-z_]+)=(\S+)")
G0 = 750.0 / 120.0                           # gravity per 120 Hz command (sv_gravity 750)
runs = sys.argv[1:] or ['20318', '20319']
gr = {}
for f in glob.glob('platform/logs/client/*/script.log'):
    for l in open(f, encoding='utf-8', errors='replace'):
        if '[M10-GRC]' in l:
            k = dict(KV.findall(l)); gr.setdefault(k['run'], []).append(k)
F = {}
for r in csv.DictReader(open('report/rows.csv')):
    if r['kind'] == 'frame' and r['side'] == 'cl' and r['run'] in runs:
        F.setdefault(r['run'], []).append(r)
v3 = lambda s: tuple(map(float, s.split(',')))

for run in runs:
    G = sorted(gr[run], key=lambda k: float(k['t'])); gt = [float(k['t']) for k in G]
    P = next(v3(k['hook']) for k in G if k['att'] == 'true')
    print('run %s hook entity %s' % (run, ','.join('%.2f' % x for x in P)))
    prev = None
    for r in sorted(F[run], key=lambda r: float(r['t'])):
        t = float(r['t']); o = (float(r['ox']), float(r['oy']), float(r['oz'])); v = (float(r['vx']), float(r['vy']), float(r['vz']))
        g = G[min(bisect.bisect_left(gt, t - 1e-4), len(G) - 1)]
        dmin = min(math.dist(P, o), math.dist(P, (o[0], o[1], o[2] + 70)))
        dseg = math.dist(P, (o[0], o[1], o[2] + min(max(P[2] - o[2], 0), 72)))
        if prev and prev[2] < 90:
            dvx, dvz = v[0] - prev[1][0], v[2] - prev[1][2]
            print('  t=%.4f x=%.1f z=%.1f vx=%.1f dvx=%+.2f vz=%.1f dvz=%+.2f | pre dmin=%.1f dseg=%.1f | att=%s' % (
                t, o[0], o[2], v[0], dvx, v[2], dvz, prev[2], prev[3], g['att']))
            if dvx < -400:                   # the wall hit
                vx, vz = prev[1][0], prev[1][2] - G0 / 2
                s = next(s / 10000 for s in range(1, 2000) if vx * (s / 1e4) ** 2 + vz * (s / 1e4) * math.sqrt(1 - (s / 1e4) ** 2) >= v[0])
                c = math.sqrt(1 - s * s); vn = -vx * c + vz * s
                print('  wall hit: normal z %.4f (%.2f deg off vertical) -> predicted vz %.1f, measured %.1f' % (
                    s, math.degrees(math.asin(s)), vz - vn * s - G0 / 2, v[2]))
                break
        prev = (o, v, dmin, dseg)
