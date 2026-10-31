# 公共部件 B：电击（EMP）减速 + 屏幕干扰 + NPC 击晕

批次 B 共用。Wattson 电网直接调用；Ash 电弧陷阱、Conduit 屏障是否走这里见各自记录。APEX-REPORT 2.2（电弧星）已经研究过同一套代码，本文只补"给一个固定时长"的那条分支（`empDurationOverride`），以及 NPC 的分支。

来源根目录：`research-src/s21-platform/scripts/vscripts/`（下文简写）。

## 0. 概要

- **部件**：`Electricity_DamagedPlayerOrNPC`（`weapons/_weapon_utility.nut:3114`）。伤害回调里调用，给受害者上"电击"效果。
- **一句话**：玩家 → 移动 ×0.5、转向 ×0.3、屏幕雪花；NPC → 按种类击晕（打断动作）或机械类加伤；同一个 NPC 3 s 内只吃一次。
- **分类**：系统（可复用的状态效果）。
- **可拆出的部件**：
  - 定时状态效果（带淡出）→ 3.1 `GiveEMPStunStatusEffects`
  - 屏幕干扰强度 / 时长曲线 → 3.2 `EMPWeapon_EffectsPlayer`
  - NPC 击晕免疫窗 → 3.3 `Electricity_ShouldStunNPCAndAddImmunity`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 移动减速 | 状态效果 `eStatusEffect.move_slow`，`StatusEffect_AddTimed(ent, id, 强度, 时长, 淡出)` | 引擎按强度乘速度（强度 0.5 = 速度 ×0.5，APEX 2.2 实测 0.498） |
| 转向减速 | 状态效果 `turn_slow`，强度 0.7 | 转身速度 ×(1−0.7) |
| 屏幕雪花 | 状态效果 `emp`，强度 0.15–0.4 | 客户端按强度画屏幕干扰 |
| 身上电弧特效 | `EMP_FX(FX_EMP_BODY_HUMAN, ent, "CHESTFOCUS", 时长)` | 所有人可见 |
| NPC 击晕 | `StunWhenInterruptable(ent, damageInfo)`（潜行者、幽灵、Prowler、蜘蛛、Grunt、Nessie） | 等 NPC 能被打断时播击晕动画 |
| 机械 NPC | `GiveEMPStunStatusEffects(ent, 2.5, 1.0)` + 伤害 ×2.05 | `_weapon_utility.nut` 约 3245–3258，**在 `#if DEVELOPER` 里**，正式服可能不跑 |
| 无人机 / 炮艇 | `NpcEmpRebootPrototype` | 重启原型，未读 |

## 2. 流程

1. 某个技能造成伤害时带 `damageType = DF_ELECTRICAL`、`scriptType = DF_STUN_AI`（例：电网 `mp_weapon_tesla_trap.nut:4269`）。
2. 技能的伤害回调（例 `TeslaTrap_DamagedTarget`，`mp_weapon_tesla_trap.nut:2067`）先问 `Electricity_ShouldStunNPCAndAddImmunity(npc)`：
   - NPC 在免疫表里 → 伤害 ×0，直接返回（这一下**连伤害都没有**）；
   - 不在 → 加进免疫表 3 s（`ELECTRICITY_NPC_STUN_IMMUNITY_DURATION`，`_weapon_utility.nut:372`），本次照常。
3. 再调 `Electricity_DamagedPlayerOrNPC(ent, damageInfo, empDurationOverride)`：
   - 按种类挂身体特效、起击晕线程；
   - 队友（攻击者同队且不是自己）→ 只有特效，没减速；
   - 玩家 → `EMPWeapon_EffectsPlayer`（3.2）；泰坦 / 机械 → `GiveEMPStunStatusEffects(2.5, 1.0)`。
4. 玩家在相位（`IsPhaseShifted`）里不吃；再次被电会先发 `OnEMPPilotHit` 打断上一个线程，新的覆盖旧的（`_weapon_utility.nut` `EMPWeapon_EffectsPlayer` 开头）。

## 3. 代码

### 3.1 `GiveEMPStunStatusEffects(target, duration, fade, slowTurn=0.7, slowMove=0.5)`

`weapons/_weapon_utility.nut:2866`。

```
先停掉上一次记下的 EMP 状态效果（相位时要清的那张表）
turn_slow 强度 slowTurn，持续 duration，最后 fade 秒淡出
move_slow 强度 slowMove，同上
```

注意：变量名写反了（`slowEffect` 存的是 turn_slow），不影响结果。

### 3.2 `EMPWeapon_EffectsPlayer(player, damageInfo, durationOverride)`

`weapons/_weapon_utility.nut` 约 3545–3590。

```
if durationOverride >= 0:          // 电网走这条
    strength = 0.4                 // EMP_GRENADE_PILOT_SCREEN_EFFECTS_MAX
    duration = durationOverride
    fade     = min(duration*0.5, 1.0)
else:                              // 电弧星走这条（APEX 2.2）
    frac = GraphCapped(dist, R/2, R, 1, 0)
    strength = 0.15 + 0.25*frac
    fade = 1.0*frac
    duration = 0.2 + 2.3*frac - fade
减速：GiveEMPStunStatusEffects(player, duration + fade, fade)
      （电弧星粘在身上那次 slowTurn 传 0）
屏幕：StatusEffect_AddTimed(player, emp, strength, duration, fade)
隐身的人：SetCloakFlicker(0.5, duration)
```

所以 **电网（override = 3.0）**：减速和转向持续 3 + 1 = 4 s（最后 1 s 淡出）；屏幕雪花 0.4 强度，持续 3 s（最后 1 s 淡出）。这是推断出的总时长，要实测（见 5）。

### 3.3 NPC 免疫窗

`Electricity_ShouldStunNPCAndAddImmunity`（`_weapon_utility.nut:3084`）+ `GiveNPCImmunityForDuration_Thread`（3101）：一张数组，NPC 进去 3 s 后出来。返回 true = 在免疫期。

`Electricity_ShouldDamageStunNPC`（约 3062）：要求带 `DF_STUN_AI`、活着、没在执行 ContextAction、没有父实体、不是 `NoTarget`。

### 3.4 依赖

- 常量：`sh_consts.gnut:611-615`（屏幕效果 0.2 / 2.5 / 1.0 / 0.15 / 0.4），`_weapon_utility.nut:372,378-379`。
- 状态效果是引擎内置的；HSD 的 `CombatUnit.slowScale / slowUntil` 就是 move_slow 的简化版。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| EMP_SEVERITY_SLOWMOVE | 0.50 | 速度倍率（强度） | `_weapon_utility.nut:379` | 移动减速 | 强度越大越慢 |
| EMP_SEVERITY_SLOWTURN | 0.70 | 强度 | `_weapon_utility.nut:378` | 转向减速（转身 ×0.3） | |
| SCREEN_EFFECTS_MAX / MIN | 0.4 / 0.15 | 强度 | `sh_consts.gnut:614-615` | 屏幕雪花 | |
| SCREEN_EFFECTS_DURATION_MAX / MIN | 2.5 / 0.2 | s | `sh_consts.gnut:611-612` | 距离型时长 | |
| SCREEN_EFFECTS_FADE | 1.0 | s | `sh_consts.gnut:613` | 淡出上限 | |
| ELECTRICITY_NPC_STUN_IMMUNITY_DURATION | 3.0 | s | `_weapon_utility.nut:372` | 同一 NPC 再次被电的间隔 | 改小 = 能连续电晕 |
| 机械 NPC 伤害倍率 | 2.05 | × | `_weapon_utility.nut` ~3250（DEVELOPER 块） | | |
| 机械 NPC 减速 | 2.5 + 淡出 1.0 | s | 同上 | | |

## 5. 未解决和要实测的

- 固定时长分支（电网 3.0 s）下减速是否真是 4 s：用 R5 runner 站在电网中间穿一次，记录 `move_slow` / `turn_slow` / `emp` 强度随时间（APEX 2.2 的 arcself 脚本可直接改）。
- 机械 NPC 分支在 `#if DEVELOPER` 里，S3 dedi 是否编译了 DEVELOPER 未知；在 dedi 上用电网打一个 spectre 看伤害倍率。
- `StunWhenInterruptable` 的动画时长没读。

## 6. HSD 实现

- 已有近似实现：`CombatSim.Emp(u, t, turnSlow)`（`HSD-Unity/.../Combat/CombatSim.Items.cs:354`）+ `ArcStar.MoveSlow / TurnSlow / FadeTime`（`Ordnance.cs:42-43`）。对单位只设 `slowScale = 0.5`，对玩家做转向和屏幕。
- 差别：HSD 对 NPC 没有"3 s 免疫窗"，也没有"在免疫期内整次伤害 ×0"；没有固定时长分支（只有电弧星的距离曲线）。
- 建议：把 `Emp` 改成 `Emp(u, duration, fade, turnSlow)`，电弧星和电网共用；新增 `CombatUnit.stunImmuneUntil`。开关：不需要（数值都是 R5 原值）。
