# 公共部件 W：扩散和后坐

会话 wp1，2026-11-01，静态研究。出处从 `research-src/s21-platform/scripts/` 开始。`vk` = `weapons/viewkick_patterns.txt`，`wu` = `vscripts/weapons/_weapon_utility.nut`。

**这部分几乎全在引擎里**：脚本不读这些字段（[W-S3-FIELD-CHECK](W-S3-FIELD-CHECK.md) 的 `in_vscripts` 列），下面的语义都是从字段名和数值**推断**的，第 5 节要实测。

## 0. 概要

- **部件**：子弹偏多少（扩散）和镜头怎么跳（后坐）。两件事分开算。
- **一句话**：**扩散**随机，由姿态决定基础值，每发累加，停火后回落。**后坐**是一张固定图案表（每发偏移），加弹簧和随机量。
- **分类**：效果、可视化（手感的主体）、系统（配件直接乘这些字段）。
- **可拆出的部件**：扩散状态机 → 3.1；固定后坐图案 → 3.2；图案 + 弹簧 → 3.3；腰射 / 开镜分开 → 第 4 节。

## 1. 实现手段

| 效果 | 手段 | 来源 |
|---|---|---|
| 扩散 | 引擎按 `spread_*` 算，开火时在圆锥内取方向；`dontApplySpread` 可关（霰弹用） | `wu:1378`（`fireBoltParams.dontApplySpread`） |
| 脚本侧扩散（NPC、霰弹工具） | `ApplyVectorSpread`：高斯 / 平坦 / 反高斯，`bias` 控制 | `wu:1052-1085` |
| 后坐图案 | `viewkick_pattern` 指向 `vk` 里一张表 | `weapons/mp_weapon_rspn101.txt` `"viewkick_pattern" "rspn101_2"`，`vk:845` |
| 弹簧 | `viewkick_spring` 指向弹簧配置（如 `rspn101_vkp`），`_hot` 是连射版，`heatpershot` 累加 | `weapons/mp_weapon_rspn101.txt:107` 起；弹簧配置本身不在 `.txt`，推断在引擎数据里 |

## 2. 流程

```
开火那一刻：
  扩散 = 姿态基础值(stand/crouch/air/hip/ads) + 累计 kick
  方向 = 圆锥内随机
  累计 kick += spread_kick_on_fire_*（不超过 spread_max_kick_*）
  镜头 += 图案第 n 发 × scale + 随机
停火：
  过 spread_decay_delay 后，累计 kick 按 spread_decay_rate 回落
  移动：spread_moving_increase_rate / decay_rate 在静止和跑动基础值之间过渡
```

## 3. 代码和数据

### 3.1 扩散字段（推断语义）

`spread_{stand,crouch,air}_{hip,ads}` 基础；`spread_stand_hip_run / _sprint`、`spread_wallrunning`、`spread_wallhanging` 特殊姿态；`spread_air_*_moving` 见 [W-S3-FIELD-CHECK](W-S3-FIELD-CHECK.md)。

### 3.2 后坐图案（`vk`）

```
"rspn101_2" {                              // vk:845
  "loop_offset" "0"   "start_max" "-1"
  "bullet_0" "-0.30 -0.54 0.40 0.40"       // 推断：yaw pitch 和两个随机幅度
  ...
}
```

- 表里共 30 张图案（`3030_repeater`、`alternator_2`、`autopistol_2`、`burstenergyar`、`car_smg`、`dragon_lmg`、`energy_ar_2/3`、`esaw_2/3`、`eva_double_tap`、`flatline_2`、`flatline_highcal`、`g2`、`g2_double_tap`、`hemlok_2/3`、`lmg_2`、`lstar_2/3/4`、`pdw_auto_2`、`pdw_burst_2`、`r97_2`、`rampart_turret`、`rspn101_2`、`rspn101_highcal`、`rspn101_zero`、`volt_2`、`autopistol_fusion`）。
- `loop_offset`：打完后从第几发循环（推断）。Spitfire `lmg_2` 共 30 发，循环点 23（`vk:541`）；R-301 `rspn101_2` 28 发，循环点 0（`vk:845`）。
- 同一把枪换模式就换图案：G7 `g2` → 双发 `g2_double_tap`（`weapons/mp_weapon_g2.txt:380`）；R-301 `rspn101_highcal`。

### 3.3 缩放字段

`viewkick_pitch_base / random / softScale / hardScale`、`viewkick_yaw_*`、`viewkick_roll_*`、`viewkick_scale_*`（按发数在 `min` 和 `max` 之间插值）、`viewkick_air_scale_ads`、`viewkick_move_scale`、`viewkick_duck_scale`。枪管稳定器就是乘 `viewkick_pitch_base` 等（`mp_weapon_rspn101.txt` `barrel_stabilizer_l1`：`*0.95`、random `*0.8`）。

## 4. 参数（代表枪，全部见各族 PARAMS.md）

| 枪 | 图案 | `spread_stand_hip` | `spread_stand_ads` | `spread_kick_on_fire_stand_hip` | `spread_max_kick_stand_hip` | `spread_decay_rate` | `viewkick_pitch_softScale` | `viewkick_yaw_softScale` |
|---|---|---|---|---|---|---|---|---|
| R-301 | `rspn101_2` | 3 | 0 | 0.2 | 2 | 100 | 2.325 | 0.725 |
| R-99 | `r97_2` | 2 | 0.35 | 0.18 | 2 | 12 | 4.25 | 2 |
| Flatline | `flatline_2` | 4.5 | 0 | 0.2 | 2 | 100 | 2 | 3 |
| Spitfire | `lmg_2` | 3 | 0 | 0.25 | 3.5 | 12 | 2.9 | 2.3 |
| Hemlok | `hemlok_2` | 4 | 0 | 0.45 | 3.75 | 18 | 1.75 | 0.8 |
| Wingman | 无 | 2.4 | 0 | 2.5 | 5.5 | 11 | 0.65 | 0.8 |
| Kraber | 无 | 8 | 0 | 1 | 12 | 4 | 1 | 1 |

规律：**步枪开镜扩散 0，SMG 开镜 0.35**；狙击腰射 8° 很大；单发枪没有图案，靠基础值和随机。Sheila 用负 `spread_kick` 越打越准（[rampart-sheila-weapon](../rampart-sheila-weapon/SYSTEM.md)）。

## 5. 未解决和要实测的

- **图案 4 列的含义和单位**：连开一匣打墙，弹孔和表比。场景：训练场静止、开镜。
- **`softScale` 和 `hardScale` 的差别**：推断前者是平滑的视角，后者是即时的。录视角角度曲线。
- **弹簧配置**：`rspn101_vkp` 的数值不在 `.txt`。查 `script_viewkick` 或引擎数据；否则只能拟合。
- **`spread_decay_rate` 单位**：R-301 是 100，R-99 是 12，推断 °/s。

## 6. HSD 实现

**未实现。** `TestRifle` 完全没有扩散和后坐（`Weapons.cs`）。`Camera/Native/NativeCamera.cs` 有落地的 view kick（CAM-02），但和武器无关，可以共用施加通道。

建议：`Weapon` 加 `SpreadState`（基础 + 累计 kick + 回落）和 `RecoilPattern`（读 `vk` 导出的表）。先按字段做，语义靠实测校准，差异写进 `R5-DIFF-ARCHIVE.md`。
