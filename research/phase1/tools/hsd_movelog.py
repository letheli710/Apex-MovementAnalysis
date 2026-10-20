#!/usr/bin/env python3
"""Parse R5Flowstate movement logs into CSV and per-airtime summaries.

Inputs it understands:
  [MOVE-TRACE] ...  per-command FullWalkMove dump of the SDK
                    (s21-r5sdk/src/game/server/move_sim_trace.cpp:220-232,
                     s21-r5sdk/src/game/client/move_sim_trace.cpp:189-198)
  [HSD-MD] ...      key=value lines of the HSD.MoveDiag mod

Subcommands:
  trace   <log> -o out.csv   one row per [MOVE-TRACE] line plus derived columns
  air     <log> -o out.csv   one row per airborne segment of a [MOVE-TRACE] log
  hsd     <log> -o out.csv   one row per [HSD-MD] line (union of keys)
  selftest                   run the built-in checks on synthetic lines

Standard library only. Read-only on its inputs.
"""
import argparse
import csv
import math
import re
import sys

# in_buttons.h:17-43
BUTTONS = {
    "ATTACK": 1 << 0, "JUMP": 1 << 1, "DUCK": 1 << 2, "FORWARD": 1 << 3, "BACK": 1 << 4,
    "USE": 1 << 5, "MOVELEFT": 1 << 9, "MOVERIGHT": 1 << 10, "ATTACK2": 1 << 11,
    "SPEED": 1 << 17, "DODGE": 1 << 28,
}
# tapstrafe.cpp:26 -- IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT
LURCH_MASK = 0x618

# MSVC prints NaN/Inf as "-nan(ind)", "nan", "inf" (or "1.#INF" on old CRTs).
_F = r"(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?|-?nan(?:\([a-z]+\))?|-?inf|-?1\.#(?:INF|IND|QNAN)\d*)"
TRACE_RE = re.compile(
    r"\[MOVE-TRACE\] cmd=(-?\d+) ent=(-?\d+) ms=" + _F + r" spr=(\d+) duck=(-?\d+) slide=(\d+) ge=(\d+) "
    r"fwd=" + _F + r" sd=" + _F + r" b=([0-9A-Fa-f]{8}) msc=" + _F +
    r" o=" + _F + " " + _F + " " + _F + r" v=" + _F + " " + _F + " " + _F +
    r" po=" + _F + " " + _F + " " + _F + r" pv=" + _F + " " + _F + " " + _F + r"( rp=1)?")
HSD_RE = re.compile(r"\[HSD-MD\](.*)$")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)")


def _num(text):
    t = text.lower()
    if "nan" in t or "#ind" in t or "#qnan" in t:
        return float("nan")
    if "inf" in t:
        return float("-inf") if t.startswith("-") else float("inf")
    return float(t)


def button_names(mask):
    return "|".join(n for n, b in BUTTONS.items() if mask & b)


def parse_trace_line(line):
    m = TRACE_RE.search(line)
    if not m:
        return None
    g = m.groups()
    f = [_num(x) for x in g[2:3]]  # ms
    row = {
        "cmd": int(g[0]), "ent": int(g[1]), "maxspeed": f[0],
        "sprint": int(g[3]), "duck": int(g[4]), "slide": int(g[5]), "ground": int(g[6]),
        "fwd": _num(g[7]), "side": _num(g[8]), "buttons": int(g[9], 16), "movescale": _num(g[10]),
    }
    o = [_num(x) for x in g[11:14]]
    v = [_num(x) for x in g[14:17]]
    po = [_num(x) for x in g[17:20]]
    pv = [_num(x) for x in g[20:23]]
    row.update(ox=o[0], oy=o[1], oz=o[2], vx=v[0], vy=v[1], vz=v[2],
               pox=po[0], poy=po[1], poz=po[2], pvx=pv[0], pvy=pv[1], pvz=pv[2],
               replay=1 if g[23] else 0)
    return row


def derive(rows):
    """Adds per-command derived columns. The trace carries no frametime, so dt is
    estimated from displacement over mean speed and left blank when slow."""
    prev = None
    for r in rows:
        s0 = math.hypot(r["vx"], r["vy"])
        s1 = math.hypot(r["pvx"], r["pvy"])
        r["spd2d_pre"] = round(s0, 4)
        r["spd2d_post"] = round(s1, 4)
        r["dspd2d"] = round(s1 - s0, 4)
        if s0 > 1.0 and s1 > 1.0:
            a0 = math.atan2(r["vy"], r["vx"])
            a1 = math.atan2(r["pvy"], r["pvx"])
            d = math.degrees((a1 - a0 + math.pi) % (2 * math.pi) - math.pi)
            r["dheading_deg"] = round(d, 4)
        else:
            r["dheading_deg"] = ""
        disp = math.dist((r["ox"], r["oy"], r["oz"]), (r["pox"], r["poy"], r["poz"]))
        vmean = (math.dist((0, 0, 0), (r["vx"], r["vy"], r["vz"])) +
                 math.dist((0, 0, 0), (r["pvx"], r["pvy"], r["pvz"]))) / 2.0
        r["dt_est"] = round(disp / vmean, 5) if vmean > 50.0 else ""
        # The first line has no predecessor, so its press edges are unknown (0).
        pressed = (r["buttons"] & ~prev["buttons"]) if prev else 0
        r["pressed"] = pressed
        r["pressed_names"] = button_names(pressed)
        r["buttons_names"] = button_names(r["buttons"])
        r["dir_press_air"] = 1 if (pressed & LURCH_MASK) and not r["ground"] else 0
        prev = r
    return rows


def air_segments(rows):
    """One summary per run of ground=0 commands (pre-move ground flag)."""
    segs, cur = [], None
    for r in rows:
        if r["ground"] == 0:
            if cur is None:
                cur = {"cmd_start": r["cmd"], "n": 0, "takeoff_spd": r["spd2d_pre"], "peak_spd": 0.0,
                       "dir_presses": 0, "max_abs_dheading": 0.0, "max_dspd": -1e9, "slide_at_takeoff": r["slide"]}
            cur["n"] += 1
            cur["peak_spd"] = max(cur["peak_spd"], r["spd2d_post"])
            cur["dir_presses"] += r["dir_press_air"]
            if r["dheading_deg"] != "":
                cur["max_abs_dheading"] = max(cur["max_abs_dheading"], abs(r["dheading_deg"]))
            cur["max_dspd"] = max(cur["max_dspd"], r["dspd2d"])
            cur["cmd_end"] = r["cmd"]
            cur["land_spd"] = r["spd2d_post"]
        elif cur is not None:
            cur["gain"] = round(cur["land_spd"] - cur["takeoff_spd"], 4)
            segs.append(cur)
            cur = None
    if cur is not None:
        cur["gain"] = round(cur["land_spd"] - cur["takeoff_spd"], 4)
        cur["open"] = 1
        segs.append(cur)
    return segs


def parse_hsd_line(line):
    m = HSD_RE.search(line)
    if not m:
        return None
    row = dict(KV_RE.findall(m.group(1)))
    if "label" in row:
        row["label"] = re.sub(r"[^A-Za-z0-9_-]", "", row["label"])
    return row


def write_csv(rows, path, fieldnames=None):
    if fieldnames is None:
        fieldnames = []
        for r in rows:
            for k in r:
                if k not in fieldnames:
                    fieldnames.append(k)
    out = open(path, "w", newline="") if path != "-" else sys.stdout
    w = csv.DictWriter(out, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    if out is not sys.stdout:
        out.close()


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.readlines()


def load_trace(path, keep_replays):
    rows = [r for r in (parse_trace_line(l) for l in read_lines(path)) if r]
    if not keep_replays:
        rows = [r for r in rows if not r["replay"]]
    return derive(rows)


def selftest():
    sv = ("[MOVE-TRACE] cmd=100 ent=1 ms=300.000 spr=1 duck=0 slide=0 ge=0 fwd=1.000 sd=0.000 b=0000000A "
          "msc=1.0000 o=0.000 0.000 0.000 v=300.000 0.000 0.000 po=4.000 0.200 -0.100 pv=301.000 10.000 -12.500")
    cl = sv.replace("cmd=100", "cmd=101").replace("b=0000000A", "b=0000020A") + " rp=1"
    gnd = sv.replace("cmd=100", "cmd=102").replace("ge=0", "ge=1")
    rows = [parse_trace_line(x) for x in (sv, cl, gnd)]
    assert all(rows), "trace regex failed"
    assert rows[1]["replay"] == 1 and rows[0]["replay"] == 0
    assert rows[0]["buttons"] == 0x0A and button_names(0x0A) == "JUMP|FORWARD"
    derive(rows)
    assert rows[1]["pressed"] == 0x200 and rows[1]["dir_press_air"] == 1, rows[1]
    assert abs(rows[0]["dspd2d"] - (math.hypot(301, 10) - 300)) < 1e-3
    assert rows[0]["dt_est"] != "" and 0.01 < rows[0]["dt_est"] < 0.02
    segs = air_segments(rows)
    assert len(segs) == 1 and segs[0]["n"] == 2 and segs[0]["dir_presses"] == 1, segs
    h = parse_hsd_line("CLIENT: [HSD-MD] side=cl kind=land t=12.5000 airtime=0.6100 takeoff=320.00 "
                       "peak=335.10 land=330.00 gain=10.00 hop=2 spd2d=330.00 vz=0.00 v=1,2,3 o=4,5,6 ground=1 slide=0")
    assert h["kind"] == "land" and h["gain"] == "10.00" and h["v"] == "1,2,3", h
    m = parse_hsd_line("[HSD-MD] side=sv kind=mark t=1.0 who=me label=tap/strafe#1")
    assert m["label"] == "tapstrafe1"
    nanline = sv.replace("v=300.000 ", "v=-nan(ind) ")
    assert parse_trace_line(nanline) is not None and math.isnan(parse_trace_line(nanline)["vx"])
    print("selftest ok")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("trace", "air", "hsd"):
        p = sub.add_parser(name)
        p.add_argument("log")
        p.add_argument("-o", "--out", default="-")
        if name != "hsd":
            p.add_argument("--keep-replays", action="store_true",
                           help="keep client re-predicted commands (rp=1)")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "trace":
        write_csv(load_trace(a.log, a.keep_replays), a.out)
    elif a.cmd == "air":
        write_csv(air_segments(load_trace(a.log, a.keep_replays)), a.out)
    elif a.cmd == "hsd":
        write_csv([r for r in (parse_hsd_line(l) for l in read_lines(a.log)) if r], a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
