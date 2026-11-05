#!/usr/bin/env python3
"""B: per state and aim. Fire runs (st_, s2_): kick scale against the same gun standing, spread, speed, air, zoom, latency. Still runs (sw_): view model sway, view drift, aim movement.
  py -3 -I an_states.py <session dir> <runs dir> <fire.tsv> <still.tsv>"""
import math, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut

RG = re.compile(r"\] g t=([\d.]+) zf=(\S+) fov=\S+ sp=(\S+) clip=(-?\d+) rel=(\d) spd=(\S+) vz=(\S+) gr=(\d) duck=(\d) spr=(\d) wr=(\d)")


def glines(runs, tag):
    p = os.path.join(runs, tag + ".txt")
    if not os.path.exists(p): return []
    out = []
    for l in open(p, encoding="utf-8"):
        g = RG.search(l)
        if g: v = g.groups(); out.append(dict(t=float(v[0]), zf=float(v[1]), sp=float(v[2]), clip=int(v[3]), rel=int(v[4]), spd=float(v[5]), vz=float(v[6]), gr=int(v[7]), duck=int(v[8]), spr=int(v[9]), wr=int(v[10])))
    return out


def fire_row(tag, F, S, M, runs):
    a, b = M[tag][0][0], M[tag][-1][0] + 0.2
    fr, sh = cut(F, a, b), cut(S, a, b)
    atk = [t for t, m in M[tag] if m == "+attack"]
    row = dict(tag=tag, kicks=len(sh))
    G = glines(runs, tag)
    if sh:
        # raw: per kick pitch step over hard, so scale * (row + random); keep the row or base to divide later
        dx = [(x["s2P1"] - x["s2P0"]) / x["hard"] for x in sh if x["hard"]]
        cs = [x["c1"] for x in sh]
        row["sumdx"] = sum(dx); row["sumc"] = sum(c for c in cs if c == c) if any(c == c for c in cs) else float("nan"); row["n"] = len(dx)
        row["first_dx"] = dx[0] if dx else float("nan")
        row["zf_first"] = sh[0]["zf"]
        row["spd_first"] = math.hypot(sh[0]["vx"], sh[0]["vy"]); row["vz_first"] = sh[0]["vz"]
        row["spd_mean"] = st.mean(math.hypot(x["vx"], x["vy"]) for x in sh)
        if atk: row["latency"] = sh[0]["t"] - atk[0]
        tk = [x["ct"] for x in sh]
        sp = [g["sp"] for g in G if tk[0] - 0.02 <= g["t"] <= tk[-1] + 0.02]
        # the client log uses Time(): only near ct, so also take spread in the fire window from the marks' order
        if sp: row["sp_min"] = min(sp); row["sp_max"] = max(sp)
    if G:
        row["gr_any0"] = int(any(g["gr"] == 0 for g in G)); row["duck_any"] = int(any(g["duck"] for g in G)); row["spr_any"] = int(any(g["spr"] for g in G)); row["wr_any"] = int(any(g["wr"] for g in G))
        row["zf_max"] = max(g["zf"] for g in G); row["spdmax"] = max(g["spd"] for g in G)
    return row


def still_row(tag, F, M, runs):
    a, b = M[tag][0][0], M[tag][-1][0]
    fr = cut(F, a, b)
    G = glines(runs, tag)
    row = dict(tag=tag)
    if not fr: return row
    t0 = fr[0]["t"]
    # window: the wait 1.2 before the release: from 35 % to 80 % of the run
    w = [r for r in fr if t0 + (b - a) * 0.35 <= r["t"] <= t0 + (b - a) * 0.8]
    if not w: return row
    rg = lambda k: max(r[k] for r in w) - min(r[k] for r in w)
    row.update(zf=st.mean(r["zf"] for r in w), vmF=rg("vmF"), vmR=rg("vmR"), vmU=rg("vmU"), vmaP=rg("vmaP"), vmaY=rg("vmaY"), vmaR=rg("vmaR"), driftP=rg("puP"), driftY=rg("puY"), roll=rg("fR"),
               spd=st.mean(math.hypot(r["vx"], r["vy"]) for r in w), fov=st.mean(r["fov"] for r in w), meanF=st.mean(r["vmF"] for r in w), meanR=st.mean(r["vmR"] for r in w), meanU=st.mean(r["vmU"] for r in w))
    sp = [g["sp"] for g in G]
    if sp: row["sp_med"] = st.median(sp)
    return row


def main():
    d, runs, f1, f2 = sys.argv[1:5]
    F, S, M = load(d)
    fk = ["tag", "kicks", "n", "sumdx", "sumc", "first_dx", "zf_first", "spd_first", "vz_first", "spd_mean", "latency", "sp_min", "sp_max", "gr_any0", "duck_any", "spr_any", "wr_any", "zf_max", "spdmax", "scale_vs_stand"]
    rows = {t: fire_row(t, F, S, M, runs) for t in M if t.startswith(("st_", "s2_"))}
    for t, r in rows.items():
        g = re.match(r"(st|s2)_(\w+?)_(\w+)_(hip|ads)$", t)
        base = rows.get(f"st_{g[2]}_stand_{g[4]}") if g else None
        if base and r.get("kicks") and base.get("kicks"):
            n = min(r["kicks"], base["kicks"])
            # compare mean per kick / mean table of the same rows; semi guns have no table so use mean dx
            sc = r["sumdx"] / r["sumc"] if r.get("sumc") == r.get("sumc") and r.get("sumc") else r["sumdx"] / r["n"]
            sb = base["sumdx"] / base["sumc"] if base.get("sumc") == base.get("sumc") and base.get("sumc") else base["sumdx"] / base["n"]
            r["scale_vs_stand"] = sc / sb if sb else float("nan")
    with open(f1, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(fk) + "\n")
        for r in rows.values():
            f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in fk) + "\n")
    sk = ["tag", "zf", "spd", "fov", "sp_med", "vmF", "vmR", "vmU", "vmaP", "vmaY", "vmaR", "driftP", "driftY", "roll", "meanF", "meanR", "meanU"]
    with open(f2, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(sk) + "\n")
        for t in M:
            if re.match(r"sw_(r301|wingman)_\w+_(hip|ads)$", t):
                r = still_row(t, F, M, runs)
                f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in sk) + "\n")


if __name__ == "__main__":
    main()
