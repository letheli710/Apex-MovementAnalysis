import math
import os
import shutil
import tempfile
import unittest

from _common import LOGS, FAULTY, FIXTURES
import hsd_tel
from hsdtel import analysis, derive, validate

TWO = os.path.join(FIXTURES, "two_sessions", "platform", "logs")


def mt_row(side, session, cmd, wall, x=0.0, ent=1, rank=0, line=0):
    return {"source": "MT", "side": side, "kind": "cmd", "session": session, "ent": ent, "cmd": cmd, "replay": 0,
            "buttons": 0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "pvx": 0.0, "pvy": 0.0, "pvz": 0.0,
            "ox": x, "oy": 0.0, "oz": 0.0, "pox": x, "poy": 0.0, "poz": 0.0,
            "file": f"{session}.log", "line_no": line, "_rank": rank, "wall": wall}


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


class TestJoin(unittest.TestCase):
    """Client/dedi pairing on (session, ent, reset batch, cmd), SYNTHETIC data."""

    def test_two_sessions_with_overlapping_cmds(self):
        _, rows, issues = hsd_tel.load([TWO])
        cl = [r for r in rows if r["source"] == "MT" and r["side"] == "cl"]
        sv = [r for r in rows if r["source"] == "MT" and r["side"] == "sv"]
        self.assertEqual({r["cmd"] for r in cl if r["session"].endswith("a-client")},
                         {r["cmd"] for r in cl if r["session"].endswith("b-client")})   # every cmd occurs twice
        self.assertTrue(all(r["drv_join"] == "ok" for r in cl + sv))
        for r in cl:
            p = r["_join"]
            self.assertEqual(p["session"][:16], r["session"][:16])                       # same recording
            self.assertAlmostEqual(p["ox"], r["ox"], delta=0.002)
            self.assertAlmostEqual(p["oy"], r["oy"], delta=0.002)
        # dedi rows inherit the run label of their own session's client rows (A = r1, B = r2)
        self.assertEqual({r["drv_run"] for r in sv if "-a-" in r["session"]}, {"r1"})
        self.assertEqual({r["drv_run"] for r in sv if "-b-" in r["session"]}, {"r2"})
        codes = {i.code: i for i in validate.validate(rows, issues)}
        self.assertNotIn("W_DUP_CMD", codes)
        self.assertNotIn("W_JOIN_AMBIGUOUS", codes)
        self.assertIn("(432/432; ambiguous 0)", codes["I_JOIN"].message)

    def test_missing_dedi_session_is_not_hidden_by_the_other(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(os.path.dirname(TWO), os.path.join(d, "platform"))
            shutil.rmtree(os.path.join(d, "platform", "logs", "server", "00000000-synth-b-server"))
            _, rows, issues = hsd_tel.load([d])
            js = derive.join_stats(rows)
            # a cmd-only join would count session B's commands as matched by session A's dedi lines (100 %)
            self.assertEqual((js["ok"], js["cl"]), (216, 432))
            codes = {i.code for i in validate.validate(rows, issues)}
            self.assertIn("W_JOIN_LOW", codes)
            smoke = {name: ok for name, ok, _ in analysis.smoke(rows, [])}
            self.assertFalse(smoke["client cmds with a dedi line >= 90%"])

    def test_counter_restart_starts_a_reset_batch(self):
        # one dedi process (one session) restarts the map; the clients are two processes
        rows = [mt_row("sv", "sv1", c, 10.0 + c * 0.01, x=c, line=c) for c in range(1, 21)]
        rows += [mt_row("sv", "sv1", c, 100.0 + c * 0.01, x=-c, line=100 + c) for c in range(1, 21)]
        rows += [mt_row("cl", "clA", c, 10.0 + c * 0.01, x=c, line=c) for c in range(1, 21)]
        rows += [mt_row("cl", "clB", c, 100.0 + c * 0.01, x=-c, line=c) for c in range(1, 21)]
        derive.derive(rows)
        sv = [r for r in rows if r["side"] == "sv"]
        self.assertEqual([r["drv_batch"] for r in sv], [0] * 20 + [1] * 20)
        self.assertTrue(all(r["drv_join"] == "ok" and r["_join"]["ox"] == r["ox"] for r in rows))
        codes = {i.code for i in validate.validate(rows, [])}
        self.assertIn("I_RESET_BATCH", codes)
        self.assertNotIn("W_DUP_CMD", codes)

    def test_forward_jump_starts_a_batch_only_after_a_reset_marker(self):
        def stream(with_marker):
            rows = [mt_row("sv", "s", c, 1.0 + c * 0.01, line=c) for c in range(1, 11)]
            rows += [mt_row("sv", "s", c, 5.0 + c * 0.01, line=c) for c in range(50, 61)]
            if with_marker:
                rows.append({"source": "LOG", "side": "sv", "kind": "map", "session": "s", "value": "mp_x",
                             "file": "s.log", "line_no": 20, "_rank": 0, "wall": 3.0})
            derive.derive(rows)
            return [r["drv_batch"] for r in rows if r["source"] == "MT"]
        self.assertEqual(stream(False), [0] * 21)                       # a burst gap alone keeps the batch
        self.assertEqual(stream(True), [0] * 10 + [1] * 11)

    def test_dedi_label_follows_the_joined_client_row(self):
        # the client leaves run 1 at wall 1.0; the dedi's hsd_md_run is never reset
        def run_mark(side, ses, run, wall):
            return {"source": "HSD", "side": side, "kind": "run", "session": ses, "run": float(run), "_ver": "2",
                    "file": "s.log", "line_no": 0, "_rank": 1, "wall": wall}
        rows = [run_mark("cl", "c", 1, 0.0), run_mark("cl", "c", 0, 1.0), run_mark("sv", "s", 1, 0.0)]
        rows += [mt_row("cl", "c", c, c * 0.1, line=c) for c in range(1, 20)]
        rows += [mt_row("sv", "s", c, c * 0.1 + 0.03, line=c) for c in range(1, 20)]
        derive.derive(rows)
        sv = [r for r in rows if r["source"] == "MT" and r["side"] == "sv"]
        self.assertEqual([r["drv_run"] for r in sv], ["r1"] * 9 + ["b0"] * 10)

    def test_several_dedi_entities(self):
        rows = [mt_row("cl", "c", 7, 1.0, x=10.0), mt_row("sv", "s", 7, 1.05, x=10.0, ent=1),
                mt_row("sv", "s", 7, 1.05, x=500.0, ent=2)]
        derive.derive(rows)
        self.assertEqual(rows[0]["drv_join"], "ok")
        self.assertIs(rows[0]["_join"], rows[1])                        # resolved by origin
        rows = [mt_row("cl", "c", 7, 1.0, x=10.0), mt_row("sv", "s", 7, 1.05, x=10.0, ent=1),
                mt_row("sv", "s", 7, 1.05, x=10.0, ent=2)]
        derive.derive(rows)
        self.assertEqual(rows[0]["drv_join"], "ambiguous")
        self.assertIn("W_JOIN_AMBIGUOUS", {i.code for i in validate.validate(rows, [])})

    def test_without_wall_clock_segments_pair_in_order(self):
        rows = [mt_row("cl", "a", c, None, x=c, rank=0, line=c) for c in range(1, 6)]
        rows += [mt_row("cl", "b", c, None, x=-c, rank=1, line=c) for c in range(1, 6)]
        rows += [mt_row("sv", "sa", c, None, x=c, rank=2, line=c) for c in range(1, 6)]
        rows += [mt_row("sv", "sb", c, None, x=-c, rank=3, line=c) for c in range(1, 6)]
        derive.derive(rows)
        self.assertTrue(all(r["drv_join"] == "ok" and r["_join"]["ox"] == r["ox"] for r in rows))


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
