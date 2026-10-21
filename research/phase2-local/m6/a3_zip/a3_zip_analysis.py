#!/usr/bin/env python3
"""M6-A3 zipline analysis (Apex R5Flowstate S21, 120 fps, Gibraltar, empty-handed).

    py -3 a3_zip_analysis.py <session folder> [<session folder> ...] [--json results.json] [--params params.json]

Each session folder holds runner.json, report/rows.csv (hsd_tel output) and platform/logs (hsd_session.py layout).
Only trials with ok=true and warmup=false are used. stdlib only; prints no absolute paths.

Data sources (all read-only):
  * HSD client frames (rows.csv source HSD, side cl, kind frame, drv_run r<run>): one row per client frame = per usercmd
    at 120 fps, post-state origin / velocity / ground / view. These are the only per-command record while the player
    is on the rope: the native MOVE-TRACE hook is not reached on zipline commands, so MT has a gap from the mount
    command to the detach command (inclusive).
  * MOVE-TRACE (source MT, side cl = native client, side sv = dedi): rows before the mount and after the detach. MT rows
    are assigned to a trial by command number (from the first r<run> row to the next trial's first row), because
    hsd_tel labels the post-gap rows as bursts (b<n>).
  * SDK diag lines in platform/logs: [ZIPRAIL-USE] (mount command, server Find point), [ZIP-JUMPOFF] (native jump-off
    result velocity, client and dedi), [ZIP-MOVESTOP]/[ZIP-FORCE] (detach command), [ZIP-EXIT] (auto-detach rule, the
    dedi prints only its first 4), [ZIP-DISC] (re-mount budget, first lines only).
  * Player settings: rows.csv CV rows (client [CLASSVAR] census) and the warning log 'unknown key' lines.
The client [HSD-STATE] logger did not compile in this session, so the zipline state is inferred from motion + diag.
Key edges come from runner.json sched_lines; an edge at frame f maps to the first HSD frame with t > edge t
(that frame shows the post-state of the command that carried the edge; checked against the edge frame number).
"""
import argparse
import csv
import glob
import json
import math
import os
import re
import statistics as st
import sys

# ----------------------------------------------------------------------------- geometry (hsd_trial.py ZIP_SERVER)
ROPES = {
    "Z1": {"a": (-14600.0, 6800.0, 394.92), "b": (-13000.0, 6800.0, 394.92), "detach": 100.0, "vertical": False},
    "Z2": {"a": (-14500.0, 6350.0, 394.92), "b": (-12900.0, 6350.0, 694.92), "detach": 100.0, "vertical": False},
    "Z3": {"a": (-14700.0, 6500.0, 314.92), "b": (-14700.0, 6500.0, 1114.92), "detach": 0.0, "vertical": True},
}
SCHED_ROPE = {"z6_up": "Z2", "z6_vert": "Z3", "z6_vert_turn": "Z3"}  # everything else uses Z1
FLOOR_Z = 294.92
EYE_RAISE = 72.0          # Zipline_Find search origin = origin + 72 (SOURCE-AUDIT A3, zipline_exit_parity.cpp:281)
IN_USE, IN_JUMP, IN_DUCK = 0x20, 0x2, 0x4
JUMP_CAP_FIT = 400.0      # hypothesis tested below (not tuned: it is the observed plateau, residuals printed)

COLS = ("source", "side", "kind", "t", "ft", "cmd", "ox", "oy", "oz", "vx", "vy", "vz", "pox", "poy", "poz",
        "pvx", "pvy", "pvz", "pitch", "yaw", "ground", "crouch", "duck", "buttons", "in_jump", "in_duck",
        "drv_run", "key", "value")
NUM = ("t", "ft", "ox", "oy", "oz", "vx", "vy", "vz", "pox", "poy", "poz", "pvx", "pvy", "pvz", "pitch", "yaw")


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def inum(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(a, s):
    return tuple(x * s for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def unit(a):
    n = norm(a)
    return mul(a, 1.0 / n) if n > 1e-9 else None


def rnd(x, n=3):
    if x is None:
        return None
    if isinstance(x, (list, tuple)):
        return [rnd(v, n) for v in x]
    return round(x, n)


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return {"n": len(xs), "mean": rnd(st.mean(xs), 4), "sd": rnd(st.pstdev(xs), 4) if len(xs) > 1 else 0.0,
            "min": rnd(min(xs), 4), "max": rnd(max(xs), 4)}


def eye_dir(pitch, yaw):
    p, y = math.radians(pitch or 0.0), math.radians(yaw or 0.0)   # Source: + pitch = down
    return (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), -math.sin(p))


def rope_dir(r):
    return unit(sub(ROPES[r]["b"], ROPES[r]["a"]))


def rope_point(r, s):
    return add(ROPES[r]["a"], mul(rope_dir(r), s))


def rope_param(r, p):
    return dot(sub(p, ROPES[r]["a"]), rope_dir(r))


def rope_param_h(r, p):
    """Rope parameter of the rope point at the same horizontal position along the rope (non-vertical ropes)."""
    d = rope_dir(r)
    h = math.hypot(d[0], d[1])
    return ((p[0] - ROPES[r]["a"][0]) * d[0] + (p[1] - ROPES[r]["a"][1]) * d[1]) / (h * h)


def rope_len(r):
    return norm(sub(ROPES[r]["b"], ROPES[r]["a"]))


# ----------------------------------------------------------------------------- loading
def load_rows(folder):
    frames, mt = {}, {"cl": [], "sv": []}
    cv = {}
    with open(os.path.join(folder, "report", "rows.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            src, kind = r["source"], r["kind"]
            if src == "CV":
                cv[r["key"]] = r["value"]
                continue
            if not ((src == "MT" and kind == "cmd") or (src == "HSD" and kind == "frame" and r["side"] == "cl")):
                continue
            d = {k: r.get(k, "") for k in COLS}
            for k in NUM:
                d[k] = fnum(d[k])
            d["cmd"] = inum(d["cmd"])
            d["ground"] = inum(d["ground"])
            d["buttons"] = inum(d["buttons"]) or 0
            d["in_jump"] = inum(d["in_jump"])
            d["in_duck"] = inum(d["in_duck"])
            if src == "HSD":
                frames.setdefault(d["drv_run"], []).append(d)
            else:
                mt[d["side"]].append(d)
    for k in frames:
        frames[k].sort(key=lambda f: f["t"])
    for s in mt:
        mt[s].sort(key=lambda r: r["cmd"])
    return frames, mt, cv


DIAG_RE = re.compile(r"Native\((C|S)\):\[(ZIP[A-Z-]*)\]\s*(.*)")


def load_diag(folder):
    out, unknown_keys, find = [], [], []
    for side in ("client", "server"):
        for fn in sorted(glob.glob(os.path.join(folder, "platform", "logs", side, "*", "*.log"))):
            with open(fn, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "[CLASSVAR] unknown key" in line:
                        m = re.search(r"unknown key '([^']+)'", line)
                        if m:
                            unknown_keys.append(m.group(1))
                    if "find " in line and ("doesn't exist" in line or "Cbuf_AddText" in line):
                        find.append((side, line.strip().split("] ", 2)[-1][:120]))
                    m = DIAG_RE.search(line)
                    if not m:
                        continue
                    body = m.group(3)
                    kv = dict(re.findall(r"(\w+)=([^\s()]+)", body))
                    vec = {k: tuple(float(x) for x in v.split()) for k, v in re.findall(r"(\w+)=\(([-\d. ]+)\)", body)}
                    out.append({"side": "cl" if m.group(1) == "C" else "sv", "tag": m.group(2), "kv": kv,
                                "vec": vec, "cmd": inum(kv.get("cmd")), "body": body})
    return out, sorted(set(unknown_keys)), find


def assign_mt(mt_side, starts):
    """starts: sorted list of (first cmd, run label). Rows from a start until the next start belong to that run."""
    out = {}
    j = -1
    for r in mt_side:
        while j + 1 < len(starts) and r["cmd"] >= starts[j + 1][0]:
            j += 1
        if j >= 0:
            out.setdefault(starts[j][1], {})[r["cmd"]] = r
    return out


def parse_edges(t):
    out = []
    for line in t.get("sched_lines", []):
        kv = dict(re.findall(r"(\w+)=(\S+)", line))
        out.append({"edge": kv.get("edge"), "key": kv.get("key"), "frame": inum(kv.get("frame")),
                    "t": fnum(kv.get("t"))})
    return out


def load_session(folder):
    with open(os.path.join(folder, "runner.json"), encoding="utf-8") as fh:
        runner = json.load(fh)
    frames, mt, cv = load_rows(folder)
    diag, unknown_keys, find = load_diag(folder)
    # trial command ranges from the first r<run> MT row on the client
    starts = {}
    for r in mt["cl"]:
        lab = r["drv_run"]
        if lab.startswith("r") and lab not in starts:
            starts[lab] = r["cmd"]
    starts = sorted((c, lab) for lab, c in starts.items())
    mt_cl, mt_sv = assign_mt(mt["cl"], starts), assign_mt(mt["sv"], starts)
    bounds = {}
    for i, (c, lab) in enumerate(starts):
        bounds[lab] = (c, starts[i + 1][0] - 1 if i + 1 < len(starts) else 10 ** 9)
    trials, skipped = [], []
    for t in runner["trials"]:
        lab = "r%d" % t["run"]
        if t.get("warmup") or not t.get("ok"):
            skipped.append({"run": t["run"], "schedule": t.get("schedule"),
                            "why": "warmup" if t.get("warmup") else "ok=false: %s" % t.get("why")})
            continue
        lo, hi = bounds.get(lab, (None, None))
        dg = [d for d in diag if d["cmd"] is not None and lo is not None and lo <= d["cmd"] <= hi]
        trials.append({"session": os.path.basename(os.path.normpath(folder)), "run": t["run"],
                       "schedule": t["schedule"], "origin": t.get("origin"), "fps": t.get("measured_fps"),
                       "frames": frames.get(lab, []), "cl": mt_cl.get(lab, {}), "sv": mt_sv.get(lab, {}),
                       "diag": dg, "edges": parse_edges(t), "cmd_range": (lo, hi)})
    return {"folder": os.path.basename(os.path.normpath(folder)), "runner": runner, "cv": cv, "trials": trials,
            "skipped": skipped, "unknown_keys": unknown_keys, "find": find, "diag_all": diag}


# ----------------------------------------------------------------------------- per-trial helpers
def edge_index(fr, e):
    for i, f in enumerate(fr):
        if f["t"] > e["t"] + 1e-4:
            return i
    return None


def edges_of(t, key, kind="down"):
    return [e for e in t["edges"] if e["edge"] == kind and e["key"] == key]


def vel(f):
    return (f["vx"], f["vy"], f["vz"])


def pos(f):
    return (f["ox"], f["oy"], f["oz"])


def mt_gap(cl):
    ks = sorted(cl)
    for a, b in zip(ks, ks[1:]):
        if b != a + 1:
            return a, b
    return None


def diag_first(t, tag, side, pred=None):
    for d in t["diag"]:
        if d["tag"] == tag and d["side"] == side and (pred is None or pred(d)):
            return d
    return None


def find_angle_min(rope, P, eye, radius, samples=4000):
    """Smallest angle between the eye direction and (Q - P) over rope points Q with |Q - P| <= radius."""
    best = None
    L = rope_len(rope)
    for i in range(samples + 1):
        Q = rope_point(rope, L * i / samples)
        d = sub(Q, P)
        n = norm(d)
        if n > radius or n < 1e-6:
            continue
        a = math.degrees(math.acos(max(-1.0, min(1.0, dot(d, eye) / n))))
        if best is None or a < best[0]:
            best = (a, Q, n)
    return best


def analyse_trial(t, g_meas):
    fr, cl, sv = t["frames"], t["cl"], t["sv"]
    sch = t["schedule"]
    rope = SCHED_ROPE.get(sch, "Z1")
    out = {"run": t["run"], "schedule": sch, "rope": rope, "n_frames": len(fr), "n_mt_cl": len(cl), "n_mt_sv": len(sv)}
    # edge mapping consistency
    start = [e for e in t["edges"] if e["edge"] == "start"]
    i0 = edge_index(fr, start[0]) if start else None
    mism = 0
    end_f = next((e["frame"] for e in t["edges"] if e["edge"] == "end"), None)
    for e in t["edges"]:
        # an 'up' released on the end frame has no HSD frame after it (the run label is closed): not checkable
        if e["edge"] in ("down", "up") and e["frame"] is not None and i0 is not None and (end_f is None or e["frame"] < end_f):
            ie = edge_index(fr, e)
            if ie is None or ie - i0 != e["frame"] - (start[0]["frame"] or 0):
                mism += 1
    out["edge_map_mismatch"] = mism
    use_e = edges_of(t, "use")
    jump_e = edges_of(t, "jump")
    duck_e = edges_of(t, "duck")
    iu = edge_index(fr, use_e[0]) if use_e else None
    ij = [edge_index(fr, e) for e in jump_e]
    idk = edge_index(fr, duck_e[0]) if duck_e else None
    out["use_frame"] = (iu - i0) if (iu is not None and i0 is not None) else None
    # client diag
    use_cl = diag_first(t, "ZIPRAIL-USE", "cl", lambda d: "result" in d["kv"])
    use_sv = diag_first(t, "ZIPRAIL-USE", "sv", lambda d: "result" in d["kv"])
    out["diag_use_cl"] = {"result": inum(use_cl["kv"].get("result")), "why": use_cl["kv"].get("why"),
                          "cmd": use_cl["cmd"]} if use_cl else None
    out["diag_use_sv"] = {"result": inum(use_sv["kv"].get("result")), "cmd": use_sv["cmd"],
                          "use": rnd(use_sv["vec"].get("use"), 2)} if use_sv else None
    gap = mt_gap(cl)
    out["mt_gap"] = list(gap) if gap else None
    # IN_USE presses visible in MT (only when the command did not mount)
    out["use_press_mt"] = [k for k in sorted(cl) if cl[k]["buttons"] & IN_USE and not (cl.get(k - 1, {}).get("buttons", 0) & IN_USE)]
    # ---------------- mount detection (motion)
    mounted_motion, im = False, None
    if iu is not None and iu > 0 and iu < len(fr):
        pre = fr[iu - 1]
        for i in range(iu, min(len(fr), iu + 30)):
            f = fr[i]
            # mount signature: leaves the ground with a +z step of ~22 u and no vertical velocity
            if f["ground"] == 0 and f["oz"] - pre["oz"] > 15 and abs(f["vz"]) < 1e-6 and norm(vel(f)) < 1e-6:
                mounted_motion, im = True, i
                break
        out["pre_use"] = {"o": rnd(pos(pre), 3), "pitch": pre["pitch"], "yaw": pre["yaw"], "ground": pre["ground"],
                          "v": rnd(vel(pre), 3)}
    out["mounted_motion"] = mounted_motion
    out["mounted_diag_cl"] = bool(use_cl and use_cl["kv"].get("result") == "1")
    out["mounted_diag_sv"] = bool(use_sv and use_sv["kv"].get("result") == "1")
    out["mount_latency_frames"] = (im - iu) if mounted_motion else None
    if gap and use_cl:
        out["mount_cmd_eq_first_missing_mt"] = (use_cl["cmd"] == gap[0] + 1)
    # ---------------- Find geometry
    if iu is not None and iu > 0:
        pre = fr[iu - 1]
        P = add(pos(pre), (0.0, 0.0, EYE_RAISE))
        eye = eye_dir(pre["pitch"], pre["yaw"])
        out["find_P"] = rnd(P, 3)
        out["eye"] = rnd(eye, 4)
        # closest distance from P to the rope segment
        s = max(0.0, min(rope_len(rope), rope_param(rope, P)))
        out["dist_P_rope"] = rnd(norm(sub(rope_point(rope, s), P)), 3)
        if use_sv and "use" in use_sv["vec"]:
            Q = use_sv["vec"]["use"]
            d = sub(Q, P)
            out["find_use_dist"] = rnd(norm(d), 3)
            out["find_use_angle"] = rnd(math.degrees(math.acos(max(-1, min(1, dot(d, eye) / norm(d))))), 3)
            out["find_use_ahead"] = rnd(dot(sub(Q, pos(pre)), (math.cos(math.radians(pre["yaw"] or 0)), math.sin(math.radians(pre["yaw"] or 0)), 0.0)), 3)
        for R in (130.0,):
            b = find_angle_min(rope, P, eye, R)
            out["find_min_angle_R%d" % R] = rnd(b[0], 3) if b else None
            if b:
                out["find_min_angle_point_R%d" % R] = rnd(b[1], 2)
    if not mounted_motion:
        # control / failed: any ziplining signature at all in the trial?
        out["any_air_frames"] = sum(1 for f in fr if f["ground"] == 0)
        return finish_unmounted(t, out, fr, cl, ij, iu, g_meas)
    # ---------------- snap and blend
    pre = fr[iu - 1]
    fm = fr[im]
    out["snap_dz"] = rnd(fm["oz"] - pre["oz"], 3)
    out["snap_dxy"] = rnd(math.hypot(fm["ox"] - pre["ox"], fm["oy"] - pre["oy"]), 3)
    d_hat = rope_dir(rope)
    Q = use_sv["vec"]["use"] if (use_sv and "use" in use_sv["vec"]) else None
    # end of ride = last frame before a velocity discontinuity (jump/duck/auto-detach)
    iend = None
    for i in range(im + 1, len(fr)):
        f, p = fr[i], fr[i - 1]
        jumpish = (ij and i in ij) or (idk is not None and i == idk)
        sp, spp = norm(vel(f)), norm(vel(p))
        if jumpish or (f["ground"] == 1) or abs(sp - spp) > 20 or (not ROPES[rope]["vertical"] and abs(f["vz"] - p["vz"]) > 1.0 and rope == "Z1"):
            iend = i - 1
            break
        if ROPES[rope]["vertical"] and abs(f["vx"]) > 1.0:
            iend = i - 1
            break
        if rope == "Z2" and abs(f["vz"] / max(norm(vel(f)), 1e-6) - d_hat[2]) > 0.01 and norm(vel(f)) > 50:
            iend = i - 1
            break
    out["ride_end_frame_rel"] = (iend - im) if iend is not None else None
    ride = fr[im:(iend + 1 if iend is not None else len(fr))]
    # blend: actual vs ride reference (Find point + integrated rope speed, hang offset from the steady ride)
    steady = [f for k, f in enumerate(ride) if k >= 40]
    if steady:
        hang = st.mean(rope_point(rope, rope_param_h(rope, pos(f)))[2] - f["oz"] if not ROPES[rope]["vertical"] else 0 for f in steady)
        lat = st.mean(f["oy"] - rope_point(rope, rope_param_h(rope, pos(f)))[1] for f in steady) if not ROPES[rope]["vertical"] else st.mean(f["ox"] - ROPES[rope]["a"][0] for f in steady)
        out["hang_below_rope_cl"] = rnd(hang, 3) if not ROPES[rope]["vertical"] else None
        out["lateral_offset_cl"] = rnd(lat, 3)
        if ROPES[rope]["vertical"]:
            out["vertical_rope_dy_cl"] = rnd(st.mean(f["oy"] - ROPES[rope]["a"][1] for f in steady), 3)
    blend = []
    tails = {}
    if Q is not None and not ROPES[rope]["vertical"] and steady:
        p0 = pos(fm)
        hang_vec = (0.0, out["lateral_offset_cl"], -out["hang_below_rope_cl"])
        # rope reference: Find point advanced by the rope speed. Two integrations: with the logged (post-state) speed
        # of the same command, or with the previous command's speed (= position update before the speed update).
        for variant in ("prev", "post"):
            s = rope_param(rope, Q)
            rows_v = []
            for k, f in enumerate(ride[:61]):
                if k > 0:
                    s += norm(vel(f if variant == "post" else ride[k - 1])) * f["ft"]
                ref = add(rope_point(rope, s), hang_vec)
                d0 = norm(sub(p0, ref))
                rows_v.append({"k": k, "b": rnd(1 - norm(sub(pos(f), ref)) / d0, 5) if d0 > 1e-6 else None,
                               "err": rnd(norm(sub(pos(f), ref)), 3), "p0": p0, "ref": ref, "pos": pos(f)})
            tails[variant] = rnd(st.mean(r["err"] for r in rows_v[40:61]), 3)
            if variant == "post":   # semi-implicit: x_k = x_(k-1) + v_k * dt fits the tail better (printed)
                blend = rows_v[:46]
    out["blend"] = blend
    out["blend_tail_err_k40_60"] = tails
    # pitch lock: view pitch after the mount
    out["pitch_pre"] = pre["pitch"]
    out["pitch_after_40"] = ride[40]["pitch"] if len(ride) > 40 else None
    out["pitch_rope"] = rnd(-math.degrees(math.asin(d_hat[2])), 3)
    pk = None
    if pre["pitch"] is not None and len(ride) > 40 and abs(pre["pitch"] - ride[40]["pitch"]) > 1:
        tgt = ride[40]["pitch"]
        for k, f in enumerate(ride):
            if abs(f["pitch"] - tgt) <= 0.1 * abs(pre["pitch"] - tgt):
                pk = k
                break
    out["pitch_90pct_frames"] = pk
    # speed profile
    prof = []
    for k, f in enumerate(ride):
        sp = norm(vel(f))
        a = (sp - norm(vel(ride[k - 1]))) / f["ft"] if k > 0 else None
        pd = norm(sub(pos(f), pos(ride[k - 1]))) / f["ft"] if k > 0 else None
        prof.append({"k": k, "v": sp, "a": a, "vpos": pd, "ft": f["ft"],
                     "along": dot(vel(f), d_hat) if sp > 0 else 0.0})
    out["v_first"] = rnd(prof[1]["v"], 3) if len(prof) > 1 else None
    out["v_cap"] = rnd(max(p["v"] for p in prof), 3)
    out["dir_dot"] = rnd(min((p["along"] / p["v"]) for p in prof if p["v"] > 1), 6) if any(p["v"] > 1 for p in prof) else None
    a1 = [p["a"] for p in prof if p["a"] is not None and 2 <= p["k"] <= 55]
    a2 = [p["a"] for p in prof if p["a"] is not None and p["k"] >= 64 and p["v"] < out["v_cap"] - 1]
    out["accel_phase1"] = stats(a1)
    out["accel_phase2"] = stats(a2)
    sw = None
    for p in prof:
        if p["a"] is not None and p["k"] >= 3 and p["a"] < 500 and p["v"] < out["v_cap"] - 1:
            sw = p
            break
    out["accel_switch"] = {"k": sw["k"], "t": rnd(sum(q["ft"] for q in prof[1:sw["k"] + 1]), 4),
                           "v_before": rnd(prof[sw["k"] - 1]["v"], 3)} if sw else None
    capk = next((p["k"] for p in prof if p["v"] >= out["v_cap"] - 1e-3), None)
    out["t_to_cap"] = rnd(sum(q["ft"] for q in prof[1:capk + 1]), 4) if capk else None
    out["vpos_minus_v_after60"] = stats([p["vpos"] - p["v"] for p in prof if p["k"] >= 60 and p["vpos"] is not None])
    out["vpos_minus_vprev_after60"] = stats([p["vpos"] - prof[p["k"] - 1]["v"] for p in prof if p["k"] >= 60 and p["vpos"] is not None])
    out["profile"] = [{"k": p["k"], "v": rnd(p["v"], 3), "a": rnd(p["a"], 1)} for p in prof]
    # ---------------- exit (jump / duck / auto-detach)
    out.update(exit_analysis(t, out, fr, cl, sv, ij, idk, iend, rope, g_meas))
    return out


def finish_unmounted(t, out, fr, cl, ij, iu, g_meas):
    out["exit_kind"] = "none (not mounted)"
    # a ground jump in an unmounted jump trial (z2_jump_pd30): reference jump speed
    if ij and ij[0] is not None:
        k = None
        for c in sorted(cl):
            if cl[c]["buttons"] & IN_JUMP and not (cl.get(c - 1, {}).get("buttons", 0) & IN_JUMP):
                k = c
                break
        if k is not None:
            out["ground_jump_cmd"] = k
            out["ground_jump_post_v"] = rnd((cl[k]["pvx"], cl[k]["pvy"], cl[k]["pvz"]), 3)
            out["ground_jump_pre_ground"] = cl[k]["ground"]
    if t["schedule"] == "z7_air" and iu is not None:
        f = fr[iu - 1]
        out["air_at_use"] = {"o": rnd(pos(f), 2), "v": rnd(vel(f), 2), "ground": f["ground"],
                             "height_above_floor": rnd(f["oz"] - FLOOR_Z, 2),
                             "dist_to_rope_line_from_P": out.get("dist_P_rope")}
        out["min_dist_P_rope_in_trial"] = rnd(min(norm(sub(rope_point("Z1", max(0, min(1600, rope_param("Z1", add(pos(x), (0, 0, EYE_RAISE)))))), add(pos(x), (0, 0, EYE_RAISE)))) for x in fr), 2)
    return out


def exit_analysis(t, out, fr, cl, sv, ij, idk, iend, rope, g_meas):
    res = {}
    gap = mt_gap(cl)
    if gap is None:
        res["exit_kind"] = "no MT gap"
        return res
    k = gap[1]          # first MT command after the zipline commands; its pre-state = post-state of the detach cmd
    c, s = cl.get(k), sv.get(k)
    res["exit_cmd_first_mt"] = k
    res["exit_detach_cmd"] = k - 1
    vcl = (c["vx"], c["vy"], c["vz"])
    res["exit_v_cl"] = rnd(vcl, 3)
    res["exit_o_cl"] = rnd((c["ox"], c["oy"], c["oz"]), 3)
    if s:
        res["exit_v_sv"] = rnd((s["vx"], s["vy"], s["vz"]), 3)
        res["exit_o_sv"] = rnd((s["ox"], s["oy"], s["oz"]), 3)
    # parity over the first 30 post-gap commands
    dz, dy, dv = [], [], []
    for kk in range(k, k + 30):
        a, b = cl.get(kk), sv.get(kk)
        if a and b:
            dz.append(b["oz"] - a["oz"])
            dy.append(b["oy"] - a["oy"])
            dv.append(norm(sub((b["vx"], b["vy"], b["vz"]), (a["vx"], a["vy"], a["vz"]))))
    res["parity_dz_sv_minus_cl"] = stats(dz)
    res["parity_dy_sv_minus_cl"] = stats(dy)
    res["parity_dv"] = stats(dv)
    lcl = next((kk for kk in sorted(cl) if kk >= k and cl[kk]["ground"] == 1), None)
    lsv = next((kk for kk in sorted(sv) if kk >= k and sv[kk]["ground"] == 1), None)
    res["land_cmd_cl_sv"] = [lcl, lsv]
    jc = [d for d in t["diag"] if d["tag"] == "ZIP-JUMPOFF" and d["kv"].get("result") == "1"]
    jcl = next((d for d in jc if d["side"] == "cl"), None)
    jsv = next((d for d in jc if d["side"] == "sv"), None)
    res["diag_jumpoff_cl"] = {"cmd": jcl["cmd"], "vel": jcl["vec"].get("vel"), "state": jcl["kv"].get("state"),
                              "flags": jcl["kv"].get("flags")} if jcl else None
    res["diag_jumpoff_sv"] = {"cmd": jsv["cmd"], "vel": jsv["vec"].get("vel"), "state": jsv["kv"].get("state"),
                              "flags": jsv["kv"].get("flags")} if jsv else None
    ms = next((d for d in t["diag"] if d["tag"] == "ZIP-MOVESTOP" and d["side"] == "sv" and d["kv"].get("state", "").endswith("->0") and not d["kv"].get("state", "").startswith("0")), None)
    res["diag_movestop_sv"] = {"cmd": ms["cmd"], "state": ms["kv"].get("state")} if ms else None
    ex = next((d for d in t["diag"] if d["tag"] == "ZIP-EXIT" and d["side"] == "sv"), None)
    res["diag_exit_sv"] = {"velPre": ex["vec"].get("velPre"), "velPost": ex["vec"].get("velPost"),
                           "floor": ex["kv"].get("floor"), "ceil": ex["kv"].get("ceil")} if ex else None
    # ride speed just before the detach command (HSD frame before the exit frame)
    vr, kind = None, None
    ix = None
    if ij and ij[0] is not None and ij[0] - 1 >= 0 and fr[ij[0]]["in_jump"] == 1 and fr[ij[0] - 1]["ground"] == 0:
        kind, ix = "jump", ij[0]
    elif idk is not None and fr[idk]["in_duck"] == 1:
        kind, ix = "crouch", idk
    else:
        kind = "auto"
    res["exit_kind"] = kind
    d_hat = rope_dir(rope)
    if ix is not None:
        vr = norm(vel(fr[ix - 1]))
        res["ride_v_before"] = rnd(vr, 3)
        res["exit_v_hsd"] = rnd(vel(fr[ix]), 3)
        res["exit_pos_shift_on_cmd"] = rnd(norm(sub(pos(fr[ix]), pos(fr[ix - 1]))), 3)
        hcap = min(vr, JUMP_CAP_FIT)
        h = unit((d_hat[0], d_hat[1], 0.0))
        pred = (h[0] * hcap, h[1] * hcap, 289.828 if kind == "jump" else 0.0)
        res["exit_pred_min400"] = rnd(pred, 3)
        res["exit_resid_min400_cl"] = rnd(norm(sub(vcl, pred)), 4)
        res["exit_resid_ratio_k"] = rnd(math.hypot(vcl[0], vcl[1]) / vr, 5) if vr else None
        # held keys: mean horizontal acceleration over the 20 commands after the exit
        acc = []
        for kk in range(k, k + 20):
            a, b = cl.get(kk), cl.get(kk + 1)
            if a and b and a["ground"] == 0 and b["ground"] == 0:
                dt_ = None
                # dt from the post-state minus pre-state of row a (pv - v) / ft is not in MT; use HSD ft median
                acc.append(((b["vx"] - a["vx"]), (b["vy"] - a["vy"])))
        res["post_exit_dv_per_cmd_xy"] = rnd((st.mean(x for x, _ in acc), st.mean(y for _, y in acc)), 4) if acc else None
        res["post_exit_buttons"] = sorted(set(cl[kk]["buttons"] for kk in range(k, k + 20) if kk in cl))
    else:
        # auto-detach: compare with the SDK rule
        vpre = norm(vel(fr[iend])) if iend is not None and iend < len(fr) else None
        res["ride_v_before"] = rnd(vpre, 3) if vpre is not None else None
        if ROPES[rope]["vertical"]:
            pred = mul(d_hat, min(vpre if vpre is not None else 600.0, 1500.0))
        else:
            vd = 600.0  # clamp(v.d, ziplineSpeed 600, ziplineDetachSpeed 600) = 600 for any v
            pred = mul(d_hat, vd)
        res["exit_pred_sdk_rule"] = rnd(pred, 3)
        res["exit_resid_sdk_rule_cl"] = rnd(norm(sub(vcl, pred)), 4)
        res["exit_resid_sdk_rule_vertical_only"] = rnd(abs(vcl[2] - pred[2]), 4) if ROPES[rope]["vertical"] else None
        res["exit_horizontal_extra_cl"] = rnd(math.hypot(vcl[0] - pred[0], vcl[1] - pred[1]), 4)
        # exit position along the rope: distance left to the end, measured at the detach ref (origin + hull 80)
        ref = add((c["ox"], c["oy"], c["oz"]), (0.0, 0.0, 80.0))
        # the pre-state of the first MT command is the post-state of the detach command
        sref = rope_param(rope, ref)
        res["exit_dist_to_end"] = rnd(rope_len(rope) - sref, 3)
        res["exit_alpha"] = rnd(sref / rope_len(rope), 5)
        if s:
            refs = add((s["ox"], s["oy"], s["oz"]), (0.0, 0.0, 80.0))
            res["exit_dist_to_end_sv"] = rnd(rope_len(rope) - rope_param(rope, refs), 3)
    # super jump: second jump press
    if len(ij) > 1 and ij[1] is not None:
        i2 = ij[1]
        f2, f1 = fr[i2], fr[i2 - 1]
        pred_vz = f1["vz"] - g_meas * f2["ft"]
        res["sj_second_press_rel_frames"] = i2 - ij[0]
        res["sj_ground_before"] = f1["ground"]
        res["sj_in_jump_logged"] = f2["in_jump"]
        res["sj_dvz_minus_gravity"] = rnd(f2["vz"] - pred_vz, 3)
        res["sj_dvxy"] = rnd(math.hypot(f2["vx"], f2["vy"]) - math.hypot(f1["vx"], f1["vy"]), 3)
        res["sj_height_above_floor"] = rnd(f1["oz"] - FLOOR_Z, 2)
        res["sj_t_since_jumpoff"] = rnd(f2["t"] - fr[ij[0]]["t"], 4)
        # MT row of the second press (the jump-off cmd itself is not in MT)
        k2 = next((kk for kk in sorted(cl) if kk > k - 1 and cl[kk]["buttons"] & IN_JUMP), None)
        if k2 is not None:
            res["sj_mt_cmd"] = k2
            res["sj_mt_ground"] = cl[k2]["ground"]
            res["sj_mt_dvz"] = rnd(cl[k2]["pvz"] - cl[k2]["vz"], 3)
    # landing and any later takeoff (buffered jump?)
    land = None
    for i in range((ix or (iend or 0)) + 1, len(fr)):
        if fr[i]["ground"] == 1:
            land = i
            break
    if land is not None:
        res["land_rel_frames_after_exit"] = land - (ix if ix is not None else (iend or 0))
        res["land_v"] = rnd(vel(fr[land - 1]), 3)
        res["takeoff_after_land"] = any(fr[i]["ground"] == 0 and fr[i]["vz"] > 100 for i in range(land, len(fr)))
    return res


# ----------------------------------------------------------------------------- fits
def fit_blend(trials):
    """Mount blend b(k) per frame after the mount command; one-parameter shapes fitted by grid search."""
    rows = [b for t in trials for b in t.get("blend", []) if b["b"] is not None]
    if not rows:
        return None
    byk = {}
    for b in rows:
        byk.setdefault(b["k"], []).append(b["b"])
    table = {k: rnd(st.mean(v), 4) for k, v in sorted(byk.items())}
    spread = {k: rnd(max(v) - min(v), 4) for k, v in sorted(byk.items())}
    dt = 1.0 / 120.0

    def smooth(T):
        return lambda k: (lambda x: 3 * x * x - 2 * x ** 3)(min(1.0, k * dt / T))

    def crit(w):
        return lambda k: 1 - (1 + w * k * dt) * math.exp(-w * k * dt)

    def expo(w):
        return lambda k: 1 - math.exp(-w * k * dt)

    def pos_rms(fn):
        e = []
        for b in rows:
            if b["k"] > 40:
                continue
            p = add(b["p0"], mul(sub(b["ref"], b["p0"]), fn(b["k"])))
            e.append(norm(sub(p, b["pos"])) ** 2)
        return math.sqrt(st.mean(e))

    best = {}
    for name, fam, grid in (("smoothstep_T_s", smooth, [0.05 + 0.001 * i for i in range(400)]),
                            ("critdamp_w_per_s", crit, [5 + 0.1 * i for i in range(600)]),
                            ("exp_w_per_s", expo, [2 + 0.1 * i for i in range(600)])):
        b = min(((pos_rms(fam(p)), p) for p in grid))
        best[name] = {"param": rnd(b[1], 4), "pos_rms_u": rnd(b[0], 3)}
    # residual of the table itself (per-k mean): how much trial-to-trial scatter is left
    tab_rms = pos_rms(lambda k: table.get(k, 1.0))
    return {"table_mean_b": table, "table_spread": spread, "fits": best, "table_pos_rms_u": rnd(tab_rms, 3),
            "n_rows": len(rows)}


# ----------------------------------------------------------------------------- report
def P(*a):
    print(*a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json", default=None)
    ap.add_argument("--params", default=None)
    ap.add_argument("--round2", nargs="*", default=[], help="M6-A3 round-2 session folder(s) (optional)")
    ap.add_argument("--grapple", nargs="*", default=[], help="M6-G grapple session folder(s) (optional)")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    jpath = args.json or os.path.join(here, "results.json")
    ppath = args.params or os.path.join(here, "params.json")

    sessions = [load_session(s) for s in args.sessions]
    P("M6-A3 zipline analysis  (a3_zip_analysis.py)")
    P("=" * 100)
    allt, census = [], {}
    for S in sessions:
        r = S["runner"]
        P("session %s  label=%s  client_fps=%s  legend=%s  geometry_zip=%s" % (S["folder"], r.get("label"), r.get("client_fps"),
                                                                             r.get("legend"), r.get("geometry_zip")))
        P("  trials used %d, skipped %d: %s" % (len(S["trials"]), len(S["skipped"]),
                                               ", ".join("r%d %s (%s)" % (x["run"], x["schedule"], x["why"]) for x in S["skipped"])))
        census.update(S["cv"])
        allt.extend(S["trials"])
    cvkeys = ("ziplineSpeed", "ziplineDetachSpeed", "ziplineMaxVerticalDetachSpeed", "ziplineViewOffset",
              "ziprailAcceleration", "ziprailDetachSpeed", "pathGravityAcceleration", "maxSpeedMultiplier",
              "minSpeedFraction", "maxJumpOffSpeed", "minJumpOffSpeed", "viewInfluenceOnJumpDirection",
              "detachDirMaxDownAngle", "detachDirMaxUpAngle", "jumpHeight", "gravityScale", "airSpeed",
              "superjumpLimit", "antiMultiJumpHeightFrac")
    P("\n[census] client player settings (CLASSVAR):")
    for k in cvkeys:
        P("  %-32s %s" % (k, census.get(k, "(not in census)")))
    for S in sessions:
        P("  unknown CLASSVAR keys (client warning log): %s" % ", ".join(S["unknown_keys"]))
        P("  'find' cvar census lines: %d" % len(S["find"]))
        for side, line in S["find"]:
            P("    [%s] %s" % (side, line))
    P("  -> the 'find jump_grace / zipline / mantle_boost / lurch' census produced no cvar values: the client forwards")
    P("     'find' to the dedi, which has no 'find' command. jump_graceperiod etc. stay [unknown].")

    # gravity from free flight (client HSD frames, airborne, not on the rope)
    gs = []
    for t in allt:
        fr = t["frames"]
        for i in range(1, len(fr)):
            a, b = fr[i - 1], fr[i]
            if a["ground"] == 0 and b["ground"] == 0 and a["vz"] != 0 and b["vz"] != 0 and abs(a["vx"] - b["vx"]) < 1e-3 \
                    and -1000 < b["vz"] < 280 and abs((a["vz"] - b["vz"]) / b["ft"] - 750) < 100:
                gs.append((a["vz"] - b["vz"]) / b["ft"])
    g_meas = st.median(gs) if gs else 750.0
    P("\n[gravity] free-flight dvz/dt over %d frame pairs: median %.2f  (mean %.2f, sd %.2f) u/s^2" %
      (len(gs), g_meas, st.mean(gs), st.pstdev(gs)))

    res = [analyse_trial(t, g_meas) for t in allt]
    by = {}
    for r in res:
        by.setdefault(r["schedule"], []).append(r)
    order = sorted(by, key=lambda s: (s[:2], s))
    P("  edge->frame mapping mismatches (all trials): %d" % sum(r["edge_map_mismatch"] for r in res))

    # ------------------------------------------------------------------ Q1 mount
    P("\n" + "=" * 100 + "\nQ1 MOUNT\n" + "=" * 100)
    P("%-14s %3s  %-9s %-9s %-9s %-8s %-8s %-9s %-9s %-9s %-9s %-10s" % ("schedule", "n", "mounted", "diag_cl", "diag_sv",
                                                                        "lat_fr", "cmd=gap", "P->rope", "use_dist", "use_ang",
                                                                        "minAng130", "use_x"))
    for s in order:
        rr = by[s]
        mm = sum(r["mounted_motion"] for r in rr)
        dc = sum(r["mounted_diag_cl"] for r in rr)
        ds = sum(r["mounted_diag_sv"] for r in rr)
        lat = sorted(set(r["mount_latency_frames"] for r in rr if r["mount_latency_frames"] is not None))
        eq = sorted(set(r.get("mount_cmd_eq_first_missing_mt") for r in rr if "mount_cmd_eq_first_missing_mt" in r))
        pr = stats([r.get("dist_P_rope") for r in rr])
        ud = stats([r.get("find_use_dist") for r in rr])
        ua = stats([r.get("find_use_angle") for r in rr])
        ma = stats([r.get("find_min_angle_R130") for r in rr])
        ux = sorted(set(r["diag_use_sv"]["use"][0] for r in rr if r.get("diag_use_sv")))
        P("%-14s %3d  %d/%-7d %d/%-7d %d/%-7d %-8s %-8s %-9s %-9s %-9s %-9s %-10s" % (
            s, len(rr), mm, len(rr), dc, len(rr), ds, len(rr), ",".join(map(str, lat)) or "-",
            ",".join(map(str, eq)) or "-", pr and pr["mean"], ud and ud["mean"], ua and ua["mean"], ma and ma["mean"],
            ",".join("%.2f" % x for x in ux) or "-"))
    ok_ang = [r["find_use_angle"] for r in res if r.get("find_use_angle") is not None]
    ok_dist = [r["find_use_dist"] for r in res if r.get("find_use_dist") is not None]
    fail = [r for r in res if not r["mounted_motion"] and r["schedule"] not in ("z0_nouse",) and r.get("use_frame") is not None]
    fail_ang = [r["find_min_angle_R130"] for r in fail if r.get("find_min_angle_R130") is not None]
    P("\nFind model check: Q = server Find point ([ZIPRAIL-USE] use=), P = pre-use origin + (0,0,72), eye from the pre-use view.")
    P("  successful mounts: |Q-P| %s ; angle(eye, Q-P) %s" % (stats(ok_dist), stats(ok_ang)))
    P("  failed mounts (any use press, not mounted): %d trials; smallest achievable angle to a rope point within 130 u: %s"
      % (len(fail), stats(fail_ang)))
    P("  failed with no rope point within 130 u: %d" % sum(1 for r in fail if r.get("find_min_angle_R130") is None))
    if ok_ang and fail_ang:
        P("  -> cone half-angle bracket [fit]: %.2f deg < theta_max < %.2f deg  (radius 130 from |Q-P|)" % (max(ok_ang), min(fail_ang)))
    P("  per-trial failed: " + "; ".join("%s r%d P->rope %.1f minAng %s" % (r["schedule"], r["run"], r.get("dist_P_rope") or -1,
                                                                            r.get("find_min_angle_R130")) for r in fail[:40]))
    P("  IN_USE (0x20) presses seen in MOVE-TRACE: failed trials %d/%d show one; mounted trials show none (the mount cmd"
      " is the first missing MT cmd)" % (sum(1 for r in fail if r["use_press_mt"]), len(fail)))
    P("  control z0_nouse: air frames %s, MT gaps %s, diag use events %s" % (
        [r.get("any_air_frames") for r in by.get("z0_nouse", [])], [r["mt_gap"] for r in by.get("z0_nouse", [])],
        [r["diag_use_cl"] for r in by.get("z0_nouse", [])]))
    m_ok = [r for r in res if r["mounted_motion"]]
    P("\nSnap at the mount command (client HSD post-state of the use cmd):")
    P("  dz %s ; horizontal move %s" % (stats([r["snap_dz"] for r in m_ok]), stats([r["snap_dxy"] for r in m_ok])))
    P("  steady ride hang below the rope (client) %s ; lateral offset (client, y - rope y) %s" % (
        stats([r.get("hang_below_rope_cl") for r in m_ok]), stats([r.get("lateral_offset_cl") for r in m_ok if r["rope"] != "Z3"])))
    P("  vertical rope Z3: x - rope x %s, y - rope y %s" % (stats([r.get("lateral_offset_cl") for r in m_ok if r["rope"] == "Z3"]),
                                                           stats([r.get("vertical_rope_dy_cl") for r in m_ok if r["rope"] == "Z3"])))
    P("  Find point ahead of the player along the view yaw: %s" % "; ".join(
        "%s %s" % (s, stats([r.get("find_use_ahead") for r in by[s] if r.get("find_use_ahead") is not None])["mean"])
        for s in order if any(r.get("find_use_ahead") is not None for r in by[s])))
    bl = fit_blend(m_ok)
    if bl:
        P("\nMount blend (flat/uphill ropes): position = p0 + b(k) * (rope reference - p0), rope reference = Find point")
        P("  advanced by the logged rope speed; k = frames after the mount command. Mean b(k) over %d rows:" % bl["n_rows"])
        tb = bl["table_mean_b"]
        P("  " + " ".join("%d:%.3f" % (k, v) for k, v in list(tb.items())[:41]))
        P("  per-k spread (max-min) up to k=30: max %.4f" % max(v for k, v in bl["table_spread"].items() if k <= 30))
        for n, f in bl["fits"].items():
            P("  fit %-18s param %-8s position RMS %.3f u" % (n, f["param"], f["pos_rms_u"]))
        P("  per-k mean table as the model: position RMS %.3f u" % bl["table_pos_rms_u"])
        P("  reference tail error k=40..60 (mean |pos - ref|): previous-cmd speed integration %s ; same-cmd speed %s" % (
            stats([r["blend_tail_err_k40_60"].get("prev") for r in m_ok if r.get("blend_tail_err_k40_60")]),
            stats([r["blend_tail_err_k40_60"].get("post") for r in m_ok if r.get("blend_tail_err_k40_60")])))
    vt = [r for r in m_ok if r["rope"] == "Z3" and r.get("diag_use_sv")]
    if vt:
        P("\nVertical rope Z3 Find point: Q.z - pre-use origin.z %s ; angle to eye %s (the min-angle rule would give the eye-height"
          " point, angle 0) -> vertical ropes pick the point at hang height (origin + hull 80), not the min-angle point" % (
              stats([r["diag_use_sv"]["use"][2] - r["pre_use"]["o"][2] for r in vt]), stats([r["find_use_angle"] for r in vt])))
    P("\nView pitch on mount (client view is driven to the rope pitch):")
    for r in m_ok:
        if r["pitch_pre"] is not None and abs((r["pitch_pre"] or 0) - (r["pitch_after_40"] or 0)) > 1:
            P("  %s r%d pitch before %.2f -> after 40 frames %.3f (rope pitch %.3f); 90%% reached after %s frames" % (
                r["schedule"], r["run"], r["pitch_pre"], r["pitch_after_40"], r["pitch_rope"], r["pitch_90pct_frames"]))

    # ------------------------------------------------------------------ Q2 ride
    P("\n" + "=" * 100 + "\nQ2 RIDE\n" + "=" * 100)
    P("%-14s %3s %-8s %-8s %-22s %-22s %-24s %-8s %-10s" % ("schedule", "n", "v_first", "v_cap", "a1 (k 2..55) mean/sd",
                                                           "a2 (k>=64,<cap) mean/sd", "switch k / t / v_before", "t_cap", "dir.dot"))
    for s in order:
        rr = [r for r in by[s] if r["mounted_motion"]]
        if not rr:
            continue
        a1 = stats([x for r in rr for x in ([r["accel_phase1"]["mean"]] if r["accel_phase1"] else [])])
        a1sd = max((r["accel_phase1"]["sd"] for r in rr if r["accel_phase1"]), default=None)
        a2 = stats([x for r in rr for x in ([r["accel_phase2"]["mean"]] if r["accel_phase2"] else [])])
        a2sd = max((r["accel_phase2"]["sd"] for r in rr if r["accel_phase2"]), default=None)
        sw = [r["accel_switch"] for r in rr if r["accel_switch"]]
        P("%-14s %3d %-8s %-8s %-22s %-22s %-24s %-8s %-10s" % (
            s, len(rr), stats([r["v_first"] for r in rr])["mean"], stats([r["v_cap"] for r in rr])["max"],
            "%s / %s" % (a1 and a1["mean"], a1sd), "%s / %s" % (a2 and a2["mean"], a2sd),
            "%s / %s / %s" % (stats([x["k"] for x in sw]) and stats([x["k"] for x in sw])["mean"],
                              stats([x["t"] for x in sw]) and stats([x["t"] for x in sw])["mean"],
                              stats([x["v_before"] for x in sw]) and stats([x["v_before"] for x in sw])["mean"]) if sw else "-",
            stats([r["t_to_cap"] for r in rr]) and stats([r["t_to_cap"] for r in rr])["mean"],
            stats([r["dir_dot"] for r in rr]) and stats([r["dir_dot"] for r in rr])["min"]))
    P("  |d origin|/ft minus logged speed of the same cmd (k>=60, per-trial means): %s" % stats(
        [r["vpos_minus_v_after60"]["mean"] for r in m_ok if r.get("vpos_minus_v_after60")]))
    P("  |d origin|/ft minus logged speed of the previous cmd (k>=60): %s" % stats(
        [r["vpos_minus_vprev_after60"]["mean"] for r in m_ok if r.get("vpos_minus_vprev_after60")]))
    P("  (origins are 6-digit rounded in rows.csv: 0.1 u in x -> +-6 u/s per-frame noise; means are what count)")
    jo = [r for r in m_ok if r.get("diag_jumpoff_cl")]
    P("  dedi state at the jump command (z5, 61 cmds after the mount): %s" % sorted(
        set((r["schedule"][:6], r["diag_jumpoff_sv"]["state"]) for r in jo if r.get("diag_jumpoff_sv"))))
    P("\nAuto-detach (rope end) vs the SDK rule v_out = d_end * clamp(v.d_end, ziplineSpeed, ziplineDetachSpeed):")
    P("%-14s %-6s %-26s %-26s %-26s %-9s %-9s %-10s %-10s" % ("schedule", "run", "exit v cl", "exit v sv", "pred", "resid", "h_extra",
                                                             "dist_end", "dist_end_sv"))
    for r in m_ok:
        if r.get("exit_kind") == "auto":
            P("%-14s r%-5d %-26s %-26s %-26s %-9s %-9s %-10s %-10s" % (
                r["schedule"], r["run"], r["exit_v_cl"], r.get("exit_v_sv"), r["exit_pred_sdk_rule"], r["exit_resid_sdk_rule_cl"],
                r["exit_horizontal_extra_cl"], r["exit_dist_to_end"], r.get("exit_dist_to_end_sv")))
    P("  dedi [ZIP-EXIT] lines (first 4 only, rate-limited): %s" % sorted(set(
        (str(r["diag_exit_sv"]["velPre"]), str(r["diag_exit_sv"]["velPost"]), r["diag_exit_sv"]["floor"], r["diag_exit_sv"]["ceil"])
        for r in m_ok if r.get("diag_exit_sv"))))
    P("  detach command: client exit cmd vs dedi [ZIP-MOVESTOP] cmd equal in %d/%d trials with a dedi line" % (
        sum(1 for r in m_ok if r.get("diag_movestop_sv") and r["diag_movestop_sv"]["cmd"] == r.get("exit_detach_cmd")),
        sum(1 for r in m_ok if r.get("diag_movestop_sv"))))
    P("\nClient/dedi parity over the first 30 MT commands after the detach (sv - cl):")
    for s in order:
        rr = [r for r in by[s] if r.get("parity_dz_sv_minus_cl")]
        if not rr:
            continue
        P("  %-14s dz %s | dy %s | |dv| max %.4f | landing cmd sv-cl %s" % (
            s, stats([r["parity_dz_sv_minus_cl"]["mean"] for r in rr]), stats([r["parity_dy_sv_minus_cl"]["mean"] for r in rr]),
            max(r["parity_dv"]["max"] for r in rr),
            sorted(set((r["land_cmd_cl_sv"][1] - r["land_cmd_cl_sv"][0]) if None not in r["land_cmd_cl_sv"] else None for r in rr),
                   key=lambda x: (x is None, x))))
    ex = [r for r in m_ok if r.get("exit_o_sv")]
    exdz = [r["exit_o_sv"][2] - r["exit_o_cl"][2] for r in ex]
    exdy = [r["exit_o_sv"][1] - r["exit_o_cl"][1] for r in ex]
    P("  at the detach (post-state of the detach cmd, sv - cl): dz %s ; dy %s ; exits with no offset at all: %d/%d" % (
        stats(exdz), stats(exdy), sum(1 for a, b in zip(exdz, exdy) if abs(a) < 1e-3 and abs(b) < 1e-3), len(ex)))
    P("  -> the dedi hangs at rope - 80.00 (y on the rope), the client at rope - 80.17, y - 0.23; this offset (not a"
      " half-duck step, which would be (80 - duck hull)/2 = many u) is carried into every exit kind incl. crouch-off")

    # ------------------------------------------------------------------ Q3 jump-off / crouch-off
    P("\n" + "=" * 100 + "\nQ3 JUMP-OFF / CROUCH-OFF\n" + "=" * 100)
    P("%-14s %-6s %-6s %-9s %-26s %-26s %-26s %-9s %-7s %-20s %-8s" % ("schedule", "run", "kind", "ride_v", "exit v cl (MT)",
                                                                       "diag cl vel", "diag sv vel", "resid", "k=h/v",
                                                                       "dv/cmd xy after", "shift"))
    for r in m_ok:
        if r.get("exit_kind") in ("jump", "crouch"):
            P("%-14s r%-5d %-6s %-9s %-26s %-26s %-26s %-9s %-7s %-20s %-8s" % (
                r["schedule"], r["run"], r["exit_kind"], r["ride_v_before"], r["exit_v_cl"],
                r["diag_jumpoff_cl"] and r["diag_jumpoff_cl"]["vel"], r["diag_jumpoff_sv"] and r["diag_jumpoff_sv"]["vel"],
                r["exit_resid_min400_cl"], r["exit_resid_ratio_k"], r.get("post_exit_dv_per_cmd_xy"), r.get("exit_pos_shift_on_cmd")))
    jr = [r for r in m_ok if r.get("exit_kind") in ("jump", "crouch")]
    P("\nModel v_out = h_rope * min(v_ride, %.0f) + z * (289.828 jump | 0 crouch):" % JUMP_CAP_FIT)
    P("  residual |v_cl - pred| over %d exits: %s" % (len(jr), stats([r["exit_resid_min400_cl"] for r in jr])))
    P("  ride speeds covered: %s" % sorted(set(round(r["ride_v_before"]) for r in jr)))
    P("  alternative k = v_h/v_ride: %s" % "; ".join("ride~%d: %s" % (v, stats([r["exit_resid_ratio_k"] for r in jr if round(r["ride_v_before"] / 10) == v // 10])["mean"])
                                                       for v in sorted(set(round(r["ride_v_before"], -1) for r in jr))))
    P("  jump-off flags (diag, = held buttons): %s" % sorted(set((r["schedule"], r["diag_jumpoff_sv"]["flags"]) for r in jr if r.get("diag_jumpoff_sv"))))
    P("  diag cl == diag sv jump-off velocity: %d/%d" % (sum(1 for r in jr if r.get("diag_jumpoff_cl") and r.get("diag_jumpoff_sv") and r["diag_jumpoff_cl"]["vel"] == r["diag_jumpoff_sv"]["vel"]),
                                                          sum(1 for r in jr if r.get("diag_jumpoff_cl"))))
    pd = by.get("z2_jump_pd30", [])
    P("  view pitch: z2_jump_pu30 mounted but the mount drives the view to the rope pitch (0) before the jump -> pitch"
      " law untestable here; z2_jump_pd30 did not mount (%d/%d) -> its jump is a ground jump: post v %s" % (
          sum(1 for r in pd if r["mounted_motion"]), len(pd), sorted(set(str(r.get("ground_jump_post_v")) for r in pd))))
    P("  ground-jump vz reference = sqrt(2 * g * jumpHeight) = %.3f (g %.1f, jumpHeight %s)" % (
        math.sqrt(2 * g_meas * float(census.get("jumpHeight", 56))), g_meas, census.get("jumpHeight")))
    P("  crouch-off duck state after the exit (MT duck/crouch fields): %s" % sorted(set(
        (t["cl"][k]["duck"], t["cl"][k]["crouch"]) for t in allt if t["schedule"] == "z3_crouch" for k in t["cl"]
        if mt_gap(t["cl"]) and mt_gap(t["cl"])[1] <= k < mt_gap(t["cl"])[1] + 30)))

    # ------------------------------------------------------------------ Q4 super jump
    P("\n" + "=" * 100 + "\nQ4 SUPER JUMP (second jump K frames after the jump-off)\n" + "=" * 100)
    P("%-12s %-6s %-6s %-7s %-8s %-8s %-11s %-9s %-9s %-8s %-8s %-8s" % ("schedule", "run", "K+1", "t_since", "ground", "in_jump",
                                                                      "dvz-grav", "dvxy", "h_floor", "mt_gnd", "mt_dvz", "relan"))
    for s in order:
        if not s.startswith("z5"):
            continue
        for r in by[s]:
            P("%-12s r%-5d %-6s %-7s %-8s %-8s %-11s %-9s %-9s %-8s %-8s %-8s" % (
                s, r["run"], r.get("sj_second_press_rel_frames"), r.get("sj_t_since_jumpoff"), r.get("sj_ground_before"),
                r.get("sj_in_jump_logged"), r.get("sj_dvz_minus_gravity"), r.get("sj_dvxy"), r.get("sj_height_above_floor"),
                r.get("sj_mt_ground"), r.get("sj_mt_dvz"), r.get("takeoff_after_land")))
    z5 = [r for r in res if r["schedule"].startswith("z5")]
    P("  second press applied (|dvz - gravity| > 5): %d/%d ; second press on the ground: %d ; takeoff after landing: %d" % (
        sum(1 for r in z5 if r.get("sj_dvz_minus_gravity") is not None and abs(r["sj_dvz_minus_gravity"]) > 5), len(z5),
        sum(1 for r in z5 if r.get("sj_ground_before") == 1), sum(1 for r in z5 if r.get("takeoff_after_land"))))
    P("  jump-off -> landing: %s frames" % stats([r.get("land_rel_frames_after_exit") for r in z5]))

    # ------------------------------------------------------------------ Q5 air grab
    P("\n" + "=" * 100 + "\nQ5 AIR GRAB (z7_air)\n" + "=" * 100)
    for r in by.get("z7_air", []):
        P("  r%d mounted %s diag_cl %s; at the use press %s; P->rope %.1f u; min P->rope in trial %s u; use presses in MT %s" % (
            r["run"], r["mounted_motion"], r["diag_use_cl"], r.get("air_at_use"), r.get("dist_P_rope") or -1,
            r.get("min_dist_P_rope_in_trial"), r["use_press_mt"]))
    P("  -> no air mount; the standing jump reached only ~15 u of the 200 u lateral gap, so the press was ~185 u from the rope:")
    P("     outside the measured ground range (40 ok / 80 fail). Air mount itself remains untested [unknown].")

    # ------------------------------------------------------------------ budget
    disc = [d for S in sessions for d in S["diag_all"] if d["tag"] == "ZIP-DISC"]
    P("\n[re-mount budget] [ZIP-DISC] lines (rate-limited, first trials only): %s" % sorted(set((d["side"], d["body"].split()[0], d["kv"].get("left")) for d in disc)))

    # ------------------------------------------------------------------ outputs
    def clean(r):
        r = dict(r)
        r["blend"] = [{"k": b["k"], "b": b["b"], "err": b["err"]} for b in r.get("blend", [])]
        return r
    results = {"sessions": [S["folder"] for S in sessions], "gravity": rnd(g_meas, 3),
               "census": {k: census.get(k) for k in cvkeys}, "blend_fit": bl,
               "find": {"ok_dist": stats(ok_dist), "ok_angle": stats(ok_ang), "fail_min_angle_R130": stats(fail_ang)},
               "skipped": [x for S in sessions for x in S["skipped"]], "trials": [clean(r) for r in res]}
    ext = None
    if args.round2 or args.grapple:
        ext = run_extensions(args.round2, args.grapple, g_meas)
        results.update(ext["results"])
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    a1all = [r["accel_phase1"]["mean"] for r in m_ok if r["accel_phase1"]]
    a2all = [r["accel_phase2"]["mean"] for r in m_ok if r["accel_phase2"]]
    params = {
        "_doc": "M6-A3 per-usercmd zipline model for Unity (Source units, u/s). Labels: meas = measured here, fit = fitted "
                "here (residual given), src = source audit / census, unknown = not determined. See A3-ZIPLINE.md.",
        "census": {"ziplineSpeed": [float(census.get("ziplineSpeed", 600)), "src+meas"],
                   "ziplineDetachSpeed": [float(census.get("ziplineDetachSpeed", 600)), "src"],
                   "ziplineMaxVerticalDetachSpeed": [float(census.get("ziplineMaxVerticalDetachSpeed", 1500)), "src (not reached)"],
                   "jumpHeight": [float(census.get("jumpHeight", 56)), "src"], "gravity": [rnd(g_meas, 2), "meas"]},
        "attach": {"input": ["+use press edge (IN_USE 0x20), mounts on the press command itself", "meas"],
                   "search_origin_raise": [EYE_RAISE, "src+fit (Find points reproduce with this origin)"],
                   "find_radius": [rnd(max(ok_dist), 2) if ok_dist else None, "fit (|Q-P| of every pitch-0 Find point)"],
                   "find_point_rule": ["argmin angle(eyeDir, Q-P) over rope points Q with |Q-P| <= radius (flat/sloped ropes; every"
                                       " Find point reproduced to 0.1 deg / 0.1 u)", "fit"],
                   "find_point_rule_vertical": ["rope point at origin.z + 80.1 (hang height), not the min-angle point", "meas (1 geometry)"],
                   "cone_half_angle_deg_bracket": [[rnd(max(ok_ang), 2), rnd(min(fail_ang), 2)] if ok_ang and fail_ang else None, "fit (bracket)"],
                   "auto_attach_on_touch": [False, "meas (z0_nouse)"],
                   "air_attach": [None, "unknown (z7 never came within range)"],
                   "snap_dz_on_mount_cmd": [rnd(st.mean(r["snap_dz"] for r in m_ok), 3), "meas (pop to standing / hang start)"],
                   "hang_below_rope_client": [rnd(st.mean(r["hang_below_rope_cl"] for r in m_ok if r.get("hang_below_rope_cl") is not None), 3), "meas"],
                   "blend_table_b_of_k": [bl and bl["table_mean_b"], "meas (position = p0 + b*(ropeRef - p0))"],
                   "blend_fit": [bl and bl["fits"], "fit"],
                   "view_pitch_driven_to_rope_pitch": [True, "meas (90% after 22 cmds, -30 -> 0 and 0 -> -10.62)"],
                   "position_integration": ["x_k = x_(k-1) + v_k * dt along the rope (same-cmd speed)", "fit (tail 0.43 u vs 1.69 u)"]},
        "ride": {"v_first_cmd": [rnd(st.mean(r["v_first"] for r in m_ok), 3), "meas"],
                 "accel_state2_first_0p5s": [rnd(st.mean(a1all), 2) if a1all else None, "meas"],
                 "accel_state3": [rnd(st.mean(a2all), 2) if a2all else None, "meas"],
                 "state2_duration_s": [0.5, "meas (accel switch at k=60, dedi state 2->3 at the same cmd; a speed threshold 300 is not excluded)"],
                 "cap": [rnd(max(r["v_cap"] for r in m_ok), 3), "meas (= ziplineSpeed)"],
                 "slope_effect": ["none: same |v| profile along the rope on the uphill rope", "meas (Z2 only, uphill)"],
                 "vertical": ["same profile up the vertical rope", "meas"]},
        "detach": {"auto_rope": ["v_out = d_end * 600 (clamp(v.d, ziplineSpeed, ziplineDetachSpeed))", "meas+src, residual 0"],
                   "auto_rope_rule": ["after the ride step, if (remaining to the end - v*dt) < 90 (= autoDetach 100 - 10) detach at the"
                                    " current position with v_out", "fit (remaining after the detach cmd 90.1..94.8 u)"],
                   "auto_rope_stop_short_u": [rnd(st.mean(r["exit_dist_to_end"] for r in m_ok if r.get("exit_kind") == "auto" and r["rope"] != "Z3"), 3), "meas (distance to the rope end of origin+80 at the detach)"],
                   "auto_vertical": ["v_out = vertical ride velocity (600, below the 1500 clamp) + 400 horizontal along the view yaw", "meas (direction yaw vs approach ambiguous)"],
                   "jump_off": ["v_out = h_rope * min(v_ride, 400) + z * 289.83 (= sqrt(2 g jumpHeight)); keys ignored on the jump cmd; the jump cmd itself does not translate", "fit (2 ride speeds), residual in A3-ZIPLINE.md"],
                   "crouch_off": ["v_out = h_rope * min(v_ride, 400), vz = 0", "fit (1 ride speed)"],
                   "jump_off_view_pitch_law": [None, "unknown (view locked to the rope pitch while riding)"],
                   "post_exit_air_control": ["standard air accel 500 u/s^2, wish cap 69 (M2), from the first post-exit cmd", "meas"],
                   "client_dedi_offset": ["client hangs 0.17 u lower and 0.23 u to -y of the dedi; carried into the exit", "meas"]},
        "super_jump": {"applies": [False, "meas: second jump K=1..12,40 frames after the jump-off is ignored (airborne, no grace)"]},
        "remount_budget": ["3, +1 per 3 s, reset on landing (SDK bridge_zip_disc)", "src; diag shows consume/reset only"],
    }
    if ext:
        params.update(ext["params"])
    with open(ppath, "w", encoding="utf-8") as fh:
        json.dump(params, fh, indent=1)
    P("\nwrote %s and %s" % (os.path.basename(jpath), os.path.basename(ppath)))



# ============================================================================= round 2 + grapple (optional arguments)
# Everything below runs only with --round2 / --grapple; the round-1 command line and its outputs are unchanged.
STATE_RE = re.compile(r"\[HSD-STATE\]\s*(.*)")
JUMP_V = 289.828


def load_state(folder):
    """Client [HSD-STATE] lines: run -> list of dicts sorted by t (zip / gr / trav / mant / hang / wr / ph / glide)."""
    out = {}
    for fn in sorted(glob.glob(os.path.join(folder, "platform", "logs", "client", "*", "script*.log"))):
        with open(fn, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = STATE_RE.search(line)
                if not m:
                    continue
                kv = dict(re.findall(r"(\w+)=(\S+)", m.group(1)))
                d = {"t": fnum(kv.get("t"))}
                for k in ("trav", "mant", "hang", "wr", "zip", "gr", "ph"):
                    d[k] = kv.get(k) == "true"
                d["glide"] = fnum(kv.get("glide"))
                out.setdefault("r%s" % kv.get("run"), []).append(d)
    for k in out:
        out[k].sort(key=lambda d: d["t"])
    return out


def attach_state(t, states):
    ss = states.get("r%d" % t["run"], [])
    j, n_ok = 0, 0
    for f in t["frames"]:
        while j < len(ss) - 1 and ss[j]["t"] < f["t"] - 0.004:
            j += 1
        if ss and abs(ss[j]["t"] - f["t"]) < 0.005:
            f["st"] = ss[j]
            n_ok += 1
        else:
            f["st"] = None
    return n_ok


def state_runs(fr, key):
    """[(first, last)] frame index runs where state[key] is true."""
    runs, a = [], None
    for i, f in enumerate(fr):
        on = bool(f.get("st") and f["st"][key])
        if on and a is None:
            a = i
        if not on and a is not None:
            runs.append((a, i - 1))
            a = None
    if a is not None:
        runs.append((a, len(fr) - 1))
    return runs


def heading(v):
    return math.degrees(math.atan2(v[1], v[0]))


def angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def v_std_curve(fts, v1=8.333, a1=600.0, a2=400.0, k_switch=60, cap=600.0):
    """Rest-mount ride speed for k = 0..len(fts)-1 (k = cmds after the mount cmd; fts[k] = frame time of cmd k)."""
    out = [0.0]
    for k in range(1, len(fts)):
        v = v1 if k == 1 else out[-1] + (a1 if k <= k_switch else a2) * fts[k]
        out.append(min(v, cap))
    return out


def s_or(x, key):
    return x[key] if x else None


def run_round2(folders, g):
    out = {"sessions": [], "trials": []}
    P("\n" + "=" * 100 + "\nROUND 2 (M6-A3 zip2)\n" + "=" * 100)
    allt = []
    for fo in folders:
        S = load_session(fo)
        states = load_state(fo)
        out["sessions"].append(S["folder"])
        n_st = sum(attach_state(t, states) for t in S["trials"])
        n_fr = sum(len(t["frames"]) for t in S["trials"])
        P("session %s  label=%s  legend=%s  trials used %d, skipped %s ; HSD-STATE matched to %d/%d frames" % (
            S["folder"], S["runner"].get("label"), S["runner"].get("legend"), len(S["trials"]),
            ["r%d %s (%s)" % (x["run"], x["schedule"], x["why"]) for x in S["skipped"]], n_st, n_fr))
        allt.extend(S["trials"])
    by = {}
    for t in allt:
        by.setdefault(t["schedule"], []).append(t)
    rows = []
    # ---------------------------------------------------------------- jump-off law over ride speeds (z5b, z8, z9)
    P("\n[R2-1] Jump-off law v_out = h_rope * min(v_ride, 400) + z * 289.828 over new ride speeds")
    P("%-14s %-6s %-6s %-9s %-26s %-26s %-9s %-7s %-8s" % ("schedule", "run", "state", "ride_v", "exit v cl (MT)", "exit v sv",
                                                            "resid", "zip_fr", "mountlat"))
    law = []
    for sch in sorted(by):
        if not (sch.startswith("z5b") or sch.startswith("z8") or sch.startswith("z9")):
            continue
        for t in by[sch]:
            r = analyse_trial(t, g)
            zr = state_runs(t["frames"], "zip")
            r["zip_state_frames"] = sum(b - a + 1 for a, b in zr)
            res_sv = None
            if r.get("exit_v_sv") and r.get("exit_pred_min400"):
                res_sv = rnd(norm(sub(tuple(r["exit_v_sv"]), tuple(r["exit_pred_min400"]))), 4)
            r["exit_resid_min400_sv"] = res_sv
            st_ = r.get("diag_jumpoff_sv") and r["diag_jumpoff_sv"]["state"]
            P("%-14s r%-5d %-6s %-9s %-26s %-26s %-9s %-7s %-8s" % (sch, t["run"], st_, r.get("ride_v_before"), r.get("exit_v_cl"),
                                                                    r.get("exit_v_sv"), r.get("exit_resid_min400_cl"),
                                                                    r["zip_state_frames"], r.get("mount_latency_frames")))
            if r.get("exit_resid_min400_cl") is not None:
                law.append(r)
            rows.append(r)
    P("  residual |v_cl - pred| over %d round-2 exits: %s ; dedi: %s" % (len(law), stats([r["exit_resid_min400_cl"] for r in law]),
                                                                       stats([r["exit_resid_min400_sv"] for r in law])))
    P("  ride speeds covered (round 2): %s" % sorted(set(round(r["ride_v_before"], 1) for r in law)))
    # ---------------------------------------------------------------- super jump the community way (z5b)
    P("\n[R2-2] Super Jump: jump-off M cmds after the mount (still near the ground), second jump K cmds after it")
    P("%-11s %-6s %-4s %-4s %-9s %-7s %-9s %-9s %-10s %-8s %-7s %-8s" % ("schedule", "run", "M", "K", "released", "dk_air",
                                                                        "vz_pre", "vz_post", "dvz-grav", "resid", "dvxy", "apex+"))
    sj = []
    for sch in sorted(by):
        if not sch.startswith("z5b"):
            continue
        for t in by[sch]:
            fr = t["frames"]
            je = edges_of(t, "jump")
            ju = edges_of(t, "jump", "up")
            iu = edge_index(fr, edges_of(t, "use")[0])
            ij = [edge_index(fr, e) for e in je]
            released = not (ju and len(je) > 1 and ju[0]["frame"] == je[1]["frame"])
            i2 = ij[1]
            f2, f1 = fr[i2], fr[i2 - 1]
            dvz = f2["vz"] - (f1["vz"] - g * f2["ft"])
            pred = JUMP_V - 0.5 * g * f2["ft"]
            applied = dvz > 5
            apex = max(f["oz"] for f in fr[ij[0]:]) - fr[ij[0]]["oz"]
            row = {"schedule": sch, "run": t["run"], "M": ij[0] - iu, "K": i2 - ij[0], "released": released,
                   "dk_air": i2 - iu, "vz_pre": rnd(f1["vz"], 3), "vz_post": rnd(f2["vz"], 3), "dvz_minus_grav": rnd(dvz, 3),
                   "applied": applied, "resid_vs_jump": rnd(dvz - pred, 3) if applied else None,
                   "dvxy": rnd(math.hypot(f2["vx"], f2["vy"]) - math.hypot(f1["vx"], f1["vy"]), 3),
                   "apex_gain": rnd(apex, 2), "ground_before": f1["ground"], "jumpoff_v": rnd(vel(fr[ij[0]]), 3),
                   "jumpoff_z_above_floor": rnd(fr[ij[0]]["oz"] - FLOOR_Z, 2)}
            sj.append(row)
            P("%-11s r%-5d %-4d %-4d %-9s %-7d %-9s %-9s %-10s %-8s %-7s %-8s" % (sch, t["run"], row["M"], row["K"], released,
                                                                                  row["dk_air"], row["vz_pre"], row["vz_post"],
                                                                                  row["dvz_minus_grav"], row["resid_vs_jump"],
                                                                                  row["dvxy"], row["apex_gain"]))
    ap_ = [r for r in sj if r["applied"]]
    P("  applied %d/%d ; not applied (schedule, button released between presses): %s" % (
        len(ap_), len(sj), sorted(set((r["schedule"], r["released"]) for r in sj if not r["applied"]))))
    P("  applied: dvz - gravity step %s ; model vz_post = vz_pre + 289.828 - 1.5 g dt residual %s" % (
        stats([r["dvz_minus_grav"] for r in ap_]), stats([r["resid_vs_jump"] for r in ap_])))
    P("  cmds since the mount lifted the player off the ground, at the second press: applied %s ; round 1 (never applied)"
      " had >= 63" % sorted(set(r["dk_air"] for r in ap_)))
    P("  jump-off height above the floor %s ; apex gain above the jump-off point: applied %s vs not applied %s" % (
        stats([r["jumpoff_z_above_floor"] for r in sj]), stats([r["apex_gain"] for r in ap_]),
        stats([r["apex_gain"] for r in sj if not r["applied"]])))
    out["super_jump"] = sj
    # ---------------------------------------------------------------- view turn during the ride (z9) + vertical turn
    P("\n[R2-3] View yaw during the ride and the exit direction")
    vt = []
    for sch in ("z9_yaw45", "z9_yaw90", "z6_vert_turn"):
        for t in by.get(sch, []):
            fr = t["frames"]
            iu = edge_index(fr, edges_of(t, "use")[0])
            ir = edge_index(fr, edges_of(t, "right")[0])
            irr = edge_index(fr, edges_of(t, "right", "up")[0])
            kfree = None
            for i in range(ir, irr):
                if abs(angdiff(fr[i]["yaw"], fr[i - 1]["yaw"])) >= 0.5 and abs(angdiff(fr[i + 1]["yaw"], fr[i]["yaw"])) >= 0.5:
                    kfree = i
                    break
            rates = [abs(angdiff(fr[i]["yaw"], fr[i - 1]["yaw"])) / fr[i]["ft"] for i in range((kfree or ir) + 2, irr - 1)]
            nudge = max((abs(fr[i]["yaw"]) for i in range(ir, kfree or irr)), default=None)
            row = {"schedule": sch, "run": t["run"], "right_down_k": ir - iu, "free_turn_k": (kfree - iu) if kfree else None,
                   "max_abs_yaw_before_free": rnd(nudge, 3), "turn_rate_deg_s": rnd(st.median(rates), 2) if rates else None,
                   "yaw_end_turn": rnd(fr[irr]["yaw"], 3)}
            g2 = mt_gap(t["cl"])
            if g2:
                c = t["cl"][g2[1]]
                v = (c["vx"], c["vy"], c["vz"])
                ie = next((i for i in range(iu + 1, len(fr)) if fr[i].get("st") and not fr[i]["st"]["zip"]
                           and fr[i - 1].get("st") and fr[i - 1]["st"]["zip"]), None)
                yaw_exit = fr[ie]["yaw"] if ie is not None else None
                sv_ = t["sv"].get(g2[1])
                row.update({"exit_v_cl": rnd(v, 3), "exit_v_sv": rnd((sv_["vx"], sv_["vy"], sv_["vz"]), 3) if sv_ else None,
                            "exit_h_speed": rnd(math.hypot(v[0], v[1]), 3), "exit_heading": rnd(heading(v), 3),
                            "yaw_at_exit": rnd(yaw_exit, 3),
                            "heading_minus_yaw": rnd(angdiff(heading(v), yaw_exit), 3) if yaw_exit is not None else None,
                            "heading_minus_rope": rnd(angdiff(heading(v), 0.0), 3)})
            vt.append(row)
            P("  %-13s r%d right@k%s free turn from k%s (max |yaw| before %s) rate %s deg/s yaw %s ; exit v %s |h| %s heading %s"
              " yaw_exit %s (heading-yaw %s, heading-rope %s)" % (
                  sch, t["run"], row["right_down_k"], row["free_turn_k"], row["max_abs_yaw_before_free"], row["turn_rate_deg_s"],
                  row["yaw_end_turn"], row.get("exit_v_cl"), row.get("exit_h_speed"), row.get("exit_heading"), row.get("yaw_at_exit"),
                  row.get("heading_minus_yaw"), row.get("heading_minus_rope")))
    out["view_turn"] = vt
    # ---------------------------------------------------------------- air grab (z7b tap, z7c hold)
    P("\n[R2-4] Air grab (start 120 u from Z1 at y 6680, facing +Y, pitch -15)")
    ag = []
    for sch in ("z7b_air", "z7c_air_hold"):
        for t in by.get(sch, []):
            fr = t["frames"]
            iu = edge_index(fr, edges_of(t, "use")[0])
            pre = fr[iu - 1]
            Pp = add(pos(pre), (0.0, 0.0, EYE_RAISE))
            eye = eye_dir(pre["pitch"], pre["yaw"])
            sP = max(0.0, min(rope_len("Z1"), rope_param("Z1", Pp)))
            b = find_angle_min("Z1", Pp, eye, 130.0)
            ucl = [d for d in t["diag"] if d["tag"] == "ZIPRAIL-USE" and d["side"] == "cl" and "result" in d["kv"]]
            usv = [d for d in t["diag"] if d["tag"] == "ZIPRAIL-USE" and d["side"] == "sv" and "result" in d["kv"]]
            zr = state_runs(fr, "zip")
            jumps = [rnd(norm(sub(pos(fr[b_ + 1]), pos(fr[b_]))), 2) for a_, b_ in zr if b_ + 1 < len(fr)]
            g2 = mt_gap(t["cl"])
            sv_use = sum(1 for k in range(t["cmd_range"][0], t["cmd_range"][1] + 1) if k in t["sv"] and t["sv"][k]["buttons"] & IN_USE)
            row = {"schedule": sch, "run": t["run"], "press_k_after_jump": iu - edge_index(fr, edges_of(t, "jump")[0]),
                   "o_pre": rnd(pos(pre), 2), "v_pre": rnd(vel(pre), 2), "P_to_rope": rnd(norm(sub(rope_point("Z1", sP), Pp)), 2),
                   "rope_minus_P_z": rnd(394.92 - Pp[2], 2), "min_angle_R130": rnd(b[0], 2) if b else None,
                   "cl_use_events": [(d["cmd"], d["kv"].get("result"), d["kv"].get("cd")) for d in ucl],
                   "sv_use_events": len(usv), "zip_state_runs": zr, "pos_jump_after_zip_run": jumps,
                   "mt_cl_gap": list(g2) if g2 else None, "sv_cmds_with_IN_USE": sv_use}
            ag.append(row)
            P("  %-13s r%d press k+%d after the jump: o %s v %s P->rope %s rope-P z %s minAng %s | client use %s | dedi use events %d,"
              " dedi cmds with IN_USE %d | zip-state runs %s, position jump after each %s, MT cl gap %s" % (
                  sch, t["run"], row["press_k_after_jump"], row["o_pre"], row["v_pre"], row["P_to_rope"], row["rope_minus_P_z"],
                  row["min_angle_R130"], row["cl_use_events"], row["sv_use_events"], sv_use, zr, jumps, row["mt_cl_gap"]))
    out["air_grab"] = ag
    # ---------------------------------------------------------------- duck held through the crouch-off
    P("\n[R2-5] Crouch-off with duck held 1 s (half-duck parity)")
    dh = []
    for t in by.get("z3_duckhold", []):
        r = analyse_trial(t, g)
        k0 = mt_gap(t["cl"])[1]
        dz_air, dz_gnd, steps, duckseq, prev = [], [], {"cl": 0, "sv": 0}, [], None
        for k in range(k0, k0 + 150):
            c, s_ = t["cl"].get(k), t["sv"].get(k)
            if not (c and s_):
                continue
            (dz_gnd if c["ground"] == 1 and s_["ground"] == 1 else dz_air).append(s_["oz"] - c["oz"])
            for side, rr in (("cl", c), ("sv", s_)):
                if rr["poz"] is not None and rr["ground"] == 0 and rr["pvz"] is not None:
                    if abs((rr["poz"] - rr["oz"]) - 0.5 * (rr["vz"] + rr["pvz"]) / 120.0) > 2.0:
                        steps[side] += 1
            key = (c["duck"], s_["duck"])
            if key != prev:
                duckseq.append((k - k0, key))
            prev = key
        row = {"run": t["run"], "exit_v_cl": r.get("exit_v_cl"), "ride_v": r.get("ride_v_before"),
               "resid_min400": r.get("exit_resid_min400_cl"), "dz_air_sv_minus_cl": stats(dz_air),
               "dz_ground_sv_minus_cl": stats(dz_gnd), "z_steps_gt2u": steps, "duck_field_seq": duckseq[:6],
               "land_cmd_cl_sv": r.get("land_cmd_cl_sv"), "hsd_crouch_values": sorted(set(str(f["crouch"]) for f in t["frames"]))}
        dh.append(row)
        P("  r%d exit v %s (ride %s, resid %s) | dz sv-cl air %s ground [%s, %s] | z steps >2u %s | MT duck (cl,sv) %s | landing"
          " cmd cl/sv %s | HSD crouch %s" % (t["run"], row["exit_v_cl"], row["ride_v"], row["resid_min400"], s_or(stats(dz_air), "mean"),
                                             s_or(stats(dz_gnd), "min"), s_or(stats(dz_gnd), "max"), steps, duckseq[:5],
                                             row["land_cmd_cl_sv"], row["hsd_crouch_values"]))
    out["duck_hold"] = dh
    out["jumpoff_rows"] = [{k: r.get(k) for k in ("schedule", "run", "ride_v_before", "exit_v_cl", "exit_v_sv", "exit_resid_min400_cl",
                                                  "exit_resid_min400_sv", "diag_jumpoff_sv", "zip_state_frames", "exit_kind")} for r in rows]
    out["n_trials"] = len(allt)
    return out


def run_grapple(folders, g):
    out = {"sessions": []}
    P("\n" + "=" * 100 + "\nGRAPPLE (M6-G: release, momentum, grapple -> zipline handoff)\n" + "=" * 100)
    allt = []
    for fo in folders:
        S = load_session(fo)
        states = load_state(fo)
        out["sessions"].append(S["folder"])
        n_st = sum(attach_state(t, states) for t in S["trials"])
        P("session %s  label=%s  legend=%s  trials used %d, skipped %s ; HSD-STATE matched to %d/%d frames" % (
            S["folder"], S["runner"].get("label"), S["runner"].get("legend"), len(S["trials"]),
            ["r%d %s (%s)" % (x["run"], x["schedule"], x["why"]) for x in S["skipped"]], n_st,
            sum(len(t["frames"]) for t in S["trials"])))
        allt.extend(S["trials"])
    by = {}
    for t in allt:
        by.setdefault(t["schedule"], []).append(t)
    P("\n[G1] Grapple release (second tactical or attack 72 cmds after the grapple press) vs hold")

    def base(t):
        fr = t["frames"]
        ip = edge_index(fr, edges_of(t, "offhand1")[0])
        gr = state_runs(fr, "gr")
        lift = next((i for i in range(ip, len(fr)) if fr[i]["ground"] == 0), None)
        return fr, ip, gr, lift

    hold_v = {}
    for t in by.get("g1_hold", []):
        fr, ip, gr, lift = base(t)
        for i in range(ip, len(fr)):
            hold_v.setdefault(i - ip, []).append(vel(fr[i]))
    g1 = []
    for sch in ("g1_rel_tac", "g1_rel_attack", "g1_hold"):
        for t in by.get(sch, []):
            fr, ip, gr, lift = base(t)
            row = {"schedule": sch, "run": t["run"], "gr_runs_rel": [(a - ip, b - ip) for a, b in gr],
                   "gr_frames": sum(b - a + 1 for a, b in gr), "liftoff_k": (lift - ip) if lift is not None else None}
            sp = [norm(vel(f)) for f in fr]
            kmax = max(range(ip, len(fr)), key=lambda i: sp[i])
            row["max_speed"] = rnd(sp[kmax], 3)
            row["max_speed_k"] = kmax - ip
            stop = next((i for i in range(ip + 1, len(fr)) if sp[i - 1] - sp[i] > 150), None)
            row["pull_stop_k"] = (stop - ip) if stop else None
            row["pull_stop_o"] = rnd(pos(fr[stop]), 2) if stop else None
            row["pull_stop_v_before_after"] = (rnd(vel(fr[stop - 1]), 3), rnd(vel(fr[stop]), 3)) if stop else None
            first = edges_of(t, "offhand1")[0]["frame"]
            sec = [e for e in t["edges"] if e["edge"] == "down" and e["key"] in ("offhand1", "attack") and e["frame"] != first]
            if sec:
                i2 = edge_index(fr, sec[0])
                row["second_press_k"] = i2 - ip
                rel = None
                for i in range(i2, len(fr) - 6):
                    if all(fr[j]["ground"] == 0 and math.hypot(fr[j]["vx"] - fr[j - 1]["vx"], fr[j]["vy"] - fr[j - 1]["vy"]) < 0.05
                           for j in range(i, i + 6)):
                        rel = i
                        break
                if rel is not None and stop is not None and rel >= stop:
                    rel = None   # the pull ended at the wall, not at the press
                row["release_k"] = (rel - ip) if rel is not None else None
                row["release_latency_cmds"] = (rel - i2) if rel is not None else None
                if rel is not None:
                    vr = vel(fr[rel])
                    row["release_v"] = rnd(vr, 3)
                    hv = hold_v.get(rel - 1 - ip)
                    if hv:
                        hm = tuple(st.mean(v[c] for v in hv) for c in range(3))
                        row["hold_v_same_k_minus1"] = rnd(hm, 3)
                        row["release_minus_hold_h"] = rnd(math.hypot(vr[0], vr[1]) - math.hypot(hm[0], hm[1]), 3)
                    land = next((i for i in range(rel, len(fr)) if fr[i]["ground"] == 1), None)
                    seg = fr[rel:land] if land else fr[rel:]
                    row["post_release_dvxy_total"] = rnd(math.hypot(seg[-1]["vx"], seg[-1]["vy"]) - math.hypot(seg[0]["vx"], seg[0]["vy"]), 4) if len(seg) > 1 else None
                    gz = [(seg[j - 1]["vz"] - seg[j]["vz"]) / seg[j]["ft"] for j in range(1, len(seg))]
                    row["post_release_gravity"] = rnd(st.median(gz), 2) if gz else None
                    row["land_k"] = (land - ip) if land else None
                    row["land_v"] = rnd(vel(fr[land - 1]), 3) if land else None
                    row["gr_true_after_release_cmds"] = (gr[0][1] - rel) if gr else None
            g1.append(row)
            P("  %-13s r%d gr %s (%d fr) lift k%s max|v| %s @k%s pull stop k%s %s %s | 2nd press k%s release k%s (latency %s)"
              " v_rel %s hold(k-1) %s d|v_h| %s | post: d|v_h| %s g %s land k%s v %s | gr flag true %s cmds after release" % (
                  sch, t["run"], row["gr_runs_rel"], row["gr_frames"], row["liftoff_k"], row["max_speed"], row["max_speed_k"],
                  row["pull_stop_k"], row["pull_stop_o"], row["pull_stop_v_before_after"], row.get("second_press_k"),
                  row.get("release_k"), row.get("release_latency_cmds"), row.get("release_v"), row.get("hold_v_same_k_minus1"),
                  row.get("release_minus_hold_h"), row.get("post_release_dvxy_total"), row.get("post_release_gravity"),
                  row.get("land_k"), row.get("land_v"), row.get("gr_true_after_release_cmds")))
    att = by.get("g1_rel_attack", [])
    if att and hold_v:
        dmax = 0.0
        for t in att:
            fr, ip, gr, lift = base(t)
            for i in range(ip, min(len(fr), ip + 180)):
                hv = hold_v.get(i - ip)
                if hv:
                    dmax = max(dmax, abs(norm(vel(fr[i])) - st.mean(norm(v) for v in hv)))
        P("  attack vs hold: max | |v|_attack(k) - mean |v|_hold(k) | over the first 180 cmds = %.3f u/s" % dmax)
        out["attack_vs_hold_max_dv"] = rnd(dmax, 3)
    out["g1"] = g1
    # ---------------------------------------------------------------- g3: grapple -> zipline handoff
    P("\n[G3] Grapple aimed at the middle of Z1 from 250 u (yaw 36.87, pitch -9.09), with / without a use press")
    g3 = []
    d_hat = rope_dir("Z1")
    for sch in ("g3_hook", "g3_hook_use"):
        for t in by.get(sch, []):
            fr = t["frames"]
            ip = edge_index(fr, edges_of(t, "offhand1")[0])
            gr = state_runs(fr, "gr")
            zr = state_runs(fr, "zip")
            ucl = [d for d in t["diag"] if d["tag"] == "ZIPRAIL-USE" and d["side"] == "cl" and "result" in d["kv"]]
            usv = [d for d in t["diag"] if d["tag"] == "ZIPRAIL-USE" and d["side"] == "sv" and "result" in d["kv"]]
            okc = next((d for d in ucl if d["kv"].get("result") == "1"), None)
            oks = next((d for d in usv if d["kv"].get("result") == "1"), None)
            g2 = mt_gap(t["cl"])
            row = {"schedule": sch, "run": t["run"], "gr_runs_rel": [(a - ip, b - ip) for a, b in gr],
                   "zip_runs_rel": [(a - ip, b - ip) for a, b in zr],
                   "cl_attempts_fail": sum(1 for d in ucl if d["kv"].get("result") == "0"),
                   "cl_fail_why": sorted(set((d["kv"].get("why"), d["kv"].get("wdf")) for d in ucl if d["kv"].get("result") == "0")),
                   "sv_attempts_fail": sum(1 for d in usv if d["kv"].get("result") == "0"),
                   "cl_first_attempt_cmd": ucl[0]["cmd"] if ucl else None, "cl_success_cmd": okc and okc["cmd"],
                   "sv_success_cmd": oks and oks["cmd"], "grapple_flag": okc and okc["kv"].get("grapple"),
                   "success_eq_first_missing_mt": (okc["cmd"] == g2[0] + 1) if (okc and g2) else None,
                   "first_attempt_minus_mt_start": (ucl[0]["cmd"] - t["cmd_range"][0]) if ucl else None,
                   "Q": rnd(oks["vec"].get("use"), 2) if oks else None}
            if zr:
                iz = zr[0][0]
                pre = fr[iz - 1]
                vpre = vel(pre)
                row["mount_k_after_press"] = iz - ip
                row["v_pre"] = rnd(vpre, 3)
                row["speed_pre"] = rnd(norm(vpre), 3)
                Pp = add(pos(pre), (0.0, 0.0, EYE_RAISE))
                eye = eye_dir(pre["pitch"], pre["yaw"])
                if oks:
                    Q = oks["vec"]["use"]
                    row["Q_minus_P_dist"] = rnd(norm(sub(Q, Pp)), 3)
                    row["Q_angle_eye"] = rnd(math.degrees(math.acos(max(-1, min(1, dot(sub(Q, Pp), eye) / norm(sub(Q, Pp)))))), 3)
                    row["v_pre_angle_to_Q"] = rnd(math.degrees(math.acos(max(-1, min(1, dot(unit(vpre), unit(sub(Q, pos(pre)))))))), 3)
                    bp = find_angle_min("Z1", Pp, eye, 130.0, 8000)
                    row["Q_pred_minangle"] = rnd(bp[1], 2) if bp else None
                    row["Q_pred_minus_Q_x"] = rnd(bp[1][0] - Q[0], 2) if bp else None
                    row["Q_pred_angle"] = rnd(bp[0], 3) if bp else None
                    # designed aim point: the start view ray (yaw 36.87, pitch -9.09 = atan(40/250)) meets Z1 at x -13800
                    aim = (-13800.0, 6800.0, 394.92)
                    row["Q_minus_aim_x"] = rnd(Q[0] - aim[0], 2)
                    row["dist_origin_to_aim_at_mount"] = rnd(norm(sub(aim, pos(pre))), 2)
                    row["dist_P_to_aim_at_mount"] = rnd(norm(sub(aim, Pp)), 2)
                first_ok, first_in_r = None, None
                for i in range(ip, iz):
                    f = fr[i]
                    b = find_angle_min("Z1", add(pos(f), (0.0, 0.0, EYE_RAISE)), eye_dir(f["pitch"], f["yaw"]), 130.0, 1600)
                    if b and first_in_r is None:
                        first_in_r = (i, b[0])
                    if b and b[0] < 40.7:
                        first_ok = i
                        break
                row["first_frame_rope_within_130_k"] = (first_in_r[0] - ip, rnd(first_in_r[1], 2)) if first_in_r else None
                row["first_frame_find_possible_k"] = (first_ok - ip) if first_ok is not None else None
                row["mount_minus_first_possible_cmds"] = (iz - first_ok) if first_ok is not None else None
                ride = fr[iz:]
                sp = [norm(vel(f)) for f in ride]
                e = sp[1]
                row["entry_speed"] = rnd(e, 3)
                row["entry_dir_dot_rope"] = rnd(dot(unit(vel(ride[1])), d_hat), 6)
                row["proj_v_pre_on_rope"] = rnd(dot(vpre, d_hat), 3)
                row["entry_minus_proj"] = rnd(e - dot(vpre, d_hat), 3)
                row["entry_minus_proj_over_ft"] = rnd((e - dot(vpre, d_hat)) / ride[1]["ft"], 2)
                row["mount_cmd_moves"] = rnd(norm(sub(pos(ride[0]), pos(pre))), 3)
                vs = v_std_curve([f["ft"] for f in ride[:200]])
                pred = [0.0]
                for k in range(1, len(vs)):
                    pred.append(max(e, vs[k]) if k <= 60 else min(600.0, pred[-1] + 400.0 * ride[k]["ft"]))
                end = next((k for k in range(1, len(vs)) if ride[k].get("st") and not ride[k]["st"]["zip"]), len(vs))
                row["state2_model_resid"] = stats([abs(sp[k] - pred[k]) for k in range(1, min(end, len(vs)))])
                row["speed_k"] = {k: rnd(sp[k], 3) for k in (1, 30, 58, 59, 60, 61, 62, 100) if k < len(sp)}
                if len(ride) > 40:
                    row["yaw_pitch_k0_k40"] = (rnd((ride[0]["yaw"], ride[0]["pitch"]), 3), rnd((ride[40]["yaw"], ride[40]["pitch"]), 3))
                row["view_90pct_k"] = next((k for k in range(len(ride)) if abs(ride[k]["yaw"]) <= 0.1 * abs(ride[0]["yaw"])), None)
                steady = ride[60:end]
                if steady:
                    row["hang_below_rope"] = rnd(st.mean(394.92 - f["oz"] for f in steady), 3)
                    row["lateral_y"] = rnd(st.mean(f["oy"] - 6800.0 for f in steady), 3)
                row["dist_to_hang_line_k"] = {k: rnd(math.hypot(ride[k]["oy"] - 6799.77, ride[k]["oz"] - 314.75), 2)
                                              for k in (0, 5, 10, 15, 20, 30, 40) if k < len(ride)}
            if g2:
                c = t["cl"][g2[1]]
                ref = add((c["ox"], c["oy"], c["oz"]), (0.0, 0.0, 80.0))
                row["exit_v_cl"] = rnd((c["vx"], c["vy"], c["vz"]), 3)
                sv_ = t["sv"].get(g2[1])
                row["exit_v_sv"] = rnd((sv_["vx"], sv_["vy"], sv_["vz"]), 3) if sv_ else None
                row["exit_dist_to_end"] = rnd(rope_len("Z1") - rope_param("Z1", ref), 3)
                row["zip_frames"] = sum(b - a + 1 for a, b in zr)
            ue = edges_of(t, "use")
            row["use_press_k"] = (edge_index(fr, ue[0]) - ip) if ue else None
            g3.append(row)
            P("  %-12s r%d gr %s zip %s | client attempts: first cmd %s (+%s after trial start), %d fails %s, success cmd %s"
              " (= first missing MT: %s); dedi fails %d, success cmd %s | Q %s" % (
                  sch, t["run"], row["gr_runs_rel"], row["zip_runs_rel"], row["cl_first_attempt_cmd"], row["first_attempt_minus_mt_start"],
                  row["cl_attempts_fail"], row["cl_fail_why"], row["cl_success_cmd"], row["success_eq_first_missing_mt"],
                  row["sv_attempts_fail"], row["sv_success_cmd"], row["Q"]))
            P("      mount k%s (use press k%s) v_pre %s |v| %s ; |Q-P| %s angle %s (min-angle rule: angle %s, x - Q.x %s) ; v_pre angle"
              " to Q %s ; rope first within 130 u at k%s ; Find first possible k%s (mount %s cmds later) ; mount cmd moves %s ;"
              " Q.x - aim.x %s, |aim - origin| %s, |aim - P| %s" % (
                  row.get("mount_k_after_press"), row["use_press_k"], row.get("v_pre"), row.get("speed_pre"), row.get("Q_minus_P_dist"),
                  row.get("Q_angle_eye"), row.get("Q_pred_angle"), row.get("Q_pred_minus_Q_x"), row.get("v_pre_angle_to_Q"),
                  row.get("first_frame_rope_within_130_k"), row.get("first_frame_find_possible_k"),
                  row.get("mount_minus_first_possible_cmds"), row.get("mount_cmd_moves"), row.get("Q_minus_aim_x"),
                  row.get("dist_origin_to_aim_at_mount"), row.get("dist_P_to_aim_at_mount")))
            P("      entry |v| %s (dir.rope %s) vs v_pre.rope %s: diff %s (= %s u/s^2 x dt) ; state-2 model max(entry, rest curve)"
              " |resid| %s ; speeds %s" % (row.get("entry_speed"), row.get("entry_dir_dot_rope"), row.get("proj_v_pre_on_rope"),
                                          row.get("entry_minus_proj"), row.get("entry_minus_proj_over_ft"),
                                          row.get("state2_model_resid"), row.get("speed_k")))
            P("      view (yaw, pitch) k0 -> k40 %s (90%% at k%s) ; distance to the hang line %s ; hang %s lat %s ; exit v cl %s sv %s"
              " dist_end %s ; zip frames %s" % (row.get("yaw_pitch_k0_k40"), row.get("view_90pct_k"), row.get("dist_to_hang_line_k"),
                                                row.get("hang_below_rope"), row.get("lateral_y"), row.get("exit_v_cl"), row.get("exit_v_sv"),
                                                row.get("exit_dist_to_end"), row.get("zip_frames")))
    P("  summary: entry - v_pre.rope %s ; state-2 |resid| max %s ; mount k after the grapple press %s ; Q x %s ; |Q-P| %s" % (
        stats([r.get("entry_minus_proj") for r in g3]),
        max((r["state2_model_resid"]["max"] for r in g3 if r.get("state2_model_resid")), default=None),
        stats([r.get("mount_k_after_press") for r in g3]), stats([r["Q"][0] for r in g3 if r.get("Q")]),
        stats([r.get("Q_minus_P_dist") for r in g3])))
    P("  Q.x - designed aim point x %s ; |aim - origin| at the mount %s" % (stats([r.get("Q_minus_aim_x") for r in g3]),
                                                                         stats([r.get("dist_origin_to_aim_at_mount") for r in g3])))
    out["g3"] = g3
    return out


def run_extensions(r2_folders, g_folders, g):
    results, params = {}, {}
    if r2_folders:
        r2 = run_round2(r2_folders, g)
        results["round2"] = r2
        sj = [r for r in r2["super_jump"] if r["applied"]]
        params["super_jump"] = {
            "applies": [True, "meas (round 2): a second jump press after a zip jump-off applies when it comes soon after the mount"
                              " lifted the player off the ground (applied at %s cmds; never at >= 63 cmds in round 1); a released"
                              " jump button between the presses is required" % sorted(set(r["dk_air"] for r in sj))],
            "impulse": ["vz_post = vz_pre + 289.828 - 1.5 g dt (the ground-jump post-state rule), v_xy unchanged", "fit (residual in A3-ZIPLINE.md)"],
            "window_cmds_since_ground": [[max(r["dk_air"] for r in sj) if sj else None, 63], "bracket [applied max, never-applied min]"],
        }
        params["view_on_ride"] = ["yaw and pitch are pulled to the rope direction during the 0.5 s mount state (input ignored);"
                                  " free look afterwards; vertical rope: yaw free at once", "meas (z9, z6_vert_turn)"]
        params["jump_off_direction"] = ["along the rope, independent of the view yaw (tested to -63 deg)", "meas (z9)"]
        params["jump_off_speed_law_round2"] = ["h = min(v_ride, 400) confirmed for v_ride 0 .. 600", "fit, residual 0 (round 1 + round 2)"]
        params["vertical_exit_push"] = ["400 horizontal along the view yaw at the top", "meas (z6_vert_turn)"]
        params["air_attach_round2"] = ["held use 120 u from the rope: the client predicts a mount, the dedi never mounts and corrects"
                                       " the client; a tap: nothing on either side", "meas (z7b/z7c)"]
        params["half_duck_parity"] = ["duck held through the crouch-off: no hull step on either side; only the 0.17 u hang offset"
                                      " until landing", "meas (z3_duckhold)"]
    if g_folders:
        gg = run_grapple(g_folders, g)
        results["grapple"] = gg
        params["grapple_zip_handoff"] = [
            "while the grapple is active the client and dedi call Zipline_Use(grapple=1) every cmd; it mounts on the first cmd whose"
            " Find succeeds; entry speed = v_pre . rope_dir + 400*dt; during the 0.5 s mount state v = max(entry, rest-mount curve);"
            " afterwards identical to a rest mount; no use press needed", "meas+fit (GRAPPLE-ZIP.md)"]
        params["grapple_release"] = ["a second tactical press ends the pull; the instantaneous velocity is kept, then ordinary"
                                     " gravity with no drag; attack does not release", "meas (GRAPPLE-ZIP.md)"]
    return {"results": results, "params": params}

if __name__ == "__main__":
    main()
