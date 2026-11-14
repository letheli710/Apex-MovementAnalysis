# 99 待研究清单

hb0 建（2026-11-14）。各章会话发现新的缺口，写进自己的 `_notes/<会话名>.md`，由 hb-integrate 合进来。

**11-14 第一轮整合（hb-integrate）**：并进了 hb-ch02、hb-ch03、hb-ch04、hb-ch07、hb-tables 的 `_notes`。编号规则：已有的编号不改；各章备注里的新条目接着本章最大号往下编（hb-ch04 原来用字母 B04-a … k，换成数字，"来源"列写原编号；hb-ch02 的 B02-3 和已有编号撞了，改成 B02-8）。"来源"列写提出的会话。05、06、08、09、10、11 章和附录 A 的会话还在写，第二轮再并。

## 白话说明

这里列的是**还没研究、手册写不出来**的东西。用户 11-14 定：这些全部放到所有阶段做完以后再做，**这一轮不做任何新实测**。

分两部分：

- **A. 用户点名的四个题目**：防晕和可关闭选项、屏幕效果、音效和镜头同步、第三人称 / 驾驶舱切换。都还没有专门研究，下面写了现在零散有什么、要研究什么。
- **B. 盘点时发现的缺口**：手册某一章需要、但研究里没有实测或没有读的东西，按章排。每条写清：缺什么、影响哪一章、要在哪测（R5 / TF2 / 只读文件）、优先级。

优先级：**高** = 手册那一项写不完整，或者 HSD 现在的做法可能是错的；**中** = 有推断能先用，实测能把推断变成事实；**低** = 只影响少数情况或只影响验收表。

---

## A. 用户点名的四个题目

### A-1 防晕和可关闭选项

- **现在有什么**：
  - M5.5 镜头的分组强度 0–2 和 `response`，`CameraFeedbackSettings.Off()`（`HSD-Unity: Assets/HSD/Game/Runtime/Camera/M55/CameraFeedback.cs`，main）。
  - 原生镜头每个通道都有单独开关（`NativeCameraParams`，`Camera/Native/NativeCamera.cs`，main）；FOV 设置（D-44）。
  - 镜头技能 `fps-camera-design` 的 `references/verification.md` §6（强度 0、关）。
  - `research/phase2-local/m55/ACCEPTANCE-M55.md`（M5.5 的强度设置）；TITAN-FEEL §6.2、§7.3 列的泰坦实验开关（PR #118，还没合并）。
- **没有的**：R5 / TF2 菜单里到底有哪些防晕选项（镜头晃动、FOV、横滚、头部晃动、动态模糊）；每个选项关掉以后哪些通道归零、哪些只是变小；"关掉"以后玩法信息（落地 kick 表示落地重）怎么补。
- **要研究**：R5 设置菜单逐项开关 × 镜头录像（R5 实测）；业界常见防晕选项清单（只读）；HSD 的选项分组（设计）。
- **影响**：07 镜头、11 验收（每个选项要有"关掉以后是什么样"的验收）。

### A-2 屏幕效果（暗角、速度线等）

- **现在有什么**：
  - 速度线只在 M5.5 设计里有（`speedStreaks`，330 → 650 u/s），DESIGN-PHILOSOPHY §6.5 判定是**偏离 R5**（R5 没有速度线，`research/rea-native/camera/CAMERA-REFERENCE.md` §1）。
  - 震屏：`research/rea-native/camera/CAMERA-INVENTORY.md` CAM-21、CAM-23。
  - 调色、去色：`research/combat/_shared/E-SCREEN-COLOR-CORRECTION.md`（PR #86，还没合并）；毒气、震撼：`_shared/A-gas-cloud.md`、`A-shellshock.md`（同 #86）。
  - 受伤闪屏、低血量：`research/ui/UI-INVENTORY.md` H-07（PR #102，还没合并）。
  - 泰坦：受伤色差、开机分块亮起（`tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` §5，main；TITAN-FEEL §3，PR #118）；Unity `TitanCockpitFx`（HSD-Unity PR #66，还没合并）。
- **没有的**：**暗角（vignette）完全没有资料**；冲刺 / 滑铲 / 高速下 R5 有没有任何后处理（FOV 之外）；后处理和镜头通道的先后顺序。
- **要研究**：R5 冲刺、滑铲、滑索、钩爪、受伤时的截图对比（R5 实测，看后处理）；`r5apex` 后处理参数读取（反编译）。
- **影响**：07 镜头（§"R5 没有的东西"）、09 命中反馈。

### A-3 音效和镜头同步

- **现在有什么**：
  - R5 方面几乎没有：只有 `research/rea-native/camera/C3-CAPTURE.md` 里入水 / 出水音效一笔；DESIGN-PHILOSOPHY §10.2 #12 写明音频完全没测。
  - TF2 泰坦：TITAN-FEEL §4（各类声音由什么触发、脚步间隔，PR #118）；`tf2/expansion/titan/anim/TITAN-ANIM-FEEL.md` 结论 4（脚、骨盆、镜头、声音同一刻发生，main）；D-171（重型步幅和镜头步调差 0.12 s，泰坦线 PR，还没合并）。
  - 命中声音：UI-INVENTORY H-02（PR #102）。
  - Unity：`Titan/Damage/TitanSynth.cs` 13 个占位合成音（HSD-Unity PR #66）；`PracticeGame.cs` 的 `PadJumpCue` 提示音（main）。
- **没有的**：铁驭脚步声跟计时器还是跟动画；落地、起跳、滑铲、翻越的声音和 kick 的时间差；开枪声和后坐 kick 的先后；声音音量和移动速度的关系。
- **要研究**：先定方法（R5 录音 + 镜头录像同一时间轴，或读脚本里的声音事件触发点），再决定测不测。
- **影响**：07 镜头（事件型 kick 的时刻）、08 身体动画、09 战斗手感。

### A-4 第三人称 / 驾驶舱镜头切换

- **现在有什么**：
  - TF2 上机 / 下机：`tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md` §4.5（上机约 3.25 s 镜头动画、下机 1.6 s、处决切第三人称 `CE_FLAG_TITAN_3P_CAM`，main）；TITAN-FEEL §3（上机 3.45 s、下机后低头约 43°，PR #118）；`tf2/expansion/titan/anim/ref-upper/REF-UPPER-1109.md`（旁人镜头、`thirdperson` 测法，main）；D-90（不做处决和第三人称配对动画）。
  - Unity：`Titan/View/TitanCamera.cs`（`Compute(..., bool thirdPerson)`）、`TitanGameView.ThirdPerson`（只在 tour 里用）、`Titan/Camera/TitanCockpitCamera.cs`（HSD-Unity PR #66 / #78，还没合并）。
- **没有的**：R5 铁驭第三人称镜头（MOVEMENT-ANIMATION §10 写了"另外研究"）；第一 ↔ 第三人称切换时的过渡曲线、碰撞避让、FOV 变化；驾驶舱 ↔ 外部视角切换的手感规则。
- **要研究**：TF2 `thirdperson` 下的镜头位置和过渡（TF2 实测）；R5 第三人称（如果 HSD 要做）。
- **影响**：07 镜头、08 泰坦。

---

## B. 盘点时发现的缺口

### 01 单位与身体

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B01-1 | **R5 碰撞体尺寸没测**：站立 32 × 32 × 72 u 和蹲姿 48 u 都是 HSD 设计值（Source 默认）。`airUnduckDrop` 16.5 u 推出的蹲高是 55.5 u 或 39 u，和 48 都对不上（R5-DIFF HB-4b）。参考身高 H 也依赖站立高度 | R5：Frida 读 `GetPlayerMins/Maxs`，或钻不同高度的缝 | 高 | hb0；hb-ch02 |
| B01-2 | **台阶高度对不上**：R5 setfile `stepHeight` 22 u，HSD `MovementWorld.stepUp` 18 u（等于 TF2 的值）。11-14 已补进 R5-DIFF HB-1，决定 D-194 等用户定 | 和 B02-1 一起测 | 高 | hb0；hb-ch02；hb-tables |

### 02 底层

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B02-1 | 台阶梯 18 / 20 / 22 / 24 u + 蹲姿头顶间隙，一次回答 B01-1 和 B01-2。同一批里测：走、冲刺、滑铲（看速度减多少，验证 `slide_step_velocity_reduction` 10 × Δz，D-203）、空中贴着台边落下；看镜头是否把抬高平滑掉 | R5，便宜：和 R6 一样用道具拼台阶，状态日志逐命令 | 高（决定 D-194 台阶 18 / 22） | hb0；hb-ch02 扩充 |
| B02-2 | 不滑铲时在坡上走（非冲刺）没单独测；能站的最陡坡 0.7 只有源码（实测见 B02-6） | R5，可选 | 低 | hb0 |
| B02-3 | tick：R5 可变帧时长、Unity 固定 1/120。11-14 已写成 D-195（补记，等用户确认）、R5-DIFF 三节 | 不用测 | 中 | hb0 |
| B02-4 | **平地走下台边**：R5 走下 2 / 8 / 16 / 22 u 的路沿时贴下去还是掉下去（Source 的 StayOnGround 会贴下去） | R5：冲刺走下道具台阶，看着地标志是否断 | 中（影响落地镜头、跳的时机） | hb-ch02 |
| B02-5 | **空中迈台面**（R5-DIFF HB-3）：HSD 空中身体只要脚离台面 ≤ 18 u 就能水平越过台面侧面、落下时被放到台上。R5 里同样的情况是撞墙还是翻越 | R5：起跳后贴着 10 / 16 / 20 u 高的台边水平移动 | 中 | hb-ch02 |
| B02-6 | 能站的最陡坡 0.7 的实测（44° / 46° / 48° 坡）；Unity 关卡尺度表实跑 45.5° | R5：R6 坡加大角度 | 低 | hb-ch02；hb-tables |
| B02-7 | 读 R5 原生 StepMove / TryPlayerMove：碰几次、台阶怎么迈、圆底到底是什么形状（R6 只按高度推出"像半径 16 的圆底"） | Ghidra（`ghidra-projects` 持久工程） | 低 | hb-ch02 |
| B02-8 | **落地条件**（R5-DIFF HB-2）：R5 v_z ≤ 140 就能着地，HSD 要求 v_z < 0。找 v_z 为小正值又碰到能站的面的情况（冲上坡顶又落回坡上、跳板弹到斜面、上坡起跳的第一条命令） | R6 坡 + 起跳；或 Frida 读 `CategorizePosition` 的分支 | 中 | hb-ch02（它的备注里叫 B02-3，和已有编号撞了，改成 B02-8） |

### 03 地面、空中、跳跃

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B03-1 | **coyote time**：走下台边以后还能起跳多久；`jump_graceperiod` 0.2 的读取方没追。Unity 没有通用 coyote | R5：走下台边后第 k 条命令按跳（k = 1 – 30）；Ghidra 追 `jump_graceperiod`（0x14019cc50）的 xref | 高 | hb0；hb-ch03 |
| B03-2 | **跳跃缓冲**：落地前按跳算不算（DEFERRED E3 方案 4）。Unity 没有 | R5：落地前 1 – 6 条命令按跳 | 高 | hb0；hb-ch03 |
| B03-3 | **硬着陆降速**（N2-J J-09）：Unity 实测拟合（M4 Octane 15 次，f0 = clamp(1.9965 − 1.6714e-6·vz²)，折成自由落体高度 397 → 796 u）和原生读法（`landSlowdownHeightMin/Max` 300 → 800 u）**对不上**，起点差约 100 u；`landSlowdownNoSprintFrac` 0.7 的读取方 0x140b02ca0 没读。手册暂按拟合（D-197） | R5：从 300 / 400 / 500 / 800 u 静止落下（不经过跳板），看落地后水平速度和上限；Ghidra 读 player+0x3684 写入处，看"下落高度"怎么定义 | **中**（总控 11-14 从"低"升为"中"） | hb0；hb-ch03 |
| B03-4 | G-09（冲刺 × 1.25 对按键转向）只有代码；`sprintStartDelay` 等冲刺起步键没测到影响；`AirMove` 本体没读（`airDrag` / `airFriction` 怎么取） | 读代码（Ghidra 0x140a48f90）/ R5 | 低 | hb0；hb-ch03 |
| B03-5 | 连跳惩罚开关标志 player+0x36a9 什么时候为真（社区说地面 / coyote / 攀爬 / 跳板跳打开，滑索 / 翻越跳不打开）。Unity 每次地面跳都惩罚，翻越跳、滑索跳后接地面跳会不会多惩罚没核 | Ghidra 读 0x36a9 的写入；R5：翻越落地后马上跳、滑索跳离落地后马上跳 | 中 | hb-ch03（原来在 B03-3 里，拆出来） |
| B03-6 | 斜后方 / 纯侧向能不能冲刺（Unity 要求前后轴 > 0）；冲刺使按键转向 × 0.67（M4b）和 G-09 的关系 | R5：冲刺键 + W+D / D / S+D；冲刺中 W → D 急转对照 N4B | 低 | hb-ch03 |
| B03-7 | 蹲姿 138 u/s 以上的加速；下蹲过渡中的移动速度 | R5：冲刺 180 u/s（不够滑铲）时按蹲 | 低 | hb-ch03 |
| B03-8 | 原生 `Friction` 的 0.5 s 淡入时刻 T（player+0x2a50）是什么 | Ghidra | 低 | hb-ch03 |
| B03-9 | lurch：A 按住再按 S（不同的新键）是否也按合成意图；M8 b1 的 11.6 u/s 残差；手柄（`jump_grace_controller_disable_duration`） | R5 | 低 | hb-ch03 |
| B03-10 | **`R5MotorV2` 没有"最高点"测试**：README 示范原来列的 `ReferenceMotorTests.JumpApexMatchesJumpHeight` 测的是 M1 的 `ReferenceMotor`。要补一个：120 Hz 原地跳最高点 = V²/2g − V·dt/2 + g·dt²/8 ≈ 54.8 u | 不用测，补 Unity EditMode 测试（等 HSD-Unity 下一次改动时顺手做） | 中 | hb-ch03；hb-tables（关卡尺度表实跑 54.8 u） |

### 04 滑铲、翻越

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B04-1 | 翻越的触发几何没读（`AutoMantle_Try` / `AutoMantle_Search` 的距离、角度、高度，`WallClimb_Move`）；Unity 台沿探测参数是设计值；`automantle_cooldown` 0.25 s Unity 没做 | Ghidra 读代码；必要时 R5 接近角 / 距离扫描 | 中 | hb0；hb-ch04（B04-c） |
| B04-2 | > 40°、< 5° 的坡，> 30° 的坡度折角、更高速时会不会离地 | R5 | 低 | hb0；hb-ch04（B04-d） |
| B04-3 | h120 蹲姿短的那种（状态 3）Unity 复现不了；h120 M 类 S27 窗口 0.45 对 0.28 s；滑铲下沉 0.19 对 0.167 s（D-70 只记录；口径问题见 B07-13） | R5 + 分析 | 低 | hb0 |
| B04-4 | 起滑的两个原生条件没读出值：视角前向和速度方向点积 ≥ `slide_max_angle_dot`（ConVar 0.6，D-204）；下蹲比例 < `slide_max_duck_frac_to_start`。另有额外检查 0x140ac1d70 没读 | Ghidra 读一次 setfile / 函数即可 | 中（D-204 要它） | hb-ch04（B04-a） |
| B04-5 | 滑铲摩擦衰减指数的 (1 − 0.75·x)（x 来自 0x140abdc20）、标志 0x1dfc（滑铲减速 = 0）、0x1dfd 的含义；平地上推测不起作用，Unity 没做 | Ghidra | 低 | hb-ch04（B04-b） |
| B04-6 | 起滑加成的大小和 msc 缩放：只测到上限（460）和一次加法分支（255 → 427.5），换传奇 / 武器 msc 没测；现在按 census 150 × msc | R5 新测（低入口速度、第二个 msc） | 中 | hb-ch04（B04-e） |
| B04-7 | 滑铲跳起跳后水平速度 R5 258.x、Unity 260.3（R6 看到，平地也一样，+2 u/s）；04 §4.6 写成已知差别 | 先对照回放查是哪条命令多的 | 低 | hb-ch04（B04-f） |
| B04-8 | 空中按蹲：R5 蹲到底（0.42 s）原点抬高 16.5 u，Unity 不抬（只在翻越探测 / 蹲着翻越里用） | 不用新测，是要不要改 Unity 的决定 | 中 | hb-ch04（B04-g） |
| B04-9 | 蹲着翻越结束的出口速度（是不是也是 299 / 199.525）没单独测；Unity 和站姿一样 | 从 D72 数据可以读，不用新测 | 低 | hb-ch04（B04-h） |
| B04-10 | 翻越路径的形状（Unity 0.75 / 0.6 smoothstep 是 [设计]） | 从 D72 Frida 逐帧原点读出 | 低 | hb-ch04（B04-i） |
| B04-11 | U-3 落地算不算"换地面实体"（原生 `SetGroundEntity` 落地也调）；Unity 保守：不算 | R5 新测（落到道具上的滑铲跳） | 低 | hb-ch04（B04-j） |
| B04-12 | superglide 起跳后为什么还能吃到滑铲加成（原生要求着地）；"切断 / superglide"分界的原生来源（M-03 / M-04 剩余部分） | Frida 读按键时的翻越进度 | 低 | hb-ch04（B04-k） |
| B04-13 | `slideStopSpeed` 125 对 M10 实测 112（NS S-05）：hb-ch04 解释为结束后第一条蹲走命令（124.75 − 1500/120 = 112.25），[推断]，没重跑数据。建议关闭（D-200） | 不用测；用户定 D-200 后划掉 | 低 | hb-tables；hb-ch04 |

### 05 跑墙和外力

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B05-1 | TF2 跑墙 P-a 剩三项：0.5 s 计时从没见到它起作用；墙跳后马上贴另一面墙；窗户辅助的地面起跳 / 墙跳 / lurch 触发（`L:TF2-Research/REF-TESTS-1112.md` P1 – P3，ref-pilot-ai 做到一半） | TF2（先修好 11-12 起的 `no_game` 启动问题） | 中 | hb0 |
| B05-2 | 墙跳排斥：HSD `repelTime` 0.2，TF2 实测无效、原生是死代码（#115），PRESET-DIFF M-2 建议默认关 | 不用测，**等用户定** | 中 | hb0 |
| B05-3 | 快速上升时的二段跳：HSD √(vz² + 22500)，TF2 实测 vz + 150（GAPS A6，PRESET-DIFF M-1） | 不用测，**等用户定** | 中 | hb0 |
| B05-4 | 击退：被炸时正在跑墙 / 钩爪 / 滑索 / 翻越；地面门槛精确值 | R5 或 TF2，可选 | 低 | hb0 |
| B05-5 | 传送门离开后 1.0 s 不能再进没实测（只测到 0.5 s 时还能进） | R5 | 低 | hb0 |
| B05-6 | TF2 本体的跑墙长度和二段跳高度没量过（Unity 关卡尺度表实跑：跑墙三套规则 550 / 536 / 701 u；二段跳 HSD 99.8 u、TF2 规则 114.8 u，用 R5 重力） | TF2（目前启动不了） | 低 | hb-tables |

### 06 动量、仲裁、输入

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B06-1 | R5 同一条命令上多个动作谁赢（翻越 / 跳 / 滑铲 / 钩爪），只在 SG 和翻越跳里零散测过；Unity 的优先级是 HSD 设计（M8-A） | R5 小测，可选 | 中 | hb0 |
| B06-2 | 第一次按方向键轴值 0.5 → 0.75（N2-T T-03）只在回放电机里有，游戏输入 `DirKeys` 没实现 | 不用测，要定 Unity 改不改 | 中 | hb0 |
| B06-3 | 手柄输入没测（`jump_grace_controller_disable_duration` −1） | R5（如果 HSD 支持手柄） | 低 | hb0 |

### 07 镜头

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B07-1 | 二段跳 punch 没有录像（本地角色没有二段跳） | R5（需要能二段跳的角色）或只靠反编译 | 中 | hb0 |
| B07-2 | 墙跑 punch（CAM-03 / 04）只找到函数，S21 关了墙跑 | TF2 实测（只在 HSD 要做墙跑镜头时） | 中 | hb0 |
| B07-3 | rodeo 时钩爪横滚实测 13.9°，公式给 18.5°（`research/rea-native/n10/N10-CAMERA.md` §7）。hb-tables：R5-DIFF C-12（D-42）改成共用 SmoothCD 后 Unity 是 13.7–13.9°，**可能已解决**，等用户确认划掉 | 读代码 + R5 补测（如果不划掉） | 低 | hb0；hb-tables |
| B07-4 | 拉栓 / 泵动动画带镜头只量了 Peacekeeper、Kraber、Longbow，规则没写进 DESIGN-PHILOSOPHY §6.1（`F-GAPS.md` §2，PR #122） | R5 runner 自动跑其他单发枪 | 低 | hb0 |
| B07-5 | 跑步晃动偏航和俯仰的相位是推断 | R5 镜头录像 | 低 | hb0 |
| B07-6 | 跳板、重力炮、抓墙的 punch 数值（CR §8 只知道它们进同两组弹簧） | 只读：反编译调用点 + setfile；R5 跳板可实测 | 中 | hb-ch07 |
| B07-7 | 铁驭被爆炸震屏：R5 是否有、振幅 → 角度的换算、距离衰减 | R5 实测（手雷 / 电弧星在身边爆） | 中 | hb-ch07 |
| B07-8 | 铁驭近战的镜头（C-MOTIONS §6 只量了时间） | R5 镜头录像 | 低 | hb-ch07 |
| B07-9 | Unity 第二组弹簧 / 子弹含 punch1 和开镜 drift / 鼠标抵消（R5-DIFF HB-6 – HB-8） | 不用测，定 Unity 改不改（D-201） | 高 | hb-ch07 |
| B07-10 | 眼高 smoothstep：下蹲曲线函数 0x1409d9750 没读 | 只读反编译 | 低 | hb-ch07 |
| B07-11 | 移动 punch 有没有 0.001 归零门槛（武器弹簧实测有；Unity 移动 punch 不归零，差 < 0.03°） | 只读反编译 0x140a34170 | 低 | hb-ch07 |
| B07-12 | **横滚总上限（待核）**：`N2-C-CAMERA.md` §7 写"总上限 40°"；`CAM2-CAMERA.md` §5、`CAMERA-REFERENCE.md` §3.9 读 `View_CalcRoll` 说没有总上限、±180° 折回（`maxCameraRoll` 40 只封滑索分支 B）。手册 07 §4 和镜头事件表按 CAM2 写（D-53），两边都留 | 只读：再读一次 `View_CalcRoll`，确认 N2-C 的 40° 指的是哪一项；可选 R5 钩爪 + 滑铲同时横滚实测 | 中 | hb-tables；总控 11-14 定"两边都留、待核" |
| B07-13 | 滑铲眼高下沉时间有三个说法：C3 实测 64 → 32 用 0.208–0.213 s（`NativeEyeParams` 注释同）；R5-DIFF 二节"滑铲下沉"R5 约 0.167 s / Unity 约 0.19 s（D-70）；`hullCrouchTime` 0.2 s。可能是"到最低点"和"过渡计时"两种量法 | 不用新测，按同一个口径重算 C3 数据 | 低 | hb-ch04；hb-tables |

### 08 身体动画

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B08-1 | R5 走路晃动（bob）从哪来没找到（MOVEMENT-ANIMATION §10，PR #123） | 读代码，不用开游戏 | 高 | hb0 |
| B08-2 | 转视角时枪的滞后只测了一个转速，俯仰没测（`HOLD-POSE.md` §7，PR #95） | R5：`cl_yawspeed` + runner，便宜 | 中 | hb0 |
| B08-3 | 叠加层的进度和权重读不到；开镜过程的横滚读不到；手臂骨骼（rmdl 解不开） | 反编译 / 工具 | 低 | hb0 |
| B08-4 | 泰坦：13° 以上斜坡没测；轻 / 重冲刺摆动的俯仰和左右没拟合；蹲起镜头过渡是占位；舱内炮没有 bob / sway | TF2（TF2 从 11-12 起启动是 `no_game`，测不了）；TITAN-FEEL §7.2 写了可以先做 | 低 | hb0 |

### 09 战斗手感

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B09-1 | 开镜动画只测了 3 把枪，"手枪窗口宽、步枪窄"是推断（`ADS-CURVES.md` §5，PR #93） | R5 runner 自动跑 | 中 | hb0 |
| B09-2 | 命中 X 在截图里没认出来，伤害数字只有脚本 | R5 射击场打开"显示命中标记"再截图 | 中 | hb0 |
| B09-3 | 蹲、走、滑铲下的 kick 缩放主要靠字段（DESIGN-PHILOSOPHY §10.2 #2） | R5 | 中 | hb0 |
| B09-4 | R-301 开镜回落慢 0.04 s 的原因（`B5-ADS-RECOVERY.md`，PR #123） | R5 | 低 | hb0 |
| B09-5 | 可变倍率第二档切不出来；Kinetic Loader 滑铲装填没测成；枪口焰亮度没测成 | R5 | 低 | hb0 |
| B09-6 | TF2 铁驭枪的画面弹簧（`springs.txt`）没有实测 | TF2（目前启动不了） | 低 | hb0 |

### 10 技能和 AI

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B10-1 | P9"威力换预告"证据最弱：预告时长只读过脚本，而且是多人游戏数值 | R5：核对 2–3 个技能（滚雷、Focus of Attention） | 低 | hb0 |
| B10-2 | 没有跨 R5 技能 / TF2 泰坦套件的统一"新技能怎么写"模板（`SYSTEM-RECORD-TEMPLATE.md` 只描述 R5，泰坦用 `KitDef`） | 不用测，设计工作（hb-ch10） | 中 | hb0 |
| B10-3 | AI：快速移动时中远距离命中率样本太少（AI1）；High / VeryHigh 档（AI2）。`TF2-Research/runtime/ref-pilot-ai/` 只有脚本，**AI1–AI6 没有结果** | TF2（目前启动不了） | 低（只影响验收表） | hb0 |
| B10-4 | Frontier Defense 每波刷什么：本地 Northstar 服务端是空壳，用户 11-09 定不再找 | — | 到此为止（11-09，用户定） | hb0 |

### 11 验收

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| B11-1 | 跑圈时间没有 R5 参照，只能当 HSD 自己的回归 | R5 跑同一条路线（要先在 R5 里搭出来） | 低 | hb0 |
| B11-2 | 技能、道具、AI 没有和 R5 / TF2 叠图的自动验收，只有单元测试 | 不用新测，缺对比脚本 | 中 | hb0 |
| B11-3 | Tf2 预设有 3 处和 TF2 对不上（`tf2/runtime/PRESET-DIFF-1109.md`），修复只在本地工作树 `HSD-Unity-PRESETFIX`（分支 `tf2/preset-fix-1109`，有没提交的改动，**没推送、没有 PR**） | 不用测，要有人收尾 | 中 | hb0 |
| B11-4 | 关卡尺度表（`tables/level-scale.tsv`）只有 Unity 的数：在 R5 里搭和 `level_scale_harness` 一样的几何（平地跳远、最高墙、坡上滑铲距离），跑一次对照 | R5 | 低 | hb-tables |

### 附录 A 研究方法

| # | 缺什么 | 要在哪测 | 优先级 | 来源 |
|---|---|---|---|---|
| BA-1 | Frida 没有独立的方法文档，用法散在各份报告里 | 不用测，整理 | 中 | hb0 |
| BA-2 | 整体方法文档只有本地 `TECH-REPORT-1104/01-方法论和工具.md`，不在 git | 不用测，整理进附录 A | 中 | hb0 |
