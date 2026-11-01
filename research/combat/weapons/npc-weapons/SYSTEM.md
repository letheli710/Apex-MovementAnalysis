# NPC 武器：敌人开枪的节奏和准度：系统记录

武器阶段 W1，2026-11-01，静态研究（只读脚本，没进游戏）。这是 PvE 里敌人用来打玩家的数值。

出处从 `research-src/s21-platform/scripts/` 开始。`he` = `weapons/npc_weapon_hemlok.txt`，`ls` = `weapons/npc_weapon_lstar.txt`，`sg` = `weapons/npc_weapon_shotgun.txt`，`es` = `weapons/npc_weapon_energy_shotgun.txt`，`bb` = `weapons/npc_weapon_boss_beam.txt`，`br` = `weapons/npc_weapon_boss_turret_rockets.txt`，`ss` = `weapons/npc_weapon_super_spectre.txt`，`r1` = `weapons/mp_weapon_rspn101.txt`，`r9` = `weapons/mp_weapon_r97.txt`，`lm` = `weapons/mp_weapon_lmg.txt`，`kr` = `weapons/mp_weapon_sniper.txt`，`sh` = `weapons/mp_weapon_shotgun.txt`，`ha` = `weapons/mp_weapon_energy_ar.txt`，`dm` = `vscripts/ai/_ai_dummie.gnut`，`cs` = `vscripts/sh_consts.gnut`。

逐字段全表：[`PARAMS.md`](PARAMS.md)。

## 0. 概要

- **武器**：12 个 `npc_weapon_*.txt`，加所有玩家枪里的 `npc_*`、`proficiency_*` 字段。
- **一句话**：NPC 开枪不按住扳机，而是"连发 N 发 → 休息 T 秒"循环。每把枪写好连发发数、休息时间、NPC 专用伤害、交战距离、每个熟练度的扩散倍数。伤害通常比玩家低（R-301 玩家 15，NPC 10），节奏让 DPS 更低。
- **本地跑不了**：`npc_dummie`、`npc_prowler` 能生成和追人，**但不开枪也不近战**；`npc_spectre` 会让 dedi 挂死。所以这份记录的开火节奏**全部是字段值，没有实测**，也没办法在本地实测（第 5 节）。
- **分类**：
  - 效果：敌人火力手感。
  - 可视化：无（NPC 武器走枪的表现）。
  - 可复用系统：连发 / 休息节奏、熟练度扩散、交战距离。这是 HSD 敌人开枪的直接模板。
- **可拆出的部件**：
  - 连发 / 休息节奏 → 3.2.1
  - 精度插值（`_min_precision` / `_max_precision`）→ 3.2.2
  - 熟练度扩散 → 3.2.3
  - 开火前预警（`npc_pre_fire_delay`）→ 3.2.4
  - 交战距离 → 3.2.5
  - 打偏策略（`npc_burst_radius_*`、`npc_lead_*`）→ 3.2.2

## 1. 它用什么实现各种效果

| 效果 | 实现手段 | 来源 |
|---|---|---|
| 连发 / 休息 | 字段 `npc_min_burst`、`npc_max_burst`、`npc_rest_time_between_bursts_min/max`，引擎 AI 读 | `r1:83-86` |
| 新版节奏 | 同样字段的 `_min_precision`、`_max_precision` 版本 | `he:133-138` |
| NPC 伤害 | `npc_damage_near_value` 等，和玩家字段分开 | `r1:74-75` |
| 扩散 | `npc_spread_cone_*`；每个熟练度一个倍数 `proficiency_*_spreadscale` | `he:126-127`、`r1:69-73` |
| 开火回调 | 单独的 `OnWeaponNpcPrimaryAttack` | `he:28` |
| 预警 | `npc_pre_fire_delay` + `OnWeaponNpcPreAttack` | `bb:189`、`bb:24` |
| 谁拿什么枪 | `aisettings/*.txt` 的 `DefaultWeapon` | `aisettings/npc_dummie_combat.txt:25`、`aisettings/npc_spectre.txt:38` |

**S3 / S21 差异**：

- `npc_*`、`proficiency_*` 不在 [`../_shared/W-S3-FIELD-CHECK.md`](../_shared/W-S3-FIELD-CHECK.md) 的"只有客户端"和"只有 dedi"表里（那份文件在重新生成），推断 exe 认。SDK 源码里 grep `npc_min_burst`、`proficiency_` 没有结果，所以走的是原生引擎。字符串证据，不是行为证据。
- `ap_*`（AI 玩家字段，如 `ap_min_burst`、`ap_aim_accuracy_easy`，`r1:382-397`）在两个二进制里都没有（`W-S3-FIELD-CHECK`，推断是更新版本的 AI 玩家字段）。**HSD 不要以它们为准**；只能当"Respawn 给 AI 玩家写的目标值"做参考。
- 回调缺失：`OnWeaponNpcPreAttack_BossBeam`、`_SuperSpectre`、`_boss_turret_rockets`、`OnWeaponNpcPrimaryAttack_SuperSpectre`、`_boss_turret_rockets`、`_weapon_plasma_cannon` 都是 `vscripts/weapons/_missing_callback_stubs.gnut` 的空壳。**这些 boss 武器本地开不了火**。
- `npc_spectre` 挂死 dedi：脚本 `vscripts/npc/npc_precache_spectre.nut:6-9` 预载 `npc_weapon_hemlok`、`npc_weapon_thermite_grenade`、`npc_weapon_lstar`。原因没查（运行事实，不是脚本能读出来的）。

## 2. 流程

```
AI 决定交战（距离在 npc_min_engage_range–npc_max_engage_range）
  ↓（boss 类：npc_pre_fire_delay，OnWeaponNpcPreAttack）
一轮连发：N = random( npc_min_burst, npc_max_burst ) 发，间隔 1 / fire_rate
  每发方向 = 瞄准 + 扩散（基础 × proficiency_*_spreadscale）
  回调 OnWeaponNpcPrimaryAttack → 出弹
休息：T = random( npc_rest_min, npc_rest_max ) + proficiency_*_additional_rest
重复；超过 npc_max_range 不开火（推断）
```

全部是推断。引擎侧看不到代码，字段语义从名字和注释来。NPC 不扣备弹、不换弹之类的细节也要测。

## 3. 代码

### 3.1 入口

- 引擎 AI 读字段，调用 `OnWeaponNpcPrimaryAttack`（例 `OnWeaponNpcPrimaryAttack_weapon_basic_bolt`，`vscripts/weapons/mp_weapon_basic_bolt.nut:54`）。和玩家开火走同一函数，`playerFired = false`（`:58`）。
- 假人的枪：`dm:109-111`：`WEAPON_NPC_COMBATDUMMIE_RIFLE = npc_weapon_hemlok`、`_SHOTGUN = npc_weapon_energy_shotgun`、`_ENERGY = npc_weapon_lstar`。

### 3.2 核心逻辑

#### 3.2.1 连发 / 休息节奏

**节奏决定 DPS**。公式（推断，假设全命中、`fire_rate` 适用于 NPC）：

```
一轮时长 = 平均连发 / fire_rate + 平均休息
DPS = 平均连发 × npc_damage_near_value / 一轮时长
```

结果在第 4 节的表。要点：

- 自动枪：连发短（R-301 2–4 发，R-99 4–7 发），休息 0.5–0.8 s。玩家能明显感到"一阵一阵"。
- 狙：1 发，休息 5 s（`kr:123-127`）。Kraber 和 Sentinel 字段几乎一样。这是"给你躲的时间"。
- **Spitfire 特殊**：`npc_damage_near_value 2`（`lm:111`），15–20 发连发，休息 5–6 s（`lm:123-126`）。伤害只有 2，DPS ≈ 4.7。Sheila `mp_weapon_mobile_hmg.txt:146-161` 完全一样，推断 Sheila 的 NPC 字段抄自 Spitfire，也可能都是占位。

#### 3.2.2 精度插值（`npc_weapon_*` 新写法）

`he:124-138` 用了另一套：每个字段两份，`_min_precision`、`_max_precision`。

| 字段 | min | max | 来源 |
|---|---|---|---|
| `npc_burst_radius_*_precision` | 45 | 12 | `he:124-125` |
| `npc_spread_cone_*_precision` | 1.25 | 0.5 | `he:126-127` |
| `npc_lead_projectiles_fraction_*_precision` | 0.2 | 0.75 | `he:131-132` |
| `npc_max_burst_*_precision` | 3 | 4 | `he:134`、`he:136` |
| `npc_min_rest_time_between_bursts_min_precision` | 1.35 | | `he:137` |
| `npc_max_rest_time_between_bursts_min_precision` | 1.7 | | `he:138` |

读法（推断）：AI 有一个 "precision" 值（低到高），字段按它插值。精度高：打得更集中（半径 45 → 12）、提前量算得更准（0.2 → 0.75）、连发多一点。这比单一熟练度细。

`npc_burst_radius_distribution_bias_*`（`he:128-129`）：-1 到 0.75。推断：低精度偏向打在目标身边（一整轮故意打偏），高精度集中。**这是 PvE 公平感的关键**：不是纯随机。

L-STAR 用同一套（`ls:80-83`）；它的 mod 再改成 3 发连发（`ls:149-152`）。

#### 3.2.3 熟练度扩散

枚举 `eWeaponProficiency`：POOR、AVERAGE、GOOD、VERYGOOD、PERFECT（`cs:454-461`）。

字段 `proficiency_<级别>_spreadscale`：扩散倍数。`proficiency_<级别>_additional_rest`：额外休息。`proficiency_<级别>_bias`：只有几把 NPC 枪有（`br:30`、`ls:89`），推断同 3.2.2 的 bias。

**怎么给 NPC 设**：脚本里几乎没有。`vscripts/ai/_ai_soldiers.gnut:280` 的 `SetProficiency( soldier )` 被注释；唯一设的是 `vscripts/_utility.gnut:2329`（bullseye `kv.WeaponProficiency = VERYGOOD`，打靶实体）。假人默认级别不知道，第 5 节第 3 条。

异常（数据里的不一致）：

- **R-301 `proficiency_average_spreadscale` 是 2.0，比 good 的 3.0 还小**（`r1:70-71`），和 Havoc（average 3.5，`ha:89`）、R-99（3.5，`r9:70`）不一样。推断是手误或 R-301 被单独调过。
- `br:29-37`：average 5.0 比其他都大。
- `r9`、`kr`、`sh` 没有 `proficiency_perfect_spreadscale`（默认不知道）。

#### 3.2.4 开火前预警

全部 `npc_pre_fire_delay` 只有 3 个文件（grep），全是 boss 级：

| 武器 | `npc_pre_fire_delay` | `npc_pre_fire_delay_interval` | 来源 |
|---|---|---|---|
| Boss 光束 | 3.5 s | 3 s | `bb:189-190` |
| Boss 炮台火箭 | 1.0 s | 2 s | `br:39-40` |
| Super Spectre（mod） | 0.5 s（另一 mod ×0.1） | 1.5 s | `ss:114-115`、`ss:168` |

**普通枪没有预警**。玩家枪的 `npc_*` 里没这个字段。所以"开枪前闪红"这类提示在 R5 普通敌人上不存在，只有 boss 有（回调 `OnWeaponNpcPreAttack`，本地空壳）。

Boss 光束另有 `chargeup_time`（两边引擎都不认，脚本读，`W-S3-FIELD-CHECK`）。

#### 3.2.5 交战距离

`npc_min_engage_range`、`npc_max_engage_range`（主动交战）、`npc_max_range`（能开火的上限）、`_heavy_armor` 版。数值在第 4 节。近距离枪 `npc_max_engage_range` 比玩家习惯短得多（R-99 1100 u ≈ 28 m），这决定敌人站位。

### 3.3 客户端表现

NPC 枪走同一把枪的特效。`npc_weapon_hemlok` 是真有 3 发点射（`burst_fire_count 3`、`burst_fire_delay 0.15`，`he:142-143`，`fire_rate 15.5`，`he:141`）。

### 3.4 依赖的公共代码

- 弹道：`../_shared/W-BALLISTICS.md`；伤害：`../_shared/W-DAMAGE.md`；扩散：`../_shared/W-SPREAD-RECOIL.md`。
- 字段核对：`../_shared/W-S3-FIELD-CHECK.md`。
- 敌人的 AI（目标选择、追逐）：`../../_shared/D-TARGET-ASSIGN.md`、`../../_shared/D-DECOY-AI.md`。

## 4. 参数

### 4.1 玩家枪里的 NPC 字段

| 字段 | R-301 | R-99 | Spitfire | Kraber | Peacekeeper `mp_weapon_shotgun` | Havoc `mp_weapon_energy_ar` |
|---|---|---|---|---|---|---|
| `damage_near_value`（玩家） | 15（`r1:57`） | 12（`r9:57`） | 21（`lm:100`） | 150（`kr:37`） | 7/粒（`sh:74`） | 20（`ha:74`） |
| `npc_damage_near_value` | 10（`r1:74`） | 9（`r9:66`） | 2（`lm:111`） | 49（`kr:130`） | 25（`sh:82`） | 18（`ha:81`） |
| `npc_damage_far_value` | 8（`r1:75`） | 7（`r9:67`） | 2（`lm:112`） | 49（`kr:131`） | 13（`sh:83`） | 18（`ha:82`） |
| `fire_rate` | 13.5（`r1:87`） | 18（`r9:86`） | 9（`lm:134`） | 1.2（`kr:19`） | 2.8（`sh:125`） | 11.2（`ha:111`） |
| `npc_min_burst` | 2（`r1:83`） | 4（`r9:77`） | 15（`lm:123`） | 1（`kr:123`） | 1（`sh:116`） | 7（`ha:98`） |
| `npc_max_burst` | 4（`r1:84`） | 7（`r9:78`） | 20（`lm:124`） | 1（`kr:124`） | 1（`sh:117`） | 12（`ha:99`） |
| `npc_rest_time_between_bursts_min` | 0.5（`r1:85`） | 0.5（`r9:79`） | 5（`lm:125`） | 5（`kr:126`） | 0.5（`sh:118`） | 0.7（`ha:100`） |
| `npc_rest_time_between_bursts_max` | 0.8（`r1:86`） | 0.7（`r9:80`） | 6（`lm:126`） | 5.25（`kr:127`） | 0.7（`sh:119`） | 1.2（`ha:101`） |
| 一轮时长（推断） | 0.87 s | 0.91 s | 7.44 s | 5.96 s | 0.96 s | 1.80 s |
| **全中 DPS（推断）** | 34 | 55 | 4.7 | 8.2 | 26 或 209（见下） | 95 |
| `npc_max_engage_range` | 2000（`r1:80`） | 1100（`r9:74`） | 1500（`lm:118`） | 12000（`kr:135`） | 800（`sh:111`） | 2000（`ha:86`） |
| `npc_max_range` | 2500（`r1:79`） | 2000（`r9:68`） | 3000（`lm:122`） | 12000（`kr:129`） | 800（`sh:115`） | 2500（`ha:85`） |
| `npc_min_engage_range` | 0（`r1:78`） | 0（`r9:73`） | 100（`lm:117`） | 750（`kr:134`） | 0（`sh:110`） | 0（`ha:96`） |
| `proficiency_poor_spreadscale` | 5（`r1:69`） | 5（`r9:69`） | 没写 | 3（`kr:139`） | 7（`sh:106`） | 5（`ha:88`） |
| `proficiency_average_spreadscale` | 2（`r1:70`） | 3.5（`r9:70`） | 没写 | 2.2（`kr:140`） | 5（`sh:107`） | 3.5（`ha:89`） |
| `proficiency_good_spreadscale` | 3（`r1:71`） | 3（`r9:71`） | 没写 | 2（`kr:141`） | 4.5（`sh:108`） | 3（`ha:90`） |
| `proficiency_very_good_spreadscale` | 2.5（`r1:72`） | 2.5（`r9:72`） | 没写 | 1.5（`kr:142`） | 3.7（`sh:109`） | 2.5（`ha:91`） |
| `proficiency_perfect_spreadscale` | 1（`r1:73`） | 没写 | 没写 | 没写 | 没写 | 1.75（`ha:92`） |
| `proficiency_poor_additional_rest` | 0.2（`r1:66`） | 没写 | 没写 | 没写 | 没写 | 0.2（`ha:93`） |

读法：

- 喷子不确定：`npc_damage_near_value 25` 对比玩家每粒 7，`projectiles_per_shot 8`（`sh:68`）。如果 25 是每粒，一发 200；如果 NPC 每发只算一次，就是 26 DPS。`sg:21`、`sg:28` 的 NPC 专用喷子每粒 3、8 粒 = 24，后一种解释更合理（推断）。第 5 节第 2 条。
- Havoc 95 DPS 在样本里最高，比 R-99 高 70%。如果 HSD 敌人直接拿这些数，敌人用什么枪差很多。
- 全中是上限。实际要乘命中率，命中率由扩散和 `npc_burst_radius` 决定。

### 4.2 `npc_weapon_*`

| 武器 | 谁用 | `npc_damage_near_value` | `fire_rate` | 节奏 | 来源 |
|---|---|---|---|---|---|
| `npc_weapon_hemlok` | 战斗假人步枪、Spectre | 8 | 15.5，3 发点射 | 3–4 发，休息 1.35–1.7 s | `he:105`、`he:141-143`、`he:133-138`；`dm:109` |
| `npc_weapon_lstar` | 战斗假人能量、Death Spectre | 15 | 12 | 8–12 发 | `ls:59`、`ls:95`、`ls:80-83`；`dm:111` |
| `npc_weapon_energy_shotgun` | 战斗假人喷子 | 10/粒，4 粒 | 4，拉栓 1.1 | 连发 1.5（精度两端相同） | `es:78`、`es:34`、`es:113-114`、`es:100-103`；`dm:110` |
| `npc_weapon_shotgun` | | 3/粒，8 粒 | 2 | 1–2 发，休息 0.5–3 s | `sg:21`、`sg:28`、`sg:66`、`sg:84-87` |
| `npc_weapon_boss_beam` | Boss | 字段 10 | 8 | 1 发，休息 30–45 s，预警 3.5 s | `bb:69`、`bb:80`、`bb:185-190` |
| `npc_weapon_boss_turret_rockets` | Boss | 8 | 20，16 发 | 16 发，休息 1–2 s | `br:46`、`br:56-57`、`br:52-55` |

其余（Super Spectre、Spider、Nessie、Goliath、等离子炮、铝热）看 [`PARAMS.md`](PARAMS.md)。

调参：`npc_rest_*` 是最有效的旋钮（线性改 DPS，不改单发手感）；`npc_max_burst` 决定一阵压制多久；`proficiency_*_spreadscale` 改命中率；`npc_max_engage_range` 改站位。

## 5. 未解决和要实测的

**NPC 开火在本地测不了**。已知运行事实：`npc_dummie`、`npc_prowler` 能生成和追人，但**不开枪不近战**；`npc_spectre` 挂死 dedi。下面这些测试都在"有能开火的 NPC"的前提下，目前做不了。不要排进本地 runner；要测得等别的构建，或者等查清本地 NPC 为什么不开火。

1. **节奏公式**：连发发数和休息时间是否按字段随机，`fire_rate` 是否对 NPC 生效。量：录音或记 `OnWeaponNpcPrimaryAttack` 时间戳。**本地不能跑。**
2. **喷子伤害**：NPC 每粒还是每发。**本地不能跑。**
3. **默认熟练度**：假人是哪一级，`kv.WeaponProficiency` 能否生效。**本地不能跑开火**；能先做的：生成假人后读 `kv` 值，这个不需要开枪。
4. **`precision` 是什么、从哪来**：`aisettings` 和脚本都没写它（grep `proficiency` 只命中枚举和一处 bullseye）。推断是引擎按距离或 AI 设置算。这条光看字段定不了。
5. **能查的前置问题（可以本地做）**：为什么 `npc_dummie` 不开枪。候选：S3 dedi 的 AI 和 S21 aisettings 不合；`npc_dummie_combat` 的 `DefaultWeapon`（`aisettings/npc_dummie_combat.txt:25`）没给到。测：生成后读 `npc.GetActiveWeapon()`，有枪说明是 AI 行为问题。
6. **`ap_*` 字段**两个二进制都没有，不用测，不作依据。

结论：**HSD 敌人开枪的手感不能拟合 R5 实测**，只能照字段值做，并写明这一点。

## 6. HSD 实现

**未实现**。现状：

- `Dummy`（`Combat/CombatCore.cs`）：不开枪；追逐型有近战（`meleeRange 48`、`meleeDamage 10`、`meleeInterval 1`、`aggroRange 1500`），`CombatSim.cs` 里走到近身打。
- `Turret`（`Boosts.cs`）是玩家方的自动炮，不是敌人。
- 分支 `origin/claude/w2-framework-b44e35`：grep `proficiency`、`spread` 没有结果；`TargetPicker.cs` 可用来选目标。

建议做法（下一步最值的一件事）：

1. **`NpcWeaponProfile`** 数据类，字段和 R5 同名：`damageNear`、`damageFar`、`fireRate`、`minBurst`、`maxBurst`、`restMin`、`restMax`、`minEngage`、`maxEngage`、`maxRange`、`spreadScale`。默认数值抄第 4.1 节。
2. **`NpcShooter`** 组件挂在 `Dummy` 上，状态机：`Idle → Burst（N 发，间隔 1 / fireRate）→ Rest（T）→ Burst`。子弹先用 `sim.TraceBullet`，瞄准方向 = 指向玩家 + 锥形随机（扩散 × 倍数）。
3. **打偏策略**（3.2.2）：做一个 `burstRadius`，每轮选一个"偏移圆"，半径随 precision 变小。这样不是纯随机喷，玩家能感觉到"敌人在追枪"。**HSD 新增的解释**，R5 语义是推断，写进 `R5-DIFF-ARCHIVE.md`。
4. **Boss 预警**：`preFireDelay`，配 HUD 或特效。普通敌人不加（R5 也没有）。
5. **第一版选型**：起步用 Hemlok 档（8 伤害、3–4 发、休息 1.35–1.7 s），它是 R5 给假人的枪（`dm:109`）；不要直接用 Havoc（95 DPS）。

开关建议：`hsd.combat.npc.fireEnabled`（默认开）、`npc.damageScale`、`npc.spreadScale`，方便调难度。
