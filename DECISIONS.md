# 决定日志（Decision Log）

这份文件按时间记录项目里**用户做过的决定**（选哪个方案、走哪个分支、改不改）和**大的改动**，方便以后回顾：当时为什么这么定、现在是什么状态、想改的话去哪里改。

- 新的决定**追加在最后一节的末尾**（越新越靠下），编号接着往下排，不改旧编号。
- 决定被推翻时，**不删旧条目**：在旧条目里标"已被 D-xx 取代"，新的决定另起一条。
- "怎么改"一栏写开关或文件的位置。游戏里能直接切的写菜单 / 按键；代码里的开关大多在 `HSD-Unity/Assets/HSD/R5Replay/Runtime/MovementConfig.cs` 的 `MovementConfigs.Reference()` / `Fun()` 里（下文简称"Reference / Fun"），Fun 默认继承 Reference。
- 暂缓、还没决定的设计问题另有清单：[DEFERRED-DESIGN-TODO.md](DEFERRED-DESIGN-TODO.md)；搁置的能力：[SHELVED-ABILITIES.md](SHELVED-ABILITIES.md)；每天的执行过程：[EXECUTION-LOG.md](EXECUTION-LOG.md)。
- 两套电机：**回放电机**（`R5MotorV2` 默认值，用来逐命令复现 R5 录像，保持和基线逐字节相同，一般不改）和**游戏身体**（Reference / Fun，玩家实际在玩的）。下面的改动除非特别说明，都只改游戏身体。

## 总表

| # | 日期 | 主题 | 决定 | 怎么改 | 记录 |
|---|---|---|---|---|---|
| D-01 | 2026-10-20 | Unity 工程位置 | 在工作区里新建 Unity 工程；原来的 `High Speed Test 01` 只读，不再改 | — | EXECUTION-LOG 2026-10-20 |
| D-02 | 2026-10-21 | 研究范围 | 以 R5Flowstate S21 为准，不是官方当前版本；tap strafe 只算单次按键 lurch | — | M4-REPORT |
| D-03 | 2026-10-21 | M5.5 镜头 | 用户试玩认可；方法写成 `fps-camera-design` skill，以后每个新动作可以有自己的镜头语言（复用方法，不复用数值） | 镜头模型见 D-14 | HSD-Unity#6、#7 |
| D-04 | 2026-10-21 | 做哪些传奇能力（M6-B） | 只做 Valkyrie 喷气补全和 Ash 相位突破；Loba、Alter 搁置 | — | SHELVED-ABILITIES.md，HSD-Unity#10 |
| D-05 | 2026-10-22 | 跑墙、抓边悬挂、二段跳（M7-A） | R5 S21 没有，算 HSD 设计：Reference 关，Fun 开 | 游戏内 `7` / `8` / `9`；`MovementConfig.hsd`（`HsdMovementParams.Off()` / `.Fun()`） | HSD-Unity#11 |
| D-06 | 2026-10-22 | 三个设计问题暂缓（M9） | E1 两种二段跳能否同时装备、E2 Fun 斜坡滑铲 1.6 倍加速度、E3 跳跃输入缓冲：先不决定，到游戏接近完成时再看 | 见清单 | DEFERRED-DESIGN-TODO.md |
| D-07 | 2026-10-22 | 跳板起飞后能不能 lurch（M10-D3） | Reference 按 R5：不能；Fun 保留 M5.5 的"跳板 → lurch" | `padLaunchOpensLurchWindow`：Reference false，Fun true | HSD-Unity#18–#23 |
| D-08 | 2026-10-22 | Ash 冲刺 | 不做 | — | M10-REPORT |
| D-09 | 2026-10-22 | Wraith 传送门 | 做（M10-W） | — | M10-REPORT |
| D-10 | 2026-10-23 | S21 客户端和本地服务端结果不一致时（主控规则，用户可以推翻） | Reference 跟 S21 客户端（有社区证据时），标 [S21-client] | 天花板滑行：`p.ceilingSurf`（Reference true） | M10-REPORT |
| D-11 | 2026-10-23 | 技能代码结构（M10-R） | 一个技能一个文件夹，每个文件夹一份中文 README；新技能也照这样 | `Assets/HSD/R5Replay/Runtime/Abilities/<技能>/` | HSD-Unity#24 |
| D-12 | 2026-10-23 | 原生研究的顺序 | N6 补测 → N7 把建议改进 Unity（每项用户批准，只改 Reference）→ N8 传送研究最后 | — | research rea-native |
| D-13 | 2026-10-24 | N7：12 项 REFERENCE-CHANGES | 全部改成原版（"全部改成原版"）：地面摩擦和加速、空中额外加速、滑铲加成冷却 2 s（从上次滑铲开始算）、滑铲跳下限、滑铲转向等 | 各项都是 Reference 里的 `[NonSerialized]` 开关，清单见 research `rea-native/n7/N7-UNITY.md` | HSD-Unity#25，research #43 |
| D-14 | 2026-10-24 | 镜头改成原生（N8-CAM） | 默认用原生镜头；M5.5 镜头原样保留在 `Camera/M55/`，可以切回去 | 游戏菜单"Camera model"（保存在 PlayerPrefs `hsd.m55.model`）；代码 `Game/Runtime/Camera/CameraModels.cs` | HSD-Unity#26，research #46 |
| D-15 | 2026-10-24 | 传送类能力（N8-E） | E-1 相位中的身体不被跳板弹起；E-2 / E-3 重新进入的间隔 1.0 s；E-6 旧传送门预设标成设计；E-4、E-5 保持不变 | `padPhasedNoLaunch`（Reference true）；`DimensionalRiftAbility` 的 `reuseDebounce` 1.0；`PhaseBreachParams.reentryDebounce` 1.0 | HSD-Unity#27，research #49 |
| D-16 | 2026-10-24 | S27 翻越加速（mantle boost，B1） | 把 S27 的翻越加速（准星 BOOST 圈）移植进来；用户喜欢这个手感 | 游戏菜单"Mantle boost (B1, S27 port)"，默认开（PlayerPrefs `hsd.b1.mantleboost`），只影响正在玩的身体；`SuperglideMode.MantleBoostS27` | HSD-Unity#28、#29，research #50、#51 |
| D-17 | 2026-10-25 | 重力升梯和相位（N9 L-1 / L-2） | L-1 按原版：相位中的身体不受升梯影响；L-2 改标签为 [native]；重力炮不做（项目里用不到） | `liftPhasedNoLift`（Reference true） | HSD-Unity#32，research #53、#54 |
| D-18 | 2026-10-25 | 蹲着翻越的时长 | 按 R5：蹲姿开始的翻越更长（0.517 / 0.625 / 0.813 s） | `crouchedMantleTime`（Reference true，Fun 继承） | HSD-Unity#32 |
| D-19 | 2026-10-25 | J-1：起跳朝墙推 30 u/s | 按原版：起跳时朝最后碰到的墙面推 30 u/s（superglide 402 的来源） | 电机 `p.jumpSurfacePush`（Reference 30，回放电机 0） | HSD-Unity#33，research #55 |
| D-20 | 2026-10-25 | N10 镜头 | C-10 走路晃动带偏航半频项（步长 0.280 s）；C-11 滑索侧倾按原版 A 分支（3.0 /s） | 原生镜头 `Game/Runtime/Camera/Native/` | HSD-Unity#34，research #56 |
| D-21 | 2026-10-25 | 手感怎么验收 | 不靠真人试玩（没有动画，感觉不可靠），改成用同样的 R5 输入把 Unity 和 R5 叠在一起比指标 | 叠图页面 https://claude.ai/artifact/P1mjgrbW1Yoiu9HdukTbDv；脚本 `research/feel/` | HSD-Unity#35，research #57 |
| D-22 | 2026-10-25 | F-1：滑铲跳退还的时间边界 | 按 R5：下蹲过渡从下一条命令开始算（0.201 s 退还，0.215 s 不退还） | `p.slideDuckTransitionFromNextCommand`（Reference true） | HSD-Unity#35 |
| D-23 | 2026-10-26 | C-1：台沿探测死区 | 修（是 bug）：墙顶在 80–98 u 时不再"既不翻越也不攀爬" | 没有开关，`MovementWorld.ProbeLedge`，所有游戏身体都受影响 | HSD-Unity#37，research #59 |
| D-24 | 2026-10-26 | C-5：走路翻越的出口速度 | 按 R5：没按冲刺时出口是走路速度 199.525 | `mantleExitWalkSpeed`（Reference true，Fun 继承） | HSD-Unity#37 |
| D-25 | 2026-10-26 | C-2：superglide 窗口前沿（第一次） | 保持简化，不做斜坡。**已被 D-27 取代** | — | research #59 |
| D-26 | 2026-10-26 | C-3、C-4 | 都不改：C-3 翻越时长公式和 R5 一致；C-4 走路 superglide 402 由命令内部碰墙时刻决定，模拟不了，取多数结果 200 | — | research FEEL §6.4 |
| D-27 | 2026-10-26 | C-2：superglide 窗口前沿（推翻 D-25） | 按 R5 做减量 superglide：离翻越结束 102.5–117 ms 按跳且按着蹲，照样起跳，水平 385 → 425；Fun 不做 | `superglideReducedBand`：Reference 0.015，Fun 0（0 = 关） | HSD-Unity#38，research #60 |
| D-28 | 2026-10-26 | 两种 superglide | 都保留：原生 superglide（跳 + 蹲，460）和 S27 翻越加速（只按跳，388.7）。两者互斥，S27 打开时拿不到 460 | 同 D-16 的菜单开关；测试、回放、手感对照都按原生 | HSD-Unity#39 |

## 说明

**D-25 → D-27（C-2 为什么推翻）**：第一次决定时以为 Unity 的 102.5 ms 窗口已经盖住了 R5 的减量段，所以"简化 = 不改代码"。后来按 Unity 自己的翻越时钟重排（Unity 的翻越比 R5 长约 25 ms），发现减量段其实在窗口外面，原来的 Reference 在这段是"切到台面"，并不是"给完整 460"。用户随后要求继续做 C-2 并合并。细节见 research `research/feel/FEEL.md` §6.4 和 `Climb/README.md`。

**D-16 / D-28 和 D-27 的关系**：游戏里默认开着 S27 翻越加速，这时 superglide 走 S27 规则，D-27 的减量段看不到；在菜单里关掉 S27 才是原生 superglide。

## 记录里还没有结论的事

下面这些在过去的记录里写着"等用户决定"，后来没看到明确结论。要么还没定，要么定了没记下来，回顾时请确认：

- 回放电机要不要也换成 M10 的新滑铲规则（换了会让 2 个 M3 滑铲连招片段更准，但回放基线会变）。
- F-2：一次原地跳 Unity 比 R5 高 1.8 u（两套电机都是）。
- M8 留下的：LS / RAS 参考片段、Fun 斜坡 1.6 倍（已转成 E2）、两种二段跳同时装备（已转成 E1）、跳跃输入缓冲（已转成 E3）。
- M9 留下的：要不要升级旧的 Revenant-Wraith 预设；待看的视频。
- N10 剩下的镜头项目（CAM-18 / 19、冲刺和钩爪侧倾的补测）。
