#!/usr/bin/env python3
"""Run every check that needs no game, save the outputs under results/.

  python research/phase2-prep/run_checks.py [--base <s21-platform>/scripts/vscripts]

Steps (each prints PASS/FAIL/SKIP and its exact command):
  1. unit tests (python -m unittest discover -s tests -v)
  2. Phase 1 hsd_movelog.py selftest
  3. hsd_modlint.py on the mod (loader rules)
  4. hsd_vmcheck.py --strict on the mod (needs the base scripts; SKIP otherwise)
  5. hsd_tel.py validate on the clean and the faulty SYNTHETIC fixtures
  6. hsd_tel.py report on the SYNTHETIC fixtures -> results/synthetic_report/
  7. hsd_tel.py schema -> TELEMETRY-SCHEMA.json
  8. check_refs.py: every `path:line` reference and Markdown link in the
     research docs resolves (external refs need --src-root clones)
Exit code 0 only when nothing FAILed.
"""
import argparse
import os
import platform
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RESULTS = os.path.join(HERE, "results")
PY = sys.executable


def default_src_root():
    """HSD_SRC_ROOT, else the cloud path, else a research-src/ folder beside the repository."""
    if os.environ.get("HSD_SRC_ROOT"):
        return os.environ["HSD_SRC_ROOT"]
    for p in ("/home/user/research-src", os.path.join(REPO, os.pardir, "research-src")):
        if os.path.isdir(p):
            return os.path.normpath(p)
    return "/home/user/research-src"


def rel(p):
    return os.path.relpath(p, REPO)


def step(log, name, args, expect=0, cwd=None):
    cmd = [PY] + args
    shown = "python " + " ".join(rel(a) if os.path.exists(a) else a for a in args)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or REPO)
    ok = r.returncode == expect
    status = "PASS" if ok else "FAIL"
    log.append(f"## {status} {name}\n\n```\n$ {shown}\n(exit {r.returncode}, expected {expect})\n```\n")
    tail = (r.stdout + r.stderr).strip().splitlines()
    log.append("```\n" + "\n".join(tail[-25:]) + "\n```\n")
    print(f"{status} {name}: exit {r.returncode}")
    return ok, r


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=os.environ.get("HSD_BASE_SCRIPTS",
                    os.path.join(default_src_root(), "s21-platform", "scripts", "vscripts")))
    ap.add_argument("--src-root", default=default_src_root(),
                    help="folder holding s21-r5sdk/, s21-platform/, launcher/ clones")
    a = ap.parse_args(argv)
    os.makedirs(RESULTS, exist_ok=True)
    tools = os.path.join(HERE, "tools")
    fixtures = os.path.join(HERE, "fixtures", "synthetic")
    mod = os.path.join(REPO, "research", "phase1", "mod", "hsd_movediag")
    log = [f"# Cloud check run\n\n- date (UTC): {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}\n"
           f"- python: {platform.python_version()} on {platform.system()}\n"
           f"- base scripts: {a.base if os.path.isfile(os.path.join(a.base, 'scripts.rson')) else 'not available'}\n"
           f"- source clones for reference checks: {a.src_root if os.path.isdir(a.src_root) else 'not available (external refs unchecked)'}\n\n"
           "All data used below is SYNTHETIC (hsdtel.synth) or static source; no game was run.\n\n"]
    results = []

    ok, r = step(log, "unit tests", ["-m", "unittest", "discover", "-s", os.path.join(HERE, "tests"), "-v"],
                 cwd=HERE)
    results.append(ok)
    with open(os.path.join(RESULTS, "unittest.txt"), "w") as fh:
        fh.write(r.stdout + r.stderr)
    results.append(step(log, "phase1 hsd_movelog selftest",
                        [os.path.join(REPO, "research", "phase1", "tools", "hsd_movelog.py"), "selftest"])[0])
    results.append(step(log, "hsd_modlint (loader rules)",
                        [os.path.join(REPO, "research", "phase1", "tools", "hsd_modlint.py"), mod])[0])
    if os.path.isfile(os.path.join(a.base, "scripts.rson")):
        ok, r = step(log, "hsd_vmcheck --strict (per-VM API evidence)",
                     [os.path.join(tools, "hsd_vmcheck.py"), mod, "--base", a.base, "--strict"])
        results.append(ok)
        with open(os.path.join(RESULTS, "vmcheck.txt"), "w") as fh:
            fh.write(r.stdout)
    else:
        log.append("## SKIP hsd_vmcheck (base scripts not available; pass --base)\n\n")
        print("SKIP hsd_vmcheck")
    results.append(step(log, "validate clean SYNTHETIC fixture",
                        [os.path.join(tools, "hsd_tel.py"), "validate", os.path.join(fixtures, "platform", "logs"), "--quiet"])[0])
    results.append(step(log, "validate faulty SYNTHETIC fixture (exit 2 expected)",
                        [os.path.join(tools, "hsd_tel.py"), "validate", os.path.join(fixtures, "faulty")], expect=2)[0])
    results.append(step(log, "report on SYNTHETIC fixture",
                        [os.path.join(tools, "hsd_tel.py"), "report", os.path.join(fixtures, "platform", "logs"),
                         "-o", os.path.join(RESULTS, "synthetic_report")])[0])
    results.append(step(log, "schema export",
                        [os.path.join(tools, "hsd_tel.py"), "schema", "-o", os.path.join(HERE, "TELEMETRY-SCHEMA.json")])[0])
    results.append(step(log, "smoke checks on SYNTHETIC fixture",
                        [os.path.join(tools, "hsd_tel.py"), "smoke", os.path.join(fixtures, "platform", "logs")])[0])
    ok, r = step(log, "documentation references (check_refs)",
                 [os.path.join(tools, "check_refs.py"), "--src-root", a.src_root])
    results.append(ok)
    failed = results.count(False)
    log.append(f"\n**{len(results) - failed}/{len(results)} steps passed.**\n")
    with open(os.path.join(RESULTS, "CHECKS.md"), "w") as fh:
        fh.write("\n".join(log))
    print(f"{len(results) - failed}/{len(results)} passed; details in {rel(os.path.join(RESULTS, 'CHECKS.md'))}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
