"""RPS replay baseline (native slide rules, D-47): write or check the per-file sha256 manifest, stdlib only.

    python rps_check.py <run dir>            check a fresh run against unity/baseline_sha256.json
    python rps_check.py <run dir> --write    rewrite the manifest from <run dir> (only when the baseline is meant to move)

<run dir> holds m2m1/ (BatchReplay -motor both over ../m2/trials/* and ../m1/trials/*), m3/ (-motor v2 over ../m3/trials/*) and m4/
(-motor v2 -scenarios ../m4/unity/scenarios.json over ../m4/trials/*, not *_REJECTED), with the default (native) replay motor. Same file
rules as ../m4/unity/regression_check.py: steps.csv raw, .md/.json with CRLF folded to LF, index.md and *.log skipped. The legacy baseline
(M2/M3 slide rules, BatchReplay -legacyM2) is still checked by ../m4/unity/regression_check.py and ../m5/unity/m4_replay_check.py.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "unity", "baseline_sha256.json")


def content(path):
    b = open(path, "rb").read()
    return b if path.endswith(".csv") else b.replace(b"\r\n", b"\n")


def hashes(run):
    out = {}
    for sub in ("m2m1", "m3", "m4"):
        root = os.path.join(run, sub)
        for d, _, files in os.walk(root):
            for f in files:
                if f == "index.md" or f.endswith(".log"):
                    continue
                p = os.path.join(d, f)
                out[sub + "/" + os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(content(p)).hexdigest()
    return dict(sorted(out.items()))


def main():
    run = sys.argv[1]
    h = hashes(run)
    if "--write" in sys.argv:
        json.dump(h, open(MANIFEST, "w", encoding="utf-8", newline="\n"), indent=0)
        print(f"wrote {len(h)} hashes to {MANIFEST}")
        return 0
    base = json.load(open(MANIFEST, encoding="utf-8"))
    same = [k for k in h if base.get(k) == h[k]]
    diff = [k for k in h if k in base and base[k] != h[k]]
    missing = [k for k in base if k not in h]
    extra = [k for k in h if k not in base]
    for sub in ("m2m1", "m3", "m4"):
        print(f"{sub}: identical {sum(k.startswith(sub + '/') for k in same)}, different {sum(k.startswith(sub + '/') for k in diff)}, "
              f"missing {sum(k.startswith(sub + '/') for k in missing)}, extra {sum(k.startswith(sub + '/') for k in extra)}")
    for k in diff + missing + extra:
        print("  " + k)
    return 0 if not (diff or missing or extra) else 1


if __name__ == "__main__":
    sys.exit(main())
