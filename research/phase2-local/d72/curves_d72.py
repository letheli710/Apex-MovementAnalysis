"""D-72: mean camera pitch (deg, Source + = down, relative to the frame before the mantle) from the mantle start, R5 vs Unity
(Reference, before D-72), per height x stance x R5 duration cluster (summarize_d72.cl). R5 from analyze_d72 cam.csv; Unity from the
CameraFeelBatch reference.csv / body.csv (MANTLE_START), joined by run number through unity_d72.py's unity_pre.csv.

Usage: curves_d72.py <cam.csv> <unity_pre.csv> <unity_out> <out.csv>   (t = 0, 0.025 … 0.9 s; linear interpolation per trial)
"""
import csv
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summarize_d72 import cl  # noqa: E402

TS = [round(0.025 * i, 3) for i in range(37)]


def interp(ts, ps, t):
    if not ts or t < ts[0] or t > ts[-1]:
        return None
    for i in range(1, len(ts)):
        if ts[i] >= t:
            a = (t - ts[i - 1]) / (ts[i] - ts[i - 1]) if ts[i] > ts[i - 1] else 0.0
            return ps[i - 1] + a * (ps[i] - ps[i - 1])
    return ps[-1]


def main():
    cam, upre, uo, out = sys.argv[1:5]
    r5 = defaultdict(list)
    for r in csv.DictReader(open(cam, encoding="utf-8")):
        r5[r["run"]].append((float(r["t"]), float(r["pitch"])))
    groups = defaultdict(lambda: {"r5": [], "u": []})
    for u in csv.DictReader(open(upre, encoding="utf-8")):
        if u["r5_mantle"] != "1" or not u["r5_dur"]:
            continue
        key = (int(u["height"]), "蹲" if u["r5_cr"] == "1" else "站", cl(float(u["r5_dur"])))
        tr = sorted(r5.get(u["run"], []))
        if tr:
            groups[key]["r5"].append([interp([a for a, _ in tr], [b for _, b in tr], t) for t in TS])
        if u["u_mantle"] == "1":
            B = list(csv.DictReader(open(os.path.join(uo, u["trial"], "body.csv"), encoding="utf-8")))
            C = list(csv.DictReader(open(os.path.join(uo, u["trial"], "reference.csv"), encoding="utf-8")))
            ts = next(float(b["t"]) for b in B if "MANTLE_START" in b["events"])
            pre = [c for c in C if float(c["t"]) < ts - 1e-9]
            p0 = float(pre[-1]["pitch"]) if pre else 0.0
            cc = [(float(c["t"]) - ts, float(c["pitch"]) - p0) for c in C if float(c["t"]) >= ts - 1e-9]
            groups[key]["u"].append([interp([a for a, _ in cc], [b for _, b in cc], t) for t in TS])
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["height", "stance", "cluster", "src", "n"] + TS)
        for key in sorted(groups):
            for src in ("r5", "u"):
                rows = groups[key][src]
                if not rows:
                    continue
                means = []
                for i in range(len(TS)):
                    xs = [r[i] for r in rows if r[i] is not None]
                    means.append(round(st.mean(xs), 3) if xs else "")
                w.writerow([key[0], key[1], key[2], src, len(rows)] + means)
    print("->", out)


if __name__ == "__main__":
    main()
