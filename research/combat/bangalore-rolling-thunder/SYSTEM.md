# Bangalore 大招 Rolling Thunder（滚雷）系统记录

来源根目录：`research-src/s21-platform/scripts/`。`gnut` = `vscripts/weapons/mp_weapon_grenade_creeping_bombardment.nut`（199 行），`gtxt` = `weapons/mp_weapon_grenade_creeping_bombardment.txt`，`mnut` = `vscripts/weapons/mp_weapon_creeping_bombardment_weapon.nut`（136 行），`mtxt` = `weapons/mp_weapon_creeping_bombardment_weapon.txt`，`bu` = `vscripts/mp/_bombardment_utility.gnut`。静态研究，2026-10-31，会话 combat-a。

## 0. 概要

- **技能**：Bangalore / 大招 / Rolling Thunder / `mp_weapon_grenade_creeping_bombardment`（扔的信号弹）+ `mp_weapon_creeping_bombardment_weapon`（看不见的投弹武器）。
- **一句话**：扔一个信号弹，落地 2 s 后从天上沿扔的方向一排排落下 36 枚"地雷火箭"（6 排 × 6 枚，每排 0.75 s 往前推进），每枚**落地插在地上 6 s 后才炸**，40 伤害 r350，被炸到的玩家 shellshock 6 s（减速 + 模糊），队友也会被 shellshock（但不掉血）。
- **分类**：好技能（大面积、延时、可预读的地毯轰炸，PvE 封路 / 驱赶）；系统（天降炮击调度器、延时引爆的"落地雷"）；可视化（信号弹烟、插地火箭冒烟、威胁箭头）。
- **可拆出的部件**：
  - 落地才激活的投掷罐 → `_shared/A-ground-canister.md`
  - 线形推进炮击（DetCord 图案）→ `_shared/A-bombardment.md` 3.2.1
  - 插地延时引爆的弹头 → 3.2.2 `CreepingBombardmentWeapon_Detonation`
  - 友伤为 0 但仍给 debuff 的伤害回调 → 3.2.3 `CreepingBombardment_DamagedTarget`
  - Shellshock → `_shared/A-shellshock.md`

### 0.1 四个脚本的关系（任务要求理清）

| 名字 | 是什么 | 和滚雷的关系 | 依据 |
|---|---|---|---|
| `mp_weapon_grenade_creeping_bombardment` | 大招本体：手里拿着、扔出去的信号弹 | **滚雷本体** | `gtxt:3-31`（hud_icon `ultimate_bangalore`、模型 `w_bangalore_canister`） |
| `mp_weapon_creeping_bombardment_weapon` | 投弹武器（隐藏副手 `OFFHAND_RIGHT`），每枚火箭是它发的导弹；它的碰撞回调负责"插地 6 s 后爆" | **滚雷的弹头** | `gnut:13`、`gnut:75-77`、`gnut:163`；`mtxt:20` |
| `mp_ability_rolling_thunder_piece` | **不是 Bangalore 的**。是 Mad Maggie 破坏球留下的碎片（加速片）用的投弹武器；"RollingThunder"是破坏球的内部代号（客户端类名 `prop_rollingthunder`、函数 `ServerCallback_RT_*`）。`.txt` 的模型是 Gibraltar 护罩占位，printname `#WPN_EARTHSHAKER` | 无关（名字撞了） | `vscripts/weapons/mp_ability_wrecking_ball.nut:273`、`:755`、`:282`、`:291-293`；`weapons/mp_ability_rolling_thunder_piece.txt:3-19` |
| `mp_weapon_sonar_dart` | **不是 Bangalore 的**。是 Sparrow（`WPN_ARTEMIS_TACTICAL` = "Tracker Dart"，追踪飞镖）的战术；它的 `.txt` 是拿滚雷的 `.txt` 复制改的，printname / readymessage 还留着 `#WPN_CREEPING_BOMBARDMENT*`、`#HUD_BURNMETER_READY_DEFENSIVE_BOMBARDMENT` | 无关（复制模板遗留） | `weapons/mp_weapon_sonar_dart.txt:3-10`；`vscripts/sh_damage_types.nut:1003`；`localization/localization_english.txt:29686-29689`；`mp_weapon_sonar_dart.nut:20-40`（全是 `sprw_` 资源） |

另：Bangalore 战术烟雾的伤害定义 `damagedef_bangalore_smoke_explosion`（10 伤害 r256）也在 `damage/damagedefs.txt:387-399`，和滚雷无关。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 信号弹 | 投掷武器 `is_toss_weapon`，1100 u/s，仰角偏移 8°，盘状扔法 `grenade_disc_throw` | `gtxt:13`、`gtxt:46`、`gtxt:119-120` |
| 落地激活 | `PlantStickyEntityOnWorldThatBouncesOffWalls(…, 0.7)` | `gnut:106`；见 `_shared/A-ground-canister.md` |
| 方向 | 出手时存 `attackParams`，落地后用 `Normalize(FlattenVec(dir))` | `gnut:79`、`gnut:172-175` |
| 信号弹烟 | 粒子 `P_bFlare` 挂 `FX_TRAIL`，持续 = 4.5 + 2 s；声音 `Bangalore_Ultimate_Flare_Hiss` | `gnut:170`、`gnut:178`、`gnut:193-197` |
| 炮击 | `Bombardment_MortarBarrageDetCord`（服务端线程） | `gnut:186-191`；`_shared/A-bombardment.md` |
| 火箭 | 投弹武器的导弹，12000 u/s（推断倍率），朝向速度 | `mtxt:14`、`mtxt:33` |
| 插地 | 导弹碰撞 → 在碰撞点生成 `prop_dynamic` 火箭模型（朝 −法线，移动物体上就挂父物体）+ 冒烟粒子 `P_bBomb_smoke` | `mnut:73-98` |
| 延时爆炸 | `wait 6.0` → `Explosion_DamageDefSimple(damagedef_creeping_bombardment_detcord_explosion)` | `mnut:100-104` |
| 爆炸 | 40 伤害（重甲 40）、内外半径都 350（**不衰减**）、推力 25000 向上 | `damage/damagedefs.txt:402-414` |
| 震屏 | 爆炸时 `CreateShake(5, 150, 1 s, 1028)` | `mnut:105-108` |
| Shellshock | 伤害回调里 `ShellShock_ApplyForDuration(victim, 6.0)`（只玩家） | `gnut:150-151` |
| 威胁箭头 | 客户端：火箭模型出现时 `ShowGrenadeArrow(player, bomb, 350, 0)` | `mnut:127-135` |
| 击杀回放 | `SetAllowForKillreplayProjectileCam`、自定义追踪镜头 | `mnut:129-130` |

服务端 / 客户端：全部判定在服务端。客户端只有威胁箭头和回放。

## 2. 流程

```
按大招（充能满 210/210）→ 掏出罐子（拿出 0.5 s），罐子开始发光 P_bFlare_glow
 按住可瞄（offhand_toss_hold_is_resumable），近战可取消（offhand_cancelled_by_melee）
松开 → toss_time 0.4 s 后出手：OnWeaponTossReleaseAnimEvent
 ├ 保证副手有投弹武器（没有就给）
 ├ 存出手方向
 └ 扣 210 弹药（= 整条充能）
罐子飞行 / 弹跳（浅 0.53、陡 0.32）→ 碰到平地（法线·上 ≥ 0.7）粘住
 └ GrenadeIgnite；thread CreepingBombardmentSmoke
     ├ 信号弹烟 + 嘶嘶声
     └ DetCord( 炮位 = 玩家当前位置 + 10000 上方, 目标 = 罐子位置, dir = 出手水平方向 )
         t = 0      开始（落地）
         t = 2.0    第 1 排（罐子所在的那排）开始发射，每排 6 发，发与发间隔 0.125 s，之字形
         t = 2.75 … 5.75  第 2–6 排，每排往前 458 u
         每发：炮位 → 落点（落点 128 u 内随机）；约 0.83 s 后落地（推断）
         落地 → 插地火箭冒烟 → 6 s → 爆（40 / r350）
         → 爆炸大约在 t ≈ 8.8 s 到 t ≈ 13.2 s 之间依次发生（推断：2 + 0.83 + 6 起，到 5.75 + 0.625 + 0.83 + 6）
     t = 6.5   信号弹烟停
```

**炮位跟玩家走**：`owner.GetOrigin() + <0,0,height>`（`gnut:186`）在罐子落地时取一次，之后不变。炮位挪到整条线中间上空（`bu:374`），所以火箭是从前上方斜着落的，不是垂直落。

打断：主人 `CleanUpPlayerAbilities` 结束信号弹烟线程（`gnut:161`）；炮击线程看的是投弹武器 `OnDestroy`；插地火箭看主人 `OnDestroy`（`mnut:75`）——**主人只是死掉（不销毁实体）时，已经插地的火箭照样爆**（推断）。

冷却：`ammo_clip_size 210`、`regen_ammo_refill_rate 1` → 210 s（`gtxt:79-84`）。`upgrade_core_ult_cooldown_reduction` mod 写的还是 210（`gtxt:207-213`，等于没减）。

## 3. 代码

### 3.1 入口

- `OnWeaponReadyToFire_WeaponCreepingBombardment`（`gnut:52-55`）：手里罐子发光。
- `OnWeaponTossReleaseAnimEvent_WeaponCreepingBombardment`（`gnut:63-83`）：`Grenade_OnWeaponTossReleaseAnimEvent` 扔出 → 给投弹武器 → 存 `file.playerLaunchParams[owner]`。
- `OnProjectileCollision_WeaponCreepingBombardment`（`gnut:85-124`）：落地判定 → `CreepingBombardmentSmoke`。命中玩家 / NPC 和命中世界两个分支做的是同一件事（`gnut:113-120`，遗留）。

### 3.2 核心逻辑

#### 3.2.1 `CreepingBombardmentSmoke`（`gnut:154-198`）

```
weapon = VerifyBombardmentWeapon(owner, "mp_weapon_creeping_bombardment_weapon")
dir    = flatten(出手方向)
h      = 地图有 bombardment_uses_extended_height ? 25000 : 10000
DetCord(weapon, marker="", dir, owner.pos + (0,0,h), canister.pos,
        width = 2750, stepLength = 2750/6, stepCount = 6, stepInterval = 0.75, delay = 2.0)
```

图案：`n = floor(2750 / (2750/6))` = 6 发 / 排（浮点除法可能算出 5.999… → 5，推断，见第 5 节），排距 458.3 u，6 排共 2750 u 长 → **一块 2750 × 2750 u（约 70 m × 70 m）的方形区域**，横向以罐子为中线，纵向从罐子往前铺。

#### 3.2.2 插地延时弹头：`OnProjectileCollision_WeaponCreepingBombardmentWeapon` / `CreepingBombardmentWeapon_Detonation`（`mnut:49-109`）

```
碰撞：主人有效、位置合法、EntityShouldStick → 防刷声音 → thread Detonation
Detonation:
    bomb = prop_dynamic(火箭模型, 碰撞点, 朝 -normal)；挂到移动物体上
    冒烟粒子；targetName = "creeping_bombardment_projectile"（客户端据此画威胁箭头）
    wait 6.0
    Explosion_DamageDefSimple(detcord, bomb.pos, attacker=owner, inflictor=owner)
    震屏
```

`ShouldCreepingBombardmentDetonateOnHitEnt` 和可插的移动物体白名单（悬浮坦克、火车、升降墙…，`mnut:20-31`、`mnut:114-123`）定义了但没被调用（推断遗留）。

#### 3.2.3 伤害回调：`CreepingBombardment_DamagedTarget`（`gnut:127-152`）

```
相位中 → 跳过
不同 realm → 0
攻击者是队友且不是自己 → 伤害 ×0（但仍往下走）
否则 → 统计
受害者是玩家 → shellshock 6 s
```

即：**敌人** 40 伤害 + shellshock；**队友** 0 伤害 + shellshock；**自己** 40 伤害 + shellshock（damagedef 没有 `DF_NO_SELF_DAMAGE`，推断会炸到自己）。`_base_gametype.gnut:237` 把这个伤害源列为"队伍无关"，所以引擎会把队友也算进爆炸，由回调把伤害清零。

### 3.3 客户端表现

- 罐子发光 `P_bFlare_glow_FP/3P`（`gnut:24-25`）；飞行拖尾 `P_bFlare_trail`（`gtxt:37-38`）；抛物线显示 `P_arc_red`、弹 1 次、腰射也画（`gtxt:47-51`）。
- 插地火箭的威胁箭头（`mnut:133-134`），显示距离 350 = 爆炸半径。
- 火箭拖尾 `P_projectile_bBomb_trail_OPT`（`mtxt:24-25`）、落地特效表 `exp_creeping_barrage_land`、爆炸特效表 `exp_creeping_barrage_detonation`（`damagedefs.txt:413`）。
- 声音：开始 `Bangalore_Ultimate_Activate`（`mtxt:38`），每发 `Bangalore_Ultimate_Rocket_Trails`（`bu:439`）。

### 3.4 依赖

`_shared/A-bombardment.md`、`_shared/A-shellshock.md`、`_shared/A-ground-canister.md`；`Grenade_OnWeaponTossReleaseAnimEvent`（`vscripts/weapons/_grenade.nut`）；`Explosion_DamageDefSimple`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| CREEPING_BOMBARDMENT_WIDTH | 2750 | u | `gnut:16` | 区域宽（也决定长） | |
| CREEPING_BOMBARDMENT_BOMBS_PER_STEP | 6 | 发 | `gnut:17` | 每排发数（排距 = 宽 / 6） | 大 → 排距变短、区域变短（长 = 排距 × 排数） |
| CREEPING_BOMBARDMENT_STEP_COUNT | 6（注释原 16） | 排 | `gnut:18` | 排数 | |
| CREEPING_BOMBARDMENT_STEP_INTERVAL | 0.75（原 1.0） | s | `gnut:19` | 排间隔 | |
| CREEPING_BOMBARDMENT_DELAY | 2.0 | s | `gnut:20` | 落地到第一排 | |
| CREEPING_BOMBARDMENT_SHELLSHOCK_DURATION | 6.0 | s | `gnut:21` | | |
| CREEPING_BOMBARDMENT_WEAPON_DETONATION_DELAY | 6.0 | s | `mnut:10` | 插地到爆 | |
| CREEPING_BOMBARDMENT_WEAPON_SMOKESCREEN_DURATION | 15.0 | s | `mnut:8` | 未用 | |
| 爆炸伤害 / 重甲 | 40 / 40 | HP | `damagedefs.txt:404-405` | | |
| 爆炸内 / 外半径 | 350 / 350 | u | `damagedefs.txt:406-407` | 不衰减 | |
| 爆炸推力 | 25000 | — | `damagedefs.txt:408` | 带 `SF_ENVEXPLOSION_UPWARD_FORCE` | |
| 炮位高度 | 10000（地图特例 25000） | u | `bu:29-30` | | |
| 落点漂移 | 128 | u | `bu:438` | | |
| 每排内发射间隔 | 0.75 / 6 = 0.125 | s | `bu:420` | | |
| 火箭速度 | 12000 | u/s | `mtxt:14` | 推断（倍率 1） | |
| 投弹武器 explosion_damage / radius / impulse | 0 / 350 / 30000 | — | `mtxt:44-48` | 落地本身不伤人；推力是否生效见第 5 节 | |
| 罐子出手速度 / 仰角偏移 | 1100 / 8 | u/s / ° | `gtxt:119-120` | | |
| 罐子弹跳 浅 / 陡 / 法向 / 随机 / 竖直随机 / 滚动 | 0.53 / 0.32 / 0.5 / 0.2 / 0.2 / 0.1 | — | `gtxt:109-114` | | |
| toss_time / toss_overhead_time / deploy_time | 0.4 / 0.4 / 0.5 | s | `gtxt:117-118`、`gtxt:99` | | |
| 罐子 explosion_damage / radius | 150 / 512 | — | `gtxt:87-92` | `SetDoesExplode(false)`，不生效 | |
| 充能 | 210 / 1 每秒 | — | `gtxt:79-84` | 210 s | |
| pas_ordnance_pack | 充能 ×1.6 | — | `gtxt:197-205` | TF2 遗留 mod | |
| 威胁箭头距离 | 350 | u | `mnut:134` | | |
| 信号弹烟持续 | 6 × 0.75 + 2 = 6.5 | s | `gnut:193-194` | | |

## 5. 未解决和要实测的

1. **每排到底几发（6 还是 5）**：`floor(2750 / (2750/6))` 浮点误差。测法：火力训练场放大招，runner 记录 `creeping_bombardment_projectile` 道具出现的数量和位置（应为 36 或 30），顺便测火箭速度（12000 是否倍率）。
2. 插地火箭爆炸时间线（推断 8.8–13.2 s）：同一次记录每个火箭模型生成和销毁时间。
3. 投弹导弹落地时 `impulse_force 30000`、`explosion_damage 0` 会不会推人。
4. 自伤：站在区域里放，看自己掉不掉 40。
5. 队友 shellshock：需要两个玩家或把 dummy 设成同队，低优先级。
6. 服务端是否 SDK 改写：本文件没看到 SDK 注释；`_base_gametype` 的 FF 列表、damagedef 数值看起来是原版风格。和官方说明对照：官方滚雷"每发 40、减速"（**记忆，未查证**），一致。

## 6. HSD 实现

**未实现**。HSD 里没有大招，也没有天降炮击。建议：

- 新建 `Runtime/Combat/Ultimates.cs`（或 `Bombardment.cs`，和 Gibraltar 共用），类 `RollingThunderFlare : ThrownItem`：`ThrowParams{ launchSpeed = 1100, pitchOffset = 8, shallow = 0.53, sharp = 0.32, alongNormal = 0.5 }`，`OnBounce` 用 `_shared/A-ground-canister.md` 第 6 节的落地判定；落地后交给 `BombardmentScheduler`（`_shared/A-bombardment.md` 第 6 节）用 DetCord 图案。
- 弹头：`DelayedMine : ICombatEntity`，落地后 6 s 调 `CombatSim.Explode(at, 40, 350, 350, 25000, owner, "rolling thunder", selfDamage: true)`，再对范围内单位 `ApplyShellshock(6)`（NPC 也给，见 `_shared/A-shellshock.md` 第 6 节）。
- 能复用：`Throw.cs`（弹道、弹跳）、`CombatSim.Explode`（伤害 + 推力 + 墙挡）、`CombatUnit.slowScale`、`Charges`（大招充能 210 s）。
- PvE 建议：火箭落地到爆的 6 s 对 AI 是"预警时间"，可以让 AI 读插地火箭做躲避（R5 里只有威胁箭头给玩家看）。
- 开关：`hsd.combat.ult.rollingThunder`；数值全部放 `ThrowParams` / 常量，和本节第 4 节一一对应。
