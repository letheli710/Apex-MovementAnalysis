"""D-72 summary tables from analyze_d72.py runs.csv files (one per height or merged).

Usage: summarize_d72.py <runs.csv> [<runs.csv> ...]  ->  markdown tables on stdout:
  1. per height x stance: n, mantled, climbed to the top, duration clusters, zmax
  2. per height, crouched, per duck delay D (and jump-earlier E): lead range, short / long counts, durations
  3. camera and S27 per height x duration cluster
Duration clusters (s): A < 0.60 (standing-like), S 0.60-0.69 (short), M 0.69-0.79, L >= 0.79 (long).
"""
import csv
import statistics as st
import sys
from collections import defaultdict


def cl(d):
    return "A" if d < 0.60 else "S" if d < 0.69 else "M" if d < 0.79 else "L"


def f(x):
    return None if x in (None, "") else float(x)


def rng(xs, nd=3):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "–"
    return f"{min(xs):.{nd}f}–{max(xs):.{nd}f}" if max(xs) - min(xs) > 10 ** -nd else f"{xs[0]:.{nd}f}"


def mean(xs, nd=2):
    xs = [x for x in xs if x is not None]
    return f"{st.mean(xs):.{nd}f}" if xs else "–"


def main():
    R = []
    for p in sys.argv[1:]:
        R += list(csv.DictReader(open(p, encoding="utf-8")))
    for r in R:
        r["h"] = int(r["height"])
        r["dur_"] = f(r.get("dur"))
        r["cls"] = cl(r["dur_"]) if r["dur_"] is not None else "-"
    hs = sorted({r["h"] for r in R})
    print("### 1. 每个高度 × 姿态\n")
    print("| 高度 | 姿态 | n | 翻越 | 上到台面 | A <0.60 | S 0.60–0.69 | M 0.69–0.79 | L ≥0.79 | 时长 s | 最高点 z |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for h in hs:
        for cr in ("0", "1"):
            g = [r for r in R if r["h"] == h and r["cr"] == cr]
            if not g:
                continue
            c = defaultdict(int)
            for r in g:
                c[r["cls"]] += 1
            print(f"| h{h} | {'蹲' if cr == '1' else '站'} | {len(g)} | {sum(r['mantle'] == '1' for r in g)} | "
                  f"{sum(r['climbed'] == '1' for r in g)} | {c['A']} | {c['S']} | {c['M']} | {c['L']} | "
                  f"{rng([r['dur_'] for r in g])} | {rng([f(r['zmax']) for r in g], 1)} |")
    print("\n### 2. 蹲姿，按下蹲时刻（起跳后 D 帧；E = 早起跳帧数）\n")
    for h in hs:
        g = [r for r in R if r["h"] == h and r["cr"] == "1"]
        if not g:
            continue
        print(f"\n**h{h}**\n")
        print("| E | D | n | 提前量 s | 蹲到底（距翻越开始）s | A | S | M | L | 时长 s |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for (e, d) in sorted({(int(r["e"]), int(r["d"])) for r in g}):
            gg = [r for r in g if int(r["e"]) == e and int(r["d"]) == d]
            c = defaultdict(int)
            for r in gg:
                c[r["cls"]] += 1
            print(f"| {e} | {d} | {len(gg)} | {rng([f(r.get('lead')) for r in gg])} | {rng([f(r.get('snap')) for r in gg])} | "
                  f"{c['A']} | {c['S']} | {c['M']} | {c['L']} | {rng([r['dur_'] for r in gg])} |")
    print("\n### 3. 镜头和 S27，按高度 × 时长类\n")
    print("| 高度 | 姿态 | 类 | n | 时长 s | 俯仰峰 ° | 峰时 s | 开始先 降/升/平 | 前 3 帧 ° | S27 δ 峰 ° | S27 开窗剩余 s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for h in hs:
        for cr in ("0", "1"):
            for k in "ASML":
                g = [r for r in R if r["h"] == h and r["cr"] == cr and r["cls"] == k]
                if not g:
                    continue
                fd = defaultdict(int)
                for r in g:
                    fd[r.get("cam_first") or "?"] += 1
                c3 = "/".join(mean([f(r.get(c)) for r in g]) for c in ("c1", "c2", "c3"))
                print(f"| h{h} | {'蹲' if cr == '1' else '站'} | {k} | {len(g)} | {mean([r['dur_'] for r in g], 3)} | "
                      f"{mean([f(r.get('cam_peak')) for r in g])} ({rng([f(r.get('cam_peak')) for r in g], 2)}) | "
                      f"{mean([f(r.get('cam_peak_t')) for r in g], 3)} | {fd['up']}/{fd['down']}/{fd['flat']} | {c3} | "
                      f"{mean([f(r.get('peak_delta')) for r in g])} | {mean([f(r.get('win_open_rem')) for r in g], 3)} |")


if __name__ == "__main__":
    main()
