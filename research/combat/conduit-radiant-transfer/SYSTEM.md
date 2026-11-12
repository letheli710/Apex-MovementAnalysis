# Conduit 战术 Radiant Transfer（辐射传输）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_ability_conduit_arc_flash.nut`（1617 行），`txt` = `weapons/mp_ability_conduit_arc_flash.txt`。静态研究，2026-10-31，会话 combat-b。

## 0. 概要

- **技能**：Conduit / 战术 / Radiant Transfer / `mp_ability_conduit_arc_flash`。
- **一句话**：拿出战术时先给自己上一份打折的临时护盾；如果准星附近（50° 锥、50 m 内）有队友，按"缺盾多 + 越靠准星中心"打分挑一个，开火时射一道光束过去，给他 9 s 内慢慢充临时护盾（每秒 15，上限 125，只能填补缺的护盾），之后保持 20 s，再每 0.1 s 掉 2。
- **分类**：参考（系统 / 可视化）。**重点是指派目标系统**——它是"持续打分、选最优、HUD 上标出"的通用写法，Lifeline 无人机、以后的 PvE 伙伴 / 增益技能都能用。回盾本身简单。
- **可拆出的部件**：
  - 指派目标（持续打分选最优）→ 3.2.1 `TargetingThread` + `ScoreTarget` + `IsValidTacTarget`，公共写法见 `_shared/B-targeting.md`
  - 没目标就自用 → 3.2.2 `DoSelfCast` / `CheckTarget_thread`
  - 三段式临时护盾（充能 → 保持 → 衰减），状态用一个状态效果的强度编码 → 3.2.3
  - 目标 HUD（每个队友一个图标：护盾档位、是否最优、是否被敌人挡住）→ 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 选目标 | 服务端线程每帧给每个队友打分，最优写进 netvar `CONDUIT_ARC_FLASH_BEST_TARGET_NETVAR` | `nut:430-470`；拿到武器时启动（`OnWeaponOwnerChanged`，`nut:256`），不是拿出战术才启动 |
| 自用 | 武器拿出完成（`OnWeaponReadyToFire` 且动作是 DRAW）→ `DoSelfCast` → 给自己 0.67 倍充能 | `nut:311-326`、`nut:373` |
| 4 s 没目标就收起 | `CheckTarget_thread`：有目标就把充能条设满，4 s 没目标 `Holster()` | `nut:328-371` |
| 不开火也扣 | 收起时若 `shouldConsumeAmmoOnDeactivate` → 扣 `ammo_min_to_fire` | `nut:288-309` |
| 光束 | 粒子 `FX_TAC_BEAM`：一端挂目标胸口，另一端是挂在施法者眼前（前 9、左 7、上 5）的控制点，3 s | `nut:1167-1225` |
| 临时护盾 | 引擎 `SetTempshieldHealth`（玩家的第三条血条） | `nut:587` |
| 阶段 | 状态效果 `shields_repairing` 的强度：1.0 = 充能，0.5 = 保持，0.1 = 衰减 | `nut:34-43`、`GetArcFlashState` `nut:1227` |
| HUD | 每个队友一个 RUI `conduit_simplified_ally_ui`：可见 / 最优 / 被敌人挡 / 护盾档位图标 / 阶段剩余时间 | `nut:1301-1452` |

## 2. 流程

```
拿到 Conduit（武器 owner 变化）→ 服务端 TargetingThread 常驻；客户端 TargetingHUD_Thread 常驻
按战术：
 ├ 拿出动作完成 → DoSelfCast：给自己 TempshieldRegen(倍率 0.67)；标记"收起也要扣能量"
 ├ CheckTarget_thread：每帧看 bestTarget；有 → 充能条满（可以开火）；4 s 都没有 → 收起
 └ 开火（动画事件）→ 扣能量；对 bestTarget DoArcFlash：光束 3 s + TempshieldRegen(倍率 1)
TempshieldRegen_Thread(target)：
 ├ 发 "RefreshTempshield" 打断旧的（重复上 = 重新开始）
 ├ 充能 9 s（升级二：×0.5 = 4.5 s，可叠加剩余时间但 ≤ 9）：
 │    期望速率 = int(3 × 倍率 × 5) /s；按"累计可回复时间 × 速率"补齐（受伤 2 s 内暂停）
 ├ 保持 20 s：临时护盾 = min(当前, 缺的护盾)；被打到 0 → 结束
 └ 衰减：每 0.1 s −2，直到 0
```

打断：目标相位、被沉默、倒地、在 Revenant 暗影形态（`conduit_rev_nerf` 默认开）→ 充能暂停（`CanTempshieldRegen`，`nut:646`）；目标死亡 → 结束。

升级：`PAS_TAC_UPGRADE_ONE` → 射程 ×1.2（60 m）；`PAS_TAC_UPGRADE_TWO` → 充能时间 ×0.5（速率不变，所以总量减半？推断，见第 5 节）；`txt upgrade_tac_one` → 能量 ×2。

## 3. 代码

### 3.1 入口

- `OnWeaponOwnerChanged_ability_conduit_arc_flash`（`nut:239`）：启动选目标线程。
- `OnWeaponReadyToFire_ability_conduit_arc_flash`（`nut:311`）：自用。
- `OnWeaponPrimaryAttackAnimEvent_ability_conduit_arc_flash`（`nut:399`）：对目标施放。`OnWeaponPrimaryAttack` 直接返回 true（不发射投射物，`nut:393`）。

### 3.2 核心逻辑

#### 3.2.1 指派目标（重点）

`TargetingThread`（`nut:430`），每帧：

```
allies = GetArrayOfPossibleAlliesForPlayer(player, 含同盟)   // _utility_shared.nut:1354：同队活人（或同盟），去掉自己
best = null; bestScore = 0
for a in allies:
    s = ScoreTarget(player, a)
    if s > bestScore: best = a; bestScore = s
player.SetPlayerNetEnt(BEST_TARGET, best)     // 客户端读这个画 HUD，开火时服务端也读这个
```

`IsValidTacTarget(user, target, ignoreFaceWhenClose)`（`nut:477`）返回枚举：

```
FAILED_GENERIC：无效 / 不是友军 / 倒地 / 相位 / 暗影形态 / 正在重生
SUCCESS：ignoreFaceWhenClose 且距离 < 5 m（197 u）→ 不看朝向直接通过
FAILED_OUT_OF_RANGE：距离 > 50 m（1969 u，升级 ×1.2）
FAILED_NOT_FACING_ALLY：dot(相机→目标胸, 视线) < cos 50°
SUCCESS
```

`ScoreTarget(player, target)`（`nut:521`）：

```
if !IsValidTacTarget(…, true): return 0
shieldScore = GraphCapped(护盾比例, 0→1, 25→0)          // 缺盾越多越高，满盾 0
distScore   = GraphCapped(距离², 5m²→50m², 0→0) = 0     // 权重 0，距离不影响
coneScore   = GraphCapped(dot, cos50°→cos5°, 0→35)      // 越靠准星中心越高，5° 内满分
score = shieldScore + distScore + coneScore             // 0–60
```

要点：
- 满盾、正好在锥边上的队友得 0 分 → **不会被选**（`> bestScore` 且 bestScore 初值 0）。
- 5 m 内的队友不看朝向，但 coneScore 仍按 dot 算（背后的队友 dot < cos50° → 0 分），所以背后满盾的近处队友也选不上。
- 没有视线检查：隔墙的队友也能选（推断：HUD 有"被敌人挡住"的提示，但服务端不拦）。
- 没有"粘住"：每帧重选，准星一动最优目标就可能换人。

#### 3.2.2 自用（`DoSelfCast`，`nut:373`）

不是"没目标时的兜底"，而是**每次拿出都先给自己**（0.67 倍速率：`int(3×0.67×5) = 10`/s，9 s → 90）。之后有目标才能开火给队友；4 s 内都没目标就自动收起，能量照扣。

#### 3.2.3 临时护盾三段（`TempshieldRegen_Thread`，`nut:677`；充能 `TempshieldRegen_RegenPhase_Thread`，`nut:826`）

```
充能（state CHARGE，状态强度 1.0，时长 9 s）：
  rate = int(perFrame 3 × 倍率 × (1/0.2))            // 给队友 15/s，给自己 10/s
  每帧 if CanTempshieldRegen:
      accum += dt
      应加总量 = int(accum × rate)；本帧加 = 应加总量 − 已加总量（"追平"写法，和帧率无关）
      临时护盾 = min(当前 + 本帧, 缺的护盾, 125)
  最后一帧把剩余时间补进 accum，保证总量 = 有效时间 × rate
保持（ACTIVE，强度 0.5，20 s）：每帧 临时护盾 = min(当前, 缺的护盾)；到 0 结束
衰减（DECAY，强度 0.1）：每 0.1 s −2，并 ≤ 缺的护盾，到 0 结束
```

`CanTempshieldRegen`：受伤后 2 s 内不回（且只看施放之后的受伤）。

### 3.3 客户端表现

- 每个队友一个 HUD（`SingleTargetRui_Thread`，`nut:1301`）：
  - `isVisible` = 是合法目标（或被动的目标）且自己在可施法状态；
  - `isBestTarget` 高亮当前最优；
  - `enemyObstructing`：眼睛到队友做 6 u hull trace，打到敌人 → 提示；
  - 护盾档位图标：≤ 20% 危急、≤ 60% 低、< 100% 高、满（`nut:1405-1420`）；
  - 阶段和剩余时间（读状态效果剩余时间）。
- 光束 3 s；目标身上充能特效、受击特效。
- 声音：充能快结束 4 s、护盾快没 2 s 时提示（`nut:72-74`）。

### 3.4 依赖

- `GetArrayOfPossibleAlliesForPlayer`（`_utility_shared.nut:1354`；同文件 `UseShortNPCTitles` 有"S21 CLIENT"注释，说明共用代码也被 SDK 改过）。
- 引擎临时护盾 `Get/SetTempshieldHealth`、状态效果 `shields_repairing`。
- Conduit 被动（`pilot/sh_pilot_passive_conduit.gnut:255`）用同一个 ally 列表和另一个 netvar `CONDUIT_PASSIVE_BEST_TARGET_NETVAR`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| 锥角 | 50° | | `nut:26` `DOT_50DEGREE` | 选目标范围 | |
| 满分角 | 5° | | `nut:556` `DOT_5DEGREE` | | |
| 近距不看朝向 | 5 m = 197 | u | `nut:29` | | |
| 最大距离 | 50 m = 1969（升级 ×1.2） | u | `nut:31`、`nut:185` | | |
| 权重 护盾 / 距离 / 角度 | 25 / 0 / 35 | 分 | `nut:523-525` | 选人偏好 | 改距离权重 = 偏向近的 |
| 充能时长 | 9（升级 4.5） | s | `nut:34`、`nut:206` | | |
| 回复速率 | 3 / 0.2 s = 15 /s（自用 ×0.67 → 10 /s） | 盾 / s | `nut:38-39,41`；playlist `conduit_tac_regend_per_frame / interval` | | |
| 临时护盾上限 | 125 | | `nut:44` | | |
| 受伤暂停 | 2.0 | s | `nut:40` | | |
| 保持 | 20 | s | `nut:36` | | |
| 衰减 | 2 / 0.1 s = 20 /s | | `nut:42`、`nut:798` | | |
| 4 s 没目标收起 | 4.0 | s | `nut:360` | | |
| 光束时长 | 3 | s | `nut:1222` | | |
| 能量 | 弹匣 541，每次 270，回充 10/s → 27 s 一次 | | `txt:48-55` | **541 ≥ 2×270，推断 2 次**，见第 5 节 | |
| 开火 | `charge_time 5`、`charge_end_forces_fire 1`、`fire_duration 0.8` | | `txt:63-73` | | |

## 5. 未解决和要实测的

1. **能量 541 / 270**：按数字是 2 次；但 `ammo_stockpile_max 501`。测法：R5 runner 连按两次战术看第二次能否施放。
2. **升级二"充能时间 ×0.5"**：速率不变时总量减半，像是削弱；也可能配合"可叠加"是"更快充满"。本地化里没有 Conduit 升级的文字（`localization_english.txt` 搜不到），要看游戏内说明。
3. **对 NPC 队友**：`GetArrayOfPossibleAlliesForPlayer` 只返回玩家，NPC 不会被选。PvE 伙伴要另写。
4. 隔墙选人：测法：队友躲在墙后、准星对着墙，看 HUD 和施放是否成功。

## 6. HSD 实现

**未实现。** HSD 现在没有护盾，也没有队友，回盾部分暂时用不上；**指派目标**可以先做成公共部件。

建议做法：

- 公共部件 `TargetPicker`（新文件 `Combat/Targeting.cs`），照 `_shared/B-targeting.md`：
  ```
  Pick(source, viewDir, candidates, filter, weights) → best (score > 0)
  score = wHealth·(1 − hp/max) + wAngle·Remap(dot, cosCone, cos5°, 0, 1) + wDist·Remap(d², min², max², 1, 0)
  ```
  每帧调用，结果存起来给 HUD（`CombatHud.Draw` 画一个框，`CombatHud.UnitRect` 已有，`CombatHud.cs:168`）。
- 用途：PvE 里给"友方单位"（分身、炮台、以后的伙伴）上增益，或者反过来给敌人上标记（权重换成"血少 + 近"）。
- 回护盾：等 HSD 有护盾层再做；先可以做成"临时血"（`Health` 加一个 `temp` 字段），三段式照 3.2.3。
- 开关：`hsd.combat.radiant.*`（锥角、权重）。
