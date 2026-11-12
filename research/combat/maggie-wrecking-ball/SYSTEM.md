# Mad Maggie 大招 Wrecking Ball（破坏球）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_wrecking_ball.nut`（2214 行），`txt` = `weapons/mp_ability_wrecking_ball.txt`，`ptxt` = `weapons/mp_ability_rolling_thunder_piece.txt`，`mc` = `vscripts/weapons/mp_weapon_maggie_common.nut`。静态研究，2026-10-31，会话 combat-a。

> **重要警告**：本地这份服务端脚本的"球怎么滚"部分**很可能被 SDK 社区重写过**（证据见 1.1）。滚动、爆炸次数、伤害数值都要实测后才能当 R5 数据用。加速片（magnet / speed trigger）部分看起来是原版。

## 0. 概要

- **技能**：Mad Maggie / 大招 / Wrecking Ball / `mp_ability_wrecking_ball`（内部代号 RollingThunder，碎片武器 `mp_ability_rolling_thunder_piece`）。
- **一句话**：扔出一个球，落地后变成一个自己往前滚的物理球（最多 10 s），沿路每 0.8 s 左右交替甩出一片"磁片"，磁片落地后 60 s 内是一个半径 88 的加速区（+0.15 速度、滑铲时地面摩擦 −0.5）；球靠近敌人（225 u）就爆炸（伤害 + 震荡 + 击退），时间到也爆。
- **分类**：好技能（追着敌人滚的炸弹 + 震荡 + 击退）；系统（**自走物理体 + 撞墙反射 + 路径邻近检测**、**一路投放**、加速 / 低摩擦区、设备 EMP 列表）；可视化（球展开动画、地面磁片、玩家加速身体特效和屏幕特效、颜色随剩余时间变化）。
- **可拆出的部件**：
  - 投掷物落地换成物理实体（保留动画子模型）→ 3.2.1 `WreckingBall_DestroyProjectileAndSpawnBall`
  - 自走滚动 + 撞墙水平反射 + 低速补推 → 3.2.2 `WreckingBall_GetTheBallRolling`
  - 沿路径段的邻近检测（防高速穿过）→ 3.2.3 `WreckingBall_CheckForNearbyEnemies`
  - 一路投放（定时、左右交替、斜下抛）→ 3.2.4 `WreckingBall_SpawnRepulsorPropFromEntity`
  - 投放物间距去重（新的溶解 80 u 内旧的）→ 3.2.4 `OnMagnetExplosionDamage`
  - 加速 / 摩擦区（进出计数、离开后余留 2 s）→ 3.2.5 `WreckingBall_OnTriggerEnter/Leave`、`WreckingBall_InWakeThink`、`WreckingBall_PostWakeThink`
  - 爆炸后 shellshock + 击退（每人一次）→ 3.2.6 `OnWreckingBallDamaged` + `mc` `MaggieCommon_KnockbackTargetFromEntity`
  - 设备 EMP（注册表 + 路径距离）→ 3.2.7
  - Shellshock → `_shared/A-shellshock.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 扔球 | `FireWeaponGrenade(vel = 出手方向, angVel <10,1600,10>)`；600 u/s，仰角偏移 25°，继承 ×0.2，hull ±16 | `nut:395-440`；`txt:40-41`、`txt:75-77`、`txt:89` |
| 展开动画 | 动画子模型 `madmaggie_ultimate_ball`，`ultimate_ball_expand` → `ultimate_ball_idle`；主体先隐藏 | `nut:331-334`、`nut:540-616` |
| 落地变球 | 碰撞 → 删投射物 → `prop_physics`（`madmaggie_ultimate_ball_static`，VPHYSICS，重力 1），子模型移过去 | `nut:373-393`、`nut:618-697` |
| 滚 | 脚本每 0.2 s：前方 100 u hull trace，撞墙就把方向按法线水平反射；速度 < 400 时重新设速度 = 方向×600 + 上 150 | `nut:853-888` |
| 半径特效 | `P_mm_roll_ball_hld`，控制点 1 = 225 − 25 | `nut:769-776` |
| 威胁指示 | `CreateThreatIndicator(GRENADE_INDICATOR_GENERIC, 300 + 100)` 挂在球上 | `nut:779-782` |
| 邻近检测 | 每 0.2 s：球这一段路径（上一位置 → 现在）225 u 内的敌方玩家 / 分身 / 战斗 NPC，非相位非隐身，有视线 | `nut:1243-1280`、`nut:1627-1668` |
| 爆炸 | `Explosion_DamageDefSimple(damagedef_wrecking_ball)` + 震屏 + 两片磁片 | `nut:1282-1344` |
| 伤害数值 | 本地 damagedef：300 / 重甲 500，内 100 外 200，推力 3000 | `damage/damagedefs.txt:117-128`（**和 `nut:32` 注释的 20 对不上**，见第 5 节） |
| 震荡 + 击退 | 伤害回调：每个受害者第一次 → 玩家 shellshock 3–6 s；击退 300（队友 200，0 伤害、震荡 3 s） | `nut:470-524`；`mc:84-107` |
| 一路投放 | 每 0.8 s 一片磁片（`prop_physics` debris，不实体，100 血），左右交替斜下甩出；全局最多 48 片 | `nut:1068-1088`、`nut:1671-1774` |
| 加速区 | 磁片一生成就挂一个 `trigger_cylinder`（r88，高 16），**飞行中就生效** | `nut:1807-1837`、`nut:1350-1406` |
| 加速 | 在区里：`speed_boost 0.15`（不限时）；离开：`speed_boost 0.15` 2 s | `nut:1438`、`nut:1497-1498` |
| 低摩擦 | 在区里滑铲 → `SetGroundFrictionScale(−0.5)`；不滑 → 0.75；离开后 2 s 0.75，然后 1.0 | `nut:1507-1514`、`nut:1554-1584` |
| 加速表现 | 胸口粒子 `P_mm_boost_body_human`（对友军和敌人可见）、第一人称屏幕粒子 `P_mm_player_boost_screen`、颜色随剩余时间变（黄 → 白）；Octane 兴奋剂 / 相位中不画 | `nut:1534-1625`、`nut:1949-1996` |
| 磁片寿命 | 落地 60 s；落地时 1 伤害 r80 的爆炸让 80 u 内的旧磁片溶解 | `nut:1839-1922`、`nut:526-538` |
| 设备 EMP | 全局两个注册表：要摧毁的（路径 400 u 内 → `Signal("EMP_Destroy")`）、要伤害的（路径 100 u 内 → 300 伤害） | `nut:959-1037`、`nut:1206-1224` |
| 门 | 原生回调 `CodeCallback_WreckingBallWallCheck`：碰到门 → 20 伤害（`riot_shield_impact`） | `nut:2184-2203` |

### 1.1 SDK 重写的证据

- 客户端注册的类是 `prop_rollingthunder`（`nut:282`），原生回调叫 `CodeCallback_WreckingBallImpact` / `WallCheck`（`nut:2126`、`nut:2184`）——原版的球是**引擎里的专用实体类**，滚动由引擎做；本地服务端却 `CreateEntity("prop_physics")`（`nut:632`）然后脚本每 0.2 s 手动推（`nut:854`、`nut:884-888`）。
- 原版滚动用的常量 `Z_BOUNCE_POWER_*`、`CANNOT_MOVE_COUNT_MAX`、`CHECK_FOR_GROUND_DELAY`（只用作 wait）、`FORWARD_TRACE_OFFSET`、`WRECKING_BALL_PROXY_DELAY 0.5` 等定义了但没用（`nut:36`、`nut:701-717`）。
- `CafeMod_*`（`big_balls`、`maggie_mitosis` 分裂球、实体数量上限）、`try/catch` 包实体创建、`Warning("Maggie ball exploded")`（`nut:1292`）都是社区风格。
- 铝热剂升级的 `BeginProjectileFire` 是空函数（`nut:1140-1143`）→ 升级"球爆后变铝热剂"不生效。
- 升级一"扫描附近敌人"只剩喊话，路点创建被删（`nut:916-923`）。
- `damagedef_wrecking_ball` 300 伤害和脚本注释的 20 不符。

## 2. 流程（按本地脚本）

```
按大招（120/120）→ 拿出 0.05 s → 扔（600 u/s，仰角 +25°）
球（投射物）旋转飞行，同时展开动画
碰到任何东西 → 换成物理球，方向 = 出手方向的水平分量 → WreckingBall_GetTheBallRolling
 t=0  速度 = 方向×800 + 上 300
 循环（每 0.2 s），直到 10 s：
   ├ 前方 100 u 撞墙 → 方向水平反射
   ├ 速度 < 400 → 速度 = 方向×600 + 上 150
   ├ （升级二）1 s 后点火特效
   ├ 设备 EMP：路径 400 u 内要摧毁的、100 u 内要伤害的（各一次）→ 警告声
   ├ 邻近检测：
   │    已触发 且 过了重触发延迟：
   │        第 1 次 → CreateExplosion（球继续滚），重触发延迟 2 s
   │        第 2 次 → 跳出循环
   │    未触发 且 检测到敌人 → 标记触发 + 警告声（下一轮 0.2 s 后爆）
   └ 每 0.8 s：甩一片磁片（左右交替）
 结束（10 s 或第 2 次触发）→ 最终爆炸（+ 两片磁片）→ 删球
磁片：飞行中就有加速区 → 落地停住、溶解 80 u 内旧磁片 → 60 s 后消失
玩家踩进加速区 → +0.15 速度、低摩擦 → 离开后余留 2 s
```

即本地脚本里一个球**最多爆两次**（第一次邻近爆炸后继续滚，2 s 后再碰到敌人才结束），官方是碰到敌人爆一次（**记忆，未查证**）。

冷却：120 s（`txt:43`、`txt:56-61`）。`balance_wreckingBallPauseRegen` 默认 false（`nut:225`），充能不暂停。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_WeaponWreckingBall`（`nut:300-360`）：存出手参数、`WreckingBall_Launch`、动画子模型。
- `OnProjectileCollision_ability_WreckingBall`（`nut:372-393`）：换物理球、开滚。

### 3.2 核心逻辑

#### 3.2.1 投射物 → 物理球（`nut:618-697`）

`prop_physics`，`massScale = modelScale`，主人 realm，队伍 = 主人队，`SetForceVisibleInPhaseShift`；动画子模型改挂到新球，本地角度 +90° pitch。

#### 3.2.2 滚动（`nut:699-1138`，本地版）

```
dir = 水平出手方向；vel = dir×800 + (0,0,300)
loop every 0.2 s while t < 10:
    tr = TraceHull(pos+16 → pos+dir×100+16, ±16×0..32, NPCSOLID)
    if 撞到: dir = reflect(dir, n) 后水平化归一
    if |vel| < 400: vel = dir×600 + (0,0,150)
```

#### 3.2.3 邻近检测：`WreckingBall_CheckForNearbyEnemies`（`nut:1243-1280`）

```
候选 = GetPlayerArrayEx / 分身 / GetNPCArrayEx 在 (225×2 + 这一步走的距离) 内，过滤 ShouldWreckingballHitEntity
for e: p = 线段(上一位置, 现在) 上离 e 最近点；|e − p| > 225 → 跳过（有父物体也要满足）
       TraceLine(球+40, e+40, NPCSOLID_BRUSHONLY)：打到 e / e 的父物体 / fraction ≥ 0.95 → true
```

`ShouldWreckingballHitEntity`（`nut:1652-1668`）：同 realm、非相位、**非隐身**、非友军、NPC 不是非战斗 AI。

#### 3.2.4 一路投放：`WreckingBall_SpawnRepulsorPropFromEntity`（`nut:1671-1774`）

```
throwDir = 球水平速度方向 + 侧向（左右交替）：(∓dir.y×0.5, ±dir.x×0.5, −0.5)
起点 = 球心 + (throwDir.xy × 15, 10)
速度 = throwDir × 200 × rand(0.75, 1.75)
prop_physics debris，不实体，阻尼 (0, 100)
thread AirThink（立刻建加速区 + 飞行粒子）
等第一次碰撞 → 阻尼 (1, 100)、速度清零、特效表 mm_ball_pcs_initialimpact
GroundThink：RadiusDamage(1, r80, puck) → 溶解 80 u 内其他磁片；地面粒子；60 s
```

最终爆炸额外甩两片：`dir ± 垂直方向`（`nut:1332-1338`）。

#### 3.2.5 加速区（`nut:1350-1625`）

```
trigger_cylinder r88，上 16、下 0，过滤全部，挂在磁片上
Enter（只认玩家、同 realm、不在滑索上）:
    第一次碰任何区 → 开记录（统计距离）
    从 0 个区变 1 个 → speed_boost(0.15) 不限时；声音；InWakeThink
    已在别的区里 → 计数 +1
Leave → 计数 −1；到 0 → Signal LeftSpeedZone
InWakeThink（每帧）: 滑铲 → 摩擦 −0.5；不滑 → 0.75；画加速特效
    结束 → 停不限时加速，加 speed_boost(0.15, 2 s, 淡出 0.25) → PostWakeThink
PostWakeThink: 摩擦 0.75，2 s 后（没再进区）→ 摩擦 1.0，清特效
```

**没有队伍判断**：敌方玩家踩到也加速（推断，`WreckingBall_ValidateEntityInWake` `nut:1593-1608` 只看是不是玩家）。NPC 不加速。

#### 3.2.6 爆炸伤害回调：`OnWreckingBallDamaged`（`nut:470-524`）

```
受害者是磁片 → 0
T_full = 球 spawnTime + 3
shellshock = 6
if now < T_full:
    frac = (T_full − now) / 3                // 刚出生 ≈ 1，快满 3 s ≈ 0
    shellshock = 3 + (6 − 3) × frac
队友（非自己）→ 伤害 0、shellshock 3、击退 200
第一次被这个……（全局表 hasBeenHit）:
    玩家 → shellshock
    击退：方向 = (目标 + 40) − (球 − 40)，水平 × 力度，竖直固定 300；玩家 KnockBack 0.25 s；NPC 在地面 ×1、空中 ×0.1
```

**疑点**：`frac` 公式和注释"充能时间不够就按进度比例给"相反——刚出生给满 6 s，接近 3 s 时降到 3 s，过了 3 s 又回到 6 s（推断 bug，应为 `(now − spawn) / 3`）。`hasBeenHit` 是全局表，球线程结束时整个清空（`nut:828`）。

#### 3.2.7 设备 EMP（`nut:959-1037`、`nut:2126-2177`）

其他技能用 `AddWreckingBallEMPDestroyDevice` / `AddWreckingBallEMPDamageDevice` 把自己注册进来（例如电桩、摄像头，见 `mc:15-23` 的 `destroyTrapNames`），球路过时摧毁或打 300。

### 3.3 客户端表现

展开动画、半径圈、威胁指示、磁片地面粒子 `P_mm_roll_pcs_hld` + 特效表 `mm_ball_pcs`（1 s 重放）、加速身体粒子（颜色 `COLOR_SPEEDBOOST_START/MID/END`，`nut:80-82`）、第一人称加速屏幕特效（`nut:1949-1996`）、击杀回放镜头（`nut:2207-2213`）。

### 3.4 依赖

`VerifyBombardmentWeapon`（拿碎片武器 `mp_ability_rolling_thunder_piece`，`nut:755`，但后面没用它发射，推断遗留），`_shared/A-shellshock.md`，`mc`，`Explosion_DamageDefSimple`，状态效果 `speed_boost`，`SetGroundFrictionScale`（引擎），`CreateThreatIndicator`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| WRECKING_BALL_BALL_DURATION | 10.0 | s | `nut:34` | 球最长寿命 | |
| WRECKING_BALL_WAKE_DURATION | 60.0 | s | `nut:35` | 磁片寿命 | |
| WRECKING_BALL_WAKE_BUFF_DURATION | 2 | s | `nut:37` | 离开区后余留（**playlist 键写成了 `wrecking_ball_wake_duration_override`，和寿命共用**，`nut:233-234`） | |
| WRECKING_BALL_WAKE_BUFF_SEVERITY | 0.15 | 严重度 | `nut:42` | 加速 | |
| 区内滑铲摩擦 / 区内不滑 / 离开后 | −0.5 / 0.75 / 0.75（2 s 后 1.0） | × | `nut:1507-1508`、`nut:1554` | | |
| WRECKING_BALL_SPEED_TRIGGER_RADIUS / HEIGHT | 88 / 16 | u | `nut:46-47` | | |
| 磁片间隔 | 0.8 | s | `nut:703` | | |
| 磁片抛出 | 速度 200 × 0.75–1.75，侧 0.5，下 −0.5，偏移 15 / 10 | — | `nut:715-716`、`nut:1673-1677` | | |
| 磁片血 | 100 | HP | `nut:1678` | | |
| 磁片去重半径 | 80 | u | `nut:1845` | | |
| MAGGIE_MAX_MAGNETS | 48 | 片 | `nut:62` | SDK 上限（推断） | |
| WRECKING_BALL_PLAYER_PROXIMITY_DIST | 225 | u | `nut:45` | 邻近爆炸距离 | |
| RETRIGGER_DELAY | 2.0 | s | `nut:56` | 两次爆炸间隔 | |
| WRECKING_BALL_PROXY_DELAY | 0.5 | s | `nut:36` | **未用**（实际 0.2 s） | |
| 滚动初速 / 补推 / 补推阈值 | 800+300↑ / 600+150↑ / 400 | u/s | `nut:854`、`nut:884-888` | 本地版 | |
| 撞墙探测 | 前 100 u，hull ±16×0..32 | u | `nut:866-867` | | |
| 循环间隔 | 0.2（两次 0.1） | s | `nut:858`、`nut:1092` | | |
| WRECKING_BALL_FORCE_TO_MOVE | 600 | — | `nut:49` | 原版"每次弹跳推力"，本地当速度用 | |
| WRECKING_BALL_TRACE_RADIUS | 40 | u | `nut:50` | 检测抬高 / 击退源偏移 | |
| damagedef_wrecking_ball | 300 / 重甲 500，r 100 / 200，推力 3000 | — | `damagedefs.txt:117-128` | 待实测 | |
| WRECKING_BALL_DAMAGE_FINAL | 20 | HP | `nut:32` | 注释说"见 damagedef"，只用于门 | |
| WRECKING_BALL_FINAL_EXPLOSION_RADIUS | 300 | u | `nut:33` | 只用于威胁指示（+100） | |
| Shellshock 最短 / 最长 / 队友 / 满充时间 | 3 / 6 / 3 / 3 | s | `nut:38-41` | | |
| 击退 敌 / 友 | 300 / 200（竖直固定 300） | u/s | `nut:43-44`；`mc:93` | | |
| 设备摧毁 / 伤害范围 | 400 / 100（伤害 300） | u | `nut:52-53`、`nut:959`、`nut:998`、`nut:1035` | | |
| 升级二点火 | 1.0 s 后 | s | `nut:245` | 只有特效（BeginProjectileFire 为空） | |
| 升级一扫描 | 400 u | u | `nut:244` | 只喊话 | |
| 扔出速度 / 仰角 / 继承 | 600 / 25 / 0.2 | u/s / ° / × | `txt:40-41`、`txt:89` | | |
| 投射物 hull | ±16 | u | `txt:75-76` | | |
| 充能 | 120，1/s | — | `txt:43`、`txt:56-61` | 120 s | |
| ptxt explosion 字段 | 0 伤害，r350，推力 30000 | — | `ptxt:36-40` | 碎片武器没被用来发射，不生效 | |

## 5. 未解决和要实测的

1. **爆炸伤害到底是 300 还是 20**（最重要）：火力训练场对 `npc_dummie` 放大招，记血量。如果 300，就是本地 damagedef 被改过；官方数值要另查（**不要用 300 设计 HSD**）。
2. **球的运动**：runner 每 0.05 s 记录 `wreckingball_ball` 位置和速度，看是不是"每 0.2 s 一次补推"的锯齿形速度（本地版），撞墙是否水平反射。
3. 爆炸次数（本地推断最多 2 次）：让球穿过两个分开的 dummy。
4. shellshock 时长曲线（推断 bug）：在球出生 0.5 s / 2.5 s / 4 s 时让它碰到玩家，记 shellshock 时长。需要第二个玩家，低优先级。
5. 敌人踩加速区是否加速：需要两个玩家，低优先级；HSD 里自己决定。
6. 磁片飞行中就有加速区：观察即可。

## 6. HSD 实现

**未实现**。移动研究那边已经有加速 / 地面摩擦相关的电机参数（`R5MotorV2`），**加速片部分适合先做**（纯移动，和 Octane 跳板一样能单独验收）：

- `SpeedPad : ICombatEntity`：圆柱 r88、高 16、寿命 60 s；玩家在里面 → 速度加成 0.15、滑铲时地面摩擦 ×(−0.5)；离开余留 2 s。需要电机提供"速度倍率"和"地面摩擦倍率"两个外部输入（`R5MotorV2` 目前没有，属于移动线，要和移动会话商量接口）。开关 `hsd.combat.ult.wreckingBallPads`。
- 球本体：`WreckingBall : CombatUnit`（可被打？R5 不可），每 0.2 s 按 3.2.2 推（或者等实测后照原版改），撞墙用 `IMovementWorld.Blocked` 反射；邻近检测照 3.2.3（线段最近点 + `WorldClear`）；爆炸走 `CombatSim.Explode`，击退复用 `CombatSim.Push`。
- 一路投放（`SpawnRepulsorProp`）做成通用的 `TrailDropper` 部件：给一个移动实体、间隔、左右交替、抛射速度，就能"沿路留东西"（以后火焰轨迹、地雷轨迹都能用）。
- shellshock：`_shared/A-shellshock.md` 第 6 节；时长公式用注释写的意图（`(now − spawn) / 3`），差别写进 `R5-DIFF-ARCHIVE.md`。
