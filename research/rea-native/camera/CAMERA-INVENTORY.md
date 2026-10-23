# C1 第一人称镜头效果清单

日期 2026-10-23（N1）。对应计划 [§5.1](../REA-PLAN-DRAFT.md)。逐条数据在 [../map/camera-effects.csv](../map/camera-effects.csv)。

**方法**：在 dx12 客户端里找所有名字带 view / punch / tilt / roll / drift / fov / eye / shake / sway / offset 的 setfile 键（共 81 个）和 ConVar（地图里被读到的共 120 个），再找出读它们的函数（`n1/SetfileReaders.java`、`n1/MapMovement.java`）。一个函数读的一组参数，就对应一个效果。

**这一步只回答"有哪些、叫什么、由什么触发、在哪里算"。** 每个效果具体怎么算是 C2（N2）的事，目前一行公式都还没读。

## 1. 清单

| id | 效果 | 触发 | 通道 | 原生函数（dx12） | 主要参数 |
|---|---|---|---|---|---|
| CAM-01 | **view punch 弹簧**（所有移动类 punch 的衰减） | 下面各种 punch | 俯仰 / 偏航 / 横滚 | `0x140a34170` | ConVar `viewpunch_base_springConstant` / `Damping` 的 X/Y/Z；setfile `viewPunchSpring` |
| CAM-02 | **落地 view kick** | 落地 | 俯仰（punch） | `0x140a35750` | setfile `viewkickFallDistMin` / `Max` / `MaxScale`；`sv_gravity`；同一函数还触发手柄震动（`rumbleOnLanding*`） |
| CAM-03 | 墙跑开始 punch | 开始墙跑 | 三轴 punch | `0x140a34e40` | setfile `wallrun_viewpunch_onStart_base*` / `random*` |
| CAM-04 | 墙跑超时 punch | 墙跑超时结束 | 三轴 punch | `0x140a35170` | setfile `wallrun_viewpunch_onTimeout_*` |
| CAM-05 | **横滚汇总**：侧移、滑铲、墙跑、闪避、冲刺 | 侧向移动、滑铲、墙跑、闪避、冲刺 | 横滚 | `0x140afc480` | ConVar `sv_rollangle`、`sv_rollspeed`（Source 的侧移横滚）、`slide_viewTilt*`、`wallrun_maxViewTilt`、`wallrun_viewTiltSpeed`、`dodge_viewTilt*`；setfile `sprinttiltMaxRoll` |
| CAM-06 | 墙跑倾斜预测 | 墙跑 | 横滚 | `0x140a4d4e0` | ConVar `wallrun_viewTiltPredictTime` |
| CAM-07 | 冲刺倾斜 | 冲刺中转向 | 横滚，经 PoseParameter 交给动画 | `0x140a5a430`、`0x140a5a630` | ConVar `sprinttilt_accel`、`sprinttilt_maxvel`、`sprinttilt_turnrange`；netvar `m_sprintTilt*` |
| CAM-08 | 冲刺视角偏移 | 冲刺 | 位置 | `0x140af2370` | setfile `sprintViewOffset` |
| CAM-09 | **滑铲 FOV** | 滑铲 | FOV | `0x1407f2bb0` | setfile `slideFOVScale`、`slideFOVLerpInTime`、`slideFOVLerpOutTime` |
| CAM-10 | **眼高**（站立、蹲下、滑铲下沉） | 蹲、滑铲、起身 | 位置（z） | `0x140a53d50`、`0x140a53f30`、`Duck` `0x140a54080` | setfile `viewheight`（向量，按姿态）；SDK 名 `SetDuckedEyeOffset` |
| CAM-11 | 钩爪镜头横滚 | 钩爪拉动 | 横滚 | `0x1407fac60` | setfile `grapple_roll*`（6 个） |
| CAM-12 | 摆荡镜头横滚 | 钩爪摆荡 | 横滚 | `0x1407fb0f0` | setfile `swingRoll*`。S21 Pathfinder 的 `grapple_swing = false`（M10），这项可能不生效 |
| CAM-13 | 滑索镜头横滚 | 滑索转弯 | 横滚 | `0x1407fb580` | setfile `ziplineRoll*`、`maxCameraRoll`、`ziprailMaxCurvatureRollAngle`；ConVar `ziprail_roll_strength` |
| CAM-14 | 滑索倾斜 | 滑索 | 横滚，经 PoseParameter | `0x14074bd60` | ConVar `banktilt_accel`、`banktilt_maxvel`；netvar `m_ziprailBankTilt*` |
| CAM-15 | 滑索视角偏移 | 滑索 | 位置 | `0x140b110c0` | setfile `ziplineViewOffset` |
| CAM-16 | **攀越 / mantle 视角过渡** | mantle、攀越 | 位置 + 角度 | `0x1406668a0`（SDK 名 `GetTraversalViewPosition`） | ConVar `traversal_viewLerpInDuration`、`traversal_viewLerpOut*` |
| CAM-17 | mantle 角度缩放 | mantle | 角度 | `0x140a40710` | setfile `mantleAngleScale`。可能只是判定条件，不是镜头效果（N2 确认） |
| CAM-18 | cockpit sway（移动和转向时的摇摆） | 移动、转向 | 位置 + 角度 | `0x1405fc020` | setfile `cockpitSway*`（20 个） |
| CAM-19 | cockpit 弹簧 | 第一人称装置的运动 | 位置 + 角度 | `0x1407ef190` | setfile `cockpit_spring_*`（8 个） |
| CAM-20 | view drift | 待机或瞄准（ADS） | 俯仰 / 偏航 | `0x140af0d00`、`0x140af15a0` | ConVar `viewDrift` 和 40 个 `viewDrift_*`（振幅、频率、相位）；`cockpitDrift_*` |
| CAM-21 | 屏幕震动的施加 | 脚本和动画事件调用 `ClientScreenShake` | 位置 + 角度 | `0x140838830` | ConVar `shake_angleFactor_human`、`shake_offsetFactor_human`；触发点在脚本（`cl_player.gnut:624`、`sh_anim_events.gnut:433`、`sh_survival_freefall.gnut:2241`）和动画事件里 |
| CAM-22 | 窗户提示的视野判定 | 穿窗户 | 视野锥判定，不是效果 | `0x140a58560` | ConVar `window_hint_fov_*` |
| CAM-23 | 上升气流震动 | Valkyrie / 上升气流 | 抖动 | 未定位 | netvar `m_updraftMin/MaxShakeActivationHeight` |

**边界项**（只登记，不研究）：

| id | 内容 | 位置 |
|---|---|---|
| BND-01 | 手臂和武器模型的晃动（viewmodel shake、蹲下偏移） | `0x14085bdb0`、`0x14085c3e0`；`viewmodelShake`、`shake_viewmodelFactor_*`、`viewmodelDuckOffset` |
| BND-02 | 武器后坐力 | 武器 `viewkick_*` 键、netvar `m_vecPunchWeapon_*` |
| BND-03 | 受伤或被技能打中的 punch | `sh_damage_utility.gnut`、`_pilot_passive_newcastle.gnut` |

## 2. 初步观察

- **移动类镜头效果基本都是原生代码算的，参数是 setfile 键和 ConVar。** 脚本里只有屏幕震动（CAM-21）的触发点。
- **所有 punch 共用一个弹簧**（CAM-01），三轴各有弹性系数和阻尼。落地、墙跑开始、墙跑超时各自只决定"踢一下"的大小。复现时先复现这个弹簧，再逐个加触发。
- **横滚集中在一个函数里**（CAM-05），而且用到了 Source 引擎的 `sv_rollangle` / `sv_rollspeed`。这说明侧移时镜头横滚是 Source 的老规则，滑铲、墙跑、闪避、冲刺的倾斜都叠加在同一个地方。叠加方式是 C2 的重点。
- **有两类效果的一部分在动画里**：冲刺倾斜（CAM-07）和滑索倾斜（CAM-14）是代码算一个比例、交给动画用；屏幕震动有一部分由动画事件触发。这些只能靠 C3 逐帧实测拿曲线。
- 滑铲下沉（眼高变化）的过渡曲线还没找到具体代码，只知道眼高来自 setfile `viewheight`，由 `Duck` 一带的函数处理。

## 3. 还没覆盖的

- 跑步晃动（head bob）：**没有找到** bob 类参数。Apex 的跑步晃动可能完全来自第一人称动画（镜头挂在动画骨骼上），或者来自 cockpit sway（CAM-18）。C2 先确认 CAM-18 / CAM-19 是在动镜头还是只在动手臂；如果都不是，就由 C3 实测确认。
- 跳跃起跳时的镜头变化、钩爪发射和收回时的 punch：没找到专门的参数，可能在 `Jump` 或钩爪代码里直接调用 punch。C2 读 `ApplyViewPunch` 的调用方时补上。
- CAM-23 的读取函数。
