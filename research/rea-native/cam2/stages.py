"""CAM2: summarise the camera-stage probe (frida_cam2_stages.js) around jumps, mantles and zipline rides.

Usage: stages.py <probe.csv> [jumps|rides]
  jumps  per takeoff (vz rises above 150 from below 20): final pitch, the punch (spring 1 + spring 2), spring 1 alone, the traversal stage
         and the final / roll-in roll, every 0.1 s for 1 s after the takeoff
  rides  per zipline ride (Zipline_CameraRoll ran): the native roll target, the smoothed rope roll, the final roll, the eye above the origin
         and the smoothed zipline view offset (player +0x2f78, yaw frame: forward, left, up), every 0.2 s
The probe CSV is local data (not committed). stdlib only.
"""
import csv
import math
import sys


def load(path):
    return [{k: (float(v) if v not in ("", None) else float("nan")) for k, v in r.items()} for r in csv.DictReader(open(path))]


def at(rows, t, lo, hi):
    return min(range(lo, hi), key=lambda i: abs(rows[i]["t"] - t))


def jumps(rows):
    tk = [i for i in range(1, len(rows)) if rows[i]["vz"] > 150 and rows[i - 1]["vz"] < 20]
    print(f"{len(tk)} takeoffs")
    for i in tk:
        t0, r0 = rows[i]["t"], rows[i - 1]
        lo, hi = max(0, i - 50), min(len(rows), i + 400)
        print(f"t0 {t0:.2f}  origin z {rows[i]['oz']:.0f}")
        for k in ("fP", "puP", "p1P", "tvP", "fR", "rollIn"):
            base = 0.0 if k in ("p1P", "tvP") else r0[k]
            print(f"   {k:6s}" + " ".join(f"{rows[at(rows, t0 + j * 0.1, lo, hi)][k] - base:6.2f}" for j in range(11)))


def rides(rows):
    on = [i for i, r in enumerate(rows) if not math.isnan(r["zipRoll"])]
    groups, cur = [], []
    for i in on:
        if cur and i - cur[-1] > 5:
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)
    print(f"{len(groups)} rides")
    for g in groups:
        a, b = g[0], g[-1]
        print(f"ride {rows[a]['t']:.2f}-{rows[b]['t']:.2f} s")
        t = rows[a]["t"] - 0.2
        while t <= rows[b]["t"] + 0.6:
            r = rows[at(rows, t, max(0, a - 60), min(len(rows), b + 120))]
            print(f"   t {r['t'] - rows[a]['t']:5.2f} yaw {r['fY']:7.2f} target {r['zipRoll']:6.2f} rope {r['smRoll']:6.2f} final {r['fR']:6.2f}"
                  f"  eye {r['ez'] - r['oz']:6.2f}  offset {r['zoX']:5.2f} {r['zoY']:5.2f} {r['zoZ']:6.2f}")
            t += 0.2


if __name__ == "__main__":
    data = load(sys.argv[1])
    (rides if len(sys.argv) > 2 and sys.argv[2] == "rides" else jumps)(data)
