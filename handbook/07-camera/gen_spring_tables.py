import math, sys, os
out = sys.argv[1]
k, c = 65.0, 9.0
a = c/2; wd = math.sqrt(k - a*a)
def step(x, v, dt):
    e = math.exp(-a*dt); cs = math.cos(wd*dt); sn = math.sin(wd*dt)
    return e*(x*cs + (v + a*x)/wd*sn), e*(v*cs - (a*v + k*x)/wd*sn)
dt = 1/120
g = 750.0
vmin = math.sqrt(2*g*12*10); vmax = math.sqrt(2*g*12*70)
def s_of(v):
    if v <= 0: return 0
    if v < vmin: return v/vmin
    if v <= vmax: return 1 + 11*(v-vmin)/(vmax-vmin)
    return 12
# unit impulse response, both springs (1 + 0.2)
rows = []
x1 = v1 = 0; x2 = v2 = 0
v1 = 1.0; v2 = 0.2
n = int(1.2/dt)
peak = (0, 0)
for i in range(n+1):
    t = i*dt
    tot = x1 + x2
    rows.append((t, x1, tot))
    if tot > peak[1]: peak = (t, tot)
    x1, v1 = step(x1, v1, dt); x2, v2 = step(x2, v2, dt)
with open(os.path.join(out, 'punch-response.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# 07-camera punch spring impulse response. k 65 /s^2, c 9 /s, exact step, dt 1/120 s. Impulse = 1 deg/s into spring 1 pitch rate and 0.2 deg/s into spring 2 (the rule for every movement kick).\n')
    f.write('# Column angle_both_deg = what the screen pitch shows (spring 1 + spring 2) per 1 deg/s of pitch impulse; multiply by the event impulse (e.g. landing s*(2+0.75r)*20).\n')
    f.write('# Command 0 = the command the impulse is added on (angle still 0 there in the reference order: step first, then add).\n')
    f.write('cmd\tt_s\tangle_spring1_deg\tangle_both_deg\n')
    for i,(t,a1,tot) in enumerate(rows):
        f.write(f'{i}\t{t:.5f}\t{a1:.6f}\t{tot:.6f}\n')
print('peak per unit', peak)
# landing table
vs = [150, 276, 318, 374, 424.26, 481, 600, 769, 900, 1122.5, 1156, 1500]
with open(os.path.join(out, 'landing-kick.tsv'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# 07-camera landing kick: strength s, pitch impulse and the screen pitch peak (both springs) at r1 = -0.5 / 0 / +0.5; roll peak bound |r3| = 0.5.\n')
    f.write('# Fall speed v = downward speed of the command before the landing [u/s]; [m/s] = v * 0.0254. g 750 u/s^2, viewkickFallDistMin 10 ft, Max 70 ft, MaxScale 12.\n')
    f.write('v_fall_u_s\tv_fall_m_s\ts\tpitch_impulse_r0_deg_s\tpeak_r-0.5_deg\tpeak_r0_deg\tpeak_r+0.5_deg\troll_peak_max_deg\tpeak_time_s\n')
    unit = peak[1]
    for v in vs:
        s = s_of(v)
        imp = s*2*20
        f.write(f'{v:.2f}\t{v*0.0254:.3f}\t{s:.3f}\t{imp:.1f}\t{unit*s*(2-0.375)*20:.2f}\t{unit*imp:.2f}\t{unit*s*(2+0.375)*20:.2f}\t{unit*s*0.5*20:.2f}\t{peak[0]:.3f}\n')
# per-frame landing curve for v=769 r=0 at 120 Hz first 1.0 s
print('vmin', vmin, 'vmax', vmax)
