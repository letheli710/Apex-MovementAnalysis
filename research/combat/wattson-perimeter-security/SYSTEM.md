# Wattson 战术 Perimeter Security（电网）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_tesla_trap.nut`（4598 行），`txt` = `weapons/mp_weapon_tesla_trap.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Wattson / 战术 / Perimeter Security / `mp_weapon_tesla_trap`。
- **一句话**：放一个个电桩，相邻两桩（≤ 768 u）自动连成 4 层电线；敌人穿过 → 20 伤害 + 电击减速 3 s 级别，每人每秒最多一次；队友穿过时整段电网关 0.4 s 让路。
- **分类**：好技能（PvE 守点、卡路口）；系统（放置预览 + 吸附 + 链式连接 + 线段穿越检测）；可视化（电线由立杆升起、被挡时断开）。
- **可拆出的部件**：
  - 放置校验和吸附 → 3.2.1 `TeslaTrap_GetPlacementInfo` / `TelsaTrap_AttemptSnapToNeighbor`（另见 `_shared/B-placement.md`）
  - 链式连接（"焦点桩"）→ 3.2.2 `TeslaTrap_CanLink` / `TeslaTrap_AttemptTrapLink`
  - 线段穿越触发器 → 3.2.3 `TeslaTrap_CreateLinkTriggerCylinder` + `CodeCallback_TeslaTrapCrossed`
  - 实时遮挡（物体挡在线上就断开一段时间）→ 3.2.4 `TeslaTrap_CheckForRealTimeGeoObstructions`
  - 电击效果 → `_shared/B-electric-emp.md`
  - 每个目标的冷却表 → 3.2.3 `file.trapTimes`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 电桩 | `CreatePropScript(wattson_electric_fence.rmdl, SOLID_VPHYSICS)`，血 25，可被近战 | `nut:1781-1795` |
| 立杆升起 | 动画 pose parameter `Height`，0 → 最大；`TESLA_TRAP_RISE_DURATION 0.5`、`RISE_HEIGHT 40` | `nut:109-110`；撤掉时 1 s 降回 0（`nut:1960` 附近 `SetPoseParameterOverTime`） |
| 电线判定 | 触发器 `trigger_cylinder_heavy`，**轴沿着两桩连线**，半径 96，`SetTriggerType(TT_TESLA_TRAP)` + `SetTeslaLink(主桩, 副桩, up, 高度)`；穿过由引擎回调 `CodeCallback_TeslaTrapCrossed` | `nut:2662-2755`、`nut:4204`。"穿过平面"的判定在引擎里，脚本看不到 |
| 伤害 | `TakeDamage(20, owner, 主桩, DF_ELECTRICAL, DF_STUN_AI, damageSourceId mp_weapon_tesla_trap)` | `nut:4269` |
| 减速 + 屏幕 | 伤害回调 `TeslaTrap_DamagedTarget` → `Electricity_DamagedPlayerOrNPC(…, 3.0)` | `nut:2067-2110`；见 `_shared/B-electric-emp.md` |
| 队友让路 | `trigger.SetObstructedEndTime(Time()+0.4)` | `nut:4214-4219` |
| 被物体挡住断开 | 线程每 0.3 s 做 1 次 hull trace + 每层一次 line trace，挡住 → 断开 1.1 s | `nut:2757-2870` |
| 电线特效 | 服务端每层一个 `P_tesla_trap_link_CP` 光束（控制点实体），客户端 `TeslaTrap_CreateClientTeslaTrapEffects` | `nut:2453-2525`、`nut:3950` |
| 小地图 | 小地图连线 + 敌人碰到时环形脉冲 `Minimap_RingPulseForTeam(…, 256/10, 2.0, 8)`、自动 ping | `nut:4290-4320` |
| 收回 | 主人对桩按 Use → 返还一次充能 | `nut:3265-3340` |
| 门 | 电线扫到门直接打爆门（伤害 = 门最大血） | `nut:2834` |

服务端 / 客户端：伤害、连接、遮挡全在服务端；客户端负责放置预览、电线特效、HUD 图标、小地图。注释里两处写着 "HoverVehicle_StunBegin is not registered on the S3 dedi entity VM"（`nut:4279`、`nut:4350` 附近）——**说明这份脚本被 SDK 社区为 S3 dedi 改过**，载具击晕被删了。

## 2. 流程

```
按键（offhandHybrid，可按住）
 └ 放置预览：每帧 TeslaTrap_GetPlacementInfo（距离 ≤ 300，坡度、吸附、能否连到焦点桩）
松开 / 开火：OnWeaponPrimaryAttack → 合法则 TeslaTrap_Deploy
 ├ 生成电桩，若有焦点桩 → AttemptTrapLink（≤ 768 u、两端都 < 2 条连接、4 层里至少 3 层视线通）
 ├ 新桩成为玩家的"焦点桩"（下一根会连向它）
 ├ 0 帧：放置特效；1.0 s：TESLA_TRAP_DEPLOY_DELAY，电线才通电（trigger.SetObstructedEndTime(now+1.0)）
 └ 循环等 "TeslaTrap_Unlinked"（直到被毁 / 收回）
通电后：
 ├ 敌人穿线 → 每人每 1.0 s 最多一次：20 伤害 + 电击 3 s（减速 4 s，见共享记录）
 │          每人每 3.0 s 最多一次：自动 ping、小地图脉冲（被动"周界监视"）
 ├ 队友 / 自己穿线 → 这段电网关 0.4 s（只有玩家和分身会关）
 └ 物体挡住 → 关 1.1 s；门 → 打爆；缆车停站 → 关 8 s
结束：桩血 25 打掉 / 收回 / 超过 12 根时最旧的被挤掉（AddNewLimitedLegendObject）/ 回合结束
取消：玩家离焦点桩 > 1024 u 且瞄准点也 > 1024 u → 自动切走武器（invnext），链断开（nut:3565）
```

链规则：每根桩最多 2 条连接（`TESLA_TRAP_LINK_COUNT_MAX`）。新连接如果和该桩已有连接方向夹角太小（2D 点积 > 0.98，约 11°）→ 不让放（`TeslaTrap_IsLinkAngleTooSteep`，`nut:4573`）。焦点桩有 1 条连接时，新桩成为下一个焦点；有 2 条时清空焦点（链的端点闭合，`nut:2363-2373`）。

升级 / mod（`txt` Mods）：
- `extra_tactical_charges`：每次 15 / 弹匣 90 → 6 次，回充 0.5 /s（30 s 一次）。
- `upgrade_tac_one`：每次 12 / 弹匣 48 → 4 次，回充 1 /s（12 s 一次）。
- `interception_pylon_super_charge`：回充 ×5（站在自己拦截塔旁边）。
- `double_link_mod`：空的；代码 `TeslaTrap_IncrementPlacementMaxLinks`（`nut:1336`）按它改每次放置的连接数。

## 3. 代码

### 3.1 入口

- `OnWeaponAttemptOffhandSwitch_weapon_tesla_trap`（`nut:517`）：弹药 ≥ ammo_per_shot 才能切出。
- `OnWeaponActivate_weapon_tesla_trap`（`nut:426`）：开预览线程 `TeslaTrap_PlacementProxy`（客户端，`nut:1600`）、服务端开 `TeslaTrap_MaxDistanceAutoCancelUpdate`。
- `OnWeaponPrimaryAttack_weapon_tesla_trap`（`nut:559`）：再算一次 placementInfo；服务端如果吸附到已有桩（`snapTo`），只做"连接已有两桩"，不生成新桩、不扣弹（`nut:600-620`）；否则 `thread TeslaTrap_Deploy`。

### 3.2 核心逻辑

#### 3.2.1 放置（`TeslaTrap_GetPlacementInfo`，`nut:~770-1095`）

```
eye → 视线方向 trace，最远 300（playlist tesla_trap_range_override）
坡度 = |n.x|+|n.y|，太陡用"前方地面"兜底
从命中点前 20、上 32 往下 44 找地面；再从眼睛 trace 到那里确认没穿墙（roof trace）
hull trace（mins <-8,-8,0> maxs <8,8,16>）落地
表面法线：在 4 个角各打一条向下 trace，取和竖直最接近的法线（nut:966-1020）
法线和竖直夹角 > TESLA_TRAP_ANGLE_LIMIT(0.55) 不合格（推断：点积阈值）
立杆净空：从底部 +12 到 +96 trace，能放几层 = int(高度/24)，< 3 层不合格
吸附：64 u 内有自己的桩 → snapTo（nut:1128）
能否连焦点桩：TeslaTrap_CanDeploy
```

`.txt` 的 `object_placement_*` 字段（`object_placer 1`、`distance_max 300`、`hill_angle_max 50` 等）给引擎的通用放置器用，见 `_shared/B-placement.md`。

#### 3.2.2 连接（`TeslaTrap_CanLink`，`nut:4466`）

```
不连自己、不连死桩
两端连接数都 < 2
父实体必须相同（都在同一个移动平台上，或都不在）
距离 ≤ 768
4 层（高度 24/48/72/96）逐层 line trace，挡住就停：通的层数 < 3 → 不连
```

连上后 `TeslaTrap_LinkTraps`（`nut:2269`）→ `TeslaTrap_CreateTrapLinkData`（`nut:2453`）：建光束特效、控制点、触发器。

#### 3.2.3 穿越触发器和伤害

触发器（`nut:2662`）：

```
mid  = 两桩底部各沿 up 抬 48 的中点
轴向 = 两桩连线方向；半长 = 距离/2 + 32；半径 96
TT_TESLA_TRAP + SetTeslaLink(主, 副, up, 底部偏移 + 24) + SetVertOverride(底部偏移 + 层数×24)
NPC 和玩家都触发；挂在主桩上
初始 obstructedEnd = now + 1.0（1 s 后才通电）
```

穿越回调 `CodeCallback_TeslaTrapCrossed`（`nut:4204`），服务端：

```
if 友军或主人:
    if 是玩家或分身: obstructedEnd = now + 0.4
    return
if now < obstructedEnd: return
VO（每 6 s 一次，>2953 u 说"远"）
if now < trapTimes[ent].nextDamageTime: return
trapTimes[ent].nextDamageTime = now + 1.0
ent.TakeDamage(20, …, DF_ELECTRICAL | DF_STUN_AI)
if now < nextPingTime: return; nextPingTime = now + 3.0
ping / 小地图脉冲 / 威胁区（两个桩不同主人时两人都收到）
```

伤害回调 `TeslaTrap_DamagedTarget`（`nut:2067`）：NPC 在电击免疫期 → 伤害 ×0；友军 ×0；暗影模式 ×0.5；然后 `Electricity_DamagedPlayerOrNPC(victim, info, 3.0)`。

**`trapTimes` 是按受害者存的全局表**，不是按电线：同一个人 1 s 内穿两段不同的电网也只吃一次伤害。

#### 3.2.4 实时遮挡（`nut:2757`）

```
每 (0.4-0.1)=0.3 s：
  hull trace 主桩→副桩（高度 = 层数×24）：
    碰到移动平台根 → 关 0.4 s；缆车在站 → 关 8 s；普通门 → 关 0.5 s
  逐层 line trace（层间交替方向）：
    碰到世界 / func_brush / 骨骼 / 注册过的实时障碍 → 关 1.1 s
    碰到门 / 战利品滚筒 → 直接打爆
```

`SetLinkedTrapsObstructedForDuration`（`nut:2949`）：设 obstructedEnd，隐藏光束，等完再显示。

#### 3.2.5 桩受伤（`nut:2112-2223`）

友军和自己的电网伤害 ×0；其余伤害自己扣血（伤害 ×0 后手动 `SetHealth`），≤ 0 播爆炸、给攻击者一个追踪视野点。

### 3.3 客户端表现

- 放置预览：代理模型 + 范围特效 `P_tesla_trap_ar_place`，预览里画出到焦点桩的连线（`TeslaTrap_SnapClientOnlyModel`，`nut:1425`）。
- 电线：`ClientCodeCallback_TeslaTrapLinked`（`nut:3943`）→ 每层一个光束；被挡时 `ClientCodeCallback_TeslaTrapVisibilityChanged`（`nut:4093`）停特效、关环境音。
- HUD：每根桩一个图标（`TeslaTrap_UpdateHudMarkers`，`nut:3761`），被敌人碰过时换成 `wattson_trap_enemy_collided`。
- 客户端也做一次"友军穿过 → 关 1.0 s"的预测（`nut:4350-4370`），比服务端 0.4 s 长。

### 3.4 依赖

- `_shared/B-electric-emp.md`（减速、屏幕、NPC 击晕）。
- `AddNewLimitedLegendObject`（数量上限）、`PlayerObjects_CommonInit`、`TrapDestroyOnRoundEnd`。
- 引擎：`TT_TESLA_TRAP` 触发器类型、`SetTeslaLink`、`GetObstructedEndTime`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 伤害 | 20 | HP / 次 | `nut:140` `TESLA_TRAP_LINK_DAMAGE_AMOUNT_UPDATE`；playlist `tesla_trap_damage_override`（`nut:388`） | 每次穿越 | |
| 伤害间隔 | 1.0 | s / 每个受害者 | `nut:139`（旧值 0.5，`nut:138` 未用） | 同一人的冷却 | 改小 = 站在线里持续掉血更快 |
| 电击时长 | 3.0 | s | `nut:141` `TESTLA_TRAP_EMP_DURATION_UPDATE` | 屏幕 3 s；减速 3+1 s（推断） | |
| 减速 / 转向 | 0.5 / 0.7 | 强度 | `_weapon_utility.nut:378-379` | | |
| 重型护甲伤害 | 250 | HP | `nut:133`（未见使用） | | |
| 电线层高 | 24 | u | `nut:118` | 层距 | |
| 层数 | 4（最少 3） | 层 | `nut:124-125` | 电网高 24–96 u | 3 层 = 72 u，可能被跳过 |
| 连接距离 | 768 | u | `nut:119`（旧 512） | | |
| 每桩连接数 | 2 | 条 | `nut:123` | 链 / 不能分叉 | |
| 最小夹角 | 点积 0.98（≈11°） | | `nut:126` | 防止折返 | |
| 触发器半径 | 96 | u | `nut:150` | 圆柱半径（真正的穿越判定在引擎） | |
| 放置距离 | 300 | u | `nut:93`、`txt object_placement_distance_max 300`；playlist `tesla_trap_range_override` | | |
| 桩间最小距离 / 吸附距离 | 64 | u | `nut:95` | < 64 吸到旧桩 | |
| 坡度限制 | 0.55 | 点积（推断） | `nut:104` | | |
| 桩血量 | 25 | HP | `nut:103` | | |
| 桩数量上限 | 12 | 根 | `nut:35` | 超出挤掉最旧 | |
| 通电延迟 | 1.0 | s | `nut:106` | 放下到通电 | |
| 友军让路 | 0.4 | s | `nut:114` | | |
| 遮挡断开 | 1.1 | s | `nut:2830-2850` | | |
| 遮挡检查周期 | 0.3 | s | `nut:2765` | | |
| 立杆升起 | 40 u / 0.5 s；收回 1.0 s | | `nut:109-111` | 表现 | |
| ping 间隔 | 3.0 | s | `nut:147` | | |
| 自动取消距离 | 1024 | u | `nut:120` | | |
| 充能 | 弹匣 120，每次 30 → 4 次 | | `txt ammo_clip_size / ammo_per_shot` | | |
| 回充 | 7.5 /s → 一次 4 s | | `txt regen_ammo_refill_rate 7.5` | | **看起来太快，要实测** |
| 移速修正 | ×1.07 | | `txt move_speed_modifier 1.07` | 拿着电网走得快 | |
| mods | 见 2 节 | | `txt Mods` | | |

## 5. 未解决和要实测的

1. **回充 4 s 一次可信吗**：`txt` 是 7.5 /s ÷ 30。正式服记忆是更慢。可能是 SDK 改过的 `.txt`，或是"ammo_stockpile_max 30"另有作用。测法：R5 runner 放 4 根，计时回满。
2. **穿越判定的几何**：`TT_TESLA_TRAP` 在引擎里，触发器半径 96 是"候选"范围，真正是否"穿过平面"未知。测法：从电线一侧慢慢贴近、停在线上（不穿过）、跳过最上层（> 96 u），各看是否掉血。
3. **减速总时长**：见 `_shared/B-electric-emp.md` 第 5 节。
4. **对 NPC**：每 3 s 免疫窗内伤害整次 ×0。测法：dedi 上放电网，让 spectre / prowler 来回穿，看伤害数字是否每 3 s 一次而不是每 1 s。
5. **载具击晕被删**（S3 dedi 注释）：PvE 用不上，记录即可。

## 6. HSD 实现

**未实现。**

建议做法（`HSD-Unity/Assets/HSD/Game/Runtime/Combat/`）：

- 新文件 `Traps.cs`：`TeslaPost : CombatUnit, ICombatDrawable`（血 25，可被打）+ `TeslaLink : ICombatEntity`（两根桩、层数、`obstructedUntil`）。
- 放置：复用 `CombatSim.WorldRay`（放置 trace）和 `CombatSim.PlaceTurret` 的写法（`CombatSim.Items.cs:243`）。
- 穿越：每帧对每个单位，拿上一帧位置和这一帧位置的线段，和电网平面（两桩连线 × 竖直，高 0–层数×24）求交（`CombatGeometry` 已有平面射线帮助函数）。比 R5 的"引擎圆柱 + 回调"简单，结果应当一样（要和第 5 节第 2 条的实测对比）。
- 冷却：`Dictionary<CombatUnit, double> nextDamage`，全局共享（照 R5，不按电线分）。
- 效果：调 `CombatSim.Emp`（改成固定时长版本，见共享记录第 6 节）。
- 遮挡：每 0.3 s 对每层做 `CombatSim.WorldClear`，被挡关 1.1 s。
- 充能：`Charges(4, 4.0)`（R5 脚本值，待实测）。
- 开关：PlayerPrefs `hsd.combat.tesla.*`（层数、间隔、伤害）。
- 和 R5 的差：穿越判定用线段求交而不是引擎触发器；没有门 / 缆车 / 小地图；写进 `R5-DIFF-ARCHIVE.md`。
