#!/usr/bin/env python3
"""A3: what real key presses switch (fire mode / hop-up, variable optic zoom).
  py -3 -I analyze_a3.py <frames.csv> <marks.tsv> <runs_dir> <out_dir>
A3-EVENTS.tsv: per key / wheel step: zf and FOV just before, lowest zf and FOV range in the next 0.65 s, zf and FOV at +0.65 s,
the server mods read just before and just after (the 'mods' steps), and the view pitch excursion (the fire-mode switch motion).
A3-BURSTS.tsv: per 0.6 s hold of +attack: rounds fired (clip drop from the server log)."""
import csv, os, re, sys
from collections import defaultdict


def main():
    frames, marks, runs, out = sys.argv[1:5]
    mk = defaultdict(list)
    for l in open(marks, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if p[0].startswith("a3"):
            mk[p[0]].append((float(p[1]) * 1000, p[2], p[3] if len(p) > 3 else ""))
    fr = [r for r in csv.DictReader(open(frames)) if r["w"]]
    eo = open(os.path.join(out, "A3-EVENTS.tsv"), "w", encoding="utf-8")
    eo.write("run\tt\tevent\tmods_before\tmods_after\tzf_before\tfov_before\tzf_min_0.65s\tfov_min_0.65s\tfov_max_0.65s\tzf_+0.65s\tfov_+0.65s\tviewP_minus_aimP_range\n")
    bo = open(os.path.join(out, "A3-BURSTS.tsv"), "w", encoding="utf-8")
    bo.write("run\thold_n\tmods_before\trounds\n")
    for tag, m in mk.items():
        t0 = m[0][0]
        mods = [(x[0], re.sub(r"^\S+ mods=", "", x[2]).split(" zf=")[0]) for x in m if x[1] == "mods"]
        def mods_at(w, after):
            c = [x for x in mods if (x[0] > w if after else x[0] < w)]
            return (c[0] if after else c[-1])[1] if c else ""
        for x in m:
            if x[1].startswith(("key", "wheel", "rclick")):
                w = x[0]
                pre = [r for r in fr if w - 60 <= float(r["w"]) < w]
                post = [r for r in fr if w <= float(r["w"]) <= w + 650]
                if not pre or not post: continue
                d = [float(r["fP"]) - float(r["bP"]) for r in post]
                eo.write("\t".join([tag, f"{(w - t0) / 1000:.3f}", x[1], mods_at(w, False), mods_at(w, True), pre[-1]["zf"], pre[-1]["fov"],
                                    f"{min(float(r['zf']) for r in post):.3f}", f"{min(float(r['fov']) for r in post):.2f}", f"{max(float(r['fov']) for r in post):.2f}",
                                    post[-1]["zf"], post[-1]["fov"], f"{min(d):.3f}..{max(d):.3f}"]) + "\n")
        # rounds per hold, from the server clip log (times relative to the snippet start, so pair holds in order)
        txt = open(os.path.join(runs, tag + ".txt"), encoding="utf-8").read()
        clip = [(float(a), int(b)) for a, b in re.findall(r"\[RT\] clip t=([\d.]+) c=(\d+)", txt)]
        holds = [x[0] for x in m if x[1] == "+attack"]
        if holds and clip:
            # offset: first clip drop belongs to the first hold
            drops = [c for c in clip[1:]]
            off = holds[0] / 1000 - (t0 / 1000) - drops[0][0] if drops else 0
            for n, h in enumerate(holds):
                hs = (h - t0) / 1000 - off
                c_before = [c for t, c in clip if t < hs - 0.01]
                c_after = [c for t, c in clip if t < hs + 1.1]
                r = (c_before[-1] - c_after[-1]) if c_before and c_after else ""
                bo.write(f"{tag}\t{n + 1}\t{mods_at(h, False)}\t{r}\n")
    eo.close(); bo.close()
    print(open(os.path.join(out, "A3-EVENTS.tsv")).read()); print(open(os.path.join(out, "A3-BURSTS.tsv")).read())


if __name__ == "__main__":
    main()
