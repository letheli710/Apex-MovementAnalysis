"""L-1 hit-rate tables from ai_hit_* runs.

usage: python -I analyze_hit.py <run dir> [<run dir> ...]
For every run: NPC (hsd_npc id 1 / 2 / 3 = near / mid / far spot) x segment (TAG):
  shots      clip drops (NSHOT), = bullets fired
  forced     MISS lines with miss=1 (forced miss decided by the script callback)
  fastshare  share of shots fired while the player counted as a fast pilot
  hits       PDMG lines from that NPC
  hit/shot   all shots;  hit/aimed = hits / (shots - forced)
  dist       mean NPC-player distance at the shots
plus hit/shot over time since the NPCs spawned (warmup), in 3 s bins.
Writes <run>/hit_table.tsv.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ai import load, segments  # noqa: E402

ORDER = ["warmup", "stand", "walk", "sprint", "slide", "wallrun", "air", "stand2"]


def table(run):
    rows = load(run)
    segs = [s for s in segments(rows) if s[0] in ORDER]
    eh2id = {}
    for r in rows:
        if r[0] == "ANPC":
            eh2id[r[2]] = r[3]
    kind = next((r[4] for r in rows if r[0] == "ANPC"), "?")
    weapon = next((r[9].split("=")[1] for r in rows if r[0] == "ANPC" and r[9].startswith("weapon=")), "?")
    spawn_t = min((float(r[1]) for r in rows if r[0] == "ANPC"), default=0.0)
    lethality = next((r[2] for r in rows if r[0] == "AI" and r[1] == "info"), "?")
    cell = defaultdict(lambda: defaultdict(float))
    for name, t0, t1 in segs:
        def seg_of(t):
            return t0 <= t < t1
        for r in rows:
            if r[0] == "NSHOT" and seg_of(float(r[1])):
                c = cell[(r[3], name)]
                n = int(r[4])
                c["shots"] += n
                c["fast"] += n * int(r[18])
                c["dist"] += n * float(r[12])
                c["see"] += n * int(r[19])
            elif r[0] == "PDMG" and seg_of(float(r[1])):
                cell[(r[5], name)]["hits"] += 1
            elif r[0] == "MISS" and seg_of(float(r[1])):
                c = cell[(eh2id.get(r[2], "?"), name)]
                c["calls"] += 1
                c["forced"] += int(r[8])
    out = [f"# {Path(run).name}  npc={kind} weapon={weapon} {lethality}"]
    out.append("id\tsegment\tshots\tcalls\tforced\tfastshare\thits\thit/shot\thit/aimed\tdist\tcansee")
    for i in sorted({k[0] for k in cell if k[0] not in ("?", "-1")}, key=int):
        for name in ORDER:
            c = cell.get((i, name))
            if not c or not c["shots"]:
                continue
            sh = c["shots"]
            aimed = sh - c["forced"]
            out.append("%s\t%s\t%d\t%d\t%d\t%.2f\t%d\t%.3f\t%s\t%.0f\t%.2f" % (
                i, name, sh, c["calls"], c["forced"], c["fast"] / sh, c["hits"], c["hits"] / sh,
                "%.3f" % (c["hits"] / aimed) if aimed > 0 else "-", c["dist"] / sh, c["see"] / sh))
    # focus: warmup + stand shots by time since spawn (all NPCs together, per id)
    bins = defaultdict(lambda: [0, 0])
    warm = [s for s in segs if s[0] == "warmup"]
    if warm:
        _, w0, w1 = warm[0]
        for r in rows:
            if r[0] == "NSHOT" and w0 <= float(r[1]) < w1:
                bins[(r[3], int((float(r[1]) - spawn_t) // 3))][0] += int(r[4])
            elif r[0] == "PDMG" and w0 <= float(r[1]) < w1:
                bins[(r[5], int((float(r[1]) - spawn_t) // 3))][1] += 1
    out.append("id\twarmup_bin_s\tshots\thits\thit/shot")
    for (i, b), (sh, h) in sorted(bins.items(), key=lambda kv: (int(kv[0][0]), kv[0][1])):
        out.append("%s\t%d-%d\t%d\t%d\t%.3f" % (i, b * 3, b * 3 + 3, sh, h, h / sh if sh else 0))
    text = "\n".join(out) + "\n"
    (Path(run) / "hit_table.tsv").write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    for run in sys.argv[1:]:
        print(table(run))
