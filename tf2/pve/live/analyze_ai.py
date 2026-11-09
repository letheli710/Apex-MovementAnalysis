"""Summaries of tf2-ai-live runs (runtime/data/<run>/diag.tsv).

usage: python -I analyze_ai.py <run dir> [--shots] [--events]
Per TAG segment (server time): shots per NPC (NSHOT clip drops and NATK next-attack
moves), hits on the player (PDMG), forced-miss callback calls (MISS) by branch, and the
player state at each shot. Hits are counted by attacker target id (hsd_npc id).
"""
import sys
from collections import defaultdict
from pathlib import Path


def load(run):
    rows = []
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split()
        if len(p) < 2 or p[0] != "HSDDIAG":
            continue
        rows.append(p[1:])
    return rows


def segments(rows):
    """[(name, t0, t1)] from TAG lines (server time)."""
    tags = [(r[1], float(r[2])) for r in rows if r[0] == "TAG" and len(r) >= 3]
    out = []
    for i, (n, t) in enumerate(tags):
        t1 = tags[i + 1][1] if i + 1 < len(tags) else 1e9
        if n != "-":
            out.append((n, t, t1))
    return out


def summary(rows):
    segs = segments(rows)
    shots = [r for r in rows if r[0] == "NSHOT"]
    atks = [r for r in rows if r[0] == "NATK"]
    hits = [r for r in rows if r[0] == "PDMG"]
    miss = [r for r in rows if r[0] == "MISS"]
    for name, t0, t1 in segs:
        inside = lambda r, k=1: t0 <= float(r[k]) < t1  # noqa: E731
        s_by = defaultdict(int)
        a_by = defaultdict(int)
        h_by = defaultdict(int)
        dmg_by = defaultdict(float)
        fast = defaultdict(int)
        dist = defaultdict(list)
        for r in shots:
            if inside(r):
                s_by[r[3]] += int(r[4])
                fast[r[3]] += int(r[4]) * int(r[18])
                dist[r[3]].append(float(r[12]))
        for r in atks:
            if inside(r):
                a_by[r[3]] += 1
        for r in hits:
            if inside(r):
                h_by[r[5]] += 1
                dmg_by[r[5]] += float(r[2])
        m_by = defaultdict(lambda: defaultdict(int))
        for r in miss:
            if inside(r):
                m_by[r[3]][r[4] + ("+miss" if r[8] == "1" else "")] += 1
        ids = sorted(set(s_by) | set(a_by) | set(h_by), key=lambda x: int(x))
        print(f"== {name}  {t0:.2f}-{t1 if t1 < 1e8 else float('nan'):.2f}  ({t1 - t0 if t1 < 1e8 else 0:.1f} s)")
        for i in ids:
            d = dist[i]
            md = sum(d) / len(d) if d else float("nan")
            print(f"   id {i}: shots(clip) {s_by[i]:4d}  atk {a_by[i]:4d}  hits {h_by[i]:4d}  dmg {dmg_by[i]:7.1f}"
                  f"  hit/shot {h_by[i] / s_by[i] if s_by[i] else float('nan'):.3f}"
                  f"  hit/atk {h_by[i] / a_by[i] if a_by[i] else float('nan'):.3f}  fast-shot {fast[i]}  dist {md:.0f}")
        for cls, b in m_by.items():
            print(f"   MISS {cls}: " + ", ".join(f"{k} {v}" for k, v in sorted(b.items())))


if __name__ == "__main__":
    rows = load(sys.argv[1])
    kinds = defaultdict(int)
    for r in rows:
        kinds[r[0]] += 1
    print("lines:", dict(sorted(kinds.items())))
    for r in rows:
        if r[0] in ("AI", "ANPC") or (r[0] == "NPC" and r[1] in ("spawn", "err")):
            print(" ".join(r)[:260])
    summary(rows)
    if "--events" in sys.argv:
        for r in rows:
            if r[0] in ("NENEMY", "NSEE", "NSTATE", "NSCHED", "TAG", "AI"):
                print(" ".join(r))
