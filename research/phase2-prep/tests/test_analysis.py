"""Fitters must recover the SYNTH-1 parameters. These are synthetic numbers by
construction and say nothing about Apex."""
import math
import random
import unittest
import xml.etree.ElementTree as ET

from _common import LOGS
import hsd_tel
from hsdtel import analysis, plot
from hsdtel.synth import P


class TestFits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, _ = hsd_tel.load([LOGS])

    def _ground(self, source, side):
        fits = {g["drv_run"]: g for g in analysis.fit_ground(self.rows, source, side)}
        return fits["r1"]

    def test_ground_accel_linear_recovered(self):
        for source, side in (("HSD", "cl"), ("MT", "cl"), ("MT", "sv")):
            g = self._ground(source, side)["accel"]
            self.assertEqual(g["best"], "linear", (source, side))
            self.assertTrue(g["good"])
            self.assertAlmostEqual(g["models"]["linear"]["a"], P["ground_accel"], delta=0.01 * P["ground_accel"])
            self.assertAlmostEqual(g["vmax"], P["wish_ground"], delta=0.5)

    def test_ground_friction_recovered(self):
        for source, side in (("HSD", "cl"), ("MT", "sv")):
            d = self._ground(source, side)["decel"]
            self.assertEqual(d["best"], "friction")
            self.assertTrue(d["good"])
            self.assertAlmostEqual(d["models"]["friction"]["k"], P["friction_k"], delta=0.05 * P["friction_k"])
            self.assertAlmostEqual(d["models"]["friction"]["stopspeed"], P["stopspeed"], delta=0.1 * P["stopspeed"])

    def test_air_recovered_and_forms_indistinguishable_with_keyboard(self):
        res = analysis.fit_air(analysis.air_samples(self.rows, "cl"))
        self.assertTrue(res["ok"])
        flat = res["forms"]["flat"]
        self.assertAlmostEqual(flat["cap"], P["air_cap"], delta=0.02 * P["air_cap"])
        self.assertAlmostEqual(flat["accel"], P["air_accel"], delta=0.02 * P["air_accel"])
        self.assertLess(flat["rms"], 0.1 * res["rms_no_accel"])
        self.assertEqual(res["best"], "indistinguishable")

    def test_air_forms_separate_with_varying_wish(self):
        rng = random.Random(7)
        samples, vx, vy, yaw = [], 300.0, 0.0, 0.0
        for _ in range(400):
            mag = rng.uniform(0.2, 1.0) * 300.0
            yaw -= 1.25
            wy = yaw - 90.0
            nx, ny = analysis._air_step(vx, vy, wy, mag, 1 / 144.0, 40.0, 2400.0, "flat")
            samples.append((vx, vy, nx, ny, wy, mag, 1 / 144.0))
            vx, vy = nx, ny
        res = analysis.fit_air(samples)
        self.assertEqual(res["best"], "flat")

    def test_vertical(self):
        v = analysis.fit_vertical(self.rows, "cl")[0]
        self.assertAlmostEqual(v["gravity_median"], P["gravity"], delta=0.005 * P["gravity"])
        # SYNTH-1 applies no gravity on the jump command itself.
        self.assertAlmostEqual(v["takeoff_vz_median"], P["jump_vz"], delta=0.01)

    def test_events_and_hops(self):
        ev = analysis.events(self.rows)
        mt_cl = [e for e in ev if e["source"] == "MT" and e["side"] == "cl"]
        self.assertEqual(sum(e["event"] == "TAKEOFF" for e in mt_cl), 6)
        self.assertEqual(sum(e["event"] == "LAND" for e in mt_cl), 6)
        self.assertEqual(sum(e["event"] == "SLIDE_START" for e in mt_cl), 1)
        self.assertEqual(sum(e["event"] == "SLIDE_END" for e in mt_cl), 1)
        sv_evt = [e for e in ev if e["event"].startswith("SV_")]
        self.assertEqual(sum(e["event"] == "SV_JUMP" for e in sv_evt), 6)
        hops = analysis.hops(self.rows)
        self.assertEqual(len(hops), 4)   # r2: 2 relandings + r3: wait 0/2 frames (5 frames > ... still < 0.5 s)
        self.assertTrue(all(h["ground_time"] < 0.06 for h in hops))

    def test_summary_and_compare(self):
        summ = analysis.run_summary(self.rows)
        runs = {(r["source"], r["side"], r["drv_run"]) for r in summ}
        self.assertIn(("HSD", "cl", "r2"), runs)
        cmp_rows = analysis.compare(summ, "r1")
        m = next(c for c in cmp_rows if c["source"] == "HSD" and c["run"] == "r2" and c["metric"] == "max_spd2d")
        self.assertGreater(m["delta"], 200)   # strafing gained speed in r2


class TestSlidesAndSmoke(unittest.TestCase):
    def test_slide_decel_recovered(self):
        _, rows, _ = hsd_tel.load([LOGS])
        sl = analysis.slides(rows)
        self.assertEqual(len(sl), 3)                     # MT cl, HSD cl, MT sv
        for r in sl:
            self.assertAlmostEqual(r["mean_decel"], P["slide_decel"], delta=0.01 * P["slide_decel"])

    def test_smoke_passes_on_clean_and_fails_on_faulty(self):
        from _common import FAULTY
        from hsdtel import validate
        _, rows, iss = hsd_tel.load([LOGS])
        self.assertTrue(all(ok for _, ok, _ in analysis.smoke(rows, validate.validate(rows, iss))))
        _, rows, iss = hsd_tel.load([FAULTY])
        failed = [n for n, ok, _ in analysis.smoke(rows, validate.validate(rows, iss)) if not ok]
        self.assertIn("validation errors == 0", failed)
        self.assertIn("MT dedi rows", failed)


class TestCensus(unittest.TestCase):
    def test_census_merges_readers_and_flags_differences(self):
        _, rows, _ = hsd_tel.load([LOGS])
        c = {r["key"]: r for r in analysis.census(rows)}
        self.assertEqual(c["airAcceleration"]["readers"], 3)
        self.assertEqual(c["airAcceleration"]["differs"], 0)
        self.assertEqual(c["airSpeed"]["differs"], 1)          # injected: client dump 45 vs 40
        self.assertEqual(c["doubleJump"]["differs"], 0)        # "false" == 0
        self.assertEqual(c["dodgeSpeed"]["readers"], 0)
        self.assertEqual(c["dodgeSpeed"]["cl_classvar_type"], "unknown")


class TestContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, _ = hsd_tel.load([LOGS])

    def test_export_check_compare(self):
        import tempfile, csv, os
        from hsdtel import contract
        with tempfile.TemporaryDirectory() as d:
            for run in ("r1", "r2", "r3"):
                m, samples = contract.export_trial(self.rows, run, os.path.join(d, run), source="synthetic")
                self.assertEqual(contract.check_trial(os.path.join(d, run)), [], run)
                self.assertEqual(m["contract"], "hsdmove-trial/2")
            same = contract.compare_trials(os.path.join(d, "r2"), os.path.join(d, "r2"))
            self.assertTrue(same["pass"])
            self.assertEqual(same["pos_rms_u"], 0.0)
            # perturb: shift positions by 10 u and drop the first LAND event
            path = os.path.join(d, "r2", "samples.csv")
            with open(path, newline="") as fh:
                rows = list(csv.DictReader(fh))
            dropped = False
            for r in rows:
                r["pos_x"] = str(float(r["pos_x"]) + 10.0)
                if "LAND" in r["events"] and not dropped:
                    r["events"] = ""
                    dropped = True
            os.makedirs(os.path.join(d, "bad"))
            with open(os.path.join(d, "bad", "samples.csv"), "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            with open(os.path.join(d, "r2", "trial.json")) as src, open(os.path.join(d, "bad", "trial.json"), "w") as dst:
                dst.write(src.read())
            res = contract.compare_trials(os.path.join(d, "r2"), os.path.join(d, "bad"))
            self.assertFalse(res["pass"])
            self.assertFalse(res["checks"]["pos_rms_u"])
            self.assertFalse(res["checks"]["events"])
            self.assertTrue(res["checks"]["vel_rms_ups"])

    def test_parameters_from_census(self):
        import tempfile, os, csv
        from hsdtel import contract
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "census.csv")
            rows = analysis.census(self.rows)
            with open(path, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["cl_setting", "cl_setting_type"],
                                   extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)
            params, issues = contract.parameters_from_census(path)
            # client trajectory -> client readers; the class var wins over the client setting
            self.assertEqual(params["airSpeed"]["side"], "cl")
            self.assertEqual(params["airSpeed"]["reader"], "cl_classvar")
            self.assertEqual(params["airSpeed"]["value"], "40")
            self.assertTrue(params["airSpeed"]["differs_between_readers"])
            self.assertEqual(params["airSpeed"]["same_side_readings"], {"cl_setting": "45.000000"})
            self.assertFalse(params["airSpeed"]["side_mismatch"])
            self.assertNotIn("dodgeSpeed", params)
            self.assertEqual(issues, [])
            m, _ = contract.export_trial(self.rows, "r1", os.path.join(d, "t"), parameters=params)
            self.assertIn("airAcceleration", m["parameters"])
            self.assertEqual(m["parameters_side"], "cl")

    def test_dt_matches_frametime(self):
        import tempfile, os
        from hsdtel import contract
        with tempfile.TemporaryDirectory() as d:
            _, samples = contract.export_trial(self.rows, "r1", d)
            for s in samples[1:]:
                self.assertAlmostEqual(s["dt"], 1 / 144.0, delta=2e-5)

    def test_missing_run_is_a_clear_error(self):
        import tempfile
        from hsdtel import contract
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as cm:
                contract.export_trial(self.rows, "r99", d)
            self.assertIn("hsd_md_cl_trace", str(cm.exception))

    def test_unity_axes(self):
        from hsdtel import contract
        # Source +Y is "left"; Unity +X is "right" -> left maps to -X.
        self.assertEqual(contract.to_unity_position(0, 1, 0), (-0.0254, 0.0, 0.0))
        self.assertEqual(contract.to_unity_position(1, 0, 0), (0.0, 0.0, 0.0254))
        self.assertEqual(contract.to_unity_position(0, 0, 1), (-0.0, 0.0254, 0.0))
        self.assertEqual(contract.to_unity_yaw(90.0), -90.0)


class TestPlot(unittest.TestCase):
    def test_svg_is_well_formed(self):
        svg = plot.svg_plot([("r1", [(0, 0), (1, 300)]), ("r<2>", [(0, 10), (1, float("nan")), (2, 5)])],
                            title="t & <x>", xlabel="s", ylabel="u/s", markers=[(0.5, "JUMP")])
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("r&lt;2&gt;", svg)

    def test_nice_ticks_degenerate(self):
        self.assertTrue(plot._nice_ticks(5.0, 5.0))
        self.assertTrue(math.isfinite(plot._nice_ticks(0.0, 1e-9)[-1]))


if __name__ == "__main__":
    unittest.main()
