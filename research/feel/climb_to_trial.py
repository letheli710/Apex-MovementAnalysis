"""F2: turn raw R5 climb / mantle / superglide sessions (M6-A2, M8 r_sg) into hsdmove-trial/2 folders that FeelBatch replays.

Usage: climb_to_trial.py <out_dir> <session_dir> [<session_dir> ...]
  <session_dir>  a raw local session (runner.json + platform/logs), e.g. research/phase2-local/data/20261022_045433_M8_sg_h120
Per scored trial: <out_dir>/<trial_id>/trial.json + samples.csv, one row per client first-time usercmd (a2_load), post-state of the
command. Extra column `state` (none / climb / mantle / hang from [HSD-STATE]) and events TAKEOFF / LAND / CLIMB_START / MANTLE_START /
MANTLE_END. trial.json carries a `world` block for the Unity side: floor_z, and the wall as a box (face_x, top_z, y_min, y_max, depth).
  - top_z: the median origin z standing on the wall top after a mantle in this session (exit z = floor + H + 5.92, A2 §3)
  - face_x: −13704.5, the A2 face line (A2 §3: contact origin −13720.5 = face − 16); checked against each session's contact x
  - depth: 208, from where R5 walks off the back of the top (origin −13481 = edge + 16 hull)
Raw logs stay local; the output folders are derived data and are not committed.
stdlib only.
"""
import csv
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "phase2-local", "m6", "a2_climb"))
import a2_load as L  # noqa: E402

FACE_X = -13704.5
WALL_Y = (6500 - 220, 6500 + 220)
WALL_DEPTH = 208                                       # R5 walks off the top at origin x -13481 (median, 108 runs) = edge + 16
IN_JUMP, IN_DUCK = 0x2, 0x4
IN_SPRINT = (1 << 15) | (1 << 17)
COLS = ["step", "t", "dt", "cmd", "n_cmds", "in_fwd", "in_right", "in_yaw", "in_pitch", "in_jump", "in_duck", "in_sprint", "buttons",
        "cmd_fwd", "cmd_side", "movescale", "maxspeed", "pressed", "released", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z",
        "grounded", "sliding", "crouched", "sprinting", "state", "events"]


def state_at(states, t):
    """The [HSD-STATE] flags of the latest frame at or before game time t."""
    best = None
    for s in states:
        if s["t"] <= t + 1e-6:
            best = s
        else:
            break
    if not best:
        return "none"
    return "mantle" if best["mant"] else "hang" if best["hang"] else "climb" if best["trav"] else "none"


def fill_gaps(cmds, frames):
    """Neither side prints MOVE-TRACE during a traversal (the mantle is kinematic), so the command numbers jump by its length. Fill each
    gap of n commands with the next n client frames after the first one (which still shows the command before the gap): one command per
    frame at the client rate, inputs from the frame (in_jump / in_duck / in_fwd, ax_fwd / ax_right, yaw), state from the frame. Sprint
    and the side keys keep the previous command's buttons."""
    out = []
    for i, c in enumerate(cmds):
        out.append(c)
        if i + 1 >= len(cmds):
            break
        n = cmds[i + 1]["cmd"] - c["cmd"] - 1
        if n <= 0:
            continue
        g = [f for f in frames if f["plat"] is not None and c["plat"] < f["plat"] < cmds[i + 1]["plat"]][1:1 + n]
        if len(g) < n:
            return None                                          # a frame missing inside the gap: the commands cannot be lined up
        for k, f in enumerate(g):
            b = c["buttons"] & ~(IN_JUMP | IN_DUCK | 0x8)
            b |= (IN_JUMP if f["in_jump"] else 0) | (IN_DUCK if f["in_duck"] else 0) | (0x8 if f["in_fwd"] else 0)
            nxt = g[k + 1] if k + 1 < len(g) else f
            out.append({"cmd": c["cmd"] + 1 + k, "plat": f["plat"], "t": f["t"], "dt": f["ft"], "yaw": f["yaw"], "fwd": f["ax_fwd"],
                        "sidemove": f["ax_right"], "buttons": b, "msc": c["msc"], "maxspeed": c["maxspeed"], "sprint": c["sprint"],
                        "ground": f["ground"], "slide": f["slide"], "duck": f["crouch"],
                        "ox": f["ox"], "oy": f["oy"], "oz": f["oz"], "vx": f["vx"], "vy": f["vy"], "vz": f["vz"],
                        "pox": nxt["ox"], "poy": nxt["oy"], "poz": nxt["oz"], "pvx": nxt["vx"], "pvy": nxt["vy"], "pvz": nxt["vz"], "gap": True})
    return out


def relabel(rows, floor):
    """Events from the ground flag and the state, once the rows are complete. (R5 sets its traversal flag a few commands after the wall
    contact, while the origin already moves along the path; the comparison therefore uses the mantle END, not its start.)"""
    for i, r in enumerate(rows):
        ev = []
        if i > 0:
            p = rows[i - 1]
            if p["grounded"] and not r["grounded"]:
                ev.append("TAKEOFF")
            if not p["grounded"] and r["grounded"]:
                ev.append("LAND")
            if r["state"] != p["state"]:
                if r["state"] == "climb":
                    ev.append("CLIMB_START")
                if r["state"] == "mantle":
                    ev.append("MANTLE_START")
                if p["state"] == "mantle":
                    ev.append("MANTLE_END")
        r["events"] = "|".join(ev)


def convert(session, out_dir):
    d = L.load(session)
    label = d["runner"].get("label", os.path.basename(session))
    floor = d["runner"]["origin"][2]
    tops, contacts, written, skipped = [], [], [], 0
    rows_by = {}
    for tr in d["trials"]:
        cmds = fill_gaps(tr["cmds"], tr["frames"])
        if cmds is None:
            skipped += 1
            continue
        if len(cmds) < 50:
            continue
        dts = [c["dt"] for c in cmds if c["dt"]]
        dflt = statistics.median(dts) if dts else 1 / 120
        t0 = next((c["t"] - c["dt"] for c in cmds if c["t"] is not None and c["dt"]), None)
        if t0 is None:
            continue
        states = sorted(tr["states"], key=lambda s: s["t"])
        rows, t, prev_b, prev_state, prev_g = [], 0.0, 0, "none", None
        for i, c in enumerate(cmds):
            dt = c["dt"] or dflt
            t += dt
            nxt = cmds[i + 1] if i + 1 < len(cmds) else c
            g = nxt["ground"] if i + 1 < len(cmds) else c["ground"]
            st = state_at(states, (c["t"] if c["t"] is not None else t0 + t))
            if st == "mantle":
                g = 0                                            # the traversal is kinematic: airborne, as the Unity mantle (R5 frames say ground)
            b = c["buttons"]
            ev = []
            if prev_g is not None and prev_g and not g:
                ev.append("TAKEOFF")
            if prev_g is not None and not prev_g and g:
                ev.append("LAND")
            if st != prev_state:
                if st == "climb":
                    ev.append("CLIMB_START")
                if st == "mantle":
                    ev.append("MANTLE_START")
                if prev_state == "mantle":
                    ev.append("MANTLE_END")
            pressed = [n for bit, n in ((IN_JUMP, "JUMP"), (IN_DUCK, "DUCK")) if b & bit and not prev_b & bit]
            rows.append({"step": i, "t": round(t, 6), "dt": round(dt, 6), "cmd": c["cmd"], "n_cmds": 1,
                         "in_fwd": c["fwd"], "in_right": c["sidemove"], "in_yaw": c.get("yaw") if c.get("yaw") is not None else (rows[-1]["in_yaw"] if rows else 0.0),
                         "in_pitch": 0.0, "in_jump": int(bool(b & IN_JUMP)), "in_duck": int(bool(b & IN_DUCK)), "in_sprint": int(bool(b & IN_SPRINT)),
                         "buttons": b, "cmd_fwd": c["fwd"], "cmd_side": c["sidemove"], "movescale": c["msc"], "maxspeed": c["maxspeed"],
                         "pressed": "|".join(pressed), "released": "",
                         "pos_x": c["pox"], "pos_y": c["poy"], "pos_z": c["poz"], "vel_x": c["pvx"], "vel_y": c["pvy"], "vel_z": c["pvz"],
                         "grounded": g, "sliding": nxt["slide"] if i + 1 < len(cmds) else c["slide"], "crouched": nxt["duck"] if i + 1 < len(cmds) else c["duck"],
                         "sprinting": c["sprint"], "state": st, "events": "|".join(ev)})
            if st in ("climb", "mantle") and prev_state == "none":
                contacts.append(c["ox"])
            if prev_state == "mantle" and st == "none" and g:
                tops.append(c["poz"])
            prev_b, prev_state, prev_g = b, st, g
        relabel(rows, floor)
        rows_by[tr["run"]] = (tr, rows, cmds)
    top = statistics.median(tops) if tops else None
    hm = re.search(r"_h(\d+)", label)
    if top is None and hm:
        top = floor + int(hm.group(1)) + 5.92                  # no mantle in this session (too low / too high): the A2 exit-z law
    for run, (tr, rows, cmds) in rows_by.items():
        sched = tr["schedule"] or "x"
        tid = f"{label}_{sched}_r{run}"
        od = os.path.join(out_dir, tid)
        os.makedirs(od, exist_ok=True)
        c0 = cmds[0]
        man = {"contract": "hsdmove-trial/2", "trial_id": tid, "source": "r5flowstate", "experiment": label, "recorded_side": "cl",
               "producer": "research/feel/climb_to_trial.py from a2_load (client first-time MOVE-TRACE usercmds)",
               "space": {"axes": "source_zup_righthanded", "length_unit": "u", "meters_per_unit": 0.0254, "angle_unit": "deg"},
               "initial_state": {"cmd": c0["cmd"], "pos": [c0["ox"], c0["oy"], c0["oz"]], "vel": [c0["vx"], c0["vy"], c0["vz"]],
                                 "grounded": c0["ground"], "angles": {"pitch": 0.0, "yaw": rows[0]["in_yaw"]}, "buttons_held": 0},
               "terrain": {"map": "mp_rr_canyonlands_staging_mu1", "course_note": "A2 wall prop on lane A"},
               "world": {"floor_z": floor, "wall": None if top is None else
                         {"face_x": FACE_X, "top_z": top, "y_min": WALL_Y[0], "y_max": WALL_Y[1], "depth": WALL_DEPTH}},
               "schedule": sched, "session": label}
        json.dump(man, open(os.path.join(od, "trial.json"), "w", encoding="utf-8"), indent=1)
        with open(os.path.join(od, "samples.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, COLS)
            w.writeheader()
            w.writerows(rows)
        written.append(tid)
    cx = statistics.median(contacts) if contacts else None
    print(f"{label}: {len(written)} trials ({skipped} skipped: frame missing in a traversal gap), top_z {top}, contact x median {cx} (face - 16 = {FACE_X - 16})")
    return written


def main():
    out = sys.argv[1]
    for s in sys.argv[2:]:
        convert(s, out)


if __name__ == "__main__":
    main()
