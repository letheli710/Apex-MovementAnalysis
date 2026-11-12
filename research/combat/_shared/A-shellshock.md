# 公共部件 A：Shellshock（炮击震荡：减速 + 景深模糊 + 调色）

批次 A 共用：Bangalore 滚雷（6 s）、Gibraltar 防御轰炸（4 s）、Mad Maggie 破坏球（3–6 s）。静态研究，2026-10-31，会话 combat-a。

来源根目录：`research-src/s21-platform/scripts/vscripts/`。`ss` = `mp/sh_shellshock.gnut`（247 行）。

## 0. 概要

- **部件**：`ShellShock_ApplyForDuration( player, duration )`（`ss:46-51`），伤害回调里调用。
- **一句话**：被炮击打到的**玩家**，加一个定时 `shellshock` 状态效果和一个 0.25 的移动减速；客户端看到状态效果后做屏幕调色、晃动的景深模糊、屏幕粒子和喘气声。
- **分类**：系统（定时状态效果 + 客户端按状态效果驱动表现）；可视化（"被炸懵"的屏幕表现）。
- **可拆出的部件**：
  - 服务端：定时状态效果（带淡出）→ 3.1
  - 客户端：按状态严重度驱动的景深振荡 → 3.2 `ShellShock_UpdatePlayerDOF`
  - 客户端：调色淡入淡出 → 3.2 `ShellShock_ColorCorrection`

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 状态标记 | 状态效果 `eStatusEffect.shellshock`，严重度 1.0，时长 = 参数，淡出 0.5 s | `ss:48` |
| 移动减速 | 状态效果 `move_slow`，严重度 0.25，同时长，淡出 0.5 s | `ss:49`；`SHELLSHOCK_MOVE_SLOW_EFFECT_WEIGHT` `ss:13` |
| 转向减速 | 注释掉了（原 0.25） | `ss:50`；`SHELLSHOCK_TURN_SLOW_EFFECT_WEIGHT` `ss:14` 未用 |
| 屏幕调色 | `ColorCorrection_Register("materials/correction/shell_shock.raw_hdr")`，0.25 s 淡入、1 s 淡出 | `ss:35`、`ss:214-230` |
| 景深模糊 | 每帧 `DoF_SetFarDepth/NearDepth`，远景深随 sin(6t) 振荡 | `ss:87-136` |
| 屏幕粒子 | `P_shell_shock_FP`，挂在镜头（cockpit）上；控制点 1 读的是 **gas_cloud** 的严重度（复制粘贴遗留，推断） | `ss:157-161`、`ss:203` |
| 声音 | `gruntcooper_wounded_loop_1p`，结束时 `..._end_1p` | `ss:164`、`ss:178-179` |

服务端 / 客户端：服务端只加状态效果；表现全在客户端的状态效果回调里（`StatusEffect_RegisterEnabledCallback`，`ss:40-41`）。**SDK 痕迹**：`ss:116`、`ss:153-156` 注释 "Match S21 original…" 和一段防 SCRIPT ERROR 的保护，说明这份文件被社区改过（只改了客户端健壮性，数值看起来未动，推断）。

**只对玩家**：三个调用方都写 `if ( victim.IsPlayer() ) ShellShock_ApplyForDuration(...)`，NPC 不吃减速（PvE 要自己补）。

## 2. 流程

```
伤害回调（damageSourceId 对应的炮击 / 破坏球）
 └ victim 是玩家 → shellshock(1.0, T, 淡出0.5) + move_slow(0.25, T, 淡出0.5)
客户端 shellshock 开始 →
 ├ 调色 0 → 1（0.25 s）
 ├ 屏幕粒子 + 喘气声
 └ 景深线程（距上次结束 < 1 s 就先等）
客户端 shellshock 结束 → 调色 1 → 0（1 s），景深 1 s 回默认，停声音
```

重复命中：再调一次 `StatusEffect_AddTimed` 会再叠一个句柄（引擎状态效果按最大严重度取，推断），时长按最后一次重新算。

## 3. 代码

### 3.1 入口（服务端）

`ShellShock_ApplyForDuration`（`ss:46-51`）：

```
AddTimed(player, shellshock, 1.0, T, fade=0.5)
AddTimed(player, move_slow, 0.25, T, fade=SHELLSHOCK_FADE_TIME 0.5)
```

### 3.2 客户端表现

- `ShellShock_StartVisualEffect`（`ss:138-168`）：只对本地视角玩家；非泰坦才加屏幕粒子和景深。
- `ShellShock_UpdatePlayerDOF`（`ss:87-136`）：

```
w = severity(shellshock)
s = GraphCapped(sin(6t), -1, 1, 0.25w, w)       // 在 0.25w..w 之间振荡，约 1 Hz
far  = (32 / s, 1024 / s)
near = (8 / w, 64 / w)
```

- `ShellShock_ColorCorrection` / `ColorCorrection_LerpWeight`（`ss:214-246`）：线性插值权重。

### 3.4 依赖

状态效果系统（`StatusEffect_*`，引擎 + `sh_status_effects`）；`move_slow` 的实际减速倍率由引擎按严重度换算（0.25 → 推断"速度 ×0.75"，见第 5 节）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小 |
|---|---|---|---|---|---|
| SHELLSHOCK_MOVE_SLOW_EFFECT_WEIGHT | 0.25 | 严重度 | `ss:13` | 移动减速强度 | 大 → 更慢 |
| SHELLSHOCK_TURN_SLOW_EFFECT_WEIGHT | 0.25 | 严重度 | `ss:14` | 未用（注释掉） | — |
| SHELLSHOCK_FADE_TIME | 0.5 | s | `ss:17` | 减速结束时淡出 | — |
| shellshock 淡出 | 0.5 | s | `ss:48` 字面量 | 状态淡出 | — |
| SHELLSHOCK_DURATION | 12.0 | s | `ss:16` | 未用（时长由调用方给） | — |
| DOF far inner / outer | 32 / 1024 | u | `ss:7-8` | 远景深基准 | 小 → 更糊 |
| DOF near inner / outer | 8 / 64 | u | `ss:10-11` | 近景深基准 | |
| DOF 振荡频率 | sin(t·6) | rad/s | `ss:119` | ≈0.95 Hz | |
| 调色淡入 / 淡出 | 0.25 / 1.0 | s | `ss:223`、`ss:227` | | |
| 调用方时长 | Bangalore 6.0；Gibraltar 4.0；破坏球 3–6（队友 3） | s | 各自记录 | | |

## 5. 未解决和要实测的

- **move_slow 0.25 到底是速度 ×0.75 还是别的映射**：严重度到速度的换算在原生代码。测法：火力训练场里用 runner 给自己 `StatusEffect_AddTimed(move_slow,0.25,5,0)`，记录地面冲刺稳定速度，对比无效果时。
- 重复命中的叠加规则（多个句柄是取最大还是相加）：连续被两发炮击，记录速度。
- 屏幕粒子控制点读 `gas_cloud` 严重度 → 炮击时这个值是 0，粒子强度可能停在最小值 5。在游戏里看一眼即可。

## 6. HSD 实现

**未实现**。建议：

- 在 `CombatCore.cs` 的 `CombatUnit` 已有 `slowScale` / `slowUntil`（电弧星用），直接复用：`ApplyShellshock(u, T)` → `slowScale = 0.75`（待第 5 节确认）、`slowUntil = now + T`，末 0.5 s 线性淡回 1（现有字段没有淡出，需要加一个 `slowFadeFrom`）。
- **对 NPC 也生效**（R5 只对玩家）：PvE 的价值就在减速敌人。这是和 R5 的差别，写进 `R5-DIFF-ARCHIVE.md`，开关 `hsd.combat.shellshockNpc`（默认开）。
- 屏幕效果放 `CombatVisuals.cs`：只在玩家被炸时画；先做调色 + 简单模糊，景深振荡公式照 3.2。
