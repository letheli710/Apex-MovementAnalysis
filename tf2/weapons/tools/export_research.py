"""Copy this study into the research repo worktree (session tf2-weapons, 2026-11-08).

Usage: python -I export_research.py <research worktree> <run dir> [<run dir> ...]
  - TF2-Research/weapons/**  -> <worktree>/tf2/weapons/**   (no __pycache__)
  - each run dir: diag.tsv, meta.json, plan.gnut, analysis.txt -> <worktree>/tf2/runtime/data/<run>/
    (raw.log is NOT copied: it holds machine paths and the account name; it goes to HSD-RawData)
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEAPONS = HERE.parent
KEEP = ("diag.tsv", "meta.json", "plan.gnut", "analysis.txt")


def main():
    wt = Path(sys.argv[1])
    dst = wt / "tf2" / "weapons"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(WEAPONS, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    n = 0
    for run in sys.argv[2:]:
        run = Path(run)
        out = wt / "tf2" / "runtime" / "data" / run.name
        out.mkdir(parents=True, exist_ok=True)
        for f in KEEP:
            if (run / f).exists():
                shutil.copy2(run / f, out / f)
                n += 1
    print("weapons copied; run files:", n)


if __name__ == "__main__":
    main()
