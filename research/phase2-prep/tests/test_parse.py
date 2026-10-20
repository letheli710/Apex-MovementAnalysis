import math
import os
import tempfile
import unittest

from _common import LOGS  # noqa: F401  (sets sys.path)
from hsdtel import parse

MT = ("[MOVE-TRACE] cmd=100 ent=1 ms=300.000 spr=1 duck=0 slide=0 ge=0 fwd=1.000 sd=0.000 b=0000000A "
      "msc=1.0000 o=0.000 0.000 0.000 v=300.000 0.000 0.000 po=4.000 0.200 -0.100 pv=301.000 10.000 -12.500")


def _write(path, text, lines=False):
    with open(path, "w", newline="\n") as fh:
        if lines:
            fh.writelines(text)
        else:
            fh.write(text)


class TestLines(unittest.TestCase):
    def test_mt_basic(self):
        r = parse.parse_trace(MT)
        self.assertEqual(r["cmd"], 100)
        self.assertEqual(r["buttons"], 0x0A)
        self.assertEqual(r["ground"], 0)
        self.assertEqual(r["replay"], 0)
        self.assertAlmostEqual(r["pvy"], 10.0)

    def test_mt_replay_and_prefixes(self):
        wall, side, rest = parse.split_prefix("[2026-10-21 10:00:01.250] Native(C): " + MT + " rp=1\r\n")
        self.assertEqual(side, "cl")
        self.assertAlmostEqual(wall % 86400, 36001.25, places=3)
        r = parse.parse_trace(rest)
        self.assertEqual(r["replay"], 1)

    def test_ansi_console(self):
        raw = "\x1b[38;2;059;120;218mNative(S): \x1b[38;2;204;204;204m" + MT + "\x1b[0m"
        wall, side, rest = parse.split_prefix(raw)
        self.assertIsNone(wall)
        self.assertEqual(side, "sv")
        self.assertIsNotNone(parse.parse_trace(rest))

    def test_nonfinite_spellings(self):
        for spelling in ("-nan(ind)", "nan", "-nan", "inf", "-inf", "1.#INF00", "-1.#IND00", "1.#QNAN0"):
            line = MT.replace("v=300.000 ", f"v={spelling} ")
            r = parse.parse_trace(line)
            self.assertIsNotNone(r, spelling)
            self.assertFalse(math.isfinite(r["vx"]), spelling)

    def test_truncated_mt_is_rejected(self):
        self.assertIsNone(parse.parse_trace(MT[:MT.index(" po=")]))

    def test_hsd_v2_frame(self):
        line = ("[HSD-MD] ver=2 side=cl kind=frame run=3 seq=17 t=12.5000 ft=0.00694 o=1.000,2.000,3.000 "
                "vel=100.000,0.000,-5.000 spd2d=100.000 vz=-5.000 ground=0 slide=-1 sprint=1 crouch=0 "
                "ang=-1.000,90.000 in_jump=1 in_duck=0 in_fwd=1 ax_fwd=1.000 ax_right=-0.500")
        r, problem = parse.parse_hsd(line)
        self.assertIsNone(problem)
        self.assertEqual((r["side"], r["kind"], r["run"], r["seq"]), ("cl", "frame", 3.0, 17.0))
        self.assertEqual((r["vx"], r["vz"], r["yaw"], r["slide"], r["ax_right"]), (100.0, -5.0, 90.0, -1.0, -0.5))

    def test_hsd_v1_land_maps_ing_columns(self):
        line = ("CLIENT: [HSD-MD] side=cl kind=land t=12.5000 airtime=0.6100 takeoff=320.00 peak=335.10 "
                "land=330.00 gain=10.00 hop=2 spd2d=330.00 vz=0.00 v=1,2,3 o=4,5,6 ground=1 slide=0")
        r, problem = parse.parse_hsd(line)
        self.assertIsNone(problem)
        self.assertEqual(r["_ver"], "1")
        self.assertEqual((r["ing_airtime"], r["ing_gain"], r["vx"], r["oz"]), (0.61, 10.0, 1.0, 6.0))

    def test_hsd_msg_takes_rest_of_line(self):
        r, problem = parse.parse_hsd("[HSD-MD] ver=2 side=sv kind=error run=0 seq=4 where=dump count=1 "
                                     "msg=the index 'GetPlayerSettingInt' does not exist")
        self.assertIsNone(problem)
        self.assertEqual(r["msg"], "the index 'GetPlayerSettingInt' does not exist")
        self.assertEqual(r["where"], "dump")

    def test_hsd_bad_vector(self):
        _, problem = parse.parse_hsd("[HSD-MD] ver=2 side=cl kind=frame run=0 seq=1 t=1 o=1,2 vel=1,2,3 ground=1")
        self.assertIn("o=", problem)


class TestFiles(unittest.TestCase):
    def test_rotated_order(self):
        with tempfile.TemporaryDirectory() as d:
            for n in ("message.log", "message.1.log", "message.2.log", "script.log"):
                open(os.path.join(d, n), "w").close()
            names = [os.path.basename(p) for p in parse.expand_inputs([d])]
            self.assertEqual(names, ["message.2.log", "message.1.log", "message.log", "script.log"])

    def test_side_from_path_when_no_prefix(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "server", "x.log")
            os.makedirs(os.path.dirname(p))
            _write(p, MT + "\n")
            rows, issues = parse.parse_file(p)
            self.assertEqual(rows[0]["side"], "sv")
            self.assertEqual(issues, [])

    def test_side_unknown_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.log")
            _write(p, MT + "\n")
            rows, issues = parse.parse_file(p)
            self.assertEqual(rows[0]["side"], "unknown")
            self.assertEqual([i.code for i in issues], ["W_SIDE_UNKNOWN"])

    def test_fixture_counts(self):
        files, rows, issues = parse.parse_inputs([LOGS])
        self.assertEqual(len(files), 4)
        self.assertEqual(issues, [])
        mt = [r for r in rows if r["source"] == "MT"]
        self.assertEqual(sum(1 for r in mt if r["side"] == "cl" and not r["replay"]), 2070)
        self.assertEqual(sum(1 for r in mt if r["side"] == "sv"), 2070)
        self.assertEqual(sum(1 for r in mt if r["replay"]), 41)


if __name__ == "__main__":
    unittest.main()
