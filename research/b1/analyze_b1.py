"""B1 mantle boost analysis: per-frame ring values ([B1-MB] client logger), press decisions ([MB-TRIG]) and the per-traversal
sweet-spot fractions ([MB-RUI]) from hsd_session B1_* sessions.

delta (deg) = the angle between the aim and the rendered (traversal-camera) view, from the two RUI offsets the ring reads:
  vao = -0.5 sin(a) / (cos(a) tanY) with a = the 1.5 deg threshold  ->  tanY
  cho = -0.5 tan(d) / tanY                                             ->  d = atan(cho / vao * tan(a))   (sign as [MB-TRIG] delta)

Usage: analyze_b1.py <out_dir> <session_dir> [<session_dir> ...]
Writes curves.csv (one row per traversal frame), runs.csv (one row per trial) and prints a summary.
"""
import csv
import glob
import json
import math
import os
import re
import sys

THR = 1.5
LINE = re.compile(r"\[B1-MB\] run=(\d+) fc=(\d+) t=([\d.]+) mant=(\w+) trav=(\w+) st=(\d+) anim=([-\d.]+) prog=([-\d.]+) "
                  r"ss=([-\d.]+) vao=([-\d.]+) cho=([-\d.]+) ep=([-\d.]+) ey=([-\d.]+) v=([-\d.]+),([-\d.]+),([-\d.]+) z=([-\d.]+)")
TRIG = re.compile(r"\[MB-TRIG\] t=([\d.]+) travState=(\d+) raw=([\d.]+) anim=([\d.]+) delta=(!?)([-\d.]+) prev=([-\d.]+) "
                  r"thr=([\d.]+) gate=(\w+) -> (\d)")
RUI = re.compile(r"\[MB-RUI\] sweetSpotFrac travState=(\d+) thresh=([\d.]+) eyePitch=([-\d.]+) -> ([\d.]+)")


def delta_deg(cho, vao):
    if abs(vao) < 1e-9:
        return float("nan")
    return math.degrees(math.atan(cho / vao * math.tan(math.radians(THR))))


def load_session(sdir):
    man = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    sched = {t["run"]: t["schedule"] for t in man["trials"]}
    geo = next((g for g in man.get("argv", []) if str(g).startswith("h")), None)
    m = re.search(r"_h(\d+)", os.path.basename(sdir))
    height = int(m.group(1)) if m else None
    frames, trigs, ruis = {}, [], []
    for f in glob.glob(os.path.join(sdir, "platform", "logs", "client", "*", "*.log")):
        for ln in open(f, encoding="utf-8", errors="replace"):
            mm = LINE.search(ln)
            if mm:
                g = mm.groups()
                run = int(g[0])
                frames.setdefault(run, {})[int(g[1])] = dict(
                    fc=int(g[1]), t=float(g[2]), mant=g[3] == "true", trav=g[4] == "true", st=int(g[5]), anim=float(g[6]),
                    prog=float(g[7]), ss=float(g[8]), vao=float(g[9]), cho=float(g[10]), ep=float(g[11]), ey=float(g[12]),
                    vx=float(g[13]), vy=float(g[14]), vz=float(g[15]), z=float(g[16]))
                continue
            mm = TRIG.search(ln)
            if mm:
                g = mm.groups()
                trigs.append(dict(t=float(g[0]), trav=int(g[1]), raw=float(g[2]), anim=float(g[3]), nocam=g[4] == "!",
                                  delta=float(g[5]), prev=float(g[6]), gate=g[8], state=int(g[9])))
                continue
            mm = RUI.search(ln)
            if mm:
                g = mm.groups()
                ruis.append(dict(trav=int(g[0]), eye=float(g[2]), frac=float(g[3])))
    return dict(dir=sdir, height=height, sched=sched, frames=frames, trigs=trigs, ruis=ruis)


def analyse_run(sess, run):
    fr = [sess["frames"][run][k] for k in sorted(sess["frames"][run])]
    mant = [f for f in fr if f["mant"]]
    if not mant:
        return None, []
    i0 = fr.index(mant[0])
    # the first mantle block only
    block = []
    for f in fr[i0:]:
        if not f["mant"]:
            break
        block.append(f)
    after = fr[i0 + len(block):]
    t0, t1 = block[0]["t"], block[-1]["t"]
    dt = (t1 - t0) / max(1, len(block) - 1)
    dur = t1 - t0 + dt
    rows = []
    prev = None
    win = []
    for f in block:
        d = delta_deg(f["cho"], f["vao"])
        # SDK gate (require_decreasing 1): 0 <= delta <= prev (positive lobe settling toward zero), |delta| < 1.5, anim > 0.5
        dec = prev is not None and 0 <= d <= prev + 1e-9
        ok = d < THR and f["anim"] > 0.5 and dec
        rows.append(dict(t=f["t"] - t0, rem=t1 + dt - f["t"], anim=f["anim"], prog=f["prog"], delta=d, ok=ok, st=f["st"], ep=f["ep"]))
        if ok:
            win.append(rows[-1])
        prev = d
    peak = max(rows, key=lambda r: abs(r["delta"]))
    ex = next((f for f in after if abs(f["vx"]) + abs(f["vy"]) + abs(f["vz"]) > 1), None)
    sched = sess["sched"].get(run, "?")
    res = dict(run=run, schedule=sched, height=sess["height"], frames=len(block), duration=round(dur, 4), dt=round(dt, 5),
               ss=block[-1]["ss"], peak_delta=round(peak["delta"], 3), peak_anim=round(peak["anim"], 3),
               win_open_anim=round(win[0]["anim"], 4) if win else None, win_open_rem=round(win[0]["rem"], 4) if win else None,
               win_frames=len(win), final_state=after[0]["st"] if after else block[-1]["st"],
               exit_vh=round(math.hypot(ex["vx"], ex["vy"]), 2) if ex else None, exit_vz=round(ex["vz"], 2) if ex else None,
               start_pitch=block[0]["ep"], end_pitch=block[-1]["ep"])
    return res, rows


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    runs, curves, trigs, ruis = [], [], [], []
    for sdir in sys.argv[2:]:
        s = load_session(sdir)
        for run in sorted(s["frames"]):
            r, rows = analyse_run(s, run)
            if not r:
                continue
            runs.append(r)
            for row in rows:
                curves.append(dict(run=run, schedule=r["schedule"], height=r["height"], **{k: (round(v, 5) if isinstance(v, float) else v)
                                                                                          for k, v in row.items()}))
        for tr in s["trigs"]:
            trigs.append(dict(height=s["height"], **tr))
        for ru in s["ruis"]:
            ruis.append(dict(height=s["height"], **ru))
    for name, rows in (("runs.csv", runs), ("curves.csv", curves), ("trig.csv", trigs), ("rui.csv", ruis)):
        if rows:
            with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
    print("runs", len(runs), "frames", len(curves), "trig", len(trigs), "rui", len(ruis))
    for r in runs:
        r = {k: ("-" if v is None else v) for k, v in r.items()}
        print("{height!s:>4} {schedule:<24} T={duration:.3f} n={frames:>3} peak={peak_delta!s:>6} @{peak_anim!s:<5} open_anim={win_open_anim} "
              "open_rem={win_open_rem} wf={win_frames} st={final_state} exit={exit_vh}/{exit_vz} pitch {start_pitch}->{end_pitch}".format(**r))


if __name__ == "__main__":
    main()
