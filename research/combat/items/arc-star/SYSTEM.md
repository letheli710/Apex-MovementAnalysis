# 电弧星 系统记录

会话 `i1-records`，2026-11-01。静态记录，转写 APEX-REPORT 2.2 并补缺口；标 [实测] 的是 APEX 那次测的（`TF2-Research/expansion/apex/runs/20261029_202344_arcself.txt`）。

来源根目录：`research-src/s21-platform/scripts/`。`nut` = `vscripts/weapons/mp_weapon_grenade_emp.nut`，`txt` = `weapons/mp_weapon_grenade_emp.txt`，`wu` = `vscripts/weapons/_weapon_utility.nut`。

电击效果的完整写法见 [B-electric-emp](../../_shared/B-electric-emp.md)，这里只写电弧星走的分支。

## 0. 概要

- **道具**：军械 / 电弧星 / `mp_weapon_grenade_emp`（loot `survival_loot.csv:279`，tier 1）。
- **一句话**：2200 u/s 平飞，碰到任何东西就粘，2.8 s 后爆 75 伤害，范围内减速 + 转向减速 + 屏幕干扰，时长按距离 0.2–2.5 s；对 NPC 按种类击晕或加伤。
- **分类**：效果。
- **可拆出的部件**：
  - 碰撞即粘 + 点燃计时 → 3.1
  - 爆炸距离 → 时长 / 强度曲线 → 3.2
  - 按 NPC 种类分支的电击 → 3.3（在 [B-electric-emp](../../_shared/B-electric-emp.md)）
  - 粘到身上的人没有转向减速 → 3.2
  - 枪声诱饵（社区添加）→ 3.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 粘附 | 碰撞回调 `PlantStickyEntity` | `nut:29`（服务端）、`nut:70`（客户端） |
| 延迟引爆 | `GrenadeIgnite()` + `grenade_ignition_time 2.8` | `nut:34`、`txt:88`；0.3 s 粘住、3.1–3.2 s 爆 [实测] |
| 警告音 | 粘住 0.2 s 后 `sound_cook_warning` | `nut:146-157` |
| 爆炸 | `explosion_*`，标记含 `DF_ELECTRICAL`、`DF_STUN_AI` | `txt:73-77` |
| 电击 | 按伤害来源注册 `EMP_DamagedPlayerOrNPC` | `wu:599`、`wu:3057` |
| 减速 / 转向减速 | 状态效果 `move_slow` 0.5、`turn_slow` 0.7 | `wu:378-379`；0.498 / 0.698 [实测] |
| 屏幕干扰 | 状态效果 `emp` 0.15–0.4 | `wu:3595`、`sh_consts.gnut:611-615` |
| 身上电弧 | `EMP_FX` | `wu:3218` |
| 电弧光束（打 NPC 时） | `EMPGrenade_ArcBeam` | `wu:3266-3270` |
| 飞行外观 | 飞盘旋转 `grenade_disc_throw 1` | `txt:115` |

## 2. 流程

```
公共投掷流程（I-THROW-TOSS）→ 无飞行引信（fuse 0）
碰撞 → 碰到扔的人自己：忽略（nut:11）
     → 粘住 + GrenadeIgnite（只第一次）+ 0.2 s 后响警告音
2.8 s → 爆炸（75，内 72，外 350）
  伤害回调 EMP_DamagedPlayerOrNPC → Electricity_DamagedPlayerOrNPC
    ├ 玩家 → EMPWeapon_EffectsPlayer（3.2）
    └ NPC → 按种类（3.3）
```

## 3. 代码

### 3.1 碰撞：服务端和客户端**是两份**

`nut:7-39` 服务端（6 参数）、`nut:40-78` 客户端（7 参数，S21 签名）。

| 差别 | 服务端 | 客户端 |
|---|---|---|
| 队友 / 友方载具 | **不过滤** | 不粘（`nut:49-53`） |
| 死亡图腾召回中的玩家 | 照粘 | 掉落不粘（`nut:62-67`） |

混合构建的痕迹：`nut:3` 是 SDK 注释。本地 dedi 跑的是服务端这份。PvE 单人下差别无所谓。

### 3.2 对玩家：`EMPWeapon_EffectsPlayer`（`wu:3542-3597`）

```
相位中 → 不吃
dist = |爆点 − 玩家中心|；r = 350
frac = GraphCapped( dist, r/2, r, 1, 0 )
强度 = 0.15 + 0.25 × frac
fade = 1.0 × frac
总时长 = 0.2 + 2.3 × frac
被粘的（damageType != DMG_BLAST）：GiveEMPStunStatusEffects( 总时长, fade, slowTurn = 0 )
其他：GiveEMPStunStatusEffects( 总时长, fade )
emp 屏幕：强度, 总时长 − fade, fade
```

注意 `wu:3581` 的注释写"No move slow"，但传 0 的位置是 **`slowTurn`**（函数签名 `wu:3114`、[B-electric-emp](../../_shared/B-electric-emp.md) 3.1）。所以被粘的人**有移动减速，没有转向减速**，和 APEX 2.2 一致。

再次被电：`OnEMPPilotHit` 打断上一个线程（`wu:3544-3545`）。

### 3.3 对 NPC：`Electricity_DamagedPlayerOrNPC`（`wu:3114-3271`）

| 种类 | 表现 | 控制 | 伤害 |
|---|---|---|---|
| 潜行者、幽灵、Prowler、蜘蛛、超级幽灵（`wu:3135`） | 身上电弧 | `StunWhenInterruptable`（打断时播击晕） | 再看是否机械 |
| Nessie、Grunt（`wu:3147-3160`） | 同上 | 同上 | |
| 空中无人机、炮艇（`wu:3176-3193`） | 电弧 | `NpcEmpRebootPrototype`（掉下来重启） | |
| 训练假人（`wu:3161`、`wu:3261`） | 电弧 | `GiveEMPStunStatusEffects( 2.5, 1.0 )` | 不变 |
| `IsMechanical()`（`wu:3244`） | | `GiveEMPStunStatusEffects( 2.5, 1.0 )` | **× 2.05** |
| `IsHuman()`（`wu:3257`） | | | × 0.99 |
| 运输机（`wu:3240`） | | | × 0 |

三个要点：
- 电弧星不走 `Electricity_ShouldStunNPCAndAddImmunity`（那是电网调的），所以**电弧星没有 3 s 击晕免疫**（推断：`EMP_DamagedPlayerOrNPC` 只有一行，`wu:3057-3060`）。
- 机械 NPC 上 `move_slow` 0.5。W2 实测 NPC 速度 = 基础 × (1 − s)，所以是 ×0.5。
- **更正 B-electric-emp**：它写机械分支"在 `#if DEVELOPER` 里，正式服可能不跑"。本地 `wu:3120-3270` 没有任何 `#if`，这段正常跑。

身上电弧特效的时长（`wu:3216`）`GraphCapped( dist, r/2, r, MIN, MAX )`：近的 0.2 s，远的 2.5 s，和玩家效果相反（只影响特效，疑似原代码笔误）。

### 3.4 枪声诱饵（社区添加，不属于电弧星）

`nut:81-144`、`nut:161-334` 是 `OnProjectileCollision_weapon_grenade_decoy`：粘住后按主人武器的射速和弹匣循环播放枪声，打完可能再来一轮，然后销毁。风格和文件其他部分不同（`printt` 调试、拼写 `aditionaltime`），`AUDIO_DECOY_FIGHT` 全局开关（`nut:5`）；推断是社区加的。

PvE 价值：声音吸引 AI 的现成写法思路，但本身**只放声音，不通知 AI**。见 [creature-bait](../creature-bait/SYSTEM.md) 第 6 节。

### 3.5 依赖

[I-THROW-TOSS](../_shared/I-THROW-TOSS.md)、[B-electric-emp](../../_shared/B-electric-emp.md)、[E-STATUS-EFFECT](../../_shared/E-STATUS-EFFECT.md)、[B-move-slow](../../_shared/B-move-slow.md)。粘附 `PlantStickyEntity` 在 `wu:1703`，见 [B-placement](../../_shared/B-placement.md)。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| `projectile_launch_speed` | 2200 | u/s | `txt:111`；[实测] | | |
| `projectile_launch_pitch_offset` | 2 | ° | `txt:112` | | |
| `projectile_gravity_scale` | 1.6 | | `txt:114`；重力 1200 [实测] | 下坠更快 | |
| `projectile_inherit_owner_velocity_scale` | 1 | | `txt:118` | | |
| `grenade_fuse_time` | 0 | s | `txt:86` | 不会自己爆 | |
| `grenade_ignition_time` | 2.8 | s | `txt:88` | 粘住到爆 | 改小：躲不开 |
| `explosion_damage` / `_heavy_armor` | 75 / 75 | HP | `txt:74-75` | | |
| `explosion_inner_radius` | 72 | u | `txt:76` | | |
| `explosionradius` | 350 | u | `txt:77` | 也决定时长曲线 | |
| `damage_flags` | `DF_RAGDOLL \| DF_EXPLOSION \| DF_ELECTRICAL \| DF_STUN_AI` | | `txt:73` | | |
| `damage_shield_scale` | 1 | | `txt:79` | | |
| `impulse_force` | 3000 | | `txt:68` | | |
| `stick_pilot` / `titan` / `npc` / `drone` | 1 / 1 / 1 / 1 | | `txt:119-122` | | |
| 弹跳组 | 0.53 / 0.32 / 0.5 / 0.2 / 0.2 / 0.1 | | `txt:98-103` | 第一下就粘，用不上 | |
| `EMP_SEVERITY_SLOWMOVE` | 0.5 | | `wu:379` | 速度 ×(1−0.5) | |
| `EMP_SEVERITY_SLOWTURN` | 0.7 | | `wu:378` | 转身 ×0.3 | |
| 时长最小 / 最大 | 0.2 / 2.5 | s | `sh_consts.gnut:611-612` | | |
| 淡出 | 1.0 | s | `sh_consts.gnut:613` | | |
| 屏幕强度 | 0.15 – 0.4 | | `sh_consts.gnut:614-615` | | |
| NPC 机械加伤 | 2.05 | | `wu:3248` | | |
| NPC 定时控制 | 2.5 / 淡出 1.0 | s | `wu:3246` | | |
| `toss_pullout_time` / `toss_time` / `toss_overhead_time` | 0.2 / 0.4 / 0.7 | s | `txt:108-110` | | |
| `deploy_time` | 0.5 | s | `txt:90` | | |
| 粘住后警告音延迟 | 0.2 | s | `nut:153` | | |
| Fuse 被动 | 速度 × 1.7 | | `txt:283` | | |

## 5. 未解决和要实测的

- **对 NPC 实际效果**（APEX 2.2 未解项）：`npc_prowler`、`npc_dummie` 被电的速度、动画、时长，机械加伤有没有生效。`IsMechanical` 对 Prowler 的值决定走哪条。R5：脚本发射，读 `GetVelocity` 和伤害。
- 没有 3 s 免疫（推断）：连电两颗看第二颗有没有再击晕。
- `emp` 屏幕时长：`AddTimed` 的 `duration` 含不含淡出（E-STATUS-EFFECT 的语义）。
- 粘在玩家身上的分支没实测（要第二个玩家，PvE 下 NPC 粘玩家才需要）。

## 6. HSD 实现

**已实现**：`Ordnance.cs` `ArcStar`（`Ignition 2.8`、`Damage 75`、`Inner 72`、`Outer 350`、`MoveSlow 0.5`、`TurnSlow 0.7`、`MaxTime 2.5`、`MinTime 0.2`、`FadeTime 1.0`）。`EffectTime(dist)` 和 R5 的总时长曲线相同。

差别：NPC 分支（按种类击晕 / 机械 2.05）没做，要等 HSD 敌人分类；屏幕强度随距离变化按需求核对。

这份记录没改代码。
