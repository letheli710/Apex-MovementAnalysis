"""ref-titan-gait: read a run's diag.tsv into segments (2026-11-09).

Lines used: HSDDIAG CMD <t> <command> (plan commands, client clock), C (client frame: velocity),
GC (client frame: attachments, cycle), GS (server 0.1 s: activity, cycle, speed).
"""
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[4] / "runtime" / "data"
TAGS = ["footL", "footR", "torso", "chest", "head"]


def run_dir(name):
    hits = sorted(p for p in DATA.iterdir() if p.name.endswith(name) or p.name == name)
    return hits[-1]


def load(name):
    d = run_dir(name)
    cmds, C, GC, GS, other = [], [], [], [], []
    for line in (d / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) < 3:
            continue
        k = p[1]
        try:
            if k == "CMD":
                cmds.append((float(p[2]), " ".join(p[3:])))
            elif k == "C" and len(p) >= 18:
                C.append(dict(t=float(p[2]), o=tuple(map(float, p[3:6])), v=tuple(map(float, p[6:9])),
                              yaw=float(p[10]), ground=p[11] == "1"))
            elif k == "GC":
                r = dict(t=float(p[2]), o=tuple(map(float, p[3:6])), cyc=None if p[6] == "-" else float(p[6]))
                vals = p[7:]
                for i, tg in enumerate(TAGS):
                    xyz = vals[3 * i:3 * i + 3]
                    r[tg] = None if "-" in xyz else tuple(map(float, xyz))
                a = vals[15:18]
                r["tang"] = None if "-" in a else tuple(map(float, a))
                for key, sl in (("lang", vals[18:21]), ("rang", vals[21:24])):
                    r[key] = None if (len(sl) < 3 or "-" in sl) else tuple(map(float, sl))
                GC.append(r)
            elif k == "GS":
                GS.append(dict(t=float(p[2]), act=int(p[4]), cyc=float(p[5]), spd=float(p[6])))
            else:
                other.append(line)
        except (ValueError, IndexError):
            other.append(line)
    return dict(dir=d, cmds=cmds, C=C, GC=GC, GS=GS, other=other)


def tag_windows(run):
    """[(tag, t_start, t_end)] from hsd_tag commands (end = next hsd_tag)"""
    tags = [(t, c.split()[1]) for t, c in run["cmds"] if c.startswith("hsd_tag ")]
    out = []
    for i, (t, name) in enumerate(tags):
        end = tags[i + 1][0] if i + 1 < len(tags) else 1e9
        if name != "-":
            out.append((name, t, end))
    return out


def cmd_time(run, text, after=0.0):
    for t, c in run["cmds"]:
        if t >= after and c == text:
            return t
    return None


def speed2d(v):
    return math.hypot(v[0], v[1])


def between(rows, t0, t1):
    return [r for r in rows if t0 <= r["t"] < t1]


def anim_updates(G):
    """keep only the frames where the body pose was re-evaluated. The local titan's body (not drawn
    in first person) is re-posed about every 7th client frame (~0.049 s, ~20 Hz; run gait_smoke);
    in between, attachments keep their offset from the origin and the cycle does not change."""
    out, prev = [], None
    for g in G:
        if g["footL"] is None:
            continue
        rel = [g[tg][k] - g["o"][k] for tg in ("footL", "footR", "torso") for k in range(3)]
        if prev is None or g["cyc"] != prev[1] or max(abs(a - b) for a, b in zip(rel, prev[0])) > 0.05:
            out.append(g)
            prev = (rel, g["cyc"])
    return out
