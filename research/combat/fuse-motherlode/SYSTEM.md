# Fuse 大招 The Motherlode（火焰环）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`rnut` = `vscripts/weapons/mp_weapon_mortar_ring.nut`（559 行），`mnut` = `vscripts/weapons/mp_weapon_mortar_ring_missile.nut`（1549 行），`rtxt` = `weapons/mp_weapon_mortar_ring.txt`，`mtxt` = `weapons/mp_weapon_mortar_ring_missle.txt`（注意文件名拼写 missle），`wu` = `vscripts/weapons/_weapon_utility.nut`。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Fuse / 大招 / The Motherlode / `mp_weapon_mortar_ring`（肩扛发射器）+ `mp_weapon_mortar_ring_missle`（空爆后撒出的 15 颗小炸弹的武器）。
- **一句话**：举起望远镜瞄一个点（522–7875 u），发一枚迫击炮弹，按弹道飞到目标点上空 750 u 空爆，撒出 15 颗小炸弹落成一圈（半径约 294–462 u），每两颗相邻炸弹之间沿地面连出一段火墙；火墙先 1 s"预燃"（5 伤害），再烧 15 s；碰到火的人第一跳 35、之后每 0.83 s 8（还在火里 ×1.5）共 6 跳，期间减速 0.25。
- **分类**：好技能（圈住敌人、封区域，PvE 价值高）；系统（**抛物线求解 + 准星落点 + 空爆**、**相邻炸弹连线成火墙段**、地面跟随的线段触发器）；可视化（望远镜 HUD、地面圈颜色反馈、火墙特效、沿线段的环境声、线段威胁箭头）。
- **可拆出的部件**：
  - 准星落点 + 抛物线求解（定速、低弧）→ 3.1 / 3.2.1 `GetCrosshairTargetData` + `SolveBallisticArc`
  - 瞄准预览（圈颜色、遮挡判定、抛物线覆盖、炮管俯仰动画）→ 3.3 `WeaponActiveThread_Client`
  - 飞到目标水平距离就强制空爆 → 3.2.2 `BombFlightThread`
  - 空爆撒一圈（定角度、随机半径、逐个抛物线）→ 3.2.3 `MortarRingAirburst` / `GetTargetPointsAroundOrigin`
  - 相邻配对 + 落地等待 → 3.2.3（`trackedEnt`）、3.2.4 `BombletExplosion`
  - 落点推人（按左右侧推离或推入）→ 3.2.4
  - 沿地面画线段（前进 + 向下 trace）→ 3.2.5 `FindValidEndPosForFireSegment`
  - 线段触发器（胶囊式判定 + LOS）→ 3.2.6 `MortarRingFireSegmentTriggerThread` / `…InTriggerThread`
  - 燃烧 DoT（首跳大、在火里加成、按攻击者去重）→ 3.2.7 `BurnDamageThink`
  - 客户端线段环境声 + 最近点威胁箭头 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 瞄准 | `fire_mode offhandHybrid`（举起后按开火），客户端每帧 `GetCrosshairTargetData`，RUI `ui/mortar_binoculars.rpak` | `rtxt:10`、`rnut:222-391` |
| 落点圈 | 粒子 `P_ar_target_fuse_instant`，控制点 2 = 420/20 | `rnut:236-241` |
| 抛物线显示 | 武器的抛物线指示器，脚本覆盖初速和时长（`SetIndicatorEffectVelocityOverride`） | `rnut:286-287`；被挡 → mod 换橙色，出界 → mod 关掉 |
| 主炮弹 | `FireWeaponGrenade(pos, vel = 解出的初速)`，客户端预测 | `rnut:443-452` |
| 弹道 | `SolveBallisticArc(起点, 定速, 空爆点, sv_gravity, 低弧)` | `wu:5556-5607`；`rnut:435-436` |
| 空爆 | 飞行线程：水平走过（目标距离 − 50）就把炮弹瞬移到空爆点 → 空爆；提前撞到东西也空爆 | `rnut:467-506`、`rnut:194-220` |
| 小炸弹 | 小炸弹武器（隐藏副手，`VerifyBombardmentWeapon`）逐个 `FireWeaponGrenade`，无敌，旋转 900°/s | `mnut:916-1032` |
| 落地 | 只在地面（法线·上 > 0.75）粘住；不粘玩家；弹 16 次以上强制落 | `mnut:165-235` |
| 落地推人 | 80 u 内、有视线、没冲刺且几乎不按方向的玩家：速度 + 350 沿"离心 / 向心"方向，5 伤害；`mortar_ring_push` 1 s 防重复 | `mnut:272-310` |
| 火墙段 | 两颗相邻炸弹都落地（或 2.5 s 超时）→ 沿地面连线 | `mnut:313-426` |
| 火墙判定 | `trigger_cylinder`（粗筛）+ 每帧"到线段最近点 ≤ 50 u、高度在 −5..+65、LOS" | `mnut:573-780` |
| 预燃 | 1 s，粒子 `P_mortar_preburn`；玩家 / NPC 5 伤害、其他 10，每个攻击者一次 | `mnut:536-548`、`mnut:781-812` |
| 燃烧 | 15 s，粒子 `P_wpn_mortar_firewall`；AI 危险区（半径 = 段长一半） | `mnut:550-570` |
| 燃烧伤害 | 线程：首跳 35，之后 8 ×（在火里 1.5），间隔 0.83 s，共 6 跳；减速 0.25 | `mnut:814-892` |
| 道具 / 陷阱 | `TryApplyingBurnDamage`（50 伤害、2.8 s、最多 4 层、0.7 s 间隔、1.2 s 跳） | `mnut:674-680`、`mnut:763` |
| 被烧屏幕 | 状态效果 `mortar_ring_burn` → 客户端调色 `mortar_fire.raw_hdr`（0.5 权重，1 s 淡入淡出）+ 粒子 `P_mortar_victim_burning_1p` | `mnut:1314-1357` |
| 声音 | 段上客户端环境声 `Firebomb_Mortar_Ring_Flame_Burn`（按线段发声）；被烧循环 `Firebomb_damaging_loop_1p/3p` | `mnut:1395-1434`、`mnut:832-840` |
| 威胁箭头 | 客户端：离最近一段火 ≤ 165 u 且有视线 → 屏幕箭头 | `mnut:1436-1549` |
| 揭示（扫描） | `MortarRingReveal_SonarThink` 存在，但调用被注释 → **不生效** | `mnut:941-942`、`mnut:1084-1123` |

服务端 / 客户端：瞄准和预览在客户端（结果通过 `Remote_ServerCallFunction` 改服务端武器 mod，只为抛物线颜色），开火两端都跑（客户端预测）；空爆、火墙、伤害只在服务端。

## 2. 流程

```
按大招（120/120）→ 举起发射器（raise 0.8 s）
 └ 客户端 WeaponActiveThread_Client（每帧）
     ├ 准星 trace（最远 7875）；水平距离 < 522 → 往前推到 522，向下找地
     ├ 空爆点 = 地面点 + (0,0,750)
     ├ 定速 v = lerp(距离, 0→7875, 2750→4000)；解低弧
     ├ 模拟落点 arcPos；arcPos 离空爆点 ≤ 50 → "有净空"（绿），否则"被挡"（橙，圈画在 arcPos 下方 750）
     ├ 超出 7875 / trace 没打到 → "出界"（红），禁止开火
     └ 炮管俯仰动画：pose param 0..150，每帧最多 ±7
开火（in range）→ OnWeaponPrimaryAttack：服务端重新算一遍 → LaunchBomb（扣 120）
 └ 炮弹按解出的初速飞（受 sv_gravity 750）
     ├ 每帧对准速度方向
     ├ 水平走过 (startDist − 50) → 瞬移到空爆点 → MortarRingAirburst
     └ 提前撞到（非自己、非投射物、合法位置）→ 在撞点 MortarRingAirburst
MortarRingAirburst（在空爆点）
 ├ 空爆特效 + 声音；删炮弹；给小炸弹武器
 ├ 15 个目标点：角度 i·24°，半径 420 × rand(0.7, 1.1)，高度 −750
 ├ 打乱顺序逐个发射，每第 3 个等 0.1 s（共约 0.5 s）
 │   初速 = SolveBallisticArc(空爆点, 375, 目标点)；无解则水平 375
 └ 每颗记下"环上顺序的下一颗"（trackedEnt），第 15 颗配第 1 颗 → 闭环
小炸弹落地（只认地面）
 ├ 落地爆：特效、80 u 内推人 + 5 伤害
 └ 等配对炸弹落地（最多 2.5 s）
     ├ 两颗水平距离 ≤ 450 → 一段火墙：从本颗沿地面走向配对颗（走不通就从两头各走一半）
     └ 否则 / 超时 → 单点火（半径 50）
火墙段：t=0 预燃 1 s → t=1 燃烧 15 s
 └ 人进入（胶囊判定 + LOS）
     ├ 预燃中：5 伤害（每个攻击者一次）
     └ 燃烧中：in_mortar_ring 状态；BurnDamageThink（每个攻击者一个线程）
         首跳 35 → 每 0.83 s 8（仍在火里 12）→ 共 6 跳 ≈ 4.15 s；全程减速 0.25、被烧屏幕
         6 跳打完线程结束；如果还站在火里，下一帧再开一个线程（又从 35 开始）（推断）
```

**伤害估算**（推断，按代码）：碰一下就走 = 35 + 5×8 = **75**（不含预燃）；一直站在火里 = 35 + 5×12 = **95** / 4.15 s，然后再来一轮（≈ 23 DPS 持续）。

打断：主人销毁时炮弹线程结束（炮弹 `Destroy`，`rnut:470-478`）；火墙不依赖主人存活。燃烧线程玩家死亡 / 图腾回溯 / `CleanUpPlayerAbilities` 结束（`mnut:816-822`）。

冷却：120 s（`rtxt:83-88`）。

## 3. 代码

### 3.1 入口

- `OnWeaponActivate_ability_mortar_ring`（`rnut:105-125`）：客户端开瞄准线程。
- `OnWeaponPrimaryAttack_ability_mortar_ring`（`rnut:160-192`）：

```
data = GetCrosshairTargetData(owner, minDist = 420×1.1+60 = 522, maxDist = 7875, airburst = 750)
if data.inRange:
    v  = GraphCapped(data.distance, 0, 7875, 2750, 4000)
    as = SolveBallisticArc(attackPos, v, data.airburstTarget, sv_gravity)
    arcPos = SimulateGrenadeImpactPos(as.fire_velocity, as.duration)
    inRange = |arcPos − 镜头| ≤ 7875
if inRange: LaunchBomb(...); return 120
else: 播"不能开火"声; return 0
```

注意服务端开火**只看 inRange，不看"有净空"**：被挡也能开火，炮弹会提前撞到障碍空爆（推断）。

### 3.2 核心逻辑

#### 3.2.1 弹道求解：`SolveBallisticArc`（`wu:5556-5607`）

定速 v、水平距离 x、高度差 y：

```
root = v⁴ − g(g·x² + 2·y·v²)；root < 0 → 无解
θ_low = atan2(v² − √root, g·x)       // 低弧（默认）
fire_velocity = 水平方向·cos θ·v + 上·sin θ·v
duration = x / (水平速度)
```

`GetCrosshairTargetData`（`wu:5609-5654`）：镜头 trace（忽略自己和 Crypto 无人机，遮挡体积算挡）；太近就沿视线水平方向推到最小距离再向下 250 找地。

#### 3.2.2 `BombFlightThread`（`rnut:467-506`）

```
startDist = 水平距离(起点, 空爆点)
每帧: 炮弹朝向 = 速度方向
      服务端: 已水平走过 ≥ startDist − 50 → SetOrigin(空爆点) → Airburst
```

即**不靠弹道精确打中空爆点**，而是"水平距离到了就传送过去"，弹道只是为了看起来对。

#### 3.2.3 `MortarRingAirburst`（`mnut:921-989`）+ `LaunchBomblet`（`mnut:991-1032`）+ `GetTargetPointsAroundOrigin`（`mnut:1056-1081`）

```
pts[i] = center + dir(i·360/15) × 420 × rand(0.7, 1.1) + (0,0,−750),  i = 0..14
randomized = shuffle(pts)
for k, p in randomized:
    if (k+1) % 3 == 0: wait 0.1
    thread LaunchBomblet(p): v = SolveBallisticArc(center, 375, p) 或 水平×375
                             bomb.dirFromCenter = flatten(p − center)
                             bomb.dirForFire   = dirFromCenter × up（切向）
配对: bomb(pts[i]).trackedEnt = bomb(pts[(i+1) % 15])
```

`radiusModMin/Max` 由调用方传入 0.7 / 1.1（`rnut:218`、`rnut:500`）。

#### 3.2.4 落地：`OnProjectileCollision_ability_mortar_ring_missile`（`mnut:165-235`）+ `BombletExplosion`（`mnut:257-347`）

```
碰撞：忽略自己 / 投射物 / 玩家 / 非法位置；bounce++；>16 强制
      法线·上 ≤ 0.75 或粘不上 → 继续弹
落地：隐藏、停物理；爆炸特效（朝向 −dirFromCenter）
      80 u 内玩家（非相位、无 push 状态、有 LOS）:
          push 状态 1 s
          if 没冲刺 且 输入幅度 < 0.45:
              v = (dirFromCenter · 指向玩家 > 0) ? dirFromCenter : −dirFromCenter
              玩家速度 += v × 350          // 在环外侧的推出去，内侧的推进来
          敌人或自己: 5 伤害
      等配对落地（≤ 2.5 s）→ BeginBombletFire
```

#### 3.2.5 火墙段几何：`BeginBombletFire`（`mnut:368-424`）+ `FindValidEndPosForFireSegment`（`mnut:446-504`）

```
if 没有配对 或 水平距离 > 450: 单点段（start = end）
else:
    e = 从 start 沿水平方向走向 partner：每步 15 u，在离地 60 u 处前向 trace，
        再向下 125 u 找地；撞墙、悬空、换了支撑物体就停
    if e 到 partner < 20: 一段 start→partner
    else: 两段 start→e 和 partner→(从 partner 往回走)
```

段挂到支撑物体上（移动平台），坐标存局部（`mnut:426-444`）。

#### 3.2.6 线段触发器：`MortarRingFireSegmentTriggerThread`（`mnut:573-640`）+ `MortarRingFireSegmentInTriggerThread`（`mnut:653-780`）

```
trigger_cylinder: 中心 = 段中点，半径 = 段长/2（单点 50），上 = 半高差 + 65，下 = 半高差
进入 → 线程（每帧，直到离开触发器）:
    p = 段上离目标最近点
    在火里 ⇔ 目标脚高 ∈ [p.z − 5, p.z + 60] 且 水平距离 ≤ 50 且 从 (p.x,p.y,脚高) 到目标有 LOS
    预燃段: 每个攻击者一次 PreburnDamageThink
    燃烧段: 玩家 / NPC → in_mortar_ring 状态 + BurnDamageThink（每个攻击者一个）
            其他（道具、陷阱、载具）→ TryApplyingBurnDamage
    不在火里 → 停 in_mortar_ring
```

判定实际上是一个**半径 50、高 65 的胶囊沿线段**；触发器只是粗筛。

#### 3.2.7 燃烧 DoT：`BurnDamageThink`（`mnut:814-892`）

```
move_slow 0.25（有 PAS_MOTHERLODE_RESISTANCE 的玩家不加）；mortar_ring_burn 状态
for tick = 1..6:
    mult = 有 in_mortar_ring ? 1.5 : 1
    dmg  = tick == 1 ? 35 : 8 × mult
    抗性玩家: tick 1 = 20，然后等 1 s 结束
    敌人或自己: TakeDamage(dmg, sourceId mp_weapon_mortar_ring)
    wait 0.83
```

`target.e.mortarRingBurnInflictors` 防止同一个 Fuse 的多段火叠多个线程（`mnut:731`）；**两个 Fuse 可以叠**（推断）。

### 3.3 客户端表现

- 瞄准：望远镜 RUI（`maxRangeDist`、`inRange`、`hasClearance`、`rangeDist`），落点圈 + 标记三色：绿 `<10,255,0>` / 橙 `<255,125,0>` / 红 `<255,10,0>`（`rnut:40-42`），进出射程有提示音（`rnut:29-33`）。抛物线 `P_arc_green`，被挡 mod 换 `P_arc_orange`（`rtxt:22-28`、`rtxt:224-235`）。
- 发射器炮管俯仰：`DoPoseParamLerp`（`rnut:393-413`），角度 25–180° 映射到 0–150。
- 火墙：每段一个客户端环境声，`SetSegmentEndpoints` 让声音沿线段（`mnut:1406-1410`）；威胁箭头取所有段声音位置中最近的一个（`mnut:1484-1496`）。小 bug：`shouldBeVisible` 一旦设 false 不会再设回 true，只靠 0.25 s 宽限显示（`mnut:1475-1517`，推断箭头会闪）。
- 被烧：调色 + 第一人称火焰粒子。

### 3.4 依赖

`SolveBallisticArc`、`GetCrosshairTargetData`（`wu`）、`VerifyBombardmentWeapon`（`_shared/A-bombardment.md` 3.1，和 Bangalore / Gibraltar 抢同一个副手槽）、`AI_CreateDangerousArea_Static`、`TryApplyingBurnDamage` / `BurnDamageSettings`（`_weapon_utility`，铝热剂同一套，见 APEX-REPORT 2.3）、`GetClosestPointOnLineSegment`、`CreateClientSideAmbientGeneric`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| MORTAR_RING_RADIUS | 420 | u | `rnut:45` | 预览圈；空爆环基准半径（`mnut:945` 写死 420） | |
| MORTAR_RING_NUM_MISSILES | 15 | 颗 | `rnut:47` | 小炸弹数 | 多 → 段更短、更密 |
| 环半径随机 | 0.7–1.1 | × | `rnut:52-53` | 环是"毛边"的 | |
| MORTAR_RING_AIRBURST_BASE_LAUNCH_SPEED | 375 | u/s | `rnut:51` | 小炸弹出射速度 | |
| MORTAR_RING_BOMB_AIRBURST_HEIGHT | 750 | u | `rnut:57` | 空爆高度 | |
| MORTAR_RING_LAUNCH_SPEED_MIN / MAX | 2750 / 4000 | u/s | `rnut:54-55` | 主炮弹定速（按距离插值） | |
| MORTAR_MIN_FIRE_DISTANCE | 420×1.1+60 = 522 | u | `rnut:70` | | |
| MORTAR_MAX_FIRE_DISTANCE | 7875（≈200 m） | u | `rnut:71` | | |
| 空爆提前量 | 50 | u | `rnut:491` | 水平距离差多少就传送 | |
| 净空判定 | 50 | u | `rnut:291` | | |
| 炮管俯仰 | 角 25–180 → 0–150，每帧 ±7，差 < 1 吸附 | — | `rnut:60-68` | | |
| 小炸弹最多弹跳 | 16 | 次 | `mnut:192` | | |
| 落地法线阈值 | 0.75 | cos | `mnut:201` | | |
| 落地推人半径 / 速度 / 伤害 | 80 / 350 / 5 | u / u/s / HP | `mnut:272`、`mnut:298`、`mnut:308` | | |
| 推人条件 | 没冲刺且输入 < 0.45 | — | `mnut:294` | | |
| mortar_ring_push 防重复 | 1.0（淡出 0.25） | s | `mnut:291` | | |
| MORTAR_RING_MISSILE_POST_IMPACT_LIFETIME | 2.5 | s | `mnut:36` | 等配对超时 | |
| MORTAR_RING_MISSILE_FIRE_DISTANCE_THRESHOLD | 450 | u | `mnut:34` | 配对能连的最大距离 | |
| FIRE_FWD_TRACE_HEIGHT / STEP / DOWN_TRACE | 60 / 15 / 125 | u | `mnut:30-32` | 地面走线 | |
| MORTAR_RING_MISSILE_FIRE_HEIGHT_THRESHOLD | 90 | u | `mnut:33` | 未用 | |
| MORTAR_RING_MISSILE_PREBURN_DURATION | 1.0 | s | `mnut:39` | | |
| MORTAR_RING_MISSILE_BURN_DURATION | 15.0 | s | `mnut:40` | | |
| MORTAR_RING_FIRE_SEGMENT_HEIGHT | 65 | u | `mnut:41` | 火的高度 | |
| MORTAR_RING_FIRE_SEGMENT_WIDTH | 50 | u | `mnut:42` | 离线段距离 | |
| MORTAR_RING_FIRE_SEGMENT_DEFAULT_RADIUS | 50 | u | `mnut:44` | 单点段 | |
| 判定下沿 | −5 | u | `mnut:704` | | |
| MORTAR_RING_FIRST_TICK_DAMAGE | 35 | HP | `mnut:52` | | |
| MORTAR_RING_SUBSEQUENT_TICK_DAMAGE | 8 | HP | `mnut:53` | | |
| MORTAR_RING_IN_FIRE_DAMAGE_MULTIPLIER | 1.5 | × | `mnut:46` | | |
| MORTAR_RING_MISSILE_NUM_TICKS | 6 | 跳 | `mnut:57` | | |
| MORTAR_RING_MISSILE_TICK_INTERVAL | 0.83 | s | `mnut:58` | | |
| MORTAR_RING_MISSILE_DAMAGE_PER_TICK | 12 | HP | `mnut:56` | 未用 | |
| 燃烧减速 | 0.25 | 严重度 | `mnut:828` | | |
| PREBURN_DAMAGE_PLAYER / NON_PLAYER | 5 / 10 | HP | `mnut:54-55` | | |
| 抗性升级首跳 | 20，之后无 | HP | `mnut:868-876` | 敌方 Fuse 升级（对玩家） | |
| NON_PLAYER 燃烧 | 50 dmg，2.8 s，4 层，0.7 s，1.2 s 跳 | — | `mnut:61-65` | 道具 / 陷阱 | |
| 威胁箭头距离 | 165 | u | `mnut:28` | | |
| 调色权重 / 淡入淡出 | 0.5 / 1.0 | — / s | `mnut:47-48` | | |
| 扫描（未生效） | 半径 300×高度比、长 1000、最短 350、18 s、125° 锥 | — | `mnut:70-72`、`mnut:1086-1100` | | |
| 扫描延长上限 | 4.0 | s | `mnut:76` | 升级，未生效 | |
| 中心伤害（升级，已删） | 5 / 2 s | — | `mnut:1136-1144` | | |
| 充能 | 120，1/s | — | `rtxt:83-88` | 120 s | |
| rtxt burn_* 字段 | burn_damage 25、burn_duration 15、burn_time 2.8、burn_tick_rate 1.2 … | — | `rtxt:107-120` | **脚本没读**（推断遗留，用的是 `mnut` 常量） | |

## 5. 未解决和要实测的

1. 燃烧伤害时间线（75 / 95、站着会不会每 4.15 s 重来）：火力训练场对 `npc_dummie` 放大招，runner 每 0.05 s 记血量。**NPC 也走 `BurnDamageThink`（`mnut:670` 把 NPC 算作 isPlayer）**，所以可以直接用 dummy 测，也能确认 NPC 吃减速。
2. 环的实际形状和段数：记录 15 颗 `mp_weapon_mortar_ring_missle` 投射物落点，看有没有没连上的段（超过 450 或被挡）。
3. 被挡时开火：对着近处墙上方的点开火，看炮弹在哪里空爆。
4. 落地推人：站在环线上，静止 vs 冲刺各测一次。
5. 服务端是否 SDK 改写：注释"todo: Upgrade Removed"（`mnut:1181`）是原版风格；扫描调用注释掉可能是原版移除。暂无明显 SDK 痕迹（推断）。

## 6. HSD 实现

**未实现**。这是批次 A 里 PvE 价值最高、部件最多的一项。建议拆成三个可复用部件，放在 `Runtime/Combat/`：

1. `ArcSolver`（放进 `Throw.cs` 的 `Ballistics`）：`SolveLowArc(from, to, speed, g)`，公式照 3.2.1；`Ballistics.PredictArc` 已能画抛物线，预览直接复用。
2. `GroundLineSegment`：给两点，按 3.2.5 用 `IMovementWorld.Blocked` / `SupportHeight` 沿地面走线（`Ordnance.cs` 的 Thermite 已有同样思路：步进 + 爬高 46 / 掉落 225 限制），输出一串点；判定 = 到折线最近点距离 ≤ 50、高度窗 65、`WorldClear`。
3. `BurnDot`：`Ordnance.cs` 的 `BurnTracker` 是铝热剂的"层"模型，和这里的"首跳 + 6 跳 + 在火里 ×1.5"不同，**另写一个**，不要硬塞进 `BurnTracker`。

主流程：`MotherlodeShell : ThrownItem`（`gravityScale = 1`，初速由 `ArcSolver` 给，飞到水平距离就空爆）→ 15 个 `MotherlodeBomblet : ThrownItem`（`OnBounce` 只认 `n.z > 0.75`）→ 配对连线 → `FireSegment : ICombatEntity`（预燃 1 s、燃烧 15 s）。减速复用 `CombatUnit.slowScale`。

和 R5 的差别（写进 `R5-DIFF-ARCHIVE.md`）：HSD 场景小，最大射程 7875 可能要改小；开关 `hsd.combat.ult.motherlodeRange`。
