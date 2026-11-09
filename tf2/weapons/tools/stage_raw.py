"""Copy the raw.log of runner_wp.py runs into an HSD-RawData worktree and add MANIFEST.tsv rows
(session tf2-weapons, 2026-11-08).

Usage: python -I stage_raw.py <HSD-RawData worktree> <run dir> [<run dir> ...]
  run dir: TF2-Research/runtime/data/<time>_<plan>
Each raw.log goes to tf2/runtime/data/<run>/raw.log (category tf2-rawlog, same layout as the
11-03 titan runs). raw.log holds machine paths and the account name, so it stays out of the public
research repo (D-76); diag.tsv / meta.json / plan.gnut go to the research repo instead.
Rows already in MANIFEST.tsv are not added twice.
"""
import hashlib
import shutil
import sys
from pathlib import Path


def main():
    raw = Path(sys.argv[1])
    manifest = raw / "MANIFEST.tsv"
    have = {line.split("\t", 1)[0] for line in manifest.read_text(encoding="utf-8").splitlines()}
    rows = []
    for run in sys.argv[2:]:
        run = Path(run)
        src = run / "raw.log"
        if not src.exists():
            print("no raw.log:", run)
            continue
        rel = "tf2/runtime/data/%s/raw.log" % run.name
        dst = raw / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if rel in have:
            print("already in manifest:", rel)
            continue
        data = dst.read_bytes()
        rows.append("\t".join([rel, str(len(data)), hashlib.sha256(data).hexdigest(),
                               "TF2-Research/runtime/data/%s/raw.log" % run.name,
                               "Apex-MovementAnalysis: tf2/runtime/data/%s/raw.log" % run.name, "tf2-rawlog"]))
    if rows:
        # append only (the manifest is LF and large; never rewrite it)
        ends_nl = manifest.read_bytes().endswith(b"\n")
        with open(manifest, "a", encoding="utf-8", newline="\n") as f:
            f.write(("" if ends_nl else "\n") + "\n".join(rows) + "\n")
    print("added", len(rows), "rows")


if __name__ == "__main__":
    main()
