#!/usr/bin/env python3
"""M6-B legend mobility analysis (Apex R5Flowstate S21 offline client + S3 dedi + SDK, 120 fps).

    py -3 m6b_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Each session folder holds runner.json and platform/logs (hsd_session.py layout). The legend is read from
runner.json ("legend"). Summaries use trials with ok=true and warmup=false; the Loba timeline and the Ash re-entry
check also look at the warm-up / failed trials, because an event can spill over from one trial into the next.
stdlib only; prints no absolute paths; reads nothing outside the given folders.

Data sources (read-only), all from the raw logs (report/rows.csv keeps only 6 significant digits):
  * dedi MOVE-TRACE (server message.log): authoritative per-usercmd pre/post origin and velocity. Teleports are
    found as origin jumps between consecutive commands (|pre_i - post_(i-1)| > 50 u). During the Ash breach the dedi
    prints no MOVE-TRACE (controls frozen, player parented to a mover), so the breach shows up as a command gap.
  * dedi HSD-RESET lines: the per-trial server window (from one reset to the next).
  * dedi SDK / script diag lines: [TRANSLOC] tossloop begin/end (Loba bracelet in flight), [LUNGE-CLR] (called by the
    Loba teleport and the phase-tunnel entry), [OPL-SRV] (Alter placement search), PhaseTunnel_PhaseEntity /
    PhaseTunnel_PrepareToMoveEntAlongTunnel (Ash breach entry).
  * client MOVE-TRACE first-time prints: button bits (offhand1 0x00200000, offhand4 0x01000000, attack 0x1,
    jump 0x2), mapped to the dedi by command number.
  * client [HSD-STATE]: ph= (IsPhaseShifted) and glide= (m_glideMeter, client prediction) per frame.
  * client [CLASSVAR]: player-settings census (jetpack / glide keys).
  * runner.json sched_lines: key edges with client game time t.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

PLAT_RE = re.compile(r"^\[[^\]]*\]\s*\[\s*(-?\d+\.\d+)\]")
MT_RE = re.compile(r"\[MOVE-TRACE\] cmd=(\d+) ent=(\d+) ms=(\S+) spr=(\d) duck=(\d) slide=(\d) ge=(\d) fwd=(\S+) sd=(\S+) "
                   r"b=([0-9A-Fa-f]+) msc=(\S+) o=(\S+) (\S+) (\S+) v=(\S+) (\S+) (\S+) po=(\S+) (\S+) (\S+) "
                   r"pv=(\S+) (\S+) (\S+)")
STATE_RE = re.compile(r"\[HSD-STATE\] run=(\d+) fc=(\d+) t=([\d.]+) (.*)$")
RESET_RE = re.compile(r"\[HSD-RESET\].* run=(\d+) .*o=(\S+?),(\S+?),(\S+?) vel=.* weapon=(\S+)")
SCHED_RE = re.compile(r"edge=(\S+)(?: key=(\S+))? frame=(\d+) fc=(\d+) pt=(\S+) t=(\S+)")
CLASSVAR_RE = re.compile(r"\[CLASSVAR\] (\w+) = (.*?) \(type=")
KV_RE = re.compile(r"(\w+)=(\S+)")
VEC_RE = r"<(-?[\d.]+) (-?[\d.]+) (-?[\d.]+)>"

B_JUMP, B_ATTACK, B_OFF1, B_OFF4 = 0x2, 0x1, 0x00200000, 0x01000000
DT = 1.0 / 120.0
G = 750.0
EYE = 60.0

# Aim pitch per schedule (tools/hsd_trial.py SCHEDULE_PITCH); Ash aims at the ground d = EYE / tan(pitch).
PITCH = {"b_ash_600": 5.71, "b_ash_1200": 2.86, "b_ash_2000": 1.72, "bp_ash_att": 2.86, "bp_ash_hold_att": 2.86}
ROCK_FACE_X = -13706.0  # M3 test wall face (m55/GRAPPLE-RANGE.md); the Alter lanes face it at yaw 0

# M4 Valkyrie jets model (m4/valk_rev/VALK-REV-PRIMITIVES.md section 2.3) + this session's census for the down
# tightness. Vertical axis only (no move input in M6-B).
M4 = {"T": 1.9, "tu": 0.27, "td": 0.1, "s0": 1.8, "R": 0.5, "above": 0.4, "vzScaleOff": 0.4, "postG": 0.45}


# ============================================================================ helpers
def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0}
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) if len(vals) > 1 else 0.0
    return {"n": len(vals), "mean": m, "sd": sd, "min": min(vals), "max": max(vals)}


def fmt(s, nd=3):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    if s["n"] == 1:
        return f"{s['mean']:.{nd}f} (n=1)"
    return f"{s['mean']:.{nd}f} (sd {s['sd']:.{nd}f}, {s['min']:.{nd}f}..{s['max']:.{nd}f}, n={s['n']})"


def linfit(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    rms = math.sqrt(sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / n)
    return a, b, rms


def d3(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def d2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def r3(v, nd=1):
    return [round(x, nd) for x in v] if v else v


OUT = []


def out(s=""):
    OUT.append(s)
    print(s)


# ============================================================================ loader
def _files(folder, side, stem=None):
    fs = glob.glob(os.path.join(folder, "platform", "logs", side, "*", "*.log"))
    if stem:
        fs = [f for f in fs if re.fullmatch(stem + r"(\.\d+)?\.log", os.path.basename(f))]
    return sorted(fs)


def _mt(m, plat):
    g = m.groups()
    return {"plat": plat, "cmd": int(g[0]), "ground": int(g[6]), "b": int(g[9], 16), "msc": float(g[10]),
            "o": (float(g[11]), float(g[12]), float(g[13])), "v": (float(g[14]), float(g[15]), float(g[16])),
            "po": (float(g[17]), float(g[18]), float(g[19])), "pv": (float(g[20]), float(g[21]), float(g[22]))}


class Session:
    def __init__(self, folder):
        self.folder = folder
        self.name = os.path.basename(os.path.normpath(folder))
        with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
            self.runner = json.load(fh)
        self.legend = self.runner.get("legend")
        self.trials = self.runner["trials"]
        for t in self.trials:
            t["edges"] = []
            for ln in t.get("sched_lines", []):
                m = SCHED_RE.search(ln)
                if m:
                    t["edges"].append({"edge": m.group(1), "key": m.group(2), "frame": int(m.group(3)),
                                       "fc": int(m.group(4)), "pt": float(m.group(5)), "t": float(m.group(6))})
            m = re.search(r"weapon=(\S+)", t.get("reset", ""))
            t["reset_weapon"] = m.group(1) if m else None
            m = re.search(r"edge=end .* o=(\S+),(\S+),(\S+)", " ".join(t.get("sched_lines", [])))
            t["end_o"] = tuple(float(x) for x in m.groups()) if m else None
        self._server()
        self._client()

    def _server(self):
        self.sv_mt = {}
        self.resets = []
        self.sv_ev = []   # (plat, tag, text)
        for f in _files(self.folder, "server"):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    pm = PLAT_RE.match(raw)
                    if not pm:
                        continue
                    plat = float(pm.group(1))
                    if "[MOVE-TRACE]" in raw:
                        m = MT_RE.search(raw)
                        if m:
                            r = _mt(m, plat)
                            self.sv_mt.setdefault(r["cmd"], r)
                        continue
                    if "[HSD-RESET]" in raw:
                        m = RESET_RE.search(raw)
                        if m:
                            self.resets.append((plat, int(m.group(1)), (float(m.group(2)), float(m.group(3)),
                                                                         float(m.group(4))), m.group(5)))
                        continue
                    for tag in ("[TRANSLOC]", "[LUNGE-CLR]", "[OPL-SRV]", "PhaseTunnel_PhaseEntity",
                                "PhaseTunnel_PrepareToMoveEntAlongTunnel", "PhaseTunnel_ShouldPhaseEnt PASSED", "ALTER:",
                                "TRANSLOCATION:", "[JETPACK]", "LockWeaponsAndMelee from TranslocationLifetimeThread"):
                        if tag in raw:
                            self.sv_ev.append((plat, "THROW" if tag.startswith("LockWeapons") else tag.strip("[]:"),
                                               raw.rstrip("\n")))
                            break
        self.resets.sort()
        self.sv_ev.sort(key=lambda e: e[0])
        self.sv_cmds = sorted(self.sv_mt)
        self.windows = {}
        for i, (p, run, o, w) in enumerate(self.resets):
            end = self.resets[i + 1][0] if i + 1 < len(self.resets) else float("inf")
            self.windows.setdefault(run, (p, end, o, w))

    def _client(self):
        self.cl_mt = {}
        self.states = {}
        self.classvars = {}
        for f in _files(self.folder, "client", "message"):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    if "[MOVE-TRACE]" in raw:
                        m = MT_RE.search(raw)
                        if m:
                            pm = PLAT_RE.match(raw)
                            r = _mt(m, float(pm.group(1)) if pm else None)
                            self.cl_mt.setdefault(r["cmd"], r)
                    elif "[CLASSVAR]" in raw:
                        m = CLASSVAR_RE.search(raw)
                        if m:
                            self.classvars[m.group(1)] = m.group(2).strip()
        for f in _files(self.folder, "client", "script"):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    if "[HSD-STATE]" not in raw:
                        continue
                    m = STATE_RE.search(raw)
                    if not m:
                        continue
                    kv = dict(KV_RE.findall(m.group(4)))
                    self.states.setdefault(int(m.group(1)), []).append(
                        {"fc": int(m.group(2)), "t": float(m.group(3)), "ph": kv.get("ph") == "true",
                         "glide": float(kv.get("glide", "nan"))})
        for k in self.states:
            self.states[k].sort(key=lambda s: s["fc"])
        self.cl_cmds = sorted(self.cl_mt)

    # -- helpers
    def scored(self):
        return [t for t in self.trials if t.get("ok") and not t.get("warmup")]

    def sv_rows(self, run):
        w = self.windows.get(run)
        if not w:
            return []
        return [self.sv_mt[c] for c in self.sv_cmds if w[0] <= self.sv_mt[c]["plat"] < w[1]]

    def sv_events(self, run, tag=None):
        w = self.windows.get(run)
        if not w:
            return []
        return [e for e in self.sv_ev if w[0] <= e[0] < w[1] and (tag is None or e[1] == tag)]

    def cl_rows(self, t):
        """client first-time MT rows inside the trial's schedule (start .. end edge, client plat)."""
        e = {x["edge"]: x for x in t["edges"] if x["edge"] in ("start", "end")}
        if "start" not in e or "end" not in e:
            return []
        lo, hi = e["start"]["pt"] - 0.02, e["end"]["pt"] + 0.02
        return [self.cl_mt[c] for c in self.cl_cmds if self.cl_mt[c]["plat"] is not None and lo <= self.cl_mt[c]["plat"] <= hi]

    def press_cmds(self, t, bit):
        rows = self.cl_rows(t)
        outp, prev = [], False
        for r in rows:
            on = bool(r["b"] & bit)
            if on and not prev:
                outp.append(r["cmd"])
            prev = on
        return outp

    def sv_plat_of_cmd(self, cmd):
        if cmd in self.sv_mt:
            return self.sv_mt[cmd]["plat"], cmd
        import bisect
        i = bisect.bisect_left(self.sv_cmds, cmd)
        if i < len(self.sv_cmds):
            c = self.sv_cmds[i]
            return self.sv_mt[c]["plat"], c
        return None, None

    def run_of_plat(self, plat):
        for run, (lo, hi, o, w) in self.windows.items():
            if lo <= plat < hi:
                return run
        return None

    def jumps(self, thresh=50.0):
        """origin jumps between consecutive dedi MOVE-TRACE rows (session-wide; a command gap is allowed)."""
        key = ("jumps", thresh)
        if key in self.__dict__:
            return self.__dict__[key]
        res = []
        self.__dict__[key] = res
        prev = None
        for c in self.sv_cmds:
            r = self.sv_mt[c]
            if prev is not None and d3(r["o"], prev["po"]) > thresh:
                res.append({"cmd": c, "prev_cmd": prev["cmd"], "plat": r["plat"], "frm": prev["po"], "to": r["o"],
                            "v_pre": r["v"], "dist": d3(r["o"], prev["po"])})
            prev = r
        return res

    def is_reset_jump(self, j):
        for p, run, o, w in self.resets:
            if -0.3 <= j["plat"] - p <= 1.0 and d3(j["to"], o) < 5.0:
                return run
        return None


# ============================================================================ census
def census(sessions, R, P):
    keys = ["jetpackEnabled", "jetpackThrust", "jetpackMeterRate", "jetpackMeterOnActivation", "jetpackTacticalMeterRate",
            "jetpackThrustScaleOnActivation", "jetpackThrustScaleTimeOnActivation", "jetpackPostEffectTime",
            "jetpackPostEffectGravity", "jetpackPostEffectDrag", "jetpackTightnessUp", "jetpackTightnessDown",
            "jetpackTightnessSideways", "jetpackTightnessForwardBack", "glideDuration", "glideEnabled", "hoverEnabled",
            "glideRechargeOnlyInGroundedState", "glideRechargeOnlyWhenFeetOnGround"]
    out("== CENSUS ([CLASSVAR], client) ==")
    R["census"] = {}
    for s in sessions:
        if not s.classvars:
            continue
        cv = {k: s.classvars.get(k) for k in keys if k in s.classvars}
        R["census"][s.legend or s.name] = cv
        if s.legend == "valkyrie":
            for k, v in cv.items():
                out(f"  {s.legend:9s} {k} = {v}")
                try:
                    P[f"valk.census.{k}"] = {"value": float(v) if v not in ("true", "false") else v, "unit": "",
                                             "source": "client [CLASSVAR] census (" + s.name + ")", "n": 1}
                except ValueError:
                    pass
        else:
            out(f"  {s.legend:9s} jetpack/glide keys: " + ", ".join(f"{k}={v}" for k, v in cv.items() if k in
                                                                        ("jetpackEnabled", "glideDuration", "jetpackMeterRate")))
    out()


# ============================================================================ Alter
def alter(sessions, R, P):
    out("== ALTER, Void Passage (mp_ability_phase_door) ==")
    rows_out = []
    for s in sessions:
        sess_types = {}
        for p, tag, txt in s.sv_ev:
            if tag == "OPL-SRV":
                k = re.sub(r"[-\d.<>]+", "", txt.split("[OPL-SRV]", 1)[1]).split("=")[0].strip()
                sess_types[k] = sess_types.get(k, 0) + 1
        out(f"-- {s.name}: [OPL-SRV] message types (session): " + "; ".join(f"{k} x{v}" for k, v in sorted(sess_types.items(), key=lambda x: -x[1])))
        for t in s.scored():
            run = t["run"]
            ev = s.sv_events(run, "OPL-SRV")
            acc = [e for e in ev if "placement accepted" in e[2]]
            shallow = [e for e in ev if "shallow exit accepted" in e[2]]
            edgefail = [e for e in ev if "entrance edge-correction failed" in e[2]]
            thick = [float(re.search(r"thickness=([\d.]+)", e[2]).group(1)) for e in ev if "exit probe" in e[2]]
            depth = [float(re.search(r"depth=([\d.]+)", e[2]).group(1)) for e in ev if "exit probe" in e[2]]
            ent = exi = None
            if acc:
                m = re.search(r"entrance=" + VEC_RE + r".* exit=" + VEC_RE, acc[0][2])
                if m:
                    ent = tuple(float(x) for x in m.groups()[:3])
                    exi = tuple(float(x) for x in m.groups()[3:])
            alt_tp = len(s.sv_events(run, "ALTER"))
            holst = sum(1 for e in s.sv_events(run, "TRANSLOC") if "HolsterInternal 'mp_ability_phase_door'" in e[2])
            ph = sum(1 for st_ in s.states.get(run, []) if st_["ph"])
            sv = s.sv_rows(run)
            maxx = max((r["po"][0] for r in sv), default=None)
            vmax = max((math.hypot(*r["pv"][:2]) for r in sv), default=None)
            jumps = [j for j in s.jumps() if s.run_of_plat(j["plat"]) == run and not s.is_reset_jump(j)]
            row = {"session": s.name, "run": run, "schedule": t["schedule"], "opl_accepted": len(acc),
                   "opl_shallow": len(shallow), "opl_edge_fail": len(edgefail), "thickness": stats(thick).get("mean"),
                   "exit_depth": stats(depth).get("mean"), "entrance": ent, "exit": exi, "alter_teleport_prints": alt_tp,
                   "phase_door_holsters": holst, "ph_frames": ph, "max_x": maxx,
                   "gap_to_rock_face": (ROCK_FACE_X - maxx) if maxx is not None else None, "max_spd2d": vmax,
                   "teleports": len(jumps)}
            rows_out.append(row)
    out(f"{'session':28s} {'sched':18s} run   acc shal efail thick  depth ph tele altTP hol  maxX     face-gap  vmax")
    for r in rows_out:
        out(f"{r['session'][16:]:28s} {r['schedule']:18s} {r['run']:5d} {r['opl_accepted']:3d} {r['opl_shallow']:4d} {r['opl_edge_fail']:5d} "
            f"{(r['thickness'] or 0):6.1f} {(r['exit_depth'] or 0):5.1f} {r['ph_frames']:2d} {r['teleports']:4d} {r['alter_teleport_prints']:5d} "
            f"{r['phase_door_holsters']:3d} {r['max_x']:9.2f} {r['gap_to_rock_face']:7.2f} {r['max_spd2d']:7.2f}")
    n = len(rows_out)
    out(f"summary: {n} scored trials; portal/teleport in {sum(1 for r in rows_out if r['teleports'] or r['ph_frames'] or r['alter_teleport_prints'])}; "
        f"trials with >=1 '[OPL-SRV] placement accepted' {sum(1 for r in rows_out if r['opl_accepted'])}; "
        f"all accepted exits shallow (depth < 8): {all(r['opl_shallow'] >= 1 for r in rows_out if r['opl_accepted'])}")
    out(f"  exit-probe thickness {fmt(stats([r['thickness'] for r in rows_out]), 1)} u; exit depth {fmt(stats([r['exit_depth'] for r in rows_out]), 2)} u")
    out(f"  max x reached {fmt(stats([r['max_x'] for r in rows_out]), 2)} (rock face x {ROCK_FACE_X}); "
        f"edge-correction failures per trial {fmt(stats([r['opl_edge_fail'] for r in rows_out]), 0)}")
    out()
    R["alter"] = {"trials": rows_out}
    P["alter.triggered_portals"] = {"value": 0, "unit": "trials", "source": "dedi MT (no teleport), client ph=false, no 'ALTER: Teleporting'", "n": n}
    P["alter.sdk_exit_depth"] = {"value": stats([r["exit_depth"] for r in rows_out]).get("mean"), "unit": "u",
                                 "source": "[OPL-SRV] exit probe (SDK placement reimplementation)", "n": n}
    P["alter.sdk_wall_thickness"] = {"value": stats([r["thickness"] for r in rows_out]).get("mean"), "unit": "u",
                                     "source": "[OPL-SRV] exit probe thickness", "n": n}


# ============================================================================ Loba
def loba(sessions, R, P):
    out("== LOBA, Burglar's Best Friend (mp_ability_translocation) ==")
    out("throw marker: dedi script 'LockWeaponsAndMelee from TranslocationLifetimeThread' (printed once per toss); "
        "[TRANSLOC] tossloop begin/end are budget-limited SDK diag lines (not printed for every throw)")
    allrows = []
    for s in sessions:
        throws = [p for p, tag, txt in s.sv_ev if tag == "THROW"]
        loopb = [p for p, tag, txt in s.sv_ev if tag == "TRANSLOC" and "tossloop begin" in txt]
        ends = [(p, float(re.search(r"held=([\d.]+)", txt).group(1))) for p, tag, txt in s.sv_ev
                if tag == "TRANSLOC" and "tossloop end" in txt]
        jumps = [j for j in s.jumps() if not s.is_reset_jump(j) and s.resets and j["plat"] > s.resets[0][0]]
        press1 = {}
        for t in s.trials:
            if t.get("ok") and t["run"] in s.windows:
                press1[t["run"]] = [s.sv_plat_of_cmd(c)[0] for c in s.press_cmds(t, B_OFF1)]
        for j in jumps:
            prev_t = [p for p in throws if p < j["plat"]]
            j["throw_plat"] = prev_t[-1] if prev_t else None
            j["throw_run"] = s.run_of_plat(j["throw_plat"]) if j["throw_plat"] else None
            j["run"] = s.run_of_plat(j["plat"])
            prev_e = [(p, h) for p, h in ends if j["throw_plat"] and j["throw_plat"] - 0.1 <= p <= j["plat"] + 0.01]
            j["end_plat"], j["held"] = prev_e[-1] if prev_e else (None, None)
            pw = [p for p in press1.get(j["run"], []) if p is not None and p < j["plat"]]
            j["since_window_press1"] = (j["plat"] - pw[0]) if pw else None
            cands = [s.sv_mt[c] for c in s.sv_cmds if j["throw_plat"] and abs(s.sv_mt[c]["plat"] - j["throw_plat"]) < 0.06]
            j["throw_pos"] = cands[0]["po"] if cands else None
            nxt = [s.sv_mt.get(j["cmd"] + k) for k in (0, 1, 12, 24)]
            j["spd_after"] = [round(math.sqrt(sum(x * x for x in r["v"])), 3) if r else None for r in nxt]
        out(f"-- {s.name}: {len(throws)} throws, {len(loopb)} 'tossloop begin', {len(ends)} 'tossloop end', "
            f"{len(jumps)} non-reset teleports")
        for t in s.trials:
            if not t.get("ok"):
                continue
            run = t["run"]
            w = s.windows.get(run)
            if not w:
                continue
            pp = press1.get(run, [])
            th = [p for p in throws if w[0] <= p < w[1]]
            en = [(p, h) for p, h in ends if w[0] <= p < w[1]]
            tj = [j for j in jumps if j["run"] == run]
            row = {"session": s.name, "run": run, "schedule": t["schedule"], "warmup": bool(t.get("warmup")),
                   "reset_weapon": t["reset_weapon"], "offhand1_presses": len(pp),
                   "throw_after_press1": (th[0] - pp[0]) if th and pp and pp[0] else None,
                   "press2_after_throw": (pp[1] - th[0]) if th and len(pp) > 1 and pp[1] else None,
                   "press2_after_press1": (pp[1] - pp[0]) if len(pp) > 1 and pp[0] and pp[1] else None,
                   "tossloop_end_after_throw": (en[0][0] - th[0]) if th and en and en[0][0] > th[0] else None,
                   "held": [h for _, h in en], "throws": len(th),
                   "teleports": [{"cmd": j["cmd"], "dt_from_trial_reset": round(j["plat"] - w[0], 3),
                                  "own_throw": j["throw_run"] == run, "throw_run": j["throw_run"],
                                  "t_after_throw": round(j["plat"] - j["throw_plat"], 3) if j["throw_plat"] else None,
                                  "t_after_window_press1": round(j["since_window_press1"], 3) if j["since_window_press1"] else None,
                                  "t_after_loop_end": round(j["plat"] - j["end_plat"], 3) if j["end_plat"] else None,
                                  "held": j["held"],
                                  "dist_from_throw_pos": round(d2(j["to"], j["throw_pos"]), 1) if j["throw_pos"] else None,
                                  "dz_from_throw_pos": round(j["to"][2] - j["throw_pos"][2], 1) if j["throw_pos"] else None,
                                  "jump_dist": round(j["dist"], 1), "to": r3(j["to"]),
                                  "spd_pre_k0_k1_k12_k24": j["spd_after"]} for j in tj],
                   "end_o": t["end_o"]}
            allrows.append(row)
    out(f"{'sched':18s} run   wu reset_weapon               thr  thr-p1  p2-thr  loopEnd held  teleports in window "
        f"(whose throw, t after throw, t after this window's 1st press, dist from throw pos, dz, |v| k0/k1/k12/k24)")
    for r in allrows:
        tel = "; ".join(f"{'own' if x['own_throw'] else 'prev(' + str(x['throw_run']) + ')'} +{x['t_after_throw']}s "
                        f"p1+{x['t_after_window_press1']}s d={x['dist_from_throw_pos']} dz={x['dz_from_throw_pos']} "
                        f"v={x['spd_pre_k0_k1_k12_k24']}" for x in r["teleports"]) or "-"
        f = lambda v: f"{v:6.3f}" if v is not None else "   -  "
        out(f"{r['schedule']:18s} {r['run']:5d} {'w' if r['warmup'] else ' '}  {str(r['reset_weapon']):26s} {r['throws']:2d} "
            f"{f(r['throw_after_press1'])} {f(r['press2_after_throw'])} {f(r['tossloop_end_after_throw'])} "
            f"{','.join(f'{h:.2f}' for h in r['held']) or '-':5s} {tel}")
    sc = [r for r in allrows if not r["warmup"]]
    out("summary per schedule (scored trials):")
    summ = {}
    for sch in sorted(set(r["schedule"] for r in sc)):
        g = [r for r in sc if r["schedule"] == sch]
        own = [x for r in g for x in r["teleports"] if x["own_throw"]]
        prev = [x for r in g for x in r["teleports"] if not x["own_throw"]]
        thr = [r for r in g if r["throws"]]
        summ[sch] = {"n": len(g), "trials_with_throw": len(thr), "own_teleport_in_trial": len(own),
                     "teleport_from_previous_trials_throw": len(prev),
                     "throw_after_press1": stats([r["throw_after_press1"] for r in g]),
                     "press2_after_throw": stats([r["press2_after_throw"] for r in g]),
                     "own_dist": stats([x["dist_from_throw_pos"] for x in own]),
                     "own_t_after_throw": stats([x["t_after_throw"] for x in own]),
                     "prev_t_after_throw": stats([x["t_after_throw"] for x in prev]),
                     "prev_t_after_window_press1": stats([x["t_after_window_press1"] for x in prev]),
                     "prev_dist": stats([x["dist_from_throw_pos"] for x in prev]),
                     "prev_dz": stats([x["dz_from_throw_pos"] for x in prev])}
        out(f"  {sch:18s} n={len(g)} trials with a throw={len(thr)}; own-throw teleport inside the trial={len(own)}; "
            f"carried-over teleport (an earlier trial's throw)={len(prev)}; throw-press1 {fmt(summ[sch]['throw_after_press1'])}; "
            f"press2-throw {fmt(summ[sch]['press2_after_throw'])}")
        if own:
            out(f"      own: dist {fmt(summ[sch]['own_dist'], 1)} u; t after throw {fmt(summ[sch]['own_t_after_throw'])}; "
                f"t after loop end {fmt(stats([x['t_after_loop_end'] for x in own]))}; held {fmt(stats([x['held'] for x in own]))}")
        if prev:
            out(f"      carried-over: dist {fmt(summ[sch]['prev_dist'], 1)} u, dz {fmt(summ[sch]['prev_dz'], 1)}; t after throw "
                f"{fmt(summ[sch]['prev_t_after_throw'])}; t after this window's 1st press {fmt(summ[sch]['prev_t_after_window_press1'])}")
    tele = [x for r in allrows for x in r["teleports"]]
    v0 = [x["spd_pre_k0_k1_k12_k24"][0] for x in tele if x["spd_pre_k0_k1_k12_k24"][0] is not None]
    v1 = [x["spd_pre_k0_k1_k12_k24"][1] for x in tele if x["spd_pre_k0_k1_k12_k24"][1] is not None]
    out(f"all teleports (incl. warm-up windows): n={len(tele)}; |v| pre on the teleport cmd {fmt(stats(v0), 3)}, "
        f"next cmd {fmt(stats(v1), 3)}")
    lat = [r["throw_after_press1"] for r in allrows if r["throw_after_press1"] is not None
           and r["reset_weapon"] == "mp_weapon_melee_survival"]
    out(f"press -> throw latency from a melee-active start (incl. warm-up): {fmt(stats(lat))} s")
    co = [x for x in tele if not x["own_throw"]]
    dropw = [x for x in co if x["t_after_window_press1"] is not None and x["t_after_window_press1"] < 2.0]
    out(f"carried-over teleports < 2 s after that window's first offhand1 press: {len(dropw)} / {len(co)}; "
        f"t after that press {fmt(stats([x['t_after_window_press1'] for x in dropw]))} s")
    out()
    R["loba"] = {"trials": allrows, "summary": summ}
    P["loba.throw_latency_from_melee"] = {"value": stats(lat).get("mean"), "unit": "s",
                                          "source": "client offhand1 press cmd -> dedi throw script line",
                                          "n": len(lat), "spread": [stats(lat).get("min"), stats(lat).get("max")]}
    P["loba.speed_after_teleport"] = {"value": stats(v0).get("mean"), "unit": "u/s",
                                      "source": "dedi MT pre-velocity on the teleport cmd",
                                      "n": len(v0), "spread": [stats(v0).get("min"), stats(v0).get("max")]}
    own_all = [x for r in sc for x in r["teleports"] if x["own_throw"]]
    if own_all:
        ds = stats([x["dist_from_throw_pos"] for x in own_all])
        P["loba.early_drop_teleport_dist"] = {"value": ds.get("mean"), "unit": "u",
                                              "source": "dedi MT; drop press 0.35 s after the throw (b_loba_drop_t15)",
                                              "n": len(own_all), "spread": [ds.get("min"), ds.get("max")]}
        ts_ = stats([x["t_after_throw"] for x in own_all])
        P["loba.early_drop_throw_to_teleport"] = {"value": ts_.get("mean"), "unit": "s",
                                                  "source": "dedi throw line -> MT origin jump",
                                                  "n": len(own_all), "spread": [ts_.get("min"), ts_.get("max")]}
    if co:
        cs = stats([x["t_after_window_press1"] for x in dropw])
        P["loba.late_drop_press_to_teleport"] = {"value": cs.get("mean"), "unit": "s",
                                                 "source": "next trial's first offhand1 press -> MT origin jump (bracelet still in flight)",
                                                 "n": len(dropw), "spread": [cs.get("min"), cs.get("max")]}


# ============================================================================ Ash
def ash(sessions, R, P):
    out("== ASH, Phase Breach (mp_weapon_phase_breach, ultimate, +offhand4) ==")
    out("breach = dedi 'PhaseTunnel_PhaseEntity'; travel = dedi MOVE-TRACE command gap (no MT while frozen/parented); "
        "re-entry = a PhaseEntity that comes right before a runner reset (reset placed the player on the 15 s entry portal)")
    rows, entries_all = [], []
    for s in sessions:
        jumps = s.jumps()
        reset_plats = [p for p, *_ in s.resets]
        passed = [p for p, tag, txt in s.sv_ev if tag == "PhaseTunnel_ShouldPhaseEnt PASSED"]
        for t in s.trials:
            run = t["run"]
            w = s.windows.get(run)
            if not w:
                continue
            ent = [p for p, tag, txt in s.sv_ev if tag == "PhaseTunnel_PhaseEntity" and w[0] <= p < w[1]]
            holst = [txt.split("HolsterInternal ")[1].split(" state")[0] for p, tag, txt in s.sv_ev
                     if tag == "TRANSLOC" and "HolsterInternal" in txt and w[0] <= p < w[1]]
            presses4 = s.press_cmds(t, B_OFF4)
            pressA = s.press_cmds(t, B_ATTACK)
            ph = [st_ for st_ in s.states.get(run, []) if st_["ph"]]
            row = {"session": s.name, "run": run, "schedule": t["schedule"], "ok": bool(t.get("ok")),
                   "warmup": bool(t.get("warmup")), "why": t.get("why", ""), "reset_weapon": t["reset_weapon"],
                   "breach_entries": len(ent), "holsters": holst, "press_offhand4": len(presses4),
                   "press_attack": len(pressA), "ph_frames": len(ph),
                   "ph_dur": (ph[-1]["t"] - ph[0]["t"] + DT) if ph else None, "entries": []}
            pa = s.sv_plat_of_cmd(pressA[0])[0] if pressA else None
            aim = EYE / math.tan(math.radians(PITCH[t["schedule"]])) if t["schedule"] in PITCH else None
            for p0 in ent:
                reentry = any(0 <= rp - p0 < 0.1 for rp in reset_plats) or any(0 <= p0 - q < 0.01 for q in passed)
                # the breach is a gap in the dedi MT: last row printed before the entry, first row after it
                before = [c for c in s.sv_cmds if s.sv_mt[c]["plat"] <= p0]
                after = [c for c in s.sv_cmds if s.sv_mt[c]["plat"] > p0 and before and c > before[-1] + 5][:1]
                e = {"plat_rel_window": p0 - w[0], "reentry": reentry}
                if before and after:
                    j = {"prev_cmd": before[-1], "cmd": after[0]}
                    r0, r1 = s.sv_mt[j["prev_cmd"]], s.sv_mt[j["cmd"]]
                    start, exitp = r0["po"], r1["o"]
                    if reentry:   # the reset put the player back on the start (entry portal) while MT was silent
                        nr = [o for p, run_, o, w_ in s.resets if 0 <= p - p0 < 0.1]
                        start = nr[0] if nr else start
                    dist = d2(start, exitp)
                    ptime = min(max(dist / 1200.0, 0.3), 1.8)
                    nfr = int(ptime / 0.1 + 0.5)
                    land = None
                    for k in range(j["cmd"] + 1, j["cmd"] + 240):
                        r = s.sv_mt.get(k)
                        if r and r["ground"]:
                            land = k
                            break
                    airv = [s.sv_mt[k]["pv"][2] for k in range(j["cmd"], land or j["cmd"]) if k in s.sv_mt]
                    e.update({"last_cmd_before": j["prev_cmd"], "first_cmd_after": j["cmd"],
                              "gap_cmds": j["cmd"] - j["prev_cmd"] - 1, "gap_s_cmd": (j["cmd"] - j["prev_cmd"] - 1) * DT,
                              "gap_s_plat": r1["plat"] - p0,
                              "attack_to_entry_s": (p0 - pa) if (pa and not reentry) else None,
                              "start": r3(start, 2), "exit": r3(exitp, 2), "dist2d": dist,
                              "aim_dist": aim if not reentry else None,
                              "exit_short": (aim - dist) if (aim and not reentry) else None,
                              "exit_dz_above_start": exitp[2] - start[2], "exit_v": r3(r1["v"], 3),
                              "exit_speed": math.sqrt(sum(x * x for x in r1["v"])),
                              "src_path_time": ptime, "src_path_frames": nfr,
                              "land_cmds_after_exit": (land - j["cmd"]) if land else None,
                              "land_vz_min": min(airv) if airv else None, "msc_after": r1["msc"],
                              "fwd_after": r1.get("b")})
                row["entries"].append(e)
                entries_all.append((row, e))
            rows.append(row)
    out(f"{'session':14s} {'sched':16s} run   ok wu rst_weapon              o4 at ent  re  gap(cmd) gap_s  plat_s att->ent  dist    aim  short  exit_dz |v_exit| land ph_dur why")
    f = lambda v, n=3, w=6: (f"{v:{w}.{n}f}" if v is not None else " " * (w - 1) + "-")
    for r in rows:
        es = r["entries"] or [{}]
        for k, e in enumerate(es):
            head = (f"{r['session'][16:]:14s} {r['schedule']:16s} {r['run']:5d} {'Y' if r['ok'] else 'n'}  {'w' if r['warmup'] else ' '} "
                    f"{str(r['reset_weapon']):25s} {r['press_offhand4']:2d} {r['press_attack']:2d} {r['breach_entries']:2d}") if k == 0 else " " * 78
            out(f"{head}  {'R' if e.get('reentry') else ' '}  {str(e.get('gap_cmds', '-')):>5s}  {f(e.get('gap_s_cmd'))} {f(e.get('gap_s_plat'))} "
                f"{f(e.get('attack_to_entry_s'))} {f(e.get('dist2d'), 1, 6)} {f(e.get('aim_dist'), 0, 5)} {f(e.get('exit_short'), 1, 6)} "
                f"{f(e.get('exit_dz_above_start'), 2)} {f(e.get('exit_speed'), 3)} {str(e.get('land_cmds_after_exit', '-')):>4s} "
                f"{f(r.get('ph_dur')) if k == 0 else '      '} {r['why'][:38] if k == 0 else ''}")
    good = [(r, e) for r, e in entries_all if r["ok"] and not r["warmup"] and not e["reentry"] and e.get("gap_cmds") is not None]
    reent = [(r, e) for r, e in entries_all if e["reentry"] and e.get("gap_cmds") is not None]
    out("summary (primary breaches in ok, non-warm-up trials):")
    summ = {}
    keys = ("dist2d", "gap_cmds", "gap_s_cmd", "gap_s_plat", "attack_to_entry_s", "exit_short", "exit_dz_above_start",
            "exit_speed", "src_path_time", "src_path_frames", "land_cmds_after_exit", "land_vz_min")
    for sch in sorted(set(r["schedule"] for r, e in good)):
        g = [e for r, e in good if r["schedule"] == sch]
        summ[sch] = {k: stats([e[k] for e in g]) for k in keys}
        summ[sch]["ph_dur"] = stats([r["ph_dur"] for r, e in good if r["schedule"] == sch])
        out(f"  {sch:16s} n={len(g)} dist {fmt(summ[sch]['dist2d'], 1)}; freeze gap {fmt(summ[sch]['gap_s_cmd'])} s "
            f"(cmds {fmt(summ[sch]['gap_cmds'], 1)}); source path time {fmt(summ[sch]['src_path_time'])} "
            f"({fmt(summ[sch]['src_path_frames'], 0)} x 0.1 s path frames)")
        out(f"      attack->entry {fmt(summ[sch]['attack_to_entry_s'])} s; exit short of aim {fmt(summ[sch]['exit_short'], 1)} u; "
            f"exit dz {fmt(summ[sch]['exit_dz_above_start'], 2)}; |v| at exit {fmt(summ[sch]['exit_speed'], 3)}; "
            f"client ph {fmt(summ[sch]['ph_dur'])} s; land after {fmt(summ[sch]['land_cmds_after_exit'], 1)} cmds, vz {fmt(summ[sch]['land_vz_min'], 2)}")
    if reent:
        out(f"  re-entries (reset onto the live entry portal): n={len(reent)}; freeze gap {fmt(stats([e['gap_s_cmd'] for r, e in reent]))} s; "
            f"dist {fmt(stats([e['dist2d'] for r, e in reent]), 1)}; |v| at exit {fmt(stats([e['exit_speed'] for r, e in reent]), 3)}; "
            f"entry {fmt(stats([e['plat_rel_window'] for r, e in reent]), 2)} s after the trial's reset")
    if len(good) >= 3:
        fit = linfit([e["src_path_frames"] for r, e in good], [e["gap_s_cmd"] for r, e in good])
        fit2 = linfit([e["dist2d"] for r, e in good], [e["gap_s_cmd"] for r, e in good])
        if fit:
            out(f"  freeze gap vs source path frames: gap = {fit[0]:.4f} + {fit[1]:.4f} * frames (rms {fit[2]:.4f} s, n={len(good)})")
            P["ash.freeze_gap_vs_frames"] = {"value": {"a": fit[0], "b_per_frame": fit[1]}, "unit": "s",
                                             "source": "dedi MT command gap vs round(clamp(d/1200,0.3,1.8)/0.1)", "n": len(good), "rms": fit[2]}
        if fit2:
            out(f"  freeze gap vs distance: gap = {fit2[0]:.4f} + {fit2[1] * 1000:.4f} ms/u * d (rms {fit2[2]:.4f} s; 1/slope {1 / fit2[1]:.0f} u/s)")
            P["ash.freeze_gap_vs_dist"] = {"value": {"a": fit2[0], "b": fit2[1]}, "unit": "s, s/u", "source": "dedi MT command gap",
                                           "n": len(good), "rms": fit2[2]}
    ev = [e["exit_speed"] for r, e in good]
    P["ash.exit_speed"] = {"value": stats(ev).get("mean"), "unit": "u/s", "source": "dedi MT pre-velocity on the first post-breach cmd",
                           "n": len(ev), "spread": [stats(ev).get("min"), stats(ev).get("max")]}
    P["ash.exit_height_above_start"] = {"value": stats([e["exit_dz_above_start"] for r, e in good]).get("mean"), "unit": "u",
                                        "source": "dedi MT", "n": len(good)}
    at = stats([e["attack_to_entry_s"] for r, e in good])
    P["ash.attack_to_entry"] = {"value": at.get("mean"), "unit": "s", "source": "client attack press cmd -> dedi PhaseTunnel_PhaseEntity",
                                "n": at.get("n"), "spread": [at.get("min"), at.get("max")]}
    for sch, sm in summ.items():
        P[f"ash.{sch}.freeze_gap"] = {"value": sm["gap_s_cmd"].get("mean"), "unit": "s", "source": "dedi MT command gap",
                                      "n": sm["gap_s_cmd"].get("n"), "spread": [sm["gap_s_cmd"].get("min"), sm["gap_s_cmd"].get("max")]}
        P[f"ash.{sch}.dist"] = {"value": sm["dist2d"].get("mean"), "unit": "u", "source": "dedi MT start -> exit", "n": sm["dist2d"].get("n")}
    first = [r for r in rows if r["session"].endswith("_M6B_ash") and r["ok"]]
    if first:
        out(f"  first run (tap offhand4 only): breach entries {sum(r['breach_entries'] for r in first)} in {len(first)} ok trials; "
            f"attack presses {sum(r['press_attack'] for r in first)}; reset weapon per trial: "
            f"{' '.join('B' if r['reset_weapon'] == 'mp_weapon_phase_breach' else 'm' for r in first)} (B = breach weapon still raised)")
    fails = [r for r in rows if not r["ok"]]
    out(f"  failed (not ok) trials: {len(fails)}; why: {sorted(set(r['why'][:45] for r in fails))}")
    out()
    R["ash"] = {"trials": rows, "summary": summ}


# ============================================================================ Valkyrie
def jet_step(vz, t):
    th = M4["T"] * ((t / M4["R"]) * (1 - M4["s0"]) + M4["s0"] if t <= M4["R"] else 1.0)
    vin = vz
    v = vz + G * th * DT
    tight = M4["tu"] if v > 0 else M4["td"]
    v = math.exp(-math.log(2) / tight * DT) * v
    term = (th - 1) * G * DT / (1 - math.exp(-math.log(2) / M4["tu"] * DT))
    if vin > 0 and vin - term > 0.01:
        v = vin + vin * (math.exp(-math.log(2) / M4["above"] * DT) - 1) + G * DT
    return v


def valk(sessions, R, P):
    out("== VALKYRIE, VTOL jets (passive; hold +jump airborne) ==")
    rows = []
    for s in sessions:
        for t in s.scored():
            run = t["run"]
            stl = s.states.get(run, [])
            ed = t["edges"]
            air = [e for e in ed if e["edge"] == "waitair"]
            land_e = [e for e in ed if e["edge"] == "waitland"]
            downs = [e for e in ed if e["edge"] == "down" and e["key"] == "jump" and air and e["frame"] > air[0]["frame"]]
            ups = [e for e in ed if e["edge"] == "up" and e["key"] == "jump" and air and e["frame"] > air[0]["frame"]]
            row = {"session": s.name, "run": run, "schedule": t["schedule"], "glide_start": stl[0]["glide"] if stl else None,
                   "pulses": []}
            ts = [x["t"] for x in stl]
            gl = [x["glide"] for x in stl]

            def idx_after(tt):
                for i, x in enumerate(ts):
                    if x >= tt - 1e-4:
                        return i
                return None

            for k, dn in enumerate(downs):
                up = ups[k] if k < len(ups) else None
                i0 = idx_after(dn["t"])
                if i0 is None or i0 == 0:
                    continue
                g_before = gl[i0 - 1]
                # first frame where the meter drops by > 0.5 (activation)
                ia = next((i for i in range(i0, min(i0 + 6, len(gl))) if gl[i] < g_before - 0.5), None)
                iu = idx_after(up["t"]) if up else len(gl) - 1
                # held, non-empty frames
                held = [(ts[i], gl[i]) for i in range((ia or i0) + 2, iu - 1) if gl[i] > 0.0]
                # drop dips of one frame (client prediction) are excluded by a median filter
                fit = None
                if len(held) >= 5:
                    hx, hy = [h[0] for h in held], [h[1] for h in held]
                    fit = linfit(hx, hy)
                    if fit and fit[2] > 0.002:   # remove outliers > 3x rms once
                        keep = [(x, y) for x, y in held if abs(y - (fit[0] + fit[1] * x)) < 0.005]
                        if len(keep) >= 5:
                            fit = linfit([q[0] for q in keep], [q[1] for q in keep])
                cost = None
                if fit and ia is not None:
                    t_act = ts[ia - 1] if ia > 0 else ts[ia]   # meter still full on this frame
                    cost = g_before - (fit[0] + fit[1] * t_act)
                elif ia is not None and up:
                    # short pulse: drop on activation frame minus one frame of drain (rate from the long holds)
                    cost = None
                empty_t = next((ts[i] for i in range(ia or i0, len(gl)) if gl[i] <= 0.0), None)
                g_up = gl[iu] if iu is not None and iu < len(gl) else None
                row["pulses"].append({"t_down": dn["t"], "t_up": up["t"] if up else None, "hold": (up["t"] - dn["t"]) if up else None,
                                      "g_before": g_before, "act_frame_delay": (ia - i0) if ia is not None else None,
                                      "drop_first_frame": (g_before - gl[ia]) if ia is not None else None,
                                      "drain_rate": -fit[1] if fit else None, "fit_rms": fit[2] if fit else None,
                                      "activation_cost": cost, "g_at_release": g_up,
                                      "t_empty_after_down": (empty_t - dn["t"]) if empty_t and up and empty_t < up["t"] else None})
            # between pulses: meter change in the gaps
            gaps = []
            for k in range(len(row["pulses"]) - 1):
                a = idx_after(row["pulses"][k]["t_up"] + 2 * DT)
                b = idx_after(row["pulses"][k + 1]["t_down"]) - 1
                if a is not None and b is not None and b > a:
                    gaps.append(gl[b] - gl[a])
            row["gap_change"] = gaps
            # pulse drain from (g_before - g_release - cost) / hold, using the hold-trial cost
            t_land = land_e[0]["t"] if land_e else None
            last_up = ups[-1]["t"] if ups else None
            # recharge start: first frame after landing with a rise
            rech = None
            if t_land:
                il = idx_after(t_land)
                for i in range(max(il or 1, 1), len(gl)):
                    if gl[i] > gl[i - 1] + 1e-4 and gl[i - 1] >= 0 and (i + 1 < len(gl) and gl[i + 1] > gl[i]):
                        rech = i
                        break
            row["t_land_after_last_up"] = (t_land - last_up) if t_land and last_up else None
            row["air_change_after_jets"] = None
            if last_up and t_land:
                a, b = idx_after(last_up + 3 * DT), idx_after(t_land)
                if a is not None and b is not None:
                    row["air_change_after_jets"] = gl[b] - gl[a]
            row["glide_end"] = gl[-1] if gl else None
            row["trial_end_after_land"] = (ts[-1] - t_land) if t_land and ts else None
            if rech is not None:
                xs = [ts[i] for i in range(rech, min(rech + 120, len(gl)))]
                ys = [gl[i] for i in range(rech, min(rech + 120, len(gl)))]
                f = linfit(xs, ys)
                t0 = (gl[rech - 1] - f[0]) / f[1] if f else None  # time the fit crosses the pre-recharge level
                row.update({"recharge_rate": f[1] if f else None, "recharge_fit_rms": f[2] if f else None,
                            "recharge_start_after_land": (t0 - t_land) if t0 else None,
                            "recharge_start_after_last_up": (t0 - last_up) if t0 and last_up else None,
                            "recharge_from": gl[rech - 1]})
                emp = row["pulses"][0].get("t_empty_after_down") if row["pulses"] else None
                if emp and t0:
                    row["recharge_start_after_empty"] = t0 - (row["pulses"][0]["t_down"] + emp)
            else:
                row.update({"recharge_rate": None, "recharge_start_after_land": None})
            # ---------------- dedi dynamics
            sv = sorted(s.sv_rows(run), key=lambda r: r["cmd"])
            byc = {r["cmd"]: r for r in sv}
            act = []
            prevj = False
            for r in sv:
                on = bool(r["b"] & B_JUMP)
                if on and not prevj and not r["ground"]:
                    act.append(r["cmd"])
                prevj = on
            dyn = []
            for k0 in act:
                res, fuel_stop = [], None
                c = k0
                while c in byc and (byc[c]["b"] & B_JUMP):
                    r, nx = byc[c], byc.get(c + 1)
                    if nx is None:
                        break
                    tt = (c - k0) * DT
                    post, npre = r["pv"][2], nx["v"][2]
                    # fuel stop: jump still held but the jet step is replaced by the stop cut (x0.4 below the terminal)
                    if fuel_stop is None and tt > 1.0 and abs(npre - 0.4 * post) < 0.05:
                        fuel_stop = (c, tt, post, npre)
                    if fuel_stop is None:
                        res.append((c, tt, npre - jet_step(post, tt), post, npre, r["v"][2]))
                    c += 1
                rel = c  # first cmd without jump (release) or end of the held run
                errs = [e for (cc, tt, e, post, npre, pre) in res]
                term = [pre for (cc, tt, e, post, npre, pre) in res if 3.0 <= tt <= 6.5]
                d = {"k0": k0, "held_cmds": c - k0, "n_resid": len(errs),
                     "resid_rms": math.sqrt(sum(e * e for e in errs) / len(errs)) if errs else None,
                     "resid_max": max((abs(e) for e in errs), default=None),
                     "resid_gt_0p1": sum(1 for e in errs if abs(e) > 0.1),
                     "terminal_pre_vz": stats(term).get("mean") if term else None, "terminal_n": len(term),
                     "peak_pre_vz": max((pre for (cc, tt, e, post, npre, pre) in res), default=None)}
                if fuel_stop:
                    d.update({"fuel_stop_t": fuel_stop[1], "fuel_stop_post_vz": fuel_stop[2],
                              "fuel_stop_next_pre_vz": fuel_stop[3], "fuel_stop_scale": fuel_stop[3] / fuel_stop[2]})
                    stop_c = fuel_stop[0] + 1
                else:
                    r, nx = byc.get(rel), byc.get(rel + 1)
                    if r and nx:
                        # stop runs inside the release cmd after its air move: next pre / this post
                        d.update({"release_post_vz": r["pv"][2], "release_next_pre_vz": nx["v"][2],
                                  "release_scale": nx["v"][2] / r["pv"][2] if r["pv"][2] else None})
                    stop_c = rel + 1
                # post effect: per-cmd dvz (post - pre) while airborne after the stop; low g = -0.45*g*dt
                low, full, first_full = 0, 0, None
                for cc in range(stop_c, stop_c + 1500):
                    r = byc.get(cc)
                    if r is None or r["ground"] or (cc in act):
                        break
                    dv = r["pv"][2] - r["v"][2]
                    if abs(dv + 0.45 * G * DT) < 0.05:
                        low += 1
                    elif abs(dv + G * DT) < 0.05:
                        full += 1
                        if first_full is None:
                            first_full = cc
                d.update({"post_lowg_cmds": low, "post_fullg_cmds": full, "post_lowg_s": low * DT,
                          "first_fullg_after_stop_s": (first_full - stop_c) * DT if first_full else None,
                          "first_fullg_height": (byc[first_full]["o"][2] - 294.274) if first_full else None})
                dyn.append(d)
            zmax = max((r["po"][2] for r in sv), default=None)
            landing_vz = None
            for i in range(1, len(sv)):
                if sv[i]["ground"] and not sv[i - 1]["ground"] and act and sv[i]["cmd"] > act[0]:
                    landing_vz = min(x["pv"][2] for x in sv[max(0, i - 3):i])
            row.update({"dyn": dyn, "apex_height": (zmax - 294.274) if zmax else None, "landing_vz": landing_vz})
            rows.append(row)
    # print
    f = lambda v, n=4: f"{v:.{n}f}" if v is not None else "-"
    for r in rows:
        out(f"-- {r['schedule']} run {r['run']}: meter at start {r['glide_start']}, apex {f(r['apex_height'], 1)} u, landing vz {f(r['landing_vz'], 1)}")
        for k, p in enumerate(r["pulses"]):
            out(f"   jets {k}: hold {f(p['hold'], 3)} s, meter {f(p['g_before'])}, drop on the first state frame {f(p['drop_first_frame'])} "
                f"(+{p['act_frame_delay']} frame), drain {f(p['drain_rate'])}/s (rms {f(p['fit_rms'], 5)}), activation cost {f(p['activation_cost'])}, "
                f"meter at release {f(p['g_at_release'])}, empty {f(p['t_empty_after_down'], 3)} s after the press")
        out(f"   meter change in the pulse gaps {[round(x, 4) for x in r['gap_change']]}; airborne after the last jets {f(r['air_change_after_jets'])}; "
            f"landed {f(r['t_land_after_last_up'], 3)} s after the last release; recharge start {f(r.get('recharge_start_after_land'), 3)} s after landing "
            f"({f(r.get('recharge_start_after_last_up'), 3)} after the last release, {f(r.get('recharge_start_after_empty'), 3)} after empty) "
            f"at {f(r.get('recharge_rate'))}/s; trial ends {f(r['trial_end_after_land'], 3)} s after landing with meter {f(r['glide_end'])}")
        for d in r["dyn"]:
            stop = (f"fuel stop {f(d.get('fuel_stop_t'), 3)} s after activation: post vz {f(d.get('fuel_stop_post_vz'), 3)} -> next pre {f(d.get('fuel_stop_next_pre_vz'), 3)} "
                    f"(x{f(d.get('fuel_stop_scale'), 5)})") if d.get("fuel_stop_t") else \
                   (f"release: post vz {f(d.get('release_post_vz'), 3)} -> next pre {f(d.get('release_next_pre_vz'), 3)} (x{f(d.get('release_scale'), 5)})")
            out(f"   dedi jets k0={d['k0']}: {d['held_cmds']} held cmds; M4 one-step vz residual rms {f(d['resid_rms'])} max {f(d['resid_max'])} "
                f"(>0.1: {d['resid_gt_0p1']} of {d['n_resid']}); peak pre vz {f(d['peak_pre_vz'], 2)}; terminal pre vz {f(d['terminal_pre_vz'], 3)} (n {d['terminal_n']}); "
                f"{stop}; then low-g {d['post_lowg_cmds']} cmds ({d['post_lowg_s']:.3f} s), full-g {d['post_fullg_cmds']} cmds, "
                f"first full g {f(d['first_fullg_after_stop_s'], 3)} s after the stop at h {f(d['first_fullg_height'], 1)} u")
    hold = [r for r in rows if r["schedule"] == "b_valk_hold10"]
    pulse = [r for r in rows if r["schedule"] == "b_valk_pulse"]
    drain = [p["drain_rate"] for r in hold for p in r["pulses"] if p["drain_rate"]]
    cost = [p["activation_cost"] for r in hold for p in r["pulses"] if p["activation_cost"] is not None]
    dm = stats(drain).get("mean") or 1.0
    pcost = [p["g_before"] - p["g_at_release"] - dm * p["hold"] for r in pulse for p in r["pulses"]
             if p["g_at_release"] is not None and p["hold"]]
    empty = [p["t_empty_after_down"] for r in hold for p in r["pulses"] if p["t_empty_after_down"]]
    rr = [r["recharge_rate"] for r in rows if r.get("recharge_rate")]
    rsl = [r["recharge_start_after_land"] for r in rows if r.get("recharge_start_after_land") is not None]
    rse = [r.get("recharge_start_after_empty") for r in rows if r.get("recharge_start_after_empty") is not None]
    rsu = [r.get("recharge_start_after_last_up") for r in rows if r.get("recharge_start_after_last_up") is not None]
    term = [d["terminal_pre_vz"] for r in hold for d in r["dyn"] if d["terminal_pre_vz"]]
    rms = [d["resid_rms"] for r in rows for d in r["dyn"] if d["resid_rms"] is not None]
    allerr_n = sum(d["n_resid"] for r in rows for d in r["dyn"])
    big = sum(d["resid_gt_0p1"] for r in rows for d in r["dyn"])
    fs = [d.get("fuel_stop_t") for r in hold for d in r["dyn"] if d.get("fuel_stop_t")]
    fsc = [d.get("fuel_stop_scale") for r in hold for d in r["dyn"] if d.get("fuel_stop_scale")]
    lowg = [d["post_lowg_s"] for r in hold for d in r["dyn"]]
    ffh = [d["first_fullg_height"] for r in hold for d in r["dyn"] if d["first_fullg_height"] is not None]
    rel_sc = [d["release_scale"] for r in pulse for d in r["dyn"] if d.get("release_scale")]
    rel_vz = [d["release_post_vz"] for r in pulse for d in r["dyn"] if d.get("release_post_vz")]
    plow = [d["post_lowg_cmds"] for r in pulse for d in r["dyn"]]
    peak = [d["peak_pre_vz"] for r in pulse for d in r["dyn"] if d["peak_pre_vz"]]
    nact = [len(r["dyn"]) for r in pulse]
    out("summary:")
    out(f"  meter at trial start {sorted(set(r['glide_start'] for r in rows))} (the runner reset refills it; census glideDuration 8)")
    out(f"  drain while held (hold10) {fmt(stats(drain), 4)} /s; activation cost (hold10, fit extrapolated to the press) {fmt(stats(cost), 4)}")
    out(f"  activation cost from pulses (meter drop - drain x hold) {fmt(stats(pcost), 4)}; activations per pulse trial (dedi) {nact}")
    out(f"  hold10: meter empty {fmt(stats(empty))} s after the press (= (8 - 1) / 1); dedi fuel stop {fmt(stats(fs))} s after activation; "
        f"vz scale at the fuel stop {fmt(stats(fsc), 5)}; low-g after the fuel stop {fmt(stats(lowg))} s (census jetpackPostEffectTime 3); "
        f"full g resumes at h {fmt(stats(ffh), 1)} u")
    out(f"  pulse releases (0.3 s holds): post vz at release {fmt(stats(rel_vz), 1)}; next-pre/post {fmt(stats(rel_sc), 5)}; low-g cmds after "
        f"release {sorted(set(plow))}; peak pre vz per pulse {fmt(stats(peak), 1)}")
    out(f"  terminal pre vz (3..6.5 s, no input) {fmt(stats(term), 3)} (M4 model 260.13); M4 one-step residual rms per activation {fmt(stats(rms), 4)} u/s; "
        f"|resid| > 0.1 u/s in {big} of {allerr_n} cmds")
    out(f"  recharge: rate {fmt(stats(rr), 4)} /s; start after landing {fmt(stats(rsl))} s; after the last release {fmt(stats(rsu))} s; after empty {fmt(stats(rse))} s")
    out(f"  airborne meter change between the last release and landing: {[round(r['air_change_after_jets'], 4) if r['air_change_after_jets'] is not None else None for r in rows]}")
    out(f"  apex: hold10 {fmt(stats([r['apex_height'] for r in hold]), 1)} u, pulse {fmt(stats([r['apex_height'] for r in pulse]), 1)} u; "
        f"landing vz hold10 {fmt(stats([r['landing_vz'] for r in hold]), 1)}, pulse {fmt(stats([r['landing_vz'] for r in pulse]), 1)}")
    out()
    R["valkyrie"] = {"trials": rows}

    def sp(v):
        s_ = stats(v)
        return {"n": s_.get("n"), "spread": [s_.get("min"), s_.get("max")], "value": s_.get("mean")}
    P["valk.meter_drain_rate"] = dict(sp(drain), unit="1/s", source="client glide= (HSD-STATE) slope while held (hold10)")
    P["valk.meter_activation_cost"] = dict(sp(cost + pcost), unit="meter", source="client glide= step at activation (hold10 + pulses)")
    P["valk.meter_max"] = {"value": 8.0, "unit": "meter (= seconds at drain 1)", "source": "glide= at trial start; census glideDuration", "n": len(rows)}
    P["valk.time_to_empty_continuous"] = dict(sp(empty), unit="s", source="client glide= reaches 0 while held")
    P["valk.fuel_stop_vz_scale"] = dict(sp(fsc), unit="", source="dedi MT next pre / post vz at the fuel stop (vz 253.9 < terminal 265.75)")
    P["valk.post_effect_time"] = dict(sp(lowg), unit="s", source="dedi MT dvz = -0.45 g per cmd after the fuel stop (high altitude, probe not reached)")
    P["valk.release_above_terminal_scale"] = dict(sp(rel_sc), unit="", source="dedi MT next pre / post vz on a 0.3 s pulse release (vz > 265.75)")
    P["valk.recharge_rate"] = dict(sp(rr), unit="1/s", source="client glide= slope after the recharge starts")
    P["valk.recharge_delay_after_landing"] = dict(sp(rsl), unit="s", source="client glide=, waitland edge (hold10 only)")
    P["valk.recharge_delay_after_release"] = dict(sp(rsu), unit="s", source="client glide=, jump up edge (hold10 only)")
    P["valk.terminal_pre_vz"] = dict(sp(term), unit="u/s", source="dedi MT pre vz 3..6.5 s after activation")
    P["valk.m4_model_resid_rms"] = dict(sp(rms), unit="u/s per cmd", source="one-step (post_i -> pre_i+1) residual of the M4 jets model")
    P["valk.apex_hold10"] = dict(sp([r["apex_height"] for r in hold]), unit="u", source="dedi MT")


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args()
    sessions = [Session(f) for f in a.sessions]
    out("M6-B legend mobility analysis. Sessions: " + ", ".join(f"{s.name} ({s.legend}, {len(s.scored())} scored)" for s in sessions))
    out()
    R, P = {"sessions": [{"name": s.name, "legend": s.legend, "schedules": sorted(set(t["schedule"] for t in s.trials)),
                          "trials": len(s.trials), "scored": len(s.scored())} for s in sessions]}, {}
    census(sessions, R, P)
    by = {}
    for s in sessions:
        by.setdefault(s.legend, []).append(s)
    if "alter" in by:
        alter(by["alter"], R, P)
    if "loba" in by:
        loba(by["loba"], R, P)
    if "ash" in by:
        ash(by["ash"], R, P)
    if "valkyrie" in by:
        valk(by["valkyrie"], R, P)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(R, fh, indent=1, default=str)
    if a.params:
        with open(a.params, "w", encoding="utf-8") as fh:
            json.dump(P, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
