"""Offline derived columns (all prefixed drv_). Never overwrites observed values."""
import bisect
import math
from collections import OrderedDict

from .schema import IN_JUMP


def stream_key(row):
    """Rows of one physical sample stream: same source, side, kind family, entity
    and log session. Key = (source, side, family, ent, session)."""
    ses = row.get("session")
    if row["source"] == "MT":
        return ("MT", row.get("side"), "cmd", row.get("ent"), ses)
    if row["source"] in ("CV", "LOG"):
        return (row["source"], row.get("side"), row.get("kind"), None, ses)
    kind = row.get("kind")
    fam = "frame" if kind == "frame" else ("edge" if kind in ("takeoff", "land") else kind)
    ent = row.get("ent") if row.get("side") == "sv" else None
    return ("HSD", row.get("side"), fam, ent, ses)


def order_key(row):
    return (row.get("_rank", 0), row.get("line_no", 0))


def streams(rows):
    out = OrderedDict()
    for r in sorted(rows, key=order_key):
        out.setdefault(stream_key(r), []).append(r)
    return out


def _hyp(a, b):
    return math.hypot(a, b) if a is not None and b is not None else None


def _finite(*vals):
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in vals)


def reset_markers(rows):
    """Wall times after which command numbers may restart, per (side, session):
    level loads (LOG map), script VM starts (HSD init) and dedi RESPAWN events."""
    out = {}
    for r in rows:
        if r.get("wall") is None:
            continue
        if r["source"] == "LOG" or (r["source"] == "HSD" and (r.get("kind") == "init" or r.get("evt") == "RESPAWN")):
            out.setdefault((r.get("side"), r.get("session")), []).append(r["wall"])
    for v in out.values():
        v.sort()
    return out


def _marker_between(marks, w0, w1):
    if not marks or w0 is None or w1 is None:
        return False
    i = bisect.bisect_right(marks, w0)
    return i < len(marks) and marks[i] <= w1


def derive(rows, burst_gap=8, teleport_slack=64.0, join_slack=5.0):
    """Adds drv_* columns in place and returns rows.

    drv_batch (MT, per stream): a new reset batch starts at a non-replay row when
      (a) its cmd is lower than the previous non-replay cmd (the counter
          restarted: reconnect, map restart), or
      (b) cmd jumped forward by more than burst_gap AND a reset marker lies
          between the two rows: a level load / VM start / dedi RESPAWN of the
          same side and session (by wall clock), or a position jump larger than
          teleport_slack.
    Contiguous commands never start a batch: a respawn or teleport that keeps the
    numbering cannot collide, and splitting there would break the cl/sv join."""
    markers = reset_markers(rows)
    for key, srows in streams(rows).items():
        source = key[0]
        if source in ("CV", "LOG"):
            continue
        prev = None
        burst = 0
        batch = 0
        for r in srows:
            flags = []
            if _finite(r.get("vx"), r.get("vy")):
                r["drv_spd2d"] = math.hypot(r["vx"], r["vy"])
            elif r.get("vx") is not None:
                flags.append("nonfinite")
            if r.get("ground") == -1 or r.get("slide") == -1:
                flags.append("api_missing")

            if source == "MT":
                if _finite(r.get("pvx"), r.get("pvy")):
                    r["drv_spd2d_post"] = math.hypot(r["pvx"], r["pvy"])
                if "drv_spd2d" in r and "drv_spd2d_post" in r:
                    r["drv_dspd2d"] = r["drv_spd2d_post"] - r["drv_spd2d"]
                    if r["drv_spd2d"] > 1.0 and r["drv_spd2d_post"] > 1.0:
                        a0 = math.atan2(r["vy"], r["vx"])
                        a1 = math.atan2(r["pvy"], r["pvx"])
                        r["drv_dheading"] = math.degrees((a1 - a0 + math.pi) % (2 * math.pi) - math.pi)
                if _finite(r.get("ox"), r.get("oy"), r.get("pox"), r.get("poy")) and r.get("drv_spd2d_post", 0) > 20.0:
                    disp = math.hypot(r["pox"] - r["ox"], r["poy"] - r["oy"])
                    r["drv_dt_est"] = disp / r["drv_spd2d_post"]
                    r["drv_dt"] = r["drv_dt_est"]
                    if "drv_dspd2d" in r and r["drv_dt_est"] > 1e-5:
                        r["drv_accel2d"] = r["drv_dspd2d"] / r["drv_dt_est"]
                if r.get("replay"):
                    r["drv_burst"] = burst
                    r["drv_batch"] = batch
                    r["drv_flags"] = "|".join(flags)
                    continue  # replays never advance the stream state
                if prev is not None:
                    gap = r["cmd"] - prev["cmd"]
                    if gap > burst_gap or gap < 0:
                        burst += 1
                    r["drv_pressed"] = r["buttons"] & ~prev["buttons"]
                    jump = None
                    if _finite(prev.get("pox"), prev.get("poy"), prev.get("poz"), r.get("ox"), r.get("oy"), r.get("oz")):
                        jump = math.dist((prev["pox"], prev["poy"], prev["poz"]), (r["ox"], r["oy"], r["oz"]))
                    if jump is not None and 0 < gap <= burst_gap and jump > teleport_slack:
                        flags.append("teleport")
                    marker = (jump is not None and jump > teleport_slack) or \
                        _marker_between(markers.get((key[1], key[4])), prev.get("wall"), r.get("wall"))
                    if gap < 0 or (gap > burst_gap and marker):
                        batch += 1
                else:
                    r["drv_pressed"] = 0
                r["drv_burst"] = burst
                r["drv_batch"] = batch
            else:
                if prev is not None and _finite(r.get("t"), prev.get("t")):
                    dt = r["t"] - prev["t"]
                    if dt > 0:
                        r["drv_dt"] = dt
                        if "drv_spd2d" in r and "drv_spd2d" in prev:
                            r["drv_accel2d"] = (r["drv_spd2d"] - prev["drv_spd2d"]) / dt
                        if _finite(r.get("ox"), prev.get("ox")):
                            jump = math.dist((prev["ox"], prev["oy"], prev["oz"]), (r["ox"], r["oy"], r["oz"]))
                            vmax = max(prev.get("drv_spd2d", 0.0), r.get("drv_spd2d", 0.0)) + abs(r.get("vz") or 0.0)
                            if jump > vmax * dt * 3.0 + teleport_slack:
                                flags.append("teleport")
                ax_f, ax_r = r.get("ax_fwd"), r.get("ax_right")
                if _finite(ax_f, ax_r, r.get("yaw")) and ax_f > -2 and ax_r > -2 and math.hypot(ax_f, ax_r) > 0.1:
                    r["drv_wish_yaw"] = r["yaw"] + math.degrees(math.atan2(-ax_r, ax_f))
            r["drv_flags"] = "|".join(flags)
            prev = r
    join_sides(rows, join_slack)
    _assign_runs(rows)
    return rows


# ---------------------------------------------------------------- client/dedi join
def join_key(row):
    """Per-side identity of one usercmd line: (session, ent, reset batch, cmd)."""
    return (row.get("session"), row.get("ent"), row.get("drv_batch", 0), row.get("cmd"))


def _segments(mt_rows):
    """(side, session, ent, batch) -> [wall_min, wall_max, first order key]."""
    segs = {}
    for r in mt_rows:
        k = (r.get("side"),) + join_key(r)[:3]
        s = segs.setdefault(k, [None, None, order_key(r)])
        w = r.get("wall")
        if w is not None:
            s[0] = w if s[0] is None else min(s[0], w)
            s[1] = w if s[1] is None else max(s[1], w)
        s[2] = min(s[2], order_key(r))
    return segs


def _odist(a, b):
    if not _finite(a.get("ox"), a.get("oy"), a.get("oz"), b.get("ox"), b.get("oy"), b.get("oz")):
        return float("inf")
    return math.dist((a["ox"], a["oy"], a["oz"]), (b["ox"], b["oy"], b["oz"]))


def join_sides(rows, slack=5.0, max_origin_diff=8.0):
    """Pair every first-time client MT row with the dedi MT row of the same usercmd.

    Each side's key is join_key() = (session, ent, reset batch, cmd). The sides
    write different session folders and the client always prints ent=1, so the
    client key is mapped onto dedi keys like this:
      1. candidates = dedi rows with the same cmd whose (session, ent, batch)
         segment is live at the client row's wall time (segment wall span
         +/- slack s); without wall clocks, the dedi segments at the same
         position in segment order as the client row's segment;
      2. several candidates (several dedi entities, back-to-back sessions or
         batches) are narrowed to the one whose pre-move origin is within
         max_origin_diff u while all others are farther, else to the one
         nearest in wall time when the next is more than slack/5 s farther;
      3. otherwise the row is 'ambiguous' and stays unjoined. A dedi row
         claimed by two client rows makes both ambiguous.
    Sets drv_join = ok|none|ambiguous on client (non-replay) and dedi MT rows and
    the private _join partner reference."""
    mt = [r for r in rows if r["source"] == "MT" and not r.get("replay")]
    cl = [r for r in mt if r.get("side") == "cl"]
    sv = [r for r in mt if r.get("side") == "sv"]
    for r in cl + sv:
        r["drv_join"] = "none"
        r.pop("_join", None)
    if not cl or not sv:
        return
    segs = _segments(cl + sv)
    order = {}
    for side in ("cl", "sv"):
        ks = sorted((k for k in segs if k[0] == side), key=lambda k: segs[k][2])
        order.update({k: i for i, k in enumerate(ks)})
    by_cmd = {}
    for r in sv:
        by_cmd.setdefault(r["cmd"], []).append(r)

    def live(c, kc, s):
        ks = ("sv",) + join_key(s)[:3]
        lo, hi = segs[ks][0], segs[ks][1]
        if c.get("wall") is not None and lo is not None:
            return lo - slack <= c["wall"] <= hi + slack
        return order[kc] == order[ks]

    claims = {}
    for r in cl:
        kc = ("cl",) + join_key(r)[:3]
        cands = [s for s in by_cmd.get(r["cmd"], ()) if live(r, kc, s)]
        if len(cands) > 1:
            d = sorted((_odist(r, s), i) for i, s in enumerate(cands))
            if d[0][0] <= max_origin_diff < d[1][0]:
                cands = [cands[d[0][1]]]
            elif r.get("wall") is not None and all(s.get("wall") is not None for s in cands):
                w = sorted((abs(s["wall"] - r["wall"]), i) for i, s in enumerate(cands))
                if w[1][0] - w[0][0] > slack / 5:
                    cands = [cands[w[0][1]]]
        if len(cands) == 1:
            claims.setdefault(id(cands[0]), (cands[0], []))[1].append(r)
        elif cands:
            r["drv_join"] = "ambiguous"
    for s, crs in claims.values():
        if len(crs) == 1:
            crs[0]["drv_join"] = s["drv_join"] = "ok"
            crs[0]["_join"], s["_join"] = s, crs[0]
        else:  # two client lines claim one dedi line (e.g. two clients, one traced entity)
            s["drv_join"] = "ambiguous"
            for c in crs:
                c["drv_join"] = "ambiguous"


def join_stats(rows):
    """Counts over first-time client MT rows (cl = all, ok / ambiguous / none)
    plus the dedi MT row count; ratio = ok / cl."""
    out = {"cl": 0, "ok": 0, "ambiguous": 0, "none": 0, "sv": 0}
    for r in rows:
        if r["source"] != "MT" or r.get("replay"):
            continue
        if r.get("side") == "sv":
            out["sv"] += 1
        elif r.get("side") == "cl":
            out["cl"] += 1
            out[r.get("drv_join") or "none"] += 1
    out["ratio"] = out["ok"] / out["cl"] if out["cl"] else 0.0
    return out


def _assign_runs(rows):
    """drv_run: 'r<run>' for HSD rows. Client MT rows take the HSD run active at
    their wall time in the same client session; dedi MT rows take the label of
    the client row they are joined to (join_sides) whenever that client session
    has run marks -- including 'b<burst>' when the client was outside a run, so
    a dedi whose hsd_md_run was never reset cannot extend a trial -- else the
    dedi HSD run of their session at their wall time (approximate: the dedi runs
    commands in 50 ms batches); else 'b<burst>'."""
    marks = {}
    for r in rows:
        if r["source"] == "HSD" and r.get("wall") is not None and r.get("run") is not None:
            marks.setdefault((r.get("side"), r.get("session")), []).append((r["wall"], int(r["run"])))
    for k in marks:
        marks[k].sort()
    ordered = sorted(rows, key=lambda r: (r["source"] != "HSD", r.get("side") != "cl"))
    for r in ordered:
        if r["source"] in ("CV", "LOG"):
            r["drv_run"] = ""
            continue
        if r["source"] == "HSD":
            r["drv_run"] = f"r{int(r['run'])}" if r.get("run") is not None else "r0"
            continue
        # a dedi line inherits the label of the client line for the same usercmd
        partner = r.get("_join")
        if r.get("side") == "sv" and partner is not None and (
                str(partner.get("drv_run", "")).startswith("r") or ("cl", partner.get("session")) in marks):
            r["drv_run"] = partner["drv_run"]
            continue
        lab = None
        m = marks.get((r.get("side"), r.get("session")))
        if m and r.get("wall") is not None:
            i = bisect.bisect_right(m, (r["wall"], float("inf"))) - 1
            if i >= 0 and m[i][1] != 0:
                lab = f"r{m[i][1]}"
        r["drv_run"] = lab or f"b{r.get('drv_burst', 0)}"


def jump_press(row):
    return bool(row.get("drv_pressed", 0) & IN_JUMP)
