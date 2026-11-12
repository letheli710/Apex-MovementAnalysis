# 公共部件 A：天降炮击（Bombardment 工具库）

批次 A 共用：Bangalore 滚雷用 `Bombardment_MortarBarrageDetCord`，Gibraltar 防御轰炸用 `Bombardment_MortarBarrageFocused`。另外两种（`Creeping`、`AirBurstFocused`）脚本里有、没人调用（`grep` 全库，2026-10-31）。静态研究，会话 combat-a。

来源根目录：`research-src/s21-platform/scripts/`。`bu` = `vscripts/mp/_bombardment_utility.gnut`（1044 行）。

## 0. 概要

- **部件**：一套"从头顶高处的一个点（或一排点）往地面目标点发射导弹"的工具函数，加地面落点取样。
- **一句话**：给一个投弹武器、一个"炮位"（玩家头顶 10000 u）、一个目标区域和节奏，就按图案（一条推进的线 / 一个圆里的随机点）分批发射，每发都是该武器的真导弹，落地后由武器自己的碰撞回调决定伤害。
- **分类**：系统（可复用的"区域炮击调度器"）；可视化（落点标记、空中呼啸声）。
- **可拆出的部件**：
  - 投弹武器挂载：`VerifyBombardmentWeapon` → 3.1
  - 推进式线形炮击（DetCord）→ 3.2.1
  - 推进式锯齿线炮击（Creeping，未用）→ 3.2.2
  - 圆形区域持续炮击（Focused）→ 3.2.3
  - 空爆一次性炮击（AirBurstFocused，未用）→ 3.2.4
  - 单发发射 + 落点标记 + 落地震屏：`MortarFromWeapon` → 3.2.5
  - 落点取样（圆内均匀、圆环内、圆周等分、能被天上打到的地面点）→ 3.2.6
  - 防刷声音：`PlayBombardmentImpactSoundIfNeeded` → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 炮弹 | 投弹武器 `FireWeaponMissile`（`speed = 1`、不随机、不预测） | `bu:458-467`。速度来自投弹武器 `.txt` 的 `projectile_launch_speed`（推断：`speed` 是倍率，见第 5 节） |
| 投弹武器 | 玩家身上的隐藏副手 `OFFHAND_RIGHT` | `bu:72-84`；伤害和碰撞在该武器的脚本里 |
| 炮位 | 玩家脚下 + (0,0,10000)（地图有状态效果 `bombardment_uses_extended_height` 时 25000） | 调用方传入；常量 `bu:29-30` |
| 落点 | `OriginToGround(点 + (0,0,高))` 往下找地面（引擎） | `bu:556` 等 |
| 落点标记 | 武器给的 `markerFx` 粒子，导弹销毁时停 | `bu:497-522`。滚雷传 `$""`（没有标记），防御轰炸传 `P_ar_artillery_marker` |
| 呼啸声 | `sound_incoming_first`（开始一次）、`sound_incoming`（逐发） | `bu:93-98`、`bu:352-357` |
| 落地震屏 | `CreateShake(target, 振幅5, 频率150, 1 s, 半径1000)`，空中也震 | `bu:488-491` |
| AI 威胁 | 调用方另行 `ThreatDetection_CreateThreatZoneForBombardment`（只有 Gibraltar 调） | `mp/_threat_detection.gnut:302` |

全部是服务端。客户端只看到导弹、粒子、声音。

## 2. 流程

```
调用方（技能的投掷物落地）
 └ thread Bombardment_xxx( 投弹武器, 标记, 炮位, 目标, 图案参数, delay )
     ├ 播 sound_incoming_first
     ├ wait delay
     ├ 按图案生成全部落点（一次算好）
     └ 按节奏逐批 thread MortarFromWeapon( 单发延迟 )
         ├ wait 单发延迟
         ├ FireWeaponMissile( 炮位 → 落点 方向 )
         ├ 落点标记（导弹活着时显示）
         └ 导弹销毁 → 落点震屏
导弹碰撞 → 投弹武器的 OnProjectileCollision（伤害 / 延时引爆，见各技能）
```

打断：线程 `EndSignal(weapon, "OnDestroy")` 和 `EndSignal(owner, "CleanUpPlayerAbilities")`（`bu:89-91`、`bu:445-447`）。**主人死亡不打断**（死亡不发 CleanUpPlayerAbilities，推断），换角色 / 回合结束才清。

## 3. 代码

### 3.1 入口：`VerifyBombardmentWeapon`（`bu:72-84`）

```
w = player.offhand[RIGHT]
if w 存在且不是 weaponName: 拿掉
if 没有: 给 weaponName
return 该副手
```

同一个槽也被 Fuse 大招的小炸弹武器、Maggie 破坏球的碎片武器复用（`VerifyBombardmentWeapon(owner, "mp_weapon_mortar_ring_missle")`、`"mp_ability_rolling_thunder_piece"`）。**一个玩家同时只能有一种投弹武器**，换了就会让上一种的线程 `weapon OnDestroy` 结束（推断：同时放两种炮击会互相打断）。

### 3.2 核心逻辑

#### 3.2.1 DetCord 线形推进（`bu:348-441`，Bangalore 用）

```
creepDist = stepLength × stepCount
cross = dir × up                         // 线的横向
n = floor(width / stepLength)            // 每步发数
spacing = width / n
gunPos = gunOrigin + dir × creepDist/2   // 炮位挪到整条线中间上空
for i in 0..stepCount-1:
    起点 = targetOrigin + dir×stepLength×i + cross×width/2
    targets[i][j] = Ground( 起点 - cross×spacing×j + (0,0,4000) ),  j = 0..n-1
    if i 为奇数: 反转顺序（之字形，DETCORD_ZIGZAG_PATTERN = true）
每步（间隔 stepInterval）:
    每发 j 延迟 j × (stepInterval / n)
    落点再在 128 u 圆内随机漂移（Bombardment_GetRandomGroundPosInCircle）
    投弹声 "Bangalore_Ultimate_Rocket_Trails"
```

#### 3.2.2 Creeping 锯齿（`bu:241-343`，未用）

和 3.2.1 的差别：偶数列落点前移一个 stepLength（锯齿）；每发有自己的炮位（一排，横向排开，+4000 u）；单发延迟随机 0.125–0.5 s。

#### 3.2.3 Focused 圆形（`bu:87-164`，Gibraltar 用）

```
zones   = 圆周等分 density 个点（半径 radius/2）          // Bombardment_GetDistributedRandomGroundPositionsInCircle
targets[z] = 以 zone 为圆心、半径 radius/4 的圆周等分 density 个点   // 函数内部 subRadius = 传入半径/2
while 时间 < duration:
    打乱 zones 顺序、打乱每个 zone 内顺序
    for i in 0..density-1:                // 每 1.0 s 一轮
        每个 zone 发 1 发 → 落点 targets[z][i]，单发延迟随机 0.25–1.0 s
        wait 1.0
```

注意：`calculationOffset = 2000` 只用于往下找地（`bu:106`）；`driftTarget` 算了没用（`bu:143`，落点不漂移）。函数名叫 "Random" 实际是**等角取点**（`bu:561-587`），随机性只来自顺序打乱和单发延迟。每波每个区 1 发 = density 发，共 density 波 = 36 发（density = 6）。

**落点几何**（density 6、radius 1024）：区中心在离目标 512 u 的圆上（每 60° 一个），每区 6 个落点在离区中心 256 u 的圆上。所以 36 个落点**全部离目标 256–768 u，目标点本身和 256 u 以内没有落点**（只有 40 伤害 r256 的爆炸边缘能扫到中心，推断）。实际是一个"甜甜圈"。循环条件每走完一整轮 `for`（6 s）才检查一次，所以 `duration = 6` 时实际只打**一整轮 6 波 = 36 发**（推断，按代码：for 内 6 次 wait 1.0 = 6 s，之后 while 条件不满足）。

#### 3.2.4 AirBurstFocused（`bu:167-237`，未用）

一次性：zones 半径 radius/3，所有落点 0 延迟同时发射。

#### 3.2.5 单发：`MortarFromWeapon`（`bu:443-495`）

```
wait delay
missile = weapon.FireWeaponMissile( pos=炮位, dir=normalize(落点-炮位), speed=1 )
标记延迟 = (炮位高度差 - 10000)/10000 × 2.1          // 默认高度时为 0；25000 时 3.15 s
thread 落点标记（延迟后显示，导弹销毁时停）
等导弹销毁 → CreateShake(落点, 5, 150, 1, 1000)
```

#### 3.2.6 落点取样

| 函数 | 行 | 作用 |
|---|---|---|
| `Bombardment_GetRandomGroundPosInCircle` | `bu:545-559` | 圆内**面积均匀**随机点：r = √b × R |
| `Bombardment_GetDistributedRandomGroundPositionsInCircle` | `bu:561-587` | 圆周等分点（半径 = 传入/2） |
| `Bombardment_GetRandomGroundPosInRing` | `bu:590-615` | 圆环内均匀随机点 |
| `Bombardment_GetGroundPositionsOnCircleEdge` | `bu:618-648` | 圆周等分（含 printt 调试） |
| `Bombardment_GetGroundPositionsForRingOfCircles` | `bu:651-686` | 一圈相切的小圆 |
| `Bombardment_GetWeightedGroundPosInRadius` | `bu:695-` | 按权重找能放下 hull、能从天上打到的地面点 |

### 3.3 声音防刷

`PlayBombardmentImpactSoundIfNeeded`（`bu:1002-1025`）：每个主人 12 s 内只播一次"持续落弹"声（防御轰炸有声音，滚雷的是占位注释）。

### 3.4 依赖

`OriginToGround`（引擎）、`FireWeaponMissile`、`AddToUltimateRealm`、`CreateShake`、`StartParticleEffectInWorld_ReturnEntity`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| DEFAULT_BOMBARDMENT_HEIGHT | 10000 | u | `bu:29` | 炮位高度 | 大 → 炮弹飞得久、预警长 |
| EXTENDED_BOMBARDMENT_HEIGHT | 25000 | u | `bu:30` | 特定地图（`mp_rr_canyonlands_mu1/mu3_common.nut`）用 | |
| 落点上探高度 | 4000 | u | `bu:297`、`bu:393` | 找地面时从多高往下找 | 小 → 屋顶下面可能找不到 |
| DetCord 落点漂移 | 128 | u | `bu:438` | 每发随机偏移半径 | |
| Creeping 漂移 / 单发延迟 | 128 / 0.125–0.5 | u / s | `bu:337-340` | 未用 | |
| Focused 单发延迟 | 0.25–1.0 | s | `bu:144` | 同一波里的散布 | |
| Focused 波间隔 | 1.0 | s | `bu:159` | | |
| Focused calculationOffset | 2000 | u | `bu:106` | 找地起点偏移 | |
| AirBurst calculationOffset | 200 | u | `bu:185` | | |
| 落地震屏 | 振幅 5，频率 150，1 s，半径 1000 | — | `bu:488` | | |
| 标记延迟系数 | 2.1 | s / 10000 u | `bu:472` | 高炮位时标记晚出现 | |
| 声音防刷 | 12 | s | `bu:31-32` | | |

## 5. 未解决和要实测的

- **`FireWeaponMissile` 的 `speed = 1` 是倍率还是绝对速度**：如果是倍率，滚雷炮弹 12000 u/s（10000 u 落差约 0.83 s），防御轰炸 4500 u/s（约 2.2 s，和"标记延迟系数 2.1"吻合，推断是倍率）。测法：火力训练场放 Gibraltar 大招，runner 每 0.05 s 记录 `mp_weapon_defensive_bombardment_weapon` 投射物位置，算速度。
- Focused 实际打几波（推断 6 波 36 发）：同一次实测数导弹数量。
- 两种投弹武器争 `OFFHAND_RIGHT` 是否互相打断：同一玩家先放 Gibraltar 大招，炮击中途切 Fuse 放大招（需要能同时有两个大招的测试角色），看炮击是否停。
- 主人死亡后炮击是否继续：放完大招立刻 `kill` 自己。

## 6. HSD 实现

**未实现**。建议在 `Runtime/Combat/` 新建 `Bombardment.cs`：

- `BombardmentScheduler : ICombatEntity`：持有一列 `(fireAt, from, to)`，`Step` 时到点就生成一个 `Shell`（可以直接派生 `ThrownItem`，`ThrowParams{ gravityScale = 0, stick = true }`，速度给定），图案生成器做成静态函数：`DetCordPattern(...)`、`FocusedPattern(...)`、`CreepingPattern(...)`，照 3.2 的伪代码。
- 落点找地：用 `IMovementWorld.SupportHeight`（`Ordnance.cs` 的 Thermite 已在用）。
- 伤害交给 `CombatSim.Explode`（线性衰减 + 墙挡，已有）。
- PvE 可以把炮位高度降到 3000–5000 u，让玩家看得见炮弹落下（R5 的 10000 u 在 HSD 场景里多半看不见）；这是可选差别，开关 `hsd.combat.bombardHeight`。
