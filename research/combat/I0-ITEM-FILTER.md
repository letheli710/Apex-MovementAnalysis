# I0 · 战斗研究第二阶段：道具过滤（PvE）

状态：**Leader 自己定的草稿，等用户事后看**（2026-11-01）。用户 11-01 说过各阶段自己往下推，不用等他确认，所以这份过滤先按标准定下来，共享日志里记成 pending。

标准和技能阶段一样（D-78）：每样道具看三样——**效果**（伤害 / 控制）、**可视化**、**可复用系统**——有一样有价值就研究。另加一条：已经在技能阶段或 APEX-REPORT 研究过的，只补缺口。

来源：`research-src/s21-platform/datatable/survival_loot.csv`（按 `type` 分组）和 `scripts/vscripts/weapons/`。武器、配件、hop-up（含金马 hop-up）、弹药留到**武器阶段**。

**2026-11-01 改过（i1-records）**：只改事实错误，每项标"更正"。去留结果一项没动。读脚本后发现的判断性问题（比如生物诱饵值不值得留）不在这里改，见 [items/I1-SUMMARY.md](items/I1-SUMMARY.md) 第 3 节。

## 1. 保留：研究 + 实现

| 道具 | 脚本 / 数据 | 三样里哪一样 | 备注 |
|---|---|---|---|
| 破片手雷 | `mp_weapon_frag_grenade` | 效果 | APEX-REPORT 2.1 已有弹道和伤害，补成 SYSTEM.md 格式 |
| 电弧星 | `mp_weapon_grenade_emp` | 效果 | APEX-REPORT 2.2；减速走 `_shared/B-electric-emp.md` |
| 铝热剂 | `mp_weapon_thermite_grenade` | 效果、可视化 | APEX-REPORT 2.3；沿地面走线和 Fuse 火焰环同类，**更正：代码不共用** |
| 飞刀 | `mp_weapon_throwingknife` | 效果 | **更正：不是近战**。占主武器槽的直射投掷物，命中 100，爆头 ×3 |
| Revenant 手雷（活动道具） | `mp_weapon_grenade_rev_shell` | 效果 | loot 表里禁用，脚本还在。**更正：本地只锁玩家，不锁 NPC** |
| 生物诱饵 | `mp_weapon_creaturebait` | **系统** | 引怪：PvE 里"吸引 AI 去某处"的部件，和分身仇恨互补。**更正：本地脚本是空的，没有引怪代码，也没有 `.txt`** |
| 进化护甲 | `armor_pickup_*_evolving`、`armor_core_*`（**更正：逻辑在 `sh_survival_loot.gnut`**，`cl_survival_loot.nut` 只是显示） | **系统** | 造成伤害 → 护甲升级。PvE 成长系统的现成参考 |
| 头盔 | `helmet_pickup_lv1–5` | 系统 | 爆头减伤 → 走伤害修正链 |
| 治疗 / 护盾消耗品 | `health_pickup_*`（注射器、医疗包、电池、小电池、凤凰） | **系统** | 回血本身简单（D-78 当天"太基础"已取消），但"读条使用 + 使用限制 + 按键取消"是通用的使用流程部件。**更正：没有移动减速（只是不能冲刺、不能攀爬）；脚本里被打不打断** |

## 2. 参考：只看系统 / 可视化

| 道具 | 脚本 / 数据 | 参考什么 | 备注 |
|---|---|---|---|
| 增益包：相位回溯 | `mp_ability_boost_kit_phase_rewind` | 系统：回到几秒前的位置 | 和 Death Totem 召回、TF2 相位回溯对照；**本地只有 .txt，没有服务端脚本**（loot 表注释"needs server script"） |
| 增益包：吸血 | `mp_ability_boost_kit_lifesteal_kit` | 系统：命中回血 → **更正：结算后钩子，不是修正链** | 增益包只有 .txt；**更正：吸血系统本身有完整脚本 `weapons/_lifesteal.nut`** |
| 增益包：地图透视 | `mp_ability_boost_kit_map_hack` | 可视化：全图敌人显示 | APEX-REPORT 2.6 相关；只有 .txt |
| 增益包：召唤 Nessie | `mp_ability_boost_kit_nessie_summon` | 系统：召唤伙伴 AI | 和跟随运动对照；增益包只有 .txt；**更正：同样的召唤在 `hopup_golden_horse.nut`、`sh_player_pet.nut` 里有脚本** |
| 增益包：范围治疗 | `mp_ability_boost_kit_heal_radius` | 可视化：范围圈 | 只有 .txt |
| 重投气球 | `mp_ability_redeploy_balloon` | 系统：**更正：不发射人**。部署一条垂直滑索，玩家爬上去转跳伞 | 偏移动，和跳板对照 |
| 炮台 v2 | `mp_ability_gun_turret_v2` | 系统：放置炮台 | 和 Sheila 放置、哨戒炮对照。**更正：也只有 .txt，回调是桩，不在 loot 表** |

只有 `.txt` 的几项，静态研究只能记字段和意图，没法写完整流程，要在 SYSTEM.md 第 5 节写明。**更正：5 个增益包的 `.txt` 除名字和图标外完全相同，没有效果字段**，见 `items/_shared/I-STUB-ITEMS.md`。

## 3. 不要

| 道具 | 不要的原因 |
|---|---|
| 背包 | 物品栏容量，PvE 练习场用不上 |
| 击倒护盾、自救护盾 | 倒地和复活是团队机制 |
| 移动重生信标 | 团队重生 |
| 增益包：金甲、悬浮 | 金甲是单纯数值；悬浮 TF2X 已经做了 |
| 增益包：威胁烟雾 | 烟雾挡视线（D-78 已定不要） |
| Void Ring | Alter 已搁置 |
| 增强件 augment | 本地构建不支持这个 loot 类型 |
| 宝箱、钥匙卡、Marvin 手臂、旗帜、Nessie 收集品、进化球、`custom_pickup` | 模式和活动道具，和战斗无关 |
| 数据刀 | Ash 的地图交互，和战斗无关 |

## 4. 下一步

1. 第一波：并行写静态 SYSTEM.md（第 1 节 9 项 + 第 2 节 7 项），手雷三项从 APEX-REPORT 转写并补缺口。
2. R5 实测：手雷对 NPC、进化护甲升级、治疗读条和打断。
3. Unity 实现，叠在技能阶段的分支上。
