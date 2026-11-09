"""L-3 / L-4 / L-5 from an ai_percept run.

notice_<case>: t0 = "AI sense <eh> 1" line; then for that NPC (ehandle):
  see    first NSEE 1          (npc.CanSee( player ))
  enemy  first NENEMY player   (player became its enemy)
  combat first NSTATE combat
  turn   first NP line whose yaw is within 15 deg of the direction to the player
  shot   first NSHOT
hide<i>: t0 = TAG hide<i>; for the NPC alive then: NSEE 0, last NSHOT, NENEMY none, NSTATE changes, schedules.
usage: python -I analyze_percept.py <run dir>
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_ai import load, segments  # noqa: E402


def first(rows, kind, eh, t0, t1, pred=lambda r: True):
    for r in rows:
        if r[0] == kind and r[2] == eh and t0 <= float(r[1]) < t1 and pred(r):
            return float(r[1]) - t0
    return None


def fmt(x):
    return "-" if x is None else "%.2f" % x


def main(run):
    rows = load(run)
    segs = segments(rows)
    pst = [r for r in rows if r[0] == "PST"]
    out = ["case\tsee\tenemy\tcombat\tturn\tshot  (s after senses on)"]
    for name, t0, t1 in segs:
        if not name.startswith("notice_"):
            continue
        sense = next((r for r in rows if r[0] == "AI" and r[1] == "sense" and t0 - 0.2 <= float(r[4]) < t1), None)
        if not sense:
            out.append(name + "\tno sense line")
            continue
        eh, ts = sense[2], float(sense[4])
        p = next((q for q in pst if float(q[1]) >= ts), None)

        def facing(r):
            if not p:
                return False
            want = math.degrees(math.atan2(float(p[3]) - float(r[5]), float(p[2]) - float(r[4])))
            d = (float(r[7]) - want + 180) % 360 - 180
            return abs(d) < 15
        out.append("%s\t%s\t%s\t%s\t%s\t%s" % (
            name[7:], fmt(first(rows, "NSEE", eh, ts, t1, lambda r: r[4] == "1")),
            fmt(first(rows, "NENEMY", eh, ts, t1, lambda r: r[4] == "player")),
            fmt(first(rows, "NSTATE", eh, ts, t1, lambda r: r[4] == "combat")),
            fmt(first(rows, "NP", eh, ts, t1, facing)), fmt(first(rows, "NSHOT", eh, ts, t1))))
    out.append("")
    out.append("hide\tcansee_lost\tlast_shot\tenemy_none\tstate_changes / schedules (s after hiding)")
    for name, t0, t1 in segs:
        if not name.startswith("hide"):
            continue
        ehs = {r[2] for r in rows if r[0] == "NP" and t0 <= float(r[1]) < t0 + 0.5}
        for eh in ehs:
            shots = [float(r[1]) - t0 for r in rows if r[0] == "NSHOT" and r[2] == eh and t0 <= float(r[1]) < t1]
            ev = ["%s %.2f" % (r[4], float(r[1]) - t0) for r in rows
                  if r[0] in ("NSTATE", "NSCHED") and r[2] == eh and t0 <= float(r[1]) < t1]
            out.append("%s eh%s\t%s\t%s\t%s\t%s" % (
                name, eh, fmt(first(rows, "NSEE", eh, t0, t1, lambda r: r[4] == "0")),
                fmt(max(shots) if shots else None),
                fmt(first(rows, "NENEMY", eh, t0, t1, lambda r: r[4] == "none")), "; ".join(ev[:14])))
    text = "\n".join(out) + "\n"
    (Path(run) / "percept_table.tsv").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1])
