# Mount sheets (annotated Blender blockouts) + effect schematics for the four M-1 kits.
import json, math, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Wedge, Arc, Rectangle, FancyArrowPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, 'renders')
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\simhei.ttf'):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams['axes.unicode_minus'] = False

FAM = {
    '能量': '#B04CFF', '实弹': '#D9A441', '电': '#4FE3FF', '屏障': '#DCEBFF',
    '回补': '#5CFF9D', '标记': '#FFD23F', '机体色': '#FF5A1F', '通用座': '#4D5259',
}
S = 900 / 7.0
CZ = 3.05

def proj(view, p):
    x, y, z = p
    if view == 'front': u = x
    elif view == 'side': u = y
    else: u = -x
    return 350 + u * S, 450 - (z - CZ) * S

HP = {  # id: (name, world point, views)
    'HP1': ('右前臂炮座', (-1.30, 0.0, 2.6), ('front', 'back')),
    'HP2': ('左肩舱', (0.62, 0.30, 5.70), ('front', 'side')),
    'HP3': ('左前臂外侧', (1.66, 0.0, 3.35), ('front', 'side')),
    'HP4': ('胸口发射器', (0.0, -1.084, 4.78), ('front', 'side')),
    'HP5': ('投掷口', (0.60, 0.72, 5.86), ('side', 'back')),
    'HP6': ('背包顶', (0.56, 1.24, 5.70), ('side', 'back')),
}

KITS = {
    'base': ('M-1 通用挂点（不带套件）', [
        ('HP1', '通用座', '右前臂炮座：肘下保留 0.87 m 炮座，炮座以下整段炮管按套件换'),
        ('HP2', '通用座', '左肩舱座：原火箭巢的位置，舱体按套件换'),
        ('HP3', '通用座', '左前臂外侧导轨：原护盾垫 S_Shield_L，防御投射器按套件换'),
        ('HP4', '通用座', '胸口发射器 S_Chest：核心的出口和"核心就绪"灯，所有套件共用'),
        ('HP5', '通用座', '投掷口 S_Mine_L：绊线桩、声呐钟从这里抛出'),
        ('HP6', '通用座', '背包顶（新增 S_Smoke_L/R）：电烟罐架'),
    ]),
    'spectra': ('分光 SPECTRA（规则：Ion）', [
        ('HP1', '能量', '三棱步枪：三角截面炮管，炮口两片导流翼（开镜时外张）；三道能量槽 = 棱压三格'),
        ('HP2', '能量', '针光：细长方管发射器 + 尾部两片散热鳍'),
        ('HP3', '屏障', '捕光壳：三片刻面花瓣护腕，举臂时张开投出刻面壳'),
        ('HP4', '能量', '全谱光束：发射器外三片三角棱叶（核心蓄力时翻起）'),
        ('HP5', '能量', '棱栅：三根三棱桩卧在肩舱后上'),
    ]),
    'tally': ('猎标 TALLY（规则：Tone）', [
        ('HP1', '实弹', '刻痕炮：短粗炮管 + 六角制退器；外侧三室转鼓（三连装蓄级）'),
        ('HP1', '标记', '炮身三颗刻度灯：准星下目标的标记层数'),
        ('HP2', '实弹', '清账导弹舱：2×3 方管、虹膜盖；外侧锁定探头'),
        ('HP3', '屏障', '折屏投射器：竖导轨 + 四片百叶（展开成墙）'),
        ('HP4', '实弹', '核心：舱门中板下的三联小发射格（核心时和肩舱轮流）'),
        ('HP5', '标记', '探钟：卧在肩舱后的钟形声呐弹'),
    ]),
    'ascent': ('进阶 ASCENT（规则：Monarch）', [
        ('HP1', '实弹', '阶梯机炮：双管交替 + 上方供弹盒'),
        ('HP1', '电', '升级 1 电镀弹：三圈铜线圈套上炮管'),
        ('HP2', '实弹', '花开齐射：六角巢、六管成一圈（和火箭张开的 60° 一一对应）'),
        ('HP2', '标记', '升级 3 点名导弹：两侧颊板弹起，露出锁定灯'),
        ('HP3', '回补', '汲光镜头；升级 1 分盾：前臂绿环；升级 2 汲场：镜头外圈碟'),
        ('HP6', '电', '电烟罐架；升级 2 旋雷：罐架上竖起放电杆'),
        ('HP4', '机体色', '右肩三道升级刻度（第几次升级亮几道），远处可读'),
    ]),
    'wayfarer': ('远行 WAYFARER（规则：BT 远征装）', [
        ('HP1', '实弹', '阶梯机炮（和进阶共用）+ 三片散热鳍（爆发核心时发红热）'),
        ('HP2', '实弹', '点名导弹舱：猎标的 2×3 舱体 + 顶沿六颗锁定灯'),
        ('HP3', '屏障', '折屏投射器（和猎标共用）'),
        ('HP6', '电', '电烟罐架（和进阶共用，不带放电杆）'),
        ('HP4', '通用座', '核心不换挂件：爆发核心走主炮'),
    ]),
}

def mount_sheet(kit):
    title, items = KITS[kit]
    fig = plt.figure(figsize=(17, 8.2), dpi=110)
    fig.suptitle(f'{title} —— M-1 挂点图（体块示意，不是模型；模型没改）', fontsize=15, x=0.02, ha='left')
    used = {i[0] for i in items}
    for k, view in enumerate(('front', 'side', 'back')):
        ax = fig.add_axes([0.005 + k * 0.205, 0.04, 0.2, 0.86])
        img = plt.imread(os.path.join(R, f'{kit}_{view}.png'))
        ax.imshow(img[60:880, 90:610]); ax.set_axis_off()
        ax.set_title({'front': '正面', 'side': '左侧（左边是前）', 'back': '背面'}[view], fontsize=11)
        for hid, (nm, p, views) in HP.items():
            if view not in views or (kit != 'base' and hid not in used):
                continue
            u, v = proj(view, p)
            u -= 90; v -= 60
            ax.add_patch(Circle((u, v), 15, fc='white', ec='black', lw=1.4, zorder=5))
            ax.text(u, v, hid[2], ha='center', va='center', fontsize=10, weight='bold', zorder=6)
    ax = fig.add_axes([0.63, 0.04, 0.36, 0.86]); ax.set_axis_off()
    y = 0.98
    ax.text(0, y, '挂点 / 挂件', fontsize=13, weight='bold', va='top'); y -= 0.06
    for hid, fam, txt in items:
        ax.add_patch(Rectangle((0, y - 0.035), 0.035, 0.03, fc=FAM[fam], ec='black', lw=0.6, transform=ax.transAxes))
        ax.text(0.05, y, f'{hid}  {HP[hid][0]}', fontsize=10.5, weight='bold', va='top')
        ax.text(0.05, y - 0.035, txt, fontsize=9.5, va='top', wrap=True)
        y -= 0.095
    y -= 0.01
    ax.text(0, y, '颜色 = 效果家族（见 MEDIUM.md 第 1 节）', fontsize=10, weight='bold', va='top'); y -= 0.045
    for i, (k2, c) in enumerate(FAM.items()):
        xx = (i % 4) * 0.25; yy = y - (i // 4) * 0.045
        ax.add_patch(Rectangle((xx, yy - 0.03), 0.03, 0.025, fc=c, ec='black', lw=0.5, transform=ax.transAxes))
        ax.text(xx + 0.04, yy, k2, fontsize=9.5, va='top')
    fig.savefig(os.path.join(OUT, f'{kit}_mounts.png')); plt.close(fig)

# ---------------- effect schematics ----------------
def deg_line(ax, ang, L, **kw):
    a = math.radians(ang); ax.plot([0, L * math.cos(a)], [0, L * math.sin(a)], **kw)

def fx_spectra():
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=110)
    fig.suptitle('分光 SPECTRA —— 弹道和效果怎么读（示意，角度放大画）', fontsize=15)
    ax = axs[0, 0]; ax.set_title('三棱步枪：开镜一枪分成水平扇形（俯视）\n3 发 ±1.26°；五棱镜 5 发 ±1.26° / ±2.52°（ION §1、§7）', fontsize=10)
    for a, c, lw in ((0, FAM['能量'], 3), (1.26 * 6, FAM['能量'], 2), (-1.26 * 6, FAM['能量'], 2),
                     (2.52 * 6, '#D9B3FF', 1.5), (-2.52 * 6, '#D9B3FF', 1.5)):
        deg_line(ax, a, 10, color=c, lw=lw)
    for d in (3, 6, 9):
        for a in (0, 7.56, -7.56):
            r = math.radians(a); ax.plot(d * math.cos(r), d * math.sin(r), marker=(3, 0, -90 + a), ms=10, color=FAM['能量'])
    ax.text(0.3, -2.4, '每发是一枚扁平的三角光片，尖朝前；\n中间一发亮、两侧淡；五棱镜多出的两发最淡（伤害 × 0.55）', fontsize=9)
    ax.set_xlim(-0.5, 11); ax.set_ylim(-3, 3); ax.set_aspect('equal'); ax.axis('off')
    ax.text(-0.4, 0.3, '枪口', fontsize=9)
    ax = axs[0, 1]; ax.set_title('捕光壳：举左臂，前方张开一片刻面壳（侧视）\n接弹锥 ±60°；收集点在眼前 110、左 28、下 22（ION §3）', fontsize=10)
    th = np.linspace(-60, 60, 7)
    pts = [(3.8 * math.cos(math.radians(t)), 3.8 * math.sin(math.radians(t))) for t in th]
    for i in range(len(pts) - 1):
        ax.add_patch(Polygon([(0.6, 0), pts[i], pts[i + 1]], fc=FAM['屏障'], ec=FAM['能量'], alpha=0.5))
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=FAM['能量'], lw=2)
    ax.plot(2.8, -0.56, 'o', color='black'); ax.text(2.9, -0.9, '收集点：接住的弹\n变成嵌在刻面里的亮点', fontsize=8.5)
    for yy in (2.0, 0.6, -1.4):
        ax.annotate('', xy=(3.6, yy), xytext=(7, yy), arrowprops=dict(arrowstyle='->', color='gray'))
    ax.text(4.3, 2.6, '来弹', color='gray')
    ax.text(-0.2, -3.6, '刻面数随消耗变：满能量 6 面亮，用掉越多，熄灭的刻面越多、闪烁越快（不用变色表示）', fontsize=8.5)
    ax.set_xlim(-0.5, 7.5); ax.set_ylim(-4, 4); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 0]; ax.set_title('棱栅：一次抛 3 根桩（俯视），只连 0–1、1–2 两道\n落地 1 s 升起；任意碰线 → 三根都炸，半径 400 u（ION §4）', fontsize=10)
    P = [(-4.0, 6.0), (0, 7.2), (4.0, 6.0)]
    for i, p in enumerate(P):
        ax.add_patch(Circle(p, 4.0 * 0.6, fc=FAM['电'], alpha=0.08, ec=FAM['电'], ls='--'))
        ax.plot(*p, marker='^', ms=14, color=FAM['能量']); ax.text(p[0] + 0.3, p[1] - 0.8, f'桩 {i}', fontsize=9)
    for a, b in ((0, 1), (1, 2)):
        ax.plot([P[a][0], P[b][0]], [P[a][1], P[b][1]], color=FAM['能量'], lw=2.5, ls=(0, (6, 3)))
    ax.plot(0, 0, 's', color='gray', ms=12); ax.text(0.4, -0.4, 'M-1', fontsize=9)
    for p in P:
        ax.annotate('', xy=p, xytext=(0, 0.3), arrowprops=dict(arrowstyle='->', color='lightgray'))
    ax.text(-6.5, -2.0, '线是一串往前爬的短划（看得出是活的、朝哪边连）；桩 0 和桩 2 之间故意不连，留一个看得见的缺口', fontsize=8.5)
    ax.set_xlim(-7, 7); ax.set_ylim(-2.5, 10); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 1]; ax.set_title('全谱光束：时间线和光束样子（ION §5）', fontsize=10)
    ax.add_patch(Rectangle((0, 2.2), 1.1, 0.5, fc='#E9D6FF')); ax.text(0.05, 2.85, '蓄力 1.1 s：棱叶翻起，芯从橙到白', fontsize=8.5)
    ax.add_patch(Rectangle((1.1, 2.2), 3.5, 0.5, fc=FAM['能量'])); ax.text(1.2, 2.35, '放电 3.5 s，35 跳', color='white', fontsize=9)
    ax.add_patch(Rectangle((4.6, 2.2), 2.0, 0.5, fc='#EEEEEE')); ax.text(4.65, 2.85, '减速淡出 2 s', fontsize=8.5)
    for t in np.arange(1.1, 4.61, 0.1):
        ax.plot([t, t], [2.2, 2.05], color='black', lw=0.6)
    ax.plot([0, 6.6], [1.2, 1.2], color='white', lw=14, solid_capstyle='butt')
    ax.plot([0, 6.6], [1.2, 1.2], color=FAM['能量'], lw=16, alpha=0.35)
    ax.plot([0, 6.6], [1.2, 1.2], color='white', lw=5)
    for k, c in enumerate(('#FF5A5A', '#FFD23F', '#5CFF9D', '#4FA8FF')):
        ax.plot([0, 6.6], [1.2 + 0.22 - k * 0.03, 1.2 + 0.22 - k * 0.03], color=c, lw=0.8)
    for x in np.arange(0.3, 6.6, 0.6):
        ax.add_patch(Polygon([(x - 0.08, 0.85), (x + 0.08, 0.85), (x + 0.14, 1.2), (x + 0.08, 1.55), (x - 0.08, 1.55), (x - 0.14, 1.2)],
                             fill=False, ec=FAM['能量'], lw=1))
    ax.text(0, 0.35, '白芯 + 边上一圈细彩虹色散（"棱镜"）；每一跳从胸口推出一个六边形光环往前走，\n数得出一秒 10 跳；命中点是白热亮斑 + 彩色火星', fontsize=8.5)
    ax.set_xlim(-0.2, 7); ax.set_ylim(0, 3.2); ax.axis('off')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'spectra_fx.png')); plt.close(fig)

def fx_tally():
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=110)
    fig.suptitle('猎标 TALLY —— 弹道和效果怎么读（示意）', fontsize=15)
    ax = axs[0, 0]; ax.set_title('标记 → 锁定（TONE §1、§2）\n每次伤害 +1 层，上限 3，单层 15 s', fontsize=10)
    for k in range(4):
        x = k * 2.6
        ax.add_patch(Rectangle((x, 0), 1.6, 2.2, fc='#DDDDDD', ec='gray'))
        for j in range(3):
            filled = j < k
            ax.add_patch(Polygon([(x + 0.25 + j * 0.42, 2.5), (x + 0.55 + j * 0.42, 2.5), (x + 0.4 + j * 0.42, 2.85)],
                                 fc=FAM['标记'] if filled else 'white', ec='black'))
        if k == 3:
            for (a, b) in ((-0.25, -0.25), (1.85, -0.25), (-0.25, 2.45), (1.85, 2.45)):
                ax.add_patch(Rectangle((x + a, b), 0.0, 0.0))
            ax.add_patch(Rectangle((x - 0.25, -0.25), 2.1, 2.7, fill=False, ec=FAM['标记'], lw=3, ls='--'))
        ax.text(x + 0.2, -0.7, f'{k} 层' + ('：锁定' if k == 3 else ''), fontsize=9)
    ax.text(0, -1.6, '目标头顶是三格刻痕（不是圆点）；满 3 格整组变成"框住"的四角括号；\n每层自己倒计时，最后 3 s 刻痕闪', fontsize=8.5)
    ax.set_xlim(-0.6, 10.6); ax.set_ylim(-2.2, 3.4); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[0, 1]; ax.set_title('清账导弹：每个锁定目标 6 枚，间隔 1/14 s（俯视，TONE §2）\n先从肩舱往左上抛出、短暂直飞，再弯向目标', fontsize=10)
    rng = np.random.default_rng(3)
    for i in range(6):
        t = np.linspace(0, 1, 60)
        side = 1.0 + 0.15 * i
        x = 12 * t; y = side * 3 * np.sin(np.pi * t) * (1 - t) + 2 * t + rng.normal(0, 0.05, 60).cumsum() * 0.2
        ax.plot(x, y, color=FAM['实弹'], lw=1.2)
        ax.plot(x[-1], y[-1], '*', color='red', ms=6)
    ax.plot(0, 0, 's', color='gray', ms=10); ax.text(0.2, -0.9, 'M-1（肩舱在左）', fontsize=9)
    ax.text(0.5, -2.6, '导弹：深色短弹体、白热尾焰、细灰烟；6 条烟在空中散成一束"梳子"，\n一眼看出这次打了几个目标（几束）', fontsize=8.5)
    ax.set_xlim(-1, 13); ax.set_ylim(-3.2, 5); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 0]; ax.set_title('折屏：脚前立起 120° 弧墙，半径 180 u、高 360 u（俯视，TONE §3）\n只挡正面来弹；不随时间掉血，只随受伤变', fontsize=10)
    ax.add_patch(Wedge((0, 0), 4.6, 30, 150, width=0.25, fc=FAM['屏障'], ec='black'))
    for k in range(9):
        a = math.radians(30 + 120 * (k + 0.5) / 9)
        on = k not in (2, 6)
        ax.plot([4.35 * math.cos(a), 4.6 * math.cos(a)], [4.35 * math.sin(a), 4.6 * math.sin(a)],
                color='#3355AA' if on else '#BBBBBB', lw=6)
    ax.plot(0, 0, 's', color='gray', ms=10)
    ax.annotate('', xy=(0, 4.1), xytext=(0, 7), arrowprops=dict(arrowstyle='->', color='red'))
    ax.text(0.2, 6.3, '来弹被挡', color='red', fontsize=9)
    ax.text(-5, -1.6, '墙是一排竖直的光条（百叶），条与条之间有缝能看穿；\n掉血 = 光条一根根熄灭（2000 血 / 9 条 ≈ 每 222 血一条）；\n友方看边缘是队伍色细线', fontsize=8.5)
    ax.set_xlim(-5.5, 5.5); ax.set_ylim(-2.4, 7.5); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 1]; ax.set_title('探钟（声呐）+ 余响（Pulse Echo）（TONE §4、§7）\n落点立刻脉冲 1250 u，敌人描边 5 s、+1 层；2.0 s 后再脉冲一次', fontsize=10)
    ax.add_patch(Circle((0, 0), 5, fill=False, ec=FAM['标记'], lw=2))
    ax.add_patch(Circle((0, 0), 5, fill=False, ec=FAM['标记'], lw=1, ls='--'))
    ax.add_patch(Circle((0, 0), 4.6, fill=False, ec=FAM['标记'], lw=1, ls='--'))
    ax.plot(0, 0, marker='v', ms=14, color=FAM['标记'])
    ax.text(-4.8, 5.5, '第一次：一道贴地的实线环，向外扫到 1250 u', fontsize=8.5)
    ax.text(-4.8, -6.1, '余响：钟的下摆裂开，扫出"双线环"（两条虚线）——一看就知道是第二次', fontsize=8.5)
    ax.set_xlim(-6, 6); ax.set_ylim(-6.5, 6.5); ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'tally_fx.png')); plt.close(fig)

def fx_ascent():
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=110)
    fig.suptitle('进阶 ASCENT —— 弹道和效果怎么读（示意）', fontsize=15)
    ax = axs[0, 0]; ax.set_title('花开齐射：从玩家身后看准星（MONARCH §2.1）\n第 k 枚在 60°·k 方向先张开 5°，再往对侧收 10°，最后对准准星直飞', fontsize=10)
    for k in range(6):
        a = math.radians(60 * k); ca, sa = math.cos(a), math.sin(a); px, py = -sa * 0.35, ca * 0.35
        ax.annotate('', xy=(5 * ca, 5 * sa), xytext=(0, 0), arrowprops=dict(arrowstyle='->', color=FAM['实弹'], lw=2))
        ax.annotate('', xy=(-2.5 * ca + px, -2.5 * sa + py), xytext=(5 * ca + px, 5 * sa + py),
                    arrowprops=dict(arrowstyle='->', color=FAM['实弹'], lw=1, ls='--'))
        ax.annotate('', xy=(0.15 * ca, 0.15 * sa), xytext=(-2.5 * ca + px, -2.5 * sa + py),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=1, ls=':'))
        ax.text(5.6 * ca, 5.6 * sa, str(k), ha='center', va='center', fontsize=10, weight='bold')
    ax.plot(0, 0, '+', color='black', ms=20, mew=2)
    ax.text(-6, -6.4, '粗箭头 = 张开（0.2 s），虚线 = 交叉收拢到对侧（0.1 s），点线 = 转直扎向准星。六管巢本身就是一圈六个口，\n所以火箭像花一样从巢口的位置开出去——弹道形状和发射舱形状一致', fontsize=8.5)
    ax.set_xlim(-6.5, 6.5); ax.set_ylim(-7, 6); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[0, 1]; ax.set_title('汲光（能量虹吸）+ 汲场 + 分盾（MONARCH §3、§5.3）\n细光束 0.75° 打第一个目标；回补沿光束倒流回来', fontsize=10)
    ax.plot([0, 9], [0, 0], color=FAM['回补'], lw=2)
    for x in (2.5, 5, 7.5):
        ax.annotate('', xy=(x - 0.8, 0.35), xytext=(x, 0.35), arrowprops=dict(arrowstyle='->', color=FAM['回补']))
    ax.plot(9, 0, 'o', color='black', ms=10)
    ax.add_patch(Circle((9, 0), 3.5, fill=False, ec=FAM['回补'], ls='--'))
    ax.text(7.2, 3.7, '汲场：350 u 圈内每个目标都被汲', fontsize=8.5)
    ax.plot(0, 0, 's', color='gray', ms=10)
    ax.plot([0, 4], [-1.5, -3.2], color=FAM['回补'], lw=2)
    ax.add_patch(Circle((4.4, -3.4), 0.5, fc=FAM['回补'], alpha=0.3, ec=FAM['回补']))
    ax.text(5.0, -3.6, '分盾：打友方 → 友方身上一层绿色护套 +750', fontsize=8.5)
    ax.text(0, -5.2, '光束本体是细绿线；命中后一颗亮珠沿光束倒着跑回自己的护腕（0.3 s），\n珠子越大回得越多（重甲 750 / 其他 250）；对方身上留一层往下掉的绿色碎屑 = 盾上限被扣', fontsize=8.5)
    ax.set_xlim(-1, 13); ax.set_ylim(-6, 4.5); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 0]; ax.set_title('电烟 + 旋雷（MONARCH §5.3 Maelstrom 细节）\n内 320 / 外 375 u，1.0 s 后开始，每 0.1 s 一跳，5 s', fontsize=10)
    ax.add_patch(Circle((0, 0), 3.75, fc='#555B66', alpha=0.35))
    ax.add_patch(Circle((0, 0), 3.2, fill=False, ec='white', ls=':'))
    rng = np.random.default_rng(1)
    for i in range(14):
        a0 = rng.uniform(0, 2 * np.pi); r0 = rng.uniform(0.5, 3.4)
        xs = [r0 * math.cos(a0)]; ys = [r0 * math.sin(a0)]
        for j in range(4):
            xs.append(xs[-1] + rng.normal(0, 0.35)); ys.append(ys[-1] + rng.normal(0, 0.35))
        ax.plot(xs, ys, color=FAM['电'], lw=1.2)
    t = np.linspace(0, 2 * np.pi * 0.8, 100)
    ax.plot(2.2 * np.cos(t), 2.2 * np.sin(t), color=FAM['电'], lw=2.5, alpha=0.6)
    ax.plot(0, 0, 's', color='gray', ms=10)
    ax.text(-4, -4.8, '石墨色烟 + 每 0.1 s 闪一次的青白折线电弧（数得出节奏）。\n旋雷：电弧加粗、密度 ×2，烟里多一条慢慢转的电弧环（伤害 ×2 / ×3）', fontsize=8.5)
    ax.set_xlim(-4.5, 4.5); ax.set_ylim(-5.5, 4.5); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1, 1]; ax.set_title('三阶核心：每用一次，身上永久多一样东西（MONARCH §5）', fontsize=10)
    steps = [('第 1 次', '电镀弹（炮管铜线圈）\n或 分盾（前臂绿环）'), ('第 2 次', '旋雷（背包放电杆）\n或 汲场（镜头外圈碟）'),
             ('第 3 次', '点名导弹（肩舱颊板弹起）'), ('第 4 次起', '只回满护盾')]
    for i, (a, b) in enumerate(steps):
        x = i * 3.2
        ax.add_patch(Rectangle((x, 0), 2.8, 2.2, fc='#F4F4F4', ec='gray'))
        for j in range(3):
            ax.add_patch(Polygon([(x + 0.4, 2.6 + j * 0.3), (x + 1.4, 2.85 + j * 0.3), (x + 2.4, 2.6 + j * 0.3)],
                                 closed=False, fill=False, ec=FAM['机体色'] if j < min(i + 1, 3) else '#CCCCCC', lw=3))
        ax.text(x + 0.1, 1.9, a, fontsize=9, weight='bold', va='top'); ax.text(x + 0.1, 1.4, b, fontsize=8, va='top')
    ax.text(0, -1.0, '右肩三道橙色 V 形刻度 = 已升级次数，敌人远远就能数。按核心那一刻：\n全身一层绿色护盾回满闪光 0.4 s + 新挂件"咔"地弹出（0.3 s 机械动作）', fontsize=8.5)
    ax.set_xlim(-0.3, 12.8); ax.set_ylim(-1.8, 3.8); ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'ascent_fx.png')); plt.close(fig)

def fx_wayfarer():
    fig, axs = plt.subplots(1, 3, figsize=(16, 6), dpi=110)
    fig.suptitle('远行 WAYFARER —— 弹道和效果怎么读（示意）', fontsize=15)
    ax = axs[0]; ax.set_title('点名导弹：按住扫描，每 0.3 s 一把锁\n同一目标最多 6 把（MONARCH §2.2）', fontsize=10)
    for i in range(6):
        ax.add_patch(Rectangle((i * 0.8, 3), 0.6, 0.4, fc=FAM['标记'] if i < 4 else '#DDDDDD', ec='black'))
    ax.text(0, 3.6, '肩舱顶沿 6 颗灯：锁一把亮一颗（第三人称也看得见）', fontsize=8.5)
    ax.add_patch(Rectangle((1.2, 0), 1.6, 1.6, fill=False, ec=FAM['标记'], lw=2))
    for j in range(4):
        ax.plot([1.2 + j * 0.1, 1.2 + j * 0.1], [1.7, 1.9], color=FAM['标记'], lw=3)
    ax.text(0, -0.8, '准星上的目标：括号外侧一道道短竖线 = 锁数；\n松手每把锁一枚追踪导弹，12 /s 连发；没锁走花开齐射式无制导弹道', fontsize=8.5)
    ax.set_xlim(-0.3, 5.3); ax.set_ylim(-1.5, 4.2); ax.set_aspect('equal'); ax.axis('off')
    ax = axs[1]; ax.set_title('爆发核心：主炮 5.5 s、20 发/s、每发 150\n（WT/mp_titancore_amp_core.txt:35、59、133–136）', fontsize=10)
    t = np.linspace(0, 5.5, 200)
    ax.fill_between(t, 0, 1, color=FAM['实弹'], alpha=0.25)
    ax.plot(t, 0.3 + 0.7 * t / 5.5, color='#C0392B', lw=2); ax.text(3.2, 1.05, '散热鳍从暗到红热', fontsize=8.5, color='#C0392B')
    for x in np.arange(0, 5.5, 0.05 * 4):
        ax.plot([x, x], [0, 0.18], color='black', lw=0.6)
    ax.text(0, -0.35, '每发都带曳光（平时每 3 发一条）→ 枪口前一条连续的暖白"光绳"；\n弹壳成串从炮座下抛出；背包热浪扭曲', fontsize=8.5)
    ax.set_xlim(-0.2, 6); ax.set_ylim(-0.6, 1.4); ax.axis('off')
    ax = axs[2]; ax.set_title('共用件：折屏（同猎标）、电烟（同进阶，不带旋雷）\n外观区别只在涂装：远行舱体带一道机体色斜条', fontsize=10)
    ax.add_patch(Rectangle((0, 0), 4, 2, fc=FAM['实弹'], ec='black'))
    ax.add_patch(Polygon([(0.6, 0), (1.1, 0), (2.1, 2), (1.6, 2)], fc=FAM['机体色']))
    ax.text(0, -0.6, '远行的舱体 / 炮管和别的套件同形，只多一道斜条（远行的识别条）', fontsize=8.5)
    ax.set_xlim(-0.3, 5); ax.set_ylim(-1, 2.5); ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'wayfarer_fx.png')); plt.close(fig)

for k in KITS:
    mount_sheet(k)
fx_spectra(); fx_tally(); fx_ascent(); fx_wayfarer()
print('ok')
