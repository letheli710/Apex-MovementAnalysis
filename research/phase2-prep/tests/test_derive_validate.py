import math
import unittest

from _common import LOGS, FAULTY
import hsd_tel
from hsdtel import derive, validate


class TestDerive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.rows, cls.issues = hsd_tel.load([LOGS])

    def test_dt_est_matches_synthetic_frametime(self):
        # SYNTH-1 integrates origin += post velocity * frametime, so dt_est is exact
        # up to the 3-decimal printing of positions (relative error ~0.0005 u / displacement).
        dts = [r["drv_dt_est"] for r in self.rows if r["source"] == "MT" and r.get("drv_dt_est")
               and r["side"] == "cl" and not r["replay"] and r["ground"] == 1 and r["drv_spd2d_post"] > 100]
        self.assertGreater(len(dts), 500)
        for dt in dts:
            self.assertAlmostEqual(dt, 1 / 144.0, delta=2e-5)

    def test_spd_and_heading(self):
        r = next(r for r in self.rows if r["source"] == "MT" and r.get("drv_dheading") not in (None, 0.0)
                 and abs(r["drv_dheading"]) > 0.1)
        self.assertAlmostEqual(r["drv_spd2d"], math.hypot(r["vx"], r["vy"]))
        self.assertTrue(-180.0 <= r["drv_dheading"] <= 180.0)

    def test_pressed_edges_and_runs(self):
        cl = [r for r in self.rows if r["source"] == "MT" and r["side"] == "cl" and not r["replay"]]
        jumps = [r for r in cl if derive.jump_press(r)]
        self.assertEqual(len(jumps), 6)                      # 3 jumps in r2, 3 in r3
        self.assertEqual({r["drv_run"] for r in cl}, {"r1", "r2", "r3"})
        sv = [r for r in self.rows if r["source"] == "MT" and r["side"] == "sv"]
        cl_runs = {r["cmd"]: r["drv_run"] for r in cl}
        self.assertTrue(all(r["drv_run"] == cl_runs[r["cmd"]] for r in sv))

    def test_wish_yaw(self):
        r = next(r for r in self.rows if r["source"] == "HSD" and r.get("ax_right") == 1.0 and r.get("ax_fwd") == 0.0)
        self.assertAlmostEqual(r["drv_wish_yaw"], r["yaw"] - 90.0)

    def test_bursts_split_on_command_gap(self):
        rows = [{"source": "MT", "side": "cl", "kind": "cmd", "ent": 1, "cmd": c, "replay": 0, "buttons": 0,
                 "vx": 0.0, "vy": 0.0, "vz": 0.0, "pvx": 0.0, "pvy": 0.0, "pvz": 0.0,
                 "ox": 0.0, "oy": 0.0, "oz": 0.0, "pox": 0.0, "poy": 0.0, "poz": 0.0,
                 "file": "x", "line_no": i, "_rank": 0, "wall": None}
                for i, c in enumerate([1, 2, 3, 50, 51, 52])]
        derive.derive(rows)
        self.assertEqual([r["drv_burst"] for r in rows], [0, 0, 0, 1, 1, 1])
        self.assertEqual([r["drv_run"] for r in rows], ["b0", "b0", "b0", "b1", "b1", "b1"])


class TestValidate(unittest.TestCase):
    def test_clean_fixture_has_no_errors_or_warnings(self):
        _, rows, issues = hsd_tel.load([LOGS])
        s = validate.summarize(validate.validate(rows, issues))
        self.assertEqual((s["errors"], s["warnings"]), (0, 0), s)

    def test_faulty_fixture_flags_every_injected_defect(self):
        _, rows, issues = hsd_tel.load([FAULTY])
        codes = {i.code for i in validate.validate(rows, issues)}
        expected = {"E_MALFORMED_MT", "E_NONFINITE", "W_TELEPORT", "W_SEQ_GAP", "E_MISSING_FIELD",
                    "W_API_MISSING", "W_SCRIPT_ERROR"}
        self.assertTrue(expected <= codes, expected - codes)

    def test_empty_input(self):
        codes = {i.code for i in validate.validate([], [])}
        self.assertIn("I_NO_MT", codes)
        self.assertIn("I_NO_HSD", codes)


if __name__ == "__main__":
    unittest.main()
