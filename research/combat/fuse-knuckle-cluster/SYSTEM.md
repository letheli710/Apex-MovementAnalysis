# Fuse 战术 Knuckle Cluster（指节集束弹）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_cluster_bomb_launcher.nut`（571 行），`ltxt` = `weapons/mp_weapon_cluster_bomb_launcher.txt`，`btxt` = `weapons/mp_weapon_cluster_bomb.txt`。静态研究，2026-10-31，会话 combat-a。

**已有研究**：弹道、三层参数、递归结构、伤害规则、冷却见 [APEX-REPORT 2.7](../../../../TF2-Research/expansion/apex/APEX-REPORT.md)（下称 AR2.7），本文不重复，只补它没写的：完整时间线、伤害计数细节、两波的差别、一个疑似笔误、AI 危险区、升级、可拆部件。

## 0. 概要

- **技能**：Fuse / 战术 / Knuckle Cluster / `mp_weapon_cluster_bomb_launcher`（发射的主弹）+ `mp_weapon_cluster_bomb`（子弹的武器）。
- **一句话**：4400 u/s 直射一颗粘弹（能粘在敌人身上），1.7 s 后主爆一次，然后在原地两侧弹出子弹，子弹爆时再弹出下一层（2 → 4 → 16，共 22 颗），2 s 后再来一波；每次爆炸 10 伤害 r150 不衰减，同一个人第 2–6 次挨 5，之后每次 1。
- **分类**：好技能（PvE 范围持续伤害、炸门）；系统（**递归子弹树**——可以配置的"爆炸生爆炸"；每目标命中计数衰减）；可视化（子弹弹跳散开的一串小爆）。
- **可拆出的部件**：
  - 粘弹（可粘敌人，友军穿过）→ 3.1 `OnProjectileCollision_weapon_cluster_bomb_launcher`
  - 递归子弹树（数据驱动）→ 3.2.1 `ClusterBurstData` + `DoClusterBurst` / `ClusterBombThink`（AR2.7 已列参数）
  - 每目标命中计数、伤害递减 → 3.2.2 `ClusterBombDamageCallback`（共享 inflictor 的生命周期 20 s）
  - 命中后加速（升级）→ 3.2.3 `FollowUp_Start`
  - AI 危险区 → 3.2.4 `SpawnDangerousAreaForAI`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 主弹 | 投掷武器（`is_toss_weapon`），4400 u/s，仰角 0，hull ±3 | `ltxt:12`、`ltxt:91-92`、`ltxt:118-119`；AR2.7 |
| 粘 | `PlantStickyEntity(…, highDetailTrace, ignoreHullSize, stickToCharacter = 命中的是玩家或 NPC)`；**友方玩家直接忽略**（穿过）；目标正在 Revenant 图腾回溯时改成掉下去 | `nut:101-145` |
| 主弹计时 | 粒子 `P_fuse_tac_impact`、`P_fuse_tac_light` + 声音 `Fuse_Tactical_Timer_3p`，1.7 s | `nut:166-169`、`nut:188-190` |
| 爆炸 | 脚本 `Explosion(pos, owner, inflictor, 10, 10, 150, 150, NOSOUND_FOR_ALLIES, …, impulse 0, explosive, mp_weapon_cluster_bomb_launcher)` | `nut:512-530` |
| 子弹 | 子弹武器 `FireWeaponGrenade(pos, vel)`，`SetDoesExplode(false)`，到时间脚本手动爆 | `nut:532-547`、`nut:459-467` |
| 子弹物理 | 重力 ×1.1，hull 水平 ±3、高 0，弹跳浅 0.5 / 陡 0.3 / 法向 1（全反）/ 无随机 | `btxt:56-58`、`btxt:98-103` |
| 伤害计数 | 共享 inflictor（`info_target`），表 `clusterBombHitTable[inflictor][victim]`，20 s 后删 | `nut:303-321` |
| 炸门 | 伤害回调里门 → 伤害 = 门的血 | `nut:337-341` |
| 子弹互不伤 | 受害者是子弹投射物 → ×0 | `nut:333-336` |
| 角色伤害系数 | 玩家受害者 × `CharacterClass_GetDamageScale`（例如"强壮"类角色减伤） | `nut:346-351` |
| 命中加速（升级） | `speed_boost 0.15` + `adrenaline_visuals`，1 s；再命中刷新时长 | `nut:377-414` |
| AI 危险区 | `AI_CreateDangerousArea_Static(半径 150×1.25)`，持续 1.7 + 2 + 2 s | `nut:417-446` |
| 手雷警告 | `show_grenade_indicator 1`（对别人），模型 `GRENADE_INDICATOR_CLUSTER_BOMB_MODEL` | `ltxt:16-17`、`ltxt:29` |

全部伤害逻辑在服务端；客户端只做碰撞预测（`#if CLIENT` 友方载具忽略，`nut:111-114`）。

## 2. 流程

```
按战术（≥ 20 弹药，满 40）→ 拿出 0.2 s → toss_time 0.93 s 出手（语义上是"开火"，is_semi_auto）
主弹直飞 → 碰到非友方 → 粘住（世界 / 敌人 / NPC 身上）
 └ DeployClusterBombLauncher
     t=0     冲击特效 + 计时灯 + 计时声；开 AI 危险区（5.7 s）
     t=1.7   停计时声；建共享 inflictor（20 s）；给子弹武器
             主爆（10 / r150）
             第 1 波树：从主弹位置 + 前方 3 u，方向 = 主弹朝向（水平化）
     t=3.7   第 2 波树（同起点、同方向）
     子树（每一颗）：生成 → 等 explodeDelay → 停物理 → 爆（+5 u 高） → 在自己位置、按自己水平初速方向发下一层
```

**完整时间线（推断，按参数）**，每层同一节点下的兄弟子弹相隔 0.1–0.2 s 随机：

| 层 | 颗数 | 水平 / 竖直初速 | 爆炸延迟（第 1 波 / 第 2 波） | 方向（相对父方向的 yaw） |
|---|---|---|---|---|
| 0 | 2 | 200 / 300 | 0.3 / 0.3 | 90°、270° |
| 1 | 每颗 2 → 4 | 300 / 200–275 | **0.5 / 0.4** | 90°、270° |
| 2 | 每颗 4 → 16 | 300 / 50–200 | 0.4 / 0.4 | 45°、135°、225°、**215°** |

- 一波最长链约 0.3 + 0.2 + 0.5 + 0.2 + 0.4 + 0.6 ≈ 2.2 s（最后一个兄弟晚 3×0.2），所以第 1 波尾巴和第 2 波开头（t = 3.7）可能重叠一点。
- 每波 22 次小爆 + 第 1 波前的 1 次主爆 = **45 次爆炸**。
- **AR2.7 说"第二波同样的树"，不完全对**：第 2 波第 1 层延迟是 0.4（`nut:271`），第 1 波是 0.5（`nut:212`）。
- **疑似笔误**：第 2 层 yaw `[45, 135, 225, 215]`（`nut:216`、`nut:275`），215 和 225 只差 10°，按对称应为 315。实际效果：每个第 2 层落点组里有两颗几乎重叠、315° 方向是空的（推断）。注释掉的旧版（`nut:227-253`）也是 215。

打断：主弹销毁、发射武器销毁、主人销毁（`nut:153-163`）。子弹树线程只看子弹自己的 `OnDestroy`。

冷却：每发 20、满 40、每秒 1 → 2 发，每发 20 s（`ltxt:40-46`）；升级 `upgrade_core_tac_cooldown_reduction` → 15 / 30（每发 15 s，`ltxt:236-244`）。

## 3. 代码

### 3.1 入口：`OnProjectileCollision_weapon_cluster_bomb_launcher`（`nut:96-146`）

```
无目标 / 打到自己 / 打到友方玩家 → return（友军穿过）
cp.normal 为零 → 用 UP
目标在图腾回溯 → 速度清零、改成受重力（掉下）
否则 PlantStickyEntity(…, 可粘角色 = 目标是玩家或 NPC)
服务端：没部署过 → thread DeployClusterBombLauncher
```

### 3.2 核心逻辑

#### 3.2.1 递归子弹树（`nut:36-46`、`nut:195-301`、`nut:448-510`）

AR2.7 已写。补充：`ClusterBurstData` 每层字段 `yawOffset[]`、`zVelMin/Max`、`xyVel`、`explodeDelayMin/Max`、`nextSpawnDelayMin/Max`（默认 0.1 / 0.1）；脚本里 `data` 是**同一个结构体反复改再 clone**，所以第 0 层设的 `nextSpawnDelayMax = 0.2` 会遗留到第 1 层（`nut:205`、`nut:208-214`）——兄弟间隔都是 0.1–0.2 s。

```
DoClusterBurst(levels, origin, fwd, i):
    for yaw in levels[i].yawOffset:
        v = flatten(rotate(fwd, yaw)) * xyVel + (0,0, rand(zMin,zMax))
        b = 子弹武器.FireWeaponGrenade(origin, v); b.savedVel = flatten 方向
        thread ClusterBombThink(b, i)
        wait rand(nextSpawnMin, nextSpawnMax)
ClusterBombThink(b, i):
    wait explodeDelay
    StopPhysics; Explosion(b.pos + (0,0,5))
    thread DoClusterBurst(levels, b.pos, b.savedVel, i+1)
```

#### 3.2.2 伤害计数：`ClusterBombDamageCallback`（`nut:323-395`）

```
相位 → 跳过
受害者是本技能子弹 → ×0
门 → 伤害 = 门血
玩家 / NPC 且 inflictor 还在表里:
    scale = 玩家 ? 角色伤害系数 : 1
    n = ++hits[inflictor][victim]
    damage = n == 1 ? floor(10·scale) : n ≤ 6 ? floor(10·0.5·scale) : 1
有升级 PAS_TAC_UPGRADE_ONE 且受害者是活着的敌人（非倒地）→ 自己加速
```

- 计数**跨两波共用**（同一个 inflictor，`nut:193`），所以两波加起来，同一个人最多 10 + 5×5 + 1×39 = **74**（站满 45 次爆炸，推断上限）。
- inflictor 20 s 后删掉（`nut:318-320`），之后同一颗的伤害（不会再有）不再计数。
- 非玩家非 NPC（道具、陷阱）不进计数分支 → 每次 10。

#### 3.2.3 升级：命中加速 `FollowUp_Start`（`nut:397-414`）

```
已经在加速中 → 两个状态效果都把时长重设为 1 s
否则 → 喊话（4 s 防刷）；adrenaline_visuals(1, 1 s) + speed_boost(0.15, 1 s, 淡出 0.25)
```

本地化："Short speed boost on successful Knuckle Cluster hit."（`localization_english.txt:3374`）。

#### 3.2.4 AI 危险区：`SpawnDangerousAreaForAI`（`nut:417-446`）

`info_target` + `AI_CreateDangerousArea_Static(半径 187.5)`，寿命 1.7 + 2 + 2 = 5.7 s（`nut:425-427`）。NPC 会躲开这个圈（引擎 AI，推断）。

### 3.3 客户端表现

主弹拖尾 `P_fuse_tac_main_bomb_trail`、子弹拖尾 `P_fuse_tac_bomb_trail`（`ltxt:56-57`、`btxt:50-51`）；爆炸 `P_fuse_tac_exp_air` + 特效表 `exp_fuse_tac_bomb_first_explo` / `_secondary_explo`（`nut:7-13`）；抛物线 `P_arc_red` 弹 1 次、腰射不画（`ltxt:32-36`）；子弹武器抛物线弹 2 次（`btxt:30`，不显示，推断）。

### 3.4 依赖

`PlantStickyEntity`（`vscripts/weapons/_weapon_utility.nut:1703`）、`Explosion`、`AI_CreateDangerousArea_Static`、`CharacterClass_GetDamageScale`、状态效果 `speed_boost` / `adrenaline_visuals`。

## 4. 参数

AR2.7 的表全部有效，这里只列补充或修正的。

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| CLUSTER_BOMB_LAUNCHER_FIRST_EXPLOSION_DELAY | 1.7 | s | `nut:18` | 粘住到主爆 | |
| CLUSTER_BOMB_BURST_ROUGH_DURATION | 2.0 | s | `nut:22` | 两波间隔 | |
| CLUSTER_BOMB_FIRST_LAUNCH_OFFSET | 3.0 | u | `nut:28` | 子树起点前移 | |
| CLUSTER_BOMB_EXPLOSION_POS_OFFSET | (0,0,5) | u | `nut:17` | 子弹爆点抬高 | |
| CLUSTER_BOMB_EXPLOSION_RADIUS | 150（内外相同） | u | `nut:24` | 不衰减 | |
| CLUSTER_BOMB_DEFAULT_DAMAGE | 10 | HP | `nut:25` | | |
| CLUSTER_BOMB_SUBSEQUENT_DAMAGE_PERCENTAGE | 0.5 | × | `nut:20` | 第 2–6 次 | |
| CLUSTER_BOMB_MAX_HITS | 6 | 次 | `nut:23` | 超过后每次 1 | |
| CLUSTER_BOMB_LAUNCHER_DAMAGE_INFLICTOR_LIFETIME | 20 | s | `nut:19` | 计数表寿命 | |
| CLUSTER_BOMB_EXPLOSION_DURATION | 1.0 | s | `nut:21` | 未用 | |
| CLUST_BOMB_FOLLOW_UP_SPEED_BOOST_DURATION | 1.0 | s | `nut:30` | 升级加速时长 | |
| 升级加速强度 | 0.15（淡出 0.25 s） | 严重度 | `nut:411` | | |
| 子树兄弟间隔 | 0.1–0.2 | s | `nut:44-45`、`nut:205` | | |
| 第 2 波第 1 层爆炸延迟 | 0.4（第 1 波 0.5） | s | `nut:271` vs `nut:212` | | |
| 第 2 层 yaw | 45 / 135 / 225 / 215（疑似 315 笔误） | ° | `nut:216`、`nut:275` | | |
| AI 危险区 | r187.5，5.7 s | u / s | `nut:425-435` | | |
| 发射器 `.txt` explosion_damage / radius | 10 / 475 | — | `ltxt:77-80` | 主弹最后被 `Destroy()`（`nut:182`），推断不走原生爆炸，不生效 | |
| npc_min / max_range | 600 / 1200 | u | `ltxt:216-217` | NPC 用这个技能时的距离（R5 NPC 不用 Fuse 技能） | |
| 子弹 `.txt` launch_speed | 1 | — | `btxt:52` | 速度由脚本给 | |
| fire_rate / deploy / toss | 0.83 / 0.2 / 0.93 | — / s / s | `ltxt:93-103` | | |
| 升级冷却 | 15 / 30 | 弹药 | `ltxt:236-244` | 每发 15 s | |

## 5. 未解决和要实测的

1. 子弹树实际时间线、yaw 215 的落点：火力训练场对墙打一发，runner 每 0.05 s 记录 `mp_weapon_cluster_bomb` 投射物的位置和消失时间，画俯视图（第 2 层应该能看到 225/215 重叠）。
2. 74 点上限（同一人站满）：对一个 `npc_dummie` 身上直接粘，记血量变化次数和每次数值。
3. 发射器 `.txt` 的 475 半径是否有原生爆炸：同上一次实测看主弹销毁时有无伤害。
4. 服务端是否 SDK 改写：本文件除注释掉的 trophy 代码外看不到 SDK 痕迹（推断原版）。

## 6. HSD 实现

**未实现**（`Ordnance.cs` 里没有 Fuse）。建议：

- `KnuckleCluster : ThrownItem`，`ThrowParams{ launchSpeed = 4400, pitchOffset = 0, stick = true, stickUnits = true }`（`Throw.cs` 的 `stick` / `stickUnits` 已支持，`ThrownItem.stuckUnit` 已能跟随单位移动）；友方单位要能穿过——`ThrownItem.Fly` 现在按 `stickUnits` 判断，需要加"同队不碰"。
- 子弹：`ClusterSub : ThrownItem`（`gravityScale = 1.1, shallow 0.5, sharp 0.3, alongNormal = 1`），`ClusterBurstData` 原样搬成 C# 结构体数组；**把两波参数各写一份**（第 2 波第 1 层 0.4），yaw 215 照抄并加开关 `hsd.combat.clusterYawFix`（默认关 = 215）。
- 计数：`Dictionary<CombatUnit,int>` 挂在主弹对象上（主弹 20 s 后删），伤害走 `CombatSim.Damage`，爆炸走 `CombatSim.Explode(at, dmg, 150, 150, 0, …)` 时要先按计数算 dmg——`Explode` 是统一伤害，需要给它加一个 `Func<CombatUnit,double> damageFor` 重载。
- 这个"递归子弹树 + 每目标衰减"很适合做成通用部件（HSD 自创"投掷物发射器"也能用）：`ClusterTree.cs`。
