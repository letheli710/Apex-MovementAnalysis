#!/usr/bin/env python3
"""From the weapon .txt and springs.txt: each weapon's spring, and the delay + first-order time constant that best fit its return (no R5 run needed; the spring law is checked by the runs).
  py -3 -I fit_table.py <weapons dir> [weapon ...]
A burst leaves x0 at rest; the hot spring holds for hold, fades over fade, then the cold spring takes x back. Fit x0 * exp(-(t-D)/T) over t in 0..T_end by least squares on a grid.
Smooth = time to 63 % of a kick's final height while hot: soft part rises with 1/d, the hard part is instant."""
import math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import springs, step

def keys(path):
    txt = open(path, encoding="utf-8").read().split('"Mods"')[0] if False else open(path, encoding="utf-8").read()
    # top-level values only: stop at the first block that opens mods
    head = txt.split('"Mods"')[0]
    return {a: b for a, b in re.findall(r'"(viewkick_\w+)"\s+"([^"]*)"', head)}

def curve(cold, hot, hold, fade, end=3.0, dt=1 / 240):
    x, v, t, out = -1.0, 0.0, 0.0, []
    while t < end:
        h = 1.0 if t < hold else (max(0.0, 1 - (t - hold) / fade) if fade > 0 else 0.0)
        k = hot[0] + (cold[0] - hot[0]) * (1 - h); d = hot[1] + (cold[1] - hot[1]) * (1 - h)
        x, v = step(x, v, k, d, dt); t += dt; out.append((t, -x))
    return out

def fit(c):
    best = None
    for Di in range(0, 61):
        D = Di * 0.01
        for Ti in range(2, 121):
            T = Ti * 0.01
            e = sum((y - (1.0 if t < D else math.exp(-(t - D) / T))) ** 2 for t, y in c[::8])
            if best is None or e < best[0]: best = (e, D, T)
    return best[1], best[2], math.sqrt(best[0] / len(c[::8]))

def main():
    wd = sys.argv[1]; S = springs(os.path.join(wd, "springs.txt"))
    names = sys.argv[2:] or sorted(f[:-4] for f in os.listdir(wd) if f.startswith("mp_weapon_") and f.endswith(".txt"))
    print("weapon\tmode\tkC\tdC\tkH\tdH\thold\tfade\tsoft\thard\tfrac\tD\tT\trms\tt50\tt10\tSmooth\tscaleDelay\tscaleRate")
    for n in names:
        kv = keys(os.path.join(wd, n + ".txt"))
        s = kv.get("viewkick_spring")
        if not s or s not in S: continue
        C = S[s]; H = S.get(kv.get("viewkick_spring_hot", ""), C)
        hold, fade = float(kv.get("viewkick_spring_cooldown_holdtime", 0)), float(kv.get("viewkick_spring_cooldown_fadetime", 0))
        soft, hard = float(kv.get("viewkick_pitch_softScale", 0)), float(kv.get("viewkick_pitch_hardScale", 0))
        for mode, pre, fk in (("hip", "hipfire", "viewkick_hipfire_weaponFraction"), ("ads", "ADS", "viewkick_ads_weaponFraction")):
            c = (C[pre + "_pitch_springConstant"], C[pre + "_pitch_damping"]); h = (H[pre + "_pitch_springConstant"], H[pre + "_pitch_damping"])
            cv = curve(c, h, hold, fade); D, T, r = fit(cv)
            t50 = next(t for t, y in cv if y <= 0.5); t10 = next(t for t, y in cv if y <= 0.1)
            # kick response with the hot spring: v0 = soft*20, x0 = hard, final height is the peak of x
            x, v = hard, soft * 20.0; pk = abs(x); t = 0; tr = []
            while t < 0.6:
                x, v = step(x, v, h[0], h[1], 1 / 960); t += 1 / 960; tr.append((t, x))
            top = max(y for _, y in tr); sm = next((t for t, y in tr if y >= hard + 0.63 * (top - hard)), float("nan"))
            print(n.replace("mp_weapon_", ""), mode, *[f"{a:g}" for a in (c[0], c[1], h[0], h[1], hold, fade, soft, hard, float(kv.get(fk, 0)))],
                  f"{D:.2f}", f"{T:.2f}", f"{r:.3f}", f"{t50:.3f}", f"{t10:.3f}", f"{sm:.3f}", kv.get("viewkick_scale_valueDecayDelay", ""), kv.get("viewkick_scale_valueDecayRate", ""), sep="\t")

if __name__ == "__main__":
    main()
