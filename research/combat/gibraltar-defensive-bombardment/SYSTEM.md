# Gibraltar 大招 Defensive Bombardment（防御轰炸）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_grenade_defensive_bombardment.nut`（226 行），`txt` = `weapons/mp_weapon_grenade_defensive_bombardment.txt`，`mtxt` = `weapons/mp_weapon_defensive_bombardment_weapon.txt`，`bu` = `vscripts/mp/_bombardment_utility.gnut`。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Gibraltar / 大招 / Defensive Bombardment / `mp_weapon_grenade_defensive_bombardment`（扔的信标）+ `mp_weapon_defensive_bombardment_weapon`（投弹武器）。
- **一句话**：扔一个烟雾信标，落地 2 s 后，从头顶 10000 u 往信标周围 r≈768 的圈里落 6 波共 36 发等离子炮弹（每秒一波），每发**落地即爆** 40 伤害 r256（不衰减），被炸玩家 shellshock 4 s；队友不掉血但也会 shellshock。
- **分类**：好技能（圆形区域压制，PvE 守点 / 清群）；系统（天降炮击调度器的"圆形持续"图案、AI 威胁区）；可视化（信标红烟扫描、落点标记）。
- **可拆出的部件**：
  - 落地才激活的投掷罐 → `_shared/A-ground-canister.md`
  - 圆形区域持续炮击（Focused 图案）→ `_shared/A-bombardment.md` 3.2.3
  - 落地即爆的弹头 → 3.2.2 `OnProjectileCollision_WeaponDefensiveBombardmentExplosion`
  - 给 AI 的轰炸威胁区 → 3.2.1 `ThreatDetection_CreateThreatZoneForBombardment`
  - Shellshock → `_shared/A-shellshock.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 信标 | 投掷武器，1500 u/s，仰角 8°，盘状扔法；有手雷警告图标 | `txt:13`、`txt:31-32`、`txt:44`、`txt:112-113` |
| 落地激活 | `PlantStickyEntityOnWorldThatBouncesOffWalls(…, 0.7)` | `nut:94` |
| 信标烟 | 粒子 `P_artillery_marker_scan`，持续 6 + 2 s | `nut:19`、`nut:204-205`、`nut:221-224` |
| AI 威胁区 | `ThreatDetection_CreateThreatZoneForBombardment(…, 半径 1024, 1.0 s)` | `nut:207` |
| 炮击 | `Bombardment_MortarBarrageFocused(radius 1024, density 6, duration 6, delay 2)` | `nut:215-219` |
| 落点标记 | `P_ar_artillery_marker`，导弹活着时显示 | `nut:11`；`bu:497-522` |
| 炮弹 | 投弹武器导弹，4500 u/s（推断倍率），空模型 + 拖尾 `P_projectile_artillery_plasma_OPT` | `mtxt:14`、`mtxt:22`、`mtxt:26-27` |
| 爆炸 | 导弹碰撞 → `PlayImpactFXTable("exp_artillery_plasma")` + `Explosion_DamageDefSimple(damagedef_defensive_bombardment)` | `nut:111-129` |
| 伤害 | 40（重甲 40），内外半径 256，推力 25000 向上 | `damage/damagedefs.txt:427-439` |
| Shellshock | 伤害回调里给玩家 4 s | `nut:166-167` |
| 声音 | 开始 `Gibraltar_DefensiveBombardment_Activate`，每波 `…_Launch`，每发 `…_Projectile`，首发 `Gibraltar_DefensiveBombardment_Incomings_Comp_3P` | `mtxt:35-37`；`bu:149` |
| 换主人 | 武器换主人时给新主人投弹武器、拿走旧主人的 | `nut:33-52` |

全部在服务端；客户端只有特效和声音。

## 2. 流程

```
按大招（210/210）→ 掏信标（近战可取消）→ 松开扔出（过头扔 0.4 s）
 └ 保证副手有投弹武器；扣 210
信标弹跳 → 平地粘住 → GrenadeIgnite → thread DefensiveBombardmentSmoke
 ├ 信标烟
 ├ AI 威胁区 r1024，1 s
 └ Focused( 炮位 = 玩家当前位置 + 10000, 目标 = 信标, r=1024, density=6, 6 s, delay 2 )
     t=0     落地，播 Activate
     t=2.0   第 1 波：6 个区各 1 发，每发延迟随机 0.25–1.0 s
     t=3.0 … 7.0  第 2–6 波
     每发约 2.2 s 飞到（推断）→ 落地即爆
     → 爆炸约在 t ≈ 4.5 s 到 t ≈ 10.2 s（推断）
     t=8     信标烟停
```

落点"甜甜圈"：全部 36 个落点离信标 256–768 u，信标附近 256 u 内没有落点（见 `_shared/A-bombardment.md` 3.2.3）。

打断：同 Bangalore（投弹武器销毁、`CleanUpPlayerAbilities`）。已发射的炮弹不受影响。

冷却：210 s；`upgrade_core_ult_cooldown_reduction` → 180（`txt:184-190`）。

## 3. 代码

### 3.1 入口

- `OnWeaponTossReleaseAnimEvent_WeaponDefensiveBombardment`（`nut:54-71`）：给投弹武器、喊话、扔出。
- `OnProjectileCollision_WeaponDefensiveBombardment`（`nut:73-108`）：落地判定 → `DefensiveBombardmentSmoke`。

### 3.2 核心逻辑

#### 3.2.1 `DefensiveBombardmentSmoke`（`nut:191-225`）

```
weapon = VerifyBombardmentWeapon(owner, "mp_weapon_defensive_bombardment_weapon")
烟雾粒子
ThreatDetection_CreateThreatZoneForBombardment(projectile, null, pos, team=-1, 1024, 1.0)
h = 地图特例 ? 25000 : 10000
Focused(weapon, P_ar_artillery_marker, owner.pos + (0,0,h), canister.pos, 1024, 6, 6.0, 2.0)
wait 8 → 停烟
```

`DefensiveBombardment_GetRadius`（`nut:177-189`）把半径 ×1.2（playlist `passive_upgrade_gibraltar_bombardment_radius_scaler`），但**最后 `return DEFENSIVE_BOMBARDMENT_RADIUS`**，而且没人调用 → 升级"轰炸范围 +20%"在本地脚本里不生效（推断：SDK 或原版遗留 bug）。

#### 3.2.2 弹头：`OnProjectileCollision_WeaponDefensiveBombardmentExplosion`（`nut:110-129`）

```
主人无效 → 删导弹
防刷声音；特效表 exp_artillery_plasma
Explosion_DamageDefSimple(damagedef_defensive_bombardment, pos, attacker=owner, inflictor=导弹)
删导弹
```

#### 3.2.3 伤害回调：`DefensiveBombardment_DamagedTarget`（`nut:139-168`）

与 Bangalore 相同的规则（相位跳过、不同 realm 0、队友 ×0 但仍 shellshock、自己全额，推断），shellshock 4 s。多了 `ShouldDoBombardmentDamage`（PvE 保护实体的判断被注释掉，`nut:132-138`）——**说明 R5 原本就考虑过 PvE 模式下不炸某些实体**。

### 3.3 客户端表现

信标拖尾 `P_artillery_marker_trail`（`txt:36-37`）、抛物线 `P_arc_red`（弹 1 次，腰射也画，`txt:45-49`）、准星 `ui/crosshair_esmoke` + 充能环（`txt:250-290`）。落点标记粒子、炮弹拖尾见第 1 节。

### 3.4 依赖

`_shared/A-bombardment.md`、`_shared/A-shellshock.md`、`_shared/A-ground-canister.md`、`mp/_threat_detection.gnut:302`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| DEFENSIVE_BOMBARDMENT_RADIUS | 1024 | u | `nut:14` | 区域半径（落点实际 256–768） | |
| DEFENSIVE_BOMBARDMENT_DENSITY | 6 | — | `nut:15` | 区数 = 每波发数 = 每区落点数 | 大 → 发数按平方涨 |
| DEFENSIVE_BOMBARDMENT_DURATION | 6.0 | s | `nut:13` | 持续（推断实际 6 波） | |
| DEFENSIVE_BOMBARDMENT_DELAY | 2.0 | s | `nut:17` | 落地到第一波 | |
| DEFENSIVE_BOMBARDMENT_SHELLSHOCK_DURATION | 4.0 | s | `nut:16` | | |
| 升级半径倍率 | 1.2（不生效） | × | `nut:173` | | |
| 每发延迟 | 0.25–1.0 | s | `bu:144` | 同一波内散布 | |
| 波间隔 | 1.0 | s | `bu:159` | | |
| 爆炸伤害 / 重甲 | 40 / 40 | HP | `damagedefs.txt:429-430` | | |
| 爆炸内 / 外半径 | 256 / 256 | u | `damagedefs.txt:431-432` | 不衰减 | |
| 推力 | 25000，向上 | — | `damagedefs.txt:433-434` | | |
| 炮弹速度 | 4500 | u/s | `mtxt:14` | 推断倍率 | |
| 炮位高度 | 10000（特例 25000） | u | `bu:29-30` | | |
| 信标出手速度 / 仰角 | 1500 / 8 | u/s / ° | `txt:112-113` | | |
| 信标弹跳 | 浅 0.53、陡 0.32、法向 0.5、随机 0.2、竖直随机 0.2、滚动 0.1 | — | `txt:103-108` | | |
| 信标 explosion_damage / npc_explosion_damage | 0 / 150 | — | `txt:83-86` | 不爆 | |
| 威胁区 | r1024，1.0 s | — | `nut:207` | | |
| 充能 | 210（升级 180），1/s | — | `txt:73-80`、`txt:184-190` | | |

## 5. 未解决和要实测的

1. 炮弹速度（4500 是否倍率）和实际波数 / 发数：火力训练场放大招，runner 每 0.05 s 记录投弹武器投射物（类名按 `mp_weapon_defensive_bombardment_weapon` 筛），数数量、算速度、画落点分布（验证"甜甜圈"）。
2. 升级半径 ×1.2 不生效：给自己 `PAS_ULT_UPGRADE_ONE` 后再测落点分布。
3. 自伤：站在信标旁边放。
4. AI 威胁区对 NPC 的作用：刷 `npc_soldier`，看会不会跑出圈（只持续 1 s，推断只在开始时影响 AI）。

## 6. HSD 实现

**未实现**。和 Bangalore 共用 `BombardmentScheduler`（`_shared/A-bombardment.md` 第 6 节）：

- `DefensiveBeacon : ThrownItem`，`ThrowParams{ launchSpeed = 1500, pitchOffset = 8, shallow = 0.53, sharp = 0.32, alongNormal = 0.5 }`，落地后排 `FocusedPattern(center, 1024, 6, waves: 6, delay: 2)`。
- 弹头落地：`CombatSim.Explode(at, 40, 256, 256, 25000, owner, "defensive bombardment")` + 范围内 `ApplyShellshock(4)`。
- PvE 可选：修掉"甜甜圈"（落点改成圆内面积均匀随机，`Bombardment_GetRandomGroundPosInCircle` 公式 r = √u × R），开关 `hsd.combat.gibBombUniform`，默认关（= 照 R5）；升级半径按设计意图生效。
- 敌人 AI：把威胁区做成 `CombatSim` 里的"危险圈"列表，Chaser 类假人进圈就绕开；HSD 的 `Dummy` 现在没有躲避逻辑，属于以后的 AI 工作。
