# hb-ch03 备注（给总控、hb-integrate、hb-tables、别章）

会话 hb-ch03，2026-11-14。分支 `handbook/ch03`（从 `origin/handbook/base` d93f012）。只写了 `handbook/03-ground-air-jump.md` 和本文件。

## 1. 本章写了哪些条目

3.0 共同约定（参考实现 = `MovementConfigs.Reference()`、msc、命令和时间）；地面 3.1 速度上限、3.2 三段加速、3.3 冲刺、3.4 摩擦 / 减速 / 转向、3.5 蹲走；空中 3.6 空中加速和转向、3.7 重力和半步积分；跳跃和落地 3.8 起跳（README 示范条目搬入并补全）、3.9 落地（含硬着陆降速）；时间窗口 3.10 兔跳时机、3.11 起跳缓冲、3.12 coyote time、3.13 窗口总表（P4）；3.14 lurch、3.15 tap strafe 和 LS / RAS；本章参数总表；缺口。

## 2. 待研究（不改 99-TODO-RESEARCH.md，由整合会话合并）

| 编号建议 | 内容 | 做法 | 优先 |
|---|---|---|---|
| B03-1（已有） | coyote time；`jump_graceperiod` 0.2 的读取方 | R5：走下台边后第 k = 1 – 30 条命令按跳；Ghidra 追 `jump_graceperiod`（0x14019cc50）的 xref | 高 |
| B03-2（已有） | 起跳缓冲 | R5：落地前 1 – 6 条命令按跳 | 高 |
| B03-3（已有，**建议升为中**） | 硬着陆降速：Unity 实测拟合（M4 Octane 15 次，f0 = clamp(1.9965 − 1.6714e-6·vz²)，折成自由落体高度是 397 → 796 u）和原生读法（`landSlowdownHeightMin/Max` 300 → 800 u）**对不上**；`landSlowdownNoSprintFrac` 0.7 的读取方 0x140b02ca0 没读 | R5：从 300 / 400 / 500 / 800 u 静止落下（不经过跳板），看落地后水平速度和上限；Ghidra 读 player+0x3684 写入处，看"下落高度"怎么定义 | 中 |
| B03-5（新） | 连跳惩罚开关标志 player+0x36a9 什么时候为真（社区说地面 / coyote / 攀爬 / 跳板跳打开，滑索 / 翻越跳不打开）。Unity 每次地面跳都惩罚，翻越跳、滑索跳后接地面跳会不会多惩罚没核 | Ghidra 读 0x36a9 的写入；R5：翻越落地后马上跳、滑索跳离落地后马上跳 | 中 |
| B03-6（新） | 斜后方 / 纯侧向能不能冲刺（Unity 要求前后轴 > 0）；G-09 冲刺 × 1.25 对按键转向的影响（M4b 说冲刺使按键转向 × 0.67） | R5：冲刺键 + W+D / D / S+D；冲刺中 W → D 急转对照 N4B | 低 |
| B03-7（新） | 蹲姿 138 u/s 以上的加速；下蹲过渡中的移动速度 | R5：冲刺 180 u/s（不够滑铲）时按蹲 | 低 |
| B03-8（新） | 原生 `Friction` 的 0.5 s 淡入时刻 T（player+0x2a50）是什么 | Ghidra | 低 |
| B03-9（新） | lurch：A 按住再按 S（不同的新键）是否也按合成意图；M8 b1 的 11.6 u/s 残差；手柄（`jump_grace_controller_disable_duration`） | R5 | 低 |
| B03-4（已有） | `AirMove` 本体（`airDrag` / `airFriction` 怎么取） | Ghidra 0x140a48f90 | 低 |

## 3. 发现的过时 / 矛盾（以哪个为准）

| 文档 | 说法 | 以什么为准 |
|---|---|---|
| `handbook/README.md` 示范条目"实现模板"最后一段 | "照这个顺序做，跳到顶的高度才正好等于 `jumpHeight`" | **不对**：AJ §2.3 实测最高点 54.951 u（144 fps），公式 V²/2g − V·dt/2 + g·dt²/8，比 56 低约 1 u，且和帧率有关（60 fps 约 53.6）。03 §3.8 已改写。建议 README 示范条目同步改 |
| `handbook/README.md` 示范条目"验收" | 列了 `R5ReplayTests.JumpApexMatchesJumpHeight`（≤ 0.25 u） | 这个测试在类 `ReferenceMotorTests`，测的是 M1 的 `ReferenceMotor`，不是 `R5MotorV2`。`R5MotorV2` 没有最高点测试。测试名的类也不对：`R5MotorV2Tests.xxx` 实际类名是 `R5MotorV2FormulaTests`（文件 `R5MotorV2Tests.cs`）。03 章已用真实类名 |
| `handbook/README.md` 示范条目表 | 参数写的是 R5 键名 `antiMultiJumpTimeMin` / `TimeMax` 0.15 / 0.75 | Unity 字段是 `multiJumpHoldT0` 0.15 和 `multiJumpRampT` **0.60**（= TimeMax − TimeMin）。hb-tables 对照时注意这一行不是同一个量 |
| `research/DESIGN-PHILOSOPHY.md` §8.1 | 冲刺加速 115 u/s² | 117.3（census 102 × 1.15，GM §3.3；T0 smoke census 读到 100 → 115）。Unity 用 102 |
| `DEFERRED-DESIGN-TODO.md` E3"现有行为" | Reference 兔跳出口 min(v0, 299) | N7 起 Reference 是 max(299, v − 100)（`groundJumpSkipReduce` 100）；min 只剩回放电机 |
| `DEFERRED-DESIGN-TODO.md` E3"代码位置" | `Runtime/Skills/JumpArbitration.cs` | `Abilities/_Core/JumpArbitration.cs`（00-INVENTORY 已列） |
| `R5MotorV2Params.cs` 字段注释 | `groundJumpClampToSprintCap` 写着"Ground jump leaves at min(v_h, sprintspeed·msc)" | 只是回放电机的旧规则；Reference 被 `groundJumpSkipReduce` 覆盖。注释没错但容易误读 |
| 跳跃速度公式里的 g | 原生 / TF2：V = √(2·`sv_gravity`·H)，**不乘 `gravityScale`**（NJ §1.1、TF §4.1）；Unity：`JumpSpeed(h, frac, g)` 的 g = `svGravity × gravityScale` | R5 `gravityScale` = 1，现在没有区别。以后谁改 `gravityScale`（例如泰坦或 Fun）要先定用哪一种；建议 D 行 |
| 任务说明（总控） | "Unity 参考实现是 `R5MotorV2` + `R5Reference()` 配置" | 本章的原生规则（超速连跳 −100、空中额外加速、固定冲刺边界、起跳朝墙推、lurch 0.7 × 冲刺上限、1100 截断）**只在 `MovementConfigs.Reference()` 里打开**，`R5Reference()` 单独用是回放电机（D-66 尺子）。03 §3.0 写清楚了。建议 README 或 01 统一一句话 |

## 4. 想改 README / 表 / 别章的地方

- **README**：示范条目照上表三处改（最高点、测试类名、`multiJumpRampT`）。建议在写法规范第 5 条加一句"测试名写 `类名.方法名`，类名以 C# 里的 `class` 为准，不是文件名"。
- **hb-tables**：03 章末尾有"本章参数总表"（Unity 字段 ↔ R5 键 ↔ 值）。两处单位要注意：`LandingSlowdownParams.b` 是 (u/s)⁻²，换米要除以 0.0254²（= × 1550）；`multiJumpRampT` 是时长差不是 TimeMax。
- **第 02 章（hb-ch02）**：03 引用了 02 的每帧顺序、2 u 落地探测、碰撞体；`groundProbe` 2 u 是 [推断：Source CategorizePosition]，AJ §2.3 用落地命令离地 0.255–1.982 u 支持。落地那条命令是空中命令、下一条才走地面规则——兔跳保速（03 §3.10）靠这一点，02 写顺序时请保持一致。
- **第 04 章（hb-ch04）**：03 §3.8 的起跳只写到"滑铲中用 `slideJumpHeight`"；滑铲跳水平速度（退还、350 下限）、`jumpSurfacePush` 对 superglide 的作用在 04。03 §3.5 写了 `slideRequiredStartSpeed` 200 是起滑门槛。
- **第 05 章（hb-ch05）**：哪些起跳重开 lurch 窗口（蹬墙弹跳、二段跳、跑墙跳、滑索跳离）、哪些外力不开（跳板、升降梯弹出；Reference `padLaunchOpensLurchWindow` / `liftEjectOpensLurchWindow` false），滑索 super jump 0.2、钩爪附加跳 0.15 / 0.2 s 不要当 coyote。
- **第 06 章（hb-ch06）**：03 用到但归 06 的：键盘第一次按下轴值 0.5 → 0.75（R5 有，HSD 游戏输入第一条就给 1）；`DirKeys` / `TapKey` 每键独立的按下沿；跳跃仲裁里"被拒绝的按下沿直接丢掉"（= 没有缓冲）；TF2 受冲击后低摩擦。如果以后做缓冲或 coyote，位置在仲裁层（03 §3.11、§3.12 有建议）。
- **第 07 章（hb-ch07）**：冲刺眼高下沉、落地 kick 都在 07；03 §3.9 只写了落地对速度的影响。
- **第 11 章（hb-ch10）**：03 每项的合格线引用了 FEEL §2 的容差和 GM / AJ / A1 的逐命令误差水平，可以直接收进合格线总表。

## 5. 建议的 D-xx（编号留空）

- **D-??** 手册第 03 章的"Unity 参考实现"定为 `MovementConfigs.Reference()`（`R5MotorV2` + `R5Reference()` + N7 原生开关），回放电机 `R5Reference()` 只当尺子（沿用 D-66）。选中：Reference。没选：以回放电机为准（理由：缺 6 条原生规则，和 R5 在高速兔跳、lurch 上限、空中残余增益上不一致）。
- **D-??** 硬着陆降速两种写法并存：手册暂以 Unity 实测拟合（M4 Octane 15 次，rms 1e-4）为准；原生读法（300 → 800 u 高度）留档；等 B03-3 实测定。选中：实测拟合。没选：原生读法（理由：没有实测，起点差约 100 u）。
- **D-??** 起跳速度公式里的重力：R5 / TF2 原生用 `sv_gravity`、不乘 `gravityScale`；Unity 乘。现在 `gravityScale` = 1，不改代码；以后改 `gravityScale` 之前先按原生改（建议），否则跳跃高度会随 `gravityScale` 变。待用户定。
- 不新增决定：coyote time、起跳缓冲仍按 D-09 暂缓，手册只写"R5 没测、HSD 没有"。

## 6. 给总控的问题

1. 任务说明写"Unity 参考实现是 `R5MotorV2` + `R5Reference()`"，但本章的原生规则只在 `MovementConfigs.Reference()` 里打开。我按后者写了（03 §3.0），请确认各章统一这样写。
2. 硬着陆降速（J-09）放在 03 §3.9 了（00-INVENTORY 把 J-09 列在 03）。如果总控想把它挪到 06 的动量总表，03 留一个指针即可。
3. B03-3 建议从"低"升为"中"：现在 Unity 拟合和原生读法差约 100 u 的起点，影响所有高处落下的手感。
