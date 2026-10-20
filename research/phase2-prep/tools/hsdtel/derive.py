"""Offline derived columns (all prefixed drv_). Never overwrites observed values."""
import bisect
import math
from collections import OrderedDict

from .schema import IN_JUMP


def stream_key(row):
    """Rows of one physical sample stream: same source, side, kind family and entity."""
    if row["source"] == "MT":
        return ("MT", row.get("side"), "cmd", row.get("ent"))
    if row["source"] == "CV":
        return ("CV", row.get("side"), "classvar", None)
    kind = row.get("kind")
    fam = "frame" if kind == "frame" else ("edge" if kind in ("takeoff", "land") else kind)
    ent = row.get("ent") if row.get("side") == "sv" else None
    return ("HSD", row.get("side"), fam, ent)


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


def derive(rows, burst_gap=8, teleport_slack=64.0):
    """Adds drv_* columns in place and returns rows."""
    for key, srows in streams(rows).items():
        source = key[0]
        if source == "CV":
            continue
        prev = None
        burst = 0
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
                    r["drv_flags"] = "|".join(flags)
                    continue  # replays never advance the stream state
                if prev is not None:
                    gap = r["cmd"] - prev["cmd"]
                    if gap > burst_gap or gap < 0:
                        burst += 1
                    r["drv_pressed"] = r["buttons"] & ~prev["buttons"]
                    if _finite(prev.get("pox"), prev.get("poy"), r.get("ox"), r.get("oy")) and 0 < gap <= burst_gap:
                        jump = math.dist((prev["pox"], prev["poy"], prev["poz"]), (r["ox"], r["oy"], r["oz"]))
                        if jump > teleport_slack:
                            flags.append("teleport")
                else:
                    r["drv_pressed"] = 0
                r["drv_burst"] = burst
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
    _assign_runs(rows)
    return rows


def _assign_runs(rows):
    """drv_run: 'r<run>' for HSD rows. Client MT rows take the HSD run active at
    their wall time on the client; dedi MT rows take the label of the client row
    with the same command number, else the dedi HSD run at their wall time
    (approximate: the dedi runs commands in 50 ms batches); else 'b<burst>'."""
    marks = {}
    for r in rows:
        if r["source"] == "HSD" and r.get("wall") is not None and r.get("run") is not None:
            marks.setdefault(r.get("side"), []).append((r["wall"], int(r["run"])))
    for side in marks:
        marks[side].sort()
    by_cmd = {}
    ordered = sorted(rows, key=lambda r: (r["source"] != "HSD", r.get("side") != "cl"))
    for r in ordered:
        if r["source"] == "CV":
            r["drv_run"] = ""
            continue
        if r["source"] == "HSD":
            r["drv_run"] = f"r{int(r['run'])}" if r.get("run") is not None else "r0"
            continue
        # a dedi line inherits the label of the client line for the same command
        if r.get("side") == "sv" and r.get("cmd") in by_cmd:
            r["drv_run"] = by_cmd[r["cmd"]]
            continue
        lab = None
        m = marks.get(r.get("side"))
        if m and r.get("wall") is not None:
            i = bisect.bisect_right(m, (r["wall"], float("inf"))) - 1
            if i >= 0 and m[i][1] != 0:
                lab = f"r{m[i][1]}"
        r["drv_run"] = lab or f"b{r.get('drv_burst', 0)}"
        if r.get("side") == "cl" and not r.get("replay") and lab:
            by_cmd[r["cmd"]] = lab


def jump_press(row):
    return bool(row.get("drv_pressed", 0) & IN_JUMP)
