# I1 · 道具阶段静态记录总结

会话 `i1-records`，2026-11-01。输入 [I0-ITEM-FILTER](../I0-ITEM-FILTER.md)。全部静态，没进游戏。第 2 节是**给 R5 实测那一步的提议**，还没测。

结论先说：

- 16 份记录写完。**9 份能写完整流程**（破片、电弧星、铝热剂、飞刀、Revenant 手雷、进化护甲、头盔、消耗品、重投气球）。**其余 7 份道具本身没有效果代码**（生物诱饵、5 个增益包、炮台 v2），只记了字段和意图，没有编流程；其中吸血和召唤 Nessie 在别的脚本里有同类系统，记了那些。
- filter 有 **8 处事实错误**，已在 I0 里改并标"更正"。去留结果一项没动。
- 需要用户定的：生物诱饵和两个只剩壳的参考项还留不留（第 3 节）。

## 1. 每份记录的发现

| 道具 | 记录 | 本地代码 | 主要发现 |
|---|---|---|---|
| 破片手雷 | [frag-grenade](frag-grenade/SYSTEM.md) | 完整（公共代码） | 转写 APEX 2.1。补：NPC 专用伤害字段；`IsMechanical` 敌人 ×0.5 |
| 电弧星 | [arc-star](arc-star/SYSTEM.md) | 完整 | 补 NPC 分支。机械 NPC ×2.05 + 定时减速。推断没有 3 s 击晕免疫。服务端和客户端碰撞是两份，有差别 |
| 铝热剂 | [thermite-grenade](thermite-grenade/SYSTEM.md) | 完整 | **更正 APEX 三处**（第 4 节）。每个火点有 AI 危险区 |
| 飞刀 | [throwing-knife](throwing-knife/SYSTEM.md) | 完整 | **不是近战**。主武器槽，3700 u/s，100，爆头 ×3，不继承玩家速度 |
| Revenant 手雷 | [rev-shell](rev-shell/SYSTEM.md) | 完整 | **只锁玩家**，PvE 原样不能用。面包屑追踪部件值得拿：远 660 u/s、近 240 u/s。隐藏代理让飞行物可被打（实际 25 血） |
| 生物诱饵 | [creature-bait](creature-bait/SYSTEM.md) | **空** | 两个空函数，前 113 行被抹，没有 `.txt`。没有引怪 |
| 进化护甲 | [evo-armor](evo-armor/SYSTEM.md) | 完整 | 门槛 100 / 200 / 300 / 750；倒计时进度；溢出递归。打 NPC 默认 ×0.25，满级要 5400 实际伤害。按代码升级不回盾 |
| 头盔 | [helmet](helmet/SYSTEM.md) | 完整 | 只削爆头多出的部分。系数 0.8 / 0.5 / 0.35 / 0.35。tier 5 没 case，不减 |
| 消耗品 | [consumables](consumables/SYSTEM.md) | 完整 | 读条 = 武器蓄力。开火时才生效和扣费，取消不扣。**没有移动减速，被打不打断** |
| 相位回溯 | [boost-phase-rewind](boost-phase-rewind/SYSTEM.md) | **壳 + 桩** | 对照用 TF2 W3 第 1 节和 Death Totem |
| 吸血 | [boost-lifesteal](boost-lifesteal/SYSTEM.md) | 增益包是壳；**系统完整** | `_lifesteal.nut`，结算后钩子，先血后盾 |
| 地图透视 | [boost-map-hack](boost-map-hack/SYSTEM.md) | **壳** | 只有显示端。方案用 APEX 2.6 |
| 召唤 Nessie | [boost-nessie-summon](boost-nessie-summon/SYSTEM.md) | 增益包是壳；**同类系统完整** | 真实召唤在红色金马 hop-up 和 `sh_player_pet.nut` |
| 范围治疗 | [boost-heal-radius](boost-heal-radius/SYSTEM.md) | **壳** | 范围圈在情人节模式，一个共用粒子 |
| 重投气球 | [redeploy-balloon](redeploy-balloon/SYSTEM.md) | 完整 | **不发射人**：部署垂直滑索 + 到顶转跳伞 |
| 炮台 v2 | [gun-turret-v2](gun-turret-v2/SYSTEM.md) | **壳 + 桩** | 不在 loot 表。对照用 Sheila 和 TF2 |

公共部件（`_shared/`）：[I-THROW-TOSS](_shared/I-THROW-TOSS.md)、[I-BURN-STACK](_shared/I-BURN-STACK.md)、[I-DEALT-DAMAGE-HOOK](_shared/I-DEALT-DAMAGE-HOOK.md)、[I-STUB-ITEMS](_shared/I-STUB-ITEMS.md)。

没有重复写的：状态效果 [E-STATUS-EFFECT](../_shared/E-STATUS-EFFECT.md)、减速 [B-move-slow](../_shared/B-move-slow.md)、电击 [B-electric-emp](../_shared/B-electric-emp.md)、放置 [B-placement](../_shared/B-placement.md) / [C-PLACEABLE-DEPLOYABLE](../_shared/C-PLACEABLE-DEPLOYABLE.md)、伤害修正 [C-DAMAGE-MODIFIERS](../_shared/C-DAMAGE-MODIFIERS.md)。

### 对 HSD 最值得拿的部件

| 部件 | 在哪 | 给什么用 |
|---|---|---|
| "造成伤害"结算后钩子 | I-DEALT-DAMAGE-HOOK | 进化、吸血、连击 |
| 进化点数 + 倒计时 + 溢出 | evo-armor 3.2 | PvE 成长（倍率要重定） |
| 读条武器 + 取消不扣费 | consumables 3.2 | 所有"按住使用" |
| 面包屑追踪 | rev-shell 3.2.1 | 追踪导弹、追踪手雷 |
| 爆头加成系数 | helmet 3.2 | 精英敌人头部护甲 |
| AI 危险区 | thermite 3.4 | 区域逼走敌人（要实测） |
| 寿命血条 + 有人在用不消失 | redeploy-balloon 3.2.3 | 放置物 |

## 2. 提议的 R5 实测（给 runtime 那一步）

都没做。按价值排序。W2 已确认 `npc_dummie`、`npc_prowler` 能刷会追但不开火，`spectre` 一刷 dedi 就卡死。

| # | 测什么 | 怎么测 | 判定什么 | 记录 |
|---|---|---|---|---|
| 1 | **手雷对 NPC** | 脚本发射破片、电弧星、铝热剂打 `npc_dummie` 和 `npc_prowler`，各放内半径内、外半径中点 | 伤害和衰减曲线；`IsMechanical` 取值（×0.5、×2.05 走不走）；被电的速度和时长 | frag、arc 第 5 节 |
| 2 | **燃烧层** | 把 dummy 放进火点 1 帧移走读总伤；站满 10 s 记曲线；记录帧率 | 每层 25 还是 28；满层 DPS；火烧 7.5 还是 8 s；最后一刻入火后层还打不打 | I-BURN-STACK、thermite |
| 3 | **进化护甲升级** | Firing Range（NPC ×1）穿 `armor_pickup_lv1_evolving`，先掉盾再打够 100 点，读盾量和上限；一次大伤害跨级；打非 Firing Range NPC 看 ×0.25 | 升级回不回盾；溢出；过量伤害算不算；`passive_upgrade_core_enabled` 实际值 | evo-armor |
| 4 | **治疗读条和打断** | `TryTriggerConsumableUse` 每种物品一次，记 `isHealing` 到加血的时间；读条中读速度；读条中脚本 `TakeDamage` | 总时长含不含 raise 1.0 s；是否走路速度；被打断不断（预期不断）；物品扣了没 | consumables |
| 5 | AI 危险区 | `npc_prowler` 追玩家，中间放一道火 | 绕不绕；决定 HSD 要不要做 | thermite 3.4 |
| 6 | 飞刀伤害 | 脚本发射打 dummy 身、头，距离 1000 / 3000 | 100 / 300；`headshot_distance` | throwing-knife |
| 7 | 头盔公式 | Firing Range 假人头盔选项，打爆头 | 公式；优先级低 | helmet |
| 8 | Nessie 能不能刷（**小心**） | `Nessie_SpawnNPC`，**先存好工作**，可能像 spectre 那样卡死 dedi | 和武器阶段的金马一起也行 | boost-nessie-summon |

**测不了的**：生物诱饵、相位回溯、地图透视、范围治疗、炮台 v2、增益包吸血和召唤（效果代码不存在）。

**前提问题**：真实按键投掷（`+attack`）在 APEX 那次没触发，1–6 都用脚本发射绕开。仰角系数和继承速度还是要它才能测。

## 3. 对 filter 的更正

### 3.1 事实错误，已在 I0-ITEM-FILTER.md 改

| # | 项 | 原来 | 实际 | 证据 |
|---|---|---|---|---|
| 1 | 铝热剂 | "沿地面走线和 Fuse 火焰环共用" | 代码不共用 | `mp_weapon_thermite_grenade.nut:381`、`mp_weapon_mortar_ring_missile.nut:446` |
| 2 | 飞刀 | "投掷类近战伤害" | 直射投掷物，主武器 | `.txt:10-12`、`:64` |
| 3 | 进化护甲 | 在 `cl_survival_loot.nut` | 在 `sh_survival_loot.gnut` | `:6492-6868` |
| 4 | 消耗品 | "移动减速 + 被打断" | 不能冲刺、不能攀爬；只有按键取消 | `.txt:48`、`nut:660`、`cl_survival_loot.nut:114-121` |
| 5 | 吸血 | "伤害修正链的 hook"；只有 .txt | 结算后钩子；系统脚本完整 | `_lifesteal.nut`、`_gamemode_survival.nut:3632` |
| 6 | 召唤 Nessie | 只有 .txt | 同类系统有脚本 | `hopup_golden_horse.nut:1556-1590` |
| 7 | 重投气球 | "把人发射到高空" | 滑索 + 跳伞 | `mp_ability_redeploy_balloon.nut:838`、`sh_survival_freefall.gnut:590` |
| 8 | 炮台 v2 | 没标缺口 | 只有 .txt，回调是桩，不在 loot 表 | `_missing_callback_stubs.gnut:562`、`:1167` |

另外在 I0 标了两条前提问题：Revenant 手雷只锁玩家；生物诱饵是空的。

### 3.2 判断问题，**没有改**，等用户定

filter 当时的理由站不住的，按规则不改结果：

| 项 | 当前 | 我的建议 | 理由 |
|---|---|---|---|
| **生物诱饵** | 保留：研究 + 实现 | **降为"不要"，需求转给 HSD 自研** | 没有可研究的东西。"吸引 AI"用 D-DECOY-AI 的思路自己写 |
| 地图透视 | 参考 | 降为"不要"，合并到 APEX 2.6 | 这份记录没有新增 |
| 范围治疗 | 参考 | 降为"不要"，圈的写法记在 C-AURA-BUFF 旁 | 只有一个粒子 |
| 相位回溯、炮台 v2 | 参考 | 保留记录，**不再投入** | 对照项都有更好来源 |
| Revenant 手雷 | 保留 | 保留，**实现时改目标来源**（有意差别） | 部件有价值 |
| 重投气球 | 参考 | 保留参考，不实现 | PvE 单人不需要全队滑索 |
| 红色金马召唤 | 武器阶段 | **武器阶段优先读** | 这是伙伴 AI 的真代码 |

## 4. 对其他文档的更正（没动那些文件）

`TF2-Research/` 不在这个仓库。记在这里，留给下一个动它的会话：

| 文档 | 处 | 更正 | 影响 |
|---|---|---|---|
| APEX-REPORT 2.3 | "每层 24" | 25–28（首跳当帧 + 余数补齐，看帧率），待实测 | Unity 少 1–4 |
| APEX-REPORT 2.3 | "烧 8 s" | 约 7.5 s（inflictor 从落地算 8 s） | Unity 多 0.5 s |
| APEX-REPORT 2.3 | "最多爬高 46 u" | 约 126 u（相对上一个地面，推断） | Unity `ClimbMax 46` 偏小 |
| APEX-REPORT 2.3 | "有一个 mod `vertical_firestar`" | `.txt` 只有 `_disabled`，本地不存在 | Unity `alongThrow` 没有 R5 对照 |
| `_shared/B-electric-emp.md` | 机械分支"在 `#if DEVELOPER` 里" | `wu:3120-3270` 没有 `#if`，正常跑 | NPC 机械加伤算数 |

`B-electric-emp.md` 在本仓库但属于 PR #86，这个 PR 不改它，避免和那边冲突。

## 5. 混合构建相关的记录

| 位置 | 情况 |
|---|---|
| `_missing_callback_stubs.gnut` | **SDK 写的桩**，增益包和炮台的回调都在这 |
| `survival_loot.csv:407-414`、`:436` | SDK 注释掉（"needs model port and server script"、"removed in S30"） |
| `mp_weapon_grenade_emp.nut:3`、`:7-78` | SDK 注释；碰撞函数服务端和客户端两份，签名不同（S3 / S21） |
| `mp_weapon_grenade_emp.nut:81-334` | 枪声诱饵，推断社区添加 |
| `ai/_ai_dummie.gnut:1055` | `// S3: Survival_GetHeadshotDamageScale not available` |
| `mp_weapon_creaturebait.nut:1-113`、`mp_ability_consumable.nut:269-314` | 代码被抹成空白，物品或逻辑缺失 |
| `mp_ability_consumable.nut:2619`、`:2638` | SDK 加的 1v1 休息判定 |

## 6. 这份没做的

- 没读：`GetMaxCookTime`、`StunWhenInterruptable` 细节、`PushOutOfTrigger`、`npc_nessie` AI 设置、两份 `PetStartFollowingOwner` 的差别。各记录第 5 节有列。
- 没改任何 Unity 代码，没加 `R5-DIFF-ARCHIVE.md` 行（差别要实测定下来再写）。
- 没进 R5。
