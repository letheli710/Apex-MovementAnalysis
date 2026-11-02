#!/usr/bin/env python3
"""Per-case fire summary: kicks and interval from shots.csv, clip steps and damage from the server lines, FOV and zf from frames.csv, spread from the client log, reload timing.
  py -3 -I an_fire.py <session dir> <runs dir> <out.tsv> [tag-prefix ...]"""
import csv, os, re, statistics as st, sys
from collections import Counter, defaultdict


def rows(p):
    o = []
    for r in csv.DictReader(open(p)):
        try: o.append({k: float(v) if v not in ("", None) else float("nan") for k, v in r.items() if k})
        except (TypeError, ValueError): pass
    return o


def load(d):
    wall = int(open(os.path.join(d, "wall.txt")).read()) / 1000
    marks = defaultdict(list)
    for l in open(os.path.join(d, "marks.tsv"), encoding="utf-8"):
        t, ts, m = l.rstrip("\n").split("\t", 2); marks[t].append((float(ts) - wall, m))
    return rows(os.path.join(d, "frames.csv")), rows(os.path.join(d, "shots.csv")), marks


def cut(R, a, b):
    return [r for r in R if a <= r["t"] <= b]


def summary(tag, F, S, marks, runs):
    m = marks[tag]; a, b = m[0][0], m[-1][0] + 0.25
    fr, sh = cut(F, a, b), cut(S, a, b)
    out = dict(tag=tag)
    txt = open(os.path.join(runs, tag + ".txt"), encoding="utf-8").read() if os.path.exists(os.path.join(runs, tag + ".txt")) else ""
    dm = re.findall(r"\[RT\] dmg t=([\d.]+) amt=([\d.]+) hg=(\d+)", txt)
    cl = re.findall(r"\[RT\] clip t=([\d.]+) c=(-?\d+)", txt)
    out["kicks"] = len(sh)
    iv = [y["ct"] - x["ct"] for x, y in zip(sh, sh[1:]) if 0 < y["ct"] - x["ct"]]
    out["kick_iv_med"] = round(st.median(iv), 4) if iv else ""
    out["kick_iv_first"] = round(iv[0], 4) if iv else ""
    out["kick_iv_last"] = round(iv[-1], 4) if iv else ""
    # clip from frames: every drop is a shot on the client
    drops, rises = [], []
    for x, y in zip(fr, fr[1:]):
        if y["clip"] < x["clip"]: drops.append((y["ct"], x["clip"] - y["clip"]))
        if y["clip"] > x["clip"]: rises.append((y["ct"], y["clip"] - x["clip"]))
    out["clip_drops"] = len(drops); out["ammo_per_drop"] = Counter(d[1] for d in drops).most_common(1)[0][0] if drops else ""
    dv = [y[0] - x[0] for x, y in zip(drops, drops[1:])]
    out["drop_iv_med"] = round(st.median(dv), 4) if dv else ""
    out["rises"] = ";".join(f"{r[0] - (fr[0]['ct'] if fr else 0):.2f}+{int(r[1])}" for r in rises)[:80]
    cc = Counter((round(float(x[1])), int(x[2])) for x in dm)
    out["hits"] = len(dm); out["dmg"] = ",".join(f"{k[0]}h{k[1]}x{v}" for k, v in cc.most_common(5))
    zo = [r["fov"] for r in fr]
    out["minfov"] = round(min(zo), 2) if zo else ""
    out["clipmax"] = max((int(c[1]) for c in cl), default="")
    sp = re.findall(r"\] g t=\S+ zf=(\S+) fov=\S+ sp=(\S+)", txt)
    if sp:
        v = [float(s[1]) for s in sp]; out["spread_min"] = min(v); out["spread_max"] = max(v)
    out["pk_s2"] = round(max((abs(r["s2P"]) for r in fr), default=0), 2)
    return out


def main():
    d, runs, outp = sys.argv[1:4]; pre = sys.argv[4:]
    F, S, marks = load(d)
    res = [summary(t, F, S, marks, runs) for t in marks if not pre or any(t.startswith(p) for p in pre)]
    keys = ["tag", "kicks", "kick_iv_med", "kick_iv_first", "kick_iv_last", "clip_drops", "ammo_per_drop", "drop_iv_med", "hits", "dmg", "clipmax", "minfov", "spread_min", "spread_max", "pk_s2", "rises"]
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in res: f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")


if __name__ == "__main__":
    main()
