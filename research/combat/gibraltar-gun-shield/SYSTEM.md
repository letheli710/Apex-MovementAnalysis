# Gibraltar 被动 Gun Shield 枪盾：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_gibraltar_shield.nut`，`txt` = `weapons/mp_ability_gibraltar_shield.txt`，`gs` = `vscripts/pilot/sh_pilot_gun_shield.gnut`。

## 0. 概要

- **技能**：Gibraltar / 被动 / Gun Shield / `mp_ability_gibraltar_shield`（被动 `PAS_ADS_SHIELD` 给一把装备槽副手武器）。
- **一句话**：开镜时，左前臂前面出现一块小护盾（半径 18、高 32，正面 85° 内挡子弹），血量 = 玩家的"共享能量"。敌人打在盾上扣能量；能量打光盾碎，多出来的伤害（非爆炸）打到 Gibraltar 身上。最后一次受伤后 10 s，能量**一次补满**。开镜时按一个键可以关掉 / 打开这个功能。
- **分类**：**系统**（"挂在角色骨骼上的挡弹实体 + 血量用一个资源条 + 溢出伤害"）＋ **可视化**（盾颜色随血量三段渐变、破碎特效分友 / 敌 / 1P 三份）。效果本身是防御（C0 2.2 待定）。
- **可拆出的部件**：
  - 挂点护盾实体（GunShieldSettings：挂点、FOV、球半径、碰撞模型）→ 3.2.1，公共部件 `_shared/C-BULLET-BLOCKING-SHIELD.md`
  - 资源条当血量 + 受伤延迟回复 → 3.2.2 `GibraltarShield_ChargeThread`
  - 溢出伤害（盾碎后剩下的打到本人，爆炸除外）→ 3.2.3 `GibraltarShield_OnDamaged`
  - 血量三段渐变色 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 开镜出盾 | 副手武器 `offhand_activates_on_zoom 1`、`cooldown_type vortex_drain`、`charge_time -1`；开镜 = 开始"充能"，回调 `OnWeaponChargeBegin` | `txt:11`、`txt:43-48`、`nut:214-239` |
| 关掉功能 | mod `disabled`（`offhand_activates_on_zoom 0`），开镜中按 `+scriptCommand5` 切换 | `txt:227-230`、`nut:78-119` |
| 武器限制 | 主武器 `.txt` 有 `allow_gibraltar_shield 0` 就不出盾（默认允许） | `nut:136-152`、`nut:249-268` |
| 盾实体 | `CreateGunAttachedShield_PropDynamic`：`prop_dynamic`（`gibralter_gun_shield.rmdl`，隐藏），碰撞组 `BLOCK_WEAPONS`，挂在 `L_FOREARM_SHIELD`，`DAMAGE_EVENTS_ONLY`（只收事件，不真扣血） | `nut:485-532`、`gs:47-103` |
| 平时不碰撞 | 创建时 `SetCollisionAllowed(false)` / `DAMAGE_NO`；激活时打开 | `nut:526-527`、`nut:329-330` |
| 血量 | 玩家共享能量（`GetSharedEnergyCount / Total`），`gs.maxHealth = SharedEnergyTotal` | `nut:492`、`nut:543-548` |
| 回复 | 每帧：缺能量且 `Time() > scriptTime0` → **一次补满**；`scriptTime0` = 最后受伤 + `fire_duration`（10 s） | `nut:287-310`、`nut:423-424`、`txt:22` |
| 扣血 | `OnPostDamaged` 回调：扣共享能量；盾实体血量 `max(1, hp − dmg)`（不让引擎删掉它） | `nut:367-483` |
| 溢出 | playlist `enable_arm_shield_carryover_damage`（默认 true）：伤害 > 剩余能量 → 多出部分（爆炸除外）用 `DF_OVERFLOW` 打到本人 | `nut:68`、`nut:387-398`、`nut:476-479` |
| 标记联动 | 打盾时先调 Vantage 的 `SniperUlt_OnDamagedByPlayer_DiamondScan(owner, …)`：盾的主人被标记时，打盾也吃增伤 | `nut:381-385` |
| Whistler 联动 | Ballistic 子弹打中盾 → debuff 给盾的主人 | `../ballistic-whistler/SYSTEM.md` 3.2.3（`mp_ability_debuff_zone.nut:429-446`） |
| 特效 | `P_gun_shield_gibraltar_3P`（友 / 敌两份），颜色和亮度随能量比例变；破碎 `P_gun_shield_gibraltar_break_CP_3P`（友 / 敌）+ `_FP`（自己，相机前 50 u），3 s | `nut:18-21`、`nut:437-466`、`nut:550-575` |
| HUD | RUI `gibraltar_shield_regen`（能量条、"武器不允许"提示、按键提示） | `nut:154-188` |
| 声音 | 持续 `Gibraltar_GunShield_Sustain_1P/3P`；破碎 `_Destroyed_1P/3P` | `nut:23-26` |
| AI | 盾实体 `EnableAttackableByAI(AI_PRIORITY_NO_THREAT)` | `nut:524` |

**客户端 / 服务端**：盾的生成、扣血、回复在服务端；HUD 和开镜时的持续音在客户端预测。

**怀疑点**：
- `nut:302` 注释"Stands in for the collision-allowed latch: one active thread per shield."——像 SDK 社区补的写法（用 `file.shieldActive` 表代替原来的某个引擎接口）。
- `nut:278`"Poll player shared energy and activate the shield if we have any energy available"、`nut:284`"Important WaitFrame, see R5DEV-201218"、`nut:519`"dklein: Defensive fix for R5DEV-198772"是 Respawn 原注释。
- **"10 s 后一次补满"**（`nut:293-298`）和正式 Apex 的"慢慢回复"可能不同，推断回复逻辑被改写过。第 5 节要测。
- `nut:87-90`、`nut:146-149`、`nut:259-263` 有剥掉的空行。

## 2. 流程

```
被动 PAS_ADS_SHIELD 获得 → 给装备槽副手 mp_ability_gibraltar_shield → OnWeaponOwnerChanged：建盾实体（隐藏、不碰撞）
开镜（主武器允许、没 disabled）→ 副手"充能开始"：
   ChargeThread（每帧）：
      缺能量 且 now > 最后受伤 + 10 → 补满，更新盾血和颜色
      能量 > 0 且 盾还没激活 → ShieldActiveThread：开特效、开碰撞、DAMAGE_EVENTS_ONLY、声音
受到敌方伤害（OnPostDamaged）：
   友伤忽略；Vantage 标记增伤；
   伤害 > 剩余能量 → 溢出部分（非爆炸）留着
   扣能量；scriptTime0 = now + 10；更新颜色
   能量 ≤ 0 → 破碎特效 ×3、声音、PassiveConsumed、关盾；溢出伤害打到本人（DF_OVERFLOW）
松镜 → OnChargeEnd：关盾（特效、碰撞），线程结束
```

- **能量为 0 时开镜**：ChargeThread 不激活盾，等 10 s 补满后才在下次（或当前持续开镜中）激活。
- `DF_OVERFLOW` 伤害不会再被 Vantage 回调处理（`mp_ability_sniper_ult.nut:459` 开头就跳过）。

## 3. 代码

### 3.1 入口

- `MpAbilityGibraltarShield_Init`（`nut:46-70`）：预载；客户端 `+scriptCommand5`；服务端被动变化回调、读溢出开关。
- 被动变化 `PilotShield_OnPassiveChanged`（`nut:121-133`）：有被动就给副手，失去就收走。
- 武器回调（`txt:16-20`）：PrimaryAttack（`return 0`，不开火）、AttemptOffhandSwitch、OwnerChanged、ChargeBegin、ChargeEnd。

### 3.2 核心逻辑

#### 3.2.1 盾实体（`gs:47-103` + `nut:485-532`）

```
GunShieldSettings:
   maxHealth = 共享能量上限；spawnflags = SF_ABSORB_BULLETS
   bulletFOV = 85；sphereRadius = 18；sphereHeight = 32
   parent = 玩家, 挂点 L_FOREARM_SHIELD；vortex 挂点 L_HAND
   localVortexAngles = forward ∘ <0, −25, 0>（向左偏 25°）
   model = gibralter_gun_shield.rmdl（隐藏），modelOverrideAngles = <0, −90, 0>
   友 / 敌两份特效
CreateGunAttachedShield_PropDynamic:
   prop_dynamic 在挂点位置；碰撞组 BLOCK_WEAPONS；同 realm；队伍
   DAMAGE_EVENTS_ONLY（受伤只发事件）；SetParent(玩家, 挂点)
   weapon.SetWeaponUtilityEntity(盾) —— 武器通过这个找到它的盾
```

#### 3.2.2 资源条和回复

```
每帧（开镜中）：
   missing = total − count
   if missing ≠ 0 且 now > weapon.scriptTime0: AddSharedEnergy(missing)   // 一次补满
```

`scriptTime0` 只在受伤时更新为 now + 10（`nut:423-424`）。

#### 3.2.3 受伤和溢出 `GibraltarShield_OnDamaged`（`nut:367-483`）

```
if 攻击者是友方 → return
if 攻击者是玩家 → 先过 Vantage 增伤回调
carry = 0
if 溢出开关 且 dmg > energy: carry = dmg − energy；dmg = energy；爆炸 → carry = 0
扣能量 min(dmg, energy)；重置回复计时
盾实体 hp = max(1, hp − dmg)
if energy ≤ 0: 破碎特效（敌方色 / 友方色 / 1P）；PassiveConsumed；关盾；carry > 0 → owner.TakeDamage(carry, DF_OVERFLOW)
```

### 3.3 客户端表现

- 盾的亮度 `UpdateShieldWallFX(ent, GraphCapped(frac, 0, 1, 0.3, 1.0))`：能量 0 → 0.3，满 → 1.0（`nut:552`）。
- 颜色三段渐变 `GetTriLerpColor(frac, 白, 白与队伍色中间, 队伍色, 0.55, 0.10)`（`nut:561-575`）：推断满能量是队伍色，掉到 55% 以下变浅，10% 以下接近白。
- 破碎：敌人看到敌方色、队友看到友方色、自己在相机前 50 u 看到 1P 版，3 s 后删。

### 3.4 依赖的公共代码

- `sh_pilot_gun_shield.gnut`：`GunShieldSettings`、`CreateGunAttachedShield_PropDynamic`、`StartGunAttachedShieldFX`、`UpdateShieldWallFX`。同文件的 `CreateGunAttachedShield_PropShield` 是倒地护盾等用的另一种（注释 `gs` 约 105 行："Incap shield and others uses this function (NOT Gibraltar)"）。
- 共享能量（引擎玩家属性）：`GetSharedEnergyCount/Total`、`AddSharedEnergy`、`TakeSharedEnergy`。
- `PassiveConsumed`、`LiveAPI_SendCombatInstanceEvent`、`Survival_PlayerDealtDamage`、`AddAssistingPlayerToVictim`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| PLAYER_GUN_SHIELD_WALL_RADIUS | 18 | u | `nut:31` | 盾的球半径 | — |
| PLAYER_GUN_SHIELD_WALL_HEIGHT | 32 | u | `nut:32` | 盾高 | — |
| PLAYER_GUN_SHIELD_WALL_FOV | 85 | 度 | `nut:33` | 正面挡子弹的角度 | — |
| 偏转 | 向左 25° | 度 | `nut:503` | 盾朝向 | — |
| SHIELD_ANGLE_OFFSET | <0, −90, 0> | 度 | `nut:17` | 碰撞模型朝向 | — |
| 盾血量 | = 共享能量上限（玩家设置，脚本里没写） | HP | `nut:492` | 第 5 节 | — |
| fire_duration | 10 | s | `txt:22` | 受伤后多久补满 | — |
| enable_arm_shield_carryover_damage | true | — | `nut:68` | 溢出伤害 | — |
| PILOT_GUN_SHIELD_DRAIN_AMMO / RATE | false / 1.0（未用） | — | `nut:28-29` | 开镜耗能（关） | — |
| 亮度范围 | 0.3–1.0 | — | `nut:552` | — | — |
| 颜色分段 | 0.55 / 0.10 | 能量比例 | `nut:574` | — | — |
| 破碎特效时长 | 3 | s | `nut:448` 等 | — | — |
| 破碎 1P 距离 | 50 | u | `nut:458` | — | — |
| cooldown_type | vortex_drain | — | `txt:43` | — | — |
| 不出盾的武器 | `allow_gibraltar_shield 0`：例 `mp_ability_area_cloak.txt` | — | `nut:142` | — | — |

## 5. 未解决和要实测的

1. **盾血量**：共享能量上限来自玩家角色设置（`.set` 文件不在 `research-src`）。**测**：AgentLink 读 `player.GetSharedEnergyTotal()`。
2. **回复方式**：脚本是"10 s 无伤后一次补满"，正式版推断是逐渐回复。可能是 SDK 改写。**测**：打掉一半，记录每帧能量。
3. **哪些武器不出盾**：`grep allow_gibraltar_shield weapons/*.txt` 列表（只发现 `area_cloak` 一个是 0），**测**：拿狙击 / 霰弹开镜看。
4. 85° FOV 与 18 u 球的具体几何（引擎 vortex sphere）：侧面来的子弹是否打到人。

## 6. HSD 实现

**未实现**。现有零件：`IWallBlocker`（`CombatCore.cs:140`）可以挂在玩家身上随视线转。

建议做法：

1. 开镜时在视线前方左偏 25° 生成一块挡弹面（HSD 可简化为一个跟随视线的圆盘 `IWallBlocker`：半径 18–32 u，只挡从正面 85° 内来的子弹）。
2. 血量：单独的"盾能量"（数值先占位 75，第 5 节测完改），10 s 无伤补满（R5 本地脚本）；HSD 建议做开关 `gunShield.regen = instant | linear`，默认 `instant`（贴本地 R5），`linear` 留给手感调。
3. 溢出：盾碎后多余伤害（非爆炸）打到玩家身上。
4. PvE 价值：远程 AI 多时有用；近战 AI 不受影响。优先级低于穹顶。
5. 表现：盾颜色按能量三段渐变（满 → 队伍色，55% → 浅，10% → 白），破碎特效。

开关建议：PlayerPrefs `hsd.combat.gibraltar.gunshield.*`（`enabled`、`hp`、`regenDelay`、`regen`）。
