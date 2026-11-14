# hb-ch04 给总控和整合会话的备注（2026-11-14）

分支 `handbook/ch04`（从 `origin/handbook/base` d93f012）。只改了 `handbook/04-slide-mantle.md`、`handbook/04-slide-mantle/`（`slide_ref.py`、`s27-curves.tsv`）和本文件。

## 1. 本章写了什么

| 节 | 条目 | 重建检验要用 |
|---|---|---|
| 4.1 | 起滑：条件、起滑加成、2 s 冷却（从上次开始算） | 是 |
| 4.2 | 滑铲中：衰减 (s − D·dt)·0.7^dt、转向 `slideAccel` | 是 |
| 4.3 | 结束：按住蹲 < 125、松蹲 ≤ 350 / > 350 减速 400、蹲走 92 / 1500 | 是 |
| 4.4 | 再次加速：冷却、落地续滑（不加成、刷新冷却）、换地面实体重新起滑（U-3） | 是 |
| 4.5 | 斜坡滑铲：g·n_z·n_h，5–40° 表、平衡速度、上坡不倒滑 | 是（坡上位置在 02 章） |
| 4.6 | 滑铲跳：退还（0.4 s 且下蹲过渡 0.2 s 未完）、297.5–350 抬到 350、高 50 | 是 |
| 4.7 | **滑铲逐命令伪代码**（所有分支、常数表、离散化 5 条注意） | **是，主体** |
| 4.8 | 蹲下 / 起身：眼高过渡（0.4 / 0.2 s、smoothstep）、蹲姿碰撞体、空中松蹲 −16.5 | 落地镜头会用到眼高 |
| 4.9 | 翻越检测和高度范围（18–80 u，面向锥 35°，探测流程） | — |
| 4.10 | 攀爬（够不着时；速度线、终点 147.06、蹲着取消） | — |
| 4.11 | 翻越路径、时长 0.1728 + 0.0055·rise、出口 299 / 199.525、取消 | — |
| 4.12 | 蹲着翻越（原生翻越状态：基础状态、+4、速率、f0、眼高曲线） | — |
| 4.13 | 原生 superglide（窗口 0.1025 s、减量段 0.015 s、460、冷却、+30） | — |
| 4.14 | S27 翻越加速（δ 判定、8 条曲线、388.7 / 367.42，游戏默认） | — |

附件 `04-slide-mantle/slide_ref.py`：照 §4.7 写的独立 Python 实现，打印的数和 R5 实测对上（peak 460、退还 247.71 对 247.77、抬到 350、松蹲 19 / 11 条命令后结束、M10 滑铲跳表）。**建议 hb-judge 把它当作重建检验的"标准答案"之一**：重建出来的滑铲跑同样的输入，和它差 < 0.5 u/s、结束命令一样就算过。

## 2. 待研究（建议进 99-TODO-RESEARCH，编号由 hb-integrate 定；本会话没改 99）

| 建议编号 | 内容 | 现在怎么处理 | 要不要新测 |
|---|---|---|---|
| B04-a | 起滑的两个原生条件没读出值：视角前向和速度方向点积 ≥ `slide_max_angle_dot`；下蹲比例 < `slide_max_duck_frac_to_start`。另有额外检查 0x140ac1d70 没读 | Unity 不检查；§4.1 写明 | Ghidra 读一次 setfile / 函数即可 |
| B04-b | 滑铲摩擦衰减指数的 (1 − 0.75·x)（x 来自 0x140abdc20）、标志 0x1dfc（滑铲减速 = 0）、0x1dfd 的含义 | 平地上推测不起作用；Unity 没做 | Ghidra |
| B04-c | 翻越触发几何：`AutoMantle_Try` / `AutoMantle_Search` 的距离、角度、高度；`automantle_cooldown` 0.25 s Unity 没做（= 00-INVENTORY 的 B04-1） | Unity 探测参数是 [设计]，按 A2 结果校准 | Ghidra + 可选 R5 接近角 / 距离扫描 |
| B04-d | > 40°、< 5° 的坡，更大的折角、更高速度会不会离地（= B04-2） | 没测 | R5 新测 |
| B04-e | 起滑加成的大小和 msc 缩放：只有上限（460）和一次加法分支（255 → 427.5）被测到，换传奇 / 武器 msc 没测 | 按 census 150 × msc | R5 新测（低入口速度、第二个 msc） |
| B04-f | 滑铲跳起跳后水平速度 R5 258.x、Unity 260.3（R6 看到，平地也一样，+2 u/s） | §4.6 写成已知差别 | 先对照回放查是哪条命令多的 |
| B04-g | 空中按蹲：R5 蹲到底（0.42 s）原点抬高 16.5，Unity 不抬，只在翻越探测 / 蹲着翻越里用 | §4.8 写成差别 | 不用新测，是要不要改 Unity 的决定 |
| B04-h | 蹲着翻越结束的出口速度（蹲着时是不是也是 299 / 199.525）没单独测 | Unity 和站姿一样 | 从 D72 数据可以读（不用新测） |
| B04-i | 翻越路径的形状（Unity 0.75 / 0.6 smoothstep 是 [设计]） | — | 可从 D72 Frida 逐帧原点读出 |
| B04-j | U-3 落地算不算"换地面实体"（原生 `SetGroundEntity` 落地也调） | Unity 保守：不算 | R5 新测（落到道具上的滑铲跳） |
| B04-k | superglide 起跳后为什么还能吃到滑铲加成（原生要求着地），"切断 / superglide"分界的原生来源（M-03 / M-04 剩余部分） | 按实测窗口做 | Frida 读按键时的翻越进度 |

## 3. 文档矛盾和过时（建议改；本会话没改别人的文件）

1. **`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/Climb/README.md` 关键参数表写 `slideBoostRearm` Reference 1.8 s**，代码 `MovementConfigs.Reference()` 设的是 `advanced.climb.slideBoostRearm = 2.0`（N7 原生），units 导出也是 2。README 过时。README 里"距离上一次滑铲加成 / superglide 至少 1.8 s"那句也过时（现在从上次开始滑铲算，2 s）。建议下一个碰 HSD-Unity 的会话顺手改，或进 00-INVENTORY 过时表。
2. **units 导出 `preset.Reference.advanced.climb.nativeReducedBand` = 0**：这个值是建身体时由 `MovementConfig.superglideReducedBand`（Reference 0.015）写进去的，配置里的 `ClimbParams` 字段本身是 0。给 hb-tables：参数总表里 Reference 身体的值应写 0.015（Fun 0），否则会误导。同理 `crouchedMantleTime` / `crouchEndsClimb` / `nativeTraversalStates` / `mantleExitWalkSpeed` 是 `[NonSerialized]`、建身体时设的，导出里可能看不到真实值。
3. **NS（N2-S-SLIDE）§5 S-05 "按住蹲结束速度 R5 112 vs 代码 125"**：112 = 滑铲结束后第一条蹲走命令的 post（124.75 − 1500/120 = 112.25），不是矛盾。S-04 的"约 335 结束"同理（结束那条命令按蹲走减 12.5）。建议在 00-INVENTORY 过时表加一行，NS / 账本的 S-05 改"一致"。[推断，没重跑数据，但数对得上]
4. **滑铲眼高下沉时间有三个说法**：`NativeEyeParams` 注释"C3 slide sink 0.208–0.213 s"、DIFF §二"滑铲下沉 Unity 约 0.19 / R5 约 0.167 s"（D-70）、`hullCrouchTime` 0.2。可能是"到最低点"和"过渡计时"两种量法。§4.8 两个都写了。建议 hb-ch07 在 07 章定一个说法，整合时统一。
5. 00-INVENTORY 04 章"Unity 参考实现"里列 `SlopeSlideParams.cs`（M8-A 的 HSD 设计）：它只在 Fun 用，Reference 不用（`HsdMovementParams.Off()`）。§4.5 已写明，INVENTORY 可以加半句。

## 4. 和别的章的分界（请 hb-ch02 / 03 / 05 / 07 / 06 看一下）

- **02 章**：坡上的位置（U-1 上坡保持步长、U-2 圆底 16、`StayOnGround`）、走下台边离地（> 2 u）、蹲姿碰撞体尺寸——本章引用，没写细节。
- **03 章**：普通起跳（连跳惩罚 frac、半步重力、超速削减、+30 推墙 J-1）、蹲走的地面移动、空中加速、lurch——本章滑铲跳和 superglide 引用。注意：**滑铲跳不用超速削减**，§4.6 第 3 条写了，03 章写超速削减时最好也注一句。
- **05 章**：攀爬中按跳（蹬墙跳，`WallBounce`）、抓边悬挂——本章 §4.10 只指过去。攀爬本身我写在 04 章（因为"够不着先爬再翻"是翻越高度范围的一部分）。如果 hb-ch05 也写了攀爬，整合时二选一。
- **07 章**：滑铲 FOV、滑铲倾斜、翻越俯仰曲线叠到镜头（含 0.15 s 淡入）、冲刺眼高下沉的时间——本章 §4.8 写了眼高公式（含冲刺项）、§4.14 写了 S27 的 δ 曲线（附件 TSV）。hb-ch07 的事件表 `slide_start`（"starts eye 0.2 s"）和 `mantle`（`traversal-curves.tsv`）和本章一致；已核对：07 的 `07-camera/traversal-curves.tsv`（`handbook/ch07` 10ae546）和本章 `04-slide-mantle/s27-curves.tsv` 是同一套数（都从 `MantleBoostS27.cs` 抄），只是列的排法不同。整合时留一份（建议留 07 的，04 §4.14 改成指向它），另一份删掉。
- **06 章**：动作仲裁（翻越 priority 75、`handlesJump`）没写，留给 06。

## 5. 建议的 D 行（编号留空）

| D | 题目 | 选中 | 没选 | 数据 / 理由 |
|---|---|---|---|---|
| D-?? | 手册 04 章的"参考实现" | 正文写 R5 原生规则 = Reference 游戏身体（含 RPS、R6U、D-75）；Fun 的 HSD 斜坡滑铲和横向 superglide 只作为 [设计] 注明 | 把 Fun 的设计也写进规则段 | DIFF §三；用户 11-14"提炼成我们自己的技术"，以 R5 为核心（D-36） |
| D-?? | 重建检验的滑铲标准答案 | `handbook/04-slide-mantle/slide_ref.py`（照手册伪代码写、和 R5 实测对上） | 只用 Unity 回放基线 | 重建检验不应依赖 Unity 代码；脚本只用标准库 |
| D-?? | NS S-05 关闭 | "112 是结束后的蹲走命令"，S-05 改一致 | 再开 R5 测一次 | 124.75 − 1500/120 = 112.25（§4.3） |

## 6. 给总控的问题

1. 攀爬（§4.10）放在 04 章可以吗？还是要挪到 05 章（和蹬墙跳、挂墙放一起）？
2. 第 3 节第 1 条（Climb README 的 1.8 s 过时）要不要现在就派人改 HSD-Unity？今晚不合并 PR，所以我没动。
3. `slide_ref.py` 放在手册附件里是否合适（它是"标准答案"，重建检验会话不能先看）——如果担心泄题，hb-judge 可以只在评分时用。
