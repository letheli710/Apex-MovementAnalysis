"""Re-run the M5 short-range evaluation in Unity (batch) and summarise it (stdlib only).

    python run_eval.py [--unity <Unity.exe>] [--project <HSD-Unity>] [--configs baseline,reference] [--skip-unity]

For each config, Unity runs HSD.R5Replay.Editor.ShortRangeBatch.Run over every base-movement trial:
  ../../m1/trials/*, ../../m2/trials/*, ../../m3/trials/*, and the M4 trials that are not grapple and not *_REJECTED
  (../../m4/trials/*, with the M4 scenario sidecar ../../m4/unity/scenarios.json for the legend kits),
and writes windows_<config>.csv next to this file. Then summarize.py builds the distribution tables (RESULTS.md).
Defaults: Unity 6000.6.5f1 in the standard Hub folder (or $UNITY_EXE), the HSD-Unity project next to this repository
(or $HSD_UNITY). Every path handed to Unity is absolute (relative ones resolve against the Unity project).
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE = os.path.normpath(os.path.join(HERE, "..", ".."))
REPO = os.path.normpath(os.path.join(PHASE, "..", ".."))
DEFAULT_UNITY = os.environ.get("UNITY_EXE", r"C:\Program Files\Unity\Hub\Editor\6000.6.5f1\Editor\Unity.exe")
DEFAULT_PROJECT = os.environ.get("HSD_UNITY", os.path.normpath(os.path.join(REPO, "..", "HSD-Unity")))


def trial_dirs():
    out = []
    for m in ("m1", "m2", "m3"):
        out += sorted(d for d in glob.glob(os.path.join(PHASE, m, "trials", "*")) if os.path.isdir(d))
    for d in sorted(glob.glob(os.path.join(PHASE, "m4", "trials", "*"))):
        name = os.path.basename(d)
        if os.path.isdir(d) and not name.endswith("_REJECTED") and "grapple" not in name:
            out.append(d)
    return [os.path.abspath(d) for d in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unity", default=DEFAULT_UNITY)
    ap.add_argument("--project", default=DEFAULT_PROJECT)
    ap.add_argument("--configs", default="baseline,reference")
    ap.add_argument("--skip-unity", action="store_true", help="only summarise the existing windows_*.csv")
    a = ap.parse_args()
    trials = trial_dirs()
    print(f"{len(trials)} trials")
    if not a.skip_unity:
        for cfg in a.configs.split(","):
            log = os.path.join(tempfile.gettempdir(), f"hsd_shortrange_{cfg}.log")
            cmd = [a.unity, "-batchmode", "-nographics", "-projectPath", os.path.abspath(a.project),
                   "-executeMethod", "HSD.R5Replay.Editor.ShortRangeBatch.Run", "-out", HERE, "-config", cfg,
                   "-scenarios", os.path.join(PHASE, "m4", "unity", "scenarios.json"), "-logFile", log]
            for t in trials:
                cmd += ["-trial", t]
            print(f"Unity: {cfg} ...")
            r = subprocess.run(cmd)
            if r.returncode != 0:
                print(f"Unity exit code {r.returncode} for {cfg}; log: {log}")
                return r.returncode
    return subprocess.run([sys.executable, os.path.join(HERE, "summarize.py")]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
