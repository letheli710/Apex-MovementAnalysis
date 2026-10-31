"""D-72: the Unity Reference body (HSD-Unity CameraFeelBatch) on the same R5 inputs, one row per trial, next to R5 (analyze_d72.py).

Inputs: <ctr_dir> = research/feel/camera_to_trial.py output of the D72 sessions (trial.json + samples.csv + camera.csv per trial),
        <unity_out> = CameraFeelBatch -trials <ctr_dir> -out <unity_out> (body.csv: t, pos, vel, events; reference.csv: camera).
Per trial: mantle span MANTLE_START -> MANTLE_END (u_dur), climbed (top reached), zmax, CLIMB_START seen, camera pitch from the row
before MANTLE_START: peak, peak time, the first three rows (u_c1..u_c3). Joined to the R5 runs.csv by run number.

Usage: unity_d72.py <ctr_dir> <unity_out> <r5_runs.csv> [<r5_runs.csv> ...] <out.csv>
"""
import csv
import os
import re
import sys

FLOOR = 294.92


def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def main():
    ctr, uo, out = sys.argv[1], sys.argv[2], sys.argv[-1]
    r5 = {}
    for p in sys.argv[3:-1]:
        for r in load(p):
            r5[r["run"]] = r
    rows = []
    for d in sorted(os.listdir(uo)):
        bp, cp = os.path.join(uo, d, "body.csv"), os.path.join(uo, d, "reference.csv")
        if not os.path.exists(bp):
            continue
        m = re.search(r"_r(\d+)$", d)
        run = m.group(1) if m else None
        B, C = load(bp), load(cp)
        h = int(re.search(r"_h(\d+)", d).group(1))
        ts = next((float(b["t"]) for b in B if "MANTLE_START" in b["events"]), None)
        te = next((float(b["t"]) for b in B if ts is not None and float(b["t"]) > ts and "MANTLE_END" in b["events"]), None)
        zmax = max(float(b["pos_z"]) for b in B)
        row = dict(run=run, trial=d, height=h, u_mantle=int(ts is not None), u_climb=int(any("CLIMB_START" in b["events"] for b in B)),
                   u_dur=round(te - ts, 4) if ts is not None and te is not None else None, u_zmax=round(zmax, 2),
                   u_climbed=int(zmax >= FLOOR + h - 10.0))
        if ts is not None:
            pre = [c for c in C if float(c["t"]) < ts - 1e-9]
            p0 = float(pre[-1]["pitch"]) if pre else 0.0
            span = [c for c in C if ts - 1e-9 <= float(c["t"]) <= ts + (row["u_dur"] or 0.9) + 0.3]
            if span:
                pk = max(span, key=lambda c: float(c["pitch"]) - p0)
                row.update(u_cam_peak=round(float(pk["pitch"]) - p0, 3), u_cam_peak_t=round(float(pk["t"]) - ts, 4))
                for i in range(3):
                    row[f"u_c{i + 1}"] = round(float(span[i]["pitch"]) - p0, 3) if i < len(span) else None
        r = r5.get(run, {})
        for k in ("schedule", "cr", "d", "e", "lead", "snap", "dur", "mantle", "climbed", "zmax", "cam_peak", "cam_peak_t", "c1", "c2", "c3",
                  "peak_delta", "win_open_rem"):
            row["r5_" + k] = r.get(k)
        rows.append(row)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "trials ->", out)


if __name__ == "__main__":
    main()
