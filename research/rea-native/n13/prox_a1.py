"""N13 A-1: on which command each proximity rule fires in the M4 wall pulls, on R5's states and on Unity Reference's states.

  py -3 <this file> <m4 trials dir> <FeelBatch out dir>
     <m4 trials dir>     phase2-local/m4/trials
     <FeelBatch out dir> HSD.R5Replay.Editor.FeelBatch.Run -trial <the 4 m4_grapple_* trials> -scenarios phase2-local/m4/unity/scenarios.json -out <dir>

Rules (state for command n = post-state of command n - 1):
  nat  native pull step 0x14066fb60: dist = min(|P - origin|, |P - (origin + 70)|); fires if dist < 33, or dist < 50 and
       dist < 33 + (v.d^ / 400) * 1.5 * 17, d = P + (0,0,25) - (origin + (0,0,1))  (grapple_speedRampMax_human 400, grapple_lift 25)
  uni  HSD-Unity NativeGrapple: segment distance to [origin, origin + 72]; vr toward P from origin + 36; ramp / 800
The hook point P: the aim ray from the standing eye (70) hits the wall face x = -13706 (what Unity uses), or that point moved
INSET u into the wall (R5's hook entity in the d400 pulls on the same wall sits at x -13697.96: prox_d400.py).
R5's detach command = the first command without pull acceleration; Unity's = its GRAPPLE_RELEASE event.
Also: apex height above the start and the vz just before / after the wall hit.
Standard library only. Part of rea-native N13 (N13-GRAPPLE-DETACH.md).
"""
import csv, math, os, sys

WALL_X = -13706.0
TRIALS = ('m4_grapple_hold_r1701', 'm4_grapple_hold_r1702', 'm4_grapple_near_r2101', 'm4_grapple_near_r2102')


def native(P, o, v):
    dist = min(math.dist(P, o), math.dist(P, (o[0], o[1], o[2] + 70)))
    d = (P[0] - o[0], P[1] - o[1], P[2] + 25 - o[2] - 1)
    vr = sum(a * b for a, b in zip(v, d)) / math.sqrt(sum(a * a for a in d))
    return dist < 33 or (dist < 50 and dist < 33 + vr / 400 * 1.5 * 17), dist


def unity(P, o, v):
    dist = math.dist(P, (o[0], o[1], o[2] + min(max(P[2] - o[2], 0.0), 72.0)))
    c = (P[0] - o[0], P[1] - o[1], P[2] - o[2] - 36)
    vr = sum(a * b for a, b in zip(v, c)) / math.sqrt(sum(a * a for a in c))
    return dist < 33 or (dist < 50 and dist < 33 + vr / 800 * 1.5 * 17), dist


def load(path):
    return [(int(r['step']), (float(r['pos_x']), float(r['pos_y']), float(r['pos_z'])),
             (float(r['vel_x']), float(r['vel_y']), float(r['vel_z'])), r.get('events', '') or '') for r in csv.DictReader(open(path))]


def wall_hit(S):
    for a, b in zip(S, S[1:]):
        if a[2][0] > 100 and b[2][0] < 20: return b[0], a[2][2], b[2][2]


tdir, udir = sys.argv[1], sys.argv[2]
for name in TRIALS:
    R = load(os.path.join(tdir, name, 'samples.csv'))
    U = load(os.path.join(udir, 'M4_' + name, 'reference.csv'))
    fire = next(r for r in csv.DictReader(open(os.path.join(tdir, name, 'samples.csv'))) if r['pressed'])
    hz = float(fire['pos_z']) + 70 + (WALL_X - float(fire['pos_x'])) * math.tan(math.radians(-float(fire['in_pitch'])))
    u_pull = next(s for s, _, _, e in U if 'GRAPPLE_PULL' in e)
    u_rel = next((s, e.split('GRAPPLE_RELEASE_')[1].split('|')[0]) for s, _, _, e in U if 'GRAPPLE_RELEASE' in e)
    r_rel = next(R[i][0] for i in range(1, len(R)) if R[i][0] > u_pull + 20 and R[i - 1][2][0] > 100 and abs(R[i][2][0] - R[i - 1][2][0]) < 0.05)
    z0 = R[0][1][2]
    print('%s  R5 detach %d | Unity %s %d | apex R5 %.1f Unity %.1f | wall hit (step, vz before, after) R5 %s Unity %s' % (
        name, r_rel, u_rel[1], u_rel[0], max(x[1][2] for x in R) - z0, max(x[1][2] for x in U) - z0,
        '%d %.1f %.1f' % wall_hit(R), '%d %.1f %.1f' % wall_hit(U)))
    for inset in (0.0, 8.0):
        P = (WALL_X + inset, float(fire['pos_y']), hz)
        out = []
        for tag, S in (('R5', R), ('Unity', U)):
            for rule, fn in (('nat', native), ('uni', unity)):
                hit = next(((S[i][0], fn(P, S[i - 1][1], S[i - 1][2])[1]) for i in range(1, len(S))
                            if S[i][0] > u_pull and fn(P, S[i - 1][1], S[i - 1][2])[0]), (None, 0))
                out.append('%s-state %s %d (%.1f u)' % (tag, rule, hit[0], hit[1]))
        print('   hook %.0f u in: ' % inset + ' | '.join(out))
