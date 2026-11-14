#!/usr/bin/env python3
"""B6: pattern-table end (Flatline, R-99) and Wingman shot direction on server vs client.
  py -3 -I analyze_b6.py <frida dir> <marks.tsv> <runs dir> <out dir>  ->  B6-TABLE-END.tsv, B6-WINGMAN.tsv
Table end: Frida shots.csv rows inside each run (row = pattern row used by the kick). Wingman: each [RT] atk line on server and client
(attack pitch minus eye pitch) against the client punch2 at that kick (shots.csv s2P0)."""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_b1 import load_shots, marks, run_lines, ATK


def main():
    fd, mk, rd, out = sys.argv[1:5]
    sh = load_shots(fd); M = marks(mk)
    te, wg = [], []
    for tag in sorted(M):
        if not tag.startswith("b6"): continue
        t0 = M[tag][0][0] * 1000; t1 = M[tag][-1][0] * 1000 + 500
        S = [x for x in sh if t0 <= x["w"] <= t1]
        if "wingman" not in tag:
            rows = [int(x["row"]) for x in S]
            mx = max(rows) if rows else -1
            first_last = next((i for i, r in enumerate(rows) if r == mx), -1)
            dec = any(rows[i] < rows[i - 1] for i in range(1, len(rows)))
            after = rows[first_last:]
            # per-shot pitch kick column after the end (c1 = pitch of the row) to show it repeats the last row
            c1 = sorted(set(round(x["c1"], 4) for x in S[first_last:])) if first_last >= 0 else []
            te.append([tag, len(rows), mx, first_last + 1, len(after), int(dec), " ".join(map(str, c1[:4])), " ".join(map(str, rows[:3])) + " .. " + " ".join(map(str, rows[-3:]))])
        else:
            s, c = run_lines(os.path.join(rd, tag + ".txt"))
            sa = [m for m in (ATK.search(l) for l in s) if m]; ca = [m for m in (ATK.search(l) for l in c) if m]
            seen = []
            for m in ca:  # drop duplicate client lines (prediction reruns) with the same time
                if seen and abs(float(m.group(1)) - float(seen[-1].group(1))) < 1e-3: continue
                seen.append(m)
            for i, m in enumerate(seen):
                t = float(m.group(1))
                srv = min(sa, key=lambda x: abs(float(x.group(1)) - t)) if sa else None
                k = min(S, key=lambda x: abs(x["ct"] - t)) if S else None
                p2 = k["s2P0"] if k is not None and abs(k["ct"] - t) < 0.02 else float("nan")
                dc = (float(m.group(4)) + 180) % 360 - 180 - float(m.group(6))
                ds = ((float(srv.group(4)) + 180) % 360 - 180 - float(srv.group(6))) if srv else float("nan")
                wg.append([tag, i + 1, f"{t:.3f}", f"{ds:.4f}", f"{dc:.4f}", f"{p2:.4f}", f"{ds - p2:.4f}", f"{float(m.group(8)):.3f}"])
    with open(os.path.join(out, "B6-TABLE-END.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tshots\tmax_row\tfirst_shot_at_max_row\tshots_at_max_row\trow_ever_decreased\tpitch_of_rows_after_end\trows_first_last\n")
        for r in te: f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(out, "B6-WINGMAN.tsv"), "w", encoding="utf-8") as f:
        f.write("run\tshot\tt\tsv_bullet_minus_eye_pitch\tcl_bullet_minus_eye_pitch\tcl_punch2_pitch\tsv_minus_cl_punch\tspread\n")
        for r in wg: f.write("\t".join(map(str, r)) + "\n")
    print(len(te), len(wg))


if __name__ == "__main__":
    main()
