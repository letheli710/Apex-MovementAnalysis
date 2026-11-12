# Rampart 战术 Amped Cover 加强掩体：系统记录

批次 C（combat-c），2026-10-31，静态研究（只读脚本，没进游戏）。

**和已有研究的关系**：规则摘要在 `TF2-Research/expansion/apex/APEX-REPORT.md` 第 2.9 节（放置、底座 + 加强盾、单向穿透 ×1.2），本文件**不重复**那部分，只补系统细节、全部参数和 **两处更正**（见第 4 节末"和 APEX-REPORT 2.9 的差别"）。

出处从 `research-src/s21-platform/scripts/` 开始。`nut` = `vscripts/weapons/mp_weapon_cover_wall.nut`，`txt` = `weapons/mp_weapon_cover_wall.txt`，`cb` = `vscripts/sh_codecallbacks.gnut`。

## 0. 概要

- **技能**：Rampart / 战术 / Amped Cover / `mp_weapon_cover_wall`。
- **一句话**：在面前放一块矮墙（底座），2 s 后墙上升起一层"加强盾"（175 血）。友方从盾后面往前打出去的子弹穿过盾、获得 `amped_damage` mod（伤害 ×1.2）；从前面打过来的被挡住、扣盾血。底座挡子弹、能被打坏（最终 400 血），近战两下打爆。最多 4 面，3 格充能各 20 s。
- **分类**：**好技能**（PvE 守点）＋ **系统**（"单向穿透 + 给穿过的子弹加 mod"的引擎机制；两层血量的放置物；可回收）＋ **可视化**（墙展开动画、盾上的血量刻度、子弹穿过时盾闪一下）。
- **可拆出的部件**：
  - 单向穿透 + 加 mod（`SetPassThroughDirection` + `PTF_ADDS_MODS` + 代码回调返回 mod 名）→ 3.2.2，公共部件 `_shared/C-BULLET-BLOCKING-SHIELD.md`
  - 两层放置物（底座 + 延迟升起的盾，盾是底座的子实体）→ 3.2.1
  - 受伤规则表（近战 = 半血、Prowler = 半血、电弧星 ×1.5、Crypto EMP = 一击满血、升级爆炸 ×0.5）→ 3.2.3，公共部件 `_shared/C-PLACEABLE-DEPLOYABLE.md`
  - 盾后近距离换弹加速（升级）→ 3.2.4
  - 回收规则（满血才能收）→ 3.2.5

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 说明 |
|---|---|---|
| 放置 | 引擎 object placement（`.txt` `object_placement_*`）+ 脚本二次限制 | `txt:32-47`、`nut:43-49` |
| 底座 | `prop_script`，重甲 `ARMOR_TYPE_HEAVY`，起始 120 血（`rampart_higher_health` 默认 true），盾升起时 + (400 − 120) | `nut:544-748`（`nut:569-583`）、`nut:990-1015` |
| 底座挡子弹 | `SetPassThroughThickness(rampart_wall_thickness = 1)` + `PTF_NO_DMG_ON_PASS_THROUGH`；升盾前改成 −1 | `nut:726-728`、`nut:924` |
| 加强盾 | `CreatePropScript(rampart_shield_cell, SOLID_VPHYSICS)`，`CONTENTS_WINDOW`，碰撞组 `BLOCK_WEAPONS_AND_PHYSICS`，挡爆炸、挡铝热剂、不能粘东西 | `nut:950-980` |
| 单向穿透 | `SetPassThroughDirection(-0.55)` + `SetPassThroughThickness(0)` + `PTF_ADDS_MODS | PTF_NO_DMG_ON_PASS_THROUGH` | `nut:979`、`nut:997-998` |
| 加 mod | 状态效果 `pass_through_amps_weapon` → 引擎穿透时调 `CodeCallback_CheckPassThroughAddsMods`，返回 `"amped_damage"`（能量 AR 返回 `"amped_damage_alt"`） | `nut:1000`、`cb:850-893` |
| ×1.2 | 武器 mod `amped_damage`：`damage_*_value` ×1.2，换曳光弹 | 例 `weapons/mp_weapon_mobile_hmg.txt:459-470`；APEX 2.9 引的 `mp_weapon_r97.txt:766-770` |
| 盾闪 | `AddCallback_OnPassThrough` → 盾特效控制点 2 = <1,0,0>，0.05 s | `nut:132`、`nut:1073-1101` |
| 血量刻度 | 子模型 `rampart_health_ticks`，身体组 high / low（半血分界） | `nut:1002-1012`、`nut:1466-1501` |
| 展开动画 | 底座动画 `folded_idle → unfold → charging_idle + extend_arms → extend_armor → ref` | `nut:663`、`nut:869-930` |
| EMP | `AddEMPDamageDevice`、`AddWreckingBallEMPDamageDevice`（盾） | `nut:991-992` |
| 小地图 | `RegisterMinimapPackage(... RAMPART_WALL ...)` | `nut:139` |
| 盾后换弹快（升级） | 每帧检查 100 u 内、在盾**正面一侧**（dot ≥ 0），给主武器加 `auto_loader` mod（和 Ballistic 大招同一个 mod），屏幕特效 `P_clbr_ulti_screen` | `nut:192-292`、`nut:27` |

**怀疑点（SDK 改动，明确）**：
- `nut:555`："// HoverVehicle_SetAbilityAttachmentEntity is S21-only; not on S3 dedi."——放在载具上的分支被改过。
- `cb:860-861`："// Without a passing entity there is nothing to inspect, so the amped wall break and the energy weapon variant below cannot run here."——穿透回调是 SDK 补过的。

## 2. 流程

```
条件：弹量 ≥ 20（3 格，每格 20 s，ammo_timed）
拿出（deploy 1.0 s）→ 预览模型 → 开火：放置点有效才放，否则空响
CoverWall_Deploy：
  底座 120 血（重甲），能挡子弹；超过 4 面删最早的
  wait 0.3 s（旧 0.5）→ 展开动画
DeployAmpedWallAfterDelay（总 2.0 s，旧 3.0）：
  0.1 s（旧 0.25）后伸出手臂；再等 (2.0 − 0.1 − 0.3)；伸出护甲 0.3 s
  底座穿透厚度 −1；底座还活着 → DeployAmpedWall
DeployAmpedWall：
  在底座上方 39 u 生成盾（面朝 Rampart，转 180°），175 血（升级 ×1.25）
  底座最大血 400（升级 ×1.25），当前血 += 400 − 120
  震动 rumble
盾被打掉：底座手臂收起（身体组），底座还在
回收：长按使用 0.5 s，64 u 内；满血才能收（升级：受损也能收）
```

- 时间都受 playlist 控制：`rampart_wall_build_time`、`rampart_improved_deployment`（默认 true）、`rampart_higher_health`（默认 true）（`nut:873-876`、`nut:885`）。注释说动画按 3 s 做的，改时间要改动画 FPS（`nut:76`）。

## 3. 代码

### 3.1 入口

- `MpWeaponCoverWall_Init`（`nut:130-168`）：注册回收的服务端函数；服务端穿透回调；客户端 `+scriptCommand5`、使用焦点回调、小地图；升级被动 `PAS_PAS_UPGRADE_TWO` 的回调；读盾血。
- 武器回调：PrimaryAttack / Activate / Deactivate / AttemptOffhandSwitch / OnCreateClientOnlyModel（`nut:1-9`）。

### 3.2 核心逻辑

#### 3.2.1 两层放置物

- 盾是底座的子实体（`SetParent(baseWall)`），底座 `LinkToEnt(ampedWall)`，所以底座在移动物体上时盾跟着走（`nut:983-984`）。
- 底座的血量"先低后高"：放下时 120（容易被打掉），升盾瞬间补到 400。**升盾前打底座更划算**。

#### 3.2.2 单向穿透 + 加 mod

```
盾：PassThroughDirection = -0.55，Thickness = 0，Flags = ADDS_MODS | NO_DMG_ON_PASS_THROUGH
引擎：子弹碰到盾 → 判断入射方向与盾法线的点积是否满足 -0.55 阈值（推断：从盾背面出去才放行）
      放行时调 CodeCallback_CheckPassThroughAddsMods(player, hitEnt, passingEnt, …)
回调（cb:850-893）：
   跑所有 OnPassThrough 回调（盾闪特效）
   hitEnt 有 pass_through_amps_weapon：
       子弹已带 amped_damage 又穿过一面加强盾 → 那面盾受"满血"伤害（直接打碎）
       能量 AR → 返回 amped_damage_alt；否则 → amped_damage
引擎给这颗子弹加 mod → 伤害 ×1.2
```

- "双重加强会打碎第二面盾"（`cb:865-878`）：同一颗子弹穿过两面盾，第二面直接碎。推断是防止叠加。
- 爆炸：盾 `SetBlocksRadiusDamage(true)`，底座设置见 `nut:569` 附近。

#### 3.2.3 受伤规则

| 目标 | 规则 | 来源 |
|---|---|---|
| 底座，近战 | 伤害 = 最大血 / 2（两下打爆） | `nut:1241-1245` |
| 底座，Prowler 爆炸 / Shadow 手 | = 最大血 / 2 | `nut:1225-1236` |
| 底座，爆炸 + 升级一 | ×0.5（`upgrade_core_explosive_damage_multiplier`） | `nut:1237-1238`、`nut:186-189` |
| 盾，电弧星 | ×1.5 | `nut:1373-1377` |
| 盾，Crypto EMP 陷阱 | 一下打满（damageScale = 最大血 / 伤害） | `nut:1379-1380` |
| 盾，近战 | 转给底座 | `nut:1410-1414` |
| 盾 | 无友伤保护（`noFriendlyFireProtection`） | `nut:964` |

#### 3.2.4 盾后换弹加速（升级 `PAS_PAS_UPGRADE_TWO`，`nut:192-292`）

```
每帧：有 Ballistic 大招 buff → 跳过（同一个 mod）
  任何加强盾：|player - wall| ≤ 100 且 dot(wall.forward, player - wall) ≥ 0 → 加 auto_loader（换弹 ×0.6）
  否则移除所有主武器的 auto_loader
```

注意它遍历的是**所有**加强盾（`file.ampedWallEntToShieldFX`，不分主人和队伍）。推断是 bug 或有意（敌人的盾也行），第 5 节。

#### 3.2.5 回收 `CanReclaimWall`（`nut:390-428`）

升级 `PAS_PAS_UPGRADE_ONE`（`upgrade_tactical_damaged_retrieval`）→ 总能收；否则：盾还没升起时底座最大血必须还是 120（推断：防止升盾中途收）；底座、盾都必须满血。

### 3.3 客户端表现

- 预览模型 `rampart_cover_wall_replacement.rmdl`（`txt:32`）。
- 盾特效 `P_rampart_shield_top`，被打时 `PlayIncomingDamageFX_Thread`，子弹穿出时闪 0.05 s。
- 底座受损：半血切换特效 `P_rampart_wall_damaged` + 持续 `_damaged_idle`，低血被打 `_damaged_hit`；毁坏 `P_rampart_wall_destroy`；盾碎 `P_rampart_amp_destroy`；收起 `P_rampart_amp_end`（`nut:80-89`）。
- 伤害数字下移（`CoverWall_OffsetDamageNumbersLower`，`nut:497`）。

### 3.4 依赖的公共代码

- 引擎穿透：`SetPassThroughDirection/Thickness/Flags`、`CodeCallback_CheckPassThroughAddsMods`（`cb:845` 起，客户端版本 `cb:897` 起）、`AddCallback_OnPassThrough`。
- 状态效果 `pass_through_amps_weapon`；`_weapon_utility.nut:8125` 的某个投射物轨迹函数也检查它（`CheckPassThroughDir`）。
- 其他读 `amped_damage` 的地方：`ai/_ai_dummie.gnut:967`、`gamemodes/_gamemode_survival.nut:6135`（推断：统计 / 伤害数字颜色）。
- 和 Sheila 的关系：Sheila 有 `amped_damage` mod；`TIME_BEFORE_SWITCHING_FROM_MOBILE_HMG = 0.6`（`nut:41`）。

## 4. 参数

| 参数 | 值 | 单位 | 来源 | 作用 | 改大 / 改小会怎样 |
|---|---|---|---|---|---|
| COVER_WALL_MAX_WALLS（`rampart_max_walls_deployed`） | 4 | 面 | `nut:33`、`nut:643` | — | — |
| 禁止重生半径 | 256 | u | `nut:35` | — | — |
| 底座最大血 | 400（升级 ×1.25 = 500） | HP | `nut:37`、`nut:941-947` | — | — |
| 底座起始血 | 120（`rampart_higher_health`）/ 旧 45 | HP | `nut:38`、`nut:59`、`nut:569-578` | 升盾前 | — |
| 盾血（`rampart_amped_shield_health`） | 175（升级 ×1.25 = 218.75） | HP | `nut:171-174`、`nut:932-938` | — | — |
| 盾高度偏移 | 39 | u | `nut:40` | — | — |
| 放置距离（脚本） | 64–256 | u | `nut:43-44` | — | — |
| object_placement_distance_max | 128 | u | `txt:33` | 引擎放置距离 | 第 5 节 |
| 放置坡度 / 高度差 / 占地 | 法线 z 0.7 / 64 / 60×60×80 | — | `nut:46-49` | — | — |
| object_placement_hill_angle_max | 45 | 度 | `txt:34` | — | — |
| 放置后展开延迟 | 0.3（旧 0.5） | s | `nut:54`、`nut:58`、`nut:736-740` | — | — |
| 手臂开始 | 0.1（旧 0.25） | s | `nut:51`、`nut:56` | — | — |
| 护甲展开 | 0.3（旧 0.5） | s | `nut:52`、`nut:57` | — | — |
| 升盾总时间（`rampart_wall_build_time`） | **2.0**（`rampart_improved_deployment` 默认 true）/ 旧 3.0 | s | `nut:72-74`、`nut:873-876` | — | — |
| 穿透方向阈值 | −0.55 | dot | `nut:998` | 推断约 57° 内出射放行 | — |
| rampart_wall_thickness（底座） | 1 | — | `nut:726` | — | — |
| 回收距离 / 时间 | 64 / 0.5 | u / s | `nut:61-62` | — | — |
| 充能 | 弹匣 60、每次 20、回充 1/s → 3 格 × 20 s（`ammo_timed`） | — | `txt:95-108` | — | — |
| 冷却升级 | 弹匣 45、每次 15 → 3 格 × 15 s | — | `txt:184-191` | — | — |
| deploy_time / fire_rate | 1.0 / 10 | s / — | `txt:77-82` | — | — |
| 盾后换弹距离（升级） | 100 | u | `nut:211` | — | — |
| 电弧星对盾 | ×1.5 | × | `nut:1376` | — | — |
| 升级爆炸抗性 | ×0.5 | × | `nut:186-189` | — | — |
| amped_damage | ×1.2 | × | 武器 `.txt` Mods | 加强伤害 | — |
| 盾闪 | 0.05 | s | `nut:86` | — | — |

**和 APEX-REPORT 2.9 的差别（更正）**：

1. **升起延迟**：2.9 写"3 s（升级 2 s）"。实际：默认 playlist `rampart_improved_deployment = true`，**默认就是 2 s**，3 s 是关掉这个开关的旧值，和天赋升级无关（`nut:873-876`）。
2. **底座起始血**：2.9 写"起始 45"。实际默认 `rampart_higher_health = true` → **起始 120**，45 是旧值（`nut:569-578`）。
3. 2.9 的 HSD 实现（`Tacticals.cs` `AWall.RampartRise = 3`）因此和 R5 默认差 1 s，见第 6 节。

## 5. 未解决和要实测的

1. **放置距离**：脚本常量 64–256 u，`.txt` 引擎放置 `distance_max 128`。实际用哪个（推断引擎 128 决定预览，脚本常量只是旧代码未用）。**测**：训练场看最远能放多远。
2. **两个 playlist 开关在本地是否 true**：`rampart_improved_deployment`、`rampart_higher_health` 默认 true，`playlists_r5_patch.txt` 没有覆盖（APEX-REPORT 第 0 节说的）。**测**：放墙计时到盾出现。
3. **穿透角度**：−0.55 的具体含义（出射方向与盾法线夹角 ≤ 约 57°？）。**测**：在盾后面不同角度射击，看是否穿过、伤害是否 ×1.2。
4. **盾后换弹不分队伍**（3.2.4）。PvE 不重要。
5. 穿透回调被 SDK 改过（`cb:860`），"双重加强打碎第二面盾"在本地是否生效。

## 6. HSD 实现

**已有部分**：`HSD-Unity/Assets/HSD/Game/Runtime/Combat/Tacticals.cs` 的 `AWall`（TF2 A 型墙），带 Rampart 选项（`rampart = true`）：

- 有：单向（`PassCos = 0.55`，`PassAmp` 只看水平点积）、加成 ×1.2（`RampartAmp`）、盾 175 血（`RampartHp`）、3 s 后才生效（`RampartRise = 3`）、挡爆炸（`BlocksExplosions`）、实现了 `IWallBlocker`。
- 没有 / 不同：
  - **放置方式**：HSD 用 TF2 的"扔出去落地"（`ThrowParams` 500 u/s），R5 是面前直接放（64–256 或 128 u）。
  - **升起时间**：HSD 3 s，R5 默认 2 s（第 4 节更正）。
  - **底座**：HSD Rampart 选项只有一层（盾），没有 400 血底座；盾没升起前什么都不挡（`Standing` 要求 `now − deployedAt ≥ RampartRise`）。R5 底座一放下就挡子弹。
  - 平板 165 × 90（TF2 尺寸），R5 约 60 宽 × 80 高的底座 + 上方 39 u 的盾（README"A 型墙做成平板"）。
  - 数量（R5 4 面、3 格充能 20 s）、近战两下打爆、电弧星 ×1.5、回收：都没做。

建议：

1. 把 `AWall` 的 Rampart 选项拆成独立类 `AmpedCover`（`Tacticals.cs`），按 R5 放置（面前，距离先用 128，第 5 节测完再定）。
2. 两层：底座 120 → 升盾时 400，一放下就挡；盾 175，2 s 后出现。`RampartRise` 改成 2，并把 3 留成开关 `ampedCover.legacyRise`（R5 旧值），差别写进 `R5-DIFF-ARCHIVE.md`。
3. 单向判断沿用 `PassCos 0.55`；R5 是三维点积（推断），HSD 现在只算水平，差在"从高处往下打"时。记进差异档案。
4. AI 规则：近战 AI 两下打爆底座（R5 规则），对 PvE 守点有意义。

开关建议：PlayerPrefs `hsd.combat.rampart.cover.*`（`rise`、`baseHp`、`maxWalls`、`placeMode`）。
