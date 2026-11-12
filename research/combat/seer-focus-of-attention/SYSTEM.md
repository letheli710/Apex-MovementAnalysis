# Seer 战术 Focus of Attention 注视焦点：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_sonic_blast.nut`，`txt` = `weapons/mp_ability_sonic_blast.txt`，`sil` = `vscripts/weapons/sh_silence.gnut`，`hb` = `vscripts/weapons/mp_ability_heartbeat_sensor.nut`。

## 0. 概要

- **技能**：Seer / 战术 / Focus of Attention / `mp_ability_sonic_blast`。
- **一句话**：按住战术（0.4 s 后自己减速、打开心跳雷达 UI），松开后从胸前沿准星方向放出一根**管子**（半径 200 u、长约 2362 u）。管子先显示 **1 s** 预警（敌人看到红色管子和威胁箭头），1 s 后"引爆"：管里的敌方玩家被**沉默 8 s**（不能用技能）+ **打断**（0.25 s：停治疗、停 Octane 兴奋剂、取消滑索 / 钩爪等）+ 0.5 s 轻微减速和闪屏 + 被**扫描** 2.5 s（全队看到位置、血量）。伤害默认**关**（playlist 开时 5 伤害）。
- **分类**：**好技能**（区域控制：延迟、可躲的长条打击）＋ **可视化**（管状冲击波：预警管、沿管飞行的螺旋粒子、引爆的扬尘和扭曲）＋ **系统**（"线段 + 半径"的胶囊命中判定；沉默 / 打断状态；预警时间可躲）。
- **可拆出的部件**：
  - 胶囊命中判定（点到线段距离 ≤ 半径，且在发射方向前方）→ 3.2.2 `ShouldBlastHitVictim`
  - 延迟引爆的长条攻击（预警 → 引爆）→ 3.2.1 `SonicBlastAttack_Thread`
  - 沉默 + 打断（禁用技能类武器、打断一串动作）→ 3.2.4，已有记录 `../revenant-silence/SYSTEM.md` 3.2.2（批次 E，`SilenceThink` 全文），本文只记 Seer 的参数
  - 跟随敌人的扫描（相位时关、出来再开）→ 3.2.5 `SonarTrackTarget_Thread`
  - 管状冲击波表现 → 3.3
  - 威胁箭头指向"管子离我最近的点" → 3.3 `DoSonicBlastThreatIndicator_Thread`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 按住准备 | 投掷类副手（`toss_pullout_time 0.1`、`toss_time 0.9`），手上 `P_wpn_foa_blast_hold`（1P 两手 + 3P 两手） | `txt:55-56`、`nut:213-239` |
| 自己减速 | 按住 0.4 s 后加 mod `seer_tac_movespeed_modifier`（`move_speed_modifier 0.816889`） | `nut:258-289`、`txt:92-94`、`hb:31` |
| 心跳雷达 UI | 按住 0.4 s 后客户端打开被动的心跳传感器 UI | `nut:293-331` |
| 命中区域 | 服务端 `CreateTriggerCylinderNoCylinderRadius`（半径 200、长 = 射程），转到视线方向（`EyeAngles ∘ <90,0,0>`），只收敌方 | `nut:401-416`、`nut:494-520` |
| 精确判定 | 引爆时对触发器里的实体：在发射方向前方（dot > 0）、敌方、**眼睛**到线段距离 ≤ 200 | `nut:466-483`、`nut:827-858` |
| 延迟 | `.txt` 自定义字段 `sonic_blast_delay 1.0` | `txt:69`、`nut:385` |
| 预警 | 光束 `P_wpn_foa_beam_warning`（终点控制点 1）+ 管子半径特效三份（中性 / 友 / 敌，控制点 5 = 半径，随机旋转），1 s 后删 | `nut:393-397`、`nut:522-546` |
| 飞行螺旋 | `script_mover` 0.1 s 后 0.5 s 移到终点，挂 `P_foa_warning_mover_spiral` 和飞行音 | `nut:426-460` |
| 引爆特效 | `P_wpn_foa_cast_FP`（存在 = 沉默时长）、`P_wpn_foa_kickup_dust`、`P_wpn_foa_radius_MDL`（3 s） | `nut:772-790` |
| 伤害（可选） | playlist `seer_tac_does_damage`（默认 **false**）→ `TakeDamage(5, DF_EXPLOSION, mp_ability_sonic_blast)`；关时只给受击方向指示 | `nut:566-588`、`nut:1035-1043` |
| 沉默 | `SilenceThink`：状态效果 `silenced` + `silenced_seer_visuals`，`DisableWeaponTypes(ULTIMATE | TACTICAL)`，脱钩爪，切回主武器 | `nut:593-596`、`sil:97-290` |
| 打断 | `seer_tac_interrupts`（默认 true）→ 状态效果 `interrupted` 0.25 s + 信号 `Interrupted`；停 Octane 兴奋剂；Newcastle 跳中断；停治疗；打断处决 | `nut:595`、`sil:180-213` |
| 硬直 | 玩家：`emp` 0.2 / `move_slow` 0.25，0.5 s（淡出 0.25 / 0.5）；震屏 2.75 / 5 / 0.75 s | `nut:610-623`、`nut:861-867` |
| 扫描 | 默认 `SonarStart`（全队可见的声呐）；关时用菱形 `P_ar_foa_lockon`；玩家加 `seer_detected` | `nut:650-753` |
| 高亮 | `seer_highlight_target` + `HIGHLIGHT_NOVA_BLACKHOLE_THREAT`（借了黑洞威胁高亮），时长 = 沉默时长 | `nut:626-648` |
| 血条 | 给 Seer 队伍发 `ServerToClient_ShowHealthRUI`（显示代码被注释掉了） | `nut:601-608`、`nut:881-943` |
| 声音 | 蓄力、发射、成管、引爆（客户端按时间自己播）、耳鸣 1.25 s、命中提示 | `nut:57-66`、`nut:945-988` |

**客户端 / 服务端**：判定和效果在服务端；管子预警声、引爆声、威胁箭头由服务端通知每个客户端后在客户端按引爆时间播（`nut:447-454`、`nut:945-1017`）。

**怀疑点**：
- `nut` 里注释是 Respawn 原注释（`- AK`、`Tnordin`、R5DEV 单号），像官方原码。
- `sil:201`"// blocked native; helper is the safe path"——**SDK 补丁**（Newcastle 跳的判断被改成调用辅助函数）。
- 血条 RUI 的显示被整段注释（`nut:913-939`），推断是官方关掉的或 SDK 关掉的。

## 2. 流程

```
按住战术（toss prep，pullout 0.1 s）：手上特效、蓄力音
  0.4 s：自己移动 ×0.817，心跳雷达 UI 打开
松开（toss release，toss_time 0.9 s 动画）：
  start = 胸口 + 视线 × 20；end = start + 视线 × 射程
  光束预警 + 管子预警（友 / 敌 / 中性）1 s
  圆柱触发器（只收敌方、非相位）
  每个同 realm 玩家：客户端成管音 + 敌人看到指向管子最近点的威胁箭头 + 按时播引爆音
  0.1 s：螺旋 mover 0.5 s 飞到终点
  1.0 s：引爆特效；对触发器里每个实体：
           非相位、非自己、在前方、敌方、眼睛到线段 ≤ 200 → SonicBlastHitPlayer
  有命中 → Seer 听到"锁定"音
取消（OnWeaponTossCancel）：结束 UI、去掉手上特效和减速 mod
冷却：弹匣 20、每次 20、回充 1/s → 20 s
```

**SonicBlastHitPlayer**（`nut:554-624`）：

```
黑幕挡住（FerroWall_BlockScan）→ 什么都不发生
如果是玩家或训练假人、且不免疫技能:
   伤害（开关）或只给受击方向指示
   高亮 8 s
   不是假人 → 沉默 8 s + 打断 0.25 s
所有命中的（含 NPC）：扫描 2.5 s
玩家 / 分身 → 给 Seer 队伍发血条
玩家：震屏；emp 0.2 + move_slow 0.25 共 0.5 s；耳鸣 1.25 s；Signal("HitBySeerTact")（打断 Ballistic 锁定等）
```

- **普通 NPC 只被扫描**：`ShouldBlastHitVictim` 接受 `IsCombatNPC`（`nut:829`），但伤害、沉默、硬直都要求玩家 / 假人（`nut:564`、`nut:610`）。PvE 必须改。
- **升级**：扫描 +1.5 s（`PAS_TAC_UPGRADE_ONE`）、沉默 +2 s（`PAS_TAC_UPGRADE_TWO`）、被动射程升级时去掉 +10 m 余量、改用 75 m（`PAS_PAS_UPGRADE_ONE`）（`nut:1045-1107`）。
- **"延迟减速"**：任务书说的延迟减速对应两处——施法者按住 0.4 s 后自己减速；被打者在 1 s 延迟引爆后才吃 0.5 s 减速。

## 3. 代码

### 3.1 入口

- `MpAbilitySonicBlast_Init`（`nut:90-127`）：读 playlist（射程、半径、沉默、扫描、伤害、打断、全扫描），算管长 = 半径 × 4.175（注释：原版 835 对应半径 200，`nut:112`，只用于特效）；注册信号 `HitBySeerTact` 等。
- 武器回调：Activate / Deactivate / TossPrep / TossReleaseAnimEvent / TossCancel / AttemptOffhandSwitch。

### 3.2 核心逻辑

#### 3.2.1 延迟长条攻击 `SonicBlastAttack_Thread`（`nut:369-492`）

见第 2 节流程。关键：**判定发生在引爆那一刻**（`trigger.GetTouchingEntities()` 在 `wait blastDelay − 0.1` 之后），所以 1 s 内走出管子就能躲开。触发器的进入回调只做过滤（`nut:494-520`，Bangalore 被动那段被注释掉）。

#### 3.2.2 胶囊判定 `ShouldBlastHitVictim`（`nut:827-858`）

```
对象：玩家 / 分身 / 训练假人（活的）/ 战斗 NPC
dir = normalize(end - start)；to = normalize(victim.center - start)
dot(dir, to) > 0                    // 在前方半空间
敌方
eye = victim 眼睛（Crypto 在无人机视角时用 HEADFOCUS）
d = |ClosestPointOnSegment(start, end, eye) - eye|
d ≤ 200
```

#### 3.2.3 射程

```
range = seer_passive_range(50 m) / 0.0254 + 10 m / 0.0254 = 1968.5 + 393.7 ≈ 2362 u
升级：seer_passive_extended_range_upgraded(75 m) / 0.0254 ≈ 2953 u（不再加 10 m）
```

（`nut:38`、`nut:104`、`nut:1101-1107`、`hb:27-29`、`hb:1641` 起）

#### 3.2.4 沉默和打断 `SilenceThink`（`sil:97-290`）

```
身上特效（Seer 版 P_foa_victim_disrupt）；Seer 的沉默不播"技能被封"语音
Valk 在飞 → 关喷气、收起喷气副手
信号 PhaseTunnel_CancelPlacement
silenced + silenced_seer_visuals（8 s，淡出 8 s）
打断：interrupted（silence_interrupt_duration 0.25 s）+ Signal("Interrupted")
      Octane → EndStim；Newcastle 跳中 → 中断；InterruptedStopsHeals → 0.25 s 不能治疗；InterruptedStopsFinishers → 打断处决
手里是战术 / 大招 → 切回主武器；副手在取消列表里（Bangalore 烟、Revenant 沉默、Gibraltar 枪盾、Wraith 相位、传送门、滑索、心跳传感器）→ 清掉
脱钩爪；DisableWeaponTypes(ULTIMATE | TACTICAL)；Crypto 退出无人机视角
结束：EnableWeaponTypes
```

`Signal("Interrupted")` 被很多系统监听（如 `mp/sh_crafting.nut:3881`、`mp_ability_armored_leap.nut` 多处），这是 R5 的通用"打断"信号。

#### 3.2.5 扫描 `SonarTrackTarget_Thread`（`nut:650-753`）

默认 `seer_tac_does_sonar_scan = true` → `SonarStart(victim, …, Seer 队伍)`（全队可见声呐轮廓）；否则在胸口挂只给 Seer 队伍看的菱形。玩家加 `seer_detected`（多 0.1 s 淡出，修智能弹药 UI 闪，`nut:685-687`）。每帧：目标相位就关、出相位再开。

### 3.3 客户端表现（管状冲击波）

- **预警**：一根从胸前到终点的光束 + 一根半径 200 的管子（三份颜色，随机绕轴旋转让每次看起来不同，`nut:524-525`），1 s 后消失。敌人另外看到威胁箭头，箭头目标每帧移到"管子上离我眼睛最近的点"（`nut:990-1017`）。
- **飞行**：一个螺旋粒子 0.5 s 从起点飞到终点（`nut:426-460`），声音跟着走（注释说先等 0.1 s 让声音像是从 Seer 身上发出的，`nut:458-459`）。
- **引爆**：Seer 1P 施法特效（持续沉默时长）、起点扬尘、管子扭曲（3 s）。
- **被打中**：震屏 2.75 / 5 / 0.75 s、耳鸣、屏幕沉默特效 `P_foa_disrupt_screen_CP` + 调色 `ability_silence.raw_hdr`（`sil:6-9`、`sil:57-64`）。

### 3.4 依赖的公共代码

- `sh_silence.gnut`（Revenant 沉默和 Seer 共用：`eSilenceOwner` 区分特效）。
- `mp_ability_heartbeat_sensor.nut`（射程常量、按住延迟 0.4 s、心跳 UI）。
- `SonarStart / SonarEnd`、`FerroWall_BlockScan`、`CreateTriggerCylinderNoCylinderRadius`、`GetClosestPointOnLineSegment`、`ShowGrenadeArrow`。
- 其他系统听 `HitBySeerTact`：Ballistic 锁定结束（`mp_ability_debuff_zone.nut:763`、`:794`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| SONIC_BLAST_RADIUS（`seer_tac_radius`） | 200 | u | `nut:36`、`nut:1030-1033` | 管子半径 | — |
| 起点前移 | 20 | u | `nut:37` | 胸口前 | — |
| 射程 | 50 m + 10 m ≈ 2362（升级 75 m ≈ 2953） | u | `nut:38`、`nut:1101-1107`、`hb:27-29` | 管长 | — |
| 特效管长 | 半径 × 4.175（= 835） | u | `nut:112` | 只用于特效 | — |
| sonic_blast_delay | 1.0 | s | `txt:69` | 预警到引爆 | 长了更好躲 |
| SONIC_BLAST_PROJECTILE_TRAVEL_TIME | 0.5 | s | `nut:43` | 螺旋飞行 | — |
| SONAR_DURATION（`seer_tac_sonar_duration`） | 2.5（升级 +1.5） | s | `nut:39`、`nut:1020-1023`、`nut:1047` | 扫描 | — |
| SILENCE_DURATION（`seer_tac_silence_duration`） | 8.0（升级 +2） | s | `nut:40`、`nut:1025-1028`、`nut:1052` | 沉默 | 第 5 节 |
| silence_interrupt_duration | 0.25 | s | `sil:44` | 打断 | — |
| SLOW_DURATION | 0.5 | s | `nut:41` | 硬直 | — |
| 硬直 move_slow / emp | 0.25 / 0.2（emp 淡出 0.25） | 严重度 | `nut:615-617` | — | — |
| seer_tac_does_damage | **false** | — | `nut:1035-1038` | 伤害开关 | — |
| SONIC_BLAST_DAMAGE_AMOUNT（`seer_tac_damage`） | 5 | HP | `nut:46`、`nut:1040-1043` | 开时伤害 | — |
| seer_tac_interrupts | true | — | `nut:1096-1099` | 打断开关 | — |
| seer_tac_does_sonar_scan | true | — | `nut:1091-1094` | 全队声呐 vs 菱形 | — |
| 自己减速 | ×0.816889（按住 0.4 s 后） | × | `txt:92-94`、`hb:31` | — | — |
| 震屏 | 2.75 / 5 / 0.75 | 幅度 / 频率 / s | `nut:865` | — | — |
| 耳鸣 | 扫描时长 × 0.5 | s | `nut:620` | — | — |
| 引爆特效时长 | 3 | s | `nut:788-789` | — | — |
| 冷却 | 弹匣 20、每次 20、回充 1/s → 20 s | — | `txt:41-46` | — | — |
| toss_pullout / toss_time | 0.1 / 0.9 | s | `txt:55-56` | — | — |
| SONIC_BLAST_RADIUS_FX_SPACING | 200 | u | `nut:47` | 传进特效函数但没用（推断） | — |

## 5. 未解决和要实测的

1. **沉默 8 s**：注释说"Seer's silence is short enough"（`sil:120`），但默认 8 s 不短。**测**：打中训练场 bot / 两人局，计时到能再用技能。也查 `playlists_r5_patch.txt` 是否覆盖 `seer_tac_silence_duration`。
2. **对 NPC 的效果**：静态结论是只有扫描。**测**：对 Prowler 放一次，看是否减速 / 受伤。
3. **管子是"胶囊"还是"圆柱"**：判定用眼睛到线段距离（端点处是半球），触发器是圆柱，两者交集。**测**：在管子末端外 100 u 斜放假人。
4. **dot > 0 用的是中心，距离用的是眼睛**：贴脸在 Seer 侧后方时不命中。PvE 小问题。
5. 服务端代码看起来是官方原样，`sh_silence.gnut` 有一处 SDK 补丁（`sil:201`）。

## 6. HSD 实现

**未实现**。现有零件：`Tacticals.cs` 的 `Scan`（Bloodhound 锥形扫描，有轮廓 / 胸口标记时间），`CombatUnit.outlinedUntil / markedUntil`（`CombatCore.cs:78`）可以直接复用为"被扫描"；`CombatUnit.slowScale / slowUntil` 用于硬直。

建议做法（`Tacticals.cs` 加 `FocusOfAttention`）：

1. **判定**：胶囊（起点胸前 20 u、长 2362、半径 200），引爆时刻判定（1 s 后），只算前方。照搬 3.2.2。
2. **对 AI 的效果**（R5 对 NPC 只扫描，PvE 必须改，开关 `foa.aiEffect`）：
   - 扫描 2.5 s（复用 `outlinedUntil / markedUntil`）；
   - **打断**：AI 正在攻击前摇 / 读条时取消，进入 0.25 s 硬直（R5 打断时长）；
   - **沉默**（AI 版）：8 s 内不能用特殊技能（AI 有技能时），普通攻击照常——对应 R5"只封技能不封枪"；
   - 0.5 s 移动 ×0.75（R5 `move_slow 0.25`，严重度 s → 速度 ×(1−s)，APEX 2.2 实测，见 `_shared/B-electric-emp.md`、`_shared/E-STATUS-EFFECT.md`）；
   - 伤害：开关 `foa.damage`，默认 0（R5 默认关），开时 5。
   差别写进 `R5-DIFF-ARCHIVE.md`："R5 对 NPC 只扫描；HSD 对 AI 加打断 / 沉默 / 硬直"。
3. **可视化**（这个技能最值得借的部分）：预警管（半透明圆柱，敌方色）1 s → 螺旋粒子 0.5 s 飞到底 → 引爆时管子扭曲 + 起点扬尘。HSD 占位：一根半透明圆柱 + 一个沿轴移动的小球。
4. 施法：按住时自己 ×0.82 移速，按住 0.4 s 后才能放（R5 的 HEARTBEAT 延迟）。
5. 冷却 20 s，1 格。

开关建议：PlayerPrefs `hsd.combat.seer.foa.*`（`delay`、`radius`、`range`、`aiEffect`、`damage`、`silenceTime`）。
