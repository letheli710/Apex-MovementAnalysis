"""Zipline roll smoothing check: the per-frame Zipline_CameraRoll output (N10 Frida probe, column zipRoll) through
first-order smoothing at rate r vs SmoothCD (omega 6.667, View_CalcRoll), compared with the CalcView roll (calcR).

  py -3 <this file>   (cwd = phase2-local/data/20261025_040112_N10_zip; reads n10_probe.csv)
Rides are split where zipRoll is missing for > 0.2 s; the smoothing state starts at the measured roll of the ride's first
frame. Sign: calcR is the CalcView roll itself, so it is + the function output (the minus in CAM-11 / rodeo_roll.py is
the HSD-MD cang convention). Standard library only. Part of rea-native N12.
"""
import csv, math

OMEGA = 6.6666665
rows = [r for r in csv.DictReader(open('n10_probe.csv')) if r['calcR'] not in ('NaN', '')]
rides, cur, last = [], [], None
for r in rows:
    t = float(r['t']); z = r['zipRoll']
    if z in ('NaN', ''):
        continue
    if last is not None and t - last > 0.2:
        rides.append(cur); cur = []
    cur.append((t, float(z), float(r['calcR']))); last = t
if cur: rides.append(cur)
rides = [rd for rd in rides if len(rd) > 60]


def run(model, rate=3.0):
    se = n = 0
    for rd in rides:
        x = rd[0][2]; vel = 0.0; prev = None
        for t, tg, meas in rd:
            dt = t - prev if prev else 0.0; prev = t
            if dt > 0:
                if model == 'exp':
                    x += (tg - x) * min(1.0, rate * dt)
                else:
                    X = OMEGA * dt; ex = 1 / (1 + X + 0.48 * X * X + 0.235 * X * X * X)
                    c = x - tg; tmp = (vel + OMEGA * c) * dt
                    vel = (vel - OMEGA * tmp) * ex; x = tg + (c + tmp) * ex
            se += (x - meas) ** 2; n += 1
    return math.sqrt(se / n), n


print('rides', len(rides), 'frames', sum(len(r) for r in rides))
for rate in (2.0, 3.0, 4.0, 6.667):
    print('first-order %.3f /s  rms %.3f deg' % ((rate,) + run('exp', rate)[:1]))
print('SmoothCD omega 6.667  rms %.3f deg' % run('cd')[0])
print('no smoothing (target) rms %.3f deg' % math.sqrt(sum((tg - m) ** 2 for rd in rides for _, tg, m in rd) / sum(len(r) for r in rides)))
