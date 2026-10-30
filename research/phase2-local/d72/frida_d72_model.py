"""D-74 B: check the native traversal model against the Frida traversals (frida_d72_summary.py rows).

Model (TraversalMove 0x140a45380, constants read with Frida): base state b fixed at the start; every command the fraction grows by
rate(b, eye)·dt, eye = view offset +0xf0: 70 before the duck, while ducking 70 − 21.5·SimpleSpline(t / 0.4) for a duck that started in
the air before the traversal (32 once fully ducked) or 70 − 38·SimpleSpline(t / 0.4) for one pressed inside it
(state b + 4 from then on); rate(3) = 1 / 0.7, rate(b ≥ 4) = (1 − ((C_b − eye + 80) / 80)·k) / len_b, C = −10 / 10 / 30, len 0.6 / 0.5 / 0.35.
Per traversal the inputs are the measured base state, start fraction, k (+0x2b60), duck press and fully-ducked times (relative to the
start); the output is the predicted frame count against the measured one.

Usage: frida_d72_model.py <sum.csv> [<sum.csv> ...]   (prints per-file error stats and the worst rows)
"""
import csv
import statistics as st
import sys

C = {4: -10, 5: 10, 6: 30}
LEN = {3: 0.7, 4: 0.6, 5: 0.5, 6: 0.35}


def spline(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def rate(b, eye, k):
    if b == 3:
        return 1 / LEN[3]
    return (1 - (C[b] - eye + 80) / 80 * k) / LEN[b]


def predict(b, f0, k, press, full, dt):
    f, n = f0, 0
    while f < 1 - 1e-9 and n < 1000:
        t = n * dt                                   # this command's time from the start (the eye read at the frame start)
        if press is None or t < press:
            eye = 70.0
        elif full is not None and t >= full:
            eye = 32.0
        elif press >= 0:
            eye = 70 - 38 * spline((t - press) / 0.4)   # a duck started inside the traversal: the ground curve 70 -> 32
        else:
            eye = 70 - 21.5 * spline((t - press) / 0.4) # an in-air duck: 70 -> 48.5, then 32 once ducked
        f += rate(b, eye, k) * dt
        n += 1
    return n


def main():
    for path in sys.argv[1:]:
        errs, rows, mixed = [], [], []
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if int(r["frames"]) < 10:
                continue                             # a mispredicted client start (corrected on the next tick)
            if len(r["seq"].split()) > 2:
                mixed.append((r["trial"], r["seq"], r["frames"]))
                continue                             # client prediction and server correction interleaved (h130: 3 / 4 flips)
            b = int(r["seq"].split("x")[0])
            if b >= 7:
                b -= 4
            press = float(r["duck_press"]) if r["duck_press"] else None
            full = float(r["duck_full"]) if r["duck_full"] else None
            dt = 0.01
            n = predict(b, float(r["f_start"]), float(r["p2b60"]), press, full, dt)
            e = n - int(r["frames"])
            errs.append(e)
            rows.append((abs(e), e, r["trial"], r["seq"], n, r["frames"]))
        print(path, "n", len(errs), "frames error mean %.2f  |err| <= 1: %d / %d, <= 2: %d, max %d" % (
            st.mean(errs), sum(abs(e) <= 1 for e in errs), len(errs), sum(abs(e) <= 2 for e in errs), max(abs(e) for e in errs)))
        print("   left out (prediction / correction interleaved):", len(mixed))
        for a in sorted(rows, reverse=True)[:4]:
            print("   worst", a[1:])


if __name__ == "__main__":
    main()
