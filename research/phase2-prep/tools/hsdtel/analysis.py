"""Event detection, model fitting and run comparison.

Every fit returns plain dicts with the model name, parameters, the number of
samples used and a goodness value, so a caller can tell a good fit from a
forced one. Models are candidate *shapes*; picking the best-scoring shape is
evidence for it, not proof of the game's code.
"""
import math
from collections import OrderedDict

from .derive import streams, jump_press


# ---------------------------------------------------------------- utilities
def _linreg(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return slope, my - slope * mx


def r2(obs, pred):
    if len(obs) < 2:
        return float("nan")
    m = sum(obs) / len(obs)
    sst = sum((o - m) ** 2 for o in obs)
    sse = sum((o - p) ** 2 for o, p in zip(obs, pred))
    return 1.0 - sse / sst if sst > 0 else float("nan")


def _median(v):
    s = sorted(v)
    n = len(s)
    if not n:
        return float("nan")
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def time_series(srows, source):
    """(t, row) pairs with a usable time axis.
    HSD: observed Time(). MT: cumulative drv_dt_est, falling back to the median
    estimate for slow commands (the trace has no frametime)."""
    out = []
    if source == "HSD":
        for r in srows:
            t = r.get("t")
            if isinstance(t, float) and math.isfinite(t) and "drv_spd2d" in r:
                out.append((t, r))
        return out
    dts = [r["drv_dt_est"] for r in srows if r.get("drv_dt_est") and not r.get("replay")]
    fallback = _median(dts) if dts else 1.0 / 144.0
    t = 0.0
    for r in srows:
        if r.get("replay") or "drv_spd2d_post" not in r:
            continue
        t += r.get("drv_dt_est") or fallback
        out.append((t, r))
    return out


def speed_of(r):
    return r["drv_spd2d_post"] if "drv_spd2d_post" in r else r["drv_spd2d"]


def ground_of(r):
    if r["source"] == "MT":
        return r.get("ground")
    return r.get("ground")


# ---------------------------------------------------------------- events
def events(rows):
    """Edge events detected from ground/slide flags of every sample stream, plus
    jump presses (MT) and the mod's own server events (passed through)."""
    out = []
    for key, srows in streams(rows).items():
        source, side, fam, ent = key
        if fam not in ("cmd", "frame"):
            if source == "HSD" and fam == "evt":
                for r in srows:
                    out.append(_ev(r, "SV_" + str(r.get("evt")), source, side))
            continue
        prev = None
        for r in srows:
            if r.get("replay"):
                continue
            g, s = r.get("ground"), r.get("slide")
            if prev is not None:
                pg, ps = prev.get("ground"), prev.get("slide")
                if pg == 1 and g == 0:
                    out.append(_ev(r, "TAKEOFF", source, side, prev))
                elif pg == 0 and g == 1:
                    out.append(_ev(r, "LAND", source, side, prev))
                if ps == 0 and s == 1:
                    out.append(_ev(r, "SLIDE_START", source, side, prev))
                elif ps == 1 and s == 0:
                    out.append(_ev(r, "SLIDE_END", source, side, prev))
            if source == "MT" and jump_press(r):
                e = _ev(r, "JUMP_PRESS", source, side)
                e["grounded_pre"] = r.get("ground")
                e["dvz"] = (r.get("pvz") or 0.0) - (r.get("vz") or 0.0)
                out.append(e)
            prev = r
    out.sort(key=lambda e: (e["file_rank"], e["line_no"]))
    return out


def _ev(r, kind, source, side, prev=None):
    return OrderedDict([
        ("event", kind), ("source", source), ("side", side), ("drv_run", r.get("drv_run")),
        ("file", r.get("file")), ("line_no", r.get("line_no")), ("file_rank", r.get("_rank", 0)),
        ("t", r.get("t")), ("wall", r.get("wall")), ("cmd", r.get("cmd")),
        ("spd2d", r.get("drv_spd2d")), ("spd2d_prev", prev.get("drv_spd2d") if prev else None),
        ("vz", r.get("vz")),
    ])


def hops(rows, max_ground_time=0.5):
    """Land -> next takeoff pairs on HSD client frames (Time() axis)."""
    res = []
    for key, srows in streams(rows).items():
        if key[0] != "HSD" or key[2] != "frame":
            continue
        prev = None
        land = None
        for r in srows:
            g = r.get("ground")
            if prev is not None:
                if prev.get("ground") == 0 and g == 1:
                    land = (r, prev)
                elif prev.get("ground") == 1 and g == 0 and land is not None:
                    gt = r["t"] - land[0]["t"]
                    if gt <= max_ground_time:
                        res.append(OrderedDict([
                            ("side", key[1]), ("drv_run", r.get("drv_run")),
                            ("t_land", land[0]["t"]), ("ground_time", gt),
                            ("spd_air_before_land", land[1].get("drv_spd2d")),
                            ("spd_at_land", land[0].get("drv_spd2d")),
                            ("spd_at_takeoff", r.get("drv_spd2d")),
                            ("loss_on_ground", (land[1].get("drv_spd2d") or 0) - (r.get("drv_spd2d") or 0)),
                        ]))
                    land = None
            prev = r
    return res


# ---------------------------------------------------------------- ground fits
GOOD_R2 = 0.98  # below this a "best" shape is reported but flagged good=False
def _simulate_linear(ts, v0, a, vmax):
    return [min(vmax, v0 + a * (t - ts[0])) for t in ts]


def _simulate_first_order(ts, v0, k, vmax):
    return [vmax - (vmax - v0) * math.exp(-k * (t - ts[0])) for t in ts]


def fit_accel_phase(ts, vs):
    """Speed rising from rest toward a plateau. Candidate shapes:
    linear (v0 + a t, capped at vmax) and first-order (vmax - (vmax-v0) e^-kt)."""
    if len(ts) < 6:
        return {"ok": False, "reason": "fewer than 6 samples"}
    vmax = _median(vs[-max(3, len(vs) // 5):])
    if not vmax > 1:
        return {"ok": False, "reason": "no plateau"}
    lo, hi = 0.1 * vmax, 0.9 * vmax
    sel = [(t, v) for t, v in zip(ts, vs) if lo <= v <= hi]
    res = {"ok": True, "n": len(ts), "n_fit": len(sel), "vmax": vmax, "models": {}}
    if len(sel) >= 3:
        lr = _linreg([t for t, _ in sel], [v for _, v in sel])
        if lr:
            a = lr[0]
            pred = _simulate_linear(ts, vs[0], a, vmax)
            res["models"]["linear"] = {"a": a, "r2": r2(vs, pred)}
        sel2 = [(t, math.log(vmax - v)) for t, v in sel if vmax - v > 1e-6]
        lr2 = _linreg([t for t, _ in sel2], [y for _, y in sel2]) if len(sel2) >= 3 else None
        if lr2 and lr2[0] < 0:
            k = -lr2[0]
            pred = _simulate_first_order(ts, vs[0], k, vmax)
            res["models"]["first_order"] = {"k": k, "r2": r2(vs, pred)}
    res["best"] = max(res["models"], key=lambda m: res["models"][m]["r2"]) if res["models"] else None
    res["good"] = bool(res["best"]) and res["models"][res["best"]]["r2"] >= GOOD_R2
    return res


def _simulate_friction(ts, v0, k, stop):
    out, v = [v0], v0
    for i in range(1, len(ts)):
        dt = ts[i] - ts[i - 1]
        v = max(0.0, v - max(v, stop) * k * dt)
        out.append(v)
    return out


def fit_decel_phase(ts, vs):
    """Speed falling with no input. Candidate shapes: linear (v0 - d t) and
    Source-style friction (dv/dt = -k * max(v, stopspeed))."""
    if len(ts) < 6:
        return {"ok": False, "reason": "fewer than 6 samples"}
    v0 = vs[0]
    res = {"ok": True, "n": len(ts), "v0": v0, "models": {}}
    sel = [(t, v) for t, v in zip(ts, vs) if v > 0.05 * v0]
    lr = _linreg([t for t, _ in sel], [v for _, v in sel]) if len(sel) >= 3 else None
    if lr and lr[0] < 0:
        d = -lr[0]
        pred = [max(0.0, v0 - d * (t - ts[0])) for t in ts]
        res["models"]["linear"] = {"d": d, "r2": r2(vs, pred)}
    up = [(t, math.log(v)) for t, v in zip(ts, vs) if v > 0.5 * v0]
    lr2 = _linreg([t for t, _ in up], [y for _, y in up]) if len(up) >= 3 else None
    if lr2 and lr2[0] < 0:
        k = -lr2[0]
        best = None
        for i in range(0, 101):
            stop = v0 * i / 100.0
            pred = _simulate_friction(ts, v0, k, stop)
            sse = sum((o - p) ** 2 for o, p in zip(vs, pred))
            if best is None or sse < best[0]:
                best = (sse, stop, pred)
        res["models"]["friction"] = {"k": k, "stopspeed": best[1], "r2": r2(vs, best[2])}
    res["best"] = max(res["models"], key=lambda m: res["models"][m]["r2"]) if res["models"] else None
    res["good"] = bool(res["best"]) and res["models"][res["best"]]["r2"] >= GOOD_R2
    return res


def ground_phases(series, start_below=5.0, plateau_frac=0.98, end_below=2.0):
    """Split one trial (t, row) series into the first accel-from-rest phase and
    the following coast-down phase, using grounded, non-sliding samples only."""
    pts = [(t, speed_of(r)) for t, r in series if r.get("ground") == 1 and r.get("slide") in (0, None)]
    if len(pts) < 10:
        return None, None
    ts, vs = [p[0] for p in pts], [p[1] for p in pts]
    i0 = next((i for i in range(1, len(vs)) if vs[i - 1] <= start_below < vs[i]), None)
    if i0 is None and vs[0] < 0.1 * max(vs) and len(vs) > 1 and vs[1] > vs[0]:
        i0 = 1  # the trial was labelled after the first input command
    accel = decel = None
    if i0 is not None:
        start = i0 - 1
        peak = max(vs[start:])
        i1 = next((i for i in range(start, len(vs)) if vs[i] >= plateau_frac * peak), None)
        if i1 is not None:
            # keep a plateau tail so the vmax estimate sees it
            j = i1
            while j + 1 < len(vs) and vs[j + 1] >= plateau_frac * peak:
                j += 1
            accel = (ts[start:j + 1], vs[start:j + 1])
            k = j
            kend = next((i for i in range(k, len(vs)) if vs[i] < end_below), None)
            if kend is not None and kend - k >= 6:
                decel = (ts[k:kend + 1], vs[k:kend + 1])
    return accel, decel


def fit_ground(rows, source="HSD", side="cl", run=None):
    out = []
    for key, srows in streams(rows).items():
        if key[0] != source or key[1] != side or key[2] not in ("frame", "cmd"):
            continue
        by_run = OrderedDict()
        for r in srows:
            by_run.setdefault(r.get("drv_run"), []).append(r)
        for rid, rr in by_run.items():
            if run is not None and rid != run:
                continue
            series = time_series(rr, source)
            accel, decel = ground_phases(series)
            out.append(OrderedDict([
                ("source", source), ("side", side), ("drv_run", rid),
                ("accel", fit_accel_phase(*accel) if accel else {"ok": False, "reason": "no accel-from-rest phase"}),
                ("decel", fit_decel_phase(*decel) if decel else {"ok": False, "reason": "no coast-down phase"}),
            ]))
    return out


# ---------------------------------------------------------------- air fit
def _air_step(vx, vy, wyaw, wish_mag, dt, cap, accel, form):
    """Quake/Source-shaped AirAccelerate on the horizontal plane.
    form 'flat':   accelspeed = accel * dt            (inference from surf calibration)
    form 'source': accelspeed = accel * wish_mag * dt (Source sv_airaccelerate shape)"""
    wx, wy = math.cos(math.radians(wyaw)), math.sin(math.radians(wyaw))
    wishspeed = min(wish_mag, cap)
    cur = vx * wx + vy * wy
    add = wishspeed - cur
    if add <= 0:
        return vx, vy
    acc = accel * dt * (wish_mag if form == "source" else 1.0)
    acc = min(acc, add)
    return vx + acc * wx, vy + acc * wy


def air_samples(rows, side="cl", run=None, wish_scale=300.0):
    """Consecutive airborne HSD frame pairs with input; the input of the later
    frame is applied to the step (the mod samples held input after the move)."""
    out = []
    for key, srows in streams(rows).items():
        if key[0] != "HSD" or key[1] != side or key[2] != "frame":
            continue
        prev = None
        for r in srows:
            if run is not None and r.get("drv_run") != run:
                prev = None
                continue
            if (prev is not None and prev.get("ground") == 0 and r.get("ground") == 0
                    and r.get("drv_wish_yaw") is not None and r.get("drv_dt")):
                mag = min(1.0, math.hypot(r["ax_fwd"], r["ax_right"])) * wish_scale
                out.append((prev["vx"], prev["vy"], r["vx"], r["vy"], r["drv_wish_yaw"], mag, r["drv_dt"]))
            prev = r
    return out


def _air_rms(samples, cap, a, form):
    err = 0.0
    for vx, vy, nx, ny, wyaw, mag, dt in samples:
        px, py = _air_step(vx, vy, wyaw, mag, dt, cap, a, form)
        err += (px - nx) ** 2 + (py - ny) ** 2
    return math.sqrt(err / len(samples))


def fit_air(samples, cap_range=(5.0, 400.0), accel_range=(10.0, 20000.0)):
    """Coarse-to-fine search of (cap, accel) for both AirAccelerate forms.
    Score = RMS horizontal velocity error per step (u/s). For form 'source'
    the reported accel is per unit of wish speed (multiply by wish speed)."""
    if len(samples) < 10:
        return {"ok": False, "reason": f"only {len(samples)} airborne input samples"}
    res = {"ok": True, "n": len(samples), "forms": {}}
    res["rms_no_accel"] = math.sqrt(sum((s[2] - s[0]) ** 2 + (s[3] - s[1]) ** 2 for s in samples) / len(samples))
    for form in ("flat", "source"):
        lo_c, hi_c = cap_range
        lo_a, hi_a = accel_range if form == "flat" else (accel_range[0] / 300.0, accel_range[1] / 300.0)
        best = None
        for _ in range(4):
            cs = [lo_c + (hi_c - lo_c) * i / 24 for i in range(25)]
            # accel spans decades: search it on a log grid
            la, ha = math.log(lo_a), math.log(hi_a)
            as_ = [math.exp(la + (ha - la) * i / 24) for i in range(25)]
            for c in cs:
                for a in as_:
                    rms = _air_rms(samples, c, a, form)
                    if best is None or rms < best[0]:
                        best = (rms, c, a)
            sc, sa = (hi_c - lo_c) / 12, (ha - la) / 12
            lo_c, hi_c = max(cap_range[0] / 10, best[1] - sc), best[1] + sc
            lo_a, hi_a = math.exp(math.log(best[2]) - sa), math.exp(math.log(best[2]) + sa)
        res["forms"][form] = {"rms": best[0], "cap": best[1], "accel": best[2]}
    f, s = res["forms"]["flat"]["rms"], res["forms"]["source"]["rms"]
    # With a constant wish magnitude (keyboard) the two forms differ only by a
    # constant factor on accel, so they fit equally well: do not pick one.
    if abs(f - s) <= 0.01 * max(f, s, 1e-9):
        res["best"] = "indistinguishable"
        res["note"] = "forms fit equally well; distinguishing them needs varying wish magnitude (analog input)"
    else:
        res["best"] = "flat" if f < s else "source"
    return res


# ---------------------------------------------------------------- vertical
def fit_vertical(rows, side="cl"):
    """Gravity from airborne vz slope on HSD frames, and vz at each takeoff."""
    out = []
    for key, srows in streams(rows).items():
        if key[0] != "HSD" or key[1] != side or key[2] != "frame":
            continue
        segs, cur = [], []
        for r in srows:
            if r.get("ground") == 0 and isinstance(r.get("t"), float):
                cur.append(r)
            else:
                if len(cur) >= 5:
                    segs.append(cur)
                cur = []
        if len(cur) >= 5:
            segs.append(cur)
        gs, takeoffs = [], []
        for s in segs:
            lr = _linreg([r["t"] for r in s], [r["vz"] for r in s])
            if lr:
                gs.append(-lr[0])
            takeoffs.append(s[0]["vz"])
        out.append({"side": side, "segments": len(segs), "gravity_median": _median(gs) if gs else None,
                    "takeoff_vz_median": _median(takeoffs) if takeoffs else None})
    return out


# ---------------------------------------------------------------- summaries
def run_summary(rows):
    """One metrics row per (source, side, drv_run) for frame/cmd streams."""
    out = []
    for key, srows in streams(rows).items():
        source, side, fam, _ent = key
        if fam not in ("frame", "cmd"):
            continue
        by_run = OrderedDict()
        for r in srows:
            if not r.get("replay"):
                by_run.setdefault(r.get("drv_run"), []).append(r)
        for rid, rr in by_run.items():
            series = time_series(rr, source)
            if not series:
                continue
            spd = [speed_of(r) for _, r in series]
            air = sum(1 for _, r in series if r.get("ground") == 0)
            takeoffs = sum(1 for i in range(1, len(rr)) if rr[i - 1].get("ground") == 1 and rr[i].get("ground") == 0)
            accel, decel = ground_phases(series)
            fa = fit_accel_phase(*accel) if accel else {}
            fd = fit_decel_phase(*decel) if decel else {}
            row = OrderedDict([
                ("source", source), ("side", side), ("drv_run", rid), ("samples", len(series)),
                ("duration_s", series[-1][0] - series[0][0]), ("max_spd2d", max(spd)),
                ("mean_spd2d", sum(spd) / len(spd)), ("air_fraction", air / len(series)), ("takeoffs", takeoffs),
                ("accel_best", fa.get("best")), ("accel_good", fa.get("good")), ("accel_vmax", fa.get("vmax")),
                ("accel_linear_a", fa.get("models", {}).get("linear", {}).get("a")),
                ("accel_linear_r2", fa.get("models", {}).get("linear", {}).get("r2")),
                ("accel_first_order_k", fa.get("models", {}).get("first_order", {}).get("k")),
                ("accel_first_order_r2", fa.get("models", {}).get("first_order", {}).get("r2")),
                ("decel_best", fd.get("best")), ("decel_good", fd.get("good")),
                ("decel_linear_d", fd.get("models", {}).get("linear", {}).get("d")),
                ("decel_linear_r2", fd.get("models", {}).get("linear", {}).get("r2")),
                ("decel_friction_k", fd.get("models", {}).get("friction", {}).get("k")),
                ("decel_friction_stop", fd.get("models", {}).get("friction", {}).get("stopspeed")),
                ("decel_friction_r2", fd.get("models", {}).get("friction", {}).get("r2")),
            ])
            out.append(row)
    return out


def compare(summary_rows, baseline, metrics=None):
    """Per-metric deltas of every run against the baseline run id (same source/side)."""
    metrics = metrics or ["max_spd2d", "mean_spd2d", "air_fraction", "takeoffs", "accel_vmax",
                          "accel_linear_a", "accel_first_order_k", "decel_linear_d", "decel_friction_k"]
    out = []
    bases = {(r["source"], r["side"]): r for r in summary_rows if r["drv_run"] == baseline}
    for r in summary_rows:
        b = bases.get((r["source"], r["side"]))
        if b is None or r is b:
            continue
        for m in metrics:
            x, y = b.get(m), r.get(m)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                out.append(OrderedDict([
                    ("source", r["source"]), ("side", r["side"]), ("baseline", baseline), ("run", r["drv_run"]),
                    ("metric", m), ("baseline_value", x), ("run_value", y), ("delta", y - x),
                    ("pct", (y - x) / x * 100.0 if x else None),
                ]))
    return out


# ---------------------------------------------------------------- E0 census
def census(rows):
    """One row per settings key: the latest value seen from each reader.
      cl_classvar  bridge_classvar_get on the client (live class-var block)
      cl_setting   HSD client dump (GetPlayerSettingFloat/String on the local player)
      sv_setting   HSD server dump (GetPlayerSettingFloat/Int/String)
    'differs' compares the numeric readings that exist (tolerance 1e-4 relative)."""
    table = OrderedDict()
    for r in sorted(rows, key=lambda x: (x.get("_rank", 0), x.get("line_no", 0))):
        if r.get("kind") not in ("classvar", "setting"):
            continue
        key = r.get("key")
        if not key:
            continue
        col = "cl_classvar" if r["source"] == "CV" else f"{r.get('side')}_setting"
        t = table.setdefault(key, OrderedDict([("key", key)]))
        t[col] = r.get("value")
        t[col + "_type"] = r.get("vtype")
    for t in table.values():
        nums = []
        for col in ("cl_classvar", "cl_setting", "sv_setting"):
            v = t.get(col)
            if v in (None, "-"):
                continue
            text = str(v).split()[0].strip('"').lower()
            if text in ("true", "false"):
                nums.append(1.0 if text == "true" else 0.0)
                continue
            try:
                nums.append(float(text))
            except ValueError:
                pass
        t["readers"] = sum(1 for col in ("cl_classvar", "cl_setting", "sv_setting")
                           if t.get(col) not in (None, "-"))
        t["differs"] = int(len(nums) > 1 and (max(nums) - min(nums)) > 1e-4 * max(1.0, max(abs(x) for x in nums)))
    return list(table.values())


# ---------------------------------------------------------------- slides
def slides(rows):
    """One row per contiguous slide (slide flag 1) in every frame/cmd stream.
    boost = peak speed in the slide minus the speed on the sample before it."""
    out = []
    for key, srows in streams(rows).items():
        source, side, fam, _ent = key
        if fam not in ("frame", "cmd"):
            continue
        series = time_series([r for r in srows if not r.get("replay")], source)
        cur, before = None, None
        for idx, (t, r) in enumerate(series):
            sl = r.get("slide")
            if sl == 1 and cur is None:
                cur = {"t": [t], "v": [speed_of(r)], "run": r.get("drv_run")}
                before = speed_of(series[idx - 1][1]) if idx else None
            elif sl == 1:
                cur["t"].append(t)
                cur["v"].append(speed_of(r))
            elif cur is not None:
                out.append(_slide_row(source, side, cur, before))
                cur = None
        if cur is not None:
            out.append(_slide_row(source, side, cur, before))
    return out


def _slide_row(source, side, cur, before):
    ts, vs = cur["t"], cur["v"]
    dur = ts[-1] - ts[0]
    lr = _linreg(ts, vs) if len(ts) >= 3 else None
    return OrderedDict([
        ("source", source), ("side", side), ("drv_run", cur["run"]), ("samples", len(ts)),
        ("duration_s", dur), ("speed_before", before), ("speed_first", vs[0]), ("speed_peak", max(vs)),
        ("speed_last", vs[-1]), ("boost", (max(vs) - before) if before is not None else None),
        ("mean_decel", -lr[0] if lr else None),
        ("linear_r2", r2(vs, [lr[1] + lr[0] * t for t in ts]) if lr else None),
    ])


# ---------------------------------------------------------------- smoke test
def smoke(rows, issues, min_join=0.9):
    """Pipeline acceptance for a first short session (T0). Returns [(check, ok, detail)]."""
    from collections import Counter
    sev = Counter(i.severity for i in issues)
    n = Counter((r["source"], r.get("side"), r.get("kind")) for r in rows)
    res = []
    res.append(("MT client rows", n[("MT", "cl", "cmd")] > 0, n[("MT", "cl", "cmd")]))
    res.append(("MT dedi rows", n[("MT", "sv", "cmd")] > 0, n[("MT", "sv", "cmd")]))
    res.append(("HSD client init line", n[("HSD", "cl", "init")] > 0, n[("HSD", "cl", "init")]))
    res.append(("HSD dedi init line", n[("HSD", "sv", "init")] > 0, n[("HSD", "sv", "init")]))
    res.append(("HSD client frames (hsd_md_cl_trace 1)", n[("HSD", "cl", "frame")] > 0, n[("HSD", "cl", "frame")]))
    res.append(("HSD dedi movement events", n[("HSD", "sv", "evt")] > 0, n[("HSD", "sv", "evt")]))
    res.append(("validation errors == 0", sev.get("error", 0) == 0, sev.get("error", 0)))
    cl = {r["cmd"] for r in rows if r["source"] == "MT" and r.get("side") == "cl" and not r.get("replay")}
    sv = {r["cmd"] for r in rows if r["source"] == "MT" and r.get("side") == "sv"}
    join = len(cl & sv) / len(cl) if cl else 0.0
    res.append((f"client cmds with a dedi line >= {min_join:.0%}", join >= min_join, f"{join:.1%}"))
    fts = [r["ft"] for r in rows if r["source"] == "HSD" and r.get("kind") == "frame" and r.get("side") == "cl"
           and isinstance(r.get("ft"), float) and r["ft"] > 0]
    dts = [r["drv_dt_est"] for r in rows if r["source"] == "MT" and r.get("side") == "cl" and r.get("drv_dt_est")
           and not r.get("replay") and r.get("ground") == 1 and r.get("drv_spd2d_post", 0) > 100]
    if fts and dts:
        ratio = _median(dts) / _median(fts)
        res.append(("MT dt_est median / HSD FrameTime median within 15%", abs(ratio - 1) <= 0.15, f"{ratio:.3f}"))
    else:
        res.append(("MT dt_est vs HSD FrameTime comparable", False, f"dt_est={len(dts)} ft={len(fts)} samples"))
    api = sum(1 for r in rows if r["source"] == "HSD" and r.get("kind") == "frame"
              and (r.get("ground") == -1 or r.get("slide") == -1))
    res.append(("HSD ground/slide APIs available (no -1)", api == 0, api))
    runs = {r.get("drv_run") for r in rows if r["source"] == "HSD" and r.get("kind") == "frame"}
    res.append(("at least one non-zero hsd_md_run label", any(x not in (None, "r0") for x in runs), sorted(runs)))
    return res
