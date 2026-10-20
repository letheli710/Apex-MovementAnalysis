import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _common import FAULTY, FIXTURES, LOGS, MOD, PHASE1_TOOLS, TOOLS, BASE_SCRIPTS

PY = sys.executable


def _read(path):
    with open(path) as fh:
        return fh.read()


def _write(path, text, lines=False):
    with open(path, "w", newline="\n") as fh:
        if lines:
            fh.writelines(text)
        else:
            fh.write(text)


def run(*args, cwd=None):
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=cwd)


class TestCli(unittest.TestCase):
    def test_report_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(os.path.join(TOOLS, "hsd_tel.py"), "report", LOGS, "-o", d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for name in ("rows.csv", "events.csv", "hops.csv", "summary.csv", "fits.json", "validation.json",
                         "report.md", "spd2d_HSD_cl.svg", "spd2d_MT_sv.svg"):
                self.assertTrue(os.path.getsize(os.path.join(d, name)) > 0, name)
            report = _read(os.path.join(d, "report.md"))
            self.assertIn("SYNTHETIC", report)
            self.assertIn("SYNTHETIC - not Apex data", _read(os.path.join(d, "spd2d_HSD_cl.svg")))
            header = _read(os.path.join(d, "rows.csv")).split("\n")[0].strip().split(",")
            self.assertEqual(header[:4], ["file", "line_no", "source", "side"])
            self.assertTrue(all(c.startswith(("drv_", "ing_")) or c in header for c in header))

    def test_validate_exit_codes(self):
        self.assertEqual(run(os.path.join(TOOLS, "hsd_tel.py"), "validate", LOGS, "--quiet").returncode, 0)
        r = run(os.path.join(TOOLS, "hsd_tel.py"), "validate", FAULTY, "--quiet")
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_schema_json_matches_csv_header(self):
        r = run(os.path.join(TOOLS, "hsd_tel.py"), "schema")
        cols = [c["name"] for c in json.loads(r.stdout)["columns"]]
        self.assertEqual(len(cols), len(set(cols)))
        for c in json.loads(r.stdout)["columns"]:
            prefix_ok = (c["provenance"] == "drv") == c["name"].startswith("drv_") and \
                        (c["provenance"] == "ing") == c["name"].startswith("ing_")
            self.assertTrue(prefix_ok, c["name"])

    def test_compare_and_plot_commands(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(os.path.join(TOOLS, "hsd_tel.py"), "compare", LOGS, "--baseline", "r1", "-o", os.path.join(d, "c.csv"))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("max_spd2d", _read(os.path.join(d, "c.csv")))
            r = run(os.path.join(TOOLS, "hsd_tel.py"), "plot", LOGS, "--source", "MT", "--plot-side", "sv",
                    "-o", os.path.join(d, "p.svg"))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(_read(os.path.join(d, "p.svg")).startswith("<svg"))


class TestCollect(unittest.TestCase):
    def test_collect_copies_newest_sessions_and_reports(self):
        with tempfile.TemporaryDirectory() as d:
            game = os.path.join(d, "game")
            shutil.copytree(os.path.join(FIXTURES, "platform"), os.path.join(game, "platform"))
            old = os.path.join(game, "platform", "logs", "client", "older-session")
            os.makedirs(old)
            _write(os.path.join(old, "message.log"), "# old\n")
            os.utime(old, (1, 1))
            os.utime(os.path.join(old, "message.log"), (1, 1))
            _write(os.path.join(game, "platform", "scriptdump_hsd_movediag_settings.csv"), "key,float_value\n")
            out = os.path.join(d, "out")
            r = run(os.path.join(TOOLS, "hsd_collect.py"), "--game", game, "--out", out, "--label", "t")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            (dest,) = os.listdir(out)
            self.assertTrue(dest.endswith("_t"))
            got = os.listdir(os.path.join(out, dest, "platform", "logs", "client"))
            self.assertEqual(got, ["00000000-synth-client"])
            self.assertTrue(os.path.isfile(os.path.join(out, dest, "scriptdump", "scriptdump_hsd_movediag_settings.csv")))
            self.assertTrue(os.path.isfile(os.path.join(out, dest, "report", "report.md")))

    def test_collect_without_logs_fails_clearly(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(os.path.join(TOOLS, "hsd_collect.py"), "--game", d, "--out", os.path.join(d, "o"))
            self.assertEqual(r.returncode, 1)
            self.assertIn("Developer", r.stdout)


class TestDeterminism(unittest.TestCase):
    def test_fixtures_regenerate_identically(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(os.path.join(TOOLS, "hsd_tel.py"), "synth", "-o", d)
            self.assertEqual(r.returncode, 0, r.stderr)
            for root, _dirs, files in os.walk(d):
                for f in files:
                    new = os.path.join(root, f)
                    old = os.path.join(FIXTURES, os.path.relpath(new, d))
                    self.assertTrue(os.path.exists(old), old)
                    self.assertTrue(filecmp.cmp(new, old, shallow=False), f"{old} differs from a fresh generation")


class TestModLint(unittest.TestCase):
    def test_mod_passes_loader_rules(self):
        r = run(os.path.join(PHASE1_TOOLS, "hsd_modlint.py"), MOD)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 error(s)", r.stdout)

    def test_broken_copy_fails(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad")
            shutil.copytree(MOD, bad)
            _write(os.path.join(bad, "scripts", "vscripts", "sh_utility.gnut"), "x\n")
            r = run(os.path.join(PHASE1_TOOLS, "hsd_modlint.py"), bad)
            self.assertEqual(r.returncode, 1)
            self.assertIn("outside namespace", r.stdout)


class TestVmCheck(unittest.TestCase):
    def _fake(self, d, mod_body):
        base = os.path.join(d, "base")
        os.makedirs(base)
        _write(os.path.join(base, "scripts.rson"), 
            'When: "SERVER"\nScripts:\n[\n\tsv_only.gnut\n]\n\nWhen: "SERVER || CLIENT"\nScripts:\n[\n\tsh_both.gnut\n]\n')
        _write(os.path.join(base, "sv_only.gnut"), 
            "global function ServerOnlyThing\nvoid function ServerOnlyThing() { NativeA() }\n")
        _write(os.path.join(base, "sh_both.gnut"), 
            "#if CLIENT\nvoid function F() { NativeClient(); x.MethodC() }\n#endif\n"
            "#if SERVER\nvoid function G() { y.MethodS(); int a = IN_SPEED }\n#endif\n"
            "#if DEVELOPER\nvoid function H() { DevOnly() }\n#endif\n")
        mod = os.path.join(d, "mod")
        os.makedirs(os.path.join(mod, "scripts", "vscripts"))
        _write(os.path.join(mod, "scripts", "vscripts", "scripts.rson"), 
            'When: "SERVER || CLIENT"\nScripts:\n[\n\tm__x.gnut\n]\n')
        _write(os.path.join(mod, "scripts", "vscripts", "m__x.gnut"), mod_body)
        return base, mod

    def test_flags_server_only_names_in_client_code(self):
        with tempfile.TemporaryDirectory() as d:
            base, mod = self._fake(d, "#if CLIENT\nvoid function M() { ServerOnlyThing(); int b = IN_SPEED }\n#endif\n"
                                      "#if SERVER\nvoid function N() { ServerOnlyThing(); NativeA() }\n#endif\n")
            r = run(os.path.join(TOOLS, "hsd_vmcheck.py"), mod, "--base", base)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("CLIENT: global 'ServerOnlyThing'", r.stdout)
            self.assertIn("CLIENT: const 'IN_SPEED'", r.stdout)
            self.assertNotIn("SERVER: global 'ServerOnlyThing'", r.stdout)

    def test_weak_evidence_and_strict(self):
        with tempfile.TemporaryDirectory() as d:
            base, mod = self._fake(d, "void function M() { DevOnly(); z.MethodC() }\n")
            r = run(os.path.join(TOOLS, "hsd_vmcheck.py"), mod, "--base", base)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("WEAK", r.stdout)
            r = run(os.path.join(TOOLS, "hsd_vmcheck.py"), mod, "--base", base, "--strict")
            self.assertEqual(r.returncode, 1, r.stdout)

    @unittest.skipUnless(os.path.isfile(os.path.join(BASE_SCRIPTS, "scripts.rson")),
                         "s21-platform base scripts not available (set HSD_BASE_SCRIPTS)")
    def test_real_mod_against_real_base(self):
        r = run(os.path.join(TOOLS, "hsd_vmcheck.py"), MOD, "--base", BASE_SCRIPTS, "--strict")
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        self.assertIn("0 error(s)", r.stdout)


if __name__ == "__main__":
    unittest.main()
