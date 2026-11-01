# 近战：基础拳头、传家宝、Titan Sword、Power Sword：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`mel` = `vscripts/melee/sh_melee.gnut`，`surv` = `weapons/mp_weapon_melee_survival.txt`，`hand` = `weapons/melee_pilot_emptyhanded.txt`，`ts` = `vscripts/weapons/mp_weapon_titan_sword.nut`，`tsb` / `tsd` / `tsh` / `tsl` / `tss` / `tsu` = 同名 `_block` / `_dash` / `_heavy` / `_launcher` / `_slam` / `_super.nut`，`tst` = `weapons/mp_weapon_titan_sword.txt`，`mts` = `weapons/melee_titan_sword.txt`，`pst` = `weapons/mp_weapon_power_sword.txt`，`stub` = `vscripts/weapons/_missing_callback_stubs.gnut`。

逐字段全表：[`PARAMS.md`](PARAMS.md)。

## 0. 概要

- **武器**：所有人的拳头（持握 `mp_weapon_melee_survival` + 出招 `melee_pilot_emptyhanded`）；传家宝（同样两件套）；Titan Sword（可捡主武器）；Power Sword（只有数据）。
- **一句话**：近战由"持握武器"接按键、"出招武器"给数值，引擎做锥形吸附和判定，脚本扣血和击退。基础拳 30 伤害、60 u 射程。**传家宝全部和拳头数值一样，只差外观。** Titan Sword 是一套完整的连招系统（轻、重、上挑、下砸、冲刺、格挡、超级），但本地构建把入口回调关了，飞行也被注释掉。
- **分类**：
  - 效果：拳头是基础手段（PvE 敌人贴脸时）。Titan Sword 值得做。
  - 可视化：传家宝的挥砍特效、Titan Sword 的特效和 HUD。
  - 可复用系统：两件套近战、吸附和击退公式、Titan Sword 的"按状态分招 + mod 改数值"、格挡（方向判定 + 减伤 + 充能）。
- **可拆出的部件**：
  - 按键到判定的基础流程 → 3.2.1
  - 击退和反冲公式 → 3.2.2
  - 传家宝的数据变体 → 3.2.3
  - 招式分发（mod 切数值）→ 3.2.4
  - 格挡 → 3.2.5
  - 资源：燃料和超级 → 3.2.6
  - 下砸（高度检测 + 落地范围伤害）→ 3.2.7
  - 冲刺（状态效果 + 跟随触发器）→ 3.2.8
  - 掉落物旋转表演 → 3.2.9

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 攻击键变近战 | `attack_button_presses_melee 1` | `surv:15` |
| 实际出招的武器 | 手里武器是 offhandMelee 就用它，否则 `GetOffhandWeapon( OFFHAND_MELEE )` | `mel:1177-1194` |
| 吸附 | 引擎 `PlayerMelee_LungeConeTrace` + `Lunge_SetTargetEntity` | `mel:1257`、`mel:1416` |
| 判定 | 引擎 `PlayerMelee_AttackTrace`（范围 `GetMeleeAttackRange`） | `mel:1475-1480` |
| 扣血 | 服务端 `target.TakeDamage`，source = 武器类名 | `mel:1500`、`mel:1565` |
| 击退 | 玩家 `KnockBack`（0.25 s）；NPC `PushEnt` | `mel:1652`、`mel:1659` |
| 打中玻璃 | `BreakSphere( endPosition, 50 )` | `mel:1525` |
| Titan Sword 招式 | 按状态往武器加 mod | `ts:267-300`、`ts:346-358` |
| 格挡 | 开镜（ADS）= 格挡 mod；`AddDamageCallback( "player" )` 里减伤 | `tsb:38`、`tsb:112-116`、`tsb:205-328` |
| 燃料 | 状态效果 `titan_sword_fuel`，时长 = 冷却 | `ts:754-755` |
| 超级 | 状态效果 `titan_sword_super`，netvar 记充能到达时刻 | `tsu:46`、`tsu:490` |

**S3 / S21 差异和补丁**（字段证据见 [`../_shared/W-S3-FIELD-CHECK.md`](../_shared/W-S3-FIELD-CHECK.md)，是字符串证据，不是行为证据）：

字段核对只搜了 exe；SDK 的 `server.dll` 另有实现（源码 `research-src/s21-r5sdk/src/game/`），所以"exe 里没有"不等于"dedi 上不工作"。下面引用 SDK 源码的地方是读过的；行为都待实测。

1. **Titan Sword 的招式入口没绑定**。`tst:21-22`："Disabled on dedi: this script callback is not bound there"，`OnMeleeWeaponPrimaryAttack` 和 `OnMeleeWeaponSecondaryAttack` 被注释掉。`ts:267-300` 的分发函数（冲刺、下砸、重击、上挑、超级轻击）因此没有调用入口；全项目 grep 也没有别的调用者。推断：本地 Titan Sword 只剩格挡、超级、持握，按左键效果要实测。
2. **所有让玩家飞的调用都被注释掉**：`tsd:244`（冲刺）、`tsl:163`、`tsl:195`（上挑）、`tss:167`（下砸）、`ts:953`（空中连击）、`ts:334`。全部 7 处 `//…PlayerLaunch(` 都在 Titan Sword 文件里。另一个文件 `vscripts/weapons/mp_ability_revenant_shadow_pounce_free.nut:332` 还在正常调用，SDK 也有 dedi 版实现（`research-src/s21-r5sdk/src/game/server/player_launch.cpp`，脚本入口 `research-src/s21-r5sdk/src/game/client/vscript_player.cpp:136`、`:959`），所以函数是有的。没有注释说明谁注释的、为什么。只看脚本：即使绑定了入口，冲刺也不会移动玩家（推断）。
3. **`melee_knockback_velocity_magnitude`**：exe 只有客户端有，但 SDK 把它放进预留槽 `custom_float_1`（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3070`），`mel:1625` 能读到。值是否正确待实测（第 5 节第 2 条）。
4. **`melee_allow_held`**（`tst:97`）：SDK 只做名字映射到 `custom_float_0`（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3190`），没有看到连击逻辑。按住连击待实测。
5. **`deflect_missile_impacts_dot`**：SDK 放进预留槽 `custom_float_3`（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3072`），`tsb:223` 能读到；`deflect_missile_impacts` 只做名字映射（同文件 `:3177`）。格挡判方向用的是脚本，按这个看能跑；挡投射物的引擎行为待实测。
6. **`melee_block_*`、`fuel_cooldown_sec`、`super_max`、`slam_vel_z` 等两个引擎都不认，靠脚本读**（`GetWeaponInfoFileKeyField_Global*`），不依赖引擎版本。
7. 双份写法：`mel:1320`（"dual-arity: S3 SERVER 1-arg; S21 CLIENT 2-arg"，`PlayerMelee_StartAttack`）；`mel:1449`（"S3 dedi: 2-arg callback; S21 client: 3-arg"，`CodeCallback_OnMeleeAttackAnimEvent`）；`ts:319-320`（`ACT_VM_MELEE_LIGHT` 等 S21 的活动号，只在客户端编译，dedi 靠 `activity_types.txt` 注册）。这些是本地补丁，近战主路径明确被社区改过。处决 `vscripts/melee/sh_melee_synced.gnut:190`、`:972` 也有 "S3: ... not available" 注释，本记录不展开。
8. `mel:1270` 的 `FS_1v1_ShouldBlockLobbyMelee` 是 Flowstate 加的，HSD 不用。

## 2. 流程

### 基础拳头

```
按攻击键（持握）或近战键 → CodeCallback_OnMeleePressed
  AttackerCanStartMelee：活着、没在出招、主手没禁用、不在相位、没在吸附、playlist quick_melee_enabled
  清副手；PlayerMelee_StartAttack；TryDoorLunge；发声；选中出招武器
出招活动开始 → CodeCallback_OnMeleeStartActivity
  move_slow 严重度 > 0.05 → 不吸附
  否则找吸附目标；地面上吸附时锁俯仰
动画事件 → CodeCallback_OnMeleeAttackAnimEvent
  判定 → Melee_Attack：扣血 → 特效 → 击退 → 自己反冲
打中非世界物体：恢复时间走 quick（0.4 s），否则 normal（0.75 s）
```

### Titan Sword（S21 设计，本地入口没绑定）

```
主攻击：ADS 中 → 冲刺（要燃料）
        空中且 slam_ready → 下砸
        否则 → 重击
副攻击：地面且有燃料 → 上挑
        否则 → 轻击（超级中加 super_melee）
ADS：格挡
+scriptCommand3：充能满 → 超级（2.33 s 启动 + 20 s）
```

- 招式结束：`OnWeaponCustomActivityEnd` 清 mod（`ts:303-336`）。
- 下砸：离地 ≥ 200 u 得 `slam_ready`；出招后禁用大招、战术、消耗品（`tss:33`、`tss:353`）；落地 `OnPlayerSlamLand`。
- 超级：启动期间锁武器和近战、不能翻越和跑墙；其他武器槽上锁（`tsu:49-55`，本地上锁代码在 `tsu:630-633` 之后是空的）；结束重置充能。
- 死亡：剑掉地（`ts:605-625`，火力训练场除外）。

## 3. 代码

### 3.1 入口

- 基础：`CodeCallback_OnMeleePressed`（`mel:1312`）、`CodeCallback_OnMeleeStartActivity`（`mel:1400`）、`CodeCallback_OnMeleeAttackAnimEvent`（`mel:1451-1483`）、`Melee_Attack`（`mel:1485-1713`）。
- Titan Sword：`MpWeaponTitanSword_Init`（`ts:165`，各模块 Init `ts:179-185`），`OnWeaponActivate_weapon_titan_sword`（`ts:229`）。

### 3.2 核心逻辑

#### 3.2.1 持握 + 出招两件套

持握武器（`surv`）负责按键和移动：`surv:27` 移动 ×1.15，`surv:17` 不挡冲刺。出招武器（`hand`）给数值。

**持握和出招的 `melee_range` 不一样**：持握 40（`surv:98`），出招 60（`hand:21`）。`GetPlayerMeleeOffhandWeapon` 只在手里武器是 offhandMelee 时用手里那把（`mel:1183`）；持握是 `fire_mode automatic`（`surv:12`），所以判定用 60（推断，第 5 节第 1 条）。其他数值两边相同。

目标过滤 `IsValidMeleeAttackTarget`（`mel:1199-1239`）：玻璃总可打；要 `CanBeMeleed`；同队看友伤；要同 realm；相位不可打；处决中不可打。

NPC 特例（`mel:1541-1546`）：NPC 能被地面处决时，伤害 = 当前血量、加 `DF_RAGDOLL`、力清零。

#### 3.2.2 击退和反冲（`mel:1622-1686`）

```
dir = 视线方向；hitWithFlatTrace 时压平并归一
push = melee_knockback_velocity_magnitude × dir
if dir · (目标中心 − 自己中心) < 0: push = −push
if Titan Sword 的 VictimHitOverride 接管: 跳过默认击退
else if 目标是玩家: KnockBack( push, 0.25 )
else: PushEnt( push × (在地面 ? 1.0 : 0.1) )     // NPC 空中只有 10%
结束吸附
自己反冲 = −push；z = 0；× 0.5
if 不是在打地面（endPos.z − 10 > 自己脚底）且 反冲方向 · 当前速度 ≤ 0:
    KnockBack( 反冲, 0.25 )
```

最后一条：反冲不会让人加速。拳头 350 → 自己最多被推 175。

没打中目标：再打一条射线（`mel:1576-1578`），用于特效；打到敌方玩家时直接 return，不给击退（`mel:1584-1585`）。

#### 3.2.3 传家宝 = 数据变体

对 `weapons/melee_*.txt` 全部 41 个文件、`Mods` 之前的玩法字段做差异（字段：`melee_damage`、`_heavyarmor`、`melee_range`、`melee_angle`、`melee_attack_animtime`、三个 `melee_lunge_*` + `melee_lunge_time`、`melee_knockback_velocity_magnitude`、两个恢复时间、`melee_freezelook_on_hit`、`melee_allow_held`、`melee_can_hit_titans`、`damage_flags`、`impulse_force`），基准是 `hand`：

| 文件 | 和基础拳头的差别 |
|---|---|
| 其余 37 个：`melee_wraith_kunai`（+rt01）、`octane_knife`（+rt01）、`revenant_scythe`（+rt01）、`crypto_heirloom`（+rt01）、`ash_heirloom`、`bangalore_heirloom`、`bloodhound_axe`、`caustic_hammer`、`fuse_heirloom`、`gibraltar_club`、`horizon_heirloom`、`lifeline_baton`、`loba_heirloom`、`mirage_statue`、`newcastle_heirloom`、`pathfinder_gloves`、`rampart_wrench`、`seer_heirloom`、`valkyrie_spear`、`wattson_gadget`、`hook_sword`、`artifact_dagger`、`artifact_sword`、9 个 `agnostic_*`、`pilot_emptyhanded` 本身 | **无差别** |
| `melee_boxing_ring` | `melee_knockback_velocity_magnitude` 600（`:16`）、`melee_raise_recovery_animtime_quick` 0.75（`:15`） |
| `melee_shadowsquad_hands` | `melee_damage` 150（`:12`）、吸附范围 150、角度 80（`:13-14`） |
| `melee_shadowroyale_hands` | `melee_damage` 50（`:3`）、吸附范围 100、角度 60（`:4-5`） |
| `melee_titan_sword` | 见第 4 节 |

持握版 `mp_weapon_*_primary.txt`（36 个）和 `surv` 比：只有 `deployfirst_time` 不同（检视动画时长，1.6 到 4 s，如 `mp_weapon_newcastle_heirloom_primary` 4、`mp_weapon_fuse_heirloom_primary` 1.6）。

传家宝的差别只有：

| 方面 | 怎么差 | 例子 |
|---|---|---|
| 模型 | `viewmodel` / `playermodel` | |
| 打击表 | `impact_effect_table` | `melee_kunai`、`melee_bhaxe`、`melee_gurkha` |
| 挥砍特效 | `OnWeaponActivate_melee_*` 按状态选 | `vscripts/weapons/melee_wraith_kunai.nut:31-43`（地面普通挥、冲刺突刺，空中和滑铲用默认动画） |
| 动画 | 按状态选动画序列 | `vscripts/weapons/melee_revenant_scythe.nut:9-11`（冲刺旋转、滑铲、跳） |
| 外观 mod | `AddMod` | `vscripts/weapons/melee_crypto_heirloom.nut:85` |

Mods 里有两类和伤害有关的：所有 `melee_*` 都有 `proto_door_kick`（`hand:113`：范围、角度、吸附 ×1.4，踢门用）；部分有 `pas_extra_melee_damage`（`melee_agnostic_breachbeam.txt:137`，`melee_damage ++40`、击退 ×2）。

一致性是有意的：`vscripts/sh_mod_heirloom_parity_keys.gnut` 是生成的字段清单（含 `melee_damage`、`melee_range`、`melee_knockback_velocity_magnitude`、吸附字段），`vscripts/sh_mod_heirlooms.gnut:398` 遍历它。

**没有脚本的传家宝**：9 个 `melee_agnostic_*`、`melee_hook_sword`、`melee_newcastle_heirloom` 的回调全是空壳（`stub`，打印 "[WEAPON-STUB] ... is not implemented in this build"，`stub:255`）。回调只管特效，所以推断还能打，没挥砍特效。

结论（HSD）：传家宝 = 一条外观记录。不要给它们写逻辑。

#### 3.2.4 招式分发：mod 切数值

`ts:267-300`（入口未绑定，见第 1 节）。关键做法：所有招式共用一把武器和同一个 `Melee_Attack`。

```
TitanSword_SafelyAddAttackMod( weapon, mod ):
  客户端不在预测中 → return
  清所有招式 mod；加这个 mod
```

mod 把 `melee_damage`、`melee_range`、`melee_angle`、`melee_attack_animtime`、吸附、动画全部换掉（`tst:217-278`）。判定和击退完全不改。受击表现用 `TitanSword_VictimHitOverride`（`ts:896`），`mel:1645` 留了钩子：

| 招式 | 命中目标的运动 | 来源 |
|---|---|---|
| 上挑 | 目标速度 z = `launcher_vel_z` 800 | `tsl:244-257` |
| 下砸 | 视线水平 × 2000，z = −2200 | `tss:667-683` |
| 轻击 | 双方都在空中时：自己 z 150，目标 z 250 | `ts:913-929` |

`TitanSword_LaunchEntity`（`ts:949-961`）：玩家分支是空的（`PlayerLaunch` 注释），NPC 走 `PushEnt`。所以对 NPC 有效。

`TitanSword_TryMultiAttack`（`tsh:84-94`）：多目标判定已被剥空，固定返回 false，`tsh:17-19` 的横扫常量（150 u、90° × 30°）没有地方用。

#### 3.2.5 格挡（`tsb`）

```
线程：IsWeaponInAds → 加 blocking mod + 手势；否则去掉（tsb:110-148）

TitanSword_OnDamaged( player, damageInfo ):   // 对所有玩家受伤
  手里不是 Titan Sword → return
  blocked = 有 blocking mod 且 CanBeBlocked 且 视线·受力方向 ≤ deflect_missile_impacts_dot（−0，即正面 180°）
  if blocked:
     伤害 = clamp( floor( 伤害 × block_scale ), 1, 999 )     // 0.15，超级 0.05
     加 DF_SOUR；特效；格挡动画
     攻击来源是 Titan Sword → 攻击者被推 1150（KnockbackPlayer 内再 ×0.5）
     否则 → 自己 move_slow 0.65，1 s，淡出 0.5
             Kraber（mp_weapon_sniper）→ 自己被推 1150
  else:
     伤害 × owner_damage_scale   // 0.85，超级 0.7；强化体 1.0 / 0.82
  非超级且攻击者是敌人：超级充能 += ceil( 原伤害 × 0.3 )
```

`CanBeBlocked`（`tsb:151-203`）：没方向的不能挡；列表内不能挡（毒、铝热、电弧、地形伤害等，`tsb:174-198`）。注释里写"只挡子弹和爆炸"，但那行被注释掉（`tsb:159-164`），实际是黑名单。

注意拿着剑**不格挡**也减伤 15%。

PvE 用途：抗 AI 子弹很合适。减速 0.65 是按伤害事件上状态效果，AI 连射时会一直被减速。

#### 3.2.6 燃料和超级

燃料是一个状态效果：`TryUseFuel` 上 `titan_sword_fuel` 15 s（`ts:754-755`），`HasFuel` = 没有这个状态 或 在超级中（`ts:775`）。一个燃料共用给冲刺和上挑。HUD 读 `TitanSword_GetFuelScale`（`ts:786-792`）。

充能（`tsu`）：`NETVAR_TITAN_SWORD_SUPER` 存"满的时刻"，捡到后 +200 s（`tsu:346`）。加充能 = 把时刻提前：

```
timeCost = amount × super_cooldown_sec / super_max     // 200 / 1200 = 1/6 s 每点
newTime = 满的时刻 − timeCost
```

来源：造成伤害（`tsl:237-238`，玩家、假人、战斗 NPC；倒地的不算）；受到伤害 ×0.3（`tsb:324-325`）。推断：纯靠时间 200 s，打满 1200 点伤害也行。

开启 `TitanSword_ActivateSuper_Thread`（`tsu:468`）：`+scriptCommand3`（`tsu:151`）。加 `super` mod（移动 ×1.4），填满燃料，状态效果时长 2.33 + 20 s；启动期 `LockWeaponsAndMelee`、禁翻越、禁跑墙和二段跳（`tsu:499-522`）。一直到死亡、倒地或时间结束，`OnThreadEnd` 重置充能（`tsu:551`）。

失败条件 `TryActivateSuper`（`tsu:749-782`）：翻越、跑墙、挂墙中不行；武器要 ready。

`tsu:88-127`、`tsu:221`、`tsu:238` 有 playlist 热修开关（`titan_sword_super_*_hotfix`），注释 R5DEV-554107。

#### 3.2.7 下砸

- 检测（服务端线程，`tss:172-236`）：`CanSlam`（不在地面、不在滑索、不在太空电梯）时每帧向下打 10000 u 射线，高度 ≥ `slam_height_required` 200 → 加 `slam_ready`。
- 发动（`tss:324-415`）：`player.Signal( "JumpPad_GiveDoubleJump" )`；喷射特效；0.4 s 后每帧等落地。
- 落地（`tss:452-488`、`tss:529-592`）：`RadiusDamage`，伤害 `slam_damage_max` 60（内半径 65、外 350），`SF_ENVEXPLOSION_NO_DAMAGEOWNER`，`DF_RAGDOLL | DF_EXPLOSION`，source `mp_weapon_titan_sword_slam`。友军震屏。
- 防双倍（`tss:594-630`）：被下砸的近战打中的目标记进 `slamVictims`，范围伤害 × `slam_damage_scale`（0）。
- 击退（`tss:635-663`）：先清速度，`力 = GraphCapped( 距离, 0, 350, 600, 250 )`，方向 = 水平 + (0, 0, 0.5)。

#### 3.2.8 冲刺

`TitanSword_Dash_TryDash`（`tsd:121-143`）：只在格挡中发动。先检查"冲刺中已松镜 → 取消转重击"。

`TitanSword_Dash_Thread`（`tsd:155-273`）：状态效果 `titan_sword_dash` 0.5 s；地面 1400 u/s，空中 950（`tsd:23-24`）；空中冲刺上 `titan_sword_dash_sickness` 5 s（落地清，`tsd:248`、`tsd:278`），再次空中冲刺保留 85% 下落速度（`tsd:240-242`）；强制站立；0.1 s 后在玩家身上建 `trigger_cylinder`（半径 50、高 80，横放，持续 0.4 s，`tsd:267`）。

触发（`tsd:283-298`）：碰到敌人或门 → 停止、清速度、0 伤害加 `DF_KNOCK_BACK`。注释说这是撞停，不是攻击。作者注释 "This is kinda ass"（`tsd:157`）。真实移动的那行被注释（`tsd:244`），只算了 `dashVec`。

通用部件：`TitanSword_CreateHitbox`（`tsd:426-459`），跟随玩家的触发器 + 每帧查询 + LOS。

#### 3.2.9 掉落物表演

`LootSpin_Thread`（`ts:440` 起）：掉落物挂到 mover，上升 400 u（射线防穿顶）旋转，0.67 s 后下落（每秒 700 u，夹在 0.3–1.2 s），插在地上。开关：火力训练场和空投不演。

### 3.3 客户端表现

- 燃料 HUD：`ui/titan_sword_dash_meter.rpak`（`ts:102`），字段 `dashFrac`、`hasUnlimitedDash`、`hintText`（`ts:886-888`）。
- 超级 HUD：`ui/weapon_hud_charged_gh.rpak`（`tsu:78`）。
- 特效按招：`P_pilot_sword_swipe_light / heavy / launch / slam / super`，挂在 `blade_tip` / `blade_turn` / `blade_mid`（`ts:216`、`tsh:42`、`tsl:59`、`tss:79`）。
- 冲刺地面拖痕：每 20 u 一个 impact（`tsd:325`、`tsd:340-344`）。
- 预测：`InPrediction` 守卫贯穿全部 mod 操作（`ts:348-351`）。HSD 单机不需要。

### 3.4 依赖的公共代码

- 状态效果：`../../_shared/E-STATUS-EFFECT.md`；`move_slow`（`mel:1408`、`tsb:283`）：`../../_shared/B-move-slow.md`。
- 伤害回调和修正：`../../_shared/C-DAMAGE-MODIFIERS.md`；武器伤害字段：`../_shared/W-DAMAGE.md`；mod 系统：`../_shared/W-MOD-SYSTEM.md`。
- 字段核对：`../_shared/W-S3-FIELD-CHECK.md`。

## 4. 参数

### 4.1 招式对比

| 字段 | 拳头 `hand` | 重击 `heavy_melee` | 轻击（剑基础） | 上挑 `launcher` | 下砸 `slam` | Power Sword | `melee_titan_sword` |
|---|---|---|---|---|---|---|---|
| `melee_damage` | 30（`hand:56`） | 60（`tst:242`） | 25（`tst:91`） | 40（`tst:263`） | 60（`tst:221`） | 40（`pst:68`） | 30（`mts:16`） |
| `melee_range` | 60（`hand:21`） | 125（`tst:240`） | 100（`tst:87`） | 150（`tst:261`） | 继承 100 | 150（`pst:64`） | 100（`mts:14`） |
| `melee_angle` | 30（`hand:54`） | 70（`tst:239`） | 80（`tst:86`） | 60（`tst:260`） | 继承 80 | 80（`pst:63`） | 80（`mts:13`） |
| `melee_attack_animtime` | 0（`hand:55`） | 1.0（`tst:241`） | 0.5（`tst:88`） | 1.2（`tst:262`） | 继承 0.5 | 0.5（`pst:65`） | 0.5（`mts:15`） |
| `melee_lunge_time` | 0.35（`hand:61`） | 0.1（`tst:250`） | 0.4（`tst:98`） | 1.0（`tst:273`） | 0.4（`tst:223`） | 0.4（`pst:75`） | 0.6 |
| `melee_lunge_target_range` | 60（`hand:60`） | 0（`tst:251`） | 100（`tst:99`） | 300（`tst:274`） | 100（`tst:224`） | 200（`pst:76`） | 75 |
| `melee_lunge_target_angle` | 30（`hand:59`） | 1（`tst:252`） | 45（`tst:100`） | 75（`tst:275`） | 75（`tst:225`） | 60（`pst:77`） | 45 |
| `melee_lunge_no_target_range` | 60（`hand:58`） | 0（`tst:253`） | 0（`tst:101`） | 300（`tst:276`） | 0（`tst:226`） | 0（`pst:78`） | 0 |
| `melee_knockback_velocity_magnitude` | 350（`hand:62`） | 150（`tst:244`） | 150（`tst:93`） | 50（`tst:265`） | 继承 150 | 150（`pst:70`） | 150（`mts:18`） |
| `melee_raise_recovery_animtime_normal` | 0.75（`hand:19`） | 继承 0.2 | 0.2（`tst:89`） | 0.5（`tst:266`） | 继承（`slam_ready` 0.5，`tst:212`） | 0.2（`pst:66`） | 0.15（`mts:19`） |
| `melee_raise_recovery_animtime_quick` | 0.4（`hand:20`） | 继承 0.2 | 0.2（`tst:90`） | 0.5（`tst:267`） | 继承 | 0.2（`pst:67`） | 0.15（`mts:20`） |
| `melee_freezelook_on_hit` | 0.25（`hand:24`） | 0.25（`tst:247`） | 0.25（`tst:94`） | 0.35（`tst:270`） | 继承 | 0.25（`pst:71`） | |
| `melee_can_hit_titans` | 0（`hand:18`） | 1（`tst:246`） | 1（`tst:85`） | 1（`tst:269`） | 继承 | 1（`pst:62`） | |

调参：`melee_range` 大了手长；`melee_lunge_target_range` 大了吸附远，大到 300（上挑）就是位移技；`melee_attack_animtime` 决定一招的时长；`melee_knockback_velocity_magnitude` 决定推开多远（自己反冲是它的一半）。

### 4.2 Titan Sword 系统字段

| 字段 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| `fuel_cooldown_sec` | 15 | s | `tst:57` | 冲刺、上挑共用冷却 |
| `super_max` | 1200 | 点 | `tst:58` | 充能总量 |
| `super_cooldown_sec` | 200 | s | `tst:59` | 自然充满 |
| `super_active_sec` | 20 | s | `tst:60` | 超级时长 |
| `melee_block_scale` | 0.15 | × | `tst:61` | 正面挡下后的伤害 |
| `melee_block_scale_super` | 0.05 | × | `tst:62` | 超级时 |
| `melee_block_min_damage` | 1 | HP | `tst:63` | 下限 |
| `melee_block_max_damage` | 999 | HP | `tst:64` | 上限 |
| `melee_block_charge_scale` | 0.3 | × | `tst:65` | 受伤转充能 |
| `melee_block_sword_knockback` | 1150 | u/s | `tst:66` | 挡住剑时推攻击者 |
| `melee_block_sword_slow` | 0.65 | 严重度 | `tst:67` | 挡子弹时自己减速 |
| `deflect_missile_impacts_dot` | −0 | dot | `tst:68` | 格挡朝向，SDK 预留槽 |
| `owner_damage_scale` | 0.85 | × | `tst:69` | 拿着剑时受伤 |
| `owner_damage_scale_super` | 0.7 | × | `tst:70` | |
| `owner_damage_scale_fort` | 1.0 | × | `tst:71` | 强化体不叠减伤 |
| `owner_damage_scale_super_fort` | 0.82 | × | `tst:72` | |
| `slam_height_required` | 200 | u | `tst:73` | 下砸最低高度 |
| `slam_force_min` | 250 | u/s | `tst:74` | 边缘击退 |
| `slam_force_max` | 600 | u/s | `tst:75` | 中心击退 |
| `slam_radius_inner` | 65 | u | `tst:76` | |
| `slam_radius_outer` | 350 | u | `tst:77` | |
| `slam_damage_min` | 60 | HP | `tst:78` | 脚本没用（`tss:535` 读了，`tss:574-575` 只传 max） |
| `slam_damage_max` | 60 | HP | `tst:79` | |
| `slam_damage_scale` | 0 | × | `tst:80` | 已被近战打中的目标 |
| `slam_vel_z` | −2200 | u/s | `tst:81` | 本地没生效（`tss:167`） |
| `launcher_vel_z` | 800 | u/s | `tst:82` | 玩家没生效；打中 NPC 有效 |
| `move_speed_modifier` | 1.15（`super` ×1.4 → 1.61，推断） | × | `tst:155`、`tst:199` | 持握移动 |
| `TITAN_SWORD_DASH_SPEED` | 1400 | u/s | `tsd:23` | 没生效（`tsd:244`） |
| `TITAN_SWORD_DASH_SPEED_AIR` | 950 | u/s | `tsd:24` | 同上 |
| `TITAN_SWORD_SUPER_ACTIVATION_DURATION` | 2.33 | s | `tsu:57` | 启动 |
| `MELEE_KNOCKBACK_DURATION` | 0.25 | s | `mel:144` | 玩家被击退时长 |

### 4.3 Power Sword

只有数据：`pst`。没有 `.nut`（`vscripts/scripts.rson` 没有它，`vscripts/weapons/` 没有文件），所有回调在 `stub`（`PowerSword_OnWeaponActivate` 等，`stub:189-194`、`stub:213-215`、`stub:229`），`survival_loot.csv` 也没有它。模型路径是 `heirloom_agnostic_v24_powersword`（`pst:20-21`），本地包里有没有没查（静态读不了 rpak）。

设计信息只能从字段推断（全是推断）：蓄能 + 能量（`regen_ammo_refill_rate 0.5`，`charging` mod 7，`pst:55`）；近战 40，吸附 200 u；飞行投射物 1700 u/s（`pst:131`），爆炸 45、半径 180（`pst:155`、`pst:158`）。按下列 mod 名看：`blocking_util`、`ultimate`、`charging`，是一套"格挡 + 能量 + 发波"，和 Titan Sword 同一路（`melee_block_*` 完全相同，`pst:82-88`）。HSD 能用的是这组数值作参考，代码没有可抄的。

全部 mod 字段看 [`PARAMS.md`](PARAMS.md)。

## 5. 未解决和要实测的

1. **基础拳头实际射程**：持握 40、出招 60。测：火力训练场对假人，从远到近每 5 u 打一下，读命中的临界距离。
2. **击退量**：`melee_knockback_velocity_magnitude` 走 SDK 预留槽，`mel:1625` 拿到的是不是 350。测：打假人（`PushEnt`）量位移，自己反冲量速度；用 AgentLink 或录制。**只能打假人**，local NPC 不还手。
3. **Titan Sword 能做什么**（`tst:21-22` 入口没绑定）。测：`give mp_weapon_titan_sword`，左键、右键、近战键、ADS、`+scriptCommand3` 各按一次，看 console（`printt( "TRYING LAUNCHER" )` 这类）和动作。结果决定第 1 节第 1 条的推断。
4. **格挡方向**：`deflect_missile_impacts_dot` 走 SDK 预留槽，确认正面 / 背后判定。用第二个客户端或可开火的武器从正面、背后打持剑玩家，读伤害（预期 15% / 85%）。
5. **`melee_allow_held`**：按住攻击能否连击。
6. **`melee_titan_sword` 什么时候用到**：`mts` 有数值，source id 也注册了（`vscripts/sh_damage_types.nut:137`），但 vscripts 里没有地方发这把武器。推断：引擎按主武器的设置换出招武器，也可能根本没被用。测：持剑按近战，读 damageSourceId。
7. **`proto_door_kick` 踢门**：×1.4 什么时候生效，看 `TryDoorLunge`（`mel:1344`）。不紧急。

## 6. HSD 实现

**未实现**。现状（grep `HSD-Unity/Assets/HSD/Game/Runtime/Combat/`）：

- `CombatCore.cs` 有 `DamageKind.Melee`。玩家没有近战武器（`WeaponKind` 只有 Rifle、SmartPistol、Inferno，`Weapons.cs`）。
- **敌人有近战**：`Dummy` 的追逐型有 `meleeRange 48`、`meleeDamage 10`、`meleeInterval 1`（`CombatCore.cs`），`CombatSim.cs` 里 `Damage( d.target, ... DamageKind.Melee ... )`。没有吸附和击退。
- 分支 `origin/claude/w2-framework-b44e35`（HSD-Unity 仓库）有 `StatusEffects.cs`、`MoveSlow.cs`、`DamageModifiers.cs`（`KindScale` 可按 `DamageKind` 缩放）。格挡的减速和减伤都可以用它们，不用另写。

建议做法：

1. **基础拳头**（`Combat/Melee.cs`）：`MeleeAttack` 数据结构 = 第 4.1 节的列。流程：按键 → 锥形找吸附目标（范围、角度）→ 地面锁俯仰 → 判定 → 伤害 → 击退 → 反冲（第 3.2.2 节公式，含"不加速"那条）。先照 `hand`：30、60 u、30°，吸附 60 u、0.35 s，击退 350。
2. **招式系统**：不要每招一个类。一把武器 + 按状态选一份 `MeleeAttack`（R5 的 mod 切换），受击运动用委托。
3. **Titan Sword**：先做格挡（ADS + 方向 + 减伤 + 减速）和重击 / 轻击，这部分 R5 代码完整。冲刺、上挑、下砸的玩家位移 R5 本地被注释掉，**HSD 要按字段值自己实现**（1400 / 950 u/s、800 u/s、−2200 u/s），差别写进 `R5-DIFF-ARCHIVE.md`。
4. **传家宝**：做成外观数据，不做逻辑。

和移动系统要对齐的：`move_slow > 0.05` 不吸附（`mel:1407-1410`）；吸附中不能再次出招（`mel:1285`）。

开关建议：`hsd.combat.melee.lunge`、`knockback`、`sword.dashEnabled`。
