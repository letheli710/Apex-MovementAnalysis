"""Compare a fresh Unity batch replay of the M2/M1 and M3 trial sets with the published outputs (stdlib only).

    python regression_check.py <new M2+M1 output dir> <new M3 output dir> [--write regression.md]

<new M2+M1 output dir>: BatchReplay -motor both over ../../m2/trials/* and ../../m1/trials/* (v2 reports + m1_first_guess/).
<new M3 output dir>:    BatchReplay -motor v2 over ../../m3/trials/*.
Baselines (relative to this folder): ../../m3/unity/regression_m2_m1 (M2 + M1 trials, R5MotorV2/m3 = HSD-Unity main),
../../m2/unity (M2 + M1 trials, R5MotorV2/m2, and the M1 first guess under m1_first_guess/), ../../m3/unity (M3 trials, R5MotorV2/m3).
Files are compared byte for byte. The research repo stores .md/.json with LF (.gitattributes eol=lf) while Unity writes them with
CRLF on Windows, so for those two types CRLF is folded to LF before the comparison; steps.csv (-text) is compared raw.
index.md is skipped (it carries the generation time).
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_M3_REG = os.path.join(HERE, "..", "..", "m3", "unity", "regression_m2_m1")
BASE_M2 = os.path.join(HERE, "..", "..", "m2", "unity")
BASE_M3 = os.path.join(HERE, "..", "..", "m3", "unity")


def content(path):
    b = open(path, "rb").read()
    return b if path.endswith(".csv") else b.replace(b"\r\n", b"\n")


def compare(new, base, only=None):
    res = {"identical": [], "different": [], "missing": []}
    for root, _, files in os.walk(new):
        for f in sorted(files):
            if f == "index.md":
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, new).replace(os.sep, "/")
            if only and not only(rel):
                continue
            b = os.path.join(base, rel)
            if not os.path.exists(b):
                res["missing"].append(rel)
            elif content(p) == content(b):
                res["identical"].append(rel)
            else:
                res["different"].append(rel)
    return res


def digest(new):
    h = hashlib.sha256()
    for root, _, files in sorted(os.walk(new)):
        for f in sorted(files):
            if f == "index.md":
                continue
            p = os.path.join(root, f)
            h.update(os.path.relpath(p, new).replace(os.sep, "/").encode())
            h.update(content(p))
    return h.hexdigest()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
    if out in args:
        args.remove(out)
    new_m2, new_m3 = args[:2]
    rows = []
    checks = [
        ("M2 + M1 trials, R5MotorV2 reports", new_m2, BASE_M3_REG, "../../m3/unity/regression_m2_m1 (main = R5MotorV2/m3)",
         lambda r: not r.startswith("m1_first_guess/")),
        ("M2 + M1 trials, R5MotorV2 reports", new_m2, BASE_M2, "../../m2/unity (R5MotorV2/m2, before M3)",
         lambda r: not r.startswith("m1_first_guess/")),
        ("M2 + M1 trials, M1 first guess", new_m2, BASE_M2, "../../m2/unity/m1_first_guess", lambda r: r.startswith("m1_first_guess/")),
        ("M3 trials, R5MotorV2 reports", new_m3, BASE_M3, "../../m3/unity", None),
    ]
    lines = []
    for name, new, base, label, only in checks:
        r = compare(new, base, only)
        lines.append((name, label, r))
        print(f"{name} vs {label}: identical {len(r['identical'])}, different {len(r['different'])}, missing {len(r['missing'])}")
        for k in ("different", "missing"):
            for x in r[k]:
                print(f"   {k}: {x}")
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            for name, label, r in lines:
                fh.write(f"| {name} | `{label}` | {len(r['identical'])} | {len(r['different'])} | {len(r['missing'])} | "
                         f"{', '.join(sorted({x.split('/')[-2] if '/' in x else x for x in r['different']})) or '–'} |\n")
            fh.write(f"\nsha256 (CRLF→LF for .md/.json, index.md excluded): M2+M1 output `{digest(new_m2)}`, M3 output `{digest(new_m3)}`\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
