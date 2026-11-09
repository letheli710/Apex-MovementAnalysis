"""L-6 / L-7 summaries of ai_ref_* runs: per ref_<kind> segment, for each NPC alive in it:
path length, mean / max horizontal speed (10 Hz NP), z range above its spawn floor, shots, hits,
time to first shot, top schedules. Elite pilot: frames with z more than 40 u above the floor
(jump / wall run candidates). usage: python -I analyze_ref.py <run dir> ..."""
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ai import load, segments  # noqa: E402


def main(run):
    rows = load(run)
    out = []
    for name, t0, t1 in segments(rows):
        if not name.startswith("ref_"):
            continue
        np_ = defaultdict(list)
        for r in rows:
            if r[0] == "NP" and t0 <= float(r[1]) < t1:
                np_[r[2]].append((float(r[1]), float(r[4]), float(r[5]), float(r[6])))
        cls = {r[2]: r[3] for r in rows if r[0] == "ANPC"}
        cls = {r[2]: r[4] for r in rows if r[0] == "ANPC"}
        for eh, pts in np_.items():
            if len(pts) < 5:
                continue
            path = sum(math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(pts, pts[1:]))
            sp = [math.hypot(b[1] - a[1], b[2] - a[2]) / max(1e-3, b[0] - a[0]) for a, b in zip(pts, pts[1:])]
            z0 = min(p[3] for p in pts)
            zmax = max(p[3] for p in pts)
            high = sum(1 for p in pts if p[3] - z0 > 40)
            shots = sum(int(r[4]) for r in rows if r[0] == "NSHOT" and r[2] == eh and t0 <= float(r[1]) < t1)
            first = next((float(r[1]) - t0 for r in rows if r[0] == "NSHOT" and r[2] == eh and t0 <= float(r[1]) < t1), None)
            hits = sum(1 for r in rows if r[0] == "PDMG" and r[4] == cls.get(eh) and t0 <= float(r[1]) < t1)
            sch = Counter(r[4] for r in rows if r[0] == "NSCHED" and r[2] == eh and t0 <= float(r[1]) < t1)
            out.append("%s %s eh%s: %.1f s, path %.0f u, speed mean %.0f max %.0f u/s, z %.0f..%.0f (%d samples >40 u up), "
                       "shots %d, hits %d (class), first shot %s s; %s" % (
                           name, cls.get(eh, "?"), eh, pts[-1][0] - pts[0][0], path, sum(sp) / len(sp), max(sp), z0, zmax,
                           high, shots, hits, "-" if first is None else "%.2f" % first,
                           ", ".join("%s %d" % kv for kv in sch.most_common(6))))
    text = "\n".join(out) + "\n"
    (Path(run) / "ref_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    for r in sys.argv[1:]:
        main(r)
