#!/usr/bin/env python3
"""B1: landing then firing, and the spring constants of both punch groups after a landing.
  py -3 -I analyze_b1.py <frida dir> <marks.tsv> <runs dir> <out dir>
Writes B1-SHOTS.tsv (one shot per drop run) and B1-SPRING.tsv (k, d fitted per group per drop run).
Shot match: Frida shots.csv row whose game time ct equals the client atk time (same client clock)."""
import csv, os, re, sys
from collections import defaultdict


def load_frames(d):
    with open(os.path.join(d, "frames.csv"), encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = []
        for x in r:
            try:
                rows.append({k: (float(v) if v not in ("", None) else float("nan")) for k, v in x.items()})
            except ValueError:
                pass
    return rows


def load_shots(d):
    with open(os.path.join(d, "shots.csv"), encoding="utf-8") as f:
        return [{k: (float(v) if v else float("nan")) for k, v in x.items()} for x in csv.DictReader(f)]


def marks(path):
    m = defaultdict(list)
    for l in open(path, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        m[p[0]].append((float(p[1]), p[2]))
    return m


ATK = re.compile(r"atk t=([\d.]+) w=(\S+) n=(\d+) o=\S+ dP=(-?[\d.]+) dY=(-?[\d.]+) eP=(-?[\d.]+) eY=(-?[\d.]+) sp=([\d.]+) zf=([\d.]+)")


def run_lines(path):
    s, c, side = [], [], None
    for l in open(path, encoding="utf-8"):
        if l.startswith("## server"): side = s; continue
        if l.startswith("## client"): side = c; continue
        if side is not None: side.append(l.rstrip())
    return s, c


def fit_spring(t, x, v):
    """least squares a = -k x - d v on frames (a from successive v). Returns k, d, n."""
    A = []
    for i in range(len(t) - 1):
        dt = t[i + 1] - t[i]
        if dt <= 0: continue
        a = (v[i + 1] - v[i]) / dt
        xm, vm = (x[i] + x[i + 1]) / 2, (v[i] + v[i + 1]) / 2
        A.append((xm, vm, a))
    if len(A) < 8: return float("nan"), float("nan"), len(A)
    sxx = sum(p[0] * p[0] for p in A); svv = sum(p[1] * p[1] for p in A); sxv = sum(p[0] * p[1] for p in A)
    sxa = sum(p[0] * p[2] for p in A); sva = sum(p[1] * p[2] for p in A)
    det = sxx * svv - sxv * sxv
    if abs(det) < 1e-12: return float("nan"), float("nan"), len(A)
    k = -(sxa * svv - sva * sxv) / det
    d = -(sva * sxx - sxa * sxv) / det
    return k, d, len(A)


def main():
    fd, mk, rd, out = sys.argv[1:5]
    fr = load_frames(fd); sh = load_shots(fd); M = marks(mk)
    shots_out, spring_out = [], []
    for tag in sorted(M):
        if not tag.startswith("b1"): continue
        path = os.path.join(rd, tag + ".txt")
        if not os.path.exists(path): continue
        s, c = run_lines(path)
        t0 = min(t for t, _ in M[tag]) * 1000; t1 = max(t for t, _ in M[tag]) * 1000 + 300
        F = [x for x in fr if t0 <= x["w"] <= t1]
        if not F: continue
        land = next((float(l.split("t=")[1]) for l in c if "] land t=" in l), None)
        # landing frame in Frida: first frame after the drop where p1 velocity jumps (landing kick) - use vz from client logger instead
        vz = [float(re.search(r"vz=(-?[\d.]+)", l).group(1)) for l in c if "] g t=" in l]
        vland = min(vz) if vz else float("nan")
        if tag.startswith("b1s_") or True:
            # spring fit after the landing kick: frames after the frame where |pv1P| is largest, 1.2 s
            if land is not None or tag.startswith("b1s_"):
                ipk = max(range(len(F)), key=lambda i: abs(F[i]["pv1P"]) if F[i]["pv1P"] == F[i]["pv1P"] else 0)
                G = [x for x in F[ipk + 1:] if x["ct"] - F[ipk]["ct"] < 1.2]
                tt = [x["ct"] for x in G]
                k1, d1, n1 = fit_spring(tt, [x["p1P"] for x in G], [x["pv1P"] for x in G])
                # punch2: only frames with no shot in the window
                k2, d2, n2 = fit_spring(tt, [x["s2P"] for x in G], [x["v2P"] for x in G])
                kh = [x["kP"] for x in G if x["kP"] == x["kP"]]; dh = [x["dP"] for x in G if x["dP"] == x["dP"]]
                p1pk = max((abs(x["p1P"]) for x in F), default=float("nan")); s2pk = max((abs(x["s2P"]) for x in F), default=float("nan"))
                zf = sum(x["zf"] for x in G) / len(G) if G else float("nan")
                spring_out.append([tag, f"{vland:.0f}", f"{p1pk:.3f}", f"{s2pk:.3f}", f"{k1:.1f}", f"{d1:.2f}", n1, f"{k2:.1f}", f"{d2:.2f}", n2,
                                   f"{(sum(kh) / len(kh)) if kh else float('nan'):.1f}", f"{(sum(dh) / len(dh)) if dh else float('nan'):.2f}", f"{zf:.2f}", f"{(s2pk / p1pk) if p1pk else float('nan'):.3f}"])
        if not tag.startswith("b1_"): continue
        sa = [ATK.search(l) for l in s if "atk t=" in l]; ca = [ATK.search(l) for l in c if "atk t=" in l]
        sa = [m for m in sa if m]; ca = [m for m in ca if m]
        if not ca: shots_out.append([tag] + ["noshot"]); continue
        ct = float(ca[0].group(1))
        row = min(sh, key=lambda x: abs(x["ct"] - ct)) if sh else None
        if row is None or abs(row["ct"] - ct) > 0.02: row = None
        fframe = min(F, key=lambda x: abs(x["ct"] - ct))
        p1, s2 = (row["p1P"], row["s2P0"]) if row else (float("nan"), float("nan"))
        dPc = float(ca[0].group(4)); dPs = float(sa[0].group(4)) if sa else float("nan")
        spc = float(ca[0].group(8)); sps = float(sa[0].group(8)) if sa else float("nan")
        dmg = [l for l in s if "] dmg" in l]
        dl = (ct - land) if land is not None else float("nan")
        shots_out.append([tag, f"{vland:.0f}", f"{dl:.3f}", f"{dPs:.3f}", f"{dPc:.3f}", f"{float(sa[0].group(6)) if sa else float('nan'):.3f}", f"{p1:.3f}", f"{s2:.3f}", f"{p1 + s2:.3f}",
                          f"{dPc - (p1 + s2):.3f}", f"{dPc - s2:.3f}", f"{sps:.3f}", f"{spc:.3f}", f"{fframe['fP']:.3f}", f"{fframe['zf']:.2f}", "hit" if dmg else "miss"])
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "B1-SHOTS.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tv_land\tland_to_shot_s\tsv_bullet_pitch\tcl_bullet_pitch\tsv_eye_pitch\tpunch1_pitch\tpunch2_pitch\tp1+p2\tcl_minus_p1p2\tcl_minus_p2\tsv_spread\tcl_spread\tscreen_pitch\tzf\ttarget\n")
        for r in shots_out: f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(out, "B1-SPRING.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tv_land\tp1_peak\tp2_peak\tk1_fit\td1_fit\tn1\tk2_fit\td2_fit\tn2\tk_hook_mean\td_hook_mean\tzf\tp2/p1_peak\n")
        for r in spring_out: f.write("\t".join(map(str, r)) + "\n")
    print(len(shots_out), "shots", len(spring_out), "spring rows")


if __name__ == "__main__":
    main()
