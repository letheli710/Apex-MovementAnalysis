#!/usr/bin/env python3
"""M9 track R ③ D1 re-checks: uphill slide, superglide after a slide (boost state vs approach speed), pad double-jump lurch
clamp vs a ground-jump control, reverse lurch chains / OG Ras / momentum shift / lurch combos (R5Flowstate S21 client + S3 dedi +
SDK, local offline).

  py -3 d1_analysis.py <session> [<session> ...] [--json results.json] [--params params.json] > analysis_output.txt

stdlib only, no local paths. Loaders: ../../m6/a2_climb/a2_load.py (slope, superglide, pad) and the M6-A1 lurch walk
(../../m6/a1_lurch/a1_lurch_analysis.py: per airborne usercmd v' = v + AirAccelerate, a new move-key edge adds the lurch D;
D_obs = |v_post - (v_pre + AirAccelerate)|, t from the latest ground jump).
- uphill: per grounded sliding usercmd, the speed change beyond the M2 flat slide law s' = (s - 100 dt) 0.7^dt against the
  local slope (atan(-dz/dxy) of the usercmd's own step; negative = uphill); time series of |v| every 0.1 s;
- superglide: the traversal is the client MOVE-TRACE gap; exit = the first usercmd after it: superglide if |v_h| > 380 and
  vz > 200 (M8 classes);
- pad lurch: |dv_h| on the usercmd of the moveright press after the double jump, and dv minus AirAccelerate at 1.0 dt and at
  0.8 dt (the pad flight runs in slow-mo, M4/M8);
- chains: the heading change of v_h from the jump to 0.3 s after the last edge, the speed ratio, D_obs per edge.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a1_lurch")))
import a2_load as L  # noqa: E402
import a1_lurch_analysis as A1  # noqa: E402

FLOOR = 294.92
IN_JUMP, IN_DUCK, IN_MOVERIGHT = 0x2, 0x4, 0x400


def r(x, n=3):
    return None if x is None else round(x, n)


def dt_of(c):
    return c["dt"] if c.get("dt") else 1.0 / 120.0


def hs(c, post=True):
    return math.hypot(c["pvx"], c["pvy"]) if post else math.hypot(c["vx"], c["vy"])


def angd(a, b):
    d = (a - b + 180.0) % 360.0 - 180.0
    return d


# ----------------------------------------------------------------------------- uphill slide
def uphill_row(T):
    cs = T["cmds"]
    R = {"run": T["run"], "schedule": T["schedule"]}
    tt, acc = [], 0.0
    for c in cs:
        tt.append(acc)
        acc += dt_of(c)
    i_slide = next((q for q in range(len(cs)) if cs[q]["slide"]), None)
    R["slide_start"] = {"t": r(tt[i_slide], 3), "z": r(cs[i_slide]["oz"], 1), "pre_h": r(hs(cs[i_slide], False), 2),
                        "post_h": r(hs(cs[i_slide]), 2)} if i_slide is not None else None
    pts = []
    for i, c in enumerate(cs):
        dx, dy, dz = c["pox"] - c["ox"], c["poy"] - c["oy"], c["poz"] - c["oz"]
        dxy = math.hypot(dx, dy)
        if not c["ground"] or dxy < 0.5:
            continue
        slope = math.degrees(math.atan2(-dz, dxy))
        s0 = math.sqrt(c["vx"] ** 2 + c["vy"] ** 2 + c["vz"] ** 2)
        s1 = math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2)
        pts.append({"t": tt[i], "slope": slope, "slide": c["slide"], "s0": s0, "s1": s1, "dt": dt_of(c), "h0": hs(c, False), "h1": hs(c),
                    "vz": c["pvz"]})
    # series every 0.1 s from the slide start (or the start)
    i0 = i_slide if i_slide is not None else 0
    ser = []
    for k in range(0, 40):
        tq = tt[i0] + 0.1 * k
        q = next((j for j in range(i0, len(cs)) if tt[j] >= tq), None)
        if q is None:
            break
        c = cs[q]
        ser.append([r(tt[q] - tt[i0], 2), r(c["poz"] - 692.8, 1), c["ground"], c["slide"], r(hs(c), 2), r(c["pvz"], 2)])
    R["series"] = ser
    sl = [p for p in pts if p["slide"] and p["slope"] < -10]
    R["slide_uphill_cmds"] = len(sl)
    R["extra"] = [[r(p["slope"], 2), r(p["s0"], 2), r((p["s1"] - (p["s0"] - 100 * p["dt"]) * 0.7 ** p["dt"]) / p["dt"], 2), r(p["vz"], 2)]
                  for p in sl]
    R["slide_end_t"] = next((r(tt[q] - tt[i0], 3) for q in range(i0 + 1, len(cs)) if i_slide is not None and not cs[q]["slide"]), None)
    R["max_h"] = r(max((p["h1"] for p in pts), default=0), 2)
    R["run_speed_slope"] = [r(p["s1"], 2) for p in pts if not p["slide"] and p["slope"] < -10][-5:]
    return R


def lin_fit(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    rms = math.sqrt(sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / n)
    return a, b, rms


# ----------------------------------------------------------------------------- superglide
def sg_row(T):
    cs = T["cmds"]
    R = {"run": T["run"], "schedule": T["schedule"]}
    js = [i for i in range(1, len(cs)) if cs[i]["buttons"] & IN_JUMP and not cs[i - 1]["buttons"] & IN_JUMP]
    if not js:
        R["class"] = "no_jump"
        return R
    j = js[0]
    R["approach"] = {"pre_h": r(hs(cs[j], False), 2), "post_h": r(hs(cs[j]), 2), "slide": cs[j]["slide"]}
    gaps = [i for i in range(j + 1, len(cs)) if cs[i]["cmd"] - cs[i - 1]["cmd"] != 1]
    if not gaps:
        R["class"] = "no_traversal"
        return R
    g = gaps[0]
    first = cs[g]
    R["exit"] = {"h": r(hs(first), 3), "vz": r(first["pvz"], 2), "dir": r(math.degrees(math.atan2(first["pvy"], first["pvx"])), 2),
                 "yaw": r(first.get("yaw"), 2)}
    if hs(first) > 380 and first["pvz"] > 200:
        R["class"] = "superglide"
    elif first["pvz"] > 200:
        R["class"] = "mantle_jump"
    elif first["ground"] == 0:
        R["class"] = "cut_no_jump"
    else:
        R["class"] = "mantle_only"
    R["exit_dir_rel_yaw"] = r(angd(R["exit"]["dir"], first["yaw"]), 2) if first.get("yaw") is not None else None
    return R


# ----------------------------------------------------------------------------- pad lurch / generic press dv
def press_row(T, key_bit=IN_MOVERIGHT, slowmo=False):
    cs = T["cmds"]
    R = {"run": T["run"], "schedule": T["schedule"]}
    ps = [i for i in range(1, len(cs)) if cs[i]["buttons"] & key_bit and not cs[i - 1]["buttons"] & key_bit and cs[i]["ground"] == 0]
    if not ps:
        return R
    i = ps[0]
    c = cs[i]
    dv = (c["pvx"] - c["vx"], c["pvy"] - c["vy"])
    R["dv_abs"] = r(math.hypot(*dv), 3)
    R["v_h_pre"] = r(hs(c, False), 2)
    yaw = c.get("yaw")
    if yaw is not None:
        for tag, scale in (("aa1", 1.0), ("aa08", 0.8)):
            cc = dict(c)
            cc["dt"] = dt_of(c) * scale
            cc["movescale"] = c["msc"]
            vp = A1.air_accel(cc, (c["vx"], c["vy"]), yaw)
            R["D_" + tag] = r(math.hypot(c["pvx"] - vp[0], c["pvy"] - vp[1]), 3)
    return R


# ----------------------------------------------------------------------------- chains
def chain_row(t):
    w = A1.walk(t)
    cs = t["cmds"]
    R = {"run": t["run"], "schedule": t["schedule"]}
    if not w["jumps"]:
        R["jumps"] = 0
        return R
    j0 = w["jumps"][0]
    h0 = math.degrees(math.atan2(cs[j0]["pvy"], cs[j0]["pvx"]))
    s0 = hs(cs[j0])
    pr = [a for a in w["air"] if a["new"]]
    R["entry_h"] = r(s0, 2)
    R["edges"] = [{"t": r(a["t"], 4), "keys": a.get("keys"), "D_obs": r(a.get("D_obs"), 3), "head1": r(angd(a["head1"], h0), 2),
                   "s1": r(a["s1"], 2)} for a in pr]
    if pr:
        tl = pr[-1]["t"]
        late = [a for a in w["air"] if a["t"] >= tl + 0.3 - 1e-6]
        a = late[0] if late else w["air"][-1]
        R["heading_change"] = r(angd(a["head1"], h0), 2)
        R["speed_ratio"] = r(a["s1"] / s0, 4) if s0 else None
        R["yaw_change"] = r(angd(a["yaw"], cs[j0].get("yaw") or a["yaw"]), 2)
        R["max_abs_heading"] = r(max(abs(angd(x["head1"], h0)) for x in w["air"] if x["t"] <= tl + 0.3), 2)
    # landing in a slide (OG Ras: crouch held)
    land = next((i for i in range(j0 + 2, len(cs)) if cs[i]["ground"]), None)
    if land is not None:
        R["land_slide"] = cs[land]["slide"] or (land + 1 < len(cs) and cs[land + 1]["slide"])
        R["land_h"] = r(hs(cs[land]), 2)
    return R


def pad_chain_row(T):
    """Chain after a pad launch (no ground-jump anchor for the A1 walk): heading of v_h from the launch usercmd (first |v| jump
    > 300) to 0.3 s after the last move-key edge in the air; |dv_h| per edge."""
    cs = [c for c in T["cmds"] if c.get("t") is not None]
    R = {"run": T["run"], "schedule": T["schedule"]}
    la = next((c for c in cs if math.sqrt(c["pvx"] ** 2 + c["pvy"] ** 2 + c["pvz"] ** 2) -
               math.sqrt(c["vx"] ** 2 + c["vy"] ** 2 + c["vz"] ** 2) > 300), None)
    if not la:
        return R
    k = cs.index(la)
    h0 = math.degrees(math.atan2(la["pvy"], la["pvx"]))
    mask = 0x8 | 0x10 | 0x200 | 0x400
    ed = [c for i, c in enumerate(cs[k + 1:], k + 1) if not c["ground"] and (c["buttons"] & mask) & ~(cs[i - 1]["buttons"] & mask)]
    R["entry_h"] = r(hs(la), 2)
    R["edges"] = [{"t": r(c["t"] - la["t"], 4), "dv": r(math.hypot(c["pvx"] - c["vx"], c["pvy"] - c["vy"]), 3),
                   "head1": r(angd(math.degrees(math.atan2(c["pvy"], c["pvx"])), h0), 2)} for c in ed]
    if ed:
        c2 = next((c for c in cs if c["t"] >= ed[-1]["t"] + 0.3 - 1e-6), cs[-1])
        R["heading_change"] = r(angd(math.degrees(math.atan2(c2["pvy"], c2["pvx"])), h0), 2)
        R["speed_ratio"] = r(hs(c2) / hs(la), 4)
    return R


def stats(v):
    return L.stats(v)


def fmt(s, nd=3):
    return L.fmt(s, nd)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--params")
    a = ap.parse_args(argv)
    metas, up, sg, pad, ch = [], [], [], [], []
    for folder in a.sessions:
        D = L.load(folder)
        excl = [(t["run"], t["schedule"], t["why"]) for t in D["runner"]["trials"] if not t["ok"] and not t.get("warmup")]
        metas.append({"session": D["folder"], "legend": D["runner"].get("legend"), "both_cvars": D["runner"].get("both_cvars"),
                      "geometry_wall_z": D["runner"].get("geometry_wall_z"), "scored": len(D["trials"]), "excluded": excl,
                      "fps": [r(min(t["fps"] for t in D["trials"]), 2), r(max(t["fps"] for t in D["trials"]), 2)] if D["trials"] else None})
        for T in D["trials"]:
            s = T["schedule"]
            if s.startswith("m9d_up"):
                up.append(uphill_row(T))
            elif s.startswith("m9d_sg"):
                sg.append(sg_row(T))
            elif s in ("m8_pad_dj_lurch", "m8_lurch_spr_d_k2", "m8_lurch_sj_d_k2"):
                pad.append(press_row(T))
            elif s.startswith("m8_pad_chain"):
                ch.append(pad_chain_row(T))
        if any(T["schedule"].startswith(("m9d_chain", "m9d_ras", "m9d_mshift", "m9d_r1", "m9d_r2")) for T in D["trials"]):
            S1 = A1.load_session(folder)
            for t in S1["trials"]:
                if t["schedule"].startswith(("m9d_chain", "m9d_ras", "m9d_mshift", "m9d_r1", "m9d_r2")):
                    ch.append(chain_row(t))
    print("M9 R D1 re-checks (R5Flowstate S21 client + S3 dedi + SDK, local offline)")
    print("=" * 100)
    print("\n1. Sessions")
    for m in metas:
        print("  %s legend=%s cvars=%s wall_z=%s scored=%d fps=%s excluded=%s" % (m["session"], m["legend"], m["both_cvars"],
              m["geometry_wall_z"], m["scored"], m["fps"], m["excluded"] or "none"))
    out = {"sessions": metas}
    # uphill
    if up:
        print("\n2. Uphill slide / run (hillside 29-41 deg; z relative to the start 692.8)")
        allx = []
        for w in up:
            print("  r%s %s slide_start=%s slide_end_after=%s uphill sliding cmds=%d max_h=%s run speed on slope=%s" % (
                w["run"], w["schedule"], w["slide_start"], w["slide_end_t"], w["slide_uphill_cmds"], w["max_h"], w["run_speed_slope"]))
            print("     series [t, dz, ground, slide, |v_h|, vz]: %s" % w["series"][:16])
            allx += w["extra"]
        if allx:
            f = lin_fit([math.sin(math.radians(-e[0])) for e in allx], [e[2] for e in allx])
            print("  extra accel beyond the flat slide law on uphill sliding cmds: n=%d mean %s; fit extra = a + b*sin(uphill angle): %s"
                  % (len(allx), r(sum(e[2] for e in allx) / len(allx), 2), [r(x, 3) for x in f] if f else None))
            out["uphill_fit"] = {"n": len(allx), "a_b_rms": [r(x, 3) for x in f] if f else None,
                                 "slope_range": [r(min(-e[0] for e in allx), 1), r(max(-e[0] for e in allx), 1)]}
        out["uphill"] = up
    # superglide
    if sg:
        print("\n3. Superglide after different approaches (native, mantle_boost_enabled=0; H from the runner)")
        G = {}
        for w in sg:
            G.setdefault(w["schedule"], []).append(w)
        out["sg"] = {}
        for k, ws in sorted(G.items()):
            cl = {}
            for w in ws:
                cl[w["class"]] = cl.get(w["class"], 0) + 1
            eh = stats([w.get("exit", {}).get("h") for w in ws])
            print("  %-18s n=%d classes=%s exit |v_h| %s approach pre_h %s exit dir rel yaw %s" % (k, len(ws), cl, fmt(eh, 3),
                  fmt(stats([w.get("approach", {}).get("pre_h") for w in ws]), 2), [w.get("exit_dir_rel_yaw") for w in ws]))
            out["sg"][k] = {"n": len(ws), "classes": cl, "exit_h": eh, "trials": ws}
    # pad lurch
    if pad:
        print("\n4. Lurch press after the pad double jump vs ground-jump controls")
        G = {}
        for w in pad:
            G.setdefault(w["schedule"], []).append(w)
        out["pad"] = {}
        for k, ws in sorted(G.items()):
            res = {f: stats([w.get(f) for w in ws]) for f in ("dv_abs", "D_aa1", "D_aa08", "v_h_pre")}
            print("  %-20s n=%d |dv| %s  D(-AA dt) %s  D(-AA 0.8dt) %s  v_h pre %s" % (k, len(ws), fmt(res["dv_abs"]), fmt(res["D_aa1"]),
                  fmt(res["D_aa08"]), fmt(res["v_h_pre"], 2)))
            out["pad"][k] = res
    # chains
    if ch:
        print("\n5. Lurch chains / OG Ras / momentum shift / combos (heading of v_h relative to the jump, 0.3 s after the last edge)")
        G = {}
        for w in ch:
            G.setdefault(w["schedule"], []).append(w)
        out["chains"] = {}
        for k, ws in sorted(G.items()):
            res = {f: stats([w.get(f) for w in ws]) for f in ("entry_h", "heading_change", "max_abs_heading", "speed_ratio", "yaw_change")}
            ls = sum(1 for w in ws if w.get("land_slide"))
            print("  %-20s n=%d entry %s heading %s max|heading| %s speed x%s yaw %s land in slide %d" % (k, len(ws), fmt(res["entry_h"], 1),
                  fmt(res["heading_change"], 1), fmt(res["max_abs_heading"], 1), fmt(res["speed_ratio"], 3), fmt(res["yaw_change"], 1), ls))
            e0 = next((w["edges"] for w in ws if w.get("edges")), [])
            print("      edges (first trial): %s" % [(e.get("keys"), e["t"], e.get("D_obs", e.get("dv")), e["head1"]) for e in e0])
            out["chains"][k] = {"n": len(ws), **res, "land_slide": ls, "edges_first": e0}
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1)
    if a.params:
        with open(a.params, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(build_params(out), fh, indent=1)
    return 0


def build_params(out):
    P = []
    if out.get("uphill_fit"):
        P.append({"name": "uphill_slide_extra_accel", "value": out["uphill_fit"], "class": "fit", "n": out["uphill_fit"]["n"],
                  "note": "extra = a + b*sin(uphill angle) beyond the M2 flat slide law, grounded sliding usercmds on the 29-41 deg hillside"})
    for k, g in (out.get("sg") or {}).items():
        P.append({"name": "sg_" + k, "value": g["classes"], "class": "meas", "n": g["n"],
                  "exit_h_mean": r(g["exit_h"].get("mean"), 3) if g["exit_h"].get("n") else None})
    for k, g in (out.get("pad") or {}).items():
        P.append({"name": "lurch_" + k, "value": {f: r(g[f].get("mean"), 3) for f in g if g[f].get("n")}, "class": "meas", "n": g["dv_abs"]["n"]})
    for k, g in (out.get("chains") or {}).items():
        P.append({"name": k, "value": {"heading_change": r(g["heading_change"].get("mean"), 2) if g["heading_change"].get("n") else None,
                                       "speed_ratio": r(g["speed_ratio"].get("mean"), 4) if g["speed_ratio"].get("n") else None,
                                       "entry_h": r(g["entry_h"].get("mean"), 1) if g["entry_h"].get("n") else None},
                  "class": "meas", "n": g["n"]})
    return {"build": "R5Flowstate S21 client + S3 dedicated server + SDK, local offline, 120 fps", "params": P}


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
