"""M-1 round 7 (R7): the hip axle, for the walk (Unity's B-沉 with the foot floor, HSD-Unity #75).

  blender.exe -b -P build_m1_r7.py -- r7          build R7: checks, joint test, renders to r7_final/, Titan_M1.blend / .fbx

Unity's walk replayed on the mesh (replay_walk_m1.py, joints.tsv): in the gait route's sprint the pelvis's own axle stub (y 0.40-0.58, r 0.17,
on the hip axis) meets the thigh's inner face when the thigh twists / swings out (Pelvis x Thigh 46 of 144 frames, turn 3-4 of 120; the
19 still poses never reach those angles). The stub is the hip joint itself: R7 ends it at y 0.50 and starts R6's hip axle piece there
(y 0.50-0.68, r 0.15, excluded against the thigh only), so the axle still reads as one, and the pelvis armour is still tested against the thigh.
build_m1_r6.py and build_m1_r5.py are not changed; this file imports them.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = [a if a != "r7" else "_r7" for a in sys.argv]       # build_m1_r6 runs its own main on "r6" only
import build_m1_r6 as R6  # noqa: E402
import build_m1_r5 as F  # noqa: E402

S = F.S
OUT = os.path.join(HERE, "r7_final")


def fix_hip_axle_r7(P):
    pieces = P["Pelvis"]["pieces"]
    # the axle stub is the pelvis's second piece (build_m1_final: merge(axle, mirror(axle)), frame, not bevelled)
    axle = F.cyl("y", (0, 2.85), 0.17, 0.40, 0.50, 24)
    pieces[1] = (F.merge(axle, F.mirror(axle)), "frame", False, "mid")
    a = F.ring_y([(0.50, 0.15), (0.68, 0.15)], 0.0, 2.85, 24)
    P["Hip_Axle_L"]["pieces"] = [(a, "frame", False, "detail")]
    P["Hip_Axle_R"]["pieces"] = [(F.mirror(a), "frame", False, "detail")]


R6.R6_FIXES.append(fix_hip_axle_r7)


def main():
    for ext in ("blend", "fbx"):          # keep R6 before Titan_M1.* is rewritten
        dst = os.path.join(HERE, "r6_final", "Titan_M1_r6." + ext)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(HERE, "Titan_M1." + ext), dst)
    F.FINAL = OUT
    F.BOLT_LOG.clear()
    objs, meshes = F.build("final")
    R, solved = F.run_checks(objs, meshes)
    R["joints_connected"] = R6.all_gaps(objs, meshes, solved)
    os.makedirs(OUT, exist_ok=True)
    R["visible_colour_pct"] = F.visible_colour_share(objs, solved)
    F.render_grey(objs, solved, OUT, "")
    F.render_colour(objs, solved, OUT)
    R["fbx_roundtrip"] = F.export(objs)
    json.dump(R, open(os.path.join(OUT, "m1_r7_checks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("=== R7 tris", R["tris_total"], "max", R["tris_max_part"], "poses", R["poses_clean"], "joints", R["joints_connected"]["ok"],
          json.dumps(R["joints_connected"]["worst_gap_m"]), "arm", R["arm_raise"]["clean_up_to_deg"], "hatch", R["kneel_hatch"]["ok"], "pilot", R["pilot_fit"]["ok"])


if "_r7" in sys.argv:
    main()
