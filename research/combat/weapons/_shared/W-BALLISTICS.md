# 公共部件 W：子弹怎么飞（弹道 / 命中扫描）

会话 wp1，2026-11-01，静态研究。出处从 `research-src/s21-platform/scripts/` 开始。`wu` = `vscripts/weapons/_weapon_utility.nut`，`bb` = `vscripts/weapons/mp_weapon_basic_bolt.nut`。

## 0. 概要

- **部件**：枪怎么把子弹发出去。
- **一句话**：Apex 的枪几乎全是**有速度、有下坠的弹道子弹**，不是命中扫描。真正写了 `ballistic_type hitscan` 的只有两个文件。
- **分类**：系统（HSD 现在的 `TraceBullet` 是命中扫描，要加弹道子弹才贴近 R5）。
- **可拆出的部件**：归零补偿 → 3.1；开火 API 三选一 → 1；命中盒随时间变大 → 4。

## 1. 三种开火 API

| API | 谁用 | 发出什么 | 来源 |
|---|---|---|---|
| `weapon.FireWeapon_Default(pos, dir, speedScale, patternScale, ignoreSpread)` | 大部分枪；没绑 `OnWeaponPrimaryAttack` 的枪走引擎默认（推断也是这条路） | 引擎按 `.txt` 决定：弹道子弹 / 图案弹丸 | `mp_weapon_r97.nut:27`、`mp_weapon_rspn101.nut:27` |
| `FireBallisticRoundWithDrop(...)` → `FireWeaponBoltAndReturnEntity` | Kraber（`mp_weapon_sniper.nut:85`）、`bb`、霰弹工具函数 | 脚本算好归零后发一个 bolt | `wu:1378`，`bb:62-76` |
| `weapon.FireWeaponBullet(pos, dir, n, flags)` / `FireWeaponBullet_Special` | Havoc 替代开火（`mp_weapon_energy_ar.nut:119`）、Instagib（`mp_weapon_clickweapon.nut:404`）、智能弹药（`sh_smart_ammo.gnut:273`） | 命中扫描（推断，函数名和 `mp_weapon_clickweapon.nut:1` 注释 "hitscan rail"） | |

**绑定陷阱**：很多 `.nut` 里写了 `OnWeaponPrimaryAttack_xxx`，但 `.txt` 没绑。Alternator（`mp_weapon_alternator_smg.nut:47` 用 `FireWeaponBullet`）、Spitfire、Longbow、Kraber 的 `.txt` 里都查不到 `"OnWeaponPrimaryAttack"` 这一行（grep 结果），所以这些 `.nut` 函数**可能根本没被调用**，开火走引擎默认。Alternator 的命中扫描函数因此不能算数，第 5 节要实测。

`ballistic_type hitscan` 只出现在 `weapons/mp_weapon_buster_rifle.txt:58` 和 `weapons/mp_weapon_shotgun_pistol_energy.txt:8`。

## 2. 流程（一发子弹）

```
按键 → 引擎按 fire_rate 放行 → OnWeaponPrimaryAttack（没绑就默认）
→ 在扩散圆锥里定方向（W-SPREAD-RECOIL）
→ 生成 bolt，speed = projectile_launch_speed，重力 = sv_gravity × projectile_gravity_scale
→ 每帧移动，碰撞（命中盒 bolt_hitsize，见第 4 节）
→ 命中：按飞行距离算伤害（W-DAMAGE）→ OnProjectileCollision（大多是空函数）
→ 活过 projectile_lifetime 消失
```

客户端预测：`bb:62-76` 判断 `IsServer() || weapon.ShouldPredictProjectiles()`，客户端也生成一份弹道（`clientPredicted`）。Kraber 同样（`mp_weapon_sniper.nut:75-85`）。

## 3. 代码

### 3.1 归零补偿（`wu:1378-1418`，`FireBallisticRoundWithDrop`）

```
if bolt_gravity_enabled:
    z = bolt_zero_distance（缺省 4096）
    g = sv_gravity × projectile_gravity_scale
    t = z / speed
    dir += (0, 0, 0.5 × g × t) / speed     // GetZVelocityForDistOverTime，wu:1430-1440
```

**含义**：子弹抬一点点，让它在 `bolt_zero_distance` 正好回到准星上；更近时打高一点，更远时下坠。R-301 `bolt_zero_distance 1968.5`（`weapons/mp_weapon_rspn101.txt:226`，1968.5 u = 50 m）。

下坠公式（相对直线，不算归零）：`drop = 0.5 × g × (d / speed)²`。

### 3.2 工具函数

`FireGenericBoltWithDrop`（`wu`，紧跟 `GetZVelocityForDistOverTime` 之后）是另一个简化版，只带扩散不补偿。

## 4. 参数

每把枪的值见各族 `PARAMS.md` 的"弹道"一段，比较表见 [W-PARAM-COMPARE](W-PARAM-COMPARE.md)。

| 字段 | 例子 | 单位 | 作用 | 改大 / 改小 |
|---|---|---|---|---|
| `projectile_launch_speed` | R-99 19000；R-301 29000；Charge Rifle 33999；Ray Gun 2200；Bocek 10000（满弦另有字段） | u/s | 初速 | 大 = 近似命中扫描；小 = 要提前量 |
| `projectile_gravity_scale` | R-301 1.3；L-STAR 0.5；Ray Gun 0 | 倍 | 下坠 | |
| `bolt_gravity_enabled` | 多数 1；Ray Gun 0 | 开关 | 归零补偿和重力 | |
| `bolt_zero_distance` | R-301 1968.5 | u | 归零距离 | |
| `bolt_hitsize` + `bolt_hitsize_grow1_time / size`、`grow2`、`growfinal` | 多数枪 0 起步；Ray Gun 10；Mastiff 0.4 | u | 子弹碰撞半径，随时间变大（字段语义推断） | PvE 对小怪容错 |
| `projectile_lifetime` | R-301 5 | s | 超时消失 | 决定最大射程 |
| `projectile_ricochet_max_count` | | 次 | 反弹 | Kraber 在 `OnProjectileCollision` 里计数（`mp_weapon_sniper.nut:97-104`） |
| `pass_through_depth`、`pass_through_damage_preserved_scale` | | | 穿透 | |

**S21 / S3**：`projectile_launch_speed`、`bolt_zero_distance`、`projectile_drag_coefficient`、`ballistic_type` 两边引擎都认。分段重力 `projectile_gravity_scale_2 / _final` 和 `projectile_air_friction*` S3 引擎不认，SDK 只读入（`s21-r5sdk/src/game/server/weapon_kv_s21_ext.cpp`），文件外没发现使用方（[W-S3-FIELD-CHECK](W-S3-FIELD-CHECK.md)）。用到它们的主要是投掷物和 Bocek，推断 dedi 弹道和客户端预测不一致，要实测。

## 5. 未解决和要实测的

- **分段重力**：Bocek 远距离下坠，dedi 和客户端弹道比。
- **弹速和下坠实测**：R-301、Kraber 打 2000 / 5000 u 的墙，记落点和命中时间，和公式比。为什么：引擎里的积分方式和 `drag` 看不到。
- **Alternator 是不是命中扫描**：`.txt` 没绑函数，只能靠测。打远处移动目标看有没有提前量。
- **`bolt_hitsize_grow*` 的语义**：字段名推断，脚本不读（`W-S3-FIELD-CHECK`）。贴着假人边缘开火，分距离测命中率。

## 6. HSD 实现

**部分有。** `CombatSim.TraceBullet`（`HSD-Unity/Assets/HSD/Game/Runtime/Combat/CombatSim.cs`）是命中扫描，`Weapon.Shoot`（`Weapons.cs`）用它。没有弹道子弹。`Throw.cs` 有投掷物的抛物线和预测，可以复用积分。

建议：加 `BallisticRound`（纯 C#，进 `CombatSim` 的每步更新），字段就用第 4 节这些。命中扫描保留，给 `ballistic_type hitscan` 和 PvE 上快速判定用。进 `R5-DIFF-ARCHIVE.md` 的差别等实现时再写。
