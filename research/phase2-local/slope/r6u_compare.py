#!/usr/bin/env python3
"""R6U: R5 vs Unity Reference before / after the slope changes U-1..U-4 (SLOPE-SLIDE.md "修改建议").

Reads slope_analysis.py result files (same R5 trials, Unity runs of the harness with different rule sets) and prints Markdown tables:
uphill (ramp entry speed, distance up the slope at the slide end), joints (speed change -0.1 s -> +0.1 s), rest height and step ratio
on the slope, re-boosts (time since the slide start, speeds), lateral slide end.

  py -3 r6u_compare.py before=<res.json> after=<res.json> [more=<res.json> ...]
"""
import json
import sys


def load(arg):
    name, path = arg.split("=", 1)
    return name, json.load(open(path, encoding="utf-8"))


def mean(st):
    return None if not st else st.get("mean")


def f(v, d=1):
    return "–" if v is None else ("%." + str(d) + "f") % v


def cond(res, side, sched):
    return res["cond_" + side].get("r6_" + sched)


def main():
    runs = [load(a) for a in sys.argv[1:]]
    names = [n for n, _ in runs]
    first = runs[0][1]
    hdr = " | ".join(["R5"] + names)
    sep = "|".join(["---"] * (len(names) + 2))

    print("## Uphill slide (10/20/30/40 deg): ramp entry speed, distance up the slope at the slide end\n")
    print("| condition | entry " + " / ".join(["R5"] + names) + " | distance " + " / ".join(["R5"] + names) + " |")
    print("|---|---|---|")
    for th in (10, 20, 30, 40):
        for kind in ("slide", "jump"):
            s = "up%d_%s" % (th, kind)
            r5 = cond(first, "r5", s)
            e = [mean(r5.get("entry_h"))] + [mean(cond(r, "unity", s).get("entry_h")) for _, r in runs]
            d = [mean(r5.get("end_up_slope"))] + [mean(cond(r, "unity", s).get("end_up_slope")) for _, r in runs]
            print("| %s | %s | %s |" % (s, " / ".join(f(x) for x in e), " / ".join(f(x) for x in d)))

    print("\n## Joints: speed change -0.1 s -> +0.1 s (" + hdr + ")\n")
    print("| condition | joint | " + hdr + " |")
    print("|" + sep + "|---|")
    for s in ("dn5_slide", "dn10_slide", "dn15_slide", "dn20_slide", "dn25_slide", "dn30_slide", "v20_slide", "crest_slide", "up20_slide", "up40_slide"):
        r5 = cond(first, "r5", s)
        for j, tr in enumerate(r5.get("transitions", [])):
            vals = [mean(tr["dh_m01_p01"])]
            for _, r in runs:
                u = cond(r, "unity", s)["transitions"]
                vals.append(mean(u[j]["dh_m01_p01"]) if j < len(u) else None)
            print("| %s | %+d -> %+d | %s |" % (s, tr["from_deg"], tr["to_deg"], " | ".join(f(v) for v in vals)))

    print("\n## On the slope: horizontal step / (|v_h| dt) and origin above the plane (" + hdr + ")\n")
    print("| slope | kind | ratio " + " / ".join(["R5"] + names) + " | height " + " / ".join(["R5"] + names) + " |")
    print("|---|---|---|---|")
    key = lambda q: (q["slope_deg"], q["kind"])  # noqa: E731
    r5m = {key(q): q for q in first["move_r5"]}
    um = [{key(q): q for q in r["move_unity"]} for _, r in runs]
    for k in sorted(r5m):
        if k[1] not in ("up", "down"):
            continue
        rat = [r5m[k]["ratio"]] + [u.get(k, {}).get("ratio") for u in um]
        dz = [r5m[k]["dz_on_slope"]] + [u.get(k, {}).get("dz_on_slope") for u in um]
        print("| %d | %s | %s | %s |" % (k[0], k[1], " / ".join(f(x, 4) for x in rat), " / ".join(f(x, 2) for x in dz)))

    print("\n## Re-boosts (first per trial): time since the slide start, speed before -> after\n")
    print("| condition | " + hdr + " |")
    print("|" + sep + "|")

    def rb(c):
        out = []
        for b in c.get("reboosts", []):
            if b["since_slide_start"] is None or b["since_slide_start"] < 0.05:
                continue
            out.append("%.2f s %.0f→%.0f" % (b["since_slide_start"], b["h0"], b["h1"]))
        # one per trial: the analysis lists every trial's boosts; collapse identical strings
        uniq = []
        for x in out:
            if x not in uniq:
                uniq.append(x)
        return "; ".join(uniq[:4]) + (" …" if len(uniq) > 4 else "") if uniq else "none"

    for s in ("dn15_slide", "dn20_slide", "dn25_slide", "dn30_slide", "v20_slide", "crest_slide", "lat20_slide", "diag20d_slide", "diag20u_slide"):
        cells = [rb(cond(first, "r5", s))] + [rb(cond(r, "unity", s)) for _, r in runs]
        print("| %s | %s |" % (s, " | ".join(cells)))

    print("\n## Lateral / diagonal 20 deg: slide time, end speed, downhill drift (" + hdr + ")\n")
    print("| condition | slide time | end speed | drift |")
    print("|---|---|---|---|")
    for s in ("lat20_slide", "diag20d_slide", "diag20u_slide"):
        cs = [cond(first, "r5", s)] + [cond(r, "unity", s) for _, r in runs]
        print("| %s | %s | %s | %s |" % (s, " / ".join(f(mean(c.get("slide_t")), 2) for c in cs),
                                         " / ".join(f(mean(c.get("end_h"))) for c in cs), " / ".join(f(mean(c.get("dx_downhill"))) for c in cs)))


if __name__ == "__main__":
    main()
