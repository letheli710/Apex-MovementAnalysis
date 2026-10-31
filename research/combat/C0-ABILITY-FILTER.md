# C0 · 战斗研究第一步：技能过滤（PvE）

状态：**草稿，等用户确认**（2026-10-31）。

用户 2026-10-31 定：HSD 是 PvE 游戏，攻击研究按 **技能 → 道具 → 武器** 的顺序做；先把技能过滤一遍，只研究要用的。本文件是技能这一步的过滤表。

来源：本地 R5Flowstate S21 脚本 `research-src/s21-platform/scripts/weapons/*.txt` 和 `vscripts/weapons/*.nut`。传奇和能力的对应关系是按脚本名和本地化键对的；标 `?` 的还没核对。

## 1. 过滤标准（请先确认这一节）

**每个技能看三样**（用户 10-31 改定："我们不能仅因为这个技能的使用程度，还包括可视化，以及这些有参考价值的系统"）：

1. **效果**：伤害、控制。
2. **可视化和表现**：动画、特效、跟随运动、绳子、屏幕效果、HUD 等。
3. **背后可复用的系统**：指派目标、跟随、瞬移、伙伴 AI、仇恨、可操控载具等，HSD 做别的东西时能参考。

三样里有一样有价值，就不算"太基础"。下表的判定以这三样为准。

| 判定 | 标准 | 例子 |
|---|---|---|
| **保留** | 直接造成伤害，或者对敌人有控制效果（减速、眩晕、拉扯、破盾、限制行动）。这些效果对 AI 敌人一样有用 | 轰炸、手雷类、陷阱、黑洞 |
| **待定** | 只作用在自己或队友身上的增益、防御、续航。打 AI 用得上，但不算"攻击" | 护盾罩、移动掩体、自身伤害 / 换弹增益 |
| **参考（系统 / 可视化）** | 效果本身对 PvE 不重要或很简单，但可视化或背后的系统有参考价值 | Lifeline 治疗无人机（跟随 + 指派）、Mirage 分身（仇恨） |
| **不要** | 三样都没有价值：效果只对真人或多人团队有用，表现和系统也很普通 | Loba 黑市、Caustic 毒气视觉 |
| **移动线已做** | 已经在移动研究里做过或搁置过，这次不重复 | Octane 兴奋剂、Wraith 虚空、Valk 喷气 |
| ~~太基础，不做~~（用户 10-31 先定，同日改掉） | 原来是"单纯回血 / 加速 / 加护甲 / 加弹药就不做"。用户同日改为看三样，这一类取消，原来的 5 项全部重新分类（见 2.2b） | — |

被动技能只看和攻击有关的那几个（比如 Fuse 多带手雷），其他的跳过。

## 2. 过滤表

### 2.1 保留（攻击 / 控制）：20 项

| 传奇 | 槽位 | 能力 | 脚本 | 对敌效果 | 备注 |
|---|---|---|---|---|---|
| Bangalore | 大招 | Rolling Thunder 滚雷 | `mp_weapon_grenade_creeping_bombardment` | 一路地毯式爆炸，伤害 + 减速 | |
| Gibraltar | 大招 | Defensive Bombardment 防御轰炸 | `mp_weapon_grenade_defensive_bombardment` | 圆形区域炮击 | |
| Fuse | 战术 | Knuckle Cluster 指节集束弹 | `mp_weapon_cluster_bomb_launcher` | 弹射后散开爆炸 | 弹道部分已在 APEX-REPORT 2.7 |
| Fuse | 大招 | The Motherlode 火焰环 | `mp_weapon_mortar_ring` | 落点一圈火墙，进出都受伤 | |
| Fuse | 被动 | Grenadier 投掷专家 | — | 多带手雷、扔更远 | 已在 APEX-REPORT 2.7；道具阶段一起看 |
| Caustic | 战术 | Nox Gas Trap 毒气陷阱 | `mp_weapon_dirty_bomb` | 触发后毒气持续伤害 + 减速 | |
| Caustic | 大招 | Nox Gas Grenade 毒气手雷 | `mp_weapon_grenade_gas` | 大范围毒气 | |
| Wattson | 战术 | Perimeter Security 电网 | `mp_weapon_tesla_trap` | 穿过受伤 + 减速 | 适合 PvE 守点 |
| Rampart | 大招 | Mobile Minigun "Sheila" | `mp_weapon_mobile_hmg` | 一把重机枪 | 偏武器，可以挪到武器阶段 |
| Valkyrie | 战术 | Missile Swarm 导弹群 | `mp_ability_valk_cluster_missile` | 伤害 + 晕眩 | |
| Horizon | 大招 | Black Hole 黑洞 | `mp_ability_horizon_black_hole` | 把敌人吸到中心 | PvE 里聚怪价值高 |
| Mad Maggie | 战术 | Riot Drill 钻头 | `mp_weapon_riot_drill` | 穿墙持续伤害 | |
| Mad Maggie | 大招 | Wrecking Ball 破坏球 | `mp_ability_wrecking_ball` | 弹跳后爆炸，路上留加速片 | 加速片部分属移动 |
| Ash | 战术 | Arc Snare 电弧陷阱 | `mp_weapon_arc_bolt` | 伤害 + 拴住 | |
| Catalyst | 战术 | Piercing Spikes 尖刺 | `mp_ability_spike_strip` | 伤害 + 减速 | |
| Conduit | 大招 | Energy Barricade 能量屏障 | `mp_ability_conduit_shield_mines_line` | 一排地雷，伤害 + 减速 | |
| Crypto | 大招 | Drone EMP | `mp_ability_crypto_drone_emp` | 破盾 + 减速 | 要先放无人机 |
| Newcastle | 大招 | Castle Wall 城墙 | `mp_ability_armored_leap` | 落地冲击伤害 + 减速，再立墙 | 跳跃部分偏移动，城墙偏防御 |
| Vantage | 大招 | Sniper's Mark 狙击标记 | `mp_ability_sniper_ult`（`SniperUlt_*`、`SniperUlt_VantageDamageScaleDefault`，已核对） | 一把特殊狙击，标记后伤害加成（本地构建没有禁疗，是死代码；10-31 批次 C 更正） | 偏武器 |
| Ballistic | 战术 | Whistler 呼啸弹 | `mp_ability_debuff_zone` | 追踪弹，打中后对方开枪会过热 | 过热是针对玩家的；对 AI 要改成"压制" |

（Rampart 大招、Vantage 大招本质是武器，计数时算在保留里，但研究时可以放到武器阶段。）

### 2.2 待定（防御类，机制不简单）：5 项

| 传奇 | 槽位 | 能力 | 脚本 | 作用 | 待定的原因 |
|---|---|---|---|---|---|
| Gibraltar | 战术 | Dome of Protection 护罩 | `mp_weapon_bubble_bunker`（`mp_ability_area_cloak` 只有 .txt 没脚本，无关） | 挡子弹的穹顶 | 防御；AI 会不会打穿要看敌人设计 |
| Gibraltar | 被动 | Gun Shield 枪盾 | `mp_ability_gibraltar_shield` | 开镜时前方护盾 | 防御 |
| Rampart | 战术 | Amped Cover 加强掩体 | `mp_weapon_cover_wall` | 掩体 + 从后面打出去伤害加成 | 有伤害加成；TF2 那边 A 型墙也在做（APEX-HANDOFF 2.9） |
| Newcastle | 战术 | Mobile Shield 移动护盾 | `mp_ability_shield_throw` | 可控移动的护盾 | 防御 |
| Wattson | 大招 | Interception Pylon 拦截塔 | `mp_weapon_trophy_defense_system` | 拦截投射物、回护盾 | 防御；要看 AI 是否丢投掷物 |

### 2.2b 参考（系统 / 可视化）：从"太基础"拿回的 5 项

历史：用户 10-31 先定"简单的回血、加速没必要添加"，把这 5 项归到"太基础，不做"；同日改成看三样（第 1 节），5 项按脚本重新看，全部拿回。效果本身仍然简单，研究时**只看可视化和系统**，回血 / 加速的数值照样按 DESIGN-LIST 设计。

| 传奇 | 槽位 | 能力 | 脚本 | 可视化 | 可复用的系统 | 依据 |
|---|---|---|---|---|---|---|
| Lifeline | 战术 | D.O.C. Heal Drone | `mp_ability_lifeline_follow_medic` | 无人机飞行姿态（前倾最大 20°、侧倾最大 17°）、治疗绳（10 节点，接上 / 收回各 0.25 s）、瞬移拖尾 | **指派目标**（45 m、50° 锥内的队友，没有就跟自己）；**跟随运动**（目标点在头顶 70 / 蹲下 46，速度 = 距离×3，远时 +40，叠加目标速度×0.5，上限约目标速度 1.6 倍，每帧按 8·dt 逼近）；**断线瞬移**（断视线 >1 s 或绳断就瞬移回来）。回血每秒 8、持续 20 s | `FollowMedic_MoveThread` 第 801–870 行（分叉会话核过）。可能是 SDK 社区重写的服务端代码，要实测 |
| Conduit | 战术 | Radiant Transfer | `mp_ability_conduit_arc_flash` | 光束特效、锁定 HUD | **指派目标**：`TargetingThread`（第 430 行）、`ScoreTarget`、`IsValidTacTarget`，没目标就给自己（`DoSelfCast`）；临时护盾分阶段回复 | 函数名，待读细节 |
| Revenant | 大招 | Forged Shadows 暗影护甲 | `mp_ability_shadow_form` | 暗影皮肤、包住玩家的护盾壳、受击 / 破碎特效、屏幕调色 | 护盾实体跟随玩家、处理黏附物（`ShadowShield_TrackStickyEnt_Thread`）、击杀回复和计时延长 | 函数名，待读细节 |
| Bloodhound | 大招 | Beast of the Hunt 狩猎 | `mp_ability_hunt_mode` | 全屏调色（`HuntMode_UpdatePlayerScreenColorCorrection`）、身体特效、敌人高亮 | 跟随玩家的扫描触发器（`SonarTrigger_*`、`TriggerTrackOwner`），击杀延长时间 | 函数名，待读细节 |
| Ballistic | 大招 | Tempest 风暴 | `mp_ability_portable_auto_loader`（已核对：`IsBallisticUltActive`、`GetUpgradedTempestRangeMultiplier`） | 屏幕特效、背包特效、光束 | 范围内给队友上 buff（`AutoLoader_ApplyTeammateBuff_Think`）；第三把武器 Sling 变金（`ConvertSlingWeaponToGold`） | 和武器的 Sling 一起，放到武器阶段看 |

Mad Maggie 破坏球留下的加速片：效果是简单加速，但属于"一路留下东西"的表现，研究破坏球时一起记。

### 2.3 原"不要"按三样重看（10-31）

#### 2.3a 拿回：9 项

| 传奇 | 能力 | 脚本 | 拿回的理由（效果 / 可视化 / 系统） |
|---|---|---|---|
| Catalyst | 大招 Dark Veil 黑幕 | `mp_weapon_ferro_wall` | **效果**：穿过的敌人减速 + 致盲（`AttemptToApplyDarkStatus(…, applyMoveSlow)` 第 1647 行），算控制；**可视化**：墙由一根根柱子长出来（`CreateFerroWallPillar`）、穿过时屏幕特效 |
| Mirage | 战术 Psyche Out 分身 | `mp_ability_holopilot` | **系统**：分身的移动 AI、仇恨优先级（`GetThreatPriorityForHolopilot` 第 567 行）、分身被打的结算。10-29 已经列进 HSD（D-59..D-64），APEX-REPORT 2.5 研究过 |
| Mirage | 大招 Life of the Party | `mp_ability_mirage_ultimate`（211 行，调用 holopilot） | 和分身一起，"一次放多个"的升级分支 |
| Bloodhound | 战术 Eye of the Allfather 扫描 | `mp_ability_area_sonar_scan` | **可视化**：锥形扫描波、屏幕效果、高亮时长；**系统**：锥形范围查询。10-29 已列入，APEX-REPORT 2.4 |
| Seer | 战术 Focus of Attention | `mp_ability_sonic_blast` | **效果**：可选伤害（`GetSonicBlastDoesDamage` 第 1035 行）、延迟减速、打断；**可视化**：管状冲击波 |
| Seer | 被动 Heart Seeker 心跳 | `mp_ability_heartbeat_sensor` | **可视化**：心跳雷达波形 HUD，可做 HSD 的感应类 HUD 参考。优先级低 |
| Crypto | 战术 Surveillance Drone | `mp_ability_crypto_drone`（3659 行） | **系统**：可操控的飞行无人机（`CryptoDrone_CreateFlyingCameraVehicle`）、视角切换、召回；EMP 大招也依赖它 |
| Lifeline | 大招 Care Package | `mp_ability_care_package` + `sh_care_package.nut` | **系统**：空投舱从天上落下。PvE 里可以拿来刷敌人或刷补给；物资生成部分不要 |
| Revenant | 旧大招 Death Totem | `mp_ability_revenant_death_totem` | **系统**：标记位置 → 死后 / 主动召回传送、召回后无敌帧（`DeathTotem_RecallPlayer` 第 684 行）。可参考做检查点式回溯。S21 已不是 Revenant 的能力，但脚本在 |

另外 Revenant 旧战术 Silence（`mp_ability_silence`）：有伤害（`Hack_HandleSilenceDamage`）+ 黏附投射物 + 区域，**效果**一项就够，拿回，优先级低（S21 已不是 Revenant 的能力）。

#### 2.3b 仍然不要：6 项（Seer Exhibit 10-31 已找到脚本并拿回）

| 传奇 | 能力 | 三样都不够的原因 |
|---|---|---|
| Bangalore | 战术 Smoke Launcher 烟雾 | 效果是挡视线（用户点名不要）；烟雾就是普通粒子 + 触发区，表现和系统都普通。烟里高亮敌人的被动可在扫描里参考 |
| Caustic | 被动 Nox Vision | 只是毒气里的敌人高亮，扫描那几项已经覆盖 |
| Crypto | 被动 Neurolink | 只是无人机范围内报敌，和无人机一起看即可，不单列 |
| Loba | 大招 Black Market | 物资拾取 UI，PvE 用不上 |
| Newcastle | 被动 Retrieve the Wounded | 拖倒地队友，单人 PvE 没有倒地队友 |
| Gibraltar / Lifeline 等 | 复活相关被动 | 团队复活 |
| ~~Seer~~ | ~~大招 Exhibit~~ | **10-31 批次 E 找到脚本 `mp_ability_echo_locator`**，按三样有可视化和系统价值（区域 + 行为条件侦测），已拿回，记录见 `seer-exhibit/SYSTEM.md` |

### 2.4 移动线已做 / 已搁置（不重复）

Octane 兴奋剂和跳板、Wraith 虚空和传送门、Pathfinder 钩爪和滑索、Valkyrie 喷气和升空、Ash 相位突破、Horizon 重力电梯、Revenant 暗影突袭、Vantage 回声、Mad Maggie 加速片部分。Loba 手环、Alter 两个技能已搁置（见 `SHELVED-ABILITIES.md`）。

### 2.5 不属于传奇的能力脚本

`mp_ability_boost_kit_*`、`copycat_kit_*`、`gun_turret_v2`、`mobile_respawn_beacon`、`second_chance_token`、`void_ring` 等是模式道具或活动内容，放到**道具阶段**再过。

## 3. 和已有决定的冲突（要用户定）

TF2 扩展清单（D-59..D-64，10-29）已经把下面两项列进 HSD，而且 APEX-REPORT 2.4 / 2.5 / 2.6 已经研究过：

- **扫描 / 透视**（Bloodhound、Seer、Crypto）
- **全息分身**（Mirage，含"一次放多个"和"多次释放"两个升级分支）

按最初的 PvE 标准它们会落到"不要"。**按 10-31 改定的三样标准，两者都有可视化或系统价值，已拿回（2.3a），和 10-29 的决定一致，冲突消失。** 用户确认第 1 节时一并确认即可。

## 4. 下一步

1. 用户确认第 1 节的三样标准、第 2.2 节的待定项。
2. ~~核对 Vantage / Ballistic 大招的脚本~~（10-31 已核对：Vantage = `mp_ability_sniper_ult`，Ballistic Tempest = `mp_ability_portable_auto_loader`）。Seer 大招 Exhibit 的脚本还没找到。
3. "参考"类（2.2b、2.3a）读细节时只记可视化和系统，并实测确认（SDK 可能重写过服务端代码）。
4. 对"保留"的能力开始研究：规则、时序、范围、伤害和控制效果，按 APEX-HANDOFF 的写法（先写 HSD 怎么做，再写依据）。
5. 然后进入道具阶段（手雷三种已有 APEX-REPORT 2.1–2.3）。
