"""Sampling-phase analysis: HSD script-frame samples vs MOVE-TRACE usercmds.

Usage:
    python sampling_phase.py <logs-dir> [--run N] [--json out.json]

<logs-dir> is a session's platform/logs folder (holding client/<guid>/ and
server/<guid>/). Reads only; prints a text report (and optional JSON).

Clock: every SDK log line carries "[wall] [plat]" where plat is Plat_FloatTime()
at emission, printed %.3f (s21-r5sdk/src/tier0/platform.cpp:107). It is one
process-wide clock shared by message.log (MOVE-TRACE) and script.log (HSD) of
the same process, so it orders client MT lines against client HSD lines to 1 ms.
The client and dedi are different processes: their plat clocks are unrelated.

stdlib only. Re-uses the line parsers in research/phase2-prep/tools/hsdtel.
"""
import argparse
import bisect
import json
import math
import os
import re
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "phase2-prep", "tools")))
from hsdtel.parse import parse_trace, parse_hsd, HSD_TAG, MT_TAG  # noqa: E402

BATCH_GAP = 0.020  # dedi MT lines closer than this (plat) belong to one batch (one server frame)
PREFIX_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]\s*\[\s*(-?\d+\.\d+)\]\s*")


def find_logs(root, side):
    base = os.path.join(root, side)
    out = []
    for d in sorted(os.listdir(base)):
        p = os.path.join(base, d)
        if os.path.isdir(p):
            out.append(p)
    if len(out) != 1:
        raise SystemExit(f"expected exactly one {side}/<guid> folder, found {len(out)}")
    return out[0]


def read_lines(path, tag):
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for ln, raw in enumerate(fh, 1):
            if tag not in raw:
                continue
            m = PREFIX_RE.match(raw)
            if not m:
                continue
            rest = raw[m.end():].rstrip("\r\n")
            if tag == MT_TAG:
                r = parse_trace(rest)
                if r is None:
                    continue
            else:
                r, prob = parse_hsd(rest)
                if prob:
                    continue
            r["plat"] = float(m.group(2))
            r["wallstr"] = m.group(1)
            r["line_no"] = ln
            rows.append(r)
    return rows


def pct(n, d):
    return 100.0 * n / d if d else float("nan")


def q(vals, p):
    if not vals:
        return float("nan")
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def summ(vals):
    if not vals:
        return "n=0"
    return (f"n={len(vals)} mean={statistics.fmean(vals):.5f} p05={q(vals, .05):.5f} "
            f"p50={q(vals, .5):.5f} p95={q(vals, .95):.5f} min={min(vals):.5f} max={max(vals):.5f}")


def vec(r, keys):
    return tuple(r[k] for k in keys)


O, V, PO, PV = ("ox", "oy", "oz"), ("vx", "vy", "vz"), ("pox", "poy", "poz"), ("pvx", "pvy", "pvz")


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def dt_est(c):
    """|po_xy - o_xy| / |pv_xy| (TELEMETRY-SCHEMA drv_dt_est), None below 20 u/s."""
    s = math.hypot(c["pvx"], c["pvy"])
    if s <= 20.0:
        return None
    return math.hypot(c["pox"] - c["ox"], c["poy"] - c["oy"]) / s


def run_window(hsd_rows, run):
    """(plat_start, plat_end) of hsd_md_run == run on that side, from kind=run lines."""
    start = end = None
    for r in hsd_rows:
        if r.get("kind") != "run":
            continue
        if int(r.get("run", -1)) == run and start is None:
            start = r["plat"]
        elif start is not None and end is None and int(r.get("run", -1)) != run:
            end = r["plat"]
    return start, (end if end is not None else float("inf"))


# --------------------------------------------------------------------------
# Client analysis
# --------------------------------------------------------------------------
def client_analysis(cdir, run, out):
    mt_all = read_lines(os.path.join(cdir, "message.log"), MT_TAG)
    hsd_all = read_lines(os.path.join(cdir, "script.log"), HSD_TAG)
    p0, p1 = run_window(hsd_all, run)
    frames = [r for r in hsd_all if r.get("kind") == "frame" and int(r.get("run", -1)) == run]
    mt_run = [c for c in mt_all if p0 <= c["plat"] < p1]
    cmds = [c for c in mt_run if not c["replay"]]
    reps = [c for c in mt_run if c["replay"]]
    res = {"run": run, "plat_window": [p0, p1]}
    res["n_frames"] = len(frames)
    res["n_frames_all_runs"] = sum(1 for r in hsd_all if r.get("kind") == "frame")
    res["n_cmds_all"] = sum(1 for c in mt_all if not c["replay"])
    res["n_cmds"] = len(cmds)
    res["n_replays_in_window"] = len(reps)
    res["n_replays_total"] = sum(1 for c in mt_all if c["replay"])
    res["cmd_range"] = [cmds[0]["cmd"], cmds[-1]["cmd"]] if cmds else None
    gaps = Counter(b["cmd"] - a["cmd"] for a, b in zip(cmds, cmds[1:]))
    res["cmd_number_gaps"] = dict(sorted(gaps.items()))
    span_f = frames[-1]["plat"] - frames[0]["plat"]
    span_c = cmds[-1]["plat"] - cmds[0]["plat"]
    res["frame_span_s"] = span_f
    res["cmd_span_s"] = span_c
    res["frames_per_s"] = (len(frames) - 1) / span_f
    res["cmds_per_s"] = (len(cmds) - 1) / span_c
    res["ratio_frames_per_cmd"] = len(frames) / len(cmds)

    # ---- (1) timing correspondence: commands whose plat lies in (prev frame, this frame]
    cplat = [c["plat"] for c in cmds]
    per_frame = []
    tie = 0
    for i in range(1, len(frames)):
        a, b = frames[i - 1]["plat"], frames[i]["plat"]
        lo = bisect.bisect_right(cplat, a)
        hi = bisect.bisect_right(cplat, b)
        per_frame.append(hi - lo)
        # a command printed in the same millisecond as a frame cannot be ordered
        if bisect.bisect_left(cplat, b) != hi:
            tie += 1
    res["cmds_per_frame_interval_by_plat"] = dict(sorted(Counter(per_frame).items()))
    anomalies = []
    for i in range(1, len(frames)):
        n = per_frame[i - 1]
        if n != 1:
            a, b = frames[i - 1], frames[i]
            lo = bisect.bisect_right(cplat, a["plat"])
            hi = bisect.bisect_right(cplat, b["plat"])
            anomalies.append({"seq": int(b["seq"]), "plat": [a["plat"], b["plat"]], "n_cmds": n,
                              "cmds": [cmds[lo]["cmd"], cmds[hi - 1]["cmd"]] if n else [],
                              "ft": b["ft"], "dt_t": round(b["t"] - a["t"], 5),
                              "dplat": round(b["plat"] - a["plat"], 3)})
    res["intervals_not_one_cmd"] = anomalies
    # every frame (moving or not): does its state equal post of the last command printed before it?
    eq_last = eq_prev_only = neither = 0
    for f in frames:
        j = bisect.bisect_right(cplat, f["plat"]) - 1
        if j < 0:
            neither += 1
            continue
        fo, fv = vec(f, O), vec(f, V)
        ok = dist(fo, vec(cmds[j], PO)) < 0.0015 and dist(fv, vec(cmds[j], PV)) < 0.0015
        if ok:
            eq_last += 1
        elif j > 0 and dist(fo, vec(cmds[j - 1], PO)) < 0.0015 and dist(fv, vec(cmds[j - 1], PV)) < 0.0015:
            eq_prev_only += 1
        else:
            neither += 1
    res["all_frames_state_eq_post_of_last_printed_cmd"] = eq_last
    res["all_frames_state_eq_post_of_cmd_before_that_only"] = eq_prev_only
    res["all_frames_state_matches_neither"] = neither
    # replays vs first-time lines of the same command
    orig = {c["cmd"]: c for c in mt_all if not c["replay"]}
    rdiff = [max(abs(c[k] - orig[c["cmd"]][k]) for k in O + V + PO + PV) for c in mt_all
             if c["replay"] and c["cmd"] in orig]
    res["replay_max_abs_diff_vs_first_time"] = max(rdiff) if rdiff else None
    res["replay_cmds"] = [c["cmd"] for c in mt_all if c["replay"]]
    # cadence regimes: median ft per 2 s of plat
    buckets = {}
    for f in frames:
        buckets.setdefault(int((f["plat"] - frames[0]["plat"]) // 2), []).append(f["ft"])
    res["ft_median_per_2s"] = [[k * 2, round(statistics.median(v), 5), len(v)] for k, v in sorted(buckets.items())]
    res["frames_with_same_ms_cmd"] = tie
    # plat offset from each frame to the latest command at or before it
    off_prev = []
    off_next = []
    for f in frames:
        j = bisect.bisect_right(cplat, f["plat"]) - 1
        if j >= 0:
            off_prev.append(f["plat"] - cplat[j])
        if j + 1 < len(cplat):
            off_next.append(cplat[j + 1] - f["plat"])
    res["plat_frame_minus_prev_cmd"] = summ(off_prev)
    res["plat_next_cmd_minus_frame"] = summ(off_next)

    # ---- (2) phase by state match
    by_cmd = {c["cmd"]: c for c in cmds}
    cmd_list = [c["cmd"] for c in cmds]

    def moving(f):
        return math.hypot(f["vx"], f["vy"]) > 1.0 or abs(f["vz"]) > 1.0

    def cand_window(f, w=6):
        j = bisect.bisect_right(cplat, f["plat"]) - 1
        lo, hi = max(0, j - w), min(len(cmds), j + w + 2)
        return range(lo, hi), j

    classes = Counter()
    lag_post = Counter()   # (index of matched cmd) - (index of last cmd printed at or before frame)
    lag_pre = Counter()
    unique_post = 0
    ambiguous = 0
    matched = []           # (frame index, cmd index) for unique exact post matches
    resid_none = []
    for fi, f in enumerate(frames):
        if not moving(f):
            classes["static"] += 1
            continue
        fo, fv = vec(f, O), vec(f, V)
        rng, j = cand_window(f)
        post = [k for k in rng if dist(fo, vec(cmds[k], PO)) < 0.0015 and dist(fv, vec(cmds[k], PV)) < 0.0015]
        pre = [k for k in rng if dist(fo, vec(cmds[k], O)) < 0.0015 and dist(fv, vec(cmds[k], V)) < 0.0015]
        post_o = [k for k in rng if dist(fo, vec(cmds[k], PO)) < 0.0015]
        if post:
            classes["post_exact"] += 1
            if len(post) == 1:
                unique_post += 1
                k = post[0]
                lag_post[k - j] += 1
                matched.append((fi, k))
            else:
                ambiguous += 1
        elif pre:
            classes["pre_exact"] += 1
            if len(pre) == 1:
                lag_pre[pre[0] - j] += 1
        elif post_o:
            classes["post_origin_only"] += 1
        else:
            # nearest within tolerance (post origin)
            best = min(rng, key=lambda k: dist(fo, vec(cmds[k], PO))) if len(rng) else None
            d = dist(fo, vec(cmds[best], PO)) if best is not None else float("inf")
            resid_none.append(d)
            classes["none_exact"] += 1
            if d < 0.5:
                classes["none_but_within_0.5u"] += 1
    res["phase_classes"] = dict(classes)
    res["phase_moving_frames"] = sum(v for k, v in classes.items() if k not in ("static", "none_but_within_0.5u"))
    res["phase_unique_post"] = unique_post
    res["phase_ambiguous_post"] = ambiguous
    res["lag_post_idx_vs_last_printed_cmd"] = dict(sorted(lag_post.items()))
    res["lag_pre_idx_vs_last_printed_cmd"] = dict(sorted(lag_pre.items()))
    res["none_nearest_post_origin_dist"] = summ(resid_none)

    # commands between consecutive matched frames (state-defined, immune to ms ties)
    steps = Counter()
    for (fa, ka), (fb, kb) in zip(matched, matched[1:]):
        if fb == fa + 1:
            steps[kb - ka] += 1
    res["cmds_between_consecutive_matched_frames"] = dict(sorted(steps.items()))

    # ---- (3) FrameTime semantics
    ft_rows = []
    for fi, k in matched:
        f = frames[fi]
        row = {"ft": f["ft"]}
        if fi > 0:
            row["dt_t_prev"] = f["t"] - frames[fi - 1]["t"]
            row["dplat_prev"] = f["plat"] - frames[fi - 1]["plat"]
        if fi + 1 < len(frames):
            row["dt_t_next"] = frames[fi + 1]["t"] - f["t"]
        for off, name in ((0, "dte_N"), (1, "dte_N+1"), (-1, "dte_N-1")):
            kk = k + off
            if 0 <= kk < len(cmds):
                d = dt_est(cmds[kk])
                if d is not None:
                    row[name] = d
        ft_rows.append(row)
    cmp = {}
    for a in ("dt_t_prev", "dt_t_next", "dte_N", "dte_N+1", "dte_N-1", "dplat_prev"):
        diffs = [r["ft"] - r[a] for r in ft_rows if a in r]
        cmp[a] = {"n": len(diffs),
                  "mean_abs_diff": statistics.fmean(abs(x) for x in diffs) if diffs else None,
                  "frac_abs_lt_0.5ms": pct(sum(1 for x in diffs if abs(x) < 0.0005), len(diffs)),
                  "frac_abs_lt_0.02ms": pct(sum(1 for x in diffs if abs(x) < 0.00002), len(diffs)),
                  "median_diff": q(diffs, .5)}
    res["ft_compare_matched"] = cmp
    vote = Counter()
    for r in ft_rows:
        cands = {k: abs(r["ft"] - r[k]) for k in ("dte_N", "dte_N+1", "dte_N-1") if k in r}
        if len(cands) == 3:
            vote[min(cands, key=cands.get)] += 1
    res["ft_closest_cmd_dt_est_vote"] = dict(vote)
    # decisive subset: fast (|pv_xy| >= 150, print-rounding error ~5 us) and cmd N's dt_est
    # differs from both neighbours by > 0.2 ms, so N vs N+-1 cannot be confused
    dvote = Counter()
    for fi, k in matched:
        if k < 1 or k + 1 >= len(cmds):
            continue
        trio = [cmds[k - 1], cmds[k], cmds[k + 1]]
        if any(math.hypot(c["pvx"], c["pvy"]) < 150.0 for c in trio):
            continue
        d = [dt_est(c) for c in trio]
        if abs(d[1] - d[0]) > 2e-4 and abs(d[1] - d[2]) > 2e-4:
            e = [abs(frames[fi]["ft"] - x) for x in d]
            dvote[("N-1", "N", "N+1")[e.index(min(e))]] += 1
    res["ft_closest_cmd_dt_est_vote_decisive"] = dict(dvote)
    bad = []
    for i in range(1, len(frames)):
        dtt = frames[i]["t"] - frames[i - 1]["t"]
        if abs(frames[i]["ft"] - dtt) >= 5e-5:
            bad.append({"seq": int(frames[i]["seq"]), "plat": frames[i]["plat"], "ft": frames[i]["ft"],
                        "dt_t": round(dtt, 5), "dplat": round(frames[i]["plat"] - frames[i - 1]["plat"], 3)})
    res["frames_ft_ne_dt_t"] = bad
    # all frames: ft vs t deltas
    allp = [frames[i]["ft"] - (frames[i]["t"] - frames[i - 1]["t"]) for i in range(1, len(frames))]
    alln = [frames[i]["ft"] - (frames[i + 1]["t"] - frames[i]["t"]) for i in range(len(frames) - 1)]
    res["ft_minus_dt_prev_all"] = summ(allp)
    res["ft_minus_dt_next_all"] = summ(alln)
    res["frac_ft_eq_dt_prev_all_lt_0.05ms"] = pct(sum(1 for x in allp if abs(x) < 5e-5), len(allp))
    res["frac_ft_eq_dt_next_all_lt_0.05ms"] = pct(sum(1 for x in alln if abs(x) < 5e-5), len(alln))
    res["ft_all"] = summ([f["ft"] for f in frames])
    res["dt_t_all"] = summ([frames[i]["t"] - frames[i - 1]["t"] for i in range(1, len(frames))])
    res["dplat_all"] = summ([frames[i]["plat"] - frames[i - 1]["plat"] for i in range(1, len(frames))])
    dtes = [d for d in (dt_est(c) for c in cmds) if d is not None]
    res["cmd_dt_est_all_moving"] = summ(dtes)
    res["cmd_dplat_all"] = summ([b["plat"] - a["plat"] for a, b in zip(cmds, cmds[1:])])

    # sum of dt_est over the commands between matched frames vs ft / t delta
    sums = []
    for (fa, ka), (fb, kb) in zip(matched, matched[1:]):
        if fb != fa + 1 or kb <= ka:
            continue
        ds = [dt_est(cmds[k]) for k in range(ka + 1, kb + 1)]
        if any(d is None for d in ds):
            continue
        sums.append((sum(ds), frames[fb]["ft"], frames[fb]["t"] - frames[fa]["t"]))
    res["sum_dte_between_frames_minus_ft"] = summ([s - ft for s, ft, _ in sums])
    res["sum_dte_between_frames_minus_dt_t"] = summ([s - dt for s, _, dt in sums])

    # ground-edge timing: first frame ground=0 vs first cmd with ge=0 (pre) / takeoff
    edges = []
    for fi in range(1, len(frames)):
        a, b = frames[fi - 1], frames[fi]
        if a.get("ground") != b.get("ground"):
            j = bisect.bisect_right(cplat, b["plat"]) - 1
            edges.append({"frame_seq": int(b["seq"]), "ground": f"{int(a['ground'])}->{int(b['ground'])}",
                          "frame_plat": b["plat"], "frame_vz": b["vz"],
                          "last_cmd_printed": cmds[j]["cmd"] if j >= 0 else None})
    # MT ground transitions (pre ge of cmd k+1 is post ground of cmd k)
    mt_edges = []
    for a, b in zip(cmds, cmds[1:]):
        if a["ground"] != b["ground"]:
            mt_edges.append({"cmd": a["cmd"], "ge_pre_next": f"{a['ground']}->{b['ground']}",
                             "cmd_plat": a["plat"], "post_vz": a["pvz"]})
    res["hsd_ground_edges"] = edges
    res["mt_ground_edges"] = mt_edges

    # sample rows for the report
    examples = []
    for fi, k in matched[:: max(1, len(matched) // 6)][:6]:
        f, c = frames[fi], cmds[k]
        j = bisect.bisect_right(cplat, f["plat"]) - 1
        examples.append({"seq": int(f["seq"]), "frame_plat": f["plat"], "t": f["t"], "ft": f["ft"],
                         "o": vec(f, O), "vel": vec(f, V), "matched_cmd": c["cmd"], "cmd_plat": c["plat"],
                         "po": vec(c, PO), "pv": vec(c, PV), "dte": dt_est(c),
                         "last_printed_cmd": cmds[j]["cmd"] if j >= 0 else None})
    res["examples"] = examples
    out["client"] = res
    return frames, cmds


# --------------------------------------------------------------------------
# Server analysis
# --------------------------------------------------------------------------
def server_analysis(sdir, run, out, cl_cmds, cl_frames):
    mt = read_lines(os.path.join(sdir, "message.log"), MT_TAG)
    hsd = read_lines(os.path.join(sdir, "script.log"), HSD_TAG)
    res = {"n_mt": len(mt), "n_hsd": len(hsd)}
    res["hsd_kinds"] = dict(Counter(r.get("kind") for r in hsd))
    # batches: runs of MT lines whose plat stamps are within 2 ms of the previous one
    batches = []
    cur = [mt[0]]
    for a, b in zip(mt, mt[1:]):
        if b["plat"] - a["plat"] <= BATCH_GAP:
            cur.append(b)
        else:
            batches.append(cur)
            cur = [b]
    batches.append(cur)
    sizes = [len(b) for b in batches]
    starts = [b[0]["plat"] for b in batches]
    res["n_batches"] = len(batches)
    res["batch_size_hist"] = dict(sorted(Counter(sizes).items()))
    res["batch_interval"] = summ([b - a for a, b in zip(starts, starts[1:])])
    res["batch_duration"] = summ([b[-1]["plat"] - b[0]["plat"] for b in batches])
    p0, p1 = run_window(hsd, run)
    inrun = [b for b in batches if p0 <= b[0]["plat"] < p1]
    res["run_batches"] = len(inrun)
    res["run_batch_size_hist"] = dict(sorted(Counter(len(b) for b in inrun).items()))
    res["run_batch_interval"] = summ([b[0]["plat"] - a[0]["plat"] for a, b in zip(inrun, inrun[1:])])
    # server dt_est per command (if moving)
    sdte = [d for d in (dt_est(c) for c in mt) if d is not None]
    res["sv_cmd_dt_est"] = summ(sdte)
    # client vs server state for same cmd
    cl = {c["cmd"]: c for c in cl_cmds}
    same = diff = 0
    maxd = 0.0
    for c in mt:
        k = cl.get(c["cmd"])
        if not k:
            continue
        d = max(dist(vec(c, PO), vec(k, PO)), dist(vec(c, PV), vec(k, PV)))
        maxd = max(maxd, d)
        if d < 0.0015:
            same += 1
        else:
            diff += 1
    res["cl_sv_same_cmd_post_equal"] = same
    res["cl_sv_same_cmd_post_differ"] = diff
    res["cl_sv_same_cmd_max_post_diff"] = maxd

    mplat = [c["plat"] for c in mt]
    cl_by = {c["cmd"]: c for c in cl_cmds}
    evs = []
    for r in hsd:
        if r.get("kind") != "evt":
            continue
        # which MT line is printed nearest; which cmd's pre/post state equals the event state
        j = bisect.bisect_right(mplat, r["plat"]) - 1
        bi = bisect.bisect_right(starts, r["plat"]) - 1
        b = batches[bi] if bi >= 0 else None
        fo, fv = vec(r, O), vec(r, V)
        lo, hi = max(0, j - 30), min(len(mt), j + 30)
        m_post = [mt[k]["cmd"] for k in range(lo, hi)
                  if dist(fo, vec(mt[k], PO)) < 0.0015 and dist(fv, vec(mt[k], PV)) < 0.0015]
        m_pre = [mt[k]["cmd"] for k in range(lo, hi)
                 if dist(fo, vec(mt[k], O)) < 0.0015 and dist(fv, vec(mt[k], V)) < 0.0015]
        m_pre_o = [mt[k]["cmd"] for k in range(lo, hi) if dist(fo, vec(mt[k], O)) < 0.0015]
        m_post_o = [mt[k]["cmd"] for k in range(lo, hi) if dist(fo, vec(mt[k], PO)) < 0.0015]
        # the command of this batch whose execution explains the event
        trans = None
        if b:
            for c in b:
                nxt = next((x for x in mt if x["cmd"] == c["cmd"] + 1), None)
                if r.get("evt") in ("JUMP", "LEAVE_GROUND") and c["ground"] == 1 and c["pvz"] > 100:
                    trans = c["cmd"]
                if r.get("evt") == "TOUCH_GROUND" and c["ground"] == 0 and nxt is not None and nxt["ground"] == 1:
                    trans = c["cmd"]
        # client frame whose state is the post of cmd (trans-1): its Time() is the start time of cmd trans
        cl_t = None
        if trans is not None:
            prev = cl_by.get(trans - 1)
            if prev is not None:
                for f in cl_frames:
                    if abs(f["plat"] - prev["plat"]) < 0.02 and dist(vec(f, O), vec(prev, PO)) < 0.0015                             and dist(vec(f, V), vec(prev, PV)) < 0.0015 and f["plat"] >= prev["plat"]:
                        cl_t = f["t"]
                        break
        evs.append({"evt": r.get("evt"), "explaining_cmd": trans,
                    "pos_in_batch": ([c["cmd"] for c in b].index(trans) + 1 if (b and trans is not None) else None),
                    "batch_len": len(b) if b else None,
                    "client_t_at_start_of_cmd": cl_t,
                    "sv_t_minus_client_t": (r.get("t") - cl_t) if cl_t is not None else None, "t": r.get("t"), "plat": r["plat"],
                    "o": fo, "vel": fv, "ground": r.get("ground"),
                    "last_mt_cmd_printed": mt[j]["cmd"] if j >= 0 else None,
                    "last_mt_plat": mt[j]["plat"] if j >= 0 else None,
                    "batch_cmds": [b[0]["cmd"], b[-1]["cmd"]] if b else None,
                    "batch_plat": [b[0]["plat"], b[-1]["plat"]] if b else None,
                    "post_state_match_cmds": m_post[:6], "pre_state_match_cmds": m_pre[:6],
                    "pre_origin_match_cmds": m_pre_o[:6], "post_origin_match_cmds": m_post_o[:6]})
    res["events"] = evs
    # MT detail around jump cmds
    jump = [c for c in mt if c["buttons"] & 2]
    if jump:
        k0 = mt.index(jump[0])
        res["mt_around_first_jump"] = [{"cmd": c["cmd"], "plat": c["plat"], "ge": c["ground"], "b": c["buttons"],
                                        "o": vec(c, O), "v": vec(c, V), "po": vec(c, PO), "pv": vec(c, PV)}
                                       for c in mt[max(0, k0 - 2):k0 + 4]]
    out["server"] = res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", help="platform/logs folder of one session")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--json", help="write the full result as JSON here")
    a = ap.parse_args()
    out = {}
    cdir = find_logs(a.logs, "client")
    sdir = find_logs(a.logs, "server")
    frames, cmds = client_analysis(cdir, a.run, out)
    server_analysis(sdir, a.run, out, cmds, frames)
    txt = json.dumps(out, indent=1, default=lambda x: list(x) if isinstance(x, tuple) else str(x))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            fh.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
