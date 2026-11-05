#!/usr/bin/env python3
"""Curves the C and B reports did not write out, read from the client's per-frame lines in runs/: spread over time, the muzzle through a swap, a reload's muzzle speed, the speed of the aiming curve.
  py -3 -I an_report.py <gun-measure dir> <out dir>
Writes R-SPREAD-FIRE.tsv, R-SPREAD-MOVE.tsv, R-SWAP-CURVE.tsv, R-SWAP-SUMMARY.tsv, R-RELOAD-SPEED.tsv, R-ADS-SPEED.tsv."""
import csv, glob, math, os, re, statistics as st, sys

RG = re.compile(r"\] g t=([\d.]+) zf=(\S+) fov=(\S+) sp=(\S+) clip=(-?\d+) rel=(\d) spd=(\S+) vz=(\S+) gr=(\d) duck=(\d) spr=(\d) wr=(\d) m=([-\d.]+),([-\d.]+),([-\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+) w=(\S+)")


def frames(path):
    out = []
    for l in open(path, encoding="utf-8", errors="replace"):
        g = RG.search(l)
        if not g: continue
        v = g.groups()
        out.append(dict(t=float(v[0]), zf=float(v[1]), sp=float(v[3]), clip=int(v[4]), spd=float(v[6]), gr=int(v[8]), m=(float(v[12]) - float(v[15]), float(v[13]) - float(v[16]), float(v[14]) - float(v[17])), w=v[18]))
    # a run ends with a reset that refills and teleports: keep the frames before it as they come; callers cut by shots
    return out


def write(path, rows, keys):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(keys)
        for r in rows: w.writerow([("" if r.get(k) is None else (f"{r[k]:.3f}" if isinstance(r[k], float) else r[k])) for k in keys])


def spread_fire(runs):
    """Hip fire: the baseline, the step per shot, the top, then how it falls."""
    rows = []
    for p in sorted(glob.glob(os.path.join(runs, "st_*_hip.txt"))):
        name = os.path.basename(p)[3:-8]
        gun, _, state = name.partition("_")
        fr = frames(p)
        # a run opens by giving the gun: the clip of the gun before it is not a shot
        changed = [r["t"] for a, r in zip(fr, fr[1:]) if a["w"] != r["w"]]
        drops = [i for i in range(1, len(fr)) if fr[i]["clip"] < fr[i - 1]["clip"] and fr[i]["clip"] >= 0 and not any(0 <= fr[i]["t"] - t < 1 for t in changed)]
        if len(drops) < 1: continue
        first, last = drops[0], drops[-1]
        base = fr[first - 1]["sp"]
        steps = [fr[min(j + 2, len(fr) - 1)]["sp"] - fr[max(j - 1, 0)]["sp"] for j in drops[:6]]
        top = max(r["sp"] for r in fr[first:min(last + 40, len(fr))])
        tail = fr[last:]
        peak_i = max(range(len(tail)), key=lambda i: tail[i]["sp"] if tail[i]["t"] - tail[0]["t"] < 0.3 else -1)
        fall_at = next((tail[i]["t"] - tail[0]["t"] for i in range(peak_i, len(tail)) if tail[i]["sp"] < tail[peak_i]["sp"] - 0.03), None)
        settled = next((tail[i]["t"] - tail[0]["t"] for i in range(peak_i, len(tail)) if fall_at and tail[i]["sp"] <= base + 0.05 and tail[i]["t"] - tail[0]["t"] >= fall_at), None)
        slope = None
        if fall_at is not None:
            pts = [r for r in tail if fall_at <= r["t"] - tail[0]["t"] <= fall_at + 0.06]
            if len(pts) > 2 and pts[-1]["t"] > pts[0]["t"]: slope = (pts[0]["sp"] - pts[-1]["sp"]) / (pts[-1]["t"] - pts[0]["t"])
        rows.append(dict(gun=gun, state=state, shots=len(drops), base=base, step=st.median(steps) if steps else None, top=top, fall_starts=fall_at, fall_rate=slope, back_at=settled))
    return rows


def spread_move(runs):
    """No fire: how the spread goes up and down as the body starts and stops."""
    rows = []
    for p in sorted(glob.glob(os.path.join(runs, "sw_*_hip.txt"))):
        name = os.path.basename(p)[3:-8]
        gun, _, state = name.partition("_")
        fr = [r for r in frames(p) if r["zf"] == 0]
        if len(fr) < 30: continue
        sp = [r["sp"] for r in fr]
        ups, downs = [], []
        for a, b in zip(fr, fr[5:]):
            dt = b["t"] - a["t"]
            if dt <= 0 or dt > 0.2: continue
            rate = (b["sp"] - a["sp"]) / dt
            if rate > 0.5: ups.append(rate)
            if rate < -0.5: downs.append(-rate)
        rows.append(dict(gun=gun, state=state, low=min(sp), high=max(sp), up_rate=st.median(ups) if ups else None, down_rate=st.median(downs) if downs else None, speed_max=max(r["spd"] for r in fr)))
    return rows


def norm(d): return math.sqrt(sum(x * x for x in d))


def swap_curves(runs, gm):
    """The muzzle against the camera through a holster and a plain draw, in the swap runs. Windows are the measured lengths (holster_time, deploy_time): a draw of a gun seen before, so from the third swap on."""
    gv = {}
    from guns import GUNS
    rows = list(csv.DictReader(open(os.path.join(gm, "GUN-VARS.tsv"), encoding="utf-8"), delimiter="\t"))
    for r in rows:
        if r["gun"] in GUNS: gv["mp_weapon_" + GUNS[r["gun"]]] = r
    summary, curves = [], []
    for p in sorted(glob.glob(os.path.join(runs, "ws_*_swap.txt"))):
        fr = frames(p)
        changes = [i for i in range(1, len(fr)) if fr[i]["w"] != fr[i - 1]["w"]]
        for n, c in enumerate(changes):
            if n < 2: continue
            old, new = fr[c - 1]["w"], fr[c]["w"]
            if old not in gv or new not in gv: continue
            tc, H, D = fr[c]["t"], float(gv[old]["holster_time"]), float(gv[new]["deploy_time"])
            hol = [r for r in fr[:c] if r["t"] >= tc - H]
            dep = [r for r in fr[c:] if r["t"] <= tc + D and r["w"] == new]
            calm_old = [r for r in fr[:c] if tc - H - 0.08 <= r["t"] < tc - H]
            calm_new = [r for r in fr[c:] if tc + D + 0.1 <= r["t"] <= tc + D + 0.25 and r["w"] == new]
            if len(hol) < 5 or len(dep) < 5 or not calm_old or not calm_new: continue
            rest_old, rest_new = calm_old[0]["m"], calm_new[-1]["m"]
            def dist(r, rest): return norm([a - b for a, b in zip(r["m"], rest)])
            def describe(rs, rest, t0, length, phase, gun):
                d = [dist(r, rest) for r in rs]
                peak = max(d)
                speeds = []
                for x, y in zip(rs, rs[6:]):
                    dt = y["t"] - x["t"]
                    if dt > 0: speeds.append((norm([a - b for a, b in zip(y["m"], x["m"])]) / dt, (x["t"] + y["t"]) / 2))
                top, at = max(speeds)
                shares = []
                for k in range(0, 11):
                    t = t0 + length * k / 10
                    r = min(rs, key=lambda q: abs(q["t"] - t))
                    shares.append(dist(r, rest) / peak if peak else 0)
                    curves.append(dict(gun=gun, phase=phase, frac=k / 10, f=r["m"][0] - rest[0], r=-(r["m"][1] - rest[1]), u=r["m"][2] - rest[2], dist=dist(r, rest)))
                return peak, top, (at - t0) / length
            hp, hv, hat = describe(hol, rest_old, tc - H, H, "holster", old.replace("mp_weapon_", ""))
            dp, dv, dat = describe(dep, rest_new, tc, D, "draw", new.replace("mp_weapon_", ""))
            summary.append(dict(gun_from=old.replace("mp_weapon_", ""), gun_to=new.replace("mp_weapon_", ""), holster=H, holster_reach=hp, holster_peak_speed=hv, holster_peak_at=hat, deploy=D, draw_reach=dp, draw_peak_speed=dv, draw_peak_at=dat))
    return summary, curves


def reload_speed(gm):
    """Peak muzzle distance and speed in a reload, from C-RELOAD-CURVE (5 % steps) and the time to the unlock."""
    unlock = {(r["gun"], r["kind"]): float(r["flag"]) for r in csv.DictReader(open(os.path.join(gm, "C-RELOAD-SUMMARY.tsv"), encoding="utf-8"), delimiter="\t") if r["flag"]}
    pts = {}
    for l in open(os.path.join(gm, "C-RELOAD-CURVE.tsv"), encoding="utf-8"):
        if l.startswith("#") or l.startswith("gun"): continue
        g, k, fr, a, b, c, _ = l.rstrip("\n").split("\t")
        pts.setdefault((g, k), []).append((float(fr), float(a), float(b), float(c)))
    rows = []
    for key, p in sorted(pts.items()):
        if key not in unlock: continue
        T = unlock[key]
        p.sort()
        d = [norm(x[1:]) for x in p]
        i = max(range(len(d)), key=d.__getitem__)
        sp = [norm([p[j + 1][q] - p[j][q] for q in (1, 2, 3)]) / max(1e-6, (p[j + 1][0] - p[j][0]) * T) for j in range(len(p) - 1)]
        rows.append(dict(gun=key[0], kind=key[1], unlock=T, reach=d[i], reach_at=p[i][0] * T, peak_speed=max(sp), mean_speed=sum(sp) / len(sp)))
    return rows


def ads_speed(combat):
    """The aiming curve per gun in u/s and u/s², from the measured table and the zoom times."""
    T = {("r301", "in"): 0.27, ("r301", "out"): 0.23, ("wing", "in"): 0.18, ("wing", "out"): 0.16, ("spit", "in"): 0.34, ("spit", "out"): 0.30}
    rows_by = {}
    for r in csv.DictReader((l for l in open(os.path.join(combat, "recoil-view", "ADS-CURVES.tsv"), encoding="utf-8") if not l.startswith("#")), delimiter="\t"):
        rows_by.setdefault((r["weapon"], r["phase"]), []).append(r)
    out = []
    for (w, ph), rs in sorted(rows_by.items()):
        key = (w, ph)
        if key not in T: continue
        t = T[key]
        rs.sort(key=lambda r: float(r["zf"]))
        pos = [(float(r["zf"]), float(r["dF"]), float(r["dR"]), float(r["dU"])) for r in rs]
        v = [norm([b[q] - a[q] for q in (1, 2, 3)]) / ((b[0] - a[0]) * t) for a, b in zip(pos, pos[1:]) if b[0] > a[0]]
        acc = [abs(b - a) / (0.05 * t) for a, b in zip(v, v[1:])]
        z_at = pos[max(range(len(v)), key=v.__getitem__)][0]
        out.append(dict(gun=w, phase=key[1], zoom_time=t, peak_speed=max(v), peak_at_zf=z_at, peak_accel=max(acc) if acc else None))
    return out


def main():
    gm, out = os.path.abspath(sys.argv[1]), sys.argv[2]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    runs = os.path.join(gm, "runs")
    os.makedirs(out, exist_ok=True)
    write(os.path.join(out, "R-SPREAD-FIRE.tsv"), spread_fire(runs), ["gun", "state", "shots", "base", "step", "top", "fall_starts", "fall_rate", "back_at"])
    write(os.path.join(out, "R-SPREAD-MOVE.tsv"), spread_move(runs), ["gun", "state", "low", "high", "up_rate", "down_rate", "speed_max"])
    s, c = swap_curves(runs, gm)
    write(os.path.join(out, "R-SWAP-SUMMARY.tsv"), s, ["gun_from", "gun_to", "holster", "holster_reach", "holster_peak_speed", "holster_peak_at", "deploy", "draw_reach", "draw_peak_speed", "draw_peak_at"])
    write(os.path.join(out, "R-SWAP-CURVE.tsv"), c, ["gun", "phase", "frac", "f", "r", "u", "dist"])
    write(os.path.join(out, "R-RELOAD-SPEED.tsv"), reload_speed(gm), ["gun", "kind", "unlock", "reach", "reach_at", "peak_speed", "mean_speed"])
    write(os.path.join(out, "R-ADS-SPEED.tsv"), ads_speed(os.path.dirname(gm.rstrip("/\\"))), ["gun", "phase", "zoom_time", "peak_speed", "peak_at_zf", "peak_accel"])


if __name__ == "__main__":
    main()
