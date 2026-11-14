# 99 待研究清单

hb0 建（2026-11-14）。各章会话发现新的缺口，写进自己的 `_notes/<会话名>.md`，由 hb-integrate 合进来。

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

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B01-1 | **R5 碰撞体尺寸没测**：站立 32 × 32 × 72 u 和蹲姿 48 u 都是 HSD 设计值（Source 默认）。`airUnduckDrop` 16.5 u 推出的蹲高是 55.5 u 或 39 u，和 48 都对不上。参考身高 H 也依赖站立高度 | R5：Frida 读 `GetPlayerMins/Maxs`，或钻不同高度的缝 | 高 |
| B01-2 | **台阶高度对不上**：R5 setfile `stepHeight` 22 u，HSD `MovementWorld.stepUp` 18 u（等于 TF2 的值），R5-DIFF 没有这一条 | 先查代码和录像（不用开游戏），确认后补 R5-DIFF；必要时 R5 台阶实测 | 高 |

### 02 底层

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B02-1 | 台阶梯 18 / 20 / 22 / 24 u + 蹲姿头顶间隙，一次回答 B01-1 和 B01-2 | R5，便宜 | 高 |
| B02-2 | 不滑铲时在坡上走（非冲刺）没单独测；能站的最陡坡 0.7 只有源码 | R5，可选 | 低 |
| B02-3 | tick：R5 可变帧时长、Unity 固定 1/120，没有 D 号也没进 R5-DIFF §三 | 不用测，定 D 号（写进 `_notes`） | 中 |

### 03 地面、空中、跳跃

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B03-1 | **coyote time**：走下台边以后还能起跳多久；`jump_graceperiod` 0.2 的读取方没追。Unity 没有通用 coyote | R5：走下台边后第 k 条命令按跳（k = 1 – 30） | 高 |
| B03-2 | **跳跃缓冲**：落地前按跳算不算（DEFERRED E3 方案 4）。Unity 没有 | R5：落地前 1 – 6 帧按跳 | 高 |
| B03-3 | 落地减速（N2-J J-09）只有代码，没从高处落下测过；连跳惩罚开关标志 player+0x36a9 何时为真没读 | R5：300 / 500 / 800 u 落下；读代码 | 低 |
| B03-4 | G-09（冲刺 × 1.25 对按键转向）只有代码；`sprintStartDelay` 等冲刺起步键没测到影响；`AirMove` 本体没读 | 读代码 / R5 | 低 |

### 04 滑铲、翻越

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B04-1 | 翻越的触发几何没读（`AutoMantle_Try` / `AutoMantle_Search` 的距离、角度、高度，`WallClimb_Move`）；Unity 台沿探测参数是设计值 | Ghidra 读代码；必要时 R5 接近角 / 距离扫描 | 中 |
| B04-2 | > 40° 的坡、> 30° 的坡度折角、更高速时会不会离地 | R5 | 低 |
| B04-3 | h120 蹲姿短的那种（状态 3）Unity 复现不了；h120 M 类 S27 窗口 0.45 对 0.28 s；滑铲下沉 0.19 对 0.167 s（D-70 只记录） | R5 + 分析 | 低 |

### 05 跑墙和外力

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B05-1 | TF2 跑墙 P-a 剩三项：0.5 s 计时从没见到它起作用；墙跳后马上贴另一面墙；窗户辅助的地面起跳 / 墙跳 / lurch 触发（`L:TF2-Research/REF-TESTS-1112.md` P1 – P3，ref-pilot-ai 做到一半） | TF2（先修好 11-12 起的 `no_game` 启动问题） | 中 |
| B05-2 | 墙跳排斥：HSD `repelTime` 0.2，TF2 实测无效、原生是死代码（#115），PRESET-DIFF M-2 建议默认关 | 不用测，**等用户定** | 中 |
| B05-3 | 快速上升时的二段跳：HSD √(vz² + 22500)，TF2 实测 vz + 150（GAPS A6，PRESET-DIFF M-1） | 不用测，**等用户定** | 中 |
| B05-4 | 击退：被炸时正在跑墙 / 钩爪 / 滑索 / 翻越；地面门槛精确值 | R5 或 TF2，可选 | 低 |
| B05-5 | 传送门离开后 1.0 s 不能再进没实测（只测到 0.5 s 时还能进） | R5 | 低 |

### 06 动量、仲裁、输入

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B06-1 | R5 同一条命令上多个动作谁赢（翻越 / 跳 / 滑铲 / 钩爪），只在 SG 和翻越跳里零散测过；Unity 的优先级是 HSD 设计（M8-A） | R5 小测，可选 | 中 |
| B06-2 | 第一次按方向键轴值 0.5 → 0.75（N2-T T-03）只在回放电机里有，游戏输入 `DirKeys` 没实现 | 不用测，要定 Unity 改不改 | 中 |
| B06-3 | 手柄输入没测（`jump_grace_controller_disable_duration` −1） | R5（如果 HSD 支持手柄） | 低 |

### 07 镜头

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B07-1 | 二段跳 punch 没有录像（本地角色没有二段跳） | R5（需要能二段跳的角色）或只靠反编译 | 中 |
| B07-2 | 墙跑 punch（CAM-03 / 04）只找到函数，S21 关了墙跑 | TF2 实测（只在 HSD 要做墙跑镜头时） | 中 |
| B07-3 | rodeo 时钩爪横滚实测 13.9°，公式给 18.5°，没查（`research/rea-native/n10/N10-CAMERA.md` §7） | 读代码 + R5 补测 | 低 |
| B07-4 | 拉栓 / 泵动动画带镜头只量了 Peacekeeper、Kraber、Longbow，规则没写进 DESIGN-PHILOSOPHY §6.1（`F-GAPS.md` §2，PR #122） | R5 runner 自动跑其他单发枪 | 低 |
| B07-5 | 跑步晃动偏航和俯仰的相位是推断 | R5 镜头录像 | 低 |

### 08 身体动画

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B08-1 | R5 走路晃动（bob）从哪来没找到（MOVEMENT-ANIMATION §10，PR #123） | 读代码，不用开游戏 | 高 |
| B08-2 | 转视角时枪的滞后只测了一个转速，俯仰没测（`HOLD-POSE.md` §7，PR #95） | R5：`cl_yawspeed` + runner，便宜 | 中 |
| B08-3 | 叠加层的进度和权重读不到；开镜过程的横滚读不到；手臂骨骼（rmdl 解不开） | 反编译 / 工具 | 低 |
| B08-4 | 泰坦：13° 以上斜坡没测；轻 / 重冲刺摆动的俯仰和左右没拟合；蹲起镜头过渡是占位；舱内炮没有 bob / sway | TF2（TF2 从 11-12 起启动是 `no_game`，测不了）；TITAN-FEEL §7.2 写了可以先做 | 低 |

### 09 战斗手感

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B09-1 | 开镜动画只测了 3 把枪，"手枪窗口宽、步枪窄"是推断（`ADS-CURVES.md` §5，PR #93） | R5 runner 自动跑 | 中 |
| B09-2 | 命中 X 在截图里没认出来，伤害数字只有脚本 | R5 射击场打开"显示命中标记"再截图 | 中 |
| B09-3 | 蹲、走、滑铲下的 kick 缩放主要靠字段（DESIGN-PHILOSOPHY §10.2 #2） | R5 | 中 |
| B09-4 | R-301 开镜回落慢 0.04 s 的原因（`B5-ADS-RECOVERY.md`，PR #123） | R5 | 低 |
| B09-5 | 可变倍率第二档切不出来；Kinetic Loader 滑铲装填没测成；枪口焰亮度没测成 | R5 | 低 |
| B09-6 | TF2 铁驭枪的画面弹簧（`springs.txt`）没有实测 | TF2（目前启动不了） | 低 |

### 10 技能和 AI

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B10-1 | P9"威力换预告"证据最弱：预告时长只读过脚本，而且是多人游戏数值 | R5：核对 2–3 个技能（滚雷、Focus of Attention） | 低 |
| B10-2 | 没有跨 R5 技能 / TF2 泰坦套件的统一"新技能怎么写"模板（`SYSTEM-RECORD-TEMPLATE.md` 只描述 R5，泰坦用 `KitDef`） | 不用测，设计工作（hb-ch10） | 中 |
| B10-3 | AI：快速移动时中远距离命中率样本太少（AI1）；High / VeryHigh 档（AI2）。`TF2-Research/runtime/ref-pilot-ai/` 只有脚本，**AI1–AI6 没有结果** | TF2（目前启动不了） | 低（只影响验收表） |
| B10-4 | Frontier Defense 每波刷什么：本地 Northstar 服务端是空壳，用户 11-09 定不再找 | — | 到此为止（11-09，用户定） |

### 11 验收

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| B11-1 | 跑圈时间没有 R5 参照，只能当 HSD 自己的回归 | R5 跑同一条路线（要先在 R5 里搭出来） | 低 |
| B11-2 | 技能、道具、AI 没有和 R5 / TF2 叠图的自动验收，只有单元测试 | 不用新测，缺对比脚本 | 中 |
| B11-3 | Tf2 预设有 3 处和 TF2 对不上（`tf2/runtime/PRESET-DIFF-1109.md`），修复只在本地工作树 `HSD-Unity-PRESETFIX`（分支 `tf2/preset-fix-1109`，有没提交的改动，**没推送、没有 PR**） | 不用测，要有人收尾 | 中 |

### 附录 A 研究方法

| # | 缺什么 | 要在哪测 | 优先级 |
|---|---|---|---|
| BA-1 | Frida 没有独立的方法文档，用法散在各份报告里 | 不用测，整理 | 中 |
| BA-2 | 整体方法文档只有本地 `TECH-REPORT-1104/01-方法论和工具.md`，不在 git | 不用测，整理进附录 A | 中 |
