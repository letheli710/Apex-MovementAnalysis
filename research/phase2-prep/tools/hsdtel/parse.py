"""Line and file parsing into unified hsdtel1 rows (observed columns only).

Recognised inputs
  - SDK file logs: "[YYYY-MM-DD HH:MM:SS.mmm] Native(C): [MOVE-TRACE] ..." in
    message*.log and "[...] Script(S): [HSD-MD] ..." in script*.log
    (s21-r5sdk/src/core/logdef.cpp:50-67, core/logger.cpp:380-410,
    public/tier0/dbg.h context prefixes). Rotated files message.N.log are
    older for larger N (spdlog rotating sink, 10 MiB x 16; core/logdef.h:13,19).
  - Console copies of the same lines, with or without ANSI colour codes.
  - HSD.MoveDiag v1 (Phase 1) and v2 lines.
  - Level-load lines (kind=map, source LOG): the dedi's
    "CHostState::State_NewGame: Loading level: '<map>'" (engine/host_state.cpp:475)
    and the client's "[BRIDGE] CONNACCEPT map='<map>'"
    (engine/client/net_bridge_install.cpp:8537). They name the map and mark a
    reset (command numbers restart on a new connection).

Every row carries `session`: the log-session GUID folder its file sits in
(platform/logs/<client|server>/<GUID>/), so rows of two game processes or two
recordings never share a stream even when their command numbers overlap.
"""
import calendar
import math
import os
import re

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
WALL_RE = re.compile(r"^\[(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})\]\s*")
CTX_RE = re.compile(r"\b(Native|Script|Netcon)\(([A-Z])\):")
CTX_SIDE = {"S": "sv", "C": "cl", "U": "ui"}

_NUM = r"(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|-?nan(?:\([a-z]+\))?|-?inf(?:inity)?|-?1\.#(?:INF|IND|QNAN)\d*)"
TRACE_RE = re.compile(
    r"\[MOVE-TRACE\] cmd=(-?\d+) ent=(-?\d+) ms=" + _NUM + r" spr=(-?\d+) duck=(-?\d+) slide=(-?\d+) ge=(-?\d+) "
    r"fwd=" + _NUM + r" sd=" + _NUM + r" b=([0-9A-Fa-f]{1,8}) msc=" + _NUM +
    r" o=" + _NUM + " " + _NUM + " " + _NUM + r" v=" + _NUM + " " + _NUM + " " + _NUM +
    r" po=" + _NUM + " " + _NUM + " " + _NUM + r" pv=" + _NUM + " " + _NUM + " " + _NUM + r"(\s+rp=1)?\s*$")
HSD_TAG = "[HSD-MD]"
MT_TAG = "[MOVE-TRACE]"
CV_TAG = "[CLASSVAR]"
# bridge_classvar_get output (s21-r5sdk/src/game/client/classvar_natives.cpp:282-289)
CV_GET_RE = re.compile(r"\[CLASSVAR\] (\S+) = (.*) \(type=(\d+) off=(\d+)\)\s*$")
CV_UNKNOWN_RE = re.compile(r"\[CLASSVAR\] unknown key '([^']*)'")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S*)")
MAP_SV_RE = re.compile(r"Loading level: '([^']+)'")
MAP_CL_RE = re.compile(r"\[BRIDGE\] CONNACCEPT map='([^']+)'")
MAP_TAGS = ("Loading level: '", "CONNACCEPT map='")
# platform/logs/<side>/<GUID>/ session folder (the SDK names it with a GUID;
# the synthetic fixtures use 00000000-synth-<side>)
SESSION_RE = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Za-z-]+$")

# HSD key -> unified column for scalar values
HSD_SCALARS = {
    "run": "run", "seq": "seq", "t": "t", "ft": "ft", "ent": "ent", "bot": "bot",
    "ground": "ground", "slide": "slide", "sprint": "sprint", "crouch": "crouch",
    "in_jump": "in_jump", "in_duck": "in_duck", "in_fwd": "in_fwd", "ax_fwd": "ax_fwd", "ax_right": "ax_right",
    "airtime": "ing_airtime", "groundtime": "ing_groundtime", "takeoff": "ing_takeoff", "peak": "ing_peak",
    "land": "ing_land", "gain": "ing_gain", "hop": "ing_hop",
}
HSD_STRINGS = {"evt": "evt", "label": "label", "key": "key", "vtype": "vtype", "value": "value",
               "where": "where", "msg": "msg", "who": "who", "prev": "prev", "ok": "ok", "total": "total",
               "file": "dumpfile_ok", "mod": "mod"}


class Issue:
    __slots__ = ("severity", "code", "file", "line_no", "message")

    def __init__(self, severity, code, file, line_no, message):
        self.severity, self.code, self.file, self.line_no, self.message = severity, code, file, line_no, message

    def as_dict(self):
        return {"severity": self.severity, "code": self.code, "file": self.file,
                "line_no": self.line_no, "message": self.message}

    def __repr__(self):
        return f"{self.severity} {self.code} {self.file}:{self.line_no} {self.message}"


def num(text):
    """Parse a printed float, mapping MSVC/C99 NaN/Inf spellings to float('nan'/'inf')."""
    t = text.strip().lower()
    if "nan" in t or "#ind" in t or "#qnan" in t:
        return float("nan")
    if "inf" in t:
        return float("-inf") if t.startswith("-") else float("inf")
    return float(t)


def split_prefix(raw):
    """Strip ANSI, the log-sink timestamp and the context prefix.
    Returns (wall_seconds or None, side or None, rest)."""
    line = ANSI_RE.sub("", raw.rstrip("\r\n"))
    wall = None
    m = WALL_RE.match(line)
    if m:
        y, mo, d, hh, mi, ss, ms = (int(x) for x in m.groups())
        wall = calendar.timegm((y, mo, d, hh, mi, ss, 0, 0, 0)) + ms / 1000.0
        line = line[m.end():]
    side = None
    c = CTX_RE.search(line)
    if c and c.start() < 24:
        side = CTX_SIDE.get(c.group(2))
    return wall, side, line


def parse_trace(rest):
    m = TRACE_RE.search(rest)
    if not m:
        return None
    g = m.groups()
    row = {
        "source": "MT", "kind": "cmd", "cmd": int(g[0]), "ent": int(g[1]), "maxspeed": num(g[2]),
        "sprint": int(g[3]), "duck": int(g[4]), "slide": int(g[5]), "ground": int(g[6]),
        "fwd": num(g[7]), "sidemove": num(g[8]), "buttons": int(g[9], 16), "movescale": num(g[10]),
        "replay": 1 if g[23] else 0,
    }
    for i, k in enumerate(("ox", "oy", "oz", "vx", "vy", "vz", "pox", "poy", "poz", "pvx", "pvy", "pvz")):
        row[k] = num(g[11 + i])
    return row


def parse_classvar(rest):
    m = CV_GET_RE.search(rest)
    if m:
        return {"source": "CV", "kind": "classvar", "key": m.group(1), "value": m.group(2).strip(),
                "vtype": "cvtype" + m.group(3)}
    m = CV_UNKNOWN_RE.search(rest)
    if m:
        return {"source": "CV", "kind": "classvar", "key": m.group(1), "value": "-", "vtype": "unknown"}
    return None


def parse_hsd(rest):
    """Return (row, problem) for an [HSD-MD] payload."""
    i = rest.find(HSD_TAG)
    payload = rest[i + len(HSD_TAG):]
    msg = None
    j = payload.find(" msg=")
    if j >= 0:
        msg = payload[j + 5:].strip()
        payload = payload[:j]
    kv = dict(KV_RE.findall(payload))
    if msg is not None:
        kv["msg"] = msg
    row = {"source": "HSD", "_kv": kv}
    ver = kv.get("ver", "1")
    row["_ver"] = ver
    if "side" not in kv or "kind" not in kv:
        return row, "missing side= or kind="
    row["side"] = kv["side"]
    row["kind"] = kv["kind"]
    try:
        for key, col in HSD_SCALARS.items():
            if key in kv and kv[key] != "":
                row[col] = num(kv[key])
        for key, col in HSD_STRINGS.items():
            if key in kv:
                row[col] = kv[key]
        vel = kv.get("vel", kv.get("v") if ver == "1" else None)
        for key, cols in (("o", ("ox", "oy", "oz")), ("vel", ("vx", "vy", "vz")), ("ang", ("pitch", "yaw"))):
            text = vel if key == "vel" else kv.get(key)
            if text is None:
                continue
            parts = text.split(",")
            if len(parts) != len(cols):
                return row, f"{key}= has {len(parts)} components, expected {len(cols)}"
            for c, p in zip(cols, parts):
                row[c] = num(p)
    except ValueError as e:
        return row, f"bad number: {e}"
    return row, None


ROT_RE = re.compile(r"^(?P<base>.*?)(?:\.(?P<n>\d+))?\.(?P<ext>log|txt)$", re.I)


def expand_inputs(paths):
    """Files and directories -> ordered file list. Rotated sets come oldest first."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _d, fs in os.walk(p):
                for f in fs:
                    if f.lower().endswith((".log", ".txt")):
                        files.append(os.path.join(root, f))
        else:
            files.append(p)

    def key(path):
        d, b = os.path.split(path)
        m = ROT_RE.match(b)
        if not m:
            return (d, b, 0)
        n = int(m.group("n")) if m.group("n") else 0
        return (d, m.group("base") + "." + m.group("ext"), -n)

    return sorted(dict.fromkeys(files), key=key)


def session_of(path):
    """Session id of a log file: the nearest GUID-named folder on its path, else
    the name of the folder that holds it (loose copies: keep one session per folder)."""
    parts = os.path.normpath(os.path.abspath(path)).replace("\\", "/").split("/")[:-1]
    for part in reversed(parts):
        if SESSION_RE.match(part):
            return part
    return parts[-1] if parts and parts[-1] else "-"


def parse_map(rest):
    m = MAP_SV_RE.search(rest) or MAP_CL_RE.search(rest)
    return {"source": "LOG", "kind": "map", "value": m.group(1)} if m else None


def guess_side_from_path(path):
    p = path.replace("\\", "/").lower()
    if "/client/" in p or "client" in os.path.basename(p):
        return "cl"
    if "/server/" in p or "server" in os.path.basename(p) or "dedi" in os.path.basename(p):
        return "sv"
    return None


def parse_file(path, side_hint=None, file_rank=0):
    rows, issues = [], []
    base = os.path.basename(path)
    path_side = side_hint or guess_side_from_path(path)
    session = session_of(path)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for ln, raw in enumerate(fh, 1):
            if MT_TAG not in raw and HSD_TAG not in raw and CV_TAG not in raw:
                if not any(t in raw for t in MAP_TAGS):
                    continue
            wall, ctx_side, rest = split_prefix(raw)
            if MT_TAG not in rest and HSD_TAG not in rest and CV_TAG not in rest:
                row = parse_map(rest)
                if row is None:
                    continue
                # both producers print under the ENGINE context: the side comes from the folder
                row["side"] = path_side or "unknown"
            elif CV_TAG in rest and MT_TAG not in rest and HSD_TAG not in rest:
                row = parse_classvar(rest)
                if row is None:
                    continue  # other [CLASSVAR] chatter (resolve, writes, replays)
                row["side"] = ctx_side or path_side or "cl"
            elif MT_TAG in rest:
                row = parse_trace(rest)
                if row is None:
                    issues.append(Issue("error", "E_MALFORMED_MT", base, ln, rest.strip()[:160]))
                    continue
                row["side"] = ctx_side or path_side or "unknown"
                if row["side"] == "unknown":
                    issues.append(Issue("warning", "W_SIDE_UNKNOWN", base, ln,
                                        "no Native(C)/(S) prefix and no --side; pass --side cl|sv"))
            else:
                row, problem = parse_hsd(rest)
                if problem:
                    issues.append(Issue("error", "E_MALFORMED_HSD", base, ln, problem))
                    continue
                if row["_ver"] not in ("1", "2"):
                    issues.append(Issue("warning", "W_HSD_VERSION", base, ln, f"unknown ver={row['_ver']}"))
                if ctx_side and ctx_side != row["side"]:
                    issues.append(Issue("warning", "W_SIDE_MISMATCH", base, ln,
                                        f"line says side={row['side']} but log prefix says {ctx_side}"))
            row["file"] = base
            row["session"] = session
            row["line_no"] = ln
            row["wall"] = wall
            row["_rank"] = file_rank
            rows.append(row)
    return rows, issues


def is_synthetic(path):
    """True when the file carries the hsdtel.synth header line."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.readline().startswith("# SYNTHETIC")
    except OSError:
        return False


def parse_inputs(paths, side_hint=None):
    files = expand_inputs(paths)
    rows, issues = [], []
    for rank, f in enumerate(files):
        r, i = parse_file(f, side_hint, rank)
        rows += r
        issues += i
    if not files:
        issues.append(Issue("error", "E_NO_INPUT", "", 0, "no input files"))
    return files, rows, issues


def is_finite_row(row, cols):
    for c in cols:
        v = row.get(c)
        if isinstance(v, float) and not math.isfinite(v):
            return False
    return True
