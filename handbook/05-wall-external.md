# 05 跑墙、挂墙、二段跳、蹬墙跳；借外力的移动

由 hb-ch05 写（2026-11-14）。分支 `handbook/ch05`，还没合并。备注、待研究、建议的 D 行在 [_notes/hb-ch05.md](_notes/hb-ch05.md)；附件在 [05-wall-external/](05-wall-external/)（`pad-probe/`：查清关卡尺度表 LS-24 的程序，§5.33）。

引用的文件都在研究仓库 main（`86ec5f1`）和 HSD-Unity main（`17260f2`）上，例外：击退规格（研究 PR #85，HSD-Unity PR #52，都还没合并）、墙跳排斥是死代码（研究 PR #115，还没合并）、关卡尺度表和第 03 / 04 / 07 章（各自的 `handbook/*` 分支，还没合并）。

## 白话说明

这一章管两类动作：

1. **墙上的动作和空中再跳一次**（§5.1 – §5.14）：跑墙（贴着墙跑一段）、跑墙中蹬墙跳出去、R5 攀爬中按跳的"蹬墙跳"、二段跳、挂墙 / 抓边。R5（Apex S21）**没有**跑墙和通用二段跳——setfile 里 `wallrun = false`，二段跳只有 Octane 跳板那一种——所以这一部分的规则来自 **Titanfall 2 的实测和反编译**，加上 HSD 自己的设计（M7）。
2. **借外力的移动**（§5.15 以后）：滑索和滑索枪（第二部分 §5.15 – §5.24）、钩爪（第三部分 §5.25 – §5.31）、跳板（第四部分 §5.32 – §5.36，含兴奋剂）、爆炸击退和火箭跳（第五部分 §5.37 – §5.39）、传送和相位（第六部分 §5.40 – §5.46）、别的技能带来的移动（第七部分 §5.47 – §5.54：Horizon、Valkyrie、Revenant、Vantage 和两个 HSD 设计）。这些 R5 都有（最后两个除外），规则按 R5 原生代码和实测写。

一句话记住外力部分：**跳板和传送是"替换"速度（传送出来是 0），击退是"相加"，滑索和钩爪是"驱动"（挂上以后由它们决定速度，下来时按明确的规则交还）**。

和别的章的分界：

- 每条命令的执行顺序、碰撞体、地面检测、半步重力在第 02 章；普通起跳、空中加速、lurch（起跳后改方向）的规则在第 03 章。本章只写"哪些动作算一次起跳、会打开 lurch 窗口"（§5.14 的总表）。
- 攀爬（台沿够不着时贴墙往上爬）和翻越在第 04 章；本章接着写**攀爬中按跳**（R5 的蹬墙跳，§5.8）。
- 动量规则（谁能加速、上限多少）、同一条命令上多个动作谁赢（跳键被谁用掉）在第 06 章。本章只写本章需要的那一小块，并指过去。
- 镜头（跑墙倾斜 `wallrun_tilt`、二段跳 punch `double_jump`、下滑索 kick `zip_detach`、钩爪 / 滑索横滚 `rope_roll`）在第 07 章。
- 技能的设计结构（冷却、充能、UI）在第 10 章。

**读完能做出什么**：没看过研究档案的工程师，照本章加第 02、03 章，能做出三套规则中任何一套的跑墙（含蹬墙跳、同墙限制）、两种二段跳、R5 的攀爬蹬墙跳；照 §5.15 以后能做出和 R5 一致的滑索、钩爪、跳板和击退。

**先写清楚：跑墙有三套规则，默认是哪套**

| 规则 | 是什么 | 数值从哪来 | 在哪用 | 开关 |
|---|---|---|---|---|
| **M7 设计**（§5.7） | HSD 自己设计的 Titanfall 式跑墙：低重力、几乎水平的一条线 | 全部 [设计] | **游戏默认**（Fun 配置）。Reference 配置关 | `WallRunParams.rules = M7Design`；游戏内 `7` 键开关跑墙 |
| **TF2 规则 + R5 残留值（预设 B）**（§5.2 – §5.6） | TF2 的规则，数值换成 R5 setfile 里残留的跑墙键（Apex 版跑墙"如果开着会是什么样"） | [TF2 反编译] [TF2 实测] 的规则 + [数据] R5 setfile | 基准（D-57）；**默认关**（D-58） | `rules = Tf2`，`tf2 = Tf2WallRunParams.B()`；Esc 菜单 "Wall-run rules (P-01)" = 1 |
| **TF2 规则 + TF2 值（预设 A）**（§5.2 – §5.6） | TF2 原版多人模式 | [TF2 数据] [TF2 实测] | 可切换的对照；默认关 | `tf2 = Tf2WallRunParams.A()`；同一菜单 = 2 |

二段跳同样有两套：**HSD 设计**（§5.10，默认）和 **TF2 规则**（§5.9，P-02，默认关）。

关卡尺度（hb-tables 实跑，`tables/level-scale.md`）：同样的接近方式，M7 跑 549.84 u（LS-18），B 535.67 u（LS-19），A 701.03 u（LS-20）；二段跳总高 HSD 99.794 u（LS-21），TF2 规则 114.8 u（LS-22）。

**两件事等用户定**（00-INVENTORY 05 章第 2、3 条）：墙跳后的"排斥"（§5.6，M-2）和快速上升时的二段跳（§5.9，M-1）。两边都写在对应条目里，没有选。写本章时还查出几处 HSD 和 R5 不一样、要用户看的地方（竖直滑索往下看能不能挂、HSD 的 1100 u/s 向上天花板削掉竖直跳板发射、跳板冷却按能力而不是按玩家等），清单在 `_notes/hb-ch05.md` §7。

**本章出处缩写**（第一部分用；外力各部分开头另有自己的表）

| 缩写 | 文件 |
|---|---|
| TMS | `tf2/TF2-MOVEMENT-SUMMARY.md`（TF2 铁驭移动汇总，10-28） |
| T3 | `tf2/wallrun/T3-REPORT.md`（TF2 跑墙 / 挂墙 / 二段跳静态，和 M7 对照） |
| BSPEC | `tf2/wallrun/WALLRUN-B-SPEC.md`（B / A 两套的实现规格） |
| R1 | `tf2/wallrun/R1-R5-WALLRUN-KEYS.md`（R5 里 Apex 新加的跑墙键） |
| D12 | `tf2/wallrun/D1-D2-REPORT.md`（系数 f、参考高度 refZ） |
| T5 | `tf2/runtime/T5-REPORT.md`（TF2 运行时实测；§5 跑墙，§8 补测 BT-1 – BT-3） |
| GAPS | `tf2/runtime/GAPS-1108.md`（11-08 补测：A1 – A6 跑墙分支、B1 – B4 挂墙、C 窗户辅助） |
| PDIFF | `tf2/runtime/PRESET-DIFF-1109.md`（HSD `Tf2` 预设和 TF2 的三处差别 M-1 / M-2 / M-3，等用户定） |
| RNT | `tf2/ref-native-tail/REF-NATIVE-1112.md`（PR #115，还没合并；分支 `ref/native-tail`） |
| M7U | `research/phase2-local/m7/unity/M7A-UNITY.md`（M7-A 跑墙 / 抓边 / 二段跳） |
| M8AU / M8BU | `research/phase2-local/m8/unity/M8A-UNITY.md`（跳键仲裁）/ `M8B-UNITY.md`（墙链、共面修复） |
| WMM | `research/phase2-local/m3/wall_mantle/WALL-MANTLE-MODEL.md`（M3 蹬墙跳实测） |
| DEC | `DECISIONS.md` |
| DIFF | `R5-DIFF-ARCHIVE.md` |
| LS | `handbook/tables/level-scale.md`（分支 `handbook/tables`，还没合并） |
| U: | HSD-Unity 仓库；`U:…/` = `Assets/HSD/R5Replay/Runtime/`；测试在 `Assets/HSD/R5Replay/Tests/Editor/` |

外力部分（§5.15 以后）用到的缩写在各部分开头列。

---

## 5.0 记号和前提

- **命令**：一条 usercmd，Unity 里固定 1/120 s（第 02 章）。规则都按 dt 写。
- **墙法线 n̂**：墙面朝外的法线，只取水平分量再归一化。"朝墙" = 速度或输入和 −n̂ 同向。
- **沿墙分量** a(v) = v_h − (v_h·n̂) n̂（水平）；**离墙分量** v·n̂。
- **msc**：移动倍率（武器决定；空手 1.15，第 03 章）。表里乘了 msc 的会注明。
- **重力 g**：R5 和 HSD 都是 `sv_gravity` 750 u/s² × `gravityScale` 1 = 750 u/s²。TF2 起跳用 750、下落用 750 × 0.8 = 600 u/s²（TMS §4.1）。**HSD 的 TF2 预设一律用 HSD 的重力 750**，所以"TF2 规则"跑出来的高度和 TF2 本体不同（LS-22 的说明）。
- **按下 / 按住**：同第 04 章。
- 参考身高 H = 72 u（[01 §4.1](01-units-body.md)）。

---

## 第一部分 · 墙上的动作和二段跳（§5.1 – §5.14）

本部分的规则来自 TF2（跑墙、TF2 二段跳、挂墙、窗户辅助）、R5（攀爬蹬墙跳）和 HSD 设计（M7 跑墙、HSD 二段跳、抓边）。每一项标题写明是哪一套。

### 5.1 跑墙是什么：三套规则的共同骨架

#### 原理

跑墙让玩家把水平速度"借"给一面墙：贴上墙以后不往下掉（或掉得很慢），沿墙继续跑一段，再蹬墙跳出去接下一面墙。设计上它是**空中路线的延长**，不是加速器：三套规则都不让跑墙本身把速度刷到冲刺以上很多（P3"动量是玩家的资产，只有明确规则才能收走 / 给予"）。

TF2 的实现有一个关键想法：**跑墙不是一种单独的移动模式，而是把墙当成"地面"**，走的是地面移动那一套（加速、减速 / 摩擦），只是换成跑墙那一组参数；重力在外面每帧另算，从 0 慢慢爬到满（TMS §0、§6）。这样跑墙的手感是一条"先平、后坠"的弧线。

M7 是 HSD 另一种设计：恒定 0.15 倍重力，是一条几乎水平的线（T3 §4"最大的手感差别"）。

#### 规则和公式

三套共用的骨架（细节在 §5.2 – §5.7）：

1. **只在空中起跑**；不在滑索、梯子上，没有别的"驱动"动作在跑（钩爪拉、喷气、翻越，第 06 章）。
2. 每条命令判断能不能起跑；起跑后每条命令先判断"结束"，再走跑墙移动。
3. 跑墙中按跳 = **蹬墙跳**（跳键归跑墙，第 06 章"状态拥有者"一层），按跳那一条命令就离墙。
4. 起跑恢复二段跳次数（三套都是）。
5. 着地、墙没了、时间到都结束。
6. 同一面墙不能马上再跑（规则各不同，§5.6、§5.7）。

| 量 | M7 设计 | B（TF2 规则 + R5 值） | A（TF2 规则 + TF2 值） |
|---|---|---|---|
| 起跑要不要按前进 | 要 | 不要 | 不要 |
| 起跑速度下限 | 沿墙 200 u/s | 无 | 无 |
| 重力 | 恒定 × 0.15 | 从 0 线性爬到 1，用 1.0 s | 同 B，用 0.7 s |
| 水平速度目标 | 300 × msc | 225 × msc | 420 × msc（摩擦下实际约 375） |
| 最长时间 | 1.6 s | 2.0 s | 1.75 s |
| 蹬墙跳 | n̂·280 + 沿墙保留，vz 300，水平 ≤ 480 | 离墙 ≥ 188，输入 75，vz = min(240, vz + 360) | 离墙 ≥ 205，输入 80，vz = min(230, vz + 345) |
| 同一面墙 | 落地前不能再跑 | 只能在上次起跑点以下再贴 | 同 B |

#### 实现模板

```
// 单位：u、s。每条命令，在电机的移动之前（BeforeMove）
if running:
    if jumpPressed: wallJump(); return            // §5.5 / §5.7
    if endCondition(): end(why); return            // §5.4 / §5.7
    wallRunMove()                                  // §5.3 / §5.7：改重力倍率、改速度
else if airborne and canStart():                   // §5.2 / §5.7
    start()
    wallRunMove()
// 然后电机照常走空中那一步（重力用改过的倍率）；TF2 规则下这一步的空中加速关掉
```

Unity 参考实现：`U:…/Abilities/WallRun/WallRunAbility.cs`，`WallRunAbility`（`BeforeMove` = M7，`Tf2BeforeMove` = TF2 规则）、参数 `WallRunParams`（M7 的值 + `rules` + `tf2`）、`Tf2WallRunParams.B()` / `A()`、枚举 `WallRunRules`。跑墙是"Effect"型能力（不是驱动者）：它只改速度和重力倍率，位置照常由电机按碰撞走（第 06 章）。配置：`MovementConfig.hsd.wallRun`（`HsdMovementParams.Off()` 在 Reference，`.Fun()` 在 Fun）。所有字段都是 [u]。

#### 验收

- `Tf2WallRunTests.DefaultsStayM7AndThePresetsCarryTheSpecValues`：默认 M7；B / A 两套的数和规格一致。
- `WallRunTests.ReferenceHasNoneOfTheThreeAndTheTogglesAddThem`：Reference 没有跑墙、抓边、二段跳。
- 关卡尺度 LS-18 / 19 / 20：同一套 24 种接近方式取最长，549.84 / 535.67 / 701.03 u。合格线：改动以后这三个数不变（差 < 1 u），除非改动就是要改它们。

#### 出处

- TMS §0、§6：跑墙是地面移动的一个分支。main
- T3 §4：M7 和 TF2 逐项对照；§5：三个选项。main
- DEC D-08（跑墙 / 抓边 / 二段跳是 HSD 设计，Reference 关 Fun 开）、D-57（B 为基准，A 可切换，M7 保留）、D-58（P-01 / P-02 / P-05 默认关）。main
- LS-18 – LS-22（分支 `handbook/tables`，还没合并）。

---

### 5.2 跑墙起跑（TF2 规则）

#### 原理

TF2 的起跑很宽松：**不用按键、没有速度下限**，只要在空中朝着一面够竖的墙移动、脚离墙够近，就贴上去了。贴上去那一下会被往上"托"一把（起跑提速），这一托让跑墙有一个起始的上升，配合后面慢慢变大的重力，形成先升后降的弧线。

但这一托和后面的低重力**只给"跳上来"的人**：从台边走下去、或者被传送到空中再贴墙，就没有提速，重力从第一帧就是满的。这是为了让跑墙只奖励主动的跳跃，不让玩家靠"掉下去蹭墙"免费拿到高度。R5 在这上面又加了一道高度门：离"起跳的地面"太高的地方不能再获得提速和低重力，跑墙链不能无限往上爬。

#### 规则和公式

**要维护的状态**（每个玩家）：

| 状态 | 规则 |
|---|---|
| `boostArmed` | 着地 → false；地面起跳 → true；蹬墙跳 → true；**同一面墙再贴时**，算完这次起跑提速以后 → false |
| `refZ`（参考高度） | 站在能站的地面上（法线 z ≥ 0.7）且不在跑墙中：每条命令 = 脚底 z。腾空后只降不升（z < refZ 时跟着降）。被跳板 / 重力炮发射时 = 弹道最高点 z + v_z² / (2g) |
| 系数 **f** | f = 1 当且仅当 `boostArmed` 且（cutoff < 0 或 z − refZ < cutoff）；否则 0。**每条命令重新算**。cutoff = `heightCutoff`（B 175 u，A 关） |
| 上一面墙 | 法线、起跑那一刻的高度（同墙判断用，§5.6） |

**起跑条件**（全部满足）：

1. 在空中；不在滑索 / 梯子上；没有驱动者在跑。
2. 墙面法线 z ∈ [`minNormalZ`, `maxNormalZ`]（B [−0.5, 0.7]，A [−0.35, 0.7]）：太平的不是墙，太倒扣的天花板不行。B 的下限来自 R5 的 `wallrunCeilingLimit` 0.5。
3. **朝墙移动**：v·n̂ ≤ 0（`wallrun_minAngle_air` 180°，半角 90°）。
4. 脚离墙 ≤ 贴墙距离（B 17 u，A 13 u）。
5. **起跑高度门**（只有 B）：起跑点 z ≤ refZ + cutoff − `startHeightOffset`（175 − 28 = 147 u）。滑铲超级跳起跳的那次腾空，cutoff 再 + 200（R5 `slideSuperJumpAdditionalVerticalGainCutoff`，Unity 没做）。
6. 同一面墙、排斥、0.5 s 计时：§5.6。
7. 不需要按键，没有速度下限。
8. 撞墙但判失败后，每 0.07 s 再判一次（`wallrun_retry_interval`；Unity 每条命令都判）。

**起跑那一刻**：

1. 起跑提速：设 u = 竖直速度（墙是竖的时就是 v_z），B = `upWallBoost` × f。如果 u < B：u ← u + B − max(u, 0)。即"向上慢的补到 250，下坠中的加 250"，**不是**直接设成 250。
2. 恢复二段跳次数（`superjump_limitreset_onwallrun`）。
3. 跑墙次数 +1（只用于强度衰减，阈值 1000 次，实际不起作用，不实现）。
4. 记下这面墙的法线和起跑高度；如果是同一面墙再贴（§5.6），`boostArmed` ← false（这次跑墙有提速、没有重力爬升）。
5. 跑墙计时 t 从这一刻开始。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起跑提速 `upWallBoost`（B = A） | 6.35 m/s | 250 u/s | 3.472 H/s | 实测 +246 – +248（扣一帧重力） | [TF2 实测] T5 §5.1；[数据] R5 setfile `wallrunUpWallBoost` |
| 高度门 `heightCutoff`（B） | 4.445 m | 175 u | 2.431 H | A 关（TF2 没有这个键） | [数据] R5 `verticalGainCutoff_wallrun`；[反编译] D12 |
| 起跑高度偏移 `startHeightOffset`（B） | 0.7112 m | 28 u | 0.3889 H | — | [数据] R5 `climbFinalJumpUpHeight` |
| 起跑最高点（B，refZ 之上） | 3.734 m | 147 u | 2.042 H | 和第 04 章攀爬终点 147.06 u 是同一个数 | [算] 175 − 28 |
| 墙面法线 z 下限 `minNormalZ` | — | B −0.5 / A −0.35（×） | — | — | [数据] R5 `wallrunCeilingLimit`；[TF2 反编译] |
| 墙面法线 z 上限 `maxNormalZ` | — | 0.7（×） | — | — | [TF2 反编译] |
| 贴墙距离 | 0.4318 / 0.3302 m | B 17 / A 13 u | 0.2361 / 0.1806 H | — | [数据] R5 setfile / TF2 `wallrun_allowed_wall_dist` |
| 重试间隔 `wallrun_retry_interval` | — | 0.07 s | — | — | [TF2 反编译] |

#### 实现模板

```
// 单位：u、s。每条命令结束（AfterMove）更新状态
if jumpedThisCommand:  boostArmed = true          // 地面起跳
else if grounded:      boostArmed = false
if grounded and not running and groundNormal.z >= 0.7:  refZ = z
else if z < refZ:      refZ = z
// 跳板 / 重力炮发射时另写 refZ = z + vz²/(2g)（Unity 没做，见 _notes）

f() = (boostArmed and (cutoff < 0 or z - refZ < cutoff)) ? 1 : 0

canStart(n):                                     // n = 墙的水平外法线
    airborne, no driver, contact within reach, minNormalZ <= wall.n.z <= maxNormalZ
    dot(v, n) <= 0                                // 朝墙
    cutoff < 0 or z <= refZ + cutoff - 28
    not sameWallBlocked(n, z)                     // §5.6
start(n):
    B = upWallBoost * f()
    if v.z < B: v.z += B - max(v.z, 0)
    if sameWall: boostArmed = false
    airJumpsUsed = 0
    lastWallNormal = n; lastStartZ = z; startTime = now
```

Unity：`WallRunAbility.Tf2BeforeMove`（起跑段）、`WallRunAbility.AfterMove`（`boostArmed`、`refZ`）、`WallRunAbility.Strength`（f）。和规则的差别（都写进 `_notes`）：

- 贴墙距离不是按 17 / 13 u 量的，是用碰撞层报告的接触（`AbilityContext.Contact`，0.1 s 内的接触算数，`WallRunParams.contactGrace`）。
- 没有 0.07 s 重试间隔、没有滑铲超级跳的 +200、跳板发射时不改写 refZ。
- **HSD 加了一条**：视线朝墙 35° 以内（`WallRunParams.climbCone`）不起跑，那面墙归 R5 的攀爬（第 04 章）。这是 [设计]，TF2 没有（TF2 没有 Apex 的攀爬）。
- 有未用掉的跳键按下的那条命令不起跑（M8-A，跳键这条命令归蹬墙跳 §5.8 或二段跳，第 06 章）。
- Revenant 的扑击锁（`WallRunLock.Active`）期间不起跑。

#### 验收

- `Tf2WallRunTests.AJumpedStartGetsTheBoostToAbout250`：跳起后起跑，vz 补到 250（允许扣一条命令的重力，235 – 250.01）。
- `Tf2WallRunTests.AFallingJumpedStartGetsPlus250NotTo250`：下坠中起跑，+250（238 – 258）。
- `Tf2WallRunTests.AStartWithoutAJumpHasNoBoostAndFullGravity`：没跳过的起跑，vz 不变、重力系数 1、`boostArmed` = false；跳过的起跑重力系数从约 0 开始。
- `Tf2WallRunTests.PresetBBlocksAStartFarAboveTheTakeoffHeight`：B 不在 refZ + 147 以上起跑，A 可以。
- 对照数据：T5 §5.1（`gk_010` 175.7 → 250.0、`gk_060` −114.1 → 133.9、传送起跑不变）；GAPS A1（走下边缘再贴墙：没有提速、满重力）；T5 §8 BT-2（TF2 远高于起跳点照常提速——证明高度门只在 R5）。
- 合格线：提速后 vz 和 min(250, vz + 250) 差 ≤ 一条命令的重力 g·dt（6.25 u/s）。

#### 出处

- BSPEC §1 – §3：状态、起跑条件、起跑那一刻（B / A 两列）。main
- T3 §2.1：TF2 起跑条件。main
- R1：`verticalGainCutoff_wallrun`、`wallrunCeilingLimit` 的读法；起跑提速公式在 R5 和 TF2 一样。main
- D12 §1 – §2：f 只有 0 / 1；disable 标志的写入点；refZ 的定义。main
- T5 §5.1、§8；GAPS A1、A2。main
- 本地对照：`L:TF2-Research/wallrun/` 的反编译原文（不在 git）。
- [TF2 反编译] `CanWallRun` 0x180174890、`WallRun_Begin` 0x1801835c0（server.dll）。[反编译] R5 `WallRun_TryStart` 0x140a4e220、`WallRun_Begin` 0x140a4f120、f 0x140a4fed0、disable 标志 player+0x2ad8、refZ player+0x2078（r5apex_dx12.exe）。

---

### 5.3 跑墙中（TF2 规则）：重力、加速、减速、滑落

#### 原理

跑墙中的手感由三件事决定：

1. **重力从 0 慢慢变满**：刚贴上墙几乎不往下掉，越跑越沉，最后和空中一样。玩家感觉到的是"墙在托着我，但托不了多久"。
2. **沿墙方向像在地上跑**：按前进朝一个上限加速，不按就减速（B）或被摩擦拖慢（A）。往回看、往回按时上限只有 50，不能在墙上掉头跑。
3. **按前进会往上爬一点**：前进键额外给一份"向上"的输入，能抵消一部分重力；跑到 1.5 s 以后开始"滑落"，向上的力越来越弱。

B 和 A 的区别主要在第 2 条：B（R5 的残留值）慢、没有摩擦、用线性减速；A（TF2 原版）快、用指数摩擦。

#### 规则和公式

t = 这次跑墙已经跑了多久。

1. **重力系数** k_g = 1 − f·(1 − t / T)（t < T），t ≥ T 时 1。本条命令重力 = g × k_g。f 每条命令重新算（§5.2），所以跑到 refZ + 175 时 f 当场变 0、重力立刻变满，跑墙不再往上爬（B 的"爬升上限"）。
2. **滑落量** s = 0（t < 1.5 s），之后 s = min(1, (t − 1.5) / 1.0)；**没有移动输入时 s ≥ 0.7**。
3. **水平（沿墙）**：把移动输入投到墙面上得到方向 d̂。
   - 有输入：上限 c = `maxSpeedHorizontal` × msc；如果 d̂ 和视线朝后（d̂·视线 ≤ −0.6），c = 50 × msc。按地面加速的规则朝 c 加速：add = c − a·d̂，add > 0 时 a += d̂·min(add, `accelerateHorizontal` × msc × dt)。
   - 没有输入（只有 B）：|a| 每秒线性减 500，减到 0 为止。
4. **竖直**：按住前进时有一份"向上输入" = 前进量 × |视线的沿墙分量| × 0.65（`upwardAutoPush`）。有向上输入且 v_z < `maxSpeedVertical` 时，v_z 朝上限加速，加速度 `accelerateVertical` × (1 − s)。
5. **减速 / 摩擦**：
   - B（R5 没有 `wallrunFriction` 键）：竖直速度每秒线性减 300 趋向 0；下坠时这份减速再乘 (1 − k_g)(1 − s)。没有指数摩擦。
   - A：速度每秒 × (1 − 4·dt)（沿墙和竖直都乘）；下坠时竖直方向只乘 (1 − 4·(1 − s)·dt)，即滑落那部分不受摩擦。
6. 空中加速关掉（跑墙是地面型的移动）；离墙分量保留，另加一个很小的朝墙速度让碰撞每条命令都报告接触（Unity `WallRunParams.stick` 40 u/s，碰撞会吃掉它）。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力爬升时间 `gravityRampTime` | — | B 1.0 s / A 0.7 s | — | A 实测 g 从 41 爬到 598（t 0.03 → 0.71 s） | [数据] R5 `wallrunGravityRampUpTime`；[TF2 实测] T5 §5.1 |
| 水平上限 `maxSpeedHorizontal` × msc | 5.715 / 10.67 m/s | B 225 / A 420 u/s | 3.125 / 5.833 H/s | A 实测稳定在 375（加速 = 摩擦 4 × 375） | [数据] R5 setfile；[TF2 实测] T5 §5.2 |
| 水平加速 `accelerateHorizontal` × msc | 5.08 / 38.1 m/s² | B 200 / A 1500 u/s² | 2.778 / 20.83 H/s² | — | [数据] |
| 朝后的上限 `maxSpeedHorizontalBackward` | 1.27 m/s | 50 u/s | 0.6944 H/s | 实测 1.29 s 降到约 50 | [TF2 实测] |
| 朝后判定 `backDot` | — | −0.6（×） | — | — | [TF2 反编译] |
| 竖直上限 `maxSpeedVertical` | 2.845 / 5.715 m/s | B 112 / A 225 u/s | 1.556 / 3.125 H/s | — | [数据] |
| 竖直加速 `accelerateVertical` | 11.43 / 9.144 m/s² | B 450 / A 360 u/s² | 6.25 / 5 H/s² | A 实测反推约 360 | [数据]；[TF2 实测] |
| 向上输入比例 `upwardAutoPush` | — | 0.65（×） | — | — | [TF2 反编译] |
| 无输入水平减速 `decelerateHorizontal`（B） | 12.7 m/s² | 500 u/s² | 6.944 H/s² | A 无 | [数据] R5 `wallrunDecelerateHorizontal` |
| 竖直减速 `decelerateVertical`（B） | 7.62 m/s² | 300 u/s² | 4.167 H/s² | A 无 | [数据] R5 `wallrunDecelerateVertical` |
| 摩擦 `friction`（A） | — | 4 /s | — | 实测 4.08 | [TF2 数据] `wallrunFriction`；[TF2 实测] |
| 滑落开始 / 用时 / 无输入下限 | — | 1.5 s / 1.0 s / 0.7（×） | — | 实测 1.5 s 起明显下降 | [TF2 反编译]；[TF2 实测] |

#### 实现模板

```
// 单位：u、s。跑墙中每条命令（起跑那条也走）
t   = now - startTime
kg  = t < T ? 1 - f()*(1 - t/T) : 1
s   = t < 1.5 ? 0 : min(1, (t - 1.5)/1.0)
if no move input: s = max(s, 0.7)
gravityScale *= kg;  airAcceleration = 0
a  = alongWall(v, n);  vn = dot(v, n);  vz = v.z
d  = alongWall(wishDir, n)
if |d| > 0:
    d = normalize(d)
    c = (dot(d, viewFlat) <= -0.6 ? 50 : maxH) * msc
    add = c - dot(a, d);  if add > 0: a += d * min(add, accH*msc*dt)
else if decH > 0:  a *= max(0, |a| - decH*dt) / |a|
if friction > 0:                                  // 只有 A
    k = max(0, 1 - friction*dt);  a *= k
    vz *= (vz >= 0) ? k : max(0, 1 - friction*(1 - s)*dt)
if forward > 0 and vz < maxV:  vz = min(maxV, vz + accV*(1 - s)*dt)
if decV > 0:                                      // 只有 B
    dd = decV*dt*((vz < 0) ? (1 - kg)*(1 - s) : 1)
    vz = vz > 0 ? max(0, vz - dd) : min(0, vz + dd)
v = a + n*vn - n*stick + up*vz
// 电机接着按 g·kg 做半步重力和碰撞（第 02 章）
```

Unity：`WallRunAbility.Tf2BeforeMove`（"rt / gf / slip"之后那段）。和规则的差别（写进 `_notes`）：Unity 把"向上输入"只当开关（前进量 > 0 就按满的 `accelerateVertical` 加），没有按 前进量 × 沿墙分量 × 0.65 缩放加速；TF2 是怎么把这份输入折算成加速度的，资料只写到"朝上限加速"，没有写清。

#### 验收

- `Tf2WallRunTests.PresetAHorizontalSettlesNear375AndBNear225`：A 稳定在 1500 × msc / 4 的 0.92 – 1.04 倍；B = 225 × msc ± 1 u/s。
- `Tf2WallRunTests.AStartWithoutAJumpHasNoBoostAndFullGravity` 的后半：跑到一半时重力系数 = t / T（f = 1），差 ≤ 0.03。
- 对照数据：T5 §5.2（A：无输入 300 → 14 用 0.76 s；按前进水平 375、竖直收敛到 −58；无输入下坠只受 30 % 摩擦）。B 没有 TF2 或 R5 实测（R5 跑墙关着），只有规则。
- 合格线：A 的水平稳定速度 375 ± 4 %；重力系数和 1 − f(1 − t/T) 差 ≤ 0.03。

#### 出处

- BSPEC §4：跑墙中的每一条（B / A 两列）。main
- R1 "结论"表和第 1 条：R5 没有 `wallrunFriction`，B 用线性减速。main
- T3 §2.2；T5 §5.2。main
- [TF2 反编译] 地面 / 墙面移动 0x180185230、跑墙重力 0x180186c70。[反编译] R5 `WalkMove` 0x140a4a7c0 跑墙分支（NATIVE-MAP §3 把它错写成 `WallRun_Move`）、重力系数 0x140a34560。

---

### 5.4 跑墙结束（TF2 规则）

#### 原理

跑墙要有清楚的结束：时间到了就掉下来（这是跑墙"借"的上限），往外推就主动离开，墙没了就自然飞出去。R5 还加了一条"按蹲就下墙"，给玩家一个不跳也能离开的办法。

#### 规则和公式

按顺序判断，第一条成立的就结束（跳键在这之前，§5.5）：

1. 着地。
2. **墙没了**（这条命令没有接触）：沿法线推出 `fallAwaySpeed` 70 u/s。
3. **时间到**：t ≥ `timeLimit`（B 2.0 s，A 1.75 s）。TF2 被动 `pas_wall_runner` +2.5 s（HSD 没有这个被动）。
4. **按蹲**（只有 B，R5 `wallrunDuckCausesFallOff`）：按下蹲就离墙。
5. 别的驱动者开始（钩爪拉、滑索上绳、喷气，第 06 章）。
6. **朝外推**：移动输入朝墙外（输入·n̂ > 0.5）持续 ≥ 0.05 s。
7. **墙顶**（TF2 有，Unity 没做）：头顶上方没墙且在上升时，v_z 每秒减 3000·k，不让人冲出墙顶。
8. 墙面转折超过 cos⁻¹ 0.8（约 37°）也会脱落（TMS §6.4）。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 最长时间 `timeLimit` | — | B 2.0 s / A 1.75 s | — | A 实测 1.751 / 1.730 s | [数据] R5 setfile；[TF2 实测] T5 §5.2 |
| `pas_wall_runner` 加时 | — | +2.5 s（A 变 4.25 s） | — | 实测 3.2 s（到落地才停） | [TF2 数据] [TF2 实测] GAPS B4 |
| 朝外推的时间 `pushAwayFallOffTime` | — | 0.05 s | — | — | [TF2 反编译] |
| 墙没了的推出 `fallAwaySpeed` | 1.778 m/s | 70 u/s | 0.9722 H/s | — | [TF2 反编译] |
| 墙顶减速 | 76.2 m/s² | 3000 u/s²（× k） | 41.67 H/s² | k 没读 | [TF2 反编译] |
| 墙面转折脱落 | — | cos 0.8（约 37°） | — | — | [TF2 反编译] |

#### 实现模板

```
// 单位：u、s
why = grounded ? LAND
    : not contact ? NO_WALL
    : t >= timeLimit ? TIME
    : duckFallsOff and duckPressed ? DUCK
    : otherDriver ? DRIVER
    : pushAwayFor >= 0.05 ? PUSH_OFF : none
if why: end(why); if why == NO_WALL: v_h += n * 70
```

Unity：`WallRunAbility.Tf2BeforeMove`（`why` 一段）、`WallRunAbility.End`（发事件 `WALLRUN_END_<why>`，记下这面墙给 §5.6 用）。Unity 没做墙顶减速和墙面转折。

#### 验收

- `Tf2WallRunTests.ForwardHeldRunsToTheTimeLimit`：按住前进跑满 `timeLimit`（差 ≤ 3 条命令），结束原因 `TIME`。
- `Tf2WallRunTests.PresetBCrouchFallsOffAndAKeepsRunning`：B 按蹲 `DUCK`，A 继续跑。
- 合格线：时长和 `timeLimit` 差 ≤ 3·dt。

#### 出处

- BSPEC §5；T3 §2.3；TMS §6.4。main
- R1：`wallrunDuckCausesFallOff`。main
- GAPS B4（`pas_wall_runner`）。main
- [TF2 反编译] 脱落 0x180186d60。[反编译] R5 `WallClimb_Move` 0x140a4d4e0（按蹲脱墙）。

---

### 5.5 蹬墙跳（TF2 规则，跑墙中按跳）

#### 原理

跑墙的出口。蹬墙跳保证**一定能离开墙**（离墙速度补到至少一个值），**沿墙的速度原样保留**（不吃动量），再给一个向上的速度。按着方向键还能往按键方向多推一点。这样"墙 → 跳 → 对面墙"可以一路接下去，水平速度不涨也不掉。

蹬墙跳算一次起跳：它会让 `boostArmed` = true（下一面墙有提速和低重力），也会**打开 lurch 窗口**（跳完马上按方向键能转向，TF2 实测有，GAPS A5）。

#### 规则和公式

1. `boostArmed` ← true，再算 f（§5.2）。
2. 水平：v_h += 输入方向 × `jumpInputDirSpeed`；然后离墙分量 v·n̂ 补到至少 `jumpOutwardSpeed`（不够就沿 n̂ 加差值，够了不动）。原来的沿墙速度保留。
   - TF2 另有一条：视线和输入都朝墙时，`jumpOutwardSpeed` 最多减 80 %（T3 §2.4）。**Unity 没做**。
3. 竖直：J = `jumpUpSpeed` × f；v_z ← min(J, v_z + 1.5·J)。即正常情况下设成 J；快速下坠（v_z < −0.5·J）时是 v_z + 1.5·J。
   - 推论（B）：在 refZ + 175 以上蹬墙跳，f = 0，v_z ← min(0, v_z)，**不再给向上速度**。这就是 R5 不让跑墙链无限往上爬的另一半。
4. 记下这面墙（同墙判断和排斥，§5.6）；跳键用掉；lurch 窗口从这条命令开始（第 03 章 lurch）。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 离墙速度 `jumpOutwardSpeed` | 4.775 / 5.207 m/s | B 188 / A 205 u/s | 2.611 / 2.847 H/s | A 实测正好 205 | [数据] R5 `wallrunJumpOutwardSpeed`；[TF2 实测] T5 §5.3 |
| 向上速度 `jumpUpSpeed` | 6.096 / 5.842 m/s | B 240 / A 230 u/s | 3.333 / 3.194 H/s | 实测 vz 符合 min(230, vz + 345)，差 2.5 – 6（帧偏移） | [数据]；[TF2 实测] |
| 输入方向速度 `jumpInputDirSpeed` | 1.905 / 2.032 m/s | B 75 / A 80 u/s | 1.042 / 1.111 H/s | A 实测 79 | [数据]；[TF2 实测] |

#### 实现模板

```
// 单位：u、s
wallJump():
    boostArmed = true
    J  = jumpUpSpeed * f()
    v_h += wishDir * jumpInputDirSpeed
    out = dot(v_h, n);  if out < jumpOutwardSpeed: v_h += n * (jumpOutwardSpeed - out)
    v.z = min(J, v.z + 1.5*J)
    jumpTime = now                     // lurch 窗口
    consumeJump()
    lastWallNormal = n;  repelUntil = now + repelTime   // §5.6，等用户定
    end(JUMP)
```

Unity：`WallRunAbility.Tf2WallJump`。

#### 验收

- `Tf2WallRunTests.TheWallJumpPushesOutAtLeastTheOutwardSpeedAndCapsVz`（A）：离墙 ≥ 205、v_z = min(230, v_z + 345)、`boostArmed` = true。
- 对照数据：T5 §5.3 四个试次（例如不按键 (0, 37.3, −247.9) → (205.0, 37.3, 91.4)）。
- 合格线：离墙分量 ≥ `jumpOutwardSpeed`（差 < 1e-6）；v_z 差 < 1e-6（Unity 内部），对 TF2 记录值差 ≤ 6.3 u/s（帧偏移）。

#### 出处

- BSPEC §6；T3 §2.4；T5 §5.3。main
- D12 §1.1：墙跳先清 disable 再算 f，乘 `jumpUpSpeed`。main
- GAPS A5（墙跳打开 lurch 窗口）；PDIFF 开头"另外两点"（HSD 已经开了窗口，GAPS §6 说没开是错的）。main
- [TF2 反编译] `JumpOutOfWallRun` 0x180173a00。[反编译] R5 `JumpOutOfWallRun` 0x140a50050。

---

### 5.6 再贴墙的限制：同一面墙、墙跳排斥、0.5 s 计时

#### 原理

如果不限制，玩家可以在同一面墙上"跳一下、贴回去、再跳一下"一直往上爬。TF2 用一条很简单的规则挡住它：**同一面墙只能在上次起跑点以下再贴**，往上的不行；换一面墙随时可以。这让"墙 → 墙"的链条只能横着走或往下走，往上要靠两面墙之间来回。

另外两条规则资料里有，但实际效果存疑：

- **墙跳排斥**：TF2 代码里写了"墙跳后 0.2 – 0.4 s 削掉朝墙的速度"，但**实测没有任何效果**，#115 查出削速度的函数没有调用者，是死代码。HSD 实现成了另一种机制"0.2 s 内不能在同一面墙起跑"。**改不改等用户定**（PDIFF M-2）。
- **0.5 s 计时**："不跳、直接走下（滑下）台边之后半秒内不能跑墙"。代码读清了，但实测从没见到它起作用；HSD 没做。

#### 规则和公式

1. **同一面墙**（TF2 规则，B = A）：新墙法线和记下的墙法线点积 > `wallrun_sameWallDot` 0.9，并且现在的 z ≥ 上次起跑点 z + `wallrun_sameWallHeight` 0，就不能起跑。水平离多远都一样（`sameWallDist` 100 配 `sameWallSlope` 0，斜率为 0 等于不起作用）。落地清掉记下的墙。
   - 同一面墙在下面再贴：提速照给，但这次没有重力爬升（§5.2 起跑第 4 条）。
   - 小差别：TF2 只在墙跳和脱墙时记下这面墙；HSD 在起跑时记。效果一样（都按起跑点高度比）。
2. **墙跳排斥**（M-2，等用户定，两种都写）：

   | 选项 | 规则 | 依据 | 状态 |
   |---|---|---|---|
   | **HSD 现在** | 墙跳后 `repelTime` 0.2 s 内，法线点积 > 0.9 的墙不能起跑。不削速度 | 没有 TF2 依据 | Unity 默认 `repelTime` = 0.2 |
   | **PDIFF 建议 A** | `repelTime` 默认 0（关掉），代码留作开关 | TF2 实测没有排斥；#115：死代码 | 等用户定 |
   | PDIFF B | 保留 0.2 s | HSD 自己的保险，以后调小离墙速度时可能有用 | 等用户定 |
   | PDIFF C（不建议） | 照 TF2 代码削速度：0.2 s 内全削朝墙分量，0.2 → 0.4 s 线性淡出，按输入放宽 `repelSoftness` 5 | TF2 代码本来想做的；做了反而和 TF2 实测不一样 | 不建议 |

   实际影响：按现在的数，墙跳后回到同一面墙最快要约 0.28 s（TF2 实测，用 lurch 朝墙按）；不用 lurch 靠空中加速要 0.75 s（B）/ 0.82 s（A）[算]。所以 HSD 的 0.2 s 基本碰不到，选 A 或 B 手感都不变（PDIFF 的估算，Unity 里没跑过"墙跳后马上按朝墙键"）。
3. **0.5 s 计时**（TF2，HSD 没做）：记"不跳而离地"的时刻 t_off（离地那一刻写；离地后 0.1 s 内续写；地面起跳把它清 0；墙跳不写）。now − t_off < 0.5 s，并且上次站的地面法线 z = 1（斜面豁免）时，不能起跑。实测"走下梁边 0.15 s 后传送到墙边"照常起跑，限制没触发（GAPS A4），原因没查清。

| 量 | [m] | 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 同墙判定 `wallrun_sameWallDot` | — | 0.9（×，约 25.8°） | — | — | [TF2 数据]；GAPS A3 |
| 同墙高度 `wallrun_sameWallHeight` | 0 m | 0 u | 0 H | R5 也是 0 | [TF2 数据]；[数据] R5 N4-A 普查 |
| 排斥时间 `repelTime`（HSD） | — | 0.2 s | — | 等用户定（0 或 0.2） | [设计]（TF2 `wallrun_repelTimeMin` 0.2，死代码） |
| TF2 排斥淡出 `wallrun_repelTimeMax` | — | 0.4 s | — | 不实现 | [TF2 反编译] |
| 0.5 s 计时 | — | 0.5 s（续写 0.1 s） | — | 没实测到效果 | [TF2 反编译] GAPS A4 |
| 墙跳后最快贴回同一面墙 | — | 0.28 s | — | — | [TF2 实测] GAPS A5 `rp_toward` |

#### 实现模板

```
// 单位：u、s
sameWallBlocked(n, z):
    if lastStartZ is unset: return false            // 落地时清掉
    same = dot(lastWallNormal, n) > 0.9
    if same and z >= lastStartZ: return true        // 同一面墙只能往下
    if same and now < repelUntil: return true       // HSD 的排斥（M-2，等用户定）
    return false
```

Unity：`WallRunAbility.Tf2BeforeMove` 里 `sameWall` / `repelUntil` 两行；`Tf2WallRunParams.repelTime`。0.5 s 计时没做。

#### 验收

- `Tf2WallRunTests.TheSameWallOnlyBelowTheLastContact`：上次起跑点以上不起跑，以下起跑。
- 对照数据：T5 §5.4（离墙 265.7，再接触 328.7 不贴、118.1 贴）；GAPS A3（比起跑点低 7 u 贴回，提速照给）；T5 §8 BT-3（同墙再贴没有重力爬升）。
- M-2 定下来以后要加的测试（建议，`_notes`）：墙跳后马上按朝墙键，测最早贴回的时间；`repelTime` = 0 和 0.2 两种结果一样。

#### 出处

- GAPS §1.3（A3 同墙规则）、§1.4（A4 0.5 s 计时）、§1.5（A5 排斥实测）。main
- PDIFF M-2：两边规则、碰不碰得到、选项 A / B / C。main
- RNT §1（N1）：削速度的函数在 server.dll 和 client.dll 都没有调用者（PR #115，还没合并；分支 `ref/native-tail`）。
- T5 §5.4、§8 BT-3。main
- 00-INVENTORY 的过时表：TMS §11、`tf2/TF2-VS-APEX.md` §5、BSPEC 第 2 节最后一行说"T5 排除了离地时间、含义未知"已过时，以 GAPS A4 为准。
- [TF2 反编译] 排斥记录 0x1801603d0、削速度 0x18017eb80（无调用者）；0.5 s 计时 player+0x2588，常量 0x1808739f0。

---

### 5.7 M7 设计的跑墙（HSD，游戏默认）

#### 原理

M7 是 HSD 在研究 TF2 之前自己设计的跑墙，现在仍是游戏默认（Fun 配置）。它和 TF2 的思路不同：

- **要主动**：必须按住前进、沿墙已经有 200 u/s 才能起跑；不按前进 0.15 s 就下墙。不会"蹭"上墙。
- **和 R5 攀爬分开**：看着墙（35° 以内）是攀爬，斜着看（视线和跑的方向差 ≤ 75°）才是跑墙。跑墙中把视线转向墙，交给攀爬 → 翻越。
- **几乎水平**：重力恒定 0.15 倍，起跑时竖直速度夹到 60 – 150 u/s，是一条平平的线。
- **不加速**：沿墙速度朝 300 × msc 拉，进来时更快的话按 60 u/s² 慢慢降，永远不超过 max(进入速度, 345)。蹬墙跳水平上限 480。

所有数都是 [设计]，**真人手感没验收**（M7U 开头的两个标签）。

#### 规则和公式

**起跑**（全部满足）：在空中；按住前进；0.1 s 内碰过墙，墙面 |n_z| < 0.5；沿墙速度 ≥ 200 u/s；下坠不快于 450 u/s；没有驱动者；不是被挡住的墙（下面第 4 条）；视线和墙内法线夹角 > 35°（不在攀爬锥里）；视线和跑动方向夹角 ≤ 75°；没有"转开"（第 3 条）；这条命令没有未用掉的跳键。起跑时 v_z ← clamp(v_z, 60, 150)。恢复二段跳。

**跑墙中**（每条命令）：重力 × 0.15；沿墙速度 s：按住前进且 s < c（c = 300 × msc）→ s ← min(c, s + 400·msc·dt)；s > c → s ← max(c, s − 60·dt)；方向不变。朝墙推 40 u/s 保持接触。

**结束**（按顺序）：按跳 → 蹬墙跳（下面）；着地 `LAND`；0.1 s 没接触 `NO_WALL`；1.6 s `TIME`；沿墙 < 120 u/s `SLOW`；按蹲 `DUCK`；别的驱动者 `DRIVER`；**转开** `STEER_OFF`（视线离开"平行于墙"超过 30°，或者按着朝墙外的侧向键；离墙推 80 u/s）；松开前进满 0.15 s `RELEASE`。仲裁的 3 s 保护是最后一道。

**蹬墙跳**：v_h = 沿墙速度 × 1.0 + n̂·280，水平长度超过 480 就等比缩到 480；v_z = 300；算一次起跳（lurch 窗口）；跳键用掉。

**同一面墙**（第 4 条）：同一面墙（同一个面、法线点积 > 0.99；M8-B 起，共面的几块拼成的墙也算同一面，平面差 ≤ 2 u）**落地前不能再跑**。别的墙马上可以（墙 → 跳 → 对面墙）。旧规则"0.6 s 后可以"留作开关。

| 量 | [m] | HSD 设计值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 起跑沿墙速度 `minStartSpeed` | 5.08 m/s | 200 u/s | 2.778 H/s | — | [设计] |
| 结束沿墙速度 `minRunSpeed` | 3.048 m/s | 120 u/s | 1.667 H/s | — | [设计] |
| 跑墙速度 `runSpeed` × msc | 8.763 m/s | 300 × 1.15 = 345 u/s | 4.792 H/s | 对照 TF2 B 225 / A 420 | [设计] |
| 跑墙加速 `runAccel` × msc | 11.68 m/s² | 400 × 1.15 = 460 u/s² | 6.389 H/s² | — | [设计] |
| 超速时的降速 `overSpeedDecel` | 1.524 m/s² | 60 u/s² | 0.8333 H/s² | — | [设计] |
| 重力倍率 `gravityScale` | — | 0.15（×） | — | — | [设计] |
| 起跑竖直速度范围 `entryVzMin` / `entryVzMax` | 1.524 / 3.81 m/s | 60 / 150 u/s | 0.8333 / 2.083 H/s | — | [设计] |
| 起跑下坠上限 `maxEntryFall` | 11.43 m/s | 450 u/s | 6.25 H/s | — | [设计] |
| 最长时间 `maxDuration` | — | 1.6 s | — | TF2 1.75 / 2.0 s | [设计] |
| 接触宽限 `contactGrace` | — | 0.1 s | — | — | [设计] |
| 贴墙推力 `stick` | 1.016 m/s | 40 u/s | 0.5556 H/s | — | [设计] |
| 攀爬锥 `climbCone` / 视线到跑向 `maxViewToRun` | — | 35° / 75° | — | 35° = 攀爬的 `faceCone`（第 04 章） | [设计] |
| 转开角 `steerOffAngle` / 推力 `steerOffPush` | — / 2.032 m/s | 30° / 80 u/s | — / 1.111 H/s | — | [设计] |
| 松开前进宽限 `releaseGrace` | — | 0.15 s | — | — | [设计] |
| 蹬墙跳 法向 `jumpNormal` / 向上 `jumpUp` | 7.112 / 7.62 m/s | 280 / 300 u/s | 3.889 / 4.167 H/s | — | [设计] |
| 蹬墙跳 沿墙保留 `jumpAlongKeep` | — | 1.0（×） | — | — | [设计] |
| 蹬墙跳 水平上限 `jumpMaxSpeed` | 12.19 m/s | 480 u/s | 6.667 H/s | 随机测试最大 480 | [设计] |
| 共面容差 `coplanarTolerance` | 0.0508 m | 2 u | 0.02778 H | — | [设计] M8-B |

#### 实现模板

```
// 单位：u、s
if running:
    if jumpPressed:
        vh = alongWall(v, n)*1.0 + n*280;  if |vh| > 480: vh *= 480/|vh|
        v = (vh, 300); jumpTime = now; consumeJump(); end(JUMP); return
    why = LAND | NO_WALL | TIME(1.6) | SLOW(<120) | DUCK | DRIVER | STEER_OFF | RELEASE(0.15)
    if why: end(why); if why == STEER_OFF: v_h += n*80; return
else if canStartM7():
    running = true; v.z = clamp(v.z, 60, 150); airJumpsUsed = 0
gravityScale *= 0.15
s = |alongWall(v, n)|;  c = 300*msc
if forward > 0 and s < c: s = min(c, s + 400*msc*dt)
else if s > c:            s = max(c, s - 60*dt)
v_h = dir(alongWall(v, n))*s + n*dot(v, n) - n*40
```

Unity：`WallRunAbility.BeforeMove`（`rules = M7Design` 那条路）、`WallRunAbility.BlockedWall`（同墙 + 共面）、`WallRunAbility.SteersOff`、`WallRunAbility.ViewToInward`。开关：`WallRunParams.sameWallUntilLanding`（false = 0.6 s 规则）、`sameWallCoplanar`（false = M7-A 只比面 id 的旧规则）。

#### 验收

- `WallRunTests.AShallowApproachRunsTheWallAndAFacedWallIsTheClimbs`：斜着接近跑墙，正对是攀爬。
- `WallRunTests.TheRunHoldsTheBodyUpAndNeverAddsSpeedAboveTheRunSpeed`。
- `WallRunTests.EveryExitEndsTheRun`：TIME / NO_WALL / DUCK / STEER_OFF / RELEASE / 侧键 / LAND。
- `WallRunTests.TheJumpOffIsCappedOpensTheLurchWindowAndTheOppositeWallRunsButNotTheSameOne`。
- `WallRunTests.TheSameWallIsBlockedUntilTheNextLanding`；`WallChainM8BTests.AFlushWallOfSeveralBlocksIsOneWallForTheSameWallBlock`（旧规则复现"1.6 s 后在下一块上重新起跑"）。
- `WallChainM8BTests.TheZiplineSuperJumpIsTooSlowToStartAWallRun`。
- 演示：`m7_wallrun_chain`、`m7_wallrun_tapstrafe`、`m7_wallrun_mantle`、`m8b_chain_slope`、`m8b_chain_zip`（M7U §5、M8BU）。
- 合格线：随机测试里蹬墙跳水平速度 ≤ 480（最大 480）；跑墙中沿墙速度 ≤ max(进入, 345)；LS-18 = 549.84 u ± 1 u。

#### 出处

- M7U §3.1（规则）、§11（设计值表）、§10（已知缺口：曲面墙不算、视线不能让跑向反转）。main
- M8BU §5（共面修复）。main
- `research/phase2-local/m7/M7-A-PLAN.md`。main
- DEC D-08。main

---

### 5.8 蹬墙跳（R5：攀爬中按跳；任何贴墙的空中按跳）

#### 原理

R5 没有跑墙，但有一种"蹬墙跳"：**攀爬（第 04 章 §4.10）中按跳**，人从墙上向外弹出去，原来的竖直速度保留。它的力度和方向是固定的一个向量：朝墙外 182.78 u/s，再朝按键方向 75.08 u/s，**加**在原来的速度上。不按键时两份都朝墙外。按时间早晚没有区别。

这个数和 R5 setfile 里残留的跑墙蹬墙跳键几乎一样（`wallrunJumpInputDirSpeed` 75、`wallrunJumpOutwardSpeed` 188），说明 Apex 的攀爬蹬墙跳就是 TF2 墙跳那段代码（`JumpOutOfWallRun`）在攀爬状态下跑出来的；只是实测离墙分量是 182.78，比 188 低 2.8 %，原因没查到。

HSD 把它推广成游戏身体的基础能力（M5）：空中按跳时 0.1 s 内碰过墙，就是一次蹬墙跳（不一定在攀爬中），0.4 s 内最多一次。

#### 规则和公式

1. 触发（R5）：攀爬中或贴墙下滑中按跳（第 04 章 §4.10 第 2、4 条）。
   触发（HSD 游戏身体，`WallJumpAbility`）：在空中、按下跳、0.1 s 内有墙接触、距上次蹬墙跳 ≥ 0.4 s。跑墙中按跳归跑墙（§5.5 / §5.7），不是这一条；跑墙刚结束（按蹲、转开）接触还新鲜，按跳就是这一条。
2. Δv_h = n̂·O + d̂·I，O = 182.78 u/s，I = 75.08 u/s；d̂ = 归一化的水平输入方向（相对视线），**没有输入时 d̂ = n̂**。
3. Δv 加到现在的速度上；竖直速度保留（R5 实测多出 +3.5 – +5.3 u/s，属于这一条命令自己的空中步，不在公式里）。
4. 算一次起跳（打开 lurch 窗口）；跳键用掉。
5. 已知没对上的一种：跳的那条命令**只按侧向键**，实测 (140.9 离墙, 177.5 沿输入)，|Δv| 226.6，和公式 (182.8, 75.1) 不一样（sd 0.02，很稳定）。可能是这条命令上的新按键触发了 lurch 一类的重定向，没证实。Unity 照公式做。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 离墙 `outwardSpeed` | 4.643 m/s | 182.78 u/s | 2.539 H/s | 普查 188（差 −2.8 %，没解释） | [实测] WMM §3.2，n 73 |
| 输入方向 `inputDirSpeed` | 1.907 m/s | 75.08 u/s | 1.043 H/s | 普查 75 | [实测] |
| 接触宽限 `contactGrace`（HSD） | — | 0.1 s | — | — | [设计] |
| 最短间隔 `minInterval`（HSD） | — | 0.4 s | — | — | [设计] |

#### 实现模板

```
// 单位：u、s
if airborne and jumpPressed and contactAge <= 0.1 and now - lastWallJump >= 0.4:
    d = horizontalUnit(wishDir);  if d == 0: d = n
    v_h += n*182.78 + d*75.08        // 竖直不动
    jumpTime = now;  lastWallJump = now;  consumeJump()
```

Unity：`U:…/WallBounce.cs`（`WallBounce.Apply` / `Delta`、参数 `WallBounceParams.R5Reference()`），游戏身体用 `U:…/Abilities/WallJump/WallJumpAbility.cs`（`WallJumpAbility`、`WallJumpParams`）；R5 攀爬里的蹬墙跳在 `U:…/Abilities/Climb/ClimbAbility.cs`（`ClimbAbility.WallJump` → `ClimbAbility.Bounce`，同一个 `WallBounce.Delta`，另加实测的竖直小项 `ClimbParams.bounceUp` 4 u/s（攀爬中）/ `bounceUpSlide` 2.6 u/s（贴墙下滑中），即上面第 3 条的 +3.5 – +5.3）。游戏身体的 `WallJumpAbility` 不加这个小项。

#### 验收

- `WallBounceTests.NoInputGoesAlongTheNormal`、`WallBounceTests.ForwardIntoTheWallSubtractsBackAddsAndMagnitudeIsIgnored`、`WallBounceTests.IsAddedAndKeepsVertical`。
- `A2Climb.WallBounceFromTheClimbIsTheM3Vector`、`A2Climb.JumpFromTheSlideIsTheWallBounce`（贴墙下滑中按跳）。
- `M6LurchTests.ClimbBounceReAnchorsTheLurchWindow`；`WallChainM8BTests.RunThenCrouchThenJumpIsTheMeasuredBounceAndOpensTheWindow`；`WallRunTests.AfterTheRunAContactPressIsTheMeasuredWallBounce`。
- `JumpArbitrationTests.WallBounceOwnsAFreshContactAndTheAirJumpTheRest`：接触新鲜时跳键归蹬墙跳，否则归二段跳（第 06 章）。
- 对照数据：WMM §3.2（none = O + I、W = O − I，残差 sd 0.0005 / 0.0015）。
- 合格线：不按键 |Δv| = 257.86 u/s ± 0.01；按前进（朝墙）|Δv| = 107.70 ± 0.01。

#### 出处

- WMM §3.2：公式、拟合、和普查对照、只按侧向键的例外。main
- `U:…/Abilities/WallJump/README.md`：HSD 的 0.1 s / 0.4 s 是 M5 设计。main
- `research/phase2-local/m5/SKILL-RULES.md`（M5 门控）。main
- 第 04 章 §4.10（攀爬中按跳的入口）。分支 `handbook/ch04`，还没合并。
- [反编译] R5 `JumpOutOfWallRun` 0x140a50050（攀爬和跑墙共用）。

---

### 5.9 二段跳（TF2 规则，P-02）

#### 原理

TF2 的二段跳有两个设计目标：

1. **下坠也能救回来**：不管现在往下掉多快，二段跳把竖直速度**直接换成**一个固定的起跳速度（300 u/s），不是加上去。所以二段跳的高度是可预期的。
2. **能改方向但不刷速度**：有方向输入时，从现在的水平速度里扣掉 180，再朝输入方向加 180。快的时候等于把 180 u/s 转向输入方向；慢的时候整个换成"输入方向 × 180"。

还有一个分支：如果已经在快速上升（剩余能升的高度 + 0.25H ≥ H），不再"换成 300"（那会让人变慢），而是在原来基础上再加一点。这一点加多少，HSD 和 TF2 实测不一样，**等用户定**（PDIFF M-1）。

二段跳次数 1；落地和跑墙起跑时恢复（TF2 的落地马上再跳 skip 也会恢复，第 03 章）。

#### 规则和公式

H = 60 u（`superjumpMin/MaxHeight` 60 / 60），起跳速度 V = √(2·`sv_gravity`·H)（起跳用 `sv_gravity` 750，不乘 gravityScale）= 300 u/s。

1. **竖直**：剩余上升高度 r = v_z² / (2·750)（v_z > 0 时，否则 0）。
   - 如果 v_z ≤ 0 或 r + 0.25·H < H（即 v_z < 259.8 u/s）：v_z ← V = 300。下坠被直接取消。
   - 否则（快速上升）：**M-1，等用户定**：

     | 选项 | 公式 | 依据 | 和 TF2 实测 |
     |---|---|---|---|
     | **HSD 现在** | v_z ← √(v_z² + 2·750·0.25·H) = √(v_z² + 150²) | TF2 静态读法当时理解成"加能量" | 5 次每次少 106 – 122 u/s |
     | **PDIFF 建议 A** | v_z ← v_z + √(2·750·0.25·H) = v_z + 150 | GAPS §1.6 重读静态 + 实测 | 5 / 5 吻合，只差固定的 −6.2（帧偏移） |
     | PDIFF B | 不改 | HSD 的设计：被往上送时二段跳不叠那么多 | — |
     | PDIFF C | 加开关，A 和 B 都留 | 合留档规则 | 默认仍要定 |

     两者升高的差正好是 v_z / 5 u（(v_z + 150)² − (v_z² + 150²) = 300·v_z，除以 2·750）。碰到的场合：地面起跳后 0.040 s 内（HSD 起跳 289.8 > 259.8 只维持这么久）、跳板 / 钩爪 / 火箭跳往上送的时候（v_z 400 – 1000，差 80 – 200 u）。墙跳后碰不到（v_z ≤ 240）。
2. **水平**（有移动输入时）：s = |v_h|。s > 180 → v_h −= v̂_h·180；否则 v_h = 0。然后 v_h += 输入方向 × 180。没有输入不改水平。
3. 次数 `superjumpLimit` 1；TF2 在落地、跑墙起跑、skip 连跳时恢复。
4. 起跳后马上就能用（没有最早时间限制；T5 0.055 s 可用）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 二段跳高度 H `height` | 1.524 m | 60 u | 0.8333 H | R5 Sparrow 112 / 200（不实现） | [TF2 数据] |
| 起跳速度 V（750 下） | 7.62 m/s | 300 u/s | 4.167 H/s | 实测记录 295.8（帧偏移 −4.2） | [算] [TF2 实测] |
| 快速上升门槛（r + 0.25H ≥ H） | 6.599 m/s | v_z ≥ 259.8 u/s | 3.608 H/s | 实测 258.5 时走"换成 300" | [算] [TF2 实测] GAPS A6 |
| 最低高度比例 `minHeightFraction` | — | 0.25（×） | — | — | [TF2 数据] |
| 快速上升的加量（选项 A） | 3.81 m/s | +150 u/s | 2.083 H/s | 实测 +143.7（= 150 − 帧偏移） | [TF2 实测] |
| 水平 `horizontalSpeed` | 4.572 m/s | 180 u/s | 2.5 H/s | 实测 (166.1, 200.4) → (231.2, 61.8)，预测 (231.3, 61.8) | [TF2 数据] [TF2 实测] |
| 原地跳 + 二段跳总高（HSD 重力 750） | 2.916 m | 114.8 u | 1.594 H | TF2 本体（重力 600）[算] 约 150 u，没实测 | LS-22 [实测 Unity] |

#### 实现模板

```
// 单位：u、s
tf2DoubleJump(v, wish):
    V = sqrt(2*svGravity*60)                       // 300
    r = v.z > 0 ? v.z*v.z/(2*svGravity) : 0        // 门槛用 sv_gravity
    if v.z > 0 and r + 0.25*60 >= 60:
        v.z = sqrt(v.z*v.z + 2*svGravity*15)       // HSD 现在；选项 A：v.z += sqrt(2*svGravity*15)
    else:
        v.z = V
    if wish != 0:
        s = |v_h|;  v_h = s > 180 ? v_h - unit(v_h)*180 : 0
        v_h += wish*180
    jumpTime = now                                 // lurch 窗口（HSD 开关 opensLurchWindow）
```

Unity：`U:…/Abilities/DoubleJumpTf2/Tf2SuperJump.cs`（`Tf2SuperJump.Velocity`、常量 `Height` 60、`HorizontalSpeed` 180、`MinHeightFraction` 0.25、`MinSinceTakeoff` 0，`Tf2SuperJump.Params()`），由 `U:…/Abilities/DoubleJump/DoubleJumpAbility.cs` 在 `DoubleJumpParams.rule = DoubleJumpRule.Tf2` 时调用（`DoubleJumpAbility.ApplyTf2`）。开关：Esc 菜单 "Double jump rule (P-02)"（`hsd.tf2.djump`）。D-69：这个文件夹是可复用包，不绑成道具。

和 TF2 的差别（写进 `_notes`）：

- 门槛的重力：Unity 用 `baseParams.Gravity`（750 × gravityScale），TF2 用 `sv_gravity`。HSD 所有配置 gravityScale = 1，现在没有差别。
- 恢复规则：Unity 在 TF2 规则下仍用 HSD 的恢复开关（落地、跑墙起跑、抓边、上滑索恢复；钩爪、攀爬不恢复），TF2 只有落地、跑墙、skip。
- 重力：TF2 预设用 HSD 的 750，TF2 本体下落 600，所以总高不同（LS-22）。

#### 验收

- `Tf2SuperJumpTests.T5TrialsAreReproduced`：T5 的四个水平试次。
- `Tf2SuperJumpTests.NoInputKeepsTheHorizontalVelocity`；`Tf2SuperJumpTests.PresetIsTheP02Preset`。
- `Tf2SuperJumpTests.RisingWithEnoughRiseLeftAddsAQuarterHeight`：测的是 HSD 现在的 √ 公式；M-1 选 A 要改这个测试的期望值（PDIFF M-1 "改 A 要动"）。
- `Tf2WallRunTests.Tf2DoubleJumpReplacesVzAndRedirects180`、`Tf2WallRunTests.Tf2DoubleJumpSlowerThan180BecomesTheInputTimes180`。
- 对照数据：T5 §5.5（水平四个试次、竖直都换成 300）；GAPS A6 / PDIFF M-1 表（7 个 v_z 的实测）。
- 合格线：水平和 T5 差 ≤ 0.2 u/s；竖直"换成"分支和 300 差 < 1e-6（Unity 内部），对 TF2 记录值差 ≤ 6.3 u/s；LS-22 = 114.8 u ± 0.5 u。

#### 出处

- T3 §2.6；T5 §5.5；TMS §4.3。main
- GAPS §1.6（A6）：门槛 259.8、快速上升 +150 的实测。main
- PDIFF M-1：两边规则、实测对照、选项 A / B / C。main
- DEC D-58（P-02）、D-69（复用包）。main
- `U:…/Abilities/DoubleJumpTf2/DATA.md`、`README.md`。main
- [TF2 反编译] `Jump` 0x180172870 的 superjump 分支。

---

### 5.10 二段跳（HSD 设计，M7，游戏默认）

#### 原理

HSD 默认的二段跳更"温和"：高度 45 u（比 TF2 的 60 低），**水平速度大小永远不变**，只把方向朝输入转一半。设计意图是"二段跳是空中的一次修正，不是加速"，配合 R5 原样的地面和空中移动，不让二段跳成为刷速度的手段。

另外两条和 TF2 不同的设计：

- **往上的速度不会被压低**：v_z = max(v_z, 259.8)。被跳板送上天时按二段跳不会变慢（和跳板兼容）。
- **起跳后 0.1 s 内不能用**：连按两下跳不会马上把二段跳浪费掉。

二段跳和 Valkyrie 的喷气共用跳键，按规则分（下面第 6 条）。

#### 规则和公式

1. 触发：空中按下跳、这个跳键没被别的动作用掉（攀爬、滑索、跑墙、蹬墙跳在前面，第 06 章）、还有次数、离起跳 ≥ 0.1 s、没有驱动者在跑。
2. 次数 `maxAirJumps` 1。
3. 竖直：V = √(2·g·45) = 259.8 u/s；v_z ← max(v_z, V)（下坠被替换，上升不压低）。
4. 水平：有输入且 s = |v_h| > 0 时，方向 ← normalize((1 − 0.5)·v̂_h + 0.5·输入方向)，大小 s 不变。
5. 算一次起跳（打开 lurch 窗口，开关 `opensLurchWindow`）。
6. 和喷气：`AirJumpFirst`（默认）—— 还有二段跳就是二段跳，按住 0.25 s 从同一次按住接上喷气；没有二段跳了就给喷气。`JetsFirst` —— 喷气能开就给喷气，开不了才是二段跳。
7. 恢复：落地（总是）；跑墙起跑；抓边；上滑索。**不**在钩爪、攀爬时恢复。都有开关。

| 量 | [m] | HSD 设计值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 高度 `height` | 1.143 m | 45 u | 0.625 H | TF2 60 | [设计] |
| 起跳速度 V | 6.599 m/s | 259.8 u/s | 3.608 H/s | — | [算] |
| 转向比例 `redirect` | — | 0.5（×） | — | 0 = 不转，1 = 全转 | [设计] |
| 最早时间 `minSinceTakeoff` | — | 0.1 s | — | TF2 0 | [设计] |
| 接喷气的按住时间 `holdForJets` | — | 0.25 s | — | — | [设计] |
| 原地跳 + 二段跳总高 | 2.535 m | 99.794 u | 1.386 H | — | LS-21 [实测 Unity] |

#### 实现模板

```
// 单位：u、s
if airborne and jumpPressed and unused and airJumpsUsed < 1 and now - takeoff >= 0.1 and no driver:
    V = sqrt(2*g*45)
    if |v_h| > 0 and wish != 0:
        d = normalize(0.5*unit(v_h) + 0.5*wish);  v_h = d*|v_h|
    v.z = max(v.z, V)
    jumpTime = now;  consumeJump();  airJumpsUsed++
```

Unity：`DoubleJumpAbility.Apply`、`DoubleJumpParams`（`HsdDesign` 那一套）、枚举 `JetsJumpRule`。M8-A 起二段跳先"申请"跳键（`JumpRank.AirJump` 200），等这条命令的发射和驱动者都确定后才"提交"（`DoubleJumpAbility.CommitJump`），被跳板发射覆盖时不扣次数（第 06 章）。

#### 验收

- `DoubleJumpTests.OneAirJumpPerAirborneVzModelNoHorizontalGainAndTheLandingResetsIt`。
- `DoubleJumpTests.CountAndLurchWindowAreConfigurable`；`DoubleJumpTests.ResetRulesWallRunAndHangGiveItBackTheGrappleDoesNot`。
- `DoubleJumpTests.APadLaunchIsNeverLoweredByAnAirJump`；`DoubleJumpTests.NoAirJumpWhileSomethingDrives`。
- `DoubleJumpTests.JetsRuleAirJumpFirstHoldsIntoTheJets`、`DoubleJumpTests.JetsRuleJetsFirstGivesThePressToTheJetsUnlessTheyCannot`。
- 演示：`m7_djump_gap`（0.40 s 二段跳越过 300 u 的沟）、`m7_djump_lurch`、`m7_djump_grapple`、`m7_djump_zipline`、`m7_djump_jets`、`m7_bounce_djump`（M7U §5）。
- 合格线：二段跳不增加水平速度（随机测试每条命令检查，超出的只能是这条命令的空中加速）；LS-21 = 99.794 u ± 0.5 u。

#### 出处

- M7U §3.3、§11。main
- M8AU §2（申请 → 提交）。main
- DEC D-08；D-68（三种二段跳都用 R5 原生二段跳 punch，第 07 章）。main

---

### 5.11 挂墙（TF2，HSD 没做）

#### 原理

TF2 有一个被动 `pas_wallhang`：跑墙中按开镜键，人就钉在墙上，可以停下来瞄准。它是"跑墙中按一下暂停"，不是新的移动方式。HSD 暂时不做（P-06 留存，以后可能做成道具或被动，D-58）。这里把规则和实测写全，**以后照着做就够**（GAPS §8"能照做"）。

#### 规则和公式

1. 触发：跑墙中按开镜（`+zoom`），带被动 `pas_wallhang`（`wallrunAdsType "wallhang"`），手离墙 ≤ 18 u。下一条命令就挂上。不带被动时开镜就只是开镜。
2. 停住：速度在 `wallrun_hangStopTime` 0.5 s 内降到 0（实测 0.31 s 降到 < 1；按住前进时 0.49 s）。
3. 下滑：挂上后 `hangslipstarttime` 3 s 开始下滑，1 s 到满（实测 3.1 s v_z −0.2，3.5 s −6.7，3.75 s −30）。
4. 掉落：挂满 `wallrun_hangTimeLimit` 4 s 结束，水平 70 u/s 推离墙。中途松开开镜立刻掉，同样推 70。
5. 挂墙有自己的计时：跑了 1.3 s 才挂，仍是挂上后 4 s 掉。
6. 被动 `pas_wall_runner`：挂墙时长 +21 s（25 s），实测 4 s 不掉、3 s 起一直滑到地面。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 手离墙距离 | 0.4572 m | 18 u | 0.25 H | — | [TF2 反编译] |
| 停住时间 `hangStopTime` | — | 0.5 s | — | 实测 0.31 s（按前进 0.49 s） | [TF2 数据] [TF2 实测] GAPS B1 |
| 开始下滑 `hangslipstarttime` | — | 3 s | — | 实测 3.0 s | [TF2 数据] [TF2 实测] B2 |
| 最长 `hangTimeLimit` | — | 4 s | — | 实测 4.00 s | [TF2 数据] [TF2 实测] B3 |
| 掉落推离 `fallAwaySpeed` | 1.778 m/s | 70 u/s | 0.9722 H/s | — | [TF2 实测] B3 |
| `pas_wall_runner` 加时 | — | +21 s | — | — | [TF2 数据] B4 |

#### 实现模板

```
// 单位：u、s（HSD 没做；建议的写法）
if running and adsPressed and hasPassive(wallhang) and handDist <= 18:
    hanging = true; hangStart = now; v0 = v
hanging:
    t = now - hangStart
    v = v0 * max(0, 1 - t/0.5)                     // 0.5 s 内停住（线性是推断，见 _notes）
    if t > 3: slip = min(1, t - 3); v.z -= g*slip*dt   // 下滑曲线是推断
    if not adsHeld or t >= 4: hanging = false; v_h += n*70
```

Unity：**没有**。`ClimbAbility.LedgeHangParams` 是 M7 的抓边（§5.12），不是这个。

#### 验收

无（HSD 没做）。以后做的话，对照 GAPS B1 – B3 的四个数（0.31 s、3.0 s、4.00 s、70 u/s），合格线建议差 ≤ 一条命令。

#### 出处

- GAPS §2（B1 – B3）、§3（B4）、§8。main
- T3 §2.5；TMS §6.6。main
- DEC D-58（P-06 留存）。main
- 实测数据 `tf2/runtime/data/20261108_034342_g8_a` 的 `wh_*`；原始日志在 HSD-RawData#13。

---

### 5.12 抓边悬挂（HSD 设计，M7，默认 Fun 开）

#### 原理

R5 没有挂边（M6-A 实测）。M7 加了一个：跳到台沿刚好够不着翻越、又不够高去攀爬的位置（台沿比脚高 80 – 110 u），手抓住台沿挂在那里，之后可以爬上去（走 R5 实测的翻越）、蹬出去、或松手。它只在"本来会开始攀爬"的地方替代攀爬的开始，**正在上升时碰到墙仍然是 R5 的攀爬**，所以不改变 R5 的攀爬手感。

所有数是 [设计]，真人手感没验收。

#### 规则和公式

1. 抓住（全部满足）：本来会开始攀爬（空中、按住前进、刚碰到正对的墙、这次腾空没爬过）；翻越（≤ 80 u）够不着；台沿比脚高 80 – 110 u 且上面有空间；v_z ≤ 60 u/s（快到顶或在下落）；下落不快于 400 u/s；这次接触的撞墙水平速度 ≤ 420 u/s；沿墙速度 ≤ 200 u/s；离上次松手 / 蹬出 ≥ 0.6 s。
2. 挂着：0.12 s 内移到台沿下方 92 u 处停住。A / D 沿台沿横移 70 u/s（台沿和上方空间连续时）。
3. 出口：正对墙（90° 以内、没按后退）按跳 → 爬上去（R5 实测翻越，第 04 章）；按后退 + 跳或看着别处按跳 → 蹬出：n̂·230 + 沿墙输入 × 75，v_z 250（算起跳）；按蹲 → 松手（离墙 30 u/s）；5 s 保护 → 松手。之后落地前不能再抓或爬。
4. 抓住时恢复二段跳。

| 量 | [m] | HSD 设计值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 手的窗口 `minRise` / `maxRise` | 2.032 / 2.794 m | 80 / 110 u | 1.111 / 1.528 H | 80 = 翻越高度 `mantleHeight` | [设计] |
| 挂的位置 `hangRise` / 用时 `settleTime` | 2.337 m / — | 92 u / 0.12 s | 1.278 H / — | — | [设计] |
| 进入竖直速度 `maxEntryVz` | 1.524 m/s | 60 u/s | 0.8333 H/s | — | [设计] |
| 下落上限 `maxFallSpeed` / 撞墙上限 `maxApproachSpeed` / 沿墙上限 `maxAlongSpeed` | 10.16 / 10.67 / 5.08 m/s | 400 / 420 / 200 u/s | 5.556 / 5.833 / 2.778 H/s | — | [设计] |
| 再抓冷却 `regrabCooldown` / 最长 `maxHangTime` | — | 0.6 s / 5 s | — | — | [设计] |
| 横移 `shimmySpeed` | 1.778 m/s | 70 u/s | 0.9722 H/s | — | [设计] |
| 蹬出 `jumpOffOut` / `jumpOffUp` / `jumpOffSide` | 5.842 / 6.35 / 1.905 m/s | 230 / 250 / 75 u/s | 3.194 / 3.472 / 1.042 H/s | — | [设计] |
| 松手推力 `dropPush` | 0.762 m/s | 30 u/s | 0.4167 H/s | — | [设计] |

#### 实现模板

抓边是攀爬状态机的一个新阶段（`ClimbPhase.Hang`），复用攀爬的台沿探测和"驱动者"状态；爬上去交给已有的翻越。

```
// 单位：u、s
onClimbWouldStart(ledge):
    if hang.enabled and 80 <= ledge.rise <= 110 and v.z <= 60 and fall <= 400
       and impactSpeed <= 420 and along <= 200 and now - lastLetGo >= 0.6:
        phase = Hang; settle to (ledge.top - 92) in 0.12 s; airJumpsUsed = 0; return
    startClimb()                       // 第 04 章
```

Unity：`U:…/Abilities/Climb/ClimbAbility.cs`，`LedgeHangParams`、`ClimbPhase.Hang`。配置 `MovementConfig.hsd.ledgeHang`；游戏内 `8` 键。

#### 验收

- `LedgeHangTests.ANearApexGrabHangsAndJumpClimbsUpThroughTheMantle`、`LedgeHangTests.TheGuardsKeepTheMeasuredClimbAndPreventSnapping`、`LedgeHangTests.EveryExitIsAlwaysAvailable`、`LedgeHangTests.ShimmyMovesAlongTheLedgeAndStopsWhereItEnds`。
- 演示 `m7_hang_climbup`、`m7_hang_jumpoff`。
- 合格线：抓边关着时攀爬状态机和 M6-A 逐位一致（Reference 回放不变）。

#### 出处

- M7U §3.2、§10、§11。main
- `research/phase2-local/m6/a2_climb/A2-CLIMB.md`（R5 没有挂边）。main
- 第 04 章 §4.10 末尾（抓边归第 05 章）。分支 `handbook/ch04`，还没合并。

---

### 5.13 窗户辅助（TF2，HSD 没做）

#### 原理

TF2 地图里在窗口处放了看不见的"提示"。玩家起跳、二段跳、蹬墙跳、lurch 之后，如果预测的轨迹从窗口附近擦过，游戏会**悄悄把速度方向转一点**（不改大小），让人从窗口里穿过去，而不是撞在窗框上。这是关卡和移动之间的一个辅助：关卡可以放比较小的窗口，玩家不会因为几十 u 的偏差撞墙。HSD 没做（T-11 开关，未做）。

#### 规则和公式

1. 提示是关卡里的长方形（中心、半宽、半高、厚度 0，平面是竖的）。
2. 在这些时刻检查：空中 lurch 生效后、蹬墙跳、脱墙、钩爪、（推测）起跳。
3. 预测落点：终点 = 起点 + v·t − ½·g·t²，t = `window_hint_lookahead_time` 0.8 s。轨迹穿过某个提示附近时调整。
4. 调整：只转水平方向（实测 5.9° / 8.3°，规则上限 15°），速度大小不变；竖直速度修正在 +80 / −150 u/s 以内（实测偏高时 −40 / −44）。正对窗口不改。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 预测时间 `window_hint_lookahead_time` | — | 0.8 s | — | — | [TF2 反编译] GAPS C1 |
| 水平转角上限 | — | 15° | — | 实测 5.9° / 8.3°（偏 40 / 45 u） | [TF2 反编译] [TF2 实测] C3 |
| 竖直修正范围 | +2.032 / −3.81 m/s | +80 / −150 u/s | +1.111 / −2.083 H/s | 实测 −40 / −44 | [TF2 反编译] [TF2 实测] |

#### 实现模板

```
// 单位：u、s（HSD 没做）
onJumpLike(pos, v):
    for hint in windowHints:
        end = pos + v*0.8 - 0.5*g*0.8²*up
        if trajectory passes hint plane near hint:
            rotate v_h toward hint center by <= 15°, keep |v_h|
            adjust v.z within [-150, +80] toward hint height
```

Unity：没有。

#### 验收

无（没做）。只测过二段跳一种触发；地面起跳、墙跳、lurch 三种触发各修正多少没测（B05-1 的一部分）。

#### 出处

- GAPS §4（C1 – C3）、§8。main
- [TF2 反编译] `Script_GetWindowHint` 0x18060a610、搜索 0x1806079b0、调整函数 0x18016dd00。

---

### 5.14 哪些动作算一次起跳、打开 lurch 窗口（总表）

#### 原理

lurch（起跳后一小段时间里按方向键能改方向，第 03 章）的计时从"最近一次起跳命令"算。所以"一个动作算不算起跳"直接决定它后面能不能 tap strafe。R5 的规则是：**真正调用了跳跃的动作算**（地面跳、攀爬蹬墙跳、滑索 super jump、钩爪挂上时的跳），**被外力发射的不算**（跳板、升降梯弹出、Revenant 扑击、滑索普通跳离、钩爪松开）。HSD 的 Fun 配置在几处有意改成"算"（[设计]，M5 / M5.5 的"发射 → lurch"），Reference 跟 R5。

#### 规则和公式

| 动作 | Reference（= R5） | Fun（游戏默认） | R5 依据 | 开关 |
|---|---|---|---|---|
| 地面起跳、滑铲跳 | 算 | 算 | [实测] 第 03 章 | — |
| 攀爬 / 贴墙下滑中蹬墙跳（§5.8） | 算 | 算 | [实测] A1 §6 | — |
| 游戏身体的蹬墙跳 `WallJumpAbility`（§5.8） | 算 | 算 | 同上（推广） | — |
| 跑墙中蹬墙跳（M7 / TF2，§5.5 / §5.7） | 不适用（Reference 没有跑墙） | 算 | [TF2 实测] GAPS A5 | — |
| 二段跳（§5.9 / §5.10） | 不适用 | 算 | — [设计] | `DoubleJumpParams.opensLurchWindow` |
| 抓边蹬出（§5.12） | 不适用 | 算 | — [设计] | — |
| 滑索普通跳离 | **不算** | 算 | [实测] M9-A：跳离后 3 条命令按 D，\|Δv\| 4.18 = 普通空中加速 | `ZiplineParams.jumpOffIsLurchAnchor` |
| 滑索 super jump | 算 | 算 | [实测]（是一次地面等价的跳） | — |
| 钩爪挂上时的跳（attach jump） | 算 | 算 | [推断] | — |
| 钩爪松开 | 不算 | 不算（Fun 里接一个二段跳会重开窗口） | M8-B | — |
| 跳板发射 | **不算** | 算 | [实测] M9 r_d1：反向链每个按键都是普通空中加速 | `MovementConfig.padLaunchOpensLurchWindow` |
| 跳板二段跳（Octane） | 算 | 算 | [实测] M8 | `PadDoubleJumpParams.restartsLurchWindow` |
| 升降梯弹出（Horizon） | **不算** | 算 | [实测] M8 r_lift：弹出后 0.25 s 按后退 / 侧向是普通 800 u/s² | `MovementConfig.liftEjectOpensLurchWindow` |
| Revenant 扑击 | **不算** | 算 | [实测] M9-B | `RevenantParams.pounceOpensLurchWindow` |
| 其他发射（走仲裁的 launch；**击退不算**） | 按 `SkillRules.launchOpensLurchWindow`（默认 true） | 同左 | 没测 | `SkillRules.launchOpensLurchWindow`。击退不走技能层的发射（§5.37 第 11 条），`R5MotorV2.ApplyDamageImpulse` 不写 `jumpTime`，所以 Reference 和 Fun 都**不开** lurch 窗口（HSD-Unity PR #52 代码核对（hb-integrate 11-14 按 hb-ch06 备注改）） |
| Vantage 回声结束跳 | 不算 | 算 | — | `VantageParams.endJumpOpensLurchWindow` |

#### 实现模板

```
// 单位：s
// 任何"算起跳"的动作，在它改速度的那条命令写：
jumpTime = now
// lurch 判定只看 now - jumpTime（第 03 章 lurch 规则）
```

Unity：所有动作都写 `R5MotorV2.jumpTime`；发射统一在 `SkillArbiter` 里按 `SkillRules.launchOpensLurchWindow` 和各能力的例外写（`U:…/Abilities/_Core/SkillArbiter.cs`，发射那一段）；每个配置的开关在 `U:…/MovementConfig.cs`（`MovementConfigs.Reference()` 把升降梯和跳板设成 false）。

#### 验收

- `M6LurchTests.ClimbBounceReAnchorsTheLurchWindow`、`WallChainM8BTests.RunThenCrouchThenJumpIsTheMeasuredBounceAndOpensTheWindow`、`WallRunTests.TheJumpOffIsCappedOpensTheLurchWindowAndTheOppositeWallRunsButNotTheSameOne`、`DoubleJumpTests.CountAndLurchWindowAreConfigurable`。
- 跳板 / 升降梯 / 扑击 / 滑索的 Reference 规则在对应各节的验收里。
- 合格线：Reference 下"不算"的动作后按方向键，\|Δv\| 等于这条命令的普通空中加速（不出现 lurch 的大幅转向）。

#### 出处

- `research/phase2-local/m8/unity/M8B-UNITY.md` §2（"Turning after other moves"一段）。main
- `research/phase2-local/m6/a1_lurch/A1-LURCH.md` §6（蹬墙跳是起跳命令）；`research/phase2-local/m9/r_zip/ZIPLINE-A1.md`（滑索跳离不开窗口）；`research/phase2-local/m9/r_d1/D1.md`（跳板发射不开窗口）；`research/phase2-local/m8/r_lift/LIFT.md`（升降梯弹出不开窗口）；`research/phase2-local/m9/r_rev/REVENANT.md`（扑击）。main
- 第 03 章 lurch（分支 `handbook/ch03`，还没合并）。

---

## 第二部分 · 滑索和滑索枪（§5.15 – §5.24）

**白话说明**

这一节管两样东西：

1. **地图滑索**：地图里固定的一根绳。看着它按交互键（Apex 的 E，HSD 的 X）就挂上去，人吊在绳子下面被拉着走，越走越快，到头自动甩下来；中途可以按跳跳下来（带一个固定的向上速度）或者按蹲松手。挂上后马上再按一次跳，还能多跳一次（社区叫 Super Jump）。
2. **滑索枪**（Pathfinder 的大招 Zipline Gun）：站在地上朝远处开一枪，从脚边到落点拉出一根新绳。这根绳和地图滑索是**同一套东西**，只是滑得更快（封顶 1000 u/s，地图绳 600 u/s），陡的绳子下来时方向不一样。

和别的章的分界：

- 滑索中、滑索后的**镜头**（滑索上眼睛慢慢下沉 `zip_eye_offset`、绳子横滚 `rope_roll`、下滑索的 kick `zip_detach`）都在第 07 章。本节只写挂上时"视角被拉向绳子方向"这条**输入规则**（5.16）。
- 跳离以后的空中加速、lurch、二段跳、跑墙，以及"一次跳跃键按下只给一个动作"的仲裁，详见第 06 章；本节只写和滑索直接有关的几条（5.19、5.20）。
- 钩爪本身在本章钩爪一节；本节只写"钩爪钩到绳上自动换成滑索"这一步（5.16）。
- 普通起跳（√(2g·56) = 289.828 u/s、半步重力）在第 03 章。

**读完能做出什么**：照 5.15 – 5.22 能写出和 R5 逐命令一致的地图滑索（挂上、滑行、跳离、蹲下、到端、竖直绳、Super Jump）；照 5.23 – 5.24 能写出滑索枪，并且让它的绳直接用前面那套滑索代码。

**两套配置**：本节写的是 Reference（按 R5）。Fun 配置在滑索上有几处 HSD 设计改动，统一列在每项的规则段里，标 [设计]。

**本节出处缩写**：

| 缩写 | 文件 |
|---|---|
| NP2 | `research/rea-native/subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md`（原生钩爪 / 滑索 / 跳板） |
| A3 | `research/phase2-local/m6/a3_zip/A3-ZIPLINE.md`（M6 滑索实测，两轮 200 次） |
| GZ | `research/phase2-local/m6/a3_zip/GRAPPLE-ZIP.md`（钩爪 → 滑索交接实测） |
| ZA1 | `research/phase2-local/m9/r_zip/ZIPLINE-A1.md`（M9 中段 / 端点 / 空中 / 重抓实测，8 个会话） |
| ZG | `research/phase2-local/m10/r_zipgun/ZIPGUN-M10.md`（滑索枪实测） |
| ZGO | `research/phase2-local/m10/r_zipgun/analysis_output.txt`（滑索枪逐次数据） |
| M8A | `research/phase2-local/m8/unity/M8A-UNITY.md` §4（M8-A 滑索审查） |
| M9AU | `research/phase2-local/m9/unity/M9A-UNITY.md`（M9-A Unity 改动） |
| M10BU | `research/phase2-local/m10/unity/M10B-UNITY.md`（滑索枪 Unity 实现） |
| SV | `research/phase2-local/static-values/STATIC-VALUES.md` §3.4 |
| N4A | `research/rea-native/n4/N4A-READBACK.md` 和会话 `research/phase2-local/data/20261023_203953_N4A_classvars_pathfinder/report/census.csv`（setfile 读回） |
| TL | `research/phase2-local/m9/d_library/TECHNIQUE-LIBRARY.md` §5.2（社区 wiki 对照） |
| DIFF / DEC | `R5-DIFF-ARCHIVE.md` / `DECISIONS.md` |
| U: | HSD-Unity；`U:…/` = `Assets/HSD/R5Replay/Runtime/` |

**记号**：命令 = 一条 usercmd，Unity 固定 dt = 1/120 s；R5 实测都在 120 fps。g = 750 u/s²（A3 实测 750.12）。"沿绳方向" t̂ 指绳在该点的单位切线（指向绳的终点）；"骑行方向" d̂ = ±t̂。ĥ = d̂ 的水平投影再归一化。H = 72 u。"R5" 指本地混合构建（S21 客户端 + S3 dedi + SDK），客户端和 dedi 不一致的地方单独注明。

---

### 5.15 挂上滑索：条件和选点

#### 原理

Apex 的滑索要**看着它按交互键**才挂得上，人从下面走过、碰到绳子都不会自动挂。好处是不会被意外"吸"上去；代价是玩家得把准星对向绳子。为了不难为玩家，判定很宽：绳子任意位置都能挂（不止两端），地上和空中都能挂，视线和绳上那一点的夹角在约 34° 以内就算"看着"。

去哪一头由**视线**决定：看向哪边就往哪边滑，挂上以后不能改。唯一的例外在端点附近：如果抓点离视线那一头太近（90 u 以内），R5 不拒绝，而是**反过来往另一头滑**，免得一挂上就被甩下来。

这是"地板低"（DESIGN-PHILOSOPHY P4）的一个例子：宽松的视锥、任意位置、空中可挂，让普通玩家容易上绳；高手用空中挂（Mid Air Interact）和重抓做身法。

#### 规则和公式

每条按下交互键（按下沿）的命令，按下面的顺序判断；任一步失败就不挂，这条命令照常移动：

1. **只有按键才挂**：碰到、穿过绳子都不挂 [实测，A3 z0_nouse 0 / 5]。
2. **空中可以挂** [实测，ZA1 65 / 65，客户端和 dedi 一致]，但受重抓限制（5.17：脱离后 0.35 s 的空中锁定、3 次的次数）。
3. **搜索原点** P = 原点 + (0, 0, `findRaise`)；蹲着或滑铲中用 `crouchFindRaise`。视线 e = 三维视角方向（含俯仰）。
4. **候选绳**：绳上离 P 最近的点在 `collectorRadius` 以内 [实测拟合：115.6 u 挂上、128.0 u 挂不上]。
5. **抓点 Q**：在候选绳上、离 P 不超过 `findRadius` 的那些点里，取和视线夹角 ∠(e, Q − P) **最小**的那一点。视线平行于绳子时这一点落在 130 u 的球面上（俯仰 0 时 126.83 u 前方）。竖直绳另算（5.22）。
6. **视锥**：最小夹角 ≤ `coneHalfAngle` 才挂。几根绳都合格时取夹角最小的那根 [设计：R5 没测过多根绳]。
7. **方向**：sign(e · t̂) > 0 往绳的终点滑，≤ 0（含正好垂直）往起点滑；斜绳一样（往下看就往下滑）。离垂直 5° 就会翻过来。滑行中方向固定，转身也不变 [实测，ZA1 全部挂上的样本]。
8. **端点区**：如果抓点到"要滑去的那一头"的路程 ≤ `endZone`，方向反过来 [实测，ZA1：抓点离端点 50 / 70 u 反向，110 u 不反向、滑 0.19 s 进入 90 u 的提前脱离区，以 600 u/s 甩出]。竖直绳没有端点区。
9. 以上都通过：挂上（5.16），花掉一次次数（5.17）。

由这些规则推出来的、玩家能感觉到的结果（都是 R5 实测，Unity 一致，除非注明）：

- 站在地上，绳高（离地）100、130 u 都能挂；170 u 只有抬头看才行；200、240 u 永远挂不上（够不着）[实测]。HSD 练习地图的地图绳就是 130 u。
- 站在绳子侧面 40 / 80 u：要抬头看着绳子才行，平视横穿过去不行；侧面 120 u 永远不行 [实测]。
- **80 u 高的绳 R5 0 / 10 挂不上，原因不明；HSD 能挂**（P 在绳上方 8 u）。HSD 地图上没有这么低的绳。
- 蹲着 / 滑铲中平视挂不上（R5 0 / 5），抬头 45° 能挂（5 / 5）。原因 R5 不明；HSD 用"搜索原点降到 +50"来复现 [推断：蹲姿眼高低 22 u；≤ 约 58 的值都能复现]。

**Fun 配置的不同** [设计]：端点区不反向而是**拒绝**（`refuseMountAtEnd`，事件 `ZIP_REFUSED_END`，M8-A 的做法：不让"从静止被甩出 600 u/s"）；空中挂上按**动量**方向滑而不是视线方向（`airRideWithMomentum`）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 搜索原点高度 `findRaise` | 1.829 m | 72 u | 1.000 H | — | [数据] SDK `ZE_MOUNT_SEARCH_EYE_RAISE`；[实测] 抓点残差 ≤ 0.1 u |
| 蹲着 / 滑铲的搜索原点高度 `crouchFindRaise` | 1.270 m | HSD 设计值 50 u | 0.694 H | ≤ 约 58 u 都能复现 R5 | [推断] R5 原因不明 |
| 候选绳距离 `collectorRadius` | 3.048 m | 120 u | 1.667 H | 115.6 – 128.0 u | [实测] ZA1；SDK 注释"collector radius 120" |
| 抓点最远距离 `findRadius` | 3.302 m | 130 u | 1.806 H | — | [实测] A3 拟合，抓点全部落在 ≤ 130.00 u |
| 视锥半角 `coneHalfAngle` | — | 34°（HSD 取在区间内） | — | R5 33.2° < θ < 35.9°（M6 较宽的区间 27.0 – 40.7°） | [实测] ZA1 198 次挂上 / 65 次拒绝 |
| 端点区 `endZone` | 2.286 m | 90 u（HSD 取在区间内） | 1.250 H | R5 70 < z < 110 u | [实测] ZA1 15 次 |
| 站着能挂的最高绳（离地） | 4.318 m | 170 u（要抬头） | 2.361 H | 170 能、200 不能 | [实测] ZA1 |
| 站着挂不上的绳（离地） | 5.080 m / 6.096 m | 200 / 240 u | 2.778 / 3.333 H | — | [实测] ZA1 |
| 侧面最远 | 3.048 m | 120 u 永远不行；40 / 80 u 要抬头看 | 1.667 H | — | [实测] ZA1 5 次一格 |
| 交互键位 | — | IN_USE = 0x20 | — | — | [实测] A3 |

#### 实现模板

```
// 单位：u、s。Evaluate 没有副作用：按键挂绳和 HUD 提示都调用它
Evaluate(body, view, now):
    if not body.grounded and not airMount:                    -> refuse AIR        // Reference: airMount = true
    if not body.grounded and now - detachTime < airRemountLockout: -> refuse LOCKOUT  // 5.17
    if budgetLeft <= 0:                                        -> refuse BUDGET     // 5.17
    e = viewDir3D(yaw, pitch)
    P = body.pos + up * (crouchedOrSliding ? crouchFindRaise : findRaise)
    best = none
    for rope in activeRopes:
        if nearestDistance(rope, P) > collectorRadius: continue
        (ang, s, Q) = rope.vertical ? verticalFind(...) : minAngleOnSphere(rope, P, e, findRadius)
        if ang < best.ang: best = (rope, ang, s, Q)
    if best is none or best.ang > coneHalfAngle:              -> refuse NO_ROPE
    if rope.vertical:                                          -> 5.22
    dir = dot(e, tangentAt(s)) > 0 ? +1 : -1                   // 0 算往起点
    if endZoneReverse and remainingTowards(s, dir) <= endZone: dir = -dir
    if refuseMountAtEnd and remainingTowards(s, dir) <= stopShort: -> refuse END   // Fun
    return (rope, s, Q, dir)
```

求最小夹角点：每段绳和以 P 为心、半径 `findRadius` 的球求交，得到段内可用区间 [t0, t1]；夹角最小点只可能在 t0、t1，或区间内部的驻点（对 cos∠ 求导为 0 的那个 t），三者比一下即可。不要用逐点采样，否则残差会超过 R5 的 0.1 u。

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.Evaluate`、`Find`（两个重载）、`SearchRaise`、`AtEnd`、`NearestDistance`、`TryMount`；参数 `ZiplineParams`（`findRaise`、`findRadius`、`collectorRadius`、`crouchFindRaise`、`coneHalfAngle`、`endZoneReverse`、`endZone`、`refuseMountAtEnd`、`airMount`、`airRideWithMomentum`、`autoAttach`，全部 [u]）。Reference = `ZiplineParams.R5Reference()`（经 `AdvancedMovementParams.zipline`），Fun = `ZiplineParams.Fun()`（`MovementConfigs.Fun`）。绳子是 `U:…/World/WorldGeometry.cs` 的 `Rail`（折线 `points`，`IsVertical`，`active`）。`Rail.attachRadius` 48 是 M6 留下的字段，滑索不读它。

#### 验收

- `A3Zipline.FindRuleMinimumAngleWithinRadiusAndCone`：平视平行于绳时抓点在 130 u 球面上；超出范围返回 +∞。
- `A3Zipline.NoAutoAttachAndTheReferenceAirMount`：走过绳下不挂；Reference 空中按键挂上；视锥外、130 u 外 `ZIP_NO_ROPE`。
- `ZiplineM9ATests.MidRopeStandingMountsAnywhereAlongTheRope`（7 个位置）、`ConeBracketMatchesTheR5Bracket`、`CollectorReachIs120FromTheSearchOrigin`（115.6 挂上、128.0 不挂）、`RopeHeightsAboveTheFloor`、`BesideTheRopeTheViewMustBeOnTheRope`、`RideDirectionFollowsTheView`、`TheDirectionIsFixedForTheRide`、`EndZoneReversesInsteadOfRefusing`（50 / 70 反向，110 不反向）、`MidAirInteractGrid`（9 格）、`CrouchedLevelViewIsRefusedLookingUpMounts`、`EvaluateIsSideEffectFreeAndMatchesTheUsePress`（300 个随机情形）。
- Fun：`ZiplineM8Tests.AMountInsideTheEndZoneIsRefusedInsteadOfLaunchingAt600`。
- 对照数据：A3 §1 抓点表（off0 12.679° 对规则 12.682°，off40 22.074°，z6_up 27.038°）；ZA1 263 次站立按键（125 次站立挂上，抓点残差 ≤ 1.6 u；全部 408 次 ≤ 8.1 u）、视锥 33.18° 挂上 / 35.94° 拒绝、高度表、侧面表、端点 50 / 70 / 110 u。
- 合格线：抓点和 R5 差 ≤ 1.6 u（站立）；视锥 33.18° 必须挂上、35.94° 必须拒绝；候选距离 115.6 挂、128.0 不挂；高度 100 / 130 平视挂、170 抬头挂、200 / 240 不挂；方向规则在 ZA1 全部样本上一致。
- 已知不一致：80 u 高的绳 R5 挂不上、HSD 能挂（见 `_notes/hb-ch05.md` 缺口）。

#### 出处

- A3 §1、§7：只按键挂、Find 规则（P = 原点 + 72，130 u 内最小夹角）、M6 视锥区间 27.0 – 40.7°、IN_USE 0x20。main
- ZA1 TL;DR、"Model for Unity"：任意位置可挂、120 u 候选距离、视锥 33.2 – 35.9°、高度和侧面、方向规则、端点区反向、空中 65 / 65、蹲姿平视 0 / 5。main
- M9AU §1 – §3：Reference 原来拒绝空中挂（M6 的错规则）、M8-A 的端点拒绝，M9-A 改成 R5；Fun 保留的设计项。main
- M8A §4 缺陷 1：端点区拒绝（Fun 现在的规则）的来由。main
- TL §5.2：wiki 的"看着绳子、地面 35° / 空中 90°"、"看哪边去哪边"、"靠近杆子会被推离"。main
- [数据] SDK `ZE_MOUNT_SEARCH_EYE_RAISE` 72、"collector radius 120"（SDK 注释，A3 §1、ZA1 引用）；SDK 钩子 `Zipline_Use`（`zipline_disconnect.cpp`，NP2 §4）。挂绳的原生判定函数地址没读。

---

### 5.16 挂上那一下：吸附、入绳速度、视角

#### 原理

挂上那一刻，人不会瞬移到绳子下面，而是先被往上提一点，然后在约 0.25 s 内平滑地"荡"到吊挂位置（绳下 80 u）。这样画面连续，也解释了为什么 Apex 挂绳有一点"被拽过去"的感觉。

**原来的速度不丢**：冲刺、滑铲、被钩爪拉着上绳，沿绳方向的那部分速度会保留下来当作起步速度，在挂上后的头 0.5 s 里作为"保底"——如果正常起步曲线还没追上它，就按它走。横穿绳子的那部分和竖直速度丢掉。这对应 P3"动量是玩家的资产"：上绳不清零动量，只按明确的规则（投影到绳上）换算。

挂上后的 0.5 s 里，视角被拉向骑行方向，玩家转不动视角；0.5 s 以后可以随便看，但方向不变。

#### 规则和公式

1. **挂上那条命令**（地面按键挂）：原点 z += `mountLift`，水平不动；这条命令的速度记为 0 [实测，95 / 95，标准差 0]。**空中按键挂**：HSD 不抬（`airMountLift` = 0）[设计：R5 只量过地面挂；抬 22 u 会让"跳离—再挂"每次叠高 22 u，M8-A 发现]。**钩爪交接**：不动 [实测]。
2. **吸附到吊挂线**（第 k 条命令，k = 挂上以后的命令数）：

   pos_k = p0 + b(k) · (ref_k − p0)，ref_k = 绳上点(s_k) − (0, 0, `hangBelow`)

   p0 = 挂上那条命令后的原点。b(k) 用实测表（下表抽样；全表 46 项见 Unity `blendTable`），k ≥ 45 以后在 15 条命令内线性到 1。不用解析曲线：实测表位置 RMS 0.51 u，smoothstep（T = 0.148 s）3.57 u、临界阻尼（ω 25.9 /s）4.10 u、指数 10.7 u（没选，留档）。

   | k（条命令） | 4 | 8 | 12 | 16 | 20 | 24 | 30 | 40 |
   |---|---|---|---|---|---|---|---|---|
   | 时间 | 0.033 s | 0.067 s | 0.100 s | 0.133 s | 0.167 s | 0.200 s | 0.250 s | 0.333 s |
   | b(k) | 0.157 | 0.465 | 0.746 | 0.907 | 0.969 | 0.985 | 0.990 | 0.995 |

3. **吊挂位置**：绳下 80 u，正下方 [实测：dedi 80.00；客户端 80.17、侧偏 −0.23，只在客户端，和手感无关，不学]。
4. **入绳速度**（"保底"）：
   - 按键挂（地面或空中）：v_entry = max(0, v_pre · d̂) [实测：沿绳冲刺 → 起步 299.7，滑铲 → 395]。
   - 钩爪交接：v_entry = v_pre · d̂ + 400 · dt [实测拟合，10 / 10，残差 0.035 u/s]。
   - 挂上后的 0.5 s（"挂上状态"，`mountStateTime`）里：v = min(max(v_entry, v_rest), 速度上限)，v_rest 是从静止挂上的曲线（5.18）。0.5 s 以后从当时的 v 继续按 5.18 加速。
   - 入绳速度超过绳的上限时直接降到上限（HSD 850 → 600）[推断：R5 只测到 395]。
   - 横穿绳子的分量、竖直分量丢掉。
   - 旧版（M6-A）地面挂从 0 起步，开关 `groundEntrySpeed = false`。
5. **视角**（输入规则，不是镜头效果）：挂上状态 0.5 s 内，偏航和俯仰被拉向骑行方向（22 条命令到 90 %），偏航输入被忽略；从第 61 条命令（0.5 s）起视角自由。竖直绳一开始就自由 [实测，A3 §9.3]。滑索上的镜头效果见第 07 章。
6. **钩爪钩到绳上**（交接，GZ）：钩爪在拉、钩点在绳上（钩点离绳 ≤ `hookRadius`）时，原点离钩点 ≤ `grappleMountDistance` 的那条命令自动挂上，不用按键；抓点 = 钩点；方向按动量沿绳的符号（为 0 时看视线）；照样花一次次数；钩爪结束。R5 的真实触发条件不明（几何上早 38 条命令就能挂，但总是在 135.4 – 137.9 u 时才挂），136 u 只来自一种几何。端点区内的交接 HSD 拒绝 [设计，没测过]。交接后**不能** Super Jump（5.20）。钩爪的其他规则见本章钩爪一节。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 地面挂上时上抬 `mountLift` | 0.559 m | 22 u | 0.306 H | 实测 22.000，sd 0 | [实测] A3 95 / 95 |
| 空中挂上时上抬 `airMountLift` | 0 m | HSD 设计值 0 u | 0 H | R5 没测 | [设计] M8-A |
| 吊挂深度 `hangBelow` | 2.032 m | 80 u | 1.111 H | dedi 80.00，客户端 80.17 | [实测] |
| 吸附到 99 %（b = 0.990） | — | 0.25 s（30 条命令） | — | 每次之间 b 差 ≤ 0.08 | [实测] A3 90 次 |
| 挂上状态时长 `mountStateTime` | — | 0.5 s | — | 实测切换在 t = 0.508 s（第 61 条） | [数据] setfile `mountZiplineTime` 0.5（N4A）；[实测] |
| 视角拉到 90 % | — | 0.183 s（22 条命令） | — | — | [实测] A3 |
| 冲刺挂上的起步速度 | 7.612 m/s | 299.7 u/s | 4.162 H/s | — | [实测] ZA1 5 次 |
| 滑铲挂上的起步速度 | 10.03 m/s | 395 u/s | 5.486 H/s | — | [实测] ZA1 5 次 |
| 钩爪交接加的一步 `grappleEntryAccel` × dt | 0.085 m/s | 400 u/s² × 1/120 s = 3.333 u/s | 0.046 H/s | 实测 3.346 ± 0.035 | [实测] GZ 10 次 |
| 钩爪交接距离 `grappleMountDistance` | 3.454 m | 136 u | 1.889 H | 实测 135.4 – 137.9 u，一种几何 | [实测] GZ；原生触发不明 |
| 钩点算"在绳上"的半径 `hookRadius` | 0.254 m | HSD 设计值 10 u | 0.139 H | 未知 | [设计] |

#### 实现模板

```
// 单位：u、s
Mount(choice, grapple):
    rail, s, dir = choice
    budgetLeft -= 1
    d = tangentAt(s) * dir
    along0 = dot(vel, d)
    vEntry = grapple ? max(0, along0) + grappleEntryAccel*dt
                     : (grounded and not groundEntrySpeed) ? 0 : max(0, along0)
    v      = grapple ? vEntry : 0
    p0     = grapple ? pos : pos + up*(grounded ? mountLift : airMountLift)
    setKinematic(p0, d*v)                // 这条命令不再走普通移动
    mountTime = now; superJumpArmed = false; fromGround = grounded; grappleMount = grapple
    preMountVel = vel                    // 5.19 carry 用

eachRideCommand:                         // 5.18 的速度更新之后
    ref = ropePoint(s) - up*hangBelow
    pos = p0 + blend(now - mountTime + dt) * (ref - p0)   // blend 按 120 /s 查表
    viewLocked = not vertical and (now - mountTime) < mountStateTime
```

离散化要注意：吸附表是按 120 Hz 命令量的，Unity 用时间 × 120 查表并线性插值，所以别的帧率下也能用；但 R5 没在别的帧率测过。

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.Mount`、`Blend`、`SetView`、`BeforeMove`（钩爪交接一段）、`HookOnRail`、`GrappleSign`；参数 `ZiplineParams.mountLift`、`airMountLift`、`hangBelow`、`blendTable`、`blendTableRate`、`groundEntrySpeed`、`viewPull`、`viewPull90`、`grappleMountDistance`、`grappleEntryAccel`（[u]）。"位置由能力直接给"走电机的 kinematic 接口：`U:…/R5MotorV2.cs`，`R5MotorV2.KinematicCommand`（这条命令不做重力、加速、落地检查；滑铲结束、冲刺关掉；世界仍然扫一遍碰撞）。视角拉动由游戏层读 `ZiplineAbility.viewLocked`、`viewYaw`、`viewPitch` 执行。

#### 验收

- `A3Zipline.MountLiftsTwentyTwoAndBlendsOntoTheHangLine`：挂上那条命令 z = +22（误差 1e-9），水平不动、速度 0；吸附后在绳下 80 u（误差 0.1）。
- `A3Zipline.ViewIsPulledToTheRopeDuringTheMountState`。
- `ZiplineM9ATests.GroundEntrySpeedIsTheMountStateFloor`：入绳 299.7 → 0.5 s 303.33、1.0 s 503.33；入绳 395 → 0.5 s 395、1.0 s 595。
- `A3Zipline.GrappleOnARopeHandsOverToAZipline`；`ZiplineM8Tests.GrappleOntoTheRopeRidesAndTheJumpOffKeepsMomentumAndControl`。
- `ZiplineM8Tests.AirMountInBothConfigsAndFunKeepsTheMomentumWithoutALift`（空中挂不抬，入绳速度 = 沿绳动量 250）、`AHighSpeedMountIsCappedAtTheRopeSpeedAndFromBehindRidesWithTheMomentum`。
- 对照数据：A3 §1 吸附表和 `params.json` → `attach.blend_table_b_of_k`；GZ §2 第 7、8 条（入绳 293.8 – 297.1，残差 ≤ 0.30 u/s，2 / 10 次在状态切换处差 3.3 u/s）；ZA1 冲刺 / 滑铲入绳（R5 1.0 s 时 503.6 / 597.3）。
- 合格线：上抬 22 u 精确；吸附位置和 R5 表 RMS ≤ 0.6 u；入绳速度保底规则下 1.0 s 时速度和 R5 差 ≤ 3 u/s（HSD 503.33 / 595.0 对 R5 503.6 / 597.3）。

#### 出处

- A3 §1（上抬、吸附表和三种被否决的曲线、吊挂深度、视角拉动）、§9.3（视角 0.5 s 后自由）。main
- GZ §2、§3：钩爪交接的时刻、抓点、入绳速度 v·d̂ + 400·dt、保底规则。main
- ZA1 "Entry speed"：冲刺 299.7、滑铲 395 保留。main
- M8A §4 缺陷 2：空中挂不抬的理由。main
- M9AU §2：`groundEntrySpeed`、旧版从静止起步。main
- N4A census：`mountZiplineTime` 0.5。main
- 原生挂绳、吸附函数地址没读；SDK `[ZIPRAIL-USE]` 诊断行里的 `mountStart` 316.39 和 +22 一致（A3 §1）。

---

### 5.17 重新挂上：空中锁定和次数

#### 原理

Apex 早期可以无限次"挂上—跳下—再挂上"，后来加了两道限制（TL：wiki 记的 2020 年 6 月补丁）：

1. 刚离开绳子的一小会儿（约 0.35 s）**在空中**不能再挂；落地以后马上能挂。
2. 不落地的话一共只能挂 3 次（第一次 + 2 次空中重抓），落地或翻越上台面就恢复。

这样空中重抓仍然是一门技巧，但不能靠连按刷高度或刷距离。这条对应 P4"技巧窗口按时间算"。

#### 规则和公式

1. **空中锁定**：不在地面时，距离上一次**离开绳子**（任何一种退出：跳离、蹲下、到端、被打断、绳被移除……；Super Jump 不算离开，它发生在离开以后）不到 `airRemountLockout` 的按键挂绳被拒绝（`ZIP_REFUSED_LOCKOUT`）。在地面上没有锁定 [实测：地面跳离 / 蹲下后落地再挂 10 / 10 立即成功]。
2. **次数**：`budget` = 3。每次挂上（包括钩爪交接）减 1；为 0 时拒绝（`ZIP_REFUSED_BUDGET`）。
3. **恢复**：不在绳上时，着地或完成一次翻越 → 恢复到 3；离开绳子后每 `budgetRegen` 秒 +1（直到 3）[数据：SDK / wiki；R5 没测过这一条]。
4. 骑行中再按交互键什么也不做。
5. Fun 配置：没有空中锁定（`airRemountLockout` = 0），次数一样 [设计]。

R5 实测：跳离后空中再按，≤ 0.334 s 拒绝、0.334 – 0.37 s 起能挂；蹲下后 0.359 s 拒绝、0.403 s 能挂；和高度无关。拒绝发生在客户端调用 `Zipline_Use` **之前**（两边都没有诊断行），是 S21 客户端的门。setfile 有 `useZiplineCooldown` 0.4 [数据]。HSD 取 0.35 落在区间里；所以蹲下后 0.35 – 0.36 s 这一小段 HSD 能挂、R5 不能。

次数的来源有两个候选，这个构建分不出来：S21 客户端的冷却阶梯（每次挂上后客户端冷却 0.1 → 0.2 → 1.0 s，后面 3.0 / 5.0 s），或 SDK 里"最新 Apex"的 3 次计数。两者都在第 3 次空中重抓时拒绝。HSD 用计数。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 空中锁定 `airRemountLockout` | — | HSD 取 0.35 s | — | R5 跳离 0.33 – 0.37 s，蹲下 0.36 – 0.40 s；setfile 0.4 s | [实测] ZA1 95 次；[数据] `useZiplineCooldown` 0.4（N4A） |
| 不落地最多挂几次 `budget` | — | 3 次 | — | 实测：地面挂 + 2 次空中，第 3 次空中拒绝 | [实测] ZA1 10 次；[数据] SDK `left=3` |
| 每过多久恢复一次 `budgetRegen` | — | 3.0 s | — | 未测 | [数据] SDK / wiki，R5 没测 |
| 客户端冷却阶梯（另一种解释） | — | 0.1 / 0.2 / 1.0 s（之后 3.0 / 5.0 s） | — | — | [实测] 客户端诊断 `cd=`（A3 §9.4、ZA1） |

#### 实现模板

```
// 单位：s。每条命令开头（不在绳上时）
if grounded or mantleCompletedThisCommand: budgetLeft = budget; budgetNext = ∞
elif budgetLeft < budget:
    if budgetNext == ∞: budgetNext = now + budgetRegen
    if now >= budgetNext: budgetLeft += 1; budgetNext = budgetLeft < budget ? budgetNext + budgetRegen : ∞
// 挂绳判断里（5.15 第 2 步）
if not grounded and now - detachTime < airRemountLockout: refuse
// 每种退出都写 detachTime = now
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.BeforeMove`（次数恢复一段，读 `ClimbAbility.mantles` 判断翻越）、`Evaluate`（锁定和次数两步）、`Detach`（写 `detachTime`）；参数 `ZiplineParams.airRemountLockout`、`budget`、`budgetRegen`。

#### 验收

- `ZiplineM9ATests.AirReMountLockout`：跳离后 0.30 s 拒绝、0.37 s 挂上；蹲下后 0.30 s 拒绝、0.41 s 挂上。
- `ZiplineM9ATests.GroundReMountIsImmediateAndFunHasNoLockout`、`ReGrabBudgetGroundPlusTwoAir`（挂、挂、拒绝，落地后能挂）。
- `A3Zipline.BudgetThreeAirMountsResetOnLanding`；`ZiplineM8Tests.QuickRemountAfterAJumpOffAndTheBudget`、`TheReMountBudgetRegeneratesOffTheRope`。
- 对照数据：ZA1 "Re-mount mid-rope"、"Re-grab budget" 两行（95 次重按、10 次次数链）。
- 合格线：跳离 0.30 s 必须拒绝、0.37 s 必须挂上；蹲下 0.30 拒绝、0.41 挂上；地面立即；不落地第 4 次按键（第 3 次空中重抓）拒绝。

#### 出处

- ZA1 TL;DR "Re-mount"、"Re-grab budget"、Open questions 2、4：锁定区间、客户端门、两种次数来源。main
- A3 §6、§9.4：SDK 次数 `consume left=2` / `reset ground left=3`、客户端冷却阶梯。main
- M9AU §2、§10、§11：HSD 取 0.35 s 和 Fun 0 的理由。main
- TL §5.2：wiki 的"3 次、落地或翻越恢复、3 s 一次"、`useZiplineCooldown 0.4`、"无限连按"被移除。main
- N4A census：`useZiplineCooldown` 0.4。main
- [数据] SDK `bridge_zip_disc`（`zipline_disconnect.cpp`，NP2 §4）。客户端门所在的原生函数没找。

---

### 5.18 滑行：速度、加速、上下坡、按键

#### 原理

挂上后速度有两段：前 0.5 s 加速快（从几乎静止到约 300 u/s），之后加速变慢，约 1.25 s 到 600 u/s 封顶。上坡绳和平绳完全一样快——**滑索不管坡度**，绳子是"传送带"，不是"滑梯"。这样关卡设计只需要关心绳子长度，不需要担心上坡绳拉不上去。

滑行中身体完全由绳子决定：方向键、交互键都不起作用，只能看（0.5 s 以后）、跳下、蹲下松手。

#### 规则和公式

v_rest 是"从静止挂上"的曲线，k = 挂上后的第几条骑行命令：

1. k = 1：v_rest = `firstRideSpeed`。
2. 挂上状态内（t < `mountStateTime`）：v_rest += `mountAccel` · dt。
3. 之后：v += `rideAccel` · dt。
4. 任何时候 v ≤ `speed`（地图绳 600 u/s）。
5. 挂上状态内 v = min(max(v_entry, v_rest), `speed`)（5.16 的保底）；之后从当时的 v 继续。
6. 位置：s += dir · v · dt，用**这条命令更新后**的速度（R5 拟合：同命令速度尾差 0.43 u，上一命令速度 1.69 u）。身体在吸附公式给的位置（5.16），速度报告为 d̂ · v。
7. **没有坡度项**：上坡绳（10.6°）的速度曲线和平绳逐命令相同 [实测]。**下坡绳没测过**。
8. 滑行中：跳跃按下 → 跳离（5.19）；下蹲按下 → 蹲下松手（5.19）；交互键忽略；方向键忽略；方向固定（5.15 第 7 条）。
9. 每条命令先判断退出（5.19、5.21），再更新速度和位置。

时间线（从静止挂上，120 Hz）：v(1) = 8.333，v(60) = 303.33（t = 0.5 s），之后每条命令 +3.333，第 149 条（t ≈ 1.243 s）到 600。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 第一条骑行命令的速度 `firstRideSpeed` | 0.212 m/s | 8.333 u/s | 0.116 H/s | 实测 8.33 | [实测] A3；= 1000 u/s² × 1/120 s，见 `_notes/hb-ch05.md` [推断] |
| 挂上状态的加速度 `mountAccel` | 15.24 m/s² | 600 u/s² | 8.333 H/s² | 每次标准差 ≤ 14 | [实测] A3（setfile 里没找到对应的键） |
| 之后的加速度 `rideAccel` | 10.16 m/s² | 400 u/s² | 5.556 H/s² | 每次标准差 ≤ 0.2 | [实测] A3；[数据] setfile `ziplineAcceleration` 400（N4A） |
| 状态切换时的速度 | 7.704 m/s | 303.0 – 303.3 u/s | 4.213 H/s | — | [实测] A3 |
| 速度上限 `speed`（`ziplineSpeed`） | 15.24 m/s | 600 u/s | 8.333 H/s | — | [数据] setfile；[实测] 1.243 – 1.257 s 到顶 |
| 到上限的时间（从静止） | — | 1.25 s | — | 1.243 – 1.257 s | [实测] [算] |
| 坡度对速度的影响 | — | 0（上坡 10.6°） | — | 下坡未测 | [实测] A3 Z2 |

#### 实现模板

```
// 单位：u、s。骑行中每条命令，在普通移动之前
Ride():
    k += 1
    if rope removed: exit ROPE_GONE (5.21)
    if jumpPressed:  JumpOff(); return        // 5.19
    if duckPressed:  CrouchOff(); return      // 5.19
    if |pos - expectedPos| > pathTolerance: exit BLOCKED (5.21)
    law = rope.ride ?? mapRopeLaw             // 5.24：滑索枪的绳有自己的数
    inMount = (now - mountTime) < law.mountStateTime + dt/2
    vRest = (k == 1) ? law.first : vRest + (inMount ? law.mountAccel : law.rideAccel)*dt
    v     = inMount ? max(vEntry, min(vRest, law.cap)) : v + law.rideAccel*dt
    v     = min(v, law.cap)
    sNew  = s + dir*v*dt
    检查到端 / 竖直绳顶（5.21、5.22）
    s = clamp(sNew, 0, L); 位置按 5.16 吸附; vel = d̂*v
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.Ride`；参数 `ZiplineParams.firstRideSpeed`、`mountAccel`、`rideAccel`、`mountStateTime`、`speed`（[u]）。参数表 `params.tsv` Z-01（`speed`）、Z-06（`rideAccel`）。滑行中能力"拥有"跳跃键（`ZiplineAbility.OwnsJump`），仲裁细节详见第 06 章。

#### 验收

- `A3Zipline.RideProfileMatchesTheMeasuredCurve`：v(1) = 8.333、v(60) = 8.333 + 59 · 600 · dt = 303.33、v(61) = v(60) + 400 · dt，1.25 s（± 0.01）到 600。
- `A3Zipline.UphillRopeSameProfileAndExitAlongTheRope`：上坡绳 0.5 s 时 303.333（± 0.001），没有坡度项。
- `ZiplineM8Tests.RapidUsePressesDuringTheRideAreIgnoredAndTheRideContinues`；`ZiplineM9ATests.TheDirectionIsFixedForTheRide`。
- 对照数据：A3 §2（90 次平绳 / 上坡 / 竖直绳的速度曲线）、`results.json`。
- 合格线：每条命令速度和上面的时间线差 < 0.01 u/s；1.243 – 1.257 s 内到 600。

#### 出处

- A3 §2、§7：两段加速、600 上限、上坡没有坡度项、位置用同命令速度。main
- GZ §2 第 8 条：保底规则下状态切换在第 59 – 60 条。main
- N4A census：`ziplineSpeed` 600、`ziplineAcceleration` 400、`mountZiplineTime` 0.5、`ziplineJumpOnAcceleration` 1000。main
- SV §3.4：`ziplineSpeed` 600、`pathGravityAcceleration` 400（Gibraltar / Valkyrie 会话）。main
- NP2 §2"加速"：原生"目标 = 速度倍率 × `ziplineSpeed`、加速 `ziplineAcceleration`"。main
- 滑行中原生 MOVE-TRACE 钩子不被调用（A3 §0），所以滑行数据来自客户端每帧记录；滑行的原生函数地址没读。

---

### 5.19 下滑索：跳离、蹲下松手、挂上马上跳（carry）

#### 原理

主动下绳有两种：**跳**和**蹲**。跳离给一个固定的向上速度（和普通起跳一样，跳 56 u 高），沿绳的水平速度最多保留 400 u/s——所以满速 600 的绳上跳下来会损失 200 u/s。蹲下松手一样保留最多 400，但不给向上的速度。这个 400 的上限让"在滑索上跳"成为一个有代价的选择，而不是白拿速度（P3：收走动量要有明确规则，这里规则就是"最多 400"）。

跳离的方向总是**沿绳子**（水平方向），不看视线。跳的那条命令身体不动，下一条命令开始才是普通空中移动。

一个小技巧（社区叫 carry）：挂上那一下马上（下一条命令）跳，保留的是**挂上前的速度**，而不是沿绳的速度——比如横穿绳子跑过去挂上再跳，会以原来的横向速度飞出去。

#### 规则和公式

1. **跳离**（骑行中跳跃按下沿，任何时刻，不需要地面）：

   v_out = ĥ · min(v, `jumpOffCap`) + ẑ · `jumpOffVz`

   ĥ = 骑行方向的水平投影（归一化）。没有下限：v = 0 时水平为 0 [实测]。这条命令位置不变，速度直接设为 v_out（竖直 289.828，**不**扣半步重力，和地面起跳不同）[实测：MT 后状态 = 诊断值]；下一条命令起是普通空中移动（重力、空中加速，第 03 章）。跳的那条命令上按着的方向键不起作用 [实测]。
2. **蹲下松手**（骑行中下蹲按下沿）：v_out = ĥ · min(v, 400)，竖直 0。位置不变。点按蹲后人是站姿（MT duck = 0）；一直按着蹲也不会在空中蹲到底、不会和 dedi 分歧 [实测 5 / 5]。HSD：按着蹲落地会直接进滑铲 [模型，M8-A；R5 没专门测]。
3. **carry**（只限按键挂上，不含钩爪交接）：跳离 / 蹲下发生在**第一条骑行命令**时，水平部分 = 挂上前的水平速度，长度封顶 400 [实测：横穿 285 u/s → (0, 285, 289.8)；封顶 400 来自 wiki，R5 只测到 285]。晚一条命令（第 2 条）就是沿绳 8.3 u/s。
4. **跳离以后**：
   - Reference **不开 lurch 窗口**（跳离后 3 条命令按 D，|Δv| = 4.18 u/s，就是普通空中加速）[实测]。Fun 开 [设计，`jumpOffIsLurchAnchor`]。
   - 没有 coyote 起跳、没有二段跳；唯一的例外是 5.20 的 Super Jump。"一次跳跃按下只给一个动作"的仲裁详见第 06 章。
   - 离开绳子：写 `detachTime`（5.17 锁定从这里算）。
5. **方向**：沿绳，不看视线 [实测：视线偏 −27° / −63° 时跳出的方向仍是 0.000°，10 / 10]。竖直绳例外（沿视线，5.22）；滑索枪的陡绳和斜绳例外（5.24）。
6. **地图斜绳 / 陡绳**：HSD 地图绳一律用水平投影 ĥ（60° 陡绳跳出水平 ≤ 400）。R5 只在平绳上量过跳离；wiki 说 > 45° 的绳可以朝任意方向跳——**地图陡绳 R5 没测**。

由规则推出的总速度：平绳满速跳离 √(400² + 289.8²) = 494 u/s（wiki ≈ 490）；蹲下 400（wiki ≈ 400）。wiki 写的"手动下绳最大 445 u/s"和 R5 的 400 不符，以 R5 为准。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 跳离 / 蹲下的水平速度上限 `jumpOffCap`（`ziplineJumpOffSpeed`） | 10.16 m/s | 400 u/s | 5.556 H/s | — | [数据] setfile 400（N4A）；[实测] 125 次跳离残差 0.000，乘速 0 – 600 共 10 档 |
| 跳离竖直速度 `jumpOffVz` | 7.362 m/s | 289.828 u/s | 4.025 H/s | — | [算] √(2 · 750 · 56)；[实测] 70 / 70 客户端 = dedi |
| 跳离衰减倍率 `ziplineJumpOffDampScale` | — | 1（×，不衰减） | — | — | [数据] N4A；Unity 没有这个参数（等于 1） |
| 平绳满速跳离的总速度 | 12.55 m/s | 494 u/s | 6.861 H/s | wiki ≈ 490 | [算] |
| carry 的保留速度（实测那次） | 7.239 m/s | 285 u/s | 3.958 H/s | 上限 400 只来自 wiki | [实测] ZA1 5 次 |
| carry 窗口 | — | 第 1 条骑行命令（0.008 s） | — | 第 2 条就不行 | [实测] ZA1 |
| 跳离后按方向键的 \|Δv\| | 0.107 m/s | 4.18 u/s（每条命令） | 0.058 H/s | 有 lurch 时远大于此 | [实测] ZA1 5 + 5 次 |

#### 实现模板

```
// 单位：u、s
ExitHorizontal():
    if carry (k == 1 and not grappleMount and firstCommandCarry):
        h = horizontal(preMountVel); return |h| > jumpOffCap ? h*jumpOffCap/|h| : h
    if rope.ride != null and not rope.vertical:              // 只有滑索枪的绳，5.24
        if rope.ride.steep:            return viewYawDir * min(v, jumpOffCap)
        if rope.ride.jumpOffAlongRope: return d̂(3D)    * min(v, jumpOffCap)
    h = rope.vertical ? viewYawDir : flatten(d̂)
    return h * min(v, jumpOffCap)

JumpOff():   vel = ExitHorizontal() + up*jumpOffVz; pos 不变; consumeJump()
             if jumpOffIsLurchAnchor: jumpTime = now          // Reference: false
             detach("JUMP"); superJumpArmed = fromGround and not grappleMount   // 5.20
CrouchOff(): vel = ExitHorizontal();             pos 不变; detach("CROUCH")
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.JumpOff`、`CrouchOff`、`ExitHorizontal`、`Horizontal`、`Carry`（属性）、`Detach`；参数 `ZiplineParams.jumpOffCap`、`jumpOffVz`、`firstCommandCarry`、`jumpOffIsLurchAnchor`（[u]）。参数表 Z-04、Z-05。

#### 验收

- `A3Zipline.JumpOffLaw`（k = 1 / 24 / 60 / 120 / 190）：v_x = min(v, 400)、v_y = 0、v_z = 289.828，位置不变，Reference 不当 lurch 起点。
- `A3Zipline.CrouchOffKeepsMin400AndNoVerticalSpeed`。
- `ZiplineM9ATests.CarryKeepsThePreMountVelocityOnTheFirstCommand`（含 400 封顶）、`JumpOffOpensNoLurchWindowInTheReference`（Reference 不 lurch，Fun lurch）。
- `ZiplineM8Tests.ASteepRopeRidesUpAndItsExitsStayCapped`（60° 地图绳跳出水平 ≤ 400）、`TransitionsWithSlideLurchDoubleJumpAndWallRun`。
- 对照数据：A3 §3、§9.1（125 次跳离，乘速 0、13、28、123、243、303、423、503、584、600）；ZA1 carry、lurch 两行。
- 合格线：跳离速度和公式差 < 0.01 u/s（R5 残差 0.000）；carry 第 1 条命令保留挂上前速度、第 2 条沿绳。

#### 出处

- A3 §3、§7、§9.1、§9.3：跳离 / 蹲下公式、没有下限、不看视线、跳的那条命令不动、按键无效、蹲下不分歧（§9.5）。main
- ZA1 TL;DR "Lurch after a jump-off"、"Carry (R-12)"。main
- NP2 §2、§5 Z-01：原生"沿绳速度 × `ziplineJumpOffDampScale`，大小 ≤ `ziplineJumpOffSpeed`，再加 √(2g·`jumpHeight`)"。main
- N4A：`ziplineJumpOffSpeed` 400、`ziplineJumpOffDampScale` 1（N4A-READBACK 第 22、36 行）。main
- TL §1、§5.2：wiki 的 zip jump ≈ 490、zip crouch ≈ 400、"> 45° 任意方向"、"445"（不符）。main
- M8A §4、M9AU §2：Fun 的 lurch 设计项、carry 的 400 封顶来源。main
- [反编译] 原生跳离函数没给地址（NP2 只写了规则）；SDK 钩子 `Zipline_JumpOff`（`zipline_disconnect.cpp`）。

---

### 5.20 Super Jump：跳离后再跳一次

#### 原理

从地上挂上绳、马上跳离、再在 0.2 s 内按一次跳，会**再叠一次完整的起跳**：竖直速度从约 283 变成约 564 u/s，能跳到跳离点上方约 218 u（普通跳 56 u）。社区叫 Super Jump，是 Apex 的经典身法。

最像的解释是：挂上那一下身体刚离开地面，"离地后还能起跳一小会儿"（coyote time）的窗口还没过，所以第二次按跳被当成一次地面起跳。窗口很短（约 0.2 s），属于"天花板高"的技巧（P4）。

#### 规则和公式

1. **前提**：这次挂上是从**地面**按键挂的（不是空中挂、不是钩爪交接），并且已经跳离（5.19）。HSD 在跳离时"上膛"。
2. **触发**：新的跳跃按下沿（两次按之间要松开 [实测：上升沿和下降沿在同一帧的那组 0 / 5]），离挂上的时刻 ≤ `superJumpWindow`，人在空中。
3. **效果**：和地面起跳一样的竖直冲量，水平不变：

   vz_post = vz_pre + V − 1.5 · g · dt，V = √(2 · g · `superJumpHeight`) = 289.828 u/s

   （半步重力的处理和第 03 章普通起跳相同。）
4. 落地、窗口过期、或用掉一次后"退膛"。
5. HSD 把 Super Jump 当成一次起跳：写 `jumpTime`，**会**打开 lurch 窗口 [推断：R5 没测 Super Jump 后的 lurch；ground-equivalent jump 的推论]。和二段跳、跑墙的先后详见第 06 章。

R5 窗口实测（两组数据）：
- M6：跳离在挂上后 1 – 6 条命令，第二次按在离地后 3 – 8 条命令：20 / 20 生效；≥ 63 条：0 / 40。
- M9：跳离在挂上的下一条命令，第二次按在跳离后 K 条：K = 12、18 各 5 / 5，K = 24 3 / 5，K = 30 0 / 5。按离挂上的时间算：K = 18 ≈ 0.158 s 全中，K = 24 ≈ 0.208 s 一半，K = 30 ≈ 0.258 s 全不中。

HSD 取 0.2 s（从挂上算），对应 K ≤ 23 生效、K ≥ 24 不生效，正好落在 R5 的边上。窗口从"离开地面"算还是从"挂上"算分不出来（地面挂两者是同一条命令）；`jump_graceperiod` 没读（第 03 章 B03-1）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 窗口 `superJumpWindow` | — | HSD 取 0.2 s（从挂上算） | — | R5 0.158 s 全中、0.208 s 3 / 5、0.258 s 0 / 5 | [实测] ZA1 25 次、A3 §9.2 20 次 |
| 叠加的起跳高度 `superJumpHeight` | 1.422 m | 56 u | 0.778 H | — | [数据] `jumpHeight` |
| 叠加的竖直速度 V | 7.362 m/s | 289.828 u/s | 4.025 H/s | 实测 dvz − 重力步 = 286.705（sd 0.005） | [算] [实测] |
| 叠加后的竖直速度 | 14.33 m/s | 约 564 u/s | 7.833 H/s | — | [实测] A3 §9.2 |
| 跳离点以上的顶点高度 | 5.537 m | 218 u | 3.028 H | 普通跳离 56 u | [实测] A3 §9.2 |
| 总速度（400 水平 + 564 竖直） | 17.55 m/s | 691 u/s | 9.597 H/s | wiki ≈ 690 | [算] |

#### 实现模板

```
// 单位：u、s。每条命令开头，不在绳上时
if grounded: superJumpArmed = false
if superJumpArmed:
    if now - mountTime > superJumpWindow: superJumpArmed = false
    elif jumpPressed:
        V = sqrt(2*g*superJumpHeight)
        launch vel = (vel.x, vel.y, vel.z + V - g*dt)     // 电机再扣半步，post = vz + V - 1.5 g dt
        jumpTime = now; consumeJump(); superJumpArmed = false
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.SuperJump`、`BeforeMove`（上膛 / 退膛一段）、`JumpOff`（`superJumpArmed = fromGround && !grappleMount`）；参数 `ZiplineParams.superJumpWindow`、`superJumpHeight`；起跳速度用 `R5MotorV2.JumpSpeed`。

#### 验收

- `A3Zipline.SuperJumpInsideTheWindowAndNotAfter`：vz = vz_pre + 289.828 − 1.5 · g · dt（误差 1e-9），水平不变，记为 lurch 起点；窗口外只有重力。
- `ZiplineM9ATests.SuperJumpSecondPressWindow`：K = 12 / 18 / 23 生效，24 / 30 不生效。
- `ZiplineM8Tests.ConsecutiveJumpsJumpOffSuperJumpAirJumpOneEffectEach`（仲裁，详见第 06 章）；`WallChainM8BTests.TheZiplineSuperJumpIsTooSlowToStartAWallRun`。
- 对照数据：A3 §9.2（20 次，残差均值 0.002、最大 0.007 u/s）；ZA1 "Super Jump mid-rope"（25 次）。
- 合格线：叠加速度和公式差 < 0.01 u/s；K ≤ 18 必须生效、K ≥ 30 必须不生效（K = 24 R5 是 3 / 5，HSD 不生效可以接受）。

#### 出处

- A3 §4（第一轮"没有 Super Jump"，已被 §9.2 推翻）、§9.2：存在、公式、窗口、两次按之间要松开。main
- ZA1 TL;DR "Super Jump mid-rope"：K 窗口。main
- M9AU §2、§11：HSD 0.2 s 落在 K 24 的边上。main
- 00-INVENTORY 03 章第 1 条 / 99-TODO B03-1：`jump_graceperiod` 没追。handbook/base
- 原生 Super Jump 的判断位置没读。

---

### 5.21 到端脱离和别的退出

#### 原理

绳子快到头时人会被自动甩出去，速度**固定是 600 u/s 沿绳方向**，不管滑得多快多慢——哪怕刚挂上、几乎静止，到端也以 600 甩出（所以 Fun 配置干脆不让在端点区挂）。甩出点不在绳的最末端，而是提前约 90 u，免得撞上绳子尽头的杆子。

除此之外，人还可能被"打断"下绳：在绳上放钩爪、进传送门、被 Vantage 的跳跃带走、被别的东西挤离绳子、绳子本身被删掉。HSD 的统一原则是：**每一种退出都给一个确定的速度**，不会卡在绳上。

#### 规则和公式

1. **到端（地图平绳 / 斜绳）**：骑行一步以后，如果 剩余路程 − v · dt < `stopShort`，就在这条命令的位置脱离：

   v_out = d̂_end · clamp(v, `speed`, `detachSpeed`) = d̂_end · 600（因为两者都是 600）

   d̂_end = 骑行方向（三维，斜绳带竖直分量）。下一条命令起是普通空中移动。脱离后的位置离端点 90.1 – 94.8 u。
   `stopShort` 90 = 绳的 `autoDetach` 100 − 眼高和碰撞体差 10（SDK `ZIP-ALPHA`）。
2. **竖直绳顶部**：见 5.22（没有提前脱离区，到顶 + 沿视线 400 推出）。
3. **跳离 / 蹲下**：5.19。**Super Jump** 不是退出（已经离绳）。
4. **被挤离绳子**（HSD 设计）：绳子不是实体，身体照常扫碰撞；如果这条命令开始时身体离预期位置 > `pathTolerance`（被墙或别的东西推开），以当时的骑行速度 d̂ · v 脱离，事件 `ZIP_BLOCKED` [设计：R5 没测过绳穿墙 / 骑进墙]。
5. **被别的能力打断**（`Interrupt`）：保持这条命令的身体速度脱离，事件 `ZIP_INTERRUPT_<原因>`。测试里覆盖到的打断：在绳上发射钩爪（钩爪接着起拉）、骑进 Wraith 传送门（出口静止）、Vantage 的 JetDrive 起飞。反过来，挂上滑索会结束钩爪拉动和 Fun 的飞行。谁能打断谁详见第 06 章。
6. **绳被删掉**（只有滑索枪的绳会，5.23）：以骑行速度 d̂ · v 脱离，事件 `ZIP_ROPE_GONE`。
7. **每一种退出**都写 `detachTime`（5.17 的空中锁定从这里算）。R5 原生里到端、跳下、蹲下、被打断都走同一个下绳函数，下滑索的镜头 kick（`zip_detach`）由它触发，见第 07 章。
8. 竖直速度上限 `maxVerticalDetachSpeed` 1500 u/s：只在竖直绳顶部用（min(v, 1500)）；绳速最多 600 / 1000，所以现在永远碰不到。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 到端脱离速度 `detachSpeed`（`ziplineDetachSpeed`） | 15.24 m/s | 600 u/s | 8.333 H/s | 下限也是 `ziplineSpeed` 600，所以恒为 600 | [数据] setfile；[实测] 残差 0（平绳 (600, 0, 0)、上坡 (589.723, 0, 110.573)） |
| 提前脱离距离 `stopShort` | 2.286 m | 90 u | 1.250 H | 脱离后离端点 90.1 – 94.8 u | [数据] SDK `stopShort = 90`；[实测] 95 / 95 |
| 绳的自动脱离距离 `autoDetach` | 2.540 m | 100 u | 1.389 H | 竖直绳 0 | [数据] `CreateZipline(..., 100)`、脚本 `ZiplineAutoDetachDistance 100` |
| 竖直脱离速度上限 `maxVerticalDetachSpeed` | 38.10 m/s | 1500 u/s | 20.83 H/s | 现在碰不到 | [数据] setfile |
| 被挤离的容差 `pathTolerance` | 0.203 m | HSD 设计值 8 u | 0.111 H | 未知 | [设计] |
| 端点区内静止挂上被甩出的时间 | — | 0.19 s（抓点离端 110 u） | — | — | [实测] ZA1 |

#### 实现模板

```
// 单位：u、s。Ride() 里，速度更新之后（5.18）
remaining = (dir > 0) ? L - sNew : sNew
if not vertical and remaining - v*dt < stopShort:
    vOut = rope.ride ? rope.ride.EndExit(d̂, v)           // 5.24
                     : d̂ * clamp(v, speed, detachSpeed)  // 地图绳 = d̂ * 600
    pos  = 本条命令的吸附位置
    detach("END", vOut)
Interrupt(reason): kinematic = false; detach("INTERRUPT_" + reason, vel)   // 保持身体当时的速度
detach(kind, vOut): phase = None; lastExit = kind; detachTime = now
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.Ride`（到端、`BLOCKED`、`ROPE_GONE` 三段）、`Interrupt`、`Detach`；参数 `ZiplineParams.detachSpeed`、`speed`、`maxVerticalDetachSpeed`、`pathTolerance`；`Rail.stopShort`（`U:…/World/WorldGeometry.cs`，默认 90）。电机在 kinematic 退出离地面很近时直接落地（`R5MotorV2.KinematicCommand` 里"不会停在地板以下"一段）。参数表 Z-02、Z-03。

#### 验收

- `A3Zipline.AutoDetachNinetyBeforeTheEndAt600`：脱离后剩余 ∈ [90, 90 + 600 · dt)，速度 (600, 0, 0)，下一条命令 vz = −g · dt。
- `A3Zipline.UphillRopeSameProfileAndExitAlongTheRope`：上坡绳出口 600 · d̂（三维）。
- `ZiplineGunM10BTests.ARopeRemovedWhileRiddenLetsTheRiderGoWithTheRideVelocity`；`RiftM10WTests.AZiplineRideIntoAPortalEndsTheRide`；`JetDriveM9CTests.ALiftOffFromAZiplineEndsTheRide`；`ZiplineGunM10BTests.AGrappleFromAGunRopeEndsTheRide`；反方向（挂绳结束别的状态）`A3Zipline.UseMountDuringAGrapplePullEndsTheGrapple`、`A3Zipline.FlightEndsOnAMount`；`A3Zipline.RandomPlayHasNoStuckStates`；`ZiplineM9ATests.RandomZiplinePlayKeepsTheRopeRules`（随机测试：不会卡在绳上 ≤ 12 s、出口 ≤ 600 / 400、不进实体）。
- 对照数据：A3 §2 出口表（Z1 / Z2 / Z3，客户端 = dedi）、ZA1 端点 110 u 的 600 甩出。
- 合格线：到端速度 600 精确（R5 残差 0.0003）；脱离位置离端点 90 – 95 u；任何退出后 ≤ 1 条命令回到普通移动。

#### 出处

- A3 §2、§7：到端规则、`stopShort` 90、客户端 = dedi 的命令号（95 / 95）、0.17 u 的吊挂差导致 2 次晚一条命令落地。main
- NP2 §2、§5 Z-02：原生 clamp(v·d, 600, 600)。main
- ZA1 TL;DR "Ends"：端点附近静止挂上 0.19 s 后 600 甩出。main
- M8A §4 缺陷 1、M9AU §3：Fun 的端点拒绝。main
- M10BU §1：绳被删时骑手放手（`ZIP_ROPE_GONE`）。main
- DEC D-67、DIFF FND：原生通用下绳函数（到端、跳下、蹲下、被打断都走它）。main
- [反编译] 通用下绳函数 0x14074ccf0；它调用的下绳镜头反馈 `Zipline_DetachFeedback` 0x140a35ac0（第 07 章）。

---

### 5.22 竖直滑索

#### 原理

竖直的绳（电梯一样直上直下）在 Apex 里主要用来上高处，所以规则都偏向"往上"：从中间挂上、平视或抬头都往上走；到顶不提前脱离，而是升到顶后被往视线方向推出去 400 u/s，正好落到旁边的平台上。挂上时视角不被锁，可以马上转向要去的平台。

#### 规则和公式

1. **判定为竖直**：每一段都在竖直 ±8° 以内（|d.z| / |d| ≥ 0.99）[设计]。
2. **抓点**：绳上高度 = 原点 z + `verticalFindRaise` 的那一点（吊挂高度），仍然要在 `findRadius` 内、视锥内 [实测，一种几何：夹角 11.45°]。其余条件同 5.15。
3. **方向**：平视或抬头 → 往上 [实测 5 / 5]。**往下看**（俯仰低于水平 `verticalDownPitch` 以上）：R5 的 S21 客户端预测挂上、S3 dedi 从不派发，0.04 – 0.09 s 后被拉回——**R5 结果未定（混合构建分歧）**。HSD Reference 拒绝（`ZIP_REFUSED_DOWN`，按 dedi 的结果）[设计]；Fun 往下滑，到离底端 90 u 时以骑行速度放手 [设计]。
4. **视角**：一开始就自由（没有 0.5 s 的拉动）[实测：第 37 条命令起 180 °/s 跟手]。
5. **滑行**：速度曲线和平绳相同（5.18）[实测 Z3]。
6. **到顶**（没有提前脱离区，`autoDetach` 0）：骑到顶端，原点 = 顶端 − `verticalTopHang`，

   v_out = ẑ · min(v, `maxVerticalDetachSpeed`) + f̂_yaw · `verticalTopPush`

   f̂_yaw = 视线偏航的水平方向 [实测：(400, 0, 600) 两边相同；视线偏 −89.3 … −90.2° 时出口方向 − 视线 = 0.000°，5 / 5]。最后一步只走了 4.12 u（被夹在顶端）。
7. **跳离**：沿视线偏航水平 400 + 竖直 289.8 [实测 ZA1]。**蹲下松手**：HSD 沿视线偏航 min(v, 400) [推断：R5 没测竖直绳蹲下]。
8. 中途转身往下看不会改方向（5.15 第 7 条）[实测]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 竖直绳抓点高度 `verticalFindRaise` | 2.035 m | 80.1 u | 1.112 H | 一种几何 | [实测] A3 §1 |
| 竖直判定 | — | 每段离竖直 ≤ 约 8°（\|d.z\|/\|d\| ≥ 0.99） | — | — | [设计] |
| 往下看的阈值 `verticalDownPitch` | — | HSD 设计值 20° | — | R5 未定 | [设计] |
| 顶部原点位置 `verticalTopHang` | 2.036 m | 顶端下 80.16 u | 1.113 H | — | [实测] A3 §2 |
| 顶部推出 `verticalTopPush` | 10.16 m/s | 400 u/s（沿视线偏航） | 5.556 H/s | — | [实测] A3 §2、§9.3 |
| 顶部竖直速度 | 15.24 m/s | 600 u/s（= 绳速，没碰到 1500 的上限） | 8.333 H/s | — | [实测] |

#### 实现模板

```
// 单位：u、s
verticalFind(rope, origin, e): Q = 绳上 z = origin.z + verticalFindRaise 的点; 角度 = ∠(e, Q - P)
direction: up = 切线朝上的符号
           if e.z < -sin(verticalDownPitch): Reference -> refuse DOWN; Fun -> dir = -up
ride top:  if dir 朝上 and remaining <= 0:
               pos = top - up*verticalTopHang
               vOut = up*min(v, maxVerticalDetachSpeed) + viewYawDir*verticalTopPush
               detach("TOP", vOut)
Fun down:  if 朝下 and remaining - v*dt < stopShort: detach("END", d̂*v)
```

Unity 参考实现：`U:…/Abilities/Zipline/ZiplineAbility.cs`，`ZiplineAbility.Find`（竖直分支）、`Evaluate`（竖直分支）、`Ride`（"vertical rope" 两段）、`Horizontal`；参数 `ZiplineParams.verticalFindRaise`、`verticalDown`（枚举 `VerticalDownRule`：`Refuse` / `RideUp` / `RideDown`）、`verticalDownPitch`、`verticalTopHang`、`verticalTopPush`、`maxVerticalDetachSpeed`；`Rail.IsVertical`。

#### 验收

- `A3Zipline.VerticalRopeRidesToTheTopAndPushesAlongTheView`：视角一开始就自由；顶部 z = 900 − 80.16；vz = min(v, 1500)；水平 400 沿视线。
- `ZiplineM9ATests.VerticalRopeMidHeight`：中段平视 / 抬头往上；Reference 往下看拒绝；跳离沿视线 400 + 289.8。
- 对照数据：A3 §2、§9.3（Z3 竖直绳，5 + 5 次）；ZA1 竖直绳 11 种 × 5 次（会话 `M9R_zipC`）。
- 合格线：顶部出口 (400 沿视线, 600 竖直) 精确；中段平视 / 抬头必须往上。

#### 出处

- A3 §1（竖直绳抓点 80.1）、§2（顶部位置和 400 推出）、§9.3（推出跟视线、视角自由）。main
- ZA1 TL;DR "Vertical rope, mid height"、Open questions 3：往下看的客户端 / dedi 分歧。main
- M9AU §2、§3、§10：Reference 拒绝、Fun 往下滑，都是设计；"强制向上 / 强制下绳区"（wiki V-MokZone）没做。main
- TL §5.2：wiki"竖直绳尽量把人往上送"、两种端点区、"竖直绳 480"（和 R5 实测 600 不符，见 `_notes/hb-ch05.md`）。main

---

### 5.23 滑索枪：发射和搭绳

#### 原理

Pathfinder 的大招是"自己搭一根滑索"：举起枪，朝远处一个点开一枪，一颗飞得很快的弹头飞过去，落地后从脚边到落点拉出一根绳。为了让它是"搭路"而不是"随处飞"，有几条限制：**只能站在地上（或跑墙、挂墙）开**，空中开是哑火；**落点要在 700 – 8000 u 之间**，太近太远都是哑火；哑火**不扣次数**。一根绳搭好以后永久存在，最多同时 10 根，冷却 3 分钟。

绳的两头各有一个"桩"：起点在脚边前方 16 u、离地约 112 u（人挂上去刚好吊在绳下 80 u，脚离地约 30 u）；终点在落点上方约 113 u。

#### 规则和公式

1. **举枪**：按大招键进入瞄准；`raiseTime` 后才接受开火（之前按开火：`ZIPGUN_REFUSED_RAISING`）；瞄准中再按大招键收枪；`aimTimeout` 不开火自动收枪。都不扣次数。
2. **能开火的姿态**：在地面，或跑墙 / 挂墙中 [数据：S21 脚本 `IsOnGround` / `IsWallRunning` / `IsWallHanging`；实测：空中开 0 / 3 出绳，次数保留]。HSD 用自己的跑墙和抓边悬挂代替（这两个只在 Fun 里有，D-08）。
3. **瞄准射线**：从眼（脚 + `eyeHeight`）沿视线最远 8000 + 60 u，打到的**第一个实体**就是落点；绳子不挡 [设计]。
4. **距离**：原点 → 落点的三维距离 d 满足 `minDistance` ≤ d ≤ `maxDistance`，否则哑火（`TOO_CLOSE` / `TOO_FAR` / 打不到东西 `NO_SURFACE`）。
5. **两个桩**：
   - 起点 = 原点 + 水平视线方向 × `startOffset` + ẑ · `startHeight`。
   - 终点：落点能站（法线 z ≥ 0.7）→ 落点 + ẑ · `endHeight`；打在墙 / 天花板上 → 落点 + 法线 × `wallStandoff` [设计：R5 只测了地面 / 台面落点]。
6. **绳线检查**：起点到终点的直线（两头各让 `ropeEndClearance`）穿过实体或低于地板 → 哑火 `ROPE_BLOCKED` [设计；S21 脚本的 `CanTetherEntities` 做的是桩到桩的直线检测，原生放桩逻辑没测]。
7. **陡绳**：|绳方向 z| > `steepDirZ`（约 44.4°）→ 标为陡绳（5.24）[数据：脚本 `ZiplineVertical` + `ZiplinePreserveVelocity`]。
8. **开火**：合格 → 扣次数、收枪、弹头以 `projectileSpeed` 飞行（不受重力），在 开火 + |落点 − 眼| / 2600 那条命令把绳加入世界。落点在开火时就定死（世界是静态的）。
9. **哑火**：不出绳、不扣次数、枪还举着 [实测]。
10. **绳的数量和寿命**：每人最多 `maxRopes` 根，第 11 根出现时删最老的一根（正在骑的人放手，5.21）；绳永久存在；绳在出现后 `refundTime` 内被删 → 次数还回来 [数据：脚本 `ZIPLINE_MAX_IN_WORLD` 10、`ZIPLINE_REFUND_TIME` 3；HSD 没有绳子受伤，只有"超过 10 根"会删]；重置身体 → 所有枪绳消失 [实测]。
11. **冷却**：开火后 `cooldown`（Reference 180 s；Fun 10 s [设计]）。
12. 没有 `upgrade_ult_one` 升级，用默认的 700 / 8000 [实测：每次重置只有 `survival_finite_ordnance`]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 最近距离 `minDistance`（原点 → 落点，三维） | 17.78 m | 700 u | 9.722 H | 地面 600 哑火 / 800 出绳；墙 610 哑火 / 790 出绳 | [数据] 脚本 `zipline_distance_min`；[实测] 12 次 |
| 最远距离 `maxDistance` | 203.2 m | 8000 u | 111.1 H | 场地上最远只打到 3639 u，8000 没测 | [数据] 脚本 `zipline_distance_max` |
| 弹头速度 `projectileSpeed` | 66.04 m/s | 2600 u/s | 36.11 H/s | 800 / 1500 / 2300 / 3640 u 处 0.3 / 0.5–0.6 / 0.8 / 1.4 s 出绳 | [数据] 脚本 `projectile_launch_speed`；[实测] |
| 起点桩前移 `startOffset` | 0.406 m | 16 u | 0.222 H | 实测 16.2 u | [实测] ZGO |
| 起点桩高度 `startHeight` | 2.847 m | 112.1 u | 1.557 H | 112.1 – 112.7 u（站在岩石上 112.7） | [实测] ZGO |
| 终点高于落点 `endHeight` | 2.863 m | 112.7 u | 1.565 H | — | [实测] |
| 墙上终点外移 `wallStandoff` | 0.406 m | HSD 设计值 16 u | 0.222 H | 未知 | [设计] |
| 陡绳阈值 `steepDirZ` | — | \|d̂.z\| > 0.7（约 44.4°） | — | 实测 42.3° 普通、52.1° 陡 | [数据] 脚本；[实测] |
| 最多几根 `maxRopes` | — | 10 根 | — | 实测 4 根共存 | [数据] 脚本；[实测] 3 次 |
| 退还时限 `refundTime` | — | 3 s | — | — | [数据] 脚本 |
| 冷却 `cooldown` | — | 180 s（弹匣 180，每秒回 1） | — | 实测每秒回 0.80 – 0.99 → 182 – 225 s | [数据] 脚本 `regen_ammo_refill_rate` 1；[实测] 52 次 |
| 举枪到能开火 `raiseTime` | — | HSD 设计值 0.5 s | — | R5 只在 1.0 s 时开过火 | [设计] |
| 瞄准超时 `aimTimeout` | — | HSD 设计值 20 s | — | — | [设计] |
| 瞄准眼高 `eyeHeight` | 1.524 m | HSD 设计值 60 u | 0.833 H | 和钩爪 / 游戏镜头同一个眼高；R5 站立眼高 70 u | [设计] |
| 绳线检查两头留空 `ropeEndClearance` | 0.051 m | HSD 设计值 2 u | 0.028 H | — | [设计] |

注意：700 – 8000 u 是**原点到落点**的距离，不是绳长。绳长 = 两个桩之间的距离（例：800 u 的落点，绳长 780.8 u）。

#### 实现模板

```
// 单位：u、s
Evaluate(feet, canFire, yaw, pitch):
    eye = feet + up*eyeHeight; dir = viewDir(yaw, pitch)
    hit, n = raycastSolids(eye, dir, maxDistance + eyeHeight)    // 绳子不挡
    if no hit:                                   return NO_SURFACE (空中则 AIR)
    d = |hit - feet|; flight = |hit - eye| / projectileSpeed
    f = flatten(dir)
    start = feet + f*startOffset + up*startHeight
    end   = n.z >= 0.7 ? hit + up*endHeight : hit + n*wallStandoff
    steep = |(end - start).z| / |end - start| > steepDirZ
    if not canFire: AIR; if d < minDistance: TOO_CLOSE; if d > maxDistance: TOO_FAR
    if ropeLineBlocked(start, end, ropeEndClearance): ROPE_BLOCKED
    return valid

每条命令：Idle --大招键--> Aiming(phaseSince = now)
         Aiming: 每条命令重算 preview；大招键 -> Idle；超时 -> Idle
                 开火键: 未举好 -> 拒绝; 不合格 -> 哑火(不扣); 合格 -> 扣次数, arrival = now + flight, -> Flight
         Flight: now >= arrival -> 建 Rail(start, end, ride = GunRope(steep)), world.AddRail, 超过 10 根删最老
```

Unity 参考实现：`U:…/Abilities/ZiplineGun/ZiplineGunAbility.cs`，`ZiplineGunAbility.Evaluate`、`RopeBlocked`、`CanFireFrom`、`BeforeMove`、`Deploy`、`RemoveAt`、`DestroyRope`、`Raised`；参数 `ZiplineGunParams`（`ZiplineGunParams.Measured()` = Reference，`ZiplineGunParams.Fun()` 冷却 10 s；字段全部 [u]、[s]）。加绳用 `U:…/World/MovementWorld.cs` 的 `MovementWorld.AddRail`。预设：`U:…/Abilities/_Core/SkillRules.cs` 的 Pathfinder S21 预设把 `zipline_gun` 放在 Slot4（Z 键），1 次，`scriptCooldown`；仲裁行 `SkillRules.ZiplineGunTraits`（优先级 20、瞄准守护 25 s，详见第 06 章）。带滑索枪的身体水平速度上限 1100 u/s（`GrappleS21Params.HorizontalCeiling`，和 S21 钩爪同一个）。

#### 验收

- `ZiplineGunM10BTests.TheMinimumDistanceIs700AndADryFireKeepsTheCharge`（600 / 690 哑火，710 / 800 / 2300 出绳）、`WallTargetsFollowTheSameDistanceRule`（墙 610 哑火、790 出绳）、`AnAirFireIsADryFire`、`WallRunAndHangCountAsFiringStances`、`TheFireWaitsForTheRaiseAndZAgainHolsters`、`NothingWithinRangeAndBeyondRangeAreDryFires`、`AnObstacleInTheAimPathIsTheTarget`、`ARopeLineThroughASolidIsADryFire`。
- `ZiplineGunM10BTests.TheRopeGeometryAndTheProjectileTime`（800 / 1500 / 2300 / 3640 u：出绳时刻在 0.25–0.4 / 0.5–0.65 / 0.8–0.95 / 1.35–1.5 s；起点离原点水平 16、高 112.1；终点高 112.7）。
- `ZiplineGunM10BTests.TenRopesAtMostTheOldestIsRemovedAndARiderLetsGo`、`ARopeDestroyedWithinThreeSecondsRefundsTheCharge`（1.0 s 退、3.5 s 不退）、`TheChargeReturnsAfterTheConfigCooldown`、`AResetRemovesTheGunRopes`、`ThePathfinderPresetCarriesTheGunOnTheUltimateWithAScriptCooldown`。
- 对照数据：ZG TL;DR、ZGO 逐次表（`fire_d600` / `d800` / `d1500` / `d2300` / `flat` / `sky`、`wall_d600` / `d800`、`fire_air`）。
- 合格线：距离边界 R5 的四个点（600 / 610 哑火，790 / 800 出绳）全对；桩位置和 R5 差 ≤ 0.6 u；出绳时刻落在 R5 观测的 0.1 s 区间里。

#### 出处

- ZG TL;DR、"Model for HSD"：真大招能在本地用（本地脚本带 S3 补丁）、距离、只能在地上、桩高、弹头 2600、多根共存、冷却。main
- ZGO：逐次桩高 112.1 / 112.7、前移 16.2、出绳时刻、陡绳 42.27° / 52.09°。main
- M10BU §1 – §5、§8、§9：HSD 实现、各设计值、绳线检查、墙上终点、缺口。main
- [数据] S21 `mp_weapon_zipline.nut` / `mp_weapon_zipline.txt`（只读，M10BU 引用）：`zipline_distance_min` 700、`zipline_distance_max` 8000、`projectile_launch_speed` 2600、`ZIPLINE_MAX_IN_WORLD` 10、`ZIPLINE_REFUND_TIME` 3、`regen_ammo_refill_rate` 1、`CanTetherEntities`、`ZiplineAutoDetachDistance` 100、`ZiplineVertical` / `ZiplinePreserveVelocity`、开火姿态检查。原生放桩逻辑没读。
- DEC D-08：HSD 的跑墙、挂墙只在 Fun。main

---

### 5.24 滑索枪的绳：和地图滑索的差别（runtime rails、每根绳自己的滑行规则）

#### 原理

滑索枪搭的绳和地图滑索在玩家看来是同一种东西：一样的挂法（任意位置、空中、重抓限制）、一样的跳离、一样的 Super Jump。不同只有三点：**更快**（封顶 1000 u/s，起步也更猛），**到端照样 600 甩出**（所以长绳满速到端会被"刹"一下），**陡的绳（> 约 44°）下来时只保留竖直速度、跳离可以朝视线方向**。

所以实现上只要一套滑索代码：枪只负责"往世界里加一根绳"，绳自己带一份"这根绳怎么滑"的小参数表；地图绳没有这张表，照旧用滑索的默认值。这样地图绳的行为一个字节都不变。

#### 规则和公式

1. **运行时加绳**（runtime rail）：枪的绳是一根普通的两点绳，加进世界的绳列表。从那条命令起，挂绳判定（5.15）、挂绳提示、钩爪射线、钩爪 → 滑索交接都能看到它。
2. **删绳不挪编号**：删掉的绳只标成"不活跃"，留在列表里，所有绳的编号不变；挂绳判定、钩爪射线、`ClosestRail` 跳过不活跃的绳。
3. **每根绳自己的滑行规则**（`Rail.ride`，地图绳为空）：有就用它的数，没有就用 `ZiplineParams`。枪绳的数（5.18 的公式不变，只换数）：

   第 1 条命令 8.333 → 挂上状态 0.5 s 内 +1000 u/s² → 之后 +280 u/s² → 封顶 1000 u/s。

   结果：0.5 s 502、1.0 s 642、1.5 s 782、约 2.3 s 到 1000（地图绳：0.5 s 303、1.25 s 到 600）。
4. **到端**：d̂ · clamp(v, 600, 600)，和地图绳相同 [实测：平绳、11°、42° 都是 600 沿绳]。**陡绳**只保留竖直分量：(0, 0, d̂.z · 600) = 600 · sin θ ẑ [实测拟合，只有 52° 一个角度：R5 0.1 s 后 vz 404 – 417，HSD 473.3 − 0.1 · g ≈ 398 – 411]。
5. **跳离 / 蹲下的方向**（只对枪绳）：
   - 陡绳：沿**视线偏航**水平 min(v, 400) [实测 2 / 3：视线转 90° → (0, −400, 289.8)]。
   - 不陡的斜绳：沿**三维绳方向** min(v, 400)，再加 289.8 竖直 [实测 2 次，42° 上坡：(296, 0, 559) = 400 · d̂ + 289.8 ẑ]；蹲下同样但不加竖直 [推断]。
   - 平绳：和地图绳一样 (400, 0, 289.8) [实测 3 次]。
   - 挂上第一条命令的 carry（5.19）优先于以上。
6. **其他全部同地图绳**：挂绳规则（中段 / 空中 / 0.35 s 锁定 / 3 次 / 端点区反向 / 提示）、Super Jump（R5 在起点桩挂上马上跳：vz 约 580、水平 19；HSD 564）、视角拉动、吊挂、`stopShort` 90。
7. **钩爪钩自己的枪绳**：R5 1 / 2 次钩上并交接，交接后**重新从头加速**（进来 397 → 252 → 0.5 s 502）；HSD 用地图绳的交接规则（保留入绳速度当保底），所以头约 0.4 s 比 R5 快 [设计：只有 1 次 R5 数据，任务要求复用现有交接；一个参数可以切]。
8. **在枪绳上放钩爪**：钩爪打断骑行（5.21），从绳上直接起拉。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 枪绳速度上限 `RailRide.speed` | 25.40 m/s | 1000 u/s | 13.89 H/s | 3676 u 长绳约 2.3 s 到 1000 并保持 | [实测] ZG；来源键没找到 |
| 枪绳挂上状态加速 `RailRide.mountAccel` | 25.40 m/s² | 1000 u/s² | 13.89 H/s² | 拟合 0.5 s 时 502.2 | [实测拟合] M10BU |
| 枪绳之后的加速 `RailRide.rideAccel` | 7.112 m/s² | 280 u/s² | 3.889 H/s² | 拟合 1.0 s 641.5、1.5 s 781.9 | [实测拟合] |
| 枪绳挂上状态时长 `RailRide.mountStateTime` | — | 0.5 s | — | — | [实测] 同地图绳 |
| 0.5 / 1.0 / 1.5 s 时的速度 | 12.76 / 16.29 / 19.86 m/s | 502.2 / 641.5 / 781.9 u/s | 6.975 / 8.910 / 10.86 H/s | 每次差 ≤ 2.5 u/s | [实测] ZGO 12 次 |
| 1475 u 平绳到端前的最高速度 | 23.88 m/s | 940 u/s | 13.06 H/s | 937.8 – 941.6 | [实测] ZGO |
| 枪绳到端速度 `RailRide.detachSpeedMin` / `Max` | 15.24 m/s | 600 / 600 u/s | 8.333 H/s | 比 600 慢的到端没测 | [实测] |
| 陡绳到端竖直速度（52.09°） | 12.02 m/s | 600 · sin 52.09° = 473.3 u/s | 6.574 H/s | R5 推回到脱离时 473 – 486 | [实测拟合，一个角度] |
| 枪绳到端前的脱离距离 | 2.286 m（HSD） | HSD 90 u；R5 平绳 90.1 – 90.2、11° 96 – 98、42° 111、52° 107 – 110 u | 1.250 H | 斜绳 R5 更早脱离 | [实测] ZGO `dist_end`；HSD 和地图绳同一个 `stopShort` |
| 枪绳上的 Super Jump 竖直速度 | 14.33 m/s | HSD 564 u/s；R5 约 575 – 580（0.1 s 样本 502 – 507） | 7.833 H/s | — | [实测] ZGO 3 次 |

#### 实现模板

```
// 单位：u、s
class Rail { points; stopShort = 90; active = true; ride = null }      // ride == null: 地图绳
class RailRide { first = 8.333; mountAccel = 1000; rideAccel = 280; mountStateTime = 0.5; cap = 1000
                 detachMin = 600; detachMax = 600; steep; jumpOffAlongRope = true
                 EndExit(d̂, v): sp = clamp(v, detachMin, detachMax); return steep ? (0, 0, d̂.z*sp) : d̂*sp }

Ride():         law = rope.ride ?? ZiplineParams                         // 5.18 公式不变
到端:           vOut = rope.ride ? rope.ride.EndExit(d̂, v) : d̂*clamp(v, 600, 600)
ExitHorizontal: 见 5.19（steep → 视线偏航；jumpOffAlongRope → 三维绳方向）
删绳:           rope.active = false（编号不变）；正在骑的人下一条命令放手（ROPE_GONE）
```

Unity 参考实现：`U:…/World/WorldGeometry.cs`，`Rail.ride`、`Rail.active`（都是 `[NonSerialized]`）、`RailRide`、`RailRide.GunRope`、`RailRide.EndExit`；读它的地方是 `U:…/Abilities/Zipline/ZiplineAbility.cs` 的 `ZiplineAbility.Ride`、`ExitHorizontal`、`Evaluate`（跳过不活跃的绳）。枪在 `ZiplineGunAbility.Deploy` 里设 `ride.steep`。

#### 验收

- `ZiplineGunM10BTests.AGunRopeRampsTo1000AndExitsAt600LikeR5`：0.5 / 1.0 / 1.5 s 和 502.2 / 641.5 / 781.9 差 ≤ 3；1475 u 绳最高 939.7 ± 10；骑行 2.07 ± 0.06 s；出口 600 ± 0.5。
- `ZiplineGunM10BTests.ALongGunRopeCapsAt1000AndAMapRopeAt600`、`MapRopesCarryNoRideLaw`。
- `ZiplineGunM10BTests.SteepRopesExitStraightUpAndJumpAlongTheView`：出口水平 0、竖直 600 · sin θ；推到 0.1 s 后落在 R5 区间；跳离沿视线。
- `ZiplineGunM10BTests.ASlopedGunRopeJumpsOffAlongTheRope`（400 · d̂ + 289.828）、`AFlatGunRopeJumpOffIsTheMapLaw`、`TheSuperJumpWorksFromTheBeginStation`、`GunRopesKeepTheMapRopeMountRules`、`TheGrappleHandsOverToTheOwnGunRope`、`AGrappleFromAGunRopeEndsTheRide`。
- 回归：地图绳的所有测试（5.15 – 5.22）不变；M10BU §7 记录枪绳加入后所有旧演示的逐命令哈希和改前相同。
- 对照数据：ZGO `ride_d1500` / `ride_wall` / `ride_s40` / `ride_s50` / `ride_jump` / `ride_super`。
- 合格线：0.5 / 1.0 / 1.5 s 速度差 ≤ 3 u/s；到端 600 ± 0.5；地图绳逐字节不变。

#### 出处

- ZG TL;DR "Ride speed"、"End of ride"、"Jump-off"、"Super jump"、"Grapple onto the own rope"、Open questions 1 – 2。main
- ZGO：逐次速度、出口、`dist_end`。main
- M10BU §1（一套绳子系统、runtime rails、`RailRide`、删绳不挪编号）、§2（R5 对 HSD 表）、§8 第 4 – 6、9 条（缺口）。main
- TL §5.2：wiki"> 45° 的绳可以朝任意方向跳"（枪绳实测支持）。main
- [数据] 脚本 `ZiplineVertical` + `ZiplinePreserveVelocity`（陡绳标志，M10BU 引用）。枪绳 1000 上限的来源键没找到。

---

---

## 第三部分 · 钩爪（§5.25 – §5.31）

**白话说明**

钩爪是 Pathfinder 的战术技能：朝准星射出一个钩子，钩住以后**先把人往上弹一下**，停 0.2 s，再沿绳子把人拉过去；拉的速度从很慢开始、1.5 s 内爬到 800 u/s；拉的过程中按方向键还能"甩"出更高的速度；快到钩点、钩点跑到视线背后、或者拉不动了，钩子自己松开，**松开时速度原样保留**。每次用完按飞了多远罚 10–30 s 冷却。

这一部分管五件事：发射和挂上（5.25）、拉的时候的速度（5.26）、自动脱钩（5.27）、按键脱钩和脱钩以后（5.28）、撞上时的上抬这个"R5 有代码但不起作用"的规则（5.29）、次数和冷却（5.30）、和 TF2 钩爪的区别（5.31）。

和别的章的分界：

- 钩住时画面朝钩点那边歪（`rope_roll`，横滚上限 20°）在第 07 章 §3.8；眼高（钩子从眼睛打出去）的状态和镜头共用，规则在第 07 章 §3.1。
- 钩爪和别的动作谁先谁后（拉动中按跳不算跳、新技能顶掉旧技能、钩爪 → 滑索交接、松开后能不能 lurch）只在本节写到"需要的部分"，完整的仲裁和动量规则详见第 06 章。
- 空中加速、重力的半步积分在第 03 章；松开后落地接滑铲在第 04 章。

**读完能做出什么**：照 5.25 – 5.28 的规则和伪代码，加上第 03 章的空中移动，能写出和 R5 逐命令对得上的钩爪（拉动律在 72 个 R5 片段上逐命令误差 rms 2.08 u/s；往墙上拉的脱钩命令差 1–2 条、最高点差 ≤ 1 u）。

**本节出处缩写**（其余沿用 DESIGN-PHILOSOPHY §2.2）：

| 缩写 | 文件 |
|---|---|
| P2 | `research/rea-native/subsystems/N2-P2-GRAPPLE-ZIPLINE-PADS.md`（原生钩爪 / 滑索 / 跳板，§1、§5、§8） |
| N6 | `research/rea-native/n6/N6-MEASURE.md`（脱钩规则 Frida 实测、低速超时） |
| N13 | `research/rea-native/n13/N13-GRAPPLE-DETACH.md`（逐条原生脱钩规则；A-1 早脱钩拆解） |
| GN | `research/rea-native/gn/GN-GRAPPLE-NATIVE.md`（D-50：脱钩全部按原生；钩子父实体） |
| G6 | `research/rea-native/g6/G6-IMPACT-BOOST.md`（D-52：撞上上抬） |
| N12 | `research/rea-native/n12/N12-RODEO-ROLL.md`（钩爪横滚；rodeo 是什么） |
| LG | `research/phase2-local/m4/lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md`（M4：时间线、弹起、飞行时间） |
| SW | `research/phase2-local/m4b/swing/SWING.md`（M4b：不是钟摆；RF 律；松开保速） |
| GR | `research/phase2-local/m55/GRAPPLE-RANGE.md`（射程 850 的来历和实测） |
| GM10 | `research/phase2-local/m10/r_grapple/GRAPPLE-M10.md`（M10：72 个片段，拉动律和技巧） |
| M10A | `research/phase2-local/m10/unity/M10A-UNITY.md`（M10-A：Unity 拉动律读法、开环对照） |
| GZ | `research/phase2-local/m6/a3_zip/GRAPPLE-ZIP.md`（M6-G：第二次按键松开） |
| SV | `research/phase2-local/static-values/STATIC-VALUES.md` §3.6（Pathfinder 钩爪 setfile 值） |
| TN6 | `tf2/overnight/N6-GRAPPLE-TF2-VS-APEX.md`（TF2 和 Apex 钩爪对照；52 个 Apex `grapple_*` ConVar 默认值） |
| TN2 | `tf2/overnight/N2-GRAPPLE-BOOST.md`（TF2 钩爪实测） |
| FEEL | `research/feel/FEEL.md` §9.1、§10、§10b（A-1、F7、GN 的手感对照） |
| DIFF | `R5-DIFF-ARCHIVE.md`（A-1、GN、G6 节） |
| DEC | `DECISIONS.md`（D-03、D-13、D-34、D-38、D-50 – D-52、D-65） |
| U: | HSD-Unity 仓库；`U:…/` = `Assets/HSD/R5Replay/Runtime/` |

---

**记号和前提**

- **O**：身体原点（脚底中心）。**E** = O + (0, 0, e)：眼睛，e = 当前眼高（站 70 u、冲刺 64 u、蹲 / 滑 32 u，过渡见第 07 章 §3.1）。
- **P**：钩点（钩子打中的那一点）。HSD 里钩点挂上后固定在世界里；R5 钩在会动的东西上时 P 每条命令跟着那个东西走（N13 §2），HSD 没做。
- **绳子方向 d**（脱钩规则用）= (P + (0, 0, 25)) − (O + (0, 0, 23))，几乎就是 P − O 再往上抬 2 u。d̂ = d / |d|。**v_r** = v · d̂（朝钩点的径向速度，负 = 在远离）。
- **拉力方向 r̂**（拉动律用）= (P − O) / |P − O|。拉力用 r̂、脱钩用 d̂，两者只差 2 u 的高度，见 5.26 规则 2 的说明。
- **f**：三维瞄准方向（准星的 pitch / yaw，不是镜头角，第 07 章 §0.3）。**ŵ**：按键的水平想要方向（第 03 章 wishvel 归一化）。
- **msc**：移动倍率（空手 Pathfinder 1.15）。
- **命令**：Unity 固定 1/120 s；规则都按 dt 写。"这条命令"的状态 = 命令开始前的状态（pre）。
- **阶段**：空闲 → 飞行（钩子在空中）→ 准备（wind-up，挂上后 0.2 s）→ 拉动 → 松开。Unity 的 `GrapplePhase`：`Idle`、`Flying`、`Windup`、`Pulling`、`Released`。
- **两种钩点**：钩在**世界几何**上（地面、关卡墙）和钩在**独立实体**上（脚本摆的道具、绳子）。R5 用"钩子有没有父实体"区分，影响 5.27 的"远离"规则和 5.29 的上抬。
- 参考身高 H = 72 u（第 01 章 §4.1）。
- "R5"都指本地混合构建（S21 客户端 + S3 dedi）。钩爪上有两处只在混合构建里出现的现象（视线离开时 dedi 重挂、撞上上抬被丢掉），见 DESIGN-PHILOSOPHY §10.3 和 5.27、5.29。

---

### 5.25 发射、飞行和挂上

#### 原理

钩爪是"指哪钩哪"的：钩子沿准星从**真实眼睛**打出去，最远 850 u；打空什么都不发生，不会凭空拉人。钩子有飞行时间（约 2000 u/s，钩 400 u 外要 0.2 s），挂上那一刻**身体被固定弹起 200 u/s**，不管是在地上、空中、冲刺还是滑铲；再等 0.2 s 准备时间才开始拉。

这一下弹起是 Apex 钩爪手感的核心（TF2 钩爪没有它，5.31）：它让钩爪能当一个小跳用（往脚下钩 = grapple hop），也给了"挂上后立刻按跳"一个时间窗口（Jump Grapple：普通跳叠在弹起上，之后拉出 1000 u/s 以上）。窗口按时间算，对应 DESIGN-PHILOSOPHY P4"技巧窗口按时间算"。

钩到什么也有区别：钩在世界几何上和钩在道具 / 绳子上，后面有两条规则不一样（5.27 远离脱钩、5.29 撞上上抬）。钩到玩家 / NPC 在 R5 里另有一套（绳子指向对方眼睛、脱钩时自动近战），HSD 没有这类目标，没做。

#### 规则和公式

1. **发射**：空闲（或已松开）时，战术键**按下**的那一条命令：从 E 沿 f 打一条射线，长度 ≤ `range`。第一个命中点就是 P。
   - **打空**（射线内没有面）：移动完全不受影响，不进入飞行。R5 打空扣不扣次数没测；HSD 打空不发射、不扣次数；发射了但没挂上（飞行中被取消 / 打断）扣基础 10 s 冷却 [设计]（5.30）。
2. **飞行**：挂上时刻 t_attach = t_fire + t0 + L / v_hook，L = |P − E|。挂上发生在开始时刻 ≥ t_attach 的第一条命令。
   - R5 ConVar `grapple_shootVel` = 2000 u/s [数据]；M4b 拟合 v_hook = 2034.9 u/s、t0 = 0.0043 s（44 次，误差 0.0009 ± 0.0032 s）[实测]。两者在 1200 u 以内差不到 1 条命令（120 Hz），**HSD 现在用拟合值**。
3. **挂上**（这一条命令的移动之前）：
   - 竖直速度**设成** `hopVz`（不是加上去）：vz ← 200 u/s；水平速度不变（空中 297 u/s 挂上后还是 297）。
   - 着地的身体离地；正在滑铲的结束滑铲。
   - 记下"从地面挂上"（attachedFromGround = 挂上前着地），开始冷却计距（5.30）。
   - 只有 Pathfinder 的 setfile 有 200；别的传奇是 0（比如把钩爪给 Gibraltar 就没有弹起，N6 §1.3）。
4. **钩点类型**：命中面是独立实体（道具、绳子）→ hookOnEntity = true；世界几何 → false。
5. **准备（wind-up）**：挂上后 `windup` 秒开始拉（第一条开始时刻 ≥ t_attach + windup 的命令）。准备期间：
   - **接近规则照常检查**（5.27 规则 1）：钩点已经在身边（往脚下钩、pitch 89°）就直接松开，整次只有那一下 200 弹起，没有拉 = **grapple hop**，最高 200²/(2g) = 26.7 u。
   - **挂上跳（Jump Grapple）**：从**地面**挂上、还没开始拉、这一条命令**按下**跳：vz += √(2·g·`jumpHeight`) − ½·g·dt（普通起跳叠在弹起上，第 03 章起跳规则；连跳惩罚不算），每次挂上最多一次。这一下占用跳键（同一条命令不再触发空中跳 / 喷气等，第 06 章）。
     - R5 实测：挂上后 18 条命令（0.15 s）以内按跳有效，24 条（0.2 s）以后没效果；19 – 23 条没测。HSD 窗口开到开始拉之前（最多 23 条命令）[推断]。
     - 空中挂上能不能用这个窗口**没测**；HSD 只给从地面挂上的 [推断]。
     - HSD 把挂上跳当成一次真正的起跳，重新开始 lurch 窗口 [推断]（第 03 章、第 06 章）。
   - 准备期间再按一次战术键 = 取消（不拉），HSD [设计]，R5 没测（5.28）。
6. **地面发射时的助跑**：R5 实测"地面发射后水平速度 297 → 0"是因为测试脚本在发射那条命令松开了 W 和冲刺，速度按普通无输入地面减速掉光（M10A §1）。**没有"发射清水平速度"这条规则**，HSD 也不加。按住 W 飞行中保留助跑是 HSD 模型的结果，R5 没测。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 射程 `range`（`grapple_maxLength`） | 21.59 m | 850 u | 11.81 H | 实测有效射程 830–840 u（pitch 0，从起点到墙面） | [数据] 武器 .txt；[实测] GR §3 |
| 竖直射程 `grapple_maxLengthVert` | 21.59 m | 850 u | 11.81 H | 没测（只测了 pitch 0）；HSD 不分竖直 / 水平 | [数据] |
| 射线起点 = 眼高 e（站 / 冲刺 / 蹲滑） | 1.778 / 1.626 / 0.8128 m | 70 / 64 / 32 u | 0.9722 / 0.8889 / 0.4444 H | 72 个 R5 钩点都在这条线上，偏 ≤ 2 u（滑铲中途量到 39 u） | [数据] setfile `viewheight`、`sprintViewOffset` −6；[实测] FEEL §9.1 |
| 钩子飞行速度 v_hook（HSD `hookSpeed`） | 51.69 m/s | 2034.9 u/s | 28.26 H/s | ConVar `grapple_shootVel` 2000 u/s（50.80 m/s，27.78 H/s） | [实测] SW 第 2 轮；[数据] TN6 §2.1 |
| 飞行固定延迟 t0 `attachLatency` | — | 0.0043 s | — | 0 – 0.005 s（拟合） | [实测] |
| 挂上弹起 `hopVz`（`grapple_attachVerticalBoost`） | 5.08 m/s | 200 u/s（设成） | 2.778 H/s | 其他传奇 0 | [数据] SV §3.6；[实测] 挂上后 vz 193.7 = 200 − g·dt |
| 准备时间 `windup`（`grapple_pullDelay_human`） | — | 0.2005 s | — | ConVar 0.2 s；实测 0.203 ± 0.004 s | [数据] TN6；[实测] LG §2.1、SW |
| grapple hop 最高点（只有弹起） | 0.6773 m | 26.7 u | 0.3704 H | 实测 26.7 u | [算] 200²/(2·750)；[实测] M10A §3 |
| hop + 挂上跳最高点（第 0 / 1 / 2 / 4 条命令按跳） | 3.950 / 3.891 / 3.830 / 3.716 m | 155.5 / 153.2 / 150.8 / 146.3 u | 2.160 / 2.128 / 2.094 / 2.032 H | 实测 146.3–155.5 u，HSD 逐个对上 | [实测] GM10、M10A §3 |
| 挂上跳加的竖直速度（比同一条普通空中命令多） | 7.282 m/s | 286.7 u/s（= 289.83 − ½·750/120） | 3.982 H/s | 实测 post vz +280.5（含这条命令的重力 −6.25） | [算] [实测] GM10 |
| 挂上跳窗口 | — | ≤ 0.15 s 有效、≥ 0.2 s 无效 | — | 0.15–0.2 s 之间没测 | [实测] GM10（30 次） |
| 自动瞄准角 `grapple_autoAimAngle` | — | 10° | — | 没测；HSD 没做 | [数据] TN6 §2.1 |
| 打空宽限 `grapple_gracePeriod` | — | 0.25 s | — | Apex 冷却由脚本扣，是否生效没查；HSD 没做 | [数据] TN6 §2.1 |

#### 实现模板

```
// 单位：u、s。在这条命令的移动之前（技能的 BeforeMove）
on tacticalPressed and phase in {Idle, Released}:
    E   = O + (0,0,eyeHeight())               // 当前眼高：70 / 64 / 32（第 07 章 §3.1）
    hit = raycast(E, aimDir(pitch, yaw), range)
    if not hit: event MISS; return            // 移动不受影响
    P = hit.point;  hookOnEntity = hit.isEntity    // 道具 / 绳子 = true，世界 = false
    L = |P - E|
    tAttach = now + t0 + L / vHook
    phase = Flying

if phase == Flying and now >= tAttach - dt/2:  // 第一条开始时刻 ≥ tAttach 的命令
    vel.z = hopVz                              // 设成 200，不是加
    attachedFromGround = grounded
    grounded = false; sliding = false
    tPull = now + windup
    phase = Windup; startCooldownTracking()    // 5.30

if phase == Windup:
    if nearRule(P, O, E, vel): release("NEAR"); return     // 5.27 规则 1；grapple hop 在这里结束
    if attachedFromGround and not attachJumpUsed and jumpPressed and now < tPull - dt/2:
        vel.z += sqrt(2*g*jumpHeight) - 0.5*g*dt           // 挂上跳
        attachJumpUsed = true; consumeJump()
    if now >= tPull - dt/2: phase = Pulling; tPullStart = now
```

离散化要注意：

- 挂上那一条命令先把 vz 设成 200，**再**走这一条命令的空中移动（半步重力），所以记录到的 post vz 是 200 − g·dt（120 Hz：193.75 u/s）。
- 准备期间没有拉力，身体按普通空中移动走（重力 1 倍、空中加速照常）。

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleAbility.BeforeMove`（发射、挂上、准备、挂上跳）、`GrappleAbility.FireEyeHeight`、`GrappleAbility.AttachJumpOpen`；参数 `GrappleParams`（`range` 850、`hookSpeed` 2034.9、`attachLatency` 0.0043、`hopVz` 200、`windup` 0.2005，全部 [u]）、`GrappleS21Params`（`attachJump` true、`nativeEye` + `eye`（`NativeEyeParams`，`U:…/NativeEyeHeight.cs`））。钩点类型：`U:…/Abilities/_Core/GrappleSurface.cs`，`IGrappleSurface.Raycast`、`IGrappleHookEntity.LastHitEntity`（`MovementWorld`：道具方块、绳子为真；地面、关卡几何为假）。游戏配置由 `U:…/MovementConfig.cs` 的 `MovementConfigs.NativeGrapple()` 生成（Reference 和 Fun 相同）。

平行保留（没选的旧版）：

- **固定眼高 60 u**（pre-A-1，`GrappleParams.eyeHeight` 60，M4b 分析时假设的）：`s21.nativeEye = false` 切回。用 60 时 M4 墙上的钩点低 10 u，最高点低 15–22 u（D-34）。
- **M4 回放电机**用 `GrappleParams.R5Reference()`（`s21` 为空）：眼高 60、拉力是 M4b RF 律（5.26），钩点 = 命中点 + 31.9 u。只给回放基线用，不改。

#### 验收

- 单元测试（Unity EditMode，`Assets/HSD/R5Replay/Tests/Editor/`）：
  - `GrappleTests.AimFromEyeAttachHopWindupAndPullTiming`（M4 回放参数，眼高 60）：400 u 外的墙，第 24 条命令挂上（0.0043 + 400.07 / 2034.9 = 0.2009 s），vz = 200 − 750·dt，再 24 条命令开始拉。
  - `GrappleTests.HopAlsoInTheAir`：空中挂上 vz 也设成 200，水平速度不变。
  - `GrappleM10ATests.MaxRopeIs850`：850 u 以外打空（`GRAPPLE_MISS`），以内发射。
  - `GrappleM10ATests.GrappleHop`：不按跳 26.7 u；第 0 / 1 / 2 / 4 条按跳 155.5 / 153.2 / 150.7 / 146.3 u（容差 1 u），整次没有拉动。
  - `GrappleM10ATests.JumpGrappleNeedsTheJumpInsideTheWindup`：第 1 / 6 / 18 条命令按跳有挂上跳，出口水平速度 1015 ± 5 %；第 24 条和不按都没有，出口 798 ± 6 u/s。
  - `GrappleM10ATests.TheAttachJumpAddsTheNormalJump`：比同一条普通空中命令多 286.8 ± 0.2 u/s。
  - `GrappleM10ATests.TheAttachJumpIsOneEffect`；`JumpArbitrationTests.GrapplePullMasksTheJumpAndAPullStartRefusesIt`（第 06 章）。
  - `FeelReplayTests.TheGrappleOfAnAbilityTrialHooksTheTestWall`（R5 录像喂进游戏身体时钩子打到测试墙）。
- 注意：`GrappleM10ATests` 用的是 `GrappleParams.Measured()`（M10-A 规则：眼高 60、拟合刹车、pre-GN 脱钩），不是 Reference 现在的原生规则；**眼高按 70 / 64 / 32 打出这一条没有单元测试**，只在手感对照（FEEL §9.1：72 个钩点偏 ≤ 2 u）里验证过。
- 对照数据：M4 15 次时间线（LG §2.1：挂上 0.200 s sd 0.001、开拉 0.402 s sd 0.003）；M55 射程（GR §3，`grapple_range_check.py`）；M10 72 个 `m10_g_*` 片段（GM10，`grapple_analysis.py`）。
- 合格线：挂上和开拉的命令与 t0 + L/2035、+0.2005 s 差 ≤ 1 条命令；挂上后 post vz = 200 − g·dt（差 < 0.01 u/s）；grapple hop 最高点差 ≤ 1 u。
- 已知例外：M4 / M4b 所有钩爪试验都带着 ×2 射程的模组（`infinite_abilities_grapple`，测试工具补弹时加上的）。最长的钩只有 705 u，没影响结果；以后测钩爪要用 `m55_nomod` 前缀把模组去掉（GR §2）。

#### 出处

- LG §2.1、§2.5：发射 → 弹起 0.200 s → 开拉 0.402 s；飞行 + 准备的拆分。main
- SW 第 2 轮、§7.1：飞行速度 2034.9 u/s、t0 0.0043 s；空中挂上也设 vz 200、水平不变。main
- GR §1 – §4：850 的来历（`mp_ability_grapple.txt:49-50`）、×2 模组、有效射程 830–840 u、打空不动。main
- GM10 TL;DR：挂上弹起 200（dedi setfile 读成 0、客户端 200，[hyb]；两边轨迹都是 193.7）、准备 = ConVar `grapple_pullDelay_human` 0.2、Jump Grapple 窗口、grapple hop、"地面发射清速度"。main
- M10A §1、§3、§8：地面发射不加规则的理由；hop 逐个对上；空中挂上跳没测。main
- FEEL §9.1；DIFF A-1；D-34、D-38：钩子从真实眼睛打出（70 / 64 / 32）。main
- N6 §1.3：别的传奇 `grapple_attachVerticalBoost` 0；地面开拉时 `grapple_initialImpulseOffGround` 把身体抬离地面。main
- TN6 §2.1、§2.2：Apex ConVar `grapple_shootVel` 2000、`grapple_autoAimAngle` 10°、`grapple_gracePeriod` 0.25 s（Ghidra 读的注册默认值）。main
- GN §2：钩子父实体 = 钩到的道具；世界几何上为空。main
- [反编译] 钩子父实体句柄 hook+0x148（`FUN_1405ac0e0(hook)`）；钩点 = 钩点数组（GrappleData +0x14，每个 12 字节）下标 min(点数 − 1, 2)，点数 +0x44。

---

### 5.26 拉的时候的速度规则

#### 原理

钩爪**不是钟摆**，是"沿绳子加速 + 把横着的速度刹掉"（M4b 的结论，D-03）。拉的速度有一个随时间爬升的目标：开拉时 50 u/s，1.5 s 内线性爬到 800 u/s。沿绳速度低于目标就很快追上去（1500 u/s²），高于目标就不管——所以带着速度进来的玩家不会被减速（P3"动量是玩家的资产"）。横着绳子的速度每秒刹掉 425 u/s，所以绕着钩点甩不起来；但**按方向键**时，沿按键方向的空中加速（650 u/s²）比刹车大，于是侧键、"Slingshot"能拉出比 800 更高的速度——这是钩爪的技巧上限，靠输入挣来的，不是白给的。

另外三条让钩爪"顺着重力"：拉动中重力只剩 1/4；绳子几乎朝正下方时重力全开；拉力**永远不往下推人**。所以跳起来再钩地面（Jump Grapple），上升的速度留着，越过钩点后重力帮忙，出口能到 1000 u/s 以上。

#### 规则和公式

拉动阶段的每一条命令（没有在 5.27 / 5.28 松开时），从 pre 状态算：

1. **目标速度**：t = now − 开拉时刻（第一条拉动命令 t = 0），

   S(t) = `rampMin` + (`rampMax` − `rampMin`) · clamp(t / `rampTime`, 0, 1)

2. **分解**：r̂ = (P − O) / |P − O|；v_r = v · r̂；横向 v_t = v − v_r · r̂。
   （拉力方向从原点量、指向钩点本身：M10 的 sl_hold 片段速度指向钩点偏差 < 4 u。脱钩规则用的绳子方向 d 在此基础上抬高 2 u，两者在拉动律里没有区别。原生拉力到底用哪个方向没有单独确认 [推断]。）
3. **沿绳**：v_r < S 时 v_r′ = min(S, v_r + `accel` · dt)；v_r ≥ S 时 v_r′ = v_r（不减）。
4. **横向刹车**（原生，D-34）：先把 v_t 里两部分**放到一边不刹**：
   - 向下的部分：v_t.z < 0 时取出 v_t.z（`grapple_dontFightGravity`）；
   - 沿三维瞄准方向 f 的正分量：k = v_t · f > 0 时取出 k · f。
   剩下的 v_t 大小减 `decel` · dt（不低于 0），再把放到一边的加回来。
5. **合成**：v′ = v_r′ · r̂ + v_t′。**不往下推**：v′.z < v.z 时 v′.z = v.z（拉力这一步不减竖直速度）。
6. **按键**（任何方向键，不只 W）：沿 ŵ 的分量 c = v′ · ŵ：c < cap 时 c′ = min(cap, c + `airAccel` · dt)，c ≥ cap 时 c′ = cap（压回上限）；v′ += (c′ − c) · ŵ。cap = `wishCap` × msc；`airAccel` **不乘** msc。拉动中身体自己的空中加速关掉（这一条代替它）。
7. **重力**：拉动中重力 × `gravityFrac`；绳子和正下方的夹角 < arccos(`gravityHelpCos`)（即 −r̂.z > 0.8）时重力 × 1。
8. **积分**：拉力看成这一条命令里的恒定加速度 a = (v′ − v) / dt，和重力一起按半步法积分（第 03 章）：v += (a − g_eff·ẑ) · dt/2；pos += v · dt；v += (a − g_eff·ẑ) · dt/2。
9. **贴地拉**：身体在地面高度、v′.z ≤ 0 时竖直速度和重力都置 0，身体沿地面滑过去，**不算落地**（R5 拉动中 ground 标志一直是 0，原生靠 `grapple_initialImpulseOffGround` 把身体抬离地面）。
10. **速度上限**：带 S21 钩爪的身体，水平速度上限放宽到 1100 u/s [设计]（Jump Grapple 实测出口 1000–1035 u/s，原来的 900 会削掉它）。R5 没有这条上限。
11. **卡住保护**：拉动超过 3.0 s 强制松开（`TIMEOUT`）[设计]。R5 最长的拉动 2.27 s（tether），正常情况下低速超时（5.27）先起作用。

原生还有几项，平时为 0 或 Pathfinder 不用，HSD 没做：目标速度乘 (1 − x)，x 是一个状态效果的强度（和摩擦里同一个查询，平时 0）[推断]；摆荡分支（`grapple_swing` = false，`grapple_swing*` 整套不用）；"看向钩点下方时加重力" `grapple_gravityPushUnderContribution` 2 [数据]，没测；绕障碍推开 `grapple_around_obstacle_accel` 1000 [TF2 数据]（TF2 代码里读到，Apex 有同名 ConVar），没测。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 斜坡起点 `rampMin`（`grapple_speedRampMin`） | 1.270 m/s | 50 u/s | 0.6944 H/s | — | [数据] SV §3.6 |
| 斜坡终点 `rampMax`（`grapple_speedRampMax`） | 20.32 m/s | 800 u/s | 11.11 H/s | 无输入拉动最高 796–804.6 u/s | [数据] [实测] |
| 斜坡用时 `rampTime` | — | 1.5 s | — | — | [数据] |
| 斜坡斜率（(800 − 50) / 1.5） | 12.70 m/s² | 500 u/s² | 6.944 H/s² | 实测 d\|v\|/dt 500.0–502.7（n 17） | [算] [实测] GM10 |
| 沿绳追赶 `accel`（`grapple_accel`） | 38.10 m/s² | 1500 u/s² | 20.83 H/s² | 实测前几条命令 1446–1559；ConVar 默认 1000 被 setfile 覆盖 | [数据] [实测] M10A §2 |
| 横向刹车 `decel`（`grapple_decel`） | 10.80 m/s² | 425 u/s² | 5.903 H/s² | M4b 拟合 423 | [数据] [实测] |
| 按键加速 `airAccel`（`grapple_airAccel`，不乘 msc） | 16.51 m/s² | 650 u/s² | 9.028 H/s² | M4b 实测 a·ŵ 645 ± 2 | [数据] [实测] |
| 按键上限 `wishCap`（`grapple_airSpeedMax`）× msc | 12.27 m/s | 420 × 1.15 = 483 u/s | 6.708 H/s | 实测 v·ŵ = 483.000（n 126） | [数据] [实测] SW §3.2 |
| 拉动中重力比例 `gravityFrac`（`grapple_gravityFracMin`） | — | 0.25（×） | — | `grapple_gravityFracMax` 0.7 从没见到 | [数据] [实测] |
| 拉动中重力（0.25 × 750） | 4.763 m/s² | 187.5 u/s² | 2.604 H/s² | 实测到 0.1 u/s² | [算] [实测] M10A §2 |
| 全重力的绳子角度 `gravityHelpCos`（`grapple_letGravityHelpCosAngle`） | — | 0.8（离正下方 36.87°） | — | — | [数据] [实测] M10A §2（越过钩点时 187.5 → 750） |
| 水平速度上限（带 S21 钩爪的身体） | 27.94 m/s | HSD 设计值 1100 u/s | 15.28 H/s | 必须 > 1035（Jump Grapple 出口） | [设计] |
| 卡住保护 `maxPullTime` | — | HSD 设计值 3.0 s | — | 必须 > 最长正常拉动 2.27 s | [设计] |

几个结果（用来判断实现对不对，都是 R5 实测）：

| 情形 | R5 | 依据 |
|---|---|---|
| 无输入拉墙，起点 250 / 400 / 700 u | 最高 474 / 612 / 804 u/s，拉动 0.85 / 1.12 / 1.55 s | [实测] M10A §3 |
| 空中 297 u/s 进入 | 保持约 297，直到 0.5 s 斜坡追上再跟斜坡 | [实测] M10A §2 |
| 按住 W | 沿视线水平分量正好 483.000，松开时 \|v\| 519.7 | [实测] SW §3.2、M10A §3 |
| 45–50° 拉动按 A / D | 最高 938–945 u/s（不按 796） | [实测] GM10 |
| Slingshot（转 80°，W+A → W+D），600 / 800 u 钩点 | 854 / 911 u/s | [实测] GM10 |
| Jump Grapple（700 u 地面钩，0.15 s 内按跳） | 出口水平 1000–1030 u/s（不跳 797） | [实测] GM10（30 次） |
| 按住 S | 拉得更快（740 对 612），原因没查清 | [实测] GM10、TN6 §2.3 |

#### 实现模板

```
// 单位：u、s。拉动阶段，这条命令的输入和移动倍率定下来以后（技能的 BeforeMoveLate）
t   = now - tPullStart
S   = rampMin + (rampMax - rampMin) * clamp(t / rampTime, 0, 1)
r   = normalize(P - O)
vr  = dot(v, r)
vr2 = vr < S ? min(S, vr + accel*dt) : vr
vt  = v - vr*r
aside = 0
if vt.z < 0:  aside.z = vt.z; vt.z = 0              // 向下的不刹（dontFightGravity）
k = dot(vt, f); if k > 0: aside += k*f; vt -= k*f    // 朝视线的不刹
vt  = vt * max(0, |vt| - decel*dt) / |vt|
nv  = vr2*r + vt + aside
if nv.z < v.z: nv.z = v.z                            // 不往下推
if hasMoveInput:
    w = flat(wishdir); c = dot(nv, w); cap = wishCap*msc
    c2 = c < cap ? min(cap, c + airAccel*dt) : cap
    nv += (c2 - c) * w
gScale = (-r.z > gravityHelpCos) ? 1 : gravityFrac
if onFloor and nv.z <= 0: nv.z = 0; v.z = 0; gScale = 0   // 贴地滑，不落地
a = (nv - v) / dt                                    // 交给电机，和重力一起半步积分
airAcceleration = 0                                  // 这条命令不做普通空中加速
```

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleAbility.PullStepS21`（纯函数，第 2 – 6 步）、`GrappleAbility.TargetSpeed`、`GrappleAbility.S21GravityScale`、`GrappleAbility.BeforeMoveLate`（第 7 – 9 步，写 `m.mods.externalAccel`、`m.mods.gravityScale`，把 `airAcceleration` 设 0）；电机 `U:…/R5MotorV2.cs` 的 `R5MotorV2.AirMove` 里 `mods.hasExternalAccel` 两个半步。参数 `GrappleS21Params`：`rampMin` 50、`rampMax` 800、`rampTime` 1.5、`accel` 1500、`decel` 425、`airAccel` 650、`gravityFrac` 0.25、`gravityHelpCos` 0.8、`dontFightGravity` true、`nativeCrossBrake` true、`targetHeight` 0；`GrappleParams.wishCap` 420；上限 `GrappleS21Params.HorizontalCeiling` 1100（`MovementConfig.cs` 给带钩爪的身体放宽 `rules.maxHorizontalSpeed`）；`GrappleParams.maxPullTime` 3.0。

平行保留（没选的版本，代码里都还在）：

| 版本 | 规则 | 怎么切回 | 结果 |
|---|---|---|---|
| **M10-A 拟合刹车**（pre-A-1） | 横向全部刹，但只在"这条命令的追赶能达到 S"或按着方向键时刹（四种门控开环比出来的） | `s21.nativeCrossBrake = false`（`brakeGated` true） | 72 个 R5 片段逐命令 rms 2.68 u/s（原生 2.08）；Slingshot 889 / 975 对 R5 854 / 911（+4 / +7 %） |
| **M4b RF 律**（M4 回放电机） | 沿绳 +541 u/s² 不封顶；横向刹 423 u/s²；只在横向部分加 0.68 g；钩点 + 31.9 u | `GrappleParams.R5Reference()`（`s21` 为空），`GrappleAbility.PullStep` | 62 个无输入片段开环 rms 11.8 u；只给回放基线用 |
| 原生刹车的变体（只做过逐命令检验，没进代码） | 一直刹 / 只有向下不刹 / 再加竖直上限 200 | — | rms 2.75 / 3.15 / 3.43 u/s，都比原生差 |

#### 验收

- 单元测试（都在 `GrappleParams.Measured()` 上跑，也就是 M10-A 拟合刹车；**原生刹车 `nativeCrossBrake` 没有单元测试**，见 `_notes/hb-ch05.md`）：
  - `GrappleM10ATests.NoInputWallPullFollowsTheRamp`：700 u，0.1–1.4 s 内 \|v\| 和 min(800, 50 + 500t) 差 ≤ 12 u/s；最高 804.5 ± 10、拉动 1.55 ± 0.03 s、`NEAR` 松开。
  - `GrappleM10ATests.SlingshotAnchorHoldReachesTheRamp`、`GrappleM10ATests.AFasterEntryIsKeptUntilTheRampCatchesUp`、`GrappleM10ATests.ARopeThatPointsDownLeavesTheRiseToQuarterGravity`。
  - `GrappleM10ATests.HoldingWClampsTheWishComponentAt483`：松开时水平 483.0 ± 0.01。
  - `GrappleM10ATests.SideKeysDuringTheSlingshotPullAddSpeed`：941 ± 5 %。
  - `GrappleM10ATests.TheSlingshotInputsBeatTheNoInputPull`：854 / 911 ± 8 %，比不按高 > 40 u/s。
  - `GrappleM10ATests.OvershootUnderTheHookWhileLookingAtItKeepsPulling`、`GrappleM10ATests.AGroundHookDragsAlongTheFloorWithoutLanding`（不落地，600 ± 12 u/s 松开）。
  - `GrappleTests.PullStepTerms`、`GrappleTests.CrossSpeedIsBrakedNotSwung`、`GrappleTests.PullHasNoTerminalSpeedAndReleaseIsBallistic`（RF 律，回放电机）。
  - `SkillComboTests.CeilingClipsALongGrapplePull`。
- 对照数据：
  - 逐命令检验：72 个 M10 片段，用 R5 自己的前一状态推下一条命令，原生刹车 rms 2.08 u/s（hold_w 0.12、crouch 0.21、g200_j2 0.04）（FEEL §9.1）。
  - 开环对照：M10A §3 的表（同一个起始状态、同一套逐命令输入、记录下来的钩点），注意那张表是 M10-A 拟合刹车的数。
  - 手感对照：`FeelBatch` 喂 M4 的 4 个往墙上拉的片段（5.27 验收）。
- 合格线：无输入拉动的沿绳速度和 S(t) 差 ≤ 1 条命令的斜坡（4.2 u/s）；按住 W 的 v·ŵ = 483.000 ± 0.01；无输入片段最高速度和 R5 差 ≤ 2 %；侧键 / Slingshot 差 ≤ 8 %（现在的测试容差）。
- 已知差距：
  - **p0**（钩点在眼睛高度，绳子约 5° 朝上）：R5 728 u/s，HSD 608（−16.6 %），M10-A 时的数；当时 HSD 从 60 打钩，改成眼高 70 以后**没有复核**（M10A §8；Grapple/README"已知差异"）。
  - hold_d / dbounce / rodeo_d（贴墙、近距离横穿）低 8–11 %，M10-A 时的数。
  - Tether / rodeo 绕圈：HSD 绕 313°（GN 后），R5 393°（R5 一直贴着岩石底面刮，而且本地 dedi 不执行视线规则）。绕圈是侧键 + 转视角自然产生的，没写死。
  - 按住 S 为什么更快：R5 和 TF2 方向相反，没查清（TN6 §3）。

#### 出处

- P2 §1.2、§5 P-01 – P-04：目标速度 lerp(50, 800, t/1.5)、(1 − x)、沿绳 / 横向分解、刹车 425、侧键走 `AirMove` 的 650 / 420。main
- FEEL §9.1；DIFF A-1；D-34：原生横向刹车（向下和朝视线的部分不刹），逐命令 rms 表。main
- M10A §1、§2、§3、§8、§9：拉动律怎么从数据读出来、开环对照、1100 上限 [设计]、p0 等缺口。main
- GM10 TL;DR、"Model for HSD"：没有摆荡（`grapple_swing` false）、斜坡实测、侧键 / Slingshot / Jump Grapple、`grapple_letGravityHelpCosAngle` 0.8、`grapple_dontFightGravity` 1。main
- SW TL;DR、§3.2、§7.3、§7.5：不是钟摆、RF 律、W 夹在 483.000。main
- SV §3.6：setfile 值。main
- TN6 §2.3：TF2 / Apex 拉动同一套；`gravityPushUnderContribution` 2；ConVar `grapple_accel` 1000 被 setfile 1500 覆盖。main
- TN2 §1.3：绕障碍 1000（TF2 `server.dll`）。main
- D-03（M4b：钩爪不是钟摆）。main
- [反编译] `Grapple_SpeedRamp` 0x1406752b0；`Grapple_PullAccel` 0x1406755c0（非摆荡分支；朝视线的方向来自虚函数 +0x9a0，[推断]：拟合认出是三维视线）；`AirMove` 0x140a48f90 读 `grapple_airAccel` / `grapple_airSpeedMax`。

---

### 5.27 自动脱钩：接近、视线、远离、低速（D-50 原生）

#### 原理

钩子什么时候自己松开，决定了钩爪"到头"的手感。原则是**松开不改速度**：除了按键松开（5.28）以外，所有自动脱钩都原样保留动量，之后就是普通的抛物线（P3）。四条自动规则各管一种"该结束了"的情况：

1. **快到钩点了**：离钩点 33 u 以内一定松开；接近得越快，提前得越多（最多 50 u）。高速冲向墙时提前松开，人带着速度贴到墙上，而不是被拉进墙里。
2. **钩点跑到视线背后**（"看别处就脱钩"）：钩点离开视线 90° 就松开。这让玩家能主动用转头来结束拉动，也让"从钩点旁边飞过去"自然结束。
3. **正在高速远离钩点**（> 500 u/s）：只对钩在世界几何上的钩子生效。
4. **拉不动了**：朝钩点的速度一直 ≤ 250 u/s，1.5 s 后松开，防止卡在障碍物后面。

用户 10-28 定："钩爪这一块全部按原生的去做"（D-50）。所以下面全部是原生规则，旧版留开关可切回。

#### 规则和公式

从挂上起每条命令检查（接近规则在准备阶段也查；其余只在拉动阶段查）。哪一条成立，这一条命令就松开，**这一条命令不再加拉力**，速度原样保留：

1. **接近**（拉动律之前检查）：dist = min(\|P − O\|, \|P − E\|)，E 用当前眼高。v_r = v · d̂。

   松开 ⇔ dist < `detachLengthMin`，或 dist < `detachLengthMax` 且 dist < `detachLengthMin` + (v_r / `detachRampMax`) · 1.5 · (`detachLengthMax` − `detachLengthMin`)

   都是严格小于。阈值随接近速度变大：v_r ≥ 266.7 u/s 时阈值封顶 50 u；远离时（v_r < 0）阈值低于 33 u。
2. **绳子过长**：dist > 最大长度 + `grapple_detachExtraAllowedLength`（256 u）。射程 850 u，拉动中到不了 1106 u，HSD 不做。
3. **视线**（只在拉动阶段，挂上 0.2 s 以后）：d · f < 0（钩点在三维视线 90° 以外）就松开。
   - 往下看（f.z < 0）时还要求：d 的水平部分、以及 (P − E) 的水平部分，都在水平前方 f_h 的**后面**（点积 < 0）。
   - 原生另有两条 HSD 没做：慢动作（`AirSlowMo` < 1）时只在远离钩点时查；速度向上且和某个向量同向更陡时豁免（那个向量没认出来，测过的片段都没触发）。
   - **混合构建**：这条规则只在 S21 客户端有，本地 S3 dedi 没有。D-13：Reference 跟 S21 客户端。
4. **远离**：−v_r > `detachAwaySpeed`（平方比较）。**只在钩点是世界几何时**（钩子没有父实体）；钩在道具 / 绳子上时关掉。原生远离脱钩时还会把 vz 最多加到 200（`grapple_detachVerticalBoost` / `MaxSpeed` 200 / 200）——测过的片段从没触发，HSD 不做。
5. **低速超时**：v_r ≤ `lowSpeed` 的命令算"慢"，从拉动开始前一直算"好"。从最后一条"好"的命令起，超过时限就松开。
   - 原生时限：锁定近战目标 1.0 s；脚下有地面实体时 0.7 s（沿墙跑时 1.2 s）；摆荡 0.2 s；否则（空中）1.5 s。
   - R5 拉动中身体一直离地（ground = 0），所以**实际一律 1.5 s**；碰到墙或被天花板顶住也不改。HSD 拉动中一律 1.5 s。
   - 量的是**朝绳子的径向速度**，不是速率：绕着钩点横飞、贴着挡板横移（\|v\| 大、径向小）也会超时。
6. 不松开的情况：**落地不松开**（贴地滑，5.26 规则 9）；**碰到墙不松开**（R5 贴着墙继续拉）；**拉动中按跳不松开**（R5 测过，跳键被拉动吞掉，第 06 章）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 接近一定松开 `detachLengthMin` | 0.8382 m | 33 u | 0.4583 H | — | [数据] [反编译] |
| 接近阈值上限 `detachLengthMax` | 1.270 m | 50 u | 0.6944 H | 实测地面贴过钩点 45.0–47.1 u（≈ 600 u/s） | [数据] [反编译] [实测] N6 §1.2 |
| 接近斜坡除数 `detachRampMax`（ConVar `grapple_speedRampMax_human`） | 10.16 m/s | 400 u/s | 5.556 H/s | pre-GN 800 | [反编译] 注册默认 "400" |
| 接近斜坡系数 | — | 1.5（×） | — | — | [反编译] |
| 阈值封顶的接近速度（400 × 17 / 25.5） | 6.773 m/s | 266.7 u/s | 3.704 H/s | pre-GN 533.3 u/s | [算] |
| 绳子方向起点高度 `ropeBase`（h + 1，h = 22） | 0.5842 m | 23 u | 0.3194 H | h 换成 0 / 36 / 69 时视线规则只差 0–3 条命令 | [反编译] [实测] Frida GN §3 |
| 绳子方向终点抬高 `ropeLift`（ConVar `grapple_lift`） | 0.635 m | 25 u | 0.3472 H | — | [反编译] 注册默认 "25" |
| 视线角 | — | 90°（d · f < 0） | — | 客户端实际在越过 90° 后 0.025–0.084 s 松开（转 180 °/s 时 94–108°） | [反编译] [实测] N6 §1.2 |
| 远离速度 `detachAwaySpeed` | 12.70 m/s | 500 u/s | 6.944 H/s | 只确认了开关条件，没直接看到它脱钩 | [数据] [反编译] |
| 绳子过长余量 `grapple_detachExtraAllowedLength` | 6.502 m | 256 u | 3.556 H | HSD 不做（碰不到） | [数据] TN6 §2.4 |
| 低速线 `lowSpeed`（`grapple_detachLowSpeedThreshold`） | 6.35 m/s | 250 u/s | 3.472 H/s | 设置块下标是推断 | [数据] [推断] N13 §2 |
| 低速时限（空中，拉动中实际用的） `lowSpeedTime` | — | 1.5 s | — | 实测开拉 → 脱钩 1.508–1.517 s | [数据] [实测] N6 §1.3 |
| 低速时限：地面 / 沿墙 / 近战 / 摆荡 | — | 0.7 / 1.2 / 1.0 / 0.2 s | — | 拉动中碰不到（ground 一直 0）；没单独测 | [数据] [反编译] |
| 远离脱钩的竖直上抬 `grapple_detachVerticalBoost` / `MaxSpeed` | 5.08 m/s | 200 / 200 u/s | 2.778 H/s | 从没触发；HSD 不做 | [数据] [反编译] |

**旧版（pre-GN）和现在**（每条一个开关，`SetGnDetach(false)` 一次切回，输出和改前逐字节相同）：

| # | 开关 | 现在（= R5 原生） | 旧版（pre-GN，M10-A 定、N7 改过一次） | 影响 |
|---|---|---|---|---|
| G-1 | `nativeProxDistance` | min(\|P − O\|, \|P − E\|)，准备阶段也查 | 到线段 [O, O + 72] 的距离（准备阶段 ≤ 45 u） | 往墙上拉晚 1 条命令松开 |
| G-2 | `detachRampMax` | 400 u/s | 800 u/s | 只在接近速度 267–533 u/s 时不同；测过的片段不在这个区间 |
| G-3 | `nativeRopeDir` | 视线、接近斜坡、远离都按 d 量 | 视线从 O + 70 量，速度朝 O + 36 量 | 视线离开、rodeo 脱钩时刻不变；钩点很高（仰角约 50°）时仰着头转 180° 不再松开 |
| G-4 | `nativeLowSpeed` | v_r ≤ 250 计时 | \|v\| < 250 计时 | 绕钩点横飞、贴挡板横移现在会超时 |
| #7 | `nativeLowSpeedTimer` | 拉动中一律 1.5 s | 碰墙 / 天花板 1.2、地面高度 0.7、其余 1.5 | N6 天花板：1.200 → 1.500–1.508 s（R5 1.508–1.517） |
| G-5 | `awayOnlyWorldHooks` | 远离只对世界钩点 | 一直生效 | 测过的片段都没触发 |

更早的 M10-A 版（`nativeDetach = false`）还有一条"越过钩点"规则（远离钩点且钩点在视线 85° 以外，`passViewAngle` 85）和 100° 的视线规则；N6 查清"越过钩点" = 接近规则 + 视线规则，Reference 把 `passViewAngle` 设成 NaN、视线改成 90°（`MovementConfigs.NativeGrapple()`）。

#### 实现模板

```
// 单位：u、s。每条命令，在拉动律之前（BeforeMove）；返回 null = 继续
d    = (P + (0,0,ropeLift)) - (O + (0,0,ropeBase))
vr   = dot(v, d) / |d|
dist = min(|P - O|, |P - E|)                         // E = O + 当前眼高
near = dist < Lmin or (dist < Lmax and dist < Lmin + vr/rampDiv * 1.5 * (Lmax - Lmin))

if phase == Windup and near: return "NEAR"           // grapple hop
if phase != Pulling: return null
if crouchPressed: return "CROUCH"                    // 5.28
if near:
    if impactBoost and not hookOnEntity and v.z < 300: v.z = min(v.z + 300, 300)   // 5.29，默认关
    return "NEAR"
if not hookOnEntity and -vr > awaySpeed: return "AWAY"
behind = dot(d, f) < 0
if behind and f.z < 0:
    behind = dot2(d, f_h) < 0 and dot2(P - E, f_h) < 0
if behind: return "LOOK_AWAY"
if vr <= lowSpeed:
    if lowSince is none: lowSince = now
    if now - lowSince >= lowSpeedTime: return "LOW_SPEED"
else: lowSince = none
return null
```

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleAbility.DetachS21`（顺序同上）、`GrappleAbility.NearS21`、`GrappleAbility.NearThreshold`、`GrappleAbility.RopeDir`、`GrappleAbility.RadialSpeed`；准备阶段的接近检查在 `GrappleAbility.BeforeMove`。开关和值在 `GrappleS21Params`：`nativeDetach` true、`detachLengthMin` 33、`detachLengthMax` 50、`detachRampMax` 400、`detachAwaySpeed` 500、`ropeLift` 25、`ropeBase` 23、`lowSpeed` 250、`lowSpeedTime` 1.5、`lookAwayAngle` 90（G-3 打开时只看是不是 NaN，NaN = 关掉视线规则）、`passViewAngle` NaN，和上表 6 个开关；`SetGnDetach(bool)`、`GnDetach`。游戏 Esc 菜单 "Grapple detach rules (GN)"（PlayerPrefs `hsd.gn.grapple`，0 = 旧版；演示和 smoke 固定原生）；`FeelBatch` / `CameraFeelBatch` 加 `-preGn` 跑旧版。松开原因写在 `lastReleaseReason`，事件 `GRAPPLE_RELEASE_<原因>`。

离散化要注意：低速计时 HSD 从第一条"慢"的命令开始数、用 ≥ 时限；原生从最后一条"好"的命令数、用 > 时限。两者差 1 条命令以内，N6 天花板片段 HSD 1.500–1.508 s 对 R5 1.508–1.517 s。

#### 验收

- 单元测试：
  - `GnGrappleTests.ReferenceHasTheNativeRulesAndTheArchiveSwitchesBack`：Reference / Fun 6 个开关都开、`detachRampMax` 400、`ropeLift` 25、`ropeBase` 23、`impactBoost` 关；`SetGnDetach(false)` 全部回去。
  - `GnGrappleTests.G1WallPullReleasesLaterThanTheSegmentDistance`：仰 10° 拉墙，原生比线段距离晚 1–2 条命令，都是 `NEAR`。
  - `GnGrappleTests.G5AwayRuleOnlyOnWorldHooks`：800 u/s 远离时世界钩点 `AWAY`、道具钩点不是；旧版两种都是。
  - `GnGrappleTests.G4StrafingAcrossTheRopeTimesOutAtTheAirLimit`：横移约 480 u/s，1.5 ± 0.02 s `LOW_SPEED`；旧版不超时。
  - `GnGrappleTests.N7PinnedUnderTheCeilingTimesOutAfterTheAirTime`：天花板下 1.5 ± 0.02 s；旧版 < 1.3 s。
  - `GnGrappleTests.G3RopeDirectionIsTheHookTwoUnitsAboveTheOrigin`。
  - `N7NativeReferenceTests.GrappleUsesTheNativeDetachRules`：视线 90°、没有"越过钩点"、33 / 50。
  - `GrappleM10ATests.LookingAwayReleases`（M10-A 版 100° 规则：0.575 ± 0.03 s、331 ± 12 u/s；关掉视线规则就是 `NEAR`）。
- 对照数据（`FeelBatch`，`research/rea-native/gn/scenarios_gn.json` 的 R5 岩石，`gn_compare.py`）：

  | 片段 | R5 脱钩命令 / 最高点 | HSD 现在 | 旧规则 + 旧场景（改前） |
  |---|---|---|---|
  | M4 hold 1701 | 244 / 155.3 u | 245 / 155.7 u | 241 / 145.0 u |
  | M4 hold 1702 | 243 / 154.9 u | 245 / 155.7 u | 241 / 145.0 u |
  | M4 near 2101 | 201 / 117.3 u | 202 / 116.3 u | 199 / 111.3 u |
  | M4 near 2102 | 201 / 116.8 u | 202 / 116.6 u | 199 / 111.8 u |
  | 视线离开 ×4：脱钩（按 Q 后） | 客户端规则 1.067–1.075 s | 1.058 s | 同 |
  | rodeo ×8 | 客户端规则 0.473–0.500 s | 0.450–0.465 s | 同 |
  | N6 天花板 ×8：开拉 → 脱钩 | 1.508–1.517 s | 1.500–1.508 s | 1.200–1.208 s |

- 合格线：往墙上拉的脱钩命令和 R5 差 ≤ 2 条、最高点差 ≤ 1.0 u；视线离开 / rodeo 比客户端规则早 ≤ 0.04 s（≤ 5 条命令）；天花板超时 1.5 ± 0.02 s；回放电机基线逐字节不变（`rud_check.py`，第 11 章）。
- **A-1 和"看别处脱钩"的结论**（FEEL §10、N13 §1）：
  - F7 看到的"R5 视线离开到 1.5 s 还挂着"是**本地 dedi 的假象**：dedi 没有视线规则，客户端每 0.05–0.1 s 被重新挂上，dedi 自己 1.5 s 低速超时才放。R5 客户端自己在 1.067–1.075 s 脱钩，和 Unity 同一时刻。
  - 钩爪横滚峰值也一样：混合版本 19.2°，只有客户端 12.75–13.0°，Unity 12.8°（横滚规则见第 07 章 §3.8）。对照时 R5 的参照要用 `look_split.py --write` 切出来的"只有客户端"版本（`camera_client.csv`）。
  - A-1 剩下的 1 条命令出在对照场景（岩石形状只用两个平面近似）和拉力近似，不在规则：同一个新场景用旧规则就已经是 244 / 244 / 202 / 202。
- 没验证过的：G-2（需要 267–533 u/s 的慢速贴近）、G-4 的绕钩横飞、远离 > 500 实际脱钩——都没有 R5 片段，只有单元测试。

#### 出处

- N13 §2（逐条规则表）、§3（逐条对照）、§5（G-1 – G-6、S-1、S-2、F-1 建议）：接近距离算法、斜坡 400、视线规则、低速量径向速度、时限的选择。main
- GN §1 – §5：D-50 的实现、h = 22（Frida 读玩家 +0x1de8）、钩子父实体、#7、前后对照。main
- N6 §1：调用链、Frida 15 / 15 次视线脱钩、贴地接近 45.0–46.7 u、"越过钩点" = 接近 + 视线、低速超时 1.5 s 的第四次场景。main
- P2 §1.3、§5 P-05 – P-10、§8：参数表和对账。main
- GM10 TL;DR "Detach rule"：M10 的五条（接近 35–53 u、越过、蹲、按键、视线 [hyb]）。main
- DIFF GN 节；D-13、D-50。main
- FEEL §10、§10b：F7 横滚对照、GN 的手感对照工具。main
- DESIGN-PHILOSOPHY §10.3：视线规则客户端有、dedi 没有；"挂到 1.5 s"。main
- [反编译] 钩爪更新 0x140670ff0 → 拉动这一步 `Grapple_DetachSpeedLoss` 0x14066fb60（返回 1 = 脱钩；接近分支 0x14066fe4c）→ 脱钩规则 `Grapple_DetachRules` 0x14066f600；`Grapple_DetachLength` 0x140a3ce80；绳子方向 0x140672580 → 0x140674a90；h = 玩家 +0x1de8；`grapple_lift` 默认字符串 0x14167887c；`grapple_speedRampMax_human` 默认 "400" 0x1416658a4；1.5 常数 0x1417f8588；视角前方 0x1423735dc、水平前方 0x142373600 [推断]、豁免向量 0x142373684（没认出）；GrappleData 字段 `m_grapplePulling` +0x49、`m_grappleSwinging` +0x4a、`m_grappleMeleeTarget` +0x64、`m_grappleHasGoodVelocity` +0x6c、`m_grappleLastGoodVelocityTime` +0x70；眼睛 = 虚函数 +0x6c8 [推断]。

---

### 5.28 按键脱钩、按蹲脱钩，和脱钩以后

#### 原理

玩家有两个主动结束的办法：**按蹲**（干净地松开，速度不变，接着落地就能滑铲）和**再按一次技能键**（松开，但速度太快时扣掉一截）。第二种是 Apex 加的收费口子：自动脱钩保留全部速度，而手动"空中刹车"超过 460 u/s 时要付 300 u/s 的代价，避免玩家拉到最高速随时随地精确松手（P3"收走动量必须有写得出的规则"）。

松开以后就是普通的空中移动：速度原样、重力恢复 1 倍、空中加速恢复（第 03 章）。松开**不是起跳**：不开 lurch 窗口（第 06 章）。

#### 规则和公式

1. **按蹲**：拉动中按下蹲，这一条命令松开（`CROUCH`），速度不变。按住蹲落地接滑铲（第 04 章）。
2. **第二次按技能键**（拉动中）：这一条命令松开（`MANUAL`）。\|v\| > `releaseSpeedMin` 时：

   \|v\| ← max(`releaseSpeedMin`, \|v\| − `releaseSpeedLoss`)，方向不变（三维速度整体缩放）

   \|v\| ≤ 460 时速度不变。
3. **飞行 / 准备中再按技能键**：取消，不拉（`CANCEL`），扣基础冷却 [设计]。R5 没测。
4. 第二次按键 R5 有 0.5 s 防抖（`detachOnGrapple` true，[数据] TN6 §2.4）；**HSD 没有防抖**。
5. **拉动中按跳**：不松开（R5 M4 / M4b 测过），拉动把跳键吞掉（第 06 章）。
6. **被别的动作打断**：上滑索、进传送门、被更新的技能顶掉时结束（`INTERRUPT`），速度交给那个动作（第 06 章）。
7. **脱钩以后**：速度原样保留，之后是普通抛物线（g = 750 u/s²、v_h 不变直到撞墙）。69 次松开里松开那一条命令速度连续到 0.005 u/s。
   - 原生另有 `grapple_detachHorizontalMaxSpeed` 600 u/s 和"脱钩后重力 × 0.5（速度 ≤ 200 u/s 时）"两组值。实测脱钩 800–1030 u/s 都没被削，`detachGravityTime` = 0 时脱钩后重力规则不生效 [数据]。它们在哪个分支用没读，HSD 不做。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 按键脱钩扣速 `releaseSpeedLoss`（`grapple_detachSpeedLoss`） | 7.62 m/s | 300 u/s | 4.167 H/s | — | [数据] [实测] |
| 扣速下限 `releaseSpeedMin`（`grapple_detachSpeedLossMin`） | 11.68 m/s | 460 u/s | 6.389 H/s | 实测 580 → 458.7、675 → 458.5（下一条命令的重力） | [数据] [实测] GM10 |
| 第二次按键防抖 | — | 0.5 s | — | HSD 没做 | [数据] TN6 |
| 脱钩水平上限 `grapple_detachHorizontalMaxSpeed` | 15.24 m/s | 600 u/s | 8.333 H/s | 实测脱钩没被削；用在哪没读 | [数据] SV §3.6 |
| 脱钩后重力 `grapple_detachGravityScale` / `Speed` / `Time` | — | 0.5 / 200 u/s / 0 s | — | Time 0 = 不生效 | [数据] |

#### 实现模板

```
// 单位：u、s。BeforeMove 最前面
if tacticalPressed and phase in {Flying, Windup, Pulling}:
    if phase == Pulling:
        s = |v|
        if s > releaseSpeedMin: v *= max(releaseSpeedMin, s - releaseSpeedLoss) / s
        release("MANUAL")
    else:
        phase = Idle; event CANCEL; chargeBaseCooldown()     // [设计]
    return
// 按蹲在 5.27 的检查里最先判断（"CROUCH"）
// release(reason): phase = Released；这一条命令不加拉力；重力和空中加速恢复
```

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleAbility.BeforeMove`（第二次按键）、`GrappleAbility.DetachS21`（按蹲）、`GrappleAbility.Interrupt`、`GrappleAbility.End`；`AcceptsPressWhileActive`（`ISecondPressAbility`，`SkillArbiter` 不把这次按键当成新技能）。参数 `GrappleS21Params.releaseSpeedMin` 460、`releaseSpeedLoss` 300、`crouchReleases` true；`GrappleParams.secondPressReleases`（游戏配置由 `AdvancedMovementParams.grappleManualRelease` 打开；M4 回放关）、`jumpReleases` false。

平行保留：M6-G 版的第二次按键（GZ §1）"速度原样保留、不扣"——S21 规则关掉（`s21` 为空）时就是这个行为，只在回放电机 / 旧配置里。

#### 验收

- `GrappleM10ATests.CrouchReleasesAndKeepsTheMomentum`：`CROUCH`，202 ± 8 u/s，没有扣速。
- `GrappleM10ATests.TheSecondPressClampsAbove460`：0.9 s 按（226 u/s）不变；1.6 / 1.8 s 按（580 / 675 u/s）变成 460 ± 0.5。
- `A3Zipline.SecondGrapplePressReleasesWithTheMomentumKept`、`A3Zipline.ManualReleaseIsOffInTheReplayGrapple`、`A3Zipline.ReleasePressIsNotRefusedWithNoChargeLeft`、`A3Zipline.UseMountDuringAGrapplePullEndsTheGrapple`。
- `GrappleTests.JumpDoesNotRelease`；`LurchM8BTests.AGrappleReleaseOpensNoWindowButTheAirJumpAfterItDoes`；`M10AGameTests.ReleaseIsNoJumpAndLandsIntoASlide`；`SkillComboTests.GrappleReleaseIntoSlideAndSlideJumpStayBounded`；`RiftM10WTests.AGrapplePullIntoAPortalEndsThePull`。
- 对照数据：M10 rel_t09 / t12 / t16 / t18（HSD 223 / 373 / 574 / 671 对 R5 225 / 376 / 580 / 675，M10A §3）；SW §5 松开前后速度连续（55 次，0.005 u/s）。
- 合格线：按键扣速后 \|v\| = 460 ± 0.5（快于 460 时）；按蹲松开前后速度差 < 0.01 u/s；松开后第一条命令是纯抛物线（差 < 0.01 u/s）。

#### 出处

- GM10 TL;DR "Detach rule" (c)、(d)：按蹲、第二次按键、580 → 458.7、675 → 458.5。main
- GZ §1：第二次按键在按下那一条命令松开（延迟 0）；攻击键不松开。main
- SW TL;DR、§5：松开保速、松开后是抛物线；跳键不松开。main
- LG §2.1：拉动中按跳没有效果。main
- SV §3.6：`detachSpeedLoss` / `Min`、`detachHorizontalMaxSpeed`、`detachGravity*`。main
- TN6 §2.4：`detachOnGrapple` 0.5 s 防抖、`detachGravityTime` 0 不生效。main
- [反编译] `Grapple_DetachSpeedLoss` 0x14066fb60（脱钩时的速度处理）；`Gravity_HalfStep` 0x140a36130（`grapple_detachGravity*`）。

---

### 5.29 撞上上抬（G-6）：R5 算了但没用，HSD 默认关

#### 原理

原生代码里有一条"钩爪拉到头撞上时，把人往上送一下"的规则（竖直速度抬到 300 u/s）。TF2 里它确实起作用（拉到墙时人被送高一截）。但在 R5 里它**算出来了却被丢掉**：客户端拉动那一步把竖直速度写成 300，同一条命令的移动却从写之前的速度开始算，录像里人一次都没跳起来。

按"尽量贴合 R5 实际移动"的原则，HSD **默认关**；因为它是原设计里存在的手感（TF2 有），做成一个**可选开关**留着（用户 10-29："关留客选项开关"，D-52）。打开它就不是 R5 了。

#### 规则和公式

**选中的版本（默认，= R5 实际移动）**：接近脱钩那一条命令，竖直速度只受重力，没有上抬。

**平行保留的版本（开关打开，= R5 客户端代码，不是 R5 实际移动）**：接近脱钩（5.27 规则 1）成立的那一条命令，同时满足：正在拉动（不在准备阶段）、钩点是世界几何（不是道具 / 绳子）、vz < `impactBoostMax`：

  vz ← min(vz + `impactBoostSpeed`, `impactBoostMax`)

- vz ≥ 300 时不动；是"设到上限"，不是累加。
- 这一条命令就松开了，所以每次拉最多一次。
- 原生代码没有"在地上不加"的条件，打开后地面钩也加（GN 版曾经加过一个地面条件，是推断，G6 去掉了）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 撞上上抬 `impactBoostSpeed`（`grapple_impactVerticalBoost`） | 7.62 m/s | 300 u/s | 4.167 H/s | 默认不用 | [数据] [反编译] |
| 上抬上限 `impactBoostMax`（`grapple_impactVerticalMaxSpeed`） | 7.62 m/s | 300 u/s | 4.167 H/s | — | [数据] [反编译] |
| R5 实际：世界墙接近脱钩那条命令 vz | — | 185.1 → 178.9 u/s（只减重力） | — | Frida：拉动那一步里 185.1 → 300，移动又从 185.1 开始 | [实测] G6 §4.2 |
| R5 实际：脱钩后 1 s 内比脱钩点高（ww400_p5 / p0 / spr） | 0.4953–0.5334 / 0.0254 / 0.6960–0.7620 m | +19.5–21.0 / +1.0 / +27.4–30.0 u | 0.2708–0.2917 / 0.0139 / 0.3806–0.4167 H | 上抬生效时应 ≥ +50 u | [实测] G6 §4.1（8 条录像） |
| TF2：空中拉到墙时 vz | — | 约 288 u/s（= 300 − 一帧重力） | — | TF2 本地私服客户端和服务端同一个程序 | [TF2 实测] TN6 §2.4 |

两边都写清楚：

| | R5 代码（客户端拉动那一步） | R5 实际移动 | HSD 现在（默认） | HSD 开关打开 |
|---|---|---|---|---|
| 世界钩点接近脱钩 | vz → min(vz + 300, 300) | 没有上抬 | 没有上抬 | vz → min(vz + 300, 300) |
| 道具 / 绳子钩点 | 不加 | 没有 | 没有 | 不加 |

为什么被丢掉没追到：可能是 ProcessMovement 准备 movedata 时又拷了一次速度，也可能钩爪更新在另一份 movedata 上跑 [推断]；钩爪更新返回后整个速度 ×0.62–0.68 的缩放也一起被丢掉了，来源可能是 `GrappleAnimSelectSequence` [推断]。DESIGN-PHILOSOPHY §10.3 把它记为"是不是混合构建造成的没定"。

#### 实现模板

```
// 在 5.27 的接近规则成立、返回 "NEAR" 之前
if impactBoost and phase == Pulling and not hookOnEntity and v.z < impactBoostMax:
    v.z = min(v.z + impactBoostSpeed, impactBoostMax)
```

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleAbility.DetachS21` 的接近分支；`GrappleS21Params.impactBoost`（所有配置默认 `false`）、`impactBoostSpeed` 300、`impactBoostMax` 300。`SetGnDetach` 不改它，`-preGn` 也不上抬。打开：游戏 Esc 菜单 "Grapple impact boost (G-6)"（只在原生钩爪规则下显示；PlayerPrefs `hsd.g6.impact`，1 = 开，默认 0；演示和 smoke 固定关）；`FeelBatch -impactBoost`；代码里设 `impactBoost = true`。

#### 验收

- `GnGrappleTests.G6ImpactBoostIsOptInAndOnlyOnWorldHooks`：仰 10° 拉世界墙——关：松开那条命令 vz 只减（只有重力）；开：vz 比关时高 > 50 u/s、≤ 300；钩在道具上：开了也和关一样。
- `GnGrappleTests.ReferenceHasTheNativeRulesAndTheArchiveSwitchesBack`：Reference 默认关，`SetGnDetach` 不动它。
- 对照数据：G6 §4.1 的 8 条录像（世界墙 x −11921.5，`ww400_p5` ×4、`ww400_p0` ×2、`ww_spr` ×2；地面钩 `g400_spr` ×2），`wall_detach.py`；Frida `frida_impact_out.json`。
- 合格线：默认配置下 `FeelBatch` 105 个录像的游戏身体输出和 GN 版逐字节相同（D-52 回归）；世界墙接近脱钩那条命令 dvz = −g·dt（−6.25 u/s）。
- 没做的对照：打开开关以后的 Unity 对 R5 世界墙片段（方向已经清楚：Unity 会多一下上抬，R5 没有）。

#### 出处

- G6 §1 – §5、§7：原生条件、世界墙片段、Frida 只有客户端的读数、Unity 开关。main
- GN §2、§6：钩子父实体决定开关条件；地面钩 Frida vz 299 但轨迹不跳。main
- N13 §1（3、3b）、§4：撞墙那一下 +12 u/s 不是上抬，是岩石面后倾 1.86°；6 次道具钩点都没有上抬。main
- TN6 §2.4、§2.7：TF2 里撞上上抬生效（约 288）。main
- DIFF G6 节、二节 G-6 行；D-51（先关着、待定）、D-52（定为默认关 + 可选开关）。main
- DESIGN-PHILOSOPHY §10.3。main
- [反编译] `Grapple_DetachSpeedLoss` 0x14066fb60 接近分支 0x14066fe4c；父实体判断 `FUN_1405ac0e0(hook)` / hook+0x148；`GrappleAnimSelectSequence` 0x140b0dea0（脱钩后拿速度拷贝处理再写回，×0.62–0.68 可能来自这里 [推断]）。

---

### 5.30 次数和冷却

#### 原理

Apex 钩爪一次就用完，冷却按"这次飞了多远"算：近距离点一下 10 s，长距离大位移最多 30 s。拉完以后高速飞行的那一段也算进距离。这把钩爪限制成"偶尔一次的大位移"（对照 TF2：两次、每次约 12 s，5.31），对应 DESIGN-PHILOSOPHY P9"威力换代价"的思路。

#### 规则和公式

1. 一格充能（弹匣 300），每次使用扣 drain，按每秒 10 回复：冷却 = drain / 10 s。
2. 从挂上起记录水平路程 d：钩爪还在用（飞行 / 准备 / 拉动）或者 \|v\| > 500 u/s 时每 0.1 s 累加一次；最多记 5 s；上滑索立刻停止记录。
3. drain = min(300, 100 + floor(300 · clamp((d − 300) / (4500 − 300), 0, 1)))。
   d ≤ 300 u：10 s；d = 1700 u：20 s；d ≥ 3100 u：30 s。
4. 记录结束那一刻开始计冷却。
5. 发射了但没挂上（飞行 / 准备中取消或被打断）：扣基础 100 → 10 s [设计]。R5 没测。
6. S21 以后的 Apex 版本改成两次、固定 20 s，HSD 不用。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 基础扣量 `drainBase` / 弹匣 `clip` / 回复 `regen` | — | 100 / 300 / 10 每秒 | — | — | [数据] 脚本 `mp_ability_grapple.nut`、武器 .txt |
| 距离下限 `drainMinDist` | 7.62 m | 300 u | 4.167 H | — | [数据] 脚本 |
| 距离上限 `drainMaxDist` | 114.3 m | 4500 u | 62.5 H | — | [数据] 脚本 |
| 冷却到 30 s 的距离 | 78.74 m | 3100 u | 43.06 H | — | [算] |
| 计距速度线 `trackSpeed` | 12.70 m/s | 500 u/s | 6.944 H/s | — | [数据] 脚本 |
| 计距间隔 / 最长 `trackPoll` / `trackTime` | — | 0.1 s / 5 s | — | — | [数据] 脚本 |
| 冷却 | — | 10 – 30 s | — | — | [算] |

#### 实现模板

```
// 单位：u、s
on attach: track = true; d = 0; t0 = now; last = O; next = now
every command while track:
    if zipline mounted this command: stop()
    if now >= next:
        next += 0.1
        if (not active and |v| <= 500) or now - t0 > 5: stop(); continue
        d += |flat(O - last)|; last = O
stop(): d += |flat(O - last)|; cooldown = min(300, 100 + floor(300*clamp((d-300)/4200,0,1))) / 10; ready = now + cooldown
```

Unity 参考实现：`U:…/Abilities/Grapple/GrappleAbility.cs`，`GrappleS21Params.CooldownFor`、`GrappleAbility.StartTracking` / `Track` / `StopTracking` / `NoAttachCooldown`、`ChargeReadyTime`（`IChargeTimer`）；Pathfinder S21 预设的槽位 `scriptCooldown: 1`。别的预设（Pathfinder-Octane、Valk-Horizon、Ash route）用固定 8 s 冷却 [设计]。

#### 验收

- `GrappleM10ATests.TheScriptCooldownGoesFrom10To30SecondsWithDistance`：0 / 300 → 10 s，1700 → 20 s，3100 / 4500 / 9000 → 30 s。
- `GrappleM10ATests.ThePathfinderSlotUsesTheScriptCooldown`；`M10AGameTests.ThePathfinderPresetAndTheS21GrappleOnEveryGrappleBody`。
- 合格线：公式逐值相等。R5 没有直接实测冷却时长，只有脚本 [数据]。

#### 出处

- M10A §1（Cooldown 行）、§8 第 6 条（跳板二段跳结束信号没建模）、§9（没挂上扣 10 s [设计]）。main
- TN6 §2.5：TF2 / Apex 次数和冷却对照；S21 之后的版本。main
- SV（武器 .txt：`grapple_power_required` 100、`regen_ammo_refill_rate` 10）。main
- [数据] `mp_ability_grapple.nut`（`GrappleDecreaseAmmo`）。

---

### 5.31 和 TF2 钩爪的区别（平行保留：只有规格，没实现）

#### 原理

TF2 的钩爪是 Apex 钩爪的原型：拉动规则（斜坡 50 → 800 / 1.5 s、横向刹车 425、方向键 650 / 420、重力系数、脱钩阈值）是同一套代码、同样的数。区别在**出手、挂上那一下和次数**：TF2 钩子快、射得远、挂上不弹、能连拉两次，拉到头会被减速并向上送一下；Apex 钩子慢、近，挂上先弹 200，拉到头保速，按距离罚冷却。手感上 TF2 是"连续、快出手"的机动工具，Apex 是"一次性的大位移"。

HSD 现在的钩爪就是 Apex 原生规则，不因 TF2 改。TF2 版作为**平行保留**记下来：要做"TF2 手感的钩爪预设"只需要换出手、挂上、次数三处，拉动和脱钩原样复用。要不要做没定（TN6 §3 的建议是"现在不急"；D-65 的扩展道具清单里钩爪写的是"不做（已按 Apex 做）"）。

#### 规则和公式

和 Apex（5.25 – 5.30）不同的地方：

| 项 | Apex（HSD 现在） | TF2（平行保留） | 依据 |
|---|---|---|---|
| 挂上竖直 | vz 设成 200 | 下坠速度留 40 %（`initialSlowFracVert_human` 0.4）：−292 → −108、−688 → −221 | [TF2 实测] TN2 §1.2 |
| 挂上水平 | 不变 | 大部分保留（400 → 358、700 → 558） | [TF2 实测] |
| 起步 | 斜坡从 50 起，1500 追赶 | 离地 vz ≈ 50（`initialImpulseOffGround` 50），水平约 75 起爬；同几何到墙反而比 Apex 慢 0.26–0.43 s | [TF2 实测] TN6 §2.7 |
| 拉力追赶 | 1500 u/s² | 1000 u/s² | [TF2 数据] |
| 接近脱钩 | 保速，不弹 | 总速度削到约 458（快于 760 时少 250–300），vz 变成 +190–220 | [TF2 实测] TN6 §2.7（10 次） |
| 撞上上抬 | 默认关（5.29） | 生效，vz 约 288 | [TF2 实测] |
| 拉动中按跳 | 不松开 | 立刻松开，普通跳（vz 296） | [TF2 实测] |
| 第二次按键 | 松开 + 460 扣速 | 没有这个键 | [TF2 数据] |
| 按后退 | 拉得更快（740 对 612） | 明显减速（523 对 648） | [实测] [TF2 实测]，原因没查清 |
| 侧键多出的速度 | +18–28 % | +2–4 % | [实测] [TF2 实测]，原因没查清 |
| 次数 | 1 次，10–30 s | 能量 100、一次 50（两次），3 s 后约 4.05 /s 回复（每次约 12 s） | [TF2 实测] |
| 钩到窗户附近 | `grapple_windowCheckDist` 150 还在，是否生效没查 | 送你穿过窗户（窗户辅助，HSD 第 05 章跑墙部分 / TN2 §2） | [TF2 数据] |

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 钩子飞行速度 `grapple_shootVel` | 76.20 m/s | 3000 u/s | 41.67 H/s | 实测 660 u 0.424 s、1060 u 0.556 s（÷ 3000 + 0.2） | [TF2 数据] [TF2 实测] |
| 射程 | 27.94 m | 1100 u | 15.28 H | — | [TF2 数据] |
| 拉力追赶 `grapple_accel_human` | 25.40 m/s² | 1000 u/s² | 13.89 H/s² | — | [TF2 数据] |
| 挂上竖直保留 `initialSlowFracVert_human` | — | 0.4（×） | — | 实测 35–40 % | [TF2 数据] [TF2 实测] |
| 离地冲量 `initialImpulseOffGround_human` | 1.270 m/s | 50 u/s | 0.6944 H/s | Apex 同值 | [TF2 数据] |
| 接近脱钩后的总速度 | 11.63 m/s | 约 458 u/s（`detachSpeedLossMin` 460） | 6.361 H/s | 403–417 水平 + 189–218 竖直 | [TF2 实测] |
| 一次扣的能量 / 满能量 | — | 50 / 100 | — | — | [TF2 数据] |
| 能量回复 | — | 约 4.05 /s（3 s 后开始） | — | 满条约 25 s | [TF2 实测] |

#### 实现模板

无：HSD 没有实现 TF2 钩爪预设。如果要做，TN6 §3 列的改法是：钩子速度 / 射程 3000 / 1100；挂上弹起关、竖直留 40 %；地面发射不清水平速度（Apex 本来也不清，见 5.25 规则 6）；拉力 1000、起步约 75（不用 350 的初速）；接近脱钩总速度削到 460（快时减 300）+ 竖直上抬约 200；侧键多出的速度按实测调小；两次、每次约 12 s；第二次按键脱钩关；按跳立即脱钩（普通跳）。拉动律（5.26）和其余脱钩规则（5.27）原样复用 `GrappleS21Params`。

#### 验收

无：没有实现，就没有测试。将来做的话，对照数据是 TF2 的同几何补测（TN6 §2.7，`runtime/data/20261029_092610_night_grapple_match`，250 / 400 / 700 u 平视拉墙、仰 20°、W / S / A / D、转 45°、冲刺 / 滑铲中发射）和空中拉（TN2 §1，`night_grapple3`）。

#### 出处

- TN6 §1 – §3：对照表、同几何补测、TF2 预设的改法。main
- TN2 §1：TF2 钩爪实测（`mp_lf_stacks`，144 fps）和读代码看到的规则（绕障碍、脱钩阈值同形、钩敌人自动近战、宽限、窗户）。main
- D-65（扩展道具清单：钩爪"不做（已按 Apex 做）"）。main
- [TF2 数据] TF2 `server.dll` 钩爪移动 0x18016fa80、脱钩 0x180610390、窗户调整 0x18016dd00 / 搜索 0x1806079b0。

---

---

## 第四部分 · 跳板（§5.32 – §5.36）

读的版本：研究仓库 main `86ec5f1`；研究 PR #85 分支 `rj/knockback-a` `a0ac420`；参数对照表 `handbook/tables` `0d04dcf`；HSD-Unity main `17260f2`；HSD-Unity PR #52 分支 `rj/knockback-a` `6f7ea2d`。

**白话说明（这一部分管什么）**

这一部分写两类"别人给你的速度"：

1. **跳板**（Octane 的 Launch Pad，地图上的固定跳板也是同一个东西）：踩上去，原来的速度整个作废，换成一个固定大小、固定角度的弹射速度；飞行过程按 0.8 倍慢放；飞行中可以再按一次跳（跳板二段跳）；飞到天花板下面可以贴着天花板滑（天花板滑行）；落地很重，会被硬着陆降速吃掉大半水平速度。
2. **爆炸击退**（火箭跳）：爆炸把人沿"爆点 → 身体中心"推开，大小按距离线性衰减，和原来的速度**相加**，总速度有上限；站在地上时太小的推力不起作用；被推之后有一小段时间地面摩擦失效。

两者的区别是本部分最重要的一句话：**跳板是"替换"，击退是"相加"**。跳板不走引擎的冲量队列，所以没有"击退后不减速"的窗口；击退走，所以有。

顺带写一个很短的**兴奋剂**（Stim）条目。它不是外力，只改移动倍率（§5.36），放这里只因为它和跳板同属 Octane。

和别的章的分界：

- 硬着陆降速的通用规则在第 03 章 §3.9（落地），本部分只写跳板落地特有的数和发现。
- lurch 窗口规则在第 03 章；跳板会不会开窗口、二段跳怎么重开窗口写在这里，规则本身指过去。
- 动量规则（冲量队列、谁覆盖谁、冷却共享、HSD 的速度天花板）只写本节要用的，**详见第 06 章**。
- 镜头（二段跳 punch D-68、跳板二段跳 F7 的 1.2° 凸起）在第 07 章。
- 爆炸伤害、武器手感在第 09 章；这里只写 EPG 推人的部分。

**本部分出处缩写**

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

**记号**

- **引擎速度**：模拟里存的速度（R5 日志、Unity `R5MotorV2.vel`）。跳板慢放飞行中，屏幕上看到的速度 = 引擎速度 × 0.8，看到的重力 = 750 × 0.8² = 480 u/s²。本部分表里的速度**都是引擎速度**，除非写"看到的"。
- ĥ：水平单位向量；ẑ：竖直向上单位向量。
- msc：移动倍率（空手 1.15，第 03 章）。
- H = 72 u（参考身高，01 §4）。

---

### 5.32 跳板发射

#### 原理

跳板的手感是"不管你怎么上来，都飞同一条弧线"：走着上、冲刺上、漂着上，发射速度完全一样；原来的速度整个作废。这样关卡设计只要知道跳板在哪、玩家往哪个方向走，就能算出落点。唯一能改变弧线的是**蹲**：蹲着上跳板，弹射角从约 63° 压到 45°，飞得更低、更远。方向跟着"踩上去那一刻的运动方向"，不看视角也不看按键，所以玩家可以背着跳板倒着走上去，照样往运动方向飞。

它对应 DESIGN-PHILOSOPHY P3 的一个**有意例外**：P3 说动量是玩家的资产，跳板却把它整个收走。这是写得出条件的一条规则（"踩上跳板 = 换速度"），所以不违背 P3；但它也意味着跳板不能用来"叠速度"，叠速度要靠击退（§5.37）。

#### 规则和公式

1. **触发体**：跳板是一个竖直圆柱触发体，半径 r = 32 u，从跳板面往上 32 u、往下 16 u。身体碰撞体半径 16 u。**一条命令开始时**，身体原点到跳板轴的水平距离 ≤ r + 16 = 48 u、且脚的高度在 [跳板面 − 16, 跳板面 + 32] 内，这条命令发射 [实测] [数据]。
   - 实测：发射那条命令开始时离跳板中心 47.5 u（sd 0.45）[实测]。
   - 跳着越过跳板不会触发：脚在 48 u 范围内时离地 32.6–34.3 u，超过上沿 32 u（M4 `pad_jumpin` 5 / 5 没触发）。要"跳上跳板"，得落在跳板上或跳板前一点 [实测]。
2. **冷却**：发射后 1.0 s 内不再发射。原生里这个冷却是**玩家身上的一个字段**（不是跳板的），重力炮检查同一个字段，所以跳板和重力炮共用这 1 s [反编译]。1.0 s 和 SDK 一致性代码的值相同 [数据]；R5 里没有测过 [没测过]。
3. **相位中不弹**：Wraith "虚空"相位中的身体不被跳板弹起（D-19 E-1）[反编译] [实测 N8-D 3 / 3]。
4. **方向**：ĥ = 踩上那一刻**水平速度的方向**（不是视角、不是按键）[实测 M10，9 次]：
   - 视角朝北、按 D 往东走 → 往东；视角朝后、按 S 往前退 → 往前；松开按键漂过去（170 u/s）→ 沿漂移方向 63.4°。
   - **完全没有水平速度时竖直向上**（normalize(0 + 2ẑ)）[推断]：R5 没在正好 0 速度下测过；社区资料说"不按前进就竖直向上"。HSD 照这个做。
5. **竖直权重**：V = `JUMP_PAD_VERT_OVERRIDE` = 2.0；蹲着（下蹲状态 1 或 2）V × `jumppad_vert_override_ducked_scalar`。蹲着的倍率**在归一化之前**乘，所以蹲着是 45°、水平更快，不是"竖直减半"。
   - 倍率的值：本地生效 0.5 [实测：M4 / M10 蹲着 45°]；S21 客户端原生默认 1 [反编译 N4A]；0.5 来自本地 SDK dedi [hyb]。正版 S21 服务端用哪个没法测。HSD 用 0.5（和实测一致）。
6. **发射速度**：v = `push` · normalize(ĥ + V·ẑ)，`push` = `JUMP_PAD_PUSH_VELOCITY` 1150。**替换整个速度**（水平和竖直都替换）[实测：三种接近速度 92 / 199.5 / 299 输出相同]。发射后离地、清掉地面实体。
   - 升级 `PAS_ULT_UPGRADE_ONE` 时 × 1.2（R5 实测 1377.8 / 1378.2）[数据] [实测]；这个升级在 S21 哪一级没查到，HSD 两套配置都关。
7. **同一条命令的积分**：发射替换速度发生在这条命令开头的半步重力**之后**，所以发射这条命令只扣结束时的半步重力（在慢放的 dt' 上，§5.33）：发射后记录到的 vz = 1028.59 − ½·750·0.8·dt（120 Hz 时 1026.09）[实测 R5 1026.086；Unity 同]。
8. **发射之后**：打开慢放飞行（§5.33）；0.1 s 后给一次跳板二段跳（§5.34）；Reference **不开** lurch 窗口（D-10，M9 实测：跳板后反向按键只有普通空中加速，|Δv| 3.3 u/s），Fun 开（M5.5 的"跳板 → lurch"，[设计]）。如果起跳后才碰到跳板，起跳自己的 lurch 窗口会带过发射（HSD 模型，R5 没测，M10-C O-5）。lurch 规则见第 03 章，窗口叠加见第 06 章。
9. **跳板不走冲量队列**：原生发射函数没有写冲量事件，所以**没有**"冲量后不减速"的窗口（§5.38 那条规则不适用于跳板）[反编译]。旁证：M4 蹲着上跳板滞空 2.69 s，落地后地面减速照常 1250 u/s²；如果走队列，窗口有 1150 × 0.003 = 3.45 s，落地时应当还在减速为 0 的那段 [实测 + 算]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 推力 `push`（`JUMP_PAD_PUSH_VELOCITY`） | 29.21 m/s | 1150 u/s | 15.97 H/s | 升级 × 1.2 = 1380（实测 1377.8） | [数据] [实测] |
| 竖直权重 `vertOverride`（`JUMP_PAD_VERT_OVERRIDE`） | — | 2.0（×） | — | — | [数据] [实测] |
| 蹲着竖直权重倍率 `duckedVertScale` | — | 0.5（×，本地生效）；S21 客户端原生默认 1 | — | 0.5 – 1 | [实测] [反编译] [hyb] |
| 站着发射：水平 / 竖直 | 13.06 / 26.13 m/s | 514.30 / 1028.59 u/s（63.43°） | 7.143 / 14.29 H/s | 实测 514.309 / 1028.586（sd 0.001） | [算] [实测] |
| 蹲着发射：水平 / 竖直 | 20.65 / 20.65 m/s | 813.17 / 813.17 u/s（45°） | 11.29 / 11.29 H/s | 实测 813.181 / 813.165 | [算] [实测] |
| 没有水平速度：竖直 | 29.21 m/s | 1150 u/s（90°） | 15.97 H/s | R5 没测 | [推断] |
| 触发圆柱半径 `radius` | 0.8128 m | 32 u | 0.4444 H | — | [数据] `sh_jump_pads.gnut` |
| 触发圆柱上沿 / 下沿 `above` / `below` | 0.8128 / 0.4064 m | 32 / 16 u | 0.4444 / 0.2222 H | 上沿实测：脚高 32.6 u 不触发 | [数据] [实测] |
| 发射距离（r + 碰撞体半径 16） | 1.219 m | 48 u | 0.6667 H | 实测 47.5 ± 0.45 u | [算] [实测] |
| 冷却 `debounce`（玩家级，和重力炮共用） | — | 1.0 s | — | R5 没测 | [反编译] [数据] |
| 二段跳授予延迟 | — | 0.1 s（脚本）；实测 0.108 s | — | 见 §5.34 | [数据] [实测] |

**HSD 现在的做法和 R5 不一样的地方**（两边都写；第 1、2 条是hb-ch05 写本章时新查出来的，见 `_notes/hb-ch05.md`）：

1. **竖直速度天花板会削掉"竖直向上"的 1150**。HSD 技能层每条命令、每次发射都把向上速度夹到 `SkillRules.maxUpSpeed`：默认 1100 u/s [设计]（注释写"按跳板 1028.6 定"，那是 M10 加"竖直向上"之前定的）；带跳板二段跳的 Octane 预设抬到 `PadDoubleJumpParams.UpCeiling` 1250 u/s [设计]。所以**不是 Octane 的身体踩地图跳板、又正好没有水平速度时，发射是 1100 不是 1150**（事件 `LAUNCH_CLAMPED`），最高点 810.3 u 而不是约 885 u。R5 没有这个天花板。另外升级 × 1.2 的竖直向上 1380 会被 1250 削（默认关，碰不到）。水平天花板 `maxHorizontalSpeed` 900 u/s 对跳板碰不到（蹲着 813；× 1.2 蹲着 975.8 会被削，默认关）。
2. **冷却是每个跳板能力各一份，不是玩家级**。HSD 的 `JumpPadAbility.debounceUntil` 属于一个能力实例：Octane 自己放的跳板和地图跳板是两个实例，各算各的 1 s；HSD 没有重力炮。R5 是玩家身上一个字段、跳板和重力炮共用。实际影响很小（1 s 内连踩两个不同来源的跳板），R5 也没测过。
3. **地图跳板的二段跳只给 Octane 预设**；R5 里任何人踩跳板都能二段跳（§5.34）。

#### 实现模板

```
// 单位：u、s。在这条命令的移动之前，用命令开始时的位置
on command(now, dt):
    if now >= padCooldownUntil and not phasedInVoid:
        for pad in pads:
            dxy = horizontalDistance(pos, pad)
            dz  = pos.z - pad.z
            if dxy <= padRadius + hullRadius and -padBelow <= dz <= padAbove:
                h = horizontal(vel)
                h = |h| > 0 ? h / |h| : (0, 0)                     // 没有水平速度 → 竖直向上
                V = vertOverride * (ducked ? duckedVertScale : 1)
                d = (h.x, h.y, V)
                launch = push * pushScale * d / |d|
                // 这条命令：先做开头的半步重力，再用 launch 替换整个速度
                vel = launch
                grounded = false; groundEntity = none
                padCooldownUntil = now + 1.0                      // R5：玩家级，重力炮共用
                slowMo = true                                     // §5.33
                padDoubleJump.grant(launchTime = now)             // §5.34
                lurchWindow: 不开（Reference）/ 开（Fun）         // 第 03 章
                break
    move(dt * (slowMo ? 0.8 : 1))                                  // 只剩结束时的半步重力
```

离散化要注意：

- 判定用**命令开始**的位置，不是扫过的路径：所以在 120 Hz 下实际发射点在 47.5 u 左右（每条命令走 2.5 u，299 u/s）。
- 发射替换速度要放在开头半步重力之后。放在之前，发射后第一帧的 vz 会少 2.5 u/s，和 R5 对不上。
- 方向用的是**这条命令开始时**的水平速度。按键、视角都不参与。

Unity 参考实现：

- `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/JumpPad/JumpPadAbility.cs`：`JumpPadParams`（`push`、`vertOverride`、`duckedVertScale`、`radius`、`hullRadius`、`above`、`below`、`slowMoScale`、`debounce`、`pushScale`、`straightUpWithoutMotion`、`phasedNoLaunch`、`launchOpensLurchWindow`，全部 [u]）；`JumpPadAbility.BeforeMove`（判定、方向、发射、冷却）、`JumpPadAbility.Touches`（触发圆柱）、`JumpPadAbility.AfterMove`（落地结束慢放）。
- 发射公式：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/_Core/InstantImpulse.cs`，`InstantImpulse.PadLaunch`。
- Octane 设置：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/JumpPad/OctaneParams.cs`（`padStraightUpWithoutMotion` 默认 true、`madHops` Reference false / Fun true、`airborneAgility` 只是标志、`padPushScale` 1）。
- 发射怎么落到速度上：`AbilityContext.Launch` → `SkillArbiter.AfterAbilities`（按优先级挑一个发射、`Clamp` 按 `SkillRules.maxHorizontalSpeed` / `maxUpSpeed` 夹）；天花板在 `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/_Core/SkillRules.cs`，Octane 抬高在 `MovementConfig.Apply`。
- 配置开关（`HSD-Unity: Assets/HSD/R5Replay/Runtime/MovementConfig.cs`）：`padLaunchOpensLurchWindow`（Reference false，Fun true，D-10）、`padPhasedNoLaunch`（Reference true，D-19）、`octane`。
- 回放用的"跳板套件"（没有配置的 `new JumpPadAbility()`）没有速度时用**视角方向**（M4 的旧规则），`straightUpWithoutMotion` = false。

#### 验收

- 单元测试（`Assets/HSD/R5Replay/Tests/Editor/`）：
  - `JumpPadTests.LaunchFormula`（`R5MotorM4AbilityTests.cs`）：站着 514.296 / 1028.591，蹲着 813.173 / 813.173，没有方向 1150 竖直，差 ≤ 1e-3 u/s。
  - `JumpPadTests.ApproachLaunchSlowMoFlightAndHardLanding`：发射命令开始时离中心 ≤ 48 u、> 45.4 u；接近速度被丢掉；发射后 vz = 1028.591 − ½·750·0.8·dt。
  - `JumpPadTests.DebounceAndDuckedLaunch`：蹲着 45°；冷却内不发射。
  - `OctaneM10CTests.PadLaunchFollowsTheDirectionOfMotionNotTheViewOrTheKeys`、`OctaneM10CTests.PadLaunchesStraightUpWithoutMotionAndFlatWhenCrouched`（`R5MotorM10CTests.cs`）：方向 = 运动方向；没有速度竖直 1150；蹲着 45°、813.17。
  - `OctaneM10CTests.UpgradesAreConfigurableAndOffInTheS21Reference`：× 1.2 只作用于预设自己的跳板，1380。
  - `PadLurchM10DTests.TheReferencePadLaunchOpensNoLurchWindowAndFunKeepsIt`（`R5MotorM10DTests.cs`）；`OctaneM10CTests.APreJumpWindowSurvivesTheReferencePadLaunch`。
  - `SkillComboTests.StimDoesNotScaleThePadLaunch`（`R5MotorM5SkillTests.cs`）：兴奋剂不改发射速度。
- 对照数据：M4 15 次发射（OCT §3.1，`research/phase2-local/m4/octane/results.json`）；M10 21 次（站着 1147.76 @ 63.38°，蹲着 1148.23 @ 44.91°，这是半步重力之后的合速度，OCT-M10 TL;DR）；手感对照第 3 批跳板 87 / 90 项一致（FEEL §7）。
- 合格线：发射后第一帧的速度和公式（扣半步重力后）差 < 0.01 u/s；角度差 < 0.1°；接近速度不影响输出。
- 没测过的：冷却 1 s；正好 0 速度时的方向；空中触发（M8 只测过"起跳后落到跳板上"的 jump-in，发射和站着相同）。

#### 出处

- NP2 §3、§5 F-01 – F-03、§7：发射公式、蹲着倍率、不写冲量队列、和重力炮共用的玩家级 1 s 冷却。main
- OCT §3.1、§3.6、§3.7、§6 第 1 – 2 条：15 次发射的拟合、触发距离 47.5 u、跳着越过不触发、M4 的 Unity 原件、没测的项。main
- OCT-M10 TL;DR "Pad launch / Pad direction / Pad × 1.2"：方向 = 运动方向、升级 × 1.2。main
- M10C-U §4、§10 第 4 – 6 条：竖直向上 [推断]、升级、组合。main
- N4A §3、NR §4.4：`jumppad_vert_override_ducked_scalar` 客户端原生 1、本地 0.5 [hyb]。main
- NT §5、§6 T-04：冲量队列和低减速窗口（跳板是否走队列，NP2 §3 回答了：不走）。main
- DEC D-10（Reference 跳板不开 lurch 窗口）、D-19 E-1（相位中不弹）。main
- `research/phase2-local/m9/r_d1/D1.md`：跳板后不开 lurch 窗口的实测（M10C-U、JumpPad README 引用）。main
- FEEL §7：第 3 批技能对照（跳板 87 / 90）。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/JumpPad/README.md`：已知差异（地图跳板二段跳只给 Octane）。main
- [反编译] `JumpPad_Launch` 0x140a38a90（SDK 名）；玩家重复发射冷却字段 player+0x350（跳板写，`GravityCannon_Launch` 0x140a3af30 读）；[数据] `sh_jump_pads.gnut:346`（触发上沿 32）、`jumppad_parity.cpp:61-66, 573-643`（SDK 一致性代码）。

---

### 5.33 跳板飞行：慢放、空中、落地

#### 原理

跳板飞行是"慢动作"：整段飞行按 0.8 倍的时间走，看起来更飘、更好调整，滞空 3.4 s。规则上它不改速度，只改时间：重力、积分、空中加速全部按 0.8·dt 算。所以"跳多高"和不慢放完全一样，只是慢了；"飞多远"也一样（同样的引擎速度和重力，轨迹相同，只是走得慢）。

落地很重：跳板落地的竖直速度约 1025 u/s，远超硬着陆降速的起点 772 u/s，水平速度当场只剩约 24 %，速度上限也被压到约 28 %、1 s 内平方恢复。这让"跳板 → 落地马上接着跑"没有速度可带，想保速度就得在空中做别的（二段跳、天花板、钩爪、滑索）。

#### 规则和公式

1. **慢放**：从发射那条命令到落地那条命令（含）为止，移动用 dt' = 0.8·dt：重力、位置积分、空中加速都在 dt' 上 [实测：位置步长 / (v·dt) = 0.80001，sd 0.00007；Δvz / dt = 600.27 = 750 × 0.8004]。落地后下一条命令起恢复 1.00。
   - 0.8 这个值在原生里的来源（网络字段 `m_airSlowMoFrac` 或 setfile）**没读到** [推断]；setfile 的 `airSlowMoSpeed` 是 0.15，不是它（N4A）。
   - 实现上：**速度保持引擎单位，缩时间，不缩速度**。落地规则（第 03 章 §3.9）是按引擎 vz 定义的，缩速度会让降速算错。
2. **看到的轨迹**（[算]，给关卡用）：看到的发射速度 920 u/s，看到的重力 480 u/s²。站着：最高 705 u（离散后实测 707.8 u），滞空 3.43 s，同高落地约 1411 u（实测 1412）。蹲着：最高 439–443 u，滞空 2.69–2.70 s。竖直向上（HSD 推断的规则）：最高 881.7 u（离散 885.5 u），滞空约 3.83 s。
3. **空中控制**：飞行中照常空中加速（第 03 章），只是在 dt' 上 [推断]：M4 飞行中没有给左右键，**R5 没测过空中转向**。按住 W 有一个解释不了的小增益（d|h|/dt ≈ −0.19 + 0.00184·vz u/s²，整段飞行 +0.6 – 1.4 u/s，< 0.3 %），不做 [实测]。
4. **落地**：落地那条命令仍在 dt' 上，然后慢放结束。硬着陆降速照第 03 章 §3.9：f0 = clamp(1.996467 − 1.6714 × 10⁻⁶ · vz², 0, 1)，水平速度 × f0，之后移动倍率 1 s 内平方恢复 [实测]。跳板的典型值：
   - 站着发射落地 |vz| ≈ 1025 u/s → f0 ≈ 0.24（514.3 → 约 124.6 u/s，移动倍率最低约 0.28）[实测]。
   - 蹲着发射落地 |vz| ≈ 798 u/s → f0 ≈ 0.93（移动倍率最低约 1.07）[实测]。
   - 跳板二段跳之后落地 |vz| 可到 1336 u/s → f0 = 0，当场停下 [实测，§5.34]。
5. **落地马上再跳**（M4b，12 次）：落地后第 4 条命令起跳，起跳的超速削减给 max(R, v − 100)，R = `sprintspeed` × 当时的移动倍率（260 × 0.28 = 72.6 u/s）；这里 v − 100 < R，结果就是 R（03 §3.8 第 5 条；回放电机的旧写法 min(v, R) 在这里数值相同（hb-integrate 11-14 按 hb-ch06 备注改）），高度是连跳惩罚的最低档（frac 0.3）。**跳板速度只带走约 14 %** [实测]。起跳夹速度的规则在第 03 章。
6. **软着陆结束降速**（M4b 新发现）：落地马上跳的那一下小跳落地时（|vz| ≈ 144 u/s，本身不触发降速），**降速直接结束**，移动倍率下一条命令就回到 1.15（10 / 12；另 2 / 12 落在 1.1347 / 1.146，原因不明）[实测]。"硬着陆后小跳一下"因此是最快的恢复办法（约 0.43 s 回满，不用等 1 s）。**HSD 没做这一条**（见下）。
7. **HSD 的保护**：技能层给跳板一个 6.0 s 的"效果最长时间"（`SkillRules` traits `jump_pad` maxEffect 6.0）：慢放超过 6 s 还没落地就强行结束慢放（事件 `PAD_INTERRUPT_TIMEOUT`）[设计]。正常飞行 3.4 s 碰不到；只有"站在跳板上原地一直弹"这种情况才碰到。R5 没有这条。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 慢放倍率 `slowMoScale` | — | 0.8（×） | — | 实测 0.80001 ± 0.00007 | [实测]（原生来源没读到） |
| 慢放中的重力（引擎速度每真实秒） | 15.24 m/s² | 600 u/s²（750 × 0.8） | 8.333 H/s² | 实测 600.27 | [实测] [算] |
| 看到的发射速度（站着） | 23.37 m/s | 920 u/s | 12.78 H/s | — | [算] |
| 看到的重力 | 12.19 m/s² | 480 u/s²（750 × 0.8²） | 6.667 H/s² | — | [算] |
| 站着发射最高点 | 17.98 m | 707.8 u（Unity 707.92） | 9.831 H | 公式 705.3 | [实测] [算] |
| 站着发射水平飞行距离（同高） | 35.87 m | 1412 u（Unity 1412.5） | 19.61 H | 公式 1411 | [实测] [算] |
| 站着发射滞空 | — | 3.433 – 3.440 s（Unity 3.433） | — | — | [实测] |
| 蹲着发射最高点 | 11.15 – 11.25 m | 439 – 443 u | 6.10 – 6.15 H | — | [实测] |
| 蹲着发射滞空 | — | 2.693 – 2.701 s | — | — | [实测] |
| 蹲着发射水平飞行距离（同高） | 约 44.6 m | 约 1754 u | 约 24.4 H | 没直接量 | [算] 650.5 u/s × 2.697 s |
| 竖直向上最高点 | 22.40 m（Unity 22.49） | 881.7 u（Unity 885.5） | 12.25 H | R5 没测 | [算] [推断] |
| 站着落地的 f0 | — | ≈ 0.24（×） | — | 实测 0.2397 – 0.2427 | [实测] |
| 落地马上再跳带走的水平速度 | 1.844 m/s | 72.6 u/s（≈ 14 %） | 1.008 H/s | 12 次 0.140 – 0.141 | [实测] |
| HSD 跳板效果最长时间（maxEffect） | — | HSD 设计值 6.0 s | — | 必须 > 最长飞行 | [设计] |

**关卡尺度表 LS-24 为什么比公式低**（hb-tables 留的问题，hb-ch05 写本章时查清了；在 HSD-Unity `units/switch` 5c79a50 的同一套程序上复跑）：

- LS-24 用的装备是 Wraith S21。站着不动没有水平速度，按 HSD 的规则竖直向上 1150，但**技能层的向上天花板 1100 u/s 把它削到 1100**（`LAUNCH_CLAMPED`），第一次发射最高 810.3 u（= 1100²/1500 + 离散 3.7 u）。
- 程序没有落地：身体落回时脚离跳板 ≤ 32 u 就又触发（冷却 1 s 早过了），一直弹到 20 s 循环结束（输出的 airtime 正好 20 s 就是这个原因）。第二次以后是在离跳板约 20–30 u 的高处（命令开始时）再发射，最高点也跟着高一截（第二次 839.5 u），20 s 里的最大值 841.28 u 就是这样来的，不是一次干净的发射。中间 6 s 时 maxEffect 还把慢放切掉了一次。
- 换成 Octane S21 预设（天花板 1250）：第一次发射 vz = 1150，最高 885.5 u（= 881.7 + 离散 3.8 u），和公式对上。
- 所以 LS-24 低不是跳板规则，是 HSD 的设计天花板 + 测试程序。建议 LS-24 改用 Octane 预设、只取第一次发射，写 885.5 u；或保留 Wraith 并注明"被 1100 天花板削"。

#### 实现模板

```
// 单位：u、s
on command(now, dt):
    dtMove = slowMo ? slowMoScale * dt : dt       // 时钟照常走 dt，只有移动积分用 dtMove
    preVz  = vel.z
    move(dtMove)                                  // 重力、积分、空中加速都在 dtMove 上
    if slowMo and landedThisCommand:
        slowMo = false                            // 落地这条命令已经用了 dtMove
    if landedThisCommand:
        hardLandingSlowdown(preVz)                // 第 03 章 §3.9（用引擎 vz）
    if slowMo and now - launchTime >= 6.0:        // HSD 保护，R5 没有
        slowMo = false
```

Unity 参考实现：慢放 `JumpPadAbility.BeforeMove` 每条命令写 `CommandModifiers.timeScale` = `slowMoScale`；`R5MotorV2.Move` 里 `dt = realDt * mods.timeScale`（时钟照走真实 dt）；落地降速 `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/LandingSlowdown/LandingSlowdown.cs`（`LandingSlowdown`、`LandingSlowdownParams`，第 03 章）；6 s 保护 `SkillRules.DefaultTraits`（`jump_pad` 行）+ `SkillArbiter.EndCommand`。

**和 R5 不一样（hb-ch05 用同一套程序跑出来的，见 `_notes/hb-ch05.md`）**：

- **软着陆结束降速（规则 6）HSD 没做**：Octane S21 冲刺上跳板、落地第 4 条命令起跳、小跳落地后，`LandingSlowdown.f0` 还是 0.227，继续按 1 s 平方曲线恢复。R5 这时已经回到 1.15。
- **游戏身体的跳板落地比 R5 重一点**：同一个场景（平地上的跳板，冲刺进入），Unity 落地前 vz −1028.9 u/s、f0 0.227、水平 514.3 → 116.8 u/s；R5 vz −1024.5 ± 0.1、f0 0.242、→ 124.6 u/s。差 4.4 u/s 约等于慢放中一条命令的重力（5 u/s），**推断**是落地判定晚一条命令。手感对照第 3 批（回放场景）没报这个差别，没在那套场景上复核。

#### 验收

- 单元测试：
  - `JumpPadTests.ApproachLaunchSlowMoFlightAndHardLanding`：60 条命令后 vz 正好少 600 · 60 · dt；落地有 `LAND_SLOW`、`PAD_SLOWMO_END`。
  - `LandingSlowdownTests.ImpactFactorMatchesTheFit`、`LandingSlowdownTests.HardLandingCutsTheSpeedThenRecoversQuadratically`、`LandingSlowdownTests.SoftLandingAndZeroDurationDoNothing`（`R5MotorM4AbilityTests.cs`，第 03 章也引用）。
  - `OctaneM10CTests.PadSlideAndPadWallCombos`：蹲着发射、按住蹲落地接滑铲（813 → 733）；飞向墙按 W 被攀爬接走。
- 对照数据：OCT §3.2（15 次慢放）、§4（30 次落地）；M4b §2 – §3（12 次再跳）；关卡尺度表 LS-23（Unity 1412.5 u、707.92 u、3.433 s）。
- 合格线：慢放下 60 条命令的 Δvz 和 600 · 60 · dt 差 < 1e-6；站着发射最高点和 707.8 u 差 < 1 u、滞空差 < 0.01 s、水平距离差 < 2 u；落地 f0 和拟合差 < 0.002。
- 没测过：空中转向（R5）；软着陆结束降速的那 2 / 12 例外；落地马上再跳只测了"第 4 条命令起跳"一种时机。

#### 出处

- OCT §3.2 – §3.5、§3.7、§4、§6 第 3、7 条：慢放 0.8、看到的轨迹、空中小增益、落地降速的拟合、0.8 来源没读。main
- M4b TL;DR、§2 – §5：落地马上再跳的逐命令序列、14 %、软着陆结束降速。main
- N4A §2：`airSlowMoSpeed` 0.15、`landSlowdown*`。main
- 第 03 章 §3.9（`origin/handbook/ch03`）：硬着陆降速的通用规则和两种写法。还没合并
- `handbook/tables/level-scale.md` LS-23 / LS-24、`level_scale_harness/Program.cs` `Pads()`（`handbook/tables` 分支，还没合并）：Unity 模拟的数和 LS-24 的原因。
- [数据] `sh_jump_pads.gnut:517/549`（`EnableSlowMo`）、`jumppad_parity.cpp:175-194`（慢放挪到发射 / 落地命令）。

---

### 5.34 跳板二段跳

#### 原理

跳板发射后，空中可以再按一次跳，得到一次"补跳"。它是跳板的修正手段：竖直上补一点高度，按着方向键还能把飞行方向往按键方向拧 240 u/s。只给一次，要新按下（按住穿过发射不算），发射后 0.1 s 才能用——不让玩家在踩上跳板的同一瞬间连按两下把它变成一次更高的发射。补跳之后落地更重（f0 往往是 0，当场停下），这是它的代价。

#### 规则和公式

1. **授予**：任何一次跳板发射（Octane 自己的跳板或地图跳板，被别的发射覆盖的不算）给一次二段跳，**发射命令开始后 0.108 s 起可用**。脚本是 `wait 0.1`（在一次 WaitFrame 之后）；dedi 实测 ≤ 0.0834 s 拒绝（20 / 20）、0.1081 – 0.1083 s 混合（2 / 5 拒绝）、0.1084 s 起接受（3 / 5）、≥ 0.133 s 都接受；HSD 取 0.108（120 Hz 下第 13 条命令 0.1083 s 是第一条可用的）[实测] [数据]。
2. **使用**：跳跃键**按下沿**。授予之前按：什么都不发生，也**不消耗**授予 [实测 5 / 5]。按住跳跃穿过发射：永远不触发，松开后再按才触发 [实测 5 / 5]。一次发射只给一次（第二次按无效，0 / 5）。普通跳之后空中按不给（0 / 5）。
3. **竖直**（在这条命令的慢放重力之前，引擎单位），**不连续的两段** [实测]：
   - pre vz ≥ 分界 → vz += 201.81（n 106，sd 0.05）；
   - pre vz < 分界 → vz = 409.25（n 38，sd 0.005）。
   - 分界只夹在 (357.35, 360.04] u/s 之间，含义不明；HSD 取 358.7 [设计]。**不是** max(vz + 201.81, 409.25)：pre vz 246 给 409.25，不是 447.8。
4. **水平**：
   - 没按方向键：水平速度不变（|Δv_h| = 0，n 100；转视角也不变）[实测]。
   - 方向键**已经按住**：v_h ← v_h − 240·v̂_h + 240·ŵ，然后照常空中加速。ŵ 是按键方向（相对视角）。W 顺着速度：不变；S：沿速度减 480；D：侧向 240、前向少 240 [拟合，25 次，最大误差 0.015 u/s]。两种发射速度（514 / 813）都成立。
   - 方向键**在二段跳那条命令上才按下**：结果不同，**没建模**（D 键：沿 v̂ −264.1、沿 ŵ +272.1；S 键：沿 ŵ 净 449.3，按住 S 是 480）[实测 19 次]。HSD 当作"已按住"处理，并且那条命令不做 lurch [设计]。
5. **lurch**：二段跳**重新开始** lurch 窗口（二段跳后 0.025 s 按 D：|Δv| 212.55；不二段跳同一时刻 3.87）[实测]。二段跳后的 lurch 上限 R5 是 212.55，不是地面起跳的 209.3（0.7 × 冲刺上限），原因没查；HSD 用 209.3。lurch 规则见第 03 章。
6. **清除**：落地（R5 dedi 0 / 5，客户端预测给了然后被纠正）；上滑索 [数据]；Vantage 开始 JetDrive [数据]。
7. **Airborne Agility**（S21 L3 升级，`enable_doublejump_aircontrol`）：R5 按住 D 二段跳的结果和没升级**完全相同**，没测出作用 [实测 9 次]。HSD 只留标志。
8. **谁能用**：HSD 文档（`PadDoubleJump/README.md`）说 R5 里任何人踩跳板都能二段跳，但 M8 只用 Octane 测过，这句话的来源没找到 [没测过]。HSD 只给带跳板槽的预设（Octane S21、Pathfinder-Octane），地图跳板也只给这两个 [设计]。
9. **和别的二段跳**：一次按键只给一个；跳板二段跳优先级最高（HSD 跳跃仲裁 `JumpRank.PadDoubleJump` 300 > 喷气优先 250 > 通用二段跳 200 > 喷气 100），只扣赢家的次数。详见第 06 章（跳跃键仲裁）。
10. **镜头**：触发 R5 原生二段跳 punch（D-68），见第 07 章。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 授予延迟 `grantDelay` | — | 0.108 s（脚本 0.1 s） | — | 实测边界 0.1081 – 0.1084 s | [实测] [数据] |
| 竖直加量 `vzAdd`（pre vz ≥ 分界） | 5.126 m/s | 201.81 u/s | 2.803 H/s | sd 0.05 | [实测] |
| 竖直设定值 `vzFloor`（pre vz < 分界） | 10.39 m/s | 409.25 u/s | 5.684 H/s | sd 0.005 | [实测] |
| 分界 `vzBranch` | 9.111 m/s | HSD 设计值 358.7 u/s | 4.982 H/s | R5 夹在 357.35 – 360.04 | [实测] [设计] |
| 水平拧向量 `horizontalStep` | 6.096 m/s | 240 u/s | 3.333 H/s | 两种发射速度都成立 | [拟合] |
| 二段跳后 lurch 上限 | 5.399 m/s | 212.55 u/s（HSD 用 209.3） | 2.952 H/s | — | [实测] |
| 二段跳后落地 \|vz\| 最大 | 33.93 m/s | 1336 u/s（f0 = 0） | 18.56 H/s | — | [实测] |
| 看到的加量 / 设定值 / 拧向量（× 0.8） | 4.100 / 8.316 / 4.877 m/s | 161.4 / 327.4 / 192 u/s | 2.242 / 4.547 / 2.667 H/s | 只在按看到的单位实现时用 | [算] |
| HSD 向上速度天花板（带二段跳的身体） | 31.75 m/s | HSD 设计值 1250 u/s | 17.36 H/s | 必须 > 1028.6 + 201.81 = 1230.4 | [设计] |

#### 实现模板

```
// 单位：u、s（引擎速度，飞行在慢放里）
on padLaunch(now):            pending = true; launchTime = now
on command(now, dt):
    if grounded:              pending = false; return
    if mountedZipline:        pending = false
    if not (pending and jumpPressedEdge): return
    if now - launchTime < grantDelay: return            // 太早：什么都不消耗
    claimJump(rank = PadDoubleJump)                     // 第 06 章：一次按键只给一个
    // 在这条命令的移动（慢放重力）之前
    vel.z = vel.z >= vzBranch ? vel.z + vzAdd : vzFloor
    if moveKeysHeld:
        vh  = horizontal(vel); dir = |vh| > 0 ? vh/|vh| : 0
        vel.xy += horizontalStep * (wishDir - dir)
        if moveKeyPressedThisCommand: suppressLurchThisCommand   // HSD 近似
    lurchWindowStart = now                               // 重新开窗口
    pending = false
```

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/PadDoubleJump/PadDoubleJumpAbility.cs`（`PadDoubleJumpParams`：`grantDelay`、`vzAdd`、`vzFloor`、`vzBranch`、`horizontalStep`、`restartsLurchWindow`、`sameCommandKeyAsHeld`、`clearOnZipline`、`UpCeiling`，全部 [u]；`PadDoubleJumpAbility.BeforeMove`、`AfterMove`（授予）、`Impulse`（纯函数）、`CommitJump`）。谁有：`MovementConfig.PadDoubleJumpFor`；天花板抬到 1250：`MovementConfig.Apply`。跳跃仲裁：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/_Core/JumpArbitration.cs`。

#### 验收

- 单元测试（`R5MotorM8CTests.cs`，类 `PadDoubleJumpTests`）：
  - `PadDoubleJumpTests.GrantedFrom0108SecondsAfterTheLaunchAtEveryCommandRate`（60 / 120 / 144 Hz）。
  - `PadDoubleJumpTests.AnEarlyPressDoesNotConsumeItAndItIsOncePerLaunch`、`PadDoubleJumpTests.HoldingJumpThroughTheLaunchNeverFiresItANewPressDoes`、`PadDoubleJumpTests.NormalJumpsNeverGrantItAndTheLandingClearsAnUnusedGrant`。
  - `PadDoubleJumpTests.VerticalBranchesAreDiscontinuous`、`PadDoubleJumpTests.HorizontalNoKeyUnchangedHeldKeyStepsBy240`、`PadDoubleJumpTests.HorizontalRuleHoldsAtBothLaunchSpeeds`、`PadDoubleJumpTests.AKeyPressedOnTheDoubleJumpCommandIsTreatedAsHeld`。
  - `PadDoubleJumpTests.TheDoubleJumpRestartsTheLurchWindow`、`PadDoubleJumpTests.StandCrouchWalkAndJumpInEntriesGiveTheSameAdd`、`PadDoubleJumpTests.TheLandingAfterADoubleJumpFollowsTheM4Law`、`PadDoubleJumpTests.AZiplineMountClearsAnUnusedGrant`、`PadDoubleJumpTests.BothDoubleJumpsOnThePadOneWinsTheGenericKeepsItsCount`、`PadDoubleJumpTests.OnlyTheOctaneLoadoutCarriesItInBothConfigsAndTheReplayNever`（也核对向上天花板 1250 / 1100）。
  - `M8CFuzzTests.RandomPadFlightsKeepEveryPadDoubleJumpRule`；`PadLurchM10DTests.ThePadDoubleJumpStillRestartsTheWindow`；`JumpArbitrationTests.PadLaunchAndAirJumpOnTheSameCommandSpendNothing`（`R5MotorM8Tests.cs`）。
  - 游戏侧表现：`F7CameraTests.PadDoubleJumpHudShowsTheWindow`、`FndCameraTests.PadDoubleJumpUsesTheNativePunch`（`Assets/HSD/Game/Tests/Editor/`，第 07 章）。
- 对照数据：PAD-DJ 4 个会话 123 次二段跳（`research/phase2-local/m8/r_pad_djump/results.json`）。
- 合格线：加量 / 设定值和实测差 < 0.1 u/s；按住键的水平拧向量差 < 0.02 u/s；授予时刻和 0.108 s 差不超过一条命令。
- 没测过 / 没建模：同一条命令按方向键的结果；分界的含义；二段跳后 lurch 上限 212.55；只测了 120 fps 的授予时刻。

#### 出处

- PAD-DJ TL;DR、"Model for Unity"、"Open questions"：全部规则和数。main
- OCT-M10 TL;DR "Upgraded pad DJ"：Airborne Agility 没作用。main
- `research/phase2-local/m8/unity/M8C-UNITY.md` §2、§8；`m8/unity/M8A-UNITY.md` §2（跳跃仲裁）。main
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/PadDoubleJump/README.md`：HSD 的 [设计] 值和已知差异。main
- DEC D-43（F7 反馈，镜头部分被 D-68 取代）、D-68（二段跳镜头用原生 punch）。main
- [数据] `sh_jump_pads.gnut`（`wait 0.1`、`enable_doublejump` 设置 mod）；`JumpPad_GiveDoubleJump`（JetDrive 开始时清授予，M9-C 引用）。[反编译] 二段跳 punch `DoubleJump_Rumble` 0x140a34c00（第 07 章用）。

---

### 5.35 天花板滑行（ceiling surf）

#### 原理

跳板飞到天花板下面时，头顶贴住天花板，但竖直速度**不清零**：身体被天花板按住不动，竖直速度照常被重力慢慢吃掉，水平速度保持。飞出天花板边缘的那一刻，剩下的竖直速度把人往上抛。这是 Apex 社区早就有的技巧（2021-01 已有教程）。它不是一条专门的跳板规则，而是"撞天花板时不削速度"这条通用规则在跳板的高竖直速度下变得明显。

#### 规则和公式

1. 自由飞行中（不在攀爬 / 翻越 / 滑索 / Vantage 驱动这类"运动学"状态里，没有外加加速度如钩爪拉力，重力没关、没反向），移动扫到天花板（法线 n_z ≤ −0.7）且正朝它运动时：**位置停在天花板，速度保持**（不去掉 v·n 分量）。
2. 之后什么都不用加：竖直速度按这条命令的重力衰减（跳板慢放中 600 u/s²，平时 750），水平速度和空中加速照常（第 03 章；空中加速 500 u/s²、意图上限 69 u/s，所以贴着天花板想转向要先松开 W）。
3. 离开天花板（到边、或天花板不连续）：剩下的竖直速度把人抛上去。粗糙、拼起来的天花板每一块是一个平面，过缝就结束。
4. **R5 本地是两套结果**（[hyb]）：S21 客户端预测会滑（z 不动、vz 按 600 u/s² 衰减、v_h 保持）；本地 S3 dedi 在接触那条命令就把 vz 削到约 0（−31 … +24），6 – 16 条命令后把客户端拉回。HSD 按 D-13（客户端和本地服务端不一致、又有社区证据时，跟客户端）**做**。R5 测到的"贴住时间"只有客户端被纠正前的 0.05 – 0.09 s，完整滑行长度是 [S21 客户端 + 模型]。
5. 普通冲刺跳撞 100 u 的低天花板也一样（客户端贴住 3 条命令，vz 180；dedi 削到 −10），说明这条规则不是跳板专用 [实测]。
6. 社区说的"把竖直速度存进滑索"（经过滑索再滑）HSD 没做：上滑索是运动学状态，竖直速度丢掉 [没建模]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 天花板判定法线 n_z | — | ≤ −0.7（×） | — | — | [设计]（HSD 用的阈值；R5 没单独测） |
| 贴住时竖直速度衰减（跳板中） | 15.24 m/s² | 600 u/s²（750 × 0.8） | 8.333 H/s² | — | [实测 S21 客户端] |
| 跳板下 150 / 250 / 400 u 天花板：接触时 vz（R5 客户端） | 24.54 / 22.50 / 19.07 m/s | 966.1 / 885.9 / 750.9 u/s | 13.42 / 12.30 / 10.43 H/s | HSD 971.1 / 891.1 / 751.1 | [实测] |
| 蹲着发射、250 u 天花板：接触时 vz | 约 15.0 m/s | 590.3（平）/ 595.4（糙）u/s | 约 8.2 H/s | HSD 600.7 | [实测] |
| 冲刺跳、100 u 天花板：接触时 vz | 4.575 m/s | 180.1 u/s | 2.501 H/s | HSD 199 | [实测] |

HSD 接触时 vz 高约 5 u/s（150 / 250 u）：HSD 用碰撞体顶（72 / 48 u，[设计]），R5 用头。

#### 实现模板

```
// 单位：u、s。在世界碰撞扫过这条命令的移动之后
if hitPlane.normal.z <= -0.7 and dot(vel, hitPlane.normal) < 0:     // 正朝天花板运动
    pos = stopAtPlane(pos)
    if freeFlight and not externalAccel and gravityScale > 0:
        keep vel                                                    // 天花板滑行
    else:
        vel -= dot(vel, n) * n                                      // 普通撞顶
```

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/World/MovementWorld.cs`，`MovementWorld.AfterStep`（门控：`m.p.ceilingSurf && !m.mods.kinematic && !m.mods.hasExternalAccel && m.mods.gravityScale > 0`）；开关 `R5MotorV2Params.ceilingSurf`（`[NonSerialized]`，`MovementConfigs.Reference()` 开、Fun 继承、回放电机关）。事件 `CEILING_SURF` / `CEILING_SURF_END`。

#### 验收

- 单元测试（`R5MotorM10CTests.cs`）：`OctaneM10CTests.PadUnderACeilingSurfsAtTheSlowMoGravityAndKeepsTheHorizontalSpeed`（150 / 250 / 400）、`OctaneM10CTests.TheSurfEndsAtTheEdgeWithTheLeftoverVzAndAirStrafeWorksOnTheCeiling`、`OctaneM10CTests.ASprintJumpIntoALowCeilingIsPinnedTooAndDecaysAtG`、`OctaneM10CTests.TheSurfIsOnlyFreeFlightAndTheReplayMotorClips`。
- 对照数据：OCT-M10 68 次天花板试验（客户端 / dedi 逐命令）。
- 合格线：接触时 vz 和 R5 客户端差 < 6 u/s；贴住时 vz 衰减率 600 ± 1 u/s²；水平速度不变。
- 没测过：完整的滑行长度（R5 客户端被纠正）；S21 正版服务端会不会也滑。

#### 出处

- OCT-M10 TL;DR "Ceiling surf"、"Normal jump into a ceiling"、"Model for HSD"。main
- M10C-U §5、§10 第 3 条。main
- DEC D-13（跟客户端），"还没结论的事"表里 D-13 行的天花板数据。main
- DP §10.3（混合构建现象表）。main

---

### 5.36 兴奋剂（Stim，速度倍率，不是外力）

#### 原理

兴奋剂不推人，它把所有"跟移动倍率走的东西"一起放大约 30 %：走、冲刺、蹲走的上限，各段加速，滑铲加成和上限，空中意图上限，lurch 上限。摩擦、重力、跳高不变。所以开了兴奋剂跳得一样高，但跑得快、滑得远。持续 6 s，之后 0.5 s 平滑消退；持续期间不能再打一针。

#### 规则和公式

1. 按下后 0.16 s 生效（部署 0.15 s + 一条命令），一步到位，没有渐入 [实测 13 次]。
2. 移动倍率 msc ← msc × (1 + 2 · s · g(t))，s = 强度，g 在 6.0 s 内 = 1，之后 0.5 s 余弦消退：g = 0.5 + 0.5 · cos(π (t − 6.0) / 0.5) [拟合]。满强度倍率 1.298038，空手 msc 1.15 → 1.4927 [实测]。
   - 强度：脚本写 0.15，实测等效 0.149020 = 38/255（推断按一个字节存）[实测 + 推断]。
3. 前 6.0 s 同时改两个冲刺键：`sprintspeed` 260 → 282，`sprintAcceleration` 100 → 120（消退那 0.5 s 已经恢复）[拟合]。冲刺上限 = 282 × 1.4927 = 420.95 u/s。
4. 不受影响：无输入减速 1250 u/s²、滑铲减速、重力、起跳高度 [实测]。lurch 上限 = 0.7 × 当时的冲刺上限 = 294.67 u/s [实测]。
5. 再打一针：生效后 6.0 s 内按无效（不刷新、不扣血），之后还有 0.7 s 充能冷却；生效后 7.5 s 起可以 [实测 22 次] [数据 `charge_cooldown_time`]。网上"1.8 s 延迟"的说法和 R5 矛盾，HSD 跟 R5（M10-C O-2，还开着）。每针 −20 血（HSD 没做）。
6. 和跳板：跳板替换速度，所以兴奋剂不改发射弧线 [实测 M4]。
7. 兴奋剂连跳：R5 离地 410.6 u/s，HSD 的超速削减 max(R, v − 100) 在这里结果等于 R = sprintspeed · msc = 420.9（高 2.5 %；不是 min(v, R)，那是回放电机的旧写法（hb-integrate 11-14 按 hb-ch06 备注改）），R5 的规则没认出来 [差别，没改]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 生效延迟 `onsetDelay` | — | 0.16 s | — | 实测 0.158 – 0.167 | [实测] |
| 强度 `severity`（× `extraScale` 2） | — | 0.149020（38/255；脚本 0.15） | — | — | [实测] [数据] |
| 满强度倍率 | — | 1.298038（×） | — | — | [实测] |
| 满强度时间 `fullDuration` / 消退 `fadeDuration` | — | 6.0 s / 0.5 s（余弦） | — | 平滑步进分不开（0.484 s） | [实测] [拟合] |
| 冲刺上限键 `sprintspeed`（兴奋剂中） | 7.163 m/s | 282 u/s（平时 260） | 3.917 H/s | — | [拟合] |
| 冲刺加速键 `sprintAcceleration`（兴奋剂中） | 3.048 m/s² | 120 u/s²（× msc；平时 100） | 1.667 H/s² | — | [拟合] |
| 兴奋剂冲刺上限 | 10.69 m/s | 420.95 u/s | 5.847 H/s | — | [实测] |
| 兴奋剂走路上限 | 6.578 m/s | 258.991 u/s | 3.597 H/s | — | [实测] |
| 再用锁定 | — | 6.0 s + 0.7 s | — | 实测 6.6 s 不行、7.5 s 行 | [实测] [数据] |

#### 实现模板

```
// 单位：u、s
on stimPress(now):  if now >= stimLockedUntil: t0 = now + 0.16; stimLockedUntil = t0 + 6.0 + 0.7
each command:
    t = now - t0
    g = (0 <= t < 6.0) ? 1 : (6.0 <= t < 6.5) ? 0.5 + 0.5*cos(pi*(t-6.0)/0.5) : 0
    moveScale *= 1 + 2 * severity * g          // 和别的倍率相乘（落地降速等）
    (sprintspeed, sprintAccel) = (0 <= t < 6.0) ? (282, 120) : (260, 100)
```

Unity 参考实现：`HSD-Unity: Assets/HSD/R5Replay/Runtime/Abilities/Stim/StimAbility.cs`（`StimParams`：`onsetDelay`、`severity` = 38/255、`extraScale`、`fullDuration`、`fadeDuration`、`sprintspeed`、`sprintAcceleration`、`modDuration`；`StimAbility.Boost`）。技能层倍率怎么合（取最大、上限 1.40）：`SkillArbiter.CombineBoosts`、`SkillRules.maxSpeedBoost`，详见第 06 章。Octane S21 预设的兴奋剂槽 6.7 s 充能。

#### 验收

- `StimTests.BoostAndFadeShape`、`StimTests.TapOnsetCapsModAndEnd`、`StimTests.NotReadyAndCarriedOverStim`（`R5MotorM4AbilityTests.cs`）；`OctaneM10CTests.StimMatchesTheR5Regression`、`OctaneM10CTests.StimReuseIsLockedForTheChargeAndTheCooldown`（1.0 / 3.0 / 5.9 / 6.6 / 7.5 / 9.0 s）、`OctaneM10CTests.StimScalesTheBunnyHopsLikeEverythingThatScalesWithTheMoveScale`；`SkillCooldownTests.StimCooldownAndItsOwnReuseLockout`（`R5MotorM5SkillTests.cs`）。
- 对照：OCT §2（13 次）、OCT-M10（33 + 22 次）；手感对照第 3 批兴奋剂 77 / 78。
- 合格线：倍率和 1.298038 差 < 2e-6；冲刺上限 420.954 ± 1e-3；回到 1.15 的时刻和 6.49 s 差 < 0.01 s。

#### 出处

- OCT §2、§5、§6 第 5 – 6 条；OCT-M10 TL;DR "Stim"；M10C-U §3、§10 第 1、7 条。main
- `research/phase2-local/static-values/STATIC-VALUES.md` §6（`STIM_DURATION` 6、强度 0.15）。main
- [数据] `sh_stim.gnut:12`（`movement_speedboost_extraScale` 2）、`sh_stim.gnut:58-64`（`StatusEffect_AddTimed`）。

---

---

## 第五部分 · 爆炸击退和火箭跳（§5.37 – §5.39）

击退的白话说明、记号和出处缩写在第四部分开头（两者一起写：跳板是替换，击退是相加）。

### 5.37 爆炸击退：大小、方向、衰减、上限、地面门槛

#### 原理

爆炸把人往外推，推的方向是"爆点 → 身体中心"，大小随"爆点到身体表面"的距离线性变小。推出来的速度**加在原来的速度上**，不替换：所以冲刺中朝身后地面打会更快，朝身前打会刹车，滑铲中朝脚下打水平速度能翻倍。这是火箭跳"上限高、有技巧"的来源（用户选 A 的理由："更原生，上限更高，也更有技巧"）。

两条限制让它不失控：

1. **总速度上限 1000 u/s**，但已经比 1000 快的不会被砍下来。
2. **站在地上时，太小的推力（≤ 约 312 u/s）整个不起作用**，空中没有这个门槛。远处的小爆炸推不动站着的人，但能推动空中的人。

对应 DESIGN-PHILOSOPHY P3（"爆炸击退：直接相加，上限 max(1000, 推之前的 |v|)"）。

#### 规则和公式

记号：爆点 E；身体：脚 F，当前碰撞体高度 h（站 72，蹲 / 滑 48），中心 C = F + (0, 0, h/2)，身体按半径 16 u、高 h 的柱体。

1. **距离**：d = 从 E 出发、沿 E → C 方向走到碰到身体柱体为止的长度；E 在柱体里面时 d = 0 [实测 R5 侧面 3 点差 ≤ 0.01（约 1 – 2 u）；TF2 脚下 4 点差 ≤ 0.003]。**不是**到中心的距离，也不是到最近点的距离——这两种都对不上。
2. **衰减**：f = clamp(1 − (d − r_in) / (r_out − r_in), 0, 1)，线性（R5 侧面两点斜率正好 1/128 = 1/(180 − 52)，不是平方）[实测]。d ≥ r_out 或中间有遮挡（世界、挡爆炸的墙）不推。伤害用同一个 f。
3. **大小和方向**：Δv = F_exp · f ÷ 100 · unit(C − E)。F_exp 是武器的爆炸推力（`impulse_force_explosions`）；除以 100 [实测 + TF2 实测：TF2 记录到的伤害力向量模正好 = 推力 × 衰减，Δv 655]。**没有额外的竖直加成**：TF2 力向量解出中心高 35.9（站姿 36），R5 滑铲分量比解出 24.0（蹲姿 24）[实测] [TF2 实测]。
   - 实测比 650 大 1.4 %（地面 659）/ 0.5 %（空中 653），手雷 50000 → 488（小 2.4 %）。差在"单条命令的速度跳变"这种量法（同一帧里还有重力、摩擦），按 D-70 不追。
4. **空中 / 地面**：推力相同（`damageImpulseScaleAir` 1）[数据] [实测]。
5. **地面门槛**：着地时 |Δv| ≤ G 的推力**整个忽略**（连水平分量都没有，也不开 §5.38 的窗口）；空中没有门槛 [实测]。看的是 |Δv| 的总大小，不是竖直分量：站着 30° 的 342 u/s（竖直只有 99）推得动。R5 门槛在 310（不动）和 315（全额）之间，取 312.5 [实测]。判断写在服务端 `r5apex_ds.exe`，没分析，精确值和比较方式（≤ 还是 <）都[没测过]。
   - 以前 #64 写的"31500 一下跳到 266"是 0.1 s 后的采样值：初速就是 315，没有台阶 [算]。
   - TF2 不一样：门槛在 17500 – 25000 推力之间，30° 时竖直分量被吃掉、水平保留 [TF2 实测]。HSD 跟 R5。
6. **相加和上限**：v' = v + Δv；若 |v'| > max(L, |v|) 则 v' ← v' · max(L, |v|) / |v'|，L = `damageImpulseSpeedBoostLimit` 1000 [数据]。实测：推力 100000 和 200000 都是 948（0.1 s 后，减掉重力约 75 后约 1000），TF2 997 [实测] [TF2 实测]。"已经快于 1000 时不砍"是[推断]，没测过。
7. **离地**：向上的推力让着地的身体离地（Unity 抬 1 u，沿用 TF2X 的做法）。
8. **护盾**：R5 伤害全被护盾吃掉就完全不推，进 1 点血就全额推 [实测]。HSD 没有护盾，**不做**；以后加护盾时照这条。
9. **`damageImpulseSpeedLossLimit` 50**：意义没看出来（冲刺跳打在前面水平掉了 171，总速度却是升的），**不做** [数据] [没测过]。
10. **直接命中的冲击力**（`impulse_force`，EPG jump_kit 17500）：Unity 没做，只有爆炸推力。
11. **击退不走技能层的"发射"**：它在战斗层的爆炸这一步直接改身体速度，不替换、不进跳板那套优先级。R5 里它走引擎的冲量队列（会开 §5.38 的窗口），跳板不走。**动量规则（冲量队列、和跳板 / 钩爪 / 滑索谁覆盖谁）详见第 06 章**。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 推力 → 速度除数 `mass` | — | 100（×） | — | 实测 98.6 – 102.4（659 / 653 / 488） | [实测] [TF2 实测] |
| EPG jump_kit 推力 → 满额 Δv | 16.51 m/s | 65000 → 650 u/s | 9.028 H/s | 实测 659（地）/ 653（空） | [数据] [实测] |
| EPG 原版推力 → 满额 Δv | 7.62 m/s | 30000 → 300 u/s（地面被门槛挡） | 4.167 H/s | 空中实测 287 | [数据] [实测] |
| 手雷推力 → 满额 Δv | 12.70 m/s | 50000 → 500 u/s | 6.944 H/s | 实测 488 | [数据] [实测] |
| EPG 内径 `explosion_inner_radius` | 1.321 m | 52 u | 0.7222 H | TF2 30 u | [数据] |
| EPG 外径 `explosionradius` | 4.572 m | 180 u | 2.5 H | TF2 150 u | [数据] |
| 身体中心高：站 / 蹲、滑 | 0.9144 / 0.6096 m | 36 / 24 u | 0.5 / 0.3333 H | — | [TF2 实测] [实测] |
| 身体柱体半径 | 0.4064 m | 16 u | 0.2222 H | TF2 腿侧三点像更细的命中盒（不追） | [实测] [推断] |
| 速度上限 `damageImpulseSpeedBoostLimit` | 25.4 m/s | 1000 u/s | 13.89 H/s | 实测 948（0.1 s 后），TF2 997 | [数据] [实测] |
| 地面门槛 `groundMinSpeed` | 7.938 m/s | 312.5 u/s | 4.340 H/s | R5 在 310 – 315 之间 | [实测] |
| 空中推力倍率 `damageImpulseScaleAir` | — | 1（×） | — | — | [数据] [实测] |
| `damageImpulseSpeedLossLimit`（不做） | 1.27 m/s | 50 u/s | 0.6944 H/s | 意义不明 | [数据] |

**和 HSD 现在的做法**：

- **main 上**只有 TF2X 的推法：推力 ÷ 103（TF2 W2 拟合）、按到最近点的距离衰减、没有上限 / 门槛 / 窗口（`CombatSim.Explode` + `CombatSim.Push`，`CombatSim.PlayerMass` = 103）。
- **HSD-Unity PR #52**（还没合并；分支 `rj/knockback-a`）照本节做；`MovementConfig.knockback = null` 或游戏战斗页"R5 原生击退"关掉 = 回到 TF2X，逐字节不变。
- **HSD 技能层的速度天花板也管击退**（hb-ch05 写本章时看到的，没单独测）：`SkillArbiter.EndCommand` 每条命令结束时把 |v_h| 夹到 `maxHorizontalSpeed`（默认 900 u/s，部分预设更高）、向上 vz 夹到 `maxUpSpeed`（1100 / 1250 u/s）[设计]。R5 的上限是合速度 1000；所以 HSD 里"已经很快 + 侧向大推力"的组合，水平部分会在 900 被削，R5 能到 1000。`RjaKnockbackTests` 里的 18 个对照条件都没碰到这个天花板。

#### 实现模板

```
// 单位：u、s。爆炸发生时（战斗层），对每个单位
explode(E, damage, rIn, rOut, Fexp, attacker, ownerScale):
    for unit in unitsInRange:
        C = unit.feet + (0, 0, unit.hullHeight / 2)
        d = distanceAlongLineToCylinder(E, C, radius = 16, height = unit.hullHeight)   // E 在体内 → 0
        if d >= rOut or blocked(E, C): continue
        f  = clamp(1 - (d - rIn) / (rOut - rIn), 0, 1)
        dealDamage(unit, damage * f * (unit == attacker ? ownerScale : 1))
        dv = unit(C - E) * (Fexp * f / 100)
        applyDamageImpulse(unit, dv)

applyDamageImpulse(body, dv):
    m = |dv|
    if body.grounded and m <= groundMinSpeed: return false        // 整个忽略，不开窗口
    before = |body.vel|
    v = body.vel + dv
    lim = max(1000, before)
    if |v| > lim: v *= lim / |v|
    body.vel = v
    if dv.z > 0 and body.grounded: body.grounded = false; body.pos.z += 1
    body.lowDecelEnd = body.time + m * 0.003                     // §5.38，覆盖旧值
    return true
```

离散化要注意：Unity 在两条命令之间（战斗层这一步）加速度，下一条命令的移动才用到它；R5 服务端在处理伤害时加，客户端在下一条预测命令里看到。爆炸时刻相对起跳的先后对最高点影响很大（§5.39），对照 R5 时按"爆炸时刻"对齐，不按"开火时刻"。

Unity 参考实现（HSD-Unity PR #52，还没合并；分支 `rj/knockback-a`）：

- `HSD-Unity: Assets/HSD/R5Replay/Runtime/KnockbackParams.cs`：`KnockbackParams`（`enabled`、`mass` 100、`speedBoostLimit` 1000、`groundMinSpeed` 312.5、`lowDecelDurationScalar` 0.003、`lowDecelRamp` 0.5，全部 [u]）；`KnockbackParams.R5Native()`。
- `HSD-Unity: Assets/HSD/R5Replay/Runtime/R5MotorV2.cs`：`R5MotorV2.ApplyDamageImpulse`（门槛、相加、上限、离地、开窗口）。
- `HSD-Unity: Assets/HSD/Game/Runtime/Combat/CombatSim.cs`：`CombatSim.Explode`（新参数 `ownerDamageScale`）、`CombatSim.Knockback`（配置 + 菜单开关）、`CombatSim.PushNative`（玩家走电机，假人只受上限）。
- `HSD-Unity: Assets/HSD/Game/Runtime/Combat/CombatCore.cs`：`CombatGeometry.DistanceAlongToCentre`、`CombatGeometry.Falloff`。
- 配置：`MovementConfig.knockback`（`[NonSerialized]`；Reference = `R5Native()`，Fun 继承）；游戏 Esc → 战斗页"R5 原生击退"（PlayerPrefs `hsd.tf2.x.rjnative`，默认开）；FeelBatch / CameraFeelBatch `-preRJA`。

#### 验收

- 单元测试（HSD-Unity PR #52，还没合并；分支 `rj/knockback-a`；`Assets/HSD/Game/Tests/Editor/RjaKnockbackTests.cs`，类 `RjaKnockbackTests`）：
  - `RjaKnockbackTests.TheReferenceAndFunConfigsCarryTheNativeKnockback`：五个参数的值；菜单开关关 = TF2X。
  - `RjaKnockbackTests.TheFalloffRunsAlongTheLineToTheCentre`：R5 侧面 45° / 30° 的衰减 0.889 / 0.519（差 ≤ 0.01），TF2 脚下 37.6 u 0.937（差 ≤ 0.005），体内 d = 0。
  - `RjaKnockbackTests.AFullPushIsForceOverMassTowardTheCentreAndLeavesTheGround`：65000 → 650，指向脚 + 36，离地，窗口 1.95 s。
  - `RjaKnockbackTests.TheSumIsCappedAt1000`：200000 推力（Δv 2000）→ |v| 1000；已经 1200 u/s 再往上推 500 → |v| 仍是 1200（不加、也不砍）。
  - `RjaKnockbackTests.AGroundedBodyIgnoresAWeakPushButAnAirborneOneDoesNot`：310 不动、不开窗口；315 全额；空中 287 推得动。
  - `RjaKnockbackTests.WithoutAKnockbackTheMotorIsUnchanged`、`RjaKnockbackTests.TheSwitchOffKeepsTheTf2xPush`（50000 / 103，没有窗口）。
- 对照数据：#64 的 29 个条件（`research/epg/data/summary.csv`、`trials.csv`）和推力扫描（`research/epg/data/probe-force-sweep.csv`）；TF2 T-1 的伤害力向量（`tf2/runtime/data/20261029_020710_t1_epg/diag.tsv` 的 `HSDDIAG DMG` 行）。
- 合格线：衰减和 R5 / TF2 实测差 ≤ 0.01；满额 Δv = 推力 / 100（不追 R5 量法的 ±2 %）；门槛两侧 310 / 315 的结果和 R5 相同；回放电机和 FeelBatch 共 741 个文件开关开 / `-preRJA` 都和 main 逐字节相同。
- 没测过：门槛精确值和比较方式；已经快于 1000 时被推；`SpeedLossLimit` 50；HSD 900 u/s 水平天花板和击退叠加的情形。

#### 出处

- RJ §0、§2 – §6、§9 – §11：全部规则、为什么做门槛、为什么不做护盾、没测的项。（PR #85，还没合并；分支 `rj/knockback-a`）
- EPG §1 – §5：#64 的实测（模拟开火、推力扫描、护盾、setfile 四个变量）。main。**§7 的建议（不做地面门槛）已过时**，以 RJ §5 为准。
- TF2-EPG §1、§2：TF2 真开火的对照（力向量、门槛不同、重力 600 下飞得更高）。main
- DEC D-77（D-56 选 A + A 的规格；没选 B：Fuse Knuckle Jumper 式跳跃加成）。（PR #85，还没合并；分支 `rj/knockback-a`）
- DIFF "RJA 火箭跳 A" 节：TF2X / R5 / 现在 三列对照和切回方法。（PR #85，还没合并；分支 `rj/knockback-a`）
- DP P3 表"爆炸击退"一行。main
- NT §5：冲量队列（类型 0 加速度、类型 1 开低减速窗口）。main
- [数据] setfile `damageImpulseScale` 1、`damageImpulseScaleAir` 1、`damageImpulseSpeedBoostLimit` 1000、`damageImpulseSpeedLossLimit` 50（客户端 exe 里从没被读过，击退在服务端，`research/rea-native/map/setfile-keys.csv`）；`research/rea-native/n4/classvars-by-legend.csv`（所有传奇相同）。

---

### 5.38 击退后的无减速窗口

#### 原理

被炸飞之后，有一小段时间地面摩擦、滑铲减速和空中阻力都不起作用，然后在最后 0.5 s 慢慢恢复。窗口长短和推力大小成正比：火箭跳（650 u/s）是 1.95 s。效果是火箭跳落地后还能带着速度接滑铲、再跳，不会一落地就被摩擦吃掉；贴地横向的小推力也能把人"滑"出去一段。这是 P3（"击退后一小段时间没有减速"）的另一半。

#### 规则和公式

1. 每次**生效的**击退（被地面门槛忽略的不算）把结束时间设成 T_end = now + |Δv| · s_k，s_k = `impulse_low_decel_duration_scalar` 0.003 s/(u/s)。**覆盖**旧的结束时间（不是取较大值）[反编译]。
2. 每条命令的系数 k：now ≥ T_end 时 k = 1；否则 k = clamp(1 − (T_end − now) / 0.5, 0, 1)——前段 0，最后 0.5 s 线性回到 1 [反编译：原生写成 1 − 2·(T_end − now)，常数 0.5]。
3. k 乘在：地面减速（含 `deceleration`、`sprintDeceleration`、蹲走减速、`slideDecel`、`slideWantToStopDecel`）、空中的水平阻力、贴墙时沿墙法线的减速 [反编译：`Ground_GetDecel`、`AirMove`、`WalkMove` 三处读这个字段]。
4. **不乘**：滑铲的指数衰减 `slideVelocityDecay`（不在 `Ground_GetDecel` 里）；加速、重力。
5. 服务端用的值没在运行时核对（客户端和服务端 ConVar 一般相同，以前核对过的移动 ConVar 都一致）[没测过]。
6. 实测旁证：#64 推力扫描 0.1 s 后水平速度一点没掉（−210），正好在窗口里 [实测]。
7. 跳板**不**开这个窗口（§5.32 第 9 条）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 窗口系数 `lowDecelDurationScalar`（`impulse_low_decel_duration_scalar`） | 0.1181 s/(m/s) | 0.003 s/(u/s) | 0.216 s/(H/s) | 服务端值没核对 | [反编译] |
| 恢复段 `lowDecelRamp` | — | 0.5 s | — | — | [反编译] |
| 例：火箭跳 Δv 650 的窗口 | — | 1.95 s（前 1.45 s 减速为 0） | — | — | [算] |
| 例：地面门槛边上 Δv 315 的窗口 | — | 0.945 s | — | — | [算] |
| 例：上限 Δv 1000 的窗口 | — | 3.0 s | — | — | [算] |

#### 实现模板

```
// 单位：u、s。每条命令移动之前
k = (now >= lowDecelEnd) ? 1 : clamp(1 - (lowDecelEnd - now) / 0.5, 0, 1)
if k < 1:
    params = copy(params)
    params.deceleration        *= k
    params.sprintDeceleration  *= k
    params.crouchDeceleration  *= k
    params.slideDecel          *= k
    params.slideWantToStopDecel*= k
    airHorizontalDrag          *= k
    wallNormalDecel            *= k      // R5 有；Unity 电机没有这一项减速，没做
move(...)
```

Unity 参考实现（HSD-Unity PR #52，还没合并；分支 `rj/knockback-a`）：`R5MotorV2.lowDecelEndTime`、`R5MotorV2.lowDecelRamp`、`R5MotorV2.DecelScale`；在 `R5MotorV2.Step` 里移动前把五个减速和 `CommandModifiers.horizontalDragQuad` 乘上系数（`p.ShallowCopy()`，不改原参数）。单关：`KnockbackParams.lowDecelDurationScalar = 0`。

**和 R5 的差别**：R5 的 `WalkMove` 贴墙法线减速也乘 k；HSD 电机没有单独的"贴墙法线减速"项，所以没对应。

#### 验收

- `RjaKnockbackTests.TheLowDecelWindowStopsGroundFrictionThenRampsBack`（PR #52）：400 u/s 横推 → T_end = 1.2 s；0.6 s 时水平速度还是 800（对照组按 1250 u/s² 掉）；系数在 0.7 s 前为 0、0.95 s 为 0.5、1.2 s 为 1；恢复段按斜坡掉速（误差 ≤ 6 u/s）。
- `RjaKnockbackTests.AGroundedBodyIgnoresAWeakPushButAnAirborneOneDoesNot`：被门槛忽略的推力不开窗口。
- `RjaKnockbackTests.AFullPushIsForceOverMassTowardTheCentreAndLeavesTheGround`：650 → T_end = now + 1.95 s。
- 对照数据：#64 推力扫描 0.1 s 后水平速度（`probe-force-sweep.csv`）。
- 合格线：窗口长度 = |Δv| × 0.003 s（1e-9）；k 的折线和规则 2 一致。
- 没测过：服务端运行时的 0.003；窗口里落地 / 滑铲 / 再跳的完整轨迹没有 R5 对照（只有 0.1 s 后一个采样点）。

#### 出处

- RJ §7：字段、三个读取函数、ConVar 默认值、常数 0.5、规格。（PR #85，还没合并；分支 `rj/knockback-a`）
- NT §5、§6 T-04：冲量队列类型 1 和"低减速"窗口（T-04 的跳板猜测由 NP2 §3 否定）。main
- EPG §3：推力扫描的水平速度没掉。main
- [反编译] `m_damageImpulseNoDecelEndTime`（r5apex.exe 偏移 0x2a50）；读取方 `Ground_GetDecel` 0x140a36580、`AirMove` 0x140a48f90、`WalkMove` 0x140a4a7c0；写入方 `Pred_RunCommand?` 0x14092ab70；ConVar `impulse_low_decel_duration_scalar` 静态初始化 0x1401c5fb0、对象 0x1422f65b0（值在 +0x60）；常数 0.5 在 .rdata 0x14157ce0c。偏移表 `research/epg/ghidra/r5apex-offset-0x2a50.tsv`、`r5apex_dx12-offset-0x2a50.tsv`（PR #85）。

---

### 5.39 EPG 火箭跳和被炸时的移动状态

#### 原理

火箭跳就是"朝脚下打一发 EPG"：§5.37 的规则加上一把推力足够大的武器。站着打能上 270 u（普通跳 55 u 的 5 倍）；**跳的同时开火**最好，推力叠在起跳速度上，能上 486 u。代价是自伤：每发 48.75 血，满血连跳两次就只剩 2.5。手感上它奖励时机（爆炸越接近起跳那一刻越高），和 P4（技巧窗口按时间算）一致。

#### 规则和公式

1. **武器**（EPG 的 `jump_kit` 模式，泰坦陨落时代留下的；R5 本地 S21 没人会装上它）[数据]：弹体 2000 u/s、无重力，碰到第一个世界表面或单位就炸（离表面 2 u）；伤害 65，内径 52 u、外径 180 u，爆炸推力 65000；对自己的伤害 × 0.75（`jump_kit` 那一行脚本，TF2 同一行）。原版 EPG 推力 30000，站着推不动（≤ 门槛），空中只有 287 u/s。
2. **本地 R5 拿不到能开火的 EPG**（模型缺失、开火回调是空桩），R5 的数据是"模拟开火"：服务端沿视线找落点、按 2000 u/s 等飞行时间、在落点调引擎的 `RadiusDamage`。真手雷做对照证明走同一条推人的路 [实测]。所以 R5 数据里爆炸比开火晚 0.05 – 0.25 s（服务端分帧），移动中的条件散布大。
3. **时机**（站着朝脚下 89°，R5）：站着开火 270 u；跳 + 开火同一帧 486 u；先开火 3 帧后跳 492 u；跳后 6 / 12 / 24 / 48 帧开火 455 / 421 / 327 / 196 u [实测]。越晚开火越低：起跳的上升速度被重力吃掉，爆点也离身体越远。
4. **俯视角**：89° 几乎全竖直；70° 约 45° 斜向后上（490 / 441）；45° 基本是水平冲刺（水平 525、只升 45 u）；30° 衰减到约一半（342）；20° 落点 196 u 已超外径，不推 [实测]。
5. **和移动状态**：

| 状态 | R5 | HSD（PR #52） | 依据 |
|---|---|---|---|
| 地面站着 / 走 | 门槛以上全额推、离地 | 同；向上推力抬 1 u 离地 | [实测] |
| 空中 | 推力不变，没有门槛 | 同 | [数据] [实测] |
| 跳的同一帧 / 刚跳 | 叠加在起跳速度上（486 / 492 u） | 同 | [实测] |
| 冲刺 | 推力相同；打在前面刹车（297 → 126）、打在后面加速（200 → 663） | 同（82 / 551） | [实测] |
| 蹲 / 滑铲 | 中心低到 24，水平分量更大：363 → 680；被推离地后滑铲结束 | 同（445 → 634） | [实测] |
| 击退后落地 | 无减速窗口（§5.38） | 同 | [反编译] |
| 跑墙 | **没测过** | 速度加到身体上，跑墙能力下一条命令按自己的规则处理（跑墙只在 Fun 里有，HSD 设计） | [推断] |
| 钩爪拉动中 | **没测过** | 速度加到身体上，拉力继续叠加，不脱钩 | [推断] |
| 滑索 / 翻越 / 攀爬 | **没测过** | 这几个状态每条命令自己设位置 / 速度，击退等于被忽略，状态不被打断 | [推断] |
| 跳板飞行中 | **没测过** | 速度加到引擎速度上（慢放照旧）；向上部分会被 HSD 天花板 1100 / 1250 夹 | [推断] |

6. **自伤**：65 × 0.75 = 48.75。HSD 玩家 100 血、6 s 后每秒回 12。按原生做，菜单"EPG 自伤"开关（默认开）[设计]。Gibraltar 被动 × 0.85（R5 实测掉 55）HSD 不做。
7. **TF2 对照**：同样 65000，TF2 站着 334 u、跳 + 开火约 716 u，高是因为重力 600（750 × 0.8）和半径 30 / 150；规则相同 [TF2 实测]。TF2 冲刺中武器放下，"冲刺跳 + 开火"实际在起跳后约 0.28 s 才炸 [TF2 实测]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| EPG 弹速 `projectile_launch_speed` | 50.8 m/s | 2000 u/s（重力 0） | 27.78 H/s | — | [数据] |
| EPG 伤害 / 对自己 | — | 65 / 48.75（× 0.75） | — | TF2 90 / 68 | [数据] |
| 普通原地跳最高点（对照） | 1.397 m | 55 u | 0.7639 H | — | [实测] |
| 站着朝脚下火箭跳最高点 | 6.858 m | 270 u（Unity 282） | 3.75 H | TF2 334 u（重力 600） | [实测] |
| 跳 + 开火最高点 | 12.34 m | 486 ± 15 u（Unity 同一爆炸时刻 487；同一命令开火 563） | 6.75 H | 先开火 3 帧后跳 492 u；TF2 约 716 u | [实测] |
| 滑铲中朝脚下：水平速度 | 9.22 → 17.27 m/s | 363 → 680 ± 32 u/s | 5.04 → 9.44 H/s | Unity 445 → 634 | [实测] |
| HSD 武器节奏（射速 / 弹匣 / 换弹） | — | HSD 设计值 1 发/s、5 发、2.5 s | — | 换弹是占位 | [设计]（射速、弹匣取 TF2 武器文件） |

**和 R5 的差别**（DIFF "RJA" 对照表，不是规则差别）：

1. **爆炸时刻**：R5 是服务端模拟开火，爆炸晚 0.05 – 0.25 s；Unity 是真弹体，同一帧开火约 0.03 s 就炸，起跳竖直速度还没掉，所以"跳 + 开火"Unity 563 u。同一爆炸时刻（Unity 起跳后 12 条命令开火）是 487 u，对上 486。
2. **战斗层的眼睛**：Unity 战斗层眼睛在原点正上方 60 u；R5 在 70 u、原点前 9 u。同样的俯视角，Unity 落点更近、推力更竖直：站着 89° 282 对 270（+4 %）、70° 200 对 160、45° 69 对 45、30° 14 对 0；20° 时 Unity 落点 165 u（在外径内，推力 142 u/s），被地面门槛挡住，结果一样不动。要改是战斗层整体的眼睛（影响所有武器），没改。

#### 实现模板

```
// 单位：u、s
EpgLauncher.step(now):
    if fire and now >= nextShot and mag > 0:
        spawn EpgBolt(from = eye, dir = aim(yaw, pitch), speed = 2000, gravity = 0)
        nextShot = now + 1.0; mag -= 1
EpgBolt.step(dt):
    seg = pos → pos + dir * 2000 * dt
    hit = first(worldHit(seg) → hitPoint + normal * 2, unitHit(seg, 不含自己和队友))
    if hit: explode(hit, damage 65, rIn 52, rOut 180, Fexp 65000, attacker = owner, ownerScale = selfDamage ? 0.75 : 0)   // §5.37
```

Unity 参考实现（HSD-Unity PR #52，还没合并；分支 `rj/knockback-a`）：`HSD-Unity: Assets/HSD/Game/Runtime/Combat/Epg.cs`（`EpgLauncher.Step`；`EpgBolt` 常数 `Speed` 2000、`Damage` 65、`Inner` 52、`Outer` 180、`Impulse` 65000、`OwnerScale` 0.75、`SurfaceOffset` 2，[u]；`EpgBolt.Step`）；测试点 `CombatSim.RocketJumpSpot`、`CombatSim.RocketJumpMarks`（55 / 270 / 486）、`CombatSim.GoToRocketJump`；菜单"EPG 自伤"（`hsd.tf2.x.epgself`）、`CombatLoadout.epgSelfDamage`、`CombatLoadout.nativeKnockback`。HUD 的火箭跳最高点 `CombatSim.rocketJumpApex`。

#### 验收

- `RjaKnockbackTests.TheEpgBoltFliesAt2000AndHurtsItsOwnerAtThreeQuarters`（PR #52）：一条命令飞 2000·dt；自伤 48.75；关掉自伤推力照样有。
- `RjaKnockbackTests.TheEpgRocketJumpMatchesR5`（PR #52）：18 个条件对 #64 打表（写 `Temp/rja_vs_r5.tsv`）；断言站着最高点 270 ± 15 %（Unity 282）、跳后 12 条命令开火 486 ± 5 %（Unity 487）、20° 不动。
- 对照数据：EPG §2（29 个条件，`research/epg/data/summary.csv`）；DIFF RJA 对照表。
- 合格线：同上两条断言；规则层面（大小、方向、衰减、上限、门槛）和 §5.37 合格线相同。最高点的差别只接受"爆炸时刻"和"战斗层眼睛"两个已知来源。
- 没测过：跑墙 / 钩爪 / 滑索 / 翻越 / 跳板飞行中被炸（R5 或 TF2 都可以补，B05-4）；直接命中的冲击力；正式服 EPG-1（S23）的数值。

#### 出处

- EPG §1 – §6：模拟开火、29 个条件、时机和角度表、武器文件、自伤脚本、局限。main
- RJ §8 – §10：自伤、状态交互表、Unity 对照要点。（PR #85，还没合并；分支 `rj/knockback-a`）
- DIFF "RJA" 对照表：18 个条件的 R5 / Unity 和"差在哪"。（PR #85，还没合并；分支 `rj/knockback-a`）
- TF2-EPG §1：TF2 真开火的高度、冲刺不能开火。main
- [数据] `scripts/weapons/mp_weapon_epg.txt`（`impulse_force` 5000、`impulse_force_explosions` 30000、`jump_kit` 17500 / 65000、`explosion_damages_owner` 1、半径 52 / 180、弹速 2000）；`_base_gametype.gnut`（`jump_kit` 自伤 × 0.75）。游戏解包文件在私有仓库 HSD-RawData（D-76），不在研究仓库。

---

---

## 第六部分 · 传送和相位（§5.40 – §5.46）

**白话说明（这一部分管什么）**

Apex 里"传送"看起来有很多种，拆开以后只有三样东西：

1. **相位**：一个时间窗口。窗口里的人不和别的东西互动（不被跳板弹、不被升梯抬、不和别的玩家碰、不被锁定），但**照样撞墙、照样走路跑步**。Wraith 的虚空（Into the Void）就是"只开相位、自己跑"。
2. **隧道**：把人挂在一个看不见的载体上，沿一串路径点 0.1 s 一步地送过去，到了以后**速度清零**。Wraith 的传送门（Dimensional Rift）和 Ash 的相位突破（Phase Breach）都是这一套，只是路径来源不同：Wraith 是自己跑过的路，Ash 是一条直线。
3. **瞬间传送**：两点之间直接换位置。Loba 手环（速度清零）、Alter 虚空通道（出口给一个 50–300 u/s 的速度）。这两个 HSD 搁置了，只留规则。

**结论先说**：S21 里**没有一种传送会把你的速度带过去**。Wraith 门、Ash 突破、Loba 手环出来都是 0；只有 Alter 战术（HSD 没做）出口给一个按进门速度截断的小速度。"带速度穿门"如果 HSD 要做，是 HSD 自己的设计，不是 Apex 的规则（M4 P3 的结论，PORTAL-R2 和 M6-B 实测确认）。

和别的章的分界：

- 技能的冷却、充能、按键、UI、仲裁优先级在第 10 章；这里只写移动规则，仲裁只写"会结束哪些别的状态"。
- 出门以后的地面起步、lurch、滑铲按第 03、04 章的普通规则；本节只写出口状态（位置、速度、能不能马上动）。
- 速度在技能之间怎么叠、谁收走谁的动量，详见第 06 章；本节只写 speed_boost 的叠法（大的赢）。
- 跳板、钩爪、滑索是第 05 章别的条目；本节只写它们和相位、传送门的交互。

**本节出处缩写**（第一次出现时用；其余沿用 DESIGN-PHILOSOPHY §2.2，例如 DIFF、DEC）：

| 缩写 | 文件 |
|---|---|
| N8A / N8B / N8C / N8D / N8E | `research/rea-native/n8/` 下 `N8-A-SHARED-SYSTEM.md`、`N8-B-RULES.md`、`N8-C-PHASE-NATIVE.md`、`N8-D-MEASURE.md`、`N8-E-UNITY.md` |
| WR | `research/phase2-local/m10/r_wraith/WRAITH-M10.md`（M10 Wraith 第一轮实测） |
| PR2 | `research/phase2-local/m10/r2_wraith/PORTAL-R2.md`（传送门 24 次出口实测） |
| SB2 | `research/phase2-local/m10/r2_speedboost/SPEEDBOOST-R2.md`（speed_boost 严重度 → 移速倍率） |
| M10W | `research/phase2-local/m10/unity/M10W-UNITY.md`（Unity 的 Wraith 实现报告） |
| D4 | `research/phase2-local/m10/unity/M10D4-UNITY.md`（反向输入不减速的缺陷修复） |
| P3 | `research/phase2-local/m4/p3_transitions/P3-TRANSITIONS.md`（M4 传送过渡实测） |
| M6B | `research/phase2-local/m6/b_legends/M6-B-REPORT.md`（Alter、Loba、Ash、Valkyrie） |
| SHELF | `SHELVED-ABILITIES.md`（Loba、Alter 搁置） |
| N9 | `research/rea-native/n9/N9-NATIVE.md`（升梯、喷气、重力炮原生） |
| LG | `research/phase2-local/m4/lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md` |
| LIFT8 | `research/phase2-local/m8/r_lift/LIFT.md` |
| VR | `research/phase2-local/m4/valk_rev/VALK-REV-PRIMITIVES.md` |
| REV9 / REV8 | `research/phase2-local/m9/r_rev/REVENANT.md`、`research/phase2-local/m8/r2_revenant/REVENANT-CLIMB.md` |
| VAN9 / VAN8 | `research/phase2-local/m9/r_vantage/VANTAGE.md`、`research/phase2-local/m8/r2_vantage/VANTAGE-JETDRIVE.md` |
| U: | HSD-Unity 仓库；`U:…/` = `Assets/HSD/R5Replay/Runtime/` |

记号：H = 72 u（[01 §4.1](01-units-body.md)）；W = 手持倍率（空手拿近战 1.15，技能收起武器时 1.0）；msc = 移动倍率；"命令" = 一条 usercmd（Unity 1/120 s）。

---

### 5.40 相位：一个只关掉"互动"的时间窗口

#### 原理

相位让玩家"在虚空里"：别人打不到、碰不到，跳板和升梯也不理你。但它**不是穿墙**：墙、地板、走路跑步的手感全都不变。这样虚空是一个"躲"的工具，不是一个"捷径"工具——能去哪里，还是由你自己跑过的路决定。虚空里变快不是相位给的，是技能另外加的移速加成（5.41）。

所有传送类技能在原生层用的是**同一个相位状态**，类型（Wraith 战术、Wraith 大招、Ash、Alter…）只被脚本读来换特效和决定加不加速，移动代码只看时间窗口。

#### 规则和公式

1. 相位是实体上的三个数：类型、开始时刻 t₀ = 发动时刻 + warmup、结束时刻 t₁ = t₀ + duration。取消 = 把结束时刻清零。
2. **在相位中** ⇔ t₀ ≤ now ≤ t₁（另有一个禁用标志，为真时相位无效，含义没查清）。warmup 期间"已发动"的查询为真，但移动上的效果从 t₀ 才开始。[反编译]
3. 在相位中时**跳过**：
   - 跳板发射（Octane 跳板）[反编译 + 实测 3 / 3 不发射，对照 6 / 6 发射]；
   - Horizon 升梯（不上升、不因悬停弹出）[反编译]；
   - 另外两种移动触发区（类型 4 / 8，没认出是什么）[反编译]；
   - 和别的玩家的推挤、和玩家碰撞组的碰撞 [反编译 + 推断]；
   - 被智能弹药锁定、被逐实体的射线检查选中 [推断]；
   - 触发器接触走另一条过滤分支：**相位中走进 Wraith 传送门不传送**（实测 0 / 3，对照 3 / 3）[实测，原因是推断]。
4. 在相位中时**不变**：和世界几何的碰撞、地面摩擦和加速、空中加速、下蹲、重力。[反编译]
5. **重力炮没有相位检查**：相位中照样被发射（和跳板不同）。HSD 不做重力炮（D-21）。[反编译]

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| Wraith 战术相位时长（`charge_time`） | — | 4.0 s | — | 实测 3.9–4.0 s（10 Hz 记录） | [数据] [实测] |
| Wraith 战术 warmup | — | 0 s | — | — | [数据] |
| Alter 战术传送后的相位（类型 `DOOR`，不加速） | — | 1.0 s | — | 没测过（HSD 没做） | [数据] |

#### 实现模板

```
// 单位：s
phaseActive(now) = (phaseStart <= now <= phaseEnd) and not phaseDisabled
每个"互动"入口在开头检查一次：
    jumpPad.launch:      if phaseActive(now): return
    gravityLift.update:  if phaseActive(now): return   // 相位中离开升梯：结束升梯状态，无弹出速度，2 s 再进门槛照样开始计时
    portal.touch:        if phaseActive(now): mark occupied; return   // 要离开再进
世界碰撞、Friction、Accelerate、AirAccelerate、Duck、gravity：不看相位
```

Unity 参考实现：Unity 没有通用的"实体相位"字段，相位由 `IntoTheVoidAbility.Phased(now)`（`U:…/Abilities/IntoTheVoid/IntoTheVoidAbility.cs`）提供，三个读它的地方：

- 跳板：`JumpPadParams.phasedNoLaunch`，由 `MovementConfig.padPhasedNoLaunch` 打开（Reference true，Fun 继承；配置之外、回放工具关）（D-19 E-1）。
- 升梯：`GravityLiftParams.phasedNoLift`，由 `MovementConfig.liftPhasedNoLift` 打开（同上）（D-21 L-1）。
- 传送门：`DimensionalRiftAbility` 在相位中不送人、大招按键无效不扣充能。

**名字撞车，注意**：Unity 电机里的 `CommandModifiers.phased`（`R5MotorV2.phased`）**不是**这里的相位窗口，而是"这条命令是运动学移动，世界不做扫掠"，用于隧道旅行（5.42、5.43）时穿过实体。R5 的相位窗口不改世界碰撞。

#### 验收

- `N8ETeleportTests.APhasedBodyWalksOverThePadWithoutALaunch`（Reference / Fun）：相位中走过跳板不发射。
- `N8ETeleportTests.WithoutTheVoidOrAfterThePhaseThePadLaunches`：没有虚空、或相位结束后，照常发射。
- `N8ETeleportTests.ReferenceAndFunTurnTheRuleOnOutsideAConfigItIsOff`。
- `N9LiftPhaseTests.APhasedBodyIsNotLiftedUntilThePhaseEnds`：相位（1.175–5.175 s）中不被抬，结束后 5.17–5.3 s 内被抬。
- `N9LiftPhaseTests.WithoutTheVoidTheLiftTakesTheBodyAtOnce`、`N9LiftPhaseTests.ReferenceAndFunTurnTheRuleOnOutsideAConfigItIsOff`。
- `RiftM10WTests.PhasedBodiesWalkThroughPortalsAndTheirUltimatePressDoesNothing`。
- 对照数据：N8D §1（会话 `20261024_025925_N8_phasepad`）：相位中最大上升 0.7 u、vz 0；对照 707.8 u、vz 1001–1011 u/s。
- 合格线：相位中跳板 / 升梯 / 传送门 0 次触发；相位外 100 % 触发。

#### 出处

- N8C §1–§4：相位只是时间窗口；读窗口的函数表；世界碰撞不变。main
- N8D §1：相位中踩跳板 3 / 3 不发射。main
- N8A §2：相位类型表（类型只影响特效和加速）。main
- PR2 TL;DR "Into the Void" 行：相位中走过传送门不传送（0 / 3）。main
- N9 §4、§7：重力炮没有相位检查；L-1 升梯相位规则。main
- D-19（E-1）、D-21（L-1）。main
- [反编译] `PhaseShiftBegin` 0x1408ac780（类型 +0x19dc、开始 +0x19e0、结束 +0x19e4）；`PhaseShiftCancel` 0x1408ac640；`IsPhaseShiftedOrPending` 0x1408ac8e0（禁用标志 +0x690）；`JumpPadLaunch` 0x140a38a90；升梯 / 类型 4 处理 0x140a39420；类型 8 处理 0x140a3a620；玩家 ShouldCollide 0x140b07e20（碰撞组 0x10）；触发器过滤 0x1409fbac0；`GravityCannon_Launch` 0x140a3af30。

---

### 5.41 技能移速加成（speed_boost）

#### 原理

虚空里变快、放传送门时变快、Octane 兴奋剂变快，用的都是同一个"移速加成"状态：一个 0–1 的严重度，换算成移动倍率乘到走路和冲刺的上限上。两个加成同时有时**取大的，不相加**——技能之间不能叠出离谱的速度（对应 DESIGN-PHILOSOPHY P3：给速度也要有明确规则）。

#### 规则和公式

1. 严重度 S 按字节存：q(S) = floor(255·S) / 255。
2. 移动倍率 msc = W · (1 + 2·q(S))。W = 1.15（拿近战，HSD 所有基线）或 1.0（技能收起 / 锁住武器：传送门放置、虚空）。
3. 冲刺上限 = 260 u/s × msc，走路上限 = 173.5 u/s × msc（第 03 章）。
4. 同时有两个：取严重度大的（0.2 + 0.1 → 0.2）。
5. 定时加成（时长 D、淡出 F）：先保持 D − F，再在时长**以内**线性淡出到 0。
6. HSD 另有一个总上限 `SkillRules.maxSpeedBoost`（默认 ×1.40，[设计]）；Wraith S21 预设改成 ×2.0，否则会削掉虚空的 ×1.596 和放置的 ×1.996。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 倍率公式里的 2（`movement_speedboost_extraScale`） | — | 2（×） | — | 实测和模型差 0.0000 | [数据] [实测] |
| 拿近战的 W | — | 1.15（×） | — | 拿枪时按武器 | [实测] |
| 收起武器的 W | — | 1.0（×） | — | — | [实测] |
| S = 0.2 收起武器的冲刺（传送门放置） | 9.246 m/s | 364 u/s | 5.056 H/s | — | [实测] |
| S = 0.3 收起武器的冲刺（虚空） | 10.54 m/s | 414.98 u/s | 5.764 H/s | — | [实测] |
| S = 0.4 / 0.5 收起武器的冲刺 | 11.89 / 13.18 m/s | 468 / 518.98 u/s | 6.500 / 7.208 H/s | — | [实测] |
| S = 1.0 拿近战的冲刺（上限检查） | 22.78 m/s | 897 u/s | 12.46 H/s | — | [实测] |
| HSD 加成总上限（一般预设 / Wraith S21） | — | ×1.40 / ×2.0 | — | — | [设计] |

#### 实现模板

```
// 单位：u、s
q(S)        = floor(255*S + 1e-9) / 255
factor(S)   = 1 + 2*q(S)
S_now       = max(所有在效的加成的 S(t))        // 不相加
timedS(t)   = t < D-F ? S : (t < D ? S*(D-t)/F : 0)
msc         = W * factor(S_now)                // W：技能锁武器时 1.0，否则 1.15
```

Unity 参考实现：`U:…/Abilities/_Core/SpeedBoost.cs`（`SpeedBoost.Quantize`、`Factor`、`MoveScale`、`Combine` = max、`TimedSeverity`；`HandScale` 1.15、`LockedScale` 1.0、`ExtraScale` 2）。总上限在 `U:…/Abilities/_Core/SkillRules.cs`（`maxSpeedBoost` 1.40；`SkillLoadouts.WraithS21()` 改 2.0）。旧技能没有改用它，但数值一致：Octane 兴奋剂 38/255 = q(0.15)；M4 的 `StimParams.WraithPhase()` ×1.388 × 1.15 = 1.5962（规则 1.596078，冲刺差 0.03 u/s，为了 M4 回放逐字节不变保留）。

#### 验收

- `SpeedBoostM10WTests.MoveScaleIsWTimesOnePlusTwiceTheByteSeverity`：SB2 表 8 行，误差 5 × 10⁻⁵。
- `SpeedBoostM10WTests.LockedHandsGiveThePortalAndVoidSprints`：364 / 414.98 / 468 / 518.98 u/s。
- `SpeedBoostM10WTests.TheLargerBoostWinsAndATimedBoostFadesLinearlyInsideItsDuration`。
- `SpeedBoostM10WTests.TheOlderStimAndPhasePresetsAgreeWithTheRuleOrAreReported`。
- 对照数据：SB2 TL;DR 表（25 次，会话 `20261023_000555_M10R2_s1`）。合格线：msc 和公式差 < 10⁻⁴。

#### 出处

- SB2 TL;DR：公式、字节量化、取大、淡出在时长以内。main
- M10W §1：Unity 共用公式，旧兴奋剂 / 旧相位预设核对。main
- `research/phase2-local/m5/SKILL-RULES.md` §4：HSD 总上限 1.40。main

---

### 5.42 Wraith 战术：虚空（Into the Void）

#### 原理

按下以后先有一段"准备"（收起武器、减速、冲刺被打断），然后进入 4 s 相位，期间自动冲刺而且明显变快（冲刺 415 u/s，比平时快 39 %），最后加速慢慢退掉。它本身**不移动玩家**：你在虚空里还是用普通的走跑规则，撞墙照样撞。准备期的减速就是这个技能的"预告"（P9：威力换预告）。

#### 规则和公式

时间从按下算（S21，本地混合构建实测；准备减速的形状是重读客户端 usercmd 拟合的）：

1. 0 – 0.367 s：什么都不变（W 1.15，冲刺继续）。
2. 0.367 – 1.167 s：收起武器（W 1.0），减速 0.2：msc 从 0.8 按余弦升回 1.0（0.8 s）；**冲刺被打断**，身体按走路上限 173.5 × msc 走（0.81 s 时约 140.6 u/s）。
3. 1.175 s：进入相位（5.40），持续 4.0 s（到 5.175 s）。
4. 1.175 – 3.975 s：speed_boost S = 0.3 → msc = 1.0 × (1 + 2 × 76/255) = 1.596078，**自动冲刺**，冲刺 414.98 u/s。
5. 3.975 – 5.167 s：msc 按余弦淡回 1.0（1.192 s）。R5 淡出中间有一个小肩（1.094 约 0.07 s），没建模。
6. 之后：R5 停在 1.0（空手，直到拔枪）；**HSD 回到 1.15**（HSD 没有武器槽，[设计]）。
7. 运行中再按：无效。相位中按 Wraith 大招：无效，不扣充能 [实测 n 2]。

N8B §1 写的"0.8 s 准备（`deploy_time`）"和实测对得上：准备减速本身是 0.8 s，只是从按下后 0.367 s（收武器动作）才开始 [推断]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 按下 → 准备减速开始 `deployDelay` | — | 0.367 s（44 条命令） | — | 12 次相同 | [实测] |
| 准备减速量 `deploySlow` / 时长 `deployRamp` | — | 0.2（×）/ 0.8 s | — | — | [数据] [实测] |
| 按下 → 相位 `phaseStart` | — | 1.175 s | — | 实测 1.1756，sd 0.0013 | [实测] |
| 相位时长 `phaseDuration` | — | 4.0 s | — | 实测 3.9–4.0 s | [数据] [实测] |
| 加成严重度 `severity` | — | 0.3（q = 0.298） | — | — | [数据] [实测] |
| 加成保持 `boostHold` | — | 2.8 s | — | 实测 2.796 s | [实测] |
| 淡出 `fadeDuration` | — | 1.192 s（143 条命令） | — | 淡出肩部误差约 0.04 | [实测] |
| 相位中冲刺 | 10.54 m/s | 414.98 u/s | 5.764 H/s | — | [实测] |
| 准备期走路上限（msc 0.81） | 3.571 m/s | 140.6 u/s | 1.953 H/s | 随余弦变 | [实测] |
| 淡出后的 W | — | R5 1.0；HSD 1.15 | — | — | [实测] / [设计] |

#### 实现模板

```
// 单位：u、s。t = now - pressTime
msc(t):
    t < 0.367                  → 不管
    t < 0.367 + 0.8            → 1.0 * (0.8 + 0.2*(0.5 - 0.5*cos(pi*(t-0.367)/0.8)));  blockSprint
    t < 1.175                  → 1.0;  blockSprint
    t < 1.175 + 2.8            → 1.0 * (1 + 2*q(0.3));   forceSprint
    t < 1.175 + 2.8 + 1.192    → 1.0 + (peak-1.0)*(0.5 + 0.5*cos(pi*f));   f = 进度
    else                       → 不管（HSD 回 1.15）
phased(t) = 1.175 <= t < 5.175
```

Unity 参考实现：`U:…/Abilities/IntoTheVoid/IntoTheVoidAbility.cs`，`VoidS21Params`（字段同上表，全部 [u]）、`IntoTheVoidAbility.MoveScaleAt`、`Phased`、`BeforeMove`（`BlockSprint` / `ForceSprint` 是 M10-W 加到 `MovementAbilitySet` 的两个电机钩子）。只在 Wraith S21 预设里用（Q，冷却 25 s [设计]）。

旧版（平行保留）：`U:…/Abilities/Stim/StimAbility.cs` 的 `StimParams.WraithPhase()`（id `wraith_phase`，Revenant-Wraith ground 预设）：0 s 起 ×0.80 → 0.92 到 1.17 s、×1.388 × 1.15 保持 2.77 s、0.79 s 淡回 1.15，冲刺不打断。和 R5 的差别（准备早 0.37 s、0.92 不是 0.8、冲刺没打断、淡回 1.15 不是 1.0）按用户要求不改（D-39），只为 M4 回放逐字节不变。

#### 验收

- `VoidM10WTests.TheVoidTimelineMatchesTheR5MoveScale`（Reference / Fun）。
- `VoidM10WTests.PhasedFromTheDeployEndForFourSecondsWithAutoSprintAndARefusedRepress`。
- `VoidM10WTests.TheWraithPresetHasTheS21VoidAndRiftAndTheOldPresetIsUnchanged`。
- 演示 `m10w_void_portal`（相位中穿过两个门不传送；晚按 1.5 s 的失败版会传送），由 `MovementDemoTests.EveryDemoFailsWithItsFailureShift` 和 `M10WGameTests.TheM10WDemosCoverTheWraithItems` 检查。
- 对照数据：M10 5 次 + M4 7 次虚空的客户端 usercmd 移动倍率（WR、P3）。合格线：平台 msc 和 1.596078 差 < 10⁻⁴；冲刺 414.98 ± 0.05 u/s；相位开始 1.175 ± 1 条命令；淡出最大误差 ≤ 0.04（已知的肩部）。

#### 出处

- WR TL;DR "Into the Void" 行：0.80 / 1.175 s / 1.5961 / 2.80 s / 414.98。main
- M10W §2：重读客户端 usercmd 的时间表；和旧 M4 预设的逐项差别。main
- P3 "Wraith, Into the Void"：M4 的 7 次实测（旧预设的来源）。main
- N8B §1：脚本时间线（`deploy_time` 0.8、`charge_time` 4、`speed_boost` 0.3、结束前 1.5 s 预告特效、冷却 15 s）。main
- N8D §1：相位类型 1（`BALANCE`）、时长 3.9–4.0 s、严重度 0.30。main
- D-39（旧 Revenant-Wraith 预设当历史保留）。main
- `U:…/Abilities/IntoTheVoid/README.md`。main

---

### 5.43 Wraith 大招：次元裂隙传送门（Dimensional Rift）

#### 原理

传送门不是"两点之间瞬移"，而是"**把你自己刚跑过的路，快放一遍**"。放门时 Wraith 自动冲刺、越跑越快；放好以后两个门都能进，进去就沿着录下来的路被快速送到另一头，到了以后**站定、速度为 0**。

这样设计的效果：

- 门**不能穿墙**——路是你真跑过的；能去的地方由放门的人决定。
- 出门速度为 0，所以传送门是"位置工具"，不是"速度工具"：想带着速度过门不行（P3：动量只有明确规则才给 / 收，这里的规则就是"清零"）。
- 门存在 45 s、双向、可以反复用；为了不来回弹，站在出口不会被送回去，离开以后要隔一会儿才能再进。

#### 规则和公式

**放置**

1. 按大招 → **举手**：手持倍率保持 0.375 s，然后 msc 从 0.2 按余弦回到 1.0（0.6 s，W 1.0），冲刺被打断（299 → 约 64 u/s）。
2. 按下后 **1.04 s** 记录起点（脚下），开始放置：每 0.1 s 记一个路径点（位置、是否着地；R5 还记速度、下蹲、动作），自动冲刺，W 1.0。
3. 放置加速：严重度 = min(0.5, max(0.2, 距离档))。距离档从 0.1 起，**离起点的直线（三维）距离**超过"上一档的百分比 + 20 %"（以 6000 u 为 100 %）时 +0.1，并把"上一档"改成这次越过时的百分比（不是整 20 % 的格子）。所以平地从静止起，冲刺 364 → 415 → 468 → 519 u/s 分别在约 40 / 60 / 80 % 处。
4. 放置结束：再按一次；或水平路径走满 6000 u；或放置满 10 s。出口放在脚下。
5. 出口离起点的直线距离 < 128 u：**作废**，起点删掉，**不扣大招**。
6. 结束后：放置加速再保持 0.1 s，然后空手（W 1.0）1.0 s，再回到手持倍率。
7. 两个门存在 45 s。

**旅行**

8. 身体原点进入任一门的触发范围 → 沿路径送到另一个门（双向）。旅行中：运动学、无碰撞、忽略输入；会结束把身体带进门的滑索 / 钩爪 / 攀爬状态。
9. 旅行时长 T = clamp(L / 1024, 0.3, cap)，L = 路径长度；cap = 2.0 s，L 在 3000 → 6000 u 之间线性放宽到 3.5 s。按整 0.1 s 一步走（取整见第 10 条），再加进门 0.1 s 和出门 0.1 s。
10. **出口速度正好为 0**，不管进门速度多少（173–593 u/s 都一样）、不管哪个方向。R5 旅行中把每个路径点录下的速度写进速度字段（读出来是 364 … 177 … 0），但出门时解除挂载、直接设位置，人是静止的。
11. **到达时**：站在到达的门上不会被送回去（门处于"占用"，要离开触发范围才解除）。
12. **再进**：R5 脚本是进入 0.5 s 防抖、**离开后 1.0 s 内不能再进**。HSD 按 1.0 s（D-19 E-2，改前 0.5 s）。**1.0 s 没实测**：实测只到"走出去 0.5 s 再走回来能再进"，总间隔没细分（B05-5）。
13. 相位中（5.40）碰到门：不传送（要离开再进）；相位中按大招：无效、不扣充能。

**R5 有、HSD 改了或没做的**（全部 [设计]，M10W §3、§8）：

- 触发范围：HSD 半径 32 u、−36 … +72 u；R5 蹲姿路径点的触发区半径 16、高 32（蹲 16），站姿的大小没读到。D-19 E-4 保留设计值。
- R5 旅行中视角沿路径插值（每步 0.4 s），短旅行出门时朝向没稳定；HSD 不转视角。
- R5 强制蹲姿路径点；HSD 不强制。
- 新的一对门建成时替换旧的；放置中不能穿门（碰到的门要离开再进）；举手中再按一次 = 取消不扣充能。
- R5 终点被挡时停在最后一个站得下的点（D-19 E-5 不建模）；按住放置（R5 按住能放到约 8.6 s）、3 m 内滑行退还加速、别的玩家 / 投射物穿门、冷却升级都没做。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 按下 → 起点 `raiseTime` | — | 1.04 s | — | 客户端 1.009–1.060 s；dedi 10 Hz 行 1.11–1.17 s（同一事件的两侧） | [实测] |
| 举手减速 `raiseSlowStart` / `raiseSlowRamp` / `raiseSlowMin` | — | 0.375 s / 0.6 s / 0.2（×） | — | — | [实测] |
| 放置基础严重度 `baseSeverity` | — | 0.2 | — | — | [实测] |
| 距离档起点 / 每档 `trackerStart` / `stepSeverity` | — | 0.1 / 0.1 | — | — | [数据] [实测] |
| 每档距离 `stepPercent` × `stepDistance` | 30.48 m | 20 % × 6000 = 1200 u | 16.67 H | 实测 43–48 / 65–71 / 87 %（下落中，10 Hz 采样推后） | [数据] [实测] |
| 严重度上限 `maxSeverity` | — | 0.5（q 0.498） | — | — | [实测] |
| 路径点间隔 `nodeInterval` | — | 0.1 s | — | — | [数据] |
| 最长水平路径 `maxDistance` | 152.4 m | 6000 u | 83.33 H | — | [数据] |
| 最长放置时间 `maxPlaceTime` | — | 10 s | — | — | [实测]（PR2） |
| 最短门距 `minGap` | 3.251 m | 128 u | 1.778 H | 实测 125.7 无门、141.7 起有门 | [数据] [实测] |
| 结束后加速保持 / 空手 `endBoostHold` / `endHolster` | — | 0.1 s / 1.0 s | — | 实测 0.07–0.14 / 0.97–1.04 s | [实测] |
| 门寿命 `lifetime` | — | 45 s | — | 实测 45.1 s | [数据] [实测] |
| 旅行速度 `travelSpeed` | 26.01 m/s | 1024 u/s | 14.22 H/s | — | [数据] |
| 旅行最短 / 最长 `minTravelTime` / `maxTravelTime` | — | 0.3 s / 2.0 s | — | — | [数据] |
| 长路径放宽起点 / 终点 `longPathFrom` / `longPathTo` | 76.2 / 152.4 m | 3000 / 6000 u | 41.67 / 83.33 H | — | [数据] |
| 长路径最长 `longPathMaxTravelTime` | — | 3.5 s | — | 实测 6100–6190 u → 3.7 s | [数据] [实测] |
| 进门 / 出门 `travelInTime` / `travelOutTime` | — | 0.1 s / 0.1 s | — | 合计 +0.2 s 是实测，拆法是 [设计] | [实测] [设计] |
| 出口速度 | 0 m/s | 0 u/s | 0 | 24 / 24 | [实测] |
| 再进间隔 `reuseDebounce` | — | 1.0 s（脚本）；HSD 1.0 s | — | **没实测**（只知 ≤ 走出 0.5 s + 走回来） | [数据] |
| 触发半径 / 高 `portalRadius` / `portalHeight`（HSD） | 0.813 / 1.829 m | HSD 设计值 32 / 72 u | 0.444 / 1 H | R5 蹲姿 16 / 32 u（0.222 / 0.444 H） | [设计]；R5 [数据] |

旅行时长的几个实测点（dedi 行，n 24）：349–374 u → 0.5 s，455–482 u → 0.6 s，6166–6190 u → 3.7 s；平均速度 1160–1250 u/s（短路径），约 1700 u/s（长路径，含竖直）。

#### 实现模板

```
// 单位：u、s
状态：Idle → Raising → Placing → Idle（有一对门）；任意门触发 → Travel → Idle

Raising:  msc = raiseScale(t);  t >= 0.375 时 blockSprint
          再按 → 取消（不扣）
          t >= 1.04 → nodes = [feet]; tracker = 0.1; lastPct = 0; Placing
Placing:  W = 1.0; msc = 1 + 2*q(min(0.5, max(0.2, tracker))); forceSprint
          每 0.1 s: nodes.add(feet); horiz += |Δxy|
                    pct = 100*|feet - nodes[0]| / 6000
                    if pct > lastPct + 20: tracker += 0.1; lastPct = pct
          再按 / horiz >= 6000 / 10 s → endPlacement
endPlacement: gap = |feet - nodes[0]|
          gap < 128 → 作废，不扣
          否则 path = nodes + [feet]; 两门 45 s; 扣充能; 出口标"占用"
每条命令（Idle 且有门）:
          离开某门的触发范围 → 该门"占用"解除
          进入未占用的门 且 now >= lastExit + 1.0 且 不在相位 → Travel
          （相位中进入：标占用，不传送）
Travel:   frames = floor(clamp(L/1024, 0.3, cap(L)) / 0.1)
          total  = frames*0.1 + 0.1 + 0.1
          位置 = 0.1 s 内从入口到第一个点 → 匀速沿路径 → 停在终点
          运动学、无碰撞、锁输入、结束别的 Driver
          结束：pos = 终点, vel = 0, grounded = 终点是否着地, 到达门"占用", lastExit = now
```

离散化要注意：R5 每 0.1 s 走一步（服务器 10 Hz），Unity 按 120 Hz 命令在步与步之间连续插值；两者在出口时刻和出口速度上一致，旅行中的中间位置不一样（没对照，也没有对照的意义：R5 旅行中客户端预测关了）。

Unity 参考实现：`U:…/Abilities/DimensionalRift/DimensionalRiftAbility.cs`，`RiftParams`（字段同上表，全部 [u]）、`DimensionalRiftAbility.TravelTime` / `TravelFrames` / `TravelDuration` / `RaiseMoveScale` / `PathPoint` / `InPortal` / `BeforeMove` / `AfterMove` / `BeforeMoveLate`（旅行用 `CommandModifiers.kinematic` + `phased`，`kinematicVelocity` = 0）/ `PlacePair`（测试和场景用）。仲裁行 `SkillLoadouts.RiftTraits()`（`exclusiveOnDrive`）。预设 Wraith S21（键 `'`，Z，冷却 20 s [设计]，R5 3 min）。训练场 `PracticeMapM10W.cs`（WL 放置跑道、WT 下落塔）。Reference = Fun。

#### 验收

- `RiftM10WTests.TravelTimeFitsTheR5Rows`（10 行：349.2 / 357.7 / 373.7 u → 0.5 s，454.9 / 481.6 u → 0.6 s，6165.9 / 6190.1 u → 3.7 s，128 u → 0.5 s，3000 u → 2.2 s，4500 u → 2.9 s；误差 10⁻⁹）。
- `RiftM10WTests.TheRaiseSlowsThenTheStartNodeAndThePlacementBoostComeAt104Seconds`（冲刺 299 → 最低 64.3 ± 3 → 364）。
- `RiftM10WTests.AfterTheExitPressTheBoostHoldsATenthThenTheHandsStayEmptyForASecond`。
- `RiftM10WTests.AnExitCloserThan128CancelsAndKeepsTheChargeAFartherOneSpendsIt`。
- `RiftM10WTests.TheSpeedStepsFollowTheStraightDistanceReBasedOnEachCrossing`（下落 6000 u：44.0 / 65.7 / 87.2 %；R5 43–48 / 65–71 / 87 %）。
- `RiftM10WTests.ThePlacementEndsAtTenSecondsOrAtTheHorizontalDistance`。
- `RiftM10WTests.TheExitIsAtRestWhateverTheEntrySpeedInBothDirections`（走 / 冲刺 / 滑铲 × 两个方向）。
- `RiftM10WTests.StandingOnTheArrivalPortalSendsNobodyBackAndSteppingOutAndInTravelsAgain`、`RiftM10WTests.PhasedBodiesWalkThroughPortalsAndTheirUltimatePressDoesNothing`、`RiftM10WTests.PortalsLiveFortyFiveSeconds`、`RiftM10WTests.TheTravelIgnoresInputAndPassesThroughSolids`、`RiftM10WTests.AZiplineRideIntoAPortalEndsTheRide`、`RiftM10WTests.AGrapplePullIntoAPortalEndsThePull`、`RiftM10WTests.FromTheRestingExitAJumpAndATapStrafeStillWork`、`RiftM10WTests.NoTravelWhilePlacingAndANewPairReplacesTheOld`。
- `N8ETeleportTests.TheRiftTakesTheBodyAgainOnlyOneSecondAfterAnExit`：**只检查参数值是 1.0**，没有一条测试检查"离开 0.99 s 不能进、1.01 s 能进"的行为（见 `_notes/hb-ch05.md`）。
- 游戏侧：`M10WGameTests.TheWraithPresetIsTheNinthLoadoutInBothConfigs`、`M10WGameTests.TheWraithYardIsAppendedAfterEveryOlderItemAndFree`、`M10WGameTests.TheM10WDemosCoverTheWraithItems`、`M10WGameTests.TheHudNotesReadTheRiftAndTheVoid`；8 个演示（`m10w_rift_travel`、`m10w_rift_gap`、`m10w_exit_slide`、`m10w_rift_repeat`、`m10w_void_portal`、`m10w_place_ramp`、`m10w_drop_long`、`m10w_pad_portal`）各带失败版，`MovementDemoTests.EveryDemoFailsWithItsFailureShift`。
- 对照数据：PR2 的 24 次出口、21 次起点时刻、13 次门距、2 次寿命（会话 `20261023_000555_M10R2_s1`、`20261023_002614_M10R2_s2`，`r2_wraith/results.json`）。
- 合格线：出口速度 = 0（精确）；旅行时长和 R5 行一致到 0.1 s 一步；门距 128 u 边界两侧结果和实测一致；放置冲刺 364 / 415 / 468 / 519 u/s 各差 < 0.05 u/s。

#### 出处

- PR2 TL;DR：旅行时长、出口速度 0、门距、寿命、站在出口不回弹、再进、相位中不传送、放置距离档。main
- WR TL;DR：举手、放置冲刺 364、最初的旅行时长；"回放速度 = 放置速度"后来被 PR2 更正（那是速度字段，不是运动）。main
- SB2：放置加速的倍率规则。main
- N8B §0、§2：隧道引擎（路径整理、0.1 s 一步、出口解除挂载）、进入条件、再进 0.5 / 1.0 s、触发区大小。main
- N8E §2 E-2、E-4、E-5、§4 用户决定。main
- M10W §3–§9：Unity 规则表、设计值清单、演示、测试、缺口。main
- D-12（做传送门）、D-19（再进 1.0 s；触发范围保留设计值）、DEC"D-19 传送重新进入间隔"留档行。main
- `research/phase2-local/m10/d_library/TECHNIQUE-LIBRARY-M10.md` §3.40（S21 规则；2025 年 3 月以后的改动不算）。main
- 脚本（本地，不在仓库）：`mp_weapon_phase_tunnel.nut`（Flowstate 拷贝，注释有 "post s15"）的 `PhaseTunnel_CleanAndFinalizePath`、`PhaseTunnel_MoveEntAlongPath`、`PhaseTunnel_PhaseEntity`、`PhaseTunnel_ShouldPhaseEnt`；`wraith_portal_max_distance` 6000。

---

### 5.44 Ash 大招：相位突破（Phase Breach）

#### 原理

Ash 瞄准一个落点，按下以后沿**直线**被送过去，到了站定（速度 0、离地 5 u，然后正常落下）。起点留下一个门，15 s 内谁碰到都会被送到同一个出口。它和 Wraith 门是同一套隧道引擎，区别只在"路径是生成的直线、只有入口有触发区（单向）"。终点要能看见，所以也不能穿墙到看不见的地方。

#### 规则和公式

1. 按大招进入瞄准；左键确认；确认 0.401 s 后开始旅行。
2. 目标：从眼睛沿视线找地面点；水平距离 200 u ≤ d ≤ 2953 u（75 m；升级 100 m 没做）；视线和水平夹角在 45° 内才能用满距离（视线射程 = 2953 / cos(clamp(俯仰, ±45°))）；终点要过出口检查（站得下）。
3. 出口 = 瞄准地面水平距离的 **0.918 倍**、地面上方 **5 u**。（推断：等于眼睛 60 u 高的视线在地面上方 5 u 处的点，(60 − 5) / 60 = 0.917。）
4. 路径 = 起点到出口的直线，每 16 u 一个点，点上**不带速度**。
5. 旅行步数 frames = **round**(clamp(L / 1200, 0.3, 1.8) / 0.1)；身体冻结 0.152 + 0.1017 × frames 秒（实测拟合，rms 0.025 s）；移动只用 frames × 0.1 s，剩下的时间停在出口。
6. **出口速度 0**（31 / 31，含 11 次再进），出口后正常下落（11 条命令后落地，vz −62.5 u/s）；出口那条命令起输入就有效（没加输入测过，只看到移动记录恢复）。武器 0.4 s 后还回来 [数据]。
7. 入口门 15 s；再碰到 → 同一条路、同一个出口，不扣充能。HSD 离开出口 1.0 s 后才能再进（D-19 E-3，脚本同一引擎 [数据]，没实测）。
8. 单向：只有入口有触发区。
9. 相位中不能发动 [数据]；Unity **没有**这条检查（现在没有一个预设同时有虚空和突破）。
10. Fun 配置 [设计]：冻结减半（0.08 + 0.05 × frames），出口保留进门水平速度的 0.5 倍 + 沿路径 150 u/s。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 确认 → 旅行 `windup` | — | 0.401 s | — | n 19；按住版 0.450 s | [实测] |
| 最远 `maxDistance` | 75.0 m | 2953 u | 41.01 H | 升级 100 m | [数据] |
| 最近 `minDistance` | 5.08 m | 200 u | 2.778 H | — | [数据] |
| 满距离夹角 `maxAngleForFullDist` | — | 45° | — | — | [数据] |
| 出口比例 `exitFraction` | — | 0.918（×） | — | 0.917–0.919 | [实测] |
| 出口离地 `exitHeight` | 0.127 m | 5 u | 0.069 H | 5.00 | [实测] |
| 旅行速度 `travelSpeed` | 30.48 m/s | 1200 u/s | 16.67 H/s | — | [数据] |
| 旅行最短 / 最长 | — | 0.3 s / 1.8 s | — | 升级 1.4 s | [数据] |
| 冻结 `lockBase` + `lockPerFrame` × frames | — | 0.152 s + 0.1017 s × frames | — | 551 / 1103 / 1833 u → 0.653 / 1.076 / 1.672 s | [实测] 拟合 |
| 门寿命 `portalLifetime` | — | 15 s | — | — | [数据] |
| 再进 `reentryDebounce` | — | 1.0 s（脚本）；HSD 1.0 s | — | 没测过 | [数据] |
| 举手 `raiseTime`（HSD） | — | HSD 设计值 0.8 s | — | 不在 R5 报告里 | [设计] |
| 触发半径 / 高（HSD） | 0.813 / 1.829 m | HSD 设计值 32 / 72 u | 0.444 / 1 H | R5 16 / 32 u | [设计] |

#### 实现模板

```
// 单位：u、s
Targeting → confirm → (0.401 s) → Travel → Idle（入口门 15 s）
target:   aim = 视线和地面的交点（距离、夹角、出口检查）
          exit = start + (aim - start)_xy * 0.918;  exit.z = ground + 5
Travel:   frames = round(clamp(L/1200, 0.3, 1.8) / 0.1)
          lock   = 0.152 + 0.1017*frames
          0 … frames*0.1: 运动学沿直线（无碰撞、锁输入、结束别的 Driver）
          … lock: 停在出口
          结束: vel = 0（Fun: 0.5*v_h_entry + 150*dir_xy）, 正常下落
入口门:   碰到 且 now >= lastExit + 1.0 → 同一路径再走一次（不扣充能）
```

Unity 参考实现：`U:…/Abilities/PhaseBreach/PhaseBreachAbility.cs`，`PhaseBreachParams`（`R5Reference()` / `Fun()`，全部 [u]）、`PhaseBreachAbility.PathFrames`（Squirrel 的 round）/ `LockDuration` / `BeforeMoveLate`（`CommandModifiers.kinematic` + `phased`）。预设 Ash route（键 `4`，Z 瞄准、左键确认，冷却 15 s [设计]）。训练场 `PracticeMapM6B.cs`（Q）。

#### 验收

- `PhaseBreachTests.LockTimeExitDistanceAndRestMatchTheMeasurement`（600 / 1200 / 2000 u 三行：出口距离、冻结时间、步数、出口静止）。
- `PhaseBreachTests.TravelIsFrozenStraightAndIgnoresInput`、`PhaseBreachTests.EntryPortalSendsAlongTheSamePathFor15SecondsWithoutACharge`、`PhaseBreachTests.InvalidTargetsRefuseTheConfirmWithoutACharge`、`PhaseBreachTests.PhasedTravelPassesThroughALedgeFaceAndEndsFree`、`PhaseBreachTests.OutOfRangeAndOutsideTheConeAreRefused`、`PhaseBreachTests.AHitDuringAimOrWindupCancelsWithoutACharge_TravelCannotBeInterrupted`、`PhaseBreachTests.FunBreachIsShorterAndKeepsMomentum_ReferenceExitsAtRest`。
- `N8ETeleportTests.TheBreachPortalTakesTheBodyAgainOnlyOneSecondAfterAnExit`（只检查参数值）。
- 游戏侧：`M6BGameTests.TheBreachGapIsCrossableOnlyByBreachOrJets`；演示 `m6b_breach_gap_slide`、`m6b_breach_portal_reuse`、`m6b_breach_zipline`。
- 对照数据：M6B §3 表（20 次突破 + 11 次再进，会话 `M6B_ash2`、`M6B_ash3`、`pilot_ash`；`m6/b_legends/results.json`）。合格线：出口速度 0（精确）；冻结和拟合差 ≤ 0.05 s（20 Hz 服务器 tick 的散布）；出口距离比例 0.918 ± 0.002。

#### 出处

- M6B §3：实测表、冻结拟合、出口点、再进、脚本常量（带行号）。main
- N8B §0、§3：隧道引擎、瞄准规则、单向、相位中不能发动。main
- N8E §1、§2 E-3、§4。main
- D-07（只做 Valkyrie 喷气和 Ash 突破）、D-19（E-3）。main
- 脚本（本地）：`mp_weapon_phase_breach.nut`（速度 1200、0.3 / 1.8 s、75 m、45°、200 u、15 s）、`mp_weapon_phase_tunnel.nut`（`numPathFrames = round(pathTime / 0.1)`）。

---

### 5.45 瞬间传送：旧原语 `Teleport`，以及没做的 Loba / Alter

#### 原理

瞬间传送是"换个位置，速度按规则处理"。Apex 里两种处理都有：Loba 清零、Alter 给一个按进门速度截断的小速度。HSD 的 M5 做过一个通用的传送原语（两种出口），现在只剩旧预设和测试在用；真正的 S21 Wraith / Ash 在 5.43、5.44。

#### 规则和公式

**Unity 旧原语 `TeleportAbility`（全部 [设计]，只有"清零"一条有实测支撑）**

1. 按下 → `delay` 后把身体放到"按下时的平视方向 × `distance`"处（游戏里可以用几何求可达点）；滑铲结束。
2. `ZeroVelocity`（id `teleport`，Loba 模式）：速度清零，不锁操作。没有预设用它。
3. `FixedExit`（id `portal`）：沿平视方向给 `exitSpeed`（替换速度的发射），之后锁操作 `lockDuration`。只有 Revenant-Wraith ground 预设（键 `3`，Z）用它。**不是 S21**：S21 的 Wraith 门出口是 0（D-19 E-6，标成设计值）。

**Loba 手环（搁置，SHELF）**：按键约 1.21 s 后扔出；扔出 0.30 s 后再按可以提前落地，之后约 0.6 s 传送（其中 0.4 s 是脚本延迟）；**传送后速度为 0**（M6 15 / 15、M4 6 / 6），没有锁操作。抛射速度 1815 u/s（俯仰超过 50° 时 1390 u/s）[数据]。

**Alter 虚空通道（搁置，本地放不出来，只有脚本）**：两端都能进，瞬间传送；出口速度 = 出口方向 × clamp(进门速度在门方向上的分量, 50, 300)；穿墙 / 天花板 / 地板，墙厚 ≤ 30 m；扔出 0.7 s 后开门，门 15 s；同一人 1.35 s 防抖；传送后 1.0 s 相位（不加速）。

**Alter 大招 Void Nexus（没做）**：单向回到 Nexus，旅行 clamp(L / 1800, 0.8, 10) s，出口预测 0；本地单人测不了旅行（要第二个玩家）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 旧原语延迟 `delay` | — | HSD 设计值 0.25 s | — | — | [设计] |
| 旧原语距离 `distance` | 10.16 m | HSD 设计值 400 u | 5.556 H | — | [设计] |
| 旧 `portal` 出口速度 `exitSpeed` | 7.62 m/s | HSD 设计值 300 u/s | 4.167 H/s | S21 Wraith 门是 0 | [设计] |
| 旧 `portal` 锁操作 `lockDuration` | — | HSD 设计值 0.3 s | — | — | [设计] |
| Loba 传送后速度 | 0–0.140 m/s | 0–5.5 u/s | 0–0.076 H/s | 有一条命令的加速 | [实测] |
| Alter 出口速度下限 / 上限 | 1.27 / 7.62 m/s | 50 / 300 u/s | 0.694 / 4.167 H/s | 没测过 | [数据] |
| Alter 墙厚上限 `wallThicknessMax` | 30 m | 1181 u | 16.40 H | — | [数据] |
| Alter 再进防抖 | — | 1.35 s | — | — | [数据] |
| Alter Nexus 旅行速度 | 45.72 m/s | 1800 u/s | 25.0 H/s | 0.8–10 s | [数据] |

#### 实现模板

```
// 单位：u、s（旧原语）
press: dir = flatForward(yaw); dest = resolve(pos, pos + dir*400); due = now + 0.25
at due: pos = dest; teleported = true; endSlide
        ZeroVelocity: vel = 0
        FixedExit:    launch(dir*300)（替换速度）; lockControls 0.3 s
```

Unity 参考实现：`U:…/Abilities/Teleport/TeleportAbility.cs`，`TeleportExit`、`TeleportParams.Loba()` / `Portal()`、`TeleportAbility.BeforeMove`；`destinationResolver` 由游戏侧给。Alter / Loba 在 Unity 里没有（SHELF；D-07）。

#### 验收

- `SkillComboTests.PortalExitLocksControlsRefusesOtherSlotsAndCancelsPendingStates`：旧 `portal` 30 条命令（0.25 s）后到 400 u、出口 300 u/s、锁住期间输入和别的槽位被拒、0.3 s 后解锁；同一测试里 Loba 模式撞墙被截、出口清零。
- `N8ETeleportTests.TheOldPortalPrimitiveIsLabelledAsADesignValue`：说明文字带"design - not S21"。
- `VoidM10WTests.TheWraithPresetHasTheS21VoidAndRiftAndTheOldPresetIsUnchanged`：旧预设没被改。
- 对照数据：P3 Loba 6 次传送后 0.0–5.5 u/s；M6B §2（Loba 25 次）。合格线：清零模式出口 |v| = 0；旧 `portal` 不参加 R5 对照（设计值）。

#### 出处

- P3 "Loba"、"Design reading"：Apex 的传送都不带速度。main
- SHELF：Loba、Alter 的实测 / 源码要点、数据位置、重启条件。main
- M6B §1、§2：Alter 放置失败诊断、Loba 时序。main
- N8B §4、§5；N8D §2、§3：Alter 战术 / 大招规则和为什么测不了。main
- N8E §2 E-6、§3。main
- D-07、D-19（E-6）、D-39。main

---

### 5.46 传送对照表，以及出门以后

#### 原理

把五个传送放在一起看，差别只在三个开关上：路径从哪来（决定能不能穿墙）、几个触发区（决定单向 / 双向）、出口速度怎么处理（全部清零，只有 Alter 例外）。做新的传送技能时，先选这三个开关，再填数。

#### 规则和公式

| | Wraith 战术 | Wraith 大招 | Ash 大招 | Alter 战术 | Alter 大招 | Loba |
|---|---|---|---|---|---|---|
| 移动方式 | 自己跑（只开相位） | 隧道，回放自己跑的路 | 隧道，直线 | 瞬间 | 隧道，抬高路径 | 瞬间 |
| 速度 / 时间 | +0.3 严重度 | 1024 u/s，0.3–2.0（3.5）s | 1200 u/s，0.3–1.8 s | — | 1800 u/s，0.8–10 s | — |
| 出口速度 | 自己的 | **0** [实测] | **0** [实测] | clamp(v·n, 50, 300) [数据] | 0 [数据] | **0** [实测] |
| 方向 | — | 双向 | 单向 | 双向 | 单向 | — |
| 再进 | — | 离开 1.0 s 后 | 离开 1.0 s 后 | 1.35 s | 追随门 2 s | — |
| 寿命 | 相位 4 s | 45 s | 15 s | 15 s | Nexus 永久 | — |
| 穿墙 | 否 | 否 | 否（终点要能看见） | **是**（≤ 30 m） | 越过 | 否 |
| HSD 有没有 | 有（S21） | 有（S21） | 有 | 搁置 | 没有 | 搁置（旧原语清零模式） |

**出门以后**：出口静止、输入马上有效，接着就是普通的地面 / 空中规则（第 03、04 章）。实测和测试过的接法：出门冲刺 0.9 s（约 287 u/s）按蹲滑铲到 457 u/s（演示 `m10w_exit_slide`）；出门起跳 + tap strafe（`RiftM10WTests.FromTheRestingExitAJumpAndATapStrafeStillWork`）；跳板飞进门 → 出门静止（`m10w_pad_portal`）。

**M10-W 时发现、M10-D4 修掉的缺陷（"反向输入不减速"）**：在地上往前跑，然后鼠标不动按住 S（或者一条命令里转 180° 按住 W），身体会一直以 199.5 u/s 往前走。原因是 M5 的地面转向规则 `GroundVectorRedirect` 只衰减速度里"和想走方向垂直"的部分，正好反向时垂直部分是 0，所以什么都不衰减。修法（一行）：

- 沿想走方向 ŵ 的分量取 along = max(0, v·ŵ)；v 里剩下的部分（垂直分量，加上反向时的反向分量）按减速度 D 衰减（站 1250 u/s²，蹲 1500 u/s²）；沿 ŵ 的加速和超速限制不变。
- v·ŵ ≥ 0 时和修前逐位相同；90° 和 180° 两侧连续，没有特判。
- 结果：从 299 冲刺反向约 0.19 s 停下，从走路约 0.11 s；课程单圈 80.55 → 78.98 s（自动驾驶在 M 塔顶冲过头要往回走，修前 1.1 s 才转过来，修后 0.225 s）。
- R5 没有录过跑动中反向，这条刹车规律是 M5 摩擦向量模型的延伸，**[推断]，没实测**（D4 §7 建议的 R5 补测还没做）。
- **现在的状态**：N7（10-24，D-17）以后，Reference（Fun 继承）有输入的地面命令先走原生 WalkMove（`groundNativeFriction`），它优先于 `groundVectorRedirect`（`U:…/R5MotorV2.cs` 第 605–611 行）。按代码读，D4 修过的这条函数在两个配置里都不再执行；反向刹车现在由原生 Friction + Accelerate 负责（第 03 章）。没为这一条单独跑测试确认，D4 的 16 个测试仍在跑、用的是现在的配置。

#### 实现模板

无单独的实现：各技能见 5.42–5.45。反向刹车的规则和实现归第 03 章（地面移动）；这里只留修复记录。

#### 验收

- 出门以后：`RiftM10WTests.TheExitIsAtRestWhateverTheEntrySpeedInBothDirections`、`RiftM10WTests.FromTheRestingExitAJumpAndATapStrafeStillWork`；演示 `m10w_exit_slide`、`m10w_pad_portal`。
- 反向刹车（`Game/Tests/Editor/M10D4GameTests.cs`，16 个用例，修前全部失败）：`M10D4GameTests.HoldingBackAfterRunningReverses`、`M10D4GameTests.OneCommand180TurnReverses`、`M10D4GameTests.SnapTurnIsContinuousAt180`、`M10D4GameTests.EveryWideTurnEndsAlongTheWish`、`M10D4GameTests.PracticeSprintThenHoldBackRunsBackward`；同向逐位不变：`ReferenceModelTests.AlignedGroundMotionIsTheM2RuleBitForBit`。
- 合格线（D4 §4）：前向分量 > 0 时每条命令至少减 D·dt；0.5 s 内到 0；最后到 −上限，没有横向漂移；179–181° 的各个转角之间差 ≤ 600·sin|Δ|。

#### 出处

- N8B §6：五个技能对照表。main
- N8A §3、§4：为什么有的能穿墙、有的能反复进。main
- P3 "Design reading"。main
- M10W §5（出门接滑铲、跳板进门）、§8 第 7 条（发现反向缺陷）。main
- D4 §1–§7：缺陷、根因、一行修法、测试、单圈变化、没实测的部分。main
- `research/phase2-local/m10/M10-REPORT.md`（M10-D4 行，单圈 80.55 → 78.98 s）；DEC"2026-10-23：M10 完成"。main
- D-17（N7 改原生）、D-49（"原生的转向就是 `groundNativeFriction`"）。main

---


技能的冷却、充能、按键、UI 不写（第 10 章）。每条只写移动规则和数。

---

## 第七部分 · 其他技能带来的移动（§5.47 – §5.54）

每项写得比较短。兴奋剂（Octane）只改移动倍率，不是外力，写在 §5.36。

### 5.47 Horizon 战术：重力升梯（Gravity Lift）

#### 原理

一根竖直的"气柱"：走进去就被稳定地抬上去（替代重力，不是加速度），到顶附近悬停一下，然后被弹出去。上升中可以小范围横向操控，不按键时被拉回中轴。弹出是固定大小、替换速度的一推，方向朝视线（在边缘离开时朝外）。

#### 规则和公式

1. 进入：身体离轴水平距离 < 70 + 16 u，且 −72 ≤ z − 底 ≤ 1200 u（命令开始时，按碰撞体重叠）。
2. 上升：vz = clamp(vz + 10⁵·dt, 5, 300)（实际就是设成 300）；这条命令重力为 0；到 0.9 × 1200 u 以上，vz 从 0.5 线性降到 −0.5（悬停带）。
3. 横向：有输入 v_h = 基础 + 想走方向 × 2000·dt，|v_h| ≤ max(|基础|, 170)（进入那条命令基础 = 0）；没输入 v_h 设成朝轴的速度，按离轴距离从 25（20 u 内）到 50 u/s（70 u）。之后照常做传奇的空中加速。
4. 弹出：悬停（vz < 5 的命令）超过 0.5 s，或离开范围 → v = 方向 × 400·s + 竖直 450·s，s = clamp((停留 − 0.0206) / 0.5, 0, 1)；方向 = 平视方向，离轴 > 40 u 时朝外（径向）。替换速度。
5. 弹出后 2.0 s 内不能再进；弹出**不开 lurch 窗口**（Reference；Fun 保留 M5 设计"开"）；升梯里按跳无效（S21 没有跳出加成）。
6. 相位中升梯什么都不做（5.40，D-21）。
7. 升梯存在 10 s。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 上升速度 `upSpeed` | 7.62 m/s | 300 u/s | 4.167 H/s | — | [数据] [实测] |
| 进入半径 `radius` + `hullRadius` | 2.184 m | 70 + 16 = 86 u | 1.194 H | 实测 84.8–86.5 | [数据] [实测] |
| 高度 `height` | 30.48 m | 1200 u | 16.67 H | — | [数据] |
| 悬停起点 `hoverFrac` / 最长悬停 `maxHover` | — | 0.9（×）/ 0.5 s | — | 实测 0.5002 s，sd 0.0003 | [数据] [实测] |
| 横向操控 `steerSpeed` / `steerAccel` | 4.318 m/s / 50.8 m/s² | 170 u/s / 2000 u/s² | 2.361 H/s / 27.78 H/s² | — | [数据] [实测] |
| 回中速度 `toCenterSpeed`（内圈 20 u 时 ×0.5） | 1.27 m/s | 50 u/s | 0.694 H/s | — | [数据] |
| 弹出竖直 `ejectUp` / 水平 `ejectHorizontal` | 11.43 / 10.16 m/s | 450 / 400 u/s | 6.25 / 5.556 H/s | 实测 450.000 / 400.01 | [数据] [实测] |
| 短停留偏移 `ejectScaleOffset` | — | 0.0206 s | — | 实测 0.016–0.030 s，n 10 | [实测] 拟合 |
| 径向弹出门槛 `travelThreshold` | 1.016 m | 40 u | 0.556 H | — | [数据] |
| 再进 `reentryBlock` | — | 2.0 s | — | 实测 2.02–2.19 s 时被再抬（没试 < 2 s） | [反编译] [实测] |
| 寿命 `lifetime` | — | 10 s | — | — | [数据] |

Unity：`U:…/Abilities/GravityLift/GravityLiftAbility.cs`，`GravityLiftParams`（`R5Reference()`；`ejectScaleOffset`、`ejectOpensLurchWindow`、`phasedNoLift` 由 `MovementConfig.CreateBody` 写入）、`GravityLiftAbility`。预设 Valk-Horizon aerial（`2`）。和 HSD 不一样的：`lifetime` 只在没人乘坐时移除升梯，不会把乘客弹出（README 已知差异）。

#### 验收

- `GravityLiftTests.VerticalAndCentringGraphs`、`GravityLiftTests.WalkInRideHoverAndTopEject`、`GravityLiftTests.HoverTimeoutEjectVelocityAndReentryBlock`、`GravityLiftTests.SideExitEjectsRadiallyAndShortDwellScales`（M4 回放）。
- `LiftM8CTests.TopHoverEjectsAfterHalfASecondAlongTheViewAndJumpDoesNothing`、`LiftM8CTests.SideExitsAtAnyHeightGetTheFullEjectRadiallyOutward`、`LiftM8CTests.AShortDwellScalesTheEjectByTheFittedOffset`、`LiftM8CTests.TheEjectOpensNoLurchWindowInReferenceAndTheM5OneInFun`、`LiftM8CTests.ReentryIsBlockedForTwoSecondsAfterTheEject`；`N9LiftPhaseTests.TheReentryBlockIsTwoSeconds`。
- 对照数据：M4 25 次单升梯、M8 49 + 25 次（LIFT8）；M4 回放 trial `M4_m4_lift_ride_*` 等。合格线：弹出 450 / 400 u/s 差 < 0.05；悬停 0.500 ± 1 条命令。

#### 出处

- LG §1：算法、常量、实测。main
- LIFT8 TL;DR：悬停 0.5002 s、侧出径向、短停留缩放、再进 2.02–2.19 s、无跳出加成。main
- N9 §2、§7：原生常量和 SDK 相同；L-1、L-2。main
- `research/phase2-local/m8/unity/M8C-UNITY.md` §3。main
- params.tsv F-04 – F-07。
- D-21。main
- [反编译] 升梯处理 0x140a39420（常量 2.0）。

### 5.48 Horizon 被动：太空漫步（空中参数）

#### 原理

Horizon 在空中更好控制、落地不减速。它不是一个动作，只是把每条命令的空中参数换成 Horizon 自己的值。

#### 规则和公式

空中期望速度上限 `airSpeed` 80 u/s（× msc 1.15 = 92 u/s，普通传奇 69 u/s）、空中加速 `airAcceleration` 800 u/s²（普通 500）、落地减速时长 `landSlowdownDuration` 0（关闭落地减速；普通 1 s）。重力、跳跃不变。实测：升梯弹出后反向空中控制约 0.6 s 把 400 u/s 掉头到 −93.7 u/s；同样 |vz| 1347 u/s 的落地，Horizon 不减速，Gibraltar 当场停住。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 空中期望速度 `airSpeed`（Horizon / 普通） | 2.032 / 1.524 m/s | 80 / 60 u/s | 1.111 / 0.833 H/s | — | [数据] [实测] |
| 空中加速 `airAcceleration`（Horizon / 普通） | 20.32 / 12.70 m/s² | 800 / 500 u/s² | 11.11 / 6.944 H/s² | 实测 799.5–800.5 | [数据] [实测] |
| 落地减速时长 `landSlowdownDuration`（Horizon / 普通） | — | 0 / 1 s | — | — | [数据] [实测] |

Unity：`U:…/Abilities/AirProfile/PassiveAirProfile.cs`，`LegendAirProfile.Horizon()` / `Default()`、`PassiveAirProfile`（id `horizon_air`，常驻）。

#### 验收

`LandingSlowdownTests.HorizonAirProfileRaisesTheWishCap`；`LiftM8CTests.HorizonAirControlAfterTheEjectReversesItInAboutSixTenths`、`LiftM8CTests.SpacewalkLandingsKeepTheSpeedNormalLegendsStopDead`；演示 `m8c_horizon_soft_land`。合格线：空中加速 800 ± 0.5 u/s² 每命令。

#### 出处

- LG §3（census 类变量）；LIFT8 TL;DR 最后两行。main
- params.tsv J-09、J-10 的备注列（"Horizon 80 / 800"）。

### 5.49 Valkyrie 被动：VTOL 喷气（Jets）

#### 原理

空中按住跳持续往上推，推力有一个"终端速度"（不会无限变快），起喷那 0.5 s 推力更大（起步有劲）。松开后有一段"后效"：重力变小、水平有阻力，像降落伞。燃料有限，每次起喷先扣一格，落地一段时间后才回充——所以短促点按比一直按住"贵"（实测连续按住每格燃料约 270 u 高，点按约 122 u）。

#### 规则和公式

每条喷气命令，在普通空中移动**之后**（R5 / SDK `Jetpack_Apply`）：

1. 推力 thrust = T + (H − T)·|wish|（T 1.9、H 1.7，单位 × g），乘起喷系数 s(t)：0.5 s 内从 1.8 线性降到 1。
2. 竖直：vz = (vz + g·thrust·dt) · 2^(−dt/0.27)；如果进来的 vz 已经超过这个推力的终端速度（余量 0.01），改成 vz = vz_in · 2^(−dt/0.4) + g·dt。终端 Term(a, τ) = a·dt / (1 − 2^(−dt/τ))。
3. 水平（按视角前后、左右两轴）：每轴 2^(−dt/τ) 衰减（前后 0.14 s、左右 0.11 s、超过限制时 0.4 s），再加 wish × 1035 × H × s × taper(v·wish)，taper 在 300 → 600 u/s 之间从 1 线性降到 0。
4. 停喷（松开、落地、燃料用完）：如果 vz ≤ 终端，vz × 0.4，并开始后效；**vz 高于终端时停喷，既不砍也没有后效**（M6-B 新发现）。
5. 后效：重力 × 0.45，水平阻力 dv/dt = −1.25 × 10⁻⁴ · v_h²（单位 1/u），最长 3.0 s，或离地 50 u 以内结束。
6. 燃料 8，喷气中每秒 −1，每次起喷 −1；停喷后 0.25 s 才能再起喷，距上次按跳 > 0.1 s；落地 4.43 s 后以 0.7494 /s 回充（从落地还是从停喷算分不清，HSD 选落地 [设计]）。
7. 钩爪挂上即停喷。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 推力 `thrust` / 有输入 `moveThrust` | — | 1.9 / 1.7（× g） | — | 拟合 1.89983 / 1.69992 | [数据] [实测] |
| 竖直紧度（半衰期）`tightUp` / 超限 `tightAboveLimit` | — | 0.27 s / 0.4 s | — | — | [数据] [反编译] |
| 前后 / 左右 / 向下紧度 `tightForwardBack` / `tightSide` / `tightDown` | — | 0.14 / 0.11 / 0.1 s | — | — | [数据]（census） |
| 起喷系数 `rampScale` / 时长 `rampTime` | — | 1.8（×）/ 0.5 s | — | — | [数据] |
| 终端爬升（无输入 / 按 W） | 6.607 / 5.131 m/s | 260.13 / 202 u/s | 3.613 / 2.806 H/s | — | [算] [实测] |
| 停喷判断的终端（120 Hz，含本命令） | 6.750 m/s | 265.75 u/s | 3.691 H/s | 随 dt 变 | [算] |
| 水平推力 `strafe` | 26.29 m/s² | 1035 u/s² | 14.38 H/s² | 拟合 1035.10 | [数据] [实测] |
| 水平削减区间 `taperStart` / `taperFinish` | 7.62 / 15.24 m/s | 300 / 600 u/s | 4.167 / 8.333 H/s | — | [数据] |
| 水平终端（按 W） | 8.534 m/s | 336 u/s | 4.667 H/s | — | [算] [实测] |
| 停喷 vz 系数 `vzScaleOnStop` | — | 0.4（×） | — | 实测 0.40000 | [数据] [实测] |
| 后效重力 `postGravityScale` / 时长 `postMaxTime` | — | 0.45（×）/ 3.0 s | — | 实测 2.96–2.99 s | [数据] [实测] |
| 后效阻力 `postDragQuad` | 4.921 × 10⁻³ /m | 1.25 × 10⁻⁴ /u | — | — | [数据] |
| 后效结束离地 `postProbe` | 1.27 m | 50 u | 0.694 H | — | [数据] |
| 燃料 `fuelMax` / 消耗 `fuelDrainPerSecond` / 起喷 `activationCost` | — | 8 / 1 /s / 1 | — | 实测 1.0002 /s、1.000 | [数据] [实测] |
| 回充 `rechargeRate` / 延迟 `rechargeDelay` | — | 0.7494 /s / 4.43 s | — | 起点（落地 / 停喷）分不清 | [实测] |
| 再起喷 `reactivateDelay` | — | 0.25 s | — | — | [数据] [反编译] |
| 按住 10 s 的最高点（7 s 喷气） | 47.98 m | 1889 u | 26.24 H | — | [实测] |

Unity：`U:…/Abilities/Jetpack/JetpackAbility.cs`，`JetpackParams`、`JetpackAbility`（id `jets`，`IJumpClaimant`）、`JetsRechargeClock`。**命名陷阱**：`JetpackParams.R5Reference()` 是 **M4 模型**（M4 回放用：没有起喷消耗、不回充、每次停喷都有后效）；Reference 配置和所有游戏预设用的是 `JetpackParams.Measured()`（M6-B 实测）；`Fun()` 是 [设计]（推力 2.0 / 1.8、起喷 0.5、回充 1.0 /s 延迟 2.0 s）。

#### 验收

- `JetpackTests.TerminalSpeeds`、`JetpackTests.HoldClimbsReleaseCutsPostEffectSlowFall`、`JetpackTests.ForwardThrustTerminalAndPostEffectDrag`、`JetpackTests.FuelRunsOutAndReactivationGates`（M4 模型）。
- `JetsMeasuredTests.ContinuousHoldEmptiesTheMeterAt7SecondsThenStopsLikeARelease`、`JetsMeasuredTests.EveryActivationCostsOneMeter_PulsesMatchTheMeasuredMeter`、`JetsMeasuredTests.ReactivationNeedsQuarterSecondAndMoreThanTheCost`、`JetsMeasuredTests.RechargeStartsAfterTheLandingDelayAt0749PerSecond`、`JetsMeasuredTests.ReleaseAtOrBelowTerminalCutsAndStartsThe3SecondPostEffect_AboveTerminalDoesNeither`、`JetsMeasuredTests.SidewaysDecaysAt011AndForwardAt014_DownAt010`、`JetsMeasuredTests.TerminalAndFlightModelUnchanged`、`JetsMeasuredTests.M4PresetKeepsEveryNewRuleOff`。
- 对照数据：VR §2.3 拟合（2400 条命令，vz 残差 rms 0.0036 u/s）；M6B §4（25 次起喷）。合格线：一步残差 rms ≤ 0.05 u/s；燃料 7.000 s 用完。

#### 出处

- VR §2.3–§2.6：飞行模型、常量拟合、停喷、后效。main
- M6B §4：燃料、回充、3 s 后效、超终端停喷。main
- N9 §3：原生常量和 SDK 相同。main
- `research/phase2-local/m6/unity/M6B-UNITY.md`。main
- D-07。main
- [反编译] `Jetpack_Thrust` 0x140aff150、`Jetpack_Vertical` 0x140afee50。

### 5.50 Revenant 战术：暗影突袭（Shadow Pounce）

#### 原理

按住蓄力，松开往视线方向"扑"出去：速度直接被**替换**成扑出的速度（原来跑多快不重要），然后就是普通抛物线。默认往上抬 35°，看得越往上抬得越少、速度越小；贴地往下看时自动改成往前上方扑。扑出后一小段时间不能爬墙。

#### 规则和公式

1. 按下后 0.9 s 拔出，再蓄 1.3 s 满：c = clamp((松开 − 按下 − 0.9) / 1.3, 0, 1)；早于 0.9 s 松开就在 0.9 s 时发射，晚的在松开后下一条命令发射。
2. 俯仰 p（向下为正）：p ≥ 20° 且沿视线 200 u 内有地面 → p = 15°；p ≤ 75°。
3. p ≥ −15°：发射角 = p − 35°，除数 1；p < −15°：抬角从 35° 到 0°、除数从 1 到 1.5，在 −15° → −80° 之间线性。
4. 速度 v = (700 + 450·c) / 除数 · 方向(发射角, yaw)，**替换**原速度。
5. 之后普通弹道，无落地减速（落地后 0.083 s 恢复手持倍率）；发射**不开 lurch 窗口**（Reference），但飞行中按键照样 lurch，上限 182 u/s（= 0.7 × 260 × 1.0，拿投掷武器时 msc 1.0）。
6. 蓄力中和发射后 0.85 s 不能攀爬 / 抓边 / 跑墙（脚本 0.75 s + 一个 10 Hz 服务器 tick；Fun 0.75 s）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 拔出 `pullout` / 蓄满 `chargeTime` | — | 0.9 s / 1.3 s | — | 实测 0.916–0.922 s 发射 | [数据] [实测] |
| 最小 / 最大速度 `vMin` / `vMax` | 17.78 / 29.21 m/s | 700 / 1150 u/s | 9.722 / 15.97 H/s | 全网格误差 ≤ 1.6 u/s | [数据] [实测] |
| 抬角 `pitchRaise` | — | 35° | — | 误差 0.005° | [数据] [实测] |
| 向上门槛 / 竖直极限 / 最大除数 | — | −15° / −80° / 1.5（×） | — | −30° 实测 627.6 / 1031.0 u/s @ 56.92° | [数据] [实测] |
| 向下替换：门槛 / 替换成 / 地面距离 | 5.08 m（距离） | 20° / 15° / 200 u | 2.778 H | 实测 25 / 45 / 70° 都给 20.000° 向上 | [数据] [实测] |
| 禁爬锁 `wallRunLock`（Reference / Fun） | — | 0.85 s / 0.75 s | — | 实测攀爬在发射后 0.84–0.89 s 开始 | [实测] / [设计] |
| 落地恢复手持倍率 | — | 0.083 s | — | 实测 0.05–0.12 s | [实测] |
| 飞行中 lurch 上限 | 4.623 m/s | 182 u/s | 2.528 H/s | — | [实测] |
| Revenant 水平上限（HSD） | 24.38 m/s | HSD 设计值 960 u/s | 13.33 H/s | 满蓄水平 942 u/s | [设计] |

另有一个实测、**Unity 没做**的情况：在台沿外往下看（地面检查打空）时向下发射，竖直分量被台面吃掉（REV9）。

Unity：`U:…/Abilities/Pounce/PounceAbility.cs`（`PounceParams`、`PounceAbility`，`IWallRunBlocker`）；公式 `U:…/Abilities/_Core/InstantImpulse.cs`（`InstantImpulse.PounceCharge`、`PounceLaunch`）；Revenant 预设的三项（锁、lurch、落地保持）由 `RevenantParams` 写入（`U:…/Abilities/Revenant/RevenantProfile.cs`）。

#### 验收

`PounceM9BTests.TheLaunchFormulaIsTheSourceRule`、`PounceM9BTests.ChargeAndLaunchTimingThroughTheBody`、`PounceM9BTests.TheLaunchReplacesTheVelocityWhateverTheStartSpeed`、`PounceM9BTests.LookingDownNearTheGroundReplacesThePitchAndHighAnglesFade`、`PounceM9BTests.TheFlightIsBallisticAndTheLandingSoft`、`PounceM9BTests.APounceIsNotAJumpInReferenceTheFunConfigLurches`、`PounceM9BTests.AWallReachedInsideTheLockClimbsOnlyAfterIt`、`PounceM9BTests.TheM4PounceIsUnchanged`；`RevenantFollowUpM9CTests.PounceLurchAndLandingMatchR5`；`PounceTests.LaunchDirectionAndCharge`（M4）。对照数据：REV9 215 次发射网格。合格线：速度误差 ≤ 2 u/s，发射角 ≤ 0.01°。

#### 出处

- REV9 TL;DR：全网格、向上 / 向下规则、替换速度、无 lurch 窗口、182 u/s、禁爬锁。main
- VR §3：时序和发射速度（M4，只测了俯仰 0）。main
- `research/phase2-local/m9/unity/M9B-UNITY.md` §2。main

### 5.51 Revenant 被动：长攀爬

#### 原理

Revenant 爬墙不是"爬一下就掉"，而是按住 W 能一直往上爬，越高越慢，爬到约 1250 u 高时自己跳一下结束。松开 W 很快脱离，按 S 立刻往后离开。它是通用攀爬（第 04 章）的一组参数替换，不是新动作。

#### 规则和公式

- 速度线 vz = k · (Z0 − z)，k = 0.0921 /s，Z0 = 攀爬开始的 z + 2493 u（所以起步约 229 u/s，不管从多高开始）。
- 按住 W 不会因接触时间脱离；松开 W 平均 0.125 s 后脱离下落（无悬挂）；S 立刻往后脱离（约 70 u/s）；侧键漂移约 161 u/s。
- 结束：爬到起点上方 1246.6 u 时最后往上跳一下（dvz 150.1 u/s 的规则，实测 +144.5 / +146.0）；HSD 另加 9 s 时间保护 [设计]。**结束规则只有 n = 2**，高度 / 时间 / 速度三种解释都没排除。
- 攀爬中按跳：Reference 只是松开，0.89 s 后可以再爬；Fun 用 Sparrow 的墙面弹射 [设计]。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 速度线斜率 `speedLineK` | — | 0.0921 /s | — | Gibraltar 1.735 /s | [实测] 拟合 |
| 速度线零点 `speedLineZ0`（相对起点） | 63.32 m | 2493 u | 34.63 H | 实测 2480–2548 | [实测] 拟合 |
| 结束高度 `endHeight` | 31.66 m | 1246.6 u | 17.31 H | n = 2 | [实测] [设计] |
| 松开脱离 `detachAfterRelease` | — | 0.125 s | — | 0–0.18 s，n 24 | [实测] |
| 侧向漂移 `climbSideMax` | 4.089 m/s | 161 u/s | 2.236 H/s | — | [实测] |
| 再攀爬 `releaseReattachDelay` | — | 0.89 s | — | — | [实测] |

Unity：`U:…/Abilities/Revenant/RevenantProfile.cs`，`ClimbProfile`（写到 `U:…/Abilities/Climb/ClimbAbility` 的参数副本上）、`RevenantParams.Measured()` / `Fun()`；只对 `legend == "revenant"` 的预设生效（`MovementConfig.RevenantFor`）。

#### 验收

`RevenantClimbM9BTests.TheSpeedLineIsTheMeasuredOne`、`RevenantClimbM9BTests.ALongClimbMantlesOnTopAtEveryWallHeight`、`RevenantClimbM9BTests.TheLongClimbEndsNear1250WithAJumpUp`、`RevenantClimbM9BTests.ReleasingWEndsTheClimbWithinAboutAnEighthOfASecondAndFalls`、`RevenantClimbM9BTests.EveryOlderPresetIsBitIdenticalWithAndWithoutTheRevenantSet`；`RevenantFollowUpM9CTests.SideDriftIs161WhileClimbing`、`RevenantFollowUpM9CTests.BackKeyDetachesAtOnceBackward`、`RevenantFollowUpM9CTests.TheClimbJumpOnlyEndsTheClimbAndReattaches`。对照数据：REV8（25 次干净墙面，rms 0.02 u/s）、REV9。

#### 出处

- REV8：速度线、结束高度。main
- REV9 TL;DR 攀爬几行：侧向 161、S 脱离、按跳无冲量、长攀爬结束规则没测成（止损）。main
- `research/phase2-local/m9/unity/M9B-UNITY.md` §3、§9–§10。main

### 5.52 Vantage 战术：Echo 位移（Echo Relocation）

#### 原理

先把 Echo（一个小飞行物）送到远处，再按住技能键"飞向 Echo"：起飞速度很快，路上慢慢降到巡航速度，接近目标时刹车，刹车区里可以按跳做一次末端跳。只做 S21：起飞要 Echo 在屏幕里、视线不被挡。

#### 规则和公式

1. 点按（≤ 0.3 s，[设计]）：Echo 沿视线飞到第一个碰撞点或 1968.5 u（50 m），停在地面上方至少 246 u；飞行 1200 u/s，315 u 内减速。
2. 按住：按下后 1.82 s 起飞（固定预备，不是蓄力；Echo 在肩上时 1.662 s，一次完成"送出 + 起飞"）；起飞前 0.204 s 检查门槛：Echo 在视线 60° 内、眼睛到 Echo 的射线不被挡（两次 ±0.5 m 偏移重试）；**没有距离门槛**。
3. 起飞：943.1 u/s，保持 0.2 s；仰角 = 目标仰角 + 21°；然后按 (1 − t/T)² 降到 787 u/s，T = 0.001 s/u × 起始距离。目标 = Echo 原点下方 1.75 m，会追随移动的 Echo。
4. 离目标 180 u 内以 1047.6 u/s² 刹车（重力照常弯曲路径），速度降到 78.74 u/s 结束；撞墙在墙面停下；超时 round(2·d / 787, 0.1) s。
5. 中途按蹲：速度 × 0.8 并结束。
6. 末端跳（刹车区内按跳）：速度替换为 (512 · cos(θ/2) 沿行进方向, 394 竖直)，θ = 按下时行进仰角；不开 lurch 窗口（n = 1，弱）。和通用二段跳、跳板二段跳不共享次数；起飞会清掉没用的跳板二段跳。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| Echo 射程 `echoRange` | 50.0 m | 1968.5 u | 27.34 H | 脚本基础 40 m、最大 55 m（这个构建用的是加强值，[推断]） | [实测] |
| Echo 悬停高度 `echoHoverHeight` | 6.248 m | 246 u | 3.417 H | — | [实测] |
| 按住 → 起飞 `launchDelay` / 肩上 `launchDelayPerched` | — | 1.82 s / 1.662 s | — | 实测 1.808–1.826 s | [实测] |
| 屏幕门槛 `onScreenCos` | — | cos 60° = 0.5 | — | 50° 起飞 4 / 4，70° 0 / 5 | [数据] [实测] |
| 起飞速度 `launchSpeed` / 保持 `boostHold` | 23.95 m/s | 943.1 u/s / 0.2 s | 13.10 H/s | = 787 × 1.2 | [实测] |
| 巡航 `pathSpeed` | 19.99 m/s | 787 u/s | 10.93 H/s | — | [实测] |
| 刹车距离 `brakeDistance` / 减速 `brakeDecel` | 4.572 m / 26.61 m/s² | 180 u / 1047.6 u/s² | 2.5 H / 14.55 H/s² | — | [实测] [数据] |
| 结束速度 `minSpeed` | 2.0 m/s | 78.74 u/s | 1.094 H/s | 实测约 81 u/s 结束 | [数据] |
| 按蹲系数 `duckCancelScale` | — | 0.8（×） | — | — | [实测] |
| 末端跳 `endJumpForward` / `endJumpUp` | 13.00 / 10.01 m/s | 512 / 394 u/s | 7.111 / 5.472 H/s | 实测 vz 394.0，水平 493–507 | [数据] [实测] |
| 末端跳窗口打开距离 `endJumpOpenDistance` | 4.572 m | 180 u | 2.5 H | **数据有 115 / 180 两种读法** | [推断] |
| Vantage 水平上限（HSD） | 24.0 m/s | HSD 设计值 945 u/s | 13.13 H/s | — | [设计] |

Unity：`U:…/Abilities/VantageEcho/VantageEchoAbility.cs`，`VantageParams.Measured()` / `Fun()`、`VantageEchoAbility`（嵌套 `EndJumpClaimant`，`JumpRank.JetDriveEndJump` 280）、`IMantleBlocker`（预备和飞行中不能翻越）。没做：S22 去掉视线门槛、Echo dash、Echo tap strafe、Echolevator。

#### 验收

`VantageEchoM9CTests.EchoGoesToTheAimPointAndHovers`、`VantageEchoM9CTests.TheLiftOffIs1Point82SAfterTheHoldPressWhateverTheHold`、`VantageEchoM9CTests.LaunchGatesDistanceAndOnScreen`、`VantageEchoM9CTests.LineOfSightGateWithTheTwoOffsetRetries`；`JetDriveM9CTests.DriveShapeAgainstR5`、`JetDriveM9CTests.TheLongEchoDrive`、`JetDriveM9CTests.TheDriveTracksAMovingTarget`、`JetDriveM9CTests.CrouchScalesByPoint8AndEndsTheDrive`、`JetDriveM9CTests.AWallStopsTheDriveAtTheFace`、`JetDriveM9CTests.EndDoubleJumpWindowAndVelocity`。对照数据：VAN9（22 个计划表 × 5）、VAN8。已知差：轨迹最高点比 R5 低 10–20 u（README）。

#### 出处

- VAN9 TL;DR：射程、悬停、1.82 s、门槛、943.5 u/s、末端跳窗口。main
- VAN8：路径速度、刹车、按蹲、移动目标。main
- `research/phase2-local/m9/unity/M9C-UNITY.md`。main
- 脚本（本地）：`mp_ability_companion_launch.nut`（`CanLaunchToCompanion`）、`sh_vantage_companion.nut`。

### 5.53 飞行（Flight，HSD 设计，Fun 配置）

#### 原理

HSD 原创，不是 Apex 机制：按键切换飞行，无重力、按视角方向和方向键飞，Space 上、蹲下降。燃料限制时长，落地回充。属于"驱动者"，和钩爪 / 升梯互斥。

#### 规则和公式

切换（燃料 ≥ 1 s 才能开）；飞行中重力 0，速度以 1400 u/s² 的矢量加速度逼近期望速度（上限 450 u/s，竖直占 0.7）；燃料每秒 −1；再按、燃料尽或落地结束；落地 0.5 s 后每秒 +1；地面起飞竖直 150 u/s。HSD 全局上限（水平 900、向上 1100 u/s）照样生效。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 飞行速度 `maxSpeed` | 11.43 m/s | HSD 设计值 450 u/s | 6.25 H/s | — | [设计] |
| 加速度 `accel` | 35.56 m/s² | HSD 设计值 1400 u/s² | 19.44 H/s² | — | [设计] |
| 竖直比例 `verticalFraction` | — | 0.7（×） | — | — | [设计] |
| 燃料 `fuelMax` / 起飞最少 `fuelToStart` | — | 5 s / 1 s | — | — | [设计] |
| 回充 `refillPerSecond` / 延迟 `refillDelay` | — | 1 /s / 0.5 s | — | — | [设计] |
| 起飞竖直 `liftOff` | 3.81 m/s | HSD 设计值 150 u/s | 2.083 H/s | — | [设计] |

Unity：`U:…/Abilities/Flight/FlightAbility.cs`（`FlightParams`、`FlightAbility`）；创建在 `U:…/Abilities/_Core/FunFeatureParams.cs`（只在 Fun）。验收：`FunAbilityTests.FlightTogglesDrainsFuelAndLands`、`FunAbilityTests.FunSessionHasTheFeaturesAndTheReferenceDoesNot`、`A3Zipline.FlightEndsOnAMount`。没有 R5 对照，真人手感没验收。出处：`research/phase2-local/m5/M5-REPORT.md`（part B）、`research/phase2-local/m5/SKILL-RULES.md` §4；D-08。main

### 5.54 重力切换（GravitySwitch，HSD 设计，Fun 配置）

#### 原理

HSD 原创：重力键在 ×1.0 → ×0.45 → ×1.6 之间循环。跳跃高度跟着按 1 / 重力倍数缩放，所以**起跳速度不变**：低重力跳得高、飘；高重力跳得矮、快。它是一个世界设置，不是状态，切回去之前一直保持。

#### 规则和公式

g_eff = `sv_gravity` × 等级；`jumpHeight`、`slideJumpHeight` 按 1 / 等级缩放 → V = √(2 · g_eff · H / 等级) 不变，最高点 = H / 等级。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 重力等级 `levels` | — | HSD 设计值 1.0 / 0.45 / 1.6（× `sv_gravity`） | — | — | [设计] |
| 低重力下的起跳最高点（56 u / 0.45） | 3.161 m | 124.4 u | 1.728 H | — | [算] |
| 高重力下的起跳最高点（56 u / 1.6） | 0.889 m | 35 u | 0.486 H | — | [算] |

Unity：`U:…/Abilities/GravitySwitch/GravitySwitchAbility.cs`（`GravitySwitchParams`、`GravitySwitchAbility`），键 G（`FunButtons.Gravity`，只在游戏里）。验收：`FunAbilityTests.GravitySwitchKeepsTheTakeoffSpeedAndRaisesTheApex`。没有 R5 对照。出处：`research/phase2-local/m5/M5-REPORT.md`（part B）；D-08。main

---
