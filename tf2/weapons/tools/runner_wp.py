"""TF2 weapons runner (session tf2-weapons, 2026-11-08): runtime/runner.py plus two add-on scripts.

Usage: python -I runner_wp.py <wp_plan> [runner.py options: --timeout, --r5-wait, --map]
  Plans live in plans_wp.py (names start with wp_). Output goes to runtime/data/<time>_<plan>/ as usual.

The shared runner copies TF2-Research/mod/HSD.TF2Diag into the game for every run. This wrapper
then copies weapons/mod/hsd_wp_sv.gnut and hsd_wp_cl.gnut into the INSTALLED copy and registers
them in the installed mod.json only. The shared mod folder is not touched, so runs of other
sessions (which reinstall the mod from the shared folder) never load these scripts.
Lock, R5 guard and log collection are the shared runner's.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[1] / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(HERE))

import runner  # noqa: E402
import plans  # noqa: E402
import plans_wp  # noqa: E402

ADDONS = [
    ("hsd_wp_sv.gnut", {"RunOn": "SERVER && MP", "ServerCallback": {"After": "HsdWp_InitServer"}}),
    ("hsd_wp_cl.gnut", {"RunOn": "CLIENT && MP", "ClientCallback": {"After": "HsdWp_InitClient"}}),
]

for _name in dir(plans_wp):
    if _name.startswith("wp_"):
        setattr(plans, _name, getattr(plans_wp, _name))

_orig_install = runner.install


def install(steps):
    text = _orig_install(steps)
    vs = runner.MOD_DST / "mod" / "scripts" / "vscripts"
    mj = runner.MOD_DST / "mod.json"
    data = json.loads(mj.read_text(encoding="utf-8"))
    have = {s["Path"] for s in data["Scripts"]}
    for fname, entry in ADDONS:
        shutil.copy2(HERE.parent / "mod" / fname, vs / fname)
        if fname not in have:
            data["Scripts"].append(dict({"Path": fname}, **entry))
    mj.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")
    print("add-ons installed:", ", ".join(f for f, _ in ADDONS), flush=True)
    return text


runner.install = install

if __name__ == "__main__":
    runner.main()
