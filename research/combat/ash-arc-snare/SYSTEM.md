# Ash 战术 Arc Snare（电弧陷阱）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_arc_bolt.nut`（1324 行），`txt` = `weapons/mp_weapon_arc_bolt.txt`。SDK 源码：`research-src/s21-r5sdk/src/`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Ash / 战术 / Arc Snare / `mp_weapon_arc_bolt`。
- **一句话**：扔出一个旋转的电弧球（1200 u/s、无重力），碰到敌人或落地后变成陷阱；半径 160 内的敌人吃 10 伤害并被"拴住"——身上连一根电链到地上的锚点，锚点半径 210 内能动，走出去会被拉回、链子掉血，5 s 后断开。
- **分类**：好技能（控制）；**系统**（拴住 = 引擎原生 tether）；可视化（电链绳子、屏幕边缘、指向锚点的方向指示）。
- **重大发现**：**本地构建里"拴住"的物理是关掉的。** `nut:886` 把引擎调用 `victim.AddEntityUpdatedTether(…)` 注释掉，换成 `int tetherId = 1`；`TrackTetherHealthForAudio_Thread` 里链子血量写死 10.0（`nut:1083-1090`）；配置 tether 的 ConVar 只留了 `tether_maxvel`，其余 6 个注释掉（`nut:220-227`）。推断原因：S3 dedi 的实体 VM 没有这个原生函数（同电网的 `HoverVehicle_StunBegin` 注释）。所以本地只剩"绳子特效 + 5 s"，**不会真的拉住人**。下文第 3.2.3 节按留下的参数和 SDK 的数据结构还原原版机制，全部标"推断"。
- **可拆出的部件**：
  - 飞行中半径逐渐长大的范围伤害 → 3.2.1 `Bolt_Thread`
  - 投射物命中 → 原地生成陷阱（`PlantStickyEntity`）→ 3.2.2 `PlantBolt`
  - 拴住（锚点 + 半径 + 拉回 + 链子血量）→ 3.2.3 `CreateTether_Thread`，HSD 要自己实现
  - 绳子表现（3p 绳 + 1p 绳分开）→ 3.3
  - 屏幕方向指示（箭头指向锚点）→ 3.3 `TetherDirectionalEffect_Thread`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投射物 | `CreateBolt` → 引擎 bolt，`projectile_launch_speed 1200`、`projectile_gravity_scale 0`、寿命 6 s、最多反弹 5 次 | `txt:25,51-53`；`nut:300-330` |
| 伤害 + 触发 | 每帧 `RadiusDamage(中心, 10, 内外半径 = 当前半径, DF_ELECTRICAL \| DF_NO_SELF_DAMAGE, mp_weapon_arc_bolt)` | `nut:615-628`。半径在 0.5 s 内按指数 1.5 从 1 长到 160 |
| 直接命中 | 碰撞回调里对敌人 `TakeDamage(10)`，不落地（让 RadiusDamage 那一下触发拴住） | `nut:384-389` |
| 落地陷阱 | `PlantBolt` → 新建一个 planted bolt + `PlantStickyEntity`，0.3 s 后激活 | `nut:425-452` |
| 拴住 | 伤害回调 `OnDamaged_Shock` → `CreateTether_Thread`：锚点 `prop_physics`（链模型）+ 引擎 tether（**本地被注释**） | `nut:723-1020` |
| NPC 电击 | NPC 被打 → `EMP_DamagedPlayerOrNPC`（电弧星同一条路径，APEX 2.2） | `nut:750` |
| 绳子 | `CreateRope(锚点 → 受害者 CHESTFOCUS, 长 210, ash_arcbolt_chain_cable)` 两根：一根给别人看，一根挂在受害者身上的 mover 上只给自己看 | `nut:858-880` |
| 半径圈 | 粒子 `P_ash_arcbolt_tether_radius`，CP1 = 210，红色，只给敌人和自己看 | `nut:840-850` |
| 屏幕 | 客户端 `P_ash_tether_screen_edge`（在半径内强度 25，出半径 100）+ 方向指示 `P_ash_tether_indicator_cp10` | `nut:1116-1205` |
| 挡 ping | 陷阱周围 `CreateTraceBlockerVolume(半径 210×0.75)`，挡 ping | `nut:575-582` |

## 2. 流程

```
按住 → 握在手里（toss_pullout 0.23 s）
松开 → OnWeaponTossReleaseAnimEvent（toss_time 0.56 s）→ WeaponAttackBolt → Bolt_Thread(飞行)
飞行中（≤ 6 s）：
 ├ 每帧 RadiusDamage，半径 r(t) = 160·(min(t,0.5)/0.5)^1.5
 ├ 碰到敌人玩家 / 战斗 NPC → 直接 10 伤害，继续飞（不落地）
 ├ 碰到友军 → 忽略
 └ 碰到其他东西 → PlantBolt：在碰撞点生成陷阱，飞行体删除
陷阱（planted）：
 ├ 0.3 s 激活延迟
 ├ 半径从"飞行已用时"接着长（startTime -= timeBeforePlanted）
 └ 每帧 RadiusDamage(10, 半径 160)，持续 5 s（升级 15 s）
任何一次伤害命中敌人 → OnDamaged_Shock → CreateTether_Thread
 ├ 锚点位置：陷阱 / 打中玩家 → 用 bolt 位置；打中 NPC → NPC 脚下 +12
 ├ 锚点：受害者在地上或陷阱 → 速度 0；空中 → 继承水平速度，竖直 ≤ −60，落地就钉住
 ├ 绳子、特效、"我被拴住了"语音；关掉受害者的受伤提示
 ├ 不升级：删除 bolt（一个陷阱只拴一次）；升级：bolt 留着
 ├ 引擎 tether（原版）：见 3.2.3
 └ 结束：TetherTimeOut 等 5 s（升级 15 s）→ SIGNAL_TETHER_REMOVED；或受害者死亡 / 相位 / 传送 / 跳伞
结束：锚点 2 s 后删除；断开音效
```

打断：受害者进相位（Ash 自己的相位突破、Wraith）、被传送、死亡都会提前结束（`nut:781` EndSignal）。

升级：`PAS_TAC_UPGRADE_ONE`（`upgrade_ash_longer_tac_duration`）→ 陷阱和拴住时长 15 s，陷阱拴人后不消失，最后 5 s 蜂鸣。`txt upgrade_tac_one` → 弹匣 ×2（2 次）。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_arc_bolt`（`nut:273`）→ `WeaponAttackBolt`（`nut:300`）→ `CreateBolt` + `thread Bolt_Thread(bolt, owner, 6, 0, false)`。
- `OnProjectileCollision_arc_bolt`（`nut:369`）。

### 3.2 核心逻辑

#### 3.2.1 长大的范围伤害（`Bolt_Thread`，`nut:467`）

```
r_max = shock_radius(160); grow = 0.5 s; exp = 1.5
每帧:
  t = now - startTime
  r = t < grow ? max(r_max * (t/grow)^1.5, 1) : r_max
  RadiusDamage(origin(+前 4 u 若已落地), 10, r, r, BRUSHONLY 遮挡, 无推力, DF_ELECTRICAL|DF_NO_SELF_DAMAGE)
```

注意：`RadiusDamage` 每帧都打。不升级时第一次命中就删 bolt，所以只吃 10；升级时 bolt 不删，**理论上每帧 10 伤害**——原版应该有引擎层面的重复伤害限制，本地没看到，要实测（第 5 节）。

#### 3.2.2 落地（`PlantBolt`，`nut:425`）

`CreateBolt(isPlanted=true)` + `PlantStickyEntity(newBolt, 碰撞点)`（粘在表面，跟随移动物体），记 `timeBeforePlanted`，`Bolt_Thread(lifetime 5, activationDelay 0.3, planted)`。

#### 3.2.3 拴住（`CreateTether_Thread`，`nut:778`）

脚本部分（本地实际运行）：

```
锚点 = prop_physics(链模型)，碰撞组 DEBRIS，阻尼(0, 100)
空中 → 锚点下落，第一次碰撞时钉住（TetherAnchor_PlantOnFirstCollision，nut:1035）
陷阱 → 锚点直接不动，角度 = bolt + 180°，跟 bolt 的父实体
绳 ×2、特效 ×3
tetherId = 1                              ← 原版是 victim.AddEntityUpdatedTether(...)
等 SIGNAL_TETHER_REMOVED（5 s 后由 TetherTimeOut 发出，或引擎 CodeCallback_OnTetherRemoveApex 发出）
```

原版引擎 tether（**推断**，依据：注释掉的调用参数 `nut:886`、注释掉的 ConVar `nut:220-227`、SDK `basecombatcharacter.h:34` 的 `CTether` 结构和 `s21_dt_schema.h:5052` 的 `DT_Tether` 网络字段）：

```
AddEntityUpdatedTether(锚点, maxHealth=1000, drainPerSec=200, drainDelay=1.0, cutoffPct=0,
                        stretchDmgScale=0.3, velocityDmgScale=0.011, radius=210)
每个角色最多 2 根 tether（m_tethers[2]）
每帧（引擎）：
  d = |玩家 - 锚点|
  d ≤ 210：自由移动
  d > 210：把玩家往锚点拉，拉回速度上限 tether_maxvel = 100 u/s（这个 ConVar 本地仍然设置了）
           拉力强度 tether_default_strength 50，按链子血量缩放（strength_healthScale 0.6）
           链子掉血 = (d-210)·0.3 + |v|·0.011，每帧最多 10（tether_maxStretchDamage）
  1 s 后链子每秒自然掉 200；血量 ≤ 0 → 断开，回调 CodeCallback_OnTetherRemoveApex
  掉落（重力）也会掉链子血：tether_gravity_dmg_frac_per_sec 0.5
  在滑索上：速度 > 200 时强度 ×0.15
最长存活 ≈ 1 + 1000/200 = 6 s（不算拉扯掉血）；脚本 5 s 超时先到
```

客户端方向指示的大小 = `链子血量/1000 × 70 + 30`（`nut:1196`），说明血量会被客户端读到、越挣扎越细。

#### 3.2.4 伤害回调（`OnDamaged_Shock_Thread`，`nut:734`）

无效、打自己、打队友 → 伤害 0；非战斗 NPC（除训练假人）→ 0；NPC → 电击；非玩家非 NPC → 0；然后拴住。护盾伤害倍率 `ash_tether_shield_dmg_scale` 默认 1.0（`nut:770`）。

### 3.3 客户端表现

- 绳子：两根 `CreateRope`，长 210（= 半径），`Rope_SetCanEnterRestingState(false)` 一直晃。第一人称那根挂在一个跟着胸口的 mover 上，只对受害者可见；第三人称那根对别人可见。这个"一人两绳"的写法可以直接借给 HSD 的任何绳索技能。
- 屏幕边缘：在半径内 25，出半径 100（`nut:1130-1140`）。
- 方向指示：只在同时 ≤ 2 根 tether 时显示，角度 = 锚点方向相对视角，正前方 ±70° 内被推到侧边（`nut:1180-1190`）。
- 威胁指示：飞行中的 bolt 有威胁图标（`CreateProjectileBoltThreatIndicator`）。

### 3.4 依赖

- `PlantStickyEntity`、`RadiusDamage`、`CreateRope`、`CreateTraceBlockerVolume`。
- `EMP_DamagedPlayerOrNPC`（电弧星路径，见 APEX-REPORT 2.2；和 `_shared/B-electric-emp.md` 是同一套 EMP 代码的另一个入口）。
- 引擎 tether（`CTether`、`DT_Tether`、`tether_*` ConVar）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 伤害 | 10 | HP | `txt:60 shock_damage` | 每次命中 | |
| 伤害半径 | 160 | u | `txt:61 shock_radius` | 触发拴住的范围 | |
| 半径长大时间 / 指数 | 0.5 / 1.5 | s / — | `nut:148,150` | 刚扔出时范围小 | |
| 飞行速度 | 1200 | u/s | `txt:51` | | |
| 重力 | 0 | × | `txt:25` | 直线飞 | |
| 飞行寿命 | 6 | s | `txt:52` | 6 s × 1200 = 7200 u 后消失 | |
| 反弹次数 | 5 | | `txt:53`（但碰到东西就落地，推断不反弹） | | |
| 落地激活延迟 | 0.3 | s | `nut:450` | | |
| 陷阱 / 拴住时长 | 5（升级 15） | s | `nut:78,80`；playlist `ash_tether_duration(_upgraded)` | | |
| 拴住半径 | 210 | u | `nut:95`；playlist `ash_tether_radius` | 自由活动半径 = 绳长 | |
| 拉回速度上限 | 100 | u/s | `nut:84`；ConVar `tether_maxvel`（`nut:220`） | 原版 | 改大 = 拉得更猛 |
| 拉力强度 | 50（× 血量 0.6） | | `nut:85-86`（ConVar 被注释） | 推断 | |
| 链子血量 | 1000 | | `nut:87` | | |
| 自然掉血 / 延迟 | 200 /s，1.0 s | | `nut:98,102` | 最长 ≈ 6 s | |
| 拉扯掉血 | 超出距离 ×0.3 + 速度 ×0.011，每帧 ≤ 10 | | `nut:99-105` | 挣扎越猛断得越快 | |
| 下落掉血 | 0.5 /s（比例） | | `nut:107` | | |
| 滑索 | 速度 > 200 时强度 ×0.15 | | `nut:108-109` | | |
| 最大半径倍率 | 1.5（强度 100） | | `nut:96-97`（未使用，推断给引擎） | | |
| 退还 | 1.0 s 内没打中 → 退 50% | | `nut:113-114` | 本地未见调用 | |
| 冷却 | 弹匣 20，每次 20，回充 1 /s → 20 s | | `txt:20,45-48` | | |
| 挡 ping 半径 | 210×0.75 = 157.5 | u | `nut:576` | | |

## 5. 未解决和要实测的

1. **拴住在本地完全不起作用（静态结论）**：测法：R5 runner 里朝自己脚下扔（打不到自己，`DF_NO_SELF_DAMAGE`）→ 需要 bot。dedi 上刷一个 dummie，扔中后看 dummie 能否自由走出 210。预期：本地能走出去；正式服数据要从视频或别的构建补。
2. **原版拉回的数学**：引擎 C++ 里，SDK 没有实现代码（只有结构体）。如果要精确，可以用 REA 反编译 S21 客户端的 tether 预测代码（客户端也要预测移动，应当有同一份 `CTether` 更新函数）。搜字符串 `tether_maxvel` 定位。
3. **升级后每帧 10 伤害**：要实测伤害频率。
4. **NPC 的拴住**：脚本对 NPC 也走 `CreateTether_Thread`，但 `ai_basenpc.h:512` 有 `m_tethered` 字段，推断 NPC 有另一套原生拴住。PvE 关心这条。
5. 反弹 5 次的字段和"碰到就落地"矛盾，测一下扔向墙是否落在墙上。

## 6. HSD 实现

**未实现。**

建议做法：

- 投射物：`ArcSnare : ThrownItem`（`Throw.cs`），`ThrowParams { launchSpeed = 1200, gravityScale = 0, stick = true }`；粘住后变陷阱，0.3 s 激活。
- 长大半径：`r = 160 * Math.Pow(Math.Min(t, 0.5) / 0.5, 1.5)`，每帧对敌人做 `CombatGeometry.DistanceToUnit` 判定。
- 拴住：新类 `Tether : ICombatEntity`（锚点、半径 210、血量 1000）。每帧：
  ```
  d = 单位到锚点水平距离
  if d > 210: 把单位速度沿远离方向的分量削掉，再加一个指向锚点、上限 100 u/s 的速度；
              health -= min(10, (d-210)*0.3 + |v|*0.011)
  if t > 1: health -= 200*dt
  health <= 0 或 t > 5 → 结束
  ```
  对玩家要写身体速度，按 README "战斗层只在这几处写移动身体"，需要新增一处（和 `CombatSim.Push` 并列），开关 `hsd.combat.snare.pull`。
- 对 NPC：直接限制 `Dummy` 的移动目标点在锚点 210 内（比物理拉回简单）。
- 绳子：`CombatDraw` 画一条线段（锚点 → 胸口），颜色随血量变。
- 和 R5 的差：原版引擎拉回公式未知，HSD 用上面的近似；写进 `R5-DIFF-ARCHIVE.md` 并等第 5 节第 2 条的反编译结果。
