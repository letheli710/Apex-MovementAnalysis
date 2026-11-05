#!/usr/bin/env python3
"""Weapon script fields about the sights, one row per gun: IS-STATIC.tsv. Field values, read from the local build's platform/scripts/weapons (S21 client's files).
  py -3 static_scan.py <bg_scan.json> <out.tsv>"""
import json, os, re, sys
W = os.path.expanduser("~/Games/R5Flowstate/platform/scripts/weapons/")
IRON = ("sight_front", "sight_rear", "sight_rear_on", "sight", "sight_on", "mastiff_sight")
info = json.load(open(sys.argv[1], encoding="utf-8"))
rows = []
for g, i in info.items():
    t = open(W + i["id"] + ".txt", encoding="utf-8", errors="replace").read()
    parts = t.split('"Mods"')
    head, mods = parts[0], parts[1] if len(parts) > 1 else ""
    def fld(k, s=head):
        m = re.search(r'"%s"\s+"([^"]*)"' % k, s)
        return m[1] if m else ""
    num = {m[2]: m[1] for m in re.finditer(r'"bodygroup(\d+)_name"\s+"([^"]+)"', t)}
    iron_n = {n: num[n] for n in num if n in IRON}
    in_model = {n: n in i["bg"] for n in num if n in IRON}
    # what each optic mod does to the irons
    eff = {}
    for m in re.finditer(r'"(optic_[a-z0-9_]+)"\s*\{(.*?)\n\s*\}', mods, re.S):
        sets = {n: re.search(r'"bodygroup%s_set"\s+"(\d)"' % k, m[2]) for n, k in iron_n.items()}
        eff[m[1]] = {n: v[1] for n, v in sets.items() if v}
    vals = sorted({json.dumps(v, sort_keys=True) for v in eff.values()})
    rows.append(dict(
        gun=g, id=i["id"], viewmodel=i["vm"].split("/")[-1],
        center_attachment=fld("viewmodel_ads_centerpoint_attachment"), rui_attachment=fld("viewmodel_ads_rui_bottomleft_attachment"),
        offset_hip=fld("viewmodel_offset_hip"), offset_ads=fld("viewmodel_offset_ads"), zoom_fov=fld("zoom_fov"), zoom_fov_viewmodel=fld("zoom_fov_viewmodel"),
        dof_near=fld("dof_zoom_nearDepthStart") + ".." + fld("dof_zoom_nearDepthEnd"), dof_focus_h=fld("dof_zoom_focusArea_horizontal"), dof_focus_top=fld("dof_zoom_focusArea_top"), dof_focus_bot=fld("dof_zoom_focusArea_bottom"),
        iron_default=";".join(f"{n}={fld('bodygroup%s_set' % k)}{'' if in_model[n] else ' (not in model)'}" for n, k in iron_n.items()),
        optics_set=" | ".join(vals) if vals else "", optics=len(eff)))
keys = list(rows[0])
with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
    f.write("\t".join(keys) + "\n")
    for r in rows:
        f.write("\t".join(str(r[k]) for k in keys) + "\n")
print(len(rows))
