"""Landing law from g_land2 (speed sweep). Usage: an_land2.py <run dir>
One row per landing: landing speed, kick (pitch, roll, yaw peak), spring fit, body dip, speed change."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from g_tools import load, tags
import numpy as np

d, c = load(sys.argv[1])
CAM = np.array([x[:8] for x in d['CAM']])
C = np.array([x[:10] for x in d['C']])
CH = np.array([x[:7] for x in d['BD_CHESTFOCUS']])
FL = np.array([x[:7] for x in d['BD_foot_L_sole']])
G = np.array([x[:8] for x in d['GK'] if len(x) >= 8])
SPR = {"ion": (65, 15), "ronin": (35, 9), "legion": (95, 30)}


def impulse(t, k, dmp):
    """unit initial velocity response of x'' = -k x - d x'"""
    a = dmp / 2.0
    w2 = k - a * a
    if w2 > 0:
        w = np.sqrt(w2)
        return np.exp(-a * t) * np.sin(w * t) / w
    if abs(w2) < 1e-6:
        return t * np.exp(-a * t)
    w = np.sqrt(-w2)
    return np.exp(-a * t) * np.sinh(w * t) / w


rows = []
for a, b, n in tags(c):
    m = re.match(r'(s|mwalk|msprint)(\d+)(?:_(\d))?_(\w+)', n)
    if not m:
        continue
    cls = m.group(4)
    F = C[(C[:, 0] >= a) & (C[:, 0] < b)]
    i = [j for j in range(1, len(F)) if F[j, 9] == 1 and F[j - 1, 9] == 0]
    if not i:
        print(n, 'no landing')
        continue
    i = i[-1]
    tl = F[i, 0]
    vz = F[i - 1, 6]
    K = CAM[(CAM[:, 0] >= tl - 0.02) & (CAM[:, 0] < tl + 1.5)]
    t = K[:, 0] - tl
    p = K[:, 2] - K[0, 2]
    r = K[:, 4] - K[0, 4]
    y = (K[:, 3] - K[0, 3] + 180) % 360 - 180
    dz = K[:, 7] - K[0, 7]
    ip = np.argmax(np.abs(p))
    k, dmp = SPR[cls]
    u = impulse(np.clip(t, 0, None), k, dmp)
    v0 = (p @ u) / (u @ u)  # initial angular velocity from a least-squares fit
    res = np.sqrt(np.mean((p - v0 * u) ** 2))
    pk = u.max() * v0
    Ch = CH[(CH[:, 0] >= tl - 0.3) & (CH[:, 0] < tl + 1.6)]
    dip = Ch[:, 6].min() - np.median(Ch[Ch[:, 0] < tl, 6]) if len(Ch) and (Ch[:, 0] < tl).any() else 0
    tdip = Ch[np.argmin(Ch[:, 6]), 0] - tl if len(Ch) else 0
    sp = np.hypot(F[:, 4], F[:, 5])
    gk = G[(G[:, 0] >= tl - 0.02) & (G[:, 0] < tl + 1.5)]
    gu = gk[:, 4] - gk[0, 4] if len(gk) else np.zeros(1)
    rows.append((n, cls, -vz, p[ip], t[ip], v0, res, r[np.argmax(np.abs(r))], y[np.argmax(np.abs(y))], dz[np.argmax(np.abs(dz))], dip, tdip, sp[i - 1], sp[i:i + 5].min(), sp[min(i + 140, len(sp) - 1)], gu[np.argmax(np.abs(gu))]))
print("tag cls v_land p_peak t_peak v0_fit fit_rms roll yaw dz chest_dip t_dip sp_before sp_after sp_1s ck_u")
for r in sorted(rows, key=lambda r: (r[1], r[0][0], r[2])):
    print(f"{r[0]:22s} {r[1]:7s} {r[2]:7.1f} {r[3]:+6.2f} {r[4]:.3f} {r[5]:+7.1f} {r[6]:.2f} {r[7]:+5.2f} {r[8]:+5.2f} {r[9]:+6.2f} {r[10]:+6.1f} {r[11]:.2f} {r[12]:4.0f} {r[13]:4.0f} {r[14]:4.0f} {r[15]:+5.2f}")
print()
for cls in SPR:
    R = [r for r in rows if r[1] == cls and r[0][0] == 's']
    v = np.array([r[2] for r in R])
    p = np.array([abs(r[3]) for r in R])
    for lo, hi in ((0, 400), (400, 500), (500, 650), (650, 850), (850, 1100), (1100, 1500), (1500, 2100), (2100, 3200)):
        s = (v >= lo) & (v < hi)
        if s.any():
            print(cls, f"v {lo}-{hi} n={s.sum()} mean v={v[s].mean():.0f} p mean={p[s].mean():.2f} min={p[s].min():.2f} max={p[s].max():.2f}")
