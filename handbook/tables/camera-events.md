# 镜头事件表

由 hb-tables 写（2026-11-14）。**原件是同目录的 [`camera-events.tsv`](camera-events.tsv)**（76 行，17 列，UTF-8，制表符分隔；第 3 列"第 07 章事件名"是 [07 §0.5](../07-camera.md) 的英文事件名，用来和第 07 章互相查，hb-integrate 11-14 加），这一页是照着它手写的给人看的版本，只留了最常用的几列。两边对不上时以 TSV 为准；改数先改 TSV，再改这一页。

## 白话说明

**镜头事件**就是"玩家做了一个动作，镜头跟着动一下"：起跳时画面往下点一下、落地时往下砸、滑铲时视野变宽、冲刺转弯时画面往弯里歪。每一种事件只动镜头，不动准星：瞄准角永远只来自鼠标（R5 实测 26 次落地瞄准角一次都没变）。

**这张表怎么读**：一行是"一个事件 × 一个通道"。通道只有六种：俯仰（上下点头）、偏航（左右转头）、横滚（歪头）、位移、眼高、FOV。一个事件动几个通道就有几行，比如起跳 punch 有俯仰、偏航、横滚三行。每行写 R5 的原值、Unity 现在的值，再判断"和 R5 一致吗"：一致 / 不一致 / 只有 HSD / 没测过。R5 没测过的也留着，写明为什么没测。

**组合规则一句话**：R5 的所有"一下子"的事件（落地、起跳、二段跳、下滑索、开枪）都不直接改角度，而是往**同一套弹簧**里加一个角速度冲量。弹簧是欠阻尼的：刚度 **65**、阻尼 **9**（阻尼比 0.558），所以踢一下 0.146 s 到峰、0.47 s 过零、回弹约 12 %，大约 1 s 回正。弹簧有两组：第一组全收；第二组同时收 0.2 倍，空手时也是 65 / 9，拿枪时换成这把枪的武器弹簧（武器开火的 kick 也写在第二组）。因为弹簧是线性的，**几个事件同时发生就是简单相加**，没有谁优先、谁取消谁，也**没有总上限**；落地马上再跳，镜头就是落地 kick 加起跳 punch（R5 5.0–5.6°）。持续的效果（眼高、滑铲倾斜、冲刺倾斜、钩爪 / 滑索横滚、drift、跑步晃动）也是加在各自那一行上。唯一"封顶"的是每一项自己：滑铲倾斜 15°、冲刺倾斜 2°、钩爪横滚 20°、滑索横滚 25° × 0.7；横滚总和按 360° 折回 ±180°，**不夹 ±40°**（`maxCameraRoll` 40 只封滑索分支 B 自己那一项，S21 不走分支 B）。唯一的"三选一"是绳子横滚：钩爪 > 滑索 > 摆荡，共用一个平滑状态，切换时不跳。

## 单位

- 长度、速度按 [01 §2](../01-units-body.md) 换算：1 u = 0.0254 m，身高比例除以 H = 72 u。角度（°）、时间（s）、角速度（°/s）、比例、弹簧常数不换算，`[m]` 和身高比例写"—"。
- 落地 kick 的两个键是**英尺**：`viewkickFallDistMin` 10 ft、`Max` 70 ft，先 × 12 到 u（120 u、840 u）再算速度门槛。
- kick 一列写的是"往弹簧角速度里加多少 °/s"，r ∈ [−0.5, 0.5] 是按命令号取的确定性随机数；画面上的峰值 ≈ 0.0771 × 俯仰冲量（两组合计，空手）。
- Unity 的参数名后面标 `[u]` 的是长度或速度，全部是 u 模式的值（`HSD-Unity: Docs/units/units-params.tsv` 的 `camera.native.*`、`camera.m55.*` 行）。

## 表

### 起跳 / 落地

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-01 | 起跳 punch | 俯仰 | 冲量 (2 + r)·20 °/s；峰值 2.3–3.9°，0.146 s | `jumpPitchBase` 2、`jumpPitchRandom` 1；15 片段差 ≤ 0.15° | 一致 |
| CE-02 | 起跳 punch | 偏航 | r·20 °/s；≤ 0.77° | `jumpYawRandom` 1 | 一致 |
| CE-03 | 起跳 punch | 横滚 | (0.9 + 0.5r)·20 °/s；1.0–1.8° 向右 | `jumpRollBase` 0.9、`jumpRollRandom` 0.5 | 一致 |
| CE-04 | 二段跳 punch | 俯仰 | (4.5 + r)·20 °/s；6.2–7.7° [算]；**没有录像** | `doubleJumpPitchBase` 4.5（D-68） | 没测过 |
| CE-05 | 二段跳 punch | 偏航 | r·20 °/s；≤ 0.77° [算] | `doubleJumpYawRandom` 1 | 没测过 |
| CE-06 | 二段跳 punch | 横滚 | 2r·20 °/s；≤ 1.54° [算] | `doubleJumpRollRandom` 2 | 没测过 |
| CE-07 | 落地 kick | 俯仰 | s·(2 + 0.75r)·20 °/s；v_min 424.3 u/s（10.78 m/s）、v_max 1122.5 u/s（28.51 m/s），s 到 12 封顶；0.89–44° | `kickFallDistMinFt` 10、`MaxFt` 70、`kickMaxScale` 12；R5 随机数逐次对上 | 一致 |
| CE-08 | 落地 kick | 横滚 | s·r·20 °/s；s = 12 时 ≤ 9.25° | 同上 | 一致 |
| CE-09 | 水中落地 | 俯仰 | s × 0.2 [反编译]；训练场没有水 | 没有（练习场没有水） | 没测过 |
| CE-10 | 落地马上再跳 | 俯仰 | 4.96–5.56°（两个相加） | 5.01–5.56° | 一致 |
| CE-11 | 滑铲跳落地 kick | 俯仰 | 1.8–2.4° | 1.7–2.4°（D-71 更正） | 一致 |
| CE-12 | 跳板起跳（launch） | 俯仰 | 列为 punch 事件，值没读 | 没有 | 没测过 |
| CE-13 | 重力炮、抓墙、墙跑开始 / 超时 punch | 俯仰 | 函数已定位，值没读；S21 墙跑关 | 没有 | 没测过 |

### 滑铲

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-14 | 滑铲开始 | 俯仰 | 没有找到 punch [推断] | 没有（M5.5 有 FOV kick 4°） | 一致 |
| CE-15 | 滑铲倾斜 | 横滚 | −15° × (S · 视角右方)；125 → 400 u/s（3.175 → 10.16 m/s）；增 5 / 减 2.5 每秒；转视角 30° 时 6.35° | `slideTilt*` 同值；测试 6.36 ± 1.2 | 一致 |
| CE-16 | 滑铲 FOV | FOV | 4:3 水平 FOV × 1.1，进出各 0.25 s 线性 | `slideFovScale` 1.1 | 一致 |
| CE-17 | 滑铲眼高下沉 | 眼高 | 64 / 70 u → 32 u，计时 0.2 s，smoothstep | `slideDuckTime` 0.2；到底约 0.19 s（R5-DIFF 记 R5 0.167 s） | 不一致 |
| CE-18 | 下蹲 / 起身眼高 | 眼高 | 70 u（1.778 m，0.972 H）↔ 32 u（0.813 m，0.444 H），0.4 s | `standEye` 70、`crouchEye` 32、`duckTime` 0.4 | 一致 |

### 冲刺

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-19 | 冲刺眼高下沉 | 眼高 | 70 − 6·sin(f·π/2)；−6 u = −0.152 m；等 0.16 s 后每秒 1.25，停下等 0.11 s 后每秒 6.67 | `sprintOffset` −6 等同值 | 一致 |
| CE-20 | 冲刺转向倾斜 | 横滚 | 2° × n，n 目标 = 转速 / 120 °/s；60 °/s → 1.0°，120 °/s → 2.0° | `sprintTilt*` 同值 | 一致 |
| CE-21 | 跑步晃动 | 俯仰 | 每步 0.28 s，±0.25°，> 200 u/s（5.08 m/s），每秒 20 淡入 | `sway*` 同值（K-3） | 一致 |
| CE-22 | 跑步晃动 | 偏航 | 两步一周期，−0.085 … +0.806°；相位 [推断] | `swayYawMid` 0.36、`swayYawAmp` 0.445 | 一致 |
| CE-23 | 侧移横滚 | 横滚 | 没有（`sv_rollangle` 0） | 原生没有；M5.5 有 1.5° | 一致 |

### 跑墙 / 钩爪 / 滑索

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-24 | 墙跑倾斜（R5 代码值） | 横滚 | 10°、每秒 6 [反编译]；S21 墙跑关 | `wallRunMaxTilt` 10、`wallRunTiltSpeed` 6（M7） | 没测过 |
| CE-25 | 墙跑倾斜（TF2 规则 P-05） | 横滚 | TF2：B 10° / A 15°，速度 6，提前 0.25 s | 默认关；没有提前量 | 不一致（对 TF2） |
| CE-26 | 闪避倾斜 | 横滚 | S21 没有闪避 | 没有 | 没测过 |
| CE-27 | 钩爪横滚 | 横滚 | 距离 150 u（3.81 m）× 视角 65° × 方位，封顶 20°；共用 SmoothCD ω 6.667 | 同公式；rms 0.24–0.45°，rodeo 峰值 13.7–13.9°（R5 13.9°） | 一致 |
| CE-28 | 滑索横滚 | 横滚 | 分支 A，强度 0.7、视角 30–50°、封顶 25°；绳上点水平投影 | 同公式；10 / 10 | 一致 |
| CE-29 | 滑索眼睛偏移 | 位移 | Perlin 噪声，±5 u（±0.127 m），ω 4 | `zipOffsetNoise` 5 等同值 | 一致 |
| CE-30 | 滑索眼高 | 眼高 | −13 … −4 u；1–2 s 降 5–9 u（0.127–0.229 m） | 65.57–65.87 u（R5 65.47–65.88） | 一致 |
| CE-31 | 下滑索 punch | 俯仰 | (10 + 3r)·20 °/s；14–18° | 逐次差 ≤ 0.05°（一次早一条命令下绳，差 1.1°） | 一致 |
| CE-32 | 下滑索 punch | 偏航 | 10r·20 °/s；实测 1.5–6.6° | `zipDetachYawRandom` 10 | 一致 |
| CE-33 | 下滑索 punch | 横滚 | 10r·20 °/s；实测 ±1–7° | `zipDetachRollRandom` 10 | 一致 |
| CE-34 | 摆荡横滚 | 横滚 | S21 Pathfinder 不能摆荡 | 没有 | 没测过 |
| CE-35 | 滑索倾斜（bank tilt） | 横滚 | 值没读，没实测 | 没有 | 没测过 |

### 翻越

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-36 | 翻越镜头 | 俯仰 | 跟翻越动画的镜头挂点；h80（2.03 m）6.0–6.9°，h120（3.05 m）4.5–5.3°，h200（5.08 m）5.3–5.8° | B1 曲线；h80 7.4–7.8°，h120 4.6°，h200 4.8°；时刻对上 | 不一致 |
| CE-37 | 翻越镜头淡入 | 俯仰 | 0.15 s SimpleSpline；第一帧 −0.10 … +0.18° | `traversalLerpIn` 0.15；第一帧 −0.09 … +0.02° | 一致 |
| CE-38 | 蹲着翻越的镜头时刻 | 俯仰 | h120 蹲有短 / 长两种（约 1 / 4 短） | 总是长的；平均差 0.19–0.22 s | 不一致 |
| CE-39 | 翻越镜头淡出 | 俯仰 | 开着，形状没读 | 没有单独淡出 | 没测过 |

### 持续型（drift / sway 等）

| id | 事件 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-40 | 站立 drift | 俯仰 | ±0.195°，5.2 s；< 10 u/s（0.254 m/s）时 | 同值 | 一致 |
| CE-41 | 站立 drift | 偏航 | ±0.084°，3.2 s | 同值 | 一致 |
| CE-42 | 开镜 drift | 俯仰 | 俯仰最大 0.29°、偏航 0.21°；也进子弹 | 没做 | 不一致 |
| CE-43 | cockpit sway（CAM-18） | 位移 | 只动手臂和枪，不动镜头 | 镜头里没有 | 一致 |
| CE-44 | cockpit 弹簧（CAM-19） | 位移 | S21 一直是 0 | 没有 | 一致 |
| CE-45 | 屏幕震动（CAM-21） | 位移 | 有，由脚本 / 动画的世界事件触发；移动和开枪不触发 | 没接（空投舱震动只存数据） | 不一致 |
| CE-46 | 上升气流震动（CAM-23） | 位移 | 函数没定位 | 没有 | 没测过 |

### 武器

| id | 事件 | 通道 | R5 | Unity 现在（HSD-Unity PR #67，还没合并） | 一致吗 |
|---|---|---|---|---|---|
| CE-47 | 开火 kick | 俯仰 | 第二组：Δ角度 = hard × kick，Δ角速度 = soft × 20 × kick；R-301 腰射第 1 / 5 / 20 发 ÷ 表 2.10 / 1.86 / 0.57 | `ViewKick`；2.07 / 1.88 / 0.52 | 一致 |
| CE-48 | 开火 kick | 偏航 | 表第 1 列负数 = 向右 | 方向按 R5（D-88 改掉镜像） | 一致 |
| CE-49 | 开火 kick | 横滚 | 自己一根弹簧（R-301 k 20000 / d 22），≤ 0.45–0.58°，进画面 1 × | 同规则 | 一致 |
| CE-50 | 腰射 / 开镜的武器弹簧 | 俯仰 | 按热度和 `zf` 插值；R-301 腰射 40 / 20、开镜 115 / 20 | 按字段 | 一致 |
| CE-51 | 停火回落 | 俯仰 | R-301 开镜到 50 % 0.244 s，腰射 0.365 s | 0.203 s / 0.350 s | 不一致 |
| CE-52 | punch 进画面的份额 | 俯仰 | 画面 × (1 − fraction)：R-301 腰射 0.05 / 开镜 0，Wingman 0.4 / 0.3 | 按字段 | 一致 |
| CE-53 | 每发缩放 | 俯仰 | Mastiff 腰射首发 2.03；Devotion 1.02；Kraber 开镜 1.37 | 2.0；1.2；1.5 | 不一致 |
| CE-54 | 开枪震屏 | 位移 | 0（7 把枪） | 0 | 一致 |
| CE-55 | 拉栓 / 泵动动画镜头 | 俯仰 | Peacekeeper 腰射 5.15°，Kraber 4.9°，Longbow 0.43° | 没有 | 不一致 |
| CE-56 | 拉栓 / 泵动动画镜头 | 横滚 | Peacekeeper −1.84°，Kraber −1.46°，Longbow 0.70° | 没有 | 不一致 |
| CE-57 | 拉栓 / 泵动动画镜头 | 偏航 | Peacekeeper −0.31°，Kraber −0.87° | 没有 | 不一致 |
| CE-58 | 开镜 FOV | FOV | 基础 + (`zoom_fov` × S − 基础) × smoothstep(zf)；R-301 89 → 69.97 | `AdsCurves` 同公式 | 一致 |
| CE-59 | 中弹 punch | 俯仰 | 0（27 发真实中弹） | 没有 | 一致 |

### 组合规则

| id | 规则 | 通道 | R5 | Unity 现在 | 一致吗 |
|---|---|---|---|---|---|
| CE-60 | punch 弹簧（第一组） | 俯仰 | k 65、c 9；峰值 0.146 s，过零 0.47 s，回弹 12 % | `springK` 65、`springC` 9，精确解 | 一致 |
| CE-61 | 第二组弹簧（空手） | 俯仰 | 冲量 × 0.2，65 / 9 | `secondSpring` 0.2 | 一致 |
| CE-62 | 第二组弹簧（拿枪） | 俯仰 | 换成武器弹簧（R-301 腰射 40 / 20，峰值比 0.13；开镜 0.112），进画面 × (1 − fraction) | 永远 65 / 9，峰值比 0.200 | 不一致 |
| CE-63 | 子弹和画面 | 俯仰 | 子弹 = 瞄准 + punch1 + punch2 + 开镜 drift + 扩散 | 子弹 = 瞄准 + 武器 punch | 不一致 |
| CE-64 | 鼠标抵消 punch | 俯仰 | 反向输入先把 punch2 减到 0 | 没做 | 不一致 |
| CE-65 | kick 叠加 | 俯仰 | 线性相加，无优先级、无上限 | 同 | 一致 |
| CE-66 | 横滚合成 | 横滚 | 相加后折回 ±180°，不封顶 | `rollWrap` 开 | 一致 |
| CE-67 | 绳子横滚三选一 | 横滚 | 钩爪 > 滑索 > 摆荡，共用 SmoothCD ω 6.667 | `nativeRollSmooth` 开 | 一致 |
| CE-68 | 俯仰 / 偏航合成 | 俯仰 | 瞄准 + 翻越 + rodeo + punch1 + (1 − f) × punch2 + drift / 晃动 | 相加（HSD 没有 rodeo） | 一致 |
| CE-69 | 眼睛位置合成 | 眼高 | 原点 + 眼高 + 冲刺偏移 + 滑索偏移，没有位置 kick | 同 | 一致 |
| CE-70 | FOV 合成 | FOV | 基础 + 开镜；滑铲 × 1.1 | 滑铲和开镜在两处代码，同时生效的先后没核对 | 没测过 |
| CE-71 | 强度设置 | 俯仰 | R5 没有 | 高度 / 横滚 / FOV 三组强度 | 只有 HSD |

### M5.5 才有（HSD 设计，菜单 "Camera model" 切回）

| id | 事件 | 通道 | M5.5 的值 | 一致吗 |
|---|---|---|---|---|
| CE-72 | 速度 FOV | FOV | +8° × clamp((v − 200) / 500)，200–700 u/s = 5.08–17.78 m/s | 只有 HSD |
| CE-73 | 技能 FOV | FOV | +2 到 +6°，总和上限 22° | 只有 HSD |
| CE-74 | 位置 kick（lift） | 眼高 | 起跳 1.0 u（0.025 m），滑铲跳 2.5 u，峰值 0.07 s | 只有 HSD |
| CE-75 | 位置 kick（dip） | 眼高 | 落地 4·k u（硬落地 8 u = 0.203 m） | 只有 HSD |
| CE-76 | 身体惯性滞后 | 位移 | 0.006 s × 速度误差，最多 1.5 u（0.038 m） | 只有 HSD |

M5.5 还有速度线（330 → 650 u/s），它是屏幕叠层，不属于六个通道，没有进表。

## 和 R5 不一致的

一共 14 行。最重要的放前面。

| id | 差在哪 | 原因 / 处理 |
|---|---|---|
| CE-63 | 子弹不含移动 punch1 和开镜 drift。R5 落地后马上开枪，子弹跟着画面往下偏（400 u 落差 0.1 s 后 15.5–17.2°）；Unity 子弹只加武器 punch | PR #122 实测（11-13）后才知道，主线 DESIGN-PHILOSOPHY T2 还写"推断不进"。Unity 没跟，无 D 号。影响落地开枪、跳下开枪的命中 |
| CE-62 | 拿枪时移动 punch 的第二组应换成武器弹簧并乘 (1 − fraction)；Unity 永远用 65 / 9、全进画面。拿 R-301 腰射时第二组峰值比 R5 0.13，Unity 0.20 | PR #122 新测出，无 D 号。差的是第二组（约占画面的 1 / 6），肉眼差别小，但开镜后子弹也受影响 |
| CE-55 – CE-57 | 拉栓、泵动、换弹时镜头跟着动作动画动（Peacekeeper 腰射俯仰 5.15°、横滚 −1.84°；Kraber 4.9°），Unity 没有 | PR #122 新发现，还没定做不做。做的话属于"动画挂点"那一类（和翻越镜头同一行），不是震屏 |
| CE-64 | 鼠标反向输入先抵消 punch2，Unity 没做 | R5-DIFF「瞄准、后坐和开镜」写了"还没做"（PR #100）。压枪手感和停火落点都靠它 |
| CE-42 | 开镜 drift（俯仰 0.29°、偏航 0.21°）Unity 没做；R5 里它也进子弹 | R5-DIFF「后坐的缩放、横滚和枪模跳动」：还没做（PR #100）；公式没读，只有幅度 |
| CE-36 | 站姿翻越镜头峰值差约 ±1°（h80 Unity 7.4–7.8°，R5 6.0–6.9°；h160 / h200 Unity 偏低约 0.5–1°），时刻对上 | D-53 / R5-DIFF CAM2 K-6：用的是 B1 量的按类曲线；K-6 指标 53 / 88，没再调 |
| CE-38 | 蹲着翻越 h120 R5 约 1 / 4 是短的那种（0.656 s），Unity 总是长的；平均差 0.19–0.22 s | R5-DIFF 二「D-75 剩下的」：亚 1 u 的起点差来自帧时间抖动，复现不了，按拟合原则（D-70）只记 |
| CE-53 | 每发缩放 Devotion 腰射首发 R5 1.02 / Unity 1.2，Kraber 开镜首发 R5 1.37 / Unity 1.5；其余枪对上 | D-94；R5-DIFF（PR #100）"留着的差别"，没查 |
| CE-51 | R-301 开镜回落到 50 % R5 0.244 s，Unity 0.203 s（不带随机 0.175 s） | RV §10.3：弹簧本身逐帧对上，0.04 s 没解释；以前推断是服务端纠正，已否定 |
| CE-45 | R5 有脚本 / 动画触发的世界屏幕震动（`ClientScreenShake`），Unity 没接到镜头 | `fps-camera-design` 第 3 条：没要求不加震屏。移动和开枪本来就不触发，所以对现有动作没影响 |
| CE-17 | 滑铲眼高到底 Unity 约 0.19 s，R5-DIFF 记 R5 约 0.167 s | D-70 只记不追（差约 3 条命令）。11-14 统一（重建检验 H-7）：复刻的是公式（比例 1 / 0.2 s 线性、眼高 smoothstep，起滑后第 24 条命令到 32 u）；0.19 / 0.167 / 0.208–0.213 s 是不同的量法，不是三个规则（04 §4.8） |
| CE-25 | TF2 墙跑倾斜少了提前 0.25 s（`wallrun_viewTiltPredictTime`） | 对照的是 TF2，不是 R5；P-05 默认关（D-58）。没有 R5-DIFF 条目 |

## 没测过的

一共 13 行：

- **CE-04 – CE-06 二段跳 punch**：只有反编译公式（`0x140a34c00`），R5 训练场里没有二段跳的镜头录像。Unity 按公式做了（D-68）。
- **CE-09 水中落地 × 0.2**：训练场没有水；Unity 也没有水。
- **CE-12 跳板起跳 punch**：CAM2 和 CR §8 把跳板列进"往弹簧加冲量"的事件，但值没读；起跳 punch 本身不在 launch 上调用。
- **CE-13 重力炮、抓墙、墙跑开始 / 超时 punch**：函数定位了，setfile 值没读；S21 墙跑关闭。
- **CE-24 墙跑倾斜（R5 代码值）**：S21 墙跑关闭；"每秒 6"是不是速率没读清。
- **CE-26 闪避倾斜**：S21 没有闪避。
- **CE-34 摆荡横滚**：S21 Pathfinder 不能摆荡。
- **CE-35 滑索倾斜（bank tilt）**：值没读，没实测。
- **CE-39 翻越镜头淡出**：`traversal_viewLerpOut` 开着，淡出形状没单独读。
- **CE-46 上升气流震动**：读取函数没定位。
- **CE-70 FOV 合成**：R5 规则清楚，但 Unity 滑铲 FOV（`NativeCameraFeedback`）和开镜 FOV（`AdsCurves`）同时生效时谁先谁后没有核对。

## 资料之间对不上的地方

两边都写，按"哪个更新、哪个是实测"标出现在用哪个。

1. **横滚总上限（待核）**：`N2-C-CAMERA.md` §7 写"总上限 40°"；`CAM2-CAMERA.md` §5 和 `CAMERA-REFERENCE.md` §3.9 读了 `View_CalcRoll`，没有总上限，折回 ±180°。表里暂按 CAM2 写（D-53），N2-C 的说法保留；**两边都留，标"待核"**，见 [99 B07-12](../99-TODO-RESEARCH.md)（hb-integrate 11-14，按总控决定）。Unity 的 `maxRoll` 40 只在旧版开关（`rollWrap = false`）下起作用。
2. **二段跳 punch 的峰值**：同一个冲量 (4.5 + r)·20 °/s，DESIGN-PHILOSOPHY §6.2 写 6.2–7.7°（两组合计，按 0.0771 算是对的）；CAM2 §2.1 / §7 和 D-68 写"约 3.9–6.2°"；R5-DIFF FND 写"合计约 5.6–7.7°"；Unity 代码注释写"4.6–6.6°"。按弹簧公式两组合计是 6.17–7.71°，只算第一组是 5.14–6.42°。**表里用 6.2–7.7°**。
3. **滑铲眼高到底的时间**：C3 实测 R5 64 → 32 用 0.208–0.213 s；R5-DIFF 二「滑铲下沉」写 R5 约 0.167 s、Unity 约 0.19 s。两者是不是同一个口径（眼高到底 / 到 32 ± 某个容差）没写清。〔11-14 统一（重建检验 H-7）：复刻的是公式（比例 1 / 0.2 s 线性、眼高 smoothstep，起滑后第 24 条命令到 32 u）；0.19 / 0.167 / 0.208–0.213 s 是不同的量法，不是三个规则，见 [04 §4.8](../04-slide-mantle.md)〕
4. **移动 punch 进不进子弹**：C3 写"punch 只动镜头，不动准星"（瞄准角不变，这一点仍然对）；主线 DESIGN-PHILOSOPHY T2 写"未测，推断不进"；`fps-camera-design` 规则 2 的子弹公式也没有 punch1。PR #122 的 F-GAPS §1 实测：**进**，子弹 = 瞄准 + punch1 + punch2。**用 PR #122**。
5. **第二组弹簧拿枪时听谁的**：主线 DESIGN-PHILOSOPHY §10.4 写"没对过"；PR #122 F-GAPS §1.3 测清：空手 65 / 9，拿枪用武器弹簧，两边都对。
6. **rodeo 钩爪横滚**：N10 §7 和 00-INVENTORY B07-3 写"实测 13.9°、公式 18.5°，没查"；R5-DIFF C-12（D-42）改成共用 SmoothCD 后 Unity 是 13.7–13.9°。按 C-12 已经对上，B07-3 可以划掉（建议写进 `_notes`）。
7. **CAMERA-REFERENCE 里过时的数**：§3.1 站立眼高 64（K-4 改成 70）；§3.8 跑步晃动幅度 0.335、淡入每秒 4（K-3 改成 0.25、每秒 20）；§1 写的"滑索横滚以 6.667 /s 平滑"是 C-12 以后才对，C-12 以前 Unity 滑索是 3.0 /s。
8. **武器后坐动不动镜头**：主线 DECISIONS D-86 写"后坐只作用在子弹上，不动镜头"；PR #100 上的 D-88 取代了它（画面跟着 punch 走）。PR #100 还没合并，所以主线现在仍写着 D-86。

## 和第 07 章事件名的对照

`camera-events.tsv` 第 3 列"第 07 章事件名"就是这张对照（hb-integrate 11-14 按 `_notes/hb-tables.md` 加）。在第 07 章看到一个事件名，用它在 TSV 里筛；在表里看到一个 CE 编号，用它回到 07 的对应一节。

| 第 07 章事件名 | CE 编号 |
|---|---|
| `jump` | CE-01 – CE-03 |
| `double_jump` | CE-04 – CE-06 |
| `land` | CE-07 – CE-11（CE-10 是 `land` + `jump`） |
| `wall_kick`、`wallrun_start` / `wallrun_timeout` | CE-13（合在一行） |
| `slide_start` | CE-14（滑铲眼高 CE-17 也由它开始） |
| `slide_tilt` / `slide_fov` | CE-15 / CE-16 |
| `eye_height` | CE-17（滑）、CE-18（站 / 蹲） |
| `sprint_eye` / `sprint_tilt` | CE-19 / CE-20 |
| `step_bob` | CE-21、CE-22 |
| `wallrun_tilt` | CE-24、CE-25 |
| `rope_roll` | CE-27、CE-28、CE-34、CE-67 |
| `zip_eye_offset` | CE-29、CE-30 |
| `zip_detach` | CE-31 – CE-33 |
| `mantle` | CE-36 – CE-39 |
| `view_drift` / `ads_drift` | CE-40、CE-41 / CE-42 |
| `explosion` | CE-45（屏幕震动） |
| `fire` | CE-47 – CE-54 |
| `ads_fov` | CE-58 |
| `hit` | CE-59 |
| `melee`、`ability`、`titan_embark` / `titan_eject`、`weapon_sway` | 表里没有（CE-43 是 cockpit sway，不是 `weapon_sway`） |

表里有、第 07 章没有单独名字的：CE-12 跳板起跳、CE-23 侧移横滚、CE-26 闪避倾斜、CE-35 滑索 bank tilt、CE-43 / 44 cockpit、CE-46 上升气流震动、CE-55 – 57 拉栓 / 泵动动画镜头、CE-60 – 71 组合规则（07 §4）、CE-72 – 76 M5.5。

## 本章出处缩写和出处

| 缩写 | 文件 | 在哪 |
|---|---|---|
| DP | `research/DESIGN-PHILOSOPHY.md` T2、T3、T5、T9、§6.1 – §6.5、§10 | main；§6.2 的两行、§6.5、T2、T3 的更正在 PR #122（还没合并；分支 `r5gap/gun`） |
| CR | `research/rea-native/camera/CAMERA-REFERENCE.md` §1 – §8 | main |
| CI | `research/rea-native/camera/CAMERA-INVENTORY.md` | main |
| C3 | `research/rea-native/camera/C3-CAPTURE.md` | main |
| N2C | `research/rea-native/subsystems/N2-C-CAMERA.md` §1 – §8 | main |
| CAM2 | `research/rea-native/cam2/CAM2-CAMERA.md` §1 – §7 | main |
| N10 | `research/rea-native/n10/N10-CAMERA.md` | main |
| DIFF | `R5-DIFF-ARCHIVE.md` K-1 – K-4、C-12、CAM2、FND、D-75、二节 | main；「瞄准、后坐和开镜」「后坐的缩放、横滚和枪模跳动」在 PR #100（还没合并；分支 `combat/gun-models-records`） |
| DEC | `DECISIONS.md` D-05、D-18、D-24、D-35、D-37、D-38、D-42、D-43、D-53、D-54、D-58、D-67、D-68、D-70、D-71、D-75 | main；D-88、D-89、D-94 在 PR #100（还没合并） |
| RV | `research/combat/RECOIL-VIEW.md` §1 – §6 | PR #93，还没合并；分支 `combat/recoil-view-measure`；§10 在 PR #95（分支 `combat/gun-measure`） |
| ADS | `research/combat/ADS-CURVES.md` §1 | PR #93，还没合并 |
| FG | `research/combat/gun-measure/F-GAPS.md` §1 – §3 | PR #122，还没合并；分支 `r5gap/gun` |
| EM | `research/combat/gun-measure/E-MOUSE.md` §1 | PR #122，还没合并 |
| TF2W | `tf2/wallrun/WALLRUN-B-SPEC.md` §8 | main |
| U-NC | `HSD-Unity: Assets/HSD/Game/Runtime/Camera/Native/NativeCamera.cs`（`NativeCameraParams`、`NativeCameraFeedback.Observe`、`PunchAxis`、`SmoothCD`、`PerlinNoise`） | main（和 `units/switch` 只差 `KickVMin` 的 `Units.L`） |
| U-NE | `HSD-Unity: Assets/HSD/R5Replay/Runtime/NativeEyeHeight.cs`（`NativeEyeParams`、`NativeEyeHeight.Height`） | main |
| U-M55 | `HSD-Unity: Assets/HSD/Game/Runtime/Camera/M55/CameraFeedback.cs`（`CameraFeedbackDesign`、`CriticalSmoother`） | main |
| U-VK | `HSD-Unity: Assets/HSD/Game/Runtime/Combat/Arsenal/ViewKick.cs`、`ArsenalWeapon.cs`、`AdsCurves.cs` | HSD-Unity PR #67，还没合并；分支 `combat/wp4-recoil-gunkick` |
| U-UP | `HSD-Unity: Docs/units/units-params.tsv` 的 `camera.native.*`、`camera.m55.*` 行 | HSD-Unity PR #88，还没合并；分支 `units/switch` |
| SKILL | `HSD-Unity: .claude/skills/fps-camera-design/SKILL.md`、`references/` | main |

R5 函数地址按 README 写法规范 §5 只放在出处（TSV 的出处列有逐行的）：起跳 punch `0x140a349c0`、二段跳 `0x140a34c00`、落地 `Land_ViewKick` `0x140a35750`、下滑索 `0x140a35ac0`、弹簧 `0x140a34170`、横滚汇总 `View_CalcRoll` `0x140afc480`、滑铲倾斜 `0x140afc040`、冲刺眼高 `0x140af2370`、翻越镜头 `GetTraversalViewPosition` `0x1406668a0`、鼠标抵消 `0x140a33ff0`。

泰坦镜头（驾驶舱、开机、眼高 185）不在这张表里，见 07 章和 `tf2/expansion/titan/pose/TITAN-POSE-CAMERA.md`。枪模每发的跳动（D-95）动的是枪模，不是镜头，也不在这张表里。
