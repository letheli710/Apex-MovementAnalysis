"""F4: R5 camera sessions (C3 drops / jump landing / slides, N6 / N10 sprint turns; F7: N6 / N12 grapple) as hsdmove-trial/2 folders plus
the R5 camera per frame.

Usage: camera_to_trial.py <out_dir> <session_dir> [<session_dir> ...]
  <session_dir>  a raw local session with the HSD.MoveDiag camera tokens (C3-CAPTURE §0), e.g. research/phase2-local/data/20261023_221239_C3_camera
Per trial: the climb_to_trial.py folder (trial.json + samples.csv: the client usercmds Unity replays) and camera.csv, one row per client
frame in the trial's time span, in the trial's own time (row t):
  pitch, yaw, roll  camera angles minus the aim angles (cang - eang, Source degrees: pitch + = down, roll + = bank right) = what the camera adds
  eye               eye height above the origin (epos z - origin z)
  fov               the frame's vertical FOV divided by the trial's first-frame FOV (the scale the camera applies)
  ground, slide     the frame's flags
Drops (c3_drop*) are different: R5 lands before the client labels the trial (C3-CAPTURE §0), so the command window starts after the
landing. A drop has no input, so it is written as a synthetic trial instead: rest at floor + H (crouch held for _duck), no other input,
2.0 s after the landing; its camera.csv holds R5's frames from 0.3 s before to 1.5 s after the landing found in time order (as
c3_analysis.py does), with t shifted so R5's landing is at the synthetic trial's free-fall landing time. trial.json says
"camera_align": "landing" (the comparison also aligns on the landing).
Raw logs stay local; the output folders are derived data and are not committed.
stdlib only.
"""
import csv
import glob
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rea-native", "camera"))
import climb_to_trial as C  # noqa: E402
import c3_analysis as A  # noqa: E402

COLS = ["t", "pitch", "yaw", "roll", "eye", "fov", "ground", "slide"]
G = 750.0
DT = 1 / 120


def cam_row(r, t, fov0):
    return [round(t, 6), round(r["cang"][0] - r["eang"][0], 4), round(wrap(r["cang"][1] - r["eang"][1]), 4),
            round(r["cang"][2], 4), round(r["epos"][2] - r["o"][2], 3), round(r["fov"] / fov0, 5), r["ground"], r["slide"]]


def landing_cmds(session):
    """R5's landing commands of fast falls (client first-time MOVE-TRACE: airborne before, |vz| > 250 before, vz 0 after), in time order.
    The landing view kick is seeded with MD5_PseudoRandom(this command number) (F6 K-1 / K-2)."""
    seen, out = set(), []
    for r in C.L._parse_mt(session, "client", lambda plat, cmd: True):
        if r["cmd"] in seen:
            continue
        seen.add(r["cmd"])
        if not r["ground"] and r["vz"] < -250 and abs(r["pvz"]) < 1e-3:
            out.append(r["cmd"])
    return out


def drops(session, out_dir, frames, runner, floor):
    """One synthetic trial per R5 drop landing (see the module doc). Its command numbers are shifted so that the landing row carries R5's
    landing command number (the kick seed); every fast-fall landing of the session is matched in time order."""
    names = {str(t["run"]): t["schedule"] for t in runner["trials"] if t.get("ok") and not t.get("warmup")}
    label = runner.get("label", os.path.basename(session))
    lands, li = landing_cmds(session), 0
    out = []
    for i in range(1, len(frames)):
        p, q = frames[i - 1], frames[i]
        if not (p["ground"] == 0 and q["ground"] == 1 and p["vel_z"] < -250):
            continue
        land_cmd = lands[li] if li < len(lands) else None
        li += 1
        run = next((r["run"] for r in frames[i:i + 400] if names.get(r["run"], "").startswith("c3_drop")), None)
        if run is None or any(o["run"] == run for o in out):
            continue
        sched = names[run]
        h = int(sched.split("drop")[1].split("_")[0])
        duck = sched.endswith("_duck")
        t_land = (2 * h / G) ** 0.5                                   # free fall from rest (the half-step gravity lands within a command)
        n = int(round((t_land + 2.0) / DT))
        k_land = next(k for k in range(n) if floor + h - 0.5 * G * ((k + 1) * DT) ** 2 <= floor)
        cmd0 = (land_cmd - k_land) if land_cmd is not None else 1000
        tid = f"{label}_{sched}_r{run}"
        od = os.path.join(out_dir, tid)
        os.makedirs(od, exist_ok=True)
        man = {"contract": "hsdmove-trial/2", "trial_id": tid, "source": "r5flowstate", "experiment": label, "recorded_side": "cl",
               "producer": "research/feel/camera_to_trial.py: synthetic drop (no input) for the R5 drop landing of run " + run,
               "space": {"axes": "source_zup_righthanded", "length_unit": "u", "meters_per_unit": 0.0254, "angle_unit": "deg"},
               "initial_state": {"cmd": cmd0, "pos": [p["o"][0], p["o"][1], floor + h], "vel": [0.0, 0.0, 0.0], "grounded": 0,
                                 "angles": {"pitch": 0.0, "yaw": 0.0}, "buttons_held": 4 if duck else 0},
               "world": {"floor_z": floor}, "schedule": sched, "session": label, "camera_align": "landing",
               "r5_land_vz": p["vel_z"], "drop_height": h, "r5_land_cmd": land_cmd}
        json.dump(man, open(os.path.join(od, "trial.json"), "w", encoding="utf-8"), indent=1)
        with open(os.path.join(od, "samples.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, C.COLS)
            w.writeheader()
            for k in range(n):
                t = (k + 1) * DT
                z = max(floor, floor + h - 0.5 * G * t * t)
                w.writerow({"step": k, "t": round(t, 6), "dt": round(DT, 6), "cmd": cmd0 + k, "n_cmds": 1, "in_fwd": 0, "in_right": 0,
                            "in_yaw": 0.0, "in_pitch": 0.0, "in_jump": 0, "in_duck": int(duck), "in_sprint": 0, "buttons": 4 if duck else 0,
                            "cmd_fwd": 0, "cmd_side": 0, "movescale": 1.15, "maxspeed": 199.525, "pressed": "", "released": "",
                            "pos_x": p["o"][0], "pos_y": p["o"][1], "pos_z": round(z, 3), "vel_x": 0, "vel_y": 0,
                            "vel_z": 0 if z <= floor else round(-G * t, 3), "grounded": int(z <= floor), "sliding": 0, "crouched": int(duck),
                            "sprinting": 0, "state": "none", "events": ""})
        t0 = p["t"]
        fr = [r for r in frames if t0 - 0.3 <= r["t"] <= t0 + 1.5]
        fov0 = fr[0]["fov"] or 1.0
        with open(os.path.join(od, "camera.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(COLS)
            for r in fr:
                w.writerow(cam_row(r, r["t"] - t0 + t_land, fov0))
        out.append({"run": run, "trial": tid})
    print(f"  {len(out)} drop landings as synthetic trials ({li} fast-fall landings in the frames, {len(lands)} in MOVE-TRACE)")
    return [o["trial"] for o in out]


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


# The zipline of the m9zd_* schedules (phase2-local/tools/hsd_trial.py M9_ROPES "r130": y, x0, h0 above the floor, x1, h1)
ROPE_R130 = (6500.0, -14600.0, 130.0, -13000.0, 130.0)

C.L.INCLUDE_UNSCORED = True   # the C3 slide trials failed the fps check (107–116 fps) but their commands are complete (C3-CAPTURE §0)


USE = 0x20


def restore_use(trial_dir, floor):
    """The N10_zip usercmd log has no Use bit although R5 mounts the rope (the N6 rides show Use one command before the lift): put it back
    on the command before the first lift-off from the floor without a jump, so the replayed body grabs the rope too."""
    path = os.path.join(trial_dir, "samples.csv")
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or any(int(r["buttons"]) & USE for r in rows):
        return
    k = next((i for i in range(1, len(rows)) if float(rows[i]["pos_z"]) > floor + 1 and float(rows[i - 1]["pos_z"]) <= floor + 1
              and not int(rows[i]["in_jump"]) and not int(rows[i - 1]["in_jump"])), None)
    if k is None:
        return
    rows[k - 1]["buttons"] = str(int(rows[k - 1]["buttons"]) | USE)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


GRC = re.compile(r"([A-Za-z_]+)=(\S+)")


def grapple_hooks(session):
    """F7: the client [M10-GRC] lines (game time t, attached flag, hook entity position) of a grapple session, in time order."""
    out = []
    for f in glob.glob(os.path.join(session, "platform", "logs", "client", "*", "*.log")):
        for line in open(f, encoding="utf-8", errors="replace"):
            if "[M10-GRC]" in line:
                k = dict(GRC.findall(line))
                if k.get("att") == "true" and "t" in k and "hook" in k:
                    out.append((float(k["t"]), [float(x) for x in k["hook"].split(",")]))
    return sorted(out)


def add_hooks(man, hooks, t_end):
    """F7: the grapple trials (m10_g_*, n12_*): Pathfinder's kit and the hook points R5 attached at in the trial's span (to 1 u), which
    the Unity replay's grapple hits instead of the rock it does not have (CameraFeelReplay RecordedHookSurface)."""
    t0 = man["t0_game"]
    pts = []
    for t, h in hooks:
        if t0 <= t <= t0 + t_end and not any(max(abs(a - b) for a, b in zip(h, p)) < 1.0 for p in pts):
            pts.append(h)
    man["world"]["legend"] = "pathfinder"
    man["world"]["hooks"] = pts
    return len(pts)


def convert(session, out_dir):
    written = C.convert(session, out_dir)
    hooks = grapple_hooks(session)
    frames = sorted((r for v in A.load(session).values() for r in v if r["cang"] and r["eang"] and r["epos"] and r["o"]), key=lambda r: r["t"])
    runner = json.load(open(os.path.join(session, "runner.json"), encoding="utf-8"))
    for tid in [w for w in written if "_c3_drop" in w]:               # the post-landing windows: replaced by the synthetic drops
        shutil.rmtree(os.path.join(out_dir, tid))
    written = [w for w in written if "_c3_drop" not in w]
    drops(session, out_dir, frames, runner, runner["origin"][2])
    n_ok = 0
    for tid in written:
        d = os.path.join(out_dir, tid)
        man = json.load(open(os.path.join(d, "trial.json"), encoding="utf-8"))
        if man.get("schedule", "").startswith("m9zd"):                 # the rope for the Unity world (FeelReplay.World rails)
            y, x0, h0, x1, h1 = ROPE_R130
            floor = man["world"]["floor_z"]
            man["world"]["rails"] = [{"name": "r130", "attach_radius": 48, "points": [[x0, y, floor + h0], [x1, y, floor + h1]]}]
            json.dump(man, open(os.path.join(d, "trial.json"), "w", encoding="utf-8"), indent=1)
            restore_use(d, floor)
        with open(os.path.join(d, "samples.csv"), encoding="utf-8") as fh:
            t_end = float(list(csv.DictReader(fh))[-1]["t"])
        if man.get("schedule", "").startswith(("m10_g_", "n12_")) and hooks:
            add_hooks(man, hooks, t_end)
            json.dump(man, open(os.path.join(d, "trial.json"), "w", encoding="utf-8"), indent=1)
        t0 = man["t0_game"]
        fr = [r for r in frames if t0 <= r["t"] <= t0 + t_end + 1e-6]
        if not fr:
            continue
        fov0 = fr[0]["fov"] or 1.0
        with open(os.path.join(d, "camera.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(COLS)
            for r in fr:
                w.writerow(cam_row(r, r["t"] - t0, fov0))
        n_ok += 1
    print(f"  camera.csv for {n_ok} / {len(written)} trials")
    return written


def main():
    out = sys.argv[1]
    for s in sys.argv[2:]:
        convert(s, out)


if __name__ == "__main__":
    main()
