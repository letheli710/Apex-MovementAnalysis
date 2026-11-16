# 08 身体动画：持枪和移动叠加、泰坦步态 / 脚 / 地形 / 惯性、驾驶舱镜头

hb-ch08 写（2026-11-14），分支 `handbook/ch08`，还没合并。附件在 [08-body-animation/](08-body-animation/)：`pilot-seq-fades.tsv`（铁驭枪模常用序列的淡入淡出）、`titan-blend-times.tsv`（泰坦换步态的混合时长）。给总控的备注、建议的 D 行和待研究在 [`_notes/hb-ch08.md`](_notes/hb-ch08.md)。

## 白话说明

这一章讲"身体和手里的东西怎么跟着移动动起来"，分两半：

**铁驭（第 1 节）**：第一人称里看到的那把枪。人在走、跑、蹲、滑、跳、翻越的时候，枪怎么晃、怎么放低、怎么歪；换弹、切枪、开火、开镜这些"手上的动作"又怎么和移动叠在一起。R5 的做法可以浓缩成一句话：**一层慢慢换的主动作，加一层一直在算的小运动**。主动作只给"手的姿势明显不同"的情况（换弹、冲刺、翻越），走、蹲、滑、跳都不换主动作，只靠叠加。所以任何手上动作都能和任何移动自由组合，不用做"走路换弹""滑铲换弹"这种组合动画。手是一种"资源"：换弹占着手直到解锁，解锁后谁要手谁就能立刻抢走；跳和滑铲不用手，从不打断换弹。开镜时小运动几乎全收掉，所以"开镜就稳"。镜头和枪是两条线：同一个脚步节奏，镜头只晃零点几度，枪晃几度。

**泰坦（第 2、3 节）**：泰坦身体的步态、脚、地形和"重"的手感，以及驾驶舱里的第一人称镜头。资料来自 TF2（本地 Northstar 实测、模型解码、原生代码），R5 没有泰坦。TF2 的泰坦"重"不是靠慢，是靠**稳**：站着完全不动；头和骨盆像一块铁；持枪的手臂几乎不动；脚踩实、骨盆最低、脚步声在同一刻发生；身体比速度慢半拍（换步态要混 0.2–0.55 s，播放速度有死区）。驾驶舱镜头**不挂在身体上**：走路的起伏是一个 0.70 s 的定时器，每步给舱体弹簧一个很小的竖直冲量；冲刺下沉、dash 横滚、舱框晃动都是程序算的。和铁驭"轻"的对比放在 §2.8。

读完能做出：

1. 铁驭第一人称枪模的分层结构、持枪姿势、走路和冲刺的晃动、移动中换弹和切枪的规则、开镜压制。
2. 泰坦的步态选择、播放速度、腿的朝向、脚 IK、地形适应、上身叠加层，以及"重"的约束表。
3. 泰坦驾驶舱的常驻镜头、冲刺下沉、dash 横滚、舱框晃动、开火时舱框和画面的关系。

**和别的章的分界**

- 身体怎么移动（速度、加速度、状态）在 02–06 章；本章只**读**移动状态，从不写回模拟。
- 镜头在 07 章。本章只写两样镜头：铁驭"枪模不进镜头"的那条分界（§1.1），和泰坦驾驶舱镜头（§3，07 章 §2.8 / §2.13 已写的受击、上下机以 07 为准，这里只指过去）。
- 后坐（punch、jolt、枪的 kick）、开镜曲线本身（枪移到瞄具、FOV）、扩散、枪的重量（移动倍率）、命中反馈在 09 章。本章只讲"开镜时程序层被收掉"（§1.10）和"换弹 / 切枪对手的占用"（§1.8、§1.9）；弹药规则（加弹前被打断就没加上）只简述，细节以 09 为准。
- 泰坦的移动电机（两段加速、冲刺加速、dash 推力曲线、能量、转向、重力和小跳）在 [12 章](12-titan-motor.md)（总控 11-14 定）。本章 §2.8 / §2.9 只引用它的结果来解释惯性感和 dash 的身体。

### 本章出处缩写

| 缩写 | 路径（研究仓库根目录） | 在哪 |
|---|---|---|
| MA | `research/combat/MOVEMENT-ANIMATION.md`（§12 读代码、§13 实测） | **PR #123，还没合并（分支 `r5gap/anim`）**；#97 原版的 §2、§4 已被 §12 / §13 更正，不要用 #97 版 |
| HP | `research/combat/gun-measure/hold-pose/HOLD-POSE.md` | **PR #95，还没合并（分支 `combat/gun-measure`）**；#123 的分支里没有这个文件 |
| CM | `research/combat/gun-measure/C-MOTIONS.md` | PR #95，还没合并；表里"解锁"两列作废（D-118），用 RM |
| DS | `research/combat/gun-measure/report/02-draw-swap.md` | PR #95，还没合并 |
| SG | `research/combat/gun-measure/report/08-states-gaps.md` | PR #95，还没合并 |
| RM | `research/combat/gun-measure/reload-motion/RELOAD-MOTION.md`、`RM-SUMMARY.tsv` | PR #95，还没合并 |
| N10 | `research/rea-native/n10/N10-CAMERA.md` | main |
| DP | `research/DESIGN-PHILOSOPHY.md`（§7.11 腰射枪身角度） | main |
| TAF | `tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md` | main（结论 5 的"0.95 s"已被 RG 更正；§3 F6 / F7 里带"11-09 补测"的那几行为准） |
| RG | `tf2/expansion/titan/anim/ref-gait/REF-GAIT-1109.md` | main（研究 PR #113 合进来的内容；原始日志 RawData #19） |
| RN | `tf2/expansion/titan/anim/ref-native/REF-NATIVE-1109.md` | main（PR #111） |
| RU | `tf2/expansion/titan/anim/ref-upper/REF-UPPER-1109.md` | main（PR #112） |
| TPC | `tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` | main |
| TFC | `tf2/expansion/titan/kits/T-f-COCKPIT-RELOAD.md` | main |
| GAPS | `tf2/expansion/titan/full/TF2-GAPS.md` | **PR #98，还没合并（分支 `titan/full-decisions`）**；工作区本地也有 |
| TFE | `tf2/expansion/titan/feel/TITAN-FEEL.md` | **PR #118，还没合并（分支 `titan/feel-doc`）** |
| DEC | `DECISIONS.md` | D-127 / D-136 在 PR #98（`titan/full-decisions`）；D-187 在 PR #116（`titan/model-v3`）；D-118 在 PR #91（`combat/w3-records`）；D-123 在 PR #100（`combat/gun-models-records`）。都还没合并 |

**Unity 简写**（都在 HSD-Unity，`Assets/HSD/Game/Runtime/` 下）：

- 铁驭持枪：`Combat/Arsenal/HoldPose.cs`（`HoldState`、`HoldWave`、`HoldGun`、`HoldData`、`HoldBlend`）、`HoldData.gen.cs`（每把枪的实测表）、`HeldMotion.cs`（`HeldMotion`、`ReloadShow`、`HoldInput`）、`HeldModels.cs`（`HeldModelView`，枪模有自己的相机）、`ArsenalWeapon.cs`（换弹三个时刻、收枪再掏枪）、`ArsenalConfig.cs`（开关 `reloadMoments`、`swapHolster`、`holdPose`）。**在 HSD-Unity PR #65 上，还没合并（分支 `combat/wp4-reload-swap`，6ec7285）**；PR #67 及以上的叠加分支也带着它。测试在 `Assets/HSD/Game/Tests/Editor/`：`CombatHoldPoseTests`、`CombatReloadSwapTests`。
- 泰坦：`Titan/Animation/`（`TitanBodyCore`、`TitanBodyAnimator`、`TitanFeet`（`TitanFoot`）、`TitanWalkKeyPoses*`（`TitanKeyGait`）、`TitanDims*`）、`Titan/Camera/`（`TitanCamParams`、`TitanCamModel`、`TitanCockpitCamera : ITitanCameraLayer`、`TitanCockpitView`）、`Titan/Weapon/TitanGunMotion.cs`。**最全的是 HSD-Unity PR #78（分支 `titan/integration`，551b50e），还没合并**；调参面板和三种底盘能开在 PR #83（`titan/feel-build`，还没合并）。测试 `TitanAnimTests`、`TitanCamTests`。

---

## 0. 约定

### 0.1 单位、身高和符号

- 长度 u（R5 / TF2 原值），`[m]` 列 = u × 0.0254（[01 §3](01-units-body.md)），是算出来的。
- **铁驭**的身高比例除以 H = 72 u；**泰坦**按 [01 §4.3](01-units-body.md) 的建议除以 **H_t = 235 u**（TF2 泰坦碰撞体高度，三种底盘相同），比例列写 `H_t`。不要拿泰坦的数除以 72。
- 角度、时间、周期、相位（0–1 的周期比例）、比例、播放倍率不换算，`[m]` 和比例两列写"—"。
- 枪模的坐标在**镜头坐标系**里：F 前、R 右、U 上（u）。枪身角度用 R5 / Source 的号：俯仰 + 是向下（枪口压低），偏航 + 是向左，横滚 + 是向右倾（HP 的 `gP`、`gY`；横滚只用相对站立的差 `dgR`）。
- "相位"指一个完整左右步（周期）里的位置，0–1。

### 0.2 依据标签

沿用 README §5：[实测] [反编译] [数据] [算] [推断] [设计]，TF2 来源写 [TF2 实测] [TF2 数据]（设置文件、脚本、ConVar、解码的模型）[TF2 反编译]。"R5" 指本地混合构建（S21 客户端 + S3 dedi）；枪模动画在客户端，**推断**和正版相同（MA 开头）。样本少的地方在依据列写次数。

### 0.3 名词

- **主序列**：枪模（或泰坦身体）当前播的那一段动画，一次只有一段。
- **过渡层**：换主序列时，旧序列不立刻消失，而是压成一层慢慢淡掉。
- **叠加层（overlay / gesture）**：在主序列上**加**一段 delta 动画（只记相对差的动画），比如开火、起蹲、落地。
- **程序层**：代码每帧算的偏移（姿势表、晃动、转向超前）。
- **解锁**：换弹里"能开枪、能开镜"的那一刻，比动画结束早。

---

## 1. 铁驭：持枪和移动怎么叠在一起

### 1.1 分层结构和序列过渡

#### 原理

动作和移动分两层，组合就不用做了。主序列管"手在干什么"（换弹、冲刺放枪、翻越收枪），程序层和叠加层管"身体在怎么动"（走路晃、蹲下侧翻、落地一沉）。换弹 × 走、蹲、跳、滑铲全靠相加得到，所以动画量只和"手的动作数"有关，不和"动作 × 移动"的组合数有关（MA §8 第 1 条）。

换主序列时旧动作用 smoothstep 淡出，枪的位置连续，玩家看不到"跳一下"。

镜头和枪分开：枪的晃动不进镜头，镜头的晃动也不是枪带的。同一个脚步节奏，镜头只拿很小一部分（冲刺时镜头俯仰 ±0.3°，枪几度），所以"世界稳，只有手在动"（MA §7、§8 第 7 条；07 章 §3.4）。

#### 规则和公式

1. 每帧枪模 = 主序列当前帧 + 过渡层（旧序列按权重）+ 叠加层（delta，至少一层一直开着）+ pose parameter 驱动的变化 + 程序层（持枪姿势 §1.2、走路晃动 §1.3、转向超前 §1.7、开火 jolt 见 09）。
2. **主序列只有这些**（R-301 名字，别的枪结构相同、编号不同）：

   | 状态 | 主序列 | 长度 |
   |---|---|---|
   | 站、走、蹲、蹲走、跳、下落、落地、滑铲 | `ads_out` 停在最后一帧（**腰射站姿就是关镜动画的终点**） | 一直 |
   | 开镜 | `ads_in`，进度 = 开镜比例 zf | 跟 zf |
   | 冲刺 | `sprint` 循环 | 0.556 s |
   | 松开冲刺 / 冲刺中起跳 | `sprintraise`（或 `_regrip`） | 0.30–0.33 s |
   | 冲刺中按滑铲 | `sprintslide`，之后回 `ads_out` | 0.43 s |
   | 换弹 | `reload` / `reload_empty`（滑索上 `_onehanded`） | = 换弹时间 |
   | 翻越 | `holster` → `raise` | 1.43 s、0.50 s |
   | 上滑索 / 钩爪 | `lower_onehanded` → `raise_onehanded` → 单手持枪 | 0.49 s、约 0.35 s |

3. **叠加层**（视图模型最多 9 层，实测只用到 0、1 两层）：

   | 层 | 平时 | 会变成 |
   |---|---|---|
   | 0 | `idle`（循环 delta） | 蹲：`idle_to_crouch` → `crouch`（循环）→ `crouch_to_idle`；开火：`fire` / `fire_regrip` 交替；滑索：`idle_onehanded`。冲刺、换弹时**关掉** |
   | 1 | 关 | 跳：`jump`；落地：`land` / `land_low` / `land_med` / `land_high` |

   有两代模型：新模型（R-301、Spitfire、Longbow）的起蹲收蹲放叠加层 0，主序列不变；旧模型（P2020、Peacekeeper、R-99、G7、Wingman，序列名带 `_TEMP`）换主序列 `idle_to_crouch_TEMP`（约 0.84 s）。手册取新模型的做法。
4. **序列过渡**（主序列和叠加层都一样）：换序列那一帧，旧序列压成一个过渡层，

   淡出时长 T = min(旧序列的淡出时间, 新序列的淡入时间)
   s = clamp(1 − (现在 − 开始) / T, 0, 1)，旧层权重 w = (3 − 2s)·s²（smoothstep）

   旧序列在过渡中按自己的速率继续播；更早的过渡层的权重再乘上所有更新层的权重；标了 snap 的序列不过渡。淡入淡出时间写在每段动画里，代码没有固定值。常用值见附件 `pilot-seq-fades.tsv`，多数 0.2 s。
5. pose parameter（模型的输入，0–1，按模型里的范围夹住）：`ads_blend` = zf、`crouchFraction`、`oneHandFraction`、`aimPitch`、`aimYaw`、`sprintfrac`、`velocity` = 三维速度 / 500 u/s（到 1 封顶）、`move_yaw` 等共 14 个。**实测走路晃动的幅度不跟 `velocity`、`crouchFraction` 变**（§1.3），所以手册不靠它们驱动晃动。
6. 镜头：枪模的任何运动都不进镜头（07 章 §3.4）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 多数序列的淡入 / 淡出 | — | 0.2 s / 0.2 s | — | 见附件 | [实测] 482 次切换全部 = min(旧淡出, 新淡入) |
| `ads_in` 淡入 | — | 0.1 s | — | — | [实测] |
| `idle`、`crouch` 叠加层 | — | 0.3 s / 0.3 s | — | — | [实测] |
| 开火叠加 `fire` / `fire_regrip` | — | 0.05 s / 0.2 s | — | — | [实测] |
| 跳 `jump` / 落地 `land*` | — | 0.2 / 0.35 s；0.05 / 0.35 s | — | — | [实测] |
| `velocity` 满值的速度 | 12.7 m/s | 500 u/s | 6.94 H/s | — | [实测]（173.5 → 0.35，572 → 1.0） |
| 切序列时枪口每帧最大位移（约 7 ms 一帧） | 0.0008–0.0018 m | 0.03–0.07 u | — | 位置连续 | [实测] R-301 / Wingman |

#### 实现模板

```
// 单位：u、°、s。只是画面，不回写模拟
class ViewModelAnimator:
    main: Sequence;  transitions: List<(seq, t0, T, cycleAt0, rate)>  // 最多 6 层
    overlays[0..8]: (seq, weight, t0)
    on setMain(next):
        if next == main: return
        if next.snap: transitions.clear()
        else transitions.push(main, now, min(main.fadeOut, next.fadeIn), main.cycle, main.rate)
        main = next; main.cycle = 0
    pose(now):
        p = main.sample()
        wNewer = 1
        for tr in transitions newest→oldest:
            s = clamp01(1 - (now - tr.t0)/tr.T);  w = (3 - 2s)*s*s * wNewer
            p = blend(p, tr.seq.sampleAt(tr.cycleAt0 + (now-tr.t0)*tr.rate), w)
            wNewer = w
        transitions.removeWhere(t0 + T <= now)
        for o in overlays where o.on: p += o.weight * o.seq.sampleDelta()
        p += holdPose()(§1.2) + walkSwing()(§1.3) + turnLead()(§1.7) + jolt()(09 章)
        return p * adsMask(zf)(§1.10 只作用在程序层和叠加层)
```

注意：

- 没有骨骼动画的占位枪（HSD 现在）只能动整把枪：主序列用"按时间查表的枪口位置 + 枪身角度"代替（换弹走 RM 的逐帧表，§1.8），叠加层和程序层照样相加。
- 过渡要用 smoothstep，不要线性；线性在开始和结束处有拐角（MA §12.2）。

Unity 参考实现：`HeldModels.cs` 的 `HeldModelView.Update`（主序列 = 换弹表 / 切枪 / 开镜曲线；程序层 = `HoldBlend`，权重 `(1 − zoom) × (1 − reloadShare)`）；`HoldPose.cs` 的 `HoldBlend.Step`（状态之间 smoothstep）。HSD 没有通用的序列过渡器，换弹被切断时用 `cutOffset` / `cutTurn` 接住，避免跳（`HeldModelView.Update` 末尾）。分支 `combat/wp4-reload-swap`（PR #65，还没合并）。

#### 验收

- `CombatHoldPoseTests.TheTransitionTakesItsMeasuredTime`：状态之间按实测 90 % 时间过渡。
- `CombatReloadSwapTests.HoldingFireWaitsForTheUnlockThenCutsTheAnimation`：被切断时位置连续（不跳）。
- 指标：切序列那一帧枪口位移 ≤ 0.1 u（R5 最大 0.07 u / 7 ms）。
- 对照数据：MA `movement-anim/runtime/FADES.tsv`（482 次过渡）、`SEQTABLE.tsv`（8 把枪的序列表）。PR #123，还没合并。
- **没有**通用过渡器的测试：HSD 以后做了骨骼动画再补（`_notes`）。

#### 出处

- MA §1、§2、§3：主序列只在冲刺换、换弹直接相加、开镜收程序层、切序列不跳。PR #123，还没合并
- MA §12.2、§13.7：过渡规则和秒数（482 次）；§13.9 叠加层整体；§13.3 两代下蹲做法；§12.3 14 个 pose parameter。PR #123，还没合并
- MA §7、N10 §1–§3：枪的晃动不进镜头。main
- [反编译] 序列过渡建层 0x140aba4d0、权重 0x140abaf40、合成 0x140abb2b0；骨骼合成顺序 0x1407620e0；视图模型叠加层 0x1409e0a70；pose parameter 0x1408596d0 / 0x14085a3c0；序列表 `CStudioHdr +0x10`，描述 `+0x40` 淡入、`+0x44` 淡出。

---

### 1.2 持枪姿势（hold pose）

#### 原理

每把枪的"站着拿"位置都不一样，而且枪身**不是平着拿的**：多数枪横滚 2–10°，冲刺时整把枪大幅转动（R-301 侧翻 −50°）。这些姿势是枪的个性所在；走路的晃动所有枪几乎一样，所以"枪和枪的差别主要来自主序列和停放位置，不是程序层"（MA §4.2 末）。

用户 11-05 定（DP §7.11、D-123）：以后新增或重做的枪，腰射枪身角度都用 R5 实测，不平着拿；没实测的要标明。**绕枪口转**：枪口点不动，曳光起点和开火位置都不受姿势影响。

#### 规则和公式

1. 站立腰射：每把枪一个枪口位置（镜头坐标）和枪身角度，查表（HP `HP-POSE.tsv` 的 `stand` 行，以它为准，不用旧的 `D-VIEWMODEL`，D-121 作废）。
2. 其他状态（走、冲刺、蹲、蹲走、滑铲、空中）都是**相对站立的差**，在**同一次旋转**里和站立角度相加（不要先转站立、再转差值）。
3. 枪模原点 = 枪口位置 − R × 枪口在模型里的位置；旋转顺序按 Source 的 yaw、pitch、roll [推断]。
4. 每种状态怎么取值：

   | 状态 | 怎么做 | 依据 |
   |---|---|---|
   | 冲刺 | **按枪查表**（平均姿势 + 32 相位波形，§1.4）；分组只给新枪做默认值 | 分组误差最大 16 u |
   | 站立位置 | 按枪查表 | 每把枪都不同 |
   | 走 | 一条共用的角度波形（§1.3），枪口由旋转带出 | 枪之间差最多 0.9° |
   | 蹲、滑铲 | 每把枪一个侧翻角 + 小平移；滑铲再下移 0.55 u | 组内侧翻标准差 4.3° |
   | 跳、落地 | 共用一条（§1.5） | Bocek 例外 |
   | 过渡 | 共用约 0.2 s 的 smoothstep，按 90 % 时间换算 | §1.5 表 |

5. 站立有轻微"呼吸"：上下 ±0.23 u（中位数），周期约 1.2 s。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 站立枪口位置（前、右、上） | 0.813, 0.076, −0.076 m | 32, 3, −3 u | 0.444, 0.042, −0.042 H | 各枪见 DS §7 / HP-POSE | [实测] |
| R-301 站立枪身角度（俯仰 / 偏航 / 横滚） | — | 0.84° / 0.11° / 6.14° | — | 多数枪横滚 2–10°，俯仰 0–3°；Bocek 横滚 42° | [实测] DP §7.11 |
| 站立呼吸（上下） | ±0.0058 m | ±0.23 u（最大 ±0.76） | ±0.0032 H | — | [实测] 31 把 |
| 站立呼吸周期 | — | 约 1.2 s | — | — | [实测] |
| 两次测量的姿势重复性 | ≤ 0.0099 m | 中位 0.00–0.03 u，最大 0.39 u | — | — | [实测] |

#### 实现模板

```
// 单位：u、°
gunPose(state, gun):
    base  = HOLD[gun].stand                      // 枪口位置 + 枪身角度
    delta = blendStates(HOLD[gun].pose[state])   // §1.5 的过渡
    delta += walkSwing() + sprintWave() + landing() + turnLead()
    angles = base.angles + delta.angles          // 同一次旋转
    muzzle = base.muzzle + delta.offset
    origin = muzzle - R(angles) * gun.muzzleInModel
```

注意：枪模有自己的 FOV，表是**世界坐标**，屏幕上的大小取决于枪模相机的 FOV（09 章，D-122）；表是默认皮肤、不带配件；只有枪身，手和手臂没用上（挂点 `R_HAND`、`L_HAND` 以后可取）。

Unity 参考实现：`HoldData`（`HoldData.gen.cs` 由 HP 的 TSV 生成，`HoldGun.stand / pose / waves`）、`HoldBlend.Rotation`（Source 角度 → Unity 旋转）、`HeldModelView.Update`（绕枪口转）。开关 `ArsenalConfig.holdPose`（关 = 旧的单一位置、不动）。分支 `combat/wp4-reload-swap`（PR #65，还没合并）。

#### 验收

- `CombatHoldPoseTests.EveryGunThatShowsAModelHasAMeasuredHold`、`EachGunSitsWhereItDoesInR5`、`TheAnglesTurnTheWayR5Says`、`TheOffSwitchIsTheOldPlaceAndNothingMoves`。
- `CombatHoldPoseTests.ATracerLeavesTheMuzzleAndTheRoundStillFliesFromTheEye`：姿势不改开火位置。
- 合格线：每把枪站立枪口和 HP-POSE 差 < 0.1 u、角度差 < 0.5° [设计]。屏幕上的大小要和 R5 截图对比，**还没做**（`_notes`）。

#### 出处

- HP §1、§6、§8：站立位置、按枪查表的理由、角度从挂点读。PR #95，还没合并
- DP §7.11：腰射枪身角度通用规则（用户 11-05）。main；D-123（PR #100，还没合并）
- DS §7：31 把枪腰射 / 开镜枪口位置。PR #95，还没合并
- D-121（PR #99）：`D-VIEWMODEL` 作废。

---

### 1.3 走路和蹲走的晃动（bob）

#### 原理

走路时枪按"横放的 8 字"晃：上下走两趟、左右走一趟，一步一次上下、两步一次左右。**晃动的快慢跟着走过的距离，大小不跟速度**：慢慢走晃得慢，但幅度一样，甚至略大。所有枪几乎一样，所以一条共用曲线就够（MA §13.3、§13.5）。

前进时枪整体往下、往后挪一点（sway），停下后有弹性地回来。

#### 规则和公式

1. 相位 φ（0–1，一个左右来回）按**走过的水平距离**推进：dφ = |v_h|·dt / D，D = 每个来回的距离；同时 dφ/dt ≤ 1 / T_min（最快每 0.80 s 一个来回）。满速走路 173.5 u/s 时正好碰到上限。
2. 偏移 = A × 波形(φ)：左右、偏航、横滚用一次谐波（周期 = 一个来回），俯仰和上下用二次谐波（周期一半）。幅度 A **不乘速度**。波形不是纯正弦，有 32 相位的实测表（HP `HP-WAVE-MEAN.tsv` 的 walk / crouchwalk）。
3. 蹲走用同一规则，D 相同，幅度略小（表）。
4. 前进 sway：一直按前进时枪口相对站立下移、后移（表）；走和冲刺一样大，不随速度变。停下后位置以时间常数约 0.5 s 回零，角度约 0.1 s。
5. 跳的时候也走这一层（§1.5）。
6. 速度从 0 起步到满速时，幅度按状态过渡（§1.5，约 0.35 s）淡入；停下按约 0.9 s 回稳（HP §5 "走 → 站"）。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 每个来回的距离 D（R-301） | 3.53 m | 139 u | 1.93 H | 136–141 u | [实测] 7 档速度 |
| D（多数枪：Wingman、R-99、Spitfire 等） | 3.05 m | 120 u | 1.67 H | G7 132 u | [实测] |
| 最短来回时间 T_min | — | 0.80 s | — | 满速 173.5 u/s 时碰到 | [实测] 所有枪 |
| 满速走速 | 4.41 m/s | 173.5 u/s | 2.41 H/s | — | [实测] |
| 偏航幅度（走） | — | ±1.38–1.59°（R-301） | — | 速度越低越大；所有枪差 < 0.1° | [实测] |
| 横滚幅度（走） | — | ±1.0–1.3° | — | — | [实测] |
| 俯仰幅度（走） | — | ±0.44–0.50° | — | — | [实测] |
| 枪口左右 / 上下摆幅（走，中位数） | ±0.0165 / ±0.0119 m | ±0.65 / ±0.47 u | ±0.0090 / ±0.0065 H | 枪口差来自枪长 | [实测] 31 把 |
| 偏航 / 横滚幅度（蹲走） | — | ±1.05–1.30° / ±1.0–1.2° | — | — | [实测] |
| 走路平均姿势（相对站立）：前 / 上 | −0.0030 / −0.0150 m | −0.12 / −0.59 u，角度 0 | −0.0017 / −0.0082 H | 31 把一样 | [实测] |
| 前进 sway：上 / 前 | −0.0145 / −0.0028 m | −0.57 / −0.11 u | −0.0079 / −0.0015 H | 冲刺一样 | [实测] R-301 / Wingman |
| sway 位置回零时间常数 | — | 0.49–0.54 s | — | 1 次 | [实测] |
| sway 角度回零 | — | 约 0.1 s | — | — | [实测] |

R5 武器文件里的 `bob_*`、`sway_*` 字段（如 `bob_cycle_time` 0.4）**客户端根本不读**，是 TF2 留下的；幅度和字段对不上是正常的。晃动来自哪段代码还没找到（加在视图模型实体自己的位置和角度上，不是主序列也不是叠加层 0，换弹时照样晃）。所以这条规则是**照实测曲线写的**，不是 R5 公式。

#### 实现模板

```
// 单位：u、s
walkSwing(dt):
    if state not in {Walk, CrouchWalk}: target = 0
    rate  = min(|v_h| / D, 1 / T_min)          // 来回 / 秒
    phase = frac(phase + rate * dt)
    w     = stateBlend(Walk or CrouchWalk)     // §1.5 的过渡权重，不乘速度
    offset += w * table(phase)                 // 32 相位插值：dF dR dU gP gY gR
    sway   = follow(sway, forwardHeld ? swayFwd : 0, tauPos 0.5 s, tauAng 0.1 s)
```

Unity 参考实现：`HoldBlend.Step` 里 `toWave[1]`（走）、`toWave[2]`（蹲走）和 `AddWave`。**HSD 现在和 R5 不一样**：Unity 的相位按**时间**推进（`phase += dt / period`），走路波形的权重**乘了** `speed / 173.5`；R5 是按距离推进、幅度不跟速度。满速走路时两者一样，低速时 HSD 晃得快而小、R5 晃得慢而大。sway（前进下移 + 弹性回位）HSD 没有单独做，只有走路平均姿势。这两条写进 `_notes`（建议的 R5-DIFF 条目）。分支 `combat/wp4-reload-swap`（PR #65，还没合并）。

#### 验收

- `CombatHoldPoseTests.TheSwingHasItsPeriodAndSize`：满速走路周期 0.80 s、幅度符合 HP。
- **要补的测试**（按距离推进那条做了以后）：69.4 u/s 走路一个来回 2.00 s（R-301），121.8 u/s 1.14 s；幅度和 173.5 u/s 差 < 15 %。数据：MA `movement-anim/runtime/PERIODS.tsv`、`C4-CROUCHWALK.tsv`（PR #123，还没合并）。
- 合格线：周期差 < 3 %，偏航幅度差 < 0.15° [设计]。
- 开镜下的走路晃动见 §1.10。

#### 出处

- MA §4.1、§4.2、§13.3、§13.5：晃动周期、幅度、按距离推进、所有枪一样；sway 和回位。PR #123，还没合并
- MA §12.1：客户端不读 `bob_*`（[反编译] 武器字段登记 0x1400eaef0，1175 项里没有 `bob_*`）；§10 新开一行"晃动从哪来"（读 0x14085c3e0 之前写实体 `+0x188` / `+0x194` 的代码）。PR #123，还没合并
- HP §3：31 把枪走路一样、摆幅和周期。PR #95，还没合并

---

### 1.4 冲刺姿势和冲刺循环

#### 原理

冲刺是唯一换主序列的移动：枪放下来、大幅转过去。这是"只有手的姿势明显不同才值得一段主序列"（MA §8 第 2 条）。冲刺循环的节奏**固定**，不跟速度：顶着墙几乎不动也是这个节奏，被加速到 572 u/s 也是。进入冲刺时用约 1 s 把摆动幅度从小拉满。

有两种冲刺持枪法：步枪式（枪口向左、枪身侧翻约 −50°）和手枪式（枪口向右向下、下压约 22°）。每把枪的握法确实不一样，分组误差太大，所以按枪查表。

#### 规则和公式

1. 按冲刺键立刻进 `sprint` 循环（没有进入动画），从 0.2 s 的过渡里自然甩进去：R-301 0.2 s 内枪口压到 −1.3°、横滚 −1.2°，约 0.5 s 接上循环。
2. 循环周期固定 0.556 s（每秒 1.80 次），**不随速度缩放**。步枪式的上下是半个周期（约 0.277 s），左右和偏航一个周期；手枪式和 30-30 上下左右同周期。
3. 摆幅权重 = `sprintfrac`，按时间（不是速度）在冲刺开始后约 1 s 从 0 涨到 1；涨的那段幅度小（R-301 偏航 0.3–1.0°）。
4. 平均姿势和波形按枪查 HP（`HP-POSE.tsv` 的 sprint、`HP-WAVE-MEAN.tsv`），波形不是单一正弦。
5. 松开冲刺：`sprintraise` 约 0.30–0.33 s 抬回；姿势 90 % 到位约 0.20 s（§1.5）。冲刺中起跳也走 `sprintraise`，空中回到腰射，落地继续冲刺时循环从 0 开始。
6. 冲刺中换弹：换弹占了主序列，**冲刺姿势和循环都不播**，手是换弹的姿势，枪上只叠走路那样的晃动（§1.8）。
7. 没有冲刺动画的枪（Sheila）用走路的晃动。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺循环周期 | — | 0.556 s | — | 25–572 u/s 都是 0.555–0.556 s | [实测] R-301 / Wingman 各 2 次 |
| `sprintfrac` 涨满时间 | — | 约 1 s | — | 和速度无关 | [实测] |
| 冲刺速度（参考） | 6.60 m/s | 260 u/s | 3.61 H/s | — | [实测] |
| R-301 冲刺平均（相对站立）前 / 右 / 上 | −0.051 / −0.244 / −0.119 m | −2.0 / −9.6 / −4.7 u | −0.028 / −0.133 / −0.065 H | 步枪式右 −5.7 … −26.0 u | [实测] |
| R-301 下压 / 向左 / 侧翻 | — | 5.0° / 18.8° / −50.7° | — | 步枪式侧翻 −46 … −51° | [实测] |
| R-301 摆幅：右 / 上 / 偏航 | ±0.160 / ±0.069 m / — | ±6.3 / ±2.7 u / ±13.1° | ±0.088 / ±0.038 H | — | [实测] |
| P2020（手枪式）平均 前 / 右 / 上 | −0.384 / 0.315 / −0.414 m | −15.1 / 12.4 / −16.3 u | −0.210 / 0.172 / −0.226 H | 手枪式 6 把 | [实测] |
| P2020 下压 / 向左 / 侧翻 | — | 22.1° / −16.0° / −40.8° | — | — | [实测] |
| 手枪式偏航摆幅 | — | ±27° | — | 26.9–27.2° | [实测] |
| 镜头俯仰 / 偏航跑步晃动（对比） | — | ±0.3° / ±0.4° | — | 07 章 §3.2 | [实测] |

#### 实现模板

```
// 单位：u、°、s
sprintLayer(dt):
    if state == Sprint and not reload.active:
        sprintFrac = min(1, sprintFrac + dt / 1.0)      // 按时间
        phaseS = frac(phaseS + dt / 0.556)              // 不跟速度
        offset += HOLD[gun].pose[Sprint] * stateBlend + sprintFrac * WAVE[gun].sprint(phaseS)
    else: sprintFrac = 0
```

Unity 参考实现：`HoldBlend.Step` 的 `toWave[0]`（冲刺波形，权重 1）、`Target(...HoldState.Sprint)`、`HoldData.IntoSprint`。HSD 没有 `sprintfrac` 那 1 s 的幅度爬升（直接按状态过渡 0.2 s 进满幅），写进 `_notes`。冲刺中换弹：`HeldModelView.Update` 的 `overridden = reload.active && state == Sprint`，0.1 s 内把整个程序层收掉。HSD 收掉的是全部（包括走路那样的晃动），R5 只换掉冲刺姿势、晃动还在，小差别，写进 `_notes`。分支 `combat/wp4-reload-swap`。

#### 验收

- `CombatHoldPoseTests.SprintIsThePoseOfThatGun`、`TheSwingHasItsPeriodAndSize`（冲刺 0.556 s）。
- 要补：冲刺开始后 0.3 s 内摆幅 ≤ 满幅的 60 %（`sprintfrac`）[设计]。
- 对照数据：HP `HP-POSE.tsv`、`HP-WAVE-MEAN.tsv`（PR #95）；MA `C3-SPRINT.tsv`（PR #123）。
- 合格线：每把枪平均姿势枪口差 < 0.5 u、角度 < 1°；波形角度中位差 < 1.5° [设计]（R5 自己两次之间冲刺枪口差中位 0.4 u、最大 3.2 u）。

#### 出处

- HP §2、§6：31 把枪冲刺表、两种持枪法、为什么不分组。PR #95，还没合并
- MA §3、§6、§13.4：冲刺循环 0.556 s 不跟速度、`sprintfrac` 按时间、进入冲刺的甩动。PR #123，还没合并
- MA §5.1：冲刺中换弹手是换弹的姿势。PR #123，还没合并

---

### 1.5 蹲、滑铲、跳和落地

#### 原理

蹲和滑铲是**同一个姿势**：枪侧翻约 −55°（"歪着拿"）。滑铲没有自己的枪动画，只比蹲多下移一点，所以拉长的滑铲和自然滑铲看起来完全一样。跳的时候枪只动很小：起跳枪口先抬、过顶后压、落地再弹一下，和竖直速度反着走，像手的惯性。落地一下最大偏 2–3 u，0.6–0.8 s 回稳。

#### 规则和公式

1. 蹲：每把枪一个侧翻角（−45 … −60°，例外见表）+ 枪口向左 2.5 u、向下 0.8 u。另有"下蹲时枪下移" `viewmodelDuckOffset × sin(crouchFraction · π/2)`，开镜时在 `zoom_scope_frac_start` 之前淡出（§1.10）。
2. 滑铲 = 蹲的姿势，再下移约 0.55 u；没有周期摆动（枪口上下 ±0.18 u）。冲刺进滑铲时主序列 `sprintslide` 0.43 s，之后回腰射主序列。
3. 空中：枪口平均上 0.9 u、上抬 0.7°。起跳：枪口先抬 1.5°（0.1 s），过顶后压到 −0.8°（0.5 s），落地再抬 1.0° 回弹；枪的高度和竖直速度反向，滞后约 0.3 s（R-301，1 次）。叠加层 1 放 `jump`。
4. 落地：叠加层 1 换 `land*`；枪口最多偏 2.3–2.7 u，约 0.15 s 到最大，0.6–0.8 s 回稳。HSD 用一条共用曲线，按落地竖直速度缩放（−280 u/s 时满幅）[设计]。
5. 状态之间的过渡（90 % 时间，角度那组；按 smoothstep 的 90 % 点换算成总时长：总时长 = t90 / 0.804）：

   | 过渡 | 距离 | 角度 50 % / 90 % | 90 % 的范围 |
   |---|---|---|---|
   | 站 → 冲刺 | 15 u，53° | 0.10 / 0.17 s | 0.16–0.30 s |
   | 冲刺 → 站 | 同上 | 0.14 / 0.20 s | 0.14–0.33 s |
   | 蹲下 | 2.9 u，54° | 0.16 / 0.21 s | 0.16–0.39 s |
   | 站起 | 同上 | 0.12 / 0.19 s | 0.17–0.35 s |
   | 冲刺 → 滑铲 | 10 u，21° | 0.07 / 0.25 s | 0.00–0.36 s |
   | 滑铲 → 站 | 3 u，54° | 0.16 / 0.21 s | 0.18–0.54 s |
   | 站 → 走 / 走 → 站（枪口，主要是摆动） | 0.6 u | 0.30 / 0.35 s；0.35 / 0.91 s | — |

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 蹲 / 滑铲侧翻（相对站立） | — | 约 −55° | — | −45 … −60°；Mozambique、Peacekeeper −27°，Mastiff −11°，Nemesis −72°，Bocek +36°，Sheila 0 | [实测] 31 把 |
| 蹲时枪口向左 / 向下 | 0.064 / 0.020 m | 2.5 / 0.8 u | 0.035 / 0.011 H | — | [实测] |
| 滑铲比蹲多下移 | 0.014 m | 0.55 u | 0.0076 H | — | [实测] |
| 自然滑铲 vs 拉长滑铲的姿势差 | 0.002 m | 中位 0.08 u，最大 0.17 u | — | — | [实测] |
| 空中平均：枪口上 / 上抬 | 0.023 m / — | 0.9 u / 0.7° | 0.0125 H | Bocek 1.9 u / 3.3° | [实测] |
| 起跳上抬 / 过顶下压 / 落地回弹 | — | 1.5° @0.1 s / −0.8° @0.5 s / 1.0° | — | 1 次 | [实测] R-301 |
| 落地最大偏移 | 0.058–0.069 m | 2.3–2.7 u | 0.032–0.0375 H | — | [实测] |
| 落地到最大 / 回稳 | — | 0.15 s / 0.6–0.8 s | — | — | [实测] |
| 落地缩放满幅的竖直速度 | 7.11 m/s | 280 u/s | 3.89 H/s | 实测两档 −280、−610 | [设计]（HSD 取值） |

#### 实现模板

```
// 单位：u、°、s
onStateChange(from, to):
    blendFrom = current; blendT = 0
    blendLen = t90(from, to) / 0.804           // smoothstep 在 0.804 处到 90 %
landing(t, vzAtLand):
    k = clamp01(|vzAtLand| / 280)
    offset += k * LAND_CURVE(t)                // 21 点曲线，HP-TRANSITION.tsv jump_land
```

Unity 参考实现：`HoldBlend.Seconds`（`HoldData.IntoSprint`、`OutOfSprint`、`SprintToSlide`、`SlideToStand`、`DuckDown`、`DuckUp`，`SmoothstepAt90` = 0.804）、`HoldBlend.AddLanding`（`HoldData.Landing`，按 `|vz| / 280` 缩放）、`HoldState.Crouch / Slide / Air`。分支 `combat/wp4-reload-swap`。

#### 验收

- `CombatHoldPoseTests.CrouchAndSlideAreOnePoseMostlyRolled`、`ALandingDipsThenSettles`、`TheTransitionTakesItsMeasuredTime`、`TheSimSaysWhatTheBodyIsDoing`。
- 对照数据：HP `HP-TRANSITION.tsv`（50 % / 90 % 和 21 点曲线）、`HP-POSE.tsv`。PR #95，还没合并
- 合格线：过渡 90 % 时间差 < 0.03 s；落地最大偏移差 < 0.5 u [设计]。

#### 出处

- HP §4、§5：蹲、滑铲、跳、落地、过渡。PR #95，还没合并
- MA §4.2（跳的 sway）、§13.3（叠加层 1 放 `jump` / `land*`）、§12.1（下蹲时枪下移 [反编译] 0x14085bdb0）。PR #123，还没合并

---

### 1.6 翻越、滑索、钩爪、跑墙时的枪

#### 原理

动作要不要占手，决定枪怎么动。翻越要用两只手撑，所以**收枪再抬枪**；上滑索要一只手抓绳，所以换成**单手持枪**；钩爪拉人也把枪放下。跑墙不用手，R5 模型里有一段 `run_layer_wall` 叠加动画，但本地构建里跑墙关着，没看到它播。

#### 规则和公式

1. 翻越：主序列 `holster`（约 1.43 s，覆盖翻越过程）→ `raise`（0.50 s，等于 `raise_time`，1 次，可能巧合）。翻越开始就打断开火（R-301 只打出 4 发、Wingman 1 发，之后枪收起）。翻越结束后多久能开火**没测**。
2. 上滑索：`lower_onehanded` 0.49 s → `raise_onehanded` 约 0.35 s → 单手腰射（`ads_out_onehanded` 停住）；叠加层 0 换 `idle_onehanded`；`oneHandFraction` 按速率走到 1。下滑索：`switch_to_twohanded`。刚上绳开火有延迟：R-301 0.399 s、Wingman 0.523 s。滑索上可以换弹（`reload_onehanded`，2.40 s，和双手一样长）。
3. 钩爪：拉人时枪放下（`lower_onehanded` 约 1.45 s → `raise_onehanded` → `holster` 0.2 s → `raise` 0.5 s），这期间按换弹无效（§1.8）。
4. 跑墙（R5 关着，没有数据）：模型里有 `run_layer_wall`（循环 delta，0.2 / 0.2 s），推断是跑墙时放进叠加层的。HSD 做跑墙枪模时按 [设计]：主序列不换（不占手），叠加一层轻微侧倾，开镜收掉。**列为待研究**（TF2 跑墙时枪模怎么动没测过）。
5. 兴奋剂（Octane）：R-301 记到主序列 6 → 12，按序列表名字对不上，原因不明，不要照抄。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 翻越收枪 `holster` | — | 1.43 s | — | 跟翻越长度 | [实测] R-301 1 次 |
| 翻越后抬枪 `raise` | — | 0.50 s | — | = `raise_time`（1 次） | [实测] |
| 上滑索：放下 / 单手抬起 | — | 0.49 s / 约 0.35 s | — | — | [实测] |
| 刚上滑索第一发延迟 | — | 0.399 s（R-301）/ 0.523 s（Wingman） | — | — | [实测] 1 次 |
| 滑索上换弹 `reload_onehanded` | — | 2.40 s | — | = 双手 | [实测] |

#### 实现模板

```
// 动作是否占手，决定主序列
HANDS = { mantle: both, zipline: one, grapple_pull: both, wallrun: none, slide: none, jump: none }
onTraversalStart(kind):
    match HANDS[kind]:
        both: setMain(holster);   cancelFire(); reloadInterrupt(kind)   // §1.8
        one:  setMain(lower_onehanded) then raise_onehanded; oneHand = 1
        none: overlay(kind_layer) if exists
onTraversalEnd(kind): setMain(raise or switch_to_twohanded)
```

Unity 参考实现：**没有**。HSD 的占位枪在翻越、滑索、钩爪时没有收枪 / 单手动作（PR #65 只做了换弹、切枪、冲刺）。写进 `_notes` 和建议的 R5-DIFF。

#### 验收

- 没有测试（Unity 没做）。做的时候：翻越开始那一帧开火被打断；滑索上 0.4 s 内不开火；滑索上换弹 2.40 s 完成。
- 对照数据：MA §3 表、§13.2（PR #123）；SG §1、§4（PR #95）。

#### 出处

- MA §3（翻越、上滑索的序列）、§13.2（滑索 / 钩爪 × 换弹）、§13.7（`run_layer_wall`）。PR #123，还没合并
- SG §1 第 6 条、§4：翻越打断开枪、滑索第一发延迟。PR #95，还没合并
- CM §7：翻越结束后的抬枪没测。PR #95，还没合并

---

### 1.7 转视角时枪的超前

#### 原理

鼠标转得快的时候，枪身会朝**转动方向**多转一点（超前，不是滞后），停下后慢慢回正。这让转身有"手在甩"的感觉，又不影响准星（枪口位置是画面的事，子弹从眼睛出）。

HP 第一版写成"向转动反方向"，是错的；原始记录是向转动方向（Leader 11-03 更正）。

#### 规则和公式

1. 偏航超前 = clamp(转速 / 233 °/s, −1, 1) × 2.44°，方向同转动方向；只测了 233 °/s 一个转速，分不清是线性还是到了上限。
2. 用一阶跟随：停转后回到 10 % 约 0.4–0.8 s（枪口量），对应时间常数约 0.26 s [算，HSD 拟合]。
3. 枪口位移由枪长带出（Kraber ±2.5 u、R-301 ±1.3 u、P2020 ±0.45 u），不单独算。
4. 俯仰方向（抬头低头）**没测**，HSD 暂不做 [设计]。
5. 和腰射枪身角度（§1.2）、走路晃动相加。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 偏航超前（233 °/s 时） | — | 2.44° | — | 绝大多数枪相同；Sheila 0.9°；Spitfire 左右 1.89 / 2.88 | [实测] 全部枪各 2 次 |
| 测量转速 | — | 233 °/s | — | 只有这一档 | [实测] |
| 停转回到 10 % | — | 0.4–0.8 s | — | 短枪更久（噪声） | [实测] |
| 跟随时间常数（HSD） | — | 0.26 s | — | — | [算] 由回到 10 % 拟合 |
| R-301 枪口左右 | ±0.033 m | ±1.3 u | ±0.018 H | Kraber ±2.5 u | [实测] |

#### 实现模板

```
// 单位：°、s
turnLead(dt, yawRate):          // yawRate 左为正
    wanted = clamp(yawRate / 233, -1, 1) * 2.44
    lead  += (wanted - lead) * (1 - exp(-dt / 0.26))
    angles.yaw += lead
```

Unity 参考实现：`HoldBlend.Step` 末尾（`HoldData.TurnRate` 233、`TurnLead`、`TurnSettle` 0.26），`HeldModelView.Update` 从镜头偏航差算 `rate`。分支 `combat/wp4-reload-swap`。

#### 验收

- `CombatHoldPoseTests.TheGunLeadsATurn`。
- 对照数据：HP `HP-TURN.tsv`（PR #95）。合格线：233 °/s 稳定时超前 2.44 ± 0.2°；停转 0.6 s 时 < 15 % [设计]。
- 多转速和俯仰：B08-2（99-TODO），做完后改第 1、4 条。

#### 出处

- HP §7（含 Leader 11-03 更正）：转视角超前。PR #95，还没合并
- 99-TODO B08-2。handbook/base

---

### 1.8 手是资源：移动中换弹、谁能切掉换弹

#### 原理

换弹占着手，直到"解锁"那一刻（子弹已装好，能开枪、能开镜）。解锁之后剩下的那一小段动画只是收尾，**谁要手谁就能立刻切掉它**（开火、开镜、冲刺）。不用手的动作（跳、滑铲）**从不**打断换弹；要手的移动（滑索一只手、钩爪两只手）会把枪放下，解锁前被切的，回来后用一段"后半截"动画补完。

换弹不减速；走路换弹就是"换弹动画 + 走路晃动"直接相加，没有"走路换弹"专门的动画。所以玩家的操作永远优先于动画播完（MA §8 第 3、4 条）。

#### 规则和公式

1. 换弹三个时刻（从换弹开始算）：**加弹**（弹匣数变化）、**解锁**、**动画结束**（= `reload_time` / `reloadempty_time`，动画匀速播放）。每把枪不同，没有通用比例；解锁以 RM `RM-SUMMARY.tsv` 为准（D-118；CM 表里"解锁"两列作废）。
2. 谁能切掉换弹动画：

   | 换弹中 | 解锁前 | 解锁后 |
   |---|---|---|
   | 冲刺 | 不切，边换边跑（手是换弹姿势）；**解锁那一刻**切到冲刺循环 | 立刻切 |
   | 开镜 | 不切，解锁后才开镜 | 立刻切到开镜 |
   | 开火 | 等到解锁那一刻才打 | 立刻切，开枪 |
   | 跳、滑铲 | 不切 | 不切，播完 |
   | 换枪、近战 | 切；加弹前切就没加上 | 切，弹药保留 |
   | 上滑索、开钩爪 | 切（放下枪）；放回后自动用 `reload_late1` 补完（比完整短约 0.6 s） | 切，不补（已装好） |
   | 钩爪拉人时按换弹 | 无效 | — |

3. 换弹开始时正在冲刺：立刻进换弹序列。
4. 移动中换弹的枪模 = 换弹主序列 + 程序层（走路晃动、蹲的侧翻等照常相加）；冲刺姿势被换弹换掉（§1.4 第 6 条）。换弹期间叠加层 0 关着。
5. 换弹动作本身不是匀速的：起手甩枪 → 歪着枪操作弹匣（最大倾斜约 76°，在全程 38–40 % 处）→ 加弹同时快速回正 → 解锁后轻轻落定。最快的 20 % 时间走完近一半的路；角速度峰值是中位数的 4–5 倍。**不要匀速插值姿势**，按 RM 的逐帧表查。
6. 弹药规则（加弹前被切就没加上、开火等解锁）以 09 章为准，这里只写手的占用。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 战术：加弹 / 解锁 / 结束 | — | 1.39 / 1.64 / 2.40 s | — | 各枪见 RM-SUMMARY | [实测] |
| 解锁在全程的位置 | — | 战术中位 87 %，空仓 90 % | — | — | [实测] 26 把 |
| 加弹在全程的位置 | — | 战术中位 63 %（51–79 %），空仓 74 % | — | — | [实测] |
| 解锁前开火的等待 | — | 第一发在解锁 +0.01 s | — | — | [实测] R-301 / Spitfire |
| `reload_late1` 比完整短 | — | 约 0.6 s（R-301 1.80 对 2.40 s） | — | — | [实测] |
| 换弹最大倾斜 | — | 约 76°（33–118°） | — | 每把枪不同 | [实测] |
| 解锁后收尾 | 0.076 m | 约 0.25–0.30 s，枪口离原位约 3 u | 0.042 H | — | [实测] |
| 换弹时移动速度 | 4.41 / 6.60 m/s | 走 173.5 / 冲刺 260 u/s，不减速 | 2.41 / 3.61 H/s | — | [实测] |

#### 实现模板

```
// 手的占用：一个优先级规则代替组合动画
handsBusy(now) = reload.active and now < reload.unlockAt
onWants(action):           // action ∈ {fire, ads, sprintPose, swap, melee, zipline, grapple}
    if not reload.active: do(action); return
    if action in {swap, melee}: cutReload(keepAmmo = now >= reload.ammoAt); do(action)
    elif action in {zipline, grapple}:
        cutReload(); if now < reload.unlockAt: pending = reloadLate1   // 手空出来后补
        do(action)
    elif handsBusy(now): queue(action)          // fire / ads / sprintPose 等到解锁
    else: cutReload(); do(action)               // 解锁后立刻切
// jump / slide 不在列表里：从不打断
```

Unity 参考实现：`ArsenalWeapon.cs`（`ReloadLocked`、`reloadUntil`、开关 `reloadMoments`：解锁后冲刺切掉换弹那一行注释 `[R5] MOVE…`）；`HeldMotion.Of` / `HeldMotion.Reload`（换弹走 RM 逐帧表，`ReloadTable`，绕枪口转）；`HeldModelView.Update`（被切断时 `cutOffset` 接住）。分支 `combat/wp4-reload-swap`（6ec7285，D-118 的单时钟表）。**没做**：滑索 / 钩爪打断换弹和 `reload_late1` 补完（HSD 的滑索、钩爪不放枪，§1.6）。

#### 验收

- `CombatReloadSwapTests.AReloadHasThreeMomentsPerGun`、`HoldingFireWaitsForTheUnlockThenCutsTheAnimation`、`AimingWaitsForTheUnlock`、`SprintAndJumpDoNotBreakAReload`、`APunchBeforeTheAmmoMomentLosesItAndAfterKeepsIt`、`ASwapBeforeTheAmmoMomentLosesTheReload`、`TheGunFollowsR5sReloadInBurstsNotAtAnEvenPace`、`EveryMeasuredGunHasItsReloadAsItMoved`、`TheOldReloadStaysBehindItsSwitch`。
- 对照数据：RM `RM-SUMMARY.tsv`、`tables/<枪>_<tac|emp>.tsv`（PR #95）；MA `C1-RELOAD.tsv`（PR #123）。
- 合格线：三个时刻和 RM 差 < 0.02 s；最快 20 % 时间走完的路程占比 ≥ 40 % [设计，R5 中位 45 %]。
- 要补：滑索 / 钩爪打断（做了 §1.6 再加）。

#### 出处

- MA §5、§13.2：谁能切掉换弹、滑索 / 钩爪 × 换弹、`reload_late1`。PR #123，还没合并
- CM §1–§3：三个时刻、打断表、换弹不减速。PR #95，还没合并（解锁列作废）
- RM 全文：换弹节奏、解锁时刻。PR #95，还没合并
- D-118（PR #91，还没合并）：解锁用 RM 的单时钟表。
- `R5-DIFF-ARCHIVE.md`：换弹 / 切枪的差别**还没写进去**（MA §9），见 `_notes`。

---

### 1.9 切枪、冲刺到开火、近战

#### 原理

切枪分两段：先把旧枪收下去（`holster_time`），再把新枪掏上来（`deploy_time`）。**新枪不用等掏完就能开火**：枪快到位就能打。收枪先慢后快（越来越快往下掉），掏枪先快后慢（一下甩上来再小幅过冲稳住），所以切枪有"甩"的节奏。

冲刺时枪是放下的，按开火要先抬起来，所以冲刺到开火有 0.14–0.25 s 延迟；滑铲时枪本来就是端着的，几乎没有延迟——这是"滑铲开火"比"冲刺开火"快的原因。

#### 规则和公式

1. 切枪：收枪走旧枪 `holster_time`，再走新枪 `deploy_time`；第一次拿到这把枪走 `deployfirst_time`（更长）。开火中切枪：立刻停火开始收枪。
2. 新枪能开火的时刻在掏枪的 50–90 % 处（每个方向 1 次，比例不固定）；那时枪口已回到离静止位置 4 u 以内。
3. 收枪曲线：前 10–20 % 几乎不动，之后越来越快，结束时还在往下；掏枪：开始离得最远，前 30 % 走掉大半，50 % 时基本到位，之后小幅过冲（R-301 3–4 u）。曲线查 DS §3 表。
4. 冲刺到开火：按开火立刻结束冲刺（速度从 260 掉到 174），到第一发 0.14–0.25 s（按枪），`sprintraise` 不播完，第一发一出就被切掉。延迟的来源没查清（不是 `raise_time` 的比例）。
5. 滑铲到开火：0.013 s（等于站立的基础延迟，一帧半）。冲刺到开镜：开镜比例 0.02 s 内开始变化。
6. 近战：按键后 0.367 s 最早能开枪；不开枪约 0.98 s 回到枪。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| R-301 收枪 / 掏枪 / 第一次掏枪 | — | 0.55 / 0.6 / 1.1 s | — | 全部枪见 DS §1 | [数据] [实测] |
| 能开火在掏枪的 | — | 50–90 % | — | 每方向 1 次 | [实测] |
| R-301 收枪枪口走的距离 | 0.744 m | 29.3 u | 0.407 H | Kraber 85.6 u | [实测] |
| R-301 掏枪最快速度 / 在第几成 | 6.30 m/s / — | 248 u/s / 4 % | 3.44 H/s | 掏枪峰值在 4–40 % | [实测] |
| 冲刺到第一发 | — | 0.138–0.249 s | — | R-301 0.247、Wingman 0.180、P2020 0.138 | [实测] 各 3 次 |
| 第一发时的速度（冲刺开火） | 4.42 m/s | 174 u/s | 2.42 H/s | — | [实测] |
| 滑铲到第一发 / 站立基础延迟 | — | 0.013 s | — | — | [实测] |
| 近战后最早开枪 / 回到枪 | — | 0.367 s / 约 0.98 s | — | 3 把枪相同 | [实测] |

#### 实现模板

```
// 单位：s
swap(old, new):
    lower(old, old.holsterTime, curve = HOLSTER)   // 先慢后快
    raise(new, first ? new.deployFirst : new.deployTime, curve = DEPLOY)  // 先快后慢 + 过冲
    canFireAt = raiseStart + k * new.deployTime    // k = 0.5–0.9，按枪；没测的枪 k = 0.5 [设计]
sprintToFire(): endSprint(); raiseFromSprint(gun.sprintRaiseDelay)   // 0.14–0.25 s 查表
```

Unity 参考实现：`ArsenalWeapon.cs`（`swapHolster` 开关：先收后掏、`deployedAt`、每把枪保留自己的弹匣、第一次掏枪更长）；`HeldMotion.Of`（`lowered` 一个比例，收枪的枪动 `swapOffset` / `swapTurn` 是 [guess]，没按 DS §3 的曲线）。冲刺到开火的抬枪延迟 HSD 用 `lowered`，形状 [guess]。分支 `combat/wp4-reload-swap`。

#### 验收

- `CombatReloadSwapTests.ASwapHolstersTheOldGunThenDrawsTheNew`、`EachGunKeepsItsOwnMagazineAndAFirstDrawIsLonger`、`TheGunGoesDownInTheHolsterAndComesUpByTheReadyMoment`、`TheOldSwapStaysBehindItsSwitch`。
- 要补：收枪 / 掏枪枪口距离曲线和 DS §3 表每 10 % 差 < 3 u [设计]；冲刺到开火延迟按枪查表。
- 对照数据：CM `C-SWITCH.tsv`、`C-RAISE.tsv`、`C-MELEE.tsv`（PR #95）。

#### 出处

- DS §1–§6：每把枪时长、收枪掏枪曲线、切枪后多久开火、冲刺 / 滑铲到开火、近战。PR #95，还没合并
- CM §5–§7。PR #95，还没合并
- MA §5.3：冲刺结束序列不会播完。PR #123，还没合并

---

### 1.10 开镜时的压制

#### 原理

越需要瞄准，程序运动越少。开镜走路时枪几乎不动，准星区域稳定，这是"开镜就准"的手感来源之一（MA §8 第 6 条）。压制的是**程序层和叠加层**（走路晃动、蹲的下移、持枪姿势差），开镜动画本身（枪移到瞄具、FOV）在 09 章。

#### 规则和公式

1. 开镜比例 zf（0 腰射 → 1 开镜）。程序层和持枪姿势差的权重 = 1 − zf。
2. 开镜走路（zf = 1）实测：位置 ≤ 0.02 u、角度 ≤ 0.12°（所有枪）；R-301 留约 ±0.22° 横滚（武器字段 `bob_roll_zoomed` 0.25 的枪），Wingman 约 0。HSD 按"全部收掉"做，R-301 那点横滚不做 [设计]。
3. 下蹲时枪下移那一项（`viewmodelDuckOffset × sin(crouchFraction · π/2)`）随 zf 在 `zoom_scope_frac_start` 之前线性淡出 [反编译]。
4. 换弹动作的姿势也乘 1 − zf（开镜中换弹的少数情况）[设计，HSD]。
5. 开镜腰射之间的枪身横滚：R5 读不到过程，Unity 按开镜进度线性退掉 [推断]（DP §7.11）。
6. 开镜不在地面时后坐变大（× `viewkick_air_scale_ads`）——那是后坐，09 章。

| 量 | [m] | R5 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 开镜走路：位置晃动 | ≤ 0.0005 m | ≤ 0.02 u | — | 所有枪 | [实测] |
| 开镜走路：角度晃动 | — | ≤ 0.12°（R-301 横滚 ±0.22°） | — | Wingman ±0.007° | [实测] |
| 程序层权重 | — | 1 − zf | — | — | [设计]（R5 读不到权重曲线，B08-3） |

#### 实现模板

```
adsMask(zf) = 1 - zf
gun = adsCurve(zf)(09 章) + adsMask(zf) * (holdDelta + walkSwing + sprintWave + landing + turnLead + reloadPose)
```

Unity 参考实现：`HeldModelView.Update` 的 `weight = (1 − zoom) × (1 − reloadShare)`；`HeldMotion.Of` 的 `weight = 1 − zoom`（换弹）。分支 `combat/wp4-reload-swap`。

#### 验收

- `CombatReloadSwapTests.OnlyAnEmptyReloadWorksTheBoltAndAimingTakesTheMotionAway`。
- 要补：zf = 1 走路 2 s，枪口位置变化 ≤ 0.05 u、角度 ≤ 0.15° [设计]。
- 对照数据：MA §4.3、§13.3（PR #123）。

#### 出处

- MA §4.3（含 11-13 更正）、§12.1（0x14085bdb0 是下蹲下移，不是走路晃动淡出）、§13.3。PR #123，还没合并
- DP §7.11：开镜过程的横滚线性退掉 [推断]。main

---

## 2. 泰坦：身体

**先说两条路。** TF2 的泰坦身体是"美术片段 + 薄程序层"：身体动作几乎全是做好的循环片段，程序只做五件事——按移动方向在 3 个片段之间混合、按速度调播放快慢、把瞄准姿势叠在上面、脚落地时 IK 贴地、腿落后视线 60° 才转过去。HSD 现在反过来：泰坦模型没有蒙皮骨架，身体全靠程序生成（关键姿势表 + 脚 IK + 弹簧，D-98、D-127），默认走法是 **B-沉**（D-136）。

手册两条都写：**规则**按 TF2（不管用哪条路都该满足），**HSD 现在的做法**写在每项的"实现模板"里，和 TF2 不同的地方标出来。泰坦的身体在第一人称里看不见（驾驶舱里看不到自己的腿），只在第三人称和别人眼里看得见。

### 2.1 步态选择和换步态的混合

#### 原理

泰坦按速度在"走、跑、冲刺"之间换片段，换的时候不硬切，而是旧姿势按 smoothstep 淡掉。混合时长取两段动画各自时长里**短的那个**，所以起步、停步都只有 0.2 s，走和跑之间是 0.55 s。从按键到身体完全进入跑约 0.6 s，这是"身体比速度慢半拍"的主要来源之一（另一半是 §2.2 的死区）。

#### 规则和公式

1. 每次更新按水平速度 v 选（没有滞回）：

   ```
   v ≤ 0.5 u/s           → 待机
   冲刺状态开着          → 冲刺（不看速度；按键后 0.06–0.08 s 换上）
   v ≥ 0.45 × 站姿速度   → 跑
   否则                  → 走
   v > 1.05 × 冲刺速度（后退时 1.05 × 站姿速度）→ dash 姿势（SLIDE）
   ```

   **推论：中型泰坦满速 250 u/s 走路时播的是跑片段，不是走片段。**
2. 换序列的混合：T = min(旧序列混出, 新序列混入)，旧姿势权重 smoothstep（同 §1.1 第 4 条）。混合从"在动"变"不在动"（v ≤ 0.5 u/s）那一刻开始。
3. 方向：移动方向相对视线 |d| ≤ 90° 用前进组，否则后退组，10° 滞回；泰坦不用四向片段（`quadMoveAnims 0`），横移也是前进组，靠 `move_yaw` 在 3 个片段（右 / 中 / 左）间线性插值。
4. 混合时长（附件 `titan-blend-times.tsv`）：

   | 换法 | 时长 | 由谁定（旧混出 / 新混入） |
   |---|---|---|
   | 待机 → 走 / 跑（起步） | 0.2 s | 0.2 / 0.95 |
   | 走 / 跑 → 待机（停步） | 0.2 s | 0.55 / 0.2 |
   | 走 ↔ 跑 | 0.55 s | 0.55 / 0.95 |
   | 走 / 跑 → 冲刺 | 0.55 s（轻、重 0.2 s） | 0.55 / 0.95（轻、重 0.2） |
   | 待机 → 冲刺 | 0.2 s | 0.2 / 0.95 |
   | 冲刺 → 走 / 跑 | 0.2 s | 0.2 / 0.95 |
   | → dash | 0.15 s | — / 0.15 |
   | dash → 走 / 跑 | 0.95 s | 0.95 / 0.95 |

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 待机门槛 | 0.0127 m/s | 0.5 u/s | — | — | [TF2 反编译] |
| 走 → 跑门槛系数 | — | 0.45 × 站姿速度 | — | — | [TF2 反编译] [TF2 实测] |
| 中型走 → 跑门槛 | 2.858 m/s | 112.5 u/s | 0.479 H_t/s | 实测在 110.8 和 112.7 之间 | [TF2 实测] |
| 重型 / 轻型门槛 | 2.400 / 3.086 m/s | 94.5 / 121.5 u/s | 0.402 / 0.517 H_t/s | 没实测 | [TF2 反编译] |
| 中型站姿 / 冲刺速度 | 6.35 / 9.652 m/s | 250 / 380 u/s | 1.064 / 1.617 H_t/s | 轻 270 / 400，重 210 / 310 | [TF2 数据] |
| 起步 / 停步混合 | — | 0.2 s | — | 实测 0.189–0.208 s（32 次停步） | [TF2 实测] |
| 走 ↔ 跑、跑 → 冲刺混合 | — | 0.55 s | — | 实测 0.557–0.64 s | [TF2 实测] |
| 冲刺 → 跑混合 | — | 0.2 s | — | 实测 0.208–0.215 s | [TF2 实测] |
| 方向滞回 | — | 10° | — | — | [TF2 反编译] |

#### 实现模板

```
// 单位：u、s
selectGait(v, sprinting, standSpeed, sprintSpeed, backward):
    if v <= 0.5: return Idle
    if v > 1.05 * (backward ? standSpeed : sprintSpeed): return DashPose
    if sprinting: return Sprint
    return v >= 0.45 * standSpeed ? Run : Walk
onGaitChange(old, new): pushTransition(old, T = min(old.fadeOut, new.fadeIn))   // smoothstep
```

**HSD 现在**：没有片段，用"每种步态一张关键姿势表"（`TitanWalkKeyPoses`：`TitanKeyGait` walk / walk_heavy / run / sprint），步态权重用一阶跟随 `moveW = Follow(moveW, target, τ = 0.22 s 起步 / 0.14 s 停步)`（`TitanBodyCore`，约 965 行），不是 TF2 的 0.2 s smoothstep；电机没有稳定的"跑"（走 250、冲刺 380），跑权重随速度混。和 TF2 的差别写进 `_notes`。分支 `titan/integration`（PR #78，还没合并）。

#### 验收

- TF2 规则的验收（HSD 做片段路线时）：停步时身体离待机姿势的距离 D(t)/D(0) 对 0.2 s smoothstep 的 RMS ≤ 0.1（TF2 实测 0.084）[TF2 实测]；起步到 ≥ 125 u/s 时，按键到身体完全进入跑 0.58–0.64 s。
- HSD 现在：`TitanAnimTests.StepsAreBoundToSpeed`、`TheThreeWalksAreMeasured`、`TheWalkStyleStartsAsBHeavy`、`NoWalkStyleChangesTheSim`。
- 停步回弹 0（§2.8）。

#### 出处

- RN §3、§4：走跑门槛、SLIDE、混合 = min(旧, 新)。main
- RG §2、§3：门槛和混合实测（32 次停步）。main
- TAF §1.1、§1.2、§2.1–§2.6（以"11-09 补测"行为准）。main
- [TF2 反编译] server.dll：选活动 0x1805ee970、换序列淡出时间 0x1802013d0、淡出队列 0x180200590、权重 0x180200460、每帧更新 0x1805ef770；活动号 RUN 0x19e、WALK 0x1a8、SPRINT 0x1bd、SLIDE 0x1bf。

---

### 2.2 播放速度和步频

#### 原理

腿的动作快慢跟着实际速度：播放速度 = 速度 ÷ 片段自带的地速，这样脚基本不滑。但 TF2 有一个 0.15 的**死区**：只有算出来的值和当前值差超过 0.15 才改，所以匀速走时播放速度停在"加速过程中最后一次改写的值"，比目标慢最多 0.14，脚会滑一点（最多约 40 u/s）。这个"跟不太上"也是慢半拍的感觉。

"重"不是靠步子短（TF2 重型和中型用同一套走路片段）。

#### 规则和公式

1. 目标 = clamp(v_h ÷ 地速(当前片段), 0.25, 10)；冲刺再 ≤ 1.25。斜向时地速乘 |sin(move_yaw)| + |cos(move_yaw)|。
2. 只有 |目标 − 当前| > 0.15 才把当前改成目标；起步时当前从 1.0 开始；停下（v ≤ 0.5）置 1.0。
3. 脚滑速度 = |v − 播放速度 × 地速|，实测和这个式子差 ±3 u/s。
4. 片段：

   | 片段（中型） | 周期 | 地速 | 一步（半周期）距离 | 踩实相位 右 / 左 |
   |---|---|---|---|---|
   | 走 `a_WalkForward*` | 1.133 s | 246.1 u/s | 139.5 u | 0.294 / 0.765 |
   | 跑 `a_RunForward*` | 1.067 s | 311.6 u/s | — | 0.312 / 0.812 |
   | 冲刺 `a_combat_sprint*` | 0.833 s | 437.6 u/s | — | 0.24 / 0.72 |
   | 后退走 | 1.8 s | 87 u/s | — | 0.185 / 0.685 |
   | 后退跑 | 0.8 s | 282 u/s | — | — |
   | 轻型走 = 跑 | 1.0 s | 274 u/s | — | — |

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 播放速度下限 / 上限 / 冲刺上限 | — | 0.25 / 10 / 1.25（×） | — | — | [TF2 反编译] ConVar |
| 死区 | — | 0.15（×） | — | 31 段匀速全部在内 | [TF2 反编译] [TF2 实测] |
| 走片段地速 | 6.251 m/s | 246.1 u/s | 1.047 H_t/s | — | [TF2 数据] |
| 跑片段地速 | 7.915 m/s | 311.6 u/s | 1.326 H_t/s | — | [TF2 数据] |
| 冲刺片段地速 | 11.115 m/s | 437.6 u/s | 1.862 H_t/s | 轻 466、重 441 | [TF2 数据] |
| 走一步距离 | 3.543 m | 139.5 u | 0.594 H_t | 约 1.2 倍髋高 117 u | [TF2 数据] |
| 250 u/s 实际周期（跑片段） | — | 1.35–1.60 s（中位 1.37） | — | 6 次 | [TF2 实测] |
| 最大脚滑 | 1.016 m/s | 约 40 u/s | 0.170 H_t/s | 冲刺 75–84 u/s（提早解锁） | [TF2 实测] |
| 播放速度停在下限的速度（走） | 1.562 m/s | 61.5 u/s | 0.262 H_t/s | — | [算] 0.25 × 246.1 |

#### 实现模板

```
// 单位：u、s
updateRate(v, clip, sprint):
    if v <= 0.5: rate = 1; return
    gs = clip.groundSpeed * (|sin(moveYaw)| + |cos(moveYaw)|)
    target = clamp(v / gs, 0.25, 10); if sprint: target = min(target, 1.25)
    if |target - rate| > 0.15: rate = target
phase += rate * dt / clip.period
```

想脚不滑可以把死区改小，但那就不是 TF2 了（RG §1 "照做"）。

**HSD 现在**：没有片段，步伐时钟**按走过的距离**推进（等效于"播放速度 = v ÷ 地速"且没有死区，所以 HSD 不会因死区滑脚）；一步距离 B-沉 105 u（B 138.3 u = TF2 走），周期由 `cycle = clamp(速度 × basePeriod, 2.4 m, 2 × stride)` 换算（`TitanBodyCore`，`KeyPoseMinCycle` 2.4 m、`KeyPoseMaxPeriod` 1.45 s）。B-沉 一步 0.420 s，比 TF2 的 0.57 s 快约 35 %：这是 D-136 用户选的 [设计]，和 TF2 不同。分支 `titan/integration`。

#### 验收

- TF2 规则（片段路线）：250 u/s 匀速直走周期 1.35–1.60 s；50 / 75 u/s 停在下限 0.25；160 u/s 从下面加速上来播放 0.424、从 250 减下来 0.600（历史决定停在哪）。数据 RG `out/f6_segments.tsv`。main
- HSD 现在：`TitanAnimTests.StepsAreBoundToSpeed`、`KeyPoseStepsFollowTheGroundNotTheClock`、`PlantedFeetBarelySlide`；脚滑合格线（走路路线）≤ 2 × 平地（中型 9.9、重型 2.2 m / 100 m，C1 的线）。
- F1 约束（TAF §4.2）：250 u/s 下走路一步 0.55–0.6 s。**HSD B-沉 不满足**（0.420 s），是有意的（D-136），写成偏离。

#### 出处

- RN §5：播放速度公式、0.15 台阶、斜向乘 |sin|+|cos|（[TF2 反编译] 0x1805eb300）。main
- RG §1：31 段匀速实测、脚滑式子。main
- TAF §2.1–§2.3、§3 F1。main
- D-127、D-136：B / B-沉 一步距离和周期。PR #98，还没合并

---

### 2.3 腿的朝向：落后 60°、400 °/s、整步跳

#### 原理

泰坦原地转视角时，上身先跟着视线转，腿不动；视线和腿差到 60° 才迈一步，一步正好转 60°，两只脚一起动。停下后腿可以就留在偏 30–40° 的地方，不再修正。这让泰坦转身"有分量"：小幅瞄准不带动全身，大幅转身才一步一步挪。

#### 规则和公式

1. 站着：视线和腿目标差 ≤ 60°，腿不动。
2. 差超过 60° 时，腿目标朝视线方向**整跳 60°**（差 ≥ 120° 就跳 120°，依此类推）。
3. 腿追目标的角速度 = 400 × min(1, 剩余角度 / 60) °/s，最低 4 °/s。差 60° 以内就是时间常数 τ = 60 / 400 = 0.15 s 的指数收敛：一步走完 90 % 要 0.32 s，95 % 要 0.42 s。
4. 腿不能落后视线超过瞄准层的 `aim_yaw` 范围（中型 ±90°）；转太快时腿被硬拖着走。
5. 一动起来（v > 0.5 u/s），腿目标就是视线（或移动方向，§2.4），追法同第 3 条。
6. 上身跟视线是瞄准姿势参数的平滑：胸落后视线 15 °/s 时 1.5–2°，180 °/s 时 20°，300 °/s 时 27°（中型）；轻 / 重 300 °/s 时 20.7° / 40°。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 身体落后视线上限 `mp_maxbodyyaw` | — | 60° | — | — | [TF2 反编译] [TF2 实测] |
| 腿追视线峰值 `mp_bodyyawrate` | — | 400 °/s | — | — | [TF2 反编译] |
| 收敛时间常数 | — | 0.15 s | — | — | [算] |
| 一步走完 90 % / 95 % | — | 0.32 / 0.42 s | — | 实测一步 0.33–0.5 s | [算] [TF2 实测] |
| 最低追速 | — | 4 °/s | — | — | [TF2 反编译] |
| 中型 `aim_yaw` 范围 | — | ±90° | — | 轻 / 重不同 | [TF2 数据] |
| 胸落后视线（300 °/s，中型） | — | 27° | — | 轻 20.7°、重 40° | [TF2 实测] |

#### 实现模板

```
// 单位：°、s
feetYaw(dt, view, moving):
    if moving: target = view          // 或移动方向，§2.4
    else:
        d = wrap(view - target)
        if |d| > 60: target += sign(d) * 60 * floor(|d| / 60)
    r = wrap(target - feet)
    rate = max(4, 400 * min(1, |r| / 60))
    feet += sign(r) * min(|r|, rate * dt)
    feet = clampBehind(view, feet, aimYawRange)   // ±90
```

**HSD 现在**：照做了"60° 才迈、每步 60°"，迈步用固定 `TurnStepTime` 0.42 s 的两脚摆动（左脚先、右脚晚 0.04 s），不是指数收敛（`TitanBodyCore.StartTurnSteps`，约 1100 行）。时长和 TF2 的 95 % 点一致。分支 `titan/integration`。

#### 验收

- `TitanAnimTests.LegsWaitUntil60DegreesThenStep`、`TheChestFollowsTheViewWhileTheLegsStay`。
- TF2 对照（RN §2.3，60 Hz 积分）：30° 以 30 °/s 转，腿不动、最后落后 30°；90° 以 90 °/s 转，最大落后 60°，停后腿留在偏 30°；一步正好 60°。

#### 出处

- RN §2：腿朝向规则、和实测对照（[TF2 反编译] 腿朝向 0x1805ebab0、收敛 0x1805ec620）。main
- TAF §2.4、§3 F9；TPC §3.2；GAPS §8（PR #98）。

---

### 2.4 横移、后退、边走边转

#### 原理

泰坦横移不走"螃蟹步"：腿和骨盆转向移动方向，胸靠瞄准层转回视线，腰扭到 ±85°。所以腰的扭转范围是关键约束，不够就只能做螃蟹步。后退走是动作最大的步态（骨盆扭 63°）。

#### 规则和公式

1. 移动时腿的朝向跟**移动方向**（前进组 ±90° 内），胸跟视线；中间的差由腰扭吃掉。
2. 腰扭范围至少 ±85°（D-92：±90° 限位、±85° 要求无碰撞）。
3. 后退（移动方向在后半圈）用后退组片段；泰坦后退和前进一样快（`speedScaleBack` 1.0），全速后退用后退跑。
4. 后退、横移时第一人称镜头不旋转（§3.1）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 横移时腰扭 | — | ±85°（TF2 移动中 −86 … 88°） | — | HSD 限位 ±90° | [TF2 数据] D-92 |
| 后退走骨盆 / 胸扭转 | — | 63° / 38° | — | — | [TF2 数据] |
| 前进组 / 后退组分界 | — | 90°，滞回 10° | — | — | [TF2 反编译] |

#### 实现模板

```
legsYaw  = moving ? moveDir : feetYaw(§2.3)
chestYaw = view
waistYaw = clamp(wrap(chestYaw - legsYaw), -90, 90)   // 要求 ±85 无碰撞
group    = |wrap(moveDir - view)| <= 90 (±10 滞回) ? Forward : Backward
```

Unity 参考实现：`TitanBodyCore`（腰扭范围按 D-92；`Backward` 姿势表）；测试 `TitanAnimTests.StrafingPointsTheLegsAlongTheWay`、`NoJointLeavesItsRangeInAnyState`、`TheUpperBodyIsNotAskedPastItsRange`。分支 `titan/integration`。

#### 验收

- 上面三个测试。横移 250 u/s 时腰扭 ≥ 80°、无碰撞 [设计]。

#### 出处

- TAF §2.5、§3 F10；TPC §2.2；D-92（PR #98，还没合并）；RN §3.3。main

---

### 2.5 脚踩地和 IK（只在画出来时做）

#### 原理

每个移动片段里标好每只脚什么时候踩实。踩实时脚锁在世界坐标里（不滑），骨盆按地面高度修正。**骨盆最低点正好在脚踩实那一刻**，脚步声早约 0.07 s——"顿挫"不是曲线形状做出来的，而是脚、骨盆、声音在同一刻发生。

TF2 的脚 IK **只在身体被画出来时做**：第三人称和别人眼里的泰坦脚贴地；第一人称下自己的身体每 7 帧才摆一次姿势、不做 IK（反正看不到）。

#### 规则和公式

1. 片段标三样：根运动地速（算播放速度用）、每只脚的踩实窗口（开始、满权重、放开、结束、踩实相位）、脚步事件相位。
2. 中型走：右脚满权重 0.294–0.588，左脚 0.765–下一周期 0.206（不对称：持枪的右侧前倾，右脚支撑短 [推断]）；踩实相位右 0.294、左 0.765；脚步事件右 0.235、左 0.647（比踩实早约 0.06 周期 = 0.067 s）。冲刺两者重合（0.24 / 0.72）。
3. 冲刺片段另有"提早解锁"规则：锁脚提早放开，脚可以滑一点换流畅。
4. dash、跳、上下机、弹射、处决：全程不做脚 IK。待机：两只脚整段踩实。
5. IK 参数：探测高度 50 u、脚半径 15 u；骨盆高度修正速度 2 × 步长 / s；脚掌转向地面法线 100 °/s（这条没能实测确认）。
6. 骨盆高度曲线：98 % 是纯二次谐波（每步一次），最低点放在踩实相位；不要靠腿长反推骨盆（会"一帧掉下去"）。
7. 第一人称可以不做脚 IK [TF2 实测]。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 骨盆起伏（走，峰峰） | 0.394 m | 15.5 u | 0.066 H_t | 跑 13.7 u | [TF2 数据] |
| 骨盆最低点相位 = 右脚踩实 | — | 0.294 | — | 误差 < 0.03 周期 | [TF2 数据] |
| 脚步事件早于踩实 | — | 0.067 s（0.06 周期） | — | 冲刺 0 | [TF2 数据] |
| IK 探测高度 / 脚半径 | 1.27 / 0.381 m | 50 / 15 u | 0.213 / 0.064 H_t | — | [TF2 数据] |
| 骨盆修正速度 `ik_height_adjust_speed` | — | 2.0 × 步长 / s | — | — | [TF2 反编译] ConVar |
| 脚掌转法线 `ik_normal_lerp_rate` | — | 100 °/s | — | 没实测确认 | [TF2 反编译] |
| 第一人称自己身体摆姿势的间隔 | — | 7 帧（约 0.049 s） | — | 交叉淡入时每帧 | [TF2 实测] |
| 两脚间距（中型待机） | 2.108 m | 83 u | 0.353 H_t | 轻 92、重 124 | [TF2 数据] |

#### 实现模板

```
// 单位：u、s
for foot in feet:
    w = clip.ikWeight(foot, phase)                 // 踩实窗口
    if w > 0 and rendered:                         // 第一人称可跳过
        if not foot.locked: foot.lockAt = groundUnder(foot)   // 探测 50 u
        foot.pos = lerp(animPos, foot.lockAt, w)
    else: foot.locked = false
pelvisZ += clamp(groundOffset - pelvisZ, ±2 * stride * dt)
onPhase(clip.footstepEvent): playStep()           // 比锁住早 0.07 s
```

**HSD 现在**：脚 IK 一直做（第一人称也算，因为模型同一套）；`TitanFoot`（`Mode.Planted / Swing / Free / Clip`）、`TitanFootstep`（`TitanStepKind`）；B-沉 的骨盆高度由关键姿势表给，"落脚后快落硬停"（D-127），最低点在落脚后（D-127 / D-136 的数据）。B-沉 的脚滑主要出在踝卡在 −35° 设计上限时（开关 `b_heavy_ankle`，待用户定，D-136）。分支 `titan/integration`。

#### 验收

- TAF §4.2 约束表（HSD 自己录像量）：骨盆最低点在脚锁住那一帧，误差 < 0.03 周期；骨盆高度一帧变化平滑无跳变；脚步声在脚接触那一帧。
- `TitanAnimTests.PlantedFeetBarelySlide`、`LegSolveReachesTheFootAndPointsIt`、`LocomotionCollisionsAreRare`、`TheHeavyAnkleSwitchStartsAtTheDesignRange`。
- 对照数据：TAF `anim/out/walkphase.csv`、`walkevents.csv`。main

#### 出处

- TAF §1.4、§1.2、§3 F4、F8。main
- RG §4：IK 只在画出来时做、7 帧刷新。main
- D-127、D-136（PR #98，还没合并）。
- [TF2 数据] MDL v53 animdesc `+0x24` IK 规则（+0x48 start、+0x4C peak、+0x50 tail、+0x54 end、+0x58 contact），TAF 附录 A。

---

### 2.6 地形适应：斜坡和台阶

#### 原理

泰坦踏上台阶是碰撞体一下迈上去，身体（骨盆、上身）用一个平滑把跳变吃掉，不跟着跳；站立的脚被 IK 放到台面上。斜坡上站立脚贴着坡面。TF2 9° 坡上水平速度不变（没有"爬坡减速"）。

HSD 的地形适应做到"占位版 v1"就收住了（用户 11-13：转去做设计，不再精调动画，D-187）。

#### 规则和公式

1. 台阶：碰撞体前沿碰到台阶一个 tick 内抬高（`stepheight` 80 u 以内都是迈步）；骨盆世界高度只升约 +2.5…+3.5 u，之后在走路起伏里慢慢追上（相对原点先低 8–12 u）。第一 / 第三人称一样，是渲染原点的平滑，不是 IK。
2. 斜坡：站立脚脚高随前后位置的斜率 ≤ ±0.045（贴地）；不贴地应是 −tan θ。
3. 上坡骨盆比平地低约 11 u、下坡约 2 u（两种视角一样，原因没查清，像身体落后于上升的原点）。HSD 要不要照做由自己定 [设计]。
4. 13° 以上的坡、最大坡度、脚掌转法线：**没测成**。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 泰坦台阶 `stepheight` | 2.032 m | 80 u | 0.340 H_t | — | [TF2 数据] |
| 实测台阶 | 0.279 m | 11 u（原点抬 10.6 u，一个 tick） | 0.047 H_t | — | [TF2 实测] |
| 迈上台阶后骨盆世界高度跳变 | 0.064–0.089 m | +2.5…+3.5 u | — | 第一 / 第三人称相同 | [TF2 实测] |
| 站立脚贴坡斜率 | — | ≤ ±0.045 | — | 9° 不贴地应 ±0.16–0.19 | [TF2 实测] |
| 上坡 / 下坡骨盆降低（9°） | 0.279 / 0.051 m | 约 11 / 2 u | 0.047 / 0.0085 H_t | 原因不明 | [TF2 实测] |
| 9° 坡上水平速度 | — | 不变（250 / 100 u/s） | — | 13°+ 没测 | [TF2 实测] |
| HSD 台阶镜头平滑 `stepSmoothTime` | — | 0.12 s | — | [placeholder] | [设计] |

#### 实现模板

```
// 单位：u、s
onRootStep(dz):                     // |dz| 每帧 ≥ 阈值才算台阶，斜坡不算
    bodySmoothOffset -= dz          // 身体不跟着跳
bodySmoothOffset = approach(bodySmoothOffset, 0, 每步起伏内吃掉)
plantedFoot.z = groundUnder(foot)   // 斜率 0
```

**HSD 现在**：C1 共用地形跟随（`TitanDims.TerrainSoleSmooth` 6、`TerrainContourTurn` 开），重型 / 轻型 / M-1 各自调过，D-187 "到此为止"：坡上悬空 10° 转身 0.23、30° 冲刺 0.21；短踏面插地；脚滑 4.6（目标约 1.2）等以后的落地规划。HSD 的台阶判断：只有每帧 |Δz| ≥ 0.12 m 才算台阶（斜坡约 0.06 m）。地形试验场 `Editor/TitanTerrainCourse.cs`（PR #77）。分支 `titan/integration`。

#### 验收

- C1 合格线（HSD 自己定，`README-terrain.md`）：站立脚 ≥ −2 cm / ≤ +3 cm，摆动脚 ≥ +5 cm，穿插 0；30° 坡和 80 u 台阶 −5 / +5 / 0 / ≤ 1 %；平地中型 48 / 48 逐字节不变。
- TF2 对照：9° 坡站立脚斜率 ≤ ±0.045（第三人称）。
- 已知没过线的项和原因见 D-187。

#### 出处

- RG §4、§6：坡、台阶实测。main
- TAF §3 F20；TFE §1 斜坡、台阶行（PR #118，还没合并）。
- D-187（PR #116，还没合并）；`hsd-terrain-c1` / 重型 / 轻型的 `README-terrain.md`（HSD-Unity PR #77 / #79–#81，#78 已包含）。

---

### 2.7 上身叠加层：开火、换弹、受击

#### 原理

上半身的动作（开火、换弹、挨打）都是叠加层，按骨骼权重**只作用于上身**：腿 0、骨盆 0–0.1、脊柱约 0.6、手臂 1、镜头骨 0。所以开火、换弹、挨打时腿照走、镜头不被身体带歪。挨打分两档：小伤害只抖上身，大伤害（护盾打空后的重武器）才全身踉跄，而且有 1 s 冷却——不要每一发都全身晃。

#### 规则和公式

1. 骨骼权重（每骨一个数）：

   | 层 | 腿 | 骨盆 | 脊柱 | 手臂 | 镜头骨 | 进 / 出 |
   |---|---|---|---|---|---|---|
   | 开火 | 0.06 | 0.10 | 0.57 | 1 | 0 | 0.2 / 0.2 s，每发重新触发 |
   | 换弹 | 0.06 | 0 | 0.47–0.64 | 1 | 0 | 0.2 / 0.2 s |
   | 小伤害抖动 | 0.06 | 0 | 0.60 | 1 | 0 | 0.2 / 0.2 s，1.27 s |

2. 换弹：3P 片段**整段快放，不截断**，倍数 = 片段长 ÷（换弹时间 + 0.2 s）；换弹结束时片段播到约 90 %，剩下的由 0.2 s 混出盖掉。
3. 小伤害抖动：单次伤害 ≥ 500（濒死扣血不算），按来向 4 档（每档 90°）。在服务端和自己第三人称身体上**都没看到**，可能只在别人眼里播（没测）。
4. 大伤害踉跄：玩家泰坦、护盾 0、单次 ≥ 1000、来自重武器名单、距上次 ≥ 1.0 s。主动作整个换成踉跄片段（站 / 走跑 / 冲刺 / 后退各自一组），播到片段尾减 0.2 s 再混出；播放倍数 ≈ 速度 ÷ 片段地速；**身体位置不动**（片段根运动不用）；正在踉跄时不重开。
5. 核心技能、换武器：不是加一个动作，而是用"标签"整套换掉移动和瞄准片段（状态 × 标签集合 → 片段）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 换弹快放倍数（Monarch） | — | 1.75–1.80 × | — | Tone 0.9–1.1 × | [TF2 实测] |
| 换弹结束时片段进度 | — | 约 90 %（89–91 %） | — | — | [TF2 实测] |
| 小抖动门槛 | — | 500 伤害 | — | — | [TF2 数据] |
| 踉跄门槛 / 冷却 | — | 1000 伤害 / 1.0 s | — | 护盾 0 才有 | [TF2 数据] [TF2 实测] |
| 踉跄时长（站 / 前进 / 冲刺 / 后退） | — | 3.38 / 2.95–3.04 / 1.94 / 1.04 s（+0.2 s 混出） | — | — | [TF2 实测] |
| 踉跄身体位移 | — | 0 | — | 片段根运动 171 u/s 不用 | [TF2 实测] |

#### 实现模板

```
gestureLayer.play(clip, boneMask = UPPER_MASK, fadeIn = 0.2, fadeOut = 0.2)
reloadGesture.rate = clip.length / (reloadTime + 0.2)
onDamage(d, src):
    if d >= 1000 and shield == 0 and src in HEAVY and now - lastStagger >= 1:
        setMain(staggerClipFor(gait)); lastStagger = now      // 不移动身体
    elif d >= 500: gestureLayer.play(flinch[dir4(src)])
```

Unity 参考实现：HSD 的炮、换弹手臂（D-111，`LendArm`）、受击身体（`TitanAnimTests.HitsMoveTheBodyAndSettle`、`ALentArmTakesTheGivenAnglesAndComesBack`）是程序做的；骨骼权重那套没有（没有骨架动画）。分支 `titan/integration`。

#### 验收

- `TitanAnimTests.HitsMoveTheBodyAndSettle`、`ALentArmTakesTheGivenAnglesAndComesBack`、`FromTheCockpitTheCannonStaysWhereItWasAndTheClawShows`。
- 规则验收：开火 / 换弹时腿的轨迹和不开火时差 < 1 cm、镜头差 0 [设计]；踉跄 1 s 内不重开；挨打时身体速度不变。

#### 出处

- TAF §2.10–§2.13、§3 F16、F17。main
- RU §2.1–§2.3：换弹快放、踉跄、小档没看到。main
- D-111（PR #98，还没合并）。
- [TF2 数据] seqdesc `+0x9C` 骨骼权重表；脚本 `TitanStagger`（`sh_titan.gnut:1137`）、`TITAN_ADDITIVE_FLINCH_DAMAGE_THRESHOLD` 500（`_settings.nut:884`）。

---

### 2.8 惯性和"重"：泰坦 vs 铁驭

#### 原理

泰坦的"重"不是靠慢，是靠**稳**和**慢半拍**：

- **站着就是不动**：待机所有通道 < 0.3°，没有呼吸晃动（铁驭的枪还有 ±0.23 u 呼吸）。
- **头和骨盆是一块铁**：走路时头相对骨盆只变 2.8 u，相关 0.99；上身和下身只在"扭"上反向（骨盆扭 13°，胸反扭 10°）。把这个关系拆开就是 TF2 的"濒死走"——HSD 第一版"像喝醉"就是这个样子（D-127 的起因）。
- **持枪臂稳、空手臂摆**：右臂（持枪）肩 3°、肘 5°；左臂 11° / 35°。底盘越重摆得越少。
- **身体比速度慢半拍**：电机 0.19 s 就到走速（12 章 §1.1），身体要 0.2 s 混入走、再 0.55 s 换到跑，播放速度还有死区。
- **停步不回弹**：停下就停下，不加欠阻尼弹簧。

铁驭的"轻"正好相反：身体响应即时（第 02–06 章），第一人称里的枪一直有小运动（走路晃 ±1.5°、冲刺枪大幅甩、转身超前 2.44°、站着呼吸），镜头也有更多事件。两者共用的是"镜头只拿很小一部分"（铁驭跑步镜头 ±0.3°；泰坦走路镜头 0.35 u）。

#### 规则和公式

程序生成路线要守住的约束（TAF §4.2，片段路线照片段做自然满足）：

| 约束 | 目标值 | 依据 |
|---|---|---|
| 走路一步（250 u/s） | 0.55–0.6 s | [TF2 数据]；**HSD B-沉 0.42 s 有意偏离（D-136）** |
| 待机 | 所有通道 < 0.3° | [TF2 数据] |
| 头 − 骨盆高度差峰峰 | ≤ 骨盆起伏的 20 %（TF2 18 %） | [TF2 数据] |
| 胸和骨盆滚转 | 不同向叠加；胸滚转 ≤ 1.3 × 骨盆滚转 | [TF2 数据] [推断] |
| 胸扭转 | 和骨盆反向，比例约 0.8（走）/ 0.5（冲刺） | [TF2 数据] |
| 骨盆最低点 | 脚锁住那一帧，误差 < 0.03 周期 | [TF2 数据] |
| 骨盆高度一帧变化 | 平滑，无跳变 | [TF2 数据] |
| 持枪臂（走） | 肩 < 3°、肘 < 5° | [TF2 数据] |
| 移动权重混入 / 混出 | 待机 ↔ 移动 0.2 s，走 ↔ 跑 0.55 s，smoothstep | [TF2 实测] |
| 停步回弹 | 0 | [TF2 数据] |
| 脚步声 | 脚接触那一帧（比锁住早约 0.07 s） | [TF2 数据] |
| 腰扭范围 | ±85° | [TF2 数据] |
| 冲刺 | 胸前倾 41°，骨盆俯仰几乎不变（1.4°），骨盆扭 42° / 胸反扭 20°，骨盆滚转 25° | [TF2 数据] |
| 冲刺转弯倾斜 | 目标 = 转速 ÷ 120 °/s（钳 ±1），二阶追随、临界阻尼 | [TF2 反编译] `sprinttilt_*` |

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 电机 0 → 走速（规则见 12 章 §1.1） | — | 0.19 / 0.19 / 0.24 s（轻 / 中 / 重） | — | — | [TF2 实测] |
| 走速 → 冲刺速度（12 章 §1.1） | — | 0.83 / 1.06 / 0.56 s | — | 重型最快 | [TF2 实测] |
| 头 − 骨盆高度差（走，峰峰） | 0.071 m | 2.8 u | 0.012 H_t | 轻 2.5、重 5.6 u | [TF2 数据] |
| 骨盆 / 胸扭转（走） | — | 12.9° / 10.1°（反向，滞后 0.38 周期） | — | — | [TF2 数据] |
| 骨盆左右挪（走） | 0.206 m | 8.1 u | 0.034 H_t | 约两脚间距的 10 % | [TF2 数据] |
| 持枪臂 肩 / 肘（走） | — | 3.0° / 4.7° | — | 冲刺 12° / 35° | [TF2 数据] |
| 空手臂 肩 / 肘（走） | — | 10.8° / 34.6° | — | 冲刺 39° / 59°；重型冲刺 1.9° | [TF2 数据] |
| 冲刺倾斜满值转速 `sprinttilt_turnrange` | — | 120 °/s | — | — | [TF2 反编译] |
| 濒死走：头 − 骨盆 / 相关 | 0.427 m | 16.8 u / 0.64 | 0.071 H_t | 健康时出现就是 bug | [TF2 数据] |

#### 实现模板

```
// 守约束的检查（HSD 录像 / TitanWalkFilm 输出 body.tsv 后跑）
check(body):
    assert period/2 in [0.55, 0.6] or allowDeviation("D-136")
    assert idleMaxAngle < 0.3
    assert ptp(head.z - pelvis.z) <= 0.2 * ptp(pelvis.z)
    assert sameSign(chestRoll, pelvisRoll) == false or |chestRoll| <= 1.3*|pelvisRoll|
    assert |argmin(pelvis.z) - contactPhase| < 0.03
    assert stopOvershoot == 0
```

**HSD 现在**：B-沉（`TitanWalkStyle.KeyPoseHeavy`，默认）。D-136 的数据（走路路线 38.1 m，B / B-沉）：脚滑 2.03 / 4.93 m 每 100 m，骨盆滚转 5.0 / 3.6°，扭转 9.9 / 7.0°，起伏 0.256 / 0.220 m，躯干滚转 1.2 / 0.9°，一步 0.553 / 0.420 s，停步回弹 0。B（一步 138.3 u = TF2 走）留开关 `walk_style = b`；游戏里 Backspace 切。工具 `TitanWalkFilm.Run -out <dir>`（编辑器批处理，30 fps 帧 + `body.tsv` / `feet.tsv`）。分支 `titan/integration`。

#### 验收

- `TitanAnimTests.TheWalkStyleStartsAsBHeavy`、`TheThreeWalksAreMeasured`、`TheKeyPoseTableIsWhatTheWalkPlays`、`SprintTurnRollsThePelvis`。
- 上面的约束表逐条量（TAF §4.1 第 6 条）。B-沉 已知不满足"一步 0.55–0.6 s"，是用户选的。
- **手感**：用户试玩（`HSD-Build/Titan-Feel-v1`，PR #83），这一轮没人试玩过（TFE 结论）。

#### 出处

- TAF §3 F1–F7、F11、F19，§4.2。main
- TFE §1、§5（三种底盘差别表）。PR #118，还没合并
- D-127、D-136（PR #98，还没合并）。

---

### 2.9 dash 的身体

#### 原理

dash 是**喷气推**，不是腿蹬：起步 0.2 s 身体压低前冲，背部喷口开喷，飘的时候腿收起不动，落地三小步收住。全程不做脚 IK。

#### 规则和公式

1. 三段：起（0.2 s）→ 飘（0.27 s 循环）→ 落（0.4 s），每段按 `move_yaw` 在左 / 前 / 右 3 片段间混；每段混入混出 0.15 s。
2. 起和飘没有根运动（位移全由电机：按下当帧到 dash 速度，保持 0.2 s，再按冲刺减速度降回走速，推力曲线和能量见 [12 章 §2](12-titan-motor.md)）；落地段自带约 350 u/s 的根运动，三步小碎步（脚步事件 0.083 / 0.417 / 0.75）。
3. 喷口在起步段 0.333 处开、落地段 0.5 处停。
4. 前 dash 身体（第三人称实测）：+0.2 s 胸高 157 → 118 u、胸前倾 12° → 35°、胸滚转 −22°，保持到 0.6 s，0.9–1.1 s 收回。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| dash 速度（中型，12 章 §2.1） | 17.78 m/s | 700 u/s | 2.98 H_t/s | 轻 800、重 600 | [TF2 实测] |
| 起 / 飘 / 落 | — | 0.2 / 0.27 / 0.4 s | — | — | [TF2 数据] |
| 落地段根运动 | 8.89 m/s | 约 350 u/s | 1.49 H_t/s | — | [TF2 数据] |
| 前 dash 胸高下降 | 0.991 m | 157 → 118 u（−39） | 0.166 H_t | — | [TF2 实测] |
| 前 dash 胸前倾 | — | 12° → 35° | — | — | [TF2 实测] |

#### 实现模板

```
dash: setMain(dodgeStart) → dodgeFloat(loop) → dodgeLand(rootMotion 350 u/s, 3 stamps)
      ik = off; jets on at start 0.333 → off at land 0.5
```

Unity 参考实现：`TitanBodyCore` 的 `DashShape`（前、后、左、右四个关键姿势）、`DashLandLength` 0.43 s、`ThrustFrom` 0.077；测试 `TitanAnimTests.TheJetsRunFromOneThirdOfTheStartToTheMiddleOfTheLanding`、`ADashLandsWithThreeStamps`。分支 `titan/integration`。

#### 验收

- 上面两个测试；前 dash 0.2 s 时骨盆 / 胸下降 ≥ 30 u、前倾 ≥ 30° [设计，按 TF2 实测]。

#### 出处

- TAF §2.7、§3 F15；GAPS §7（PR #98，还没合并）；TFE §1 dash 行（PR #118，还没合并）。main

---

### 2.10 三种底盘的差别放在哪

#### 原理

TF2 三种底盘共用一套动画结构，只换少数几个数；镜头规则几乎完全一样。而且方向和直觉相反：**轻型晃得更多，重型更硬、更稳**——TF2 靠"硬"表现重，不是靠"慢"（重型从走速到冲刺反而最快）。用户要"三种底盘明显拉开"（TFE 结论 3），就得在 TF2 的基础上加我们自己的差别，标 [设计]。

#### 规则和公式

| 项 | 轻 | 中 | 重 | 依据 |
|---|---|---|---|---|
| 走路周期 | 1.0 s（走跑同一套） | 1.133 s | 1.133 s | [TF2 数据] |
| 待机髋高 | 136 u | 118 u | 129 u | [TF2 数据] |
| 两脚间距 | 92 u | 83 u | 124 u | [TF2 数据] |
| 冲刺手臂 | 摆 | 摆 | 锁住（肩 1.9°），上身扭 | [TF2 数据] |
| 上身跟随滞后（300 °/s） | 20.7° | 27° | 40° | [TF2 实测] |
| 落地 punch 弹簧 k / d | 35 / 9 | 65 / 15 | 95 / 30 | [TF2 数据]（07 章） |
| 踏步冲量（§3.1） | −6 u/s | −5 u/s | −4 u/s | [TF2 数据] |
| 走 → 跑门槛 | 121.5 u/s | 112.5 u/s | 94.5 u/s | [TF2 反编译] |
| 舱框晃动、受击、dash 横滚、冲刺下沉、步伐定时器、眼高、FOV | 同 | 同 | 同 | [TF2 实测] |

可以拉开的地方（[设计]，默认 = TF2）：走路起伏、舱框晃动、冲刺摆动、眼高、引擎底噪（TFE §6 的开关，按底盘一个倍数）。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 中型待机髋高 | 2.997 m | 118 u | 0.502 H_t | 轻 136、重 129 | [TF2 数据] |
| HSD 眼高（三种都） | 4.699 m | 185 u | 0.787 H_t | 设计候选 150–260 u | [TF2 实测] [设计] |

#### 实现模板

```
TitanChassis { gaitTables, dims, punchSpring, stepJolt, runThreshold = 0.45 * standSpeed, ... }
// 共用：动画结构、镜头规则；按底盘：上表几项 + 设计倍数
```

Unity 参考实现：`TitanChassis`、`TitanDims` / `TitanDimsHeavy` / `TitanDimsLight`（PR #72 引入）、`TitanWalkKeyPosesHeavy` / `Light`、`TitanClipsHeavy` / `Light`；三种底盘能开在 PR #83（`titan/feel-build`，还没合并）。

#### 验收

- `TitanAnimHeavyTests`、`TitanAnimLightTests`、`TitanDimsTests`（各底盘尺寸、平地中型逐字节不变）。
- 用户试玩 Titan-Feel-v1（没做）。

#### 出处

- TAF §3 F18；TFE §5、§6（PR #118，还没合并）；TPC §3.1。main

---

## 3. 泰坦：驾驶舱镜头

驾驶舱镜头**不挂在身体骨骼上**：身体动画在第一人称里看不见，镜头全部由程序算；只有上机、下机、弹射、处决、近战这几个脚本序列由动画驱动（07 章 §2.11、§2.13）。受击（`JoltCockpit`）以 07 章 §2.8 为准。本节写其余的：常驻、冲刺下沉和摆动、dash 横滚、舱框晃动、开火时舱框和画面的关系、舱内炮的摆动。

**两个弹簧**（07 章 §1.1 的 punch 弹簧同一种形式）：舱体弹簧 k 65、d 9（走路冲量、受击）；落地 punch 弹簧按底盘（07 章 §2.3 的泰坦行）。HSD 的弹簧解是精确解，和帧率无关（`TitanCamTests.TheSpringIsExactWhateverTheStep`）。

### 3.1 常驻：眼高、FOV、走路定时器起伏

#### 原理

泰坦第一人称几乎不动：FOV 固定 75，冲刺、dash、受击都不变；走路时镜头只有每步一下极小的竖直顿挫（0.3 u 级），没有旋转。这一下来自**定时器**，不跟身体步频（身体一步 0.585 s，镜头 0.70 s，会漂）——这样镜头不依赖动画，也不用绑定步幅。脚步声和灰尘用动画事件（§2.5）。

#### 规则和公式

1. 眼高 185 u，蹲 125 u，高度平滑过渡（时长没测，HSD 0.2 s 占位）。
2. FOV 75（Source 4:3 水平），所有状态不变。
3. 走路定时器：速度超过门槛就每 0.70 s（冲刺 0.417 s）一步，第一步在按键后约 0.03 s。每步给舱体弹簧一个竖直**速度**冲量 `stepJolt`（中型 −5 u/s），弹簧 k 65、d 9：下沉峰值在冲量后 0.146 s，回弹 +12 %（0.62 s）。没有旋转。
4. 蹲走：幅度约一半（−0.16 u 对 −0.32 u）；节奏 0.5 s 还是 0.7 s 没定（设置文件 500 ms，Unity 实测像 0.70）。
5. 横移、后退：镜头不旋转。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 眼高 站 / 蹲 | 4.699 / 3.175 m | 185 / 125 u | 0.787 / 0.532 H_t | 三种底盘相同 | [TF2 实测] |
| FOV | — | 75° | — | 铁驭 70° | [TF2 实测] |
| 步伐间隔 走 / 冲刺 `footstepInterval*` | — | 0.70 / 0.417 s | — | 三种相同 | [TF2 实测] [TF2 数据] |
| 第一步延迟 | — | 约 0.03 s | — | — | [算] |
| 踏步冲量 `cockpit_stepJolt_origin` z | −0.127 m/s | −5 u/s（轻 −6、重 −4） | −0.021 H_t/s | 设计 0 … −20 u/s | [TF2 数据] |
| 每步下沉（峰峰，中型） | 0.0089 m | 0.35 u（算 0.321） | 0.0015 H_t | 轻 0.42、重 0.28 u | [TF2 实测] |
| 舱体弹簧 k / d | — | 65 / 9 | — | 设计 20–200 / 3–40 | [TF2 数据] |
| 下沉峰值时刻 / 回弹 | — | 0.146 s / +12 % | — | — | [算] [TF2 实测] |
| 蹲走幅度 | — | × 0.5 | — | — | [TF2 实测] HSD 记录 |

#### 实现模板

```
// 单位：u、s
stepClock(dt, speed, sprint):
    if speed < stepMinSpeed: clock = interval - stepFirst; return
    interval = sprint ? 0.417 : 0.70
    clock += dt
    if clock >= interval: clock -= interval; cockpitSpring.vel.z += stepJolt * (crouch ? 0.5 : 1)
eye = eyeHeight(crouchBlend) + cockpitSpring.pos      // 弹簧 k 65 d 9，精确解
```

Unity 参考实现：`TitanCamParams`（`stepWalk` 0.70、`stepSprint` 0.417、`stepFirst` 0.03、`stepJolt` −5、`crouchStepScale` 0.5、`stepMinSpeed` 5 [设计]、`cockpitK` 65、`cockpitD` 9）、`TitanCamModel`、`TitanCamera.SourceFov` 75。分支 `titan/integration`（PR #78，还没合并）。

#### 验收

- `TitanCamTests.StepsAreATimerOfCockpitSpringImpulses`、`TheCockpitSpringPeaksAsTheGapsTableSays`、`TheFovStaysFixedInEveryMove`、`TheRealMotorsStepsSprintDashAndLandingReachTheCamera`、`AimIsTheMouseWhateverTheLayersDo`。
- 对照：TF2 生成的参考表 `TitanCamReference.gen.cs`（`Assets/HSD/Game/Tests/Editor/`）；合格线峰值差 < 5 %、时间形状对上（07 章 §2.8 同一套）。

#### 出处

- GAPS §6：定时器、冲量、下沉表（PR #98，还没合并）。
- TPC §4.1；TFC §1.1（stepJolt 三底盘）。main
- TFE §2 走路起伏、蹲走、FOV 行；§3 眼高。PR #118，还没合并
- TAF §1.5、§3 F12。main

---

### 3.2 冲刺下沉和冲刺摆动

#### 原理

冲刺时镜头压低 25 u（"压低身子冲"），1 s 才压到位，松开 0.3 s 回来——进得慢，就是有份量的加速。同时有一个两步周期的小摆动（俯仰、左右、滚转各约 1–2°）。

#### 规则和公式

1. 下沉：线性进度 + smoothstep 读者曲线（07 章 §1.2 同一种），进 1.0 s、出 0.3 s；下沉开始比按键 / 松键晚约 0.05 s（两个方向都是）。
2. 摆动：周期 0.834 s（= 2 × 0.417），从冲刺开始算时间；傅里叶拟合（直流 + 1–3 次谐波），俯仰 −1.06 … +0.51°、左右 ±1.1°、滚转 0 … 1.76°。摆动约 0.15 s 进来、随下沉 0.3 s 出去。
3. 三种底盘实测相同（设置文件 `sprinttiltMaxRoll` 4 / 3 / 2 不起作用；轻、重型的俯仰左右没拟合，按相同处理）。
4. 冲刺 FOV 不变。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 冲刺下沉 `sprintViewOffset` | 0.635 m | 25 u（实测 25.4–25.6） | 0.106 H_t | 设计 0–40 u | [TF2 数据] [TF2 实测] |
| 进 / 出时长 | — | 1.0 / 0.3 s | — | 设计 0.2–2 / 0.1–1 s | [TF2 数据] |
| 下沉延迟 | — | 约 0.05 s | — | — | [TF2 实测] 拟合 |
| 摆动周期 | — | 0.834 s | — | — | [TF2 实测] |
| 摆动 俯仰 / 左右 / 滚转 | — | −1.06…+0.51° / ±1.1° / 0…1.76° | — | 只拟合了中型 | [TF2 实测] |
| 摆动进 / 出 | — | 约 0.15 / 0.3 s | — | 偏航约 0.1 s 先走 | [TF2 实测] |

#### 实现模板

```
// 单位：u、°、s
sprintCam(dt, sprinting):
    p = advance(p, sprinting, after = 0.05, in = 1.0, out = 0.3)   // 线性
    eye.z -= 25 * smoothstep(p)
    w = approach(w, sprinting, in 0.15, out 0.3)
    t = sprinting ? t + dt : t
    view += w * fourier(t / 0.834)        // pitch / yaw / roll，Source 号
```

Unity 参考实现：`TitanCamParams`（`sprintDrop` 25、`sprintIn` 1.0、`sprintOut` 0.3、`sprintDropDelay` 0.05、`swayPeriod` 0.834、`SwayPitch/Yaw/Roll` 系数、`swayIn` 0.15、`swayOut` 0.3）、`TitanCamModel`。分支 `titan/integration`。

#### 验收

- `TitanCamTests.SprintDropsAndSwaysOnItsTimer`、`KeysPassThroughTheirPeaksWithoutOvershoot`。
- 拟合残差（t1_cam sprint_ion）：俯仰 0.11°、左右 0.06°、滚转 0.12° rms。

#### 出处

- TPC §4.2；TAF §2.3 镜头行；T0-REPORT §2.4（`tf2/expansion/titan/T0-REPORT.md`）。main
- TFE §2 冲刺下沉、冲刺摆动行；§6.2。PR #118，还没合并

---

### 3.3 dash 的横滚和舱框下压

#### 原理

左右 dash 把画面往一边甩（滚转约 8.5°），前后 dash 不转；"推背感"只靠舱框被压下去和声音，**没有 FOV 冲击**。

#### 规则和公式

1. 左右 dash：滚转 ∓8.5°（向 dash 反方向倾），按键后约 0.18 s 到峰值，再约 0.52 s 回零（三次曲线：以给定斜率开始下降、平着落地）。
2. 前后 dash：没有旋转；镜头只沉 0.26–0.39 u。
3. 舱框（§3.4）朝 dash 方向压下：前 dash 上沿 +24 px，0.11 s 峰，0.43 s 回零；HSD 用舱体弹簧上的 7.3 u 位移 + 4° 滚转表示。
4. 三种底盘相同。
5. dash FOV 冲击：TF2 没有；HSD 的 `dashFovKick` 是 [设计]，默认 0。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 左右 dash 滚转峰值 | — | 8.5–8.6°（`dodge_viewTiltMax` 10 × …） | — | 设计 0–15° | [TF2 实测] |
| 到峰 / 回零 | — | 0.171–0.18 s / 0.52 s | — | — | [TF2 实测] |
| 前 dash 镜头下沉 | 0.0066–0.0099 m | 0.26–0.39 u | — | — | [TF2 实测] |
| 舱框下压（前 dash） | — | +24 px @1280×720，0.11 s 峰，0.43 s 回零 | — | 三底盘差 ≤ 2 px | [TF2 实测] |
| HSD 舱框位移 / 滚转 | 0.185 m / — | 7.3 u / 4° | 0.031 H_t | 设计 0–15 u / 0–8° | [算] [TF2 数据] `dodge_cockpitTiltMax` 4 |

#### 实现模板

```
onDash(side):
    if side in {Left, Right}: rollCurve.start(peak = ±8.6, rise 0.171, fall 0.52)
    cockpitSpring.kick(offset = 7.3 toward dash, roll = 4)
```

Unity 参考实现：`TitanCamModel.Dash(TitanDashSide)`；`TitanCamParams`（`dashRollPeak` 8.6、`dashRollRate` 50、`dashRollFall` 0.52、`dashRollStartSlope` −0.845、`dashFrameUnits` 7.3、`dashFrameRoll` 4）。分支 `titan/integration`。

#### 验收

- `TitanCamTests.DashRollsOnlySideways`、`TheFramePushesInADashAndIsBackInHalfASecond`。

#### 出处

- TPC §4.2；TFC §1.3；GAPS §5（PR #98，还没合并）；TFE §2 dash 推背行（PR #118，还没合并）。main

---

### 3.4 舱框晃动（转身、俯仰、移动）

#### 原理

**视角没有滞后**（鼠标 1:1，泰坦和铁驭转速一样）；滞后的是**舱框**：转身时舱框向转动的反方向落后，停下后约 0.37 s 回位。这是"坐在一台大机器里"的主要画面线索。视角事件（落地、开火、受击）**带着舱框一起动**，舱框相对屏幕几乎不变。

#### 规则和公式

1. 舱框在自己的相机里画，有一个相对视线的偏移（位移 + 角度），上限 ±3 u、±1.5°（`cockpitSwayGain` 3 × 文件值 1 / 0.5）。
2. 转身：舱框偏移目标 = −上限 × clamp(转速 / 40 °/s, −1, 1)；向目标一阶追随，时间常数 0.37 s（停转 −33 → −20 px @0.2 s → −8 px @0.5 s）。≥ 60 °/s 时到顶（约屏宽 2.7 %）。
3. 俯仰运动中同样向反方向落后（44 °/s 时 0.2 s 落后 8 px，还在增大，稳定值没拍到）；停住的俯仰：+29° 舱框上移 10 px，−58° 下移 6 px。
4. 移动：前进时舱框约 (−5, −10) px 的持续偏移，后退 (+4, −5) px；单步起伏分辨不出；横移数据不可靠。
5. 落地、开火、受击：舱框跟画面（落地 8.8° 只让舱框动 8 px）。
6. 没有漂移（`cockpitDrift_*` 四个都是 0）。三种底盘逐像素相同。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 舱框位移 / 角度上限 | ±0.076 m / — | ±3 u / ±1.5° | ±0.013 H_t | 设计 0–8 u / 0–4° | [TF2 数据] |
| 转身满值转速（HSD） | — | 40 °/s | — | 30 °/s 时 60 %，≥ 60 °/s 到顶 | [TF2 实测] 拟合 |
| 回位时间常数 | — | 0.37 s | — | 设计 0.1–1.0 s | [TF2 实测] |
| 满值落后（屏幕） | — | −33 … −37 px @1280×720 | — | 约屏宽 2.7 % | [TF2 实测] |
| 1° ≈ 屏幕 | — | 10.9 px（中心）/ 13.8 px（上梁） | — | — | [算] |

#### 实现模板

```
// 单位：u、°、s
frameSway(dt, yawRate, pitchRate):
    target = -clamp(yawRate / 40, -1, 1) * (3 u, 1.5°)    // 俯仰同理（系数 HSD 拟合）
    sway  += (target - sway) * (1 - exp(-dt / 0.37))
    frame = sway + moveOffset(forward/back) + heldPitchOffset(pitch)
// 视角事件：加在视角上，舱框随视角一起动（不加到 frame 上）
```

Unity 参考实现：`TitanCamParams`（`swayTau` 0.37、`swayFullRate` 40、`swayUnits` 3、`swayDegrees` 1.5、`moveForwardYaw/Pitch`、`moveBackYaw/Pitch`、`moveStrafeYaw` [设计]、`lookDownPitch`、`lookUpPitch`、`landFrameShare` 0.083）；`TitanCockpitView`（灰盒舱框和炮在自己的相机上，梁深 110 u、柱 60 u）；`TitanCockpitCamera.FrameOffset`。分支 `titan/integration`。

#### 验收

- `TitanCamTests.TheFrameLagsATurnAndComesBackAtTheMeasuredRate`、`WalkingAndHeldPitchOffsetTheFrameAsMeasured`、`ALandingBarelyMovesTheFrame`、`BoardingsViewJumpIsNotATurn`。

#### 出处

- GAPS §5（PR #98，还没合并）；TFC §1.2、§1.3。main
- TFE §2 转向滞后行、§3 舱框相对屏幕行（PR #118，还没合并）。

---

### 3.5 开火时的驾驶舱镜头

#### 原理

泰坦开火的镜头规律和铁驭一样（每把枪自己的弹簧，画面只拿后坐的一部分），细节在 09 章。这里只写驾驶舱特有的两条：**舱框跟着画面一起动**（开火时舱框相对屏幕 ≤ 3 px），以及**屏幕震动只传 10 % 给舱内的炮**。开火的身体动作是上身叠加层，镜头骨权重 0，所以身体不会推镜头（§2.7）。

#### 规则和公式

1. 画面后坐 = (1 − `weaponFraction`) × punch（09 章；TF2 XO-16 `viewkick_hipfire_weaponFraction` 0.7）。
2. 舱框：开火时不单独动（Monarch ≤ 1 px，Ronin ≤ 3 px），随视角。
3. 屏幕震动传给舱内炮的份额 `shake_viewmodelFactor_titan` 0.10。
4. 换弹：1P 武器动画带着镜头角度摆（Monarch 俯仰 −1.2 … +4.4°），位移 0；HSD 的炮换弹是自己的设计（D-111 手臂、开关 `cameraCues`），只借幅度。
5. ADS 只改 FOV（Ronin、Ion 75 → 55；Legion 不变），舱框不动，枪上抬到画面中下方。

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 开火时舱框相对屏幕 | — | ≤ 1–3 px | — | — | [TF2 实测] |
| 屏幕震动传给炮 | — | 0.10（×） | — | — | [TF2 反编译] ConVar |
| 换弹镜头俯仰摆（Monarch） | — | −1.2 … +4.4° | — | 位移 0 | [TF2 实测] |
| ADS FOV（Ronin、Ion） | — | 75 → 55° | — | Legion 不变 | [TF2 实测] |

#### 实现模板

```
view += (1 - weaponFraction) * weaponPunch()    // 09 章
cannon += 0.10 * screenShake()
frame 不加开火项
```

Unity 参考实现：`TitanRecoil.Designed` / `Xo16`、`recoilScale`（`Titan/Weapon/TitanWeaponData.cs`，后坐见 09 章）；配置键 `walk_style`、`b_heavy_ankle` 的说明在 `Titan/Animation/README.md`；舱框随视角在 `TitanCockpitCamera`。**屏幕震动传给炮 10 % 没做**（舱框和炮在自己的相机上，不受震动）。分支 `titan/integration`。

#### 验收

- `TitanCamTests.TheWeaponSlotsRunOnlyWhileDriving`、`TheCameraChangesNothingInTheSimulation`；后坐的测试在 09 章。

#### 出处

- GAPS §4、§5（PR #98，还没合并）；TPC §4.3；TAF §2.10、§2.11 镜头行、§3 F13。main
- TFE §2 开火后坐、换弹镜头行（PR #118，还没合并）。

---

### 3.6 舱内炮的摆动（bob / sway）

#### 原理

驾驶舱里最能看出"在走路"的，不是镜头（每步只沉 0.3 u），而是**右下角的炮**跟着步子晃。TF2 的炮晃动周期 0.69 s，和镜头定时器 0.70 s 同拍。重枪（Legion 类）晃得大、转得少（转身滚转只有 ±1°），"拖不动"的感觉就出来了。这和铁驭不同：铁驭的枪晃动周期按走过的距离（§1.3），泰坦的炮跟定时器。

**HSD 现在没有**（炮在舱框相机上不动），是 TFE §7.1 的第 2 项。

#### 规则和公式

以下是 TF2 武器文件的值（TF2 泰坦武器的客户端读这些字段，和 R5 铁驭不同 [推断]，没在 TF2 里逐帧验证幅度）：

| 键 | 通用值 | 例外 |
|---|---|---|
| `bob_cycle_time` | 0.69 s | Northstar 0.7，Legion 0.715 |
| `bob_vert_dist` / `bob_horz_dist` | 0.6 / 0.1 | Northstar 0.8 / 1，Legion 2 / 2.25 |
| `bob_max_speed` | 150 u/s（到这个速度摆满） | Northstar 300 |
| `bob_pitch` / `yaw` / `roll` | 0.75 / −1.7 / −1.2 | Legion 0.5 / −0.75 / −1.35 |
| `sway_translate_gain` / `sway_rotate_gain` | 4 / 7 | Northstar、Legion 旋转 4 |
| `sway_*` 位移上限 / 角度上限 | x ±0.5、y ±2、z ±2.7 u；pitch ±3、yaw ±2.5、roll ±4° | 全同 |
| 前进时枪下沉 `sway_move_forward_translate_z` | −2.7 u | 全同 |
| 转身时枪滚转 `sway_turn_left/right_rotate_roll` | −4 / 4° | Legion ±1 |
| 抬头 / 低头时枪 `sway_turn_up/down_rotate_pitch` | −3 / 3° | Legion ±1 |

| 量 | [m] | TF2 原值 [u] | 身高比例 | 合理范围 | 依据 |
|---|---|---|---|---|---|
| 炮 bob 周期 | — | 0.69 s | — | 和镜头 0.70 s 同拍；设计 0.4–1.2 s | [TF2 数据] |
| bob 上下 / 左右 | 0.0152 / 0.0025 m | 0.6 / 0.1 u | — | 重枪 2 / 2.25 u | [TF2 数据] |
| 摆满速度 | 3.81 m/s | 150 u/s | 0.638 H_t/s | Northstar 300 | [TF2 数据] |
| 前进下沉 | −0.069 m | −2.7 u | −0.011 H_t | — | [TF2 数据] |
| 转身滚转 | — | ±4°（重枪 ±1°） | — | 设计 0–6° | [TF2 数据] |

#### 实现模板

```
// 单位：u、°、s。周期跟定时器，不跟距离（和铁驭 §1.3 不同）
cannonBob(dt, speed):
    w = clamp01(speed / bobMaxSpeed)
    t += dt; φ = t / bobCycle
    offset = w * (bobHorz*sin(2πφ), bobVert*sin(4πφ)); angles = w * (bobPitch, bobYaw, bobRoll) * waves(φ)
cannonSway = follow(turnRate → roll ±4, move → z −2.7; gains 4 / 7, clamp to sway_* limits)
```

Unity 参考实现：**没有**。`TitanGunMotion.cs`（`SpringFollower`）是第三人称炮跟手的弹簧，不是舱内 bob / sway。TFE §6.3 已列开关名（`gunBob`、`gunBobCycle`、`gunBobVert/Horz`、`gunBobMaxSpeed`、`gunSwayTurnRoll`、`gunSwayGain`、`gunShakeShare`），feel-build v1 没做。

#### 验收

- 没有测试。做了以后：走路 250 u/s 时炮的上下周期 0.69 s ± 0.02、和镜头步伐同拍（相位差漂移 ≤ 0.01 s / 步）[设计]；重枪转身滚转 ≤ 1.2°。
- 用户试玩。

#### 出处

- TAF §3 F13、`anim/out/weapon_sway.csv`（七把主武器）。main
- TFE §3 舱内枪行、§6.3、§7.1 第 2 项（PR #118，还没合并）。

---

## 4. 做一个新动作时的检查清单

做新枪、新的手上动作、新的泰坦动作时照这几条检查（和 DP §9、07 章 §5 一起用）：

**铁驭**

- [ ] 手的姿势有明显变化吗？没有就不要加主序列，用程序层或叠加层。
- [ ] 它和走、跳、滑铲同时发生时，能靠相加得到吗？不要做组合动画。
- [ ] 它占几只手？占手的移动（翻越、滑索、钩爪）来时它怎么让？
- [ ] 它什么时候开始不再需要手（"解锁"）？那一刻之后，开火、开镜、冲刺都要能立刻切掉它。
- [ ] 不用手的动作（跳、滑铲）不打断它。
- [ ] 开镜时它的程序运动收掉了吗？
- [ ] 镜头是不是只拿了很小一部分？
- [ ] 切换时位置连续吗（smoothstep，min(旧淡出, 新淡入)）？
- [ ] 腰射枪身角度有 R5 实测吗？没有要标明（DP §7.11）。

**泰坦**

- [ ] 上身动作只作用上身（腿 ≤ 0.06、镜头骨 0）？
- [ ] 换步态是 min(旧, 新) 的 smoothstep，起停 0.2 s？停步 0 回弹？
- [ ] 健康时头和骨盆同步、胸和骨盆滚转不同向叠加？（拆开 = 濒死 / 坏了）
- [ ] 骨盆最低点、脚锁住、脚步声在同一刻？
- [ ] 驾驶舱镜头没挂回骨骼？视角事件带着舱框一起动？
- [ ] 按底盘拉开的差别标 [设计]，默认值仍是 TF2？

---

## 5. 待研究和缺口（本章）

详细建议在 [`_notes/hb-ch08.md`](_notes/hb-ch08.md)，编号沿用 [99-TODO-RESEARCH.md](99-TODO-RESEARCH.md) 的 B08-*：

- **B08-1**：R5 走路晃动的来源（加在视图模型实体上，代码没找到）。手册按实测曲线写，不影响重建。
- **B08-2**：转视角枪超前只测了 233 °/s，俯仰没测。
- **B08-3**：叠加层的进度和权重、开镜过程的横滚、手臂骨骼读不到。
- **B08-4**：泰坦 13° 以上斜坡、轻 / 重冲刺摆动的俯仰左右、蹲起镜头过渡、舱内炮 bob / sway 的实测（TF2 现在启动是 `no_game`，测不了）。
- 新增（建议，见 `_notes`）：跑墙时枪模怎么动（R5 关着、TF2 没测）；翻越结束后的抬枪时间；冲刺到开火 0.25 s 上限的来源；小伤害抖动在别人眼里播不播；泰坦踉跄 / 换弹在 HSD 骨架动画里的做法。
