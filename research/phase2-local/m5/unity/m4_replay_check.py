"""Compare the M5 build's replay of the 38 M4 trials with the published M4 outputs (stdlib only).

    python m4_replay_check.py [<new dir>]        (default: m4_replay/ next to this file)

<new dir>: BatchReplay -motor v2 -scenarios ../../m4/unity/scenarios.json over ../../m4/trials/* (not *_REJECTED).
Baseline: ../../m4/unity/<trial_id>/ (HSD-Unity main, M4). Same file rules as ../../m4/unity/regression_check.py: steps.csv raw,
.md/.json with CRLF folded to LF, index.md skipped. For a differing summary.json the differing top-level keys are listed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "..", "m4", "unity")


def content(path):
    b = open(path, "rb").read()
    return b if path.endswith(".csv") else b.replace(b"\r\n", b"\n")


def main():
    new = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "m4_replay")
    same, diff, missing = [], [], []
    for d in sorted(os.listdir(new)):
        p = os.path.join(new, d)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            a, b = os.path.join(p, f), os.path.join(BASE, d, f)
            if not os.path.exists(b):
                missing.append(f"{d}/{f}")
            elif content(a) == content(b):
                same.append(f"{d}/{f}")
            else:
                diff.append(f"{d}/{f}")
    print(f"identical {len(same)}, different {len(diff)}, missing {len(missing)}")
    for x in diff:
        line = "  different: " + x
        if x.endswith("summary.json"):
            ja = json.load(open(os.path.join(new, x), encoding="utf-8"))
            jb = json.load(open(os.path.join(BASE, x), encoding="utf-8"))
            keys = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))
            line += "  keys: " + ", ".join(keys)
        print(line)
    for x in missing:
        print("  missing: " + x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
