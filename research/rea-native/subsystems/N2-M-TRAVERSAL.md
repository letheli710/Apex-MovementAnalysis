# N2-M 攀越、mantle、superglide、墙

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

**这一份只读了一部分。** `TraversalMove` 有 6831 字节，里面是一个按动画状态推进的状态机。出口速度和 mantle 跳的规则已经读清楚，superglide 的精确窗口还没读通，下面如实标出。

## 1. 开关和参数

| 项 | 值 | 来源 |
|---|---|---|
| 墙跑 | setfile `wallrun` = **false**（census）；ConVar `wallrun_enable` = 1 | 墙跑代码在（Titanfall 遗留），**S21 默认关闭**。HSD M7 的墙跑是 HSD 设计 |
| 攀爬 | setfile `climbEnabled` = true | S21 的攀墙（爬一段墙再翻上去） |
| 自动 mantle | `automantle_enable` 1、`automantle_cooldown` 0.25 s | ConVar |
| mantle 高度分档 | `automantle_height_below` −10、`level` 10、`above` 30 | ConVar；按档选 setfile 的 `mantleDurationBelow` / `Level` / `Above` / `High` |
| mantle 跳 | `automantle_jumpoff_duration` 0.1 s、`automantle_jumpoff_anim_maxfrac` 0.5 | ConVar |
| 回退 | `automantle_backoff_anim_maxfrac` 0.7 | ConVar |
| 静止比例 | `automantle_rest_frac` 0.4、`rest_frac_below` 0.3 | ConVar |
| 窗户穿越 | `traversal_window_duration` 0.3 s | ConVar |
| 钩爪后自动 mantle | `grapple_autoMantle` 0.25 s | ConVar |

## 2. `TraversalMove`（0x140a45380）[native]

### 2.1 进度

- 开始时清零速度，位置由动画和插值驱动。
- 进度的推进速率 = 1 / mantle 时长。时长按高度档从 setfile 取（`mantleDuration*`），并按实际高度相对 `mantleHeight` 的比例修正。窗户穿越用 `traversal_window_duration`。
- 动画状态记在玩家 0x2b34（编号 4、0xb、0xc 等）。**下蹲已完成时，动画状态编号 + 4**，也就是有一套蹲姿版本的 mantle。

### 2.2 mantle 中按跳

1. 本条命令有跳的按下边沿时，记下按键时刻（0x2ba8），每次 mantle 只记一次。
2. 在下面任一条件满足时执行"mantle 跳"：
   - 现在 ≥ 按键时刻 + `automantle_jumpoff_duration`（0.1 s）；
   - 进度 > `automantle_jumpoff_anim_maxfrac`（0.5）。
3. mantle 跳有两种：
   - 进度还没到某个阈值（[native-inf]：还在墙面上，没翻过沿）：按**墙跳**处理，速度 = `wallrunJumpOutwardSpeed` × 向外 + `wallrunJumpUpSpeed` × 向上；
   - 否则：水平速度设为**当前姿态的最大速度**（冲刺中 = msc × `sprintspeed` = 299，否则走路上限），方向沿意图（movedata 0xb4），然后调用 `Jump()`。

### 2.3 自然结束

向前移动时，水平速度 = 当前姿态的最大速度（冲刺中 299）× 前向。

## 3. Superglide（只有推断）

M8 实测：mantle 最后约 0.085 s 内按跳，下一条命令按蹲 → 出口 |v_h| = **460**，vz ≈ 286；太早按 → "切断、不跳"（299，vz 0）；太晚 → 顶上普通跳（299）。

代码里能对上的部分：
- **460** = 滑铲加成上限 msc × `slideSpeedBoostCap`（1.15 × 400）。mantle 跳把水平速度设成 299，再加满加成 min(299 + 172.5, 460) = 460。
- **vz ≈ 286** = mantle 跳调用 `Jump()` 产生的普通起跳速度。

还解释不了的部分：
- `slide_whileInAir` = 0，`Slide_TryBegin` 要求地面法线 z > 0.7。起跳后为什么还能拿到滑铲加成？推测：`Duck` 调 `Slide_TryBegin` 时传的是"上一次的地面法线"（玩家 0x43dc），起跳后那一两条命令里它还没更新 [native-inf]。
- 窗口为什么是"最后约 0.085 s"，而不是 jumpoff 参数给出的"进度 > 0.5 或按键后 0.1 s"：要读状态机里"太早按 → 切断"的那条路径（可能和 `backoff_anim_maxfrac` 0.7、`rest_frac` 0.4 有关）。

**这两点都标为未定（M-03、M-04）。**

## 4. SDK 钩子

| 钩子 | 文件 | 默认 | 影响 |
|---|---|---|---|
| `TraversalMove` | `mantle_boost.cpp` | `mantle_boost_enabled` = 1 | SDK 的 mantle boost 状态机。M8 R3 实测：开启时出口 388.7 / 367.42，并且能在滑铲跳之后触发。**M8 R3 的原生 SG 数据是在关闭它（`--both-cvar mantle_boost_enabled=0`）的条件下测的** |
| `AirMove_TapStrafe` | `mantle_boost.cpp` | 同上 | mantle boost 状态 4 时关掉 lurch（N2-L §4） |
| `JumpOutOfWallRun` | `wall_launch.cpp` | Sparrow 专用 | 不起作用 |

## 5. 和实测对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| M-01 | mantle 自然结束出口 | 当前姿态最大速度 × 前向（冲刺 299） | M8：太晚按 / 不按 → 299 | **一致** |
| M-02 | mantle 顶上跳 | 水平 = 299，再 `Jump()` | M8：顶上跳 299，vz 286.7 | **一致** |
| M-03 | SG 出口 460 | 299 + 满滑铲加成，封顶 460 | M8：一律 460.000 | **一致**（数值）。为什么起跳后还能滑铲拿加成，只有推断 |
| M-04 | SG 窗口最后约 0.085 s | jumpoff：进度 > 0.5 或按键后 0.1 s | M8：最后 0.005–0.085 s 100 % 成功 | **未定**：还没读通"太早 → 切断"的路径 |
| M-05 | mantle 跳 328.98 ≈ 1.1 × 299 | `Jump` 朝上一帧撞到的表面加 30 u/s：299 + 30（`ledger-open/LEDGER-OPEN-5.md`、`n11/N11-OPEN-ITEMS.md`） | M8：3 / 12 次，接近墙面时 | **一致** |
| M-06 | 走路起跳 SG 出口 402.009 | 同一个 +30：199.5 + 30 > 200，滑铲加成生效，+ 172.5 = 402.0（同上） | M8：3 / 15 次 | **一致** |
| M-07 | 滑铲跳接近后没有 SG | S-02：滑铲加成冷却被上一次滑铲刷新，所以 SG 拿不到加成 | M8：0 / 15 次 SG，"推测和滑铲加成没恢复有关" | **一致**（M8 的推测得到代码支持） |
| M-08 | 原生 SG 和 SDK mantle boost 的区别 | SDK 在 `TraversalMove` 外面包了一个状态机，默认开 | M8：SDK 开启时 388.7 / 367.42，关闭时 460 | **一致**：两套行为，Reference 要分清用哪一套 |
| M-09 | S21 墙跑 | setfile `wallrun` = false | M7：墙跑是 HSD 设计 | **一致** |

## 6. 还没读的

- `TraversalMove` 的完整状态机（M-04、M-05）。
- `AutoMantle_Try` / `AutoMantle_Search`：mantle 的触发条件（距离、角度、高度）。
- `WallClimb_Move`：攀墙的速度和时长（setfile `climb*`），对照 M6-A2、M8 R2 的 Revenant 攀爬。

## 7. SG 窗口（M-04）的第二轮阅读（"后放的事"，2026-10-23）

`TraversalMove` 的进度推进是一个带平滑（3 − 2x 的 smoothstep）的动画状态机。能确认的：
- 进度 > `automantle_jumpoff_anim_maxfrac`（0.5）时按跳：**下一条命令就执行 mantle 跳**，和 M8"按键后下一条命令结束攀越"一致；
- 进度 < 0.5 时按跳：等 `automantle_jumpoff_duration`（0.1 s）后才执行；
- 执行时分两种出口：进度还没过一个阈值（推测是"翻过沿"）→ 墙跳式出口；过了 → 水平 299 + `Jump()`，再按蹲才有 SG。

**M8 的"太早 → 切断"和"最后 0.085 s → SG"的分界**，看来就是上面那个"翻过沿"阈值。它从动画数据里来，静态读不出具体值。改成 N4 实验：记录按键时的攀越进度（`m_traversalProgress` 一类的字段），直接测出分界。
