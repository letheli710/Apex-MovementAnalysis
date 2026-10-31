"""D-75: Unity before (main c97e804, unity_pre.csv) and after (d72/crouch-mantle, unity_post.csv) against R5 on the same 606 D72 trials.

Both CSVs come from unity_d72.py (one row per trial, joined to the R5 runs). Per height x stance x R5 duration cluster (summarize_d72.cl):
n, R5 / before / after mean mantle time, mean |Unity − R5| before / after, climbed (on the top) R5 / before / after, and the first
camera row of the mantle (pitch from the row before, deg) R5 / before / after. Rows without an R5 mantle keep only the climbed count.

Usage: compare_d75.py <unity_pre.csv> <unity_post.csv> <out.md>
"""
import csv
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summarize_d72 import cl  # noqa: E402


def f(x):
    return float(x) if x not in (None, "") else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def fmt(x, d=3):
    return "—" if x is None else ("%." + str(d) + "f") % x


def main():
    pre = {r["run"]: r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
    post = {r["run"]: r for r in csv.DictReader(open(sys.argv[2], encoding="utf-8"))}
    g = defaultdict(list)
    for run, a in pre.items():
        b = post.get(run)
        if not b:
            continue
        stance = "蹲" if a["r5_cr"] == "1" else "站"
        c = cl(float(a["r5_dur"])) if a["r5_mantle"] == "1" and a["r5_dur"] else "没翻越"
        g[(int(a["height"]), stance, c)].append((a, b))
    lines = ["| 高度 | 姿态 | R5 类 | n | R5 时长 | Unity 改前 | Unity 改后 | 平均差 改前 → 改后 | 上台面 R5 / 改前 / 改后 | 第一帧俯仰 R5 / 改前 / 改后 |",
             "|---|---|---|---:|---:|---:|---:|---|---|---|"]
    tot = {"pre": [], "post": []}
    for k in sorted(g):
        rows = g[k]
        r5 = [f(a["r5_dur"]) for a, _ in rows]
        up = [f(a["u_dur"]) for a, _ in rows]
        uq = [f(b["u_dur"]) for _, b in rows]
        ep = [abs(u - r) for u, r in zip(up, r5) if u is not None and r is not None]
        eq = [abs(u - r) for u, r in zip(uq, r5) if u is not None and r is not None]
        tot["pre"] += ep
        tot["post"] += eq
        climbed = "%d / %d / %d" % (sum(a["r5_climbed"] == "1" for a, _ in rows), sum(a["u_climbed"] == "1" for a, _ in rows),
                                    sum(b["u_climbed"] == "1" for _, b in rows))
        c1 = "%s / %s / %s" % (fmt(mean([f(a["r5_c1"]) for a, _ in rows]), 2), fmt(mean([f(a["u_c1"]) for a, _ in rows]), 2),
                               fmt(mean([f(b["u_c1"]) for _, b in rows]), 2))
        lines.append("| h%d | %s | %s | %d | %s | %s | %s | %s → %s | %s | %s |" % (
            k[0], k[1], k[2], len(rows), fmt(mean(r5)), fmt(mean(up)), fmt(mean(uq)), fmt(mean(ep)), fmt(mean(eq)), climbed, c1))
    lines.append("")
    lines.append("全部有时长的试次：平均 |Unity − R5| 改前 %s s（n %d）→ 改后 %s s（n %d）。" % (
        fmt(mean(tot["pre"])), len(tot["pre"]), fmt(mean(tot["post"])), len(tot["post"])))
    open(sys.argv[3], "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
