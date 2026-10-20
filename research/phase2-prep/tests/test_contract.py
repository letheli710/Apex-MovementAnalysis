"""hsdmove-trial/2: side-explicit parameters, replay fields, strict checks and
usercmd alignment. All inputs are SYNTHETIC (hsdtel.synth)."""
import contextlib
import csv
import io
import json
import os
import shutil
import tempfile
import unittest

from _common import LOGS, FIXTURES
import hsd_tel
from hsdtel import contract, schema

TWO = os.path.join(FIXTURES, "two_sessions", "platform", "logs")


def _rewrite(path, fn):
    """Apply fn(rows) -> rows to a trial's samples.csv."""
    p = os.path.join(path, "samples.csv")
    with open(p, newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows = fn(rows)
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _copy(src, dst, fn=None):
    shutil.copytree(src, dst)
    if fn:
        _rewrite(dst, fn)
    return dst


def _main(*argv):
    """hsd_tel.main with its stdout swallowed; returns the exit code."""
    with contextlib.redirect_stdout(io.StringIO()):
        return hsd_tel.main(list(argv))


def _write_census(path, rows):
    cols = ["key", "cl_classvar", "cl_classvar_type", "cl_setting", "cl_setting_type", "sv_setting",
            "sv_setting_type", "readers", "differs"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(dict({c: "-" for c in cols[1:]}, **r))


class TestParametersSide(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, _ = hsd_tel.load([LOGS])

    def test_side_explicit_and_mismatch_reported(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "census.csv")
            _write_census(path, [
                {"key": "airSpeed", "cl_classvar": "40", "sv_setting": "45.000000", "differs": "1"},
                {"key": "speed", "cl_classvar": "173.5"},                 # client only
                {"key": "gravityScale", "sv_setting": "1.000000"},        # dedi only
            ])
            cl, cl_issues = contract.parameters_from_census(path, side="cl")
            self.assertEqual((cl["airSpeed"]["value"], cl["airSpeed"]["reader"]), ("40", "cl_classvar"))
            self.assertTrue(cl["airSpeed"]["side_mismatch"])
            self.assertEqual(cl["airSpeed"]["other_side_readings"], {"sv_setting": "45.000000"})
            self.assertNotIn("gravityScale", cl)                       # never filled in from the dedi
            self.assertTrue(any(i.startswith("airSpeed:") and "differs" in i for i in cl_issues), cl_issues)
            self.assertTrue(any(i.startswith("gravityScale: no cl reading") for i in cl_issues), cl_issues)
            sv, sv_issues = contract.parameters_from_census(path, side="sv")
            self.assertEqual((sv["airSpeed"]["value"], sv["airSpeed"]["side"]), ("45.000000", "sv"))
            self.assertNotIn("speed", sv)
            self.assertTrue(any(i.startswith("speed: no sv reading") for i in sv_issues), sv_issues)
            # a client trajectory refuses dedi parameters unless asked for explicitly
            with self.assertRaises(ValueError) as cm:
                contract.export_trial(self.rows, "r1", os.path.join(d, "t1"), parameters=sv)
            self.assertIn("same side", str(cm.exception))
            m, _ = contract.export_trial(self.rows, "r1", os.path.join(d, "t2"), parameters=sv,
                                         parameters_side="sv", parameter_issues=sv_issues)
            self.assertEqual(m["parameters_side"], "sv")
            self.assertEqual(contract.check_trial(os.path.join(d, "t2")), [])
            m, _ = contract.export_trial(self.rows, "r1", os.path.join(d, "t3"), parameters=cl,
                                         parameter_issues=cl_issues)
            self.assertEqual(m["parameter_issues"], cl_issues)

    def test_parameters_without_side_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                contract.export_trial(self.rows, "r1", d, parameters={"airSpeed": {"value": "40"}})

    def test_census_flags_client_vs_dedi(self):
        from hsdtel import analysis
        c = {r["key"]: r for r in analysis.census(self.rows)}
        # SYNTHETIC: client class var 40, client setting 45, dedi 40 -> cl_setting disagrees with the dedi
        self.assertEqual(c["airSpeed"]["cl_sv_differs"], 1)
        self.assertEqual(c["airAcceleration"]["cl_sv_differs"], 0)


class TestReplayFields(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, _ = hsd_tel.load([LOGS])
        cls.d = tempfile.mkdtemp()
        cls.m, cls.samples = contract.export_trial(cls.rows, "r2", os.path.join(cls.d, "r2"), source="synthetic",
                                                   course_note="SYNTHETIC flat plane")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_usercmd_per_sample(self):
        cl = {r["cmd"]: r for r in self.rows if r["source"] == "MT" and r["side"] == "cl" and not r["replay"]}
        cmds = [s["cmd"] for s in self.samples]
        self.assertEqual(cmds, list(range(cmds[0], cmds[0] + len(cmds))))  # one usercmd per SYNTH-1 frame
        self.assertTrue(all(s["n_cmds"] == 1 for s in self.samples))
        for s in self.samples:
            c = cl[s["cmd"]]
            self.assertEqual(s["buttons"], c["buttons"])
            self.assertEqual((s["pos_x"], s["pos_y"]), (round(c["pox"], 6), round(c["poy"], 6)))
            self.assertEqual(s["in_sprint"], int(bool(c["buttons"] & schema.IN_SPEED)))
        self.assertEqual(self.m["timing"]["frames_without_cmd"], 0)
        self.assertIn(f"{len(self.samples)}/{len(self.samples)} steps", self.m["timing"]["cmd_association"])

    def test_edges_from_buttons_and_axes(self):
        jumps = [s for s in self.samples if "JUMP" in s["pressed"].split("|")]
        self.assertEqual(len(jumps), 3)                                   # three jumps in r2
        self.assertTrue(all(s["in_jump"] == 1 for s in jumps))
        # releasing W for the air strafe: FORWARD bit and the forward axis go up, MOVERIGHT goes down
        first_air = next(s for s in self.samples if "MOVERIGHT" in s["pressed"])
        self.assertIn("AX_RIGHT", first_air["pressed"])
        self.assertIn("FORWARD", first_air["released"])
        self.assertIn("AX_FWD", first_air["released"])

    def test_initial_state_and_terrain(self):
        init = self.m["initial_state"]
        first = next(r for r in self.rows if r["source"] == "MT" and r["side"] == "cl" and not r["replay"]
                     and r["cmd"] == self.samples[0]["cmd"])
        self.assertEqual(init["cmd"], first["cmd"])
        self.assertEqual(init["pos"], [round(first[k], 6) for k in ("ox", "oy", "oz")])
        self.assertEqual(init["vel"], [round(first[k], 6) for k in ("vx", "vy", "vz")])
        self.assertEqual((init["grounded"], init["stance"]), (1, "standing"))
        self.assertEqual(init["inputs_held"], "")                         # r1 ends with no input held
        self.assertIn("the command before step 0", init["inputs_source"])
        self.assertEqual(self.samples[0]["pressed"], "FORWARD|AX_FWD")    # r2 starts by pressing W
        self.assertIn("yaw", init["angles"])
        t = self.m["terrain"]
        self.assertEqual(t["start_origin"], init["pos"])
        self.assertTrue(t["standable"])
        self.assertIsNone(t["ground_normal"])
        self.assertEqual(t["course_note"], "SYNTHETIC flat plane")
        self.assertEqual(t["map"], "")                                    # the main fixture has no level-load line

    def test_map_from_level_load_line(self):
        _, rows, _ = hsd_tel.load([TWO])
        with tempfile.TemporaryDirectory() as d:
            m, _ = contract.export_trial(rows, "r1", d)
            self.assertEqual(m["terrain"]["map"], "mp_synth_flat")
            self.assertEqual(m["session"], "00000000-synth-a-client")

    def test_load_roundtrip_and_v1_compat(self):
        m, samples = contract.load_trial(os.path.join(self.d, "r2"))
        self.assertEqual(m["contract"], "hsdmove-trial/2")
        self.assertEqual(int(samples[3]["cmd"]), self.samples[3]["cmd"])
        # a v1 trial (no usercmd/edge columns) still loads and checks against the v1 rules
        v1 = os.path.join(self.d, "v1")
        _copy(os.path.join(self.d, "r2"), v1,
              lambda rows: [{k: v for k, v in r.items() if k in contract.V1_COLUMNS} for r in rows])
        with open(os.path.join(v1, "trial.json")) as fh:
            man = json.load(fh)
        man["contract"] = "hsdmove-trial/1"
        for k in ("initial_state", "terrain", "parameters_side", "parameter_issues", "session"):
            man.pop(k)
        with open(os.path.join(v1, "trial.json"), "w") as fh:
            json.dump(man, fh)
        self.assertEqual(contract.check_trial(v1), [])
        m1, _ = contract.load_trial(v1)
        self.assertIsNone(m1["initial_state"])

    def test_cli_export_with_params_from_logs(self):
        out = os.path.join(self.d, "cli")
        r = _main("export-contract", LOGS, "--run", "r1", "-o", out, "--params", "logs", "--course-note", "SYNTHETIC")
        self.assertEqual(r, 0)
        with open(os.path.join(out, "trial.json")) as fh:
            m = json.load(fh)
        self.assertEqual(m["source"], "synthetic")
        self.assertEqual(m["parameters"]["airSpeed"]["reader"], "cl_classvar")
        self.assertEqual(_main("check-contract", out), 0)


class TestStrictChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, _ = hsd_tel.load([LOGS])
        cls.d = tempfile.mkdtemp()
        cls.ref = os.path.join(cls.d, "ref")
        contract.export_trial(cls.rows, "r1", cls.ref, source="synthetic")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def _bad(self, name, fn):
        return contract.check_trial(_copy(self.ref, os.path.join(self.d, name), fn))

    def _set(self, i, **kw):
        def fn(rows):
            rows[i].update({k: str(v) for k, v in kw.items()})
            return rows
        return fn

    def test_reference_is_clean(self):
        self.assertEqual(contract.check_trial(self.ref), [])

    def test_duplicate_and_backwards_time(self):
        def dup(rows):
            rows[5]["t"] = rows[4]["t"]
            return rows
        self.assertTrue(any(p.startswith("duplicate t: 1 row(s) (first: 5)") for p in self._bad("dupt", dup)))
        p = self._bad("backt", self._set(7, t=0.0))
        self.assertTrue(any(x.startswith("t goes backwards") for x in p), p)

    def test_dt_must_match_t(self):
        p = self._bad("dt", self._set(9, dt=0.5))
        self.assertTrue(any(x.startswith("dt differs from the t difference") for x in p), p)

    def test_cmd_duplicates_and_gaps(self):
        def dup(rows):
            rows[10]["cmd"] = rows[9]["cmd"]
            return rows

        def gap(rows):
            for r in rows[20:]:
                r["cmd"] = str(int(r["cmd"]) + 3)   # three usercmds missing before row 20
            return rows
        self.assertTrue(any(x.startswith("duplicate cmd") for x in self._bad("dupc", dup)))
        p = self._bad("gapc", gap)
        self.assertTrue(any(x.startswith("cmd gap (usercmds missing between steps): 1 row(s) (first: 20)") for x in p), p)

    def test_input_completeness(self):
        p = self._bad("noin", self._set(12, in_yaw=""))
        self.assertTrue(any(x.startswith("input missing (in_yaw)") for x in p), p)

        def drop_col(rows):
            return [{k: v for k, v in r.items() if k != "in_sprint"} for r in rows]
        self.assertIn("missing input column in_sprint", self._bad("nocol", drop_col))

    def test_missing_edges(self):
        def lose(rows):
            i = next(k for k, r in enumerate(rows) if r["pressed"])
            rows[i]["pressed"] = ""
            return rows
        p = self._bad("noedge", lose)
        self.assertTrue(any(x.startswith("missing input edge") for x in p), p)

        def spurious(rows):
            rows[3]["pressed"] = "JUMP"
            return rows
        p = self._bad("spur", spurious)
        self.assertTrue(any(x.startswith("spurious input edge") for x in p), p)


class TestAlignment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, rows, _ = hsd_tel.load([LOGS])
        cls.d = tempfile.mkdtemp()
        cls.ref = os.path.join(cls.d, "ref")
        contract.export_trial(rows, "r2", cls.ref, source="synthetic")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d)

    def test_identical_passes_aligned_by_cmd(self):
        res = contract.compare_trials(self.ref, self.ref)
        self.assertTrue(res["pass"])
        self.assertEqual(res["alignment"]["by"], "cmd")

    def test_shorter_test_trial_fails_instead_of_truncating(self):
        short = _copy(self.ref, os.path.join(self.d, "short"), lambda rows: rows[:-5])
        res = contract.compare_trials(self.ref, short)
        self.assertFalse(res["pass"])
        self.assertFalse(res["checks"]["alignment"])
        self.assertIn("only in ref: 5", res["alignment"]["message"])
        self.assertNotIn("pos_rms_u", res)                                # no metrics on a truncated overlap

    def test_length_mismatch_without_cmds(self):
        def strip(rows):
            for r in rows:
                r["cmd"] = ""
            return rows
        a = _copy(self.ref, os.path.join(self.d, "nocmd_a"), strip)
        b = _copy(self.ref, os.path.join(self.d, "nocmd_b"), lambda rows: strip(rows)[1:])
        res = contract.compare_trials(a, b)
        self.assertFalse(res["pass"])
        self.assertEqual(res["alignment"]["by"], "step")
        self.assertIn("length mismatch", res["alignment"]["message"])

    def test_same_length_but_shifted_usercmds_fails(self):
        def shift(rows):
            # drop the first step and append a copy of the last: same length, different usercmds
            extra = dict(rows[-1])
            extra["cmd"] = str(int(extra["cmd"]) + 1)
            rows = rows[1:] + [extra]
            for i, r in enumerate(rows):
                r["step"] = str(i)
            return rows
        res = contract.compare_trials(self.ref, _copy(self.ref, os.path.join(self.d, "shift"), shift))
        self.assertFalse(res["pass"])
        self.assertIn("usercmd sequences differ", res["alignment"]["message"])

    def test_cli_exit_code(self):
        short = os.path.join(self.d, "short_cli")
        _copy(self.ref, short, lambda rows: rows[:-1])
        self.assertEqual(_main("compare-contracts", self.ref, short), 3)


if __name__ == "__main__":
    unittest.main()
