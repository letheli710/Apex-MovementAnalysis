"""GN: the inputs of the grapple feel comparison with the R5 scene (N13 S-1 / S-2).

Usage: make_gn_inputs.py [<camera trials dir>]
  1. writes scenarios_gn.json next to this script: phase2-local/m4/unity/scenarios.json (unchanged, the replay motor's file) with a
     feel_rock block on the two grapple schedules (FeelReplay.AddRock): the M3 rock face that stops the body, tilted back 1.86 deg
     (N13 sec. 4.1), and the hook on a parallel plane through the recorded d400 hook (N13 sec. 3.3; GN session 22001 [M10-GRC]).
  2. with a camera trials dir (feel/camera_to_trial.py output): adds world.boxes to the N6 low-speed ceiling trials (m10_g_n6ceil*):
     the ceiling (the M10 Octane rock pitched 90 deg, underside floor + 80, ~450 u along x centred at x -13800; hsd_trial.py _N6_CEIL)
     and the 33 u ledge (the M3 rock sunk, face x -13706; N6-MEASURE sec. 1.3 round 4). Approximate boxes [inf].
stdlib only.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(REPO, "research", "phase2-local", "m4", "unity", "scenarios.json")
FLOOR = 294.92

ROCK = {
    "face": [-13704.59, 6500.0, 425.69],     # body stopped at origin x -13720.59, z 425.69 (hull 16): GN 22001, N13 d400 -13720.6
    "hook": [-13697.93, 6500.45, 436.27],    # [M10-GRC] hook of GN 22001 (N13 d400: -13697.96)
    "tilt_deg": 1.86,                        # N13 sec. 4.1: face normal z 0.0324 (vx 575 -> 6.5, vz +12 at the wall hit)
    "box": {"min": [-13706.0, 6380.0, FLOOR], "max": [-13506.0, 6620.0, FLOOR + 232.0]},
    "source": "N13 S-1 / S-2: rock face x -13704.6 at the body (tilted 1.86 deg), hook on a parallel plane through the recorded hook "
              "(x -13697.9, 6-7 u behind the face that stops the body); research/rea-native/gn/make_gn_inputs.py",
}

CEIL_BOXES = [
    {"min": [-14025.0, 6350.0, FLOOR + 80.0], "max": [-13575.0, 6650.0, FLOOR + 300.0], "name": "n6_ceiling"},
    {"min": [-13706.0, 6380.0, FLOOR], "max": [-13506.0, 6620.0, FLOOR + 33.0], "name": "n6_ledge_h20"},
]


def main():
    with open(SRC, encoding="utf-8") as f:
        sc = json.load(f)
    for k in ("m4_grapple_hold", "m4_grapple_near"):
        sc["schedules"][k]["feel_rock"] = ROCK
    sc["description"] = sc.get("description", "") + " GN: grapple schedules carry feel_rock (the R5 rock for the game bodies)."
    out = os.path.join(HERE, "scenarios_gn.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("wrote", out)
    if len(sys.argv) > 1:
        root = sys.argv[1]
        n = 0
        for d in sorted(os.listdir(root)):
            if "m10_g_n6ceil" not in d:
                continue
            p = os.path.join(root, d, "trial.json")
            with open(p, encoding="utf-8") as f:
                man = json.load(f)
            man.setdefault("world", {})["boxes"] = CEIL_BOXES
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                json.dump(man, f, indent=1)
            n += 1
        print("ceiling boxes added to", n, "trials")


if __name__ == "__main__":
    main()
