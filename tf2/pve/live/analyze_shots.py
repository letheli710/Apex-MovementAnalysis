"""Per-shot L-1 table: every NPC bullet (NSHOT) gets
  forced = decision of the latest MISS line of that NPC at or before the shot (the callback is
           re-asked on every aim update, ~0.05 s, so the bullet uses the latest one)
  hit    = a PDMG from that NPC logged within -0.10 … +win s of the shot line (the two logs are up to 0.083 s apart) (hitscan R-201; for projectile
           weapons use a longer window, see --win)
  state  = the player's state logged with the shot (first 12 s after the NPC appeared skipped); distance bin from the logged NPC-player distance.
usage: python -I analyze_shots.py [--win 0.15] <run dir> ...  -> prints and writes <run>/shots_table.tsv
"""
import bisect
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ai import load, segments  # noqa: E402

STATES = ["warmup", "stand", "walk", "sprint", "slide", "wallrun", "air", "stand2"]
SHOT_STATES = ["stand", "walk", "sprint", "slide", "wallrun", "air"]
FOCUS_SKIP = 12.0  # shots in the first 12 s after the NPC appeared are left out (aim cone still focusing, N-2)


def shot_state(r):
    """player state logged with the shot: ground wallrun slide sprint speed"""
    ground, wall, slide, sprint, speed = r[13] == "1", r[14] == "1", r[15] == "1", r[16] == "1", float(r[17])
    if wall:
        return "wallrun"
    if not ground:
        return "air"
    if slide:
        return "slide"
    if speed < 20:
        return "stand"
    return "sprint" if (sprint or speed > 180) else "walk"
MISS_WIN = 0.035
BINS = [(0, 500, "<500"), (500, 1100, "500-1100"), (1100, 9e9, ">1100")]


def dbin(d):
    return next(n for a, b, n in BINS if a <= d < b)


def run_table(run, win):
    rows = load(run)
    segs = [s for s in segments(rows) if s[0] in STATES]
    eh2id = {r[2]: r[3] for r in rows if r[0] == "ANPC"}
    spawn_t = {r[3]: float(r[1]) for r in rows if r[0] == "ANPC"}
    miss = defaultdict(list)
    for r in rows:
        if r[0] == "MISS":
            miss[eh2id.get(r[2], "?")].append((float(r[1]), int(r[8]), int(r[9])))
    hits = defaultdict(list)
    for r in rows:
        if r[0] == "PDMG":
            hits[r[5]].append(float(r[1]))
    used = set()
    cell = defaultdict(lambda: [0, 0, 0, 0, 0])  # shots, forced, hits, hits on aimed, fast
    for r in rows:
        if r[0] != "NSHOT":
            continue
        t, i, n, d = float(r[1]), r[3], int(r[4]), float(r[12])
        seg = next((s[0] for s in segs if s[1] <= t < s[2]), None)
        if seg is None or seg == "warmup" or t - spawn_t.get(i, 0.0) < FOCUS_SKIP:
            continue
        seg = shot_state(r)
        ms = miss.get(i, [])
        ts = [m[0] for m in ms]
        k = bisect.bisect_left(ts, t)
        near = [j for j in (k - 2, k - 1, k, k + 1) if 0 <= j < len(ms) and abs(ms[j][0] - t) <= MISS_WIN]
        # all MISS calls of that NPC within MISS_WIN of the shot line; forced if any of them said miss
        # (the bullet's own call cannot be told apart when two calls fall inside the window)
        forced = 1 if any(ms[j][1] for j in near) else 0
        unclear = len({ms[j][1] for j in near}) > 1
        hit = 0
        for ht in hits.get(i, []):
            if t - 0.1 <= ht <= t + win and (i, ht) not in used and hit < n:
                used.add((i, ht))
                hit += 1
        c = cell[(seg, dbin(d))]
        c[0] += n
        c[1] += forced * n
        c[2] += hit
        c[3] += hit if not forced else 0
        c[4] += n * int(r[18])
    return cell


if __name__ == "__main__":
    args = sys.argv[1:]
    win = 0.05
    if args and args[0] == "--win":
        win = float(args[1])
        args = args[2:]
    total = defaultdict(lambda: [0, 0, 0, 0, 0])
    for run in args:
        for k, v in run_table(run, win).items():
            for j in range(5):
                total[k][j] += v[j]
    lines = ["state\tdist\tshots\tforced\tfast_share\thits\thit/shot\thit/aimed"]
    for s in SHOT_STATES:
        for _, _, b in BINS:
            c = total.get((s, b))
            if not c or not c[0]:
                continue
            aimed = c[0] - c[1]
            lines.append("%s\t%s\t%d\t%d\t%.2f\t%d\t%.3f\t%s" % (s, b, c[0], c[1], c[4] / c[0], c[2], c[2] / c[0],
                         "%.3f" % (c[3] / aimed) if aimed else "-"))
    text = "# runs: " + " ".join(Path(r).name for r in args) + "\n" + "\n".join(lines) + "\n"
    print(text)
    if len(args) == 1:
        (Path(args[0]) / "shots_table.tsv").write_text(text, encoding="utf-8")
