#!/usr/bin/env python3
"""R6: turn raw R5 slope sessions into hsdmove-trial/2 folders for the Unity slope harness (same layout as feel/climb_to_trial.py).

  py -3 slope_to_trial.py <out_dir> <session_dir> [<session_dir> ...]

Per scored trial: <out_dir>/<trial_id>/trial.json + samples.csv, one row per client first-time usercmd (a2_load), post-state of the
command. trial.json carries `world.slope_segments` (the lane's planar segments from tools/slope_geo.py) and `world.floor_z` (the lane's
lowest flat, ZB). Raw logs stay local; the output folders are derived data and are not committed. stdlib only.
"""
import csv
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slope_load as SL  # noqa: E402

IN_JUMP, IN_DUCK = 0x2, 0x4
IN_SPRINT = (1 << 15) | (1 << 17)
COLS = ["step", "t", "dt", "cmd", "n_cmds", "in_fwd", "in_right", "in_yaw", "in_pitch", "in_jump", "in_duck", "in_sprint", "buttons",
        "cmd_fwd", "cmd_side", "movescale", "maxspeed", "pressed", "released", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z",
        "grounded", "sliding", "crouched", "sprinting", "state", "events"]


def convert(session, out_dir):
    d = SL.L.load(session)
    label = d["runner"].get("label", os.path.basename(session))
    written = []
    for tr in d["trials"]:
        sched = tr["schedule"] or ""
        if not sched.startswith("r6_"):
            continue
        cmds = tr["cmds"]
        if len(cmds) < 50:
            continue
        lane = SL.lane_of(sched)
        frames = [f for f in tr["frames"] if f.get("yaw") is not None]
        yaw = statistics.median([f["yaw"] for f in frames[:20]]) if frames else 0.0
        dts = [c["dt"] for c in cmds if c.get("dt")]
        dflt = statistics.median(dts) if dts else 1 / 120
        rows, t, prev_b, prev_g = [], 0.0, 0, None
        for i, c in enumerate(cmds):
            dt = c.get("dt") or dflt
            t += dt
            nxt = cmds[i + 1] if i + 1 < len(cmds) else c
            g = nxt["ground"] if i + 1 < len(cmds) else c["ground"]
            b = c["buttons"]
            ev = []
            if prev_g is not None and prev_g and not g:
                ev.append("TAKEOFF")
            if prev_g is not None and not prev_g and g:
                ev.append("LAND")
            pressed = [n for bit, n in ((IN_JUMP, "JUMP"), (IN_DUCK, "DUCK")) if b & bit and not prev_b & bit]
            rows.append({"step": i, "t": round(t, 6), "dt": round(dt, 6), "cmd": c["cmd"], "n_cmds": 1,
                         "in_fwd": c["fwd"], "in_right": c["sidemove"], "in_yaw": yaw, "in_pitch": 0.0,
                         "in_jump": int(bool(b & IN_JUMP)), "in_duck": int(bool(b & IN_DUCK)), "in_sprint": int(bool(b & IN_SPRINT)),
                         "buttons": b, "cmd_fwd": c["fwd"], "cmd_side": c["sidemove"], "movescale": c["msc"], "maxspeed": c["maxspeed"],
                         "pressed": "|".join(pressed), "released": "",
                         "pos_x": c["pox"], "pos_y": c["poy"], "pos_z": c["poz"], "vel_x": c["pvx"], "vel_y": c["pvy"], "vel_z": c["pvz"],
                         "grounded": g, "sliding": nxt["slide"] if i + 1 < len(cmds) else c["slide"],
                         "crouched": nxt["duck"] if i + 1 < len(cmds) else c["duck"], "sprinting": c["sprint"], "state": "none",
                         "events": "|".join(ev)})
            prev_b, prev_g = b, g
        tid = f"{label}_{sched}_r{tr['run']}"
        od = os.path.join(out_dir, tid)
        os.makedirs(od, exist_ok=True)
        c0 = cmds[0]
        man = {"contract": "hsdmove-trial/2", "trial_id": tid, "source": "r5flowstate", "experiment": label, "recorded_side": "cl",
               "producer": "research/phase2-local/slope/slope_to_trial.py from a2_load (client first-time MOVE-TRACE usercmds)",
               "space": {"axes": "source_zup_righthanded", "length_unit": "u", "meters_per_unit": 0.0254, "angle_unit": "deg"},
               "initial_state": {"cmd": c0["cmd"], "pos": [c0["ox"], c0["oy"], c0["oz"]], "vel": [c0["vx"], c0["vy"], c0["vz"]],
                                 "grounded": c0["ground"], "angles": {"pitch": 0.0, "yaw": yaw}, "buttons_held": 0},
               "terrain": {"map": "mp_rr_canyonlands_staging_mu1", "course_note": "R6 slope lane %s (tools/slope_geo.py)" % lane},
               "world": {"floor_z": SL.G.ZB, "slope_lane": lane, "slope_segments": SL.G.segments(lane)},
               "schedule": sched, "session": label}
        json.dump(man, open(os.path.join(od, "trial.json"), "w", encoding="utf-8"), indent=1)
        with open(os.path.join(od, "samples.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, COLS)
            w.writeheader()
            w.writerows(rows)
        written.append(tid)
    print(f"{label}: {len(written)} trials")
    return written


def main():
    out = sys.argv[1]
    for s in sys.argv[2:]:
        convert(s, out)


if __name__ == "__main__":
    main()
