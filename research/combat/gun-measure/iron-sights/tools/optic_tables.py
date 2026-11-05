#!/usr/bin/env python3
"""IS-OPTIC-FOV.tsv (the measured view model scale for each optic) and D-VM-PITCH.tsv (why D-VIEWMODEL's aimed U is off).
  py -3 -I optic_tables.py <optic-r301 dir> <optic-sentinel dir> <old runs dir> <data dir>
"""
import csv, json, math, os, re, statistics as st, sys

r301, sentinel, runs, data = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
GM = os.path.join(HERE, "..", "..")


def tsv(p):
    return list(csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"))


keys = ["gun", "mod", "state", "S", "world_fov", "zoom_fov", "zoom_fov_viewmodel", "scale_vs_prop", "one_minus_iou", "measured_f", "code_f", "zoom_fov_f", "measured_over_code", "code_vertical",
        "muzzle_F", "muzzle_R", "muzzle_U", "center_F", "center_R", "center_U", "center_on_gun_F", "center_on_gun_U", "part_F", "part_U", "eye_dist", "quality"]
out = []
for gun, d in (("r301", r301), ("sentinel", sentinel)):
    ex = json.load(open(os.path.join(d, "optic_extents.json")))
    for r in tsv(os.path.join(d, "fit.tsv")):
        m = [float(x) for x in r["muzzle"].split("/")]
        c = [float(x) for x in r["center"].split("/")]
        w = r["weapon"]
        zf = float(w.split("zoom_fov=")[1].split()[0])
        vm = float(w.split(" vm=")[1].split()[0])
        cf, mf = float(r["code_f"]), float(r["vm_f"])
        iou = float(r["err_px"])
        q = "good" if iou < 0.45 else ("weak" if iou < 0.7 else "failed")
        if abs(mf / cf - 1) > 0.15:
            q = "failed"  # far from every number the gun could use: the outlines did not lock (long gun off screen, or the scope picture)
        e = ex.get(r["mod"]) if r["mod"] != "none" else None
        eye = f'{m[0] + e["F"][0]:.2f}..{m[0] + e["F"][1]:.2f}' if e and r["state"].startswith("ads") else ""
        out.append(dict(gun=gun, mod=r["mod"], state=r["state"].split("_")[0], S=r["S"], world_fov=r["world_fov"], zoom_fov=zf, zoom_fov_viewmodel=vm,
                        scale_vs_prop=r["scale_vs_prop"], one_minus_iou=r["err_px"], measured_f=round(mf), code_f=round(cf), zoom_fov_f=round(float(r["zoom_fov_f"])),
                        measured_over_code=round(mf / cf, 3), code_vertical=round(2 * math.degrees(math.atan(450 / cf)), 1),
                        muzzle_F=m[0], muzzle_R=m[1], muzzle_U=m[2], center_F=c[0], center_R=c[1], center_U=c[2],
                        center_on_gun_F=round(c[0] - m[0], 2), center_on_gun_U=round(c[2] - m[2], 2),
                        part_F=f'{e["F"][0]}..{e["F"][1]}' if e else "", part_U=f'{e["U"][0]}..{e["U"][1]}' if e else "", eye_dist=eye, quality=q))
with open(os.path.join(data, "IS-OPTIC-FOV.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(keys) + "\n")
    for r in out:
        f.write("\t".join(str(r[k]) for k in keys) + "\n")
print(len(out), "optic rows")

# D-VIEWMODEL against the eye pitch logged in the same run
RC = re.compile(r"\[RT\] clip t=\S+ c=\S+ ammo=\S+ reload=\S+ adsf=\S+ active=\S+ ea=([-\d.]+),([-\d.]+)")
RG = re.compile(r"\] g t=([\d.]+) .*?m=([-\d.]+),([-\d.]+),([-\d.]+) c=([-\d.]+),([-\d.]+),([-\d.]+)")
new = {r["gun"]: r for r in tsv(os.path.join(data, "IS-GUNS.tsv"))}
rows = []
for r in tsv(os.path.join(GM, "D-VIEWMODEL.tsv")):
    if r["mode"] != "ads" or not new.get(r["gun"], {}).get("aim_U"):
        continue
    g = r["gun"]
    p = os.path.join(runs, f"fr_{g}_adshold.txt")
    txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    c = RC.findall(txt)
    pitch = float(c[0][0]) if c else ""
    F, U = float(r["muzzleF"]), float(r["muzzleU"])
    nF, nU = float(new[g]["aim_F"]), float(new[g]["aim_U"])
    # was the gun still moving in the old window? the frames 1.95..2.35 s into the log: the aim is on and the attack has not started
    fr = [(float(m[1]), float(m[2]) - float(m[5]), float(m[4]) - float(m[7])) for m in RG.finditer(txt)]
    spread = ""
    if fr:
        t0 = fr[0][0]
        w = [x for x in fr if 1.95 < x[0] - t0 < 2.35]
        if len(w) > 3:
            spread = round(max(x[2] for x in w) - min(x[2] for x in w), 3)
    th = math.radians(pitch) if pitch != "" else 0.0
    row = dict(gun=g, old_F=F, old_U=U, log_pitch=pitch if pitch != "" else "not logged", old_U_range_in_window=spread, new_F=nF, new_U=nU, old_minus_new_U=round(U - nU, 2),
               corrected_U=round(F * math.sin(th) + U * math.cos(th), 2) if pitch != "" else "", corrected_minus_new_U=round(F * math.sin(th) + U * math.cos(th) - nU, 2) if pitch != "" else "",
               pitch_that_would_explain_it=round(math.degrees(math.atan2(U - nU, F)), 2))
    rows.append(row)
ks = list(rows[0])
with open(os.path.join(data, "D-VM-PITCH.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(ks) + "\n")
    for r in rows:
        f.write("\t".join(str(r[k]) for k in ks) + "\n")
bad = [r for r in rows if abs(r["old_minus_new_U"]) >= 0.4]
print(len(rows), "aim rows,", len(bad), "off by 0.4 or more")
for r in bad:
    print(r)
