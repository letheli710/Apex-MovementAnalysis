# 11 手感怎么验收

由 hb-ch10 写（2026-11-14）。分支 `handbook/ch10`，还没合并。写法照 [README.md](README.md)；单位照 [01](01-units-body.md)（1 u = 0.0254 m，H = 72 u）。本章的容差都在 u 模式下定义，所以数值表只写 `[u]` 列，换米的地方单独说明（§11.7）。

## 白话说明

"手感对不对"很难靠玩来判断：Unity 里没有动画，人玩几次的感觉也不稳定。所以项目从 10-25 起（D-25）改成：**拿 R5 里录下的同一串输入，喂给 Unity 的角色，用同一套指标代码去量两边，再叠在一起看**。差多少算合格，事先写成数。

这一章讲四件事：

1. **量什么**：起跳速度、跳多高、滑铲多快多久、停下多远、空中转多少度、镜头抖多大……每个指标有一个容差，差在容差内叫"一致"，3 倍以内叫"接近"，再大叫"不一致"，次数都不一样叫"次数不同"（§11.2）。
2. **用什么比**：R5 录像 → Unity 批处理 → 指标脚本 → 叠图页面（§11.3）。
3. **怎么防止改坏**：几百个回放输出算 sha256，改代码前后必须逐字节相同；要动基线有严格的"没有变差"判据和留档要求（§11.4）。再加上两千多个自动测试、参数表校验和单位开关的等价检查（§11.5）。
4. **差多少算合格**：§11.6 是全手册的**合格线总表**，从各章、各 D 行、测试和脚本里收集，每行写出处。

最后 §11.7 讲为什么 R5 对照永远在 u 模式下跑，§11.8 给新功能的验收流程，§11.9 用阶段 4 的重建检验做示范，讲"只看手册能不能重新做出来"怎么验收。

**这些都证明不了"好玩"**。移动哈希只保证移动没变；自动测试只测写下来的逻辑；对照只说明"像 R5"。手感最后由用户玩了以后定（TECH-REPORT 11-04 §6）。

**和别章的分界**

| 内容 | 在哪 |
|---|---|
| 每一项功能自己的合格线、测试名 | 各章该项的"验收"段。本章 §11.6 把它们收成一张表 |
| 回放对比**怎么操作**（取片段、跑批处理、对齐） | [附录 A §A.7](A-research-methods.md) |
| 单位开关本身 | [01 §5](01-units-body.md)、HSD-Unity `Assets/HSD/UNITS-SWITCH.md`（PR #88，还没合并） |
| AI、技能的验收 | [10](10-abilities-ai.md)（AI 没有实现，只有建议的测试） |

**本章出处缩写**（路径从研究仓库根目录算）

| 缩写 | 文件 | 在哪 |
|---|---|---|
| FEEL | `research/feel/FEEL.md` | main |
| FM | `research/feel/feel_metrics.py`（`TOL`、`verdict`、`FRAME = 1/144`） | main |
| CC | `research/feel/camera_compare.py`（`TOL`、`ANG`、`FRAME = 1/120`） | main |
| RUD | `research/phase2-local/rud/README.md`、`rud_check.py`、`rud_compare.py`、`unity/baseline_sha256.json` | main |
| RPS | `research/phase2-local/rps/README.md`、`rps_check.py`、`rps_compare.py` | main |
| M1 | `research/phase2-local/m1/M1-REPORT.md` | main |
| M55A | `research/phase2-local/m55/ACCEPTANCE-M55.md` | main |
| VR | `research/phase2-prep/VALIDATION-REPORT.md` | main |
| LED | `research/rea-native/CROSSCHECK-LEDGER.md`、`ledger.csv` | main |
| PD | `tf2/runtime/PRESET-DIFF-1109.md` | main |
| US | HSD-Unity `Assets/HSD/UNITS-SWITCH.md` | HSD-Unity PR #88，还没合并（分支 `units/switch`） |
| TR | 工作区 `TECH-REPORT-1104/01-方法论和工具.md` | 本地，不在 git |

Unity 测试都在 HSD-Unity `Assets/HSD/R5Replay/Tests/Editor/`、`Assets/HSD/Game/Tests/Editor/`、`Assets/HSD/Game/Tests/PlayMode/`。**测试名写 `类名.方法名`，类名以 C# 的 `class` 为准，不是文件名**：例如 `R5MotorV2Tests.cs` 里是 `R5MotorV2FormulaTests`，`R5MotorM8BTests.cs` 里是 `BunnyHopTests`、`LurchM8BTests`、`SuperglideM8BTests`、`SlopeM8BTests`，`R5MotorM5SkillTests.cs` 里是 `SkillComboTests` 等。

---

## 11.1 验收的原则

#### 原理

先定"拿什么当真值、怎么才算像"，后面的工具和数才有意义。项目的回答是：R5 本地实测是真值；同一串输入、同一套指标代码；差别要么改成 R5，要么写进存档说明为什么不改。

#### 规则和公式

1. **同输入叠图，不靠试玩**（D-25）：R5 录下的每条命令原样喂给 Unity 的身体，两边用同一套指标代码算，叠在一起比。
2. **R5 是复刻核心**（D-36）：对照找到的差别原则上改成 R5；改之前和 R5 不一样的地方写进 `R5-DIFF-ARCHIVE.md`，每项写怎么切回。
3. **差零点几个百分比可以不追，但要写出差在哪、差多少**（D-70）。没选：全追到 0；小的不记。
4. **回放电机只当尺子**（D-66）：`R5MotorV2Params.R5Reference()`（回放电机）冻结在 RUD 版，不再往里加 Reference 独有的规则；它的输出只用来防止改坏。手感对照的对象是**游戏身体** `MovementConfigs.Reference()`。
5. **不是移动代码造成的差别不改**（D-55）：例如测试工具在 dedi 上重置玩家被算成落地，导致原地跳矮 1.8 u。
6. **随机量用 R5 的种子复现**（D-35，`R5SharedRandom`）：落地 kick 这类随机，用 R5 的命令号重放，才能逐次比。
7. **每个指标事先写好容差**，判档只有一条规则（§11.2），不能看了结果再定。
8. **能证明什么要说清楚**：移动哈希只证明移动没变；EditMode 只测写下的逻辑；截图巡检是 AI 看的图；这些都不证明手感（TR §6）。

#### 实现模板

无：这一项是原则，具体做法在 §11.2 – §11.8。

#### 验收

每个差别都有编号（F-1、K-1、C-1…）、在 FEEL 或 R5-DIFF 里有一行，写明 R5 值、Unity 值、改不改、开关。

#### 出处

- D-25、D-35、D-36、D-55、D-66、D-70。main
- FEEL §1。main
- TR §4"判断真假"、§6"防止改坏"。本地，不在 git

---

## 11.2 指标和判档

#### 原理

"像不像"拆成一组可以量的数：每次起跳的速度、每段滑铲的峰值和时长、每次停下的距离……每个数单独比，差别就能定位到具体的规则上。容差同时有绝对值和相对值，取大的那个，这样小数值不会被相对容差卡死，大数值也不会被绝对容差放过。

#### 规则和公式

1. **每个指标按"每次出现"算**：每次起跳、每次滑铲、每段稳定移动各一个值。起跳和落地按地面标志算（两边同一个定义）；翻越中的行算在空中。
2. **容差** = max(绝对值, 相对值 × |R5 值|)。
3. **判档**：|差| ≤ 1 倍容差 = **一致**；≤ 3 倍 = **接近**；更大 = **不一致**；两边出现次数不一样 = **次数不同**。
4. 另外逐帧算路线偏差（水平距离的均方根）、事件（起跳、落地、滑铲开始 / 结束）的时间差，只记录，不判档。
5. "帧"：移动指标按 1/144 s（FM），镜头指标按 1/120 s（CC）。两个脚本不一样（缺口 3）。

**移动指标**（FEEL §2 的表 + FM 里另有、FEEL 没写的）

| 指标 | 定义 | 容差 [u] |
|---|---|---|
| 起跳水平速度 / 落地前速度 | 起跳那一帧 / 落地前一帧的水平速度 | 2 u/s 或 1 % |
| 跳跃高度 / 滞空时间 | 最高点 − 起跳高度；起跳到落地 | 1 u 或 2 % / 1.5 帧 |
| 滑铲峰值速度 / 时长 / 结束速度 | 每段滑铲 | 3 u/s 或 1 % / 3 帧或 3 % / 5 u/s 或 2 % |
| 地面稳定速度 | 每段 ≥ 0.4 s、全程着地、不滑铲的有输入阶段，最后 0.25 s 的平均 | 2 u/s 或 1 % |
| 加速到 90 % 用时 | 同一阶段，从开始到走完 90 % 变化 | 3 帧或 5 % |
| 停下用时 / 距离 | 松开输入后，水平速度降到 1 u/s 以下 | 3 帧或 5 % / 2 u 或 5 % |
| 空中转向角 / 速度 | 空中输入改变后 0.15 s 的方向变化和速度 | 2° / 3 u/s 或 1 % |
| 结束时速度 | 最后一帧 | 3 u/s 或 2 % |
| 翻越结束时刻（FM `mantle_end`） | 攀爬批 | 2 帧 |
| 翻越出口水平 / 竖直速度（`mantle_exit_speed` / `_vz`） | 攀爬批 | 3 u/s 或 1 % / 5 u/s 或 2 % |
| 技能峰值速度 / 水平 / 竖直（`peak_*`） | 技能批 | 3 u/s 或 1 % |
| 技能最大上升高度（`max_rise`） | 技能批 | 2 u 或 2 % |
| 到最高点用时 / 总滞空（`rise_time` / `air_total`） | 技能批 | 2 帧或 2 % |
| 落地 0.25 s 后速度（`land_after`） | 技能批 | 3 u/s 或 2 % |
| 水平位移（`travel`） | 技能批 | 5 u 或 2 % |

**镜头指标**（FEEL §8.1 的 13 个，CC 现在共 25 个键）

| 指标 | 键 | 容差 |
|---|---|---|
| 落地 kick 俯仰峰值 / 落地后横滚峰值 | `kick_peak` / `kick_roll` | max(0.3°, 10 %) |
| kick 到峰值用时 / 回到零的时刻 | `kick_t_peak` / `kick_t_zero` | max(2 帧, 10 %) / max(3 帧, 10 %) |
| 滑铲眼高最低 / 下沉用时 | `slide_eye_min` / `slide_t_eye` | 1.0 u / max(3 帧, 10 %) |
| 滑铲横滚峰值 / FOV 倍数 | `slide_roll` / `slide_fov` | max(0.3°, 10 %) / 0.005 |
| 转向横滚峰值 / 结束时横滚 | `turn_roll_peak` / `turn_roll_end` | max(0.3°, 10 %) |
| 跑步晃动俯仰 / 偏航峰峰值 | `bob_pitch_p2p` / `bob_yaw_p2p` | max(0.05°, 10 %) |
| 跑步晃动周期 | `bob_period` | max(3 帧, 5 %) |
| 起跳 kick 峰值 / 横滚 / 到峰值（K-5） | `jump_kick_*` | 角度 max(0.3°, 10 %)；时间 max(2 帧, 10 %) |
| 翻越俯仰峰值 / 到峰值（K-6） | `mantle_pitch_peak` / `mantle_t_peak` | max(0.3°, 10 %) / max(3 帧, 10 %) |
| 站立 / 冲刺眼高 | `eye_stand` / `eye_sprint` | 1 u |
| 滑索横滚峰值 / 结束 | `zip_roll_*` | max(0.3°, 10 %) |
| 钩爪横滚峰值 / 到峰值 / 逐帧 rms | `grapple_roll_*` | max(0.3°, 10 %) / max(3 帧, 10 %) / 0.5° |

R5 的落地 kick 有随机成分，同一高度不同次就差几度；只用 R5 种子重放的片段逐次比，其余只看平均值明显偏的（FEEL §8.3）。

#### 实现模板

```
verdict(unity, r5, (abs_tol, rel_tol)):
    tol = max(abs_tol, rel_tol * |r5|)
    d = |unity - r5|
    return d <= tol ? "一致" : d <= 3*tol ? "接近" : "不一致"
// 次数不同：两边事件数不等，单独一档，不做配对
```

参考实现：FM（`TOL`、`verdict`）、CC（`TOL`、`ANG = (0.3, 0.10)`、`PENDING`）。新指标加进同一张 `TOL` 表，不另写判档。

#### 验收

指标脚本本身的检查：FEEL §1 的"同一套指标代码"——R5 和 Unity 两边的值由同一个函数算；`FeelReplayTests.TheGameBodyReplayIsTheGameBodyStepped`（游戏身体回放和手动逐帧调用 `SkillBody.Step` 位置差 ≤ 1e-9）证明喂入方式不引入差别。

各批现状（FEEL）：平地 511 / 513 一致（剩 2 项是 F-2）；攀爬 1968 / 2221；技能 479 / 536；镜头 CAM2 后 332 / 361。

#### 出处

- FEEL §2、§3、§6、§7、§8.1、§8.3、§12。main
- FM、CC（`TOL` 表是数的原件）。main

---

## 11.3 回放对比工具

#### 原理

一条流水线：R5 录像变成标准片段，Unity 批处理把片段喂给几个身体、写出逐命令的结果，Python 脚本用同一套指标算分，最后放进叠图页面给人看。每一环都可以单独重跑。

#### 规则和公式

| 工具 | 做什么 | 输入 → 输出 | 开关 |
|---|---|---|---|
| `hsd_tel.py export-contract` / `check-contract` | R5 会话 → `hsdmove-trial/2` 片段；严格检查 | 会话 → `trial.json` + `samples.csv` | `--run rN` |
| `research/feel/climb_to_trial.py` | 攀爬 / 翻越会话 → 片段（翻越中没有命令的段用客户端帧补，加 `world`） | `<trials_out> <会话…>` | — |
| `research/feel/camera_to_trial.py` | 镜头会话 → 片段 + `camera.csv`（镜头额外的俯仰 / 偏航 / 横滚、眼高、FOV 倍数；落差片段按落地对齐） | `<trials_out> <会话…>` | — |
| `HSD.R5Replay.Editor.BatchReplay.Run`（Unity） | 回放电机逐命令复现 R5 | `-trial` → `<out>/<trial>/{steps.csv, summary.json, report.md}` | `-motor v2\|m1\|both`、`-scenarios`、`-legacyM2` |
| `HSD.R5Replay.Editor.FeelBatch.Run`（Unity） | 同一串命令喂回放电机、Reference、Fun | `-trial` / `-trials` → `{replay, reference, fun}.csv` | `-scenarios`、`-preGn`、`-impactBoost`、`-preD72`（`-preD72E`、`-preD72B`） |
| `HSD.Game.Editor.CameraFeelBatch.Run`（Unity） | Reference 身体 + 原生镜头 | `-trials` → `reference.csv`（GN 起另有 `body.csv`） | `-preF7Roll`、`-preGn`、`-preCam2`、`-preFnd`、`-preK8`、`-preDjPunch`、`-preD72*` |
| `research/feel/feel_compare.py` | 移动指标打分 | `<feel_out>[,<dir2>] <trials…>` → 档位表 | `--json`、`--series`、`--export` |
| `research/feel/camera_compare.py` | 镜头指标打分 | `<camera_out> <trials>` → 档位表 | `--json`、`--export` |
| 叠图页面"R5 手感对照" | 选片段叠画水平速度、高度、俯视路线；"不一样的地方"表、按指标统计 | `scorecard.json`、`trials.json`、`series*.json` | claude.ai 页面，**不在 git** |

- `-pre*` 开关：每次改游戏身体都留一个"切回旧版"的批处理开关，开关下输出必须和改前逐字节相同（例：`-preD72` 606 个片段的 1212 个输出；`-preFnd` 181 个镜头片段；`-preCam2` 166 个旧片段）。
- 提交：`research/feel/data/scorecard.json`、`trials.json` 进 git；`series*.json`（3 – 5.5 MB）能重新生成，不提交。
- TF2：`tf2/runtime/t5_metrics.py`、`night_match.py` **只算量、只打印，没有容差**；TF2 规则对不对靠"规则和实测的差是常数 = 一帧半步重力"这类判断（PD M-1）。

#### 实现模板

重跑顺序（FEEL §5、§8.5）：

```
FeelBatch.Run -trial <M1/M2/M3 trials> -out <out>
feel_compare.py <out> phase2-local/m1/trials phase2-local/m2/trials phase2-local/m3/trials --export feel/data
# 攀爬批：climb_to_trial.py <trials_out> <会话…> → FeelBatch.Run -trials <trials_out> -out <out2> → feel_compare.py <out>,<out2> …
# 镜头批：camera_to_trial.py → CameraFeelBatch.Run -trials -out <cam_out> → camera_compare.py <cam_out> <trials_out> --export <dir>
```

操作细节和坑在 [附录 A §A.7](A-research-methods.md)。

#### 验收

同一批片段重跑两次，`scorecard.json` 除时间戳外不变。

#### 出处

- FEEL §1、§4、§5、§6.1、§8.1、§8.5、§9.7、§10.3。main
- `research/phase2-prep/UNITY-DATA-CONTRACT.md`（片段格式）。main
- HSD-Unity：`Assets/HSD/R5Replay/Editor/BatchReplay.cs`、`FeelBatch.cs`、`Assets/HSD/Game/Editor/CameraFeelBatch.cs`、`Assets/HSD/R5Replay/Runtime/FeelReplay.cs`。main

---

## 11.4 回放回归和哈希

#### 原理

改一处代码，可能悄悄改了别处的移动。最可靠的检查是：**同一批 R5 录像，改前改后跑一遍，输出逐字节相同**。只要有一个字节不同，就说明移动变了。基线不是不能动，但动之前要证明"没有变差"，变差的每一项要查清原因、用户同意，并且旧版要能用开关逐字节复现。

#### 规则和公式

1. **回放电机基线（RUD，现行）**：`BatchReplay` 在 M2 + M1（`-motor both`）、M3、M4（`-scenarios`）三组录像上的全部输出，共 **426** 个文件的 sha256（m2m1 222、m3 90、m4 114）。
   - `steps.csv` 按原始字节算；`.md` / `.json` 先把 CRLF 换成 LF；跳过 `index.md`（带生成时间）和 `*.log`。
   - `rud_check.py <运行目录>`：每组 identical / different / missing / extra 计数，全同退出码 0，否则 1。
2. **旧基线**（必须仍能复现）：`BatchReplay -legacyM2` 跑 M2/M1 111 / 111、M1 首猜 111 / 111、M3 90 / 90、M4 114 / 114 逐字节相同（`m4/unity/regression_check.py`、`m5/unity/m4_replay_check.py`）。RPS 基线（D-47）426 条只作"改前"留档。
3. **游戏身体**：`FeelBatch` 105 个录像 × replay / reference / fun = **315** 个输出和改前逐字节相同。**这一批没有提交的清单**，只能改前改后各跑一次比（缺口 4）。
4. **合计 741**（426 + 315）。实际跑出 744 个文件，去掉 3 个带生成时间的 `index.md`。
5. **演示**：真实按键演示 238 / 238（`-smoke`）；课程单圈 78.88 s（D-72 后 78.883 s）。
6. **什么时候能动基线**：
   - D-66 以后**回放电机冻结**，所有改动只改游戏身体，回放基线不许动；
   - 改游戏身体时，只有预期的片段变，旧版留 `-pre*` 开关且开关下逐字节相同；
   - 真要重定回放基线（只有改回放电机本身才会）：按"变差"判据，**任何一项增加超过 1e-6 就算变差**：位置 / 高度 / 速度 / 水平 / 竖直速度的 rms 和最大值、起跳竖直速度、最高点误差、着地 / 滑铲 / 冲刺 / 上限状态不一致的命令数；或事件时刻误差总和变大（`rud_compare.py`）。
7. **重定基线要交的东西**：改前 / 改后逐录像对照表（`unity/before_after.md`）；变了的和例外录像的完整输出（`unity/changed/<录像>/`）；旧电机做成开关（`-legacyM2`）且旧基线逐字节复现；DECISIONS 写 D 行；R5-DIFF 记一节；`rud_check.py --write` 重写清单。
8. **RUD 的例外**（用户同意，D-49）：M2 `e1_turn` r331、r332（"最高速度出现在第几条命令"由 1e-13 级浮点噪声决定，速度贴在 299 平台上）；M3 `e8_hop350_d0` r1237（沙盘第 498 条离地 2.075 u，刚超出原生 2.0 u 着地探测，晚一条命令着地，丢一次连跳；**不调参数掩盖**）。
9. **战斗层不动移动**：不装道具时所有移动演示逐帧相同、741 个文件不变（`CombatBaseTests.EmptyCombatLeavesEveryDemoByteIdentical`）。

#### 实现模板

```
# 改代码前后
BatchReplay.Run -motor both -trial <M2,M1> -out <run>/m2m1
BatchReplay.Run -motor v2   -trial <M3>    -out <run>/m3
BatchReplay.Run -motor v2   -trial <M4> -scenarios m4/unity/scenarios.json -out <run>/m4
py -3 research/phase2-local/rud/rud_check.py <run>                 # 426 identical，退出码 0
FeelBatch.Run … (改前一次、改后一次) → 315 个文件逐字节比
```

坑：参数列表文件是 CRLF 时，bash 读进来每个参数带 `\r`，Unity 什么都不跑、退出码仍是 0、不写输出，"相同"其实是 0 对 0。先去掉 `\r`，**跑完数文件数**。`BatchReplay` 退出码：0 全部跑了，1 有录像读不了 / 回放不了，2 参数错；路径要绝对路径。

#### 验收

`rud_check.py` 退出码 0（426 identical）；FeelBatch 315 个逐字节相同；`-legacyM2` 旧基线逐字节相同；文件数对（744 − 3）。

#### 出处

- RUD、RPS（README、脚本、清单、`before_after.md`）。main
- D-47（RPS）、D-49（RUD 和三个例外）、D-66（回放电机冻结）。main
- `research/phase2-local/m4/unity/regression_check.py`、`m5/unity/m4_replay_check.py`。main
- DECISIONS"现在的状态"（741、238 / 238、78.88 s）。main
- HSD-Unity `titan/integration` 的 `README-terrain.md` 固定步骤第 6 条（CRLF 坑、744 个文件）。HSD-Unity PR #78（draft），还没合并

---

## 11.5 自动测试

#### 原理

叠图对照要跑游戏、跑批处理，一次几十分钟；自动测试几分钟跑完，每次改代码都能跑。它们守住三类东西：**公式本身**（起跳速度、半步重力、滑铲衰减逐条命令对）、**和 R5 对照过的数**（某个实测值 ± 一个小容差）、**不变量**（帧率无关、模拟不被镜头改动、什么都不装时身体逐字节不变、随机按 30 s 后所有技能都能回到空闲）。

#### 规则和公式

| 类 | 是什么 | 例子（`类名.方法名`） | 规模 |
|---|---|---|---|
| EditMode：公式 | 一条规则的逐命令值 | `R5MotorV2FormulaTests.JumpRemovesOneAndAHalfGravitySteps`、`GravityHalfStep`（≤ 1e-12）、`SlideBoostCapAndGain` | 2335 / 2335（PR #88 分支上，11-14） |
| EditMode：R5 对照 | 实测值 ± 容差 | `GrappleM10ATests.NoInputWallPullFollowsTheRamp`、`SuperglideM8BTests.SprintSuperglideLeavesAt460AtEveryMeasuredHeight`、`OctaneM10CTests.StimMatchesTheR5Regression` | 同上 |
| EditMode：不变量 | 帧率无关、模拟不被表现层改动、空装备不改身体 | `PracticeSessionTests.SameCommandsAtAnyFrameRateGiveTheSameState`、`NativeCameraTests.TheSimulationIsUntouchedAndTheAimIsRaw`、`CameraFeedbackTests.FeedbackAndVisualsAtMaxLeaveTheSimulationBitIdentical`、`CombatBaseTests.EmptyCombatLeavesEveryDemoByteIdentical` | 同上 |
| EditMode：随机 | 随机输入 30 s + 松手 12 s，全部 Idle 并站在地上 | `SkillFuzzTests.PathfinderOctane` 等（每个预设 5 个种子） | — |
| EditMode：帧率 | 同一串输入 60 / 144 Hz | `SkillFrameRateTests.AllPresetsAt60And144Hz` | — |
| EditMode：演示不作弊 | 演示轨迹 = 录下的输入直接喂 `SkillBody.Step` | `MovementDemoTests.DemoTrajectoryEqualsTheRecordedInputsThroughSkillBodyStep`、`DemoProbeAndVisualCodeHaveNoSimulationWrites` | 12 / 12 |
| PlayMode | 场景里的游戏 | `PracticeGamePlayModeTests`（演示行数 = 2 × 演示数） | — |
| 冒烟 | 无界面跑路线和演示 | 游戏 `-smoke` → `[HSD-SMOKE] ok` | 238 / 238 |
| 参数表校验 | 手册总表和 Unity 导出逐行对 | `handbook/tables/check_params.py`（分支 `handbook/tables`，还没合并） | 150 行参数、38 行关卡尺度、76 行镜头事件 |
| 单位：[u] 不变 | u 模式下 869 个批处理输出逐字节和改前相同 | 批处理输出比对 | 869 |
| 单位：u ↔ m 等价 | 同一段输入 u 跑一次、m 跑一次 | `UnitsEquivalenceTests.MetersRunEqualsResearchRun`、`M55CameraMetersEqualsResearchRun`、`Tf2DoubleJumpMetersEqualsResearchRun`、`BuildTimeLimitsAreConvertedWithTheBody` | 10 段验收 + 119 个演示 |
| 单位：标记和拒绝 | 每个数值字段有量纲标记；R5 对照在 m 下报错 | `UnitsTests.EveryNumericFieldIsMarked`、`ReplayAndShortRangeEvalRefuseMeters`、`BatchEntryPointsSwitchBackToResearch`、`ReplayInResearchUIsUnchangedByTheSwitch`；`UnitsEquivalenceTests.CameraFeelReplayRefusesMeters` | — |

`check_params.py` 查：表里的参数名还在 Unity 导出里、量纲和单位没变、"Unity 现在的值"等于导出、导出自己的 [m] = [u] × 0.0254^k、表里的 [m] 和身高比例是从 R5 原值算对的、"和 R5 一致吗"和两个数对得上。对不上打印每一处、退出码 1。什么时候跑：HSD-Unity 合并了动参数的 PR、或者改了单位标记以后，重新导出（`HSD.Game.Editor.UnitsExport.Run`）再跑。

单位等价的容差：位置 / 眼高差 < `PosTolM` = 1e-4 m，镜头角度差 < `AngleTolDeg` = 1e-6°，事件逐条相同；实测最大 2.2e-12 m、2.2e-12°。119 个演示里 118 个等价；`wall_bounce` 差 4.6 mm，是 `AirAccelerate` 里 `add <= 0` 的浮点边界分叉，不是单位换错；为了 u 模式逐字节不变没改电机。

#### 实现模板

新功能至少写三条测试：一条公式、一条 R5 对照（实测值 ± 容差，容差写进 §11.6）、一条不变量（开关关掉时旧行为逐字节不变）。Unity 批处理不要按进程名杀（别的会话可能在用同一个编辑器），用 `-quit` 让它自己退。

#### 验收

EditMode 全绿；PlayMode 全绿；`-smoke` ok；`check_params.py` 退出码 0；单位等价全部通过（除已知的 `wall_bounce`）。

#### 出处

- HSD-Unity 测试目录（main）；单位测试在 HSD-Unity PR #88（`units/switch`），还没合并：US §3.3、§3.5、§5、§6；`Assets/HSD/Game/Runtime/Units/UnitsEquivalence.cs`。
- `handbook/tables/check_params.py`、`handbook/tables/README.md`。分支 `handbook/tables`，还没合并
- M55A §1、§2（M5.5 镜头的不变量）。main
- 00-INVENTORY 第 11 章（测试文件数）。

---

## 11.6 合格线总表

#### 原理

各章每一项都写了自己的合格线，但散在十几章、几十个 D 行、几百个测试里。这张表把它们收在一起：**以后改任何一处，先查这里，知道它要守哪条线、哪个测试在守**。表里的线按三种来源：手册章节（已经核过）、测试代码里的容差（实际在执行的）、D 行和研究文档（定下来的规矩）。章节写的线和测试的线不一样时，两个都写，并在 `_notes` 里报出来。

#### 规则和公式

- 线写的是"Unity 和 R5（或公式）差多少算合格"，单位都是 u 模式（泰坦模型的线是 [m]，已标）。
- "检查"列：`类名.方法名`（EditMode 测试）、脚本名，或"人工"。
- "出处"列：章节 §、D 行、文档；没合并的写 PR 号。
- 只收已经存在的线。

**原件是 [`tables/pass-lines.tsv`](tables/pass-lines.tsv)**（185 行），这里是给人看的摘要。TSV 的列：`id`（PL-001 …）、`领域`、`章`、`节`、`量`、`合格线`、`检查`、`出处`、`在哪`、`来源`（章节 / 脚本容差 / 测试 / D行 / 重建检验）。

- PL-001 – PL-055：不属于某一章的线（总口径、FM / CC 的容差、技能和 AI、单位、泰坦模型、TF2、流水线、重建检验），手写。
- PL-056 – PL-185：从 02、03、04、05、06、07、08、09、12 各章每一项"验收"段里的"合格线"一句逐条摘出来（02 7、03 13、04 13、05 47、06 13、07 3、08 9、09 23、12 2），"检查"列是同一段里写到的测试名。各章分支：`handbook/ch02` – `ch09`（12 章在 `handbook/ch08`），都还没合并；摘的是 11-14 晚上的版本（ch05 3be1917、ch06 63dad4f、ch08 16190c0、ch09 d4c4944）。章节改了合格线，要重新摘。
- 有的行写的是"还没有合格线"（例：03 §3.11 起跳缓冲、09 §5.2 扩散分布），照原样保留，提醒这里是空的。

**总口径**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 任一移动 / 镜头指标 | 差 ≤ max(绝对, 相对 × \|R5\|) = 一致；≤ 3 倍 = 接近 | FM / CC `verdict` | FEEL §2；§11.2 |
| 回放电机输出 | 426 个 sha256 全同 | `rud_check.py` | D-49；RUD |
| 游戏身体输出 | FeelBatch 315 个逐字节相同（除非这次就是要改游戏身体，且旧版 `-pre*` 开关下逐字节相同） | 改前改后比对 | DECISIONS"现在的状态" |
| 重定回放基线 | 判据中任一项增加 ≤ 1e-6；否则查原因 + 用户同意 | `rud_compare.py` | RUD；D-47、D-49 |
| 和 R5 的差别 | 差零点几个百分比可以不追，但要写出差在哪、差多少 | R5-DIFF 二节 | D-70 |

**底层（02 章）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 帧率无关 | 30 / 60 / 75 / 144 / 240 fps 加每帧 ±20 % 随机，同样命令数下位置、速度逐位相同 | `PracticeSessionTests.SameCommandsAtAnyFrameRateGiveTheSameState`；`MovementDemoTests.DemoIsFrameRateIndependent` | 02 §2.1 |
| 每条命令的顺序 | 改顺序后公式测试（半步重力 ≤ 1e-12）和回放基线逐字节不变 | `R5MotorV2FormulaTests.GravityHalfStep`、`JumpRemovesOneAndAHalfGravitySteps`、`LandsWithinGroundProbeAndSnapsOnNextGroundCommand`；`rud_check.py` | 02 §2.2 |
| 碰撞体站 / 蹲 | 测试通过；RUD 基线不变 | `MovementWorldTests.CrouchedHullFitsUnderALowCeilingAndStaysCrouched` | 02 §2.4 |
| 扫掠碰撞 | 2 u 厚墙在 900 / 20000 u/s、60 / 120 / 144 Hz 下正好停在面上 | `MovementWorldTests.NoTunnellingThroughThinWallsAndCeilings` | 02 §2.5 |
| 地面检测 | 原生向下探测 2.0 u；回放基线不变 | `MovementWorldTests.GroundProbeOnBoxRampAndSteepRamp` | 02 §2.6 |
| 台阶 | 18 u 支撑、18.1 u 不支撑；和 M5.5 方盒规则在 20 万个点上相同 | `WorldEquivalenceTests.SupportAndBlockedMatchTheM55BoxWorldOnTheMap` | 02 §2.7（缺"走上台阶"整段测试） |
| 斜坡 | 比例和高度按公式到 1e-6；对 R5 高度差 ≤ 0.2 u、比例差 ≤ 0.005 | `R6USlopeTests.UphillStepAndRestHeight` 等 | 02 §2.8 |
| 换世界实现 | 冒烟路线和每个演示逐位相同 | `WorldEquivalenceTests.SmokeRouteIsBitIdenticalToTheM55BoxWorld`、`EveryDemoIsBitIdentical` | Unity 测试 |

**地面、空中、跳跃、lurch（03 章）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 速度上限 | 稳定速度和上限差 < 0.01 u/s（199.525 / 299 / 92） | `R5MotorV2FormulaTests.CapsWalkSprintCrouch` | 03 §3.1 |
| 地面稳定速度 | 2 u/s 或 1 % | FM `ground_terminal` | FEEL §2 |
| 三段加速 | 开环每条命令误差 ≤ 0.015 u/s；加速到 90 % 用时 3 帧或 5 % | `R5MotorV2FormulaTests.AccelBandsFollowPreMoveSpeed`；`N7NativeReferenceTests.SprintAccelBandStartsAtTheFixedEdge`；FM `accel_time90` | 03 §3.2 |
| 冲刺 | 按下到 299 的时间差 ≤ 3 帧；稳定 299.000 | `R5MotorV2FormulaTests.SprintFlagSetOneCommandAfterThePress` | 03 §3.3 |
| 摩擦、减速、按键急转 | 停下每条命令误差 ≤ 0.01 u/s；急转逐命令 rms ≤ 0.05 u/s；停下用时 3 帧或 5 %、距离 2 u 或 5 % | `R5MotorV2FormulaTests.DecelIsConstantNotScaledAndSnapsBelowOne`；`N7NativeReferenceTests.NativeGroundStepTurnsGraduallyAndAppliesTheInputCurve`；FM `stop_*` | 03 §3.4；账本 G-07 |
| 蹲走 | 上限 92.000；停下 9 条命令 | `R5MotorV2FormulaTests.CapsWalkSprintCrouch` | 03 §3.5 |
| 空中加速和转向 | 每条空中命令 rms ≤ 0.005 u/s、最大 ≤ 0.015；冲刺跳水平净增 0.30 ± 0.05 u/s；空中转向 2° / 3 u/s 或 1 % | `R5MotorV2FormulaTests.AirAccelCappedAtAirSpeedTimesMoveScaleWithoutDrag`；`N7NativeReferenceTests.ExtraAirAccelAddsTwoAtTheCapUnderThe3DLimit`；FM `air_turn*` | 03 §3.6 |
| 重力半步积分 | Δz 每条命令误差 ≤ 0.002 u | `R5MotorV2FormulaTests.GravityHalfStep` | 03 §3.7 |
| 起跳 | 起跳速度和 289.83 u/s 差 < 0.05 u/s；144 fps 最高点和 54.95 u 差 < 0.1 u；连跳系数和 frac(t) 差 < 0.01；超速连跳出口和 max(299, h − 100) 差 < 0.01 u/s；跳高 1 u 或 2 %、滞空 1.5 帧 | `R5MotorV2FormulaTests.JumpRemovesOneAndAHalfGravitySteps`、`MultiJumpPenaltyFraction`；`N7NativeReferenceTests.OverCapHopLosesAHundredWithinTheSkipTime`；FM `apex_rise`、`air_time` | 03 §3.8 |
| 起跳 / 落地前水平速度 | 2 u/s 或 1 % | FM `takeoff_speed`、`land_speed` | FEEL §2 |
| 落地 | 落地命令差 ≤ 1 条；硬着陆后速度和拟合差 ≤ 0.5 % | `LandingSlowdownTests.ImpactFactorMatchesTheFit` | 03 §3.9 |
| 兔跳 | 同起跳；冲刺兔跳 299 ± 0.02 | `BunnyHopTests.*` | 03 §3.10 |
| 起跳缓冲 | **还没有**（B03-2 实验以后） | — | 03 §3.11 |
| lurch | 窗口外逐命令误差 ≤ 0.01 u/s，衰减段 ≤ 0.35 u/s；三键组合 −31.9 ± 0.5° | `R5MotorM3LurchTests.*`；`InputM10DTests.ThreeKeyCombinationsFollowTheMeasuredRule` | 03 §3.14 |
| tap strafe | 0.25 s 一段最终航向差 ≤ 2°（**测试用 ±8°**） | `LurchM8BTests.TapStrafeAt720And1440DegreesPerSecondFollowsTheViewAndKeepsTheSpeed` | 03 §3.15 |
| 反向 lurch（LS / RAS） | 和 R5 差 3° 以内，不改 | 对照 L-11 | D-40 |
| 结束时速度 | 3 u/s 或 2 % | FM `end_speed` | FEEL §2 |

**滑铲、翻越、superglide（04 章）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 滑铲峰值 / 时长 / 结束速度 | 3 u/s 或 1 % / 3 帧或 3 % / 5 u/s 或 2 % | FM `slide_*` | FEEL §2 |
| 起滑加成 | 峰值和 min(s + 172.5, 460) 差 < 0.01 u/s；0 / 1.0 / 2.5 s 序列加成 1 次 | `R5MotorV2FormulaTests.SlideBoostCapAndGain`；`N7NativeReferenceTests.SlideBoostCooldownCountsFromTheLastSlideStart` | 04 §4.1 |
| 衰减和转向 | 逐命令速度和 (s − 100·dt)·0.7^dt 差 < 0.01 u/s；1 s 侧向转向横向 41 ± 1 u/s（**测试 ±1.5**） | `R5MotorV2FormulaTests.SlideDecayEndAndCrouchOverspeed`；`N7NativeReferenceTests.SlideSteeringMatchesTheN4CLateralGrowth` | 04 §4.2 |
| 松蹲结束 | 结束命令差 ≤ 1 条；之后速度差 < 1 u/s | `SlideM10DTests.CrouchReleaseEndsTheSlideAtOrBelow350WithTheStrongerDecel` | 04 §4.3 |
| 再次加速 | 二次加成时刻差 ≤ 0.05 s、速度差 ≤ 2 u/s；2 s 内跨接缝不加速 | `R6USlopeTests.GroundEntityChangeRebeginsTheSlide` | 04 §4.4；D-46 |
| 斜坡滑铲 5 – 40° | 逐命令额外加速度和 750·sinθ·cosθ 差 < 1 u/s²（**测试：R5 拟合 ±4 %**）；上坡滑行距离差 < 2 u；转折处离地 0 条 | `SlopeM8BTests.ReferenceSlopeSlideMatchesTheR5FitWhereItWasMeasured`；`R6USlopeTests.SlideSlopeTermOnAGentleSlope` | 04 §4.5；账本 S-09 |
| 滑铲跳 | 起跳后水平速度差 < 1 u/s（1.0 s 那行 < 3 u/s）；退还边界在 0.201 / 0.215 s 之间 | `FeelReplayTests.ASlideJump0201sAfterTheDuckPressIsRefunded`、`ASlideJump0215sAfterTheDuckPressKeepsTheBoost`；`SlideM10DTests.SlideJumpExitFollowsTheMeasuredAgeTable` | 04 §4.6；D-26 |
| 眼高 / 蹲姿碰撞体 | 0.2 s 内到 32 ± 1 u；空中松蹲原点下降 16.5 ± 0.1 u，在离地 0.08 s 以后 | `NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt`；`NativeTraversalTests.TheEyeFollowsTheMeasuredDuckCurves` | 04 §4.8 |
| 翻越检测 | 每个墙高的结果类别和 R5 一样；台沿高度差 < 1 u | `A2Climb.*`；`FeelReplayTests.TheLedgeProbeHasNoDeadZoneAboveTheReach` | 04 §4.9；D-27 |
| 攀爬 | 满爬时长差 ≤ 0.01 s；终点高度差 ≤ 0.2 u | `A2Climb.ShortClimbThenMantle` 等 | 04 §4.10 |
| 翻越时长和出口 | 时长差 ≤ 0.03 s；出口 299 / 199.525 ± 0.01；攀爬批：结束时刻 2 帧、出口水平 3 u/s 或 1 %、竖直 5 u/s 或 2 % | `FeelReplayTests.TheMantleEndLeavesAtTheStanceSpeed`；FM `mantle_*` | 04 §4.11；D-28 |
| 蹲着翻越 | 按类平均时长差 ≤ 0.05 s（h120 S / A 类除外）；站姿时长不变 | `NativeTraversalTests.*` | 04 §4.12；D-75 |
| superglide | 窗口中间出口 460.000 ± 0.01；切断 / 起跳分界在剩余 0.1025 s（R5 混合区 0.086 – 0.12 s）；滑铲后 < 2 s 不给 | `SuperglideM8BTests.SprintSuperglideLeavesAt460AtEveryMeasuredHeight`、`TheTimeLeftDecidesCutSuperglideOrPlainJump` | 04 §4.13；D-31 |
| S27 翻越加速 | 每类窗口秒数在 R5 ± 0.02 s；站姿 0.09 – 0.18 s、蹲姿 0.15 – 0.50 s（守护测试） | `MantleBoostS27Tests.TheWindowOpensWhereR5OpensIt`、`TheLiveConfigsKeepTheStandingWindowInTheR5Range`、`TheLiveConfigsKeepTheCrouchedWindowInTheR5Range` | 04 §4.14 |

**技能层、战斗层（10 章），以及直接从测试收的外力技能行（和上面 05 章的行有重叠，以 05 章为准）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 技能批指标 | 峰值速度 3 u/s 或 1 %；最大上升 2 u 或 2 %；到最高点 / 总滞空 2 帧或 2 %；落地 0.25 s 后 3 u/s 或 2 %；水平位移 5 u 或 2 % | FM `peak_*`、`max_rise`、`rise_time`、`air_total`、`land_after`、`travel` | FEEL §7 |
| 钩爪拉力 | 无输入拉动跟 min(800, 50 + 500t) ± 12 u/s；侧键弹弓 941 ± 5 %；跳钩出口 1015 ± 5 %；按住 W 夹到 483 ± 0.01；视线离开 0.575 ± 0.03 s | `GrappleM10ATests.NoInputWallPullFollowsTheRamp`、`SideKeysDuringTheSlingshotPullAddSpeed`、`JumpGrappleNeedsTheJumpInsideTheWindup`、`HoldingWClampsTheWishComponentAt483`、`LookingAwayReleases` | Unity 测试 |
| 钩爪原生拉力 | 72 个片段速度误差 rms 2.08 u/s（旧 2.68） | 逐命令推演 | FEEL §9.1；D-34 |
| 钩爪脱钩 | 低速超时 1.5 ± 0.02 s | `GnGrappleTests.G4StrafingAcrossTheRopeTimesOutAtTheAirLimit` | D-50 |
| 撞上上抬（G-6） | 默认关 = R5；打开时 105 个录像和 GN 版逐字节相同 | `GnGrappleTests.G6ImpactBoostIsOptInAndOnlyOnWorldHooks` | D-52 |
| 滑索枪 | 枪绳到 1000、出口 600 ± 0.5；超级跳 564 ± 10 | `ZiplineGunM10BTests.AGunRopeRampsTo1000AndExitsAt600LikeR5`、`TheSuperJumpWorksFromTheBeginStation` | Unity 测试 |
| 兴奋剂 / 跳板 | 兴奋剂起滑 594.7 ± 0.5；兴奋剂兔跳 420.95 ± 0.1；蹲着跳板竖直 813.17 ± 0.01；天花板滑行 514.3 ± 1.5 | `OctaneM10CTests.StimMatchesTheR5Regression`、`PadLaunchesStraightUpWithoutMotionAndFlatWhenCrouched`；`M10CGameTests.EveryCeilingLaneSurfsInBothConfigs` | Unity 测试 |
| Wraith | 冲刺 415.01 对 R5 414.98；传送门寿命 45 s ± 1 帧 | `SpeedBoostM10WTests.TheOlderStimAndPhasePresetsAgreeWithTheRuleOrAreReported`；`RiftM10WTests.PortalsLiveFortyFiveSeconds` | Unity 测试 |
| 蹬墙反弹 | 无输入沿法线 −257.86 ± 0.01；朝墙 −107.70 ± 0.01 | `WallBounceTests.NoInputGoesAlongTheNormal`、`ForwardIntoTheWallSubtractsBackAddsAndMagnitudeIsIgnored` | Unity 测试 |
| 翻越跳朝墙推（J-1） | 翻越跳 299 ± 0.01 | `J1SurfacePushTests.AMantleJumpAfterTouchingTheFaceGainsThirty` | D-23 |
| 技能组合 | 全部通过；随机 30 s + 12 s 后全部 Idle、站在地上 | `SkillComboTests.*`、`SkillFuzzTests.*` | 10 §10.2、§10.4 |
| 减速语义 | W2 实测速度由读回严重度算出；同类取最大；冲刺门槛 0.05 | `CombatFrameworkTests.TheMeasuredR5SpeedsComeOutOfTheReadBackSeverities`、`ASlowAboveFivePercentBlocksTheSprint` | 10 §10.6（HSD-Unity PR #53，还没合并） |
| 战斗层不动身体 | 什么都没装时身体逐字节不变 | `CombatControlTests.NothingActingIsAnExactNoOp`；`CombatBaseTests.EmptyCombatLeavesEveryDemoByteIdentical` | 10 §10.5 |

**跑墙、滑索、外力（05 章，摘要；全部 47 行见 TSV PL-089 – PL-135）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 跑墙关卡尺度 LS-18 / 19 / 20 | 改动以后 549.84 / 535.67 / 701.03 u 不变（差 < 1 u），除非改动就是要改它们 | `Tf2WallRunTests.DefaultsStayM7AndThePresetsCarryTheSpecValues` | 05 §5.1 |
| TF2 跑墙中 | A 的水平稳定速度 375 ± 4 %；重力系数和 1 − f(1 − t/T) 差 ≤ 0.03 | `Tf2WallRunTests.PresetAHorizontalSettlesNear375AndBNear225` | 05 §5.3 |
| HSD 跑墙（游戏默认） | 随机测试里蹬墙跳水平速度 ≤ 480；沿墙速度 ≤ max(进入, 345)；LS-18 = 549.84 ± 1 u | `WallRunTests.*` | 05 §5.7 |
| TF2 二段跳 | 水平和 T5 差 ≤ 0.2 u/s；竖直"换成"分支和 300 差 < 1e-6；LS-22 = 114.8 ± 0.5 u | `Tf2SuperJumpTests.T5TrialsAreReproduced` | 05 §5.9 |
| 挂上滑索 | 抓点差 ≤ 1.6 u；视锥 33.18° 必须挂、35.94° 必须拒；候选距离 115.6 挂、128.0 不挂 | `A3Zipline.FindRuleMinimumAngleWithinRadiusAndCone` | 05 §5.15 |
| 滑索滑行 / 到端 | 每条命令速度和时间线差 < 0.01 u/s；1.243 – 1.257 s 内到 600；到端 600 精确、离端点 90 – 95 u 脱离 | `A3Zipline.RideProfileMatchesTheMeasuredCurve`、`AutoDetachNinetyBeforeTheEndAt600` | 05 §5.18、§5.21 |
| 钩爪发射和拉 | 挂上 / 开拉的命令和 t0 + L/2035、+0.2005 s 差 ≤ 1 条；无输入拉动和 S(t) 差 ≤ 4.2 u/s；按住 W 483.000 ± 0.01 | `GrappleTests.AimFromEyeAttachHopWindupAndPullTiming`；`GrappleM10ATests.NoInputWallPullFollowsTheRamp` | 05 §5.25、§5.26 |
| 钩爪自动脱钩 | 往墙上拉的脱钩命令差 ≤ 2 条、最高点差 ≤ 1.0 u；天花板超时 1.5 ± 0.02 s；回放基线不变 | `GnGrappleTests.*` | 05 §5.27 |
| 跳板 | 发射后第一帧速度和公式差 < 0.01 u/s、角度 < 0.1°；站着发射最高点和 707.8 u 差 < 1 u | `JumpPadTests.LaunchFormula`、`ApproachLaunchSlowMoFlightAndHardLanding` | 05 §5.32、§5.33 |
| 兴奋剂 | 倍率和 1.298038 差 < 2e-6；冲刺上限 420.954 ± 1e-3 | `StimTests.BoostAndFadeShape` | 05 §5.36 |
| 爆炸击退 | 衰减和 R5 / TF2 差 ≤ 0.01；满额 Δv = 推力 / 100；门槛两侧 310 / 315 结果和 R5 相同；741 个文件开关开 / `-preRJA` 都和 main 逐字节相同 | `RjaKnockbackTests.*` | 05 §5.37 |
| Wraith 虚空 / 传送门 | 平台 msc 和 1.596078 差 < 1e-4；冲刺 414.98 ± 0.05；出口速度 0；放置冲刺 364 / 415 / 468 / 519 各差 < 0.05 u/s | `VoidM10WTests.TheVoidTimelineMatchesTheR5MoveScale`；`RiftM10WTests.*` | 05 §5.42、§5.43 |
| 升梯 / 喷气 / 突袭 | 弹出 450 / 400 差 < 0.05、悬停 0.500 ± 1 条；喷气一步残差 rms ≤ 0.05 u/s；突袭速度误差 ≤ 2 u/s、角度 ≤ 0.01° | `GravityLiftTests.*`、`JetpackTests.*`、`PounceM9BTests.*` | 05 §5.47、§5.49、§5.50 |

**动量、仲裁、输入（06 章，摘要；全部 13 行见 PL-136 – PL-148）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 速度上限 | R5 实测里的每个动作在对应装备上不被夹；随机测试 0 次越过天花板 | `SkillComboTests.CeilingClipsALongGrapplePull`；`M7FuzzTests.*` | 06 §6.3 |
| 驱动者和跳键 | 随机测试 0 次"两个驱动者"、0 次双重效果、0 次超时以外的卡住 | `JumpArbitrationTests.*`、`SkillComboTests.*` | 06 §6.7 – §6.10 |
| 按键边沿 / 逐键输入 | 松开永远不产生边沿；没有相反键时键写法和轴写法逐位相同；组合 lurch 角度差 ≤ 0.5° | `InputM10DTests.*` | 06 §6.11、§6.13、§6.15 |
| 游戏侧采样 | 任意帧率下同样的按键序列得到同样的状态；每格滚轮一个边沿 | `M6GameTests.ATapInsideOneFrameIsAOneCommandPress` | 06 §6.14 |

**身体动画和泰坦电机（08、12 章，摘要；PL-152 – PL-160、PL-184 – PL-185）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 持枪姿势 | 站立枪口和 HP-POSE 差 < 0.1 u、角度 < 0.5° [设计] | `CombatHoldPoseTests.EveryGunThatShowsAModelHasAMeasuredHold` | 08 §1.2 |
| 冲刺姿势 | 平均姿势枪口差 < 0.5 u、角度 < 1°；波形角度中位差 < 1.5° [设计] | `CombatHoldPoseTests.SprintIsThePoseOfThatGun` | 08 §1.4 |
| 转视角枪超前 | 233 °/s 稳定时 2.44 ± 0.2°；停转 0.6 s 时 < 15 % [设计] | `CombatHoldPoseTests.TheGunLeadsATurn` | 08 §1.7 |
| 泰坦脚滑 | 走路路线 ≤ 2 × 平地（中型 9.9、重型 2.2 m / 100 m） | `TitanAnimTests.PlantedFeetBarelySlide` | 08 §2.2 |
| 泰坦镜头 | 峰值差 < 5 %、时间形状对上 | `TitanCamTests.*` | 08 §3.1 |
| 泰坦地面速度 / dash | 各时间和 T0 / 713 差 ≤ 0.02 s；dash 后 0.3 s 速度差 ≤ 5 u/s | `TitanMotorTests.NoughtToWalkSpeedAsT0`、`DashIsAtOnceHeldThenDownAtSprintDeceleration` | 12 §1.1、§2.1 |

**战斗手感（09 章，摘要；全部 23 行见 PL-161 – PL-183）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 开一枪 | 第一发偏移 0（逐位）；射速和字段差 < 3 % | `CombatWeaponTests.*` | 09 §1.1 |
| 武器 punch 弹簧 | 到 50 % 的时间差 ≤ 0.02 s（已知例外 R-301 开镜 0.04 s） | `CombatWeaponTests.TheSpringStepIsExact` | 09 §2.1 |
| 每发 kick | 幅度比差 ≤ 0.1；方向逐发一致；D-94 缩放和 R5 差在 ±0.2 噪声内 | `CombatWeaponTests.ANegativeTableYawGoesRight` | 09 §2.2、§2.3 |
| 开镜 | zf 到 1 = `zoom_time_in` ± 1 命令；R-301 FOV 曲线差 ≤ 0.01°；枪的路径差 ≤ 0.05 u | `CombatWeaponTests.TheZoomFollowsTheMeasuredSmoothstep` | 09 §3.1、§3.2、§3.4 |
| 重量轴字段 | 逐位等于 R5 读回值（775 项只差 Sheila 的 `LerpEnd`） | `CombatWeaponTests.TheTableHoldsEveryKeptGunWithItsSource` | 09 §4.1 |
| 霰弹 | 关掉随机时和 R5 固定图案差 ≤ 0.006°；区域两两不重叠 | `ShotgunScatterTests.*` | 09 §5.3 |
| 换弹 / 切枪 | 解锁时刻差 ≤ 0.05 s；切枪"能开火"时刻差 ≤ 0.02 s | `CombatReloadSwapTests.*` | 09 §7.1、§7.4 |
| 扩散分布 | **还没有合格线**（等 R5 实测） | — | 09 §5.2 |

**重建检验（§11.9；PL-052 – PL-055）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 移动：位置 / 速度 | 每条命令差 ≤ 0.5（u、u/s） | `handbook/rebuild-test/judge/compare.py` | judge REPORT §0 |
| 移动：事件 | 同一条命令（±1 条算"基本过"） | 同上 | 同上 |
| 镜头：落地 kick | 峰值差 ≤ 0.05°；峰值时刻 ±1 帧；回到 0.05° 以内 ±2 帧 | 同上 | 同上 |
| 第一次结果 | 移动 10 / 10 逐命令一致（最大 0.0001 u）；镜头随机数取 0 时 5 / 5（0.0000°） | 同上 | judge REPORT §1 |

**镜头（07 章）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 镜头角度指标 | max(0.3°, 10 %)；时间 max(2 – 3 帧, 10 %)；晃动幅度 max(0.05°, 10 %)；眼高 1 u；FOV 0.005 | CC | FEEL §8.1；§11.2 |
| 镜头不改模拟 | 镜头开 / 关，每个模拟状态逐位相同；瞄准角不变 | `NativeCameraTests.TheSimulationIsUntouchedAndTheAimIsRaw`；`F7CameraTests.GrappleRollUsesTheSharedSpringAndOnlyTheCamera` | DP P1 / P2 |
| punch 弹簧 | 单位冲量两组合计峰值 0.0771 ± 0.0005，峰值时间 0.146 ± 0.01 s，过零 0.47 ± 0.01 s，反向峰 −12 % ± 1 % | `NativeCameraTests.PunchSpringShapeMatchesC3`、`PunchAxisIsFrameRateIndependent` | 07 §1.1 |
| 落地 kick | v、r 给定时峰值和公式差 < 1 %；实测落在随机范围内；用 R5 命令号重放 32 / 34 峰值一致 | `NativeCameraTests.LandingKickScaleMatchesTheC3Table`；`R5SharedRandomTests.TheSeedMixMatchesTheGame` | 07 §2.3；D-35 |
| 眼高 | 站 70、冲刺稳态 64、蹲 / 滑 32 精确；过渡曲线差 ≤ 1.5 u | `NativeCameraTests.StraightSlideSinksTheEyeOpensTheFovAndDoesNotTilt` | 07 §3.1；D-38 |
| 钩爪横滚 | 逐帧 rms ≤ 0.5° | CC `grapple_roll_rms` | FEEL §10.1 |
| M5.5 镜头（旧版留开关） | 无过冲、单调收敛、90 % 时间符合设定、30 / 60 / 144 / 240 Hz 与 120 Hz 一致（1e-9） | `CameraFeedbackTests.*` | M55A §1 |

**单位开关（HSD-Unity PR #88，还没合并）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| u 模式不变 | 869 个批处理输出逐字节相同 | 批处理比对 | US §5 |
| u ↔ m 等价 | 位置 < 1e-4 m、角度 < 1e-6°、事件逐条相同（实测 2.2e-12） | `UnitsEquivalenceTests.MetersRunEqualsResearchRun` 等 | US §5 |
| 全部演示 | 119 个中 118 个等价；`wall_bounce` 4.6 mm 是已知浮点边界 | `UnitsEquivalenceBatch.Run` | US §5 |
| R5 对照拒绝 m | 在 m 下抛 `UnitModeException`；批处理自动切回 u | `UnitsTests.ReplayAndShortRangeEvalRefuseMeters`、`BatchEntryPointsSwitchBackToResearch` | US §3.5 |
| 手册参数表 | 和 Unity 导出逐行一致 | `check_params.py` 退出码 0 | `handbook/tables/README.md` |

**泰坦（研究 PR #116 / #117、HSD-Unity PR #75 – #79，都还没合并）**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 模型尺寸 | 和 `[v2]` / `[meas]` 值差 ≤ 5 %（重型骨长改成 `[meas]` × 0.878 后差 ≤ 1 %） | SPEC §5 清单 | D-143 → D-148 |
| 关节贴合 | 表面相交，或表面最近距离 ≤ 5 mm | `checks/joint_test.py` | D-155 |
| 走路不穿模 | 四条路线 0 帧相交 | `joints.tsv` 复核 | D-162 |
| 导入 Unity | 三角面一个不丢、每件面积和 Blender 一致 | `TitanImportTests` | D-166 |
| 地形（普通要素） | 重型：踩住的脚 ≥ −2 cm、摆动脚 ≥ +5 cm、穿模 0 帧 | `score.py`；`TitanWalkFilm -route terrain` | `README-terrain.md`（HSD-Unity PR #78） |
| 地形（极端要素） | 重型：踩住 ≥ −5 cm、摆动 ≥ 0、穿模 ≤ 该段帧数 1 % | 同上 | 同上 |
| 地形 24 段过线 | D-187 起**只记录**，不判 | `score.py` | D-180、D-186、D-187 |

泰坦的数是 `[m]` 模式下的（模型按米导入，[01 §3.4](01-units-body.md)），只有这一组。

**TF2**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| TF2 规则对不对 | 规则和实测的差是常数（= 起跳帧一帧半步重力：慢 −4.2、快 −6.2 … −6.3 u/s），不随竖直速度变 | 人工 | PD M-1 |
| TF2 二段跳包 | T5 试次复现 231.2 ± 0.15、61.8 ± 0.05 | `Tf2SuperJumpTests.T5TrialsAreReproduced` | D-69 |
| TF2 跑墙预设 | A 水平稳定在约 375，B 在 225·msc ± 1.0；时间上限 ± 3 帧 | `Tf2WallRunTests.PresetAHorizontalSettlesNear375AndBNear225`、`ForwardHeldRunsToTheTimeLimit` | D-57、D-58 |
| AI 命中率（建议） | 近距各状态落在 L-1 实测 95 % 置信区间内 | 还没有测试 | 10 §10.12 |

**早期流水线**

| 量 | 合格线 | 检查 | 出处 |
|---|---|---|---|
| 游戏内冒烟（M1 A1） | 11 / 11，客户端 ↔ dedi 配对 ≥ 90 % | `hsd_tel.py smoke` | M1 §1 |
| 实测帧率 | 每个试次实际帧率在计划 ±3 % 内，否则作废重跑 | `hsd_trial.py`（`--fps-tol`） | M1 §2；附录 A §A.5 |
| 合成数据管线 | 7 类注入缺陷全报出；+10 u 平移和丢一个落地正好失败 | `research/phase2-prep/run_checks.py` 10 / 10 | VR §1、§3 |
| 账本一行"一致" | **没有数值线**：状态只表示代码和实测的关系，数字证据写在条目里 | `ledger.csv` | LED §1、§2 |

#### 实现模板

新的一行：写"量 / 合格线 / 检查 / 出处"四列；合格线要有数，有对应的测试或脚本；没有测试的写"还没有"并进 `_notes` 的待研究。章节和测试的线不一致时两个都写、标粗。

#### 验收

表里每一行的"检查"都能跑；章节里的线和测试里的线一致（现在有三处不一致，见缺口 2）。

#### 出处

见每行。收集来源：02 – 09、12 章（11-14 已合进 `handbook/base`，PR #124，还没合并进 main）；FM、CC；DECISIONS（main、#116、#117）；HSD-Unity 测试（main、PR #53 / #58 / #88）；重建检验 `handbook/rebuild-test/judge/REPORT.md`（已合进 `handbook/base`，PR #124，还没合并进 main）。原件 [`tables/pass-lines.tsv`](tables/pass-lines.tsv)（本分支 `handbook/ch10`）。

---

## 11.7 为什么 R5 对照永远在 u 模式下跑

#### 原理

R5 的数都是 u。在 u 模式下，Unity 的每个数可以**直接**和 R5 的数逐个对上，不经过任何换算；回放基线是 sha256 逐字节比，也只有在 u 模式下才成立。米模式在数学上等价，但只能做到浮点误差以内一样（2.2e-12 m），做不到逐字节；而且一旦允许"换算以后再比"，就分不清差别是规则不同还是换算错了。

#### 规则和公式

1. **数要能逐个对上**：研究阶段一直用 u，算出来的数和 R5 的数可以逐个对上（US §1）。
2. **研究数据全按 0.0254 存**：录像格式、`SourceSpace.DefaultMetersPerUnit`、测试、所有对比报告都按这个系数；换系数就要重算所有对照数据（01 §3.2）。
3. **不允许悄悄换算再比**：回放对比、R5 对照测试在米模式下**直接报错**（01 §5.1、§5.2 第 3 条）。
4. **误用要大声失败**：库函数在米模式下抛 `UnitModeException`；批处理是"拿 R5 对照"的命令，**自动切回 u 模式**（US §3.5）。
5. **只有 u 模式能逐字节**：步进代码里写死的长度乘 `Units.L`，u 模式下正好是 1.0，所以逐位相同；米模式只是浮点等价，而且 `wall_bounce` 在 `add <= 0` 边界上分叉 4.6 mm（US §3.3、§5）。sha256 基线只在 u 模式成立。
6. **用户规则**（11-14）：测试和研究阶段用 u；米模式保留设计，以后再切；R5 对照永远在 u 模式。

| 量 | [m] | [u] | 说明 |
|---|---|---|---|
| 换算系数 | 0.0254 m | 1 u | 只有一个，`SourceSpace.DefaultMetersPerUnit`（01 §3） |
| u ↔ m 等价容差：位置 | 1e-4 m | 0.00394 u | `PosTolM`；实测最大 2.2e-12 m |
| u ↔ m 等价容差：角度 | — | 1e-6° | `AngleTolDeg`，角度不换算 |

#### 实现模板

```
RunR5Comparison():
    if Units.Mode != ResearchU:
        if called from a batch entry point: Units.Mode = ResearchU      // 自动回研究状态
        else: throw UnitModeException("R5 comparison runs in u only")
    ... run replay / feel batch ...
    write "units: u" into every output header
```

一键回研究状态：命令行 `-researchU`、Esc 菜单、编辑器 `HSD ▸ Units ▸ Back to research (u)`（HSD-Unity PR #88）。

#### 验收

`UnitsTests.ReplayAndShortRangeEvalRefuseMeters`、`BatchEntryPointsSwitchBackToResearch`、`ReplayInResearchUIsUnchangedByTheSwitch`；`UnitsEquivalenceTests.CameraFeelReplayRefusesMeters`（HSD-Unity PR #88，还没合并）。合格线：全部通过；批处理输出头写明 u 模式。

#### 出处

- [01 §3.2、§5](01-units-body.md)。分支 `handbook/base`
- US §1、§3.3、§3.5、§5。HSD-Unity PR #88，还没合并
- `HANDBOOK-PLAN.md`"用户定下的事"第 2 条（11-14）。工作区，不在 git

---

## 11.8 新功能怎么验收（流程）

#### 原理

把前面几节串成一个固定流程，任何新功能（移动、镜头、技能）都照着走，这样"做完了"有统一的含义。

#### 规则和公式

1. **先定合格线再写代码**：在功能的章节里写好"验收"段（指标、容差、对照数据），加进 §11.6。
2. **有 R5 对照的**：准备 R5 片段（附录 A §A.5、§A.7），跑 FeelBatch / CameraFeelBatch，用 FM / CC 打分；新指标加进同一张 `TOL` 表。
3. **没有 R5 对照的**（R5 没有原型、或测不了）：找两个 R5 锚点（DP §9.1），按锚点的量级定合格线，标 [设计]；TF2 有原型的用 TF2 实测，标 [TF2 实测]。
4. **写三类测试**（§11.5）：公式、对照、不变量。
5. **防改坏**：回放基线 426 个不变；FeelBatch 315 个只有预期的变；旧版做成开关，开关下逐字节相同。
6. **参数**：重新导出参数表、跑 `check_params.py`。
7. **留档**：差别进 FEEL / R5-DIFF（编号、R5 值、Unity 值、改不改、开关）；决定进 DECISIONS（选中和没选中都写）；共享日志写一条。
8. **最后由用户试玩**。没试玩前，新值都是 [设计]。

#### 实现模板

```
□ 章节"验收"段写了合格线，§11.6 加了一行
□ R5 片段 / 锚点 / TF2 数据：____
□ FM / CC 打分：一致 __ / 接近 __ / 不一致 __ / 次数不同 __
□ 测试：公式 ____  对照 ____  不变量 ____
□ rud_check.py 426 identical；FeelBatch 315 只变了 ____
□ check_params.py 退出码 0
□ FEEL / R5-DIFF / DECISIONS / 共享日志
□ 用户试玩
```

#### 验收

清单每一格都有内容。

#### 出处

- DP §9.1（8 步）。main
- 本章 §11.2 – §11.7。

---

## 11.9 重建验收（示范：阶段 4 的重建检验）

#### 原理

前面几节验收的是"Unity 做得像不像 R5"。手册还有一个更根本的目标：**删掉 R5 和 TF2，只看手册也能重新做出同样的移动和镜头**。这要单独验收：找一个没看过 Unity 代码的人（这里是一个单独的会话 hb-rebuild），只给他手册，让他从零写一个实现，再和 Unity 的参考实现逐命令比。比出来的差别分三类：**手册错了**、**手册没写死、靠猜**（猜对了也要补）、**题目本身有歧义**。只有第一类说明手册的规则有问题。

#### 规则和公式

1. **两个隔离的角色**：
   - 出题和评分（hb-judge，分支 `handbook/rebuild-judge`）：写题目、用 Unity 参考实现（`MovementConfigs.Reference()` + 原生镜头 `NativeCameraFeedback`）生成标准答案、写评分脚本。
   - 重建（hb-rebuild，分支 `handbook/rebuild-build`）：**只读 `handbook/*.md` 和 `handbook/tables/`**，不看评分文件夹、不看 Unity 代码；从零写一个实现，对每道题输出逐命令的 CSV；看不懂的地方记进 `GAPS.md`（猜了什么）。
2. **题目**：每道题是一串固定输入（每条命令按什么键），输出每条命令的位置、速度、竖直速度、事件（起滑、结束、起跳、落地）、镜头角度、眼高。这一轮 10 题：滑铲 S1 – S5（含斜坡、滑铲跳、冷却），落地镜头 L1（50 / 100 / 200 / 400 u 落下），原地跳镜头 L2。
3. **合格线**（评分脚本 `compare.py` 开头）：

   | 量 | 合格线 [u] |
   |---|---|
   | 位置、速度 | 每条命令差 ≤ 0.5 u、0.5 u/s |
   | 事件 | 同一条命令（±1 条 = 基本过） |
   | 落地镜头 | 峰值差 ≤ 0.05°；峰值时刻 ±1 帧；回到 0.05° 以内 ±2 帧 |

4. **分开评**，把随机和条件的影响拆出来：
   - 主评分：题目原样，镜头随机数按 R5 的种子规则；
   - 镜头随机数全取 0（`r0`）：只比镜头公式本身；
   - 换一个条件（msc 1.15）：检查规则对条件是否成立；
   - "按重建方的读法"：题目有歧义时，按重建方合理的读法再评一次。
5. **差别归类**：每一个不过的题，找到差在哪一条命令、哪一个量，归到"手册错 / 手册没写死 / 题目"之一，写出要改的句子。
6. 评分方自己先做**自检**：用标准答案对标准答案评分必须全过；故意挪一条命令、放大 2 % 必须被抓出来。

#### 实现模板

```
出题：PROBLEMS.md（题目原文 + 标准答案用的读法） → harness（只读编译 Unity 参考实现） → answers/<题>.csv、answers/r0/、answers/msc115/
重建：只读 handbook/ → src/ → out/<题>.csv、out/r0/、out/msc115/ + GAPS.md
评分：compare.py out/ answers/；compare.py --build-dir out/r0 --answers answers/r0；…
报告：逐题结果表 → 差别归类 → 要改的句子 → 建议的下一轮
```

方法步骤在 [附录 A §A.9](A-research-methods.md)。

#### 验收

第一次结果（重建 62f0418，评分 11-14）：

| 口径 | 过 | 不过 |
|---|---|---|
| 按题目原样 | 5 / 10 | 5（S5、L2 是题目读法；L1_50、L1_400 是手册错） |
| 按重建方的读法 | 8 / 10 | 2（L1_50、L1_400：手册错） |
| **移动列**（位置、速度、竖直速度、事件），按重建方读法 | **10 / 10**（最大差 0.0001 u） | 0 |
| **镜头随机数取 0** | **5 / 5**（0.0000°） | 0 |
| msc 1.15，S1 – S4 | 4 / 4 | 0 |

- **唯一的手册错误：07 §1.4 的随机种子**。手册写成"无符号数直接取模"，参考实现把混合后的种子当**有符号 32 位整数**（< 1 先取反，还 < 1 用 0xbc8f，再用 Schrage 方法算 48271·s mod (2³¹ − 1)）。种子最高位是 1 的命令，随机数正好变号（命令 42：Unity −0.4159，重建 +0.4159），所以 L1_50、L1_400 的落地 kick 峰值不对（1.609° / 2.204°、17.780° / 21.824°）。随机数取 0 时镜头完全一致，说明 07 章的 kick 公式、弹簧、落地速度定义全对，只错这一句。改法写在评分报告 §2，交给整合会话改 07 §1.4。
- **两个题目造成的不过**：S5"滑铲结束后第 1 条命令再按冲刺 + 蹲"——结束时速度约 124 u/s，低于起滑门槛 200，怎么按都起不了滑，测不到冷却；L2"原地跳一次"没说哪条命令（出题方 tick 30、重建方 tick 0），位置和事件错开 30 条，按命令号取的随机数也对不上（错开 30 条以后随机数取 0 的镜头 0.0000° 一致）。这两题要改题目，不改手册。
- 另外两处题目不清（S4 滑不停没说录多久；msc 是 1 还是空手 1.15）没有丢分。
- **手册没写死、靠猜（猜对了）的 14 处**（H-1 – H-14：msc 默认、滑铲跳退还用严格小于、硬着陆取哪一刻的竖直速度、按键锁存不产生新的按下沿、镜头只在命令上更新等），评分报告 §4 逐条写了要改的句子，交给整合会话。
- 结论：凡是规则本身，只看手册就能逐命令重建；改完 07 §1.4 和两道题，预计下一轮 10 / 10。

**这次重建检验教会我们的验收规矩**：

1. 随机量要把"公式"和"随机数"分开验：随机数取 0 先比公式，再单独比随机数生成器（种子规则写到位级：有符号还是无符号、字节顺序、初值）。
2. 题目要写死每一个会影响结果的条件：从哪条命令开始、录多久、移动倍率、命令号的定义。按命令号取随机数的题，命令号错开一条整题都比不了。
3. 重建方"猜对了"也要记：下一个重建方可能猜错。`GAPS.md` 是手册的补漏清单。

#### 出处

- `handbook/rebuild-test/judge/REPORT.md` §0 – §5、`README.md`、`PROBLEMS.md`、`compare.py`。分支 `handbook/rebuild-judge`（11afdb7），还没合并
- `handbook/rebuild-test/build/GAPS.md`、`out/`。分支 `handbook/rebuild-build`（62f0418），还没合并
- `HANDBOOK-PLAN.md` 阶段 4。工作区，不在 git

---

## 缺口

都写进了 [`_notes/hb-ch10.md`](_notes/hb-ch10.md)。

1. **合格线是 11-14 晚上从各章摘的**（[`tables/pass-lines.tsv`](tables/pass-lines.tsv)）：章节以后改了合格线，TSV 要重新摘；TSV 和测试代码里实际的容差还没有自动对照（建议以后让校验脚本查"测试里的容差 = 表里的线"）。07 章只有 3 行写成"合格线："，其余项的验收是测试名，没摘进来。
2. **章节和测试的线不一样**（三处）：04 §4.2 横向 41 ± 1，测试 ±1.5；03 §3.15 tap strafe ≤ 2°，测试 ±8°；04 §4.5 < 1 u/s²，测试 R5 拟合 ±4 %（账本 S-09 写 3 %）。要么收紧测试，要么改章节。
3. **两个指标脚本的"帧"不一样**：FM 1/144 s，CC 1/120 s；M3 有 60 / 120 / 144 fps 的片段，帧容差和片段自己的帧率无关。
4. **FeelBatch 315 个和镜头批没有提交的哈希清单**，只能改前改后各跑一次比。建议加一个 `feel_check.py`（和 `rud_check.py` 同一套规则）。
5. **FEEL §2 的表不全**（翻越、技能的容差只在代码里）；"镜头 13 个指标"过时（现在 25 个）。本章 §11.2 已补全，FEEL 本身没改。
6. 账本没有数值判定线；TF2 脚本没有容差。
7. 起跳缓冲、走上台阶、技能（除了移动技能）、道具、AI 都**没有叠图验收**（B11-2）。跑圈没有 R5 参照（B11-1）。
8. 文件数口径不统一：426 / 429 / 741 / 744 / 315 / 869，869 由哪几批组成没拆开。
9. TF2 预设的 3 处对不上（PD M-1 – M-3）修复只在本地工作树，没推送（B11-3）。
10. 叠图页面在 claude.ai，不在 git；页面数据（`scorecard.json`、`trials.json`）在 git。
