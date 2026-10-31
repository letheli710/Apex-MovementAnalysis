# 公共部件 E：屏幕调色 / 去色 / 驾驶舱粒子（Screen Color Correction）

批次 E（combat-e），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/`。
`ColorCorrection_*`、`GfxDesaturateOn/Off`、`EffectSetIsWithCockpit` 都是**引擎原生**，脚本只调用。批次 A 的 `_shared/A-shellshock.md`（`shell_shock.raw_hdr`）、`_shared/A-gas-cloud.md`（`gas_cloud.raw_hdr`）用的是同一套，可以对照。

## 0. 概要

- **部件**：客户端全屏 LUT 调色（按权重 0–1 混合），可选独占；加上"驾驶舱粒子"（贴在镜头上的屏幕特效）和全局去色。
- **一句话**：技能的"屏幕变色"= 注册一张 LUT，客户端状态效果开时把权重从 0 拉到 1，关时拉回 0；常配一个驾驶舱粒子。
- **分类**：可视化 ✔。
- **可拆出的部件**：
  - 权重线性插值 `ColorCorrection_LerpWeight` → 3.2.1
  - 权重跟状态效果严重度 / 剩余时间走 → 3.2.2
  - 全局去色 + 指定粒子不去色 → 3.2.3
  - 驾驶舱粒子（控制点调强度 / 颜色）→ 3.2.4

## 1. 它用什么实现各种效果

| 技能 | LUT | 淡入 / 淡出 | 权重来源 | 驾驶舱粒子 | 来源 |
|---|---|---|---|---|---|
| Forged Shadows | `ability_silence.raw_hdr` | 0.25 / 1.0 | 固定插值 | `p_rev_reborn_FP_ult_screen_base`（CP1 = 1,1,1）+ 护盾在时 `p_rev_reborn_FP_ult_screen_shield` | `mp_ability_shadow_form.nut:181`、`:1223-1249` |
| Beast of the Hunt | `ability_hunt_mode.raw_hdr` + `GfxDesaturateOn` | 0.0125 / 最后 5 s | `hunt_mode_visuals` 严重度 | `P_hunt_screen`（不去色） | `mp_ability_hunt_mode.nut:47`、`:647-686`、`:714`、`:742-744` |
| Eye of the Allfather | `area_sonar_scan.raw_hdr` | 0.5 / 0.5 | 固定插值 | `P_sonar` | `mp_ability_area_sonar_scan.nut:60`、`:746-777` |
| Silence（被沉默者） | `ability_silence.raw_hdr` | 立刻 1 / 15 s 线性 | 剩余 / 15 | `P_bSilent_screen_CP`（CP1.x = 剩余 / 15） | `sh_silence.gnut:60`、`:451-569` |
| Exhibit（区域内） | 无 LUT | — | — | `P_killroom_hud_static`（CP2.x = 强度，每帧 ±0.01；CP3 = 友 / 敌色；CP1 = 1,999,0） | `mp_ability_echo_locator.nut:1537`、`:1961-2086` |
| Death Totem | 无 LUT | — | — | 标记中 `P_Bshadow_screen`；召回 `P_training_teleport_FP`（0.25 s） | `mp_ability_revenant_death_totem.nut:1608-1671` |

本地脚本里所有 LUT（`vscripts/` 全局搜 `ColorCorrection_Register`）：`ability_hunt_mode`、`ability_silence`、`area_sonar_scan`、`gas_cloud`、`launch_hud`、`player_is_hurt`（.raw）、`shell_shock`、`smoke_cloud`、`soft_landing_passive`。

## 2. 流程

```
Init（客户端）：cc = ColorCorrection_Register("materials/correction/xxx.raw_hdr")
状态效果开 → SetExclusive(cc, true)；权重 0 → 1（或跟严重度）；起驾驶舱粒子
状态效果关 → 权重 → 0；（有的）SetExclusive(cc, false)；停粒子
```

## 3. 代码

### 3.1 接口

| 函数 | 作用 |
|---|---|
| `ColorCorrection_Register(path) → int` | 注册 LUT，返回句柄 |
| `ColorCorrection_SetWeight(cc, w)` | 混合权重 0–1 |
| `ColorCorrection_SetExclusive(cc, bool)` | 独占（推断：开着时其他 LUT 不混进来） |
| `GfxDesaturateOn()` / `Off()` | 全局去色（推断：高亮和标了不去色的粒子除外） |
| `Effects_SetParticleFlag(fx, PARTICLE_SCRIPT_FLAG_NO_DESATURATE, true)` | 这个粒子不被去色 |
| `StartParticleEffectOnEntity(cockpit 或 player, fx, …)` + `EffectSetIsWithCockpit(fx, true)` | 驾驶舱粒子 |
| `EffectSetControlPointVector(fx, i, v)` | 粒子控制点（强度、颜色、范围） |

### 3.2 核心逻辑

#### 3.2.1 `ColorCorrection_LerpWeight(cc, start, end, time)`

同一份代码复制在 `mp_ability_shadow_form.nut:1425-1439` 和 `mp_ability_area_sonar_scan.nut:779-793`（批次 A 的 `sh_shellshock.gnut` 也有一份）：

```
SetExclusive(cc, true)
t0 = now；t1 = t0 + time
while now <= t1: WaitFrame；SetWeight(cc, GraphCapped(now, t0, t1, start, end))
SetWeight(cc, end)
```

注意：淡出结束后**没有** `SetExclusive(false)`，下一张 LUT 开时再设自己的独占（推断：独占是"最后设的赢"）。

#### 3.2.2 权重跟状态走

- 严重度：`w = GraphCapped(now − start, 0, 0.0125, 0, GetSeverity(hunt_mode_visuals))`（`hunt_mode.nut:676-685`），淡出靠状态效果的 fadeOut（5 s）。
- 剩余时间：`w = GetTimeRemaining / 总时长`（`sh_silence.gnut:490-501`）。

#### 3.2.3 去色

Hunt Mode 开时 `GfxDesaturateOn()`，屏幕粒子标 `NO_DESATURATE`（`hunt_mode.nut:714`、`:744`）；Exhibit 的脚印、锁定框也都标了 `NO_DESATURATE`（`mp_ability_echo_locator.nut:1717`、`:1950`），为的是 Bloodhound 开大招时 Seer 的标记还是彩色。

#### 3.2.4 驾驶舱粒子强度渐变

Exhibit：每帧 `当前 += sign(目标 − 当前) × 0.01`，写 CP2.x（`mp_ability_echo_locator.nut:2023-2036`）。和帧率耦合。

### 3.3 客户端表现

本部件全在客户端。

### 3.4 依赖

状态效果框架（`_shared/E-STATUS-EFFECT.md`）；引擎原生调色和粒子。

## 4. 参数

见第 1 节表格。LUT 内容（颜色曲线）在 `.raw_hdr` 资源里，脚本看不到。

## 5. 未解决和要实测的

1. **各 LUT 的颜色**：资源文件没解包。测法：开技能前后同一位置截图，对比色彩（或解包 `materials/correction/*.raw_hdr`）。
2. **独占的规则**（两个技能同时开时谁赢）：测法：Bloodhound 大招中被沉默，看画面。
3. **去色强度**：截图对比。

## 6. HSD 实现

**未实现。** `CombatVisuals.cs` 只画几何体，没有后处理。

建议：URP Global Volume，每种效果一个 Volume Profile（Color Lookup / Color Adjustments：饱和度、色调、对比度），脚本只改 `Volume.weight`；独占 = 同时只让一个效果 Volume 权重 > 0（或按优先级）。驾驶舱粒子用贴在相机前的全屏 UI 图 / 粒子，强度参数对应 R5 的 CP。HSD 有自己的外观，LUT 颜色不用照抄，**淡入 / 淡出时长和权重来源照 R5**。开关：`hsd.combat.screenFx`（总开关）。
