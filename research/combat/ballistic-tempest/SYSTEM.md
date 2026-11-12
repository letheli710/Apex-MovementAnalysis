# Ballistic 大招 Tempest 风暴：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_portable_auto_loader.nut`，`txt` = `weapons/mp_ability_portable_auto_loader.txt`，`sling` = `vscripts/pilot/sh_pilot_passive_sling.gnut`，`loc` = `research-src/s21-platform/localization/localization_english.txt`。

## 0. 概要

- **技能**：Ballistic / 大招 / Tempest / `mp_ability_portable_auto_loader`。
- **一句话**：开大后 30 s 内，Ballistic 和他 3620 u 内的队友获得：主武器换弹 / 充能时间 ×0.6、无限备弹、拿着主武器时移动加速（`speed_boost` 0.075）；Ballistic 的第三把武器（Sling）变成金色（满配件）。期间队伍击倒或击杀敌人，每个有 buff 的人 +5 s（`loc:9440`："Nearby teammates get faster reloads, faster armed move speed, and Infinite Ammo. The sling weapon will be upgraded to gold."）。
- **分类**：**系统**（光环：施法者周围每帧找队友、上同一份剩余时间的 buff、击杀延时）＋ **可视化**（背包展开、背部到队友的光束、身体光环、屏幕特效）。数值增益本身简单（C0 2.2b）。
- **可拆出的部件**：
  - 光环 buff（施法者为中心，范围内队友进入就上 buff，buff 时长 = 施法者剩余时间）→ 3.2.1 `AutoLoader_Deploy`
  - buff 本体（武器加 mod + 无限弹药 + 条件加速，结束时全部撤销）→ 3.2.2 `AutoLoader_ApplyTeammateBuff_Think`
  - 击杀 / 击倒延时（所有带 buff 的人 +5 s）→ 3.2.3 `ApplyTimeIncreaseToUlt`
  - 武器"临时换成金色版、结束换回并保留弹量"→ 3.2.4 `ConvertSlingWeaponToGold`
  - 连接光束（施法者两个挂点 → 队友胸口，2 s）→ 3.3 `WarpBeamFXThread`，公共部件 `_shared/C-AURA-BUFF.md`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 大招是否开着 | 全局网络变量 `ballisticUltIsActive`（`SNDC_PLAYER_GLOBAL`） | `nut:44`、`nut:67`、`nut:176`；背包、表情、Sling 都读它 |
| buff 计时 | 状态效果 `has_auto_loader`（1.0，30 s，淡出 0.5） | `nut:534` |
| 光环找队友 | 服务端每帧遍历同队玩家，按施法者 **脚底到脚底** 距离² 比较 | `nut:236-265` |
| 换弹快 | 武器 mod `auto_loader`：`reload_time*`、`reloadempty_time*` ×0.6；能量武器 `charge_cooldown_time`、`charge_overheat_cooldown_time*` ×0.6 | 例 `weapons/mp_weapon_r97.txt:781-795`；96 个武器 `.txt` 都有 |
| 无限备弹 | `SetInfiniteAmmoForPlayer(teammate, true, ["crate"], …)`（空投武器除外） | `nut:552-553`、`nut:561` |
| 持枪加速 | `StatusEffect_AddEndless(speed_boost, 0.075)`，只在手里的主武器有 `auto_loader` mod 时存在 | `nut:611-628` |
| Sling 变金 | 收走 Sling，按原武器 ref 重新生成；`SetWeaponLockedSetForSlingWeapon` 在大招期间设 `eWeaponLockedSet.GOLD` | `nut:326-371`、`sling:354-358`（`survival_loot.gnut:3834` 调用） |
| 背包展开 | 角色姿势参数 `characterScriptParam` = 1（结束时 0） | `nut:149-150`、`nut:316-324` |
| 背包特效 | 起始脉冲 `P_clbr_ulti_backpack_init`（控制点 1 = <10, 范围/768, 0>，2 = 颜色 134 182 255）；左右臂 `P_clbr_ulti_backpack_arm_idle_l/r`；左右喷口 `P_clbr_ulti_backpack_jet_idle` | `nut:459-520` |
| 连接光束 | 每加一个队友：施法者 `r_/l_backpiston_fx` 两个挂点 → 队友 `CHESTFOCUS`，`info_particle_system`（`P_clbr_ulti_backpack_connect`）+ `info_placement_helper` 做终点，2 s | `nut:373-457` |
| 身体光环 | `P_clbr_ulti_buff_body` 挂 `CHESTFOCUS`，隐身 / 相位时隐藏 | `nut:545-550`、`nut:643-646` |
| 屏幕特效 | 驾驶舱粒子 `P_clbr_ulti_screen` | `nut:751-778` |
| HUD | 武器 RUI 显示"快速换弹"图标（`OnPrimaryWeaponStatusUpdate_FastReloadIcon`，**本文件内没有调用**） | `nut:702-718` |
| 声音 | 开 / 关各 3 份（1P / 友 / 敌）；队友收到 / 失去；剩 5 s 警告；延时提示 | `nut:30-42` |

**客户端 / 服务端**：光环、buff、换枪都在服务端；客户端只有屏幕特效、按 `+offhand4` 时切到 Sling（`nut:720-726`）、大招结束时强制结束 Sling 的蓄力（`nut:780-790`）。

**怀疑点**：`nut:360-365` 是被剥掉的 `#if` 空行，`nut:693-695` 同样，像官方原码剥离。没有 SDK 重写迹象。

## 2. 流程

```
条件：大招满（弹匣 120，回充 1/s → 120 s）且大招没开着（OnWeaponAttemptOffhandSwitch）
按大招 → 投掷动画 1.3 s → OnWeaponTossReleaseAnimEvent
  背包展开；AutoLoader_Deploy 线程；TrackingVision POI；扣 120
AutoLoader_Deploy：
  netvar = true；ConvertSlingWeaponToGold；
  如果自己没有 buff：建背包特效 + 给自己上 buff（30 s）
  每帧：timeLeft = 自己 buff 剩余
        对每个同队、非自己、非倒地的玩家：距离² < 3620²（升级 ×50）且没有 buff → 光束 2 s + 上 buff（时长 = timeLeft）
  timeLeft 到 0 后：等手里不是消耗品（打药中不打断）；手里是 Sling 时再等它不在开火 / 换弹 / 充能 / 拉栓
  结束（OnThreadEnd）：背包收起；netvar = false；Sling 换回普通版（保留弹匣、能量状态、alt_ammo）
```

- **buff 本体**（每个人一个线程，`nut:522-650`）：上状态效果；开无限弹；每帧给手里的主武器加 `auto_loader` mod（记进 `modsToRemoveOnDrop`，扔掉时会被去掉）；手里有这个 mod 时加速，没有就去掉加速；剩 < 5 s 播警告。
- **队友离开范围**：**不会掉 buff**——只在进入时检查距离，之后不再检查（推断，代码里没有离开的判断）。
- **结束 / 打断**：施法者死亡、倒地、`AutoLoaderEnded` 结束施法者线程；队友自己死亡 / 倒地结束他的 buff。施法者的 buff 是在 `AutoLoader_Deploy` 里开的，队友的 buff 在施法者死后（`EndSignal(ballisticPlayer, "OnDeath")`）也会结束（`nut:530-531`）。
- **延时**（`nut:652-698`）：带 buff 的人击杀（且受害者不在倒地中）或击倒敌人 → 队伍所有存活、带 buff 的人：buff 剩余 + 5 s（先停再加，时长重算）；播音效、提示。施法者的光环时长看自己的 buff，所以光环也一起延长。
- **升级**：`PAS_ULT_UPGRADE_ONE`（`upgrade_ballistic_ult_range`）：范围倍数 playlist `tempest_range_upgraded_multiplier` = 50（`nut:104-132`），见第 4 节"乘在平方上"。

## 3. 代码

### 3.1 入口

- `MpAbilityPortableAutoLoader_Init`（`nut:52-83`）：注册网络变量；读 playlist `ballistic_ult_auto_loader_duration`（30）、`ballistic_ult_additional_time`（5）；服务端注册击杀、倒地回调；客户端注册 `+offhand4` 回调、buff 开关的屏幕特效回调。
- 武器回调（`txt`）：`OnWeaponAttemptOffhandSwitch`、`OnWeaponTossReleaseAnimEvent`、`OnWeaponActivate`（喊话）。

### 3.2 核心逻辑

#### 3.2.1 光环 `AutoLoader_Deploy`（`nut:163-314`）

```
inRange(t) = DistanceSqr(caster.origin, t.origin) < MAX_DISTANCE(=3620²) × (升级 ? 50 : 1)
loop while caster.buffLeft > 0:
   for t in 同队玩家, t ≠ caster, 非倒地, 非 rabid 队伍:
       if inRange(t) and !t.hasBuff: Beam(caster, t, 2 s); Buff(t, caster.buffLeft)
   WaitFrame
```

- 注意 `MAX_DISTANCE` 本身已经是平方（`nut:15`），升级的 ×50 乘在平方上 → 半径 ×√50 ≈ 7.07（3620 → 约 25600 u）。特效用的 `GetAutoLoaderVFXRange` 是 256 × 50 = 12800（不是平方，`nut:110-120`）。推断升级的设计意图就是"全图"，数值不精确无所谓。
- `IsTeamRabid`（`nut:251`）：某模式的特殊队伍，跳过。

#### 3.2.2 buff 本体 `AutoLoader_ApplyTeammateBuff_Think`（`nut:522-650`）

```
StatusEffect_AddTimed(t, has_auto_loader, 1.0, buffTime, 0.5)
身体光环特效；无限弹（除 crate）
loop while t.hasBuff:
   w = 手里的主武器（非副手、flags == WPT_PRIMARY、非固定炮台）
   if w 没有 auto_loader: AddMod(auto_loader)；登记扔掉时移除
   speed_boost 0.075：w 有 mod 就开（无限期），没有就关
   剩 < 5 s：播一次警告；剩余又变回 > 5（被延时）就重置警告
   隐身 / 相位：光环特效隐藏
结束：关无限弹；停特效、状态效果、加速；所有主武器（含 Sling）移除 auto_loader
```

#### 3.2.3 击杀延时 `ApplyTimeIncreaseToUlt`（`nut:677-698`）

```
for t in 攻击者队伍存活玩家 if t.hasBuff:
   left = 剩余；停掉 buff；重新加 buff（left + 5）
```

#### 3.2.4 Sling 变金 / 换回

- 变金（`nut:326-371`）：每帧等到有 Sling；记下 `alt_ammo`；`TakeWeaponByEntNow`；`GivePlayerSlingWeaponByRef(原 ref, 切过去, 满弹, alt_ammo)`。新武器经过 `survival_loot.gnut:3834` → `SetWeaponLockedSetForSlingWeapon`，大招中设 `GOLD` 配件组（`sling:354-358`），否则按被动升级给白 / 蓝 / 紫。武器有能量机制（`has_energized`）就直接设为已充能，时长 = `energized_duration`。
- 换回（`nut:197-228`）：记下 Sling 是否在手、弹匣、能量状态和到期时间、`alt_ammo`；`ForceChargeEndNoAttack`；收走；按原 ref 重新给（白 / 蓝 / 紫），恢复弹匣和能量。
- 生成武器用的是 `SpawnGenericLoot` 生成掉落物再装给玩家再销毁（`sling:202-229`），去掉瞄具。

### 3.3 客户端表现

- 背包：施法者看不到自己的臂 / 喷口特效（`ENTITY_VISIBLE_EXCLUDE_PARENT_PLAYER`），起始脉冲所有人可见，脉冲大小 = 范围 / 768（`nut:473`）。
- 光束：从背部两个活塞挂点分别连到队友胸口，2 s 后删除（只在队友刚进入时出现一次）。终点是 `info_placement_helper`，**创建时的位置，不跟随队友**（推断，`nut:404-408` 只设一次位置）。
- 屏幕：本人有 buff 时驾驶舱粒子，每帧把控制点 1 设成 <1, 999, 0>（`nut:769-777`）。

### 3.4 依赖的公共代码

- `SetInfiniteAmmoForPlayer`、`StatusEffect_AddTimed/AddEndless/GetTimeRemaining/StopAllOfType`、`GetPlayerArrayOfTeam`、`Bleedout_*`。
- Sling：`GetPlayerSlingWeapon`、`GivePlayerSlingWeaponByRef`、`GetStoredPreSlingWeaponRefForPlayer`、`SetWeaponLockedSetForSlingWeapon`（`sling`）。
- 其他系统对 buff 的反应：`sh_pilot_passive_knock_adrenaline.gnut:71`（有 buff 时不叠击倒加速）、`sh_gamemode_control.nut:12350`、`cl_survival_inventory.nut`（大招中不能动 Sling 栏）、`sh_emotes.nut:1532`（大招中不能表情）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| AUTO_LOADER_DURATION（`ballistic_ult_auto_loader_duration`） | 30 | s | `nut:8`、`nut:69` | buff / 光环时长 | — |
| ADDITIONAL_TIME（`ballistic_ult_additional_time`） | 5 | s | `nut:16`、`nut:70` | 每次击杀 / 击倒延长 | 大了滚雪球 |
| MAX_DISTANCE | 3620²（半径 3620 ≈ 92 m） | u² | `nut:15` | 光环半径（脚底距离） | — |
| AUTOLOADER_RANGE | 256 | u | `nut:9` | 只用于起始脉冲特效大小 | — |
| AUTOLOADER_START_EFFECT_SIZE / COLOR | 768 / <134,182,255> | u / RGB | `nut:10-11` | 脉冲特效缩放基准和颜色 | — |
| tempest_range_upgraded_multiplier | 50（乘在 u² 上 → 半径 ×7.07） | × | `nut:104-107` | 升级范围 | — |
| AUTOLOADER_SPEEDBOOST_SEVERITY | 0.075 | 严重度 | `nut:13` | 持枪加速（推断 +7.5%） | — |
| buff 淡出 | 0.5 | s | `nut:534`、`nut:690` | — | — |
| 剩余警告 | 5 | s | `nut:632` | — | — |
| 光束时长 | 2 | s | `nut:454` | — | — |
| auto_loader mod | reload / reloadempty（含 late1–5）×0.6；能量武器 charge_cooldown、charge_overheat_cooldown ×0.6 | × | `weapons/mp_weapon_r97.txt:781-795` 等 96 个 | 换弹提速 | — |
| 大招充能 | 弹匣 120、回充 1/s → 120 s | — | `txt` `MP_BASE` | — | — |
| fire_duration | 30 | s | `txt` `MP_BASE` | 推断：HUD 显示大招持续 | — |
| toss_time / toss_pullout_time | 1.3 / 0.1 | s | `txt` | 开大动画 | — |
| 无限弹例外 | `crate`（空投武器） | — | `nut:553` | — | — |

## 5. 未解决和要实测的

1. **移动加速 0.075 的实际倍数**：`speed_boost` 严重度和速度的关系（推断 +7.5%，和 Octane 被动一类）。**测**：开大后拿枪 / 空手各跑 3 s，AgentLink 记水平速度。
2. **离开范围是否掉 buff**：静态看不掉。**测**：两人局（或用 bot 队友），队友进范围后跑出 4000 u，看状态效果。PvE 单人可不管。
3. **光束终点是否跟随**：推断不跟随。看录像即可。
4. **升级半径**：×50 乘在平方上，实测半径应 ≈ 25600 u。
5. 本地 S21 客户端 + S3 dedi：S3 时代没有 Ballistic，**服务端能否加载这个脚本**要实测（开局选 Ballistic、开大，看是否报错）。

## 6. HSD 实现

**未实现**。HSD 是单人 PvE，"给队友上 buff"没有直接对象。现有零件：`Boosts.cs`（增益）、`Charges`。

建议做法（借系统，不借数值）：

1. **光环 buff 部件**（`_shared/C-AURA-BUFF.md` 的 `AuraBuff`）：施法者 / 区域为中心，每帧找范围内"友方单位"（PvE 里可以是召唤物、炮塔、Lifeline 无人机、以后的 AI 队友），进入即上 buff，**buff 时长 = 光环剩余时间**，离开不掉。HSD 第一个用户可以是"给自己的哨戒炮 / 分身加射速"。
2. **玩家自用版**：开大 30 s：换弹 ×0.6、备弹无限、持枪 +7.5% 移速（如果 HSD 有弹药系统）。HSD 没弹药时可以换成"射速 ×1.2"（新增，记 R5-DIFF）。
3. **击杀延时**：击杀 AI +5 s。PvE 怪多，必须加上限（建议总时长上限 60 s，开关 `tempest.maxTime`；R5 没有上限）。
4. **武器临时升级**：R5 的"Sling 变金"对应 HSD 的"大招期间当前武器换成满配版本，结束换回并保留弹量"——这个"临时换武器版本"的写法（3.2.4）HSD 做武器阶段时有用。
5. **表现**：背包展开 + 起始脉冲（大小 = 范围）+ 光束连到每个受益单位 2 s + 身体光环 + 屏幕边缘特效。

开关建议：PlayerPrefs `hsd.combat.ballistic.tempest.*`（`duration`、`killExtend`、`maxTime`、`range`）。
