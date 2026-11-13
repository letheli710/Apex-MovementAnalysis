#!/usr/bin/env python3
"""B9: grapple, mantle, Kinetic Loader, Marksman's Tempo. Reads the run logs only (game time on both sides).
  py -3 -I analyze_b9.py <runs dir> <out dir>  ->  B9-STATES.tsv
grapple : pull = client logger frames with horizontal speed > 5; shots = server [RT] atk; zf from [RT] mt / g lines
mantle  : IsMantling window from [RT] mt; shots inside / after it; zf at mantle start, lowest, back to 1
kinetic : server clip changes after the 3rd shot (slide vs stand)
tempo   : server atk intervals"""
import os, re, sys

G = re.compile(r"^\[RT\] g t=([\d.]+) zf=([\d.]+) .*?spd=([\d.]+) vz=(-?[\d.]+) gr=(\d)", re.M)
MT = re.compile(r"^\[RT\] mt t=([\d.]+) m=(\d) zf=([\d.]+) clip=(-?\d+) gr=(\d)", re.M)
AT = re.compile(r"^\[RT\] atk t=([\d.]+)", re.M)
CL = re.compile(r"^\[RT\] clip t=([\d.]+) c=(\d+)", re.M)


def sides(txt):
    s, _, c = txt.partition("## client")
    return s, c


def main():
    rd, out = sys.argv[1:3]
    rows = []
    for fn in sorted(os.listdir(rd)):
        if not fn.startswith("b9_"): continue
        tag = fn[:-4]
        s, c = sides(open(os.path.join(rd, fn), encoding="utf-8").read())
        shots = sorted(set(float(x) for x in AT.findall(s)))
        if tag.startswith(("b9_grapple", "b9_grbase", "b9_grlong")):
            g = [(float(a), float(z), float(sp)) for a, z, sp, _, _ in G.findall(c)]
            mv = [t for t, _, sp in g if sp > 5]
            p0, p1 = (mv[0], mv[-1]) if mv else (float("nan"), float("nan"))
            during = [t for t in shots if p0 <= t <= p1]
            after = [t for t in shots if t > p1]
            zmax = max((z for t, z, _ in g if p0 <= t <= p1), default=float("nan"))
            rows.append([tag, "grapple", len(shots), f"pull {p0:.3f}-{p1:.3f} ({p1 - p0:.2f} s)", f"shots in pull {len(during)}",
                         f"first shot after pull end {(after[0] - p1) if after else float('nan'):.3f} s", f"zf max in pull {zmax:.2f}"])
        elif tag.startswith("b9_mantle"):
            m = [(float(a), int(b), float(z), int(cl), int(gr)) for a, b, z, cl, gr in MT.findall(c)]
            on = [t for t, mm, *_ in m if mm == 1]
            if not on:
                rows.append([tag, "mantle", len(shots), "no IsMantling frame", "", "", ""]); continue
            m0, m1 = on[0], on[-1]
            pre = [t for t in shots if t < m0]; inm = [t for t in shots if m0 <= t <= m1]; post = [t for t in shots if t > m1]
            # wall contact: last pre-mantle frame where the logger speed is still > 150 before dropping
            gl = [(float(a), float(sp)) for a, _, sp, _, _ in G.findall(c)]
            stop = next((t for i, (t, sp) in enumerate(gl[1:], 1) if gl[i - 1][1] > 150 and sp < 20 and t < m0), float("nan"))
            zs = [(t, z) for t, mm, z, *_ in m]
            z_in = min((z for t, z in zs if m0 <= t <= m1), default=float("nan"))
            z_back = next((t for t, z in zs if t > m1 and z >= 0.999), float("nan"))
            rows.append([tag, "mantle", len(shots), f"wall contact {stop:.3f}, IsMantling {m0:.3f}-{m1:.3f} ({m1 - m0:.2f} s)",
                         f"shots before contact {len([t for t in pre if t < stop])}, contact..mantle {len([t for t in pre if t >= stop])}, in mantle {len(inm)}, after {len(post)}",
                         f"first shot after mantle start {(inm[0] - m0) if inm else float('nan'):.3f} s; last shot before contact {(stop - pre[-1]) if pre else float('nan'):.3f} s before",
                         f"zf min in mantle {z_in:.2f}, back to 1 at mantle end + {(z_back - m1) if z_back == z_back else float('nan'):.3f} s"])
        elif tag.startswith("b9_kinetic"):
            cl = [(float(a), int(b)) for a, b in CL.findall(s)]
            rows.append([tag, "kinetic", len(shots), "clip " + " ".join(f"{t:.2f}:{n}" for t, n in cl), "", "", ""])
        elif tag.startswith("b9_tempo"):
            iv = [shots[i + 1] - shots[i] for i in range(len(shots) - 1)]
            rows.append([tag, "tempo", len(shots), "intervals " + " ".join(f"{x:.3f}" for x in iv), "", "", ""])
    with open(os.path.join(out, "B9-STATES.tsv"), "w", encoding="utf-8") as f:
        f.write("run\titem\tserver_shots\twindow\tshots\ttiming\tads\n")
        for r in rows: f.write("\t".join(map(str, r)) + "\n")
    print(len(rows))


if __name__ == "__main__":
    main()
