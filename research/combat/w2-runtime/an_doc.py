"""D.O.C. drone run: drone position in the player's yaw frame vs the script's desired point
(lifeline-heal-drone 3.2.2: dir = norm(right - 0.6 fwd), d0 72.5 / 40 crouched, h 70 / 46)."""
import math, re, sys
rows = []
for l in open(sys.argv[1], encoding="utf-8"):
    m = re.search(r't=([\d.]+) P o=([-\d.]+),([-\d.]+),([-\d.]+) yaw=([-\d.]+) v=([-\d.]+),([-\d.]+),([-\d.]+) duck=(\d) slide=(\d) spr=(\d) n=1 D o=([-\d.]+),([-\d.]+),([-\d.]+) a=([-\d.]+),([-\d.]+),([-\d.]+)', l)
    if m:
        rows.append([float(x) for x in m.groups()])
print("t      spd   duck  fwd_off  right_off  up_off  | want fwd/right/up   lag_fwd  pitch roll yawerr")
for r in rows[::3]:
    t, px, py, pz, yaw, vx, vy, vz, duck, slide, spr, dx, dy, dz, ap, ay, ar = r
    f = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
    rt = (f[1], -f[0])
    rel = (dx - px, dy - py)
    fo = rel[0] * f[0] + rel[1] * f[1]
    ro = rel[0] * rt[0] + rel[1] * rt[1]
    d0, h = (40.0, 46.0) if duck else (72.5, 70.0)
    n = math.hypot(1, 0.6)
    wf, wr = -0.6 / n * d0, 1 / n * d0
    print(f"{t:5.2f} {math.hypot(vx, vy):6.1f} {int(duck)} {fo:8.1f} {ro:9.1f} {dz - pz:7.1f} | {wf:6.1f} {wr:6.1f} {h:5.1f}  {wf - fo:7.1f}  {ap:5.1f} {ar:5.1f} {((ay - yaw + 180) % 360) - 180:6.1f}")
