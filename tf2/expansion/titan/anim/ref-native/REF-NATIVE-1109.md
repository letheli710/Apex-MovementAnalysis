# 泰坦转身、走跑切换、停步混合：原生代码里的规则（ref-titan-native，2026-11-09）

会话 `ref-titan-native`，补测清单 `../../REF-TESTS-1109.md` 的 §2.4，顺带 A2、A6。只用 Ghidra 读 TF2 的 `server.dll` / `client.dll`，没有开 TF2，没有改 Unity。这里只写规则、数值和函数地址；反编译原文在私有仓库 HSD-RawData 的 `tf2/local/refnat/`（分支 `ref/titan-native-raw`，HSD-RawData PR #17）。

## 先说结论

1. **转身对不上的原因：400 °/s 是最快的速度，不是一直按这个速度转。** 腿离目标越近就转得越慢：速度 = 400 × (还差的角度 ÷ 60)，最低不低于 4 °/s。所以腿追上去是一个时间常数 0.15 s 的指数曲线。60° 的一步走完 90 % 要 0.32 s，走完 95 % 要 0.42 s，和实测的 0.33–0.5 s 对得上。另外，腿的目标不是一路跟着视线走，而是每次整跳 60°。所以停转以后，腿可以一直留在偏 60° 以内的地方（实测 36°）。
2. **A2：什么时候从走换成跑。** 引擎每次更新都按水平速度判断，没有滞回：速度 ≥ 0.45 × 站姿 `speed` 就用跑。中型是 112.5 u/s，重型 94.5，轻型 121.5。冲刺不看速度，看"是否在冲刺"这个状态。速度超过 1.05 × `sprintspeed`（往后走时是 1.05 × `speed`）就换成 SLIDE，在泰坦上就是 dash 片段。**推论：中型泰坦全速（250 u/s）往前走时，播的是跑片段 `Run_forward_MP`，不是走片段。** 这和 `TITAN-ANIM-FEEL.md` §2.1/§2.2 原来的推断相反，要由 `ref-titan-gait` 用序列名实测核对。
3. **A6：停步时哪个混合时间起作用。** 换序列时，旧姿势淡出的时间 = min(旧序列的 fadeout, 新序列的 fadein)，权重按 smoothstep 曲线下降。停步（走或跑 → 待机）= min(0.55, 0.2) = **0.2 s**，所以起作用的是待机的混入 0.2。起步（待机 → 走或跑）= min(0.2, 0.95) = **也是 0.2 s**，原文"起步 0.95 s 慢慢混入"不对。混合从速度降到 0.5 u/s 那一刻才开始。

## 0. 清单（开始前列出）

| # | 要找的 | 结果 | 节 |
|---|---|---|---|
| 1 | `mp_bodyyawrate`、`mp_maxbodyyaw` 被谁读、怎么用 | ☑ 腿朝向函数 + 收敛函数，两个 dll 一样 | §2 |
| 2 | 腿落后视线的角度（60°）怎么起作用 | ☑ 目标按 60° 整步跳；另有 aim_yaw 范围硬限制 | §2 |
| 3 | 解释 400 °/s 对 0.33–0.5 s | ☑ 按比例减速，时间常数 0.15 s | §2.3 |
| 4 | A2：走 → 跑的速度门槛、是硬切还是混合 | ☑ 0.45 × speed，没有滞回；混合 0.55 s | §3 |
| 5 | A6：停步时 0.55 和 0.2 哪个起作用 | ☑ min(...) = 0.2 s，smoothstep | §4 |
| 6 | 顺带：播放速度规则 | ◐ 公式读到；泰坦会不会被某些条件锁成 1.0 倍，没读完 | §5 |

## 1. 怎么找的

- 工程：`ghidra-projects/tf2/`（Ghidra 12.1.4）。`server.dll` sha256 `a5ca3a25c8ae5695…`，`client.dll` sha256 `002b36487fec7c98…`。
- ConVar 对象地址来自 `TF2-Research/local/convar-all-*.dll.txt`；用 `TF2-Research/ledger/ghidra/ConVarReadersTF2.java` 列出每个读取点，并反编译读取它的函数。
- 再用 `TF2-Research/pve/live/ghidra/AiDig.java` 读常量、反汇编、反编译调用的函数；用 `ImmScan.java`（本目录）找用到活动号 `0x19e`（ACT_MP_RUN）的指令。全程只读（`-readOnly -noanalysis`）。
- 活动号从注册表 `0x18008d5d0` 读出：STAND_IDLE 0x199、RUN 0x19e（+1..4 = FORWARD/BACKWARD/LEFT/RIGHT）、STAGGERED_RUN 0x1a3、WALK 0x1a8（+1..4）、STAGGERED_WALK 0x1ad、SPRINT 0x1bd、STAGGERED_SPRINT 0x1be、SLIDE 0x1bf（+1..4）。

用到的函数：

| 作用 | server.dll | client.dll |
|---|---|---|
| 每帧更新（求速度、"在动"标志、方向，然后调用下面几个函数） | `0x1805ef770` | `0x18049ce80` |
| 腿朝向（读 `mp_maxbodyyaw`、`mp_bodyyawrate`） | `0x1805ebab0` | `0x1804999a0` |
| 腿朝向收敛（ConvergeYawAngles） | `0x1805ec620` | `0x18049a180` |
| 选主活动（走 / 跑 / 冲刺 / SLIDE） | `0x1805ee970` | `0x18049c050` |
| 播放速度 | `0x1805eb300` | `0x1804993e0` |
| 换序列的淡出时间（读 `sequence_transitioner_fixed_fade`） | `0x1802013d0` | `0x18031ec90` |
| 换序列时把旧序列加进淡出队列（读 `sequence_transitioner_enable`） | `0x180200590` | `0x18031e390` |
| 淡出权重曲线 | `0x180200460` | （同结构，没逐行比） |
| 方向门槛的容差（`anim_playerMovementAngleMargin`） | `0x1805f0470` | `0x18049d6d0` |

client 和 server 的腿朝向、选活动、换序列淡出时间三处都逐项比过常量（60、0.01、0.45、1.05），完全一样。

## 2. §2.4 原地转身

### 2.1 伪代码要点（`0x1805ebab0`）

```
eye  = 视线 yaw
goal = 腿的目标朝向（实体 +0x1958）
feet = 腿当前朝向（实体 +0x1950，身体就画在这个朝向上）

if 在动（水平速度 > 0.5 u/s）:
    goal = eye                     # 走路时腿直接对准视线，剩下的交给 move_yaw
else:                              # 站着
    d = AngleNormalize(eye - goal)
    if |d| > mp_maxbodyyaw (60):
        goal += sign(d) * floor(|d| / 60) * 60   # 按 60° 整步跳
    # |d| ≤ 60 时 goal 不动

if goal != feet:
    ConvergeYawAngles(goal, rate = mp_bodyyawrate (400), dt = 距上次更新的时间, &feet)

aim_yaw = clamp(AngleNormalize(eye - feet), aim_yaw 姿势参数的 min, max)
feet    = eye - aim_yaw                          # 腿不许落后超过瞄准层能扭的范围
设置姿势参数 aim_yaw
```

另有几个特例：骑在别的实体上时腿等于实体朝向；某个"强制"标志（+1）会让 feet 直接等于 goal；`+0x489` 设置项（推断是四向动画）打开时，走路时腿按移动方向 + 0/180/±90° 摆。泰坦正常走、站都不进这些分支。

```
ConvergeYawAngles(goal, rate, dt, &cur):          # 0x1805ec620
    d     = AngleNormalize(goal - cur)
    scale = clamp(|d| / 60, 0.01, 1)                # 60 = FADE_TURN_DEGREES（常量 0x18086d6b0）
    step  = rate * dt * scale
    cur   = (|d| ≤ step) ? goal : cur + sign(d) * step
```

这就是 Source 引擎 `CMultiPlayerAnimState::ConvergeYawAngles` 的原样做法。Respawn 只把速度换成了 ConVar，并把目标改成按 60° 整步跳。

### 2.2 规则（照做用）

1. 站着时，视线和腿目标的差不超过 60°，腿就不动。
2. 差超过 60° 时，腿目标朝视线方向跳 60°（差 ≥ 120° 就跳 120°，依此类推）。
3. 腿追目标的角速度 = 400 × min(1, 剩余角度 / 60)，最低 4 °/s。还差 60° 以上时按 400 °/s 匀速，60° 以内就是 τ = 60/400 = **0.15 s** 的指数衰减。
4. 腿不能落后视线超过瞄准层的 `aim_yaw` 范围（中型 ±90）。转得太快时，腿被硬拖着走。
5. 一动起来（速度 > 0.5 u/s），腿目标就是视线，追的规则同第 3 条。

### 2.3 和实测的对照（`feetyaw_sim.py`，60 Hz 积分）

| 情况 | 原生规则算出来的 | 实测（GAPS §8、POSE §3.2） |
|---|---|---|
| 一步 60°，走完 50 / 75 / 90 / 95 / 98 % | 0.08 / 0.18 / 0.32 / 0.42 / 0.55 s | 一步 0.33–0.5 s |
| 一步转多少 | 正好 60°（目标整步跳） | 正好 60° |
| 30° 转 30 °/s | 腿不动，最后落后 30° | 滞后 60° 以内脚不动 |
| 90° 转 90 °/s | 最大落后 60°，停后腿留在偏 30° | 停转后腿可以留在偏 36° |
| 400° 转 400 °/s | 落后到 90°，被 aim_yaw 范围卡住；停后留 40° | — |

**差别的解释：** 原文按"400 °/s 匀速转 60° = 0.15 s"算，但原生代码里 400 °/s 只在还差 60° 以上时才达到。从目标跳到腿转完，是一条时间常数 0.15 s 的指数曲线：0.15 s 只走完 63 %，看起来"一步转完"要 0.3–0.5 s。原文猜的"姿态交叉淡入或脚 IK 放开"不是原因。脚 IK 只是把脚钉在地上，不决定腿多快转过去。

**推断：** 实测看到"两脚一起动"，是因为整个身体（骨架根）按 `feet` 朝向画出来，而待机片段两只脚都是满权重 ground。转身时 IK 把脚锁在原地，根一转，锁就放开再落下。这一条是推断，没有在代码里读 IK 的锁放逻辑。

## 3. A2：走和跑怎么换（`0x1805ee970`）

### 3.1 伪代码要点

```
if 不在地面上等（0x1805ef580 返回假）: 不选移动活动
if 水平速度 ≤ 0.5: 不选移动活动（→ 待机）

f = 速度在视线前方向上的分量；s = 速度在视线侧向上的分量
s /= speedScaleSide                    # 设置文件 +0x98
if f < 0: f /= speedScaleBack          # +0x9c
v = sqrt(s² + f²)

walk = 站姿 speed，sprint = 站姿 sprintspeed（< 0 时用 speed）   # 玩家 +0x1dac / +0x1db0
dir  = 1 前 / 2 后（泰坦只有这两个；四向模型才有 3 左 / 4 右，见 §3.3）

if v ≥ 1.05·sprint  or  (dir ≠ 前 and v ≥ 1.05·walk):  act = ACT_MP_SLIDE
elif 正在冲刺:                                         act = ACT_MP_SPRINT   # 不加方向
elif v ≥ 0.45·walk:                                    act = ACT_MP_RUN
else:                                                  act = ACT_MP_WALK
（踉跄时换成 STAGGERED_* 版本）
act += dir（SPRINT 以外）
```

### 3.2 规则和门槛

| 底盘 | speed / sprintspeed（设置文件） | 走 → 跑（0.45 × speed） | SLIDE（前半圈 1.05 × sprint；后退 1.05 × speed） |
|---|---|---|---|
| 中型 `titan_atlas.set` | 250 / 380 | **112.5 u/s** | 399 / 后退 262.5 |
| 重型 `titan_ogre.set` | 210 / 310 | **94.5 u/s** | 325.5 / 后退 220.5 |
| 轻型 `titan_stryder.set` | 270 / 400 | **121.5 u/s** | 420 / 后退 283.5 |

- **没有滞回：** 每次更新都重新比，速度在 112.5 附近来回时，活动也会来回换（每次换都按 §4 混合）。
- **怎么换：** 走 ↔ 跑是两个序列之间换，混合时间 = min(0.55, 0.95) = 0.55 s，smoothstep（§4）。不是硬切。
- **冲刺：** 看冲刺状态（玩家 +0x27c4，`GetMaxSpeed` 也用它在 speed 和 sprintspeed 之间选），不看速度。
- **SLIDE：** 泰坦模型的 `ACT_MP_SLIDE_FORWARD` / `_BACKWARD` 是 `Slide_mp_forward` / `Slide_mp_backward`（0.267 s 循环、全 release IK、混入 0.15、混出 0.95），也就是 dash 的身体姿势。dash 时速度超过门槛，自动换成这个。
- **推论（等实测核对）：** 中型全速前进 250 u/s 远高于 112.5，按这条规则播的是 `Run_forward_MP`（地速 311.6）。原报告 §2.1"走 = Walk_forward_MP"、§2.2"跑只出现在冲刺加速段"是推断，和原生规则不符。已有的步频实测（Ion 走路段平均 227.7 u/s，周期 1.154 s）和两种假设都对不齐：走片段按速度缩放预测 1.22 s，跑片段预测 1.46 s，实测反而接近两个片段各自不缩放的周期（1.133 / 1.067）。所以 §5 的播放速度在泰坦上是否生效也要一起核。
- **没核实的一处：** `+0x1dac` 是按姿势（站、蹲）排列的 {speed, sprintspeed} 表（`0x1805e35e0` 按姿势号 × 8 填，类设置里按 "speed"、"sprintspeed" 键读，`0x180555560`）。选活动只读第 0 项，第 0 项是站姿是推断。

### 3.3 方向（顺带）

`0x1805ef770` 先算移动方向相对视线的角度 `d = eye − 速度方向`，再分两套方向：

- **四向**（+0x54）：用设置文件里的四个角（+0x3e4…+0x3f0，即 `aimAngleBackwardEnd / ForwardStart / ForwardEnd / BackwardStart`，中型 −120 / −40 / 40 / 120）。d < −120 或 > 120 是后（2），−40…40 是前（1），40…120 是右（4），−120…−40 是左（3）。`anim_playerMovementAngleMargin` 10 是滞回：已经在某个方向时，边界向外放宽 10°（`0x1805f0470`）。
- **前后两向**（+0x58）：|d| ≤ 90 是前，否则是后，同样带 10° 滞回。

设置项 +0x489 打开时（推断是 `quadMoveAnims`），+0x58 用四向；泰坦是 `quadMoveAnims 0`，只用前后两向。所以泰坦的活动只有 `*_FORWARD` / `*_BACKWARD`：横移也是 FORWARD，靠 `move_yaw` 混合（和报告 §2.5 一致）。同一个 +0x58 也决定活动修饰 movingforward/backward，以及 §3.1 里 SLIDE 的"方向不是前"。所以泰坦横移时只有超过 1.05 × sprintspeed 才进 SLIDE，后退时超过 1.05 × speed 就进。

## 4. A6：换序列的混合（停步、起步）

### 4.1 伪代码要点

```
# 0x180200590：主序列号变了
if 新序列没有 SNAP 标志 and 实体没有关插值:
    fade = TransitionFade(hdr, 旧序列, 新序列)
    把旧序列（含当时的 cycle、播放速度、姿势）加进淡出队列（最多 6 个），淡出时间 = fade

# 0x1802013d0
TransitionFade(old, new):
    if sequence_transitioner_fixed_fade ≥ 0: return 它       # 默认 -1，不生效
    return min(old.fadeout, new.fadein)                       # seqdesc +0x6c / +0x68

# 0x180200460：队列里每一项的权重（从新到旧连乘）
x = clamp(1 - (now - 加入时刻) / fade, 0, 1)
w = (3 - 2x)·x²                    # smoothstep
# 0x1802015f0：加入时刻 + fade + 0.1 s 以后从队列里删掉
```

这是 Source 引擎 `CSequenceTransitioner` 的做法（`MIN(prev.fadeouttime, seq.fadeintime)`）。`anim_transitionsequences` 1、`sequence_transitioner_enable` 1 都是开的。

### 4.2 规则（中型，括号内是两个序列各自的值）

| 换法 | 混合时间 |
|---|---|
| 走 / 跑 → 待机（停步） | **0.2 s**（走混出 0.55，待机混入 0.2） |
| 待机 → 走 / 跑（起步） | **0.2 s**（待机混出 0.2，走混入 0.95） |
| 走 ↔ 跑 | 0.55 s（0.55 / 0.95） |
| 走 / 跑 → 冲刺 | 0.55 s（0.55 / 0.95；轻、重冲刺混入 0.2 → 0.2 s） |
| 冲刺 → 走 / 跑 | 0.2 s（冲刺混出 0.2） |
| 走 / 跑 → dash（SLIDE） | 0.15 s |
| dash → 走 / 跑 | 0.95 s（0.95 / 0.95） |

**A6 的答案：** 停步时起作用的是待机的混入 0.2 s。走的混出 0.55 s 只有在新序列的混入 ≥ 0.55 时才起作用。曲线是 smoothstep，不是线性。混合从"在动"变成"不在动"那一刻开始，也就是速度 ≤ 0.5 u/s，基本是速度到 0 的时候。在这之前的减速段里，§3 的规则会先在 112.5 u/s 把跑换成走（0.55 s 混合）。§5 的播放速度在减速段也跟着降，最低到 0.25 倍。

**和实测的关系（推断）：** GAPS §7"约 0.5 s 速度到 0，约 0.9 s 回到站姿"里，0.5 → 0.9 s 这一段比 0.2 s 的混合长得多。多出来的大概是：减速末段的低播放速度、跑 → 走的 0.55 s 混合还没结束，以及原地的腿朝向收敛（§2，停下后腿目标从"等于视线"变成"60° 整步"，不再强制对齐）。要拆开这几项，需要 `ref-titan-gait` 的逐帧数据。

## 5. 顺带：播放速度（`0x1805eb300`）

```
if 不在动: rate = 1
elif 在 traversal / 某些状态（+0x195c、+0x1984、+0x197c、+0xa4、+0xb4、+0xb5 任一）: rate = 1
else:
    gs = 当前序列（含混合）的地速
    if gs < 0.001: rate = 1
    else:
        if 不是 +0x489 模式: gs *= |sin(move_yaw)| + |cos(move_yaw)|   # 斜向时片段地速按方向放大
        rate = clamp(水平速度 / gs, movement_anim_playback_minrate 0.25, maxrate 10)
        if 活动 == ACT_MP_SPRINT: rate = min(rate, 1.25)
    只有和上次相差 > 0.15 才更新        # 0.15 的台阶，不是平滑
```

**0.15 的台阶有什么后果（11-09 和 `ref-titan-gait` 对照）：** 播放速度只在和存着的值相差超过 0.15 时才改，所以稳定速度下的实际播放速度可以停在真值 ±0.15 以内的任何地方，具体停在哪取决于加速的过程。gait 冒烟测试（`20261109_105946_gait_smoke`）里，冲刺 380 u/s 量到 0.881 cyc/s，按 380/437.6/0.833 应该是 1.042。用台阶来解释：开始冲刺时约 250 u/s，速度改成 0.571；加速到约 316 u/s 时改成约 0.72；要到 381 u/s 才会再改，380 到不了，所以停在约 0.73，0.73/0.833 ≈ 0.88，和实测一致〔推断，待 gait 换不同的加速过程验证〕。gait 同一次测到：100 u/s 播走片段、175 和 250 u/s 播跑片段，停步混合约 0.2 s，和 §3、§4 一致。

`mp_scaleAnimationSpeeds` 为 0 时不调用这个函数。新读到两条：斜向时地速要乘 |sin|+|cos|；播放速度按 0.15 的台阶更新。上面那几个让 rate = 1 的条件是哪些状态，没逐个查。泰坦正常走路时会不会落进去，和 §3.2 的步频矛盾一起留给 `ref-titan-gait` 实测。

## 6. 推断不了 / 没做的

| 项 | 为什么 |
|---|---|
| `+0x1dac` 第 0 项是站姿 | 按姿势号填表的函数读到了，姿势名到序号的映射（`0x180555260`）没读 |
| 转身时 IK 锁放开、再落下的时刻 | 只读了腿朝向；IK 锁的代码没看 |
| 播放速度那几个"rate = 1"条件分别是什么状态 | 只看到字段偏移，没追到名字 |
| 客户端淡出权重曲线 | 只比了淡出时间函数，客户端的权重函数没逐行比（结构同 server） |

## 7. 文件

| 文件 | 放在哪 |
|---|---|
| 本报告、`feetyaw_sim.py`（转身模拟）、`ImmScan.java`（按立即数找指令） | 研究仓库 `tf2/expansion/titan/anim/ref-native/` |
| 反编译原文 `dec-server/`、`dec-client/`、`s*.txt`、`c*.txt`、`readers-*.tsv`、`imm-*.txt`、ConVar 对象表 `obj-*.tsv`、`dig.sh` | HSD-RawData `tf2/local/refnat/`（PR #17；本地原件在 `TF2-Research/local/refnat/`；D-76，不进公开仓库） |
