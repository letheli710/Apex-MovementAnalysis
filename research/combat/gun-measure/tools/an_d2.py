#!/usr/bin/env python3
"""D, second pass over the runs: damage against distance and hit group from every run that hit, first-shot drop only, last rows of the long clips.
  py -3 -I an_d2.py <runs dir> <out prefix>
Log order gives the shot: a dmg line comes before the clip line of the same shot, so the number of clip drops seen so far is the shot index."""
import glob, math, os, re, statistics as st, sys
from collections import defaultdict

RD = re.compile(r"\[RT\] dmg t=[\d.]+ amt=([\d.]+) hg=(\d+) src=\d+ dist=([\d.]+) type=\d+ pos=([-\d.]+),([-\d.]+),([-\d.]+)")
RC = re.compile(r"\[RT\] clip t=\S+ c=(-?\d+) ammo=\S+ reload=\S+ adsf=\S+ active=\S+ ea=([-\d.]+),([-\d.]+) eo=([-\d.]+),([-\d.]+),([-\d.]+)")
BUCKET = (0, 500, 1000, 1500, 2500, 3500, 5000, 99999)


def shots(path):
    """Yield (shot index from 0, amt, hg, dist, x, y, z), plus the run's pitch and eye."""
    out, seen, first = [], 0, None
    for l in open(path, encoding="utf-8"):
        c = RC.search(l)
        if c:
            if first is None: first = c
            else: seen += 1
            continue
        d = RD.search(l)
        if d: out.append((seen, float(d[1]), int(d[2]), float(d[3]), float(d[4]), float(d[5]), float(d[6])))
    return out, first


def main():
    runs, pre = sys.argv[1:3]
    amt = defaultdict(lambda: defaultdict(list))
    first = []
    for p in sorted(glob.glob(os.path.join(runs, "*.txt"))):
        t = os.path.basename(p)[:-4]
        g = re.match(r"(df|dg|dp|sd)_(\w+?)(?:_(\d+|head|leg))?$", t)
        if not g: continue
        H, c = shots(p)
        for s, a, hg, d, *_ in H:
            b = max(x for x in BUCKET if x <= d)
            amt[g[2]][(hg, b)].append(a)
        if c and g[1] in ("df", "dp") and g[3] and g[3].isdigit():
            pitch = float(c[2]); pitch = pitch - 360 if pitch > 180 else pitch
            ex, ey, ez = float(c[4]), float(c[5]), float(c[6])
            for s, a, hg, d, x, y, z in H:
                if s == 0 and g[2] not in ("eva8", "mastiff"):
                    X = x - ex
                    first.append(dict(tag=t, gun=g[2], x=X, rise_deg=math.degrees(math.atan2(z - ez, X)) + pitch, drop_u=X * math.tan(math.radians(-pitch)) - (z - ez), y=y - ey))
    with open(pre + "-DAMAGE-BY-DIST.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("gun\thit_group\tdist_from\tamount_values\thits\n")
        for g, v in amt.items():
            for (hg, b), a in sorted(v.items()):
                f.write(f"{g}\t{hg}\t{b}\t{','.join(str(x) for x in sorted(set(a)))}\t{len(a)}\n")
    with open(pre + "-DROP-FIRST.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("tag\tgun\tx\trise_deg\tdrop_u\ty\n")
        for r in first:
            f.write(f"{r['tag']}\t{r['gun']}\t{r['x']:.1f}\t{r['rise_deg']:.3f}\t{r['drop_u']:.2f}\t{r['y']:.2f}\n")
    for g in sorted({r["gun"] for r in first}):
        w = [r for r in first if r["gun"] == g]
        print(g, f"n={len(w)} rise_deg mean={st.mean(r['rise_deg'] for r in w):.3f} sd={st.pstdev(r['rise_deg'] for r in w):.3f} far:", " ".join(f"{r['x']:.0f}:{r['drop_u']:.1f}" for r in sorted(w, key=lambda r: r["x"]) if r["x"] > 1400))
    print("--- amounts by gun, hit group: value set across all distances")
    for g, v in amt.items():
        H = defaultdict(set)
        for (hg, b), a in v.items(): H[hg].update(a)
        D = defaultdict(set)
        for (hg, b), a in v.items(): D[b].update(a)
        print(g, {k: sorted(x) for k, x in sorted(H.items())}, "maxdist", max(b for _, b in v))


if __name__ == "__main__":
    main()
