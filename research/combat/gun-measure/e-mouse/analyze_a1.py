#!/usr/bin/env python3
"""A1: does a real downward mouse pull eat the weapon punch?
  py -3 -I analyze_a1.py <frames.csv> <marks.tsv> <out_dir> [deg_per_count=0.11]
Writes A1-FRAMES.tsv (per frame, every A1 run) and A1-RUNS.tsv (per run summary).
Mouse input in degrees = counts x deg_per_count (calibrated: 40 counts -> 4.40 deg pitch, 99 counts -> 10.89 deg yaw, no fire).
Pitch is positive down; the punch kicks up (negative)."""
import csv, os, sys
from collections import defaultdict


def main():
    frames, marks, out = sys.argv[1:4]
    k = float(sys.argv[4]) if len(sys.argv) > 4 else 0.11
    mk = defaultdict(list)
    for l in open(marks, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("a1_"):
            mk[p[0]].append((float(p[1]) * 1000, p[2], p[3] if len(p) > 3 else ""))
    fr = [r for r in csv.DictReader(open(frames)) if r["w"]]
    ws = [float(r["w"]) for r in fr]
    fo = open(os.path.join(out, "A1-FRAMES.tsv"), "w", encoding="utf-8")
    fo.write("run\tt\tfiring\tmouse_cnt\tmouse_deg\taimP\tviewP\tpunchP\tpunchVelP\tshot_idx\tzf\n")
    ro = open(os.path.join(out, "A1-RUNS.tsv"), "w", encoding="utf-8")
    ro.write("run\tkind\tfire_s\tshots\tcnt_fire\tcnt_after\tin_deg\taim_end\teaten_deg\taim_moved_while_firing\tin_deg_while_firing\tpunch_min\tpunch_end_of_fire\tview_end_minus_aim\n")
    for tag, m in mk.items():
        t0, t1 = m[0][0], m[-1][0]
        ta = next((x[0] for x in m if x[1] == "+attack"), None); te = next((x[0] for x in m if x[1] == "-attack"), None)
        mv = [(x[0], int(x[2].split(",")[1])) for x in m if x[1] == "m"]
        rows = [r for r, w in zip(fr, ws) if t0 - 100 <= w <= t1 + 100]
        cum, j, prevb = 0, 0, None
        aim0 = float(rows[0]["bP"])
        shots = 0; pmin = 0.0; aim_fire_start = aim_fire_end = None; cnt_fire = cnt_after = 0; p_end = None
        for x in mv:
            if ta and te and ta <= x[0] <= te + 30: cnt_fire += x[1]
            else: cnt_after += x[1]
        for r in rows:
            w = float(r["w"])
            while j < len(mv) and mv[j][0] <= w:
                cum += mv[j][1]; j += 1
            firing = 1 if (ta and te and ta <= w <= te) else 0
            b, s2 = float(r["bP"]), float(r["s2P"] or 0)
            if r["idx"]: shots = max(shots, int(float(r["idx"])))
            pmin = min(pmin, s2)
            if firing and aim_fire_start is None: aim_fire_start = b
            if firing: aim_fire_end = b; p_end = s2
            fo.write(f"{tag}\t{(w - t0) / 1000:.4f}\t{firing}\t{cum}\t{cum * k:.3f}\t{r['bP']}\t{r['fP']}\t{r['s2P']}\t{r['v2P']}\t{r['idx']}\t{r['zf']}\n")
        aim_end = float(rows[-1]["bP"]) - aim0
        in_deg = cum * k
        kind = tag.rsplit("_", 1)[0]
        mw = (aim_fire_end - aim_fire_start) if aim_fire_start is not None else ""
        ro.write(f"{tag}\t{kind}\t{(te - ta) / 1000 if ta else 0:.3f}\t{shots}\t{cnt_fire}\t{cnt_after}\t{in_deg:.3f}\t{aim_end:.3f}\t{in_deg - aim_end:.3f}\t{mw if mw == '' else round(mw, 3)}\t{cnt_fire * k:.3f}\t{pmin:.3f}\t{p_end if p_end is None else round(p_end, 3)}\t{float(rows[-1]['fP']) - float(rows[-1]['bP']):.3f}\n")
    fo.close(); ro.close()
    print(open(os.path.join(out, "A1-RUNS.tsv")).read())


if __name__ == "__main__":
    main()
