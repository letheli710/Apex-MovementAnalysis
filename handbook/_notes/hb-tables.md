# hb-tables 备注（给总控、hb-integrate、各章）

2026-11-14，分支 `handbook/tables`（从 `handbook/base` d93f012），只写了 `handbook/tables/` 和这份备注。

## 做了什么

- `tables/params.tsv` + `.md`：150 个参数。126 一致、2 不一致、1 近似、2 Unity 没有、4 R5 没测过、5 只有 HSD、10 开镜 / 后坐（Unity 实现不在 main）。
- `tables/camera-events.tsv` + `.md`：76 行（43 一致、14 不一致、13 没测过、6 只有 HSD）。
- `tables/level-scale.tsv` + `.md`：38 行，全部由 `level_scale_harness/`（调游戏身体的移动代码）跑出来。
- `tables/check_params.py`：表和 Unity 导出逐行核对。现在通过；故意改坏时退出码 1。
- `tables/units-conversion.tsv`：01 §2.4 要的机器可读换算表。
- `tables/unity-export/`：Unity 单位导出全量快照（HSD-Unity `units/switch` 5c79a50）。

## 建议的 D 行（编号留空）

- D-??：**台阶高度**。R5 setfile `stepHeight` 22 u，Unity `MovementWorld.stepUp` 18 u（= TF2）。选项：A 改成 22（按 R5 复刻，D-36 原则）；B 保留 18、写进 R5-DIFF 二节。数据：关卡尺度表 LS-12 实跑 18 u。等用户定（`pending`）。
- D-??：**冲刺加速度**。R5 100（只有 Wraith 102），Unity 所有装备 102。选项：A 按传奇取（Wraith 102、其余 100）；B 保留 102、写进 R5-DIFF。差 2 %（到冲刺上限多约 0.017 s）。
- D-??：**R5 有、Unity 没有的两条滑铲 ConVar 规则**：`slide_step_velocity_reduction` 10（上台阶减速 10 × 台阶高）、`slide_max_angle_dot` 0.6（冲刺时偏离前方超过约 53° 不能起滑）。选项：实现（按 R5）/ 记进 R5-DIFF 不做。

## 给 hb-units（已直接发消息）

镜头事件表的子代理发现，`camera.m55.*`（M5.5 镜头，留作开关）有几处量纲标错。我核对过源码，确实对不上：

- `speedFovFrom` / `speedFovTo` / `slideFovFloorSpeed` / `slideFovPeakSpeed` 标成 `dps`（°/s，不换算），但代码拿它和水平速度比（`CameraFeedback.cs` 第 343 行），应为 `v`。
- `lagMax` 标成 `t`，注释写"|lag| ≤ lagMax"，lag 是长度，应为 `L`。
- `eyeDownSettle` / `eyeUpSettle` 标成 `L`，看名字和用法像时间常数，要核。
- `takeoffLift` 等 `*Lift` 标成 `a`，要核它们加进的 `lift` 是什么量。
- 只影响米模式下的 M5.5 镜头。hb-units 的等价检查跑的是原生镜头，所以没发现。

## 给各章

- **hb-ch02**：台阶 18 / 22（上面 D 行）；斜坡上限实跑 45.5°（法线 0.7 → 45.57°）。
- **hb-ch03**：原地跳实跑 54.8 u，不是 56：离散积分比连续公式少 V·dt/2（120 Hz 时 1.2 u）。README 示范条目写"照这个顺序做，跳到顶的高度才正好等于 jumpHeight"，应改成"连续公式等于 jumpHeight；按命令步进少 V·dt/2"，或者说明它指的是哪种量法。
- **hb-ch04**：平地滑铲 461 u / 1.69 s（和 M10 实测的 1.69 s 一致）；滑铲跳最远在按蹲后 0.208 s 起跳（292 u）。蹲着能上的最高墙 155 u，不爬墙的最高翻越 84 u。
- **hb-ch05**：跑墙三套规则实跑 550 / 536 / 701 u；二段跳 HSD 99.8 u、TF2 规则 114.8 u（用 R5 重力）。
- **hb-ch07**：横滚总上限有矛盾。N2-C §7 写"总上限 40°"，CAM2 §5 / CR §3.9 写"没有总上限，±180° 回绕"（`maxCameraRoll` 只封滑索分支 B）。镜头事件表照 CAM2 写，params C-09 两边都注了。镜头事件表另外列了 5 处来源矛盾（二段跳峰值、滑铲下沉时间、punch 进不进子弹、rodeo 横滚、D-86 被 D-88 取代），见 `camera-events.md`。

## 给 README / 00-INVENTORY（hb0 / 整合）

- README 目录里 `tables/` 一行的状态从"空"改成"完成（hb-tables）"，并链到 `tables/README.md`。
- 01 §2.4 说的 `units-conversion.tsv` 已经有了，列名见文件。参数总表的"量纲"列用 Unity 导出的量纲名（Length、Velocity……），由它决定怎么换；01 §2.4 里"类别"一列的说法可以改成"量纲"。

## 给 99-TODO（建议）

- 在 R5 里搭和 `level_scale_harness` 一样的几何（平地跳远、最高墙、坡上滑铲距离），跑一次对照。现在关卡尺度表只有 Unity 的数。
- TF2 本体的跑墙长度和二段跳高度没量过。
- `slideStopSpeed` 125 对 M10 实测 112 的差（S-05）还没细读。
