# N2-S 滑铲

日期 2026-10-23。目标 `r5apex_dx12.exe`。只读，方法和标签同 [N2-G-GROUND.md](N2-G-GROUND.md)。

滑铲分散在五个地方：开始（`Slide_TryBegin`）、加速和摩擦（[N2-G](N2-G-GROUND.md) §2）、下蹲计时和松蹲结束（`Duck`）、低速结束（`WalkMove`）、滑铲跳（[N2-J](N2-J-JUMP-AIR.md) §1.2）。这份文档把它们串起来。

## 1. 开始 `Slide_TryBegin`（0x140a54890）[native]

由 `Duck` 在按下蹲时调用。条件（按顺序）：

1. 地面法线 z > 0.7（坡度小于约 45.6°），除非 `slide_whileInAir` 打开；
2. setfile `slide` 为真；
3. 在地面上：下蹲比例 < `slide_max_duck_frac_to_start`；
4. 水平速度 ≥ `slideRequiredStartSpeed`（census 200）。空中且竖直速度 > −200 时改用 `slideRequiredStartSpeedAir`；
5. 有地面实体时，视角前向和速度方向的点积 ≥ `slide_max_angle_dot`。

满足后进入滑铲。**加成**：
- 条件：`player_slideBoostEnabled`，并且距离**上一次滑铲开始** > `player_slideBoostCooldown`，并且某个检查（0x140ac1d70）返回 0（[native-inf]，未读）；
- 新速度 = min(h + msc × `slideSpeedBoost`, msc × `slideSpeedBoostCap`)，census 是 150 / 400，所以 = min(h + 172.5, 460)；
- 加成量（新速度 − h）记下来，供滑铲早跳时扣回；设"待退还"标志。

**无论有没有加成，都把"上一次滑铲开始"的时间更新为现在。**

## 2. 滑铲中

见 [N2-G](N2-G-GROUND.md)：
- 加速度 = `slideAccel` × msc；
- 意图里沿速度方向的分量被去掉，**只能转向**；
- 摩擦：s′ = max(0, s − D·ft) × `slideVelocityDecay`^((1 − 0.75x)·ft)；
- D = `slideDecel`（按住下蹲且向前），否则 `slideWantToStopDecel`。

**斜坡**：`Gravity_HalfStep`（0x140a36130）在滑铲贴地时，除了竖直重力，还按一组玩家字段（0x43dc / 0x43e0 / 0x43e4，[native-inf]：地面法线的水平分量和一个系数）加一个水平分量。这很可能就是斜坡滑铲加速的来源（M8 R4）。`Slide_TryBegin` 收到的参数也是 0x43dc 这组字段。**公式没细读**，留给下一步。

## 3. 下蹲计时 `Duck`（0x140a54080）[native]

- 下蹲状态（0x2a70）：0 站、1 正在蹲下、2 已蹲下、3 正在起身。
- 进入"正在蹲下"时，计时器（0x242c，毫秒）设为 **400**；如果这次按下蹲开始了滑铲，设为 **200**。计时到 0 → 状态 2。
- 从"正在起身"切回"正在蹲下"时，计时器按剩余比例换算。

## 4. 结束 [native]

| 情况 | 条件 | 位置 |
|---|---|---|
| 按住下蹲 | 移动后速度 < `slideStopSpeed`（census 125），并且标志 0x1dfc 为假 | `WalkMove` |
| 松开下蹲 | 水平速度 ≤ `slideMaxStopSpeed`（census 350）时不再保持滑铲 | `Duck` |
| 其他 | 在滑索上、近战冲刺中、墙跑中 | `Duck` |

## 5. 和实测对照（初表）

| id | 项 | 代码 [native] | 实测 | 结论 |
|---|---|---|---|---|
| S-01 | 加成大小和上限 | min(h + 150·msc, 400·msc) = min(h + 172.5, 460) | M2：只测到上限 460；M2 写着"入口低于 460 − 172.5 = 287.5 才能分开" | **一致** |
| S-02 | **加成冷却从"上一次滑铲开始"算，没拿到加成也刷新** | §1 | M2：首次加成后 0.92 / 1.32 s 再进滑铲没有加成；M8：约 1.6–2.1 s 后才恢复；M10：0.4 s 滑铲后 0.6 s 再滑没有加成 | **一致**（定性）。冷却值本身不在 census 里，N4 读 `player_slideBoostCooldown` |
| S-03 | 滑铲衰减律 | 见 G-10 | M2：(v − 100·dt)·0.7^dt | **一致** |
| S-04 | 松蹲后减速变强，并在 350 以下结束 | 改用 `slideWantToStopDecel` 400；h ≤ `slideMaxStopSpeed` 350 时结束 | M10：松蹲后减速变强，到约 335（≤ 350）结束 | **一致**（阈值）。335 和 350 的差距可能来自起身计时，待核 |
| S-05 | 按住下蹲时的结束速度 | 速度 < `slideStopSpeed` 125 | M10：普通滑铲 1.69 s 后在 112 u/s 结束 | **数值差**：125 vs 112。检查的是移动后的 3D 速度还是某个中间量，要细读 `WalkMove` 那一段 |
| S-06 | 滑铲早跳扣加成、0.6 s 抬到 350 | 见 J-07、J-08 | M10 | **一致** |
| S-07 | 滑铲中只能转向 | 见 G-12 | 无 | **只有代码** |
| S-08 | 滑铲的下蹲过渡 200 ms | §3 | M2："早期滑铲跳 H = 50.37（duck = 1）vs 49.90（duck = 2）" | **一致**（定性）：duck = 1 / 2 正是下蹲状态 |
| S-09 | 斜坡滑铲 | 重力半步里的水平分量（§2） | M8 R4：额外加速 147 + 342·sin(坡度) | **待读**：公式还没细读 |
| S-10 | 起滑坡度限制 | 地面法线 z > 0.7 | 无 | **只有代码** |

## 6. 还没读的

- 斜坡项的完整公式（S-09），以及 `Friction` 里 x 的来源（0x140abdc20，可能也和坡度有关）。
- S-05 的结束速度差。
- 0x140ac1d70（加成的额外条件）、标志 0x1dfc / 0x1dfd 的含义。
