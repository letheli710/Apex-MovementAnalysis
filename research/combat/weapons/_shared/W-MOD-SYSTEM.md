# 公共部件 W：Mods（字段覆盖）系统

会话 wp1，2026-11-01，静态研究。出处从 `research-src/s21-platform/scripts/` 开始。

## 0. 概要

- **部件**：`.txt` 里的 `Mods` 块，所有配件、hop-up、模式切换、临时增益都用它。
- **一句话**：mod = 一组对武器字段的覆盖，运行时开关。配件、切换开火模式、临时 buff 都不用改代码。
- **分类**：系统。这是武器阶段**最值得搬的一个部件**：HSD 的配件、掉落、成长都可以挂在它上面。
- **可拆出的部件**：覆盖语法 → 3.1；脚本检查 → 3.2；回调 → 3.3。

## 1. 实现手段

| 用途 | 例子 | 来源 |
|---|---|---|
| 配件等级 | `bullets_mag_l1`：`ammo_clip_size 23`；稳定器 `viewkick_pitch_base *0.95` | `mp_weapon_rspn101.txt` |
| 开火模式 | Prowler 全自动：`fire_rate 13.25`、`is_semi_auto 0`、`burst_fire_count 0`、`viewkick_pattern pdw_auto_2` | `mp_weapon_pdw.txt:881-890` |
| 穿盾增伤 | `amped_damage`：`damage_near_value *1.2` 等 | `mp_weapon_rspn101.txt:822`；触发见 [C-DAMAGE-MODIFIERS](../../_shared/C-DAMAGE-MODIFIERS.md) 3.2.3 |
| 换弹种 | C.A.R. `alt_ammo` | `mp_weapon_car.nut:20` |
| 脚本判断 | `HasMod("hopup_smart_reload")` | `mp_weapon_hemlok.nut` |

## 2. 流程

```
AddMod("x") → 引擎把 x 的覆盖叠到基础字段 → GetWeaponSetting* 读到新值
RemoveMod("x") → 恢复
AddWeaponModChangedCallback(类名, 回调) → 脚本收到通知（mp_weapon_car.nut:33）
```

## 3. 代码

### 3.1 覆盖语法（全部 `mp_weapon_*.txt` 统计）

| 写法 | 含义 | 次数 |
|---|---|---|
| `"x"` | 直接替换 | |
| `"*x"` | 乘（推断从基础值起乘） | 13703 |
| `"++x"` | 加 | 222 |
| `"--x"` | 减 | 13 |

### 3.2 只有脚本含义的 mod

`.txt` 里内容为空的 mod（`hopup_gunshield`、`laser_sight_l1` 等）靠脚本 `HasMod` 生效。各族 `PARAMS.md` 末尾列出了这些 mod。

### 3.3 多个 mod 的先后

顺序看不到（引擎）。第 5 节。

## 4. 参数

每把枪的 mod 覆盖都在各族 `PARAMS.md` 的 "Mods 的玩法覆盖" 表里。配件汇总见 [attachments](../attachments/SYSTEM.md)，hop-up 见 [hopups](../hopups/SYSTEM.md)。

## 5. 未解决和要实测的

- **多个 `*x` 是连乘还是从基础乘后相加**：同时装 `barrel_stabilizer` 和 `amped_damage` 类的 mod，用 `GetWeaponSettingFloat` 读。

## 6. HSD 实现

**未实现。** 建议数据结构：`WeaponDef`（基础字段字典）+ `WeaponMod`（字段 → 运算）+ `WeaponInstance.Effective(field)`，按安装顺序应用。纯 C#，EditMode 能测。战斗层其他东西（配件、hop-up、状态效果、临时 buff）都走它。
