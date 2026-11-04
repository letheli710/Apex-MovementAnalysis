#!/usr/bin/env python3
"""What the gun does on the move, from the no-fire runs: mean pose against standing, swing per axis, the period of the swing.
  py -3 -I an_hold_pose.py <runs dir> <out tsv>"""
import glob, math, os, re, statistics as st, sys
RG = re.compile(r"\] g t=([\d.]+) zf=(\S+) fov=(\S+) sp=(\S+) clip=(-?\d+) rel=(\d) spd=(\S+) vz=(\S+) gr=(\d) duck=(\d) spr=(\d) wr=(\d) m=([-\d.]+),([-\d.]+),([-\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+) w=(\S+)")
def frames(p):
    o = []
    for l in open(p, encoding='utf-8', errors='replace'):
        g = RG.search(l)
        if g:
            v = g.groups()
            o.append((float(v[0]), float(v[1]), float(v[6]), float(v[12]) - float(v[15]), -(float(v[13]) - float(v[16])), float(v[14]) - float(v[17]), int(v[10]), int(v[8])))
    return o
def period(t, x):
    m = st.mean(x)
    up = [t[i] for i in range(1, len(x)) if x[i - 1] < m <= x[i]]
    gaps = [b - a for a, b in zip(up, up[1:]) if b - a > 0.05]
    return st.median(gaps) if len(gaps) >= 2 else None
dst = os.path.abspath(sys.argv[2])
os.chdir(sys.argv[1])
rows = {}
for gun in ('r301', 'wingman'):
    for state in ('stand', 'walk', 'sprint', 'crouch', 'crouchwalk', 'slide'):
        p = f'sw_{gun}_{state}_hip.txt'
        if not os.path.exists(p): continue
        fr = [r for r in frames(p) if r[1] == 0]
        if state in ('stand', 'crouch'):
            sel = [r for r in fr if r[2] < 1]
        elif state == 'walk': sel = [r for r in fr if 170 < r[2] < 176]
        elif state == 'sprint': sel = [r for r in fr if r[2] > 255 and r[6]]
        elif state == 'crouchwalk': sel = [r for r in fr if 70 < r[2] < 90]
        else: sel = [r for r in fr if r[2] > 300]
        if len(sel) < 20: print(gun, state, 'few', len(sel)); continue
        # the last stretch: the pose has settled
        sel = sel[len(sel) // 3:]
        t = [r[0] for r in sel]
        m = [st.mean(r[k] for r in sel) for k in (3, 4, 5)]
        sw = [(max(r[k] for r in sel) - min(r[k] for r in sel)) / 2 for k in (3, 4, 5)]
        rows[gun, state] = (m, sw, period(t, [r[5] for r in sel]), period(t, [r[4] for r in sel]), len(sel), t[-1] - t[0])
out = open(dst, 'w', encoding='utf-8', newline='\n')
out.write('gun\tstate\tposeF\tposeR\tposeU\tswingF\tswingR\tswingU\tperiodU\tseconds\n')
for (g, s), (m, sw, pu, pr, n, d) in rows.items():
    b = rows[g, 'stand'][0]
    out.write(f"{g}\t{s}\t{m[0]-b[0]:.2f}\t{m[1]-b[1]:.2f}\t{m[2]-b[2]:.2f}\t{sw[0]:.2f}\t{sw[1]:.2f}\t{sw[2]:.2f}\t{'' if pu is None else round(pu, 3)}\t{d:.2f}\n")
