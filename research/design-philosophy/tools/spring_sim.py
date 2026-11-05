"""Exact spring replay used for the worked examples in DESIGN-PHILOSOPHY.md.

x'' = -k x - d v per axis (RECOIL-VIEW section 2.1). Each shot: x += hard * kick, v += soft * 20 * kick (section 4).
Heat: +heat per shot, capped at 1, held for `hold` after the last shot, then linear to 0 over `fade`.
k, d are lerped cold -> hot by heat. Zero snap when |x|^2 + |v|^2 < 0.001.
"""
import math


def step(x, v, k, d, dt):
    """Exact solution for constant k, d over dt."""
    if k == 0:
        if d == 0:
            return x + v * dt, v
        e = math.exp(-d * dt)
        return x + v * (1 - e) / d, v * e
    a = d / 2
    disc = k - a * a
    e = math.exp(-a * dt)
    if disc > 1e-9:
        w = math.sqrt(disc)
        c, s = math.cos(w * dt), math.sin(w * dt)
        return e * (x * c + (v + a * x) * s / w), e * (v * c - (a * v + k * x) * s / w)
    if disc < -1e-9:
        w = math.sqrt(-disc)
        c, s = math.cosh(w * dt), math.sinh(w * dt)
        return e * (x * c + (v + a * x) * s / w), e * (v * c - (a * v + k * x) * s / w)
    return e * (x + (v + a * x) * dt), e * (v - a * (v + a * x) * dt)


def run(kicks, rate, cold, hot, hard, soft, hold, fade, heat_per_shot=1.0, dt=1 / 1000, tail=4.0):
    """Returns (trace [(t, punch)], punch just before each shot)."""
    x = v = heat = 0.0
    shot_t = [i / rate for i in range(len(kicks))]
    last = -1e9
    i = 0
    t = 0.0
    tr, at_shot = [], []
    end = shot_t[-1] + tail
    while t < end:
        while i < len(kicks) and t >= shot_t[i] - 1e-9:
            at_shot.append(x)
            x += hard * kicks[i]
            v += soft * 20 * kicks[i]
            heat = min(1.0, heat + heat_per_shot)
            last = t
            i += 1
        since = t - last
        if since <= hold:
            h = heat
        else:
            h = heat * max(0.0, 1 - (since - hold) / fade) if fade > 0 else 0.0
        k = cold[0] + (hot[0] - cold[0]) * h
        d = cold[1] + (hot[1] - cold[1]) * h
        x, v = step(x, v, k, d, dt)
        if x * x + v * v < 0.001:
            x = v = 0.0
        t += dt
        tr.append((t, x))
    return tr, at_shot


def after_stop(tr, stop_t):
    post = [(t, x) for t, x in tr if t >= stop_t]
    pk_t, pk = max(post, key=lambda p: abs(p[1]))
    t50 = next((t for t, x in post if t > pk_t and abs(x) <= abs(pk) * 0.5), None)
    t10 = next((t for t, x in post if t > pk_t and abs(x) <= abs(pk) * 0.1), None)
    zero = next((t for t, x in post if t > pk_t and x == 0.0), None)
    sign = 1 if pk > 0 else -1
    over = max(0.0, -min(x * sign for _, x in post))
    return {"peak": pk, "peak_after": pk_t - stop_t, "t50": t50 - pk_t if t50 else None, "t10": t10 - pk_t if t10 else None, "zero": zero - stop_t if zero else None, "overshoot": over}


def rounded(d):
    return {k: round(v, 3) if v is not None else None for k, v in d.items()}


def punch_peak(impulse):
    """Peak of both view-punch sets together: k 65, c 9, the second set is 0.2 x the first (CAMERA-REFERENCE 3.2)."""
    a = 4.5
    w = math.sqrt(65 - a * a)
    t = math.atan(w / a) / w
    return impulse * math.exp(-a * t) * math.sin(w * t) / w * 1.2


if __name__ == "__main__":
    # Check against RECOIL-VIEW: R-301 first 11 rows (rspn101_2 pitch). Measured time to 50 %: 0.365 hip, 0.244 ADS.
    r301 = [0.54, 0.68, 0.45, 0.57, 0.45, 0.25, 0.21, 0.08, 0.17, -0.09, 0.21]
    for name, cold, hot in [("R-301 hip", (40, 20), (40, 20)), ("R-301 ADS", (115, 20), (0, 60))]:
        tr, _ = run(r301, 13.5, cold, hot, 0.35, 2.325, 0.08, 0.05)
        print(name, rounded(after_stop(tr, 10 / 13.5)))

    # Worked example A in the document: a new mid rifle.
    table = [0.60, 0.55, 0.50, 0.45, 0.35, 0.25, 0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
    for name, cold, hot in [("example hip", (60, 20), (30, 30)), ("example ADS", (115, 20), (0, 55))]:
        tr, shots = run(table, 11.0, cold, hot, 0.35, 2.4, 0.09, 0.05)
        print(name, rounded(after_stop(tr, 11 / 11.0)), "max", round(max(x for _, x in tr), 2), "table total", round(sum(table), 2),
              "before shots", [round(s, 2) for s in shots[:6]], "first step", round(0.35 * table[0], 3))

    # Worked example B: ground slam camera, using the view-punch spring.
    for s in (1, 3, 5, 6.43, 8, 12):
        print("land s", s, "pitch peak", round(punch_peak(s * 2 * 20), 1))
    for name, imp in [("takeoff 2", 2), ("double jump 4.5", 4.5), ("zip detach 10", 10), ("press 1.0", 1.0), ("press -1.5", -1.5)]:
        print(name, round(punch_peak(imp * 20), 2))
