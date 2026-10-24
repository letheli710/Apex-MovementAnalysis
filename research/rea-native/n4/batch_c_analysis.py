"""N4-C analysis: over-cap hop (J-04), slide boost cooldown chain (S-02), slide steering (G-12).

  py -3 batch_c_analysis.py <session folder> [--json out.json]

Per trial, from the client first-time MOVE-TRACE commands (M2 loader):
  n4c_hop_*         the take-off after the first landing: pre speed h, post speed,
                    native prediction max(msc*sprintspeed, h - 100), replay motor min(h, 299)
  n4c_slidechain*   every slide start: speed gain on that command (boost about +160, else ~0)
  n4c_slidesteer    lateral speed (perpendicular to the slide-start direction) over time while
                    sliding with D only; native slope slideAccel*msc = 57.5 u/s^2
Standard library only.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-local", "m2", "ground"))
import ground_analysis as ga  # noqa: E402

CAP = 299.0           # msc * sprintspeed (Gibraltar, msc 1.15)
SKIP_REDUCE = 100.0   # skip_speed_reduce
SLIDE_ACCEL = 57.5    # slideAccel 50 * msc 1.15


def hop(recs):
    landed = False
    for prev, cur in zip(recs, recs[1:]):
        if prev["ground"] == 0 and cur["ground"] == 1:
            landed = True
        elif landed and prev["ground"] == 1 and cur["ground"] == 0:
            # the jump runs on prev (the last grounded command): its pre speed is the hop entry speed
            h = prev["s0"]
            return {"pre": round(h, 3), "post": round(prev["s1"], 3), "native": round(max(CAP, h - SKIP_REDUCE), 3),
                    "motor": round(min(h, CAP), 3), "slide_at_takeoff": prev["slide"]}
    return None


def slide_starts(recs):
    out = []
    t = 0.0
    for prev, cur in zip(recs, recs[1:]):
        t += cur["dt"] or 0.0
        if prev["slide"] == 0 and cur["slide"] == 1:
            out.append({"t": round(t, 3), "pre": round(cur["s0"], 2), "post": round(cur["s1"], 2),
                        "gain": round(cur["s1"] - cur["s0"], 2)})
    return out


def steer(recs):
    start = next((i for i, (a, b) in enumerate(zip(recs, recs[1:])) if a["slide"] == 0 and b["slide"] == 1), None)
    if start is None:
        return None
    r0 = recs[start + 1]
    ux, uy = r0["vx1"], r0["vy1"]
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    px, py = uy, -ux                      # right-hand perpendicular (D side)
    pts, t = [], 0.0
    for r in recs[start + 2:]:
        if r["slide"] != 1 or r["ground"] != 1 or not (r["b"] & ga.BUTTON_BITS["MOVERIGHT"]):
            continue
        t += r["dt"] or 0.0
        pts.append((t, r["vx1"] * px + r["vy1"] * py, r["s1"]))
    if len(pts) < 5:
        return None
    mt = sum(p[0] for p in pts) / len(pts)
    ml = sum(p[1] for p in pts) / len(pts)
    slope = sum((p[0] - mt) * (p[1] - ml) for p in pts) / sum((p[0] - mt) ** 2 for p in pts)
    return {"n": len(pts), "lateral_slope": round(slope, 2), "lateral_end": round(pts[-1][1], 2),
            "speed_end": round(pts[-1][2], 2), "t_end": round(pts[-1][0], 3), "native_slope": SLIDE_ACCEL}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    runner, mt, frames_by_run, frames_by_seq, _ = ga.load_session(a.session)
    out = []
    for t in runner.get("trials", []):
        name, run = t.get("schedule", ""), f"r{t.get('run')}"
        if not name.startswith("n4c_") or t.get("warmup") or not t.get("ok"):
            continue
        cmds, frames = mt.get(run, []), frames_by_run.get(run, [])
        recs, _ = ga.build_trial(t, cmds, frames, frames_by_seq) if cmds and frames else (None, None)
        if not recs:
            print(name, run, "no data")
            continue
        recs = [r for r in recs if r["dt"] is not None]
        if name.startswith("n4c_hop"):
            res = hop(recs)
        elif name.startswith("n4c_slidechain"):
            res = slide_starts(recs)
        else:
            res = steer(recs)
        out.append({"schedule": name, "run": run, "result": res})
        print(name, run, res)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
