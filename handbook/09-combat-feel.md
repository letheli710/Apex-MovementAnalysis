# 09 战斗手感：后坐、开镜、枪的重量、扩散、准星和命中反馈、换弹和切枪

hb-ch09 写（2026-11-14），分支 `handbook/ch09`，还没合并。本章的附件在 [09-combat-feel/](09-combat-feel/)（每把枪的完整数值表，由 `make_tables.py` 从研究分支生成）。

## 白话说明

这一章讲**拿枪打起来是什么感觉**：开一枪画面往上抬多少、多久回来、连射时往哪边漂；按右键开镜时画面怎么拉近、枪怎么移到眼前；为什么手枪掏得快、狙击枪掏得慢；子弹在准星周围散多大；打中了屏幕上出现什么；换弹到哪一刻就能开枪。

读完能做出这些东西，而且每一样都能和 R5 对数：

1. **后坐**：一把枪每一发往画面上"踢"多少，由一张固定的图案表、一点随机、两个缩放系数决定；踢进去以后由这把枪自己的弹簧拉回原位（§2）。
2. **开镜**：一个从 0 走到 1 的线性进度 `zf`，画面 FOV、枪模 FOV、枪的位置、鼠标灵敏度都从它读，各用各的曲线（§3）。
3. **枪的重量**：开镜时间、掏枪收枪时间、开镜时走路多慢、冲刺到开火要多久，这几个数一起变，玩家不看数字也知道枪轻还是重（§4）。
4. **扩散**：腰射时子弹在一个圆锥里随机，圆锥大小 = 姿态的基础值 + 连射累积；霰弹不随机，是固定图案（HSD 在上面加了每颗弹丸的小随机区域）（§5）。
5. **准星和命中反馈**：准星画在哪、张多大；命中 X、霰弹的命中弹丸点；以及 R5 **没有**的反馈（开枪不震屏、中弹不抖）（§6）。
6. **换弹和切枪的时刻表**：换弹有三个时刻（加弹、解锁、动画结束），解锁比动画结束早；切枪先收再掏，新枪掏到一半就能开火（§7）。

两条总的设计理念先记住（出自 DESIGN-PHILOSOPHY，下面简称 DP）：

- **瞄准是真值**（P1、T3）。后坐只改"画面"和"子弹"，不改"瞄准"。准星指向哪里由鼠标决定；画面偏离准星时，规则写清楚子弹去哪。
- **后坐可以学，枪有分量**（P5、P7）。图案是固定表 + 小随机，熟练可以练出来；打完一定回到原位。枪的轻重不是一个参数，而是"所有操作这把枪的时间"一起变。

**和别的章的分界**：后坐对**画面**的接法（第二组弹簧、(1 − fraction)、移动 punch 也进子弹）在 [07 §2.10、§4.3](07-camera.md)，本章写后坐图案、弹簧表、每发缩放和子弹那一侧，两章说法一致；枪模和手臂的持枪姿势、走路摆动、换弹时枪怎么转（姿态曲线）在 08 章，本章只写换弹的**时刻**；技能、道具在 10 章；音效、枪口焰亮度、命中 X 的样子都还没研究，列在 [§9](#9-待研究)。

### 本章出处缩写

| 缩写 | 路径（研究仓库根目录） | 在哪 |
|---|---|---|
| DP | `research/DESIGN-PHILOSOPHY.md`（P1、P5–P7、T1–T8、§6.4 开镜、§7 枪械规范、§10） | main 是 11-02 版；**本章用 #122 版**（PR #122，还没合并；分支 `r5gap/gun`） |
| RV | `research/combat/RECOIL-VIEW.md`（§1–§9 后坐对画面；§10 每发缩放；§11 枪模跳动） | PR #93，还没合并（分支 `combat/recoil-view-measure`）；**§10、§11 只在 PR #95 的分支上**（`combat/gun-measure`） |
| ADS | `research/combat/ADS-CURVES.md`；数据 `research/combat/recoil-view/ADS-CURVES.tsv` | PR #93，还没合并 |
| FIT | `research/combat/recoil-view/FIT-TABLE.tsv`（每把枪的弹簧、回落拟合） | PR #93，还没合并 |
| GM | `research/combat/gun-measure/`：`INDEX.md`、`A-ATTACHMENTS.md`、`B-STATES.md`、`C-MOTIONS.md`、`D-EXTENSIONS.md`、`GUN-VARS.tsv`、`C-RAISE2.tsv`、`report/03-ads-optics.md`、`report/06-hipfire-spread.md` | PR #95，还没合并（分支 `combat/gun-measure`）。**`INDEX.md` 第 9 条建议用作废的 D-VIEWMODEL**，以 IS 为准 |
| RM | `research/combat/gun-measure/reload-motion/RELOAD-MOTION.md`、`RM-SUMMARY.tsv`；`SCREEN-TRACER.md` | PR #95，还没合并 |
| IS | `research/combat/gun-measure/iron-sights/IRON-SIGHTS.md`（"枪模 FOV"、"装瞄具时的枪"两节）、`data/IS-OPTICS.tsv`、`data/IS-GUNS.tsv` | PR #99，还没合并（分支 `combat/iron-sights`） |
| SR | `research/combat/gun-measure/shotgun-reticle/SHOTGUN-RETICLE.md` | PR #103，还没合并（分支 `combat/shotgun-reticle`） |
| EM | `research/combat/gun-measure/E-MOUSE.md`（鼠标下压抵消 punch、开镜灵敏度） | PR #122，还没合并（分支 `r5gap/gun`） |
| FG | `research/combat/gun-measure/F-GAPS.md`（子弹含 punch1 和开镜 drift、第二组弹簧、开枪不震屏、拉栓镜头、射速蓄力、钩爪 / 翻越中开枪） | PR #122，还没合并 |
| B5 | `research/combat/gun-measure/B5-ADS-RECOVERY.md`（R-301 开镜回落差 0.04 s） | PR #123，还没合并（分支 `r5gap/anim`） |
| UI | `research/ui/UI-INVENTORY.md`（W-01 准星、H-01 命中 X、H-04 弹丸点、H-05 伤害数字） | PR #102，还没合并（分支 `research/ui-inventory`） |
| DEC | `DECISIONS.md`：D-86 – D-89、D-94、D-95、D-113 – D-118 在 #91；D-120、D-121 在 #99；D-122、D-123 在 #100；D-124 – D-126 在 #101；D-128、D-129、D-137 在 #104 | 都还没合并。**本章读的是叠在最上面的 #104（分支 `combat/shotgun-reticle-records`），它含 #91 – #101 的全部行**；D-120、D-121 读 #99 |
| N3 | `tf2/ref-native-tail/REF-NATIVE-1112.md` §3（TF2 散布分布）、§5（punch 弹簧两条积分路径） | PR #115，还没合并（分支 `ref/native-tail`） |
| 07 | 本手册 [07-camera.md](07-camera.md) | `handbook/ch07`，还没合并 |

Unity 路径：战斗代码都在 `HSD-Unity: Assets/HSD/Game/Runtime/Combat/Arsenal/` 下，下文只写文件名。**全部在 HSD-Unity 没合并的 PR 上**，链是 U#60 → U#61 → U#63 → U#65 → U#67 → U#68 → U#69 → U#71（00-INVENTORY §0.2）。每个文件写它第一次出现的 PR；最新版本在链的最上面 U#71（分支 `combat/wp5-shotgun-reticle`），本章读的就是那里。测试在 `HSD-Unity: Assets/HSD/Game/Tests/Editor/`。所有枪的字段、后坐图案表、弹簧表都生成在 `WeaponData.gen.cs`（U#60 起），由 `WeaponDef.cs` 的 `WeaponTable` 解析——**删掉 R5 以后，枪的原始数据就在这里**。

---

## 0. 约定

### 0.1 单位和符号

- **本章几乎全是角度、时间、比例**，按 [01 §2.2](01-units-body.md) 都不换算，三列表里 `[m]` 和身高比例写"—"。有长度的只有枪的位置（u）、弹速、距离和移动速度，照常三列。
- 角度：度（°）。俯仰 + = 向下看（Source 约定，和 [07 §0.1](07-camera.md) 一样）。**后坐图案表里俯仰负数 = 向上，偏航负数 = 向右**（RV §1.4 实测；IP2 写反过，已更正）。
- 弹簧：x'' = −k·x − d·v，k 单位 1/s²，d 单位 1/s（作用在角度上，不换算）。
- FOV：R5 的度数是 **4:3 画面的水平 FOV**；Unity `Camera.fieldOfView` 是竖直 FOV。换算见 [07 §3.10](07-camera.md)。R5 本地设置 `cl_fovScale` 1.27217、基础 FOV 89 是**玩家设置**，要学的是**比例**，不是度数（DP §10.3）。
- 字段名：照抄 R5 武器文件的键名（`viewkick_pitch_base`、`zoom_time_in`……）。Unity 的 `WeaponStats.D("…")` 读的就是同名字段，所以手册、研究、代码三处同名。

### 0.2 开镜进度 `zf`

`zf` ∈ [0, 1]，0 = 腰射，1 = 开镜到位。线性走（§3.1）。本章凡是"按开镜插值"都是 `腰射值 + (开镜值 − 腰射值) × zf`，除非写了别的曲线。

### 0.3 三种角

照 [07 §0.3](07-camera.md)：

```
瞄准 aim = 只来自鼠标（鼠标先抵消反向的武器 punch，§2.6）
画面     = aim + punch1 + (1 − f)·punch2 + drift …（07 §4.1）
子弹     = aim + punch1 + punch2（这一发 kick 之前）+ 开镜 drift + 扩散
```

punch1 = 第一组弹簧（移动事件，07 §1.1），punch2 = 第二组弹簧（武器后坐 + 移动事件的 0.2 倍，本章 §2.1），f = `weaponFraction`（§2.5）。

### 0.4 依据标签

沿用 DP §2.1：[实测] [反编译] [数据] [算] [推断] [设计]，TF2 来源写 [TF2 实测] [TF2 数据]。"R5"都指本地混合构建（S21 客户端 + S3 dedi + SDK）。**客户端的东西**（镜头、FOV、灵敏度、动画、后坐 punch）推断和正版相同；**服务端的东西**（子弹弹道、伤害、hop-up 脚本）只代表 S3 dedi，引用时写 [hyb]（DP §10.3）。

### 0.5 代表枪

正文的数值只写这几把，其余的在附件 TSV：

| 枪 | 类 | 为什么选它 |
|---|---|---|
| R-301 | 步枪，连发 | 测得最全（后坐、开镜曲线、换弹、鼠标、表尾） |
| Spitfire | 机枪，连发 | 开镜和腰射都 k热 = 0，"一直爬"的代表；表尾有 loop |
| Wingman | 手枪，单发 | 没有图案；开镜 fraction 0.3，子弹和准星不重合 |
| P2020 | 手枪，单发 | 最轻；没有热弹簧 |
| Kraber | 狙击 | 最重；开镜 fraction 0.75；全屏瞄准镜 |
| EVA-8 / Peacekeeper / Mastiff / Mozambique | 霰弹 | 固定图案、弹丸点 |

---

## 1. 一发子弹的完整流程

### 1.1 开一枪的次序

#### 原理

一发子弹牵动五样东西：子弹方向、后坐 punch、图案计数、热度、扩散累积。它们的**先后顺序**决定了"第一发打在哪"和"连射第几发用表的第几行"。R5 的顺序是**先取子弹方向，再加这一发的后坐**，所以第一发永远打在准星上，第二发才开始受后坐影响。这让"点射第一发准"成为可以依赖的规则（P1、P7）。

#### 规则和公式

每发（按下扳机后，射速间隔到了）：

1. **子弹方向** = aim + punch1 + punch2 + 开镜 drift + 扩散偏移（§0.3、§5）。punch 取**这一发 kick 之前**的值。
2. **图案计数**：读当前 value（已经按 §2.4 衰减过），取行号。
3. **kick** = 这一行 × base + 随机（§2.2），乘每发缩放（§2.3），写进第二组弹簧：角度 += hard × kick，角速度 += soft × 20 × kick。横滚另算（§2.5）。
4. **计数上升**：图案 value += `viewkick_pattern_valuePerShot`；俯仰 / 偏航两个缩放计数各 += `viewkick_scale_valuePerShot`（封顶 `LerpEnd`）。**kick 读的是加之前的值。**
5. **热度** += `viewkick_spring_heatpershot`（上限 1）；**扩散累积** += `spread_kick_on_fire_*`（不超过上限）。
6. 枪模弹簧推一下（§2.8）。

开火节奏本身（射速、点射、蓄力、拉栓）由字段决定，见下表；每把枪的值在 [gun-weight.tsv](09-combat-feel/gun-weight.tsv)（`fire_rate`、`rechamber`）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 第一发的后坐偏移 | — | 0 ° | — | 4 次全是 0（假人 150 u，眼高差 0.1 u） | [实测] RV §1.3 |
| 全自动射速 R-301 `fire_rate` | — | 13.5 /s（实测 13.1） | — | 全枪 ±3 % | [数据] [实测] GM D §1 |
| 点射周期 | — | (n − 1) / 射速 + `burst_fire_delay` | — | Hemlok 0.38 s、Prowler 0.42 s | [数据] [实测] DP §7.5 |
| 拉栓 / 泵动间隔（Kraber / Sentinel / Peacekeeper，连点） | — | 2.235 / 1.597 / 1.21 s | — | 字段 `rechamber_time` 1.6 / 1.6 / 1.1 s，和间隔的关系没查清 | [实测] FG §6 |
| 蓄力进度 | — | 线性：Charge Rifle 0.84 s 满、Havoc 0.39 s、L-STAR 2.2 s | — | 25 / 50 / 75 / 100 % 等间隔 | [实测] FG §6 |
| 射速爬升（Devotion） | — | 0.203 → 0.062 s，约 15 发 | — | Rampage、Havoc 按住不爬 | [实测] GM D §1 |
| 名义 DPS（全自动） | — | 170–220 | — | 配平靠弹匣和换弹 | [数据] DP §7.5 |

#### 实现模板

```
// 单位：°、s
onFire(gun, now):
    dir   = aim + punch1 + punch2 + adsDrift            // 先取方向（kick 之前）
    dir   = spreadCone(dir, spread.angle)               // §5
    spawnRound(eye, dir)                                // 子弹从眼睛出发（D-87）
    kick  = viewKick.kick(gun, now, stance)             // §2.2–2.4，写 punch2
    spread.onFired(gun, pose, now)                      // §5.1
    gunJolt.push(...)                                   // §2.8
```

Unity 参考实现：`ArsenalWeapon.cs`（`ArsenalWeapon`，U#60；开火入口在 `CombatSim.Arsenal.cs`），射速 / 点射 / 蓄力 / 热量在 `FiringCycle.cs`（`FiringCycle`、`FireRateRamp`、`WeaponCharge`、`HeatDriver`，U#60）。子弹方向 `ViewKick.Apply`（`ViewKick.cs`，U#63），起点 `PlayerEye`（D-87）。

**HSD 现在和 R5 不一样**：Unity 的子弹 = aim + punch2（武器 punch），**没有 punch1 和开镜 drift**（[07 §4.3](07-camera.md) 已写，本章不重复；建议见 `_notes/hb-ch09.md`）。

#### 验收

- `CombatWeaponTests.TheFirstRoundHasNoRecoilAndTheSecondHasTheFirstRow`：第一发偏移 0，第二发是第 0 行。
- `CombatWeaponTests.BulletsFollowTheRecoilAndTheViewDoesNot`、`CombatWeaponTests.TheRecoilMovesTheViewAndTheRoundsTogetherThenComesBack`。
- 射速：`CombatWeaponTests.BurstCycleIsNMinusOneOverRatePlusDelay`、`CombatWeaponTests.DevotionClimbsAsMeasured`、`CombatWeaponTests.ChargeRifleFiresOnlyWhenFull`、`CombatWeaponTests.NemesisHeatSpeedsTheBurstsAsMeasured`。
- 合格线：第一发偏移 0（逐位）；射速和字段差 < 3 %。

#### 出处

- RV §1.3、§3（次序、第一发）；DP §7.1、§7.5（#122 版）。PR #93、#122，还没合并
- FG §6（射速、蓄力、拉栓）。PR #122，还没合并
- GM `D-EXTENSIONS.md` §1（射速对字段）。PR #95，还没合并
- D-87（子弹从眼睛出发）、D-88（后坐按 R5 punch，取代 D-86）。#91 / #104，还没合并
- [反编译] kick 0x140711ce0；累计值 0x1406fea80。

---

## 2. 后坐

### 2.1 武器 punch 弹簧（第二组）

#### 原理

后坐不是"把画面往上推一段再插值回来"，而是**往一个弹簧上加冲量**，弹簧自己把画面推出去再拉回来（T2）。和移动 kick 用的是同一种物理（07 §1.1）。不同的是：**拿着枪时，第二组弹簧的常数换成这把枪自己的**，而且在腰射 / 开镜、冷 / 热之间插值。这带来 R5 后坐最有特点的两种手感：

- **开镜连射一直爬**：大多数连发枪开镜的"热弹簧"刚度 k = 0，打的时候弹簧不往回拉，枪口一路往上走；停火后热度降下来，弹簧变回冷弹簧，快速回家。
- **腰射边打边回**：腰射热弹簧 k ≠ 0（或者根本没有热弹簧），连射到后面画面反而往回落。

打完一定回到原位，而且最后**直接归零**，不留尾巴（P7、T8）。

#### 规则和公式

1. 每轴（俯仰、偏航、横滚）存角度 x、角速度 v；每条命令按精确解推进 x'' = −k·x − d·v（和帧率无关，07 §1.1 的 `step`）。
2. **热度** h：每发 += `viewkick_spring_heatpershot`（上限 1）；最后一发后 `viewkick_spring_cooldown_holdtime` 内不变，之后在 `fadetime` 内**线性**降到 0（T5）。
3. **k、d 的取法**：先按热度在冷弹簧（`viewkick_spring`）和热弹簧（`viewkick_spring_hot`，没有就等于冷）之间插值，再按 `zf` 在腰射（`hipfire_*`）和开镜（`ADS_*`）之间插值。每轴有自己的 k、d。
4. **归零**：|x|² + |v|² < 0.001 时 x = v = 0。
5. **空手时**第二组用 65 / 9（和第一组一样）；拿枪时用上面的武器弹簧（FG §1.3）。移动事件写进第二组的那 0.2 倍也跟着走武器弹簧（07 §2.10 第 4 条）。

代表枪（俯仰，全部枪见 [recoil-springs.tsv](09-combat-feel/recoil-springs.tsv)）：

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 腰射 冷 / 热 k, d | — | 40, 20 /  40, 20 | — | 连发腰射冷弹簧 ζ 大多 ≥ 1（过阻尼） | [数据] [实测] RV §4 |
| R-301 开镜 冷 / 热 k, d | — | 115, 20 / **0**, 60 | — | 连发开镜 k热 = 0：15 / 17 把 | [数据] [实测] |
| Spitfire 腰射 / 开镜 冷 → 热 | — | 80, 20 → 0, 35 / 95, 15 → 0, 45 | — | — | [数据] [实测] |
| Wingman 腰射 / 开镜（没有热弹簧） | — | 120, 30 / 100, 25 | — | 单发枪多数没有热弹簧 | [数据] [实测] |
| P2020 腰射 / 开镜 冷 → 热 | — | 80, 20 / 55, 10 → 45, 10 | — | — | [数据] [实测] |
| Kraber 腰射 / 开镜 | — | 15, 4 / 25, 5 | — | 最软的一档 | [数据] |
| 热度 hold + fade（R-301 / Spitfire） | — | 0.08 + 0.05 s / 0.12 + 0.05 s | — | 全枪 0.07–0.29 + 0.05–0.3 s | [数据] [实测] RV §2.1 |
| 热度上升 `heatpershot` | — | 每发 +h，上限 1 | — | 枪不同 | [数据] |
| 归零门槛 | — | \|x\|² + \|v\|² < 0.001 | — | — | [反编译] [实测] |
| 空手第二组 | — | 65 / 9 | — | 实测 62.7–65.1 / 8.6–9.0 | [实测] FG §1.3 |
| 横滚弹簧（R-301） | — | k 20000，d 22 | — | 自己一根，不走热度 | [反编译] RV §10.1 |

#### 实现模板

```
// 单位：°、°/s、s；每条命令一次
heatNow = (now - lastShot < hold) ? heat
        : max(0, heat - (now - lastShot - hold) / fade)       // 线性降
for axis in (pitch, yaw):
    kHip = lerp(cold.hip.k[axis], hot.hip.k[axis], heatNow)   // d 同理
    kAds = lerp(cold.ads.k[axis], hot.ads.k[axis], heatNow)
    k    = lerp(kHip, kAds, zf);  d = …
    step(punch2[axis], k, d, dt)                              // 07 §1.1 的精确解，含过阻尼分支
    if x² + v² < 0.001: x = v = 0
```

**离散化要注意**：k = 0 时是纯阻尼（x 线性增长、v 指数衰减），过阻尼（ζ > 1）、欠阻尼、临界阻尼要分三个闭式（N3 §5 列了 TF2 的同一套）。不要用显式欧拉：R-301 腰射 k 40 d 20 在 60 Hz 下误差可见。

Unity 参考实现：`ViewKick.cs`（`ViewKick`，U#63；D-94 版在 U#67）字段 `pitch / yaw / roll`、`pitchSpeed …`、`heat`；弹簧表来自 `WeaponData.gen.cs` 的 springs 段，`WeaponDef.cs` `SpringValues`。

#### 验收

- `CombatWeaponTests.TheSpringStepIsExact`（逐步对精确解）、`CombatWeaponTests.EveryGunWithAKickHasItsSpring`。
- `CombatWeaponTests.TheReturnMatchesRecoilView(id, zoom, half)`：停火后到 50 % 的时间。
- 对照数据：RV §2.2 实测回落（下表），全部枪的算值在 `recoil-springs.tsv` 的 `fit_t50`、`fit_t10`。

| 枪 / 模式 | 峰值在最后一发后 | 到 50 % | 到 10 % | 归零（从最后一发） | 依据 |
|---|---|---|---|---|---|
| R-301 腰射 | 0.017 s | 0.365 s | 1.081 s | 2.4–2.7 s | [实测] |
| R-301 开镜 | 0.067 s | 0.244 s | 0.424 s | 0.8–1.0 s | [实测] |
| Spitfire 腰射 / 开镜 | 0.059 / 0.039 s | 0.341 / 0.304 s | 0.643 / 0.449 s | 1.3–1.6 / 1.0–1.2 s | [实测] |
| Wingman 腰射 / 开镜 | 0.056 / 0.070 s | 0.194 / 0.194 s | 0.535 / 0.523 s | 1.7–2.0 s | [实测] |
| P2020 腰射 / 开镜 | 0.068 / 0.111 s | 0.201 / 0.194 s | 0.500 / 0.349 s | 约 1.1 s | [实测] |

- 合格线：到 50 % 的时间和 R5 差 ≤ 0.02 s。**已知例外**：R-301 开镜 Unity 0.203 s 对 R5 0.244 s，差 0.04 s 没解释（RV §10.3、B5）。弹簧本身逐帧前推和 R5 下一帧差中位数 0.00003°（RV §10.3），所以差在别处。

#### 出处

- RV §2、§4、§5、§10.1：弹簧公式、冷热插值、归零、springs.txt 的值。PR #93（§10 在 #95），还没合并
- FG §1.3：拿枪时第二组用武器弹簧、空手 65 / 9。PR #122，还没合并
- DP T2、T5、T8、§7.2（#122 版）。PR #122，还没合并
- B5：R-301 开镜回落差 0.04 s 的排查。PR #123，还没合并
- N3 §5：TF2 的同一套弹簧和两条积分路径。PR #115，还没合并
- [反编译] 武器 punch `m_vecPunchWeapon` player+0x2448（角度）/ +0x2454（角速度）；弹簧 0x140a33ee0 / 0x140521af0；fraction 插值 0x140af0c90。

### 2.2 每发 kick：图案表 + 随机 + hard / soft

#### 原理

每把连发枪有一张**固定的图案表**：第 n 发往哪个方向踢多少。表是固定的，所以熟练的玩家能学会反着拉（P7）；随机只是表上一点小抖动，够让你不能闭眼打。同一张表配不同的弹簧、hard / soft、射速，可以做出手感完全不同的枪（Flatline 和 Spitfire 共用前两列）——**做新枪不必每次写新表**（DP §7.3）。

每一脚分成两部分：**hard**（直接加到角度，一帧就到）和 **soft**（加到角速度，由弹簧在 1/d 秒内推出来）。hard 多 = 后坐"脆"，soft 多 = 后坐"推"。

#### 规则和公式

1. 图案表每行四列：`偏航 俯仰 偏航随机 俯仰随机`，度。**俯仰负 = 向上，偏航负 = 向右**（[实测] RV §1.4）。
2. 这一发的基础量：kick_p = 行[俯仰] × `viewkick_pitch_base`，kick_y = 行[偏航] × `viewkick_yaw_base`。
3. 随机：|r| 在 `viewkick_*_random_innerexclude` … 1 之间均匀，符号抛硬币；kick += |r| × 符号 × 行[随机列] × `viewkick_*_random` × 0.5。**没有图案的枪**（P2020、Wingman 等 12 把）：kick = base + 同样的随机，随机列当 1，**也乘 0.5**（[实测] RV §10.2：Wingman −1.40 … −1.68 = 0.35 × (−4.4 ± 0.4)）。
4. 写进弹簧：x += `hardScale` × kick × 缩放（§2.3）；v += `softScale` × 20 × kick × 缩放。
5. 每发开始前，角速度先乘 `viewkick_spring_velocityScalePerShot`（基础枪都是 1）。
6. 一发的最终抬高 ≈ kick × (hard + soft × 20 / d热)（k热 = 0 时精确），所以画面上的幅度**不等于表**：R-301 开镜约 1.2 × 表，Spitfire 开镜约 1.56 ×，腰射约 2 ×（RV §1.2）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| soft × 20 / hard（R-301 / Spitfire / Wingman / P2020，俯仰） | — | 132.86 / 193.33 / 37.14 / 20.00 /s | — | 每发实测精确等于公式 | [实测] RV §4 |
| R-301 hard / soft（俯仰） | — | 0.35 / 2.325 | — | 连发 soft/hard 2.1–12（中位 6.6），单发 0.15–2.8 | [数据] DP §7.2 |
| R-301 图案 `rspn101_2` 行数 / 累计俯仰 5 · 10 · 20 发 | — | 28 行；2.69 / 3.31 / 4.66 ° | — | R-99 2.67 / 5.65 / 8.03 °（近直线） | [数据] DP §7.3 |
| R-301 图案第一行偏航 | — | −0.30 °（向右） | — | 同一把枪多只朝一边漂 | [数据] [实测] |
| R-301 每发随机 σ | — | 约 0.10 °（均值 0） | — | 随机列 ±0.15–0.225 | [实测] RV §4 |
| 单发枪 base（P2020 / Wingman / Peacekeeper） | — | −0.95 / −4.4 / −5.5 ° | — | — | [数据] [实测] |
| 系数 × 20 | — | 20 × | — | 固定，和移动 kick 同一个 | [反编译] |
| 随机 × 0.5 | — | 0.5 × | — | 有无图案都乘 | [反编译] [实测] |
| R-301 开镜 20 发连射峰值 | — | 约 5.7 °（3 次 4.93 / 5.81 / 6.44） | — | 模拟 5.29 ± 0.53 ° | [实测] RV §1.2、§10.3 |
| R-301 腰射连射 第 5 / 20 发 | — | 约 5.1 / 2.7 ° | — | 腰射边打边回 | [实测] |

#### 实现模板

```
// 单位：°、°/s
kick(gun, now, stance):
    row   = pattern ? pattern.rows[rowIndex(now, stance)] : null       // §2.4
    kp    = amount(gun.pitch_base, row?.pitch, row?.pitchRandom ?? 1, gun.pitch_random)
    ky    = amount(gun.yaw_base,   row?.yaw,   row?.yawRandom   ?? 1, gun.yaw_random)
    sp, sy = scale(gun, 0, now, stance), scale(gun, 1, now, stance)    // §2.3
    pitch      += gun.pitch_hard * kp * sp
    pitchSpeed += gun.pitch_soft * 20 * kp * sp
    yaw        += gun.yaw_hard * ky * sy;   yawSpeed += gun.yaw_soft * 20 * ky * sy
amount(base, rowVal, rowRand, rand):
    r = uniform(innerExclude, 1) * coin()
    return (rowVal ?? 1) * base + r * rowRand * rand * 0.5
```

Unity 参考实现：`ViewKick.Kick`、`ViewKick.Amount`（`ViewKick.cs`，D-94 版 U#67）；图案表 `WeaponDef.cs` `PatternTable`（行、`loopOffset`、`startMax`），数据 `WeaponData.gen.cs`。U#60 的旧做法（D-86：后坐只偏子弹、不动画面）是 `SpreadRecoil.cs` `RecoilPattern`，留在 `arsenal.recoilMovesView` 关掉时用（默认开 = 本节的做法）。

#### 验收

- `CombatWeaponTests.ANegativeTableYawGoesRight`、`CombatWeaponTests.AGunWithoutAPatternRollsHalfItsRandom(id, kick, half)`、`CombatWeaponTests.TheStabilizerScalesTheTable`、`CombatWeaponTests.OtherPatternsMatchTheRecordsFormula`。
- `CombatWeaponTests.TheAmplitudeMatchesRecoilView(id, zoom, gap, shot, r5, within)`：Unity 不带随机，步长 1/120 s，实际幅度 ÷ 表累计。

| 枪 | 模式 | 第几发 | Unity | R5 |
|---|---|---|---:|---:|
| R-301 | 腰射 | 1 / 5 / 20 | 2.07 / 1.88 / 0.52 | 2.10 / 1.86 / 0.57 |
| R-301 | 开镜 | 20 | 1.12 | 1.17–1.28 |
| Spitfire | 腰射 / 开镜 | 5 | 2.01 / 1.59 | 1.97–2.21 / 1.45–1.59 |

- 合格线：幅度比和 R5 差 ≤ 0.1；方向逐发一致（负偏航 = 右）。

#### 出处

- RV §1.2、§1.4、§4、§10.1–10.2：hard / soft、方向、随机 × 0.5、幅度。PR #93（§10 在 #95），还没合并
- DP P7、T2、§7.2、§7.3（#122 版）：数值范围、典型图案。PR #122，还没合并
- D-88、D-94。#91 / #104，还没合并
- [反编译] kick 0x140711ce0；字段偏移（武器对象 +0x2120 起 viewkick，+0x2134 soft，+0x2138 hard）；图案表 0x142819e70，每张 0x42c 字节。

### 2.3 每发缩放（D-94）：第一发、累计值、蹲、空中开镜、移动

#### 原理

同一张表，在不同情况下踢得不一样大。R5 用**乘系数**而不是写分支（T6）：一个按"打了多久"变的系数（让某些枪越打越重、某些枪第一发特别重），再乘姿态系数。最明显的一条：**空中开镜后坐翻倍**——开镜是"站稳了打"的姿态，跳着开镜打要付钱（P6）。走、蹲、滑铲对后坐几乎没影响，它们的代价在扩散里（§5）。

#### 规则和公式

```
缩放(轴) = lerp(腰射值, 开镜值, zf) × 蹲 × 空中 × 移动
腰射值   = (第一发 且 firstshot_hipfire ≠ 0) ? firstshot_hipfire
         : min_hipfire + (max_hipfire − min_hipfire) × t          // 开镜值同理
t        = clamp((累计值 − LerpStart) / (LerpEnd − LerpStart), 0, 1)；Start = End 时 t = 1
蹲       = 1 + 下蹲比例 × (viewkick_duck_scale − 1)
空中     = 1 + zf × (viewkick_air_scale_ads − 1)        // 不在地面时；只对开镜
移动     = viewkick_move_scale                           // 水平速度 > 当前姿态速度的一半时
```

1. **三个累计值**：俯仰、偏航（每发 += `viewkick_scale_valuePerShot`，封顶 `LerpEnd`）、图案（§2.4）。衰减用同一组 `valueDecayDelay` / `valueDecayRate`。**kick 读加之前的值**（EVA-8 第 2 发 1.34，读加之后会是 1.67）。
2. **"第一发"** = 扳机松开超过一段时间后的第一发（武器上的发数计数归零）。R5 实测 0.179 s、0.195 s 没归零，0.231 s、0.248 s 归零；HSD 取 0.2 s [推断]。
3. 横滚**不走缩放**（§2.5）。
4. 滑索算空中（[实测] B-STATES）；跑墙算空中是 [推断]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 空中开镜倍数 `viewkick_air_scale_ads` | — | 2 ×（18 把；G7 1；Spitfire、Mastiff 1） | — | 实测 1.6–2.1（每格 1 次，噪声 ±0.2） | [数据] [实测] B-STATES §2 |
| 腰射空中 | — | 1 × | — | 实测 0.97–1.20 | [实测] |
| 蹲 `viewkick_duck_scale` | — | 1 ×（Spitfire 0.9、Devotion 0.8） | — | 实测在噪声内 | [数据] [实测] |
| 移动 `viewkick_move_scale` | — | 1 ×（所有基础枪） | — | 只读到代码 | [数据] [反编译] |
| 第一发 Mastiff 腰射 / 开镜 | — | 2.0 / 3.0 × | — | 实测 2.03 / 3.10 | [数据] [实测] RV §10.2 |
| 第一发 Longbow / Sentinel / Triple Take | — | 1.5 × | — | 实测 1.45–1.55 | [数据] [实测] |
| EVA-8 腰射 第 2 / 3 发 | — | 1.33 / 1.67 × | — | 实测 1.34 / 1.56 | [数据] [实测] |
| HAVOC 腰射 15 发后 | — | 1.72 × | — | 实测 1.78 | [数据] [实测] |
| "第一发"的松扳机门槛 | — | 0.2 s | — | 0.195 … 0.231 s 之间 | [推断] RV §10.2 |
| **对不上的**：Devotion 腰射第一发 / Kraber 开镜第一发 | — | 公式 1.2 / 1.5 × | — | 实测 1.02 / 1.37，没查 | [实测] |

#### 实现模板

照上面的公式，每发 kick 前算一次俯仰、偏航两个缩放。下蹲比例用身体的连续值（02 / 03 章的下蹲过渡），不要只用 0 / 1。

Unity 参考实现：`ViewKick.Scale`、`ViewKick.Pick`、`ViewKick.Rise`；姿态 `KickStance`（`zoom`、`crouched`、`airborne`、`fast`、`burstCount`、`burstIndex`），在 `ArsenalWeapon.cs` 里按身体状态填。开关 `arsenal.recoilScales`（D-94，关 = D-88 的做法：不缩放、不滚、表从 loop_offset 循环）。

**HSD 现在和 R5 不一样**：`KickStance.crouched` 只有 0 / 1，R5 是连续的下蹲比例（RV §10.4）。

#### 验收

- `CombatWeaponTests.AFirstRoundHasItsGunsScale(id, zoom, scale)`、`TheScaleRisesWithTheCounterReadBeforeThisShot`、`TheCounterStopsAtTheEndOfItsRange`、`OffTheGroundAnAimedKickDoubles(id, zoom, times)`、`CrouchingTakesTheDuckScale(id, times)`、`TheGunTellsTheKickItIsInTheAir`、`EveryGunsScaleFieldsParse`、`TheSwitchKeepsTheOldKick`（类都是 `CombatWeaponTests`）。
- 合格线：上表"公式"列逐位；和 R5 实测差在噪声 ±0.2 内（Devotion、Kraber 两格例外，已登记）。

#### 出处

- RV §10.1–10.2、§10.4：规则、和实测比、Unity 现状。PR #95（`combat/gun-measure`），还没合并
- GM `B-STATES.md` §2：各姿态后坐倍率实测。PR #95，还没合并
- D-94（选中按反编译做；没选保持 D-88）。#91 / #104，还没合并
- [反编译] 缩放 0x140712e80 + 0x140712d10；累计值 0x1406fea80（俯仰 +0x1604、偏航 +0x1608、图案 +0x160c）；发数 +0x1700；空中缩放的另一个排除条件 +0x2bb9（不知道是什么）。

### 2.4 图案走到哪一行：value 倒数、表尾、start_max、连发

#### 原理

"什么时候回到第一发"不是"停火 X 秒清零"，而是一个**数值在倒数**：每发加一，停火等一小段后按速率减。所以短停顿后不是从头开始，而是**从中间某一行接着打**——点射两三发再接着打，图案是连续的。这让点射和压枪之间有平滑的过渡，而不是一个硬阈值（T5）。

#### 规则和公式

```
行号 = floor(value / valuePerShot)，不超过最后一行
每发后 value += valuePerShot（这些枪都是 1）
value 当前值 = 存值 − max(0, 现在 − 上次开火 − valueDecayDelay) × valueDecayRate，不小于 0
```

1. "回到第一发"的时间 = `valueDecayDelay` + 发数 × `valuePerShot` / `valueDecayRate`。
2. **表尾**：value 到 `行数 × 每行` 时减 `loop_offset` 行。loop 0 = **停在最后一行**（R-301、Flatline、R-99 实测）；loop 非 0 从 `行数 − loop` 接着走（Spitfire 30 行、loop 23 → 从第 7 行接着走，[反编译]，没实测）。
3. **`start_max`**：第一发（§2.3 的"第一发"）时 value 不超过 `start_max` 行。−1 = 没上限（R-301 主表）。只有 8 张表设了。
4. **连发**：一组的第一发，value 向上取整到整组 [反编译，没单独验证]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 `valueDecayDelay` / `Rate` | — | 0.09 s / 50 /s | — | 全枪 0.09–0.55 s，35–160 /s | [数据] [实测] |
| R-301 回到第一发：打 1 发 / 21 发 | — | 0.11 / 0.51 s | — | — | [算] [实测] |
| R-301 打 11 发后停 0.131 / 0.231 / 0.280 / ≥ 0.388 s，下一发行号 | — | 8 / 3 / 1 / 0 | — | 实测 value 8.93 / 3.92 / 1.25 / 0，公式 8.95 / 3.95 / 1.50 / 0 | [实测] RV §3 |
| Spitfire `valueDecayDelay` / `Rate` | — | 0.15 s / 80 /s | — | — | [数据] [实测] |
| Hemlok | — | 0.435 s + n / 35 | — | — | [数据] |
| 表尾 loop 0 | — | 停在最后一行（R-301 行 27，Flatline / R-99 行 29） | — | 3 把实测 | [实测] FG §5.1、GM D §9 |

#### 实现模板

```
rowIndex(now, stance):
    v = valueNow(now)
    if stance.burstCount > 1 and stance.burstIndex == 0: v = ceil(v / (burstCount*perRow)) * burstCount*perRow
    if shotIndex == 0 and table.startMax >= 0: v = min(v, table.startMax * perRow)
    return min(floor(v / perRow), rows - 1)
next(now):                                   // 每发之后
    v = min(rows*perRow, valueNow(now) + perRow)
    return v >= rows*perRow ? v - loopOffset*perRow : v
```

Unity 参考实现：`ViewKick.ValueNow`、`ViewKick.RowIndex`、`ViewKick.Next`（U#67）。

#### 验收

- `CombatWeaponTests.ThePatternCountsDownAndCanResumeMidTable(gap, row)`（RV §3 的 7 个间隔）、`ThePatternStaysOnTheLastRowWithoutALoop`、`ThePatternDropsByLoopOffsetRowsAtItsEnd`、`AFirstRoundStartsNoLaterThanStartMax`、`WithoutAStartMaxAFirstRoundResumesMidTable`、`TheShotIndexKeepsThroughAShortGap`。
- 合格线：RV §3 表的行号逐个一致。

#### 出处

- RV §3、§10.1。PR #93 / #95，还没合并
- FG §5.1（Flatline、R-99 表尾）；GM `D-EXTENSIONS.md` §9（R-301 表尾）。PR #122 / #95，还没合并
- DP P7、T5、§7.3。PR #122，还没合并
- [反编译] 0x140712c80（图案 value）、0x140712be0（两个缩放计数）、0x1406fea80（表尾）。

### 2.5 punch 怎么分给画面、准星和子弹：`weaponFraction`、横滚

#### 原理

同一个 punch，画面看到的、准星画的、子弹飞的可以不一样多。`weaponFraction` f 是"这把枪的后坐有多少只给子弹、不给画面"。f = 0：画面、准星、子弹三者一体（R-301 开镜）——你看到的就是子弹去的地方。f 大：画面晃得少，但子弹比准星偏得多（Kraber 开镜 0.75）——画面稳，代价是下一枪前要等枪口回来。这是 P1 的直接实现：**画面偏离准星时，规则写清楚子弹去哪**。

横滚只进画面，不进子弹，也不乘 (1 − f)。

#### 规则和公式

1. f = lerp(`viewkick_hipfire_weaponFraction`, `viewkick_ads_weaponFraction`, zf)（线性）。
2. 画面俯仰 / 偏航 += (1 − f) × punch2；**准星** = aim + (1 − f) × punch2（准星和画面中心同一个点）。
3. **子弹** = aim + punch1 + **完整** punch2（不乘 1 − f），取这一发 kick 之前。
4. **横滚**：每发 `base + 硬币 × (randomMin … randomMax)`，自己的弹簧（R-301 k 20000，d 22），**全部进画面**，不乘 1 − f，**不动子弹**。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 f 腰射 / 开镜 | — | 0.05 / 0 | — | 连发腰射 0.05–0.35，开镜 0–0.1 | [数据] [实测] RV §1.1 |
| Spitfire f 腰射 / 开镜 | — | 0.2 / 0 | — | — | [数据] [实测] |
| Wingman f 腰射 / 开镜 | — | 0.4 / 0.3 | — | 单发腰射 0–0.5，开镜 0–0.75 | [数据] [实测] |
| P2020 f 腰射 / 开镜 | — | 0 / 0.2 | — | 开镜实测扣 drift 后 0.774（期望 0.8） | [数据] [实测] GM D §9 |
| Kraber f 开镜 | — | 0.75 | — | 只读了字段，没跑 | [数据] |
| punch → 画面斜率（腰射 R-301 / Spitfire / Wingman / P2020） | — | 0.950 / 0.800 / 0.600 / 1.000 | — | 最大残差 0.000 ° | [实测] |
| 子弹 / punch（开镜，不含第一发） | — | R-301 0.96，Spitfire 0.98，P2020 1.03 | — | Wingman 1.21 = 开镜 drift 进子弹（FG §5.2） | [实测] RV §1.3 |
| 每发横滚 R-301 / Spitfire / P2020 / Wingman | — | +0.08 … +0.41 / −0.20 … −0.52 / −0.14 … −0.20 / ≈ 0 ° | — | 最大约 0.5 ° | [实测] GM D §5 |
| 横滚进画面的比例 | — | 1.00（中位数，10301 帧） | — | 俯仰同帧 0.95 | [实测] RV §10.2 |

#### 实现模板

```
f       = lerp(fracHip, fracAds, zf)
view   += (1 − f) * (punch2.pitch, punch2.yaw) ; viewRoll += punch2.roll
reticle = screenCentre                                  // 准星画在画面中心 = aim + (1−f)·punch2
round   = aim + punch1 + punch2                         // §1.1
```

Unity 参考实现：`ViewKick.ViewShare(stats, zoom)`（= 1 − f）、横滚 `ViewKick.RollAmount`（U#67）。画面接法在原生镜头 `NativeCamera.cs`（[07 §2.10](07-camera.md)）。注意 Unity `CameraPose.roll` + = 向左，R5 + = 向右，接进相机要取负（RV §11.4 修过一次符号错误）。

#### 验收

- `CombatWeaponTests.TheRoundsSitAboveTheCrosshairByTheWeaponFraction`、`TheRollKicksAndComesBackToNothing`、`TheRollMovesNoRound`、`TheRollReachesTheViewAndLeaves`。
- 合格线：腰射画面 / punch2 斜率 = 1 − f（差 ≤ 0.005）；横滚不改变子弹方向（逐位）。

#### 出处

- RV §1.1、§1.3、§10.1–10.2。PR #93 / #95，还没合并
- FG §5.2（Wingman 偏高 = drift）。PR #122，还没合并
- GM `D-EXTENSIONS.md` §5、§9。PR #95，还没合并
- DP P1、T3。PR #122，还没合并
- [反编译] fraction 0x140af0c90；武器字段 +0x2164（腰射 fraction）、+0x216c（开镜 fraction）。

### 2.6 鼠标下压抵消 punch

#### 原理

压枪时，往下拉的鼠标**先吃掉 punch**，吃完了才动瞄准。效果是：压掉的那部分后坐**不会在停火后再弹回来**，画面也不会被弹簧拉到比起点更低。玩家的感觉是"压枪不会压过头"。往上拉（和后坐同向）不抵消，全部进瞄准。这条规则只帮"反着后坐方向"的输入。

#### 规则和公式

每条命令，每个轴（俯仰、偏航各算一次，横向没实测）：

```
Δ = 这条命令的鼠标角度增量
if sign(Δ) == −sign(punch2) and punch2 != 0:
    used    = min(|Δ|, |punch2|)
    punch2 += sign(Δ) * used          // 减到 0 为止，不越过
    Δ      -= sign(Δ) * used
aim += Δ                               // 剩下的才进瞄准
```

- 对**子弹**，鼠标的作用一直是一比一（子弹 = aim + punch2，只是记账的地方不同）。
- 对**画面**，抵消期间画面随鼠标走 (1 − f) 倍（R-301 腰射 0.95，开镜 1）。
- 抵消写回的是弹簧的角度（R5 通过 `m_viewSpringCorrection`）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 抵消比例（反向） | — | 1 : 1 | — | 3 + 3 次腰射 / 开镜 | [实测] EM §1 |
| 同向输入 | — | 全部进瞄准（抵消 0） | — | 3 次 | [实测] |
| 越过 0 | — | 不越过（punch 到 −0.004 ° 后的 4 count 一个一个进瞄准） | — | — | [实测] |
| R-301 腰射按住 1 s 停火时 punch | — | −3.81 … −4.60 °；边打边下拉 30 count/s 时 −0.05 … 0 ° | — | — | [实测] |
| 停火后下拉 1.98 °，画面最后低于起点 | — | 0.09 … 0.44 °（不是 1.98 °） | — | — | [实测] |

#### 实现模板

见上面伪代码；放在"读鼠标 → 写 aim"那一步，在 §2.1 的 `step` 之前。

Unity 参考实现：**没有做**。`ViewKick.cs` 的类注释写"Left out, written in R5-DIFF-ARCHIVE: the mouse cancelling the punch（未实测）"——现在已经实测（EM，11-13），Unity 还是直接写瞄准角（`PracticeGame.cs` 的鼠标处理）。

#### 验收

- 建议的测试（还没写）：按住开火时下拉，`aim` 在 punch2 ≠ 0 期间不动；punch2 不越过 0；同向输入全部进 `aim`；停火后画面不低于起点（对 EM `A1-RUNS.tsv` 的 7 种运行）。
- 合格线：EM §1.2 表的"被吃掉"列，差 ≤ 0.11 °（1 count）。

#### 出处

- EM §1（A1）：方法、7 种运行、逐帧。PR #122，还没合并；原始数据 RawData `apex/research/combat/gun-measure/e-mouse/`
- RV §7 第 1 条（当时只有反编译）。PR #93，还没合并
- DP T3（#122 版的补句）。PR #122，还没合并
- [反编译] 0x140a33ff0；写回弹簧 0x140a34170。

### 2.7 枪模每发的跳动（D-95）

#### 原理

除了画面抬起，枪本身在画面里也往后一顿、偏一下。开镜时这一下是 R5 的明确规则（枪模自己的弹簧）；腰射时枪也在动，但来源没追到，只能用拟合。HSD 的态度是：**开镜照规则做，腰射用拟合，拟合差的通道直接置 0——不动比动错好**。

整把枪绕**眼睛**转，不绕枪口：R5 枪模原点在相机上，所以开镜横滚时瞄具还在准星上。这一项只影响画面，不进模拟，不消耗随机数。

#### 规则和公式

**开镜（规则）**：枪模有三个弹簧（后退 x、偏航 y、横滚 z），参数 `viewmodel_spring_jolt` 按 zf 插值，不走热度。每发：

```
后退 x：Δ角度 = backwardPerShot × pitch_hard × jolt_scale    Δ速度 = backwardPerShot × pitch_soft × 20 × jolt_scale   （每发一样，不乘 kick）
偏航 y：Δ = 这发 punch 偏航的 (Δ角度, Δ速度) × jolt_scale
横滚 z：Δ = 这发 punch 横滚的 (Δ角度, Δ速度) × jolt_scale
进枪模（全部 × zf，所以腰射没有）：
  向前 = x × zf
  向右 = jolt_side · (x, y, z) × zf
  横滚 = jolt_roll · (x, y, z) × zf − punch 横滚           // 最后一项不乘 zf：枪相对世界基本不滚
```

所有枪的 `jolt_side`、`jolt_roll` 只有中间一项非 0，所以**枪的横滚来自这一发的偏航后坐**。

**腰射（拟合，不是规则）**：枪的俯仰 = g × (镜头俯仰 − L)，L 用弹簧 (k, d) 追镜头俯仰；偏航同样；前、上 = 固定比例 × 枪的俯仰；全部 × (1 − zf) [推断]。每把枪每个通道一组 (k, d, g)，数据在 GM `D-GUNKICK.tsv`；残差超过幅度 60 % 或增益 > 2 的通道置 0（9 个）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 开镜连射后退峰值 | −0.00808 m | −0.318 u | −0.00442 H | 公式 −0.301 u | [实测] RV §11.2 |
| R-99 / Spitfire / Prowler 开镜后退峰值 | −0.0155 / −0.0148 / −0.0173 m | −0.610 / −0.584 / −0.682 u | −0.0085 / −0.0081 / −0.0095 H | 公式差 ≤ 0.015 u | [实测] |
| 15 把枪前后误差 RMS | 0.00003–0.00033 m | 0.001–0.013 u | — | L-STAR 0.086 u 没解释 | [实测] |
| R-301 腰射第一发枪俯仰 | — | −0.60 °（Unity 拟合 −0.481 °） | — | 拟合偏小 | [实测] |
| 单发枪 `jolt_scale` | — | 0（Mastiff、Kraber、Sentinel …） | — | 但开镜也跳，见下 | [数据] |

#### 实现模板

Unity 参考实现：开镜规则 `ViewKick.Jolt`（`ViewKick.cs` 的 `joltBack / joltYaw / joltRoll` 及速度，U#67）；腰射拟合 `GunKick.cs`（`GunLag`、`GunKickFit`、`GunKickView`，数据 `GunKickData.gen.cs`，U#67）；画在 `HeldModels.cs` `HeldModelView.Kick`。开关 `arsenal.gunKick`（D-95，关 = 不跳）。

#### 验收

- `CombatWeaponTests.AtTheHipTheJoltDoesNotReachTheGun`、`AGunWithNoJoltHasNone`、`TheJoltFadesAndUsesNoRandom`、`AtTheHipTheGunFollowsTheCameraAndSettles`、`TheStepRateDoesNotChangeTheLag`、`EveryGunHasAFitOrSaysItHasNone`。
- 合格线：开镜后退峰值和 R5 差 ≤ 0.02 u（用 R5 的射击时间回放；峰值对射击时间很敏感，R-99 第二发晚一帧就少 0.06 u）。

**单发枪开镜的跳动：缺**。Mastiff、Kraber、Sentinel 的 `jolt_scale` 是 0，但 R5 开镜也跳（Mastiff 前 +0.49 u、俯仰 −1.52°；Kraber −2.66°），既不走开镜规则也没进腰射拟合，**Unity 现在这几把开镜时枪不动**。见 §2.8 和 §9。

#### 出处

- RV §11（规则、对比、腰射拟合、没做的）。PR #95（`combat/gun-measure`），还没合并
- GM `D-GUNKICK.tsv`、`D-JOLT.tsv`。PR #95，还没合并
- D-95（选中：开镜规则 + 腰射拟合；没选：继续追腰射来源、腰射不动；没做：单发枪开镜）。#91 / #104，还没合并
- [反编译] kick 0x140711ce0；枪模 0x14085c3e0；枪模弹簧玩家 +0x3514（角度）/ +0x3520（速度）；字段 `viewmodel_jolt_scale` 0x730、`backwardPerShot` 0x734、`side` 0x738、`roll` 0x744（加武器 +0x19d0）；腰射来源候选 +0x1de0 矩阵（没追）。

### 2.8 单发枪：拉栓 / 泵动的镜头和开镜跳动（缺的部分）

#### 原理

R5 开枪**没有震屏**（7 把枪实测），想让单发枪"有分量"，R5 靠的是两样：大的第一发缩放（§2.3，Mastiff 开镜 3 ×），和**拉栓 / 泵动动画带着镜头动**（相机挂点随动画走，量级可到 5°）。后者是一条平滑曲线，不是噪声。开镜时多数被压掉。

#### 规则和公式

1. 开枪那一刻：画面只有 punch1 + punch2 + drift，别的偏移 0.000°（[实测] FG §2）。
2. 拉栓 / 泵动 / 换弹的动画镜头：从开枪后零点几秒开始，平滑曲线，峰值和时长见下表。**曲线形状没量**，只有峰值和时长（FG `B2-CYCLE.tsv`）。
3. 单发枪开镜跳动（§2.7 末尾）：只有两把的峰值。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 开枪震屏 | — | 0 °（7 把 × 腰射 / 开镜 × 2 次） | — | 探针能看见 0.9 ° 的脚本震屏 | [实测] FG §2 |
| Peacekeeper 腰射泵动：开始 / 时长 / 俯仰 / 偏航 / 横滚 | — | 射后 0.27 s / 1.09 s / 5.15 / −0.31 / −1.84 ° | — | 开镜 0.39 s 起，0.41 / 0.75 ° | [实测] |
| Kraber 拉栓（腰射 / 开镜） | — | 0.85 / 1.08 s 起，1.6–2.3 s，俯仰 4.9 °、偏航 −0.87 °、横滚 −1.46 ° | — | 开镜也有（瞄具界面） | [实测] |
| Longbow 腰射拉栓 | — | 0.32 s 起，0.6 s，俯仰 0.43 °、横滚 0.70 °、眼睛 0.1 u | — | 开镜 0 | [实测] |
| Mastiff 开镜跳动 | 前 +0.0124 m | 前 +0.49 u；俯仰 −1.52 ° | 0.0068 H | 只有峰值 | [实测] RV §11.5 |
| Kraber 开镜跳动 | — | 俯仰 −2.66 ° | — | 只有峰值 | [实测] D-95 |

#### 实现模板

Unity 参考实现：**都没有做**。HSD 的枪模是静态占位（没有动画资源），拉栓镜头和单发开镜跳动都不在 `ViewKick` / `GunLag` 里。做的话建议走 [07 §2.5](07-camera.md) 翻越镜头同样的"动画挂点曲线"通道，曲线形状先用 [设计]，峰值和时长对上表。

#### 验收

- 建议（还没有测试）：开枪那一帧画面 = aim + punch1 + (1 − f)·punch2 + drift，别的偏移逐位为 0；拉栓镜头峰值和时长对上表，差 ≤ 10 %。

#### 出处

- FG §2（B2）、`f-gaps/B2-SHAKE.tsv`、`B2-CYCLE.tsv`。PR #122，还没合并
- RV §11.5；D-95 "没做"。PR #95 / #104，还没合并
- [07 §2.10](07-camera.md) 第 7 条（同一组数）。

---

## 3. 开镜

### 3.1 开镜进度 `zf` 和开镜时间

#### 原理

开镜只有**一个**状态：线性进度 `zf`。画面上看到的加速感（先快后稳）全部来自"读 zf 的人"各自加的曲线（T1）。这样中途松开、再按，只是 zf 反向接着走，没有跳变；所有和开镜有关的东西天然同步。

#### 规则和公式

```
按住开镜：zf += dt / zoom_time_in
松开：    zf −= dt / zoom_time_out
clamp(zf, 0, 1)；反向时从当前值接着走
```

1. 关镜从不比开镜慢（29 把里 26 把更快，3 把相等）[数据]。
2. 瞄具会改开镜时间（R-301 装 HCOG `zoom_time_in` 0.27 → 0.29）；枪托 L1 × 0.85（字段），实测最多 × 0.75 [实测] GM 04 卷。
3. 不能开镜的时候：换弹解锁前（§7.1）、切枪中、钩爪拉动中、爬墙段（zf 在 0.14 s 内被取消）；冲刺中按开镜 = 结束冲刺并开镜（0.02 s 内 zf 开始变）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 `zoom_time_in` / `out` | — | 0.27 / 0.23 s | — | 步枪类全同 | [数据] [实测] ADS §1 |
| Wingman / P2020 | — | 0.18 / 0.16 s | — | 手枪 | [数据] [实测] |
| Spitfire | — | 0.34 / 0.30 s | — | 机枪 | [数据] [实测] |
| Kraber | — | 0.58 / 0.55 s | — | 狙击 0.20–0.58 | [数据] |
| 中途反向 | — | 连续（R-301 0.598 松开，下一帧 0.567） | — | — | [实测] |
| 钩爪拉完后回到开镜 / 翻完回到开镜 | — | 0.35 s / 0.28 s（zf → 1） | — | — | [实测] FG §8 |

全部枪的开镜时间在 [gun-weight.tsv](09-combat-feel/gun-weight.tsv)（`zoom_time_in`、`zoom_time_out`）。

#### 实现模板

Unity 参考实现：`ArsenalWeapon.zoom`（`ArsenalWeapon.cs`）；能不能开镜在 `ArsenalWeapon.cs` "The aim button, unless a swap or a reload's lock holds it back"一段（U#65）。

#### 验收

- `CombatWeaponTests.TheZoomFollowsTheMeasuredSmoothstep`（zf 线性 + FOV smoothstep）、`CombatHeldModelTests.AimedFollowsTheZoomTimeFieldAndReloadTakesTheMagazineOut`、`CombatReloadSwapTests.AimingWaitsForTheUnlock`。
- 合格线：zf 到 1 的时间 = `zoom_time_in` ± 1 命令。

#### 出处

- ADS §1、§4.1；GM `report/03-ads-optics.md` §1（全枪字段）。PR #93 / #95，还没合并
- DP T1、§6.4、P5。PR #122，还没合并
- FG §8.1–8.2（钩爪、翻越中开镜）。PR #122，还没合并
- D-89。#91 / #104，还没合并

### 3.2 世界 FOV（smoothstep）

#### 原理

开镜时画面拉近，用的是 smoothstep：两头慢中间快。用户说"开镜应该有加速"是对的——加速不在 zf 上，在 FOV 这条曲线上。度数是玩家设置，**要学的是 tan 比**。

#### 规则和公式

```
t   = clamp01((zf − ads_fov_zoomfrac_start) / (ads_fov_zoomfrac_end − ads_fov_zoomfrac_start))   // 默认 0, 1
R   = R基础 + (zoom_fov × S − R基础) × (3 − 2t) t²
R5 本地：S = cl_fovScale = 1.27217，R基础 = floor(70 × S + 0.5) = 89
```

换算到别的基础 FOV：按比例，`tan(V'/2) = tan(V基础/2) × tan(R/2) / tan(R基础/2)`（[推断]，换算本身没在 R5 验证）。和滑铲 FOV 的拼法见 [07 §3.10](07-camera.md)。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 / Spitfire 开镜 FOV（`zoom_fov` 55） | — | 89 → 69.97 °（4:3 水平） | — | 残差 0.001 °（16 次） | [实测] ADS §1 |
| Wingman（`zoom_fov` 60） | — | 89 → 76.33 ° | — | — | [实测] |
| R-301 开镜到位 tan 比 | — | 0.712 | — | 3x HCOG 0.305 | [算] [实测] EM §2 |
| 曲线 | — | smoothstep 3t² − 2t³ | — | — | [实测] |
| 瞄具改窗口（例 `zoomfrac` 0.1–0.8） | — | 同一公式 | — | 没跑 | [反编译] |
| Kraber `zoom_fov` | — | 13.31（窗口 0.6–0.85） | — | 全屏瞄准镜 | [数据] |

#### 实现模板

Unity 参考实现：`AdsCurves.FovRatio(stats, zoom)`（`AdsCurves.cs`，U#63），常数 1.27217、89；世界相机按比例乘到 Unity 自己的基础 FOV 上。开关 `adsCurves`（D-89，关 = 不放大、枪走直线）。

#### 验收

- `CombatWeaponTests.TheZoomFollowsTheMeasuredSmoothstep`、`TheZoomAndTheSlowerMouseStayBehindTheirSwitchAndOnlyOnAGun`。
- 合格线：R-301 FOV 曲线和 `ADS-CURVES.tsv` 差 ≤ 0.01 °（换回 R5 度数比）。

#### 出处

- ADS §1、§4.2。PR #93，还没合并
- DP §6.4、§10.3（学比例）。PR #122，还没合并
- D-89。#91 / #104，还没合并
- [反编译] FOV 0x140af16a0，由 0x140af1720（`GetFOV` 路径 0x140afd8a0）调用。

### 3.3 枪模 FOV：两个分支（D-120、D-122）

#### 原理

枪有自己的 FOV，和世界 FOV 分开。机瞄开镜时枪模 FOV 跟着世界一起收窄（按 tan 比例），所以瞄具在屏幕上变大，像人凑近了看；装了写了专用字段的瞄具，枪模 FOV 走那个字段。**两件事要记住**：新枪、新瞄具都按这条，不要按 `zoom_fov` 直接换算；枪口和曳光起点的屏幕位置都跟着枪模 FOV 变。

#### 规则和公式

`V` 是枪模 FOV（R5 度数，4:3 水平），R 是当前世界 FOV（§3.2），R基础 = 89。

```
t = 同 §3.2
写了 zoom_fov_viewmodel（> 0）：  V = 70 + (zoom_fov_viewmodel − 70) × (3 − 2t) t²     （不看 cl_fovScale）
没写：                            tan(V/2) = tan(35°) × tan(R/2) / tan(R基础/2)
腰射（zf = 0）：                  两条都等于 70
狙击镜分支：bodygroup_ads_scope_set > 0、zf 到 ads_fov_zoomfrac_end、又没写字段时  V = 70（整屏镜内画面，看不到枪）[反编译，没实测]
Unity 竖直 FOV = 2·atan(tan(V/2) × 3/4)；1600×900 下每单位正切 600 / tan(V/2) 像素
```

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 腰射 V | — | 70 °（竖直 55.4 °，857 px/tan） | — | R-301 实测 833–863 px/tan | [反编译] [实测] IS |
| 机瞄 `zoom_fov` 55 开镜 V | — | 53.0 °（竖直 41.0 °，1203 px/tan） | — | 实测 R-301 1187、Sentinel 1221 | [算] [实测] |
| 机瞄 / HCOG `zoom_fov` 60 开镜 V | — | 58.5 °（竖直 45.6 °） | — | 没量 | [算] |
| 2x HCOG（`zoom_fov` 38.59，没写字段） | — | 36.1 °（1844 px/tan） | — | 实测 1847 | [算] [实测] |
| 1x 全息（字段 20）/ 3x（字段 14）/ 2–4x（字段 13.5） | — | 20 / 14 / 13.5 ° | — | 实测差 ≤ 5 % | [数据] [实测] |
| 旧的粗估（D-116） | — | 竖直 65.5 °（700 px/tan） | — | 作废 | — |

各瞄具字段在 IS `data/IS-OPTICS.tsv`（PR #99），这里不搬。

**HSD 有意和 R5 不一样（D-122）**：Kraber 开镜保持 `zoom_fov`（Unity 没有全屏瞄准镜画面，镜环是模型画的），R5 代码是到位后 V = 70。等用户定。

#### 实现模板

Unity 参考实现：`GunSights.cs`（`GunSights.GunFov`、`GunAim`，U#68），R 和 R基础用 `AdsCurves.FovRatio`（不看 Unity 自己的基础 FOV；滑铲和兴奋剂 FOV 不进这个比例）。瞄具字段 `GunOpticData.gen.cs`（U#69）。开关 `arsenal.gunFovWorldRule`（关 = 按 `zoom_fov`）。

#### 验收

- `CombatHeldModelTests.AimedTheFovRuleSwitchGoesBackToZoomFov`、`TheTracerStartsWhereTheMuzzleShowsAndThatFollowsTheGunFov`、`TheAimAndFovSwitchesGoBackToTheOldValues`。
- 合格线：开镜 px/tan 和上表差 ≤ 3 %（R5 实测是看图，精度约 3 %）。

#### 出处

- IS "枪模 FOV"一节（11-05 改正）、`data/IS-OPTIC-FOV.tsv`。PR #99，还没合并
- DP §7.10（#122 版）。PR #122，还没合并
- D-120（规则，研究改正）、D-121（D-VIEWMODEL 作废）在 #99；D-122（Unity 采用，Kraber 例外）在 #100 / #104；D-116 被取代。还没合并
- [反编译] 0x140838830（`FUN_140838830` 末尾）；字段 `zoom_fov_viewmodel` 0xdbc、`ads_fov_zoomfrac_start/end` 0x1c0 / 0x1c4、`bodygroup_ads_scope_set` 0xb4c（武器 +0x19d0 基址）。

### 3.4 开镜时枪的路径：程序偏移 + 每把枪的动画

#### 原理

枪从腰射位置到眼前，**大部分是动画**，程序偏移只是很小的一层。动画是"先朝中间甩、下沉、枪口下压、横向冲过头，再抬起到位"，zf 约 0.5 就到位了，FOV 还要继续走到 1——这就是"先快后稳"。**关镜不是开镜的倒放**：枪先在瞄准位置停着，zf 降到约 0.83 才开始动。

#### 规则和公式

1. **程序偏移**：`偏移 = hip + (ads − hip) × (1 − cos(π t)) / 2`，t = clamp01((zf − start) / (end − start))，窗口默认 0 … 0.5 [推断：三把枪拟合，默认值没在代码确认]。读 `viewmodel_offset_hip`、`viewmodel_offset_ads`；前向比字段少 2 u（代码固定减）。
2. **动画**：播放进度 = zf（开镜）或 1 − zf（关镜），开镜和关镜是两段不同的动画。曲线在动画资源里，**只测了 3 把**（附件 [ads-curves.tsv](09-combat-feel/ads-curves.tsv)，已含第 1 层，用表时第 1 层不要再加）。
3. 没有表的枪按类借用 [推断]：横向 = 总横向 × smoothstep(clamp01((zf − a) / (b − a)))。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 视线中心总移动：前 / 横 / 上 | −0.0137 / 0.0800 / 0.0229 m | −0.54 / 3.15 / +0.90 u | −0.0075 / 0.0438 / 0.0125 H | Spitfire 横 3.97 u，Wingman 2.69 u | [实测] ADS §2.3 |
| R-301 开镜下沉最多 / 枪口下压 | −0.0348 m / — | −1.37 u / −3.52 ° | −0.019 H | Spitfire 2.08 u，Wingman 1.06 u | [实测] |
| 横向过冲 R-301 / Spitfire / Wingman | — | 15 % / 18 % / 无 | — | — | [实测] |
| 开镜横向窗口 a..b（R-301 / Spitfire / Wingman） | — | 0.05..0.28 / 0.03..0.23 / 0.05..0.53 | — | 步枪、机枪 0.05..0.25；手枪 0.05..0.53 [推断] | [实测] |
| 关镜横向窗口 | — | 0.19..0.83 / 0.26..0.80 / 0.00..0.32 | — | 步枪 0.20..0.80 [推断] | [实测] |
| R-301 程序偏移 前、上：腰射 → 开镜 | −0.0229, 0.0102 → −0.0411, 0 m | −0.90, 0.40 → −1.62, 0 u | — | RMS 0.0006 u | [实测] |
| R-301 枪就位 / FOV 到位 | — | 约 0.135 s / 0.27 s | — | — | [算] |

#### 实现模板

```
// 单位：u、°
pose(gun, zf, goingIn):
    curve = table(gun) ?? borrowByClass(gun.class)          // ads-curves.tsv
    row   = lerp(curve[goingIn ? "in" : "out"], zf)          // 已含程序偏移
    return hip + row.(dF, dR, dU), rot(row.dPitch, row.dYaw)
```

Unity 参考实现：`AdsCurves.GunPose(curve, goingIn, zoom, hip, aim, …)`、`AdsCurves.CurveOf(id, class)`（`AdsCurves.cs`，U#63）。开镜锚点（每把枪的 R5 开镜位置）在 `HeldModels.cs` / `GunAimData.gen.cs`（U#68，D-104：每把枪开镜稳定后的枪口和俯仰按 IS-GUNS，不再按枪类常数；开关 `arsenal.aimPoseR5`）。

#### 验收

- `CombatWeaponTests.TheGunSwingsInSinkingAndOvershootingAndEndsOnTheAnchors`、`ComingOutIsNotGoingInBackwards`、`EveryGunHasAnAimingPath`。
- `CombatHeldModelTests.AimedTheMuzzleIsTheMeasuredOneAndNothingElseMoves`、`TheLineOfSightRunsThroughTheRearSightToTheScreensCentre`。
- 合格线：三把实测枪逐 0.05 zf 对 `ads-curves.tsv` 差 ≤ 0.05 u；开镜到位时视线中心在镜头轴上（R5 实测 0.00–0.02 u）。

#### 出处

- ADS §2、§4.3；`ADS-CURVES.tsv`。PR #93，还没合并
- DP §6.4 第 3–5 条。PR #122，还没合并
- IS §1–§2（开镜枪口每把枪）、`data/IS-GUNS.tsv`。PR #99，还没合并
- D-89、D-104。#91 / #100，还没合并
- [反编译] `CalcViewModelView` 0x14085c3e0；动画 0x14085ab80、0x14085a3c0。

### 3.5 装瞄具：枪往前推

#### 原理

装上瞄具开镜时，对准眼睛的不再是机瞄，而是**瞄具自己的挂点**——枪被整体往前推（R-301 装 3x，枪口从 31.5 u 推到 41.6 u）。同时枪模 FOV 收窄（§3.3）。**这两件事是配对的**：瞄具把枪推远，同时收窄 FOV，屏幕上瞄具的大小才对。只改 FOV 不推，3x 和 2–4x 会大 2 倍。

#### 规则和公式

1. 字段 `viewmodel_offset_ads_by_centerpoint` = 1：把 `viewmodel_ads_centerpoint_attachment` 放到镜头前 `(offset_ads 第二项 − 2, 第一项, 第三项)`。
2. 腰射位置不变（七种状态枪口差不到 0.02 u）。
3. 过渡用瞄具自己的 `ads_fov_zoomfrac_*`、`viewmodel_offset_zoom_frac_*`、`zoom_time_in/out`。
4. 机瞄折下（bodygroup），逐把见 IS `IS-GUNS.tsv` 的 `optics` 列（G7 后瞄不折）。
5. 狙击镜（`optic_sniper*`、Kraber 默认镜）整屏镜内画面，看不到枪，不用模型凑。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 机瞄：挂点离眼 / 开镜枪口 F | 0.660 / 0.801 m | 25.99 / 31.53 u | 0.361 / 0.438 H | — | [实测] IS |
| 1x HCOG | 0.279 / 0.816 m | 11.0 / 32.11 u | 0.153 / 0.446 H | — | [实测] |
| 3x | 0.508 / 1.057 m | 20.0 / 41.60 u | 0.278 / 0.578 H | Sentinel 3x 对到 0.01 u | [实测] |
| 2–4x | 0.508 / 1.070 m | 20.0 / 42.14 u | 0.278 / 0.585 H | — | [实测] |
| 1x 全息 | 0.648 / 1.113 m | 25.5 / 43.83 u | 0.354 / 0.609 H | — | [实测] |
| 挂点处屏幕大小（R5 / 只改 FOV 不推） 3x | — | 244 / 492 px/u | — | 2–4x 253 / 540 | [实测] [算] |

#### 实现模板

Unity 参考实现：`GunOpticView.cs`（U#69），D-126：枪模 FOV 用瞄具的 `zoom_fov_viewmodel`（交给 `GunSights.GunFov`），挂点放在 `(offset_ads[1] − 2, offset_ads[0], offset_ads[2])`；其他枪的挂点位置是 [推断]（前后按 R-301 相对机瞄点平移，高度用 R-301 和 Sentinel 拟合：每高 1 u 机瞄，挂点高 0.26 u）。

#### 验收

- `GunPageTests.TheOpticViewFollowsItsSwitchAndLeavesTheHipAlone`、`EveryOpticOnEveryGunHasAPlaceExceptScopes`、`TheInferredPlaceLandsOnTheSentinelsMeasuredPose`、`AScopeKeepsTheIronPoseAndTheHipFov`、`TheKraberKeepsItsOwnScope`。
- 合格线：R-301 六种瞄具的 FOV 和枪口位置对 IS `IS-OPTIC-FOV.tsv` 差 ≤ 0.02 u、3 %。

#### 出处

- IS "装瞄具时的枪"一节、`data/IS-OPTICS.tsv`、`IS-OPTIC-FOV.tsv`。PR #99，还没合并
- D-120（配对规则）在 #99；D-126（Unity 采用）在 #101 / #104。还没合并

### 3.6 开镜灵敏度

#### 原理

开镜时鼠标慢下来，慢多少正好等于画面放大多少，所以**屏幕上的视觉转速基本不变**。关镜一松手灵敏度立刻恢复，而 FOV 还要 0.15–0.55 s 才回去——这段时间屏幕上转得比平时快（R-301 约 1.4 倍），是 R5 的原样，不是 bug。

#### 规则和公式

1. 按住开镜期间：每条命令的鼠标增量 × `tan(FOV/2) / tan(R基础/2)`，用**上一帧**的世界 FOV（§3.2）。
2. 松开开镜的下一帧（约 7 ms）：× 1，不管 zf 和 FOV 还在哪。开镜开到一半松开也一样。
3. 开镜头几帧倍率还是 1：FOV 的 smoothstep 在窗口起点之前不动，倍率跟 FOV，不跟 zf。
4. `mouse_use_per_scope_sensitivity_scalars` 本地是 0（没走分镜灵敏度）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 机瞄到位 | — | × 0.711（预测 0.7106） | — | — | [实测] EM §2 |
| R-301 + 3x HCOG 到位 | — | × 0.305（预测 0.3050） | — | — | [实测] |
| 开镜过程中逐帧 | — | = 上一帧 FOV 的 tan 比（207 帧中位误差 0） | — | — | [实测] |
| 关镜后第一帧 | — | × 1.000（zf 0.968–0.975 时） | — | — | [实测] |

#### 实现模板

```
mouseScale = adsHeld ? tan(fovPrev/2) / tan(fovBase/2) : 1
```

Unity 参考实现：`CombatSim.AdsTurnScale`（`CombatSim.Items.cs`）= `input.ads ? ViewFovRatio : 1`，在 `PracticeGame.cs` 的鼠标处理里乘上。**和 R5 的小差别**：Unity 用当前帧的 FOV 比例，R5 用上一帧（差 1 帧，没登记成 DIFF）。

#### 验收

- `CombatWeaponTests.TheZoomAndTheSlowerMouseStayBehindTheirSwitchAndOnlyOnAGun`。
- 合格线：到位倍率和 tan 比差 ≤ 0.002；松开后下一条命令倍率 = 1。

#### 出处

- EM §2（A2）。PR #122，还没合并
- ADS §3、§4.4（当时只有反编译）。PR #93，还没合并
- DP §6.4 第 6 条（#122 版）。PR #122，还没合并
- [反编译] 0x1408372b0、0x140906d10；另一个条件 0x1407f9510。

### 3.7 开镜漂移 `ads_drift`

#### 原理

开镜时准星会极慢地漂（像呼吸），而且**漂移进子弹**——开镜到位、fraction 0 的枪，子弹仍然永远打在屏幕中心。蹲下漂得更少，空中更多：又是一条"站稳了才准"的价格（P6）。

#### 规则和公式

1. 只在开镜时有（腰射 0）；幅度按姿态缩放（字段，R-301：站 0.5 / 0.4，蹲 0.3 / 0.25，空中 0.6 / 0.8）。
2. 进画面，也进子弹（FG §5.2：Wingman 第 3、4 发偏高 0.35–0.52° 就是 drift）。
3. **公式没读**，只有字段和 R-301 的幅度。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 开镜漂移最大 俯仰 / 偏航 | — | 0.29 / 0.21 °（±0.3 °） | — | 和开枪无关 | [实测] RV §1.1 |
| 姿态缩放（R-301 站 / 蹲 / 空中） | — | 0.5, 0.4 / 0.3, 0.25 / 0.6, 0.8 | — | — | [数据] |
| 子弹里的 drift（Wingman，间隔 0.4 s） | — | +0.35 … +0.52 ° | — | 间隔 0.8 s 时 −0.2 … −0.5 ° | [实测] FG §5.2 |

#### 实现模板

Unity 参考实现：**没有做**（RV §10.4"还没做：开镜漂移，只有字段，公式没读"）。站立漂移（不开镜）在原生镜头里有（[07 §3.3](07-camera.md)）。做的话要先读 drift 公式（R5 原生有 40 个 drift 参数），或者先用 [设计]：两条正弦，幅度对上表，进子弹。

#### 验收

- 建议：开镜站立 5 s，画面角最大偏离俯仰 0.29 ± 0.05 °、偏航 0.21 ± 0.05 °；开镜单发间隔 0.4 s，子弹 − punch2 = 当时的 drift（差 ≤ 0.02 °）。

#### 出处

- RV §1.1、§6.2 第 7 条。PR #93，还没合并
- FG §5.2。PR #122，还没合并
- DP P6（drift 缩放字段）。PR #122，还没合并

---

## 4. 枪的重量（P5）

### 4.1 重量轴：所有"操作这把枪"的时间一起变

#### 原理

玩家不读数字也能感到枪的轻重，因为**所有和操作这把枪有关的时间一起变**：开镜时间、掏枪收枪、从冲刺到开火、开镜时走路多慢。手枪全部快，狙击全部慢，步枪、机枪、SMG 各自是一组几乎相同的值。设计新枪时先选重量类，再直接取类值（DP §9.3）。换弹**不在**这条轴上。

#### 规则和公式

1. 一把枪的重量类决定这几个字段：`zoom_time_in / out`、`deploy_time`、`holster_time`、`raise_time`、`lower_time`、`ads_move_speed_scale`。
2. 29 把枪的秩相关：zoom in 和 deploy 0.84，zoom in 和开镜移速 −0.72，deploy 和 holster 0.87，deploy 和 raise 0.93 [算]。
3. 瞄具、枪托改这些时间（按比例乘，T4）：枪托 L1 `zoom_time` × 0.85、`deploy` × 0.85、`raise` × 0.9。

| 类 | zoom in / out [s] | deploy [s] | 开镜移速 [×] | 换弹 [s] | 依据 |
|---|---|---|---|---|---|
| 手枪 | 0.18 / 0.16 | 0.225–0.4 | 1.0 | 1.25–2.1 | [数据] DP P5 |
| 霰弹 | 0.20–0.22 / 0.18–0.20 | 0.25–0.5 | 0.9–1.0 | 0.9–2.5 | [数据] |
| SMG | 0.20–0.22 / 0.20 | 0.35–0.4 | 0.75 | 1.7–2.0 | [数据] |
| 步枪 | 0.27 / 0.23 | 0.6 | 0.5 | 2.4–3.2 | [数据] |
| 精确 | 0.30–0.50 / 0.25–0.50 | 0.6–1.0 | 0.425–0.85 | 0.33–2.6 | [数据] |
| 机枪 | 0.34 / 0.30 | 0.8 | 0.4 | 3.1–3.4 | [数据] |
| 狙击 | 0.20–0.58 / 0.15–0.55 | 0.7–1.2 | 0.35 | 2.66–3.5 | [数据] |

**反例**（照写，做新枪时可以借）：Charge Rifle 开镜 0.20 s 却切枪 0.8 s、开镜移速 0.35（身份像狙击，开镜很快）；Bocek 开镜 0.5 / 0.5 却开镜移速 0.85。

每把枪的全部字段在 [gun-weight.tsv](09-combat-feel/gun-weight.tsv)。

#### 实现模板

无单独实现：都是字段（`WeaponData.gen.cs`），各功能读自己那个（开镜 §3.1、切枪 §7.4、移速 §4.2、举枪 §4.3）。

#### 验收

- `CombatWeaponTests.TheTableHoldsEveryKeptGunWithItsSource`（字段和来源）、`GunPageTests.AnOpticGoesOnBeforeTheStockScalesItsTimes`、`GunPageTests.SheetRowsAreRealNumbersOnEveryGun`。
- 合格线：字段逐位等于 R5 读回值（RV §10.2：生成表 + 缺省值对运行时读回 775 项，只差 Sheila 的 `LerpEnd`）。

#### 出处

- DP P5、§9.3（#122 版）。PR #122，还没合并
- `research/design-philosophy/WEAPON-FIELDS.md`（字段表和秩相关的脚本）。main
- GM `GUN-VARS.tsv`。PR #95，还没合并

### 4.2 移动速度

#### 原理

开镜时走路变慢，慢多少看枪：手枪不慢，机枪、狙击慢到 0.35–0.4。**开火本身不减速，换弹不减速**——"动起来可以打"（P6），价格在扩散和开镜移速里，不在"开枪就停"。

#### 规则和公式

1. 开镜时移动速度上限 × lerp(1, `ads_move_speed_scale`, zf)。**插值形状没测**（只测了两端），线性是 [推断]。
2. 开火、换弹不改移动速度。
3. 冲刺中按开火 = 结束冲刺（第一发时速度已经从 260 降到 174 u/s）。
4. 消耗品读条、`move_slow` 在 10 章。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 拿枪走路（R-301 / Wingman） | 4.407 m/s | 173.5 u/s | 2.410 H/s | — | [实测] B-STATES §5 |
| R-301 开镜走（× 0.5） | 2.203 m/s | 86.75 u/s | 1.205 H/s | — | [实测] |
| Spitfire 开镜走（× 0.4） | 1.763 m/s | 69.4 u/s | 0.964 H/s | — | [实测] |
| Wingman 开镜走（× 1.0） | 4.407 m/s | 173.5 u/s | 2.410 H/s | — | [实测] |
| 换弹时走 / 冲刺 | 4.407 / 6.604 m/s | 173.5 / 260 u/s | 2.410 / 3.611 H/s | 和不换弹一样 | [实测] C-MOTIONS 结论 5 |
| 开火时走 | 4.407 m/s | 173.5 u/s | 2.410 H/s | 不额外减速 | [实测] |

#### 实现模板

Unity 参考实现：开镜移速通过移动的 port 传给马达（`CombatWeaponTests.AimedMoveScaleGoesThroughThePortAndHipLeavesItAlone` 测的路径；`ArsenalWeapon.cs`）。

#### 验收

- `CombatWeaponTests.AimedMoveScaleGoesThroughThePortAndHipLeavesItAlone`、`CombatReloadSwapTests.SprintAndJumpDoNotBreakAReload`。
- 合格线：开镜到位走速 = 173.5 × `ads_move_speed_scale` ± 0.5 u/s。

#### 出处

- GM `B-STATES.md` §5、结论 8；`C-MOTIONS.md` 结论 5；`report/03-ads-optics.md` §1。PR #95，还没合并
- DP P5、P6。PR #122，还没合并

### 4.3 转向

#### 原理

R5 **没有按枪限制转向速度**：拿 Kraber 和拿 P2020，鼠标转一样快。开镜时转得慢，唯一来源是灵敏度按 FOV 缩放（§3.6），而那是为了让屏幕上的视觉速度不变，不是"重"。所以"重枪转得慢"这种感觉，在 R5 里是**枪模**做出来的（转身时枪的滞后和摆动，08 章），不是瞄准。

#### 规则和公式

1. 瞄准角速度 = 鼠标 × 灵敏度 × 开镜倍率（§3.6），不乘任何枪的系数。
2. 枪模随转身的滞后 / 摆动：08 章（HOLD-POSE §7：R-301 转视角超前 2.44°）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 按枪的转向限制 | — | 没有找到 | — | 只查了字段和开镜灵敏度 | [推断] |
| 开镜转向倍率 | — | tan 比（R-301 0.711） | — | 见 §3.6 | [实测] |

**说明**：研究里没有专门测"不同枪的最大转速"，这条是从"字段里没有转向相关的键"和 EM §2 推出来的，写成 [推断]，已列入 §9。TF2X 的电弧星"转向 × 0.3"是道具效果（`CombatSim.TurnScale`），不是枪的重量。

#### 实现模板

无（不做）。

#### 验收

无（没有规则要测；如果以后加了按枪的转向限制，要写成偏离）。

#### 出处

- EM §2。PR #122，还没合并
- `research/combat/gun-measure/hold-pose/HOLD-POSE.md` §7（转视角时枪的超前）。PR #95，还没合并（08 章引用）
- DP P5（重量轴里没有转向）。PR #122，还没合并

### 4.4 举枪时间：冲刺、滑铲、滑索、钩爪、翻越到开火

#### 原理

动起来可以打，但**从"不在打"的状态切到"打"要付时间**，付多少看枪的重量和你在做什么。冲刺到开火 0.14–0.25 s（手枪快、步枪狙击慢）；滑铲几乎不付（0.013 s，和站着一样）——R5 鼓励滑铲中开枪。

#### 规则和公式

| 从 → 开火 | R-301 | Wingman | P2020 | EVA-8 | Mastiff | 依据 |
|---|---|---|---|---|---|---|
| 站立（基础延迟，约一帧半） | 0.013 s | 0.012 s | 0.013 s | 0.013 s | 0.012 s | [实测] C-RAISE2 |
| 冲刺（速度 260） | 0.249 s | 0.180 s | 0.138 s | 0.151 s | 0.145 s | [实测] |
| 滑铲 | 0.013 s | 0.012 s | 0.013 s | 0.013 s | 0.012 s | [实测] |
| 冲刺跳 | 0.141 s | 0.072 s | | | | [实测] B-STATES §4 |
| 刚上滑索 | 0.399 s | 0.523 s | | | | [实测] |
| 钩爪拉动中 | 不能开火；拉完 0.44–0.48 s 才出第一发 | | | | | [实测] FG §8.1 |
| 爬墙段 / 翻墙顶段 | 不能开火 / 进入后 0.15–0.19 s 恢复 | | | | | [实测] FG §8.2 |

1. 冲刺到开火的上限约 0.25 s，R-301、R-99、Spitfire、Kraber 都是 0.249 s——**不和 `raise_time` 成比例**（R-301 0.5、P2020 0.225），`raise_from_sprint_time` 是 0。**0.25 s 上限来自哪里没查。**
2. 冲刺中按开火立刻结束冲刺。冲刺中开镜也结束冲刺，开镜 0.02 s 内开始。
3. 全部 8 把的中位数在 [gun-weight.tsv](09-combat-feel/gun-weight.tsv) 的 `sprint_to_fire`、`slide_to_fire`、`stand_to_fire` 列。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺到开火 | — | 0.138–0.249 s | — | 8 把 × 3 次 | [实测] |
| 冲刺到开火时的速度 | 6.604 → 4.420 m/s | 260 → 174 u/s | 3.611 → 2.417 H/s | — | [实测] |

#### 实现模板

```
onFirePressed():
    if sprinting: endSprint(); fireBlockedUntil = now + sprintToFire(gun)   // 表，按枪
    if grappling or climbing: block
```

Unity 参考实现：**冲刺到开火没有做**（GM INDEX "Unity 该改什么"第 4 条；`ArsenalWeapon.cs` 的 `sprinting` 只用于扩散，`FiringCycle.cs` 没有冲刺延迟）。钩爪、爬墙挡开火也没查到实现。

#### 验收

- 建议：冲刺中按开火，第一发时间对 `gun-weight.tsv` 差 ≤ 1 命令；滑铲中按开火 ≤ 2 命令。

#### 出处

- GM `C-MOTIONS.md` §7、`C-RAISE2.tsv`、`B-STATES.md` §4。PR #95，还没合并
- FG §8.1–8.2。PR #122，还没合并
- DP P6、§7.8。PR #122，还没合并

---

## 5. 扩散

### 5.1 腰射扩散：姿态基础 + 累计 kick

#### 原理

腰射子弹在一个圆锥里随机，圆锥大小 = **姿态的基础值**（蹲 ≤ 站 ≤ 走 ≤ 冲刺 ≤ 空中）+ **连射累积**。动起来可以打，但精度代价查表，每一格都清楚（P6）。开镜在地上步枪扩散 0：开镜是"付了开镜时间和移速换来的准"。两个容易忽略的规律：

- 基础值**按速度过渡**，不是马上到：刚起步就开枪比走了一阵再开枪准。
- **回落速度**比基础值更影响"点射准不准"：R-301 停火 0.25 s 后约 0.02 s 恢复，R-99 要慢得多。

霰弹不吃扩散（§5.3）。

#### 规则和公式

```
每条命令：
  目标基础 = spread_<姿态>_hip（站且冲刺用 _sprint，站且移动用 _run，跑墙用 spread_wallrunning）
             再按 zf 插值到 spread_<姿态>_ads
  基础值 以 spread_moving_increase_rate 升向目标，或以 spread_moving_decay_rate 降向目标（°/s；没写 = 立刻到）
  若 现在 − 上一发 > spread_decay_delay：累计 kick 以 spread_decay_rate 回落到 0（°/s）
开火：
  子弹方向在 (基础值 + kick) 的圆锥内（分布见 §5.2）
  kick += spread_kick_on_fire_<姿态>_<hip|ads>，不超过 spread_max_kick_<姿态>_<hip|ads>
姿态 = 空中 / 蹲 / 站
```

1. 角度单位度，是引擎读回的 `GetAttackSpreadAngle`；**这个角是锥的全角还是半角**，R5 的读数说明是"从锥的一边到另一边的度数"（TF2 同名函数，N3 §3），所以子弹最远偏离 = 角度的一半 [推断，R5 本身没测落点]。
2. 第一次拿到的枪扩散从接近 0 开始，按基础上升速度爬到站立值（R-301 约 1 s）[实测]；这段时间开枪是否真的更准没测。
3. 落地头 0.05 s 内开枪，扩散还是空中值（FG §1.2）。

R-301（全部枪见 [spread.tsv](09-combat-feel/spread.tsv)）：

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 腰射 站 / 走 / 冲刺 / 蹲 / 空中 | — | 3 / 6.6 / 8.4 / 2.4 / 8.4 ° | — | 站腰全枪 2–5.6（狙击 8） | [数据] [实测] GM 06 卷 |
| 每发累计 / 上限 站 · 蹲 · 空中 | — | +0.2 ° / 2 · 1.5 · 3 ° | — | 每发 0.15–2.5，上限 1.5–12 | [数据] [实测] |
| 回落 等待 / 速率 | — | 0.25 s / 100 °/s | — | R-99 0.15 s / 12 °/s，Kraber 0.1 s / 4 °/s | [数据] [实测] |
| 基础值 上升 / 下降 | — | 3 / 30 °/s | — | 实测 3.0 / 26–30 | [数据] [实测] |
| 开镜 站 / 蹲 / 空中 | — | 0 / 0 / 6 ° | — | SMG 地面 0.35；手枪空中 2 | [数据] [实测] |
| 连射 10 发站立 | — | 3.0 → 5.0 °，停火 0.25 s 后约 0.02 s 回到 3.0 | — | — | [实测] |
| 滑索开镜 | — | 5.8–6.0 °（不降到开镜值） | — | Wingman 2.0 | [实测] B-STATES §1 |

#### 实现模板

Unity 参考实现：`SpreadRecoil.cs`（`SpreadState.Target`、`Step`、`OnFired`、`Angle`；姿态 `WeaponPose`，U#60）。

#### 验收

- `CombatWeaponTests.SpreadKickFallsAfterTheDelay`、`CombatWeaponTests.TheConeStaysInsideItsAngle`。
- 对照：GM 06 卷 §2 的开火表（R-301、Flatline、Spitfire、Wingman、P2020 各姿态"第一发前 / 每发加 / 最高 / 回落"）。
- 合格线：每发加量和上限逐位；回落时间差 ≤ 0.03 s。已知没解释：Wingman 冲刺这一格上升 1.15 °/s（字段 5.5）。

#### 出处

- GM `report/06-hipfire-spread.md` §1–§4、§6；`B-STATES.md` §1。PR #95，还没合并
- DP P6、§7.4。PR #122，还没合并
- FG §1.2（落地头 0.05 s）。PR #122，还没合并

### 5.2 圆锥里怎么散（分布）

#### 原理

圆锥多大定了，子弹在里面怎么落——均匀、偏中心还是别的——决定了"扩散 5°"打起来是什么感觉。**R5 的腰射落点分布没测到**（腰射命中点一次都没记）。TF2 的脚本散布函数是读到的：每轴两个均匀之和（三角分布），偏中心。HSD 现在用均匀圆盘，是猜的。

#### 规则和公式

三个版本，都写：

| 版本 | 规则 | 半径分布（单位：最大偏离） | 依据 |
|---|---|---|---|
| **TF2 脚本**（`ApplyVectorSpread`） | s = sin(角/2)；x = 0.5·U(−1,1) + 0.5·U(−1,1)，y 同理，重抽直到 x² + y² ≤ 1；dir += right·x·s + up·y·s | 中位数 0.50、平均 0.51、90 % 0.83、99 % 0.97 | [TF2 数据] N3 §3（脚本；即时命中子弹在引擎里，脚本注释说同一算法 [推断]） |
| **HSD 现在** | 圆盘内均匀：r = tan(角) × √U，方向均匀 | 中位数 0.71 | [设计]（代码注释 `[guess]`） |
| R5 | 不知道 | — | 没测（GM 06 卷 §8 写了怎么补） |

注意 HSD 现在用 `tan(角)` 当半径，等于把读数当**半角**；TF2 是 sin(角/2)，当**全角**。两者对同一个读数差约 2 倍——**这是一个可能的单位错误，没核对**，写进 `_notes`。

#### 实现模板

Unity 参考实现：`SpreadState.Cone(dir, degrees, rng)`（`SpreadRecoil.cs`，U#60）。

#### 验收

- `CombatWeaponTests.TheConeStaysInsideItsAngle`（只测不出界）。
- 分布本身没有合格线，等 R5 实测（§9）。

#### 出处

- N3 §3。PR #115，还没合并
- GM `report/06-hipfire-spread.md` 开头和 §8。PR #95，还没合并
- DP P7 反例（"腰射子弹在扩散圆内纯随机，这部分练不了"）。PR #122，还没合并

### 5.3 霰弹：固定图案 + 每颗弹丸的随机区域（D-137 默认，D-129 留开关）

#### 原理

R5 的霰弹**不随机**：每发按固定图案打，三发落点相同；所有姿态散布一样（近距离枪是给移动用的，P6 最大的例外）。用户 11-07 要随机，但不要"整个图案乱转"那种；选了守望先锋式的做法：**弹丸数和图案不变，每颗弹丸在自己的小圆盘里随机**，圆盘互不重叠，所以每颗弹丸始终在图案里自己的位置上，图案仍然可读、可学。**这是 HSD 有意偏离 R5。**

#### 规则和公式

1. **R5**：图案表（`blast_patterns.txt`）× 比例（开镜比例另有），`ignoreSpread`，没有随机。每颗弹丸各算伤害，**没有部位倍率**（头腿一样）。
2. **D-137（HSD 默认）**：图案不转。每颗弹丸 i 的区域 = 以图案点为圆心、半径 r_i = 0.45 × (i 到最近另一颗的距离) 的圆盘；每发在圆盘里取均匀随机点。相邻两颗半径和 ≤ 距离 × 0.9 → 区域互不重叠。半径在图案自己的单位里，所以开镜收紧和精准收束器一起缩小。
3. **D-129（开关）**：整个图案绕瞄准方向随机转 ±10°，每颗弹丸再在半径 0.10 × 最外弹丸偏移的圆盘里抖动。
4. 霰弹的随机用单独的随机数发生器，不影响后坐随机。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 弹丸数 EVA-8 / Peacekeeper / Mastiff / Mozambique / Triple Take | — | 8 / 9 / 5 / 3 / 3 | — | — | [实测] SR §2 |
| EVA-8 图案（表单位） | — | (±7, ±7)、(0, ±11)、(±3.5, 0)，× 1.4 | — | 单位和比例没验证 | [数据] GM 06 卷 §5 |
| 霰弹扩散读数（所有姿态） | — | EVA 1.2、PK 2.8、Mozambique 2、Mastiff 0 ° | — | 读回 0（由图案决定） | [数据] [实测] |
| Mastiff 开镜收拢 / EVA 最外 | — | 1.45 ° / 1.72 ° | — | — | [实测] DP §7.7 |
| Peacekeeper 收束器 蓄满 | — | 半径 1.28 → 0.72 °，0.9 s 到 4 级 | — | — | [实测] |
| **D-137** 区域系数 | — | 0.45 × 最近邻距离 | — | 0.3–0.5 合计命中几乎不变 | [设计] |
| D-137 腰射 300 u 区域半径 EVA / PK / Mastiff / Mozambique | 0.066–0.076 / 0.066–0.079 / 0.056 / 0.081–0.086 m | 2.6–3.0 / 2.6–3.1 / 2.2 / 3.2–3.4 u | — | 角度 0.49–0.57 / 0.50–0.59 / 0.42 / 0.60–0.65 ° | [设计] [算] |
| D-129 转角 / 抖动 | — | ±10 ° / 0.10 × 最外偏移 | — | 抖动 0.17–0.22 ° | [设计] |

命中变化（32 × 72 u 的身体，瞄中间，400 发平均，300–1500 u 合计，固定 → D-137）：EVA 32 → 31.5、PK 33 → 35.2、Mastiff 14 → 15.2、Mozambique 16 → 15.6；600 u 内最多少 0.63 颗（PK 9 → 8.37）。逐距离表在 SR §7。

#### 实现模板

```
// 单位：图案自己的单位（× 比例后才是角度）
pellets(pattern, scale, rng):
    for i, p in pattern:
        r  = 0.45 * nearestDistance(p, pattern)
        q  = p + uniformDisk(r, rng)             // D-137；关掉 = q = p（R5）
        yield aimDir + toAngles(q * scale)
```

Unity 参考实现：`SpreadRecoil.cs` `ShotPattern`（图案和 `Basis`，U#60），D-137 / D-129 的区域在 U#71（分支 `combat/wp5-shotgun-reticle`，`ShotgunReticle.cs` 同 PR）。开关：`arsenal.shotgunPatternRandom`（关 = R5 固定图案）、`arsenal.shotgunScatterD129`（开 = 回到 D-129）。

#### 验收

- `ShotgunScatterTests.OnEveryShotDiffersAndEachPelletStaysInItsRegion`、`RegionsDoNotOverlapAndAreFilled`、`ScatterShrinksWithThePattern`、`AveragePelletsOnABodyBarelyChange`、`DotsSitOnTheRandomHits`。
- `CombatWeaponTests.EvaLandsAllPelletsCloseAndEachTakesItsOwnDamage`、`TripleTakePatternFollowsTheSpreadAndChokeNarrowsThePeacekeeper`。
- 合格线：关掉随机时和 R5 固定图案差 ≤ 0.006°；合计命中不少于固定图案的九成；区域两两不重叠。

#### 出处

- SR §6（D-129）、§7（D-137）、`scatter/SCATTER-300U.tsv`。PR #103，还没合并
- GM `report/06-hipfire-spread.md` §5；DP §7.7。PR #95 / #122，还没合并
- D-129（平行版，开关）、D-137（默认）——**有意偏离 R5**，在 #104。还没合并
- IP2 §2.11（三发 EVA 落点相同）。PR #92，还没合并

---

## 6. 准星和命中反馈

### 6.1 准星：画在哪、张多大、什么形状

#### 原理

准星告诉你**下一发**会去哪：位置跟着 (1 − f)·punch，张开量跟着当前扩散。每把枪有自己的准星形状（31 把用了 9 种），霰弹的准星就是弹丸图案的样子。开镜到底准星消失（换成瞄具）。玩家枪**没有**"瞄到敌人变红"。

#### 规则和公式

1. 位置 = 画面中心 = aim + (1 − f)·punch2 + punch1（腰射残差 0.000°，RV §1.1）。
2. 张开量 = 当前扩散 + 每槽 `base_spread`，再按 FOV 换成像素。**普通准星的像素公式没定**（推断 `间隙 px = tan(spread + base_spread) / tan(FOV/2) × 半屏高`，UI W-02，要截图）。
3. **霰弹准星（D-128，实测）**：EVA-8 / Peacekeeper 是四段**固定大小**的小弧（半径约 9.8 px、约 100°、线宽 3 px）被推远：弧中点 = G(FOV) × (散布 + base_spread + 0.94)；Mastiff 一根带刻度的横杠、Mozambique 三根短线，按 FOV 查表。G 不按角度走，**直接查表插值**。
4. 开镜按 zf 淡掉 [推断]；冲刺透明度约 0.4 [截图估计]；Peacekeeper 收束器 2 级起弧变青、弧心 × 收束系数 [推断，一个点]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 霰弹弧中点 G（900 高，FOV 70 / 89 / 112） | — | 20.38 / 11.27 / 8.77 px/° | — | FOV 70–112 七个点 | [实测] SR §3.1 |
| 弧中点 EVA / PK（FOV 89） | — | 35.4 / 42.3 px | — | — | [实测] |
| Mastiff 横杠外端（FOV 89） | — | 45 px | — | 70 → 58，112 → 36 | [实测] |
| 准星形状种类 | — | 9 种（三角、十字、十字加点、Alternator、霰弹、Mastiff、Charge Rifle、L-STAR、Bocek） | — | 逐把在 UI `data/ui-crosshair.tsv` | [数据] UI W-01 |
| 瞄到敌人变红 `red_crosshair_range` | — | 0（所有玩家枪） | — | — | [数据] |

#### 实现模板

Unity 参考实现：普通准星 `ArsenalHud.cs`（U#60，IMGUI 占位）；霰弹准星 `ShotgunReticle.cs`（`ShotgunReticle`，U#71），G 表照 SR §3.1。HSD 默认竖直 70° = R5 FOV 86，所以默认下霰弹准星比 R5 默认（89）略大，按表就是这样。

#### 验收

- `ShotgunReticleTests`（类里 4 个测试，见 §6.2）；准星大小：构建里 `HSD-Practice.exe -reticleShots <目录> [-reticleFov 89]` 拍图对 SR 的截图。
- 合格线：FOV 89 时 EVA 弧中点 35.4 ± 1 px（1600×900）。

#### 出处

- SR §1、§3、§4。PR #103，还没合并
- UI W-01 – W-03。PR #102，还没合并
- RV §1.1（准星位置）。PR #93，还没合并
- D-128（选中：按 R5 实测做；其他枪仍是"+"）。#104，还没合并

### 6.2 命中反馈：命中 X、霰弹弹丸点、伤害数字

#### 原理

打中了要立刻知道，而且知道**打中几颗**。R5 的命中反馈全是界面层的（X、点、数字、声音），**不动镜头**。霰弹最直观：每颗打中的弹丸在命中位置留一个红点（爆头黄），点钉在屏幕上不跟世界走，0.75 s 消失——你能一眼看到上一发中了几颗。

#### 规则和公式

1. **霰弹弹丸点（实测，D-128）**：一发不止一颗弹丸的武器（`projectiles_per_shot` > 1：EVA 8、PK 9、Mastiff 5、Mozambique 3、Triple Take 3），**每颗打中的弹丸**一个实心点：普通红 (237, 1, 1) 约 6 px，爆头黄 (237, 237, 1) 约 8 px（1600×900）；0–0.45 s 满色，0.45–0.75 s **线性光里线性淡出**，0.75 s 消失；命中那一帧按命中点的屏幕位置放下，之后**不跟世界**（转 4° 世界移了 43 px，点不动）；大小不随距离；开镜照画；护盾、击杀不改颜色。
2. **命中 X**（脚本，没截图）：一个常驻 RUI，每次命中重启，不叠加；类型优先级 影子 > 超护盾 > 护盾 > 暴击 > 无效距离 > 护甲 > 枪盾 > 普通；击杀和击倒共用一个变体。**时长、大小、颜色没量**（UI H-01）。射击场默认关。
3. **伤害数字**（脚本）：默认累加式：距上一次命中 ≤ 0.25 s 加到同一个数，每次命中重启 1.0 s。
4. **命中声音**：普通 / 暴击 / 爆头 / 击杀各一个（UI H-02），音效本身没研究。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 弹丸点 满色 / 消失 | — | 0.45 s / 0.75 s（`RuiIsAlive` 0.766–0.771 s） | — | — | [实测] SR §2 |
| 弹丸点 淡出曲线（线性光强度，0.55 / 0.6 / 0.65 / 0.7 s） | — | 0.67 / 0.51 / 0.35 / 0.17 | — | 理论 0.667 / 0.5 / 0.333 / 0.167 | [实测] |
| 弹丸点 出现 | — | 5 ms 起满色满大小，没有放大动画 | — | — | [实测] |
| 伤害数字 累加窗口 / 停留 | — | 0.25 s / 1.0 s | — | — | [数据] UI H-05（脚本常数） |
| 命中 X 时长 / 大小 / 颜色 | — | 没量 | — | — | — |

#### 实现模板

Unity 参考实现：弹丸点 `ShotgunReticle.cs` `PelletDot`（U#71）；通用命中 X 和伤害数字是 IMGUI 占位（`HSD-Unity: Assets/HSD/Game/Runtime/Combat/CombatHud.cs`、`CombatCore.cs`，main）：X 0.15 s、击杀变红，上飘的伤害数字——**都是 HSD 自己的，不是 R5**（UI §6）。

#### 验收

- `ShotgunReticleTests.DotsHoldThenFadeInLinearLight`、`EveryEvaPelletThatHitsLeavesADotAndNothingElseChanges`、`SingleRoundGunsLeaveNoDots`、`MastiffPelletsThatMissLeaveNoDot`。
- 合格线：点的时长 0.45 / 0.75 s ± 1 帧；转视角时点的屏幕位置不变。

#### 出处

- SR §2、§4。PR #103，还没合并
- UI H-01 – H-05、§6。PR #102，还没合并
- FG §9（B10：30 把枪准星截图，命中标记没认出来）。PR #122，还没合并
- D-128。#104，还没合并

### 6.3 R5 没有的反馈：开枪不震屏、中弹不抖；枪口焰和曳光

#### 原理

R5 第一人称的"打击感"靠后坐、声音和界面，**不靠震屏**：开枪没有自己的屏幕抖动，铁驭被真枪打中镜头也不动（伤害方向由界面箭头和闪屏告诉你）。想加震屏，就是偏离（[07 §6](07-camera.md)）。曳光画面上从枪口出发，子弹判定从眼睛走。

#### 规则和公式

1. 开枪：画面只有 punch（+ drift），别的偏移 0.000°（7 把枪）。
2. 铁驭中弹：瞄准、两组 punch、画面、眼睛位置、FOV 全是 0（27 发真实命中，15–198 伤害）[实测，hyb]。受伤的屏幕效果（闪屏、低血量覆盖、方向箭头）只在脚本里读到，没测（UI H-06、H-07）。
3. 枪口焰：粒子系统寿命量到了（整个系统含烟和火星，不是亮的那一下）；亮度本地没测成。
4. 曳光：从枪口出发，收拢到子弹线上（D-117，收拢距离 600 u 是 [猜]）；枪口屏幕位置跟枪模 FOV 走（§3.3）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 开枪震屏 | — | 0 ° | — | 7 把 × 2 种 × 2 次 | [实测] FG §2 |
| 铁驭中弹镜头 | — | 0 ° | — | 27 发 | [实测，hyb] FG §3 |
| 枪口焰粒子寿命 步枪 / 手枪 / 霰弹 / 狙击 | — | 0.50–0.60 / 0.13–0.30 / 0.72–0.92 / 1.57–1.81 s | — | 两次差 0.1–0.3 s（带随机） | [实测] FG §4.1 |
| 曳光收拢距离 | 15.24 m | 600 u | 8.33 H | 没和 R5 帧比 | [设计] D-117 |
| 子弹起点 | — | 眼睛（第一发水平偏差 0.00 u） | — | — | [实测] GM D §6 |

#### 实现模板

Unity 参考实现：枪口焰 `HeldModels.cs`（`CombatHeldModelTests.TheFlashLastsItsTimeAndOnlyFollowsAShot`）；曳光 U#65（开关 `arsenal.tracerFromMuzzle`）。泰坦受击有驾驶舱弹簧（07 §2.8），不在本章。

#### 验收

- 开枪不震屏：`CombatWeaponTests.TheRecoilMovesTheViewAndTheRoundsTogetherThenComesBack`（画面随 punch 走、停火回原位）；"别的偏移为 0"没有单独的测试（见 §2.8 的建议）。
- `CombatHeldModelTests.TheTracerStartsWhereTheMuzzleShowsAndThatFollowsTheGunFov`、`TheFlashLastsItsTimeAndOnlyFollowsAShot`。

#### 出处

- FG §2、§3、§4。PR #122，还没合并
- GM `D-EXTENSIONS.md` §4、§6、§8；`reload-motion/SCREEN-TRACER.md`。PR #95，还没合并
- D-117（曳光从枪口）。#91 / #104，还没合并

---

## 7. 换弹和切枪的时刻表

### 7.1 换弹的三个时刻（D-113、D-118）

#### 原理

换弹不是"锁住 2.4 秒再给你满弹匣"。R5 的换弹有三个时刻：**加弹**（弹匣数变满）、**解锁**（能开枪、能开镜）、**动画结束**。解锁比动画结束早（R-301 战术 1.64 s 解锁，动画 2.40 s）——最后那段只是枪落回原位，开枪直接打断它。所以熟练玩家感觉 R5 换弹"比数字快"。

动画播放本身是匀速的，"加速感"来自动画里一段段快动作（起手甩枪 → 歪着枪操作弹匣 → 加弹同时快速回正 → 解锁后轻轻落定），动作的形状在 08 章；**加弹那一刻紧贴一个快动作**（26 把里战术 18 把不到 0.1 s）。

#### 规则和公式

1. 时刻按枪记（**没有通用比例**），都从换弹开始算；战术（还有子弹）和空仓（打空）分开。
2. 解锁前按住开火：等到解锁那一刻才打。解锁后按开火：立刻打，打断剩下的动画。开镜同样等解锁。
3. 换弹不减速（§4.2）。
4. 配件按比例缩放三个时刻（枪托 L1 × 0.966、L3 × 0.90；`corrupted_mag` × 1.35）。
5. Boosted Loader：Hemlok 弹匣 1–5 时 1.80 s 加满到 30 发；Wingman 弹匣 1 时 1.45 s、到 7 发；弹匣 0 和满的时候普通。

代表枪（全部在 [reload-moments.tsv](09-combat-feel/reload-moments.tsv)，**以 RM-SUMMARY 为准，C-MOTIONS 表的"解锁"列作废**）：

| 枪 | 类型 | 动画长 | 加弹 | 解锁 | 加弹比例 | 解锁比例 | 依据 |
|---|---|---|---|---|---|---|---|
| R-301 | 战术 / 空仓 | 2.40 / 3.20 s | 1.39 / 1.98 s | 1.64 / 2.43 s | 0.58 / 0.62 | 0.69 / 0.76 | [实测] RM |
| R-99 | 战术 / 空仓 | 1.80 / 2.45 s | 1.43 / 1.95 s | 1.61 / 2.19 s | 0.79 / 0.80 | 0.89 / 0.90 | [实测] |
| Spitfire | 战术 / 空仓 | 3.40 / 4.20 s | 2.03 / 3.29 s | 2.84 / 3.83 s | 0.60 / 0.78 | 0.84 / 0.91 | [实测] |
| Wingman | 战术 = 空仓 | 2.10 s | 1.49 s | 1.94 s | 0.71 | 0.92 | [实测] |
| P2020 | 战术 / 空仓 | 1.25 / 1.25 s | 0.79 / 0.94 s | 1.10 / 1.09 s | 0.63 / 0.75 | 0.88 / 0.88 | [实测] |
| Kraber | 战术 / 空仓 | 3.15 / 4.30 s | 1.91 / 2.92 s | 2.77 / 4.04 s | 0.61 / 0.68 | 0.88 / 0.94 | [实测] |
| 全部（中位数，28 把） | 战术 / 空仓 | — | — | — | 0.63 / 0.74 | 0.87 / 0.90 | [算] |

#### 实现模板

```
startReload(gun, empty):
    m = reloadTable[gun][empty]                   // length, ammo, unlock（秒，× 配件比例）
    ammoAt = now + m.ammo;  unlockAt = now + m.unlock;  endAt = now + m.length
tick(now):
    if now >= ammoAt and not loaded: clip = full
    canFire = canAds = now >= unlockAt
onFire(): if now >= unlockAt and now < endAt: cutAnimation()
```

Unity 参考实现：`ReloadMoments.cs`（`ReloadTable`、`ReloadMoment`、数据 `ReloadData.gen.cs`，U#65），用法在 `ArsenalWeapon.cs`（`unlockAt`、`ammoAt`、`reloadUntil`）。数据由 `gen-reload-data.mjs` 从 RM-SUMMARY 生成（D-118：`dur` 当分母，Sentinel 例外用 C 的 `state`）。开关 `arsenal.reloadMoments`（关 = 整个换弹锁住、结束才加满）。

#### 验收

- `CombatReloadSwapTests.AReloadHasThreeMomentsPerGun(id, empty, ammo, unlock, end)`、`HoldingFireWaitsForTheUnlockThenCutsTheAnimation`、`AimingWaitsForTheUnlock`、`EveryGunWithAMagazineHasMeasuredMomentsOrIsKnownNotTo`、`TheOldReloadStaysBehindItsSwitch`。
- 合格线：解锁时刻和 RM 差 ≤ 0.05 s（D-118 改后中位数 0.002 s；最大 Kraber 战术 +0.043 s、Sentinel 空仓 −0.041 s，不追）。

#### 出处

- RM §1–§3（节奏、时刻）、`RM-SUMMARY.tsv`。PR #95，还没合并
- GM `C-MOTIONS.md` §1–§4（三个时刻、打断、配件；**表里"解锁"列作废**）。PR #95，还没合并
- D-113（三个时刻）、D-118（解锁数据改用 RM；没选继续用 C 表）。#91 / #104，还没合并

### 7.2 什么能打断换弹

#### 原理

换弹中你还是能动：冲刺、跳、按开镜、按开火都**不**打断换弹（开镜和开火等解锁）。只有**换枪和近战**打断，而且以加弹时刻为界：加弹前打断这次就白换了，加弹后打断子弹保留。这让"换弹到一半切枪"成为一个有代价、可预期的决定。

#### 规则和公式

| 动作 | 加弹前 | 加弹后 | 依据 |
|---|---|---|---|
| 换枪 | 打断，没加弹 | 打断，弹药保留 | [实测] C-MOTIONS §3 |
| 近战 | 打断，没加弹 | 打断，弹药保留 | [实测] |
| 冲刺 / 跳 | 不打断 | 不打断 | [实测] |
| 开镜键 | 不打断，等解锁 | 解锁后开镜 | [实测] |
| 开火键 | 不打断，等解锁 | 解锁后打断动画开枪 | [实测] |

没搞清的：R-301 在加弹前被换枪 / 近战打断后，回来时又自动换了一次（各 1 次，别的枪没有），不当规律。

#### 实现模板

Unity 参考实现：`ArsenalWeapon.cs` 换弹打断逻辑（U#65）。

#### 验收

- `CombatReloadSwapTests.SprintAndJumpDoNotBreakAReload`、`APunchBeforeTheAmmoMomentLosesItAndAfterKeepsIt`、`ASwapBeforeTheAmmoMomentLosesTheReload`。

#### 出处

- GM `C-MOTIONS.md` §3、`C-CANCEL.tsv`。PR #95，还没合并
- D-113。#91 / #104，还没合并

### 7.3 逐发装填（Mastiff、30-30）

#### 原理

逐发装填的枪换弹是"开始段 + 每发一段 + 结束段"，每发一次加弹，开火可以中途停下（打断后面的发）。总长不是字段：字段是**分段长度**。

#### 规则和公式

| 枪 | 打法 | 开始段 | 每发 | 结束段 | 总长 | 加弹时刻 | 依据 |
|---|---|---|---|---|---|---|---|
| Mastiff | 差 2 发 | 0–0.74 s | 约 0.51 s | 1.26–1.80 s | 1.80 s | 0.72、1.10 s | [实测] RM §5 |
| Mastiff | 空仓 5 发 | 0–1.12 s | 约 0.51 s | 3.18–3.73 s | 3.72 s | 0.75、1.48、1.99、2.50、3.02 s | [实测] |
| 30-30 | 差 2 发 | 0–0.27 s | 0.33–0.41 s | 1.09–1.53 s | 1.53 s | 0.45、0.85 s | [实测] |
| 30-30 | 空仓 6 发 | 0–0.74 s | 0.33–0.41 s | 2.53–3.12 s | 3.12 s | 0.58、0.92、1.33、1.69、2.02、2.34 s | [实测] |

Mastiff 字段 0.9、1.6 和 30-30 的 0.33、0.75 是分段长度。Dual Shell（30-30）一次 2 发：空仓 3.15 → 2.21 s。

#### 实现模板

Unity 参考实现：`ReloadMoments.cs` `ShellSchedule`（手写逐发表，D-118 没改）。

#### 验收

- `CombatReloadSwapTests.ShellGunsLoadOnTheirMeasuredSchedule`、`TheTriggerStopsAShellReloadAfterTheShellUnderWay`；`CombatWeaponTests.ShellReloadAddsOneAtATimeAndTheTriggerStopsIt`。

#### 出处

- RM §5；GM `C-MOTIONS.md` §1"按发装填"、§4。PR #95，还没合并
- D-113、D-118。#91 / #104，还没合并

### 7.4 切枪（D-114）

#### 原理

切枪是**先收旧枪，再掏新枪**，两段时间都是字段，都按枪的重量走（§4.1）。新枪**不用等掏枪动画走完**就能开火——掏到一半就可以打。所以"从重枪切到轻枪"比"从轻枪切到重枪"快的地方在收枪那一段。每把枪留着自己的弹匣。第一次掏一把枪要更久（`deployfirst_time`）。

#### 规则和公式

1. 收枪 `holster_time` 走完才换到新枪，再走 `deploy_time`；第一次掏用 `deployfirst_time`。
2. 新枪能开火的时刻 = 收枪 + deploy × 比例；**比例不固定，0.5–0.9**（6 个方向各 1 次），其余方向用中位数 0.55 [推断]。
3. 开火中切枪：立刻停火开始收枪。开镜中能切。
4. 近战：切到空手近战，按键后 0.367 s 能开火，不开火约 0.98 s 回到枪。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 收枪 R-301 / Wingman / P2020 / Spitfire / Kraber | — | 0.55 / 0.36 / 0.18 / 0.75 / 0.8 s | — | 实测等于字段 | [数据] [实测] C-MOTIONS §5 |
| 掏枪 同上 | — | 0.6 / 0.4 / 0.225 / 0.8 / 1.2 s | — | 实测等于字段 | [数据] [实测] |
| 第一次掏枪 R-301 / Spitfire / Kraber | — | 1.1 / 1.45 / 1.5 s | — | Wingman 实测 1.277（字段 1.45，没查） | [数据] [实测] |
| 切枪到能开火：Wingman → R-301 / R-301 → Wingman / R-99 → Kraber / Kraber → R-99 | — | 0.66 / 0.85 / 0.91 / 0.99 s | — | 掏枪里用掉的比例 0.5–0.9 | [实测] |
| 没测方向的掏枪比例 | — | 0.55 | — | — | [推断] D-114 |
| 近战后最早开火 / 回到枪 | — | 0.367 / 约 0.98 s | — | 3 把一样 | [实测] C-MOTIONS §6 |

全部枪的收枪、掏枪字段在 [gun-weight.tsv](09-combat-feel/gun-weight.tsv)。

#### 实现模板

```
swap(to):
    stopFire(); holsterUntil = now + from.holster
    at holsterUntil: current = to; t0 = now
    readyAt = t0 + (to.firstDraw ? to.deployfirst : to.deploy) * drawShare(from, to)   // 表，没有就 0.55
```

Unity 参考实现：`ArsenalWeapon.cs`（`deployedAt`、`readyAt`，U#65）；枪的下放 / 抬起形状在 `HeldMotion.cs`（形状 [猜]）。开关 `arsenal.swapHolster`（关 = 隐藏等完 `deploy_time`、满弹匣）。

#### 验收

- `CombatReloadSwapTests.ASwapHolstersTheOldGunThenDrawsTheNew`、`EachGunKeepsItsOwnMagazineAndAFirstDrawIsLonger`、`TheOldSwapStaysBehindItsSwitch`、`TheGunGoesDownInTheHolsterAndComesUpByTheReadyMoment`；`CombatWeaponTests.FistNeedsAWeaponAndTheConeAndHasRecovery`。
- 合格线：6 个实测方向的"能开火"时刻差 ≤ 0.02 s。

#### 出处

- GM `C-MOTIONS.md` §5、§6，`C-SWITCH.tsv`、`report/02-draw-swap.md`。PR #95，还没合并
- D-114。#91 / #104，还没合并

---

## 8. HSD 现在和 R5 不一样的地方（汇总）

本章各项里写过的差别集中在这里。前四条是"HSD 可能做错的"，建议的 D 行在 `_notes/hb-ch09.md`；后面是有意偏离或小差别。

| # | 项 | R5 | HSD 现在 | 本章 |
|---|---|---|---|---|
| 1 | 子弹含 punch1 和开镜 drift | 子弹 = aim + punch1 + punch2 + drift | aim + 武器 punch | §1.1、§3.7；07 §4.3 |
| 2 | 第二组弹簧 | 移动 × 0.2 和武器 kick 进同一个第二组，拿枪用武器弹簧 | 两个独立弹簧（原生镜头 65 / 9、`ViewKick`） | §2.1；07 §2.10 |
| 3 | 鼠标下压抵消 punch | 有（实测） | 没做 | §2.6 |
| 4 | 冲刺到开火 0.14–0.25 s；钩爪 / 爬墙挡开火 | 有（实测） | 没做 | §4.4 |
| 5 | 开镜漂移 | 有，进子弹 | 没做 | §3.7 |
| 6 | 单发枪开镜跳动、拉栓镜头 | 有 | 没做 | §2.7、§2.8 |
| 7 | 下蹲比例对后坐 | 连续 | 0 / 1 | §2.3 |
| 8 | 扩散锥半径 | 没测；TF2 = sin(角/2) 三角分布 | tan(角) 均匀圆盘 | §5.2 |
| 9 | 开镜灵敏度用哪一帧的 FOV | 上一帧 | 当前帧 | §3.6 |
| 10 | 霰弹弹丸随机（D-137 / D-129） | 固定图案 | 每颗弹丸的随机区域 | §5.3（**有意偏离**） |
| 11 | Kraber 开镜枪模 FOV（D-122） | 到位后 70（全屏镜） | 保持 `zoom_fov` | §3.3（**我们定的，等用户**） |
| 12 | R-301 开镜回落到 50 % | 0.244 s | 0.203 s | §2.1（差 0.04 s 没解释） |

---

## 9. 待研究

本章发现的缺口，建议追加进 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md) 的 B09 表，编号和建议的测法在 `_notes/hb-ch09.md` §3。要点：

- 开镜动画只测了 3 把（B09-1）；开镜漂移的公式没读；开镜移速的插值形状没测。
- 腰射落点分布没测（只知道锥多大）；HSD 锥半径可能差 2 倍要核对。
- 冲刺到开火 0.25 s 上限的来源；钩爪 / 爬墙挡开火的规则在 Unity 里没有。
- 单发枪开镜跳动、拉栓镜头的曲线形状。
- 命中 X、伤害数字的样子（时长、大小、颜色）只有脚本；音效完全没有（A-3）。
- 普通准星的像素公式（W-02）。
- 按枪的转向限制：没找到，是推断。
- Devotion 第一发 1.02 对 1.2、Kraber 开镜第一发 1.37 对 1.5、L-STAR 枪模跳动 0.086 u、R-301 开镜回落 0.04 s，都没查。
- 表尾 loop 非 0（Spitfire）只有反编译；连发取整没单独验证。
- 可变倍率第二档、Kinetic Loader 本地测不了（B09-5）。
- TF2 铁驭枪的画面弹簧没实测（B09-6）。
