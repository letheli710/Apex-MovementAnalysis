"""F20: feet and pelvis on slopes (run gait_f20, mp_homestead; flat reference: gait_a on mp_lf_stacks).

Per segment, over the steady part (re-posed frames only):
  slope      from the origin's climb: atan(dz / horizontal distance)
  ground     floor height under each sole and under the origin, bilinear on the 32 u prop-aware map
             (hsd_gait_hmap ... above 250, logged in the same run)
  origin     origin z - ground under the origin (the hull's feet point; on a slope the hull rests on its
             lower edge, so this is > 0 by about hull half-width x tan(slope))
  pelvis     exp_torso_base z - origin z (mean, range): the body's height over the origin
  sole gap   during stance (sole world-stationary), sole z - ground under the sole; uphill / downhill foot
  sole pitch during stance, the sole attachment's pitch, against the slope angle
Usage: py -3 -I an_f20.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, run_dir, speed2d, tag_windows  # noqa: E402
from an_f6 import plants, steady  # noqa: E402


ORIGIN = [0.0, 0.0]  # lattice origin of the map (x0 of the rows, first y)


def read_map(name):
    H, st = {}, None
    for line in (run_dir(name) / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) > 5 and p[1] == "GH" and p[2] != "done":
            y, x0, st = float(p[2]), float(p[3]), float(p[4])
            if not H:
                ORIGIN[0], ORIGIN[1] = x0, y
            for k, v in enumerate(p[5:]):
                if v != "-":
                    z, nz = v.split(":")
                    H[(x0 + k * st, y)] = (float(z), int(nz) / 1000.0)
    return H, st


def ground(H, st, x, y):
    x0 = ORIGIN[0] + math.floor((x - ORIGIN[0]) / st) * st
    y0 = ORIGIN[1] + math.floor((y - ORIGIN[1]) / st) * st
    # the map rows start at y0 values of the command; snap to the stored lattice
    keys = [(x0, y0), (x0 + st, y0), (x0, y0 + st), (x0 + st, y0 + st)]
    if not all(k in H for k in keys):
        return None
    fx, fy = (x - x0) / st, (y - y0) / st
    z = [H[k][0] for k in keys]
    return (z[0] * (1 - fx) + z[1] * fx) * (1 - fy) + (z[2] * (1 - fx) + z[3] * fx) * fy


FLAT_Z = 1.0  # mp_lf_stacks lane floor (hsd_gait_hmap, run gait_b)


def stats(xs):
    if not xs:
        return (float("nan"),) * 3
    return (sum(xs) / len(xs), min(xs), max(xs))


def segment(run, name, t0, t1, H, st):
    C = between(run["C"], t0, t1)
    s = steady(C, tol=0.03)
    if len(s) < 60:
        return None
    a, b = s[0]["t"] + 0.6, s[-1]["t"]
    G = anim_updates(between(run["GC"], a, b))
    if len(G) < 10:
        return None
    o0, o1 = G[0]["o"], G[-1]["o"]
    hd = math.hypot(o1[0] - o0[0], o1[1] - o0[1])
    slope = math.degrees(math.atan2(o1[2] - o0[2], hd)) if hd > 1 else 0.0
    yaw = s[0]["yaw"]
    pel = [g["torso"][2] - g["o"][2] for g in G]
    head = [g["head"][2] - g["o"][2] for g in G]
    gfun = (lambda x, y: ground(H, st, x, y)) if H else (lambda x, y: FLAT_Z)
    org = [g["o"][2] - gz for g in G for gz in [gfun(g["o"][0], g["o"][1])] if gz is not None]
    out = dict(name=name, v=sum(speed2d(c["v"]) for c in s) / len(s), slope=slope, dur=b - a,
               pel=stats(pel), head=stats(head), org=stats(org))
    for foot, ang in (("footL", "lang"), ("footR", "rang")):
        gaps, pitch = [], []
        vb = out["v"]
        on = plants(G, foot, vmax=max(25.0, 0.3 * vb))
        slide = []
        for s0, s1 in on:
            mid = [g for g in G if s0 + 0.03 <= g["t"] <= s1 - 0.03]
            for g0, g1 in zip(mid, mid[1:]):
                dt = g1["t"] - g0["t"]
                if dt > 0.02:
                    slide.append(math.hypot(g1[foot][0] - g0[foot][0], g1[foot][1] - g0[foot][1]) / dt)
        out[foot + "_slide"] = stats(slide)
        for s0, s1 in on:
            mid = [g for g in G if s0 + 0.03 <= g["t"] <= s1 - 0.03]
            for g in mid:
                gz = gfun(g[foot][0], g[foot][1])
                if gz is not None:
                    gaps.append(g[foot][2] - gz)
                if g.get(ang):
                    pitch.append(g[ang][0])
        # gap against the foot's offset along the motion: no IK -> gap = -tan(slope) * fwd (+ flat gap)
        cyw, syw = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        pts = []
        for s0, s1 in on:
            for g in G:
                if s0 + 0.03 <= g["t"] <= s1 - 0.03:
                    gz = gfun(g[foot][0], g[foot][1])
                    if gz is not None:
                        fwd = (g[foot][0] - g["o"][0]) * cyw + (g[foot][1] - g["o"][1]) * syw
                        pts.append((fwd, g[foot][2] - gz))
        k = None
        if len(pts) > 5:
            mx, my = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
            vx = sum((p[0] - mx) ** 2 for p in pts)
            if vx > 1:
                k = sum((p[0] - mx) * (p[1] - my) for p in pts) / vx
        out[foot] = dict(gap=stats(gaps), pitch=stats(pitch), n=len(gaps), k=k)
        # lateral offset of the foot (left of the motion is +): which side is uphill does not matter on a
        # straight up/down line, both feet see the same slope
    return out


def main():
    rows = []
    fl = load("gait_c")
    for name, t0, t1 in tag_windows(fl):
        if name in ("be_160", "f6_075"):
            r = segment(fl, "flat(stacks) " + name, t0, t1, {}, None)
            if r:
                rows.append(r)
    name_ = sys.argv[1] if len(sys.argv) > 1 else "gait_f20b"
    run = load(name_)
    H, st = read_map("gait_f20")   # the prop-aware map of the first run (same map, same command)
    print("map points", len(H), "step", st)
    for name, t0, t1 in tag_windows(run):
        if name.startswith("stop") or name.startswith("spawn"):
            continue
        r = segment(run, name, t0, t1, H, st)
        if r:
            rows.append(r)
    for r in rows:
        print("%-20s v %5.1f slope %+5.1f deg over %.1f s | pelvis-origin %.1f (%.1f..%.1f) head-origin %.1f | origin-ground %s" % (
            r["name"], r["v"], r["slope"], r["dur"], r["pel"][0], r["pel"][1], r["pel"][2], r["head"][0],
            "-" if math.isnan(r["org"][0]) else "%.1f (%.1f..%.1f)" % r["org"]))
        for foot in ("footL", "footR"):
            f = r[foot]
            print("%22s %s stance: sole-ground %s  sole pitch %.1f (%.1f..%.1f)  n %d  slide %.1f u/s  d(gap)/d(fwd) %s (no IK: %.3f)" % (
                "", foot, "-" if math.isnan(f["gap"][0]) else "%.1f (%.1f..%.1f)" % f["gap"], f["pitch"][0], f["pitch"][1], f["pitch"][2], f["n"], r[foot + "_slide"][0],
                "-" if f["k"] is None else "%.3f" % f["k"], -math.tan(math.radians(r["slope"]))))
    return rows


if __name__ == "__main__":
    main()
