"""N4-B ground key-turn analysis (ledger G-07).

For each n4b_* trial, find the command where the movement keys change, then step two
models forward from the measured pre-state with the measured per-command dt and inputs:

  native  N2-G formulas: input curve m(2 - m) (x1.25 while sprinting), Friction that
          spares the wish-aligned speed up to wishspeed, banded accel, Accelerate cap
          max(|v_old|, wishspeed)
  instant the HSD replay motor: v = s * wishdir every command (M2 speed law)
  vector  the HSD Reference config (R5MotorV2.GroundVectorRedirect, groundVectorRedirect on):
          the off-wish part decays at the deceleration, the M2 band accel adds along the
          wish up to cap - s, |v| <= max(cap, s - D*dt); no input curve

and compare both with the measured post velocity of every ground command for 0.6 s.

  py -3 keyturn_analysis.py <session folder> [--json out.json]

Reuses the M2 loader (m2/ground/ground_analysis.py) and hsdtel. Standard library only.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "research", "phase2-local", "m2", "ground"))
import ground_analysis as ga  # noqa: E402

SCHEDULES = ("n4b_wd", "n4b_ws", "n4b_ad", "n4b_wwd")
WINDOW_S = 0.6
# census (Gibraltar, every legend except sprintAcceleration for Wraith)
P = {"speed": 173.5, "lowSpeed": 120.0, "acceleration": 450.0, "lowAcceleration": 2500.0,
     "sprintAcceleration": 100.0, "deceleration": 1250.0, "sprintDeceleration": 1250.0}


def wish_vec(yaw_deg, fwd, sd):
    y = math.radians(yaw_deg)
    fx, fy = math.cos(y), math.sin(y)
    rx, ry = math.sin(y), -math.cos(y)
    return fwd * fx + sd * rx, fwd * fy + sd * ry


def native_step(v, yaw, fwd, sd, sprint, maxspeed, msc, dt):
    """One ground command of WalkMove (N2-G §2), horizontal only."""
    f, s = fwd, sd
    if sprint:
        f, s = f * 1.25, s * 1.25
    m = math.hypot(f, s)
    if m > 1:
        f, s = f / m, s / m
    elif m > 0:
        k = (2 - m) * m / m
        f, s = f * k, s * k
    wx, wy = wish_vec(yaw, f, s)
    wl = math.hypot(wx, wy)
    wishspeed = min(wl, 1.0) * maxspeed
    if wl > 0:
        wx, wy = wx / wl, wy / wl
    h = math.hypot(*v)
    # Ground_GetAccel (pre-move speed)
    if h > msc * P["speed"] - 1:
        a = P["sprintAcceleration"] * msc
    elif h < msc * P["lowSpeed"]:
        a = P["lowAcceleration"] * msc
    else:
        a = P["acceleration"] * msc
    # Friction
    ux, uy = v
    keep = (0.0, 0.0)
    proj = wx * ux + wy * uy
    if wl > 0 and proj > 0 and h > 0:
        ratio = min(1.0, proj * wishspeed / (h * h))
        keep = (wx * ratio * proj, wy * ratio * proj)
    rx, ry = ux - keep[0], uy - keep[1]
    rs = math.hypot(rx, ry)
    D = P["sprintDeceleration"] if h > msc * P["speed"] else P["deceleration"]
    rs2 = max(0.0, rs - D * dt)
    if rs > 0:
        rx, ry = rx * rs2 / rs, ry * rs2 / rs
    vx, vy = keep[0] + rx, keep[1] + ry
    # Accelerate
    if wl > 0:
        old = math.hypot(vx, vy)
        add = wishspeed - (vx * wx + vy * wy)
        if add > 0:
            acc = min(add, a * dt)
            vx, vy = vx + wx * acc, vy + wy * acc
            cap = max(old, wishspeed)
            n = math.hypot(vx, vy)
            if n > cap:
                vx, vy = vx * cap / n, vy * cap / n
    return vx, vy


def instant_step(v, yaw, fwd, sd, sprint, maxspeed, msc, dt):
    """HSD replay motor ground rule: speed law on |v|, direction = wishdir."""
    s = math.hypot(*v)
    wx, wy = wish_vec(yaw, fwd, sd)
    wl = math.hypot(wx, wy)
    if wl == 0:
        s = max(0.0, s - P["deceleration"] * dt)
        d = (v[0] / math.hypot(*v), v[1] / math.hypot(*v)) if math.hypot(*v) > 0 else (0.0, 0.0)
        return d[0] * s, d[1] * s
    cap = maxspeed
    if s < cap:
        if s < P["lowSpeed"] * msc:
            a = P["lowAcceleration"] * msc
        elif not sprint or s + P["sprintAcceleration"] * msc * dt < P["speed"] * msc:
            a = P["acceleration"] * msc
        else:
            a = P["sprintAcceleration"] * msc
        s = min(cap, s + a * dt)
    else:
        s = max(cap, s - P["deceleration"] * dt)
    return wx / wl * s, wy / wl * s


def vector_step(v, yaw, fwd, sd, sprint, maxspeed, msc, dt):
    """HSD Reference ground rule (R5MotorV2.GroundVectorRedirect, standing, not ducked)."""
    s = math.hypot(*v)
    wx, wy = wish_vec(yaw, fwd, sd)
    wl = math.hypot(wx, wy)
    if wl == 0:
        return instant_step(v, yaw, fwd, sd, sprint, maxspeed, msc, dt)
    wx, wy = wx / wl, wy / wl
    D = P["deceleration"]
    along = max(0.0, v[0] * wx + v[1] * wy)
    cx, cy = v[0] - along * wx, v[1] - along * wy
    cl = math.hypot(cx, cy)
    k = max(0.0, cl - D * dt) / cl if cl > 1e-12 else 0.0
    vx, vy = along * wx + cx * k, along * wy + cy * k
    if s < P["lowSpeed"] * msc:
        a = P["lowAcceleration"] * msc
    elif not sprint or s + P["sprintAcceleration"] * msc * dt < P["speed"] * msc:
        a = P["acceleration"] * msc
    else:
        a = P["sprintAcceleration"] * msc
    cap = maxspeed
    add = min(a * dt, cap - s)
    if add > 0:
        vx, vy = vx + wx * add, vy + wy * add
    n, lim = math.hypot(vx, vy), max(cap, s - D * dt)
    if n > lim:
        vx, vy = vx * lim / n, vy * lim / n
    return vx, vy


def key_state(b):
    return b & ga.MOVE_BITS


def analyse_trial(recs):
    ground = [r for r in recs if r["ground"] == 1 and r["dt"] is not None and r["yaw"] is not None]
    change = None
    for prev, cur in zip(ground, ground[1:]):
        if key_state(prev["b"]) and key_state(cur["b"]) and key_state(cur["b"]) != key_state(prev["b"]):
            change = ground.index(cur)
            break
    if change is None:
        return None
    start = ground[change]
    v_nat = v_ins = v_vec = (ground[change - 1]["vx1"], ground[change - 1]["vy1"])
    rows, t = [], 0.0
    for r in ground[change:]:
        if t > WINDOW_S:
            break
        args = (r["yaw"], r["fwd"], r["sd"], bool(r["spr"]), r["ms"], r["msc"], r["dt"])
        v_nat = native_step(v_nat, *args)
        v_ins = instant_step(v_ins, *args)
        v_vec = vector_step(v_vec, *args)
        meas = (r["vx1"], r["vy1"])
        t += r["dt"]
        rows.append({"t": round(t, 4), "meas": meas, "native": v_nat, "instant": v_ins, "vector": v_vec,
                     "err_native": math.dist(meas, v_nat), "err_instant": math.dist(meas, v_ins),
                     "err_vector": math.dist(meas, v_vec),
                     "heading_meas": math.degrees(math.atan2(meas[1], meas[0])), "speed_meas": math.hypot(*meas)})
        # restart each model from the measurement: one-command errors, no drift
        v_nat = v_ins = v_vec = meas
    return {"start_cmd": start["cmd"], "rows": rows,
            "rms_native": math.sqrt(sum(x["err_native"] ** 2 for x in rows) / len(rows)),
            "rms_instant": math.sqrt(sum(x["err_instant"] ** 2 for x in rows) / len(rows)),
            "rms_vector": math.sqrt(sum(x["err_vector"] ** 2 for x in rows) / len(rows)),
            "max_native": max(x["err_native"] for x in rows), "max_instant": max(x["err_instant"] for x in rows),
            "max_vector": max(x["err_vector"] for x in rows)}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    runner, mt, frames_by_run, frames_by_seq, n_issues = ga.load_session(a.session)
    out = {"session": os.path.basename(os.path.normpath(a.session)), "trials": []}
    for t in runner.get("trials", []):
        name, run = t.get("schedule"), f"r{t.get('run')}"
        if name not in SCHEDULES or t.get("warmup") or not t.get("ok"):
            continue
        cmds, frames = mt.get(run, []), frames_by_run.get(run, [])
        if not cmds or not frames:
            continue
        recs, _ = ga.build_trial(t, cmds, frames, frames_by_seq)
        res = analyse_trial(recs) if recs else None
        if res is None:
            print(f"{name} run {run}: no key change found")
            continue
        res.update({"schedule": name, "run": run})
        out["trials"].append(res)
        first = res["rows"][:6]
        print(f"{name} run {run}: rms native {res['rms_native']:.3f}  instant {res['rms_instant']:.3f}  "
              f"vector {res['rms_vector']:.3f} u/s (max {res['max_native']:.2f} / {res['max_instant']:.2f} / "
              f"{res['max_vector']:.2f}); heading "
              + " ".join(f"{x['heading_meas']:.1f}" for x in first)
              + "  speed " + " ".join(f"{x['speed_meas']:.1f}" for x in first))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
