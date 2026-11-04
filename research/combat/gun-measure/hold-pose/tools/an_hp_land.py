#!/usr/bin/env python3
"""The landing as one curve with its direction: the median over the guns of the muzzle and the gun's angles against standing, every 0.05 s after touching down. And the sign of the turn lag against the turn.
  py -3 -I an_hp_land.py <runs dir> <out dir>
Writes HP-LAND.tsv; prints the turn check."""
import glob, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_hp import load, ang

AX = ("mF", "mR", "mU", "gP", "gY", "gR")


def main():
    runs, out = sys.argv[1:3]
    bins = {}
    for p in glob.glob(os.path.join(runs, "hp_*_jump_*.txt")):
        F, _ = load(p)
        tl = next((b["t"] for a, b in zip(F, F[1:]) if not a["gr"] and b["gr"]), None)
        calm = [r for r in F if not r["spd"] and r["gr"] and tl and r["t"] < tl - 1.2]
        if tl is None or len(calm) < 10: continue
        base = {a: st.median(r[a] for r in calm) for a in AX}
        for r in F:
            k = round((r["t"] - tl) / 0.05)
            if 0 <= k <= 20:
                d = bins.setdefault(k, {}).setdefault(p, {a: [] for a in AX})
                for a in AX: d[a].append(ang(r[a] - base[a]) if a[0] == "g" else r[a] - base[a])
    with open(os.path.join(out, "HP-LAND.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# R5 local hybrid, jump landings at about -280 u/s, every gun twice. Median across runs against standing. Camera frame: F R U in u; gP down, gY left, gR as in HP-POSE, degrees.\nt\t" + "\t".join(AX) + "\truns\n")
        for k in sorted(bins):
            per = bins[k].values()
            f.write(f"{k * 0.05:.2f}\t" + "\t".join(f"{st.median(st.mean(x[a]) for x in per):.3f}" for a in AX) + f"\t{len(bins[k])}\n")
    for name in ("r301", "wingman", "kraber", "p2020"):
        for p in glob.glob(os.path.join(runs, f"hp_{name}_turn*_1.txt")):
            F, K = load(p)
            pts = []
            for a, b in zip(F, F[3:]):
                dt = b["t"] - a["t"]
                if dt > 0:
                    pts.append((ang(b["caY"] - a["caY"]) / dt if "caY" in a else 0, a["gY"], a["mR"]))
            print(os.path.basename(p), "frames", len(F), "keys", K[:4])


if __name__ == "__main__":
    main()
