"""N13 look-away / rodeo grapple: how much of R5's "still attached" is the local S3 dedi re-attaching, and when the view rule fires.

  py -3 <this file> [run ...]   (cwd = phase2-local/data/<session>; no run = every run with [M10-GRC] lines)

Per run:
  1. attach intervals of the client ([M10-GRC] att) and of the dedi ([M10-GRS] att / pull), seconds after the fire (first act);
  2. the first client frame (after the pull start) on which each view-rule variant sees the hook behind the view, on R5's own state:
       eye90   angle(view, hook - real eye) > 90 (N6 lookaway_cross90.py)
       unity   angle(view, hook - (origin + 70)) > 90 (HSD-Unity GrappleAbility.DetachS21 with NativeGrapple, lookAwayAngle 90)
       nat_hN  native Grapple_DetachRules 0x14066f600: d . view < 0 with d = hook + (0,0,grapple_lift 25) - (origin + (0,0,N + 1));
               N is the player float +0x1de8 (not identified; 0 / 36 / 69 tried)
     and the measured first client frame with att false (snapshot-quantized: the flag follows the dedi's 20 Hz updates);
  3. the camera-roll peak of the N12 native model (n12/rodeo_roll.py, SmoothCD) as measured (hybrid: client + dedi re-attach) and
     with the grapple off from the client's first release on (client only), cut either at the logged flag or at the view rule
     (nat_h0) -- the true client command lies between the two.
Standard library only. Part of rea-native N13 (N13-GRAPPLE-DETACH.md).
"""
import os, re, glob, math, bisect, sys, copy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'n12'))
_argv, sys.argv = sys.argv, sys.argv[:1]
import rodeo_roll as rr                      # parses the client logs of the cwd session on import
sys.argv = _argv

KV = re.compile(r"([A-Za-z_]+)=(\S+)")
LIFT = 25.0                                  # grapple_lift (ConVar, registration default "25")
gs = {}
for f in glob.glob('platform/logs/server/*/script.log'):
    for l in open(f, encoding='utf-8', errors='replace'):
        if '[M10-GRS]' in l:
            k = dict(KV.findall(l)); gs.setdefault(k['run'], []).append(k)
vec = rr.vec
dot = rr.dot


def intervals(rows, key, t0):
    out, on = [], None
    for k in rows:
        t, a = float(k['t']), k[key] == 'true'
        if a and on is None: on = t
        if not a and on is not None: out.append('%.3f-%.3f' % (on - t0, t - t0)); on = None
    if on is not None: out.append('%.3f-..' % (on - t0))
    return ' '.join(out)


def view_rule(run, G, fire, P, pull):
    first = {}
    for k in sorted(rr.fr.get(run, []), key=lambda k: float(k['t'])):
        t = float(k['t'])
        if t < pull: continue
        f = vec(k['vv']); n = math.sqrt(dot(f, f)); f = [x / n for x in f]
        o, e = vec(k['o']), vec(k['epos'])
        tests = {'eye90': dot(f, [P[j] - e[j] for j in range(3)]) < 0,
                 'unity': dot(f, [P[0] - o[0], P[1] - o[1], P[2] - o[2] - 70]) < 0}
        for h in (0, 36, 69):
            tests['nat_h%d' % h] = dot(f, [P[0] - o[0], P[1] - o[1], P[2] + LIFT - o[2] - h - 1]) < 0
        for name, b in tests.items():
            if b and name not in first: first[name] = t - fire
    return first


def roll_peak(run, cut):
    keep = rr.gr[run]
    if cut is not None:
        rr.gr[run] = copy.deepcopy(keep)
        for k in rr.gr[run]:
            if float(k['t']) >= cut: k['act'] = k['att'] = 'false'
    try:
        rows = rr.replay(run, 1, 1)
    finally:
        rr.gr[run] = keep
    m = max(rows, key=lambda r: abs(r[2]))
    meas = max(rows, key=lambda r: abs(r[3]))
    return abs(m[2]), m[0], abs(meas[3]), meas[0]


for run in sys.argv[1:] or sorted(rr.gr, key=int):
    G = sorted(rr.gr[run], key=lambda k: float(k['t']))
    if not any(k['att'] == 'true' for k in G): continue
    fire = next(float(k['t']) for k in G if k['act'] == 'true')
    i_att = next(i for i, k in enumerate(G) if k['att'] == 'true')
    t_att, P = float(G[i_att]['t']), vec(G[i_att]['hook'])
    rel = next((float(k['t']) for k in G[i_att:] if k['att'] == 'false'), None)
    S = sorted(gs.get(run, []), key=lambda k: float(k['t']))
    print('run %s  hook %s' % (run, ','.join('%.1f' % x for x in P)))
    print('  client att : ' + intervals(G, 'att', fire))
    print('  dedi   att : ' + intervals(S, 'att', fire) + '   dedi pull: ' + intervals(S, 'pull', fire))
    vr = view_rule(run, G, fire, P, t_att + 0.2)
    print('  view rule first frame: ' + '  '.join('%s %.3f' % (k, vr[k]) for k in ('eye90', 'unity', 'nat_h0', 'nat_h36', 'nat_h69') if k in vr)
          + ('   measured client release %.3f' % (rel - fire) if rel else ''))
    off = t_att - fire
    p, tp, m, tm = roll_peak(run, None)
    print('  roll peak: measured %.2f @%.2f  model hybrid %.2f @%.2f' % (m, tm + off, p, tp + off), end='')
    for name, cut in (('client-only (cut at flag)', rel), ('client-only (cut at rule)', fire + vr['nat_h0'] if 'nat_h0' in vr else None)):
        if cut is None: continue
        p2, tp2, _, _ = roll_peak(run, cut)
        print('  %s %.2f @%.2f' % (name, p2, tp2 + off), end='')
    print()
