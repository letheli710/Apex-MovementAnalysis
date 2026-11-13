# One sheet per medium kit, same layout as LIGHT-HEAVY.md img/kit-*.png:
# header bar, three views with numbered sockets, legend, then one panel per skill (sizes from kits/ pages).
# py -3 kit_sheets.py <renders_dir> <out_img_dir>
import math, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Wedge, Rectangle, Polygon, FancyBboxPatch

RD, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
for f in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf'):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=f).get_name(); break
plt.rcParams['axes.unicode_minus'] = False

OWN = '#FF3FD2'                     # M-1 本机色（提议，替换 SPEC 的 #FF5A1F）
OWN_L = '#FFC2F0'
K_CORE, K_EDGE, SMOKE = '#FFF4D6', '#FFC860', '#7A7570'   # 实弹
E_MAIN, E_GLOW = '#CFE8FF', '#6FA8FF'                     # 电
WARN, THREAT = '#FF3B30', '#FF9A2E'
BG = '#F5F4EF'
NEW = '#FF00FF'
U = 0.0254

S = 900 / 7.0; CZ = 3.05
def proj(view, p):
    x, y, z = p
    u = {'front': x, 'side': y, 'back': -x}[view]
    return 350 + u * S, 450 - (z - CZ) * S
def visible(view, p):
    x, y, z = p
    return {'front': y <= 0.25, 'side': x >= 0.15, 'back': y >= 0.30}[view]

def scalebar(ax, x, y, L, label):
    ax.plot([x, x + L], [y, y], color='black', lw=1.2)
    for xx in (x, x + L): ax.plot([xx, xx], [y - L * 0.03, y + L * 0.03], color='black', lw=1.2)
    ax.text(x + L / 2, y + L * 0.06, label, ha='center', fontsize=7.5)

def titan_dot(ax, x=0, y=0, r=0.8):
    ax.add_patch(Circle((x, y), r, fc='#333', ec='none', zorder=5))
    ax.add_patch(Polygon([(x - r * 0.5, y + r * 0.6), (x + r * 0.5, y + r * 0.6), (x, y + r * 1.6)], fc='#333', zorder=5))

def zig(ax, x0, y0, x1, y1, n=6, amp=0.4, rng=None, **kw):
    rng = rng or np.random.default_rng(0)
    xs = np.linspace(x0, x1, n); ys = np.linspace(y0, y1, n)
    dx, dy = y1 - y0, -(x1 - x0); L = math.hypot(dx, dy) or 1
    off = rng.uniform(-amp, amp, n); off[0] = off[-1] = 0
    ax.plot(xs + off * dx / L, ys + off * dy / L, **kw)

def diamond_lock(ax, x, y, s, c, lw=2):
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        cx, cy = x + dx * s, y + dy * s
        ax.plot([cx - (dy) * s * 0.35 - dx * s * 0.35, cx, cx + (dy) * s * 0.35 - dx * s * 0.35],
                [cy - (-dx) * s * 0.35 - dy * s * 0.35, cy, cy + (-dx) * s * 0.35 - dy * s * 0.35], color=c, lw=lw)

def shard(ax, x, y, ang, L, W, c, alpha=1.0, z=3):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    pts = [(x + ca * L / 2, y + sa * L / 2), (x - ca * L / 2 - sa * W / 2, y - sa * L / 2 + ca * W / 2),
           (x - ca * L / 2 + sa * W / 2, y - sa * L / 2 - ca * W / 2)]
    ax.add_patch(Polygon(pts, fc=c, ec='white', lw=0.6, alpha=alpha, zorder=z))

# ---------------------------------------------------------------- skill panels (units: metres, top view titan faces +y)
def p_rifle(ax, lens=False):
    angs = [0, 1.26, -1.26] + ([2.52, -2.52] if lens else [])
    titan_dot(ax, 0, -1)
    for a in angs:
        k = 6  # 角度放大 6 倍画
        for d in (6, 13, 20):
            r = math.radians(90 + a * k)
            shard(ax, d * math.cos(r), d * math.sin(r), 90 + a * k, 1.4, 0.7, OWN, alpha=1.0 if a == 0 else (0.75 if abs(a) < 2 else 0.45))
        r = math.radians(90 + a * k)
        ax.plot([0, 24 * math.cos(r)], [0, 24 * math.sin(r)], color=OWN_L, lw=1, zorder=1)
    ax.set_xlim(-12, 12); ax.set_ylim(-3, 25); scalebar(ax, 5, -1.5, 5, '5 m')

def p_needle(ax):
    titan_dot(ax, 0, 0)
    ax.plot([0, 0], [0, 100], color=OWN, lw=1.6)
    ax.plot([0, 0], [0, 100], color='white', lw=0.5)
    ax.add_patch(Wedge((0, 0), 102, 90 - 0.55 * 8, 90 + 0.55 * 8, fc=OWN_L, alpha=0.35, ec='none'))
    titan_dot(ax, 0, 70, 2.0)
    for k in range(10):
        shard(ax, 2 + k * 0.8, 30 + k * 3, 60 + k * 25, 1.2, 0.8, OWN, alpha=0.7)
    ax.text(3, 85, '锥放大 8 倍画', fontsize=7)
    ax.set_xlim(-30, 30); ax.set_ylim(-5, 105); scalebar(ax, 5, 2, 20, '20 m')

def p_catch(ax):
    R = 3.8
    titan_dot(ax, 0, 0, 0.7)
    th = np.linspace(30, 150, 7)
    pts = [(R * math.cos(math.radians(t)), R * math.sin(math.radians(t))) for t in th]
    for i in range(6):
        on = i not in (0, 5)
        ax.add_patch(Polygon([(0, 0.4), pts[i], pts[i + 1]], fc=OWN if on else '#E8E8E8', alpha=0.35 if on else 0.6,
                             ec=OWN, lw=1.2))
    for i in range(5):
        ax.plot([pts[i][0] * 0.55 + pts[i + 1][0] * 0.45], [pts[i][1] * 0.55 + pts[i + 1][1] * 0.45], 'o', ms=3, color='white', mec=OWN)
    ax.plot(-0.7, 2.8, '*', ms=12, color=OWN, mec='black'); ax.text(-3.6, 2.5, '收集点', fontsize=7)
    for xx in (-2, 0.5, 2.5):
        ax.annotate('', xy=(xx, R * 0.92), xytext=(xx, 7), arrowprops=dict(arrowstyle='->', color='gray'))
    ax.set_xlim(-5, 5); ax.set_ylim(-1.5, 7.5); scalebar(ax, 2, -1, 2, '2 m')

def p_fence(ax):
    P = [(-6, 9), (0, 11), (6, 9)]
    titan_dot(ax, 0, 0)
    for i, p in enumerate(P):
        ax.add_patch(Circle(p, 10.2, fc=OWN, alpha=0.05, ec=OWN, lw=0.8))
        ax.add_patch(Polygon([(p[0] - 0.6, p[1] - 0.5), (p[0] + 0.6, p[1] - 0.5), (p[0], p[1] + 0.6)], fc=OWN, ec='black', zorder=4))
        ax.text(p[0] + 0.8, p[1] - 1.2, str(i), fontsize=8)
    for a, b in ((0, 1), (1, 2)):
        ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]], color=OWN, lw=1.8, ls=(0, (2, 1.5)), zorder=3)
    for p in P: ax.plot([0, p[0]], [0.5, p[1]], color='#BBB', lw=0.6, ls=':')
    ax.set_xlim(-18, 18); ax.set_ylim(-3, 22); scalebar(ax, 8, -2, 10, '10 m')

def p_beam(ax):
    titan_dot(ax, 0, 0)
    L = 40
    ax.add_patch(Rectangle((-0.46 * 3, 0), 0.92 * 3, L, fc=OWN, alpha=0.35, ec='none'))
    ax.add_patch(Rectangle((-0.2, 0), 0.4, L, fc='white', ec='none'))
    for k in range(10):
        y = 2 + k * 3.8
        h = [(-1.6, y), (-0.8, y + 0.7), (0.8, y + 0.7), (1.6, y), (0.8, y - 0.7), (-0.8, y - 0.7)]
        ax.add_patch(Polygon(h, fill=False, ec=OWN, lw=1.1))
    ax.text(2.3, 30, '宽度放大 3 倍画\n每跳一个六边形环', fontsize=7)
    ax.set_xlim(-12, 12); ax.set_ylim(-3, 42); scalebar(ax, 4, -2, 10, '10 m')

def p_pool(ax):
    for i in range(3):
        on = i < 2
        ax.add_patch(Rectangle((0, i * 1.3), 4, 1.0, fc=OWN if on else '#DDD', ec='black', lw=0.8))
        ax.text(4.4, i * 1.3 + 0.35, f'{(i + 1) * 333 if i < 2 else 1000}', fontsize=7.5)
    ax.add_patch(Rectangle((0, 2 * 1.3), 4, 1.0, fill=False, ec=OWN, lw=2, ls='--'))
    ax.text(0, 4.3, '顶格虚框 = 正在回能（"呼吸"）', fontsize=7.5)
    ax.text(0, -0.9, '炮管上三道槽 = 三格', fontsize=7.5)
    ax.set_xlim(-1, 8); ax.set_ylim(-1.5, 5)

def p_shell(ax):
    titan_dot(ax, 0, 0)
    for d in (8, 16): ax.plot(0, d, 'o', ms=4, color='#555')
    ax.plot([0, 0], [1, 24], color=SMOKE, lw=1.2, alpha=0.6)
    ax.add_patch(Circle((0, 25), 3.81, fc=K_EDGE, alpha=0.25, ec=OWN, lw=1.5))
    for a in range(0, 360, 30):
        r = math.radians(a); ax.plot([math.cos(r) * 0.5, math.cos(r) * 1.6], [25 + math.sin(r) * 0.5, 25 + math.sin(r) * 1.6], color=K_EDGE, lw=1)
    ax.set_xlim(-12, 12); ax.set_ylim(-3, 31); scalebar(ax, 5, -2, 5, '5 m')

def p_burstload(ax):
    for i in range(3):
        t = (i + 1) * 2.0 / 3
        ax.add_patch(Circle((t * 4, 2), 0.55, fc=OWN, ec='black'))
        ax.text(t * 4 - 0.3, 0.8, f'{t:.2f} s', fontsize=7)
    ax.plot([0, 8.5], [2, 2], color='#999', lw=0.8, zorder=0)
    for k in range(3):
        ax.plot([1 + k * 0.8], [4], 'o', ms=6, color='#555'); ax.plot([1 + k * 0.8, 1 + k * 0.8 + 0.6], [4, 4], color=K_EDGE, lw=1)
    ax.text(3.6, 3.9, '连发 0.2 s 间隔，后延迟 0.75 s', fontsize=7)
    ax.set_xlim(-0.5, 9.5); ax.set_ylim(0, 5)

def p_comb(ax, n_targets=2):
    titan_dot(ax, 0, 0)
    rng = np.random.default_rng(4)
    T = [(14, 30), (-8, 34)][:n_targets]
    for ti, (tx, ty) in enumerate(T):
        diamond_lock(ax, tx, ty, 2.0, OWN)
        for i in range(6):
            t = np.linspace(0, 1, 50)
            sx, sy = -5 - i * 0.4, 5 + i * 0.5
            x = (1 - t) ** 2 * 0 + 2 * (1 - t) * t * sx + t ** 2 * tx + rng.normal(0, 0.12, 50).cumsum() * 0.15 * (1 - t)
            y = (1 - t) ** 2 * 1 + 2 * (1 - t) * t * sy + t ** 2 * ty
            ax.plot(x, y, color=SMOKE, lw=1, alpha=0.8)
    ax.set_xlim(-20, 20); ax.set_ylim(-3, 40); scalebar(ax, 8, -2, 10, '10 m')

def p_screen(ax):
    R = 4.57
    titan_dot(ax, 0, 0, 0.7)
    for k in range(9):
        a0 = 30 + 120 * k / 9; a1 = a0 + 120 / 9 * 0.75
        on = k not in (2, 6)
        ax.add_patch(Wedge((0, 0), R + 0.25, a0, a1, width=0.5, fc=OWN if on else '#DDD', ec='none', alpha=0.9))
    ax.add_patch(Wedge((0, 0), R + 0.5, 30, 150, width=0.05, fc=OWN))
    ax.annotate('', xy=(0, R + 0.6), xytext=(0, 9), arrowprops=dict(arrowstyle='->', color='gray'))
    ax.set_xlim(-7, 7); ax.set_ylim(-2, 10); scalebar(ax, 3, -1.5, 2, '2 m')

def p_ping(ax, echo=False):
    ax.add_patch(Circle((0, 0), 31.8, fill=False, ec=OWN, lw=2, ls='-' if not echo else (0, (4, 2))))
    if echo: ax.add_patch(Circle((0, 0), 30.3, fill=False, ec=OWN, lw=2, ls=(0, (4, 2))))
    ax.plot(0, 0, marker='v', ms=10, color=OWN, mec='black')
    for (x, y) in ((12, 18), (-20, 9), (5, -24)):
        ax.add_patch(Circle((x, y), 1.4, fill=False, ec=THREAT, lw=2.2))
    ax.text(-30, 33, '敌人：橙色描边 5 s（穿墙）' + ('，再 +1 层' if echo else '，+1 层'), fontsize=7)
    ax.set_xlim(-36, 36); ax.set_ylim(-36, 36); scalebar(ax, 12, -34, 10, '10 m')

def p_storm(ax):
    titan_dot(ax, 0, 0)
    tx, ty = 6, 30
    for k in range(3):
        diamond_lock(ax, tx, ty, 1.6 - k * 0.0, OWN, lw=1.5)
    for i in range(18):
        src = (-1.2, 1.5) if i % 2 == 0 else (0.6, 1.0)
        t = np.linspace(0, 1, 40); bend = 6 + (i % 5)
        x = src[0] * (1 - t) + tx * t + np.sin(t * np.pi) * (-bend if i % 2 == 0 else bend * 0.4)
        y = src[1] * (1 - t) + ty * t
        ax.plot(x, y, color=SMOKE, lw=0.7, alpha=0.7)
    ax.text(-15, 2.5, '肩舱 / 胸口\n轮流', fontsize=7)
    ax.set_xlim(-18, 18); ax.set_ylim(-3, 36); scalebar(ax, 6, -2, 10, '10 m')

def p_marks(ax):
    for k in range(4):
        x = k * 4
        ax.add_patch(Rectangle((x, 0), 2, 3, fc='#CCC', ec='#888'))
        for j in range(3):
            ax.add_patch(Polygon([(x + 0.2 + j * 0.6, 3.4), (x + 0.6 + j * 0.6, 3.4), (x + 0.4 + j * 0.6, 3.9)],
                                 fc=OWN if j < k else 'white', ec='black', lw=0.6))
        if k == 3: diamond_lock(ax, x + 1, 1.5, 2.3, OWN)
        ax.text(x + 0.2, -0.9, f'{k} 层', fontsize=7.5)
    ax.set_xlim(-1.5, 16); ax.set_ylim(-1.5, 5)

def p_stepgun(ax, overdrive=False):
    titan_dot(ax, 0, 0)
    for s in (-0.25, 0.25):
        for k in range(12 if overdrive else 4):
            y = 3 + k * (2.2 if overdrive else 6)
            ax.plot([s, s], [y, y + 1.8], color=K_EDGE, lw=2.2); ax.plot([s, s], [y, y + 1.8], color=K_CORE, lw=0.8)
    for k in range(6):
        ax.plot([2 + k * 0.4], [0.5 - k * 0.3], 's', ms=3, color='#B08A3C')
    ax.set_xlim(-10, 10); ax.set_ylim(-3, 32); scalebar(ax, 4, -2, 5, '5 m')

def p_arcplate(ax):
    for s in (-0.25, 0.25):
        for k in range(4):
            y = 3 + k * 6; ax.plot([s, s], [y, y + 1.8], color=E_GLOW, lw=2.2); ax.plot([s, s], [y, y + 1.8], color=E_MAIN, lw=0.8)
    titan_dot(ax, 0, 28, 2.0)
    rng = np.random.default_rng(2)
    for i in range(6):
        a = rng.uniform(0, 2 * np.pi); zig(ax, 0, 27, 3.5 * math.cos(a), 27 + 3.5 * math.sin(a), rng=rng, color=E_GLOW, lw=1.4)
    titan_dot(ax, 0, 0)
    ax.set_xlim(-10, 10); ax.set_ylim(-3, 33); scalebar(ax, 4, -2, 5, '5 m')

def p_bloom(ax):
    for k in range(6):
        a = math.radians(60 * k); ca, sa = math.cos(a), math.sin(a); px, py = -sa * 0.35, ca * 0.35
        ax.annotate('', xy=(5 * ca, 5 * sa), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color='#555', lw=1.8))
        ax.annotate('', xy=(-2.5 * ca + px, -2.5 * sa + py), xytext=(5 * ca + px, 5 * sa + py), arrowprops=dict(arrowstyle='->', color=SMOKE, lw=1, ls='--'))
        ax.text(5.8 * ca, 5.8 * sa, str(k), ha='center', va='center', fontsize=8, weight='bold')
    ax.plot(0, 0, '+', color='black', ms=14, mew=2)
    ax.text(-6.5, -7, '张开 5°（0.2 s）→ 交叉收 10°（0.1 s）→ 扎向准星', fontsize=7)
    ax.set_xlim(-7.5, 7.5); ax.set_ylim(-7.5, 7.5)

def p_rollcall(ax):
    titan_dot(ax, 0, 0)
    ax.add_patch(Wedge((0, 0), 101.6 / 3, 75, 105, fc=OWN, alpha=0.08, ec=OWN, lw=0.8))
    for (x, y, n) in ((-4, 26, 6), (5, 20, 3)):
        diamond_lock(ax, x, y, 2.0, OWN)
        for j in range(n): ax.plot([x + 2.6 + j * 0.45] * 2, [y - 0.6, y + 0.6], color=OWN, lw=2)
    ax.text(-15, 32, '锥 30°、4000 u（图里距离缩 1/3）', fontsize=7)
    ax.set_xlim(-17, 17); ax.set_ylim(-3, 36); scalebar(ax, 6, -2, 5, '5 m (×3)')

def p_draw(ax, mode='enemy'):
    titan_dot(ax, 0, 0)
    tx, ty = (3, 26)
    ax.plot([0, tx], [1, ty], color=OWN, lw=1.4)
    for f in (0.3, 0.55, 0.8):
        ax.plot(tx * f, 1 + (ty - 1) * f, 'o', ms=7 if mode != 'field' else 5, color=OWN, mec='white')
    if mode == 'friend':
        ax.add_patch(Circle((tx, ty), 2.0, fc='none', ec=OWN, lw=2.5)); ax.add_patch(Circle((tx, ty), 1.2, fc='#4A90E2'))
        ax.text(tx + 2.5, ty, '友方 +750', fontsize=7.5)
    else:
        ax.add_patch(Circle((tx, ty), 1.2, fc='#333'))
        for k in range(5): ax.plot(tx - 1 + k * 0.5, ty - 1.6 - (k % 2) * 0.5, 's', ms=2.5, color=OWN)
    if mode == 'field':
        ax.add_patch(Circle((tx, ty), 8.9, fc=OWN, alpha=0.08, ec=OWN, lw=1.5))
        for (x, y) in ((tx - 5, ty + 3), (tx + 4, ty - 5)):
            ax.add_patch(Circle((x, y), 1.0, fc='#333'))
            ax.plot([x, 0], [y, 1], color=OWN, lw=0.6, ls=':')
    ax.set_xlim(-14, 16); ax.set_ylim(-3, 37); scalebar(ax, 5, -2, 5, '5 m')

def p_reset(ax):
    ax.add_patch(FancyBboxPatch((-1.5, 0), 3, 4, boxstyle='round,pad=0.1', fc='#CCC', ec='#888'))
    ax.add_patch(Rectangle((-1.0, 0.5), 2, 0.6, fc=OWN))
    for (x, y, t) in ((2.8, 4.5, '肩舱'), (3.2, 1.5, '左前臂'), (-3.2, 0.2, '推进器')):
        ax.annotate('', xy=(x, y), xytext=(0, 0.8), arrowprops=dict(arrowstyle='->', color=OWN, lw=2))
        ax.text(x + (0.2 if x > 0 else -1.6), y, t, fontsize=7.5)
    ax.text(-4.5, -1.2, '背包 → 三路光流（0.5 s）→ 三处到位动作', fontsize=7)
    ax.set_xlim(-5, 6); ax.set_ylim(-1.8, 5.5)

def p_fog(ax, storm=False):
    ax.add_patch(Circle((0, 0), 9.5, fc='#9A9EA6', alpha=0.25, ec=OWN, lw=1.2, ls='--'))
    ax.add_patch(Circle((0, 0), 8.1, fill=False, ec=OWN, lw=1.5))
    rng = np.random.default_rng(5)
    for i in range(10 if not storm else 20):
        a = rng.uniform(0, 2 * np.pi); r = rng.uniform(1, 7.5)
        x0, y0 = r * math.cos(a), r * math.sin(a)
        zig(ax, x0, y0, x0 + rng.normal(0, 2), y0 + rng.normal(0, 2), n=5, amp=0.5, rng=rng, color=E_GLOW, lw=1.0 if not storm else 1.8)
    if storm:
        t = np.linspace(0, 1.7 * np.pi, 80); ax.plot(5 * np.cos(t), 5 * np.sin(t), color=E_MAIN, lw=3); ax.plot(5 * np.cos(t), 5 * np.sin(t), color=E_GLOW, lw=1)
        for nm, x in (('L', 0.6), ('R', -0.6)): ax.plot([x, x], [0, 1.5], color=E_GLOW, lw=2)
    titan_dot(ax, 0, 0, 0.9)
    ax.set_xlim(-11, 11); ax.set_ylim(-11, 11); scalebar(ax, 3, -10.5, 5, '5 m')

def p_ascent_core(ax):
    for i in range(4):
        x = i * 3.6
        for j in range(3):
            lit = j < min(i + 1, 3)
            ax.plot([x + 0.3, x + 1.4, x + 2.5], [1.2 + j * 0.55, 1.6 + j * 0.55, 1.2 + j * 0.55], color=OWN if lit else '#CCC', lw=3)
        ax.text(x + 0.3, 0.4, ['第 1 次', '第 2 次', '第 3 次', '第 4 次起'][i], fontsize=7.5)
    ax.text(0, -0.6, '右肩 V 形刻度 = 已升级次数（远处可数）', fontsize=7)
    ax.set_xlim(-0.3, 14.5); ax.set_ylim(-1, 3.4)

def p_overdrive(ax):
    t = np.linspace(0, 5.5, 200)
    ax.fill_between(t, 0, 1, color=K_EDGE, alpha=0.25)
    ax.plot(t, 0.3 + 0.7 * t / 5.5, color='#C0392B', lw=2)
    for x in np.arange(0, 5.5, 0.2): ax.plot([x, x], [0, 0.12], color='black', lw=0.5)
    ax.text(0.1, 1.08, '散热鳍红热 = 剩余时间', fontsize=7.5, color='#C0392B')
    ax.text(0.1, -0.25, '0 s', fontsize=7); ax.text(5.2, -0.25, '5.5 s', fontsize=7)
    ax.set_xlim(-0.2, 5.9); ax.set_ylim(-0.4, 1.3)

# ---------------------------------------------------------------- kits
COMMON = [('S_Hand_L', (1.30, 0.0, 2.50), '重拳（共用 7.1）'), ('S_Vent_L', (0.23, 0.965, 5.57), '电雾 / dash（共用 7.3、7.5）'),
          ('S_Vent_R', (-0.31, 0.975, 5.57), '电雾 / dash（共用）'), ('S_Thrust', (0.0, 1.41, 4.42), 'dash 喷口（共用 7.3）')]
KITS = {
 'spectra': dict(name='分光套件', en='SPECTRA', rule='Ion（ION.md）', sockets=[
     ('S_Muzzle', (-1.30, 0, 1.72), '三棱步枪口：3.1'), ('P_Barrel', (-1.30, 0, 2.6), '提议 M-1 三棱炮管 + 导流翼：3.1 / 3.6'),
     ('P_Laser', (0.61, -0.42, 5.80), '提议 M-2 针光方管口：3.2'), ('S_Shield_L', (1.70, 0, 3.35), '捕光壳花瓣：3.3'),
     ('S_Mine_L', (0.60, 0.72, 5.86), '棱栅桩弹槽（提议 M-7）：3.4'), ('S_Chest', (0, -1.084, 4.78), '全谱光束 + 三片棱叶（提议 M-4）：3.5')] + COMMON,
     panels=[('三棱步枪', 'TRI-PRISM · 开镜俯视', p_rifle, '9 发/s；开镜一枪 3 发 ±1.26°，每发 ×0.7，耗 30（ION §1）'),
             ('五棱镜（被动）', 'PENTA LENS · 开镜俯视', lambda ax: p_rifle(ax, True), '5 发 ±1.26°/±2.52°，每发 ×0.55，耗 ×1.15（§7）'),
             ('棱压（能量池）', 'PRISM CHARGE · 炮管三格', p_pool, '1000；停用 0.5 s 后 80/s（§0.5）'),
             ('针光', 'NEEDLE · 俯视', p_needle, '0.55° 锥、4000 u（102 m）；300/1200；耗 550（§2）'),
             ('捕光壳', 'CATCH FACET · 俯视', p_catch, '球 r 150 u（3.8 m），±60°；各存 31；熄灭刻面 = 用掉的能量（§3）'),
             ('棱栅', 'PRISM FENCE · 俯视', p_fence, '3 桩只连 0–1、1–2；每桩 r 400 u（10.2 m）200/1500（§4）'),
             ('全谱光束', 'FULL SPECTRUM · 俯视', p_beam, '蓄 1.1 s + 3.5 s；35 跳 × 325；r 18 u、射程 6000 u（§5）')]),
 'tally': dict(name='猎标套件', en='TALLY', rule='Tone（TONE.md）', sockets=[
     ('S_Muzzle', (-1.30, 0, 2.02), '刻痕炮口：4.1'), ('P_Barrel', (-1.72, 0, 2.75), '提议 M-1 短炮管 + 三室转鼓（层数灯）：4.0 / 4.1'),
     ('S_Rocket_1..6', (0.60, -0.10, 5.73), '提议 M-2 2×3 方管舱（虹膜盖、探头）：4.2 / 4.5'),
     ('S_Shield_L', (1.72, 0, 3.35), '折屏投射器（提议 M-3）：4.3'), ('S_Mine_L', (0.62, 0.95, 5.75), '探钟弹槽（提议 M-7）：4.4'),
     ('P_CoreCell', (0, -1.24, 4.47), '提议 M-5 舱门三联小发射格：4.5'), ('S_Chest', (0, -1.084, 4.78), '核心就绪灯')] + COMMON,
     panels=[('标记 → 锁定', 'TALLY MARKS', p_marks, '每次伤害 +1 层，上限 3，单层 15 s；满 3 = 菱形锁定（TONE §1）'),
             ('刻痕炮', 'NOTCH · 俯视', p_shell, '1.75 发/s；爆炸 r 150 u（3.8 m）（§1）'),
             ('三连装（被动）', 'TRIPLE FEED · 蓄级', p_burstload, '开镜 2.0 s 分 3 级；连发 0.2 s，后延迟 0.75 s（§7）'),
             ('清账导弹', 'SETTLE · 俯视', p_comb, '每个锁定目标 6 枚，1/14 s；一束烟 = 一个目标（§2）'),
             ('折屏', 'FOLD SCREEN · 俯视', p_screen, 'r 180 u（4.6 m）、高 360 u、120°；2000 血 6 s；熄灭条数 = 掉血（§3）'),
             ('探钟', 'BELL · 俯视', p_ping, '落点脉冲 r 1250 u（31.8 m），揭示 5 s、+1 层（§4）'),
             ('余响（被动）', 'AFTERTONE · 俯视', lambda ax: p_ping(ax, True), '2.0 s 后同点再脉冲，双线环（§7）'),
             ('清账风暴', 'LEDGER STORM · 俯视', p_storm, '蓄 0.5 s；20 轮 × 3 枚，12 轮/s，左右交替（§5）')]),
 'ascent': dict(name='进阶套件', en='ASCENT', rule='Monarch（MONARCH.md）', sockets=[
     ('S_Muzzle_A/B', (-1.30, 0, 1.76), '阶梯机炮双管口（提议）：5.1'), ('P_Barrel', (-1.30, 0, 2.25), '提议 M-1 双管 + 供弹盒；升级铜线圈：5.1'),
     ('P_Bloom_0..5', (0.62, -0.16, 5.66), '提议 M-2 六角巢；升级颊板：5.2 / 5.3'), ('S_Shield_L', (1.72, -0.15, 3.35), '汲光镜头；升级前臂环 / 镜头外圈碟：5.4'),
     ('S_Vent_L/R', (0.23, 0.965, 5.57), '电雾（共用 7.5）；升级放电杆：5.6'), ('P_Chevron', (-1.95, 0, 5.13), '提议 M-8 右肩三道刻度：5.7'),
     ('S_Chest', (0, -1.084, 4.78), '核心就绪灯'), ('S_Hand_L', (1.30, 0.0, 2.50), '重拳（共用 7.1）'), ('S_Thrust', (0.0, 1.41, 4.42), 'dash 喷口（共用 7.3）')],
     panels=[('阶梯机炮', 'STEP GUN · 俯视', p_stepgun, '12 发/s、40 发；曳光每 3 发（MONARCH §1）'),
             ('电镀弹（升级 1）', 'ARC PLATING', p_arcplate, '弹匣 50、当前 +10；打护盾 ×1.5（§1、§5.3）'),
             ('花开齐射', 'BLOOM · 从身后看准星', p_bloom, '6 枚，第 k 枚 60°·k 张开 5° 再收 10°（§2.1）'),
             ('点名导弹（升级 3）', 'ROLL CALL · 俯视', p_rollcall, '每 0.3 s 一锁，一目标 ≤ 6；锁数 = 竖线（§2.2）'),
             ('汲光', 'DRAW · 俯视', p_draw, '0.75° 锥、4000 u；回盾 750/250、扣对方盾上限 50 %（§3）'),
             ('分盾（升级 1）', 'SHARE · 俯视', lambda ax: p_draw(ax, 'friend'), '打友方泰坦 +750 护盾（§3、§5.3）'),
             ('汲场（升级 2）', 'DRAW FIELD · 俯视', lambda ax: p_draw(ax, 'field'), '命中点 r 350 u（8.9 m）内都汲（§3）'),
             ('复位', 'RESET · 机体', p_reset, '蓄 0.5 s；进攻、防御、dash 回满（§4）'),
             ('电雾（共用 7.5）', 'STATIC VEIL · 俯视', p_fog, '内 320 / 外 375 u（8.1 / 9.5 m）；1.0 s 后每 0.1 s 一跳，5 s'),
             ('旋雷（升级 2）', 'STORM SPIN · 俯视', lambda ax: p_fog(ax, True), '泰坦 450 → 1350/s，铁驭 45 → 90/s（§5.3）'),
             ('三阶核心', 'ASCENT CORE · 右肩', p_ascent_core, '回满护盾 + 第几次给第几档；第 4 次起只回盾（§5）')]),
 'wayfarer': dict(name='远行套件', en='WAYFARER', rule='BT 远征装（_sp_loadouts.nut）', sockets=[
     ('S_Muzzle_A/B', (-1.30, 0, 1.76), '阶梯机炮（同进阶）：6'), ('P_Fins', (-1.30, 0.2, 2.05), '提议 M-1 三片散热鳍：6.1'),
     ('S_Rocket_1..6', (0.60, -0.10, 5.73), '点名导弹舱（2×3 + 顶沿锁定灯）：6'), ('S_Shield_L', (1.72, 0, 3.35), '折屏投射器（同猎标）：6'),
     ('S_Vent_L/R', (0.23, 0.965, 5.57), '电雾（共用 7.5）：6'), ('S_Hand_L', (1.30, 0.0, 2.50), '重拳；爆发核心时左手扶炮：6.1'),
     ('S_Chest', (0, -1.084, 4.78), '核心就绪灯'), ('S_Thrust', (0.0, 1.41, 4.42), 'dash 喷口（共用 7.3）')],
     panels=[('阶梯机炮', 'STEP GUN · 俯视', p_stepgun, 'XO-16 规则（MONARCH §1，不带升级）'),
             ('点名导弹', 'ROLL CALL · 俯视', p_rollcall, '基础版多目标导弹（MONARCH §2.2）'),
             ('折屏', 'FOLD SCREEN · 俯视', p_screen, '同猎标（TONE §3）'),
             ('电雾（共用 7.5）', 'STATIC VEIL · 俯视', p_fog, '同共用 7.5'),
             ('爆发核心', 'OVERDRIVE · 时间线', p_overdrive, '5.5 s、20 发/s、每发 150（amp_core.txt:35、59、133–136）'),
             ('爆发核心光绳', 'OVERDRIVE · 俯视', lambda ax: p_stepgun(ax, True), '每发都带曳光，连成"光绳"')]),
}

def sheet(kit):
    K = KITS[kit]
    npan = len(K['panels']); ncol = 5; nrow = math.ceil(npan / ncol)
    H = 8.2 + 3.4 * nrow
    fig = plt.figure(figsize=(19.7, H), dpi=100, facecolor=BG)
    hb = 0.75 / H
    ax = fig.add_axes([0, 1 - hb, 1, hb]); ax.set_axis_off(); ax.add_patch(Rectangle((0, 0), 1, 1, fc=OWN, transform=ax.transAxes))
    ax.text(0.012, 0.5, f'M-1 • {K["name"]}', fontsize=26, weight='bold', va='center', color='#2A1030')
    ax.text(0.20, 0.5, f'{K["en"]}  ·  规则：{K["rule"]}  ·  外观原创  ·  挂点画在 M-1 R7 三视图上（Blender 正交投影，品红体块 = 提议新加的件）',
            fontsize=12, va='center', color='#2A1030')
    top = 1 - hb - 0.02
    vh = 5.9 / H
    for i, view in enumerate(('front', 'side', 'back')):
        a = fig.add_axes([0.005 + i * 0.24, top - vh, 0.235, vh]); a.set_axis_off()
        img = plt.imread(os.path.join(RD, f'{kit}_{view}.png'))
        a.imshow(img[40:880, 60:640])
        a.text(0, -10, {'front': '正视', 'side': '侧视（左；左边是前）', 'back': '背视'}[view], fontsize=12, weight='bold')
        for n, (nm, p, _) in enumerate(K['sockets'], 1):
            u, v = proj(view, p); u -= 60; v -= 40
            vis = visible(view, p)
            a.add_patch(Circle((u, v), 14, fc=OWN if vis else 'white', ec='#2A1030', lw=1.4, zorder=5))
            a.text(u, v, str(n), ha='center', va='center', fontsize=8, weight='bold', color='white' if vis else '#2A1030', zorder=6)
    a = fig.add_axes([0.73, top - vh, 0.265, vh]); a.set_axis_off(); a.set_xlim(0, 1); a.set_ylim(0, 1)
    a.text(0, 0.99, '挂点（实心 = 看得到，空心 = 被挡住）', fontsize=11.5, weight='bold', va='top')
    y = 0.93
    for n, (nm, p, desc) in enumerate(K['sockets'], 1):
        a.add_patch(Circle((0.02, y - 0.012), 0.013, fc=OWN, ec='#2A1030', transform=a.transAxes))
        a.text(0.02, y - 0.012, str(n), ha='center', va='center', fontsize=6.5, color='white', weight='bold')
        a.text(0.05, y, f'{nm}  ', fontsize=8.6, weight='bold', va='top')
        a.text(0.30, y, desc, fontsize=8.3, va='top')
        y -= 0.047
    y -= 0.02
    a.text(0, y, '示意配色（第 1 节，和轻 / 重稿同一套）：', fontsize=9, weight='bold', va='top'); y -= 0.045
    for c, t in ((OWN, 'M-1 本机色 #FF3FD2 · 能量'), (K_EDGE, '实弹（白芯暖黄边、灰烟）'), (E_GLOW, '电（冷白蓝）'),
                 (WARN, '敌人看到的边圈'), (THREAT, '威胁高亮（目标描边）'), (NEW, '提议新加的件（体块）')):
        a.add_patch(Rectangle((0, y - 0.028), 0.05, 0.026, fc=c, ec='#555', lw=0.4, transform=a.transAxes))
        a.text(0.065, y, t, fontsize=8.5, va='top'); y -= 0.038
    ptop = top - vh - 0.03
    fig.text(0.01, ptop, '技能示意（尺寸按 kits 规格页数值；俯视图里机体朝上）', fontsize=14, weight='bold', va='top')
    ph = 3.0 / H; pw = 0.188
    for i, (t, sub, fn, cap) in enumerate(K['panels']):
        r, c = divmod(i, ncol)
        x0 = 0.01 + c * (pw + 0.008); y0 = ptop - 0.035 - (r + 1) * (ph + 0.012)
        fr = fig.add_axes([x0, y0, pw, ph]); fr.set_xticks([]); fr.set_yticks([]); fr.set_facecolor('white')
        for sp in fr.spines.values(): sp.set_color('#BBBBBB')
        fr.text(0.03, 0.96, t, fontsize=12, weight='bold', va='top', transform=fr.transAxes)
        fr.text(0.03, 0.86, sub, fontsize=7.5, color='#888', va='top', transform=fr.transAxes)
        fr.text(0.03, 0.03, cap, fontsize=7.3, va='bottom', transform=fr.transAxes, wrap=True)
        ia = fig.add_axes([x0 + 0.01, y0 + ph * 0.13, pw - 0.02, ph * 0.66]); ia.set_axis_off(); ia.set_aspect('equal')
        fn(ia)
    fig.savefig(os.path.join(OUT, f'kit-M1-{kit}.png'), facecolor=BG); plt.close(fig)

for k in KITS: sheet(k)
print('ok')
