"""ref-titan-upper runner: runtime/runner.py plus the HSD.RefUpper mod (ref-upper/mod).

Usage: py -3 -I ref_runner.py <plan in plans_ref.py> [runner.py options]

Same pattern as pve/live/ai_runner.py: the extra mod is copied into R2Northstar/mods only for
this run and removed as soon as the game has exited, before runner.py releases GAME-LOCK.txt,
so other sessions' runs (ref-titan-gait) never load it. Lock, R5 guard, Steam launch and log
collection into runtime/data/ are runner.py unchanged.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[3] / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(HERE))

import runner  # noqa: E402
import plans  # noqa: E402
import plans_ref  # noqa: E402

MY_SRC = HERE / "mod" / "HSD.RefUpper"
MY_DST = runner.GAME / "R2Northstar" / "mods" / "HSD.RefUpper"


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
    remove_mine()  # the game has exited; take our mod out before the lock is released
    meta["extra_mod"] = "HSD.RefUpper"
    _collect(out, meta, log)


runner.install = install
runner.collect = collect
for name in plans_ref.PLANS:
    setattr(plans, name, getattr(plans_ref, name))

if __name__ == "__main__":
    try:
        runner.main()
    finally:
        remove_mine()
