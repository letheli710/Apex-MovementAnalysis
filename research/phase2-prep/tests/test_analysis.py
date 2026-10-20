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
