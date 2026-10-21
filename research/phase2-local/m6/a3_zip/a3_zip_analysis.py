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
SCHED_ROPE = {"z6_up": "Z2", "z6_vert": "Z3"}  # everything else uses Z1
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
    with open(ppath, "w", encoding="utf-8") as fh:
        json.dump(params, fh, indent=1)
    P("\nwrote %s and %s" % (os.path.basename(jpath), os.path.basename(ppath)))


if __name__ == "__main__":
    main()
