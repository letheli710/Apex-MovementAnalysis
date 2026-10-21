#!/usr/bin/env python3
"""Export the M4 replay trials (hsdmove-trial/2) used by the Unity primitives check.

Two valid trials (ok, not warm-up) per condition. Sessions run with --no-census take their
class-var parameters from the census session of the same legend and build (the parameters block
must never be empty: an M3 lesson). Writes research/phase2-local/m4/trials/<schedule>_<run>/.

  py -3 export_trials.py
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DATA = os.path.join(REPO, "research", "phase2-local", "data")
TEL = os.path.join(REPO, "research", "phase2-prep", "tools", "hsd_tel.py")
OUT = os.path.join(HERE, "trials")

# session label -> (census session label, schedules to export)
PLAN = {
    "M4_octane": ("M4_octane", ["m4_ctrl_sprint", "m4_stim_sprint", "m4_stim_walk", "m4_stim_air", "m4_pad_sprint",
                                "m4_pad_crouch"]),
    "M4_octane_rerun": ("M4_octane", ["m4_ctrl_air", "m4_pad_walk"]),
    "M4_horizon": ("M4_horizon", ["e4_stand", "e2_noinput"]),
    "M4_horizon_lift2": ("M4_horizon", ["m4_lift_ride", "m4_lift_jumpout", "m4_lift_strafe"]),
    "M4_pathfinder": ("M4_pathfinder", ["m4_grapple_hold", "m4_grapple_fwd"]),
    "M4_pathfinder2": ("M4_pathfinder", ["m4_grapple_near", "m4_grapple_far"]),
    "M4_valkyrie": ("M4_valkyrie", ["m4_valk_ctrl", "m4_valk_jets"]),
    "M4_revenant": ("M4_revenant", ["m4_pounce_c0"]),
    "M4_revenant_rerun": ("M4_revenant", ["m4_pounce_c13"]),
}


def session(label):
    hits = sorted(d for d in glob.glob(os.path.join(DATA, "*_" + label)) if os.path.isdir(d))
    if not hits:
        raise SystemExit("no session " + label)
    return hits[-1]


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for label, (census_label, schedules) in PLAN.items():
        sdir = session(label)
        census = os.path.join(session(census_label), "report", "census.csv")
        with open(os.path.join(sdir, "runner.json"), encoding="utf-8") as fh:
            runner = json.load(fh)
        for sched in schedules:
            runs = ["r%d" % t["run"] for t in runner["trials"] if t["ok"] and not t["warmup"] and t["schedule"] == sched]
            kept = 0
            for run in runs:
                if kept == 2:
                    break
                out = os.path.join(OUT, f"{sched}_{run}")
                note = (f"M4 {label}; schedule {sched} @120 fps; kit equipped; parameters from the {census_label} census "
                        f"(same build and legend)")
                r = subprocess.run([sys.executable, TEL, "export-contract", os.path.join(sdir, "platform", "logs"),
                                    "--run", run, "--experiment", "M4_" + sched, "--trial-id", f"M4_{sched}_{run}",
                                    "--params", census, "--course-note", note, "-o", out],
                                   capture_output=True, text=True, stdin=subprocess.DEVNULL)
                ok = r.returncode == 0
                chk = subprocess.run([sys.executable, TEL, "check-contract", out], capture_output=True, text=True,
                                     stdin=subprocess.DEVNULL).stdout.strip().splitlines()[-1:] if ok else ["export failed"]
                clean = ok and bool(chk) and chk[0].startswith("0 problem")
                if not clean:
                    # strict contract check failed (e.g. a usercmd missing from the client trace): do not use it,
                    # move the export aside and take the next valid trial of the same condition
                    if os.path.isdir(out):
                        os.replace(out, out + "_REJECTED")
                print(f"{sched:20s} {run:6s} {'ok' if clean else 'SKIP'}  {chk[0] if chk else ''}")
                n += clean
                kept += clean
    print(n, "trials exported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
