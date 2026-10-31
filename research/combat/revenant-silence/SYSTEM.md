# Revenant 旧战术 Silence（沉默）· 系统记录（短版）

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`。脚本 `vscripts/weapons/mp_ability_silence.nut`（460 行）、共用 `vscripts/weapons/sh_silence.gnut`（609 行，Seer 战术的"打断"也用它）、武器 `weapons/mp_ability_silence.txt`、伤害定义 `damage/damagedefs.txt:415-426`。S21 里已经不是 Revenant 的技能。

## 0. 概要

- **技能**：Revenant（旧）/ 战术 / Silence / `mp_ability_silence`（`.txt` `printname #ABL_SILENCE`）。
- **一句话**：扔一个不弹跳的装置，碰到东西就展开成半径约 150 u 的沉默区，持续 10 s；进区的敌方玩家被沉默 15 s（不能用战术和大招），区域挡标点。
- **分类**：好技能（效果）✔：控制（禁技能）；可视化：一般（区域烟 + 屏幕调色随剩余时间淡出）；系统 ✔：通用"沉默 / 打断"状态（`SilenceThink`）、区域贴着移动物体走。
- **伤害**：`damagedef_ability_silence` 写 10 伤害（`damagedefs.txt:417`），但 `Hack_HandleSilenceDamage`（`.nut:401-414`）把**除 Flyer 和蜘蛛卵以外**所有目标的伤害设 0。按本地脚本，对玩家**没有伤害**（见第 5 节）。
- **对 NPC 无效**：`ApplySilence` 只处理玩家（`.nut:424-425`）。PvE 要用得改。
- **可拆出的部件**：
  - 区域 = 每帧在中心做一次小爆炸（damagedef）+ 受击回调施加效果 → 3.2.1 `CreateSilenceField` / `ApplySilence`
  - 区域外观：中心 + 8 个点的烟，按射线被墙挡的比例收缩 → 3.2.1
  - 通用沉默 / 打断状态 → 3.2.2 `SilenceThink`（`_shared/E-STATUS-EFFECT.md` 引用）
  - 区域挂在移动物体上 → 3.2.1

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 投掷 | 普通手雷框架 `Grenade_OnWeaponTossReleaseAnimEvent`，1500 u/s，抬 8°，不弹（`projectile_ricochet_max_count 0`） | `.nut:86-94`；`.txt` |
| 落点 | 碰撞时沿法线推出 41 u（蹲伏掩体高度），再向下 41 u 找地面、按比例回抬 | `.nut:110-153` |
| 贴着移动物体 | 碰到"有推动祖先"的非玩家实体 → 建 script mover 挂上去，区域中心每帧跟 mover | `.nut:138-148`、`.nut:246-247` |
| 区域判定 | 每帧 `Explosion_DamageDefSimple(damagedef_ability_silence, 中心)`：半径 150、伤害 10、`DF_NO_SELF_DAMAGE`；同一 inflictor 对同一实体只打一次（推断：`CreateDamageInflictorHelper` 设了只打一次） | `.nut:394-396`；`damagedefs.txt:415-426` |
| 施加沉默 | 伤害源回调 `AddDamageCallbackSourceID(damagedef_ability_silence, ApplySilence)` → 高度检查 → `SilenceThink` | `.nut:55`、`.nut:416-454` |
| 区域外观 | 9 个粒子（中心 `P_bSilent_orb`，外圈 8 个 `P_bSilent_fill`，外圈离中心 175 / 1.5 = 116.7 u）+ 每个点一个挡标点体积（半径 175×0.45 = 78.75 u，`CONTENTS_BLOCK_PING`） | `.nut:187-392` |
| 沉默 | 状态效果 `silenced` + `silenced_rev_visuals`（15 s，淡出 15 s）+ `DisableWeaponTypes(WPT_ULTIMATE \| WPT_TACTICAL)` | `sh_silence.gnut:177-186`、`:264` |
| 被沉默者画面 | 屏幕粒子 `P_bSilent_screen_CP`（CP1.x = 剩余 / 15）+ 调色 `ability_silence.raw_hdr`（权重 = 剩余 / 15） | `sh_silence.gnut:398-569` |
| 被沉默者身上 | 粒子 `P_bSilent_body`（相位中隐藏） | `sh_silence.gnut:110-130`、`:301-321` |
| HUD | 战术栏显示"被沉默"和来源（Revenant / Seer） | `sh_silence.gnut:349-396` |

## 2. 流程

```
按住（toss_pullout 0.3 s）→ 松开（toss 0.6 s）→ 扔出 1500 u/s
碰撞（不弹）→ 算落点（推出 41 u、找地面）→ [移动物体] 建 mover → 爆炸特效
0.25 s 后 CreateSilenceField（存在 10 s：inflictor helper 寿命）
   每帧：更新 9 个点的烟和挡标点体积；在中心做一次 damagedef 爆炸
   ApplySilence(玩家)：
       高度检查：爆炸点在玩家中心以上 → 爆炸点 − 脚底 < 100；以下 → 眼睛 − 爆炸点 < 100
       通过 → SilenceThink(玩家, 施放者, 10, 15)
       不通过 → 本次伤害 0，并从 inflictor 的"已伤害"表里移除（以后还能再判）
SilenceThink（sh_silence.gnut:97-322）：
   身上粒子；关伤害提示；[施放者是 Revenant] 队伍语音（10 s 防抖）
   Valk 在飞 → 关喷气、收起
   取消放置相位隧道
   加 silenced_rev_visuals + silenced（15 s）
   [applyInterrupt] interrupted 0.25 s：打断 Octane 兴奋剂、Newcastle 跳、（可选）禁药、打断处决
   手上是战术 / 大招 → 切回主武器；副手是列表里的技能（Bangalore 烟、沉默、枪盾、相位行走、相位隧道、滑索、心跳传感器）→ 清掉
   脱钩爪；禁战术和大招；Crypto 退出无人机视角
   直到 silenced 结束（倒地会提前结束 :342-345）→ 恢复
```

- **冷却**：弹夹 50、每次 25、回 1/s → 25 s 一次，最多存 2 次（`.txt` ammo_*）。

## 3. 代码

### 3.1 入口

`MpAbilitySilence_Init`（`.nut:41-57`）：playlist `revenant_silence_effect_duration`（默认 15）；注册伤害源回调。`MpAbilitySharedSilence_Init`（`sh_silence.gnut:43-94`）：两个调色（Revenant / Seer 用同一张 LUT）、状态效果回调、要清掉的副手列表、打断时长（playlist `silence_interrupt_duration` 默认 0.25）。

### 3.2 核心逻辑

#### 3.2.1 区域 `CreateSilenceField`（`.nut:156-398`）+ `ApplySilence`（`.nut:416-454`）

```
offset = 175 / 1.5                                   // 用的是脚本常量 175，不是 damagedef 的 150
点 = [中心] + 8 个方向（0°,45°…315°）× offset
每帧，对每个点：
   trace(中心 → 点)
   被挡：
       挡在一半以内 → 删这个点的烟和挡标点体积（中心点除外）
       否则 → 烟放到被挡位置
   没被挡 → 烟放在点上
   （有 mover 时烟跟 mover 走，不重新定位）
中心爆炸一次（damagedef 半径 150）
```

"每帧爆炸 + 只打一次 + 高度检查不过就允许再打"＝一个便宜的"进入区域"检测，不需要触发器。

`Hack_HandleSilenceDamage`（`.nut:401-414`，在公共受伤入口 `vscripts/_codecallbacks_common.gnut:193-194` 调用）：沉默伤害打到非 Flyer、非蜘蛛卵的目标 → 设 0。`.nut:407` 是一个被去掉的预处理行（空行），原来可能是某个模式的条件（推断）。

#### 3.2.2 通用沉默 `SilenceThink(ent, owner, areaDuration, effectDuration, applyInterrupt = false, isEndless = false)`（`sh_silence.gnut:97-322`）

参数化的"禁技能"状态：时长、是否附带 0.25 s 打断、是否无限期。外观按施放者被动选（`PAS_DEATHSTALKER` = Revenant、`PAS_PARIAH` = Seer）；两个都没有时粒子 id 未赋值（推断：S21 的 Revenant 被动若不是 `PAS_DEATHSTALKER`，外观会出问题）。Seer 战术用 `applyInterrupt`（见 `mp_ability_sonic_blast.nut`，C0 已列，不在本批）。

### 3.3 客户端表现

- 调色 `AbilitySilence_UpdatePlayerScreenColorCorrection`（`sh_silence.gnut:451-502`）：开始权重 1，之后每帧 = 剩余时间 / 15，线性淡到 0。和 Forged Shadows 用同一张 `ability_silence.raw_hdr`。
- 屏幕粒子（`:505-569`）：CP1 = (剩余 / 15, 255, 255)；剩 3 s 时停循环声。
- 结束提示音 `Survival_UI_Ability_Ready_SilenceEnded`（`:444`）。

### 3.4 依赖的公共代码

`Grenade_*`、`Explosion_DamageDefSimple`、`CreateDamageInflictorHelper`、`CreateTraceBlockerVolume`、`MapAngleToRadius`、状态效果 `silenced` / `silenced_rev_visuals` / `interrupted`、`DisableWeaponTypes`。调色 → `_shared/E-SCREEN-COLOR-CORRECTION.md`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 |
|---|---|---|---|---|
| 区域时长 | 10 | s | `.nut:14` | inflictor 寿命 |
| 区域半径（判定） | 150 | u | `damagedefs.txt:419-420` | |
| 区域半径（脚本常量，外观） | 175 | u | `.nut:15`（注释"应和 damageDef 一致"，实际不一致） | 烟点偏移 116.7、挡标点体积 78.75 |
| 高度检查 | 100 | u | `.nut:431`、`:436` | |
| 沉默时长 | 15 | s | playlist `revenant_silence_effect_duration`（`.nut:50`） | |
| 打断时长 | 0.25 | s | playlist `silence_interrupt_duration`（`sh_silence.gnut:51`） | 只有 applyInterrupt 时 |
| 展开延迟 | 0.25 | s | `.nut:159` | |
| 落点推出 | 41 | u | `.nut:127` | 蹲伏掩体高度 |
| 伤害（damagedef） | 10 | HP | `damagedefs.txt:417` | 被 Hack 设 0（Flyer / 蜘蛛卵除外） |
| 投掷速度 / 抬角 | 1500 / 8 | u/s / ° | `.txt` | |
| 弹跳 | 0 次（法线朝上 dot < 0.5 才算弹，次数上限 0） | — | `.txt`、`.nut:30`、`:116-117` | |
| toss_pullout / toss_time | 0.3 / 0.6 | s | `.txt` | |
| 冷却 | 25 s 一次，存 2 次 | s | `.txt` ammo 50 / 25 / 回 1 | |
| 语音防抖 | 10 | s | `sh_silence.gnut:144` | |
| 爆炸震屏 | 半径 500、幅度 5、频率 45、0.1 s | — | `.txt` explosion_shake_* | |

## 5. 未解决和要实测的

1. **对玩家到底有没有 10 点伤害**：本地脚本是 0（`Hack_HandleSilenceDamage`）。测法：对假人 / bot 扔沉默，读血量。
2. **沉默对 NPC 无效**：`ApplySilence` 只认玩家。HSD 若要拿来压制 AI，得自己定义"AI 被沉默 = 不能放技能"。
3. **S21 Revenant 的被动是不是 `PAS_DEATHSTALKER`**：不是的话 `SilenceThink` 外观 id 未赋值。测法：Revenant 扔沉默，看被沉默者身上有没有粒子、日志有没有报错。

## 6. HSD 实现

**未实现。** HSD 敌人目前没有"技能"，"沉默"对它们没有意义；对玩家则是禁战术 / 大招。建议做成通用状态效果 `silenced(时长)`（见 `_shared/E-STATUS-EFFECT.md`），由敌人的攻击施加给玩家，或者给 HSD 的 AI 加"技能锁"。区域判定直接每 0.1 s 查距离 + 高度差 < 100 即可。
