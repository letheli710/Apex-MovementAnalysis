"""tf2-ai-live runner: runtime/runner.py plus the HSD.TF2AILive mod (pve/live/mod).

Usage: python -I ai_runner.py <plan in plans_ai.py> [runner.py options]

The extra mod is copied into R2Northstar/mods only for this run and removed as soon as the
game has exited, before runner.py releases GAME-LOCK.txt, so other sessions' runs never load
it. Everything else (lock, R5 guard, Steam launch, log collection into runtime/data/) is
runner.py unchanged.
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
import plans_ai  # noqa: E402

MY_SRC = HERE / "mod" / "HSD.TF2AILive"
MY_DST = runner.GAME / "R2Northstar" / "mods" / "HSD.TF2AILive"


def remove_mine():
    if MY_DST.exists():
        shutil.rmtree(MY_DST)


_install = runner.install
_collect = runner.collect


# Scripts of other sessions left out of the installed HSD.TF2Diag copy for our runs only.
# 2026-11-08: hsd_diag_kit.gnut (tf2-titan-kits) did not compile ("WorldSpaceCenter does not
# exist", line 489), which stops the whole server VM; our plans never use hsd_kit_* commands.
SKIP_SCRIPTS = {"hsd_diag_kit.gnut"}


def strip_scripts():
    mj = runner.MOD_DST / "mod.json"
    data = json.loads(mj.read_text(encoding="utf-8"))
    kept = [s for s in data.get("Scripts", []) if s.get("Path") not in SKIP_SCRIPTS]
    dropped = len(data.get("Scripts", [])) - len(kept)
    data["Scripts"] = kept
    mj.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")
    for name in SKIP_SCRIPTS:
        f = runner.MOD_DST / "mod" / "scripts" / "vscripts" / name
        if f.exists():
            f.unlink()
    print("left out of the installed HSD.TF2Diag: %d script(s) %s" % (dropped, sorted(SKIP_SCRIPTS)), flush=True)


def install(steps):
    text = _install(steps)
    strip_scripts()
    remove_mine()
    shutil.copytree(MY_SRC, MY_DST)
    return text


def collect(out, meta, log):
    remove_mine()  # the game has exited; take our mod out before the lock is released
    meta["extra_mod"] = "HSD.TF2AILive"
    _collect(out, meta, log)


runner.install = install
runner.collect = collect
for name in plans_ai.PLANS:
    setattr(plans, name, getattr(plans_ai, name))

if __name__ == "__main__":
    try:
        runner.main()
    finally:
        remove_mine()
