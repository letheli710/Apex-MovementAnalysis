# 公共部件 B：放置与部署（放置器、粘附落地、贴地铺开、数量上限）

批次 B，会话 `combat-b`，2026-10-31。只读脚本。

来源根目录：`research-src/s21-platform/scripts/`。

## 0. 概要

- **部件**：四种"把东西放到世界里"的写法，B 批 10 个技能全部用到其中一种或几种。
- **分类**：系统。
- **可拆出**：
  - 引擎放置器（按住预览、松开放下）→ 3.1
  - 投出去、落地粘附（`PlantStickyEntity` 系列）→ 3.2
  - 从一点沿地面铺开一串（线 / 网格 / 蛇形）→ 3.3
  - 每人数量上限，超出挤掉最旧 → 3.4

## 1. 谁用哪种

| 技能 | 放置器 | 投出粘附 | 贴地铺开 | 数量上限 |
|---|---|---|---|---|
| Wattson 电网 | ✔（+ 脚本校验、64 u 吸附） | | | 12（`AddNewLimitedLegendObject`） |
| Wattson 拦截塔 | ✔ | | | 1 / 2（`activeUltimateTraps`） |
| Ash 电弧陷阱 | | ✔（碰到就粘） | | 每人 1 个飞行体 |
| Catalyst 尖刺 | | ✔（法线 z > 0.75 才粘） | 9×3 网格 | 2 / 3（`activeTraps`） |
| Catalyst 黑幕 | ✔ | | 20 根柱子一条线 | 1 |
| Conduit 屏障 | | ✔（`…ThatBouncesOffWalls`，45°） | 空爆分撒 7 个 | 14 |
| Newcastle 城墙 | （落点选择是自己写的） | | 蛇形 | 1 |
| Newcastle 移动盾 | | 落地即部署 | | 1 |
| Horizon 黑洞 | | `ThrowDeployable` | | 1 |

## 2. 流程

```
放置器：按住 → 每帧客户端代理模型 + 合法性（引擎 + OnObjectPlacementCanPlace 脚本回调）→ 开火时服务端再算一次
投出粘附：投掷物碰撞回调 → 判表面（法线）→ PlantStickyEntity → 隐藏投掷物、生成部署体
贴地铺开：从落点出发，每步"抬高 → 前进 → 向下找地"，失败就停或剪掉
数量上限：新部署体插到表头，表长 > 上限 → 删表尾
```

## 3. 代码

### 3.1 引擎放置器（`.txt` 字段）

`object_placer 1` 打开；关键字段（以电网为例，`weapons/mp_weapon_tesla_trap.txt`）：

| 字段 | 电网 | 拦截塔 | 黑幕 | 含义（推断） |
|---|---|---|---|---|
| `object_placement_distance_max` | 300 | 94 | 100 | 最远放置距离 |
| `object_placement_hill_angle_max` | 50 | 45 | 45 | 最大坡度（度） |
| `object_placement_drop_to_ground_offset_max` | 72 | 72 | 400 | 瞄空中时向下找地的最大距离 |
| `object_placement_distance_to_ground_max` | 20 | 20 | 20 | 离地容差 |
| `object_placement_percent_off_ledge_max` | 0.1 | 0.1 | 0.1 | 悬空比例 |
| `object_placement_last_good_*` | 50 / 25° | 100 / 25° | 100 / 0° | 预览失败时沿用上一个合法点的容差 |
| `object_placement_ignore_players` | 1 | — | 1 | 玩家不挡 |
| `object_placement_run_mode` | — | — | onPrimaryAttack | 只在开火时算 |

脚本接口：`weapon.ObjectPlacementHasValidSpot()`、`GetObjectPlacementOrigin / Angles / Parent()`、回调 `OnObjectPlacementCanPlace_<weapon>`（电网 `mp_weapon_tesla_trap.nut:1401`）。电网另外自己写了一整套 trace（`TeslaTrap_GetPlacementInfo`，见电网记录 3.2.1），因为要算连线。

### 3.2 粘附落地（`vscripts/weapons/_weapon_utility.nut`）

- `PlantStickyEntity(ent, cp, angleOffset, ignoreHullTrace, moveOnNoHitTrace)`（`:1703`）：`EntityShouldStickEx` 过滤 → 姿态 = 法线方向 + 偏移 → 沿 −法线做 hull trace 贴到表面 → 设父实体（跟随移动物体）。
- `PlantStickyEntityThatBouncesOffWalls(projectile, cp, bounceDot)`（`:1661`）：`dot(法线, up) < bounceDot` → 不粘（弹开，返回 false）；有"首个合格弹跳点附近强制再弹"的保护（最多 8 次）。
- `Deployable_CountBouncesAndRefund`（`weapons/sh_deployable.gnut:94`）：弹太多次 → 删除并退还。
- `ThrowDeployable(weapon, params, power, landedFunc, …, angVel)`（`sh_deployable.gnut:16`）：投出一个部署体，落地回调。

### 3.3 贴地铺开（三种）

| 形状 | 每步 | 爬 / 下 | 失败处理 | 来源 |
|---|---|---|---|---|
| 尖刺网格 | 抬 40、走 47（长）/ 30（宽）、下 80 | 40 / 40 | 与中心断开的格子剪掉 | `mp_ability_spike_strip.nut:966-1080`、`:880-930` |
| 黑幕直线 | 抬 95（首根 80）、走 88、下 500 | 95（被挡再 +80.75）/ 500 | 挡住或找不到地 → 停 | `mp_weapon_ferro_wall.nut:886-1100` |
| 城墙蛇形 | 测 64、段长 27，按地面法线转姿态 | 32 / 80（> 100 转弯） | 侧边 65 内无空间 → 不出；3 s 超时 | `mp_ability_armored_leap.nut:5591-6330` |

APEX-REPORT 2.3 的铝热剂火墙是同一类（每 80 u 一点，下 225、台阶 46）；尖刺连 playlist 变量名都借用 `thermite_grenade_use_new_traces`。

### 3.4 数量上限

- `AddNewLimitedLegendObject(player, obj, max)`（`vscripts/_utility.gnut:163`）：按 scriptName 分表，插表头，超出删最旧。电网（12）、Conduit 地雷（14）用。
- `owner.e.activeTraps / activeUltimateTraps`：尖刺、拦截塔、黑幕自己维护同样的"插头删尾"。

## 4. 参数

见第 3 节表。

## 5. 未解决和要实测的

- 放置器字段的精确含义在引擎里，表中"含义"是按名字推断。测法：电网预览时往坡上 / 悬崖边 / 空中瞄，看预览变红的边界。

## 6. HSD 实现

- 放置器：HSD 有 `CombatSim.PlaceTurret`（`CombatSim.Items.cs:243`）的简单版本。建议抽出 `Placement.Find(eye, view, maxDist, maxSlopeDeg, dropMax)`：视线 trace → 向下找地 → 坡度检查，失败退回上一个合法点。
- 粘附：`ThrowParams.stick` 已有（电弧星）；加 `stickMinNormalZ`（尖刺 0.75、Conduit cos45°）。
- 贴地铺开：写一个 `GroundWalk.Step(from, dir, step, climb, drop)` 给尖刺 / 黑幕 / 城墙 / 铝热剂共用。
- 数量上限：`LimitedList<T>(max)`，插头删尾。
