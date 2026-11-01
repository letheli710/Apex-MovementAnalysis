# 生物诱饵 系统记录

会话 `i1-records`，2026-11-01。静态记录。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`nut` = `weapons/mp_weapon_creaturebait.nut`（128 行）。

## 0. 概要

- **道具**：Freelance 模式的诱饵发射器 / `mp_weapon_creaturebait`。
- **一句话**：**本地没有引怪代码。** 脚本 128 行里只有两个空函数，没有武器 `.txt`。
- **更正 filter**：filter 说它是"引怪：PvE 里'吸引 AI 去某处'的部件"。这是从名字推的，本地证实不了。系统价值落空，要吸引 AI 得用别的部件（第 6 节）。
- **分类**：无（本地）。意图是系统。
- **可拆出的部件**：无。

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 证据 |
|---|---|---|
| 开火 | 空函数 | `nut:117-119`，函数体为空 |
| 碰撞 | 只把速度清零：`projectile.SetVelocity( <0,0,0> )` | `nut:121-127` |
| 引怪 | **不存在** | 全局搜 `bait`（不分大小写）只有下面几处 |

全局搜索结果：

| 位置 | 内容 |
|---|---|
| `nut:1-113` | 全是空白行：原来的代码被去掉了（和别的文件里被剥离的 `#if` 块同样形态） |
| `scripts.rson:979`、`:2816` | 注册脚本 |
| `freelance/sv_flskit_tools.nut:151`、`:166`、`:184` 附近 | `PlayerHasBaitLauncherEquipped`、`GetPlayersWithoutBaitLauncher`：只判断玩家有没有这把武器 |
| `freelance/sv_freelance.nut:284` | 注释"自动换弹，给诱饵发射器用" |
| `_script_toys.gnut:82` | 注释掉的特效常量 `P_CreatureBait_sm` |

`scripts/weapons/` 下没有 `mp_weapon_creaturebait.txt`，也不在 `survival_loot.csv`。

## 2. 流程

无法写。**不编。** 能确定的只有：投掷物碰到东西后速度清零（`nut:126`），停在原地。

## 3. 代码

就是第 1 节那两个函数。

## 4. 参数

没有。没有 `.txt`，脚本里没有常量。

## 5. 未解决和要实测的

- 代码去哪了：`nut` 前 113 行被抹掉。真实逻辑可能在 Freelance 模式服务端，本地没有。
- R5 实测帮不上：没有 `.txt`，武器发不出来（推断）。

## 6. HSD 实现

未实现。"吸引 AI 去某处"这个需求还在，本地可用的部件有：

| 部件 | 做什么 | 见 |
|---|---|---|
| 分身 AI 登记 | 假目标被 AI 当真，优先级和主人一样 | [D-DECOY-AI](../../_shared/D-DECOY-AI.md) |
| AI 危险区 | 反向：逼 AI 离开 | [thermite-grenade](../thermite-grenade/SYSTEM.md) 3.4 |
| 枪声诱饵 | 放声音（只有声音，不通知 AI） | [arc-star](../arc-star/SYSTEM.md) 3.4 |

建议：HSD 里一个不可见的假目标实体 + 投掷落点。按 D-DECOY-AI 的登记思路，自己写，没有 R5 对照可比。投掷物停住的规则就是 `nut:126` 这一行。
