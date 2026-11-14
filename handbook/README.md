# HSD 动作与技术手册

版本：**v1**（hb-integrate 第二轮整合，2026-11-14；阶段 0 骨架 hb0）。01 – 12 章和附录 A 都写完了，阶段 4 重建检验也跑过一轮（结果见下面目录里 `rebuild-test/` 一行）。分支 `handbook/base`，还没合并进 `main`（draft PR [#124](https://github.com/letheli710/Apex-MovementAnalysis/pull/124)，早上要定的事见 [_notes/MORNING-CHECKLIST.md](_notes/MORNING-CHECKLIST.md)）。

## 这份手册是什么

High Speed Doom（HSD）的移动、镜头、动画、战斗手感，过去三周是照着 Apex（本地 R5 构建）和 Titanfall 2 一项一项量出来、拆出来的。量出来的东西散在一百多份研究报告、几十个 PR 和 Unity 代码的注释里，而且大多写成"R5 的某个函数在某个地址做了什么"。

这份手册把这些结果重新写成**我们自己的技术**：每一项只讲"它为什么这样设计、规则和数是什么、怎么实现、怎么验收"，不需要打开 R5 或 TF2 才能看懂。

**判断标准**：哪天把 R5、TF2 和它们的解包文件都删掉，只留这份手册和 Unity 代码，也能把同样的移动和镜头重新做出来。阶段 4 的"重建检验"（`rebuild-test/`）就是专门检验这一点的。

## 为什么离开 R5 也能用

1. **规则写成和引擎无关的形式**：公式、状态图、伪代码，不写"调用 0x140a3b550"。R5 的函数地址、内存偏移只出现在每一项最后的"出处"里，用来回头核对，正文不依赖它。
2. **每个数都带单位和比例**：同时给出米 `[m]`、R5 原值 `[u]`、和身高的比例。换一个身高的角色（比如泰坦）也知道怎么缩放。
3. **每一项都有验收方法**：测试名、指标、合格线。实现对不对，靠跑测试和对照数据判断，不靠"开 R5 比一下"。
4. **对照数据存档**：R5 / TF2 的实测曲线、录像和原始日志已经存在研究仓库和私有仓库 `HSD-RawData` 里，删了游戏也能核对。

## 怎么读

- **第一次读**：先读本页的"写法规范"和"示范条目"，再读 [01 单位与身体](01-units-body.md)。所有数都从这里的单位规定出发。
- **做一个功能**：在目录里找到章，读该项的"原理"和"规则和公式"，照"实现模板"做，最后用"验收"一段的测试和合格线检查。
- **查一个数**：去 [tables/](tables/README.md)（参数对照表、镜头事件表、关卡尺度表，由 hb-tables 写）。表里每个数都能链回到某一章的某一项。
- **想知道资料在哪、还缺什么**：读 [00-INVENTORY.md](00-INVENTORY.md)。还没研究过的东西在 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md)。

## 目录

| 文件 | 内容 | 谁写 | 状态 |
|---|---|---|---|
| [README.md](README.md) | 本页：这是什么、怎么读、目录、写法规范、示范条目 | hb0 | 完成 |
| [00-INVENTORY.md](00-INVENTORY.md) | 逐章盘点：资料在哪、已有什么、缺什么、缺的要不要新测 | hb0 | 完成 |
| [01-units-body.md](01-units-body.md) | 单位与身体：哪些量换算、R5 角色尺寸、换算系数、u 模式和米模式 | hb0 | 完成 |
| [02-foundation.md](02-foundation.md) | 底层：时间步长、每帧顺序、碰撞体、地面检测、台阶、斜坡 | hb-ch02 | 完成（11-14 合入） |
| [03-ground-air-jump.md](03-ground-air-jump.md) | 地面、空中、跳跃、落地（含硬着陆降速）、时间窗口、lurch / tap strafe | hb-ch03 | 完成（11-14 合入） |
| [04-slide-mantle.md](04-slide-mantle.md) | 滑铲、斜坡滑铲、翻越、攀爬、蹲着翻越、superglide；附件 [04-slide-mantle/](04-slide-mantle/)（`slide_ref.py`） | hb-ch04 | 完成（11-14 合入） |
| [05-wall-external.md](05-wall-external.md) | 跑墙、挂墙、二段跳、蹬墙跳；滑索、钩爪、跳板、击退 / 火箭跳、传送门（攀爬在 04） | hb-ch05 | 完成（11-14 合入） |
| [06-momentum-arbitration-input.md](06-momentum-arbitration-input.md) | 动量规则（总表）、动作仲裁、输入（硬着陆降速在 03，这里只写指针） | hb-ch06 | 完成（11-14 合入） |
| [07-camera.md](07-camera.md) | 镜头：事件型、持续型、组合规则、力度规律；附件 [07-camera/](07-camera/README.md) | hb-ch07 | 完成（11-14 合入） |
| [08-body-animation.md](08-body-animation.md) | 持枪和移动叠加、泰坦步态 / 脚 / 地形 / 惯性、驾驶舱镜头（受击、上下机在 07）；附件 [08-body-animation/](08-body-animation/) | hb-ch08 | 完成（11-14 合入） |
| [09-combat-feel.md](09-combat-feel.md) | 后坐、开镜、枪的重量、扩散、命中反馈；附件 [09-combat-feel/](09-combat-feel/README.md) | hb-ch09 | 完成（11-14 合入） |
| [10-abilities-ai.md](10-abilities-ai.md) | 技能设计结构、敌人 AI（AI 没有参考实现，写成规格） | hb-ch10 | 完成（11-14 合入） |
| [11-acceptance.md](11-acceptance.md) | 手感怎么验收：指标、回放对比、自动测试、合格线总表（§11.6，原件 [tables/pass-lines.tsv](tables/pass-lines.tsv)）、重建验收示范（§11.9） | hb-ch10 | 完成（11-14 合入） |
| [12-titan-motor.md](12-titan-motor.md) | 泰坦电机：地面速度律、冲刺跑、dash 推力和能量、蹲、转向、状态缩放、重力 / 小跳 / 硬落地、和铁驭电机的区别 | hb-ch08 | 完成（11-14 合入）（11-14 新加的章） |
| [A-research-methods.md](A-research-methods.md) | 附录 A：反编译、Frida 实测、回放对比怎么做 | hb-ch10 | 完成（11-14 合入） |
| [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md) | 待研究清单（这一轮不做） | hb0 建，hb-integrate 合并各章备注 | 已并全部章节和重建检验 |
| [tables/](tables/README.md) | 参数对照表（含持枪动画、泰坦步态）、镜头事件表、关卡尺度表（TSV + 给人看的 md）、合格线总表 [pass-lines.tsv](tables/pass-lines.tsv)（185 行，给人看的摘要在 11 §11.6）、`check_params.py` | hb-tables；hb-integrate 补 | 完成（11-14 合入） |
| [rebuild-test/](rebuild-test/judge/REPORT.md) | 阶段 4 重建检验：只看手册写一个纯 C# 实现（`build/`），和 Unity 逐命令对比（`judge/`）。**结果**：移动 10 / 10 逐命令一致（最大差 0.0001 u），镜头随机数取 0 时 5 / 5 一致；按题目原样 5 / 10，不过的里 2 题是题目读法、3 题是同一个手册错误（07 §1.4 随机种子的符号），11-14 已改正，题目要改后再跑一轮（99 RB-1） | hb-rebuild / hb-judge | 第一轮完成（存档） |
| `_notes/<会话名>.md` | 各会话给总控的备注：想改 README / 表 / 别章的地方、建议的 D-xx 行；[早上要定的事](_notes/MORNING-CHECKLIST.md)、[研究仓库 PR 合并清单](_notes/hb0-pr-merge-list.md) | 各会话 | — |

总控计划和会话分工在工作区根目录 `HANDBOOK-PLAN.md`（不在这个仓库）。

---

## 写法规范

所有章都照这一节写。拿不准的地方看后面的[示范条目](#示范条目起跳普通跳)。

### 1. 先白话，再细节

- 每一章开头一段白话：这一章管什么、和别的章怎么分界、读完能做出什么。
- 每一项的第一段（"原理"）不出现公式、变量名、地址，用玩家能感觉到的话说清楚"为什么这样设计"。
- 后面的段落像论文：先结论，再数，再推导和例外。
- 中文写。变量名、键名、类名用代码格式（`jumpHeight`）。

### 2. 每一项五段

每一项是一个三级标题（`### 3.2 起跳`），下面固定五段，用四级标题，顺序不变：

| 段 | 写什么 | 不写什么 |
|---|---|---|
| **原理** | 为什么这样设计，玩家感觉到什么，和哪条设计哲学对应（如 DESIGN-PHILOSOPHY 的 P3、T5） | 公式、地址 |
| **规则和公式** | 和引擎无关的规则：状态、条件、先后顺序、边界情况、公式。所有数放进三列数值表（见第 3 条），写出合理范围 | 函数地址、内存偏移 |
| **实现模板** | 状态图或伪代码；离散化要注意的地方（每帧顺序、半步重力等）；指向 Unity 参考实现（文件、类、方法、开关） | 整段贴 Unity 代码 |
| **验收** | 怎么判断做对了：测试名（Unity EditMode 测试的类和方法）、指标、对照数据（录像、曲线、TSV）、合格线 | "感觉对了" |
| **出处** | 研究文档、D-xx、R5-DIFF 条目、PR 号、R5 函数地址和偏移（只放这里） | — |

一项不需要某一段时，写"无"并说一句为什么，不要删掉标题。

### 3. 三列数值表

每个有单位的数都写成三列：

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起跳高度 `jumpHeight` | 1.422 m | 56 u | 0.778 H | 见正文 | [数据] [实测] |

- **`[m]` 列**：R5 原值 × 换算系数（[01 §3](01-units-body.md)：1 u = 0.0254 m）。保留 3–4 位有效数字。这一列是算出来的，不是独立来源。
- **`R5 原值 [u]` 列**：研究里量到 / 读到的原始数，原样照抄，带单位（u、u/s、u/s²）。TF2 的数写 `TF2 原值 [u]`，在依据列注明 TF2。HSD 自己定的值写 `HSD 设计值 [u]`，依据列写 [设计]。
- **身高比例列**：除以参考身高 H = 72 u（站立碰撞体高度，[01 §4](01-units-body.md)）。速度写 `H/s`，加速度写 `H/s²`，长度写 `H`。TF2 铁驭的数也除以 H = 72 u。
- **泰坦用自己的参考身高 `H_t` = 235 u**（5.969 m，[01 §4.3](01-units-body.md)）：泰坦的身体、步态、驾驶舱、电机（第 08、12 章）的身高比例列写 `H_t`、`H_t/s`、`H_t/s²`，不要和铁驭的 H 混用。
- **不换算的量**（角度、时间、比例、次数、帧数、角速度 °/s）：`[m]` 和身高比例两列写"—"，原值写在 `R5 原值 [u]` 列并注明单位（°、s、×）。哪些量换、哪些不换，以 [01 §2](01-units-body.md) 为准；组合量（比如 °/(u/s)、1/u）按那里的规则换。
- 时间一律用秒（s），角度一律用度（°）。原文是毫秒、弧度、英尺的，换好再写，并在依据列注明原单位。
- **合理范围**：这个数改到多少还"像这个功能"。有实测就写实测的散布；只有设计判断就标 [设计]；不知道就写"未知"，不要编。

### 4. `[m]` 和 `[u]` 标记

用户 11-14 定：测试和研究阶段用 u；米模式保留设计以后再切；凡是用米的设计都要标清楚。所以：

- **表格列名**必须带单位标记：`[m]`、`[u]`。不带标记的长度、速度列不允许出现。
- **正文里的数**都带单位：`56 u`、`1.42 m`、`289.8 u/s`。不写裸数。
- **伪代码和变量名**：变量名后缀标单位体系，例如 `jumpHeight_u`、`gravity_m`。只在一个体系里的伪代码可以在代码块第一行注明 `// 单位：u`，块内不再逐个标。
- **Unity 参考实现**目前全是 u（模拟用 Source 单位，显示时才乘 0.0254，见 [01 §5](01-units-body.md)）。引用 Unity 字段时照写字段名，并注明 `[u]`。
- **"参考实现"指什么**（全手册统一，D-196）：手册里的"Unity 参考实现"指游戏身体 `MovementConfigs.Reference()`（`R5MotorV2` + `R5MotorV2Params.R5Reference()` + N7 原生开关）。`R5Reference()` 单独用是**回放电机**，是 D-66 的尺子，缺几条原生规则（超速连跳 −100、空中额外加速、固定冲刺边界、起跳推墙、lurch 上限等），不能当参考实现引用。`ReferenceMotor.cs` 是 M1 的第一版模型，也不是。
- 如果某一段**只在米模式下成立**（例如关卡按米设计的尺度），整段开头标 `[m 模式]`。

### 5. 出处写法

每一项"出处"段用列表写，每条一个来源，格式：

```
- <缩写或路径> §<节>：<这一条用了它什么>。<在哪>
```

- **路径**从研究仓库根目录算，例如 `research/rea-native/subsystems/N2-J-JUMP-AIR.md §1.1`。Unity 的路径前面加 `HSD-Unity:`，例如 `HSD-Unity: Assets/HSD/R5Replay/Runtime/R5MotorV2.cs`（`JumpCommand`）。
- **测试名**写 `类名.方法名`，类名以 C# 里的 `class` 为准，不是文件名（例如 `R5MotorV2FormulaTests.MultiJumpPenaltyFraction`，类在 `R5MotorV2Tests.cs` 里）。
- **"在哪"**写 `main`，或者未合并 PR 的写法（第 6 条），或者"本地，不在 git"（例如 `TF2-Research/REBUILD-GAP-1107.md`）。
- **决定**写 D 编号：`D-55`。R5 和 HSD 的差别写 R5-DIFF 的条目名：`R5-DIFF-ARCHIVE.md K-4`。
- **R5 函数地址和偏移**只写在这里：`[反编译] Jump 0x140a3b550；落地时刻 player+0x3680`。
- **依据标签**沿用 `research/DESIGN-PHILOSOPHY.md §2.1`：[实测] [反编译] [数据] [算] [推断] [设计]，另加 [TF2 实测] [TF2 数据] 区分 TF2 来源。"R5" 都指本地混合构建（S21 客户端 + S3 dedi + SDK）；只在混合构建里出现、不该学的现象见 DESIGN-PHILOSOPHY §10.3，引用前先查。
- 可以复用 DESIGN-PHILOSOPHY §2.2 的缩写（NG、NJ、CR、DIFF、DEC 等），第一次出现时在本章开头的"本章出处缩写"小表里列一次。

### 6. 引用还没合并的 PR

用户 11-14 定今晚不合并任何 PR。引用 PR 分支上的文件时这样写：

```
research/combat/RECOIL-VIEW.md §3（PR #93，还没合并；分支 combat/recoil-view-measure）
```

- 读法：`git show origin/<分支>:<路径>`。很多战斗 PR 是叠着的（叠法见 [00-INVENTORY.md](00-INVENTORY.md) §0.2）。**上层分支不一定包含下层最新的提交**（例如 #123 的分支里没有 #95 后来加的 `hold-pose/HOLD-POSE.md`），所以引用时写文件真正所在的那个 PR，以 00-INVENTORY 为准。
- Unity 代码同理：`HSD-Unity: Assets/HSD/Game/Runtime/Combat/ViewKick.cs（HSD-Unity PR #67，还没合并）`。
- 如果 PR 上的结论以后被改，手册跟着 PR 改；整合会话（hb-integrate）会在合并前逐条检查这些引用。

### 7. 别的规矩

- 只写自己负责的文件。想改 README、表或别的章，写进 `_notes/<会话名>.md`。
- 建议的新决定写进自己的 `_notes`，D 编号留空（`D-??`），由 hb-integrate 统一编号写进 `DECISIONS.md`。
- 研究里有矛盾、或者手册和 Unity 现在的做法不一样：两边都写，标出哪个是 R5、哪个是 HSD 现在的版本，并写进 `_notes`。不要悄悄选一个。
- R5 原值和 HSD 有意不同的（R5-DIFF "有意和 R5 不一样"一节），规则段写 HSD 的做法，并在同一段写"R5 原值是 …，HSD 有意改成 …，理由 …"。
- **没有参考实现的功能**（例如第 10 章的 AI）："实现模板"一段的标题写成"实现模板（没有参考实现）"，"验收"里的测试名写成"建议的测试（名字是建议，还没有）"。
- 一项"没测过"就写没测过，放进 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md) 的建议（写进 `_notes`），不要用推断冒充实测。

---

## 示范条目：起跳（普通跳）

下面是第 03 章里"起跳"一项的完整写法。各章照这个格式写。数据是真的，hb-ch03 可以直接搬进 03 章（搬的时候核一下有没有更新）。

### 3.x 起跳（普通跳）

#### 原理

按下跳跃，角色总是跳到**同样的高度**：跳多高由一个高度值决定，起跳速度从高度反算出来。这样改重力时跳跃高度不变，关卡里"能不能跳上去"只看一个数。

有两条附加规则，都是为了不让玩家用连续起跳刷速度或高度（对应 DESIGN-PHILOSOPHY P3"动量是玩家的资产，只有明确规则才能收走"和 P4"技巧窗口按时间算"）：

1. **刚落地又跳，跳得矮**：落地后 0.15 s 内再跳只有正常高度的 30 %，到 0.75 s 线性恢复到 100 %。连续兔跳会越来越矮，但正常的"落地—停一下—再跳"不受影响。
2. **刚落地又跳，超出冲刺速度的部分被削掉一点**：落地 1 s 内起跳、水平速度超过冲刺上限时，减 100 u/s，但不低于冲刺上限。高速连跳的速度会一跳一跳往冲刺速度收，不会无限保持。

滑铲中起跳用另一个较低的高度，滑铲跳的水平速度规则在第 04 章。

#### 规则和公式

1. 起跳只在着地时、跳跃键按下的那一帧（按下沿）触发。
2. 高度 H_j：平时 `jumpHeight`，滑铲中 `slideJumpHeight`。
3. 连跳高度系数（t = 现在 − 上次落地时刻；从没落过地则 t = ∞）：

   frac(t) = clamp(f + (1 − f) · (t − T_min) / (T_max − T_min), f, 1)，f = `antiMultiJumpHeightFrac`

4. 起跳竖直速度 V = √(2 · g · H_j · frac)。竖直速度先清零再加 V（不叠加原来的竖直速度）。
5. 超速削减：t < `skip_time` 且水平速度 v_h > R（R = 冲刺上限 = `sprintspeed` × 移动倍率）时，v_h ← max(R, v_h − `skip_speed_reduce`)，方向不变。
6. 起跳那一帧照常做空中加速（规则在第 03 章"空中"一项）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力 g（`sv_gravity` × `gravityScale`） | 19.05 m/s² | 750 u/s² × 1 | 10.42 H/s² | TF2 750 × 0.8 = 600 u/s² | [数据] [实测] |
| 起跳高度 `jumpHeight` | 1.422 m | 56 u | 0.778 H | TF2 60 u | [数据] |
| 滑铲跳高度 `slideJumpHeight` | 1.270 m | 50 u | 0.694 H | TF2 50 u | [数据] |
| 起跳速度 V（frac = 1） | 7.362 m/s | 289.83 u/s | 4.025 H/s | 实测 289.815–289.833 | [算] [实测] |
| 到顶时间 V / g | — | 0.386 s | — | — | [算] |
| 按命令步进的最高点（比 `jumpHeight` 低 V·dt/2） | 1.392–1.396 m | 54.8 u（120 Hz）– 54.95 u（144 fps 实测） | 0.761–0.763 H | 帧率越低越矮（60 fps 约 53.6 u） | [算] [实测] |
| 连跳系数下限 f `antiMultiJumpHeightFrac` | — | 0.3（×） | — | — | [数据] [实测] |
| 系数开始恢复 T_min `antiMultiJumpTimeMin` | — | 0.15 s | — | — | [数据] [实测] |
| 系数恢复到 1 T_max `antiMultiJumpTimeMax`（Unity 存的是 `multiJumpRampT` = T_max − T_min = 0.60 s） | — | 0.75 s | — | — | [数据] [实测] |
| 最矮的连跳速度（frac = 0.3） | 4.032 m/s | 158.74 u/s | 2.205 H/s | — | [算] [实测] |
| 超速削减窗口 `skip_time` | — | 1.0 s | — | — | [数据] |
| 超速削减量 `skip_speed_reduce` | 2.54 m/s | 100 u/s | 1.389 H/s | — | [数据] [实测] |
| 超速削减下限 R（空手冲刺上限 260 × 1.15） | 7.595 m/s | 299 u/s | 4.153 H/s | 随武器的移动倍率变 | [数据] [实测] |

#### 实现模板

```
// 单位：u、s
on command(dt):
    if grounded and jumpPressedThisFrame:
        t     = now - lastLandTime              // 从没落地过 = ∞
        frac  = clamp(f + (1-f)*(t - Tmin)/(Tmax - Tmin), f, 1)
        H     = sliding ? slideJumpHeight : jumpHeight
        if sliding:  slideJumpHorizontal()      // 第 04 章
        else if t < skipTime and vh > R:  vh = max(R, vh - skipSpeedReduce)
        V = sqrt(2 * g * H * frac)
        vel.z  = 0
        vel.z -= 0.5*g*dt        // 本帧开始的半步重力
        vel.z += V
        vel.z -= 0.5*g*dt        // 起跳自己的半步重力
        airAccelerate(...)       // 第 03 章"空中"
        pos   += vel * dt
        vel.z -= 0.5*g*dt        // 本帧结束的半步重力
        grounded = false
```

离散化要注意：R5 按"半步重力"积分，起跳那一帧竖直速度一共扣了 1.5 个 g·dt。所以起跳后第一帧记录到的竖直速度不是 289.8，而是 V − 1.5·g·dt（144 fps 时约 282.0 u/s）；位移用的是 V − g·dt。照这个顺序做，**连续公式**的最高点 V²/2g 等于 `jumpHeight`，但**按命令步进**的最高点 = V²/2g − V·dt/2 + g·dt²/8，比 `jumpHeight` 低约 V·dt/2：120 Hz 约 1.2 u（54.8 u），144 fps 约 1.0 u（实测 54.95 u），帧率越低越矮。这是 R5 本身的行为，照做才能和录像对上（详见 [03 §3.8](03-ground-air-jump.md)）。

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/R5MotorV2.cs`，`R5MotorV2.JumpCommand`、`MultiJumpFrac`、`JumpSpeed`、`GroundJumpSpeed`；参数在 `R5MotorV2Params.cs`（`jumpHeight`、`slideJumpHeight`、`antiMultiJumpHeightFrac`、`multiJumpHoldT0` = 0.15、`multiJumpRampT` = 0.60 = TimeMax − TimeMin（是时长差，不是 TimeMax），全部 [u]）。

#### 验收

- 单元测试（Unity EditMode，`Assets/HSD/R5Replay/Tests/Editor/`）：
  - `R5MotorV2FormulaTests.JumpRemovesOneAndAHalfGravitySteps`：V = 289.828，起跳后 vz = V − 1.5·g·dt。（类在文件 `R5MotorV2Tests.cs` 里。）
  - `R5MotorV2FormulaTests.MultiJumpPenaltyFraction`：frac(0) = frac(0.15) = 0.3，frac(0.45) = 0.65，frac(0.75) = 1。
  - `R5MotorV2FormulaTests.JumpRightAfterLandingIsPenalisedAndFirstJumpIsNot`。
  - `R5MotorV2` 没有"最高点"测试。`ReferenceMotorTests.JumpApexMatchesJumpHeight`（文件 `R5ReplayTests.cs`）测的是 M1 的第一版 `ReferenceMotor`，不是参考实现，不能拿来验收这一项；要补的测试见 [99](99-TODO-RESEARCH.md) B03-10。
- 对照数据：M2 的 42 次首跳，拟合起跳速度 289.823 u/s（sd 0.005）；连跳每一跳的系数（`research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md` §2.2、§4）。
- 合格线：起跳速度和 289.83 u/s 差 < 0.05 u/s；144 fps 最高点和 54.95 u 差 < 0.1 u；连跳系数和 frac(t) 差 < 0.01；回放基线（第 11 章）不变。
- 已知例外：测试工具在 dedi 上重置玩家会被算成一次落地，重置后 0.75 s 内的第一跳会被降高（D-55）。对照 R5 录像时，重置后等 0.75 s 以上再跳。

#### 出处

- `research/rea-native/subsystems/N2-J-JUMP-AIR.md` §1.1、§5 J-01 – J-04：起跳高度、连跳惩罚和超速削减的规则。main
- `research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md` §2.2、§4：起跳速度和连跳系数的实测拟合。main
- `research/phase2-local/static-values/STATIC-VALUES.md` §2：`jumpHeight` 56、`gravityScale` 1。main
- `research/rea-native/convar-defaults/CONVAR-DEFAULTS.md`：`sv_gravity` 750。main
- `tf2/static-values/T1-REPORT.md`：TF2 的 `jumpheight` 60 × `gravityscale` 0.8。main
- D-55（F-2 原地跳高 1.8 u 不是移动代码，是测试工具的重置）；`research/feel/FEEL.md` F-2。main
- [反编译] `Jump` 0x140a3b550；上次落地时刻 player+0x3680；连跳惩罚的开关标志 player+0x36a9（什么时候为真还没读，NJ §6）。
