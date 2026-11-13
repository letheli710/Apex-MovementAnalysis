#!/usr/bin/env python3
"""B2: does firing add any view offset beyond the punch springs?
  py -3 -I analyze_b2.py <frida dir> <marks.tsv> <out dir>  ->  B2-SHAKE.tsv
Per run and window (pre = still before the first +attack, fire = first +attack .. last shot + 0.3 s, post = after):
  r_out  = screen - aim - punch-output (anything CalcView adds after the punch function: shake would land here)
  r_fit  = screen - aim - punch1 - c * punch2, c fitted per run on the fire window (anything inside the punch output that is not the two springs: drift, or a shake)
  pos    = eye position change from the pre-window mean (position shake), roll = screen roll - punch roll
Max abs values per window; units degrees and game units."""
import csv, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_b1 import load_frames, marks


def stats(v):
    v = [x for x in v if x == x]
    return max((abs(x) for x in v), default=float("nan"))


def main():
    fd, mk, out = sys.argv[1:4]
    fr = load_frames(fd); M = marks(mk)
    rows = []
    for tag in sorted(M):
        if not tag.startswith("b2_"): continue
        ev = M[tag]
        t0 = ev[0][0] * 1000; t1 = ev[-1][0] * 1000
        F = [x for x in fr if t0 <= x["w"] <= t1]
        if len(F) < 50: continue
        fire_on = [t * 1000 for t, m in ev if m == "+attack"]
        shake = [t * 1000 for t, m in ev if m.startswith("cl ")]
        a = (fire_on or shake)[0]
        last = ([t * 1000 for t, m in ev if m == "-attack"] or shake)[-1]
        # last kick: last frame whose shot index changed
        idx_change = [F[i]["w"] for i in range(1, len(F)) if F[i]["idx"] != F[i - 1]["idx"]]
        b = max([last] + [x for x in idx_change if x > a]) + 300
        pre = [x for x in F if t0 + 300 <= x["w"] < a]; fire = [x for x in F if a <= x["w"] < b]; post = [x for x in F if x["w"] >= b]
        if not pre or not fire: continue
        e0 = [sum(x[k] for x in pre) / len(pre) for k in ("eX", "eY", "eZ")]
        # fit c on fire window: y = fP - bP - p1P = c * s2P + k
        X = [x["s2P"] for x in fire]; Y = [x["fP"] - x["bP"] - x["p1P"] for x in fire]
        n = len(X); mx = sum(X) / n; my = sum(Y) / n
        sxx = sum((x - mx) ** 2 for x in X)
        c = sum((X[i] - mx) * (Y[i] - my) for i in range(n)) / sxx if sxx > 1e-9 else float("nan")
        kk = my - (c if c == c else 0) * mx
        res = {}
        for nm, W in (("pre", pre), ("fire", fire), ("post", post)):
            res[nm] = dict(
                r_out=stats([x["fP"] - x["bP"] - x["puP"] for x in W] + [x["fY"] - x["bY"] - x["puY"] for x in W]),
                r_fitP=stats([x["fP"] - x["bP"] - x["p1P"] - (c if c == c else 1) * x["s2P"] - kk for x in W]),
                roll=stats([x["fR"] - x["puR"] for x in W]),
                pos=stats([((x["eX"] - e0[0]) ** 2 + (x["eY"] - e0[1]) ** 2 + (x["eZ"] - e0[2]) ** 2) ** 0.5 for x in W]),
                s2=stats([x["s2P"] for x in W]))
        shots = len(set(x["idx"] for x in fire)) - 1
        g = tag.split("_")
        rows.append([tag, g[1], g[2], shots, f"{c:.3f}"] + [f"{res[w][k]:.3f}" for w in ("pre", "fire", "post") for k in ("r_out", "r_fitP", "roll", "pos", "s2") if w in res])
    with open(os.path.join(out, "B2-SHAKE.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tgun\tmode\tshots\tc_punch2_to_screen\t" + "\t".join(f"{w}_{k}" for w in ("pre", "fire", "post") for k in ("r_out", "r_fitP", "roll", "pos", "punch2")) + "\n")
        for r in rows: f.write("\t".join(map(str, r)) + "\n")
    print(len(rows), "runs")


if __name__ == "__main__" and len(sys.argv) == 4:
    main()


def cycle_table(fd, mk, out):
    """B2-CYCLE.tsv: the camera offset that is not punch (r_out) after each shot / empty clip: onset after the shot, peaks, duration.
    It comes with the weapon's cycle animation (bolt, pump, reload), not at the shot."""
    fr = load_frames(fd); M = marks(mk); rows = []
    for tag in sorted(M):
        if not tag.startswith("b2_") or "ctrl" in tag: continue
        ev = M[tag]; t0 = ev[0][0] * 1000; t1 = ev[-1][0] * 1000
        F = [x for x in fr if t0 <= x["w"] <= t1]
        shots = [F[i] for i in range(1, len(F)) if F[i]["idx"] > F[i - 1]["idx"]]
        if not shots: continue
        s0 = shots[0]
        nxt = shots[1]["w"] if len(shots) > 1 else t1
        W = [x for x in F if s0["w"] <= x["w"] < nxt]
        on = [x for x in W if abs(x["fP"] - x["bP"] - x["puP"]) > 0.005 or abs(x["fR"] - x["puR"]) > 0.005]
        clip_empty = shots[-1]["clip"] == 0
        if not on:
            rows.append([tag, len(shots), "none", "", "", "", "", "", int(clip_empty)]); continue
        onset = (on[0]["w"] - s0["w"]) / 1000
        dur = (on[-1]["w"] - on[0]["w"]) / 1000
        pk = lambda f: max((f(x) for x in W), key=abs)
        rows.append([tag, len(shots), f"{onset:.3f}", f"{dur:.3f}", f"{pk(lambda x: x['fP'] - x['bP'] - x['puP']):.3f}", f"{pk(lambda x: x['fY'] - x['bY'] - x['puY']):.3f}",
                     f"{pk(lambda x: x['fR'] - x['puR']):.3f}", f"{max(abs(x['eZ'] - s0['eZ']) for x in W):.3f}", int(clip_empty)])
    with open(os.path.join(out, "B2-CYCLE.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tshots\tonset_after_first_shot_s\tvisible_s\tpeak_pitch\tpeak_yaw\tpeak_roll\tpeak_eye_z_u\tclip_emptied\n")
        for r in rows: f.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__" and len(sys.argv) > 4 and sys.argv[4] == "cycle":
    cycle_table(*sys.argv[1:4])
