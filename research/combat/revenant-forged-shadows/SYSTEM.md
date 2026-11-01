# Revenant 大招 Forged Shadows（暗影护甲）· 系统记录

批次 E（combat-e），2026-10-31，第一波静态研究：只读脚本，没进游戏。
源码根：`research-src/s21-platform/scripts/`，下文路径从这里开始。主脚本 `vscripts/weapons/mp_ability_shadow_form.nut`（1440 行），武器设置 `weapons/mp_ability_shadow_form.txt`。

## 0. 概要

- **技能**：Revenant / 大招 / Forged Shadows / `mp_ability_shadow_form`（`.txt:3` `#ABL_FORGED_SHADOWS`，图标 `ultimate_revenant_rework`）。
- **一句话**：放出后 25 s 内全身变成暗影：一个 75 血、会自己回满的"护盾壳"包住玩家，挡掉子弹 / 近战 / 爆炸；期间击倒或击杀敌人，时间 +5 s、护盾壳立刻重置。
- **分类**：可视化 ✔、系统 ✔；好技能（效果）待定——效果就是"临时第二条血 + 免硬直"，PvE 里有用但简单。
- **可拆出的部件**：
  - 跟随玩家的可受击护盾实体 → 3.2.1 `ShadowForm_CreateShieldAroundPlayer`
  - 伤害重定向（玩家伤害按类型转给护盾）+ 溢出伤害 + 同一伤害源免一次 → 3.2.2 `OnPlayerTookDamage` / `Shield_OnPostDamaged`
  - 断伤后延迟回复、回满后重建 → 3.2.3 `ShadowForm_ShieldRegenDelay`
  - 黏附物：允许哪些黏上、穿墙时剥落 → 3.2.4 `ShadowShield_IsAllowedStickyEnt` / `ShadowShield_TrackStickyEnt_Thread` / `Shield_CleanUp`
  - 击杀延长计时（有上限）→ 3.2.5 `ShadowForm_ExtendTimer`
  - 状态效果当计时器 + 客户端回调开关画面 → 3.3 / `_shared/E-STATUS-EFFECT.md`
  - 屏幕调色淡入淡出 → 3.3 `ColorCorrection_LerpWeight` / `_shared/E-SCREEN-COLOR-CORRECTION.md`
  - 换皮 / 全黑染色 → 3.2.6 `ShadowForm_ApplyShadowSkin`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 计时 25 s | 状态效果 `eStatusEffect.shadow_form`，`StatusEffect_AddTimed(player, shadow_form, 1.0, duration, 0.0)` | `.nut:516`。整个技能是否在生效 = 这个状态效果有没有严重度（`IsInForgedShadows` `.nut:288-297`）。客户端靠它的开 / 关回调开关画面 |
| 护盾壳 | 脚本道具 `CreatePropScript(forged_shadows_shield_physX.rmdl, SOLID_VPHYSICS)`，挂在 `CHESTFOCUS` 上 | `.nut:762-795`。有血量（75）、能被打、能被 AI 当目标、能被近战 |
| 护盾吸收伤害 | 玩家伤害回调 `AddDamageCallback("player", OnPlayerTookDamage)` 把伤害缩成 0，再让护盾 `TakeDamage` | `.nut:171`、`.nut:638-697` |
| 溢出伤害 | 护盾受伤回调里算 `damage - shield.GetHealth()`，用 `owner.TakeDamage(..., DF_OVERFLOW)` 打给玩家 | `.nut:932-947` |
| 护盾回复 | 网络变量 `revenant_shadow_health`（float 0–75）+ 服务端脚本线程每帧 +1 | `.nut:163`、`.nut:704-742` |
| 免受击减速 | 循环里每帧确保有 `PAS_FORTIFIED` 被动；有它时 `Survival_DamageShouldSlowDownPlayer` 返回 false | `.nut:596-605`；`vscripts/gamemodes/_gamemode_survival.nut:7769` |
| 引擎侧暗影状态 | `player.EnterShadowFormFortified()` / `LeaveShadowForm()` | `.nut:517`、`.nut:539`。原生函数，脚本看不到里面做了什么（推断：和暗影突袭 / 暗影小队共用的引擎标志） |
| 暗影皮肤 | 模型皮肤 `ShadowSquad_reborn_3p`；没有就 `rendercolor = 0,0,0` 全黑 | `.nut:1169-1185` |
| 3P 身体特效 | 粒子挂骨骼点：胸口拖尾 + 身体、两眼、两手 | `.nut:458-511` |
| 护盾外观 | 粒子 `P_rev_reborn_shield` 挂在护盾上，控制点 5 = 血量比例 | `.nut:798-805`、`.nut:1017-1024` |
| 受击 / 破碎特效 | 粒子 + 声音，受击 0.2 s、破碎 1.0 s | `.nut:979-1065` |
| 1P 屏幕 | 驾驶舱粒子 `p_rev_reborn_FP_ult_screen_base` + `p_rev_reborn_FP_ult_screen_shield`（护盾在时）+ 屏幕调色 `ability_silence.raw_hdr` | `.nut:1213-1301` |
| HUD | RUI 跟踪状态效果剩余时间，另传护盾剩余、受击 / 回复闪烁 | `.nut:1304-1316`、`.nut:1345-1423` |
| 受击方向指示 | 服务端 `Remote_CallFunction_Replay` → 客户端 `DamageIndicators` | `.nut:699-702`、`.nut:1333-1343` |
| 击杀延长 | 击杀 / 击倒 / 助攻回调 → `StatusEffect_SetDuration` | `.nut:168-170`、`.nut:1132-1167` |
| 让 Bloodhound 能追踪 | `TrackingVision_CreatePOI(...REVENANT_FORGED_SHADOWS...)` | `.nut:520` |

**服务端 / 客户端：** 护盾实体、伤害、回复、计时都在服务端（`#if SERVER`）；屏幕粒子、调色、HUD 闪烁在客户端（`#if CLIENT`）。服务端代码有可能被 SDK 社区改过（本地是 S21 客户端 + S3 dedi + SDK 混合构建），尤其是 `OnPlayerTookDamage` 里的类型分支和 `lastDamageInflictor` 逻辑，第 5 节列为要实测。

## 2. 流程

```
按键（大招充满 180/180）
 └─ OnWeaponActivate：播放蓄力声 + 语音                         (.nut:252-267)
 └─ toss 动画 2.2 s 后 → OnWeaponTossReleaseAnimEvent          (.txt:27 toss_time 2.2；.nut:269)
     └─ thread ShadowForm_Start
         ├─ 写护盾网络变量 = 75；武器加 mod 暂停大招回充        (.nut:440-442)
         ├─ 挂 3P 特效（拖尾、身体、眼、手）                    (.nut:458-511)
         ├─ thread 建护盾壳                                     (.nut:513)
         ├─ 换暗影皮肤；加状态效果 25 s；引擎进暗影             (.nut:515-517)
         ├─ thread 到期警告（剩 3 s 时响）                      (.nut:526、609-636)
         └─ 循环：状态效果在 → 每帧确保 PAS_FORTIFIED           (.nut:596-605)

状态：护盾在 ──被打掉──▶ 护盾破（网络变量 0）──1 s 不再挨打──▶ 回复中（每帧 +1）──回满──▶ 重建护盾
         ▲                    │ 期间又挨打：重置 1 s 延迟                         │
         └──── 击杀/击倒：立即重建满血护盾 ◀───────────────────────────────────────┘
```

- **不能用：** 已在暗影中时不能再切到这个技能（`OnWeaponAttemptOffhandSwitch` `.nut:239-250`）。不能在滑索上用（`.txt:23`）。
- **打断 / 结束**（`ShadowForm_Start` 的 EndSignal，`.nut:437`）：死亡、实体销毁、开始倒地（`BleedOut_OnStartDying`）、`ExitShadowForm` 信号（倒地回调 `.nut:221-224`、武器换主人 `.nut:281-286`）、状态效果到期（循环退出）。
- **结束时清理**（`.nut:528-593`）：取消皮肤、`LeaveShadowForm`、拿走 `PAS_FORTIFIED`、停声音、停状态效果、去掉暂停回充的 mod、删全部 3P 特效。护盾线程也监听同样信号，自己清理（`.nut:816-847`）。
- **冷却：** 弹夹 180，每秒回 1 → 180 s（`.txt:40-46`）。生效期间回充暂停（mod `ability_in_effect_regen_paused` `.txt:120-124`，`.nut:442`）。
- **升级分支：** `upgrade_ult_one` 弹夹 ×0.8 → 144 s（`.txt:87-94`）。护甲类 mod 回充 ×1.25 / ×1.5（`.txt:81-112`）。
- **击杀延长：** 必须有被动 `PAS_REVENANT_REWORK` 且在暗影中、目标是敌方玩家（`.nut:1115-1130`）。触发点：击倒（`.nut:192-199`）、直接击杀（对方没在倒地中，`.nut:1088-1092`）、助攻（3 s 窗口，`.nut:1094-1113`、`.nut:202-216`）。

## 3. 代码

### 3.1 入口

- `MpAbilityShadowForm_Init`（`.nut:129-189`）：读 playlist 覆盖（见第 4 节）；注册网络变量 `revenant_shadow_health`（`SNVT_FLOAT_RANGE 0..shieldHealth`）和两个服务端→客户端函数；服务端挂倒地 / 击杀 / 助攻 / 玩家受伤回调；客户端注册调色 `materials/correction/ability_silence.raw_hdr`，挂 `shadow_form` 状态效果的开 / 关回调。
- `OnWeaponTossReleaseAnimEvent_ability_shadow_form`（`.nut:269-279`）：`thread ShadowForm_Start`，返回 `GetAmmoPerShot()`（扣满 180）。
- `ShadowForm_Start`（`.nut:431-606`）：见第 2 节。注意状态效果是"线程结束的条件"，延长时间只要改状态效果时长，这个循环自然多跑。

### 3.2 核心逻辑

#### 3.2.1 跟随玩家的护盾壳 `ShadowForm_CreateShieldAroundPlayer`（`.nut:744-885`）

```
先删旧护盾和旧护盾特效（同一玩家只有一个）
shield = CreatePropScript(碰撞模型, 胸口位置, 玩家角度, SOLID_VPHYSICS)
shield: 同队；SetParent(player, "CHESTFOCUS")；Owner = player
        可受伤、发受伤通知；不挡范围伤害（SetBlocksRadiusDamage false）
        血量 = 最大 = 75；对所有人可见；碰撞组 BLOCK_WEAPONS（只挡武器，不挡人）
        rendercolor 175,50,25；EnableAttackableByAI(5, 0, NONE)
        不能放东西在上面；preventStickyEnts = true；自己不能近战它，别人能
        忽略父物体旋转；本地偏移 (0,0,-5)
        script/target name = "forged_shadows_shield"
        受伤回调 Shield_OnPostDamaged；登记为 EMP / 破坏球 EMP 可伤设备
player.SetShadowShieldIsActive(true)
护盾特效 P_rev_reborn_shield 挂在护盾上，CP5 = (1,0,0)；激活爆发特效；"充满"声
每帧：
    shield 朝向 = 玩家朝向的反方向（VectorToAngles(-forward)）
    玩家隐身 / 相位中：关碰撞、特效对所有人隐藏；否则开碰撞、特效对敌我可见
线程结束：Shield_CleanUp + Destroy；SetShadowShieldIsActive(false)
```

要点：护盾"跟着走"靠父子关系（挂骨骼点），但**忽略父物体旋转、每帧手动设朝向**，所以护盾不会跟着动画摆动，只跟水平朝向（推断：`-forward` 说明模型正面朝后建的，或是半罩朝前）。

#### 3.2.2 伤害重定向 `OnPlayerTookDamage`（`.nut:638-697`）+ `Shield_OnPostDamaged`（`.nut:887-977`）

```
玩家受伤 且 在暗影中：
  若 有护盾（表里有记录）：
     类型 == 子弹 或 近战 → 玩家伤害 ×0；shield.TakeDamage(原伤害, 同攻击者, 同 inflictor, 同 damageSourceId)
     类型 == 爆炸：
         毒气（damagedef_grenade_gas / gas_exposure）、Conduit 地雷 → 打玩家，不管护盾
         其他爆炸 → 玩家伤害 ×0（护盾自己作为实体吃范围伤害，见推断）
     特例 Crypto EMP、防御轰炸、滚雷爆炸 → 玩家伤害 ×0
     其他类型（如燃烧）→ 不处理，直接打玩家（推断）
  否则若 有 lastDamageInflictor[player]：
     这次 inflictor 和打碎护盾的是同一个 → 本次伤害 ×0
     删除记录（只免一次）
  否则：
     thread ShadowForm_ShieldRegenDelay（重新开始 1 s 延迟）
```

推断：爆炸对玩家缩成 0 后，护盾是怎么掉血的——护盾 `DAMAGE_YES` 且不挡范围伤害，爆炸的范围伤害本来就会单独打到护盾实体。要实测。

护盾受伤 `Shield_OnPostDamaged`：

```
damage <= 0 → 返回
受击特效线程；服务端→客户端发受击方向
若攻击者是玩家：
    加 DF_SOUR、DAMAGEFLAG_VICTIM_HAS_VORTEX（命中反馈不同）
    攻击者的被动（Warlord's Ire 高亮、Vantage 标记）照样触发
    给攻击者记助攻；NotifyDidDamage(伤害 = min(damage, 护盾血))，不响命中音
    记入伤害统计和伤害历史
溢出（开关 enableCarryoverDmg=1）：damage > 护盾血 且 不是破坏球 / Crypto EMP / EMP 陷阱
    → owner.TakeDamage(damage − 护盾血, 同攻击者, 同 inflictor, DF_OVERFLOW)
更新 HUD：剩余 = clamp(护盾血 − damage, 0, 75)
若打碎：
    从表里删护盾；lastDamageInflictor[owner] = 这次 inflictor
    SetShadowShieldIsActive(false)；Shield_CleanUp（黏附物掉落）；破碎特效 1 s
    网络变量 = 0；thread ShadowForm_ShieldRegenDelay
LiveAPI 事件
```

注意：溢出伤害是在"从表里删护盾"**之前**打给玩家的（`.nut:944` 早于 `.nut:957`），这时 `OnPlayerTookDamage` 还认为护盾在；溢出伤害没带子弹 / 近战 / 爆炸类型（推断：`TakeDamage` 的表里没设 damageType，默认 0），所以走"其他类型"直接打玩家。要实测。

"同一 inflictor 免一次"：子弹的 inflictor 一般是武器本身（推断），所以效果是：打碎护盾那把枪的**下一发**不掉血，之后照常。对霰弹枪来说就是"同一发的其他弹丸不会穿过去"。

#### 3.2.3 延迟回复 `ShadowForm_ShieldRegenDelay`（`.nut:704-742`）

```
发 EndShieldRegenDelay（杀掉上一个回复线程）→ 自己也监听它
wait shieldRegenDelay (1 s)
播回复声
v = 网络变量
while v != 75：
    v = clamp(v + shieldRegenRate, 0, 75)    // shieldRegenRate = 1.0，每"帧"+1
    写网络变量；通知客户端（isHeal=true → HUD 回复闪烁 0.4 s）
    WaitFrame()
回满 → thread ShadowForm_CreateShieldAroundPlayer（重建护盾实体）
```

**单位是"每帧"不是"每秒"**：`shieldRegenRate` 每个 `WaitFrame()` 加一次，所以回满 75 需要 75 个服务端帧。服务器 20 tick 时约 3.75 s，60 tick 时 1.25 s。要实测（第 5 节）。

回复期间护盾实体**不存在**，玩家直接挨打；挨打会走 `OnPlayerTookDamage` 的最后一个分支，重开 1 s 延迟（`.nut:694-695`），回复进度保留（从当前网络变量继续加）。

#### 3.2.4 黏附物 `ShadowShield_IsAllowedStickyEnt` / `ShadowShield_TrackStickyEnt_Thread`（`.nut:326-429`）

- 公共入口：`vscripts/weapons/_weapon_utility.nut:2013-2014`，投掷物判断"能不能黏在这个东西上"时，如果是暗影护盾就问它。
- 白名单（敌方的）：Fuse 集束弹 `mp_weapon_cluster_bomb_launcher`、Ash 电弧陷阱 `mp_weapon_arc_bolt`、电弧星 `GRENADE_EMP_WEAPON_NAME`。友方的一律不黏。其他投掷物不黏（护盾本身 `preventStickyEnts = true`）。
- 允许时起跟踪线程：

```
initial = TraceLine(护盾中心 → 黏附物, 忽略列表, VISIBLE)
hadLoS = initial.fraction == 1
WaitFrame()          // 让它真正黏上
每帧：
    TraceLine(护盾中心 → 黏附物)
    若被挡（fraction < 1）：     // 玩家带着护盾走，黏附物被拖进墙 / 门
        黏附物 ClearParent()
        若一开始看得见：把它放到挡住的点 endPos
        结束
```

忽略列表 `ShadowShieldIgnoreArray`（`.nut:389-429`）：所有活着的玩家、所有暗影护盾、Newcastle 移动护盾墙和无人机、Gibraltar 罩、Mirage 分身。
- 护盾被打碎 / 销毁时 `Shield_CleanUp`（`.nut:1067-1085`）：所有非粒子子物体 `ClearParent()`，黏着的手雷掉下来照样会炸。

#### 3.2.5 击杀延长 `ShadowForm_ExtendTimer`（`.nut:1132-1167`）

```
若在暗影中：
    新时长 = clamp(剩余 + extensionTime(5), 0, duration(25))   // 上限 25 s，不会超过初始
    StatusEffect_SetDuration(...)；重开到期警告线程
    enableShieldReset(=1)：杀掉回复线程，立刻重建满血护盾，网络变量 = 75，HUD 显示"击杀"
    客户端提示"大招时间 +5"
enableTacReset(=0，默认关)：战术充满
```

助攻窗口（`.nut:202-216`、`.nut:1098-1111`）：`curAssistTime = assistTime − (max_assist_time_gap − assistTime_cfg)`，等于把通用助攻窗口缩到 `assistTime`（3 s）。注意 `file.assistTime` 读的 playlist 键是 `revenant_shadow_form_extension_time`（`.nut:154`，和延长时间同一个键）：只要 playlist 覆盖了延长时间，助攻窗口会被一起改。像是原代码的笔误（推断）。

#### 3.2.6 暗影皮肤 `ShadowForm_ApplyShadowSkin`（`.nut:1169-1185`）

有 `ShadowSquad_reborn_3p` 皮肤就换上并清迷彩，没有就 `rendercolor = 0,0,0`。结束时 `ShadowSquadCancelCharacterSkin`（`.nut:538`）。`CPlayer.nut:172-175` 里重新上皮肤时对暗影护甲是空分支（被注释掉）。

### 3.3 客户端表现

- 状态效果开 → `ShadowForm_StartClient` → `ShadowForm_FXThink`（`.nut:1189-1254`）：
  - 驾驶舱粒子 `p_rev_reborn_FP_ult_screen_base`，CP1 = (1,1,1)，`EffectSetIsWithCockpit`。
  - 屏幕调色 `ability_silence.raw_hdr`：权重 0→1，0.25 s 线性；结束时 1→0，1.0 s（`ColorCorrection_LerpWeight` `.nut:1425-1439`，用 `GraphCapped` 线性插值，`ColorCorrection_SetExclusive(true)`）。
  - 1P 激活声 + 循环声。
- `ShadowShield_ToggleFX_Think`（`.nut:1256-1301`）：每帧读网络变量。护盾血 ≤0 → 停 `p_rev_reborn_FP_ult_screen_shield`；回到满（== 75）→ 重开并震动 `rumble_stim_activate`。
- 状态效果关 → `ShadowForm_StopClient`：震动 `rumble_burn_card_activate`，发 `ShadowForm_EndShadowScreenFx`。
- 受击（`ServerToClient_UpdateDamageRUI(isHeal=false)`）→ `DamageTakenFlash`（`.nut:1365-1402`）：两个 1P 粒子 `P_armor_FP_Hit_rev`、`P_health_hex_rev_fast`，震动 `rumble_pilot_hurt`，0.2 s。
- 回复（isHeal=true, isKill=false）→ `HealFlash` 0.4 s，`isRecharging=true`；击杀重置（isKill=true）→ 只记 `lastKillTime`。
- HUD `MpAbilityShadowForm_PopulateRui`（`.nut:1304-1316`）：`timeRemaining` 跟踪状态效果剩余；`mitigatedDamageRemaining`、`maxMitigatedDamage`(75)、受击 / 回复闪烁开关、`lastKillTime`。
- 击杀者 HUD：打护盾时显示"暗影护盾"样式的血条（`vscripts/client/rui/cl_hud.gnut:505-509`）。
- 智能弹药锁定：在暗影中显示锁定到期时间（`vscripts/weapons/cl_smart_ammo.gnut:196-199`）。

### 3.4 依赖的公共代码

- 状态效果框架 `StatusEffect_AddTimed / HasSeverity / GetTimeRemaining / SetDuration / Stop`、客户端 `StatusEffect_RegisterEnabledCallback` → `_shared/E-STATUS-EFFECT.md`。
- 屏幕调色 `ColorCorrection_Register / SetExclusive / SetWeight` → `_shared/E-SCREEN-COLOR-CORRECTION.md`。
- 黏附判断 `_weapon_utility.nut:2013`。
- 被动 `PAS_FORTIFIED`（`sh_passives.gnut:224`）：脚本里唯一用途是免受击减速（`_gamemode_survival.nut:7769`）。Fortified 的减伤百分比是角色类的 `CharacterClass_GetDamageScale`（`sh_character_select.gnut:4980-4985`），和这个被动无关（推断：大招里加的 Fortified 只给免减速，不额外减伤）。
- 原生：`EnterShadowFormFortified`、`LeaveShadowForm`、`SetShadowShieldIsActive`、`SetIgnoreMoveParentRotation`。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| duration | 25.0 | s | `.nut:77`、playlist `revenant_shadow_form_duration`（`.nut:152`）；`.txt:45 fire_duration 25` | 持续时间；也是延长的上限 | 大：更久；延长上限跟着变 |
| extensionTime | 5.0 | s | `.nut:78`、playlist `revenant_shadow_form_extension_time` | 每次击杀 / 击倒 / 助攻加时 | 大：连杀更容易一直开着 |
| assistTime | 3.0 | s | `.nut:79`；playlist 键**误用** `revenant_shadow_form_extension_time`（`.nut:154`） | 助攻算数的时间窗 | — |
| shieldHealth | 75 | HP | `.nut:80`、playlist `revenant_shadow_form_shield_health` | 护盾壳血量；网络变量上限 | 大：更耐打 |
| shieldRegenRate | 1.0 | HP/服务端帧 | `.nut:81`、playlist `..._shield_regen_rate` | 回复速度（每帧加） | 和 tick 率耦合，HSD 要换成 HP/s |
| shieldRegenDelay | 1.0 | s | `.nut:82`、playlist `..._shield_regen_delay` | 碎后 / 回复中挨打后多久开始回 | 大：更难回 |
| EXPIRATION_WARNING_TIME | 3.0 | s | `.nut:83` | 剩多少秒响到期警告 | |
| SHIELD_ORIGIN_OFFSET | (0,0,−5) | u | `.nut:84` | 护盾相对胸口的偏移 | |
| enableShieldReset | 1 | 开关 | `.nut:85`、playlist `..._enable_shield_reset` | 击杀时立刻重建满血护盾 | 0：击杀只加时 |
| enableTacReset | 0 | 开关 | `.nut:86` | 击杀时战术充满 | |
| enableTacCooldownReduc | 0 | 开关 | `.nut:87` | 大招期间战术加 `shadow_form_active` mod | |
| enableCarryoverDmg | 1 | 开关 | `.nut:88` | 护盾碎时溢出伤害打到玩家 | 0：最后一发多大都只碎盾 |
| 状态效果严重度 / 淡出 | 1.0 / 0.0 | — / s | `.nut:516` | | |
| 护盾 AI 仇恨 | `EnableAttackableByAI(5, 0, NONE)` | 优先级 5 | `.nut:774` | AI 会把护盾当成可打目标 | |
| 护盾颜色 | 175,50,25 | RGB | `.nut:773` | rendercolor（推断：碰撞模型本身不画，颜色可能无效） | |
| 护盾碰撞组 | `TRACE_COLLISION_GROUP_BLOCK_WEAPONS` | — | `.nut:772` | 只挡武器 | |
| 护盾特效 CP5 | 血量比例 0–1 | — | `.nut:803`、`.nut:1022` | 护盾外观随血量变 | |
| 受击特效时长 | 0.2 | s | `.nut:1026` | | |
| 破碎特效时长 | 1.0 | s | `.nut:1064` | | |
| 1P 受击闪烁 | 0.2 | s | `.nut:1399` | | |
| 1P 回复闪烁 | 0.4 | s | `.nut:1420` | | |
| 调色淡入 | 0 → 1，0.25 | 权重 / s | `.nut:1228` | | |
| 调色淡出 | 1 → 0，1.0 | 权重 / s | `.nut:1249` | | |
| 调色文件 | `materials/correction/ability_silence.raw_hdr` | — | `.nut:181` | 和 Silence 用同一张 LUT | |
| 驾驶舱粒子 CP1 | (1,1,1) | — | `.nut:1225` | | |
| 冷却（弹夹） | 180 / 回 1 每秒 | s | `.txt:40-46` | 180 s | |
| `upgrade_ult_one` | 弹夹 ×0.8 | — | `.txt:87-94` | 144 s | |
| 护甲回充 mod | ×1.25 / ×1.5 | — | `.txt:81-112` | | |
| toss_time | 2.2 | s | `.txt:27` | 按键到生效的动作时间（推断：生效在动画事件，可能早于 2.2 s） | |
| toss_pullout_time | 0.1 | s | `.txt:26` | | |
| 不能在滑索上用 | 0 | — | `.txt:23` | | |

## 5. 未解决和要实测的

1. **回复速度到底多快**：`shieldRegenRate` 按服务端帧加。要测本地 dedi 的 tick 率下 75 回满用时。测法：AgentLink 在服务端给自己开大招 → 用伤害命令打碎护盾 → 每 0.05 s 读 `revenant_shadow_health` 网络变量，记 0→75 的时间。
2. **爆炸是否打到护盾**：脚本只把玩家那份缩成 0，护盾掉血靠爆炸自己的范围伤害（推断）。测法：开大招，在脚下引爆破片手雷，读护盾血量变化和玩家血量。
3. **燃烧 / 铝热剂等其他伤害类型是否直接穿过**：脚本没处理就是穿过（推断）。测法：开大招站进铝热剂火里，看玩家血。
4. **溢出伤害的伤害类型**：推断是 0（打玩家）。测法：护盾剩 10 时吃一发 30 伤害的子弹，看玩家掉 20。
5. **同一 inflictor 免一次**：测法：用同一把枪连射打碎护盾，看碎后第一发是否不掉血。SDK 是否改过这段要对 S21 原版（没有原版对照，只能实测）。
6. **护盾实际形状和大小**：`forged_shadows_shield_physX.rmdl` 的碰撞体没看。测法：开大招，从各方向打射线（AgentLink `TraceLine`）记命中点，或解包模型看碰撞体。
7. **`EnterShadowFormFortified` 原生做了什么**（比如移动速度、受击动画）：脚本看不到。测法：开大招前后读移速、跳高；或 REA 看原生函数。**另外 S3 dedi 可能根本没有暗影状态**：SDK 在 `vscripts/mp/_staging_area.gnut:1843` 写了 `// S3: shadow form not available`。如果 `EnterShadowFormFortified` 在 S3 引擎不存在，`ShadowForm_Start` 会在 `.nut:517` 报错中断。测法：AgentLink 服务端开这个大招，看日志有没有脚本错误、状态效果是否加上（详见 `revenant-death-totem/SYSTEM.md` 第 5 节第 1 项）。
8. 生效时机：`toss_time 2.2` 内动画事件的确切时间。测法：记按键时刻和状态效果出现时刻。

**R5 实测（2026-11-01，combat-w2-rt，详见 [W2-RUNTIME.md](../W2-RUNTIME.md)）**
7. ✅ 本地能用：真大招（按住 `offhand4` 0.8 s 松开）~1.5 s 后生效，生成 `forged_shadows_shield` 壳 75 / 75（parent 在玩家身上），`shadow_form` 状态 1。`EnterShadowFormFortified()` 存在、不报错，但 `IsShadowForm()` 仍 false（只有普通 `EnterShadowForm` 会让它变 true）。
1. 回复速度**没测到**：脚本 `TakeDamage` 打壳 50 后 9 s 不回——回复走 `SHADOW_FORM_HEALTH_NETVAR`，由壳的受伤回调启动，脚本伤害触发不到；要真攻击者（本地 NPC 不开火）。服务端帧 0.05 s。
- 世界伤害（`TakeDamage` from worldspawn）直接扣玩家血，不经过壳。
2–6、8 没测。

## 6. HSD 实现

**未实现。** `HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 里没有护盾实体、伤害重定向、状态效果框架、屏幕调色（只读查过 README、`CombatCore.cs`、`CombatVisuals.cs`、`Tacticals.cs`）。

建议做法：
- **护盾壳** = 一个 `CombatUnit`（`CombatCore.cs:65`），位置每帧跟玩家胸口，`Health(75)` 带 `regenDelay = 1`、`regenRate = 75 / 实测回满时间`（`CombatCore.cs:36-63` 的 `Health` 已有"延迟 + 速度"规则，可以直接用；但 R5 是"碎了才开始回、回满才重建"，`Health` 是"不满就回"，需要加一个 `broken` 状态）。
- **伤害重定向**：在 `CombatSim` 伤害入口处，如果玩家有暗影状态且护盾在，按伤害类型（子弹 / 近战 / 爆炸 → 护盾；毒气 → 玩家）分流，溢出部分打玩家。
- **计时**：做一个通用状态效果表（id、严重度、到期时间，可改时长），见 `_shared/E-STATUS-EFFECT.md`。击杀延长 = `SetDuration(min(剩余 + 5, 25))`。
- **画面**：全屏后处理调色（URP Volume 权重 0→1 0.25 s，1→0 1 s），见 `_shared/E-SCREEN-COLOR-CORRECTION.md`。
- 开关建议：`hsd.combat.shadowForm.*`（时长、护盾血、回复速度、溢出伤害开关、击杀重置开关）。
- 和 R5 的差别：实现后在 `R5-DIFF-ARCHIVE.md` 记回复速度单位（R5 每帧，HSD 每秒）。
