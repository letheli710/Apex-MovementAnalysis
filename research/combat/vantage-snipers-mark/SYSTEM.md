# Vantage 大招 Sniper's Mark 狙击标记：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_ability_sniper_ult.nut`，`txt` = `weapons/mp_ability_sniper_ult.txt`，`bow` = `vscripts/weapons/mp_weapon_bow_ult_missile.nut`。

## 0. 概要

- **技能**：Vantage / 大招 / Sniper's Mark / `mp_ability_sniper_ult`。
- **一句话**：拿出一把专用狙击枪（50 伤害、爆头 ×1.5、子弹 34000 u/s 有下坠、两档倍镜）。用它打中敌人就给他挂"标记"10 s：标记期间 Vantage 再用这把枪打他伤害 ×2.5（旧数值 ×2），Vantage 队友的其他武器打他伤害 ×1.15。子弹从人身边 120 u 内飞过，那人身上也闪 1 s 的"擦过"标记（只是给 Vantage 队伍看的特效）。开镜时有激光（敌人看得见的反光），开过一枪后 10 s 内才亮。
- **禁疗**：**这个构建里没有**。`SniperUlt_PlayerDenyHealsThread` 写了但没有任何地方调用（`nut:745-761`），相关常量全部注释掉（`nut:28-38`）。第 3.2.4 节。
- **分类**：**好技能**（标记 + 增伤，对 AI 一样有用）＋ **系统**（"标记目标 → 不同来源不同增伤倍数"的伤害回调；"子弹线附近的人"查询）＋ **可视化**（标记特效只给己方看、敌人看到的狙击反光、背上的枪身体组切换）。偏武器（C0 2.1）。
- **可拆出的部件**：
  - 标记 + 来源区分增伤（伤害回调里看状态效果和攻击者队伍）→ 3.2.2 `SniperUlt_OnDamagedByPlayer_DiamondScan`，公共部件 `_shared/C-DAMAGE-MODIFIERS.md`
  - 子弹擦过检测（发射点到落点的线段，取中点为球心查人，再算到线段距离）→ 3.2.3 `OnProjectileCollision_sniper_ult`
  - 激光 / 反光的开关时机（开镜 + 开枪后 10 s）→ 3.3
  - 命中返还战术（升级）→ 3.2.2 `SniperUlt_TryApplyTacRefresh`
- **`mp_weapon_bow_ult_missile` 是什么**：Sparrow（内部名 Artemis，`localization_english.txt:29129`）的大招"箭落地 → 核心充能 → 每秒放电"，**和 Vantage 无关**。名字里的 bow 是 Sparrow 的弓。详见第 7 节。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 专用狙击枪 | 大招槽武器，`fire_mode offhandHybrid`，`offhand_active_slot mainHand`（像主武器一样拿着） | `txt:8-20` |
| 子弹 | `FireBallisticRoundWithDrop`（有下坠的弹道子弹），34000 u/s；命中体积 1 → 0.04 s 5 → 0.1 s 7 → 0.16 s 内 10 | `nut:309`、`txt:197-204` |
| 伤害 | `.txt`：50（近中远都 50），爆头 ×1.5，`DF_SNIPER | DF_BULLET | DF_KNOCK_BACK`，冲击力 5000 | `txt:182-193`、`txt:69` |
| 标记 | 状态效果 `sonar_round_embedded`（1.0，10 s），`target.p.sonarRoundsAttacker` 记谁标的 | `nut:688-741` |
| 增伤 | 全局伤害回调 `AddDamageByCallback("player", …)`：被标记 + 攻击者和标记者同队 → 大招枪 ×2.5（或 ×2）/ 其他 ×1.15 | `nut:101`、`nut:457-543` |
| 标记特效 | `P_van_sniper_mark` 挂 `CHESTFOCUS`，**只给标记者队伍看**（`ENTITY_VISIBLE_TO_FRIENDLY`） | `nut:697-699` |
| 擦过特效 | `P_van_sniper_mark_wizby`，1 s，只给 Vantage 队伍看 | `nut:620-645` |
| 被标记者 | 声音 `Vantage_Ult_TargetLock_Victim_1p`；武器状态 RUI 显示 debuff 倒计时 | `nut:882-945`、`client/rui/cl_weapon_status.gnut:2329-2332` |
| 命中视觉 | `emp` 0.2，0.5 s，淡出 1.0（"For visual flavour"） | `nut:542` |
| 激光 / 反光 | 武器自带 targeting laser：1P 无，3P 友方 `P_van_sniper_glint`、敌方 `P_van_sniper_glint_enemy`，长 30000；脚本 `SetTargetingLaserEnabled` 控制开关 | `txt:207-216`、`nut:139`、`nut:226-247`、`nut:317-359` |
| 背上的枪 | 身体组 `ultimate`：拿出时隐藏、收起 0.4 s 后显示 | `nut:146`、`nut:182-206`、`nut:763-774` |
| 倍镜 | `zoom_fov 19.86`、按键切换到 `zoom_toggle_fov 10.0`（0.3 s 过渡），切换音效 | `txt:238-239`、`nut:251-268` |

**客户端 / 服务端**：增伤、标记、擦过是服务端；激光开关两边预测；被标记者的 1P 特效是客户端（特效代码被剥空了，`nut:831-839`、`nut:892-900` 只剩空行，只留声音）。

**怀疑点**：
- `txt:32`：`// Disabled on dedi: this script callback is not bound there. "OnWeaponZoomFOVToggle" …`——**本地补丁**，倍镜切换音效回调在 dedi 上关掉了。同样的注释出现在 9 个 `.txt` 里（如 `mp_weapon_mobile_hmg.txt:50`）。
- `IsVantageBuffsEnabled()` 读 playlist `vantage_s25_1_buffs_enabled`，默认 true（`vscripts/weapons/sh_vantage_companion.nut:310-313`）——**这是 S25.1 的改动**，说明本地脚本比 S21 新（或混入了新版）。
- 大段被剥掉的 `#if` 空行（`nut:150-163`、`nut:776-793`、`nut:947-985`），推断是官方原码剥离，有一部分功能（可能是 S25 的新特性）被删掉了。

## 2. 流程

```
按大招（弹量够 40）→ 拿出狙击枪（deploy 1.1 s），背上的枪隐藏，激光关
开镜（zoom in 0.5 s）：激光开（S25 规则：只有在"开枪后 10 s"窗口内才开）
开枪（fire_rate 3、拉栓 1.2 s）：扣 40；子弹 34000 u/s 下坠
  S25：开镜中就开激光，并起 10 s 激光计时线程（再开枪重置）
  命中任何实体：擦过检测 → 120 u 内的其他玩家 1 s 擦过特效
  伤害回调：
    目标已被标记且攻击者与标记者同队：大招枪 ×2.5 / 其他 ×1.15
    攻击者是 Vantage（PAS_VANTAGE）且用的是大招枪：升级返还战术；标记 10 s（已有就刷新）；emp 视觉 0.5 s
收起（holster 0.4 s）：背上的枪显示
```

- **弹量**：弹匣 240、每发 40、开局 40、备弹上限 200、回充 1/s，`cooldown_type ammo`（`txt:41-68`）。推断：满弹匣 6 发、40 s 回一发。实际可用发数第 5 节要测。
- **打断**：近战取消，`offhand_restore_after_melee 1`（近战后恢复），`offhand_raise_is_interrupt_resumable 1`。
- **标记结束**：时间到 / 目标死亡 / 目标倒地（倒地时线程直接 return，`nut:736-737`）。重复命中只刷新时长，不叠加倍数（`nut:677-681`）。
- **升级**：`PAS_ULT_UPGRADE_ONE`（`upgrade_vantage_ult_tac_refresh`）：大招枪每次命中（不管是否标记）返还一发战术（`nut:441-454`）。

## 3. 代码

### 3.1 入口

- `SniperUlt_Init`（`nut:89-131`）：预载 4 个粒子；服务端注册对**所有玩家攻击**的伤害回调 `AddDamageByCallback("player", SniperUlt_OnDamagedByPlayer_DiamondScan)`；客户端注册 `healing_denied` 和 `sonar_round_embedded` 的开关回调；客户端打开 `rope_visibility_fx_enable`（激光特效要它）。
- 武器回调（`txt:24-35`）：Activate / Deactivate / PrimaryAttack / AttemptOffhandSwitch / StartZoomIn / StartZoomOut / ProjectileCollision / ClientAnimEvent。

### 3.2 核心逻辑

#### 3.2.1 发射（`nut:294-331`）

```
弹匣满时 → PlayerUsedOffhand（第一发才算"用了大招"）
projectile = FireBallisticRoundWithDrop(weapon, pos, dir, …)；记下 savedOrigin / savedDir
S25 buffs：ADS 中开激光；thread 激光 10 s 计时
TrackingVision POI
return 40
```

#### 3.2.2 增伤和标记 `SniperUlt_OnDamagedByPlayer_DiamondScan`（`nut:457-543`）

```
if 溢出伤害 (DF_OVERFLOW) → return
if 目标是训练假人:
    大招枪 → SniperUlt_Mark_Dummie（已标记则先按大招倍数加伤，再刷新标记）+ 返还战术
    其他武器且已标记 → ×1.15（注意：读了 playlist 但用的是常量，nut:477-478）
    return
if 目标不是玩家 → return                    // 普通 NPC 不会被标记、也不吃增伤
if 目标已标记 且 攻击者队伍 == 标记者队伍:
    大招枪 → ×playlist vantage_sniperult_dmgScale（默认 2.5 / 旧 2）
    其他 → ×playlist vantage_sniperult_team_dmgScale（默认 1.15）
if 攻击者不是 Vantage 或 不是大招枪 → return
返还战术（升级）
如果是第一次标记且打不死 → 喊话
SniperUlt_PlayerMarked(10 s)；emp 视觉
```

- 先算增伤再标记：**第一发不吃 ×2.5**，第二发起才吃（同一发里先判断"已标记"，`nut:487` 在 `nut:539` 之前）。
- 增伤是乘在本次伤害上，推断在爆头倍数之后（引擎先算爆头，再调脚本回调）。50 × 1.5 × 2.5 = 187.5 爆头。
- 假人分支和玩家分支用的 playlist 名字不同（`sniperult_vantage_dmgScale` vs `vantage_sniperult_dmgScale`），假人分支的队友增伤**不检查队伍**。

#### 3.2.3 擦过检测（`nut:373-429`）

```
line = 命中点 - 发射点；mid = 发射点 + line/2
候选 = GetPlayerArrayEx(任何人, 中心 mid, 半径 |line|/2)   // 线段的外接球
对每个候选（不是被打中的那个，同 realm）：
    d = 候选中心到线段的距离；d ≤ 120 → 擦过特效 1 s
```

只是给 Vantage 队伍看"子弹从谁身边过去了"，没有伤害和增伤。

#### 3.2.4 禁疗（死代码）

- `SniperUlt_PlayerDenyHealsThread`（`nut:745-761`）：加 `healing_denied` 无限期，`wait duration` 后去掉。**全仓库没有调用**（`grep` 只有定义）。
- 其他系统会读 `healing_denied`：护盾回复等着它结束（`_armor_shield_regen.nut:237`）、消耗品不能用护盾电池（`mp_ability_consumable.nut:1795`、`:2666`）、武器 RUI 显示倒计时（`cl_weapon_status.gnut:2348`）。也就是**禁疗系统还在，只是 Vantage 不再施加**。推断是某个赛季改掉了；`SNIPERULT_HEALINGDENIED_DURATION = 15` 还是 `global const`（`nut:30`）。

### 3.3 客户端表现

- **激光 / 反光**（`nut:210-249`、`nut:335-359`）：开镜时 `!IsVantageBuffsEnabled() || 在 10 s 窗口内` 才开；关镜就关；10 s 后关。也就是 **S25 规则下"不开枪就没有反光"**，开一枪后 10 s 内开镜才会暴露。反光对敌人是 `P_van_sniper_glint_enemy`，30000 u。
- **标记特效**：只给标记者队伍看；被标记的人只有声音和 debuff 图标。
- **背上的枪**：注释说 raise/lower 事件对大招武器不好用，所以收起时等 `holster_time` 再显示（`nut:181`）。

### 3.4 依赖的公共代码

- `FireBallisticRoundWithDrop`（弹道子弹）、`GetPlayerArrayEx`、`GetDistanceFromLineSegment`、`AddDamageByCallback`、`StatusEffect_*`、`FiringRange_AddToRemoveOnCharacterChange`。
- `IsVantageBuffsEnabled`（`sh_vantage_companion.nut:310`）。
- 智能弹药 UI 也读 `sonar_round_embedded`（`cl_smart_ammo.gnut:374`、`:418`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| SNIPERULT_PLAYER_MARKED_DURATION（`sniperult_marked_duration`） | 10 | s | `nut:42`、`nut:433` | 标记时长 | — |
| SNIPERULT_VANTAGE_DMG_SCALE | 2 | × | `nut:43` | 旧规则：大招枪打标记目标 | — |
| SNIPERULT_VANTAGE_DMG_SCALE_BUFFED | 2.5 | × | `nut:44`、`nut:361-364` | S25.1 规则（默认） | — |
| playlist `vantage_sniperult_dmgScale` | 默认同上 | × | `nut:495` | 覆盖 | — |
| SNIPERULT_TEAM_DMG_SCALE（`vantage_sniperult_team_dmgScale`） | 1.15 | × | `nut:47`、`nut:502` | 队友打标记目标 | — |
| SNIPERULT_WHIZ_BY_SCAN_DURATION | 1 | s | `nut:41` | 擦过特效 | — |
| 擦过距离 | 120 | u | `nut:419` | — | — |
| SNIPERULT_LASER_DURATION | 10 | s | `nut:45` | 开枪后激光窗口 | — |
| emp 视觉 | 0.2 / 0.5 s / 淡出 1.0 | — | `nut:542` | 命中闪屏 | — |
| SNIPERULT_HEALINGDENIED_DURATION | 15（未使用） | s | `nut:30` | 死代码 | — |
| vantage_s25_1_buffs_enabled | true | — | `sh_vantage_companion.nut:312` | 新旧规则切换 | — |
| 伤害 | 50（近 / 远 / 很远都 50；距离 7500 / 10000 / 12000） | HP / u | `txt:182-191` | 不衰减 | — |
| damage_headshot_scale | 1.5 | × | `txt:192` | — | — |
| headshot_distance | 29528 | u | `.txt`（`txt:191` 附近） | 爆头最远距离 | — |
| projectile_launch_speed | 34000 | u/s | `txt:197` | 子弹速度 | — |
| bolt_hitsize | 1 → 5（0.04 s）→ 7（0.1 s）→ 10（0.16 s） | u | `txt:198-204` | 子弹命中体积随时间变大 | 大了更好打中 |
| impulse_force | 5000 | — | `txt:69` | 击退 | — |
| fire_rate / rechamber_time | 3 / 1.2 | 发/s / s | `txt:56`、`txt:70` | 拉栓 | — |
| deploy / raise / holster / lower | 1.1 / 1.1 / 0.4 / 0.4 | s | `txt:57-60` | — | — |
| 弹量 | 弹匣 240、每发 40、开局 40、备弹 200、回充 1/s | — | `txt:41-50` | 推断 6 发 / 40 s 一发 | 第 5 节 |
| zoom_fov / zoom_toggle_fov | 19.86 / 10.0（过渡 0.3 s） | 度 | `txt:238-239` | 两档倍镜 | — |
| zoom_time_in / out | 0.5 / 0.5 | s | `.txt` | — | — |
| 腰射扩散 | 站 15、跑 18、冲刺 20、蹲 15、空中 20；开镜 0（空中 6） | 度 | `.txt` `spread_*` | — | — |
| targeting_laser_range | 30000 | u | `txt:213` | 反光距离 | — |

## 5. 未解决和要实测的

1. **实际发数和回充**：弹匣 240 / 每发 40 / 开局 40 / 备弹 200 / `ammo_no_remove_from_stockpile 1` 组合起来到底几发。**测**：火力训练场开大连开，记 `GetWeaponPrimaryClipCount()` 和备弹。
2. **增伤和爆头的先后**：推断回调在爆头后。**测**：标记训练假人后爆头一枪、打身体一枪，看数字（假人分支用常量 ×2.5 / ×1.15）。
3. **普通 NPC 不吃标记**：`nut:484` 非玩家直接 return（假人除外）。**测**：打 Prowler。
4. **S25.1 规则**：本地是 S21 客户端，但脚本默认开 S25.1 规则（×2.5、激光窗口）。客户端和 dedi 用的是不是同一份脚本要核对；`playlists_r5_patch.txt` 有没有设 `vantage_s25_1_buffs_enabled`。
5. 禁疗不存在：如果用户记得 Vantage 有禁疗，那是别的赛季；本地构建没有。

## 6. HSD 实现

**未实现**。现有零件：`Weapons.cs` 测试步枪的射线、`CombatSim` 伤害；没有"状态效果 + 按来源增伤"的通用层。

建议做法：

1. **先做通用的伤害修正层**（`_shared/C-DAMAGE-MODIFIERS.md`）：单位身上挂"标记"列表（来源、到期时间、对来源本人的倍数、对其他友方的倍数），`CombatSim` 结算伤害时乘上去。Vantage 标记、Whistler 选项 C、Rampart 加强掩体都走这一层。
2. **武器**：HSD 武器阶段做狙击枪时加"标记弹"模式：50 伤害、爆头 ×1.5、子弹速度 34000（HSD 里近似即时命中，或用弹道下坠）、命中体积随时间变大可以先不做。
3. **标记对 AI 生效**（R5 只对玩家）：命中 AI → 标记 10 s；玩家自己打 ×2.5，玩家的召唤物 / 炮塔打 ×1.15。差别记进 `R5-DIFF-ARCHIVE.md`。
4. **禁疗**：R5 本地构建没有；HSD 如有会回血的 AI（治疗兵），可以把"被标记的不能被治疗"做成开关 `sniperMark.denyHeal`，默认关，并写明是 HSD 新增。
5. **可视化**：标记特效挂胸口（只给玩家看）、擦过 120 u 的敌人闪一下、开枪后 10 s 内开镜有反光（PvE 里可以用作"AI 会被反光吸引"的仇恨来源，开关 `sniperMark.glintAggro`，HSD 新增）。

开关建议：PlayerPrefs `hsd.combat.vantage.ult.*`（`markTime`、`selfMult`、`teamMult`、`denyHeal`、`glintAggro`）。

## 7. 附：`mp_weapon_bow_ult_missile` 是什么

结论：**Sparrow（内部名 Artemis）的大招，和 Vantage 的 Sniper's Mark 没有关系**。

- 证据：本地化 `character_Artemis_NAME = "Sparrow"`（`localization_english.txt:29129`）；damageSourceId 显示名 `#WPN_ARTEMIS_ULTIMATE`（`vscripts/sh_damage_types.nut:1005`）；音效全是 `Sparrow_Ult_*`；入口 `BowUlt_OnArrowLanded` 由 `mp_weapon_charge_gauntlet.nut:117`（`ArrowUlt_ProjectileLanded`）调用。`.txt` 的 printname 是借来的占位 `#WPN_MORTAR_RING`（`weapons/mp_weapon_bow_ult_missile.txt:3`）。
- 做什么（`bow:304-407`、`bow:495-567`）：箭落地生成核心（400 血）→ 落地 15 伤害（内 50 / 外 150）+ 扫描能看见的敌人 3 s → 充能 1.5 s + 预热 0.5 s → 6 s 内（升级 3 s）每 1 s 放电一次：半径 800 内、核心能看见的所有活着的玩家——敌人 20 伤害 + `move_slow` 0.3 6 s，友方也被减速 0.15（`hasFriendlySlow`）；倒地的敌人只减速不扣血；升级二吸血（伤害全额回给 Sparrow，先回血再回盾）；建筑 / 载具伤害 ×5；新核心落在旧核心 200 u 内会摧毁旧的。
- **SDK 重写嫌疑很高**：文件里的注释是解释性的现代写法（如 `bow:409`"The landing pulse reveals every enemy the core can see for impact_scan_time."、`bow:345`、`bow:568-569`），没有被剥掉的 `#if` 空行，`tuning` 结构体集中所有数值——像社区按视频复刻的。数值不能当 R5 官方数据用。
- 对 HSD 的价值：一个"落地 → 充能 → 周期放电 + 可视线检查 + 连线特效"的炮塔式区域，可以在 Wattson / Conduit / 炮塔类研究时对照。不属于批次 C，**不单独建记录**，到此为止（2026-10-31，原因：和 Vantage 无关、疑似社区重写）。
