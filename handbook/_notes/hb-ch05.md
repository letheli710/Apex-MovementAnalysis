# hb-ch05 给总控和整合会话的备注（2026-11-14）

本章：`handbook/05-wall-external.md`（分支 `handbook/ch05`）。

## 1. 待研究（建议进 99-TODO-RESEARCH，编号沿用 / 新开 B05-x）

| # | 项 | 怎么补 | 优先 |
|---|---|---|---|
| B05-1（已有） | TF2 跑墙 P1 – P3：0.5 s 计时从没见到效果；墙跳后马上贴另一面墙；窗户辅助的地面起跳 / 墙跳 / lurch 三种触发（§5.6、§5.13） | TF2，ref-pilot-ai 做到一半（`L:TF2-Research/runtime/ref-pilot-ai/README.md` 结果没写） | 中 |
| B05-2（已有） | 墙跳排斥 M-2（§5.6） | 等用户定；定了以后在 Unity 跑一次"墙跳后马上按朝墙键"，测最早贴回时间（PDIFF 说没跑过） | 中 |
| B05-3（已有） | 快速上升时二段跳 M-1（§5.9） | 等用户定 | 中 |
| B05-6（新） | TF2 跑墙"向上输入 = 前进量 × 沿墙分量 × 0.65"怎么折算成竖直加速度：BSPEC / T3 只写"朝上限加速"。Unity 把它当开关（>0 就满加速） | 读 TF2 0x180185230 的墙面分支；或 TF2 实测"半按前进"和"斜看墙"两种 | 低 |
| B05-7（新） | TF2 挂墙的停住曲线和下滑曲线形状（§5.11 伪代码里线性是推断） | 照 GAPS B1 / B2 的数据逐帧拟合（数据已有，`g8_a` 的 `wh_*`） | 低（HSD 没做挂墙） |
| B05-8（新） | R5 攀爬蹬墙跳离墙 182.78 和普查 188 差 2.8 %、只按侧向键时 (140.9, 177.5) 不符合公式（§5.8） | 读 R5 `JumpOutOfWallRun` 0x140a50050 的攀爬分支 | 低 |
| B05-9（新） | R5 跑墙起跑 / 超时的镜头 punch 数值（第 07 章 §2.7 已列，这里只是提醒：R5 的 `wallrun_viewpunch_onStart/onTimeout_*` 键已知，值没读） | R5 classvar 读一次 | 低 |

## 2. Unity 和本章规则对不上的地方（不改 Unity，写给用户看）

TF2 规则（`WallRunAbility.Tf2BeforeMove` / `Tf2WallJump`）相对 BSPEC / TF2 少做的：

1. 0.07 s 重试间隔（Unity 每条命令都判）。
2. 墙顶减速 3000·k、墙面转折 > 37° 脱落。
3. 蹬墙跳"视线和输入都朝墙时离墙速度最多减 80 %"。
4. 滑铲超级跳 cutoff +200；跳板 / 重力炮发射时 refZ = 弹道最高点。
5. 0.5 s 计时（BSPEC 写了"不实现"，现在规则已读清，GAPS A4）。
6. 贴墙距离 17 / 13 u 没按距离量，用碰撞层的接触 + 0.1 s 宽限。
7. 向上输入只当开关（见 B05-6）。
8. TF2 规则下二段跳的恢复仍用 HSD 开关（抓边、上滑索也恢复），TF2 只有落地、跑墙、skip。
9. HSD 加的（有意，[设计]）：视线朝墙 35° 内不起跑（归 R5 攀爬）；有未用跳键的命令不起跑（M8-A）。

建议进 R5-DIFF 的"TF2 预设"小节（如果有），或者 DECISIONS 一行"TF2 预设的已知简化"（下面 D 行）。

## 3. 过时 / 矛盾的文档（本章按右边写）

| 文档 | 说法 | 以什么为准 |
|---|---|---|
| `tf2/wallrun/T3-REPORT.md` §2.1 | 起跑时竖直速度"提到至少 250" | T5 §5.1：vz' = min(250, vz + 250)（T3 正文后面已注更正，表里没改） |
| `tf2/wallrun/T3-REPORT.md` §2.4、BSPEC §2 | 墙跳后 0.2 – 0.4 s 排斥 | 死代码（#115 RNT N1），实测无效（GAPS A5） |
| `tf2/wallrun/WALLRUN-B-SPEC.md` §2 最后一行、`TF2-MOVEMENT-SUMMARY.md` §6.1 第 2 条 / §11 | 0.5 s 计时含义未知 | GAPS A4："不跳而离地"的时刻（00-INVENTORY 已列） |
| `TF2-MOVEMENT-SUMMARY.md` §4.3 / §11 | 二段跳"上升中只叠加 0.25H"没触发 | GAPS A6 实测：是 +150 速度 |
| `research/phase2-local/m7/unity/M7A-UNITY.md` §1 | 跑墙在 `Traversal/WallRunAbility.cs` | 现在是 `Abilities/WallRun/WallRunAbility.cs`（D-69 前后的目录整理） |
| `R5MotorTf2WallRunTests.cs` 文件 | 文件名 | 类名是 `Tf2WallRunTests`（测试名照 class 写） |

## 4. 参数名和 tables 对不上的地方（给 hb-tables）

- params.tsv W-01 – W-15 用 `preset.Reference.hsd.*` 路径，但 Reference 里这些能力是**关的**（`enabled = false`），游戏默认在 Fun。建议改成 `preset.Fun.hsd.*` 或在含义列注明"Reference 关、值同 Fun"。
- params.tsv 没有 M7 的大部分设计值（`minStartSpeed`、`entryVzMin/Max`、`jumpNormal`、`jumpUp`、`jumpMaxSpeed` 等）和 B / A 的 `gravityRampTime`、`decelerate*`、`friction`、`timeLimit` 的 A 值、`repelTime`。本章 §5.3、§5.7 的表有全部，可以照抄。
- W-01 的"TF2 值"列写 1.75，是 TF2 的 `wallrun_timeLimit`，但这一行是 M7 的 `maxDuration`，放在一起容易以为 M7 对应 TF2；建议 TF2 列写"—（M7 是 HSD 设计）"。
- 墙跳 `wall_kick`：camera-events 里叫"蹬墙跳"，本章 §5.5 / §5.7 是"跑墙中按跳"，§5.8 是 R5 攀爬中按跳。两者镜头都没有 kick（第 07 章 §2.7），名字可以共用，但建议在表里注一句"含两种"。

## 5. 想改别章 / README 的地方

- 第 03 章表格第 25 行说"跳板、击退等外力打开的 lurch 窗口"在第 05 章：本章 §5.13 后的总表就是它，整合时把链接指到那一节。
- 第 04 章 §4.10 第 2 条"按跳 → 蹬墙跳（第 05 章）"：指向本章 §5.8。

## 6. 建议的 D 行（编号留空）

| D | 题目 | 选中 | 没选 | 数据 / 理由 |
|---|---|---|---|---|
| D-?? | 手册写跑墙时以哪套为"默认" | 写清：游戏默认 M7 设计（Fun），B 是"基准"但默认关，A 是对照；三套并列写 | 只写 B（会让人以为游戏里跑的是 B） | D-57 / D-58；LS-18 – LS-20 |
| D-?? | TF2 预设的已知简化（§2 清单 1 – 8） | 记成"TF2 预设和 TF2 的差别"一张表，等用户定哪些要补 | 悄悄不写 | 本备注 §2 |
| D-?? | 技能层向上天花板削竖直跳板发射（X-2） | 等用户定 | A. 天花板抬到 ≥ 1150 u/s；B. 保持，写进 R5-DIFF | §5.33；LS-24 原因（pad-probe） |
| D-?? | 竖直滑索往下看（X-1） | 等用户定 | A. 保持 Reference 拒绝（dedi 结果，M9-A）；B. 按 D-13 改成跟客户端（往下滑） | §5.22；ZA1 |
| D-?? | 滑索 / 钩爪的 HSD 自定值进 R5-DIFF | 建议整合时在 R5-DIFF 补 Z 组（滑索）和钩爪 HSD 自定值（X-7） | 不记 | §8 滑索第 8 条、§8 钩爪 |

## 7. 外力部分查出的 HSD 和 R5 不一样（要用户看；不改 Unity）

汇总（细节和复现在 §8 各部分）：

| # | 项 | R5 | HSD 现在 | 出处 |
|---|---|---|---|---|
| X-1 | 竖直滑索往下看能不能挂 | S21 客户端预测挂上、S3 dedi 不派发，0.04 – 0.09 s 后被拉回（混合构建分歧，R5 结果未定） | Reference 跟 dedi：拒绝（M9-A 选的，早于 D-13）。可能和 D-13（客户端服务端不一致时跟客户端）冲突 | §5.22；§8 滑索第 7 条 |
| X-2 | 技能层向上天花板 `SkillRules.maxUpSpeed` 1100 u/s | 竖直向上的跳板发射 1150 u/s 不被削 | 被削到 1100，最高 810.3 u 而不是约 885 u（这就是 LS-24 = 841 的一半原因；另一半是 harness 没落地、连续弹了 20 s） | §5.33；§8 跳板 C-1 |
| X-3 | 软着陆结束降速（M4b 发现） | 小跳再落地后移动倍率回到 1.15 | 没做，`LandingSlowdown.f0` 不清。**也属于第 03 章 §3.9，请转 hb-ch03 / hb-integrate** | §8 跳板 C-2 |
| X-4 | 跳板冷却 | 玩家级，和重力炮共用 1 s | 每个能力实例一份 | §5.32；§8 跳板 C-4 |
| X-5 | 击退的速度上限 | 合速度 1000（或推之前的 \|v\|） | 另有技能层水平 900 u/s 天花板，也削击退（没测具体情形） | §5.37；§8 跳板 C-5 |
| X-6 | 钩爪：R5 原生的交叉刹车（D-34）、从真实眼高（70 / 64 / 32 u）出钩 | — | **没有 EditMode 测试**：`GrappleM10ATests` 全部跑在 `GrappleParams.Measured()`（M10-A 拟合刹车、眼高 60、GN 以前的脱钩），M10A §3 对照表没在现在的 Reference 规则下重跑 | §5.25 – §5.27；§8 钩爪 |
| X-7 | 钩爪：HSD 自己的值 1100 u/s 水平天花板、3.0 s 卡住保护、没挂上也扣 10 s | — | 都是 [设计]，R5-DIFF §三（有意偏离）没记 | §8 钩爪 |
| X-8 | 传送门离开后 1.0 s 不能再进 | 没实测（B05-5） | 测试只检查参数值 1.0，没测行为 | §5.43；§8 传送 |
| X-9 | Rift / Breach 同一个旅行引擎两种拟合 | floor(clamp/0.1) + 0.2 s 和 round + 0.152 s 各自对上各自的实测 | 两种都留 | §5.43、§5.44 |

## 8. 外力各部分的缺口、过时文档、参数表问题（原样保留各部分的整理）

### 滑索（§5.15 – §5.24）
#### 1. 缺口（待研究，建议编号 B05-x，号留空）

| 建议 | 内容 | 怎么补 | 优先级 |
|---|---|---|---|
| B05-? | **下坡绳**的速度曲线（有没有坡度项）。A3 只测了平绳和 10.6° 上坡 | R5，在 m6zip 斜绳从高端挂上 | 中 |
| B05-? | **80 u 高的绳 R5 挂不上**（0 / 10），HSD 能挂；蹲着平视挂不上的真正原因（HSD 用 `crouchFindRaise` 50 [推断] 复现） | R5 + 读 `Zipline_Use` 之前的门 | 低（HSD 地图没有 80 u 的绳） |
| B05-? | 空中锁定的真实来源：一个约 0.35 s 的计时器还是跳离 / 蹲下各一个（跳离 0.334 能挂、蹲下 0.359 还拒绝）；setfile `useZiplineCooldown` 0.4 是不是它 | R5 加密扫 0.33 – 0.41 s | 低 |
| B05-? | 次数限制用的是 S21 客户端冷却阶梯（0.1 / 0.2 / 1.0 / 3.0 / 5.0 s）还是 3 次计数；3 s 恢复一次没测 | R5 | 低 |
| B05-? | 竖直绳往下看挂上：S21 零售版到底往下滑还是拒绝（混合构建客户端 / dedi 分歧）。HSD Reference 拒绝是设计 | 需要 S21 服务端或录像 | 低 |
| B05-? | Super Jump 窗口从"离地"算还是从"挂上"算（从台沿不着地挂上就能分开）；`jump_graceperiod` 读取（和 B03-1 合并）；**空中挂上 / 钩爪交接后**能不能 Super Jump（HSD 不能 [设计/推断]）；Super Jump 后能不能 lurch（HSD 能 [推断]） | R5 | 中 |
| B05-? | **地图斜绳 / 陡绳的跳离方向**：A3 只测了平绳；HSD 地图绳一律水平投影，枪绳斜绳沿三维、陡绳沿视线。wiki 说 > 45° 都能朝任意方向 | R5，m6zip 斜绳和一根 > 45° 的 `CreateZipline` 绳 | 中 |
| B05-? | 竖直绳蹲下松手（HSD 沿视线 min(v, 400) [推断]） | R5 | 低 |
| B05-? | 空中挂上的上抬（HSD 0 [设计]）；入绳速度 > 600 时的处理（HSD 直接降到上限 [推断]）；入绳速度和骑行方向相反时 | R5 | 低 |
| B05-? | 钩爪 → 滑索交接的真实触发条件（GZ §4：距离、钩爪自己结束、还是计时）；端点区内的交接（HSD 拒绝 [设计]） | R5，改起始距离 150 / 250 / 350 u | 低 |
| B05-? | 枪绳的钩爪交接速度：R5 1 次重新加速，HSD 保留入绳速度 | R5 多测几次 | 低 |
| B05-? | 枪绳：8000 u 最远距离；跑墙 / 挂墙开火；墙上终点的位置；举枪 < 1.0 s 能不能开火；44.4° – 52° 之间和下坡陡绳的到端出口；1000 上限的来源键；斜枪绳 R5 提前脱离 96 – 111 u（HSD 90） | R5（需要更大的场地） | 低 |
| B05-? | 骑行中被墙挤开 / 绳穿过实体（HSD `pathTolerance` 8 u [设计]）；wiki 说的"通过滑索储存竖直速度"（M10C-UNITY 第 148 行记为没做） | R5 | 低 |
| B05-? | 曲线滑索（ziprail）：setfile 有一整套 `ziprail*` / `maxJumpOffSpeed` 550 / `minJumpOffSpeed` 100 / `viewInfluenceOnJumpDirection` 0.5，NP2 §2 读到了规则，但 HSD 没有曲线绳，R5 本地图也没测 | 先决定要不要做曲线绳 | 低 |
| B05-? | 地图滑索的典型长度（LS 表第 76 行已记） | 需要 R5 地图数据 | 低 |

#### 2. 过时 / 矛盾的文档

1. **M8A §4 有三行已过时**：表里 "Air mount: Reference refuses"、"Active jump-off … lurch window opened"、缺陷 1 的 `refuseMountAtEnd (true)` 都是 M8-A 当时的 Reference；M9-A 已改成按 R5（空中可挂、跳离不开 lurch、端点区反向），现在只有 Fun 保留。手册按 M9AU 写。
2. **A3 有几处结论已被后来推翻或补上**：§4（第一轮"没有 Super Jump"，文件自己标了被 §9.2 推翻）；§5、§7 的"空中挂上没测 / dedi 拒绝"被 ZA1 推翻（那次是够不着，ZA1 65 / 65）；§8 第 12 条"400 找不到来源"→ N4A 读回 `ziplineJumpOffSpeed` 400；§2 "加速切换按时间还是按速度 [open]"→ setfile `mountZiplineTime` 0.5 支持按时间。
3. **ZG TL;DR 的陡绳出口"vz ~485 after 0.1 s"和逐次数据不符**：ZGO `ride_s50` 0.1 s 后是 404.3 – 416.5（M10BU 用的是这个，并推回脱离时 473 – 486）。"485"像是把脱离时的数写成了 0.1 s 后。
4. **TL §5.2 的 wiki 数和 R5 不符**：竖直绳"480"（R5 竖直绳实测 600）、"手动下绳最大 445"（R5 400）。手册以 R5 为准，正文已注明。
5. **`Rail.attachRadius` 48 的代码注释**写"R5 zipline attach range not measured"，已经测了（候选 120、抓点 130），而且滑索不读这个字段。建议在 Unity 注释里改掉（不是手册的事，写进 _notes）。
6. **level-scale LS-26 / LS-27 叫"滑索枪绳长范围"不准**：700 / 8000 u 是原点 → 落点的距离，不是绳长（800 u 落点的绳长 780.8 u）。建议改成"滑索枪落点距离"。LS-28 写"滑索枪的绳 1000 u/s"——是上限，不是恒速（约 2.3 s 才到）。
7. **可能和 D-13 冲突**：D-13（10-23）"客户端和服务端不一致、又有社区证据时，Reference 跟客户端"。竖直绳往下看是客户端挂上、dedi 拒绝，wiki 有"竖直绳尽量往上送 / 强制向上区"的说法，但没有说往下看会往下滑；M9-A（10-22，早于 D-13）选了 dedi 的结果（拒绝）。是不是要按 D-13 重新看，交给用户，手册两边都写了。
8. **R5-DIFF 没有滑索移动的条目**：R5-DIFF 只记了滑索镜头（C-12、K-7、K-8）。Reference 里和 R5 不完全一样、或 R5 没测而 HSD 自己定的：空中锁定 0.35（R5 0.33 – 0.40，蹲下那一小段不同）、`airMountLift` 0、`crouchFindRaise` 50、竖直绳往下看拒绝、80 u 绳能挂、`pathTolerance`、端点区内的钩爪交接拒绝、枪绳的钩爪交接速度、斜枪绳的脱离距离 90 对 96 – 111。建议整合时在 R5-DIFF 第二节（还和 R5 不一样）补一组 Z 条目（写进 _notes，不改 DIFF）。
9. **地图陡绳和枪绳陡绳的跳离规则不同**：HSD 地图陡绳（M8-A 的 60° 测试）水平投影跳出；枪陡绳沿视线。R5 只测了枪陡绳。不是 bug，但读者会困惑，正文 5.19 第 6 条已注明。

#### 3. 参数名和 params.tsv 对不上的地方

1. **Z-06 `rideAccel` 的 R5 键名写成 `pathGravityAcceleration`，应该是 `ziplineAcceleration`**：N4A census 里两个都是 400，但 NP2 §2 原生"加速 `ziplineAcceleration`"、TL wiki"`ziplineAcceleration` 400 = 0.5 s 后的 400 u/s²"都指向 `ziplineAcceleration`；`pathGravityAcceleration` 更像曲线绳 / 路径的重力项。建议 Z-06 改名并把依据改成 N4A。
2. **表里缺的滑索参数**（Unity 导出路径同 `preset.Reference.advanced.zipline.*`）：`findRaise` 72、`findRadius` 130、`collectorRadius` 120、`crouchFindRaise` 50、`coneHalfAngle` 34°、`verticalFindRaise` 80.1、`mountLift` 22、`airMountLift` 0、`endZone` 90、`airRemountLockout` 0.35 s、`budget` 3、`budgetRegen` 3 s、`hangBelow` 80、`firstRideSpeed` 8.333、`mountAccel` 600、`mountStateTime` 0.5 s、`verticalTopPush` 400、`verticalTopHang` 80.16、`superJumpWindow` 0.2 s、`grappleMountDistance` 136、`grappleEntryAccel` 400、`pathTolerance` 8；`Rail.stopShort` 90（世界数据，不在 preset 里）。
3. **滑索枪一行都没有**：`ZiplineGunParams`（`minDistance` 700、`maxDistance` 8000、`projectileSpeed` 2600、`startOffset` 16、`startHeight` 112.1、`endHeight` 112.7、`wallStandoff` 16、`steepDirZ` 0.7、`maxRopes` 10、`refundTime` 3、`cooldown` 180、`raiseTime` 0.5、`aimTimeout` 20、`eyeHeight` 60、`ropeEndClearance` 2）和 `RailRide`（`speed` 1000、`mountAccel` 1000、`rideAccel` 280、`detachSpeedMin` / `Max` 600）。导出路径要 hb-tables 定（枪参数在 `MovementConfig.ziplineGun`，`RailRide` 不序列化）。
4. **Z-03 `maxVerticalDetachSpeed` 1500 标"一致"**没错，但值得加一句"现在碰不到（绳速最多 600 / 1000）"。
5. setfile 里有、Unity 没有对应参数的键：`ziplineJumpOffDampScale` 1（等于 1，不影响）、`ziplineJumpOnAcceleration` 1000、`useZiplineCooldown` 0.4（HSD 用 0.35）、`grapple_lastZiplineCooldown` 0.5、`ziplineCanMelee` false。**推断**（没验证）：`ziplineJumpOnAcceleration` 1000 可能就是枪绳挂上状态的 1000 u/s²，而地图绳第一条命令的 8.333 u/s = 1000 u/s² × 1/120 s；地图绳挂上状态的 600 u/s² 在 setfile 里没找到对应键。值得在 B05 里加一条"用 60 / 144 fps 测第一条骑行命令的速度"来验证。

#### 4. 本节用到的出处缩写

见文件开头"本节出处缩写"表：NP2、A3、GZ、ZA1、ZG、ZGO、M8A、M9AU、M10BU、SV、N4A、TL、DIFF、DEC、U:。另外引用了 `handbook/00-INVENTORY.md` / `99-TODO-RESEARCH.md`（B03-1，在 `handbook/base`）和 DESIGN-PHILOSOPHY P3 / P4（main）。

#### 5. 备注

- 镜头：本节只在白话说明和 5.21 第 7 条各有一句指向第 07 章（`zip_eye_offset`、`rope_roll`、`zip_detach`）。挂上时的"视角拉向绳子"写在 5.16，是输入规则；如果 07 章也想写，建议 07 章只引用 5.16。
- 仲裁：本节写了"滑行中能力拥有跳跃键"、"跳离 → Super Jump → 二段跳 → 无，一次一个"、"谁能打断骑行"的结论，细节全部指向第 06 章。`ZiplineAbility` 的仲裁行是 `AdvancedMovementParams` 里的 `SkillTraits("zipline", 65, interruptible, …, maxDriving 40 s) { handlesJump = true }`（`U:…/Abilities/_Core/AdvancedMovement.cs`），06 章可以直接用。
- HSD 二段跳（Fun，D-08）挂上滑索时会补满（`DoubleJumpParams.resetOnZipline`），属于 06 章。
- 测试类名都按 C# `class` 声明核对过：`A3Zipline`（R5MotorM6ZiplineTests.cs）、`ZiplineM8Tests`（R5MotorM8Tests.cs）、`ZiplineM9ATests`（R5MotorM9ATests.cs）、`ZiplineGunM10BTests`（R5MotorM10BTests.cs）、`WallChainM8BTests`（R5MotorM8BTests.cs）、`RiftM10WTests`（R5MotorM10WTests.cs）、`JetDriveM9CTests`（R5MotorM9CTests.cs）。每个方法名都 grep 过存在。
- 共享日志：这个子任务只写草稿，没有往"HSD 版本溯源"日志写条目；上面第 2、3 节里的问题（尤其 2.3、2.7、3.1）如果要记，由 hb-ch05 或整合者写。

### 钩爪（§5.25 – §5.31）
#### 缺口（待研究，建议进 99-TODO-RESEARCH）

1. **原生横向刹车（D-34）和眼高打钩没有 EditMode 单元测试**。`GrappleM10ATests` 全部跑在 `GrappleParams.Measured()`（M10-A 拟合刹车、眼高 60、pre-GN 脱钩）上；Reference 的 `nativeCrossBrake` / `nativeEye` 只在 `FeelBatch` 手感对照里验证。建议补一个 Reference 配置下的拉动 / 钩点测试。
2. **p0 差 −16.6 %**（R5 728 对 HSD 608）是 M10-A 时的数，改成眼高 70 + 原生刹车以后没复核（M10A §8；Grapple/README "已知差异"第一条）。M10A §3 整张开环对照表也是 M10-A 拟合刹车的数，Slingshot 在原生刹车下约 830（README F3 节），没有重新出表。
3. 挂上跳窗口 0.15–0.2 s 之间（19–23 条命令）没测；空中挂上有没有窗口没测。
4. 视线规则的两项原生豁免（慢动作、"向上且同向更陡"的向量 0x142373684）没认出，HSD 没做。
5. G-2（267–533 u/s 慢速贴近）、G-4（绕钩横飞）、远离 > 500 实际脱钩：没有 R5 片段。
6. `grapple_detachHorizontalMaxSpeed` 600、远离脱钩的 +200 上抬、`grapple_gravityPushUnderContribution` 2、`grapple_around_obstacle_accel` 1000、`grapple_autoMantle` 0.25、`grapple_windowCheckDist` 150、`grapple_autoAimAngle` 10°、`grapple_gracePeriod` 0.25 s：都只有数值，没读用在哪个分支 / 没测，HSD 都没做。
7. 竖直射程 `grapple_maxLengthVert` 没测；有效射程比 850 短 10–20 u 的原因（射线起点 / 钩子大小）没拆开（GR §3）。
8. 钩到会动的实体（R5 钩点跟着走、实体状态变化脱钩）、钩到玩家 / NPC（绳子指向对方眼睛、近战 1.0 s 时限、`grapple_autoMeleeOnDetach`）：没测，HSD 没有这类目标。
9. 按住 S 拉得更快（Apex 740 对 612，TF2 反而减速）、TF2 侧键加速小、TF2 起步只有约 75：要读两边的拉动函数（TN6 §3）。
10. G-6 的上抬在哪一步被覆盖、热身那次世界墙父实体 0x11fbc 是什么（G6 §7）；DESIGN-PHILOSOPHY §10.3 记"是不是混合构建造成的没定"。
11. 第二次按键的 0.5 s 防抖（`detachOnGrapple`）HSD 没做；飞行 / 准备中再按 = 取消、没挂上扣 10 s 都是 HSD 设计，R5 没测。
12. Tether / rodeo 绕圈 HSD 313° 对 R5 393°（R5 贴岩石底面刮 + 本地 dedi 不执行视线规则）；Super Grapple、Slide Grapple、Double-Bounce 在 R5 里没复现，没建模（M10A §4、§8）。
13. A-1 剩 1 条命令（场景 / 拉力近似），GN 没调（GN §6）。

#### 过时 / 矛盾的文档

1. **"Apex 地面发射清水平速度"**：TN6 §1 表和 §2.2（"地面发射时清掉水平速度：冲刺 297 → 0"）、GM10 TL;DR（"The fire kills the horizontal speed before the attach"）都这样写；M10A §1 查清是测试脚本在发射那条命令松开了 W 和冲刺，速度按 1250 u/s² 无输入地面减速掉光，**没有这条规则**。本节按 M10A 写（5.25 规则 6）。TN6 §3 的 TF2 预设改法里"地面发射不清水平速度"也因此不是区别。
2. **钩子飞行速度**：TN6 §2.1 说 Apex 实测 261 / 410 / 713 u 用 0.125 / 0.200 / 0.350 s "正好是 ÷ 2000"（ConVar `grapple_shootVel` 2000）；HSD 用 M4b 拟合 2034.9 u/s + 0.0043 s（GR §3："up to 1200 u within one command"）。两者在测过的范围里分不开。本节两边都写，HSD 现在 = 拟合值。
3. `GrappleAbility.cs` 类注释和 `Description` 字符串仍写"hook from origin + 60"、"release 45 u from the body segment, on passing the hook (> 85 deg)"、"look-away 100°"，是 M10-A 的样子；Reference 现在是眼高 70 / 64 / 32、原生接近距离、视线 90°。`GrappleS21Params.nativeDetach` 注释写"The vertical boost the client adds on some detaches is not modelled"，G6 之后 `impactBoost` 已经是开关。`GrappleS21Params.nativeLowSpeedTimer` 注释还写"with a ground entity 0.7"，但代码在开关打开时一律用 1.5（和 GN 结论一致，只是注释容易误读）。这些是 HSD-Unity 的注释，不在手册范围，建议记进 `_notes`。
4. `Abilities/Grapple/README.md` "已知差异"第 1–2 条（p0、制动门控）是 M10-A / F3 之前的数，"Unity 早约 2 条命令脱钩；R5 撞墙时竖直速度 +12 u/s"那句 GN 已解决（N13：+12 是岩石面后倾，不是上抬）。
5. DECISIONS 第 168 行附近：rodeo 之前被记成"攀在对手身上"，N12 已更正（钩岩石后转圈）。手册按 N12 写。
6. N13 §4.2 的推断"钩在世界上时有父实体"被 GN 反过来更正（父实体 = 钩到的道具）；N13 文件里已加了更正注，引用时以 GN 为准。
7. P2 §1.3 把"脱钩时竖直上抬 200"、"水平封顶 600"、"脱钩后重力 0.5"列成脱钩通用规则；N6 / N13 查清 +200 只跟远离规则；600 和脱钩后重力在实测里都没起作用。P2 §5 P-08 – P-10 的"未定"在 §8 / N6 已改成一致。
8. `R5-DIFF-ARCHIVE.md` 第三部分"有意和 R5 不一样"没有列钩爪的 HSD 设计值：带 S21 钩爪身体的水平上限 1100 u/s、3.0 s 卡住保护、没挂上扣 10 s、飞行中再按 = 取消。建议补进去（或在 `_notes` 提给 hb-integrate）。

#### 参数名和 params.tsv 对不上的地方

| 行 | 问题 | 建议 |
|---|---|---|
| P-08 `grapple.wishCap` | Unity 值写 420，但实际上限是 420 × msc = 483 u/s（实测 483.000）；表里没注明 × msc | 含义里加"× 移动倍率（空手 483）"；P-07 `airAccel` 注明"不乘 msc" |
| P-09 `grapple.hopVz` | 依据只写 [数据] setfile；本地 dedi 的 setfile 读成 0、客户端 200（[hyb]，GM10） | 依据加"[实测] 挂上后 193.7；dedi setfile 读 0 [hyb]" |
| P-13 `detachAwaySpeed` | "一致"，但 R5 从没实测到它脱钩（GN §2），而且只对世界钩点 | 依据去掉 [实测] 的暗示，写"[数据] [反编译]；只对世界钩点；没直接观察到" |
| P-16 `lowSpeed` | 设置块下标是推断（N13 §2）；Unity 现在量径向速度（G-4） | 依据加 [推断]；含义改成"朝绳子的径向速度 ≤ 250" |
| P-17 `lowSpeedTime` | 有实测 1.508–1.517 s（N6 §1.3），表里只写 [数据] | 加 "[实测] N6 1.508–1.517 s" |
| P-18 `impactBoostSpeed` | "和 R5 一致吗：一致"容易误读：值一致，但默认关（R5 实际移动没有） | 改成"值一致；作用默认关（D-52）" |
| P-01 `range` | 依据没写实测有效射程 | 加 "[实测] GR 830–840 u（pitch 0）"；LS-25 同 |
| P-11 `detachLengthMin` | "[实测] M10 35–53" 是到身体竖线段的距离（pre-GN 量法），不是原生距离 | 改成"[实测] N6 贴地 45.0–47.1 u" |
| 缺行 | `s21.detachRampMax` 400（ConVar `grapple_speedRampMax_human`）、`s21.ropeLift` 25、`s21.ropeBase` 23、`grapple.hookSpeed` 2034.9（ConVar 2000）、`grapple.attachLatency` 0.0043、`grapple.windup` 0.2005（ConVar 0.2）、`s21.gravityHelpCos` 0.8、`s21.impactBoostMax` 300、`GrappleS21Params.HorizontalCeiling` 1100 [设计]、`grapple.maxPullTime` 3.0 [设计]、冷却 `s21.drainBase` / `drainMinDist` / `drainMaxDist` / `clip` / `regen` / `trackSpeed` / `trackTime` / `trackPoll` | 建议补 P-19 起 |
| 命名 | params.tsv 用 `preset.Reference.grapple.s21.*`；Unity `ParameterDictionary` 导出的键是 `s21.<字段>`（拍平在 `grapple` 下），一致。`gravityFrac` 对应 R5 `grapple_gravityFracMin`（不是 `Max`），表里含义已写对 | 无 |
| LS-25 | "钩爪最远距离 850 u … 不是模拟" | 加"从眼睛（70 u）量；实测有效 830–840 u（pitch 0）；竖直方向没测" |

#### 出处缩写表

见本节开头"本节出处缩写"：P2、N6、N13、GN、G6、N12、LG、SW、GR、GM10、M10A、GZ、SV、TN6、TN2、FEEL、DIFF、DEC、U:。和第 04 章已用的缩写没有冲突（04 章用 NS、NG、NJ、NM、SM、SD1、N4C、R6、RPS、A2、SG、D72、B1、FEEL、DIFF）；`G6` 和 DIFF 的 "G6 节"同名，整合时如果嫌混可以改成 `G6R`。

### 跳板和击退（§5.32 – §5.39）
#### A. 判断：兴奋剂不是外力

兴奋剂只改移动倍率（和武器倍率、落地降速相乘，技能层取最大并封顶 1.40），没有任何速度增量。按 05 章的分类它不属于"外力"。建议：

- 规则主体放第 03 章 §3.1（速度上限和移动倍率），写成"倍率来源之一"；技能结构（槽位、6.7 s 锁定）放第 10 章。
- 05 章只留一句"兴奋剂不改跳板弧线（跳板替换速度）"，或保留本草稿 §5.36 的短条目——由你定。我写了完整五段，方便你搬。

#### B. 缺口（待研究，建议进 99-TODO-RESEARCH）

| 编号建议 | 内容 | 怎么测 | 优先级 |
|---|---|---|---|
| B05-P1 | 跳板正好 0 速度时的方向（HSD 推断竖直向上） | R5：跳板放在脚下，站着不动等它弹 | 低 |
| B05-P2 | 跳板 1 s 冷却、和重力炮共用（只有代码 / SDK） | R5：连踩两个跳板，间隔 0.5 / 1.0 / 1.5 s | 低 |
| B05-P3 | 跳板飞行中的空中转向（M4 没给左右键） | R5：发射后按住 A / D | 中 |
| B05-P4 | 慢放 0.8 的原生来源（`m_airSlowMoFrac`？） | Ghidra 读字段 | 低 |
| B05-P5 | 跳板二段跳：同一命令按方向键的结果；分界 357.35 – 360.04 的含义；二段跳后 lurch 上限 212.55 | R5 / Ghidra | 低 |
| B05-P6 | "任何人踩跳板都能二段跳"的出处：M8 只测了 Octane；HSD README 这句话的来源没找到 | R5：别的传奇踩地图跳板再按跳 | 中（决定 HSD 地图跳板要不要对所有预设开） |
| B05-P7 | 软着陆结束降速的那 2 / 12 例外；落地马上再跳的其他时机 | R5 | 低 |
| B05-K1 | 地面门槛的精确值和比较方式（服务端 exe） | Ghidra 建 `r5apex_ds.exe` 工程 | 低（已有 B05-4） |
| B05-K2 | 已经快于 1000 时被推；`SpeedLossLimit` 50 | R5 推力扫描加初速 | 低 |
| B05-K3 | 跑墙 / 钩爪 / 滑索 / 翻越 / 跳板飞行中被炸 | R5 或 TF2（已有 B05-4） | 低 |
| B05-K4 | `impulse_low_decel_duration_scalar` 服务端运行时的值；窗口里的完整落地轨迹 | R5 Frida / 推力扫描延长采样 | 低 |

#### C. HSD 和 R5 不一样、写本章时新查出来的（由 hb-integrate 判断要不要记 DIFF / 建 D-??）

1. **技能层向上天花板 1100 u/s 削掉"竖直向上"的跳板发射**（非 Octane 身体踩地图跳板、没有水平速度时：1150 → 1100，最高 810.3 u 而不是约 885 u）。`SkillRules.maxUpSpeed` 的注释"按跳板 1028.6 定"早于 M10-C2 的"竖直向上"规则。可选：A. 默认天花板抬到 ≥ 1150；B. 保持，写进 DIFF。D-??。
2. **软着陆结束降速（M4b 新发现，10 / 12）HSD 没做**：`LandingSlowdown` 遇到 f ≥ 1 的落地直接返回，`f0` 不清。复现：Octane S21、冲刺上跳板、落地后第 4 条命令起跳，小跳落地后 `f0` 仍是 0.227。R5 这时移动倍率已回到 1.15。这条也属于第 03 章 §3.9，请转给 hb-ch03。
3. **游戏身体跳板落地 vz −1028.9 对 R5 −1024.5**（f0 0.227 对 0.242，落地后水平 116.8 对 124.6 u/s）。推断落地判定晚一条命令。只在 `PracticeSession` 平地跳板上跑过；手感对照第 3 批（回放场景）没报，没复核。
4. **跳板冷却是每个能力实例一份**（R5 是玩家级、和重力炮共用）。
5. **HSD 水平天花板 900 u/s 也会削击退**（R5 合速度上限 1000）。没测具体情形。
6. 跳板 `maxEffect` 6.0 s 保护会在"原地一直弹"时切掉慢放（R5 没有）。正常飞行碰不到。

复现程序：`handbook/05-wall-external/pad-probe/Program.cs`（LS-24：`dotnet out/lvl.dll "Wraith S21"` / `"Octane S21"`）和 `handbook/05-wall-external/pad-probe/hop/Program.cs`（落地再跳）。用的是 hb-tables 的 harness 写法（`lvl.csproj` 里有编法）和 `HSD-Unity-HBT` 工作树里 `units/switch` 5c79a50 编出的 DLL（移动代码和 main 一样）。

#### D. 过时 / 矛盾的文档

| 文档 | 写的 | 现在 |
|---|---|---|
| `research/epg/EPG-ROCKET-JUMP.md` §7（main） | 建议不做地面门槛、"离身体中心约 70 u 内满额" | RJ §2.2、§5（#85）：做门槛 312.5；距离按"沿连线到身体表面" |
| `research/epg/EPG-ROCKET-JUMP.md` §3（main） | "31500 一下就有 266"，像是有台阶 | RJ §5：266 是 0.1 s 后的采样，初速 315，没有台阶 |
| 工作区 `TODO.md` 第 104 行 | "火箭跳等 TF2 研究出来后照那边做" | D-77 定为 A（R5 原生） |
| 工作区 `TODO.md` 第 28 行 | "HSD 火箭跳（D-56）怎么做等你定" | 同上 |
| main 的 `DECISIONS.md`"还没结论的事" | D-56 还开着 | #85 里已定，没合并 |
| `research/rea-native/subsystems/N2-T-TIMING-INPUT.md` §5、§6 T-04 | "跳板是否走冲量队列还没确认"、用跳板 1150 举窗口例子 | NP2 §3 已确认不走 |
| `SkillRules.maxUpSpeed` 注释（HSD-Unity main） | "measured maximum: jump pad 1028.6" | M10-C2 以后跳板可以竖直 1150 |
| `handbook/tables/level-scale.md` LS-24 | "比纯公式低，原因没查" | 查清了：1100 天花板 + 程序一直弹（§5.33） |
| `OCT` §3.7 / §3.5 | 二段跳授予 0.1 s、冷却 1 s 都是 [src] 没测 | 授予 M8 测了 0.108 s；冷却仍没测 |
| `M10C-U` §2.3 | 滑铲加成冷却 1.8 s | 第 04 章写 2.0 s（D-17 改成 R5）——不是本部分的事，顺带提醒 hb-ch04 / hb-integrate 核对 |
| `HSD-Unity: …/PadDoubleJump/README.md` | "R5 里任何人都能拿到" | 来源没找到，M8 只测 Octane（B05-P6） |

#### E. 参数名和 params.tsv 对不上的

1. **F-03** `defaults.JumpPadParams.duckedVertScale`："原生默认值待读"——N4A 已读：客户端原生 1、本地生效 0.5 [hyb]。依据列应改。
2. **F-09** `defaults.StimParams.severity`：R5 原值写 0.15、"近似（差 0.65 %）"。0.15 是脚本值；R5 实测行为是 38/255 = 0.149020（OCT §2.1，拟合到 1e-6），Unity 和**实测**一致。建议 R5 原值写"0.149020（实测；脚本 0.15）"、状态"一致"。
3. **表里没有的参数**（本草稿用了，建议补行）：
   - `JumpPadParams.radius` 32、`hullRadius` 16、`above` 32、`below` 16、`slowMoScale` 0.8、`debounce` 1.0、`pushScale` 1、`straightUpWithoutMotion`、`phasedNoLaunch`、`launchOpensLurchWindow`；
   - `OctaneParams.padStraightUpWithoutMotion` / `madHops` / `airborneAgility` / `padPushScale`；
   - `PadDoubleJumpParams.grantDelay` 0.108、`vzAdd` 201.81、`vzFloor` 409.25、`vzBranch` 358.7、`horizontalStep` 240、`restartsLurchWindow`、`sameCommandKeyAsHeld`、`clearOnZipline`、`UpCeiling` 1250；
   - `StimParams.onsetDelay` 0.16、`extraScale` 2、`fadeDuration` 0.5、`sprintspeed` 282、`sprintAcceleration` 120、`modDuration` 6.0；
   - `LandingSlowdownParams.a` / `b` / `duration` / `exponent`（第 03 章也要）；
   - `SkillRules.maxUpSpeed` 1100、`maxHorizontalSpeed` 900、`maxSpeedBoost` 1.40（第 06 章）；
   - `KnockbackParams.mass` 100、`speedBoostLimit` 1000、`groundMinSpeed` 312.5、`lowDecelDurationScalar` 0.003、`lowDecelRamp` 0.5（全部在 PR #52，还没合并；导出名的前缀要等合并后由 hb-tables 定）；
   - `EpgBolt.Speed` / `Damage` / `Inner` / `Outer` / `Impulse` / `OwnerScale`（PR #52）；
   - `CombatSim.PlayerMass` 103（main，TF2X）。
4. **F-01** 的含义写"JUMP_PAD_PUSH_VELOCITY"，依据只有脚本；可以补 [实测] M4 15 次、M10 21 次。
5. **F-02** 含义"v = 1150·normalize(ĥ + 2ẑ)"——ĥ 是"运动方向，静止竖直向上"，建议在含义里写清（M10-C2）。
6. 单位类别：`lowDecelDurationScalar` 的类别是"每单位速度的量"（s/(u/s)，换米 ÷ 0.0254 → 0.1181 s/(m/s)），01 §2.1 有这一类，表里要按这一类换，不要按时间。

#### F. 本部分用的出处缩写（第一次出现时进本章"本章出处缩写"表）

| 缩写 | 文件 | 在哪 |
|---|---|---|
| NP2 | `research/rea-native/subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md` | main |
| NT | `research/rea-native/subsystems/N2-T-TIMING-INPUT.md` | main |
| N4A | `research/rea-native/n4/N4A-READBACK.md` | main |
| NR | `research/rea-native/N-REPORT.md` | main |
| OCT | `research/phase2-local/m4/octane/OCTANE-PRIMITIVES.md` | main |
| M4b | `research/phase2-local/m4b/pad_rejump/PAD-REJUMP.md` | main |
| PAD-DJ | `research/phase2-local/m8/r_pad_djump/PAD-DJUMP.md` | main |
| OCT-M10 | `research/phase2-local/m10/r_octane/OCTANE-M10.md` | main |
| M10C-U | `research/phase2-local/m10/unity/M10C-UNITY.md` | main |
| FEEL | `research/feel/FEEL.md` | main |
| EPG | `research/epg/EPG-ROCKET-JUMP.md` | main |
| RJ | `research/epg/ROCKET-JUMP-A-SPEC.md` | PR #85，还没合并；分支 `rj/knockback-a` |
| TF2-EPG | `tf2/epg/T1-T7-REPORT.md` | main |
| DP | `research/DESIGN-PHILOSOPHY.md` | main |
| DEC | `DECISIONS.md`（D-10、D-13、D-19、D-43、D-68 在 main；D-77 在 PR #85） | main / #85 |
| DIFF | `R5-DIFF-ARCHIVE.md`（RJA 节在 PR #85） | main / #85 |
| U: | HSD-Unity；`U:…/` = `Assets/HSD/R5Replay/Runtime/` | main `17260f2`；击退在 HSD-Unity PR #52（`rj/knockback-a` `6f7ea2d`） |

### 传送和其他技能（§5.40 – §5.54）
#### 1. 缺口（建议进 99-TODO-RESEARCH；都没测过）

| # | 缺口 | 现在怎么写的 | 怎么补 |
|---|---|---|---|
| B05-5 | Wraith 门"离开后 1.0 s 不能再进"没实测；PR2 只知道"走出 0.5 s 再走回来能进"，总间隔没细分。Unity 也**没有行为测试**，只有 `N8ETeleportTests.TheRiftTakesTheBodyAgainOnlyOneSecondAfterAnExit` 检查参数值（Breach 同理） | 写成 [数据]（脚本）+ "没实测" | R5：出门后按 0.6 / 0.9 / 1.1 / 1.4 s 回到门里各 5 次；Unity：加一条 0.99 s 不进 / 1.01 s 进的测试 |
| W-a | 站姿传送门的触发大小没读到（HSD 32 / 72 u 是设计值，R5 只知道蹲姿 16 / 32） | [设计] | 读脚本里站姿触发区，或 R5 侧向走近测最近距离 |
| W-b | Ash 突破"相位中不能发动" Unity 没做（没有预设同时有虚空和突破） | 两边都写了 | 组合预设出现时再加 |
| W-c | 突破出口后输入马上有效只是推断（出口没加输入） | 写成"没加输入测过" | 出口后按 W 5 次 |
| W-d | Alter 战术、Alter 大招：本地测不了（SDK 放置 / 需要第二个玩家）；规则全来自脚本 | 只在 5.45 列规则 | 有机器人队友或新构建时 |
| W-e | 跑动中反向的 R5 刹车曲线（D4 §7）；而且按代码读，D4 修的函数在 Reference / Fun 里已被原生 WalkMove 盖过，没单独确认 | 5.46 两边都写 | R5：冲刺 → S、冲刺 → 180° 快转各 5 次；交 hb-ch03 |
| A-a | 喷气回充从落地还是从停喷算分不清；空中回充没测 | 写成 [设计]（选落地） | 停喷后在不同时间落地 |
| A-b | 突袭空中发射没测到（拔出 0.9 s 比站立跳滞空长）；台沿外向下发射 Unity 没做 | 写了 | — |
| A-c | Revenant 长攀爬的结束规则 n = 2（止损：地图上没有够高的光滑墙） | 写成 [实测] [设计] | 需要自建几何 |
| A-d | Vantage 末端跳窗口 115 u 还是 180 u | 写成 [推断] 180 | 115–180 u 之间密集按 |
| A-e | 升梯短停留（< 0.5 s）只有 10 次拟合 | [实测] 拟合 | — |
| A-f | 虚空淡出的小肩（1.094 约 0.07 s）没建模 | 写了 | — |

#### 2. 过时 / 矛盾的文档

1. **`U:…/Abilities/DimensionalRift/README.md` 参数表 `reuseDebounce` 写 0.5 s**，代码是 1.0（D-19 E-2）；`DimensionalRiftAbility` 类注释也还写"0.5 s debounce"。建议改 README 和注释（不改行为）。
2. **P3 "Wraith Portal / Ash Phase Breach"** 写"出口 `SetVelocity(node.velocity)`、固定出口速度 + 锁操作"——被 PR2（24 次）和 M6B（31 次）的"出口速度 0"推翻。P3 是 M4 的源码阅读，没实测。
3. **WR** 写"回放速度 = 放置速度（364）"——PR2 更正：那是速度字段，不是实际运动（实际平均 1160–1250 u/s）。
4. **N8B §1** 写虚空"按下 → 0.8 s 准备"，实测是 0.367 s 后开始的 0.8 s 减速、1.175 s 进相位。两者对得上（`deploy_time` 从收武器后算，[推断]），整合时用实测时间表。
5. **`U:…/Abilities/IntoTheVoid/README.md`** 把 `phaseDuration` 4.0 s 标成 [wiki S21]；N8B 有脚本 `charge_time` 4（[数据]），N8D 实测 3.9–4.0 s。可以升级标签。
6. **同一个隧道引擎，两种拟合**：Rift 用 floor(clamp/0.1)·0.1 + 0.2 s，Breach 用 0.152 + 0.1017·round(clamp/0.1) s。N8B §0 的脚本规则是"0.1 s 一步、最后多一步、相位 = 0.1 × (步数 + 1)"。两个都和各自的实测对得上（Rift 481.6 u：round 给 0.7 s，实测 0.6 s，所以 Rift 只能用 floor；Breach 的脚本明写 round）。没查清为什么不同（可能是 Rift 的路径整理按路径点数而不是时长取整）。两边都写了，建议进 99-TODO。
7. **`U:…/Abilities/Pounce/README.md` "已知差异"** 第一条"突袭网格只测了俯仰 0、c ≤ 0.31"过时：同一 README 开头和 REV9 都写了 M9-B 全网格 215 次。
8. **`U:…/Abilities/GravityLift/README.md` "已知差异"** 写 `reentryBlock` 是"未测的 [src] 值"：N9 已改成 [反编译]，LIFT8 实测 2.02–2.19 s 时被再抬（和 2.0 s 一致，没试 < 2 s）。
9. **P3 "Vantage"** 写 dedi 的 Echo 位移是 SDK 重写的 `jetdrive.cpp`、"不是 S21 原版"；VAN9 写"位移本身是原生 `BeginJetDrive`"。本地是 S3 dedi + SDK，两句说的可能是不同的端（客户端原生 / 服务端 SDK），没核对。手册按 VAN9 / VAN8 的实测写。
10. **`U:…/Abilities/Teleport/README.md`** 的测试列表只写了 `M10WGameTests`、`MovementDemoTests`；直接测这个原语的是 `SkillComboTests.PortalExitLocksControlsRefusesOtherSlotsAndCancelsPendingStates` 和 `N8ETeleportTests.TheOldPortalPrimitiveIsLabelledAsADesignValue`。
11. **名字撞车**（不是错误，但容易读错）：Unity 电机的 `CommandModifiers.phased` / `R5MotorV2.phased` = 运动学旅行不做世界扫掠（穿过实体）；R5 的"相位"= 不和别的东西互动、世界碰撞不变。5.40 写了一句。建议 06 / 02 章引用时也注明。
12. **`JetpackParams.R5Reference()` 是 M4 模型**，不是 Reference 配置用的（那是 `Measured()`）。参数表导出时如果按 `R5Reference()` 取值会拿到 M4 的数（没有起喷消耗、不回充）。
13. `RiftM10WTests.StandingOnTheArrivalPortalSendsNobodyBackAndSteppingOutAndInTravelsAgain` 的注释"a walk straight back against the motion is the motor's anti-parallel case"写于 D4 修复之前，现在 Reference 走原生 WalkMove，这句可能过时（没跑确认）。

#### 3. 参数名和 params.tsv 对不上的

params.tsv（`origin/handbook/tables`）里本节能对上的只有 F-04 – F-07（升梯 `defaults.GravityLiftParams.upSpeed` / `ejectUp` / `ejectHorizontal` / `lifetime`）、F-08 / F-09（兴奋剂）、J-09 / J-10 的 Horizon 备注。下面这些**表里没有行**，建议 hb-tables 加（名字按表里 `defaults.<Params类>.<字段>` 的写法猜的，以导出为准）：

| 建议的行 | Unity 字段 | 值 [u] |
|---|---|---|
| 传送门旅行速度 / 最短 / 最长 / 长路径最长 | `defaults.RiftParams.travelSpeed` / `minTravelTime` / `maxTravelTime` / `longPathMaxTravelTime` | 1024 u/s / 0.3 / 2.0 / 3.5 s |
| 传送门最短门距 / 最长路径 / 寿命 / 再进 | `defaults.RiftParams.minGap` / `maxDistance` / `lifetime` / `reuseDebounce` | 128 u / 6000 u / 45 s / 1.0 s |
| 传送门放置加速 | `defaults.RiftParams.baseSeverity` / `stepSeverity` / `stepPercent` / `maxSeverity` | 0.2 / 0.1 / 20 % / 0.5 |
| 传送门触发（设计） | `defaults.RiftParams.portalRadius` / `portalHeight` | 32 / 72 u（R5 蹲姿 16 / 32） |
| 虚空 | `defaults.VoidS21Params.deployDelay` / `phaseStart` / `phaseDuration` / `severity` / `boostHold` / `fadeDuration` | 0.367 / 1.175 / 4.0 s / 0.3 / 2.8 / 1.192 s |
| speed_boost | `SpeedBoost.ExtraScale` / `LockedScale` / `HandScale`（常量） | 2 / 1.0 / 1.15 |
| 突破 | `defaults.PhaseBreachParams.travelSpeed` / `maxDistance` / `minDistance` / `exitFraction` / `exitHeight` / `lockBase` / `lockPerFrame` / `portalLifetime` / `reentryDebounce` | 1200 u/s / 2953 / 200 u / 0.918 / 5 u / 0.152 / 0.1017 s / 15 / 1.0 s |
| 旧传送原语（设计） | `defaults.TeleportParams.distance` / `exitSpeed` / `lockDuration` / `delay` | 400 u / 300 u/s / 0.3 / 0.25 s |
| 喷气 | `JetpackParams.Measured().*`（**不是** `R5Reference()`）：`thrust`、`tightUp`、`strafe`、`vzScaleOnStop`、`postGravityScale`、`postMaxTime`、`activationCost`、`rechargeRate`、`rechargeDelay` | 见 5.49 表 |
| 突袭 | `defaults.PounceParams.vMin` / `vMax` / `pullout` / `chargeTime` / `pitchRaise`；`RevenantParams.pounceWallRunLock` | 700 / 1150 u/s / 0.9 / 1.3 s / 35° / 0.85 s |
| Revenant 攀爬 | `ClimbProfile.speedLineK` / `speedLineZ0` / `endHeight` | 0.0921 /s / 2493 u / 1246.6 u |
| Vantage | `VantageParams.Measured().echoRange` / `launchSpeed` / `pathSpeed` / `brakeDistance` / `brakeDecel` / `endJumpForward` / `endJumpUp` | 1968.5 u / 943.1 / 787 u/s / 180 u / 1047.6 u/s² / 512 / 394 u/s |
| Horizon | `LegendAirProfile.Horizon().airSpeed` / `airAcceleration` / `landSlowdownDuration` | 80 u/s / 800 u/s² / 0 s |
| 飞行、重力切换（设计） | `FlightParams.*`、`GravitySwitchParams.levels` | 见 5.53、5.54 |

另外：F-07 `lifetime` 10 s 一致，但语义不同——R5 到期移除升梯；Unity 只在没人乘坐时移除，不弹出乘客（README 已知差异），建议在"和 R5 一致吗"列注明。

#### 4. 建议的决定（D-??，由 hb-integrate 编号）

- 无必须的新决定。可选：是否统一 Rift / Breach 的旅行时长取整（见第 2 节第 6 条）；是否给 Rift / Breach 加"离开 1.0 s"的行为测试（不改行为）。

#### 5. 出处缩写表

见本草稿开头"本节出处缩写"。补充沿用的：DIFF = `R5-DIFF-ARCHIVE.md`（本节没有专门的 DIFF 条目：传送门、虚空、突破在 R5-DIFF 里都没有单列，D-19 的旧值只在 DECISIONS 的留档行）；DEC = `DECISIONS.md`。
