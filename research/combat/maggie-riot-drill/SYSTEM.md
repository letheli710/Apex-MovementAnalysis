# Mad Maggie 战术 Riot Drill（钻头）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_riot_drill.nut`（1494 行），`txt` = `weapons/mp_weapon_riot_drill.txt`，`mc` = `vscripts/weapons/mp_weapon_maggie_common.nut`（175 行）。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Mad Maggie / 战术 / Riot Drill / `mp_weapon_riot_drill`（内部名 breaching spike / concussive breach，伤害源 `mp_weapon_concussive_breach`）。
- **一句话**：瞄一面墙（≤ 1750 u），屏幕显示墙厚；射出一根钻头（10000 u/s），钉进墙后 1 s，在**墙的另一面**沿视线方向喷出一个长 224、半径 130 的圆柱形火区，持续 8 s，每 0.2 s 4 伤害（20 DPS，最多 160）；墙后的玩家要被出口"看见"才挨打，NPC 不看视线。
- **分类**：好技能（穿墙打躲在掩体后的敌人，PvE 清角落）；系统（**原生穿墙 trace 求墙厚 + 出口点**、放置预览、按出口视线过滤的圆柱伤害区）；可视化（墙厚 HUD、贯穿墙的光束、出口喷火、世界空间倒计时）。
- **可拆出的部件**：
  - 穿墙求出口（`BreachTrace`，原生）+ 结果分类 → 3.2.1 `GetRiotDrillPlacementInfo` / `FindEndSpikeLocation`
  - 放置预览（墙厚、三色）→ 3.3 `DeployableBreachChargePlacementThink`
  - 定向圆柱伤害区 + 出口视线 → 3.2.3 `RiotDrill_CreateDangerZone` / `RiotDrillExit_HasLOSToPlayer`
  - 钉在活动物体上跟着走、物体溶解即停 → 3.2.2
  - 玩法开关表（playlist 覆盖）→ 3.2.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 瞄准 | 每帧从眼睛沿视线 trace 1750 u；碰到玩家 / NPC = "保险"失败；可穿透表面递归跳过 | `nut:1388-1434` |
| 墙厚 | 原生 `BreachTrace(起点, 方向, hull (−4,−4,0)–(4,4,32), 最大 512)`（升级 728） | `nut:1436-1469` |
| 遇护盾 | 原生回调 `CodeCallback_BreachTraceEarlyExitOnEnt`：移动护盾、护罩、加强掩体、回声定位器 → 提前停 | `nut:1471-1479`、`nut:218-221` |
| 钻头 | 投掷武器，10000 u/s，仰角 0；重力 0 → 0.2 s 后 ×1.3 → 1 s 后 ×1.8 | `txt:92-101` |
| 撞人 | 撞到非世界：一次 5 伤害；撞到玩家 / NPC / 特殊名单（Pathfinder 环、死亡箱）→ 弹开不生效 | `nut:1290-1317` |
| 钉墙 | 撞到世界 / 物体：从撞点沿速度重新 trace 求起点 → `FindEndSpikeLocation` → 建系统 | `nut:1320-1375` |
| 钻头模型 | `prop_script` 放大 ×3，动画 deploy → trans → idle → shutdown；结束时 `Dissolve` | `nut:359-362`、`nut:493-524` |
| 墙内光束 | `info_particle_system` `P_mm_breach_beam`（入口 → 出口），出口预警光束 `P_mm_breach_beam_warn`（只亮 1 s） | `nut:723-786` |
| 出口区域 | `trigger_cylinder`：原点 = 出口，朝向 = 视线（钉子角度转 90°），半径 130，往前 224，往后 0 | `nut:588-606` |
| 伤害 | 循环每 0.2 s：玩家 / NPC 4，其他 1；玩家需出口视线或离出口 ≤ 86.7 u | `nut:644-687` |
| 被钉物体 | 钉在非世界物体上：该物体每跳也挨打（不管在不在区里），物体销毁 / 死亡 / 溶解就停 | `nut:397-419`、`nut:549-577`、`nut:648-649` |
| AI 危险区 | `AI_CreateDangerousArea_Static`，半径 65（= 130 × 0.5），在入口前方 65 u | `nut:615-617` |
| 冲击特效表 | `mm_breach_start` / `_enter`（入口，0.2 s 一次）、`mm_breach_exit`（出口） | `nut:471-491`、`nut:610`；`mc:152` |
| 声音 | 入口 `Maggie_Tac_Drill_Entrance_Drilling`，出口 `Maggie_Tac_Drill_Exit_Drilling`（升级一用 `_Short`），被打 `flesh_thermiteburn_3p_vs_1p` | `nut:76-81`、`nut:425-426`、`nut:673-684` |
| 倒计时 | 入口前 20 u 一个空模型，客户端在它上面画世界空间 RUI `concussive_breach_timer`（时长 = 持续时间） | `nut:818-839`、`nut:952-977` |
| 威胁箭头 | 客户端对出口实体 `ShowGrenadeArrow(距离 = 区长, 偏移 60·up)` | `nut:1138-1148` |

服务端：放置判定（再算一遍）、伤害、实体。客户端：预览、墙厚 HUD、箭头、倒计时。

## 2. 流程

```
按战术（22/22）→ 举起；客户端开放置预览线程（每帧算一次 placement，显示墙厚 + 颜色）
  墙厚失败 / 出界 / 保险 → 加 mod drill_error（落点特效换失败版）
松开 → toss 0.85 s → OnWeaponTossReleaseAnimEvent：
  服务端再算 placement：不是 SUCCESS 且不是"允许的失败"（太厚、出界、打到人）→ 空放、不扣
  默认 balance_riotDrillProjCollision = true → 只发射钻头（点燃、不爆），扣 22
钻头飞行（先直线，0.2 s 后开始下坠）
  撞到人 → 5 伤害、弹开（无效）
  撞到墙 → 重新求入口 / 出口 → RiotDrill_CreateBreachingCharge_System
      t=0     钻头模型、墙内光束、出口预警光束；入口钻墙声、出口声；钻头动画
      t=0.4   入口冲击特效开始（mm_breach_start）
      t=1.0   出口区域生成；入口特效换 mm_breach_enter；出口特效 mm_breach_exit；倒计时 RUI；AI 危险区
              每 0.2 s 伤害一次
      t=9.0   区域结束 → 钻头 shutdown 动画 → 溶解
```

打断：被钉物体销毁 / 死亡 / 溶解；`balance_riotDrillAfterDeath = true`（默认）时主人死亡**不**打断（`nut:198`、`nut:431-432`）。

冷却：22 s（`txt:104-110`）；升级一 → 2 发（`upgrade_tac_one` ×2）、持续 6 s。

## 3. 代码

### 3.1 入口

- `OnWeaponActivate_riot_drill`（`nut:1255-1267`）：客户端开预览。
- `OnWeaponTossReleaseAnimEvent_weapon_riot_drill`（`nut:1168-1214`）：校验 → `RiotDrill_FireProjectile`（`nut:1217-1253`，`Grenade_Launch`，忽略跳板 / 重力电梯 / 黑洞）。
- `OnProjectileCollision_weapon_riot_drill`（`nut:1286-1382`）。

### 3.2 核心逻辑

#### 3.2.1 放置：`GetRiotDrillPlacementInfo` / `FindEndSpikeLocation`（`nut:1388-1469`）

```
tr = TraceLineHighDetail(eye, eye + view × 1750, ignore 自己 + 分身, MASK_SHOT)
没打到                → FAILED_OUT_OF_RANGE
打到玩家 / NPC / 特殊名单 → FAILED_SAFETY_CATCH
打到可穿透面（单向）   → 忽略它再来一次
SUCCESS 时: r = BreachTrace(tr.end, view, hull(±4, 0..32), 512 或 728)
    SUCCESS       → 出口 = r.endPos，出口法线 = r.surfaceNormal
    TOO_THICK（允许）→ 出口 = 入口
```

`BreachTrace` 和 `BREACH_TRACE_RESULT_*` 在引擎里，脚本看不到怎么判"太薄"（`WALL_THICKNESS_MIN 0.18`，`nut:29`，没被脚本用，推断交给原生）。

#### 3.2.2 钉墙：碰撞分支（`nut:1320-1375`）+ `RiotDrill_CreateBreachingCharge_System`（`nut:339-469`）

```
traceStart = 撞点 − 法线×6 − 来向×5；沿速度×20 trace → 入口
placement = { 入口, 角度 = 速度方向, result = SUCCESS }
FindEndSpikeLocation(placement)   // 返回值单独存，没写回 placement.result
SAFETY_CATCH → 作废
建系统（placement.result 仍是 SUCCESS）
```

**疑点（推断 bug）**：返回 `FAILED_GENERIC` 或 `TOO_THIN` 时 `endOrigin` 没被赋值（默认 `<0,0,0>`），但系统照样建 → 出口区域可能生成在地图原点。第 5 节要测。

钉到非世界物体：`EntityShouldStick` 才能钉，否则返还充能；钉到移动物体或 Wrecking Ball（`WRECKING_BALL_BALL_SCRIPT_NAME`）时，钻头模型放在出口内 30 u 处并挂到入口模型上（`nut:367-375`）。

#### 3.2.3 伤害区：`RiotDrill_CreateDangerZone`（`nut:569-688`）

```
trigger_cylinder( origin = 出口, angles = 钉子出口角度（up = 视线方向）, r = 130, above = 224, below = 0 )
  过滤：NPC 全部、玩家全部、非角色、其他队
end = now + 8
每 0.2 s:
    ents = 区内 + 被钉物体
    玩家 / NPC:
        远 = |中心 − 出口| > 130/1.5 = 86.7
        玩家 且 远 且 出口看不到 → 跳过
        TakeDamage(4, owner, owner, concussive_breach, DMG_BURN)
    其他: TakeDamage(1)
```

`RiotDrillExit_HasLOSToPlayer`（`nut:690-717`）：从出口 + 5·up 到玩家的 5 个点（眼、眼和中心的中点 ± 右 8 u、中心）任一 `TraceLineHighDetail(BLOCKLOS)` 通（fraction > 0.995）即可。忽略所有活着的玩家。

伤害循环里**没有队伍判断**，靠引擎的友伤规则（推断：队友不掉血）；`RiotDrill_OnDamage`（`nut:891-898`）是空函数。

#### 3.2.4 playlist 开关（`nut:198-216`）

| 变量 | 默认 | 作用 |
|---|---|---|
| `breaching_spike_after_death_override` | true | 主人死后区域继续 |
| `breaching_spike_allow_thick_override` | true | 墙太厚也能放（出口 = 入口） |
| `breaching_spike_allow_out_range_override` | true | 瞄空也能射 |
| `breaching_spike_allow_projectile_collision_override` | true | **钻头碰撞时**才建系统（false = 开火瞬间按瞄准结果建） |
| `breaching_spike_allow_player_collision_override` | true | 钻头会撞人（弹开） |
| `breaching_spike_hide_models` | true | 预览不画模型 |

false 分支（瞬间建系统）里还有"出界就射出一个会冒火花的废钻头"（`RiotDrill_DrillOutOfRange_Think`，`nut:841-868`，模型借用 `drone_frag`）。

### 3.3 客户端表现

- **放置预览** `DeployableBreachChargePlacementThink`（`nut:979-1123`）：全屏 RUI `ui/mm_riot_drill.rpak` 显示 `depth`（墙厚，失败时 −1）和颜色（墙厚 / 512 三段插值：白 → 黄 `<255,210,73>` → 橙 `<255,122,0>`）；入口标记颜色：成功蓝 `<128,188,255>` / 太厚黄 `<255,200,40>` / 其他红 `<255,40,40>`（`nut:71-73`）。
- 抛物线 `P_mm_breach_arc`，落点 `P_mm_breach_arc_end`（失败 `_fail`）（`txt:82-85`、`txt:185-188`）。
- 开火震屏：动画事件 `riot_drill_screen_shake` → 振幅 2、频率 10、0.2 s（`nut:907-919`）。
- 威胁箭头 bug（推断）：`dangerZoneTeam = player.GetTeam()`（`nut:1144`）→ `IsEnemyTeam(team, dangerZoneTeam)` 恒 false，**只有主人自己看得到箭头**，敌人看不到。

### 3.4 依赖

`BreachTrace`（原生）、`mp_weapon_maggie_common.nut`（`MaggieCommon_ImpactTableFX_Think` 定时重放特效表、`MaggieCommon_CleanUpFX`）、`Trophy_*`（Wattson 拦截塔可以电掉钻头，`nut:1304-1306`、`nut:1339-1341`）、`TrapDestroyOnRoundEnd`、`AI_CreateDangerousArea_Static`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| RIOT_DRILL_FIRE_DELAY | 1.0（下限 0.25） | s | `nut:33`、`nut:202` | 钉墙到出火 | |
| RIOT_DRILL_DURATION | 8.0 | s | `nut:34` | 出火持续 | |
| RIOT_DRILL_DURATION_UPGRADE | 6.0 | s | `nut:42` | 升级一（多一发但变短） | |
| RIOT_DRILL_BLAST_LENGTH | 224（下限 64） | u | `nut:35`、`nut:209` | 区长（沿视线） | |
| RIOT_DRILL_BLAST_RADIUS | 130（下限 64） | u | `nut:36`、`nut:208` | 区半径 | |
| 升级二长 / 半径倍率 | 1.5 / 1.5 | × | `nut:43-44` | 336 / 195 | |
| RIOT_DRILL_DAMAGE | 4 | HP / 跳 | `nut:37` | 玩家 / NPC | |
| RIOT_DRILL_DAMAGE_TICK | 0.2 | s | `nut:40` | 20 DPS，8 s 共 160 | |
| RIOT_DRILL_OBJECT_DAMAGE | 1 | HP / 跳 | `nut:39` | 道具 / 被钉物体 | |
| RIOT_DRILL_IMPACT_DAMAGE | 5 | HP | `nut:38` | 钻头撞到非世界一次 | |
| 近身免视线距离 | 130 / 1.5 = 86.7 | u | `nut:661` | | |
| MAX_RANGE | 1750 | u | `nut:30` | 瞄准距离 | |
| WALL_THICKNESS_MAX | 512（下限 400；升级 728） | u | `nut:28`、`nut:207`、`nut:1448-1453` | 最大墙厚 | |
| WALL_THICKNESS_MIN | 0.18 | u | `nut:29` | 未被脚本用 | |
| breach hull | (−4,−4,0)–(4,4,32) | u | `nut:1438-1439` | | |
| AI 危险区 | 半径 65，入口前 65 u | u | `nut:615-617` | | |
| 钻头速度 / 仰角 | 10000 / 0 | u/s / ° | `txt:92-93` | | |
| 重力阶段 | 0 → 0.2 s 后 1.3 → 1 s 后 1.8 | × | `txt:96-101` | | |
| 钻头弹跳 浅 / 陡 / 法向 | 0.2 / 0.1 / 0.2 | — | `txt:75-77` | 撞人弹开后 | |
| toss_time | 0.85 | s | `txt:27` | | |
| 充能 | 22，1/s | — | `txt:104-110` | 22 s | |
| upgrade_tac_one | 充能 ×2 | — | `txt:191-197` | 2 发 | |
| 冲击特效重放 | 0.2 / 0.2 | s | `nut:215-216` | | |
| 开火震屏 | 2 / 10 / 0.2 s | — | `nut:912-914` | | |

## 5. 未解决和要实测的

1. **出口区域朝向和长度**：推断圆柱从出口沿视线方向往外 224 u。测法：训练场对一面墙放，墙后摆 3 个 `npc_dummie`（出口正前 100 u、200 u、300 u），看谁掉血。NPC 不看视线，正好测几何。
2. 失败结果仍建系统 → 区域在 `<0,0,0>`：对很薄 / 很怪的几何（栏杆、玻璃）射，runner 记录 `riot_drill_dangerzone_threat` 实体位置。
3. 墙太厚时出口 = 入口、区域朝墙里 → 是否等于没伤害：对厚 > 512 的墙射。
4. 敌人看不到威胁箭头（`nut:1144`）：需要两个客户端，低优先级。
5. 默认（碰撞建系统）路径下充能是否在区域持续期间暂停：`ability_in_effect_regen_paused` 只在非默认分支加（`nut:1198`）→ 推断默认不暂停。记录充能曲线即可。
6. 这份脚本的 SDK 痕迹：注释 "Stopgap fix for Bug 146443"（`nut:1262`）是原版风格；未见社区注释（推断原版）。

## 6. HSD 实现

**未实现**。HSD 的世界接口 `IMovementWorld` 目前只有 `Blocked` / `SupportHeight`（`Ordnance.cs` 的 Thermite 用到），没有"穿墙求出口"。建议：

- `BreachTrace` 自己写：沿视线从入口往里步进（8 u 一步，最多 512），第一个 `!Blocked` 且之后连续 16 u 都空的点 = 出口；HSD 关卡大多是盒子，可以直接对碰撞体求射线出射点（Unity `Physics.Raycast` 反向打回来）。
- `DrillZone : ICombatEntity`：出口点 + 方向 + r130 / L224 圆柱；每 0.2 s 对敌方单位"点到轴线距离 ≤ 130 + 单位半径 且 0 ≤ 轴向投影 ≤ 224"→ `CombatSim.Damage(4, Fire)`；玩家受害者才做视线（HSD 敌人是 NPC，按 R5 不看视线）。
- 预览：`CombatHud` 显示墙厚数字和三色，照 3.3。
- 钻头投射物可以直接用 `ThrownItem`（`gravityScale` 阶段变化需要 `ThrowParams` 加 `gravityStages`，或者简化成 0 重力，差别写进 `R5-DIFF-ARCHIVE.md`：10000 u/s 飞完 1750 u 只要 0.175 s，还在 0 重力阶段，下坠为 0，差别只在瞄空时）。
- 开关：`hsd.combat.tac.riotDrill`。
