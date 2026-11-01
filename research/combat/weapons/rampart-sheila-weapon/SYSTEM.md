# Rampart Sheila 的枪械调参：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。只写枪本身：扩散收紧、转速门槛、和地面枪比伤害、手持和炮台的差别。流程、形态切换、放置、炮台实体看 [`../../rampart-sheila/SYSTEM.md`](../../rampart-sheila/SYSTEM.md)，这里不重复。

出处从 `research-src/s21-platform/scripts/` 开始。`hmg` = `vscripts/weapons/mp_weapon_mobile_hmg.nut`，`hmgt` = `weapons/mp_weapon_mobile_hmg.txt`，`mt` = `vscripts/weapons/mp_weapon_mounted_turret_weapon.nut`，`mtt` = `weapons/mp_weapon_mounted_turret_weapon.txt`，`bolt` = `vscripts/weapons/mp_weapon_basic_bolt.nut`，`lmgt` = `weapons/mp_weapon_lmg.txt`，`r97t` = `weapons/mp_weapon_r97.txt`。

逐字段全表：[`PARAMS.md`](PARAMS.md)。

## 0. 概要

- **武器**：Rampart 大招槽 / `mp_weapon_mobile_hmg`（手持）+ `mp_weapon_mounted_turret_weapon`（坐炮台）。
- **一句话**：转满才开火、越打越准的高射速重机枪。没有射速爬升；"转速"就是开镜进度。
- **分类**：
  - 效果：持续压制，280 DPS，比地面的 Spitfire、R-99 高（见第 4 节）。
  - 可视化：转动音效按开镜进度 seek、激光（详见 Sheila 主记录）。
  - 可复用系统：开镜门槛当转速；负的 spread kick。
- **可拆出的部件**：
  - 开镜进度门槛 → 3.2.1
  - 负 kick 收紧扩散 → 3.2.2
  - 脚本返回值决定扣弹，和 `ammo_per_shot` 解耦 → 3.2.3
  - 手持 / 固定炮台两份调参 → 3.2.4

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 转速门槛 | 脚本判断 `IsWeaponInAds() && GetZoomFrac() >= 1.0`，否则返回 0 不开火 | `hmg:260`、`hmg:296-299` |
| 转速时间 | `zoom_time_in 1.25`，不是射速字段 | `hmgt:171` |
| 子弹 | `OnWeaponPrimaryAttack_weapon_basic_bolt` → `FireBallisticRoundWithDrop` | `hmg:294`、`bolt:74` |
| 扣弹 | `FireWeaponPlayerAndNPC` 固定 `return 1`，每发扣 1 | `bolt:76` |
| 扩散收紧 | ADS 的 `spread_kick_on_fire_*` 是负数 | `hmgt:227-229` |

**S3 / S21 差异**（字符串证据，不是行为证据，见 [`../_shared/W-S3-FIELD-CHECK.md`](../_shared/W-S3-FIELD-CHECK.md)）：

字段核对只搜了 exe；SDK 的 `server.dll` 另有实现（源码 `research-src/s21-r5sdk/src/game/`），所以"exe 里没有"不等于"dedi 上不工作"。下面引用 SDK 源码的地方是读过的；行为都待实测。

- **`spread_min_kick` 待实测**。`r5apex_ds.exe` 里没有这个字符串，但 SDK 读它：`research-src/s21-r5sdk/src/game/server/weapon_kv_s21_ext.cpp:175`。读到的值 grep 下来只有一处使用：`research-src/s21-r5sdk/src/game/server/bridge_zoom_gate.cpp:756-765` 的 `[SPREAD-GATE]` 警告，条件是 `flSpreadMinKick >= 0`，文字写 "dedi cannot reproduce this S21 term"。Sheila 是 −2.5，不进这个条件。我在 SDK 里没找到把这个值用到扩散计算的代码。所以主记录"收到约 0.5°"还不能算数，第 5 节第 1 条。
- `allow_zoom_on_raise`：exe 只有客户端有；SDK 把名字映射到别的槽（`research-src/s21-r5sdk/src/game/shared/weapon_script_vars.cpp:3173`）。行为待实测。
- `hmgt:50`、`mtt:48`：`OnWeaponZoomFOVToggle` 的回调注释写 "Disabled on dedi"。只影响倍镜切换音效。

## 2. 流程

枪的开火部分（完整流程看主记录第 2 节）：

```
按住开镜 → zoomFrac 从 0 到 1（1.25 s，升级后 1.0 s）
zoomFrac < 1：按开火 → 脚本返回 0，不出弹不扣弹（推断：也不进后坐）
zoomFrac = 1：每 1/20 s 一发，扣 1，扩散 −0.18°/发
停火 0.1 s 后扩散以 spread_decay_rate 回到基础值
松镜：zoomFrac 回落（1.0 s），门槛立刻不满足
```

打空要 173 发 / 20 发每秒 = 8.65 s（推断：`hmgt:112` ÷ `hmgt:170`，不算转速）。

## 3. 代码

### 3.1 入口

`OnWeaponPrimaryAttack_weapon_mobile_hmg`（`hmg:252-300`），`hmgt:47` 绑定。炮台是 `OnWeaponPrimaryAttack_weapon_mounted_turret_weapon`（`mt:240`，门槛 `mt:248`，`mtt:45` 绑定）。

### 3.2 核心逻辑

#### 3.2.1 开镜进度门槛

```
if IsWeaponInAds and owner.GetZoomFrac() >= 1.0: 开火
else: return 0
```

好处：不需要新状态。开镜时间就是转速时间，松镜就是减速，HUD 和音效都可以直接读 zoomFrac（`hmg:198-250`）。代价：腰射永远不开火，`hmgt:216-220` 那些腰射扩散字段没有作用（推断）。

#### 3.2.2 负 kick 收紧扩散

数据（站立 ADS）：基础 `spread_stand_ads 3`，每发 `spread_kick_on_fire_stand_ads −0.18`，`spread_max_kick_stand_ads 0`，`spread_min_kick −2.5`，停火 `spread_decay_delay 0.1` 后按 `spread_decay_rate 12` 回弹。

公式（**推断**，脚本里没有，是引擎行为）：

```
kick = clamp(kick + kickOnFire, minKick, maxKick)    // 每发
spread = max(0, base + kick)
```

两种可能的结果：

| 假设 | 收紧到 | 要几发 | 时间（20 发/s） |
|---|---|---|---|
| 有下限 −2.5（S21 客户端数据） | 0.5° | 13.9 | 0.69 s |
| 没有下限（SDK 读了值但没应用，见第 1 节）且总扩散不小于 0 | 0° | 16.7 | 0.83 s |

如果客户端和 dedi 算的不一样，准星显示和弹道可能对不上（推断）。

空中 ADS 基础 5.5°、每发只 −0.08°（`hmgt:223`、`hmgt:229`）。空中开火基本收不紧。

#### 3.2.3 扣弹和 `ammo_per_shot` 解耦

`hmgt:115` 写 `ammo_per_shot 43`，`hmgt:114` 写 `ammo_min_to_fire 43`，`hmgt:494` 的 mod `mobile_hmg_active` 只把 `ammo_min_to_fire` 改成 1、回充改 0，没改 `ammo_per_shot`。真正扣多少由脚本决定：`bolt:76` 返回 1。所以这把枪是 173 发，不是 4 发（推断：引擎用回调返回值扣弹；和 Vantage 枪 `return ammoUsed` 的写法一致，见 `../vantage-sniper-weapon/SYSTEM.md`）。第 5 节第 2 条。

#### 3.2.4 手持和炮台

炮台枪是另一份 `.txt`，手感不完全一样。差别：

| 字段 | 手持 `hmgt` | 炮台 `mtt` | 意义 |
|---|---|---|---|
| `spread_decay_rate` | 12（`hmgt:396`） | 3（`mtt:226`） | 炮台停火后扩散回弹慢 4 倍，点射更占便宜 |
| `spread_air_hip` | 5.5（`hmgt:220`） | 11（`mtt:153`） | 腰射本来不开火，无实际作用（推断） |
| `spread_air_ads` | 5.5（`hmgt:223`） | 6（`mtt:212`） | 炮台不会在空中（推断），无实际作用 |
| `spread_kick_on_fire_air_ads` | −0.08（`hmgt:229`） | 0（`mtt:218`） | 同上 |
| `viewkick_pitch_base` | 2.0（`hmgt:281`） | 1.0（`mtt:236`） | 炮台俯仰后坐基准低一半 |
| `viewkick_pitch_softScale` | 0.25（`hmgt:283`） | 0.275（`mtt:238`） | 接近 |
| `ammo_clip_size` | 173（`hmgt:112`） | 150（`mtt:109`） | 手持的弹量就是大招充能 |
| `ammo_stockpile_max` | 173（`hmgt:129`） | 300（`mtt:117`） | 炮台有备弹 |
| `reload_enabled` | 0（`hmgt:196`） | 1（`mtt:186`） | 只有炮台能换弹，8.667 s（`mtt:172`） |
| `deploy_time` | 1.6（`hmgt:178`） | 1.2（`mtt:168`） | 炮台上枪快 |
| `raise_time` | 1.6（`hmgt:180`） | 0.75（`mtt:170`） | 同上 |

相同：`fire_rate 20`、14 伤害、爆头 ×2、`zoom_time_in 1.25`、基础扩散 3°、每发 −0.18°、`spread_min_kick −2.5`、弹速 25000（`hmgt:133`、`mtt:123`、`hmgt:227`、`mtt:216`、`hmgt:65`、`mtt:61`）。

### 3.3 客户端表现

转动音效 seek、激光：看主记录第 3.3 节。

### 3.4 依赖的公共代码

- 弹道：`../_shared/W-BALLISTICS.md`；扩散后坐：`../_shared/W-SPREAD-RECOIL.md`；开火换弹：`../_shared/W-FIRE-RELOAD.md`；伤害：`../_shared/W-DAMAGE.md`；mod：`../_shared/W-MOD-SYSTEM.md`。
- `amped_damage` mod（×1.2，`hmgt:460`）：`../../_shared/C-DAMAGE-MODIFIERS.md`。

## 4. 参数

和地面枪比（全部是 `.txt` 值）。DPS = 伤害 × 射速，不算换弹、不算爆头，公式是推断。

| 字段 | Sheila 手持 | Spitfire `mp_weapon_lmg` | R-99 `mp_weapon_r97` |
|---|---|---|---|
| `damage_near_value` | 14（`hmgt:133`） | 21（`lmgt:100`） | 12（`r97t:57`） |
| `fire_rate` | 20（`hmgt:170`） | 9（`lmgt:134`） | 18（`r97t:86`） |
| DPS（推断） | 280 | 189 | 216 |
| `damage_headshot_scale` | 2.0（`hmgt:143`） | 1.25（`lmgt:91`） | 1.25（`r97t:174`） |
| `ammo_clip_size` | 173（`hmgt:112`） | 35（`lmgt:93`） | 18（`r97t:49`） |
| 一匣总伤（推断） | 2422 | 735 | 216 |
| `damage_far_distance` | 2500，且不衰减（`hmgt:141`、`hmgt:134`） | 2500，不衰减（`lmgt:108`、`lmgt:101`） | 1500，不衰减（`r97t:180`、`r97t:58`） |
| `projectile_launch_speed` | 25000（`hmgt:65`） | 27500（`lmgt:49`） | 19000（`r97t:25`） |
| `zoom_time_in` | 1.25（`hmgt:171`） | 0.34（`lmgt:135`） | 0.22（`r97t:192`） |
| `ads_move_speed_scale` | 0.4（`hmgt:204`） | 0.4（`lmgt:151`） | 0.75（`r97t:195`） |
| `spread_stand_ads` | 3（`hmgt:221`） | 0（`lmgt:320`） | 0.35（`r97t:228`） |
| `spread_kick_on_fire_stand_ads` | −0.18（`hmgt:227`） | 0（`lmgt:323`） | 0（`r97t:241`） |
| `spread_decay_delay` | 0.1（`hmgt:237`） | 0.3（`lmgt:330`） | 0.15（`r97t:233`） |
| `spread_decay_rate` | 12（`hmgt:396`） | 12（`lmgt:329`） | 12（`r97t:234`） |
| `viewkick_pattern` | rampart_turret（`hmgt:240`） | lmg_2（`lmgt:161`） | r97_2（`r97t:92`） |

读法：Sheila 的开镜移动速度和 Spitfire 一样慢。它用 1.25 s 转速和开头 3° 的大扩散，换 DPS 和弹量。地面枪的 ADS 扩散一开始就接近 0，Sheila 要打 0.7–0.8 s 才收紧到同一量级。

调参影响：

| 参数 | 改大 / 改小 |
|---|---|
| `zoom_time_in` | 小了反应快，失去"转速"代价 |
| `spread_stand_ads` | 大了头一段更散；和 kick 一起决定收紧时间 |
| `spread_kick_on_fire_stand_ads` | 更负收紧更快 |
| `spread_min_kick` | 决定最准的程度；dedi 上是否生效待实测，见第 5 节 |
| `spread_decay_rate` | 小了点射保持精度（炮台是 3） |
| `ads_move_speed_scale` | 大了开火时能走位，升级版是 0.6（`hmgt:521` 起的 mod） |

## 5. 未解决和要实测的

1. **`spread_min_kick` 在 dedi 上有没有作用**。为什么不确定：SDK 读了字段（`research-src/s21-r5sdk/src/game/server/weapon_kv_s21_ext.cpp:175`），但没找到应用它的代码（第 1 节）；开火扩散公式本身也是推断。测：火力训练场用 Sheila 开镜对墙连射 3 s，分别截第 0.3、0.7、1.0、3 s 弹孔分布；能读的话每帧记 spread。看最终扩散是 0.5° 还是 0°，准星和弹孔是否一致。
2. **实际弹量**。`ammo_per_shot 43` 和脚本 `return 1` 矛盾（`hmgt:115`、`bolt:76`）。测：记一匣打多少发、打多久，预期 173 发、8.65 s。
3. **激活门槛**。`ammo_min_to_fire 43`，主记录已列，这里不重复。
4. **`allow_zoom_on_raise`**（SDK 只做了名字映射）：拿出武器时一直按着开镜，客户端和 dedi 的开镜状态会不会不同步（门槛由 `GetZoomFrac` 决定）。测：按住开镜拿枪，看多久能开火。
5. **炮台 `spread_decay_rate 3` 的实际手感**：点射 5 发停 0.3 s 再打，炮台和手持对比散布。

## 6. HSD 实现

**未实现**。grep `HSD-Unity/Assets/HSD/Game/Runtime/Combat/` 和分支 `origin/claude/w2-framework-b44e35`：两边的 `.cs` 里都没有 spread 相关字段；`Weapon.Shoot` 沿视线打直线（`Weapons.cs`）。`WeaponKind` 只有 Rifle、SmartPistol、Inferno。

建议做法（只是枪的部分，放置和形态切换看主记录第 6 节）：

1. 在 `Combat/Weapons.cs` 加 `Minigun : Weapon`，`Step` 里读开镜进度，`zoomFrac < 1` 直接 return。
2. 扩散状态放进 `Weapon` 基类或 `SpreadState`（公共，`../_shared/W-SPREAD-RECOIL.md`）：`kick` 每发累加，夹在 `[minKick, maxKick]`，`delay` 后按 `decayRate` 回零。
3. **下限开关**：字段 `sheila.spreadMinKick`，默认 −2.5（S21 数据）。第 5 节第 1 条测完再定，差别进 `R5-DIFF-ARCHIVE.md`。
4. 手持 / 炮台两份参数，炮台 `decayRate = 3`。

开关建议：PlayerPrefs `hsd.combat.rampart.sheila.spinup`、`spreadKick`、`spreadMinKick`。
