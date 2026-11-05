#!/usr/bin/env python3
"""D: rate, damage, drop, flinch, table end, P2020 fraction, bullet against punch, jolt, view model position.
  py -3 -I an_d.py <s3 session> <s4 session> <runs dir> <out prefix>
Rate, jolt and view model come from the fr_ runs in s3, the rest from s4. Prints the small tables, writes the long ones."""
import math, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut

RD = re.compile(r"\[RT\] dmg t=([\d.]+) amt=([\d.]+) hg=(\d+) src=\d+ dist=([\d.]+) type=\d+ pos=([-\d.]+),([-\d.]+),([-\d.]+)")
RC = re.compile(r"\[RT\] clip t=\S+ c=\S+ ammo=\S+ reload=\S+ adsf=\S+ active=\S+ ea=([-\d.]+),([-\d.]+) eo=([-\d.]+),([-\d.]+),([-\d.]+)")
RG = re.compile(r"\] g t=([\d.]+) .* m=([-\d.]+),([-\d.]+),([-\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+)")


def txt(runs, t):
    p = os.path.join(runs, t + ".txt")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def vars_tab(path):
    L = open(path, encoding="utf-8").read().splitlines()
    k = L[0].split("\t")
    return {l.split("\t")[0]: dict(zip(k, l.split("\t"))) for l in L[1:]}


def write(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in keys) + "\n")


def rate(F, S, M, V, pre):
    rows, ramp = [], []
    for g, v in V.items():
        r = dict(gun=g, field=float(v["fire_rate"]), burst=v["burst_fire_count"], burst_delay=v["burst_fire_delay"], rechamber=v["rechamber_time"], clip=v["ammo_clip_size"])
        for mode in ("hold", "taps", "adshold"):
            t = f"fr_{g}_{mode}"
            if t not in M: continue
            a, b = M[t][0][0], M[t][-1][0] + 0.2
            sh = cut(S, a, b)
            iv = [y["ct"] - x["ct"] for x, y in zip(sh, sh[1:])]
            r[mode + "_n"] = len(sh)
            if iv:
                m = st.median(iv)
                r[mode + "_iv"] = m; r[mode + "_rate"] = 1 / m if m else ""
                r[mode + "_first"] = iv[0]; r[mode + "_last"] = iv[-1]
                if mode == "hold": ramp.append(dict(gun=g, ivs=",".join(f"{x:.3f}" for x in iv)[:400]))
        rows.append(r)
    keys = ["gun", "field", "burst", "burst_delay", "rechamber", "clip"] + [m + s for m in ("hold", "taps", "adshold") for s in ("_n", "_iv", "_rate", "_first", "_last")]
    write(pre + "-RATE.tsv", rows, keys)
    write(pre + "-RATE-INTERVALS.tsv", ramp, ["gun", "ivs"])


def damage(M, runs, V, pre):
    out = []
    for t in M:
        g = re.match(r"(df|dg|sd)_(\w+?)(?:_(\d+|head|leg))?$", t)
        if not g: continue
        by = defaultdict(list)
        for x in RD.findall(txt(runs, t)): by[int(x[2])].append((float(x[1]), float(x[3])))
        v = V.get(g[2], {})
        hits = ";".join(f"hg{k}:{st.mean(a for a, _ in w):.1f}x{len(w)}@{st.mean(d for _, d in w):.0f}" for k, w in sorted(by.items()))
        out.append(dict(tag=t, gun=g[2], near=v.get("damage_near_value", ""), far=v.get("damage_far_value", ""), near_d=v.get("damage_near_distance", ""), far_d=v.get("damage_far_distance", ""), head=v.get("damage_headshot_scale", ""), leg=v.get("damage_leg_scale", ""), hits=hits))
    write(pre + "-DAMAGE.tsv", out, ["tag", "gun", "near", "far", "near_d", "far_d", "head", "leg", "hits"])


def drop(M, runs, V, pre):
    rows, P = [], defaultdict(list)
    for t in M:
        g = re.match(r"dp_(\w+?)_(\d+)$", t)
        if not g: continue
        T = txt(runs, t)
        c = RC.search(T)
        if not c: continue
        pitch = float(c[1]); pitch = pitch - 360 if pitch > 180 else pitch
        ex, ey, ez = float(c[3]), float(c[4]), float(c[5])
        H = [(float(x[4]), float(x[5]), float(x[6])) for x in RD.findall(T)]
        dr = []
        for hx, hy, hz in H:
            x = hx - ex
            dr.append((x, x * math.tan(math.radians(-pitch)) - (hz - ez), hy - ey))
        v = V[g[1]]
        vel, gs = float(v["projectile_launch_speed"]), float(v["projectile_gravity_scale"])
        d = int(g[2])
        r = dict(gun=g[1], dist=d, v=vel, grav=gs, drag=v["projectile_drag_coefficient"], lift_deg=-pitch, shots=6, hits=len(dr), pred=0.5 * 750 * gs * (d / vel) ** 2)
        if dr:
            r["drop_med"] = st.median(x[1] for x in dr); r["drop_sd"] = st.pstdev(x[1] for x in dr); r["y_med"] = st.median(x[2] for x in dr); r["x_med"] = st.median(x[0] for x in dr)
            P[g[1]].extend(dr)
        rows.append(r)
    write(pre + "-DROP.tsv", rows, ["gun", "dist", "v", "grav", "drag", "lift_deg", "shots", "hits", "pred", "drop_med", "drop_sd", "y_med", "x_med"])
    for g, d in P.items():
        v = V[g]; a0 = 0.5 * 750 * float(v["projectile_gravity_scale"]) / float(v["projectile_launch_speed"]) ** 2
        n = len(d); sx = sum(x[0] ** 2 for x in d); sy = sum(x[1] for x in d); sxx = sum(x[0] ** 4 for x in d); sxy = sum(x[0] ** 2 * x[1] for x in d)
        den = n * sxx - sx * sx
        if den:
            a = (n * sxy - sx * sy) / den; b = (sy - a * sx) / n
            print(f"drop fit {g}: n={n} a/formula={a / a0:.3f} origin={b:.2f}u")


def flinch(F, M):
    rows = []
    for t in M:
        if not t.startswith("fl_"): continue
        td = [x for x, m in M[t] if m == "sv td"]
        for i, c in enumerate(td):
            fr = cut(F, c - 0.2, c + 1.2)
            base = [r for r in fr if r["t"] < c]
            aft = [r for r in fr if r["t"] >= c]
            if not base or not aft: continue
            b = {k: st.mean(r[k] for r in base) for k in ("fP", "fY", "fR", "puP", "puY", "puR", "s2P", "s2Y", "s2R", "fov", "vmF", "vmR", "vmU")}
            row = dict(tag=t, amount=15 if i == 0 else 60, base_jitter=max(abs(r["fP"] - b["fP"]) for r in base))
            for k in b:
                p = max(aft, key=lambda r: abs(r[k] - b[k]))
                row[k] = p[k] - b[k]; row["t_" + k] = p["t"] - c
            rows.append(row)
    return rows


def table_end(S, M, pre):
    out = []
    for t in M:
        if not t.startswith("lp"): continue
        a, b = M[t][0][0], M[t][-1][0] + 0.2
        for i, s in enumerate(cut(S, a, b)):
            out.append(dict(tag=t, n=i + 1, idx=int(s["idx"]), row=int(s["row"]), val=s["val"], c0=s["c0"], c1=s["c1"], hard=s["hard"], soft=s["soft"]))
    write(pre + "-TABLE-END.tsv", out, ["tag", "n", "idx", "row", "val", "c0", "c1", "hard", "soft"])


def fraction(F, S, M):
    """Slope of the view pitch offset against the punch over the settle after one shot."""
    res = []
    for t in M:
        if not t.startswith("fx_"): continue
        a, b = M[t][0][0], M[t][-1][0]
        sh = cut(S, a, b)
        if not sh: continue
        fr = [r for r in cut(F, sh[0]["t"], sh[0]["t"] + 0.6) if r["zf"] >= 0.999]
        if len(fr) < 10: continue
        mx, my = st.mean(r["s2P"] for r in fr), st.mean(r["puP"] for r in fr)
        sxx = sum((r["s2P"] - mx) ** 2 for r in fr); sxy = sum((r["s2P"] - mx) * (r["puP"] - my) for r in fr)
        res.append((sxy / sxx if sxx else float("nan"), max(abs(r["s2P"]) for r in fr)))
    return res


def bullet_vs_punch(S, M, runs):
    """Runs where every shot hit: the bullet's rise against the client punch before that shot."""
    out = defaultdict(list)
    for t in M:
        g = re.match(r"df_(\w+?)_(300|800)$", t)
        if not g or g[1] in ("eva8", "mastiff"): continue
        T = txt(runs, t); c = RC.search(T)
        a, b = M[t][0][0], M[t][-1][0] + 0.2
        sh = cut(S, a, b); H = RD.findall(T)
        if not c or len(H) != len(sh) or not sh: continue
        pitch = float(c[1]); pitch = pitch - 360 if pitch > 180 else pitch
        ex, ez = float(c[3]), float(c[5])
        for i, (s, h) in enumerate(zip(sh, H)):
            x = float(h[4]) - ex
            out[g[1]].append((i + 1, math.degrees(math.atan2(float(h[6]) - ez, x)) + pitch, -s["s2P0"]))
    return out


def jolt(F, S, M, V, runs, pre):
    rows, vm = [], []
    for g in V:
        for mode, tag in (("hip", f"fr_{g}_hold"), ("ads", f"fr_{g}_adshold")):
            if tag not in M: continue
            a, b = M[tag][0][0], M[tag][-1][0] + 0.2
            fr, sh = cut(F, a, b), cut(S, a, b)
            if not sh: continue
            t0 = sh[0]["t"]; t1 = sh[1]["t"] if len(sh) > 1 else t0 + 0.4
            before = [r for r in fr if t0 - 0.15 <= r["t"] < t0]; aft = [r for r in fr if t0 <= r["t"] < min(t1, t0 + 0.4)]
            if not before or not aft: continue
            row = dict(gun=g, mode=mode, window=min(t1, t0 + 0.4) - t0, roll_first=sh[0]["s2R1"], rolls=",".join(f"{x['s2R1']:.2f}" for x in sh[:6]))
            for k in ("vmF", "vmR", "vmU", "vmaP", "vmaY", "vmaR"):
                bm = st.mean(r[k] for r in before); p = max(aft, key=lambda r: abs(r[k] - bm))
                row[k] = p[k] - bm; row["t_" + k] = p["t"] - t0
            rows.append(row)
            # the 0.3 s before the first shot: earlier frames are still in the deploy animation
            c0 = sh[0]["ct"]
            w = [(float(x[1]) - float(x[4]), -(float(x[2]) - float(x[5])), float(x[3]) - float(x[6])) for x in RG.findall(txt(runs, tag)) if c0 - 0.3 <= float(x[0]) < c0]
            if w:
                vm.append(dict(gun=g, mode=mode, muzzleF=st.mean(x[0] for x in w), muzzleR=st.mean(x[1] for x in w), muzzleU=st.mean(x[2] for x in w), vmF=st.mean(r["vmF"] for r in before), vmR=st.mean(r["vmR"] for r in before), vmU=st.mean(r["vmU"] for r in before), fov=st.mean(r["fov"] for r in before)))
    write(pre + "-JOLT.tsv", rows, ["gun", "mode", "window", "vmF", "t_vmF", "vmR", "t_vmR", "vmU", "t_vmU", "vmaP", "t_vmaP", "vmaY", "vmaR", "roll_first", "rolls"])
    write(pre + "-VIEWMODEL.tsv", vm, ["gun", "mode", "muzzleF", "muzzleR", "muzzleU", "vmF", "vmR", "vmU", "fov"])


def main():
    s3, s4, runs, pre = sys.argv[1:5]
    V = vars_tab(os.path.join(os.path.dirname(pre), "GUN-VARS.tsv"))
    F3, S3, M3 = load(s3)
    rate(F3, S3, M3, V, pre); jolt(F3, S3, M3, V, runs, pre)
    F4, S4, M4 = load(s4)
    damage(M4, runs, V, pre); drop(M4, runs, V, pre); table_end(S4, M4, pre)
    ks = ["tag", "amount", "base_jitter"] + [x for k in ("fP", "fY", "fR", "puP", "s2P", "s2Y", "s2R", "fov", "vmF", "vmU") for x in (k, "t_" + k)]
    write(pre + "-FLINCH.tsv", flinch(F4, M4), ks)
    print("P2020 ADS slope (puP on s2P) / peak:", [f"{a:.3f}/{b:.2f}" for a, b in fraction(F4, S4, M4)])
    for g, v in bullet_vs_punch(S4, M4, runs).items():
        by = defaultdict(list)
        for i, b, p in v: by[i].append((b, p))
        print("bullet/punch", g, " ".join(f"#{i}:{st.mean(x[0] for x in w):.2f}/{st.mean(x[1] for x in w):.2f}" for i, w in sorted(by.items())))


if __name__ == "__main__":
    main()
