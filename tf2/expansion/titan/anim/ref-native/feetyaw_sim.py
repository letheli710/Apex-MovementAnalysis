"""Simulate TF2's native feet-yaw rule (server 0x1805ebab0 / client 0x1804999a0) for an in-place turn.

Rule (ref-native, 11-09): when standing still, if |eye - goal| > mp_maxbodyyaw (60) the goal jumps
by whole multiples of 60 toward the eye; the feet then converge to the goal at
mp_bodyyawrate (400 deg/s) * clamp(|goal - feet| / 60, 0.01, 1) per second. Feet are also kept within the
aim_yaw pose range of the eye (here +-90).
Usage: py -3 -I feetyaw_sim.py
"""
MAXB, RATE, FADE, MINS, AIM = 60.0, 400.0, 60.0, 0.01, 90.0


def step_turn(total, omega, dt=1 / 60, t_end=3.0):
    """Eye turns `total` degrees at `omega` deg/s from rest; returns list of (t, eye, goal, feet)."""
    eye = goal = feet = 0.0
    out, t = [], 0.0
    while t < t_end:
        eye = min(total, eye + omega * dt)
        d = eye - goal
        if abs(d) > MAXB:
            goal += (1 if d > 0 else -1) * int(abs(d) / MAXB) * MAXB
        g = goal - feet
        step = RATE * dt * min(1.0, max(MINS, abs(g) / FADE))
        feet = goal if abs(g) <= step else feet + (step if g > 0 else -step)
        feet = max(eye - AIM, min(eye + AIM, feet))  # aim_yaw clamp
        t += dt
        out.append((t, eye, goal, feet))
    return out


def settle(trace, frac):
    """Time from the goal jump until the feet have covered `frac` of the 60 deg step."""
    t0 = next(t for t, e, g, f in trace if g != 0)
    g = trace[-1][2]
    first = next(t for t, e, gg, f in trace if gg == g)
    for t, e, gg, f in trace:
        if gg == g and abs(g - f) <= (1 - frac) * MAXB:
            return t - first, t0
    return None, t0


if __name__ == "__main__":
    print("one 60-deg step (eye snaps 61 deg): time for feet to cover the step")
    tr = step_turn(61, 1e6)
    for frac in (0.5, 0.75, 0.9, 0.95, 0.98):
        print(f"  {frac:4.0%}  {settle(tr, frac)[0]:.3f} s")
    print("analytic: feet error = 60*exp(-t/0.15) -> 90% at 0.345 s, 95% at 0.449 s")
    for total, omega in ((30, 30), (90, 90), (210, 210), (400, 400)):
        tr = step_turn(total, omega)
        lag = max(e - f for t, e, g, f in tr)
        rest = tr[-1][1] - tr[-1][3]
        print(f"turn {total:3d} deg at {omega:3d} deg/s: max eye-feet lag {lag:5.1f} deg, feet left at {rest:5.1f} deg")
