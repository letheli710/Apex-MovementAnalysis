"""ref-titan-gait runner (2026-11-09): runtime/runner.py plus this session's gait add-on scripts.

Usage: py -3 -I runner_gait.py <gait_plan> [runner.py options: --timeout, --r5-wait, --map]
  Plans live in plans_gait.py (names start with gait_). Output goes to runtime/data/<time>_<plan>/.

Same pattern as runtime/gaps1108/runner_g8.py: the shared runner installs TF2-Research/mod/HSD.TF2Diag
(and takes / releases GAME-LOCK.txt), then this wrapper copies ref-gait/mod/*.gnut into the INSTALLED
copy and registers them in the installed mod.json only. The shared mod folder is not touched.
The kit add-ons (hsd_diag_kit*.gnut) are left out of this session's installed copy: not needed here,
and a server error in a foreign add-on would end the run.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[3] / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(HERE))

import runner  # noqa: E402
import plans  # noqa: E402
import plans_gait  # noqa: E402

ADDONS = [
    ("hsd_diag_gait.gnut", {"RunOn": "SERVER && MP", "ServerCallback": {"After": "HsdDiagGait_Init"}}),
    ("hsd_diag_gait_cl.gnut", {"RunOn": "CLIENT && MP", "ClientCallback": {"After": "HsdDiagGait_InitClient"}}),
]
DROP = ("hsd_diag_kit.gnut", "hsd_diag_kit_cl.gnut")

for _name in dir(plans_gait):
    if _name.startswith("gait_"):
        setattr(plans, _name, getattr(plans_gait, _name))

_orig_install = runner.install


def install(steps):
    text = _orig_install(steps)
    vs = runner.MOD_DST / "mod" / "scripts" / "vscripts"
    mj = runner.MOD_DST / "mod.json"
    data = json.loads(mj.read_text(encoding="utf-8"))
    data["Scripts"] = [s for s in data["Scripts"] if s["Path"] not in DROP]
    have = {s["Path"] for s in data["Scripts"]}
    for fname, entry in ADDONS:
        shutil.copy2(HERE / "mod" / fname, vs / fname)
        if fname not in have:
            data["Scripts"].append(dict({"Path": fname}, **entry))
    mj.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")
    print("add-ons installed:", ", ".join(f for f, _ in ADDONS), "; dropped:", ", ".join(DROP), flush=True)
    return text


runner.install = install

if __name__ == "__main__":
    runner.main()
