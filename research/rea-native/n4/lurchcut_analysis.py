"""N4-D lurch high-speed cutoff analysis (ledger L-10).

  py -3 lurchcut_analysis.py <session folder>

For each n4d_cut* trial: the airborne command with the D press edge. Prints the horizontal
speed before it, |dv_h| on that command and the heading change. Native expectation:
|dv_h| = 209.3 (lurch clamp) when h <= 1100, only AirAccelerate (a few u/s) above.
Standard library only.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-local", "m2", "ground"))
import ground_analysis as ga  # noqa: E402

RIGHT = ga.BUTTON_BITS["MOVERIGHT"]


def main(session):
    runner, mt, frames_by_run, frames_by_seq, _ = ga.load_session(session)
    for t in runner.get("trials", []):
        name, run = t.get("schedule", ""), f"r{t.get('run')}"
        if not name.startswith("n4d_cut") or t.get("warmup") or not t.get("ok"):
            continue
        cmds = mt.get(run, [])
        hit = None
        for a, b in zip(cmds, cmds[1:]):
            if b["ground"] == 0 and (b["buttons"] & RIGHT) and not (a["buttons"] & RIGHT):
                hit = b
                break
        if hit is None:
            print(name, run, "no airborne D press")
            continue
        h0 = math.hypot(hit["vx"], hit["vy"])
        dv = math.hypot(hit["pvx"] - hit["vx"], hit["pvy"] - hit["vy"])
        turn = math.degrees(math.atan2(hit["pvy"], hit["pvx"]) - math.atan2(hit["vy"], hit["vx"]))
        print(f"{name} {run}: h before {h0:.2f}  |dv_h| {dv:.2f}  heading change {turn:+.2f} deg")


if __name__ == "__main__":
    main(sys.argv[1])
