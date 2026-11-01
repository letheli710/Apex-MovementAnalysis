# 攻击研究 · 道具和武器阶段 R5 实测（IP2-RUNTIME）

会话 `ip2-r5-runtime`，2026-11-01。本地 R5Flowstate（S21 客户端 + S3 dedi + SDK 混合构建），火力训练场 `mp_rr_canyonlands_staging_mu1`，离线。工具在 [ip2-runtime/](ip2-runtime/)；原始记录（每次运行一个 `runs/<时间>_<名字>.txt`，共 165 个）在私有仓库 `HSD-RawData` 的 `apex/research/combat/ip2-runtime/runs/`（D-76）。

**版本标注**：除非另写，每个"实测"值都是 **[R5 本地混合构建]**。**期望**来自 I1 / W1 静态记录（S21 数据字段或脚本）。**S21 正版、Unity 改前都没有在这次测**；写到 Unity 的地方只是引用已有文档。标 **SDK** 的行，执行这个机制的是 SDK 重写，不是原版代码，实测说明不了 S21 正版怎样。

**状态**：**已测**、**部分**（测到一部分，缺口写明）、**没测**（写原因）。样本少的都写了次数。

## 结论先说：改变 HSD 实现的结果

| # | 结果 | 影响 |
|---|---|---|
| 1 | **消耗品读条有减速**：`move_slow` 0.4，走路 195 → 101.7 u/s。记录写的"没有移动减速"错了（`mp_ability_consumable.nut:749`） | `ChannelUse` 要带减速，别按走路速度做 |
| 2 | **爆炸衰减按碰撞盒表面算**，不是中心距（dummie 差约 16 u，prowler 更大） | 按中心距算会比 R5 低 5–8 点 |
| 3 | **燃烧每层 25，火烧约 8 s，火灭后层继续打完** | APEX-REPORT 的 24、I-BURN-STACK 的 25–28 和 7.5 s 都要改 |
| 4 | **点射周期 = (发数 − 1) / 射速 + `burst_fire_delay`**。Hemlok 0.38 s，Prowler 0.42 s | W-FIRE-RELOAD 的 `n / 射速 + delay`（0.444、0.468）多算一发 |
| 5 | **爆头倍数走 `damage_headshot_scale`**，`critical_hit_damage_scale` 不起作用 | W-DAMAGE 的问题定了 |
| 6 | **后坐图案：第 1 列 yaw、第 2 列 pitch（负 = 上），单位度，逐发累加，子弹跟着走，`EyeAngles` 不变** | `RecoilPattern` 可以直接用表 |
| 7 | **霰弹图案固定、没有随机**，EVA 最外 1.72°，和公式一致 | 图案表可以直接搬 |
| 8 | **本地 NPC 不提前绕火**（各 1 次）；`IsMechanical` 对 dummie、prowler 都是 0 | 做不做"AI 躲火"是设计决定，R5 本地没有参考行为 |
| 9 | **30-30 蓄力 ×1.4 本地没生效**（SDK 差异，推断成立） | 要不要做这个 ×1.4，取决于 W1 第 6.2 条（按 S21 字段还是本地），留给用户 |

## 方法上的新发现

- **真实 `+attack` 能开枪**：`GiveWeapon` 给的枪弹匣是 0，所以之前"按键不触发"至少有这个原因。`SetWeaponPrimaryClipCount` 填满后，`ClientCommand( "+attack" )` 能连射、打中、扣弹。手雷的真实投掷这次**没有重测**。
- **弹道子弹不是脚本实体**：`GetProjectileArrayEx` 看不到，飞行轨迹读不到，只能看命中点。
- **服务端循环大约 0.05–0.1 s 一帧**，算射速要用客户端循环（`snippets/clog.txt`）。
- 其他工具见第 4 节。

## 1. 道具（I1 第 2 节）

| # | 项 | 状态 | 实测 | 期望 | 差 / 说明 | 记录 |
|---|---|---|---|---|---|---|
| 1 | 破片打 dummie | 已测 | 60、120 u：100；140 u：99；182.5 u：82；237 u：56；290 u：34；358 u：1 | 125–350 u 线性 100 → 0（140 u = 93，237 u = 50，290 u = 27） | 高 5–8 点，相当于距离少约 16 u。推断是算到碰撞盒表面 | frag-grenade |
| 1 | 破片打 prowler | 已测 | 59、124、139 u：100；175 u：92；235 u：70；286 u：42；316 u：34 | 同上 | prowler 碰撞盒更大，差得更多。这轮 NPC 位置有抖动，距离取实测 | frag-grenade |
| 1 | 电弧星打 NPC | 已测 | dummie 33、56 u：75；101 u：71；156 u：57；251 u：31；292 u：19；303 u：17 | 72–350 u 线性 75 → 0 | 同样高一点 | arc-star |
| 1 | 直接砸中 | 部分 | 电弧星粘到 prowler：另加 10（`type = 0`），2 次 | `damage_near_value`，记录写推断 | 电弧星确认。**破片没测** | arc-star、frag-grenade |
| 1 | `IsMechanical` | 已测 | dummie 0，prowler 0 | 决定 ×0.5、×2.05 走不走 | **这两个分支本地走不到，公式没验证**（幽灵刷不了） | frag、arc-star |
| 1 | 被电（dummie） | 已测 | 138.5 → 69.5 u/s（×0.50），`move_slow` 0.498，转身 0.698；满约 1.7 s，再约 1 s 淡到 0（距爆点约 60 u） | 减速 0.5、转身 0.7，时长 0.2–2.5 s + 淡出 1 s | 一致 | arc-star、B-electric-emp |
| 1 | 被电（prowler） | 已测 | `move_slow` 读回 0；放受击动画，原地停约 1.6 s，之后回到 346 u/s | 记录没定 | prowler 走动画，不走减速。第二颗在 3.6 s 后同样让它停（1 次）。这个间隔超过 3 s，**免疫问题没测到** | arc-star |
| 2 | 每层总伤 | 已测 | **25**，跳序 4,4,4,4,4,4,1，约 2.8 s，重复 5 次 | 25 或 28 | **定为 25**。服务端帧 0.05 s | I-BURN-STACK、thermite |
| 2 | 满层 DPS | 已测 | 5.1–8.0 s 共 104 点，约 36 DPS；dummie 和 prowler 总伤都是 275（71 跳） | 4 × 25 / 2.8 = 35.7 | 一致 | I-BURN-STACK |
| 2 | 火持续 | 已测 | 点燃后 7.9 s 进火起火，8.2 s 进火 0 伤害 | 静态推断约 7.5 s | **约 8 s，推断错** | thermite |
| 2 | 火灭后的层 | 已测 | 继续打完：7.9 s 进火，打到 10.7 s；伤害回调里 inflictor 全程有效 | 未知 | 定了 | I-BURN-STACK |
| 3 | 进化护甲 | 部分 | 上限 50 / 75 / 100 / 125；升级**不回盾**（盾始终 10）；溢出带到下一级（240 = 300 − 60，440 = 750 − 310）；过量不算（血 20 打 90 只给 20 点）；1:1 | 同 | 一致，但**一次跨两级没测到**。用脚本 `TakeDamage`（攻击者 = 玩家）。直接发装备时进度是 0，第一次伤害立刻升一级，这是测试手法造成的 | evo-armor |
| 3 | Upgrade Core | 部分 | `passive_upgrade_core_enabled` 在这个 playlist 没写；玩家出生穿 `armor_core_pickup_lv3` | 代码默认 true | 推断开着 | evo-armor |
| 3 | 非训练场 ×0.25 | 没测 | | 0.25 | 要换 playlist 重启，这次没做 | evo-armor |
| 4 | 读条时长 | 已测 | 小电池 2.5，注射器 4.0，大电池 5.0，医疗包 8.0，凤凰 10.0 s（各 1 次；开火那一刻生效并扣物品） | raise 1.0 + charge | **含 raise**，0 差 | consumables |
| 4 | 读条移动 | 已测 | `move_slow` **0.400**，走 195 → 101.7 u/s（×0.52）；不能冲刺 | 记录写"没有移动减速" | **记录错**。×0.6 之外还多约 ×0.85，来源没查。W2 的公式单独算不出这个值 | consumables |
| 4 | 打断和取消 | 已测 | 脚本伤害不断；发跳键不断（1 次，没确认跳起来）；`+attack`、`Consumable_CancelHeal` 都取消，不扣物品 | 同 | 一致 | consumables |
| 5 | AI 危险区 | 部分 | prowler 直接穿火，受 7 跳；dummie 也走进火里，受伤后才横跑约 150 u（对照 0 伤害、直线）。各 1 次 | 记录说"要实测" | **都不提前绕** | thermite 3.4 |
| 6 | 飞刀 | 部分 | 身 100（989 u，987 u）；头 260（973 u）；989 u 落差约 11 u。3000 u 打 5 次没中 | 100 / 300；上抬 2° + 重力 1200 算出净落 9 u | 头 260 是 dummie 白头盔（见第 7 项），不是倍数错。`headshot_distance` 没测到 | throwing-knife |
| 7 | 头盔 | 部分 | dummie 白头盔：飞刀 100 + 0.8 × 200 = 260；Kraber、Charge Rifle、30-30、R-301 都符合 0.8 | 0.8 | 一致。**只验证了 dummie 的白头盔**（`_ai_dummie.gnut`，SDK 改过）；玩家头盔要能爆头的攻击者，本地没有 | helmet |
| 8 | Nessie | 已测 | `Nessie_SpawnNPC` 报 `Invalid setting 'npc_nessie'`，**没卡死 dedi** | 可能卡死 | 本地刷不出。AI 设置文件缺失 | boost-nessie-summon |

## 2. 武器（W1 第 4 节）

| # | 项 | 状态 | 实测 | 期望 | 差 / 说明 | 记录 |
|---|---|---|---|---|---|---|
| 0 | SDK 版本 | 部分 | `server.dll` 的 429 个 `bridge_` / `sdk_` 名字全在源码里；源码有 53 个 ConVar 不在已装的 DLL 里（`portal_`、`halo_vehicle_`、`navmesh_draw_`、`sceneview_` 等）。武器相关开关都在 | 同版 | **不是同一版**，推断源码（10077bb）更新。字符串证据 | W-S3-FIELD-CHECK |
| 1 | 弹道 | 部分 | 读回：R-301 v 29000 g 1.3；R-99 19000 / 1.2；Kraber 29500 / 1.4。落差只有少数命中：R-99 1993 u 6.4（1 发）；Kraber 2000 u 1.8（1 发）；Charge Rifle 7900 u 25.6（1 发）；飞刀见上 | `0.5 g (d/v)²`：5.0、2.4、23.3 | 大体对，**但样本太少**：开镜扩散 0.35° 在 2000 u 就有 ±12 u。5000 u 全部没中。积分方式没定下来 | W-BALLISTICS |
| 2 | 后坐图案 | 部分 | R-301 开镜 150 u，命中点累计升高（u）：1.1, 3.3, 4.5, 6.1, 7.7, 8.1, 8.5（第二次）；左偏 0.4–2.2 | `rspn101_2` 第 2 列累加换算：1.4, 3.2, 4.4, 5.9, 7.0, 7.7, 8.2 | 差不超过 0.7 u。**第 1 列 yaw、第 2 列 pitch，度，逐发累加**。三次之间差约 1 u，推断第 3、4 列是随机范围（没单独验证）。**回落没测** | W-SPREAD-RECOIL |
| 3 | 扩散 | 部分 | `GetAttackSpreadAngle` 读回。R-301：腰射站 3.2 → 5.0；走 5.2 → 8.6；跳 3.4 → 7.2；开镜 0.35。每发 +0.2 到 +0.4 | 单位是度（确认） | 跑、回落时间**没测**。开镜连射时读回 0，原因没查，别当成"开镜没有扩散" | W-SPREAD-RECOIL |
| 4 | 伤害 | 已测 | R-301 身 15、头 19、腿 11；Kraber 身 150、头 198；Charge Rifle 300–3000 u 身 75、头 123，5400 u 腿 77（1 发），7900 u 身 99（1 发） | R-301 15 / 19.5 / 11.25；Charge Rifle 75 → 99 | 头 = 基础 + 0.8 ×（基础 × `damage_headshot_scale` − 基础）。小数截断。5400 u 按线性 × 腿 0.9 = 78，实测 77 | W-DAMAGE |
| 5 | 30-30 蓄力 **SDK** | 已测 | 开镜身 43、头 57；腰射头 57 | S21 60.2；推断本地 43 | **没有 ×1.4**，推断成立。开镜 1.6 s 后开枪；命中开镜 2 发（身、头各 1）、腰射 2 发（都是头），样本少 | charge-spinup |
| 6 | 点射 **SDK** | 已测 | Hemlok 组内 0.065 s，组间最短 0.25 s（按住只打一组，要重按）；Prowler 组内 0.049 s，组间 0.228 s，按住连发 | 字段 0.25 / 0.23；0.444、0.468 | **周期 = (n − 1) / 射速 + delay**，Hemlok 0.38、Prowler 0.42。关 `bridge_burst_fire_seed` 后仍是 3 发一组，只测了 0.5 s 间隔连点，**对比不算充分** | W-FIRE-RELOAD |
| 7 | Nemesis 热量 **SDK** | 已测 | 每发 +0.04167；组间 0.30 → 0.19 s；换弹不清热量；涡轮序列几乎相同（0.294 → 0.188） | 0.31 → 0.19；涡轮推断不变 | 一致。**涡轮确实不改** | burst-fire、hopups |
| 8 | Energize **SDK** | 部分 | 按 `+reload`、`+useandreload`、`+use` 都没触发（状态 0，物品不变）；`ForceEnergizeState` 进状态 2，0.1 s 内回 0，扣 1 个铝热。Rampage 普通射速 0.2 s（5/s） | 3.7 s 动画，5 → 6.5/s | **能力本身没测到**，按键入口没找到。Sentinel 同样 | charge-spinup、sniper-marksman |
| 9 | L-STAR 过热 **SDK** | 已测 | 约 3.9 s 满（按下后 2.3 s）；开关 1：回到 0 在 7.17 s，锁约 3.25 s；开关 0：约 1.3 s 就重新升 | 约 3.69 s | 短约 0.44 s。**开关确实决定锁定** | charge-spinup |
| 10 | Devotion | 已测 | 0.204 → 0.065 s，约 15 发到顶（15.4/s）；涡轮从 0.155 起，约 9 发到顶 | 曲线形状待定 | 序列在原始记录 | charge-spinup |
| 10 | Havoc | 已测 | 按下到第一发 0.42 s；涡轮 0.02 s；0.09 s 一发 | 0.42 / 0.01 | 一致 | charge-spinup |
| 10 | Bocek | 部分 | 按 0.3 s：47；0.6、1.0 s：60（各 1 发）；1.8 s 没中 | | **弹速（26891 还是 27000）没测到**，箭读不到速度 | charge-spinup |
| 11 | 霰弹 | 部分 | EVA 150 u，3 枪位置相同：(±2.9, ±2.9)、(0, ±4.5)、(±1.4, 0)，最外 4.5 u = **1.72°**，7 伤。Mastiff 开镜 300 u 横排最外 7.6 u = 1.45°，19 伤。Peacekeeper 11 伤。Triple Take 22 伤。Mozambique 150 u 三角，17 伤 | EVA 1.72°；Mastiff 开镜 1.50° | EVA 0 差，**没有随机**。Mastiff −0.05°。Peacekeeper 收拢档位**没测**。300 u 时图案整体低约 11 u，原因没查（悬空假人的命中盒可能截掉上半） | shotgun-blast |
| 12 | Sheila | 部分 | 能给（弹匣 **150**）；切到手上开火后**客户端退出**，重复 2 次 | 173 发 | 扩散收紧**测不了**。150 和 173 的差没查 | rampart-sheila-weapon |
| 13 | NPC 武器 | 已测 | `npc_dummie_combat` 拿 `mp_weapon_rspn101`，弹匣 0 / 21；`npc_dummie_shotgun`、`_smg` 不是有效设置（**这个试法把 host 弄关了**）。开火测不了（W2） | | | npc-weapons |
| 14 | 近战 | 部分 | 拳 30；中心距 40、60、80 u 命中，110 u 不中 | 40 还是 60 | 符合 60 + 碰撞盒。**击退没测**（假人被按住）。**Titan Sword 没测**，只确认能给 | melee |
| 15 | Boosted Loader | 部分 | `hemlok_crate` 6 发时换弹：弹匣 21，约 1.4 s 填上，2.0 s 结束，1 次 | 21 + 9，1.75 s | **没看到 +9**。普通 Hemlok 用同样按法 2 次都没进换弹，所以对比不成立 | hopups |
| 15 | Kinetic Loader | 部分 | `lmg_crate` 冲刺滑铲一次，弹匣没涨，1 次 | 滑铲上弹 | 不确定是真不工作，还是滑铲没滑出来（没读状态） | hopups |
| 15 | Shatter | 已测 | `3030_crate` 腰射身 51、开镜头 67，每枪 1 个命中 | 腰射霰弹 | **腰射没有变霰弹**（3 枪） | hopups |
| 15 | 休眠 P2020 | 没测 | `dormant_hopup_double_tap` 报 mod 不存在 | | P2020 的 mod 是 `dormant_hopup_unshielded_dmg`，发现时游戏已关 | hopups |
| 16 | 备弹回充 | 已测 | Havoc 备弹约 1 发/s（1.0 s 一发，从 10 涨到 20），不开枪也涨 | 约 1 发/s | 一致。**是不是社区加的没判定** | W-FIRE-RELOAD、ammo |
| 17 | 加载 | 已测 | 不能：`raygun`、`buster_rifle`、`defender_sustained`、`rspn101_og`。能：`rspn101_crate`、`hemlok_crate`、`lmg_crate`、`3030_crate`、`semipistol`、`mounted_turret_weapon`、`titan_sword`、`melee_survival`、`nemesis`、`car` | | **Buster、Ray Gun 本地测不了**。`mounted_turret_placeable`、`sniper_ult` 是 offhand，要另外给。双持金色 P2020 没试 | special-energy、weapon-tiers |
| 18 | C.A.R. | 已测 | 备弹 0 打空：弹匣 0，**不自动换弹种**，1 次 | 回调没绑 | 符合静态 | auto-ballistic |
| 18 | Sling | 没测 | | | 要 Ballistic 套装和金色切换，排在最后，时间没留 | ballistic-sling |
| 19 | Vantage | 部分 | 读回 v 34000、g 1；弹匣 240，每发 −40，+1/s；最短约 1.7 s 一发。1000、3000、7500 u **都没打中** | `.txt` 没写重力 | **下坠没测到**。重力读回 1，说明走默认值 | vantage-sniper-weapon |

## 3. 给记录第 5 节的回填

#89、#90 还没合并，这些文件不在这个分支上，所以没有改记录本身。合并后按第 1、2 节回填，其中要**改正文**的是：

| 文件 | 改什么 |
|---|---|
| `items/consumables/SYSTEM.md` 第 0、1 节 | 删"没有移动减速"，写 `move_slow` 0.4（`nut:749`）和实测 101.7 u/s。filter 的更正 #4 也要撤回减速那部分 |
| `items/_shared/I-BURN-STACK.md` | 每层 25；火灭后层继续 |
| `items/thermite-grenade/SYSTEM.md`、I1 第 4 节 | 火约 8 s，不是 7.5 s |
| `weapons/_shared/W-FIRE-RELOAD.md` 第 44、45 行 | 周期公式，0.38、0.42 |
| `weapons/_shared/W-SPREAD-RECOIL.md` | 四列前两列的含义和单位 |
| `weapons/_shared/W-S3-FIELD-CHECK.md` | 第 0 项结论：不是同一版 |

差别确定后，`R5-DIFF-ARCHIVE.md` 的行也等合并后再加。

## 4. 工具和教训

- `ip2-runtime/run.py`：服务端片段 + 客户端按键时间表，`{{k}}` 替换。`batch.py` + `cases/*.txt`：批量跑枪，每项一行汇总。`relaunch.sh`：重启。最后两批是临时脚本，没有留，命令记在原始记录每个文件的第一行。片段在 `snippets/`，`gun.nut` 是通用枪测试，`clog.txt` 是客户端高频记录。
- **客户端脚本的运行时错误也会让 host 关掉**。这次重启 5 次：3 次是片段或试探的错（错的枚举名 `PHOENIX_KIT`、在客户端试不存在的方法、无效的 AI 设置名），2 次是 Sheila 关客户端。重启约 25 s 到可响应。
- `eye` 高度沿 yaw 0 有 20000 u 的开阔通道（`los.nut`），假人每帧 `SetOrigin` 就能悬空当靶。悬空假人的命中盒位置不完全等于站立时。
- 没有读后坐的脚本接口，`EyeAngles`、`CameraAngles` 开枪时都不变。靠近距离命中点反推。

## 5. 没做的

Sling；非训练场进化倍率；破片直接砸中；Peacekeeper 收拢；Titan Sword 招式；近战击退；休眠解锁（mod 名用错）；真实投掷（仰角、继承速度，这次发现之后该重测）；长距离弹道的足够样本。
