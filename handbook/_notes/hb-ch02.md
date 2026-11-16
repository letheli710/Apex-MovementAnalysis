# hb-ch02 备注（给总控 / hb-integrate / hb-tables）

2026-11-14。分支 `handbook/ch02`（从 `handbook/base` d93f012）。只写了 `handbook/02-foundation.md` 和这一页。

## 1. 本章写了哪些条目

| 节 | 条目 | 资料够不够 |
|---|---|---|
| 2.1 | 时间步长：固定 120 Hz 命令、累加器、卡顿、插值、输入采样 | 够（Unity 代码 + 测试）；R5 侧只有"dt = frametime" |
| 2.2 | 每条命令的执行顺序（R5 7 步 / HSD 6 步对照） | 够 |
| 2.3 | 和帧率无关的积分（T8） | 够 |
| 2.4 | 碰撞体：站 / 蹲尺寸、地上下蹲、空中松开下蹲 | 尺寸是 [设计]，蹲姿高度不确定 |
| 2.5 | 碰撞：扫掠、贴墙滑、天花板、卡住 | HSD 侧够；R5 碰撞代码没读 |
| 2.6 | 地面检测：支撑面、离地、落地 | 够；发现一处写法差别（第 3 节第 1 条） |
| 2.7 | 上台阶（R5 22 / HSD 18） | **缺 R5 实测**，是本章最大缺口 |
| 2.8 | 斜坡：能站上限、坡上走、圆底 | 够（R6 / R6U）；45.6° 本身没测 |
| 2.9 | 贴地：下坡、凸转折、走下台边 | 坡上够；**平地台边没测** |
| 2.10 | 参数一览（Unity 导出名） | — |
| 2.11 | 本章 HSD 和 R5 的差别汇总（9 条） | — |

## 2. 待研究（建议并进 99-TODO-RESEARCH.md，我没改那个文件）

| 建议编号 | 内容 | 怎么测 | 优先 |
|---|---|---|---|
| B02-1（已有，扩充） | R5 台阶梯 18 / 20 / 22 / 24 u：走、冲刺、滑铲（看速度减多少，验证 `slide_step_velocity_reduction` 10 × Δz）、空中贴着台边落下；同时看镜头是否把抬高平滑掉 | 和 R6 一样用道具拼台阶，状态日志逐命令 | 高（决定 18 / 22） |
| B02-2（已有） | 坡上走路（非冲刺）| R6 的坡 | 低 |
| B02-3 新 | **落地条件**：R5 是 v_z ≤ 140 就能着地，HSD 要求 v_z < 0。找 v_z 为小正值又碰到能站的面的情况（冲上坡顶又落回坡上、跳板弹到斜面、上坡起跳的第一条命令） | R6 坡 + 起跳；或 Frida 读 `CategorizePosition` 的分支 | 中 |
| B02-4 新 | **平地走下台边**：R5 走下 2 / 8 / 16 / 22 u 的路沿时贴下去还是掉下去（Source 的 StayOnGround 会贴下去） | 冲刺走下道具台阶，看着地标志是否断 | 中（影响落地镜头、跳的时机） |
| B02-5 新 | **空中迈台面**：HSD 里空中身体只要脚离台面 ≤ 18 u 就能水平越过台面侧面、落下时被放到台上。R5 里同样的情况是撞墙还是翻越 | 起跳后贴着 10 / 16 / 20 u 高的台边水平移动 | 中 |
| B02-6 新 | 能站的最陡坡 0.7 的实测（44° / 46° / 48° 坡） | R6 坡加大角度 | 低 |
| B02-7 新 | 读 R5 原生 StepMove / TryPlayerMove：碰几次、台阶怎么迈、圆底到底是什么形状（R6 只按高度推出"像半径 16 的圆底"） | Ghidra（`ghidra-projects` 持久工程） | 低 |

## 3. 读代码时发现的差别（DIFF 里没有，建议整合时加进 R5-DIFF §二）

1. **落地条件**（02 §2.6）：`R5MotorV2.CheckLanding` 要求 `vel.z < 0`；R5 `CategorizePosition` 是 v_z > 140 才离地。平地上没区别，坡上 / 弹射可能有。
2. **空中迈台面**（02 §2.7 第 4 条）：`MovementWorld.Offset(q, h, step)` 在 `Enter`（扫掠）里总是用 step = true，所以台阶区（顶面下 18 u）在空中也不挡路。Source 的空中移动不迈台阶。
3. **碰撞在落地判断之后**（02 §2.2）：HSD 的 `CheckLanding` 用 `BeforeStep` 时的 `floorZ`（命令开始时脚下的地面），扫掠在后。落到更高的台面上最多晚一条命令着地。
4. **蹲姿碰撞体 48 和空中下降 16.5 对不上**（02 §2.4）：空中站起时碰撞体长高 24 u，原点只降 16.5 u，碰撞体头顶上移 7.5 u。
5. **滑铲上台阶减速没做**（02 §2.7）：R5 ConVar `slide_step_velocity_reduction` 10（是否被原生代码读没查）。第 04 章可能也会提到，请 hb-ch04 / 整合时对一下。

## 4. 建议的 D 行（编号留空，按"选中 + 没选中 + 数据"写）

### D-?? 命令频率（补记；实际 M5 起就是这样）

| 选项 | role | 内容 | 数据 | 理由 |
|---|---|---|---|---|
| A 固定 120 Hz（选中，现在） | version | 身体只按整条 1/120 s 命令走，画面插值；一帧最多 12 条 | 30 / 60 / 75 / 144 / 240 fps（±20 % 抖动）逐位相同（`SameCommandsAtAnyFrameRateGiveTheSameState`） | 手感和画面帧率无关；R5 研究录像多是 120 fps（D-02），对照误差最小 |
| B 跟画面帧（R5 的做法） | parallel | 每帧一条命令，dt = 帧时长 | R5 冲到上限的时间随 dt 差 13 %（GM） | 不同机器手感不同，测试不能逐位重放 |
| C 固定 60 Hz | parallel | — | 连招漂移约 35 u/s（M5） | 太粗 |

开关：`PracticeSession.CommandRate`（常量）。建议同时进 R5-DIFF §三"有意和 R5 不一样"。

### D-?? 台阶高度（pending）

| 选项 | role | 内容 | 数据 | 理由 |
|---|---|---|---|---|
| A 保持 18（现在） | pending | TF2 / Source 值 | 没有 R5 数据支持 | 现有关卡、测试都按 18 |
| B 改成 R5 的 22，18 留开关 | pending（建议） | `MovementWorld.stepUp` = 22（同时管挡路、支撑、坡上贴地） | R5 setfile `stepHeight` 22（SV、T1-REPORT）；没实测 | 拟合原则：尽量贴合 R5 |
| C 先测再定 | pending | 做 B02-1 | — | 确认 22 真的生效、镜头怎么处理 |

建议顺序：C → B。改之前要查关卡里 18–22 u 之间的台阶 / 箱子（会从"墙"变成"台阶"）。

## 5. 想改别处的地方

- **README 写法规范第 3 条**：三列表的"R5 原值 [u]"列，本章有很多 HSD 设计值和 Unity 常量（`MaxBumps`、`CommandRate`），我把列名写成了"原值"并在格子里注明"HSD 设计值"/"R5 原值"。如果 README 想严格只用"R5 原值 [u]"列名，hb-integrate 统一一下。
- **01-units-body.md §4.2**："可站立的最陡坡 … `MovementWorld` 同"，正确；"台阶高度（HSD 现在用的）… 交给 hb-ch02 核对"——已在 02 §2.7 写清楚，01 那一行可以改成链接到 02 §2.7。
- **00-INVENTORY 02 章"资料在哪"**：可以加 `research/phase2-local/m4b/swing/SWING.md` §5（撞墙速度）、`research/phase2-local/m2/air_jump/AIR-JUMP-MODEL.md` §2.3（落地规则）、`research/rea-native/convar-defaults/CONVAR-DEFAULTS.md`（`slide_step_velocity_reduction`）。
- **tables/（hb-tables）**：02 §2.10 的参数名都对过 `HSD-Unity-UNITS/Docs/units/units-params.tsv`。注意 `hullBottomRadius` 在 `preset.R5Reference` 和 `world.default` 里是 0，游戏身体（`body.Reference.*.motor.p`）里是 16——表里取游戏身体的值。`CommandRate`、`FlatNormalZ` 只在 registry 里（常量）。`MaxCommandsPerFrame`、`MaxBumps` 没导出。
- **过时文档**：本章没有用到 00-INVENTORY 过时表里的说法。NATIVE-MAP §3 的两个错名在 02 §2.2 出处里注明了。

## 6. 给总控的问题

1. 台阶 18 / 22：手册正文按"HSD 现在 18、R5 22、待定"两边都写了。要不要在今晚的合并清单里加一条"等用户定 D-??（台阶）"？
2. 第 3 节的 5 条差别：是由 hb-integrate 写进 R5-DIFF §二，还是先留在 `_notes` 等用户看？
