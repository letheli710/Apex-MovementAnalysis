"""GAPS-1108 runner (session tf2-pilot-gaps, 2026-11-08): runtime/runner.py plus one add-on script.

Usage: python -I runner_g8.py <g8_plan> [runner.py options: --timeout, --r5-wait, --map]
  Plans live in plans_g8.py (names start with g8_). Output goes to runtime/data/<time>_<plan>/.

Same pattern as weapons/tools/runner_wp.py: the shared runner installs TF2-Research/mod/HSD.TF2Diag,
then this wrapper copies gaps1108/mod/hsd_diag_g8.gnut into the INSTALLED copy and registers it in
the installed mod.json only. The shared mod folder is not touched, so other sessions' runs never
load it. Lock, R5 guard and log collection are the shared runner's.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(HERE))

import runner  # noqa: E402
import plans  # noqa: E402
import plans_g8  # noqa: E402

ADDONS = [
    ("hsd_diag_g8.gnut", {"RunOn": "SERVER && MP", "ServerCallback": {"After": "HsdDiagG8_Init"}}),
]

for _name in dir(plans_g8):
    if _name.startswith("g8_"):
        setattr(plans, _name, getattr(plans_g8, _name))

_orig_install = runner.install


def install(steps):
    text = _orig_install(steps)
    vs = runner.MOD_DST / "mod" / "scripts" / "vscripts"
    mj = runner.MOD_DST / "mod.json"
    data = json.loads(mj.read_text(encoding="utf-8"))
    # 11-08: tf2-titan-kits' hsd_diag_kit.gnut does not compile (WorldSpaceCenter) and kills every server;
    # leave these foreign add-ons out of this session's installed copy only
    drop = ("hsd_diag_kit.gnut", "hsd_diag_kit_cl.gnut")
    data["Scripts"] = [s for s in data["Scripts"] if s["Path"] not in drop]
    have = {s["Path"] for s in data["Scripts"]}
    for fname, entry in ADDONS:
        shutil.copy2(HERE / "mod" / fname, vs / fname)
        if fname not in have:
            data["Scripts"].append(dict({"Path": fname}, **entry))
    mj.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")
    print("add-ons installed:", ", ".join(f for f, _ in ADDONS), flush=True)
    return text


runner.install = install

if __name__ == "__main__":
    runner.main()
