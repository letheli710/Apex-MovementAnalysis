"""Each part's box around its own joint, from a saved heavy model (for Unity's TitanDimsHeavy.Parts, walk retarget H5): analysis axes
(x forward, y left, z up), metres, centre and half size, the mesh's local bounds (meshes have their origin on the owner joint, at rest).

  blender.exe -b <Titan_Hx.blend> -P part_boxes.py -- <out.tsv>"""
import sys

import bpy
import numpy as np

out = sys.argv[sys.argv.index("--") + 1:][0]
rows = ["part\tjoint\tcx\tcy\tcz\thx\thy\thz"]
for ob in sorted([o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("REF_")], key=lambda o: o.name):
    v = np.array([x.co[:] for x in ob.data.vertices])
    a = np.stack([-v[:, 1], v[:, 0], v[:, 2]], 1)       # Blender local -> analysis
    lo, hi = a.min(0), a.max(0)
    c, h = (lo + hi) / 2, (hi - lo) / 2
    rows.append("%s\t%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f" % (ob.name, ob.parent.name if ob.parent else "", *c, *h))
open(out, "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("=== BOXES", len(rows) - 1)
