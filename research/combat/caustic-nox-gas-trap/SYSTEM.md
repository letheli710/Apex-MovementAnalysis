# Caustic 战术 Nox Gas Trap（毒气陷阱）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_dirty_bomb.nut`（951 行），`txt` = `weapons/mp_weapon_dirty_bomb.txt`。毒气云本身（伤害、减速、视觉）见 [`_shared/A-gas-cloud.md`](../_shared/A-gas-cloud.md)，本文只写"罐子"。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Caustic / 战术 / Nox Gas Trap / `mp_weapon_dirty_bomb`（内部名 "dirty bomb"，罐子 scriptName `caustic_trap`）。
- **一句话**：扔出一个毒气罐（最多同时 6 个，3 次充能），立起来后变成陷阱：敌人走进 140 u 且被罐子"看见"就放毒（中号云 r282，11 s）；被敌人打 / 炸 / 近战也会放毒（没立好前被敌人打则拆掉）；放毒后罐子还能被打掉（150 血）提前结束。
- **分类**：好技能（PvE 布防：陷阱、减速、穿盾持续伤害）；系统（**放置 → 布防 → 视线触发 → 生效 → 可被摧毁**的陷阱状态机、数量上限挤掉最旧的、主人可回收）；可视化（展开动画、毒罐顶部喷气、倒计时哔声、队友 HUD 图标）。
- **可拆出的部件**：
  - 陷阱状态机 → 3.2.1 `DeployCausticTrap`
  - 视线锥触发（触发器粗筛 + `FindVisibleEntitiesInCone`）→ 3.2.2 `DirtyBombProximityActivationUpdate`
  - 按伤害类型决定"引爆 / 拆除"→ 3.2.3 `OnDirtyBombCanisterDamaged*`
  - 每人数量上限、挤掉最旧 → 3.2.1（`owner.e.activeTraps`）
  - 主人回收返还充能 → 3.2.4 `WaitForCanisterPickup`
  - 毒气云 → `_shared/A-gas-cloud.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 扔出 | `ThrowDeployable(weapon, attackParams, 1.0, OnDirtyBombPlanted)`；800 u/s，仰角 2°，继承玩家速度 ×0.2，hull ±5 × 0–10 | `nut:837-863`；`txt:34-39` |
| 落地 | 通用部署碰撞 `OnProjectileCollision_weapon_deployable_LDOV`（`VEHICLES_LARGE_DEPLOYABLE`）→ 粘住后调 `deployFunc` | `txt:23`；`vscripts/weapons/sh_deployable.gnut:164-177` |
| 罐子 | `CreatePropScript(caustic_gas_tank.rmdl, SOLID_CYLINDER)`，血 150，重甲，可被近战，Bloodhound 扫描可见 | `nut:106-155` |
| 小地图 / 高亮 | 本队小地图常显；本队 / 自己 `sp_friendly_hero` 高亮 | `nut:127-135` |
| 防重生区 | `CreateNoSpawnArea(半径 256)` | `nut:142` |
| AI 威胁 | `ThreatDetection_CreateThreatZoneForTrap` | `nut:158` |
| 展开 | 动画 `prop_caustic_gastank_predeploy`（扔出来时跳过）→ `_predeploy_idle` → 变实体 → `_deploy` | `nut:207-213` |
| 触发区 | `trigger_cylinder` 半径 140、上下各 128，只认角色 | `nut:412-448` |
| 视线 | 每帧对触发区里的每个敌人：从罐子 +48 u 朝敌人做 45° 视锥、140 u 的 `FindVisibleEntitiesInCone`（测 hitbox） | `nut:467-547` |
| 放毒 | `CreateGasCloudMediumAtOrigin(canister, owner, 罐子 + (0,0,48), 11.0)` | `nut:657` |
| 放毒表现 | `GasTrap_Activate`、循环 `GasTrap_TrapLoop`、顶部粒子 `P_gastrap_start`、高亮换 `caustic_gas_canister`；最后 5 s 每秒 `Wpn_ArcTrap_Beep` | `nut:638-685` |
| 被打 | 实体回调：未布防 / 布防中 / 放毒中三套 | `nut:205`、`nut:219`、`nut:654` |
| 回收 | 主人对罐子按 Use → 充能 +100（一发） | `nut:688-750` |
| 上限 | `owner.e.activeTraps` 最新插在前，超过 6 个就 `pop()` 最旧的并销毁 | `nut:221-230` |
| 移除 | 动画 `prop_caustic_gastank_destroy` + 渐隐，然后销毁 | `nut:373-404` |
| 队友 HUD 图标 | `ui/dirty_bomb_marker_icons.rpak`，显示血量 | `nut:785-829`（`DirtyBomb_CreateBombHUDMarker`，没看到调用者，推断未用） |

服务端：全部判定。客户端：Use 提示文字（只有主人能拿，`nut:754-783`）、小地图、HUD。

**SDK 痕迹**：`CafeMod_IsEnabled("mitosis")`（罐子不停分裂扔出新罐子，`nut:235-320`）是社区"咖啡 mod"玩法；`CausticTrap_OnDamaged_Activated` 手写扣血 + `NotifyDidDamage`（`nut:323-371`）像社区补的（原版应该靠引擎扣血，推断）。

## 2. 流程（状态机）

```
[投掷] 按战术（≥ 100 / 300）→ 0.65 s 扔出（扣 100）
   ↓ 落地粘住（OnDirtyBombPlanted）
[展开] 生成罐子（不可伤、不实体）→ 设 DAMAGE_EVENTS_ONLY
   │   被"敌方玩家"打（非自己毒气）→ Disarmed → [移除]
   ↓ predeploy_idle → 变实体 → deploy 动画结束
[布防] 开触发区；可回收；加入 activeTraps（超 6 个挤掉最旧）
   │ 主人 Use → PickedUp（+1 充能）→ [移除]
   │ 被打：毒气伤害 → 忽略
   │       爆炸 / 近战 → [放毒]
   │       子弹打中 hitbox > 0 → [放毒]；hitbox 0 → Disarmed → [移除]
   │ 敌人在 140 u 内、非相位、非隐身、视锥看得见 → 警告哔声 → [放毒]
   ↓
[放毒] Signal "DirtyBomb_Active"（触发区、回收线程结束）
   │ 0.2 s 后：血回满 150，换成"可被打掉"的伤害回调，生成中号毒气云 11 s
   │ 被打（非毒气）→ 扣血，≤ 0 → [移除]（云因来源消失再留 2 s）
   │ 6 s 后每秒哔一次
   ↓ 11 s
[移除] Detonated → 摧毁动画 + 渐隐 → 销毁
```

主人 `OnDestroy` / `CleanUpPlayerAbilities` → 所有阶段都直接移除（`nut:103`、`nut:624-625`）。主人只是死亡（不销毁）时陷阱保留（推断）。

冷却：`ammo_timed`，300 / 100 每发，每秒 5 → 3 发、每发 20 s（`txt:99`、`txt:116-121`）；`extra_tactical_charges` mod 600（6 发）。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_weapon_dirty_bomb`（`nut:837-863`）：`ThrowDeployable`，部署函数 `OnDirtyBombPlanted`。
- `OnDirtyBombPlanted`（`nut:871-901`）：找主人（投射物主人不是玩家就用武器主人），记位置 / 角度 / 父物体（可以放在移动平台上），`thread DeployCausticTrap`，删投射物。

### 3.2 核心逻辑

#### 3.2.1 `DeployCausticTrap`（`nut:95-257`）

见第 2 节状态机。要点：
- 放在移动物体上时，罐子挂到一个 `script_mover` 上，mover 再挂父物体（`nut:165-174`）。
- `owner.IsNPC()` 时 `owner.SetSecondaryEnemy(canister)`、罐子不可被其他 AI 当目标（`nut:147-151`）——**R5 支持 NPC 放毒罐**。

#### 3.2.2 视线触发：`OnDirtyBombAreaEnter` / `DirtyBombProximityActivationUpdate`（`nut:450-547`）

```
进入触发区且有非本队角色 且 没有在跑的检测线程 → thread 检测
检测（每帧，直到区内没有敌人）:
    targets = 区内非本队；ignore = 区内本队 + 所有 "dirty_bomb" 实体
    for e in targets（同 realm、非相位、非隐身）:
        hits = FindVisibleEntitiesInCone(罐子+48, 方向→e, 140, 半角 45, ignore, PLAYERSOLID, 测 hitbox)
        hits 里有任何 target → 哔 → DetonateDirtyBombCanister → return
```

"敌人"的判断是 `GetTeam() != team`（`nut:458`、`nut:492`），所以中立 / 无队伍的东西也算（推断：PvE 的 NPC 只要不同队就能触发）。

#### 3.2.3 被打：三个回调

| 阶段 | 函数 | 规则 |
|---|---|---|
| 展开中 | `OnDirtyBombCanisterDamaged_PreArmed`（`nut:595-609`） | 攻击者是玩家、不是主人、伤害不是毒气 → 拆除 |
| 布防 | `OnDirtyBombCanisterDamaged`（`nut:549-593`） | 毒气 → 忽略；`isBusy` → 忽略；爆炸 / 近战 → 放毒；否则 hitbox > 0 → 放毒，= 0 → 拆除 |
| 放毒中 | `CausticTrap_OnDamaged_Activated`（`nut:323-371`） | 毒气 → 忽略；给攻击者打击反馈；扣血；≤ 0 → 关伤害、移除 |

"hitbox 0 拆除"的意思（推断）：罐子模型的 hitbox 0 是底座 / 通用部位，打中"罐体"（hitbox ≥ 1）才会破裂放毒——给敌人一个"打底座可以安全拆"的玩法。

#### 3.2.4 回收：`WaitForCanisterPickup` / `PickUpCanister`（`nut:688-750`）

只有主人；不在倒地；当前战术槽是毒罐 → `clip = min(clip + 100, max)`。

### 3.3 客户端表现

抛物线 `P_arc_green_bounce` / 落点 `P_arc_green_end`，忽略玩家速度（`txt:28-33`）；Use 提示 `#WPN_DIRTY_BOMB_DYNAMIC`；小地图图标 `rui/hud/tactical_icons/tactical_caustic`（`nut:904-913`）。毒气的屏幕效果见 `_shared/A-gas-cloud.md` 3.3。

### 3.4 依赖

`ThrowDeployable` / `sh_deployable.gnut`、`CreateGasCloudMediumAtOrigin`（`_shared/A-gas-cloud.md`）、`MakeEntityAsGasEmitter`（让云的墙裁剪 trace 忽略罐子，`nut:137`）、`FindVisibleEntitiesInCone`（引擎）、`ThreatDetection_CreateThreatZoneForTrap`、`CreateNoSpawnArea`、`AddSonarDetectionForPropScript`。`DirtyBomb_Destruction`（`nut:937-950`）被 Newcastle 大招落地时调用（`mp_ability_armored_leap.nut:6483`）：只放破坏特效和声音。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| DIRTY_BOMB_MAX_GAS_CANISTERS | 6 | 个 | `nut:22` | 同时存在上限 | |
| DIRTY_BOMB_HEALTH | 150 | HP | `nut:30` | 放毒后可被打掉 | |
| DIRTY_BOMB_DETECTION_RADIUS | 140 | u | `nut:34` | 触发区半径 + 视锥距离 | |
| 触发区上下高度 | 128 / 128 | u | `nut:425-426` | | |
| 视锥半角 | 45 | ° | `nut:528` | | |
| DIRTY_BOMB_GAS_CLOUD_HEIGHT | 48 | u | `nut:38` | 视锥起点 + 云心高度 | |
| DIRTY_BOMB_GAS_FX_HEIGHT | 45 | u | `nut:37` | 未用 | |
| DIRTY_BOMB_ACTIVATE_DELAY | 0.2 | s | `nut:41` | 触发到出毒 | |
| DIRTY_BOMB_GAS_DURATION | 11.0 | s | `nut:33` | 云寿命 | |
| DIRTY_BOMB_CLOUD_LINGER_TIME | 2.0 | s | `nut:31` | 云余留（`sh_gas` 用） | |
| 哔声开始 | 结束前 5 s，每 1 s | s | `nut:659-664`、`nut:681-685` | | |
| DIRTY_BOMB_GAS_RADIUS | 256 | u | `nut:32` | 只用于防重生区；**云半径是 282**（`GAS_CLOUD_RADIUS_MEDIUM`） | |
| DIRTY_BOMB_THROW_POWER | 1.0 | × | `nut:36` | | |
| 放置相关（PLACEMENT_RANGE、ANGLE_LIMIT…） | 64 / 32 / 0.55 / 20 | — | `nut:42-48` | 旧的"放在脚边"模式，未用（推断） | |
| 出手速度 / 仰角 / 继承 | 800 / 2 / 0.2 | u/s / ° / × | `txt:34-36` | | |
| 罐子投射物 hull | (−5,−5,0)–(5,5,10) | u | `txt:38-39` | | |
| 弹跳 浅 / 陡 / 法向 / 随机 / 滚动 | 0.5 / 0.3 / 0.1 / 0.05 / 0.1 | — | `txt:105-110` | | |
| toss_time / 升级 | 0.65 / 0.55 | s | `txt:101-102`、`txt:228-233` | | |
| 充能 | 300 / 100，5/s（`ammo_timed`） | — | `txt:99`、`txt:116-121` | 3 发，每发 20 s | |
| extra_tactical_charges | 600 | — | `txt:215-219` | 6 发 | |
| `.txt` explosion 字段 | 0 伤害，250 / 450 | — | `txt:72-75` | 不用 | |
| damagedef_dirty_bomb_explosion | 750 / 2000，r256 | — | `damage/damagedefs.txt:359-370` | **没有调用者**（推断旧版"毒罐被打爆会炸"的遗留） | |

## 5. 未解决和要实测的

1. **NPC 能不能触发**：火力训练场刷 `npc_dummie` 走进罐子 140 u，看是否放毒（视锥只认 `targetEnts` 里的实体，dummy 是角色，应该能）。这是 PvE 的关键。
2. hitbox 0 拆除：对罐子不同部位开枪，看哪里放毒、哪里拆除。
3. 放毒后打掉罐子，云是否 2 s 后消失（`sh_gas` 的"来源无效 → 余留 2 s"）。
4. SDK 改写范围：`CausticTrap_OnDamaged_Activated` 手动扣血和原版行为（原版放毒后罐子能不能被打掉）是否一致——没有原版可对照，记为疑点，测"放毒后打 150 伤害罐子会不会消失"。

## 6. HSD 实现

**未实现**。建议：

- `GasTrap : ThrownItem`（`ThrowParams{ launchSpeed = 800, pitchOffset = 2, inheritScale = 0.2, shallow 0.5, sharp 0.3, alongNormal 0.1 }`），落地后变成 `GasTrapUnit : CombatUnit`（150 血、可被子弹打），状态机照第 2 节，用一个 `enum Stage { Deploying, Armed, Venting, Removing }`。
- 触发：每帧对敌方单位 `距离 ≤ 140 && 高度差 ≤ 128 && 夹角 ≤ 45° && WorldClear(罐+48, 单位中心)`。夹角其实恒满足（视锥方向就是指向目标的方向），等效于"140 u 内且有视线"——HSD 直接这么写，差别为 0（推断）。
- 放毒：生成 `GasCloud`（`_shared/A-gas-cloud.md` 第 6 节），半径 282、11 s。
- 上限 6、挤掉最旧：`Satchel`（`Ordnance.cs`）已有"最多 2 个，第三个挤掉最旧"的写法，照搬。
- "打底座拆除"：HSD 的 `CombatUnit` 没有 hitbox，只有头部区（`headHeight`）。可以把"底部 12 u"当底座，命中底座 = 拆除；开关 `hsd.combat.gasTrapDisarm`。
- 给 NPC 用：R5 支持 NPC 主人（3.2.1），HSD 敌人以后可以直接复用这个类。
