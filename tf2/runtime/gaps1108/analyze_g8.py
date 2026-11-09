"""GAPS-1108 analysis: python -I analyze_g8.py <run dir> [family ...]
Reads diag.tsv (client frames HSDDIAG C, plan commands HSDDIAG CMD with client time) and prints one
block per trial. Families: dj (A6), rp (A5), ow (A4), wo (A1), wh (B), wr (B4), ga (D1), tk (D2), aw (D3), info."""
import math
import sys
from pathlib import Path

COLS = "t ox oy oz vx vy vz pitch yaw ground wallrun wallhang crouch fwd side buttons".split()


def load(run):
    frames, cmds, other = [], [], []
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) < 2:
            continue
        if p[1] == "C" and len(p) >= 18:
            try:
                frames.append({k: float(v) for k, v in zip(COLS, p[2:18])})
            except ValueError:
                pass
        elif p[1] == "CMD":
            cmds.append((float(p[2]), " ".join(p[3:])))
        else:
            other.append(line)
    return frames, cmds, other


def trials(frames, cmds):
    """tag name -> (start, end, frames, cmds) by the client time of each hsd_tag command"""
    tags = [(t, c.split()[1]) for t, c in cmds if c.startswith("hsd_tag ")]
    out = {}
    for i, (t0, name) in enumerate(tags):
        t1 = tags[i + 1][0] if i + 1 < len(tags) else 1e9
        out[name] = (t0, t1, [f for f in frames if t0 <= f["t"] < t1], [(t, c) for t, c in cmds if t0 <= t < t1])
    return out


def h(f):
    return math.hypot(f["vx"], f["vy"])


def first(fr, cond, after=-1e9):
    for f in fr:
        if f["t"] >= after and cond(f):
            return f
    return None


def teleports(fr, jump=40.0):
    """frames right after a position jump > jump u between consecutive frames"""
    return [b for a, b in zip(fr, fr[1:]) if math.dist((a["ox"], a["oy"], a["oz"]), (b["ox"], b["oy"], b["oz"])) > jump]


def fmt(f, keys=("t", "ox", "oy", "oz", "vx", "vy", "vz", "ground", "wallrun", "wallhang")):
    return " ".join("%s=%.3f" % (k, f[k]) if k == "t" else "%s=%.1f" % (k, f[k]) if k not in ("ground", "wallrun", "wallhang") else "%s=%d" % (k, f[k]) for k in keys)


def dj(tr):
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith("dj_"):
            continue
        # double jump = airborne frame where vz rises by > 40 between frames
        hits = [(a, b) for a, b in zip(fr, fr[1:]) if not b["ground"] and not a["ground"] and b["vz"] - a["vz"] > 40]
        take = first(fr, lambda f: f["vz"] > 150 and not f["ground"])
        print("%-10s take-off vz %s" % (name, "%.1f" % take["vz"] if take else "-"))
        for a, b in hits:
            print("    double jump at %.3f: vz %.1f -> %.1f (+%.1f); h %.1f -> %.1f; z %.1f" % (b["t"], a["vz"], b["vz"], b["vz"] - a["vz"], h(a), h(b), b["oz"]))
        apex = max(fr, key=lambda f: f["oz"]) if fr else None
        if apex:
            print("    apex z %.1f at %.3f" % (apex["oz"], apex["t"]))


def wall_jump_frame(fr):
    for a, b in zip(fr, fr[1:]):
        if a["wallrun"] and not b["wallrun"] and b["vx"] - a["vx"] > 100:
            return a, b
    return None, None


def rp(tr):
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith("rp_"):
            continue
        a, b = wall_jump_frame(fr)
        if not b:
            print("%-10s no wall jump found" % name)
            continue
        print("%-10s wall jump at %.3f: vx %.1f -> %.1f, vy %.1f, vz %.1f" % (name, b["t"], a["vx"], b["vx"], b["vy"], b["vz"]))
        kick = [t for t, c in cm if c.startswith("hsd_kick")]
        if kick:
            print("    kick sent at +%.3f" % (kick[0] - b["t"]))
        for dt in (0.03, 0.06, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.8):
            f = first(fr, lambda f: True, b["t"] + dt)
            if f and not f["ground"]:
                print("    +%.2f vx %7.1f vy %6.1f vz %7.1f x %.1f side %d wallrun %d" % (dt, f["vx"], f["vy"], f["vz"], f["ox"], f["side"], f["wallrun"]))
        if kick:
            k = kick[0]
            seg = [f for f in fr if k - 0.02 <= f["t"] <= k + 0.25]
            print("    around kick: " + "  ".join("%.3f:%.0f" % (f["t"] - b["t"], f["vx"]) for f in seg))


def ow(tr, prefix="ow_"):
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith(prefix):
            continue
        a, b = wall_jump_frame(fr)
        tps = teleports(fr)
        tp = tps[-1] if tps else None
        lift = None
        if prefix == "wo_":
            lift = first(fr, lambda f: not f["ground"])
        start = first(fr, lambda f: f["wallrun"] > 0, tp["t"] if tp else -1e9)
        line = "%-10s" % name
        if b:
            line += " wall jump %.3f" % b["t"]
        if lift:
            line += " left ground %.3f at (%.0f %.0f %.0f)" % (lift["t"], lift["ox"], lift["oy"], lift["oz"])
        if tp:
            line += " teleport %.3f" % tp["t"]
        if start:
            line += " -> wallrun at %.3f (+%.3f after teleport)" % (start["t"], start["t"] - (tp["t"] if tp else 0))
            ref = lift["t"] if lift else (b["t"] if b else None)
            if ref is not None:
                line += ", %.3f after %s" % (start["t"] - ref, "leaving ground" if lift else "wall jump")
        else:
            line += " -> no wallrun"
        print(line)
        if start:
            seg = [f for f in fr if start["t"] - 0.03 <= f["t"] <= start["t"] + 0.5]
            prev = None
            out = []
            for f in seg:
                g = ""
                if prev is not None and f["t"] > prev["t"]:
                    g = "%.0f" % (-(f["vz"] - prev["vz"]) / (f["t"] - prev["t"]))
                out.append("%.3f:vz%.0f:g%s:w%d" % (f["t"] - start["t"], f["vz"], g, f["wallrun"]))
                prev = f
            print("    " + " ".join(out[:40]))


def wh(tr):
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith("wh_"):
            continue
        zoom = [t for t, c in cm if c == "+zoom"]
        unz = [t for t, c in cm if c == "-zoom"]
        z0 = zoom[0] if zoom else None
        st = first(fr, lambda f: f["wallrun"] > 0)
        hang = first(fr, lambda f: f["wallhang"] > 0)
        print("%-10s run start %s zoom %s unzoom %s hang start %s" % (
            name, "%.3f" % st["t"] if st else "-", "%.3f" % z0 if z0 else "-", "%.3f" % unz[0] if unz else "-",
            "%.3f" % hang["t"] if hang else "-"))
        if not hang:
            end = first(fr, lambda f: not f["wallrun"], st["t"] if st else -1e9)
            if end:
                print("    run ended %.3f" % end["t"])
            continue
        hend = first(fr, lambda f: not f["wallhang"], hang["t"])
        stop = first(fr, lambda f: math.hypot(h(f), f["vz"]) < 1.0, hang["t"])
        print("    hang ends %s (%.3f after hang start); speed < 1 at %s" % (
            "%.3f" % hend["t"] if hend else "-", (hend["t"] - hang["t"]) if hend else float("nan"),
            "%.3f (+%.3f)" % (stop["t"], stop["t"] - hang["t"]) if stop else "-"))
        for dt in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 2.9, 3.0, 3.1, 3.25, 3.5, 3.75, 4.0, 4.1, 4.5, 5, 6, 8, 10, 12):
            f = first(fr, lambda f: True, hang["t"] + dt)
            if f and f["t"] < t1:
                print("    +%5.2f z %7.1f vz %7.1f h %6.1f hang %d run %d ground %d" % (dt, f["oz"], f["vz"], h(f), f["wallhang"], f["wallrun"], f["ground"]))


def wr(tr):
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith("wr_"):
            continue
        st = first(fr, lambda f: f["wallrun"] > 0)
        if not st:
            print("%-10s no run" % name)
            continue
        end = first(fr, lambda f: not f["wallrun"], st["t"])
        last = [f for f in fr if f["wallrun"] and f["t"] < (end["t"] if end else 1e9)][-1]
        print("%-10s run %.3f -> %s: %.3f s; at end y %.1f z %.1f vy %.1f vz %.1f ground %d" % (
            name, st["t"], "%.3f" % end["t"] if end else "-", (end["t"] - st["t"]) if end else float("nan"),
            last["oy"], last["oz"], last["vy"], last["vz"], end["ground"] if end else -1))


def info(other):
    for l in other:
        if any(k in l for k in ("G8SET", "G8HINT", "G8WINQ", "G8GO", "G8EDGE done", "HSDDIAG TR", "W2 MODS", "Q ", "INFO", "CLASS")):
            print(l)


def edges(other, n=60):
    rows = [l for l in other if l.startswith("HSDDIAG G8EDGE ") and "done" not in l]
    opened = [l for l in rows if l.split()[8] == "0"]
    print("edges %d, open %d" % (len(rows), len(opened)))
    for l in opened[:n]:
        print("  " + l)


def main():
    run = sys.argv[1]
    fams = sys.argv[2:] or ["info", "dj", "rp", "ow", "wo", "wh", "wr"]
    frames, cmds, other = load(run)
    tr = trials(frames, cmds)
    for fam in fams:
        print("==== " + fam)
        if fam == "info":
            info(other)
        elif fam == "edges":
            edges(other)
        elif fam == "dj":
            dj(tr)
        elif fam == "rp":
            rp(tr)
        elif fam == "ow":
            ow(tr)
        elif fam == "wo":
            ow(tr, "wo_")
        elif fam == "wh":
            wh(tr)
        elif fam == "wr":
            wr(tr)
        elif fam == "ga":
            ga(tr, other)
        elif fam == "tk":
            tk(other)
        elif fam == "aw":
            aw(other)
        elif fam == "win":
            win(tr, other)



def ga(tr, other):
    """D1: horizontal acceleration toward the star in the first air frames after the teleport"""
    stars = [l.split() for l in other if l.startswith("HSDDIAG W2P ") and "gravity" in l]
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith("ga_"):
            continue
        tp = teleports(fr)
        if not tp:
            print(name, "no teleport"); continue
        a0 = tp[-1]
        d = float(name.split("_")[1])
        st = [s for s in stars if abs(float(s[6]) - (-1864 + d)) < 3]
        sp = max(((float(s[5]), float(s[6]), float(s[7])) for s in st), key=lambda q: q[2]) if st else None
        seg = [f for f in fr if a0["t"] <= f["t"] <= a0["t"] + 0.6 and not f["ground"]]
        if len(seg) < 3:
            print(name, "landed at once"); continue
        def at(dt):
            return first(seg, lambda f: True, a0["t"] + dt)
        f1, f2 = at(0.02), at(0.15)
        acc = (f2["vy"] - f1["vy"]) / (f2["t"] - f1["t"]) if f1 and f2 and f2["t"] > f1["t"] else float("nan")
        d3 = math.dist((a0["ox"], a0["oy"], a0["oz"] + 36), sp) if sp else float("nan")
        print("%-8s star %s; player (%.0f %.0f %.0f); 3D dist to centre %.0f; accel y 0.02-0.15 s %.0f; vy at 0.3 s %s; max |v| %.0f" % (
            name, "(%.0f %.0f %.0f)" % sp if sp else "-", a0["ox"], a0["oy"], a0["oz"], d3, acc,
            "%.0f" % at(0.3)["vy"] if at(0.3) else "-", max(math.hypot(h(f), f["vz"]) for f in seg)))


def tk(other):
    for l in other:
        if any(k in l for k in ("W3TICK", "PDMG", "TAG tk", "NDEAD")):
            print(l)


def aw(other):
    for l in other:
        if any(k in l for k in ("NDMG", "NHP", "TAG aw", "NPC spawn", "W2W")) and "W2W" not in l:
            print(l)


def win(tr, other):
    info(other)
    for name, (t0, t1, fr, cm) in tr.items():
        if not name.startswith(("wb_", "wa_", "wn_")):
            continue
        jumps = [(a, b) for a, b in zip(fr, fr[1:]) if b["vz"] - a["vz"] > 40]
        print(name)
        for a, b in jumps[:2]:
            print("    jump %.3f: v (%.1f %.1f %.1f) -> (%.1f %.1f %.1f) at (%.0f %.0f %.0f)" % (b["t"], a["vx"], a["vy"], a["vz"], b["vx"], b["vy"], b["vz"], b["ox"], b["oy"], b["oz"]))
        cross = first(fr, lambda f: f["oy"] > -1476 if name.startswith("wb") else f["oy"] < -1492, fr[0]["t"] + 0.2 if fr else 0)
        if cross:
            print("    crossed window plane at (%.1f %.1f %.1f) v (%.1f %.1f %.1f)" % (cross["ox"], cross["oy"], cross["oz"], cross["vx"], cross["vy"], cross["vz"]))
        else:
            print("    did not cross")


if __name__ == "__main__":
    main()
