# T2 报告：共用底层差异账本

日期：2026-10-28。静态分析（Ghidra 反编译 `server.dll`），没有运行游戏。

## 1. 结果

账本：[ledger.csv](ledger.csv)，41 项。编号沿用 R5 子系统字母，`r5_id` 一列对应 R5 `rea-native/ledger.csv` 的条目。

| 分类 | 项数 | 含义 |
|---|---|---|
| 相同 | 25 | 代码结构和规则一样，数值可能不同 |
| 改过 | 3 | 两边都有，但 Apex 改了规则 |
| R5 已删除 | 3 | TF2 有，Apex 关掉了（代码大多还在） |
| TF2 没有 | 7 | Apex 新加的 |
| 待定 | 3 | 还没读完或要运行时确认 |

**一句话结论：地面、空中、滑铲、lurch、镜头弹簧的代码 Apex 基本原样继承了 TF2，手感差别主要来自参数，再加上几条 Apex 新加的惩罚规则。**

## 2. 关键发现

1. **地面加减速是同一套代码。** TF2 的 GetAccel（`0x18016ea60`）和 R5 一样分三段：低速、普通、冲刺，滑铲时单独一段。TF2 MP 铁驭把低速段和冲刺段设成 -1（关闭），所以加速度始终是 2500。减速 `deceleration` 也是 -1，回退为 `acceleration × 0.6` = **1500**。Apex 用的是同一份代码，只把三段填成 2500 / 450 / 100，减速改成 1250。所以 Apex 的"起步快、加到冲刺慢"完全是调参出来的。
2. **连跳保速的差别在 skip 规则（T-J03）。**

   | | TF2 | Apex |
   |---|---|---|
   | 窗口 | 落地后 0.1 s | 1.0 s |
   | 每跳扣速 | 12 | 100 |
   | 扣速下限 | 450 | 冲刺上限 299 |
   | 跳跃高度 | ×0.75 | 正常速度下不降 |

   Apex 还新加了 `antiMultiJump*` 高度惩罚和 `landSlowdown` 硬着陆减速（T-J04、T-J05）。这些合起来就是"Apex 连跳不保速"的原因。
3. **lurch 是 TF2 原有的"keyboard grace"。** 强度、窗口、上限数值完全相同，Apex 只是改了 ConVar 名字。之后 Apex 加了速度截断 1100 和多次连按衰减（T-L03、T-L04），并把"必须新按键"从写死的规则改成了 ConVar。
4. **空中的残余增益（R5 J-05）来自 TF2 的"帮助开始蹬墙跑"功能。** `player_extraairaccelleration` 2.0 的引擎说明写着 "Helps to start wall running"。Apex 关了蹬墙跑，这个加速度却还留着。
5. **滑铲规则相同。** 起滑门槛、加速、上限、冷却、衰减公式都一样。Apex 把冷却从 ConVar 改成了 setfile 键，并加了空中起滑门槛和滑铲超级跳。
6. **镜头基本相同。** 弹簧 65 / 9、落地踢、冲刺侧倾、滑铲侧倾和 FOV、视角漂移，数值都一样。
7. **蹬墙跑在 TF2 里走地面移动的代码。** `WalkMove`（`0x180185230`）同时处理地面和墙面：蹬墙跑时，墙被当作"地面实体"。T3 详细看。
8. **TF2 的速度函数里有 Denuvo 防篡改触发器**（`Denuvo_SlowSpeed`）。T5 用运行时工具时要注意，以 Northstar 下的正常运行为准。

## 3. 方法

1. Ghidra 工程 `ghidra-projects/tf2/`（server.dll、client.dll），自动分析。
2. 全部 ConVar 注册（server 903 个、client 1186 个）：[../static-values/ghidra/DumpAllRegistrations.java](../static-values/ghidra/DumpAllRegistrations.java) → [convar-all.tsv](../static-values/ghidra/convar-all.tsv)。
3. 反编译移动代码区间：server.dll 0x18015e000–0x180190000（692 个函数），玩家类 0x1805c8000–0x1805f0000（820 个函数）。脚本是 [ghidra/DecompileRange.java](ghidra/DecompileRange.java)。原文在 `local/t2/`，不进版本库。
4. 标注：[annotate.py](annotate.py) 把 ConVar 读取替换成名字。读 TF2 代码要知道两点：
   - TF2 的 ConVar 通过"对象 + 0x38"处的指针读，浮点值在 +0x58、整数在 +0x5c。R5 是对象 +0x40，两边不同。
   - `.set` 字段按 schema 的偏移读：stance 设置在 `move+0x20`，全局设置在 `move+0x18`。
5. 常量：[read_consts.py](read_consts.py)。
6. 用 R5 的 [NATIVE-MAP](../../Apex-MovementAnalysis/research/rea-native/NATIVE-MAP.md) 和账本做索引，逐项比对。

TF2 函数入口（server.dll）：

| 函数 | 地址 | 依据 |
|---|---|---|
| PlayerMove | 0x180179950 | "Bogus pmove player movetype" 字符串、movetype 分派 |
| WalkMove（空中外壳：重力半步 → 跳跃 → 蹬墙检查 → 钩爪 → 空中/墙面） | 0x18016a9f0 | 调用顺序 |
| AirMove + lurch | 0x180161170 | 读 `jump_keyboardgrace_*` |
| AirAccelerate | 0x180160f40 | 读 `player_extraairaccelleration` |
| 地面/墙面移动 | 0x180185230 | 读 `wallrun_slip*`，调用 Friction / Accelerate |
| GetAccel / GetDecel | 0x18016ea60 / 0x18016eda0 | 读 stance 设置 +0x48…+0x58 |
| Friction / Accelerate | 0x1801696b0 / 0x180160230 | |
| Jump | 0x180172870 | 读 `skip_*` |
| Slide_TryBegin | 0x180183180 | 读 `slide_*` |
| TraversalMove / AutoMantle | 0x180180780 / 0x180181d20 | 读 `automantle_*` |
| 蹬墙跑起跑 / 维持 / 重力 | 0x1801835c0 / 0x180186d60 / 0x180186c70 | 读 `wallrun_*`（T3） |
| 速度倍率（含 Denuvo） | 0x1805d2510 | |
| 武器移动倍率（主武器 × 副武器） | 0x1805d25d0 | 两个武器的 `move_speed_modifier` 相乘，可以解释 R5 SDK 注释里的 "modifier × modifier" |

## 4. 待定和未解项

1. **T-G04**：减速是否乘 msc。TF2 的加速和减速都乘 `player+0x1600`，但不确定 0x1600 是不是 msc。R5 的 M2 实测是"减速不乘 msc"。T5 运行时读这个字段。
2. **T-L02**：TF2 lurch 的"新按键"条件是推断的（`movedata+0x20` 看起来是本命令新按下的键）。T5 确认。
3. **T-S06**：滑铲跳的提速到 350、提前起跳退还滑铲加速，这两条还没读完。
4. **T-M01**：mantle 和翻越只对了结构，公式没比。之后补，或者交给 T5 实测。
5. **T-S01**：TF2 滑铲加速似乎不乘 msc，Apex 乘。铁驭拿枪时 msc 是否为 1，要等 T5 看武器移动倍率。
6. client.dll 只做了 ConVar 层面的对照（默认值和 server 完全一致），没逐个对函数。
