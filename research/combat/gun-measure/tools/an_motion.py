#!/usr/bin/env python3
"""C: reload, switching, melee, raise. Times come from frames.csv (client ct); client lines give the muzzle against the camera.
  py -3 -I an_motion.py <session dir> <runs dir> <out prefix>
Writes <prefix>-RELOAD.tsv, -RELOAD-CURVE.tsv, -CANCEL.tsv, -SWITCH.tsv, -RAISE.tsv, -MELEE.tsv."""
import math, os, re, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_fire import load, cut

RG = re.compile(r"\] g t=([\d.]+) zf=(\S+) fov=\S+ sp=(\S+) clip=(-?\d+) rel=(\d) spd=(\S+) vz=(\S+) gr=(\d) duck=(\d) spr=(\d) wr=(\d) m=([-\d.]+),([-\d.]+),([-\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+) w=(\S+)")


def G(runs, tag):
    p = os.path.join(runs, tag + ".txt"); out = []
    if not os.path.exists(p): return out
    for l in open(p, encoding="utf-8"):
        g = RG.search(l)
        if g:
            v = g.groups()
            out.append(dict(t=float(v[0]), rel=int(v[4]), clip=int(v[3]), spd=float(v[5]), m=(float(v[11]) - float(v[14]), -(float(v[12]) - float(v[15])), float(v[13]) - float(v[16])), w=v[17]))
    return out


def ws_seq(fr):
    s = []
    for r in fr:
        if not s or s[-1][0] != r["ws"]: s.append([r["ws"], r["ct"]])
    return s


def mark(M, tag, name, n=0):
    v = [t for t, m in M[tag] if m == name]
    return v[n] if len(v) > n else None


def reload_rows(F, S, M, runs, pre):
    rows, curves = [], {}
    for tag in M:
        g = re.match(r"rt_([\w+]+?)_(tac|emp)_(\d)$", tag)
        if not g: continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        fr, sh = cut(F, a, b), cut(S, a, b)
        if not fr: continue
        # reload start: the weapon state leaves the post-shot state: first ws change that holds > 0.2 s after the last kick, or the rel flag
        cl = G(runs, tag)
        rel_on = next((x["t"] for x in cl if x["rel"]), None)
        rel_off = next((x["t"] for i, x in enumerate(cl) if i and cl[i - 1]["rel"] and not x["rel"]), None)
        rises = [(y["ct"], y["clip"] - x["clip"]) for x, y in zip(fr, fr[1:]) if y["clip"] > x["clip"]]
        clip0 = min((r["clip"] for r in fr), default=-1); clip1 = fr[-1]["clip"]
        row = dict(tag=tag, gun=g[1], kind=g[2], rel_dur=(rel_off - rel_on) if rel_on and rel_off else "", first_rise=(rises[0][0] - rel_on) if rises and rel_on else "", n_rises=len(rises), rises=";".join(f"{r[0] - rel_on:.2f}+{int(r[1])}" for r in rises)[:90] if rel_on else "", clip_low=clip0, clip_end=clip1)
        # motion in the reload: cycle against time
        if rel_on and rel_off:
            w = [r for r in fr if rel_on <= r["ct"] <= rel_off]
            seqs = defaultdict(list)
            for r in w: seqs[int(r["seq"])].append(r)
            row["seqs"] = ",".join(f"{k}:{(v[-1]['ct'] - v[0]['ct']):.2f}" for k, v in seqs.items())[:60]
            lin = []
            for k, v in seqs.items():
                if len(v) < 10: continue
                t0, t1 = v[0]["ct"], v[-1]["ct"]; c0, c1 = v[0]["cyc"], v[-1]["cyc"]
                if t1 <= t0 or c1 == c0: continue
                e = [r["cyc"] - (c0 + (c1 - c0) * (r["ct"] - t0) / (t1 - t0)) for r in v]
                lin.append(max(abs(x) for x in e))
            row["cycle_max_err"] = max(lin) if lin else ""
            mm = [x for x in cl if rel_on <= x["t"] <= rel_off and any(x["m"])]
            if len(mm) > 5:
                hip = cl[max(0, cl.index(mm[0]) - 3)]["m"]
                dist = [math.dist(x["m"], hip) for x in mm]
                pk = max(dist)
                row["muzzle_peak_u"] = pk
                row["t_peak_frac"] = (mm[dist.index(pk)]["t"] - rel_on) / (rel_off - rel_on)
                key = (g[1], g[2])
                if key not in curves:
                    curves[key] = [(round((x["t"] - rel_on) / (rel_off - rel_on), 3), x["m"][0] - hip[0], x["m"][1] - hip[1], x["m"][2] - hip[2], d / pk if pk else 0) for x, d in zip(mm, dist)]
        rows.append(row)
    return rows, curves


def write(path, rows, keys=None):
    keys = keys or sorted({k for r in rows for k in r}, key=lambda k: (k != "tag", k))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join((f"{r[k]:.3f}" if isinstance(r.get(k), float) else str(r.get(k, ""))) for k in keys) + "\n")


def cancel_rows(F, S, M, runs):
    out = []
    for tag in M:
        g = re.match(r"rc_(\w+?)_(\w+)_([\d.]+)$", tag)
        if not g: continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        fr, sh = cut(F, a, b), cut(S, a, b)
        cl = G(runs, tag)
        rel = [x for x in cl if x["rel"]]
        rises = [(y["ct"], y["clip"] - x["clip"]) for x, y in zip(fr, fr[1:]) if y["clip"] > x["clip"]]
        on = rel[0]["t"] if rel else None
        off = next((x["t"] for i, x in enumerate(cl) if i and cl[i - 1]["rel"] and not x["rel"]), None)
        out.append(dict(tag=tag, gun=g[1], action=g[2], at=g[3], rel_len=(off - on) if on and off else "", rises=";".join(f"{r[0] - on:.2f}+{int(r[1])}" for r in rises)[:60] if on else "", clip_end=fr[-1]["clip"] if fr else "", kicks=len(sh), rel_second=sum(1 for i, x in enumerate(cl) if i and x["rel"] and not cl[i - 1]["rel"])))
    return out


def switch_rows(F, S, M, runs):
    out = []
    for tag in M:
        if not tag.startswith("ws_"): continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        fr, sh = cut(F, a, b), cut(S, a, b)
        cl = G(runs, tag)
        ch = [(y["t"], x["w"], y["w"]) for x, y in zip(cl, cl[1:]) if x["w"] != y["w"]]
        cm = [t for t, m in M[tag] if m.startswith("cmd ") or m == "+weaponcycle"]
        wall = {t: m for t, m in M[tag]}
        # wall-to-ct: frames have both t and ct
        def to_ct(t):
            r = next((r for r in fr if r["t"] >= t), None)
            return r["ct"] if r else None
        cc = [to_ct(t) for t in cm]
        # time from each command to the next change of the active weapon on the client, and to the next kick
        d, k = [], []
        for c in cc:
            if c is None: continue
            nx = next((h[0] for h in ch if h[0] >= c - 0.02), None); d.append(nx - c if nx else float("nan"))
            nk = next((s["ct"] for s in sh if s["ct"] >= c - 0.02), None); k.append(nk - c if nk else float("nan"))
        ids = [int(r["w"]) for r in fr]
        out.append(dict(tag=tag, swaps=len(ch), cmd_to_active=",".join(f"{x:.2f}" for x in d), cmd_to_kick=",".join(f"{x:.2f}" for x in k), kicks=len(sh), names=">".join(h[2].replace("mp_weapon_", "") for h in ch)[:60], ws=",".join(str(int(s[0])) for s in ws_seq(fr))[:50]))
    return out


def raise_rows(F, S, M, runs):
    R = defaultdict(list)
    for tag in M:
        g = re.match(r"ra_(\w+?)_(\w+)_(\d)$", tag)
        if not g: continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        sh = cut(S, a, b)
        at = [t for t, m in M[tag] if m == "+attack"]
        zt = [t for t, m in M[tag] if m == "+zoom"]
        if g[2] == "adsprint":
            fr = cut(F, a, b); z = next((r["t"] for r in fr if r["zf"] > 0 and (not zt or r["t"] >= zt[0])), None)
            R[(g[1], g[2])].append(z - zt[0] if z and zt else float("nan"))
        elif sh and at:
            R[(g[1], g[2])].append(sh[0]["t"] - at[0])
    return [dict(gun=k[0], state=k[1], n=len(v), mean=st.mean(v), lo=min(v), hi=max(v)) for k, v in sorted(R.items())]


def melee_rows(F, S, M, runs):
    out = []
    for tag in M:
        if not tag.startswith("ml_") and not tag.startswith("or_"): continue
        a, b = M[tag][0][0], M[tag][-1][0] + 0.2
        fr, sh = cut(F, a, b), cut(S, a, b)
        t0 = [t for t, m in M[tag] if m == "+melee"]
        txt = open(os.path.join(runs, tag + ".txt"), encoding="utf-8").read() if os.path.exists(os.path.join(runs, tag + ".txt")) else ""
        dm = re.findall(r"\[RT\] dmg t=([\d.]+) amt=([\d.]+)", txt)
        cl = G(runs, tag)
        names = []
        for x in cl:
            if not names or names[-1][0] != x["w"]: names.append((x["w"], x["t"]))
        k = (sh[0]["t"] - t0[0]) if sh and t0 else ""
        seq = []
        for r in fr:
            if not seq or seq[-1] != int(r["seq"]): seq.append(int(r["seq"]))
        out.append(dict(tag=tag, dmg=",".join(x[1] for x in dm)[:30], kick_after=k, kicks=len(sh), weapons=">".join(n[0].replace("mp_weapon_", "") for n in names)[:50], active_times=",".join(f"{n[1] - names[0][1]:.2f}" for n in names)[:40], seqs=",".join(map(str, seq))[:40]))
    return out


def main():
    d, runs, pre = sys.argv[1:4]
    F, S, M = load(d)
    rows, curves = reload_rows(F, S, M, runs, pre)
    write(pre + "-RELOAD.tsv", rows, ["tag", "gun", "kind", "rel_dur", "first_rise", "n_rises", "rises", "clip_low", "clip_end", "seqs", "cycle_max_err", "muzzle_peak_u", "t_peak_frac"])
    with open(pre + "-RELOAD-CURVE.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("# R5 local hybrid, one run each. frac = time / reload length; dF dR dU = muzzle against the camera, change from before the reload, game units; norm = distance / peak distance.\ngun\tkind\tfrac\tdF\tdR\tdU\tnorm\n")
        for (g, k), c in sorted(curves.items()):
            last = -1
            for x in c:
                b = round(x[0] * 20) / 20
                if b != last:
                    f.write(f"{g}\t{k}\t{b:.2f}\t{x[1]:.2f}\t{x[2]:.2f}\t{x[3]:.2f}\t{x[4]:.2f}\n"); last = b
    write(pre + "-CANCEL.tsv", cancel_rows(F, S, M, runs), ["tag", "gun", "action", "at", "rel_len", "rel_second", "rises", "clip_end", "kicks"])
    write(pre + "-SWITCH.tsv", switch_rows(F, S, M, runs), ["tag", "swaps", "cmd_to_active", "cmd_to_kick", "kicks", "names", "ws"])
    write(pre + "-RAISE.tsv", raise_rows(F, S, M, runs), ["gun", "state", "n", "mean", "lo", "hi"])
    write(pre + "-MELEE.tsv", melee_rows(F, S, M, runs), ["tag", "dmg", "kick_after", "kicks", "weapons", "active_times", "seqs"])


if __name__ == "__main__":
    main()
