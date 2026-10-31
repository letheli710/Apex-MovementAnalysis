# Gibraltar 战术 Dome of Protection 护罩：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_weapon_bubble_bunker.nut`，`txt` = `weapons/mp_weapon_bubble_bunker.txt`，`bs` = `vscripts/_bubble_shield.gnut`。

## 0. 概要

- **技能**：Gibraltar / 战术 / Dome of Protection / `mp_weapon_bubble_bunker`（护罩本体在公共代码 `_bubble_shield.gnut`）。
- **一句话**：扔出一个圆盘（800 u/s），落地播放展开动画后在原地升起一个穹顶，持续 12 s（升级 16 s）。穹顶**挡所有子弹、投射物和爆炸**（两个方向都挡），**不挡人和 AI 走进走出**，也不挡视线。没有血量，只能被 EMP 类（Crypto EMP、Maggie 破坏球）摧毁。里面的 Gibraltar（有被动）救人更快。
- **分类**：**系统**（"挡武器不挡人"的碰撞组 + 只碰撞不受伤的护罩实体；圆柱触发器记"谁在里面"）＋ **可视化**（友 / 敌两份颜色的穹顶特效、光束、最后 5 s 换特效）。效果本身是防御（C0 2.2 待定）。
- **可拆出的部件**：
  - 挡武器不挡人的护罩实体 → 3.2.2 `CreateBubbleShieldWithSettings`，公共部件 `_shared/C-BULLET-BLOCKING-SHIELD.md`
  - "落地 → 动画 → 生效 → 预警 → 关闭"的投掷放置物 → 3.2.1，公共部件 `_shared/C-PLACEABLE-DEPLOYABLE.md`
  - 圆柱触发器 + 状态效果标记"在罩里" → 3.2.3 `CreateDomeTrigger`
  - 友 / 敌两份特效 → 3.3

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投掷 | `ThrowDeployable(weapon, params, 800, OnBubbleBunkerPlanted)`；`grenade_disc_throw 1`，重力 ×1，会弹（shallow 0.5 / sharp 0.3 / along normal 0.1） | `nut:183-210`、`txt:38-93` |
| 落地朝向 | 向下 32 u 射线取地面法线，和投掷时的角度差太大（dot < 0.55）就保持原角度 | `nut:229-246` |
| 底座 | `prop_dynamic`（`gibraltar_bubbleshield.rmdl`），不碰撞、不挡视线，scriptName `gibraltar_dome_shield`；可挂在移动物体上 | `nut:252-280` |
| 展开动画 | `prop_bubbleshield_deploy` 播完 → 才生成穹顶；之后 `deploy_trans` → `deploy_idle` | `nut:376-379`、`nut:418-425` |
| 穹顶碰撞 | `prop_script`（`bb_shield.rmdl`，`SOLID_VPHYSICS`），碰撞组 `TRACE_COLLISION_GROUP_BLOCK_WEAPONS`（"挡子弹和投射物，不挡玩家和 AI"），`SetBlocksRadiusDamage(true)`，`SetBlocksLOS(false)`，`SPF_BLOCKS_AI_NAVIGATION`，`CONTENTS_NOGRAPPLE` | `bs:221-246` |
| 穹顶血量 | 没设，`CreateBubbleShieldWithSettings` 不加伤害类型 → **不能被打掉**（推断） | `bs:221-300` |
| EMP 摧毁 | `AddEMPDestroyDevice(底座)`、`AddWreckingBallEMPDestroyDevice(底座 / 穹顶)`，`EndSignal("EMP_Destroy")` | `nut:477-481` |
| 挡 Wattson 电线 | `TeslaTrap_MakeEntityRealTimeObstructor(穹顶)` | `nut:483-484` |
| 伤害敌人 | 有这个选项（`BubbleShieldDamageEnemies`），Gibraltar 关掉（`BUBBLE_BUNKER_DAMAGE_ENEMIES = false`） | `nut:24`、`bs:296-297` |
| "在罩里" | 圆柱触发器（半径 240、上 240、下 0），进入后每帧判断距离 ≤ 240 → 状态效果 `bubble_bunker` | `nut:731-818` |
| 快速救人 | 有被动 `PAS_ADS_SHIELD` 且在罩里 → `gibraltar_fast_revive`（playlist 默认 1） | `nut:869-880`、`mp/_bleedout.gnut:1012`、`:1132`、`:1297`、`mp/sh_bleedout.gnut:493` |
| 快速治疗 | 在罩里给 `quick_heal` 额外 mod（被动切换时处理） | `sh_passives.gnut:1018` |
| 特效 | 穹顶 `P_wpn_BBunker_shield`（友 / 敌各一份，颜色控制点 1）；底座光束 `P_wpn_BBunker_beam`，最后 5 s 换 `_beam_end`；小号升级用 `_small` 系列 | `nut:33-48`、`nut:405-412`、`nut:519-532`、`bs:249-281` |
| 声音 | 持续 `Gibraltar_BubbleShield_Sustain`；最后 5 s `_Ending`；关闭 `_Deactivate`；小号升级有 `BabyBubbleShield` 版 | `nut:49-54`、`bs:283-290` |
| 标点 | `CreateWaypoint_Ping_Location(ABILITY_DOMESHIELD)` 高 35 u | `nut:365-370` |
| 关闭 | 底座挂到 mover 上，播 `prop_bubbleshield_shutdown`，溶解 | `nut:557-596` |

**客户端 / 服务端**：全部在服务端；客户端的"进罩 RUI"被注释掉（`nut:118-119`、`nut:822-848`）。

**怀疑点**：`nut` 里大段被剥掉的空行（`nut:6-10`、`nut:66-82`、`nut:128-153`、`nut:292-351`），推断是官方原码剥离（删掉了一些模式的分支）。`bs:242` 注释风格是原版。`nut:285-286` 注释掉的 `HoverVehicle_ReplaceAbilityAttachmentEntity`（S21 载具接口，S3 dedi 没有，同 Rampart 墙的处理，见 `../rampart-amped-cover/SYSTEM.md` 第 1 节），推断是 SDK 注释的。

## 2. 流程

```
按住战术（toss prep，播 deploy 音）→ 松开：ThrowDeployable 800 u/s（升级 ×1.1 = 880）
飞行 / 弹跳 → 落地 OnBubbleBunkerPlanted：
   算地面朝向；生成底座 prop；删投射物；挂到被打中的移动物体上（如果能粘）
DeployBubbleBunker：
   标点；TrackingVision POI；播展开动画直到结束；idle 动画线程
   光束特效（友 / 敌）
CreateBubbleShieldAroundProjectile：
   生成穹顶（挂在底座上）；圆柱触发器；EMP 可摧毁；挡电线
   wait 12 − 5 = 7 s → 光束换成结束版、播结束音
   wait 5 s
结束：销毁穹顶；底座关闭动画 → 溶解
```

- **冷却**：`ammo_timed`，弹匣 13、每次 13、回充 1（升级冷却 6）（`txt:82-103`、`txt:133-136`）——数值和"30 s 冷却"对不上，第 5 节要测。
- **升级**（`txt` Mods、`nut`）：投掷距离 ×1.1（`PAS_TAC_UPGRADE_THREE`，`nut:165-181`；`.txt` 另有 `upgrade_dome_throw_range` 抬 4°）；持续 16 s（`upgrade_dome_duration`）；小号穹顶（`PAS_TAC_UPGRADE_TWO`，换小号碰撞模型和特效 `bb_shield_small`）。
- **打断**：近战取消投掷（`offhand_cancelled_by_melee`）；投出后只有 EMP 能提前结束。

## 3. 代码

### 3.1 入口

- `MpWeaponBubbleBunker_Init`（`nut:83-126`）：预载两套（大 / 小）特效和模型；注册信号。
- 武器回调：`OnWeaponTossPrep`、`OnWeaponTossReleaseAnimEvent`（`nut:3-4`）。

### 3.2 核心逻辑

#### 3.2.1 投掷放置

```
deployable = ThrowDeployable(weapon, attackParams, 800 × 升级, OnBubbleBunkerPlanted)
deployable.proj.refundAmount = ammoReq；isDoorBlocker = true（推断：能卡门）
OnBubbleBunkerPlanted:
   trace(origin + up*16 → origin - 32)
   if 打到: angles = AnglesOnSurface(normal, forward)；if dot(newUp, oldUp) < 0.55: 保持 savedAngles
   底座 = CreatePropDynamic(模型, origin, angles, SOLID_NONE)；duration = 武器 fire_duration（12 / 16）
```

#### 3.2.2 护罩实体 `CreateBubbleShieldWithSettings`（`bs:221-300`）

```
prop_script, 碰撞模型 bb_shield.rmdl, SOLID_VPHYSICS
contents |= NOGRAPPLE（钩爪不能钩）
CollisionGroup = BLOCK_WEAPONS        // 挡子弹 / 投射物，不挡玩家 / AI
BlocksRadiusDamage = true；BlocksLOS = false；SPF_BLOCKS_AI_NAVIGATION
队伍 = 主人队伍；realm = 主人
特效：友方 / 敌方各一份（VisibilityFlags），挂在罩上
声音；CleanupBubbleShield(duration)；damageEnemies 时开伤害线程
```

- 两个方向都挡：碰撞组按武器，不看队伍（推断，脚本没有队伍判断）。所以**里面的人也打不出去**。
- `SPF_BLOCKS_AI_NAVIGATION`：AI 寻路会绕开（推断：AI 不走进罩里）。
- 公共代码另有 `CreateKnockbackBubbleShield`、`CreateParentedBubbleShield`（`bs:1-11`），是 TF2 泰坦护罩遗留，`bs:13-19` 的伤害下限 / 上限是给 `BubbleShieldDamageEnemies` 用的（站在罩里的敌人每秒受伤，Gibraltar 不用）。

#### 3.2.3 "在罩里"判定（`nut:731-818`）

```
trigger = CreateTriggerCylinder(origin, r=240, above=240, below=0)，挂在底座上
进入的玩家：每帧
   if 3D 距离(trigger, 玩家脚底) ≤ 240: 加 bubble_bunker（无限期，记 handle）
   else: 去掉
离开 / 死亡 / 触发器销毁: 去掉
```

注释写 `BUBBLE_BUNKER_RADIUS` "Controls the trigger size but not the dome size"（`nut:57`）——穹顶大小由碰撞模型决定，第 5 节要测模型半径。

### 3.3 客户端表现

- 穹顶特效有友方色 / 敌方色两份（`FRIENDLY_COLOR_FX` / `ENEMY_COLOR_FX`），中立队伍一份（`bs:249-281`）。
- 底座的光束最后 5 s 换成结束版，配合结束音，提示要消失了。

### 3.4 依赖的公共代码

- `ThrowDeployable`（`sh_deployable.gnut`）、`CreateFriendlyEnemyFX`、`CreateTriggerCylinder`、`AddEMPDestroyDevice`、`AddWreckingBallEMPDestroyDevice`、`TeslaTrap_MakeEntityRealTimeObstructor`、`TrapDestroyOnRoundEnd`、`FiringRange_AddToPermanentDeployableQuota`。
- `_bubble_shield.gnut` 整个文件。

### 3.5 `mp_ability_area_cloak` 是什么

- 只有 `.txt`，**没有脚本**。它的回调 `OnWeaponTossPrep_ability_group_cloak` / `OnWeaponTossReleaseAnimEvent_ability_group_cloak` 在整个 `vscripts` 里找不到定义（grep 无结果）；`OnProjectileCollision_weapon_deployable_LDOV` 是通用的（`weapons/sh_deployable.gnut:164`）。
- `.txt` 的显示名直接借了 `#WPN_BUBBLE_BUNKER`、模型也是 Gibraltar 护罩，HUD 图标却是隐身（`pilot_tactical_cloak`），`fire_duration 4`、弹匣 90（`weapons/mp_ability_area_cloak.txt:3-8`、`:71`、`:100`）。推断是早期"区域隐身"原型的残留，**和护罩功能无关，不能用**。到此为止（2026-10-31，原因：无脚本）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| BUBBLE_BUNKER_THROW_POWER | 800（升级 ×1.1） | u/s | `nut:56`、`nut:161` | 投掷速度 | — |
| playlist 投掷倍数 | base 1.0 / upgraded 1.1 | × | `nut:154-162` | 只在 `UpgradeCore_IsEnabled()` 时生效 | — |
| fire_duration | 12（升级 16） | s | `txt:68`、`txt:147` | 持续时间 | — |
| BUBBLE_BUNKER_DURATION_WARNING | 5 | s | `nut:22` | 结束预警 | — |
| BUBBLE_BUNKER_DEPLOY_DELAY | 1.0（**未使用**） | s | `nut:21` | 实际以展开动画长度为准 | 第 5 节 |
| BUBBLE_BUNKER_RADIUS | 240 | u | `nut:57` | "在罩里"触发器半径和高度 | — |
| BUBBLE_BUNKER_ANGLE_LIMIT | 0.55 | dot | `nut:26` | 落地朝向 | — |
| BUBBLE_BUNKER_DAMAGE_ENEMIES | false | — | `nut:24` | 不伤敌 | — |
| 投掷弹跳 | shallow 0.5 / sharp 0.3 / along normal 0.1 / 随机 0.05 / 滚动 0.1/s | — | `txt:84-89` | — | — |
| 投射物半径 | 竖 5 / 横 16 | u | `txt:90-91` | — | — |
| deploy_time | 0.15 | s | `txt:69` | — | — |
| 冷却 | `ammo_timed`，弹匣 13、每次 13、回充 1（升级 6） | — | `txt:82-103`、`txt:135` | 第 5 节 | — |
| 穹顶尺寸 | 由 `bb_shield.rmdl` 决定（小号 `bb_shield_small.rmdl`） | u | `nut:36`、`nut:45` | 第 5 节 | — |
| gibraltar_fast_revive | 1 | — | `mp/_bleedout.gnut:1012` | 罩里快速救人 | — |
| 伤敌下限 / 上限（未用） | 玩家 30 / 60；泰坦 250 / 16000 | HP | `bs:13-18` | Gibraltar 不用 | — |

## 5. 未解决和要实测的

1. **穹顶半径**：由碰撞模型决定（推断约 240 u，和触发器一致）。**测**：训练场放罩，从中心往外每 10 u 打射线（AgentLink `TraceLine` 用 `TRACE_MASK_SHOT`）看在哪被挡。
2. **展开时间**：`DEPLOY_DELAY 1.0` 没用，实际是 `prop_bubbleshield_deploy` 动画长度。**测**：落地到第一次挡子弹的时间。
3. **冷却**：`ammo_timed` 下 13 / 13 / 回充 1 是 13 s 还是别的（Apex 正式是 30 s 级别）。**测**：放一次后计时到图标亮。
4. **血量**：静态看不受伤。**测**：对罩打一整个弹匣，看是否破。
5. **AI 进不进罩**：`SPF_BLOCKS_AI_NAVIGATION` 的效果（R5 本地 AI 只有 Prowler 等）。PvE 很关键：如果 AI 不进罩，罩就是绝对安全区。

## 6. HSD 实现

**未实现**。现有零件：`Tacticals.cs` 的 `AWall` 实现了 `IWallBlocker`（射线穿过判断 `Crosses`、挡爆炸 `BlocksExplosions`），`CombatSim.cs:322`、`:378` 结算子弹和爆炸时会问所有 `walls`。穹顶可以作为新的 `IWallBlocker`（球面 / 半球面相交）。

建议做法（`Tacticals.cs` 加 `Dome`）：

1. 投掷：复用 `Throw.cs` 公式，800 u/s，落地才展开。
2. 半球 `IWallBlocker`：`Crosses(a, b)` = 线段与半球面相交（任何方向都挡），`BlocksExplosions = true`。半径先用 240（第 5 节测完改）。
3. 不挡人：CombatUnit 走路不受影响。
4. **PvE 关键选择**（做开关 `dome.aiCanEnter`）：
   - R5 规则推断是 AI 绕开（`SPF_BLOCKS_AI_NAVIGATION`）。HSD 如果照搬，罩就是 12 s 无敌区，对 PvE 太强。
   - 建议默认**AI 可以走进来**（近战 AI 进罩打人），远程 AI 的子弹被挡。差别写进 `R5-DIFF-ARCHIVE.md`。
5. 没有血量（R5），HSD 可留开关 `dome.hp`（默认 0 = 无限）给"特殊敌人能打破护罩"。
6. 表现：半透明半球（友方蓝），最后 5 s 闪烁。

开关建议：PlayerPrefs `hsd.combat.gibraltar.dome.*`（`duration`、`radius`、`aiCanEnter`、`hp`）。
