"""tf2-kits-measure runner (2026-11-13): runtime/runner.py plus the HSD.KitMeasure mod (measure/mod).

Usage: py -3 -I kitm_runner.py <plan in plans_km.py> [runner.py options: --map, --timeout, --r5-wait]

Same pattern as ref-tail-a/ref_tail_runner.py: the extra mod is copied into R2Northstar/mods only for this run
and removed as soon as the game has exited, before runner.py releases GAME-LOCK.txt. Steam must already be
running (a Steam started by a runner cannot create Titanfall2.exe, 11-12).
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[3] / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "ref-tail-a"))

import runner  # noqa: E402
import plans  # noqa: E402
import plans_km  # noqa: E402

MY_SRC = HERE / "mod" / "HSD.KitMeasure"
MY_DST = runner.GAME / "R2Northstar" / "mods" / "HSD.KitMeasure"


def remove_mine():
    if MY_DST.exists():
        shutil.rmtree(MY_DST)


_install = runner.install
_collect = runner.collect


def install(steps):
    text = _install(steps)
    remove_mine()
    shutil.copytree(MY_SRC, MY_DST)
    return text


def collect(out, meta, log):
    remove_mine()
    meta["extra_mod"] = "HSD.KitMeasure"
    meta["session"] = "tf2-kits-measure"
    _collect(out, meta, log)


runner.install = install
runner.collect = collect
for name in plans_km.PLANS:
    setattr(plans, name, getattr(plans_km, name))


def steam_running():
    out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True).stdout
    return any(line.lower().startswith('"steam.exe"') for line in out.splitlines())


if __name__ == "__main__":
    if not steam_running():
        print("steam.exe is not running: not starting; ask the user to start Steam")
        sys.exit(5)
    try:
        runner.main()
    finally:
        remove_mine()
