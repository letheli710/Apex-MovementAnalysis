"""Diagnostic (not part of the build): rifle/shotgun offsets and rest-pose options vs collisions and lowest weapon point.
blender -b -P _diag/diag_hold.py -- L1 1"""
import os, sys, json, itertools
os.environ["LIGHT_NO_MAIN"] = "1"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import importlib
args = sys.argv[sys.argv.index("--") + 1:]
code = args[0]
mod = importlib.import_module({"L1": "l1_parts", "L2": "l2_parts"}[code])
cfgs = json.loads(args[2]) if len(args) > 2 else [[0, 0]]
res = {}
for du, dv in cfgs:
    if hasattr(mod, "RIFLE_DU"):
        mod.RIFLE_DU, mod.RIFLE_DV = du, dv
    sys.modules.pop("build_light", None)
    import build_light as B
    objs, meshes, mats = B.build()
    wpn = [n for n in meshes if n.startswith(("Rifle", "Shotgun"))]
    out = {}
    poses = B.R.poses()
    rests = json.loads(args[3]) if len(args) > 3 else {}
    for name, h in list(poses.items()):
        if "~" in name: continue
        p, off = B.solve_pose(objs, meshes, h)
        hits = B.collide(meshes)
        low = min(B.wverts(meshes[n])[:, 2].min() for n in wpn)
        out[name] = (round(float(low), 2), hits)
    for rn, rp in [("rest", {})] + list(rests.items()):
        B.set_pose(objs, rp)
        hits = B.collide(meshes)
        low = min(B.wverts(meshes[n])[:, 2].min() for n in wpn)
        out["REST:" + rn] = (round(float(low), 2), hits)
    res["du=%g dv=%g" % (du, dv)] = out
    print("=== du=%g dv=%g" % (du, dv))
    for k, (low, hits) in out.items():
        print("  %-22s low %6.2f  %s" % (k, low, "; ".join(hits) if hits else "clean"))
