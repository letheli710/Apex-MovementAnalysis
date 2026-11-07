# R5 界面盘点（UI-INVENTORY）：准星、命中反馈、移动、技能，和 HSD 现在的对照

2026-11-07，会话 `ui-inventory`。只研究，不改 Unity。配套的方案是 [UI-PLAN.md](UI-PLAN.md)。

## 先说结论（给人读的）

R5 的界面分三层：**引擎报事件**（打中了、受伤了、换弹进度多少），**脚本决定显示什么、传什么参数**，**编译好的 RUI 资源负责画**（形状、颜色、大小、淡出曲线全在 `ui/*.rpak` 里）。所以"什么时候出现、带什么数字"大部分能从脚本和武器字段读出来；"长什么样"读不出来，只能截图。

四层的情况：

1. **武器**：每把枪有自己的腰射准星，31 把枪用了 9 种形状（三角、十字、十字加点、Alternator 式、霰弹、Mastiff、Charge Rifle、L-STAR、Bocek）。准星张开多大由当前扩散角实时决定（`weapon_spread`），每把枪再加一个固定的 `base_spread`。开镜的瞄具、枪身上的弹量屏都是贴在枪模网格上的 RUI，一共 112 个资源。右下角是弹药和两把枪的标签，准星旁边有低弹量 / 换弹 / 换枪提示。
2. **命中反馈**：准星上一个 X（一个 RUI 反复重启，不叠加；按命中类型分 8 种：护盾、爆头、无效距离等，击杀和击倒共用一个变体），默认带护盾等级图标。伤害数字默认是**累加式**（0.25 s 内的连续命中合成一个数，最后一击后再留 1.0 s）。**用户说的霰弹枪红色命中图标是 `projectile_hit_dot`**：一颗弹丸打中就在世界里的命中点放一个点，只对一发多弹丸的枪（EVA-8 8、Peacekeeper 9、Mastiff 5、Mozambique 3、Triple Take 3）。受伤方向默认是 3D 箭头（不是 2D 圆环）。
3. **移动**：**R5 S21 在移动时不显示任何界面**。翻越、跳、滑铲、滑索、跳板起飞、爬墙都只有粒子、声音和镜头。例外只有：Pathfinder 钩爪的常驻射程准星、Valkyrie 喷气燃料条、滑索枪的放置界面、Flowstate 移植的 S27 翻越加速时机圈。HSD 现在的滑索上索提示、跳板二段跳提示、速度条都是 HSD 自己加的。
4. **技能**：Valkyrie 导弹群预览是 **12 个圈（4 排 × 3 列）**，升级后 20 个（4 × 5）。原生网格函数、`burst_fire_count 12`、本地化文字"4x3 改成 4x5"三处一致。用户记得的 9 个和 S21 对不上。HSD 也画 12 个圈，但排成 5 + 5 + 2，排法错了（§5.1）。技能预览大多是**世界里的粒子**（地面圈、标记、抛物线），颜色常在脚本里（Fuse 绿 / 橙 / 红），大小靠控制点；底部技能栏用一个 RUI 显示冷却比例和充能格数。

HSD 现在全部是 IMGUI 调试占位：一个通用准星点、一个通用命中 X（0.15 s，击杀变红）、上飘的伤害数字、文字行显示弹量和冷却、3D 圆柱代替技能预览。逐项对照在 §6。

**这次没能在本地 R5 截图**：开始测量时 `GAME-LOCK.txt` 被 `shotgun-reticle` 会话持有（它在测 `projectile_hit_dot`）。凡是"长什么样"的项都标了 **[要截图]**，测法清单在 §7。

### 怎么读

- 编号：武器 W-、命中 H-、移动 M-、技能 L-。每项写：样子、出现 / 消失、数字、出处。
- 标注：[脚本] 读了脚本；[字段] 武器设置文件；[原生] Ghidra 读了 `r5apex.exe`；[项目] 以前的研究；[要截图] 样子只在编译资源里；[Flowstate] 是 Flowstate 加的，不是原版 S21。
- 路径：`vs/` = `research-src/s21-platform/scripts/vscripts/`，`w/` = `research-src/s21-platform/scripts/weapons/`。行号是 S21 Flowstate 源码的。
- 原始笔记（含本机路径和 Ghidra 输出）在私有仓库 HSD-RawData 的 `research/ui/notes/`。

---

## 1. R5 的界面是怎么搭起来的

| 层 | 做什么 | 例子 |
|---|---|---|
| 引擎 | 报事件，提供"轨道"（每帧自动更新的数值） | `ClientCodeCallback_PlayerDidDamage`（`vs/client/cl_player.gnut:471`）；`RUI_TRACK_WEAPON_CLIP_AMMO_MAX`；准星参数 `weapon_spread` |
| 脚本 | 决定何时建 RUI、传哪些参数、何时重启 | `vs/client/rui/cl_hud.gnut:576-631`（命中 X）；`vs/client/rui/cl_weapon_status.gnut`（弹药和技能栏） |
| 武器字段 | 每把枪声明自己的准星和枪身 RUI，参数绑到引擎轨道 | `RUI_CrosshairData`、`UiDataN`（`w/mp_weapon_rspn101.txt:1002-1046`） |
| RUI 资源 | 画：形状、颜色、尺寸、字体、动画 | `ui/crosshair_tri.rpak`、`ui/player_hit_indicator.rpak` |
| 世界里的东西 | 粒子、模型、高亮，不是 RUI | `P_valk_rckt_AR_marker`、`mdl/weapons/bullets/damage_arrow.rmdl` |

绘制层：`RUI_DRAW_HUD`（全屏 HUD）、CockpitPostFX（贴在驾驶舱，跟镜头）、world（`drawInWorldSpace`，在世界坐标）。玩家设置（菜单 `resource/ui/menus/panels/hud_options.res`）和默认值（从 `r5apex.exe` 的 ConVar 注册读出）：

| 设置 | 默认 | 选项 |
|---|---|---|
| `hud_setting_damageIndicatorStyle`（命中 X） | **2** = X + 护盾图标 | 0 关 / 1 只有 X / 2 X + 护盾 |
| `hud_setting_damageTextStyle`（伤害数字） | **1** = 累加 | 0 关 / 1 累加 / 2 浮动 / 3 两种都有 |
| `damage_indicator_style_pilot`（受伤方向） | **2** = 只有 3D 箭头 | 0 只有 2D / 1 两种 / 2 只有 3D |
| `cl_visual_clutter`（SDK） | 1 | 1 = 去掉 3P 护盾受击包裹和 3P 破盾爆点 |

**设计规律**（解读）：R5 的 HUD 和 §5 的技术规矩一样——**行为写成字段，一把枪一行数据**。准星样式、枪身屏、开镜瞄具、技能栏显示方式（`ammo_display bar / count`）都是字段；脚本只把引擎状态接到 RUI 参数上。

---

## 2. 武器层

### W-01 每把枪的腰射准星 [字段]

表：[data/ui-crosshair.tsv](data/ui-crosshair.tsv)（31 把枪 36 个准星槽，`tools/xhair.py` 从 S21 字段生成）。

| 准星 RUI | 枪 | `base_spread` | 额外参数 |
|---|---|---|---|
| `crosshair_tri` | R-301、Hemlok（−2）、Nemesis | 0 / −2 | playerFov |
| `crosshair_tri_adjusted_alpha` | Mozambique | −3 | isFiring |
| `crosshair_plus` | R-99、RE-45（−2）、CAR、Havoc、Devotion、Spitfire、Rampage、Prowler、Volt、Wingman | 0 / −2 | isFiring |
| `crosshair_plus_adjusted_alpha` | P2020 | 0 | isFiring |
| `crosshair_plus_dot` | 30-30、Longbow、G7、Sentinel（节奏参数）、Kraber；Havoc 第二槽 | 0 | 30-30 碎甲参数 |
| `crosshair_alternator` | Alternator、Flatline、Triple Take（`charge`） | 0 | isFiring / charge |
| `crosshair_shotgun` | EVA-8（+1）、Peacekeeper | +1 / 0 | isFiring |
| `crosshair_shotgun_hopup` | Peacekeeper 扼流（choke） | 0 | charge |
| `crosshair_alternator_charged` | Triple Take 扼流 | 0 | charge |
| `crosshair_mastiff` | Mastiff | 0 | isFiring |
| `crosshair_charge_rifle` | Charge Rifle | **+10** | chargeFrac、readyFrac |
| `crosshair_lstar` | L-STAR | 0 | — |
| `crosshair_bow_temp` | Bocek | 0 | 箭种、节奏、chargeFrac（曲线后） |
| `rampart_turret_crosshair` | Sheila（`red_crosshair_range 1500`） | 0 | — |

- **每把枪都带的参数**（`DefaultArgs`）：`adjustedSpread = weapon_spread`、`adsFrac = player_zoomFrac`、`isSprinting`、`isReloading`、`teamColor = crosshair_team_color`、`isAmped`、`crosshairMovementX/Y`。
- **多个准星**：`active_crosshair_count` 全是 1，`rui_crosshair_index` 选当前那个；模式切换靠 mod 改 index：30-30 `in_ads`、Hemlok `altfire`、Triple Take / Peacekeeper `choke` 改成 1（[data/ui-crosshair-mods.tsv](data/ui-crosshair-mods.tsv)）。
- **准星变红**：`red_crosshair_range` 在所有玩家枪上是 0，只有 Sheila、炮台、滑索枪等非 0。**玩家枪没有"瞄到敌人变红"。** [字段]
- **样子** [要截图]：每种形状的线长、线宽、间隙、颜色、透明度。

### W-02 扩散怎么显示在准星上 [字段 + 推断]

- 准星的张开量来自 `weapon_spread`（引擎当前扩散角，度）+ 每槽 `base_spread`，再用 `playerFov` 换成像素。公式在 RUI 里，**推断**是 `间隙 px = tan(spread + base_spread) / tan(FOV/2) × 半屏高`。[要截图] 定系数。
- R-301 扩散字段（度）：站 3.0、走 6.6、冲刺 8.4、蹲 2.4、空中 8.4；每发 +0.2，上限站 2.0 / 蹲 1.5 / 空中 3.0；回落延迟 0.25 s、速率 100；移动变化速率 30。全枪见表 `ui-crosshair.tsv` 的 `spread_*` 列，或 `research/design-philosophy/WEAPON-FIELDS.md`。
- 霰弹不吃扩散：EVA-8 六种姿态都是 1.2，Peacekeeper 都是 2.8，Mastiff 0，Mozambique 2。所以**霰弹准星大小固定，形状 = 弹丸图案**（DESIGN-PHILOSOPHY §7.7），图案名 `eva8`、`energy_shotgun_2`、`mastiff_4`、`shotgun_pistol_3`、`doubletake`。
- 准星位置：准星 = 瞄准 + (1 − fraction) × punch，腰射残差 0.000° [项目，RECOIL-VIEW §1.1]。
- 冲刺、换弹、开镜时淡出：参数齐全，淡出速度 [要截图]。

### W-03 霰弹准星的形状 [字段 + 要截图]

- EVA-8、Peacekeeper 共用 `crosshair_shotgun`（EVA 再 +1 `base_spread`），Peacekeeper 扼流换 `crosshair_shotgun_hopup`；Mastiff 自己的 `crosshair_mastiff`；Mozambique 用三角（`tri_adjusted_alpha`）。
- 准星 RUI 没有接收图案参数，所以**图案形状是画死在每个 RUI 资源里的**（推断）。和图案对不对得上、开镜收拢（Mastiff 1.45°）时准星跟不跟，要截图。
- `shotgun-reticle` 会话（`combat/shotgun-reticle`，`research/combat/gun-measure/shotgun-reticle/`）正在实测这一块和 H-04，结果以它为准。

### W-04 开镜瞄具 [字段]

表：[data/ui-reticles.tsv](data/ui-reticles.tsv)（31 把枪 293 个 `UiData` 块，112 个不同资源）。

- 机瞄：每把枪 `ui1` 是贴在 `*_rui_upper` 网格上的发光标记（`r301_reticle`、`volt_sights` …），参数 `vis = player_zoomfrac`（随开镜淡入）、`centerOffset`。以前实测：Volt 红圈、Havoc 小红圈、Rampage 粉色括号、Mastiff 白色方括号、Triple Take 红菱形、Charge Rifle 红弧、G7 青弧 [项目，IRON-SIGHTS:78]。
- 光学瞄具：装上后 mod 把 `ui1` 关掉、开 `ui6..ui17`：`hcog_classic_sights`（1×）、`hcog_upper`（2× Bruiser）、`holo_sights`、`holo_variable_sights`（`zoomFOV`）、`hcog_ranged_sights`（3×）、`aog_variable_sights`（2–4×），这两个带 `varSightOffsets`、`sniperZeroDistance`、`boltZeroDistance`；狙击镜 `sniper_optic_sights` 带 `crossDist`（距离读数）。
- 锚点：`viewmodel_ads_rui_bottomleft_attachment`（每枪 `RUI_BL_CROSSHAIR_R301`…，每个瞄具 `_HCOG_OG / HCOG / HOLO / HOLOMAG / ACGS / AOG`）+ `viewmodel_ads_centerpoint_attachment`。引擎读，脚本不碰。
- 颜色：玩家设置 `reticle_color`（`COLORID_RETICLE`）。
- 狙击归零点：`sniper_range_auto_set.nut` 在这个版本是空的（打印 "not available in S3"）；Vantage 的 `vantage_sniper_info` 见 L-19。
- 样子 [要截图]：以前有 30 把枪的开镜图（`origin/combat/iron-sights` 的 `pics/ads-sheet-*.jpg`），瞄具类的还没有。

### W-05 枪身弹量屏 [字段]

- 每把枪 `ui2`（或同类）是下方网格上的弹量 RUI：`r101_ammo_counter`、`spitfire_ammo_counter`、`eva_shotgun_screen`… 参数 `ammo = weapon_ammo`、`clipSize`，有的带 `fireMode`、`clipCount`、`energizeFrac`（Nemesis 热量、Rampage）、`chargeFrac / isCooling`（L-STAR 过热只在枪身屏上显示）。
- G7 带 `playerDirection`（指南针），Triple Take 带 `scopeADS`。全表在 `ui-reticles.tsv`。
- 样子 [要截图]。

### W-06 右下角武器 HUD [脚本]

- `ui/weapon_hud_v2.rpak`（`vs/sh_consts.gnut:2476`，建于 `cl_weapon_status.gnut:270-281`）。弹匣 / 备弹都走引擎轨道（`:1981-2028`），所以数字永远是实时的。
- 两把枪的标签：名字、弹药颜色、选中哪一把；拿出技能或手雷时仍显示最后一把主武器（`:533-610`）。
- 颜色：弹药类型 → `COLORID_AMMO_*`（轻型、能量、霰弹、重型、狙击、箭）；稀有度 → TIER1–3、金、红（空投）。RGB 值在引擎调色板里 [要截图]。
- 配件格：瞄具、枪管、弹匣、枪托、模块，锁定格。
- 开火模式：图标 `rui/hud/weapon_toggle/single_shot / burst / automatic …`，Hemlok 爆发橙 `<1,0.5,0>`、全自动蓝 `<0,0.5,1>`。**这个版本 `WeaponHasFireModeSelect` 被写成 `return 0`**（`:1559-1563`），所有枪显示单一模式，切换播报不触发。和正版不一样，要截图确认。

### W-07 准星旁的弹量提示 [脚本 + 字段]

- `ui/ammo_status_hint.rpak`（`cl_weapon_status.gnut:221-232`）：`ammoFrac`、`reloadingFrac`、`readyToFireFrac`、`minAmmoToFireFrac`、`canShowReloadHint`。
- **低弹量阈值** = 每把枪的 `low_ammo_fraction`：大多 0.30；Wingman、Hemlok、Havoc、Nemesis 0.40；Triple Take 0.35；Charge Rifle、Mozambique 0.34；Sentinel 0.26；Kraber、Mastiff 0.25；Prowler、30-30 0.20；Bocek 0.10。低弹量还有逐发音效 `low_ammo_sound_name_1..6`。
- 没有备弹还按换弹：横幅 2.0 s（`NO_RESERVE_AMMO_DISPLAY_TIME`，`:100`）。
- 换枪提示：另一把主武器有效、没倒地、空了不自动换时显示（`:686-689`）。
- 换弹：没有专门的换弹条；`reloadingFrac` 进这个 RUI，准星也收到 `isReloading`。样子 [要截图]。

### W-08 蓄力、热量、Energize [字段 + 脚本]

| 枪 | 在哪显示 | 数字 |
|---|---|---|
| Charge Rifle | 准星 `chargeFrac` + 枪身 `charge_rifle_screen` | `charge_time 0.85`、冷却 1.1 |
| 30-30 | 准星 `readyFrac` + 枪身 `weapon_3030_charge_bars` | 0.4 s、2 级 |
| Bocek | 准星 `chargeFrac`（曲线后）+ 枪身 | 0.45 s、6 级 |
| Triple Take / Peacekeeper 扼流 | 换成 `_charged` / `_hopup` 准星 | 来自 choke mod |
| Havoc 预热 | **没有任何 HUD**，只有音效 | 0.42 s |
| Sentinel / Rampage Energize | 右下 `ui/weapon_hud_charged.rpak` 嵌套条 + 准星 `crosshair_energize_status_sentinel` | Sentinel 充 5 s、持续 150 s、提示 < 0.18；Rampage 3.7 s / 120 s / < 0.25；颜色全在字段里（Sentinel 主色 134 255 221，Rampage 255 0 4） |
| Nemesis 热量 | 右下 `weapon_hud_charged_nemesis`，`chargeBarFrac = GetHeatValue()` | 每发 0.04167（24 发满），8 s 后 8 s 降完；渐变 127 127 127 → 84 130 219 → 92 191 218 |
| L-STAR 过热 | 只在枪身 `lstar_screens` | 2.2 s 满热、过热冷却 3.63 s |
| Sentinel 上膛点 | `crosshair_single_dot_helper`：1/射速后出现，持续上膛时间 × 0.66，alpha 0.5，淡入 0.1、淡出 0.2 | `mp_weapon_sentinel.nut:149-187`；Bocek alpha 0.7，0.05 / 0.1 |

---

## 3. 命中反馈层

### H-01 准星上的 X（`ui/player_hit_indicator.rpak`）[脚本]

- **一个常驻 RUI**，每次命中把 `startTime` 重设一次（`cl_hud.gnut:578-586`），**不叠加**，连续命中就是一直重启同一个 X。
- **命中类型优先级**（`cl_player.gnut:631-647`，枚举 `sh_consts.gnut:1222`）：影子 > 超护盾 > 护盾 > 暴击（爆头或 `DF_CRITICAL`）> 无效（超出最大距离）> 护甲 > 枪盾（vortex）> 普通。
- 护盾命中 = 有护盾伤害**并且这一枪后还剩护盾**（`:497-498`）。所以打破护盾的那一枪不是护盾命中，通常是普通或爆头。
- 击杀和击倒共用一个变体（`isKillShot = isKillShot || isKnockdownShot`）。
- 默认样式 2 额外传护盾图标、等级、剩余比例（玩家看护甲；训练假人 `loot_armor_1`；A 墙、移动护盾、城墙按剩余血量）。
- 不显示：伤害 ≤ 0；脚本覆盖；**射击场里打假人默认没有 X**（"显示命中标记"默认关，`firing_range.gnut:113`）。
- 时长、大小、每种类型的颜色、击杀变体、淡出 [要截图]。旧 VGUI 的提示（TF2 时代，`hudcrosshair_code.res`）是 144×144，普通白、爆头 255 128 64、无效黑——不一定是 RUI 的样子。

### H-02 命中声音 [脚本]

- 普通 `Player.Hitbeep`、暴击 `Player.Hitbeep_crit`、爆头 `Player.Hitbeep_headshot.Human_1P_vs_3P`（击杀 `...Kill...`）、无敌 / vortex 各自一个；击杀非爆头放击杀冲击声，霰弹有专用的（`cl_player.gnut:664-718`、`cl_player_common.gnut:65-140`）。
- 破盾声由服务端放：攻击方 `humanshield_break_1p_vs_3p`（`_health_regen.gnut:816-836`）。
- 近战没有命中声但有 X；`DF_MAX_RANGE` 没有声音。

### H-03 破盾、护盾受击 [脚本]

- X 本身没有破盾参数。破盾动画挂在**累加伤害数字**上：`shieldBreakTime`、`shieldBreakTier`（`cl_hud.gnut:707-711`）[要截图]。
- 3P：护盾受击包裹 `P_armor_body_CP`、破盾 `P_armor_3P_break_CP`，按护甲等级着色；默认 `cl_visual_clutter 1` 把这两个去掉了。
- 1P（自己）：`P_armor_FP_hit`、`P_armor_FP_break`、充能、充满，都按自己的护甲等级着色（`cl_pilot_health_hud.gnut:388-444`）。

### H-04 霰弹的命中点（`ui/projectile_hit_dot.rpak`）——用户说的"红色图标" [脚本]

- 每次伤害事件，只要这把枪 `GetProjectilesPerShot() > 1`，就在**世界命中点**新建一个 RUI，带 `isCrit`（`cl_hud.gnut:636-643`）。一颗弹丸打中一个点。
- 和 X 的设置无关；**射击场里关掉**（`:845-846`）。
- 适用：EVA-8 8、Mastiff 5、Peacekeeper 9（某模式 6）、Mozambique 3、Triple Take 3；mod 可能让 30-30、Bocek、Alternator 也大于 1。
- 颜色、大小、寿命、转视角时是不是钉在世界里 [要截图]。`shotgun-reticle` 会话的 `sr.py` 正在测（`dots / life / turn`）。

### H-05 伤害数字 [脚本]

- **累加**（默认，`ui/stacking_damage_text.rpak`）：每个目标一个。距离上一次命中 ≤ **0.25 s**（`FDT_STACK_THRESHOLD`）就加到同一个数上，每次命中重启 **1.0 s**（`FDT_DURATION`）。所以连续开火时总数一直在，停手 1.0 s 后消失。
- **浮动**（选项 2 / 3，`ui/floating_damage_text.rpak`）：每次事件一个，1.0 s；同帧同目标合并；间隔 < 0.33 s 时旧的数字按序号错开。
- 位置：目标 0 u 时在身体中心，256 u 以上在包围盒顶上；屏幕上再上移 0.015（累加）/ 0.040（浮动）屏高。
- 颜色按护盾等级、暴击，在 RUI 里 [要截图]；等级颜色可能就是战利品颜色（白 192 192 192、蓝 58 133 176、紫 136 63 162、金 220 185 39、红 255 0 0），没证实。

### H-06 受伤方向 [脚本]

- **3D 箭头**（默认）：模型 `damage_arrow.rmdl`，16 个循环用，挂在镜头前 <20, 0, −2>；动画 `damage_incoming_small` **1.5 s**（玩家和 NPC 打的都是 small），titan / 无攻击者 1.75 s；large 2.0 s 飞行员用不到；**伤害大小不影响箭头大小**。每帧指向伤害来源，横滚 = sin(偏航差) × 90°（`cl_damage_indicator.gnut:1031-1222`）。
- **2D 圆环**（默认关）：`ui/damage_indicator.rpak`，每次 4.0 s，最多约 8 个，来源点按距离抖动 ±256 u（`:411-455`）。
- 不显示方向：自伤、圈、毒气、电网、燃烧等（`:376-409`）。

### H-07 受伤时的屏幕效果 [脚本]

- 闪屏 `ScreenFlash(2, 2, 2, hold, 0.2)`，hold = 0–0.25 s 按伤害 / 100；近战 `(15,15,15,0.1,0.2)` + 镜头 jolt 100 / 0.25 s；圈 `(0.7,0.5,0.5,0.1,2.0)`（`:184-219`）。亮度单位在引擎里 [要截图]。
- 低血量：`ui/hurt_overlay.rpak` 全屏，血量 1.0 → 0.25 之间渐入；掉血时镜头前 `P_health_hex_fast`（最多 6 个）；疼痛声层在 0.66 和 0.33 血量开始（`cl_pilot_health_hud.gnut`、`cl_screenfade.gnut:265`）。
- 被爆头听到 `Hitbeep_headshot.Human_3P_vs_1P`。

### H-08 手雷 / 威胁指示 [脚本]

- 敌方有爆炸伤害的投射物：镜头前 <25, 0, −4> 的箭头模型 + 图标模型（破片、EMP、集束、骷髅……），在爆炸半径 + 65 u 内且有视线时显示，0.25 s 防闪；自己的手雷延迟 0.4 s（慢速 0.15 s）（`:458-750`）。
- 技能区域（Valk 目标 195 u、Catalyst 尖刺 440、Bangalore 每弹 350 …）调 `ShowGrenadeArrow(radius)` 复用同一套。

### H-09 敌人血条 [Flowstate]

- `cl_damage_healthbar.gnut` 是 Flowstate 加的（命中后用 Seer 的 `recon_scan_target` 3.0 s，假人 2.5 s）。**原版 S21 打中敌人没有血条**，只有 X + 护盾图标 + 数字。

### H-10 射击场训练点 [脚本]

- `ui/training_target_hit_dot.rpak`，只在射击场且开了"显示命中标记"（默认关）。打中 / 爆头 / 打偏三种；打偏 2 s 内的会投影到最近目标的距离上，让你看到偏在目标旁边哪里；钉在目标上 3.485 s（`cl_hit_markers.nut`）。

---

## 4. 移动层

### M-00 结论：R5 S21 移动时没有界面 [脚本]

| 动作 | R5 有没有界面 | 证据 | 别的反馈 |
|---|---|---|---|
| 翻越 | 没有 | 原生 `TraversalMove`，没有建 RUI 的回调 [项目 B1 §1] | 动画镜头 |
| 超级滑翔 | 没有 | 原生 | — |
| 跳 / 二段跳 | 没有 | `CodeCallback_GivePlayerDoubleJump` 只跑回调 | — |
| 滑铲 | 没有 | `vs/` 里没有滑铲相关 RUI | 镜头倾斜、灰尘 |
| 爬墙 / 抓边 | 没有 | 没有脚本回调 | — |
| 滑索上索、骑行、速度 | **没有提示，没有速度** | `cl_zipline.gnut:7-10` 只跑 Chroma；上索规则 35° 视锥、开镜不能上（`sh_codecallbacks.gnut:292-327`）；没有 `SetUsePrompts`，116 条 `%use%` 文本没有滑索 | Chroma |
| 跳板起飞 | 没有 | `mp_weapon_jump_pad.nut` 没有 RUI | — |
| 落地 | 没有 | 只有回调 | 镜头 kick |
| Stim | 没有 HUD | 镜头前粒子强度随速度（0–360 → 5–200），结束闪屏 | 粒子 |

R5 的"移动 UI"只有下面几个例外。

### M-01 钩爪射程准星 [字段]

- `w/mp_ability_grapple.txt:84-111`：`crosshair_grapple_charge`（拿着钩爪时）+ `crosshair_grapple`（**常驻**，`ordnance_crosshair_always_on_start_index 1`，拿别的枪也画）：`ammoFrac`（冷却）、`isGrappleInRange`（原生，850 u）、进入 / 离开射程时间。冷却 300 / 10 = 30 s。
- 样子 [要截图]。Vantage Echo 同样模式 `crosshair_tac_range`。

### M-02 Valkyrie 燃料条 [脚本]

- `ui/valk_jets_meter.rpak`，`chargeFrac` = 滑翔计量（`mp_ability_valk_jets.nut:228-232`）。燃料量是玩家设置 `glideDuration`，不在这个仓库。

### M-03 滑索枪放置 [脚本]

- `ui/zipline_placement.rpak` + 射程脉冲 `P_ar_zipline_range`（控制点 1 = 8000）+ 线预览 `P_wpn_zipline_previs`；距离 700–8000。

### M-04 S27 翻越加速时机圈 [Flowstate 移植]

- `ui/mantle_boost.rpak`，CockpitPostFX 32000；进度 = 翻越动画比例，甜点比例，圈半径屏幕 1.5°，圆心偏 δ（动画镜头俯仰）；标签 "BOOST"；结果留 0.25 s；输入设置 0–3、UI 设置 0–3（关 / 简洁 / 标记 / 完整）。加速时镜头前 `P_van_tac_launch_screen` + `MantleBoost_1p`（`sh_pilot_passive_mantle_boost.gnut`、B1 报告 §3）。颜色、粗细、四种模式的差别 [要截图]。

### M-05 Sparrow [Flowstate 移植，2025 传奇]

- 二段跳计量 `ash_dash_meter`、蹬墙提示 `mantle_launch`。HSD 没做 Sparrow，只记下。

---

## 5. 技能层

通用部分：

- **抛物线**：引擎画，字段开（`grenade_arc_indicator_effect` 73 个文件），颜色就是选哪个粒子：红（破片、Bangalore、Gibraltar 大招、Ash、Revenant 沉默）、橙（铝热剂、Fuse 被挡）、蓝（电弧星）、浅蓝（Horizon、Conduit）、绿（Fuse、Caustic）、Maggie 专用。
- **放置虚影**：高亮 `deployable_model` / `deployable_model_invalid`，颜色不在脚本里 [要截图]。
- **底部技能栏**：`ui/tactical_ability_hud.rpak`、`ui/ability_hud.rpak`（`cl_weapon_status.gnut:238-260`）。`chargeFrac` = 弹量 / 满；**格数 = 弹量 / (每次 × 连发)**；`minFireFrac`；大招 READY / CHARGING / ACTIVE；`ammo_display bar`（Stim、Valk 战术、钻头、尖刺…）或 `count`（钩爪、Wraith、Ash、Vantage、Amped Cover…）。百分比文字和就绪脉冲 [要截图]。就绪音 `survival_ui_tactical_ready` / `Survival_UI_Ultimate_Ready`，没冷却好按键 `Survival_UI_Ability_NotReady`。
- **失败提示**：`AddPlayerHint(时长, 淡出, 图标, 文本键)`，文本键是哈希，英文只能截图对。
- **队伍颜色**（`sh_consts.gnut:367-421`）：HUD 友方 161 196 255、敌方 255 120 32；粒子友方 87 151 219、敌方 255 120 32、中立 220 220 220、燃烧 246 134 40。

### L-01 Valkyrie 导弹群：12 个圈 [原生 + 脚本 + 字段]

- **12 个（4 排 × 3 列），升级 20 个（4 × 5）。** 原生 `GetWeaponMissileMultipleTargets(row, column, …)`：外循环 4 排；每排中心 1 个，之后每步左右各 1 个，一排 = 1 + 2 × (column − 1)。脚本传 4、2（升级 3）→ 4 × 3 = 12、4 × 5 = 20。另三处一致：`burst_fire_count 12` / 升级 20；本地化 "Missile Swarm pattern modified from 4x3 to 4x5"；`fanAdjustments` 20 项。
- 脚本注释 `((1 + sideSteps*2) * (forwardSteps+1))` = 25 / 35 是过时的；`research/combat/valkyrie-missile-swarm/SYSTEM.md` 的"5 列 × 5 排，取前 12"是错的，它的待查问题 1 由此回答。
- **用户记得的 9 个**和 S21 对不上；可能是掩体挡住、看不到最远一排、或者别的赛季。俯视截图能定。
- 间距：排距 185 u、列距 163.16 u，每点从 250 u 高落到地面；整片约 326 u 宽、555 u 深；射程 400 u – 125 m（跳伞 250 m）。
- 样子：每点一个粒子 `P_valk_rckt_AR_marker`，贴地随法线转，每帧更新；只给自己看。爆炸半径 150，圈的大小和颜色在粒子里 [要截图]。
- 出现：武器激活（瞄准）；消失：第 0 发开火、收起、死亡。开火后 `P_valk_rckt_AR_lock` 留在锁定点，火箭在飞就留，最多 5 s。
- 敌方：目标 195 u（150 × 1.3）内且有视线，显示威胁箭头。
- 底部栏：`bar`，300 / 25 / 每秒 12 → 25 s，必须满才能放。

### L-02 Fuse Motherlode

- 地面圈 `P_ar_target_fuse_instant`，半径 420；中心标记。颜色每帧（控制点 1）：可放 **绿 10 255 0**、被挡 **橙 255 125 0**（模拟弧线落点离空爆点 > 50 u）、超距 **红 255 10 0**（> 7875 u = 200 m）；最小 522 u。被挡时圈移到挡住的点。
- 抛物线绿，被挡换橙，超距隐藏。望远镜界面 `ui/mortar_binoculars.rpak`（`maxRangeDist`、`inRange`、`hasClearance`、`rangeDist`）[要截图]。状态变时放 `Fuse_Ultimate_UI_InGame_True / _False`。

### L-03 Maggie 钻头

- 放置颜色写在脚本里（可以 128 188 255、太厚但能放 255 200 40、错误 255 40 40），**但 S21 看不到**（粒子是 `_none_FX_test`、代理隐藏）。玩家看到的是抛物线 `P_mm_breach_arc`，错误时末端换 `_end_fail`。
- 墙厚读数 `ui/mm_riot_drill.rpak`：`depth`（错误 −1），文字颜色 `GetTriLerpColor(depth / 最大厚度, 白, 黄 255 210 73, 橙 255 122 0, 0.6, 0.3)`，实际 0–60 % 白到黄，再往上整段橙；错误橙。最大厚度 max(设置, 512)，下限 400。

### L-04 – L-20 其他做过的技能（摘要）

| # | 技能 | 预览 / 标记 | 数字 | 出处 |
|---|---|---|---|---|
| L-04 | Bangalore 滚雷 | 只有红色抛物线；照明弹 `P_bFlare` 6.5 s；每颗没有标记；威胁箭头 350 | 宽 2750 u、6 × 6 | `mp_weapon_grenade_creeping_bombardment.nut` |
| L-05 | Gibraltar 轰炸 | 红抛物线；红烟柱 `P_artillery_marker_scan` 6 s + 2 s；每颗落点标记 `P_ar_artillery_marker`（燃烧色），落地删 | 半径 1024，6 区 × 6 | `_bombardment_utility.gnut:497-520` |
| L-06 | Caustic 毒气陷阱 / 手雷 | 绿抛物线；陷阱 RUI 图标 `dirty_bomb_marker_icons`（血量、开始时间） | 毒气 256、触发 140、11 + 2 s；3 格 | `mp_weapon_dirty_bomb.nut:795-802` |
| L-07 | Catalyst 尖刺 | 没有虚影；抛物线第一段蓝其余红；友方 80 150 255 / 敌方 255 32 10 | 2 个（升级 3），4 根 / 47 u | `mp_ability_spike_strip.nut` |
| L-08 | Catalyst 黑幕 | 脚本虚影：一排柱子 20 根（升级 27），透明度 175 / 255 ≈ 69 %，每步 88 u；**没有无效颜色**，缺柱子就是提示 | 墙 15 s | `mp_weapon_ferro_wall.nut:2183-2260` |
| L-09 | Wattson 电网 | 虚影 + 放置 RUI `tesla_trap_placement`（上限 12、连接 2）+ 连线 RUI `tesla_trap_link`（`maxDist 768`、距离表盘）+ 射程圈 | 连接 768 u、吸附 98、放置 300 | `mp_weapon_tesla_trap.nut:1610-1756` |
| L-10 | Wattson 拦截塔 | 圈 `P_ar_edge_ring_gen`，颜色 134 182 255，范围 512；进 300 u 闪 | 3 个，150 HP | `mp_weapon_trophy_defense_system.nut` |
| L-11 | Conduit 屏障 | 圈（同 Fuse 粒子）50 200 255，半径 200；中心 + 6 个标记；**没有无效颜色**，求解失败就冻住 | 120–2000 u，7 个，45 s | `mp_ability_conduit_shield_mines.nut:370-680` |
| L-12 | Newcastle 城墙 | 落点准星 前 64 220 255 / 后 128 128 128；虚影墙；无效时只剩红准星 + 4 种提示 | 跳 40 m（到队友 80 m） | `mp_ability_armored_leap.nut:3060-3330` |
| L-13 | Rampart A 墙 | 引擎虚影 128 u，只有有效 / 无效高亮；放下后血量图标 48 u 高 | 4 个，45 → 400，3 s | `mp_weapon_cover_wall.nut` |
| L-14 | Rampart Sheila | 模式提示 `mobile_hmg_hint`；瞄准激光；放置**没有射程圈**（注释掉了） | 3 个 | `mp_weapon_mobile_hmg.nut:639-660` |
| L-15 | Horizon 黑洞 | 浅蓝抛物线；半径圈 `P_wpn_black_hole_preview` 400，每帧放在预测落点；没有无效 | — | `mp_ability_horizon_black_hole.nut:221-249` |
| L-16 | Ash 电弧陷阱 | 红抛物线；放下后红圈；被拴住：屏幕边缘 + 方向箭头 | 拴 210、5 s | `mp_weapon_arc_bolt.nut` |
| L-17 | Seer 注视焦点 | **瞄准时没有锥形**；蓄力 0.4 s 后心跳波形 RUI；松开后 1.0 s 警告管（半径 200 的圆柱，长 60 m） | 沉默 8 s，暴露 2.5 s | `mp_ability_sonic_blast.nut` |
| L-18 | Ballistic 呼啸弹 | 锁定 RUI `targeting_rui`；目标标记 0.3 s → 常驻；射程脉冲 3000 | 5° 锥、锁住后 60° 视野内保持 | `mp_ability_debuff_zone.nut:279-342` |
| L-19 | Vantage 标记狙击 | 开镜 > 0.99 时 `vantage_sniper_info`（400 m、`crossDist`、目标等级）；标记 `P_van_sniper_mark` 10 s；下坠刻度不在脚本 [要截图] | 3.5° 追踪锥 | `sniper_recon_info.nut:571-780` |
| L-20 | Gibraltar 护罩 | 没有抛物线和预览；罐子上方 35 u 一个 ping | 1 s 展开、12 s、提前 5 s 警告 | `mp_weapon_bubble_bunker.nut` |

### L-21 – L-27 移动类技能（以前的阶段做过）

| # | 技能 | 界面 |
|---|---|---|
| L-21 | Pathfinder 钩爪 | 常驻射程准星（M-01），`count` 30 s |
| L-22 | 滑索枪 | 放置 RUI、射程脉冲、线预览（M-03） |
| L-23 | Octane Stim / 跳板 | Stim：镜头前粒子 + 开始结束闪屏，`bar`；跳板：`crosshair_mine`，没有抛物线和虚影 |
| L-24 | Wraith 传送门 / 虚空 | 传送门距离表是原生（状态效果 `placing_phase_tunnel` 严重度 = 1 − 距离 / 6000）[要截图]；提示 10 s；虚空：调色 + 屏幕粒子，结束前 1.5 s 警告 |
| L-25 | Valkyrie 喷气 / 天际 | 燃料条（M-02）；天际：起飞倒计时 1.6 s、高度 RUI、210 m 敌人标记 |
| L-26 | Ash 相位突破 | 射程圈 75 m（升级 100）、目标标记友方色、墙面箭头；无效时隐藏 + 提示 |
| L-27 | Vantage Echo | `crosshair_tac_range`；送达标记 2 s；发射线 |

---

## 6. 和 HSD 现在比（`combat/wp5-gun-page-models`，HSD-Unity #69）

HSD 的界面全在 IMGUI（`OnGUI`）：`CombatHud.cs`（命中、数字、血量、道具文字）、`ArsenalHud.cs`（扩散点圈、武器状态文字）、`SkillHud.cs`（屏幕染色、钻头 / Motherlode 文字）、`HsdHud.cs`（移动开关、跳板二段跳提示文字）、`PracticeGame.cs`（准星点、滑索提示、速度条、技能格）。技能的地面圈是 3D 网格（`CombatVisuals` 的圆柱）。工程里没有 uGUI 包，也没有用 UI Toolkit。

状态：**有** = 规则和 R5 一致；**占位** = 有东西但规则或样子不是 R5；**没有**；**HSD 加的** = R5 没有。

| # | 项 | HSD 现在 | 状态 |
|---|---|---|---|
| W-01 | 每把枪的准星 | 一个通用点，颜色跟钩爪状态 | 没有 |
| W-02 | 扩散显示 | `ArsenalHud.AimMarks`：下一发点 + 扩散角位置的 4 个点（真角度投影） | 占位（规则对，样子不对） |
| W-03 | 霰弹图案准星 | — | 没有（等 `shotgun-reticle`） |
| W-04 | 开镜瞄具 | 机瞄发光标记、光学瞄具画面都没有（`HeldModels`："No scope picture is built yet"） | 没有 |
| W-05 | 枪身弹量屏 | — | 没有 |
| W-06 | 右下武器 HUD | 文字 `[LMB] 名字 弹匣/容量` | 占位 |
| W-07 | 低弹量 / 换弹 / 换枪提示 | 文字 `reloading` / `swapping` / `drawing` | 占位；低弹量阈值、没备弹横幅没有 |
| W-08 | 蓄力 / 热量 / Energize | 文字百分比 | 占位；Sentinel 上膛点没有 |
| H-01 | 命中 X | 白色 X 0.15 s，击杀红 0.3 s | 占位；8 种类型和护盾图标没有 |
| H-02 | 命中声音 | 没找到 | 没有 |
| H-03 | 破盾 / 护盾受击 | — | 没有 |
| H-04 | 霰弹命中点 | — | 没有 |
| H-05 | 伤害数字 | 浮动式，每次 1 s，上升 30 u/s，白 / 爆头黄 / 击杀红 / 打自己红 | 占位（R5 默认是累加式） |
| H-06 | 受伤方向 | — | 没有 |
| H-07 | 受伤屏幕效果 | 受伤闪屏、低血量都没有；只有震撼、毒气、燃烧的屏幕染色（`SkillHud`） | 没有（染色是占位） |
| H-08 | 手雷 / 威胁指示 | — | 没有 |
| H-09 | 敌人血条 | — | 不做（原版没有） |
| H-10 | 训练点 | — | 没有（只有射击场用） |
| M-00 | 移动时没有界面 | HSD 有速度条（0–900 u/s）、姿态文字、滑索"X 上索"提示、跳板"2J"提示、悬挂按键提示 | **HSD 加的**（都是练习辅助） |
| M-01 | 钩爪射程准星 | 准星点变色 + 距离文字 | 占位 |
| M-02 | Valk 燃料条 | 条 + 文字（`JetsFuelBar`） | 占位 |
| M-04 | 翻越加速圈 | 有（B1，菜单开关） | 有（样子没对过截图） |
| L-01 | Valk 12 个圈 | 12 个圆柱，**排成 5 + 5 + 2**（`MissileSwarm.Targets`：5 列 × 最多 5 排取前 12） | 占位，排法错（R5 3 列 × 4 排） |
| L-02 | Motherlode | 圆柱圈 + 文字 "out of range / clear / blocked" | 占位（R5 用圈的颜色） |
| L-03 | 钻头 | 文字颜色蓝 / 黄 / 红（按记录 §3.3 的隐藏放置色） | 占位（R5 看到的是白→黄→橙文字） |
| L-04–L-20 | 其他技能 | 大多有 3D 圆柱或柱子代表区域 | 占位 |
| 通用 | 抛物线 | 有（`CurrentArc`，菜单可关） | 占位（颜色不按技能） |
| 通用 | 底部技能栏 | 技能格带冷却填充（`NormalHud`）+ 文字 `next 4.2 s` | 占位（格数规则没对） |
| 通用 | 放置虚影有效 / 无效 | — | 没有 |

---

## 7. 还要在本地 R5 实测的（[要截图] 的项）

这次没测：R5 锁被 `shotgun-reticle` 持有（12:36 起）。测法沿用以前的：引擎 `screenshot` 命令，不用鼠标和焦点（`tools/ui_rt.py`，`research/combat/gun-measure/iron-sights/tools/sl.py` 同法）。射击场默认关了 X 和霰弹点，要么打开"显示命中标记"，要么用非射击场模式。

| # | 测什么 | 场景 | 回答 |
|---|---|---|---|
| S-1 | 每类准星的样子和扩散系数 | 每类一把枪；站、蹲、走、冲刺、空中；连射 10 发后；开镜 0.3 / 0.6；同时记 `GetAttackSpreadAngle()` | W-01、W-02 公式 |
| S-2 | 命中 X 每种类型 | 打 2 级护甲假人：护盾、破盾那一枪、肉身、爆头、击杀；远距离（无效） | H-01、H-03 |
| S-3 | 霰弹命中点 | **交给 `shotgun-reticle`** | H-04、W-03 |
| S-4 | 累加数字 | 每个护盾等级、暴击、破盾动画、停手后的淡出 | H-05 |
| S-5 | 受伤方向和闪屏 | 服务端 `TakeDamage` 从左、右、后；伤害 10 / 50 / 100 | H-06、H-07 |
| S-6 | 低血量 | 100 / 75 / 50 / 25 % | H-07 |
| S-7 | 右下 HUD、低弹量、没备弹 | R-301 满 / 6 发 / 0 / 换弹中；每种弹药 | W-06、W-07、颜色 |
| S-8 | Energize、热量、蓄力 | Sentinel 三态、Nemesis 0 / 50 / 100 %、Charge Rifle、L-STAR 过热 | W-08 |
| S-9 | Valk 圈数 | 平地俯视，普通和升级 | L-01 |
| S-10 | 底部技能栏 | 战术充能中 / 就绪 / 空按；大招 0 / 50 / 95 / 100 %；多格（电网）；bar（Stim） | 通用 |
| S-11 | 钩爪准星 | 射程内 / 外 / 冷却 | M-01 |
| S-12 | Fuse、钻头、电网、虚影 | 绿 / 橙 / 红；薄墙 / 厚墙；连线；有效 / 无效 | L-02、L-03、L-09 |
| S-13 | 反面检查 | 看着滑索（地面、空中）、跳板起飞、滑铲、二段跳 | 确认 M-00 |

## 8. 出处

- R5 脚本和字段：`research-src/s21-platform`（Flowstate S21，和安装目录脚本一致，只差换行）。
- 原生：`ghidra-projects/r5apex.gpr`（`r5apex.exe` sha256 3f44bf9a…）：ConVar 默认值（`DumpConVarRegistrations.java`）、`GetWeaponMissileMultipleTargets` 的网格循环。反编译内容没进公开仓库。
- 生成的表：`data/ui-crosshair.tsv`、`data/ui-reticles.tsv`、`data/ui-crosshair-mods.tsv`（`tools/xhair.py`）。
- HSD：HSD-Unity `combat/wp5-gun-page-models` 8470d65。
- 原始笔记：HSD-RawData `research/ui/notes/`（三份，含本机路径）。
