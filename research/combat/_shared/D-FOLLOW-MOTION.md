# 公共部件 D：跟随运动（伙伴 / 无人机跟着一个目标飞）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。

来源：Lifeline D.O.C.（`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_lifeline_follow_medic.nut`，简写 FM）。**这份脚本是 SDK 社区重写的**（证据见 [lifeline-heal-drone 5.1](../lifeline-heal-drone/SYSTEM.md)），所以这里记的是"一套能用的跟随算法"，不是 S21 正版的精确行为。

## 0. 概要

- **部件**：`FollowMedic_DesiredPos` + `FollowMedic_MoveThread`（FM:771-870）。
- **一句话**：每帧在目标右后上方算一个"该在的点"，用"比例速度 + 继承目标速度 + 一阶平滑"追过去；被墙挡住或离太远就瞬移；姿态由速度和目标转身速度决定。
- **分类**：系统 + 可视化。
- **谁能用**：治疗无人机、跟随伙伴、宠物、护盾球、跟随玩家的扫描器（Bloodhound 大招的 `TriggerTrackOwner` 是同类需求）、Mirage 分身"跟着我"模式的简化版。
- **可拆出的部件**：目标点（3.1）、追踪（3.2）、瞬移（3.3）、姿态（3.4）。

## 1. 它用什么实现

| 部分 | 手段 |
|---|---|
| 实体 | 不碰撞的 `script_mover`（FM:558-560） |
| 移动 | 服务端每帧 `NonPhysicsMoveTo( next, dt )`——每帧给一个"dt 后到这里"的目标，引擎插值 |
| 碰撞 | 不做物理碰撞；只在算目标点时扫一次小 hull，避免目标点在墙里 |
| 视线 | 每帧一条射线（无人机 → 目标眼睛） |

## 2. 流程（每帧）

```
desired = 目标点（3.1）
LOS 检查；离 desired 太远 → 瞬移；断视线太久 → 瞬移
否则：算想要的速度 → 封顶 → 平滑 → 走一步 → 防过冲
算姿态 → 转
```

## 3. 代码（伪代码，参数见第 4 节）

### 3.1 目标点（FM:771-784）

```
fwd, right = 目标视角 yaw 的前 / 右（不看俯仰）
dir   = normalize( right·SIDE − fwd·BACK )         # SIDE=1, BACK=0.6 → 右后方 31°
d0    = 蹲 ? D_CROUCH : D_STAND
h     = max( 蹲 ? H_CROUCH : H_STAND, H_MIN )
want  = 目标原点 + dir·d0 + (0,0,h)
from  = 目标原点 + (0,0,h)
desired = HullTrace( from → want, 半宽 HULL ).终点     # 墙会把点压回目标头顶
```

### 3.2 追踪（FM:847-862）

```
toD  = desired − cur;  dist = |toD|
speed = K·dist + (dist > DEAD ? V0 : 0)
want  = dir(toD)·speed + INHERIT·v_target
cap   = (1 + CAP_MUL)·|v_target| + V0·K + K·dist
want  = clampLen( want, cap )
v    += (want − v)·min(1, SMOOTH·dt)
next  = cur + v·dt
if |next − desired| > SNAP and dist < SNAP: next = desired
```

性质（推导）：
- 静止目标：无人机按"距离的 3 倍 + 40"的速度靠近，7 u 内只剩比例项，平滑后像一个阻尼弹簧，不会来回晃。
- 匀速目标：稳态时 `K·dist + V0 + INHERIT·v_t = v_t`，所以落后 `dist = ((1 − INHERIT)·v_t − V0) / K`（v_t 足够大、dist > 7 时；上限 cap 恒大于 v_t，不起作用）。INHERIT = 0.5、K = 3、V0 = 40 时，300 u/s 落后 37 u，600 u/s 落后 87 u。
- 想要"更黏"：INHERIT → 1（不落后）或 K 加大。想要"更飘"：SMOOTH 调小。

### 3.3 瞬移（FM:792-799、832-845）

```
if |cur − desired| > BREAK_DIST: 瞬移（普通音效）
if now − lastLOS > LOS_TIME:     瞬移（安静音效）
瞬移 = 起点放拖尾粒子（朝终点）→ SetOrigin( desired ) → 到达音；v = 0；lastLOS = now
```

### 3.4 姿态（FM:864-868）

```
yaw   = 目标视角 yaw
pitch = clamp( v·fwd(yaw) / PITCH_V, −1, 1 )·PITCH_MAX       # 往前飞就低头
roll  = clamp( Δyaw / (dt·ROLL_W), −1, 1 )·ROLL_MAX          # 目标转身就侧倾
NonPhysicsRotateTo( <pitch, yaw, roll>, dt )
```
注意 yaw 直接照抄目标，没有平滑；roll 只看目标转身，不看无人机自身横向速度。

## 4. 参数

| 参数 | Lifeline 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| SIDE / BACK | 1 / 0.6 | — | FM:778 | 偏移方向 |
| D_STAND / D_CROUCH | 72.5 / 40 | u | FM:83-87、774 | 水平距离 |
| H_STAND / H_CROUCH / H_MIN | 70 / 46 / 40 | u | FM:88、112-113 | 高度 |
| HULL | ±6.3 | u | FM:100、109-110 | 目标点扫掠 |
| K | 3 | 1/s | FM:93 | 比例增益 |
| V0 | 40 | u/s | FM:92 | 基础速度 |
| DEAD | 7 | u | FM:94 | 小于它不加 V0 |
| INHERIT | 0.5 | — | FM:95 | 继承目标速度 |
| CAP_MUL | 0.6 | — | FM:97 | 上限里的目标速度倍数 −1 |
| SMOOTH | 8 | 1/s | FM:857 | 速度平滑 |
| SNAP | 50 | u | FM:96 | 防过冲 |
| BREAK_DIST | 406 | u | FM:384-393 | 超距瞬移 |
| LOS_TIME | 1.0 | s | FM:114 | 断视线瞬移 |
| PITCH_V / PITCH_MAX | 400 / 20 | u/s / ° | FM:103、865 | |
| ROLL_W / ROLL_MAX | 180 / 17 | °/s / ° | FM:104、866 | |

## 5. 未解决和要实测的

- 本地版本的实际轨迹是否符合公式：见 lifeline-heal-drone 5.2 第一条（AgentLink 记位置）。
- S21 正版跟随点的位置（右后？头顶？）：只能对照正版录像。

## 6. HSD 实现

未实现。建议：纯 C# `FollowMotion` 类，`Step( in FollowTarget t, double dt ) → (pos, vel, pitch, yaw, roll, teleported)`，所有第 4 节参数放进 `FollowMotionSettings`，EditMode 测试验证"匀速目标稳态落后 = 公式值"。HSD 的世界查询用 `IMovementWorld`（`Blocked` / 射线）代替 hull 和视线。
