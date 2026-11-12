# 公共部件 E：状态效果框架（Status Effect）

批次 E（combat-e），2026-10-31，静态研究。来源根：`research-src/s21-platform/scripts/`。
`StatusEffect_*` 全是**引擎原生函数**，脚本里没有定义（`vscripts/` 全局搜 `function StatusEffect_` 无结果），类型表在 `status_effect_types.txt`（约 130 个）。本文从批次 E 七个技能的用法归纳接口和规则；规则里凡是"原生内部怎么算"的都标推断。批次 A 的 `_shared/A-shellshock.md` 第 4 节也用了同一框架，可以对照。

## 0. 概要

- **部件**：实体身上的一组"状态"，每个有类型、严重度（0–1 浮点）、时长或无限期、淡出时间。服务端加 / 停，自动同步到客户端；客户端注册"开 / 关"回调做表现。
- **一句话**：R5 几乎所有"持续中的效果"（大招计时、加速、减速、沉默、被扫描、在区域里、HUD 数字）都靠它，技能脚本只管加和停，画面在客户端回调里做。
- **分类**：系统 ✔（HSD 战斗层最该先做的底层部件）。
- **可拆出的部件**：
  - 计时器：`AddTimed` + `GetTimeRemaining` + `SetDuration`（延长）→ 3.2.1
  - 无限期开关：`AddEndless` + 句柄 `Stop` → 3.2.2
  - 强度随时间淡出：严重度当权重 → 3.2.3
  - 把一个整数编码进严重度传给 HUD → 3.2.4
  - 客户端开 / 关回调驱动表现 → 3.3

## 1. 它用什么实现各种效果（批次 E 的全部用法）

| 状态效果 | 谁加 | 严重度 / 时长 / 淡出 | 用途 | 来源 |
|---|---|---|---|---|
| `shadow_form` | Forged Shadows | 1.0 / 25 / 0 | 大招是否在生效 + HUD 剩余时间；延长时 `SetDuration` | `mp_ability_shadow_form.nut:516`、`:1137`、`:1308` |
| `threat_vision` | Hunt Mode | 1.0 / 无限 | 原生画敌人 | `mp_ability_hunt_mode.nut:275` |
| `speed_boost` | Hunt Mode | 0.15 / 无限 | 移速 +15%（推断：严重度即加成比例） | `:276` |
| `hunt_mode` | Hunt Mode | 1.0 / D / D | 计时（HUD） | `:279` |
| `hunt_mode_visuals` | Hunt Mode | 1.0 / D / 5 | 画面开关 + 调色权重 | `:280` |
| `disable_wall_run` / `disable_double_jump` | Hunt Mode、Death Totem | 1.0 / 2.1 或无限 | 动作期间禁移动能力 | `:240-241`；`mp_ability_revenant_death_totem.nut:242-244` |
| `device_detected` | Area Sonar | 0.01 → (2+n)×0.01 / 3 / 0 | HUD 显示扫到几个 | `mp_ability_area_sonar_scan.nut:152`、`:384` |
| `sonar_pulse_visuals` | Area Sonar | 1 / 3 / 0 | 扫描者屏幕效果 | `:153` |
| `sonar_detected` | `SonarStart` | 1.0 / 无限 | 被扫者提示 + 高亮管理 | `sh_sonar.gnut:338` |
| `lockon_detected` | `LockOnWarningStart` | 1.0 / 无限（引用计数） | 被锁定提示 | `sh_sonar.gnut:200-229` |
| `inside_echo_locator` | Exhibit | 1.0 / 无限 | 在区域里 | `mp_ability_echo_locator.nut:867` |
| `death_totem_visual_effect` | Death Totem | 1.0 / 25 / 0 | 标记有效 + HUD | `mp_ability_revenant_death_totem.nut:1357` |
| `death_totem_recall` | Death Totem | 1.0 / 0.25 / 0.25 | 召回屏幕特效 | `:820` |
| `move_slow` | Death Totem | 0.9 / 1.5 / 0.5 | 召回后减速 | `:818` |
| `silenced` + `silenced_rev_visuals` | Silence | 1.0 / 15 / 15 | 禁技能 + 画面 | `sh_silence.gnut:184-185` |
| `interrupted` | Silence（可选） | 1.0 / 0.25 / 0.25 | 打断 | `sh_silence.gnut:190` |

## 2. 流程

```
服务端：id = StatusEffect_AddTimed(ent, type, severity, duration, fadeOut)    // 或 AddEndless(ent, type, severity)
        → 引擎同步到客户端
客户端：该类型"开"回调 (ent, type, actuallyChanged)
        每帧可读 GetSeverity / GetTimeRemaining
时间到 → 自动移除 → 客户端"关"回调
或 服务端 StatusEffect_Stop(ent, id) / StopAllOfType(ent, type) → "关"回调
```

## 3. 代码

### 3.1 接口（从调用处归纳）

| 函数 | 用法 | 例 |
|---|---|---|
| `StatusEffect_AddTimed(ent, type, severity, duration, fadeOut) → id` | 定时；第 5 参数推断为淡出时长（严重度在最后 fadeOut 秒内降到 0） | `hunt_mode.nut:280`（`fadeOut=5`，调色最后 5 s 淡出） |
| `StatusEffect_AddEndless(ent, type, severity) → id` | 无限期，必须手动停 | `hunt_mode.nut:275` |
| `StatusEffect_Stop(ent, id)` | 停一个句柄 | `shadow_form.nut:566` |
| `StatusEffect_StopAllOfType(ent, type)` | 停这个类型的全部句柄 | `hunt_mode.nut:108` |
| `StatusEffect_HasSeverity(ent, type) → bool` | 有没有（严重度 > 0） | `shadow_form.nut:293` |
| `StatusEffect_GetSeverity(ent, type) → float` | 当前严重度（含淡出；多个句柄时推断取最大） | `hunt_mode.nut:678` |
| `StatusEffect_GetTimeRemaining(ent, type) → float` | 剩余时间 | `shadow_form.nut:629` |
| `StatusEffect_SetDuration(ent, id, newDuration)` | 改时长（延长） | `shadow_form.nut:1137` |
| `StatusEffect_RegisterEnabledCallback(type, fn)` / `…DisabledCallback` | 客户端开 / 关回调，`fn(ent, type, actuallyChanged)` | `shadow_form.nut:182-183` |
| `RuiTrackFloat(rui, key, ent, RUI_TRACK_STATUS_EFFECT_TIME_REMAINING, type)` | HUD 直接跟踪剩余时间 | `shadow_form.nut:1308` |

### 3.2 核心逻辑（常见写法）

#### 3.2.1 计时器 + 延长

两种延长写法：
- Revenant：`SetDuration(id, clamp(剩余 + 5, 0, 25))`（`shadow_form.nut:1136-1137`），保留同一个句柄。
- Bloodhound：`StopAllOfType` 再 `AddTimed(剩余 + ext)`（`hunt_mode.nut:108-111`），新句柄；同时改服务端自己的 `endTimes` 表，因为它的结束判断靠表不靠状态效果。

#### 3.2.2 无限期 + 统一停

一个"模式"里的无限期效果（威胁视觉、加速）放进 `ids` 数组，守护线程结束时统一 `Stop`（`hunt_mode.nut:466-578`）。

#### 3.2.3 严重度当表现权重

`hunt_mode_visuals` 淡出 5 s → 客户端每帧 `GetSeverity` 当调色权重（`hunt_mode.nut:678-682`）。沉默不用淡出，客户端自己算 `剩余 / 总时长`（`sh_silence.gnut:492-495`）。

#### 3.2.4 用严重度传整数

`device_detected` 严重度 = (2 + 扫到数) × 0.01，HUD 解码（`mp_ability_area_sonar_scan.nut:380-384`）。

#### 3.2.5 状态效果当"是否在里面"

`inside_echo_locator`：服务端按区域判定加 / 停，多个区域叠加时自己记 `insideList` 引用计数，最后一个出去才停（`mp_ability_echo_locator.nut:842-933`）。

### 3.3 客户端表现

回调的固定写法（几乎每个技能都一样）：

```
fn(ent, type, actuallyChanged):
   if !actuallyChanged && 本地视角 == 本地客户端: return      // 预测重放时不重复触发
   if ent != 本地视角玩家: return                               // 只做自己的画面
   ...开画面线程，线程 EndSignal 一个"停"信号
关回调：Signal 那个"停"信号
```

例：`shadow_form.nut:1189-1211`、`hunt_mode.nut:706-732`、`mp_ability_echo_locator.nut:1520-1542`。

### 3.4 依赖

引擎原生。类型表 `status_effect_types.txt`。

## 4. 参数

框架本身没有参数；各技能的严重度 / 时长 / 淡出见第 1 节和各 SYSTEM.md 第 4 节。

## 5. 未解决和要实测的

1. **第 5 参数的含义**：推断是淡出时长。测法：AgentLink 加 `AddTimed(x, 1.0, 10, 5)`，每 0.5 s 读 `GetSeverity`，看是不是最后 5 s 线性降。
2. **多个句柄怎么合成**：取最大还是相加。测法：同类型加两个不同严重度（0.2、0.5），读 `GetSeverity`。
3. `speed_boost` / `move_slow` 严重度到实际速度倍率的换算（移动层，原生）。测法：加 0.15 / 0.9 后读冲刺速度。

## 6. HSD 实现

**未实现。** HSD Combat 现在每个道具自己存时间戳（例如 `CombatCore.cs:79` `outlinedUntil`、`:77` `slowUntil`）。

建议：在 `CombatCore.cs` 加 `StatusEffects` 表（每个单位一个）：

```
Add(type, severity, duration, fadeOut) → id
AddEndless(type, severity) → id
Stop(id) / StopAll(type)
Severity(type, now)   // 多句柄取最大（待第 5 节确认）；淡出段线性
Remaining(type, now)
SetDuration(id, d)
事件：OnEnabled(type) / OnDisabled(type)（给 CombatVisuals / CombatHud 用）
```

`outlinedUntil` / `slowUntil` 这类字段以后可以迁到这个表里（旧字段留着，迁移时进 `R5-DIFF-ARCHIVE.md`）。纯 C#，EditMode 测试可直接跑。
