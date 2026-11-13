# py -3 compose.py <rend_dir> <out_img_dir>
# Builds one concept sheet per kit: three-views with numbered mount points + per-ability schematics.
import sys, json, math
from PIL import Image, ImageDraw, ImageFont

REND, OUT = sys.argv[1], sys.argv[2]
F = "C:/Windows/Fonts/msyh.ttc"; FB = "C:/Windows/Fonts/msyhbd.ttc"
def font(sz, bold=False): return ImageFont.truetype(FB if bold else F, sz)
BG = (245, 245, 242); INK = (30, 32, 36); GREY = (150, 150, 150)
C = dict(L1=(63, 224, 255), L2=(160, 112, 255), H1=(255, 176, 58), H2=(76, 255, 106))
KIN = (255, 200, 96); KINCORE = (255, 244, 214)
FIRE = (255, 138, 30); FIREDK = (138, 26, 10); CRUST = (30, 26, 24)
ARC = (111, 168, 255); ARCW = (207, 232, 255)
ENEMY = (255, 59, 48); THREAT = (255, 154, 46); PROP = (255, 0, 217)

def darker(c, k=0.6): return tuple(int(x * k) for x in c)

# ---------------- drawing helpers for schematic panels ----------------
class Panel:
    W, H = 330, 300
    def __init__(self, title, en, sub=""):
        self.im = Image.new("RGBA", (self.W, self.H), BG + (255,))
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self.d.rectangle([0, 0, self.W - 1, self.H - 1], outline=(200, 200, 196), width=2)
        self.d.text((10, 6), title, font=font(18, True), fill=INK)
        self.d.text((12, 32), en, font=font(12), fill=GREY)
        if sub: self.d.text((12, self.H - 22), sub, font=font(12), fill=(90, 90, 90))
    def t(self, xy, s, c=INK, sz=13, anchor="la"): self.d.text(xy, s, font=font(sz), fill=c, anchor=anchor)
    def titan(self, x, y, s=9, col=INK):  # top-down icon, forward = up
        self.d.ellipse([x - s, y - s, x + s, y + s], fill=col)
        self.d.polygon([(x, y - s - 9), (x - 5, y - s - 1), (x + 5, y - s - 1)], fill=col)
    def ring(self, x, y, r, col, w=2, dash=False, fill=None):
        if fill: self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
        if not dash: self.d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=w)
        else:
            n = max(12, int(r / 3))
            for i in range(0, n, 2):
                self.d.arc([x - r, y - r, x + r, y + r], 360 * i / n, 360 * (i + 1) / n, fill=col, width=w)
    def fan(self, x, y, r, a0, a1, col, fill=None, w=2):  # angles: 0 = forward(up), clockwise
        s, e = a0 - 90, a1 - 90
        if fill: self.d.pieslice([x - r, y - r, x + r, y + r], s, e, fill=fill)
        self.d.pieslice([x - r, y - r, x + r, y + r], s, e, outline=col, width=w)
    def diamond(self, x, y, r, col, fill=None, w=2):
        p = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        if fill: self.d.polygon(p, fill=fill)
        self.d.line(p + [p[0]], fill=col, width=w)
    def scale(self, px_per_m, m=10, x=None, y=None):
        x = x or self.W - 20 - px_per_m * m; y = y or self.H - 30
        L = px_per_m * m
        self.d.line([x, y, x + L, y], fill=INK, width=2)
        self.d.line([x, y - 4, x, y + 4], fill=INK, width=2); self.d.line([x + L, y - 4, x + L, y + 4], fill=INK, width=2)
        self.t((x + L / 2, y - 4), f"{m} m", sz=11, anchor="mb")
    def zig(self, x0, y0, x1, y1, col, n=6, amp=5, w=2):
        pts = []
        for i in range(n + 1):
            f = i / n; px = x0 + (x1 - x0) * f; py = y0 + (y1 - y0) * f
            if 0 < i < n:
                nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny) or 1
                k = amp * (1 if i % 2 else -1); px += nx / L * k; py += ny / L * k
            pts.append((px, py))
        self.d.line(pts, fill=col, width=w)
    def glob(self, x, y, r):  # crusted fire glob
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=CRUST)
        self.d.line([x - r * .6, y - r * .2, x, y + r * .1, x + r * .5, y - r * .4], fill=FIRE, width=2)
        self.d.line([x - r * .1, y + r * .1, x + r * .2, y + r * .6], fill=FIRE, width=2)

def u2m(u): return u * 0.0254

# ---------------- per-ability schematics ----------------
def P_rake(k):
    p = Panel("横栅霰炮", "RAKE-8 · 弹着图案（正视）", "8 颗两排；ADS 缩一半；寿命 0.30–0.35 s ≈ 34–39 m")
    cx, cy = 165, 150
    for s, a in ((1.0, 255), (0.5, 140)):
        for row in (-1, 1):
            for i in (-1.5, -0.5, 0.5, 1.5):
                p.diamond(cx + i * 52 * s, cy + row * 26 * s, 9 * s + 3, C[k], fill=C[k] + (a,))
    p.t((cx, 88), "腰射", sz=12, anchor="mm"); p.t((cx, 196), "ADS（内圈）", sz=12, anchor="mm")
    p.d.line([cx - 10, cy, cx + 10, cy], fill=INK); p.d.line([cx, cy - 10, cx, cy + 10], fill=INK)
    return p
def P_fault(k):
    p = Panel("走雷", "FAULTLINE · 俯视", "每 0.1 s 进 112 u（2.8 m），≤15 段 = 43 m，每段 r 2.8 m")
    s = 5.4; x0, y0 = 50, 250
    p.titan(x0, y0 + 12)
    for i in range(15):
        y = y0 - (i + 1) * 2.8 * s * 0.98; x = x0 + (i + 1) * 2.8 * s * 0.55
        if y < 60: break
        p.ring(x, y, 2.8 * s, ENEMY if i == 6 else darker(C[k], .9), w=1)
        p.zig(x - 2.8 * s * .8, y, x + 2.8 * s * .8, y, ARC, n=7, amp=4)
    p.t((x0 + 125, y0 - 80), "红圈 = 敌人看到的边圈", c=ENEMY, sz=11)
    p.scale(s, 10)
    return p
def P_guard(k):
    p = Panel("横刀架", "CROSSGUARD · 俯视", "前 150° 两侧都挡：× 0.3（核心 × 0.15）")
    x, y = 165, 165; r = 100
    p.fan(x, y, r, -150, 150, C[k], fill=C[k] + (70,))
    p.fan(x, y, r, 150, 210, GREY, fill=(150, 150, 150, 60))
    p.titan(x, y); p.d.line([x - 40, y - 18, x + 40, y - 18], fill=INK, width=5)
    p.t((x + r - 10, y - r + 6), "挡（被打处\n显出菱形格）", sz=12)
    p.t((x, y + r + 4), "背后 60° 不挡", sz=12, anchor="mt", c=(90, 90, 90))
    return p
def P_slip(k):
    p = Panel("隙行", "SLIPSTEP · 俯视", "1000 u/s + 竖直 200；1 s 相位；每 0.1 s 一个线框印")
    s = 8.0; x0, y0 = 70, 240
    p.d.rectangle([x0 - 12, y0 - 12, x0 + 12, y0 + 12], outline=(60, 60, 60), width=3)  # negative afterimage
    p.t((x0, y0 + 26), "负片残影", sz=11, anchor="mm")
    for i in range(1, 11):
        x = x0 + i * 2.2 * s * .8; y = y0 - i * 2.2 * s * .6
        a = 60 + i * 15
        p.d.rectangle([x - 10, y - 10, x + 10, y + 10], outline=C[k] + (min(a, 255),), width=2)
        for j in range(-8, 9, 4): p.d.line([x - 10, y + j, x + 10, y + j], fill=C[k] + (a // 2,), width=1)
    p.t((250, 90), "1.0 s 出相位\n0.7 s 起收紧", sz=12)
    p.scale(s, 10)
    return p
def P_unsheathe(k):
    p = Panel("出鞘", "UNSHEATHE · 时间线", "刀架递刀 → 握 → 出鞘；之后 12 s 只用刀")
    x0, x1, y = 20, 310, 150
    segs = [(0, .3, "摆臂递刀"), (.3, .5, "握·卡扣"), (.5, .75, "出鞘")]
    sx = (x1 - x0) / 1.0 * 0.45
    for a, b, s in segs:
        p.d.rectangle([x0 + a * sx, y - 18, x0 + b * sx, y + 18], fill=C[k] + (90 + int(a * 200),), outline=INK)
        p.t((x0 + (a + b) / 2 * sx, y + 30 + 16 * segs.index((a, b, s))), s, sz=11, anchor="mm")
    p.d.rectangle([x0 + .75 * sx, y - 18, x1, y + 18], fill=C[k] + (200,), outline=INK)
    p.t(((x0 + .75 * sx + x1) / 2, y), "核心 12 s（光刃缩短 = 倒计时）", sz=12, anchor="mm")
    for t_, lab in ((0, "0"), (.75, "0.75 s")): p.t((x0 + t_ * sx, y - 26), lab, sz=11, anchor="mm")
    p.d.line([60, 230, 270, 230], fill=INK, width=4); p.d.line([200, 222, 270, 222], fill=C[k], width=10)
    p.t((60, 248), "刀 3.6 m：光刃从刀尖往刀根缩", sz=11)
    return p
def P_drawcut(k):
    p = Panel("拔斩", "DRAWCUT · 俯视", "325 u（8.3 m），800；锥角平时 [原生]，核心 45")
    s = 18; x, y = 165, 245
    p.fan(x, y, 8.3 * s, -40, 40, C[k], fill=C[k] + (60,))
    p.d.arc([x - 8.3 * s, y - 8.3 * s, x + 8.3 * s, y + 8.3 * s], -130, -50, fill=C[k], width=5)
    p.titan(x, y); p.t((x, y - 8.3 * s - 6), "水平横斩光弧", sz=12, anchor="mb")
    p.scale(s, 5)
    return p
def P_carom(k):
    p = Panel("折弹（被动）", "CAROM · 跳弹", "反弹 1 次，速度 × 0.5，伤害不变")
    p.d.line([40, 230, 290, 230], fill=INK, width=4)
    p.d.line([50, 90, 170, 226], fill=C[k], width=3)
    for i in range(0, 10, 2):
        f0, f1 = i / 10, (i + 1) / 10
        p.d.line([170 + 110 * f0, 226 - 136 * f0, 170 + 110 * f1, 226 - 136 * f1], fill=darker(C[k], .75), width=3)
    p.d.line([158, 214, 170, 228, 182, 214], fill=C[k], width=3)
    p.t((60, 110), "实线", sz=12); p.t((235, 110), "虚线 = 二次弹", sz=12)
    return p
def P_after(k):
    p = Panel("残影（被动）", "AFTERIMAGE · 濒死相位", "濒死自动 3 s 相位，原地，不位移")
    x, y = 165, 150
    for i, dx in enumerate((-12, 0, 12)):
        p.d.rectangle([x - 40 + dx, y - 70, x + 40 + dx, y + 70], outline=C[k] + (90 + 60 * i,), width=2)
    for j in range(-70, 71, 10): p.d.line([x - 40, y + j, x + 40, y + j], fill=C[k] + (70,), width=1)
    p.t((x, y + 92), "3 个错开 0.2 m 的线框重影；扫描线由疏到密 = 3 s", sz=11, anchor="mm")
    return p

def P_longline(k):
    p = Panel("长线磁轨炮", "LONGLINE · 蓄力 5 档", "2.25 s 满；250 + 档 × 250 / 300；光束粗随档")
    for i in range(10):
        on = i < 6
        p.d.rectangle([30 + i * 27, 70, 52 + i * 27, 90], fill=C[k] if on else (60, 70, 80), outline=INK)
    p.t((30, 96), "枪身 10 格灯 = 蓄力表（图示 3 档）", sz=11)
    for st in range(6):
        y = 140 + st * 24; w = 1 + st * 2
        p.d.line([60, y, 300, y], fill=C[k], width=w); p.t((20, y), f"{st} 档", sz=11, anchor="lm")
        if st == 5:
            for xx in range(60, 300, 8): p.d.arc([xx, y - 7, xx + 8, y + 7], 0, 180, fill=darker(C[k], .7), width=1)
    return p
def P_scatter(k):
    p = Panel("散星", "SCATTERSTAR · 侧视 + 落点", "撞击 → 0.5 s 后 250 u 内随机 25 次")
    p.d.line([20, 250, 310, 250], fill=INK, width=2)
    pts = [(40, 150), (60, 118), (90, 108), (150, 150), (210, 210), (245, 248)]
    p.d.line(pts, fill=C[k], width=3); p.t((48, 100), "先上扬再转平", sz=11)
    import random; random.seed(3)
    r = 6.4 * 6
    p.d.ellipse([245 - r, 250 - r * .35, 245 + r, 250 + r * .35], outline=C[k], width=2)
    for _ in range(25):
        a = random.random() * 6.283; rr = r * math.sqrt(random.random())
        p.diamond(245 + rr * math.cos(a), 250 + rr * .35 * math.sin(a), 3, C[k], fill=(255, 255, 255, 220), w=1)
    p.t((245, 270), "r 6.4 m", sz=11, anchor="mm")
    return p
def P_anchor(k):
    p = Panel("锚线桩", "ANCHORPIN · 俯视", "1.5 s 武装（三灯）；350 u（8.9 m）内拴住")
    s = 13; x, y = 110, 170
    p.ring(x, y, 8.9 * s, C[k], w=1, dash=True)
    p.d.polygon([(x, y - 12), (x - 11, y + 8), (x + 11, y + 8)], fill=INK)
    for i, c in enumerate((C[k], C[k], (80, 80, 80))): p.d.ellipse([x - 12 + i * 9, y - 30, x - 6 + i * 9, y - 24], fill=c)
    tx, ty = 230, 120
    for i in range(6):
        f0, f1 = i / 6, (i + .8) / 6
        col = C[k] if i < 4 else ENEMY
        p.d.line([x + (tx - x) * f0, y + (ty - y) * f0, x + (tx - x) * f1, y + (ty - y) * f1], fill=col, width=3)
    p.titan(tx, ty, col=(120, 30, 30)); p.t((tx + 14, ty + 8), "敌泰坦", sz=11)
    p.t((150, 245), "段间变红 = 快断", sz=11)
    p.scale(s, 5)
    return p
def P_hover(k):
    p = Panel("悬翼", "HOVERWING · 竖直速度（u/s）", "0.5 s 225→450 → 1.25 s 降到 70 → 3 s 结束")
    x0, y0, W_, H_ = 40, 240, 260, 150
    p.d.line([x0, y0, x0 + W_, y0], fill=INK); p.d.line([x0, y0, x0, y0 - H_], fill=INK)
    def P(t, v): return (x0 + t / 3 * W_, y0 - v / 450 * (H_ - 10))
    p.d.line([P(0, 225), P(.5, 450), P(1.25, 70), P(3, 70)], fill=C[k], width=3)
    for t in (0, .5, 1.25, 3): p.t((P(t, 0)[0], y0 + 4), f"{t}", sz=10, anchor="mt")
    p.t((x0 - 4, P(0, 450)[1]), "450", sz=10, anchor="rm"); p.t((x0 - 4, P(0, 70)[1]), "70", sz=10, anchor="rm")
    # wing icon: folded vs open
    p.d.line([210, 80, 235, 60], fill=INK, width=3); p.d.line([235, 80, 260, 60], fill=INK, width=3)
    p.d.line([270, 75, 315, 75], fill=C[k], width=3); p.d.polygon([(312, 75), (306, 92), (318, 92)], fill=C[k])
    p.t((235, 92), "收起 → 展开 0.2 s", sz=10, anchor="mt")
    return p
def P_starfall(k):
    p = Panel("星落", "STARFALL · 6 s", "悬停 6 s；1 s 收枪后 12 发 /s 追踪火箭")
    x0, y0 = 60, 90
    p.d.line([x0 - 30, y0, x0 + 30, y0], fill=INK, width=4); p.titan(x0, y0 + 14)
    import random; random.seed(5)
    for i in range(9):
        tx, ty = 200 + random.randint(-40, 80), 230 + random.randint(-20, 20)
        p.d.line([(x0 + (i % 2) * 40 - 20, y0), (x0 + 60 + i * 6, y0 - 20), (tx, ty)], fill=C[k], width=2, joint="curve")
    p.d.line([20, 255, 310, 255], fill=INK, width=2)
    return p
def P_threader(k):
    p = Panel("贯星（被动）", "THREADER · 穿透", "穿透深度 500，穿过后伤害 × 1.0")
    p.d.line([20, 150, 310, 150], fill=C[k], width=5)
    for x in (130, 220):
        p.d.rectangle([x - 18, 110, x + 18, 190], outline=INK, width=2)
        for xx in (x - 18, x + 18): p.d.ellipse([xx - 9, 141, xx + 9, 159], outline=C[k], width=3)
    p.t((165, 210), "入口 / 出口各一个环（穿珠）", sz=12, anchor="mm")
    return p
def P_snap(k):
    p = Panel("断线爆（升级）", "SNAPBACK · 爆炸陷阱", "绳断 → 陷阱处 1000 / 1000，r 350 u（8.9 m）")
    s = 12; x, y = 140, 170
    p.ring(x, y, 8.9 * s, ENEMY, w=2, fill=C[k] + (50,))
    p.d.line([x, y, 290, 90], fill=C[k], width=3); p.t((250, 70), "亮光沿缆线回跑", sz=11)
    p.d.polygon([(x, y - 12), (x - 11, y + 8), (x + 11, y + 8)], fill=ENEMY)
    p.scale(s, 5)
    return p
def P_twin(k):
    p = Panel("双星（升级）", "TWINSTAR · 双发集束", "两翼各一发，间隔 0.1 s，小八字分开")
    x, y = 165, 240; p.titan(x, y)
    p.d.line([x - 30, y - 10, x - 60, 80], fill=C[k], width=3); p.d.line([x + 30, y - 10, x + 60, 80], fill=C[k], width=3)
    for xx in (x - 60, x + 60): p.ring(xx, 72, 22, C[k], dash=True)
    p.t((x - 60, 105), "左 0 s", sz=11, anchor="mm"); p.t((x + 60, 105), "右 0.1 s", sz=11, anchor="mm")
    return p
def P_hunt(k):
    p = Panel("猎眼（被动）", "HUNTSIGHT · 威胁光学", "ADS 时准星周围 1.5 × 1.1 范围内敌人描橙边")
    p.d.rectangle([20, 60, 310, 260], fill=(40, 46, 54))
    p.d.rectangle([165 - 75, 160 - 55, 165 + 75, 160 + 55], outline=(200, 200, 200, 120), width=1)
    p.d.rectangle([190, 130, 222, 190], outline=THREAT, width=3)
    p.d.rectangle([60, 120, 84, 170], outline=(120, 120, 120), width=2)
    p.d.line([160, 160, 170, 160], fill=C[k]); p.d.line([165, 155, 165, 165], fill=C[k])
    p.t((72, 180), "范围外不亮", sz=10, c=(200, 200, 200), anchor="mt")
    return p

def P_slag(k, wild=False):
    p = Panel("散渣（被动）" if wild else "熔渣臼炮", "SLAGSPRAY · 9 团" if wild else "SLAGMORTAR · 落点俯视",
              "1 底火 + 8 散火，散开 200" if wild else "炸开 r 150 u（3.8 m）；1+4 团火，每团 r 45 u，2–2.5 s")
    s = 14; x, y = 165, 160
    p.ring(x, y, 3.8 * s, FIRE, w=2, fill=FIRE + (40,))
    import random; random.seed(1 if wild else 2)
    n = 8 if wild else 4; spread = 5.5 if wild else 2.6
    p.glob(x, y, 9)
    for i in range(n):
        a = i / n * 6.283 + random.random() * .5; rr = spread * s * (0.7 + .3 * random.random())
        gx, gy = x + rr * math.cos(a), y + rr * math.sin(a)
        p.d.line([x, y, gx, gy], fill=FIRE + (120,), width=1)
        p.glob(gx, gy, 7 if wild else 9); p.ring(gx, gy, 1.1 * s, ENEMY, w=1)
    p.scale(s, 5)
    return p
def P_firebreak(k):
    p = Panel("火堤", "FIREBREAK · 俯视", "约 1 s 推到 1500 u（38 m）；每段 r 60 u，烧 5.2 s")
    s = 5.8; x, y = 70, 260; p.titan(x, y)
    L = 38 * s; p.d.rectangle([x - 1.5 * s * 1.5, y - 20 - L * .82, x + 1.5 * s * 1.5, y - 20], fill=FIRE + (90,), outline=ENEMY)
    p.d.line([x, y - 20, x, y - 20 - L * .82], fill=CRUST, width=3)
    p.t((x + 22, y - 60), "后段：火（结壳地面）", sz=11); p.t((x + 22, y - 20 - L * .82 + 8), "前端：深色油线 + 追着跑的火头", sz=11)
    p.scale(s, 10)
    return p
def P_gate(k):
    p = Panel("炉门幕", "FURNACE GATE · 俯视", "吸收罩 120°（r 120）；烧伤 r 175 u、左右 70°")
    s = 32; x, y = 165, 245
    p.fan(x, y, 4.4 * s, -70, 70, FIRE, fill=FIRE + (60,))
    p.fan(x, y, 3.05 * s, -60, 60, k and C[k], fill=(255, 220, 160, 90))
    p.titan(x, y); p.t((x, y - 4.4 * s - 6), "扇形火 r 4.4 m", sz=11, anchor="mb"); p.t((x, y - 70), "热浪帘", sz=11, anchor="mm")
    p.scale(s, 2)
    return p
def P_fume(k, barrels=False):
    p = Panel("爆罐（升级）" if barrels else "油雾罐", "FLASHCAN · 点燃先爆" if barrels else "FUME CAN · 点燃后俯视",
              "先爆 100 / 500，r 350 u（8.9 m）" if barrels else "12 条射线 × 2 点（150 / 225 u），每点 r 75 u；中心 75 u 无火")
    s = 11 if barrels else 15; x, y = 165, 160
    if barrels: p.ring(x, y, 8.9 * s, ENEMY, w=2, fill=FIRE + (35,))
    p.ring(x, y, 6.1 * s, GREY, dash=True)
    for i in range(12):
        a = i / 12 * 6.283
        for d_ in (3.8, 5.7):
            gx, gy = x + d_ * s * math.cos(a), y + d_ * s * math.sin(a)
            p.d.ellipse([gx - 1.9 * s, gy - 1.9 * s, gx + 1.9 * s, gy + 1.9 * s], fill=FIRE + (45,))
    p.d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(90, 80, 60), outline=(255, 0, 0) if barrels else C[k], width=3)
    p.scale(s, 5)
    return p
def P_hearth(k, ember=False):
    p = Panel("余烬路（被动）" if ember else "开炉", "EMBER TRAIL · 沿路烧 1.5 s" if ember else "OPEN HEARTH · 俯视",
              "火河过后地面真在烧 1.5 s（缝宽 + 火苗）" if ember else "蓄 0.75 s；三道并排宽 ≈ 15 m、长 46 m；每目标一次")
    s = 4.6; x, y = 165, 270; p.titan(x, y)
    for i in (-1, 0, 1):
        x0 = x + i * 5 * s
        top = y - 18 - 46 * s * .9
        p.d.rectangle([x0 - 2.5 * s, top, x0 + 2.5 * s, y - 18], fill=(FIRE + (110,)) if not ember else (CRUST + (230,)), outline=FIREDK)
        if ember:
            for yy in range(int(top) + 6, y - 22, 14): p.d.line([x0 - 6, yy, x0 + 4, yy + 6], fill=FIRE, width=3)
    p.scale(s, 10)
    return p
def P_triple(k):
    p = Panel("三膛（升级）", "TRIPLE CHAMBER · 双 / 三连发", "弹匣 2 / 3；分段换弹 1.6 s（循环 1.2、收尾 0.8）")
    x, y = 165, 160; R = 70
    p.d.ellipse([x - R, y - R, x + R, y + R], fill=(60, 50, 45), outline=INK, width=3)
    for i in range(3):
        a = -90 + i * 120; cx, cy = x + 40 * math.cos(math.radians(a)), y + 40 * math.sin(math.radians(a))
        p.d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=C[k] if i < 2 else (40, 35, 30), outline=INK)
    p.t((x, y + R + 18), "琥珀窗亮 = 有弹（图示 2 发）", sz=12, anchor="mm")
    return p

def P_mill(k):
    p = Panel("碾盘六管炮", "MILLSTONE · 炮口环 = 转管进度", "转满 1.5 s 才开火；退 0.75 s；15 发 /s")
    for j, frac in enumerate((0.33, 0.66, 1.0)):
        x, y = 65 + j * 100, 140
        p.d.ellipse([x - 38, y - 38, x + 38, y + 38], outline=(80, 80, 80), width=8)
        p.d.arc([x - 38, y - 38, x + 38, y + 38], -90, -90 + 360 * frac, fill=C[k], width=8)
        for i in range(6):
            a = i * 60 + j * 25; p.d.ellipse([x + 20 * math.cos(math.radians(a)) - 6, y + 20 * math.sin(math.radians(a)) - 6,
                                                x + 20 * math.cos(math.radians(a)) + 6, y + 20 * math.sin(math.radians(a)) + 6], fill=INK)
        p.t((x, y + 52), f"{frac * 1.5:.1f} s", sz=12, anchor="mm")
    p.t((165, 225), "走满一圈 = 可开火", sz=12, anchor="mm")
    return p
def P_sledge(k):
    p = Panel("重锤", "SLEDGE · 俯视", "停转蓄 0.75 s；近距 10° 锥 2000 / 远距穿透 2000 + 爆 1800")
    x, y = 90, 250; p.titan(x, y)
    p.fan(x, y, 180, -5, 5, C[k], fill=C[k] + (90,))
    p.t((x + 10, 80), "近距：10° 锥", sz=11)
    x2 = 240; p.titan(x2, y); p.d.line([x2, y - 18, x2, 70], fill=C[k], width=6); p.ring(x2, 110, 18, C[k], fill=C[k] + (80,))
    p.t((x2 + 8, 70), "远距：穿透 + 爆", sz=11)
    return p
def P_bulwark(k):
    p = Panel("管前盾", "MUZZLE BULWARK · 侧视", "r 105 u（2.7 m）球，2500 血，6 s")
    s = 26; x, y = 150, 150
    p.d.rectangle([20, y - 14, x - 2.7 * s + 30, y + 14], fill=(50, 55, 50))
    p.d.ellipse([x - 2.7 * s, y - 2.7 * s, x + 2.7 * s, y + 2.7 * s], outline=C[k], width=2, fill=C[k] + (30,))
    for i in range(-6, 7):
        yy = y + i * 2.7 * s / 7; half = math.sqrt(max(0, (2.7 * s) ** 2 - (yy - y) ** 2))
        if i % 2 == 0: p.d.line([x - half, yy, x + half, yy], fill=C[k] + (160,), width=2)
    p.t((x, y + 2.7 * s + 10), "扫描线条数 = 剩余血量", sz=11, anchor="mt")
    p.scale(s, 2)
    return p
def P_rechamber(k):
    p = Panel("换膛", "RECHAMBER · 收束套", "近距 ↔ 远距；套环滑到炮口 = 远距")
    for j, (lab, pos) in enumerate((("近距", 0.25), ("远距", 0.9))):
        y = 110 + j * 90
        p.d.rectangle([30, y - 18, 290, y + 18], fill=(70, 80, 60), outline=INK)
        sx = 30 + 260 * pos
        p.d.rectangle([sx - 18, y - 26, sx + 18, y + 26], fill=PROP + (200,), outline=INK)
        p.t((30, y - 30), lab, sz=12)
    return p
def P_swarm(k):
    p = Panel("群锁", "SWARMLOCK · 12 s", "最多 6 个锁定；子弹弯向锁点；不耗弹；伤害 × 1.2")
    p.d.rectangle([20, 60, 310, 260], fill=(40, 46, 54))
    import random; random.seed(7)
    for i in range(6):
        x, y = 50 + i * 45, 110 + random.randint(-30, 60)
        p.diamond(x, y, 14, C[k]); p.d.line([165, 250, (165 + x) / 2, 200, x, y + 14], fill=C[k] + (160,), width=1, joint="curve")
    for i in range(6): p.diamond(110 + i * 22, 245, 6, C[k], fill=C[k])
    return p
def P_drill(k):
    p = Panel("钻芯弹（升级）", "DRILLCORE · 穿甲", "穿透深度 0 → 500 u（12.7 m）")
    p.d.line([20, 150, 310, 150], fill=KIN, width=3)
    for xx in range(30, 60, 6): p.d.arc([xx, 143, xx + 6, 157], 0, 180, fill=KINCORE, width=2)
    p.d.rectangle([150, 105, 180, 195], outline=INK, width=2)
    p.d.ellipse([185, 135, 215, 165], fill=(122, 117, 112, 160))
    p.t((200, 210), "出口灰烟", sz=11, anchor="mm")
    return p

# shared
def P_fist(k):
    p = Panel("重拳", "HAMMERFIST · 俯视", "左拳；500；280 u（7.1 m）锥 20；0.8 s + 1.0 s")
    s = 24; x, y = 165, 260; p.titan(x, y)
    p.fan(x, y, 7.1 * s, -20, 20, INK, fill=(255, 255, 255, 120)); p.scale(s, 2)
    return p
def P_tread(k):
    p = Panel("碾步", "TREAD · 侧视", "≥ 50 u/s；碰到最下 15 % 高度；一次 5000")
    p.d.rectangle([110, 40, 220, 250], outline=INK, width=2)
    p.d.rectangle([110, 250 - 31, 220, 250], fill=(255, 59, 48, 80), outline=ENEMY)
    p.d.line([20, 250, 310, 250], fill=INK, width=2); p.t((228, 232), "最下 15 %", sz=11)
    return p
def P_ram(k):
    p = Panel("冲撞", "RAM · dash", "dash 中碾步照样触发；前方压缩波只表示速度")
    x, y = 120, 160; p.titan(x, y)
    p.d.arc([x - 50, y - 70, x + 50, y + 20], 220, 320, fill=INK, width=3)
    for dy in (-6, 6): p.d.line([x - 20, y + dy, x - 90, y + dy], fill=(120, 120, 120), width=2)
    return p
def P_drop(k):
    p = Panel("坠击", "DROPSTRIKE · 俯视", "90 u 满 400 · 90–120 u 衰减 · 240 u 警告")
    s = 17; x, y = 165, 160
    p.ring(x, y, u2m(240) * s, ENEMY, w=1)
    p.ring(x, y, u2m(120) * s, ENEMY, w=2, dash=True)
    p.ring(x, y, u2m(90) * s, ENEMY, w=3, fill=ENEMY + (50,))
    p.t((x, y + u2m(240) * s + 4), "警告 6.1 m", sz=11, anchor="mt", c=ENEMY)
    p.scale(s, 2)
    return p
def P_smoke(k):
    p = Panel("电雾", "STATIC VEIL · 俯视", "内 320 / 外 375 u；1 s 后通电；每 0.1 s 一跳；5 s")
    s = 12; x, y = 165, 160
    p.ring(x, y, u2m(375) * s, ENEMY, dash=True); p.ring(x, y, u2m(320) * s, ENEMY, w=2, fill=(170, 175, 180, 90))
    import random; random.seed(11)
    for _ in range(9):
        a, b = random.random() * 6.28, random.random() * 6.28; r1, r2 = random.random() * 80, random.random() * 80
        p.zig(x + r1 * math.cos(a), y + r1 * math.sin(a), x + r2 * math.cos(b), y + r2 * math.sin(b), ARC, n=6, amp=5)
    p.scale(s, 5)
    return p
def P_core(k):
    p = Panel("熔心弹射", "COREBREAK · 倒计时", "板缝从胸口亮到四肢末端 = 爆；数值缺页（O-4）")
    x, y = 165, 160
    p.d.rectangle([x - 40, y - 70, x + 40, y + 10], outline=INK, width=2)
    for i, (dx, dy) in enumerate(((-70, -40), (70, -40), (-25, 90), (25, 90))):
        p.d.line([x + dx * .5, y - 30 + dy * .2, x + dx, y + dy], fill=(255, 210, 120), width=4)
    p.d.ellipse([x - 12, y - 42, x + 12, y - 18], fill=(255, 240, 200), outline=(255, 150, 40), width=3)
    p.t((x, y - 85), "舱门炸飞、驾驶员弹出 × 2", sz=11, anchor="mm")
    return p

KITS = {
 "L2": dict(name="L-2 · 断潮套件", rules="规则：Ronin（RONIN.md）", file="kit-L2-duanchao.png", views=["front", "side", "back"],
            panels=[P_rake, P_fault, P_guard, P_slip, P_unsheathe, P_drawcut, P_carom, P_after],
            marks=[("S_Muzzle", "霰炮口：3.1 横栅霰炮 / 3.7 折弹", C["L2"]), ("S_Sword_Back", "刀架（刀柄）：3.2–3.6", C["L2"]),
                   ("P_RackHinge", "提议 MC-1 刀架摆臂铰链", PROP), ("S_Sword_R", "右手握刀", C["L2"]), ("S_Holster", "收霰炮（右髋后）", GREY),
                   ("S_Phase", "3.4 隙行 / 3.8 残影", C["L2"]), ("S_Thrust", "dash 喷口（共用）", INK), ("S_Vent_L", "电雾（共用）", ARC), ("S_Vent_R", "电雾（共用）", ARC),
                   ("S_Chest", "熔心弹射（共用）", FIRE)]),
 "L1": dict(name="L-1 · 鹞翼套件", rules="规则：Northstar（NORTHSTAR.md）", file="kit-L1-yaoyi.png", views=["front", "side", "back", "front_open", "side_open"],
            panels=[P_longline, P_scatter, P_anchor, P_hover, P_starfall, P_threader, P_snap, P_twin, P_hunt],
            marks=[("S_Muzzle", "长枪口：4.1 长线 / 4.6 贯星", C["L1"]), ("S_Pod_L", "翼舱：4.2 散星 / 4.5 星落 / 4.8 双星", C["L1"]), ("S_Pod_R", "翼舱（右）", C["L1"]),
                   ("S_VTOL_L", "翼尖喷口：4.4 悬翼（MC-3 罩瓣）", C["L1"]), ("S_VTOL_R", "翼尖喷口（右）", C["L1"]), ("S_Tether", "前臂发射器：4.3 锚线 / 4.7 断线爆", C["L1"]),
                   ("S_Optic", "三镜头：4.9 猎眼", THREAT), ("S_Hand_L", "重拳（共用）", INK), ("S_Thrust", "背喷口：悬停 / dash", INK),
                   ("S_Vent_L", "电雾（共用）", ARC), ("S_Vent_R", "电雾（共用）", ARC), ("S_Chest", "熔心弹射（共用）", FIRE)]),
 "H1": dict(name="H-1 · 熔炉套件", rules="规则：Scorch（SCORCH.md）", file="kit-H1-ronglu.png", views=["front", "side", "back"],
            panels=[P_slag, P_firebreak, P_gate, P_fume, P_hearth, lambda k: P_slag(k, True), lambda k: P_hearth(k, True), lambda k: P_fume(k, True), P_triple],
            marks=[("S_Muzzle", "臼炮口：5.1 熔渣 / 5.6 散渣", FIRE), ("P_Cylinder3", "提议 MC-4 三膛转轮：5.9", PROP), ("S_Flame_L", "左臂喷口：5.2 火堤 / 5.3 炉门幕", FIRE),
                   ("S_Trap", "右肩发射管：5.4 油雾罐 / 5.8 爆罐", FIRE), ("P_HearthVents", "提议 MC-5 炉底三炉口：5.5 / 5.7", PROP),
                   ("S_Tank_L", "背罐顶：核心排气、液位窗", C["H1"]), ("S_Tank_R", "背罐顶", C["H1"]), ("S_Hand_L", "重拳（共用）", INK),
                   ("S_Vent_L", "电雾（共用）", ARC), ("S_Vent_R", "电雾（共用）", ARC), ("S_Chest", "熔心弹射（共用）", FIRE), ("S_Thrust", "dash 喷口（共用）", INK)]),
 "H2": dict(name="H-2 · 碾盘套件", rules="规则：Legion（LEGION.md）", file="kit-H2-nianpan.png", views=["front", "side", "back"],
            panels=[P_mill, P_sledge, P_bulwark, P_rechamber, P_swarm, P_drill],
            marks=[("S_Muzzle", "炮口：6.1 碾盘 / 6.2 重锤 / 6.6 钻芯", KIN), ("P_MuzzleRing", "提议 MC-7 炮口发光环", PROP), ("P_ChokeSleeve", "提议 MC-6 收束套：6.4 换膛", PROP),
                   ("S_GunShield", "6.3 管前盾", C["H2"]), ("S_Drum", "弹鼓（转）", KIN), ("S_Eject", "抛壳口", KIN), ("S_Optic", "6.5 群锁（镜头）", C["H2"]),
                   ("S_Hand_L", "重拳（共用）/ 换膛扶炮", INK), ("S_Vent_L", "电雾（共用）", ARC), ("S_Vent_R", "电雾（共用）", ARC), ("S_Chest", "熔心弹射（共用）", FIRE), ("S_Thrust", "dash 喷口（共用）", INK)]),
}
VIEWNAME = dict(front="正视", side="侧视（左）", back="背视", front_open="正视·翼展开", side_open="侧视·翼展开")

def sheet(tag, kit):
    pts = json.load(open(f"{REND}/{tag}_pts.json"))
    views = kit["views"]; vw, vh = 470, 556
    legend_w = 520
    top = 90; W = max(len(views) * vw + legend_w + 40, 4 * Panel.W + 60)
    per = max(4, (W - 40) // (Panel.W + 14)); rows = math.ceil(len(kit["panels"]) / per); pan_top = top + vh + 70
    H = pan_top + rows * (Panel.H + 14) + 20
    im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, W, 70], fill=C[tag] + (60,))
    d.text((20, 10), kit["name"], font=font(34, True), fill=INK)
    d.text((22 + d.textlength(kit["name"], font=font(34, True)) + 20, 26), kit["rules"] + " · 外观原创 · 挂点画在 v3 模型三视图上（Blender 正交投影）",
           font=font(16), fill=(60, 60, 60))
    for vi, v in enumerate(views):
        src = Image.open(f"{REND}/{tag}_{v}.png").convert("RGBA")
        sc = vw / src.width; src = src.resize((vw, int(src.height * sc)))
        ox, oy = 20 + vi * vw, top
        im.alpha_composite(src, (ox, oy))
        d.text((ox + 10, oy + 4), VIEWNAME[v], font=font(16, True), fill=INK)
        for n, (name, desc, col) in enumerate(kit["marks"], 1):
            if name not in pts["views"][v]: continue
            px, py, occ, _ = pts["views"][v][name]; px = ox + px * sc; py = oy + py * sc
            if not (ox < px < ox + vw and oy < py < oy + vh): continue
            r = 11
            if occ: d.ellipse([px - r, py - r, px + r, py + r], outline=col, width=3, fill=(255, 255, 255, 150))
            else: d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=INK, width=2)
            d.text((px, py), str(n), font=font(12, True), fill=(255,255,255) if (sum(col)<200 and not occ) else INK, anchor="mm")
    lx = 20 + len(views) * vw + 20; ly = top + 10
    d.text((lx, ly), "挂点（实心 = 看得到，空心 = 被挡住）", font=font(16, True), fill=INK); ly += 30
    for n, (name, desc, col) in enumerate(kit["marks"], 1):
        d.ellipse([lx, ly, lx + 22, ly + 22], fill=col, outline=INK, width=2)
        d.text((lx + 11, ly + 11), str(n), font=font(12, True), fill=(255,255,255) if sum(col)<200 else INK, anchor="mm")
        d.text((lx + 30, ly + 1), name, font=font(13, True), fill=INK)
        d.text((lx + 30 + d.textlength(name, font=font(13, True)) + 8, ly + 1), desc, font=font(13), fill=(50, 50, 50)); ly += 30
    ly += 10
    d.rectangle([lx, ly, lx + 22, ly + 22], fill=PROP); d.text((lx + 30, ly + 1), "品红体块 = 提议新加的件（第 8 节，没改模型）", font=font(13), fill=INK); ly += 34
    d.text((lx, ly), "示意配色（第 1 节）：", font=font(13, True), fill=INK); ly += 24
    for lab, col in (("本机色 · 能量", C[tag]), ("实弹", KIN), ("火", FIRE), ("电", ARC), ("敌人看到的边圈", ENEMY), ("威胁高亮", THREAT)):
        d.rectangle([lx, ly, lx + 34, ly + 16], fill=col); d.text((lx + 42, ly - 1), lab, font=font(13), fill=INK); ly += 22
    d.text((20, pan_top - 40), "技能示意（尺寸按 kits 规格页数值；俯视图里机体朝上）", font=font(20, True), fill=INK)
    for i, fn in enumerate(kit["panels"]):
        p = fn(tag); x = 20 + (i % per) * (Panel.W + 14); y = pan_top + (i // per) * (Panel.H + 14)
        im.alpha_composite(p.im, (x, y))
    im.convert("RGB").save(f"{OUT}/{kit['file']}", optimize=True)
    print("wrote", kit["file"], im.size)

def shared():
    W = 4 * (Panel.W + 14) + 40; tops = 90
    small = 300
    H = tops + 420 + 2 * (Panel.H + 14) + 60
    im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, W, 70], fill=(200, 200, 200, 255))
    d.text((20, 12), "共用六个动作 · 通用挂点", font=font(32, True), fill=INK)
    d.text((440, 26), "规则：T-b、MONARCH §7（电烟）；核弹弹射缺页", font=font(16), fill=(60, 60, 60))
    gen = [("S_Hand_L", "重拳", INK), ("S_Vent_L", "电雾", ARC), ("S_Vent_R", "电雾", ARC), ("S_Thrust", "dash", (90, 90, 90)), ("S_Chest", "熔心", FIRE), ("S_Foot_L", "碾步/坠击", (120, 90, 60)), ("S_Foot_R", "碾步/坠击", (120, 90, 60))]
    for i, tag in enumerate(("L1", "L2", "H1", "H2")):
        pts = json.load(open(f"{REND}/{tag}_pts.json"))
        for vj, v in enumerate(("front", "back")):
            src = Image.open(f"{REND}/{tag}_{v}.png").convert("RGBA"); sc = 170 / src.width
            src = src.resize((170, int(src.height * sc))); ox = 20 + i * 350 + vj * 170; oy = tops
            im.alpha_composite(src, (ox, oy))
            for name, lab, col in gen:
                if name not in pts["views"][v]: continue
                px, py, occ, _ = pts["views"][v][name]; px = ox + px * sc; py = oy + py * sc
                if occ: d.ellipse([px - 6, py - 6, px + 6, py + 6], outline=col, width=2)
                else: d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=col, outline=INK)
        d.text((20 + i * 350 + 170, tops + 205), tag + "（正 / 背）", font=font(14, True), fill=INK, anchor="mm")
    ly = tops + 225; lx = 20
    for name, lab, col in gen[:1] + gen[1:2] + gen[3:6]:
        d.ellipse([lx, ly, lx + 16, ly + 16], fill=col, outline=INK); d.text((lx + 22, ly - 2), f"{name} {lab}", font=font(13), fill=INK); lx += 200
    pan_top = tops + 270
    for i, fn in enumerate((P_fist, P_tread, P_ram, P_drop, P_smoke, P_core)):
        p = fn("L1"); x = 20 + (i % 4) * (Panel.W + 14); y = pan_top + (i // 4) * (Panel.H + 14)
        im.alpha_composite(p.im, (x, y))
    im = im.crop((0, 0, W, pan_top + 2 * (Panel.H + 14) + 10))
    im.convert("RGB").save(f"{OUT}/shared-actions.png", optimize=True); print("wrote shared")

def language():
    W, H = 1400, 560
    im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im, "RGBA")
    d.text((20, 12), "整套泰坦武器的视觉语言（第 1 节）", font=font(30, True), fill=INK)
    cols = [("实弹", "细直线 · 白芯暖黄边 · 火星 + 灰烟", [KINCORE, KIN, (122, 117, 112)]),
            ("能量", "硬边几何 · 菱片 · 扫描线 · 本机色", [C["L1"], C["L2"], C["H1"], C["H2"]]),
            ("火 / 铝热", "软团 + 滴落 · 黑壳发光缝", [(255, 248, 224), FIRE, FIREDK, CRUST]),
            ("电", "折线分叉 · 每 0.1 s 重画 · 冷白蓝", [ARCW, ARC])]
    for i, (n, desc, sw) in enumerate(cols):
        x = 20 + i * 345; y = 70
        d.rectangle([x, y, x + 330, y + 460], outline=(200, 200, 196), width=2)
        d.text((x + 12, y + 8), n, font=font(24, True), fill=INK); d.text((x + 12, y + 44), desc, font=font(13), fill=(70, 70, 70))
        for j, c in enumerate(sw): d.rectangle([x + 12 + j * 78, y + 74, x + 82 + j * 78, y + 114], fill=c, outline=INK)
        cx, cy = x + 165, y + 280
        if i == 0:
            for k_ in range(5): d.line([x + 30, cy - 80 + k_ * 40, x + 300, cy - 100 + k_ * 40], fill=KIN, width=3); d.line([x + 260, cy - 96 + k_ * 40, x + 300, cy - 100 + k_ * 40], fill=KINCORE, width=3)
        if i == 1:
            p = Panel("", "")
            for k_, c in enumerate((C["L1"], C["L2"], C["H1"], C["H2"])):
                q = [(cx - 110 + k_ * 70, cy - 30), (cx - 85 + k_ * 70, cy), (cx - 110 + k_ * 70, cy + 30), (cx - 135 + k_ * 70, cy)]
                d.polygon(q, fill=c + (180,), outline=INK)
            for yy in range(cy + 60, cy + 150, 12): d.line([x + 40, yy, x + 290, yy], fill=C["H2"], width=2)
            d.text((cx, cy + 165), "扫描线（护盾 / 相位）", font=font(12), fill=INK, anchor="mm")
        if i == 2:
            for k_ in range(5):
                gx, gy = x + 60 + k_ * 55, cy + (k_ % 2) * 30
                d.ellipse([gx - 22, gy - 22, gx + 22, gy + 22], fill=CRUST); d.line([gx - 14, gy - 4, gx, gy + 3, gx + 12, gy - 8], fill=FIRE, width=3)
                d.ellipse([gx - 10, gy - 60, gx + 10, gy - 26], fill=FIRE + (150,))
            d.text((cx, cy + 90), "熄灭后黑壳留 3 s（装饰，无伤害）", font=font(12), fill=INK, anchor="mm")
        if i == 3:
            pp = Panel("", ""); pp.d = d
            import random; random.seed(4)
            for _ in range(7):
                pp.zig(x + 30 + random.random() * 260, cy - 90 + random.random() * 160, x + 30 + random.random() * 260, cy - 90 + random.random() * 160, ARC, n=7, amp=7, w=3)
            d.text((cx, cy + 110), "画面跳的节拍 = 伤害跳的节拍（0.1 s）", font=font(12), fill=INK, anchor="mm")
    im.convert("RGB").save(f"{OUT}/visual-language.png", optimize=True); print("wrote language")

for tag, kit in KITS.items(): sheet(tag, kit)
shared(); language()
