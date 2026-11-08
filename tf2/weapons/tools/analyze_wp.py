"""Analyse a runner_wp.py run (session tf2-weapons, 2026-11-08).

Usage: python -I analyze_wp.py <run dir> [--frames]
Reads <run dir>/diag.tsv and prints, per tag segment:
  shots      client times of clip decrements (WC line) and the intervals between them
  reload     WC reloading 0->1->0: start, clip refill moment, end (relative to the start)
  zoom       time from the +zoom / -zoom command to zoomfrac 0.5 / 0.99 / 0.01
  spread     GetAttackSpreadAngle at shots, min / max over the segment
  view       eye pitch / yaw change from 0.05 s before the first shot to 0.6 s after the last (no mouse input)
  projectiles launch speed and direction vs eye angles; z(t) fit -> gravity; speed change; lateral drift;
             first stop (planted / bounce) and end
  damage     WDMG lines (victim, damage, hit group, headshot, distance)
Times: client lines (C, WC, CMD) use the client clock, server lines (TAG, PJ*, WDMG) the server clock;
the two differ by <0.1 s (CMD hsd_tag vs TAG), reported per run as "clock".
"""
import math
import sys
from collections import defaultdict
from pathlib import Path


def parse(path):
    ev = defaultdict(list)
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) < 2 or p[0] != "HSDDIAG":
            continue
        ev[p[1]].append(p[2:])
    return ev


def segments(ev):
    """client-time segments from 'CMD <t> hsd_tag <name>' lines; server times from TAG lines."""
    cmds = [(float(c[0]), " ".join(c[1:])) for c in ev["CMD"]]
    tags = [(t, c.split()[1]) for t, c in cmds if c.startswith("hsd_tag ")]
    # the same tag name can occur several times (one suite per weapon): pair the n-th CMD of a
    # name with the n-th TAG line of that name
    stag = {}
    for row in ev["TAG"]:
        stag.setdefault(row[0], []).append(float(row[1]))
    seen = {}
    segs = []
    for i, (t, name) in enumerate(tags):
        end = tags[i + 1][0] if i + 1 < len(tags) else 1e9
        n = seen.get(name, 0)
        seen[name] = n + 1
        lst = stag.get(name, [])
        segs.append((name, t, end, lst[n] if n < len(lst) else None))
    return cmds, segs


def wc_rows(ev):
    out = []
    for r in ev["WC"]:
        if len(r) < 11 or r[0] == "init":
            continue
        out.append(dict(t=float(r[0]), w=r[1], clip=int(r[2]), stock=int(r[3]), rel=int(r[4]), zoom=float(r[5]),
                        spread=float(r[6]), charge=float(r[7]), ads=int(r[8]), ready=int(r[9]), burst=int(r[10]),
                        smn=int(r[12]) if len(r) > 12 else 0, smf=float(r[13]) if len(r) > 13 else 0.0))
    return out


def c_rows(ev):
    out = []
    for r in ev["C"]:
        try:
            out.append(dict(t=float(r[0]), o=(float(r[1]), float(r[2]), float(r[3])), v=(float(r[4]), float(r[5]), float(r[6])),
                            pitch=float(r[7]), yaw=float(r[8]), ground=r[9], btn=int(r[15])))
        except (IndexError, ValueError):
            pass
    return out


def fit_quad(ts, zs):
    """least squares z = a + b t + c t^2; returns (a, b, c)."""
    n = len(ts)
    if n < 3:
        return None
    s = [sum(t ** k for t in ts) for k in range(5)]
    y = [sum(z * t ** k for t, z in zip(ts, zs)) for k in range(3)]
    m = [[s[0], s[1], s[2]], [s[1], s[2], s[3]], [s[2], s[3], s[4]]]
    # Cramer's rule
    def det(a):
        return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
    d = det(m)
    if abs(d) < 1e-12:
        return None
    res = []
    for col in range(3):
        mm = [row[:] for row in m]
        for i in range(3):
            mm[i][col] = y[i]
        res.append(det(mm) / d)
    return tuple(res)


def projectiles(ev, t0, t1):
    """projectiles first seen in [t0, t1] (server clock). Entity indices are reused, so each life
    runs from its PJNEW to the next PJEND of the same index."""
    lives = []   # (idx, t_new, t_end)
    open_ = {}
    for kind, rows in (("new", ev["PJNEW"]), ("end", ev["PJEND"])):
        pass
    events = [(float(r[0]), 0, r) for r in ev["PJNEW"]] + [(float(r[0]), 1, r) for r in ev["PJEND"]]
    events.sort(key=lambda e: (e[0], e[1]))
    news = {}
    for t, kind, r in events:
        idx = r[1]
        if kind == 0:
            open_[idx] = (t, r)
        elif idx in open_:
            tn, rn = open_.pop(idx)
            lives.append((idx, tn, t, rn, (t, float(r[2]), float(r[3]), float(r[4]))))
    for idx, (tn, rn) in open_.items():
        lives.append((idx, tn, 1e9, rn, None))
    out = []
    pj = defaultdict(list)
    for r in ev["PJ"]:
        pj[r[1]].append(r)
    for idx, tn, te, r, end in sorted(lives, key=lambda x: x[1]):
        if not (t0 - 0.2 <= tn < t1 + 0.2):
            continue
        path = []
        for q in pj[idx]:
            tq = float(q[0])
            if tn - 1e-6 <= tq <= te + 1e-6:
                path.append((tq, float(q[2]), float(q[3]), float(q[4]), float(q[5]), float(q[6]), float(q[7]), q[9],
                             q[11] if len(q) > 11 else ""))
        # PJNEW <t> <idx> <class> <weapon> eye x y z ang p y vel vx vy vz pos x y z
        out.append(dict(key=(idx, tn), cls=r[2], wcls=r[3], eye=tuple(float(x) for x in r[5:8]),
                        ang=(float(r[9]), float(r[10])), vel=tuple(float(x) for x in r[12:15]),
                        pos=tuple(float(x) for x in r[16:19]), path=path, end=end))
    return out


def vec_angles(v):
    x, y, z = v
    h = math.hypot(x, y)
    return (-math.degrees(math.atan2(z, h)), math.degrees(math.atan2(y, x)))


def describe_proj(p):
    lines = []
    sp = math.sqrt(sum(c * c for c in p["vel"]))
    pa, ya = vec_angles(p["vel"]) if sp > 0 else (0, 0)
    dyaw = (ya - p["ang"][1] + 180) % 360 - 180
    lines.append("  proj %s %s t=%.4f launch |v|=%.1f dir pitch %.3f yaw %.3f (eye %.3f %.3f; d %.3f %.3f) pos-eye %s" % (
        p["cls"], p["wcls"], p["key"][1], sp, pa, ya, p["ang"][0], p["ang"][1], pa - p["ang"][0], dyaw,
        " ".join("%.1f" % (a - b) for a, b in zip(p["pos"], p["eye"]))))
    pts = p["path"]
    if len(pts) >= 3:
        t0 = pts[0][0]
        # free-flight part: until the speed jumps (bounce / stop) or planted
        free = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            va = math.sqrt(a[4] ** 2 + a[5] ** 2 + a[6] ** 2)
            vb = math.sqrt(b[4] ** 2 + b[5] ** 2 + b[6] ** 2)
            dt = b[0] - a[0]
            if b[7] == "1" or vb < 1 or (dt > 0 and abs(vb - va) / dt > 3000):
                break
            free.append(b)
        ts = [q[0] - t0 for q in free]
        # the first server frame of a projectile already covers more than one frame of flight
        # (wp_a Cold War: 0.176 s in the first 0.1 s frame), so use frame-to-frame differences
        # from the second sample on
        gs = sorted(-(b[6] - a[6]) / (b[0] - a[0]) for a, b in zip(free[1:], free[2:]) if b[0] > a[0])
        g = gs[len(gs) // 2] if gs else float("nan")
        sps = sorted(math.dist(a[1:4], b[1:4]) / (b[0] - a[0]) for a, b in zip(free[1:], free[2:]) if b[0] > a[0])
        vz_fit = sps[len(sps) // 2] if sps else float("nan")
        if len(free) > 1 and sp > 0 and free[1][0] > free[0][0]:
            adv = math.dist(free[0][1:4], free[1][1:4]) / sp
            lines.append("    first frame covers %.3f s of flight (frame %.3f s)" % (adv, free[1][0] - free[0][0]))
        hs0 = math.hypot(free[0][4], free[0][5])
        hs1 = math.hypot(free[-1][4], free[-1][5])
        vz = [q[6] for q in free]
        gz = (vz[0] - vz[-1]) / (ts[-1] - ts[0]) if len(free) > 1 and ts[-1] > ts[0] else float("nan")
        # lateral drift: distance of the path from the launch line in the horizontal plane
        ux, uy = math.cos(math.radians(p["ang"][1])), math.sin(math.radians(p["ang"][1]))
        lat = [(q[1] - free[0][1]) * -uy + (q[2] - free[0][2]) * ux for q in free]
        along = [(q[1] - free[0][1]) * ux + (q[2] - free[0][2]) * uy for q in free]
        lines.append("    free %d frames %.3f s: g(median dvz)=%.1f g(vz first-last)=%.1f speed(median dpos)=%.1f hspeed %.1f -> %.1f along %.0f lateral max %.1f last %.1f" % (
            len(free), ts[-1], g, gz, vz_fit, hs0, hs1, along[-1], max(lat, key=abs), lat[-1]))
        if len(free) < len(pts):
            b = pts[len(free)]
            lines.append("    stop/bounce at t+%.3f pos %.1f %.1f %.1f vel %.1f %.1f %.1f planted %s" % (
                b[0] - t0, b[1], b[2], b[3], b[4], b[5], b[6], b[7]))
    if p["end"]:
        e = p["end"]
        lines.append("    end t+%.3f at %.1f %.1f %.1f (%d samples)" % (e[0] - p["key"][1], e[1], e[2], e[3], len(pts)))
    return lines


def main():
    run = Path(sys.argv[1])
    frames = "--frames" in sys.argv
    ev = parse(run / "diag.tsv")
    cmds, segs = segments(ev)
    wc = wc_rows(ev)
    cr = c_rows(ev)
    for name, t0, t1, st in segs:
        if name == "-":
            continue
        off = (st - t0) if st is not None else 0.0
        print("== %s  client %.3f-%.3f  clock(server-client) %+.3f" % (name, t0, min(t1, 1e8), off))
        seg = [r for r in wc if t0 <= r["t"] < t1]
        if not seg:
            print("  (no WC rows)")
            continue
        print("  weapon %s clip %d stock %d" % (seg[0]["w"], seg[0]["clip"], seg[0]["stock"]))
        segcmds = [(t, c) for t, c in cmds if t0 <= t < t1]
        shots = [b for a, b in zip(seg, seg[1:]) if b["clip"] < a["clip"] and b["w"] == a["w"]]
        if shots:
            ts = [s["t"] for s in shots]
            first_attack = next((t for t, c in segcmds if c == "+attack"), None)
            print("  shots %d at %s" % (len(shots), " ".join("%.4f" % (t - t0) for t in ts)))
            if len(ts) > 1:
                print("  intervals %s" % " ".join("%.4f" % (b - a) for a, b in zip(ts, ts[1:])))
            if first_attack is not None:
                print("  first shot %.4f s after +attack" % (ts[0] - first_attack))
            print("  clip drops %s" % " ".join(str(a["clip"] - b["clip"]) for a, b in zip(seg, seg[1:]) if b["clip"] < a["clip"]))
            print("  spread at shots %s" % " ".join("%.3f" % s["spread"] for s in shots[:12]))
            # view change around the shots (C lines)
            before = [c for c in cr if ts[0] - 0.06 <= c["t"] < ts[0]]
            after = [c for c in cr if ts[-1] + 0.55 <= c["t"] < ts[-1] + 0.65]
            if before and after:
                print("  view change pitch %+.3f yaw %+.3f (before first shot -> 0.6 s after last)" % (
                    after[0]["pitch"] - before[-1]["pitch"], after[0]["yaw"] - before[-1]["yaw"]))
        # ready-to-fire transitions (deploy / raise / reload unlock)
        for a, b in zip(seg, seg[1:]):
            if a["ready"] != b["ready"]:
                print("  ready %d->%d at %.4f (clip %d rel %d)" % (a["ready"], b["ready"], b["t"] - t0, b["clip"], b["rel"]))
        sp = [r["spread"] for r in seg]
        print("  spread min %.3f max %.3f last %.3f" % (min(sp), max(sp), sp[-1]))
        # reload
        for a, b in zip(seg, seg[1:]):
            if b["rel"] and not a["rel"]:
                start = b["t"]
                endr = next((r["t"] for r in seg if r["t"] > start and not r["rel"]), None)
                refill = next((r for r in seg if r["t"] > start and r["clip"] > b["clip"]), None)
                print("  reload start %.4f (clip %d) refill %s end %s" % (
                    start - t0, b["clip"],
                    "+%.4f -> %d" % (refill["t"] - start, refill["clip"]) if refill else "none",
                    "+%.4f" % (endr - start) if endr else "not in segment"))
        # zoom
        for t, c in segcmds:
            if c in ("+zoom", "-zoom"):
                after = [r for r in wc if r["t"] >= t]
                if not after:
                    continue
                z0 = after[0]["zoom"]
                marks = {}
                for r in after:
                    if r["t"] > t + 2.0:
                        break
                    for thr in (0.5, 0.99) if c == "+zoom" else (0.5, 0.01):
                        hit = r["zoom"] >= thr if c == "+zoom" else r["zoom"] <= thr
                        if hit and thr not in marks:
                            marks[thr] = r["t"] - t
                print("  %s at %.4f: zoomfrac from %.3f, %s" % (c, t - t0, z0, " ".join("%g@%.4f" % (k, v) for k, v in sorted(marks.items()))))
        sm = [r for r in seg if r["smn"] > 0]
        if sm:
            locked = next((r for r in sm if r["smf"] >= 1.0), None)
            print("  smart ammo: first target %.4f, full lock %s, max targets %d" % (
                sm[0]["t"] - t0, "%.4f" % (locked["t"] - t0) if locked else "never", max(r["smn"] for r in sm)))
        for p in projectiles(ev, t0 + off, t1 + off):
            for ln in describe_proj(p):
                print(ln)
        for r in ev["WDMG"]:
            t = float(r[0])
            if t0 + off <= t < t1 + off:
                print("  hit " + " ".join(r))
        if frames:
            for r in seg:
                print("   WC %.4f clip %d rel %d zoom %.3f spread %.3f charge %.3f ready %d burst %d sm %d %.2f" % (
                    r["t"] - t0, r["clip"], r["rel"], r["zoom"], r["spread"], r["charge"], r["ready"], r["burst"], r["smn"], r["smf"]))
    for k in ("WPT", "WPAMMO", "WP", "INFO", "WEAPON", "NPC"):
        for r in ev[k]:
            print(k, " ".join(r))


if __name__ == "__main__":
    main()
