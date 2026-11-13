"""Walk retarget numbers from one TitanWalkFilm style folder (body.tsv, feet.tsv, steps.tsv, slide.tsv): WALK-RETARGET-PLAN.md section 5.
py -3 walk_stats.py <style folder> [<style folder> ...]   (e.g. .../g1_walk/heavy)
Slide: TitanWalkFilm's own measure (slide.tsv); where it happens: per frame slide by the planted foot's ankle state.
Ankle: frames of a planted foot at the -35 limit (<= -34.9) and the worst planted ankle; reach miss: body ikMiss.
Steps: footstep spacing during the steady walk (2-6 s after the start)."""
import csv
import json
import os
import sys


def table(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def stats(d):
    body, feet, steps = table(os.path.join(d, "body.tsv")), table(os.path.join(d, "feet.tsv")), table(os.path.join(d, "steps.tsv"))
    slide = dict(l.strip().split("\t") for l in open(os.path.join(d, "slide.tsv"), encoding="utf-8") if "\t" in l)
    R = {k: float(v) for k, v in slide.items()}
    at_lim = 0
    worst = 99.0
    slide_at_lim = slide_all = 0.0
    for b, f in zip(body, feet):
        for s in "LR":
            sl = float(b["slide" + s])
            slide_all += sl
            if f["mode" + s] == "Planted":
                a = float(f["anklePitch" + s])
                worst = min(worst, a)
                if a <= -34.9:
                    at_lim += 1
                    slide_at_lim += sl
    parts = {"start": 0.0, "walk": 0.0, "stop": 0.0}
    for bb in body:
        t = float(bb["t"])
        k = "start" if t < 1.6 else "stop" if t > 7.0 else "walk"
        parts[k] += float(bb["slideL"]) + float(bb["slideR"])
    R["slide_m_start_walk_stop"] = [round(parts[k], 3) for k in ("start", "walk", "stop")]
    R["planted_ankle_at_limit_frames"] = at_lim
    R["planted_ankle_worst_deg"] = round(worst, 2)
    R["slide_share_at_ankle_limit"] = round(slide_at_lim / slide_all, 3) if slide_all else 0
    R["ik_miss_max_m"] = round(max(float(b["ikMiss"]) for b in body), 4)
    ts = [float(s["t"]) for s in steps]
    steady = [b - a for a, b in zip(ts, ts[1:]) if 3.0 <= a <= 7.0]
    R["steps"] = len(ts)
    R["step_s_steady"] = round(sum(steady) / len(steady), 3) if steady else None
    pz = [float(b["pelZ"]) for b in body if 3.0 <= float(b["t"]) <= 7.0]
    if pz:
        R["pelvis_bob_m"] = round(max(pz) - min(pz), 3)
        R["pelvis_low_m"] = round(min(pz), 3)
    return R


if __name__ == "__main__":
    out = {}
    for d in sys.argv[1:]:
        out[d] = stats(d)
        print(d)
        print("  " + json.dumps(out[d]))
