# N2-T 时序和输入

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

## 1. 每条 usercmd 的执行链 [native]

```
Pred_RunCommands?     0x1407ea760   预测：逐条处理排队的命令
  Pred_RunCommand?    0x14092ab70   设置时间、处理冲量队列、按钮、武器
    ProcessMovement?  0x140a33cf0   准备 movedata，调 PlayerMove，存按钮
      PlayerMove      0x140a54e80   按移动类型分派：普通 / 观战 / 滑索 / 跳伞 / 绳索 …
        Duck          0x140a54080
        FullWalkMove  0x140a4c810   见 N2-G §1
```

## 2. 时间 [native]

- **curtime** = 玩家的 tickbase 时间（`Pred_RunCommand` 里设置）。所有"距离某事件多久"的判断（lurch 窗口、skip、anti-multi-jump、滑铲冷却、mantle 跳）都用它。
- **frametime** = 这条 usercmd 自带的 frametime（cmd + 0x218）。所以**每条命令的 dt 等于客户端那一帧的时长**，随帧率变化。和 M1 的结论一致：每帧一条命令。
- `ProcessMovement` 里 frametime 再乘一个玩家级倍率（0x3b8c，[native-inf]：慢动作之类的效果），移动结束后恢复。
- `FullWalkMove` 里的 dt 再乘 `AirSlowMo_TimeScale`（平时为 1；`airslowmo_*` ConVar 和 setfile `airSlowMoSpeed` 控制）。
- 注意：有的公式用全局 frametime（`Friction`、`Accelerate`、`AirAccelerate` 的 extra 部分），有的用 `FullWalkMove` 传下来的 dt（重力）。平时两者相等。

## 3. 按钮和按下边沿 [native]

- movedata + 0x24 = 这条命令的按钮；+ 0x28 = 上一条命令的按钮；+ 0x2c = **本条命令新按下的按钮**（[native-inf]：Source 的写法，按钮 & ~旧按钮）。
- `ProcessMovement` 在 `PlayerMove` 之后把 0x24 存进 0x28，供下一条命令用。
- 按位（[native-inf]，和 Source 一致）：跳 0x2、蹲 0x4、前 0x8、后 0x10、左 0x200、右 0x400。lurch 用的就是 0x8 / 0x10 / 0x200 / 0x400 的按下边沿（N2-L）。
- usercmd 里还带一个"这条命令用了手柄"的标志，时间记在玩家 0x46e0。lurch 的 `jump_grace_controller_disable_duration` 用它（默认 −1，不起作用）。

## 4. 输入幅度 [native]

在 `WalkMove` 里（N2-G §2.1）：
- 冲刺中，前后、左右轴 × 1.25；
- 幅度 m ≤ 1 时改成 m·(2 − m)，m > 1 时归一到 1；
- 侧向 × `speedScaleSide`，向后 × `speedScaleBack`。

**按键的轴值**：M1 / M2 发现，一个方向键按下的第一条命令上轴值是 0.5，之后是 1。经过曲线后变成 0.75 和 1。

**冲刺 × 1.25 的含义**（推算）：斜向 W+D 时，轴值是 (1, 1)，乘 1.25 后幅度 > 1，归一后方向不变；单键时 1.25 → 归一到 1，也没有变化。所以 × 1.25 只在幅度小于 1 的时候起作用，比如第一条命令（0.5 → 0.625 → 0.86）和手柄半推。

## 5. 冲量队列和"低减速"窗口 [native]

`Pred_RunCommand` 处理一个 32 项的预测事件队列。和移动有关的是两类：
- 类型 0：直接把一个速度加到玩家的累积速度上；
- 类型 1（**冲量**）：设置"低减速结束时间" T = curtime + |冲量速度| × `impulse_low_decel_duration_scalar`（**0.003**）。

`Ground_GetDecel`（N2-G §2.4）用这个 T：T 之前 0.5 s 以外，地面减速为 **0**；最后 0.5 s 从 0 线性升到 1。

例子：一次大小 1150 的冲量（跳板的 `JUMP_PAD_PUSH_VELOCITY`）→ T = 3.45 s。落地后约 2.95 s 内地面没有减速，之后 0.5 s 内恢复。**跳板是否走这个冲量队列还没确认**，见 T-04。

## 6. 和实测对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| T-01 | dt = 每帧时长 | usercmd 自带 frametime | M1：每帧一条命令，dt 是那一帧的 frametime | **一致** |
| T-02 | 按下边沿 | 按钮 & ~上一条按钮 | M3 / M8：lurch 只在有边沿的命令上发生 | **一致** |
| T-03 | 第一条命令的有效输入 | 0.5 → 0.75（冲刺中 → 0.86） | M2：第一条命令轴值 0.5 | **新发现**，见 G-08。HSD 的输入层（M10-D2）要核对 |
| T-04 | 冲量后的低减速窗口 | T = now + |冲量| × 0.003；T − 0.5 s 前减速为 0 | 无直接实测。M4 / M8 的跳板、钩爪、击退落地后是否"滑得远" | **只有代码**。N4 可测：跳板落地后地面减速多久恢复 |
| T-05 | 帧率依赖 | 加速、摩擦都按 dt 线性；加速度按"加速前速度"选段 | M2：速度段边界附近的超调随 dt 变化，冲到上限的时间有 13 % 的差异 | **一致**：这是逐命令选段的自然结果 |

## 7. 还没读的

- `PlayerMove` 的分派细节（各移动类型的进入条件）。
- 0x14092ab70 里冲量队列的写入方（哪些事件会产生类型 1 冲量）。
- 预测和服务器纠正（`PredErrorCheck` 等）对实测的影响。
