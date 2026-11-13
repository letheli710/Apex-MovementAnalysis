# 泰坦共用动作：拳、电烟、核弹弹射（从文件读出的规格，11-13）

11-13 `tf2-kits-measure` 读文件写成（[file] 部分）；同一天的私服实测在 [T-b-TITAN-VS-INFANTRY.md](T-b-TITAN-VS-INFANTRY.md) §6.6：拳平视打不中、低头 15° 以上打中、0.30 s 出伤；电烟 0.97 s 起 40 跳、泰坦 45 / 步兵 5 每跳、中心在前方 140 u 离地 84 u；核弹 11 次（3.27 – 4.47 s）、生效内半径 350（不是 500）、天花板下铁驭会被自己炸死。下文"要实测的"里第 2、3、5、7、10、11 项已由实测回答。

**先说结论（给人读）：**

- **拳**：多人 500 伤害（对人、对泰坦一样），距离 280，锥 20°，挥拳 0.8 s。找目标是原生函数"从眼睛出发、视锥里看得见的实体"，脚本只排除自己、队友、相位中、正被处决的目标，**不排除冻结或无 AI 的 NPC**。11-08 实测一次都没打中冻结步兵，文件给出的最可能原因是**几何**：泰坦眼高 185，视线水平时，20° 的锥在 150–280 u 处的下沿还在离地 84–131 u，而步兵只有约 72 u 高，整个人都在锥下面。要低头 25–40° 才打得到。
- **电烟**：多人用的是 `mp_titanability_electric_smoke`（核心槽满 20 % 时发 1 发，Counter Ready 多 1 发），效果和单人的 `mp_titanability_smoke` 走同一段脚本。放在泰坦正前方 140 u、离地 84 u 的点，1.0 s 后开始伤害，每 0.1 s 一跳，到 5 s 结束；内半径 320、外半径 375；对铁驭 45 /s，对泰坦 450 /s（Maelstrom 90 / 1350）。自己和队友受到的伤害被脚本清零。
- **核弹弹射**（Nuclear Ejection = `pas_build_up_nuclear_core`）：只有**濒死**时弹射才会触发。按下后约 1.75 s 铁驭被弹出，速度 1900–2100（再乘 √0.8），约 1.45 s 后开始爆炸；一共 11 次，每 0.1 s 一次，每次对铁驭 75、对泰坦 2500，内半径 350、外半径 750（第一次是 600、对泰坦 0）。贴脸的泰坦一共吃 25000。队友免伤；自己没有免伤，但这时铁驭已经在约 1800 u 的高空。

本页不重复的内容：拳 / 剑的完整数值表、踩人、dash 撞人、AI 泰坦近战见 [T-b-TITAN-VS-INFANTRY.md](T-b-TITAN-VS-INFANTRY.md) 第 3、6.5 节；踩人原生规则见 `ref-native-tail/REF-NATIVE-1112.md`（分支 `ref/native-tail`） §6；Monarch 电烟的 FD 升级、Maelstrom 怎么发到身上见 `kits/MONARCH.md`（`:332, :349, :411, :414`）。

**出处缩写**（全部在 `TF2-Research/local/vpk/` 下，除 NS）：

| 缩写 | 路径 |
|---|---|
| WT | `client_mp_common/scripts/weapons/` |
| V | `client_mp_common/scripts/vscripts/`（多人共用脚本） |
| SV | `client_sp_training/scripts/vscripts/`（零售服务端脚本，含 MP 分支） |
| FE | `client_frontend/scripts/vscripts/`；`FE-R` = `client_frontend/resource/` |
| DD | `client_mp_common/scripts/damage/damagedefs.txt` |
| P | `client_mp_common/scripts/players/mp/` |
| NS | `C:\SteamLibrary\steamapps\common\Titanfall2\R2Northstar\mods\Northstar.CustomServers\mod\scripts\vscripts\` |

标记：[file] 文件里直接写着；[原生] 由引擎代码决定，脚本里看不到；[推断] 根据文件推出来的，没实测。

---

## 1. 泰坦拳打步兵

### 1.1 武器数值（`melee_titan_punch*.txt`，取多人值）

| 项 | 值 | 出处 |
|---|---|---|
| 伤害：对人 / 对重甲（泰坦） | 500 / 500 | WT/`melee_titan_punch.txt:45–46` [file] |
| 距离 `melee_range` | 280（战役 260） | `:32`（战役 `:24`） [file] |
| 锥角 `melee_angle` | 20（战役 30）；是半角还是全角 **不确定** [原生] | `:36`（战役 `:28`） |
| 能打人形 / 能打泰坦 | 1 / 1 | `:40–41` [file] |
| 挥拳动作 / 收回 | 0.8 s / 1.0 s | `:42–44` [file] |
| 打中后定格视角 | 0.25 s | `:50` [file] |
| 伤害标志 | `DF_MELEE | DF_GIB`（打人另加 GIB，见下） | `:53` [file] |
| `impulse_force` | 1000000（物理冲量；对人的实际击退由脚本另给，见 1.3） | `:55` [file] |
| 骑乘伤害 `damage_rodeo` | 100 | `:81` [file] |
| 攻击帧时刻 | **文件里没有**。脚本靠动画事件 `CodeCallback_OnMeleeAttackAnimEvent` 被引擎调用 | V/`melee/sh_melee.gnut:992–1007` [原生] |
| 前冲 | 没有（注释 "Titan melee script doesn't lunge"） | WT/`melee_titan_punch_fighter.txt:9–10` [file] |

**七个变体：** `_ion / _legion / _northstar / _scorch / _tone / _vanguard` 都只 `#base melee_titan_punch.txt` 再换声音，没改数（各文件 `:1–15`）[file]。`_fighter` 不一样：换了电拳模型，锥 MP 20 / SP 45，`pushback_scale 0.3`（打泰坦的推力 × 0.3），`melee_lunge_time 0.2`（`_fighter.txt:9–23`）[file]。`_fighter` 给谁用 **不确定**（SP 角度 45 像是战役 BT 用的 [推断]）。

**`berserker` mod**（多人拿不到 [推断]）：动作 1.23 s、收回 0.77 s、对重甲 5000、距离 300、加 `DF_EXPLOSION | DF_CRITICAL | DF_KNOCK_BACK | DF_DOOM_FATALITY`（`melee_titan_punch.txt:143–158`）[file]。

### 1.2 找目标的流程（脚本）

按键 → `CodeCallback_OnMeleePressed`（V/`melee/sh_melee.gnut:365–419`）：要 `playerAllowedToMelee`、武器没被禁、当前不在近战状态、活着 → 泰坦走 `TitanUnsyncedMelee`（`:421–426`）。

`TitanUnsyncedMelee`（V/`melee/sh_melee_titan.gnut:17–48`）：永远是普通拳 `PLAYER_MELEE_STATE_TITAN_MELEE_JAB`（`:26`），`PlayerMelee_StartAttack` 交给引擎播动作。

动作里的攻击事件到来时，引擎调 `CodeCallback_OnMeleeAttackAnimEvent`（`sh_melee.gnut:992–1007`）→ `TitanMeleeAttack`（`sh_melee_titan.gnut:79–218`）。这个回调在攻击窗口里可能**每帧**被调用 [推断]，脚本用下面第 1 步保证只打一次：

1. 本次挥拳已经打到过东西（`PlayerMelee_GetAttackHitEntity()` 非空）→ 直接返回（`:87–88`）。处决中、相位中也返回（`:89–92`）。
2. `PlayerMelee_FindVisibleEntitiesInCone( titan )` 取锥里"看得见"的实体（`:105`）[原生]。起点是 `titan.EyePosition()`（`:102`），距离、锥角来自武器的 `melee_range / melee_angle` [推断：函数没有别的参数]。"看得见"怎么判（中心点、包围盒还是 hitbox，用哪种追踪掩码）**不确定** [原生]。作对比：武器通用代码调 `FindVisibleEntitiesInCone` 时会显式传 `VIS_CONE_ENTS_TEST_HITBOXES`（V/`weapons/_weapon_utility.nut:528`），近战版本看不到参数。
3. 对每个结果做 `CodeCallback_IsValidMeleeAttackTarget`（`sh_melee.gnut:316–363`）：排除自己、同队、相位中、骑乘时自己骑的泰坦正在 embark 的铁驭、挂在自己身上的、正在被处决的；`CanBeMeleed` 对所有玩家和 NPC 都返回 true（`:657–668`）。**没有任何"冻结 / 无 AI / 被动"相关的判断** [file]。
4. 一帧里锥中所有合法目标**全部**挨打（`foreach`，`:106–176`）。人形（`IsHumanSized`：玩家铁驭、身体类型 `human` / `marvin` 的 NPC、小炮塔，V/`_utility_shared.nut:3514–3530`）走 `TitanAttackHumanSized`；泰坦走 `TitanAttackTitan`；其他 NPC 走 `TitanAttackDefault`。
5. 锥里**一个合法目标都没有**时，沿视线打一条 280 u 的只撞世界的线（`TRACE_MASK_SOLID_BRUSHONLY`，`:185–188`）；撞到墙 / 地就记成"打中了世界"并 `SetAttackHitEntity`（`:189–199`）——**之后这次挥拳的后续帧全部作废**（回到第 1 步）。
6. 涡旋挡近战：playlist 变量 `vortex_blocks_melee` 默认 0，不挡（`:122–136`）[file]。

### 1.3 对步兵 / 铁驭的效果

| 项 | 值 | 出处 |
|---|---|---|
| 伤害 | `GetDamageAmountForArmorType`：人 500 | `sh_melee_titan.gnut:259` [file] |
| 碎尸 | 目标 `IsHuman()` 或 prowler 时加 `DF_GIB` | `:233–234, 395–403` [file] |
| 击退 | 速度 **+800 u/s**，方向沿泰坦视线（含俯仰）；若和"泰坦→目标"方向相反就翻转 | `:236–240, 260` [file] |
| 伤害源 | 武器名对应的编号；有 PAS_SHIFT_CORE（Ronin 剑核心）时改为 `mp_titancore_shift_core` | `:255–258` [file] |
| 被骑乘的铁驭 | 打到骑在别的泰坦身上的铁驭，会去掉友军骑乘保护 | `:241–247` [file] |
| NPC 静音 | 被打碎的步兵不惨叫（`silentDeath`） | `:249–253` [file] |
| 打中力度反馈 | 打到敌方泰坦 1.0、打世界 0.5、打其他 0.2 | `:202–216` [file] |

对泰坦（对照，T-b 已写）：推力 510（剑 400 / 剑核心 100），最低保底 0.85 倍，+100 向上，再限制竖直速度；自己被反推同样大小的水平速度；对方正在出拳会被打断（`:264–345`）[file]。

### 1.4 为什么 11-08 冻结步兵一次都没打中

11-08 的情况（`tf2/runtime/data/20261108_142447_kit_d/plan.gnut:126–193`）：步兵 `hsd_npc soldier static` 在 z = 7，泰坦在 z ≈ 1、视角全 0（`hsd_setup -800 -1400 7 0 0 0 0 0`）；按 `+melee` 0.1 s。`diag.tsv` 里 `KIT` 行在 97.42–98.12 s 显示当前武器是 `melee_titan_punch_ion`，**说明拳确实挥出去了**，只是没打中。`static` 的实现是 `npc.Freeze()` + `NPC_IGNORE_ALL | NPC_DISABLE_SENSING` + 收走枪（NS 上的 `HSD.TF2Diag/.../hsd_diag_npc.gnut:103–128, 148–155, 237–259`）。

可能原因，按可能性排序：

1. **几何：步兵在锥的下面**（最可能）[推断]。泰坦站姿眼高 185（P/`titan_base.set:171`，各底盘的 `.set` 没覆盖这项）；步兵高约 72（铁驭站姿 `hull_max` z = 72，P/`pilot_base.set:255`；步兵 NPC 的盒没查，按同高估）。视线水平时，假设 20° 是**半角**，锥的下沿在距离 d 处的高度是 186 − d·tan20°：

   | 距离 | 150 | 250 | 280 |
   |---|---|---|---|
   | 锥下沿离地 | 131 | 95 | 84 |
   | 步兵头顶 | 79 | 79 | 79 |

   三处步兵都完全在锥下面。如果 20° 是全角（半角 10°），差得更远。所以文件层面不需要"冻结的 NPC 被排除"也能解释 0 命中。实际玩的时候，铁驭贴着泰坦，玩家自然会低头。
2. **"看得见"的判法和冻结有关**（可能性较低）[原生, 不确定]。如果原生函数测 hitbox，而 `Freeze()` 停了动画、hitbox 没更新 / 不参与，就会漏掉。脚本层面没有排除冻结 NPC 的代码。
3. **低头太多会打到地面**（这次不是原因，但是设计实测时的坑）[推断]。锥里没目标时沿视线打 280 u 的线；眼高 185，俯角 ≥ asin(185/280) ≈ 41° 时这条线会撞到地面，挥拳被记成"打中世界"，后面的帧不再找目标（`sh_melee_titan.gnut:87–88, 185–199`）。所以测的时候俯角最好 < 40°。
4. 队伍：脚本排除同队（`sh_melee.gnut:327–328`）。同一轮踩人能伤到这些步兵，踩人跳过友军（REF-NATIVE-1112 §6），所以步兵是敌方 [推断]，可以排除。

### 1.5 私服实测建议

都用 `hsd_npc`，先 `static`，再用 `idle`（不冻结、不开枪）做对照。眼点 z ≈ 186，步兵胸口 z ≈ 52（Δz ≈ 134）。

| # | 摆法 | 视角俯仰（向下为正） | 想回答什么 |
|---|---|---|---|
| A | 步兵 250 u 正前方，地面 | 0（对照，应该打不中） | 复现 11-08 |
| B | 同 A | 28°（正对胸口：atan(134/250)） | 低头能不能打中冻结步兵 → 证实原因 1 |
| C | 步兵 150 u | 35°（胸口在 42°，看锥半角是否 ≥ 7°） | 锥的大小 |
| D | 步兵 250 u，站在 120 u 高的箱子上（胸口 z ≈ 172，几乎平视） | 0 | 不低头也打中 → 几何原因确认；打不中 → 怀疑原因 2 |
| E | 同 B，但 `idle` 步兵 | 28° | 冻结 / 不冻结有没有差别 |
| F | 步兵 250 u，俯仰固定 28°，水平偏 0 / 10 / 15 / 20 / 25° | 28° | 20 是半角还是全角 |
| G | 没有目标，俯仰 30 / 40 / 45° | — | 打地面的反馈（震动强度 0.5）从多少度开始出现 |
| H | 步兵 280 / 300 / 320 u，俯仰按胸口算 | 25° 左右 | 280 量到中心还是包围盒 |

记：伤害源 143–150（T-b §6 的表）、伤害值 500、步兵受伤后一帧的速度（≈ 800 沿视线）。**攻击窗口时刻**：服务端每次调用动画事件都会 `print( "SERVER: ... is calling CodeCallback_OnMeleeAttackAnimEvent()" )`，按键时也有 `"SERVER: ... pressed melee"`（`sh_melee.gnut:368, 996`）。把服务端控制台日志带时间戳录下来，两条之间的时差就是攻击帧时刻，调用次数就是窗口有几帧 [推断：`print` 会进 Northstar 日志，要确认]。

---

## 2. 电烟（Electric Smoke）

### 2.1 多人用哪个武器

多人泰坦身上的电烟是 **`mp_titanability_electric_smoke`**（`CORE_SMOKE_WEAPON`，V/`earn_meter/sh_earn_meter.gnut:30`），不是 `mp_titanability_smoke`。两个文件的 `OnWeaponPrimaryAttack` 都是 `OnWeaponPrimaryAttack_titanability_smoke`（WT/`mp_titanability_electric_smoke.txt:19`；WT/`mp_titanability_smoke.txt:17`），所以**效果完全一样**，只是发放和次数不同 [file]。`mp_titanability_smoke` 是可充能的战术技能（100 一发、每秒回 5，即 20 s；`mp_titanability_smoke.txt:44–52`），多人是给 NPC 泰坦和战役用的 [推断：多人脚本只发 electric 版]。

| 项 | `mp_titanability_electric_smoke`（多人） | 出处 |
|---|---|---|
| 类型 | `weaponType "inventory"`，`offhand_instant` | WT/`mp_titanability_electric_smoke.txt:16–17` [file] |
| 槽位 | `OFFHAND_INVENTORY` | SV/`earn_meter/sv_earn_meter.gnut:474–485` [file] |
| 弹药 | 弹匣 1、默认 1、每发 1、库存上限 4；`ammo_no_remove_from_clip 1` | `:44–50` [file] |
| 回充 | `regen_ammo_refill_rate 5` 写着，但实际次数由脚本加减（见 2.4）；会不会自己回 **不确定** | `:53–54` |
| mod | 只有空的 `maelstrom` | `:70–76` [file] |
| 武器文件里的伤害键 | 爆炸 100 / 250、半径 50–120、近远 900——**都不用**，伤害由 `smokescreen.nut` 的 `RadiusDamage` 给 [推断：电烟不发射弹体] | `:31–42` |

### 2.2 伤害和形状

`TitanSmokescreen`（V/`weapons/mp_titanability_smoke.nut:63–123`）填参数，交给 `Smokescreen`（SV/`superbar/smokescreen.nut:80–121`）。NS 的 `superbar/smokescreen.nut` 和零售 `diff -w` 只差换行 [file]。

| 项 | 值 | 出处 |
|---|---|---|
| 每秒伤害：对铁驭 / 对泰坦 | **45 / 450** | `mp_titanability_smoke.nut:95–96` [file] |
| Maelstrom（Monarch 第 5 级 core） | 90 / 1350 | `:86–92` [file] |
| 跳间隔 | 0.1 s；每跳 = 每秒值 × 0.1 → 铁驭 4.5、泰坦 45（Maelstrom 9 / 135） | `smokescreen.nut:185–188` [file] |
| 4.5 这种小数会不会被截成 4 | **不确定**（`RadiusDamage` 的伤害参数类型）[原生] | `:221–233` |
| 生效延迟 | 1.0 s（结构默认 2.0，泰坦电烟改成 1.0） | `mp_titanability_smoke.nut:98`；`smokescreen.nut:36, 209` [file] |
| 持续 | 5.0 s（`lifetime` 默认）；伤害循环条件是"从放出算起 ≤ 5 s"，所以伤害在 1.0–5.0 s，约 41 跳 [推断：服务器帧对齐可能是 40] | `smokescreen.nut:17, 184, 211` |
| `burn_mod_titan_smoke` | 持续 12 s（多人拿不到 [推断]） | `mp_titanability_smoke.nut:66–72` |
| 内 / 外半径 | **320 / 375**（结构默认 320 / 350） | `mp_titanability_smoke.nut:84–85`；`smokescreen.nut:37–38` [file] |
| 衰减 | 320 内满额，320–375 衰减到 0；衰减形状（线性？）[原生] | `smokescreen.nut:227–228` |
| 遮挡 | `SF_ENVEXPLOSION_MASK_BRUSHONLY`：只有世界几何挡伤害 [推断：按旗标名] | `:229` |
| 伤害标志 | `DF_ELECTRICAL | DF_NO_HITBEEP`，冲量 0 | `:230–232` [file] |
| 伤害源 | `mp_titanability_smoke` | `:27` [file] |
| 满打满算 | 铁驭站在内半径里 1.0 s 后约 2.2 s 死（100 血 / 45）；泰坦整段约 1845（Maelstrom 约 5535）[推断] | — |

### 2.3 放在哪里

| 项 | 值 | 出处 |
|---|---|---|
| 朝向 | 只取眼睛的 yaw（俯仰、横滚 0） | `mp_titanability_smoke.nut:100–101` [file] |
| 基点 | 泰坦原点 + 前方 240 u；从眼睛到这点的线被挡住 → 改用泰坦原点 | `:103–109` [file] |
| 5 团烟的偏移（前、右、上） | (−200, 0, 20)、(0, 200, 20)、(0, −200, 20)、(0, 0, 148)、(−200, 0, 148) | `:111–120` [file] |
| 伤害中心 | 5 团的包围盒中心 = 基点 + (−100, 0, 84) → **泰坦前方 140 u、离地 84 u**；被挡时变成**泰坦后方 100 u** | `smokescreen.nut:150, 175` [推断：按代码算出] |
| 挡视线体积 | 一个跟着朝向的盒（5 团的范围外扩 230·0.707 / 170·0.707，再 × 0.9），存在到 4.5 s | `:152–156, 239–246, 286–291` [file] |
| "在烟里"的球半径 | 中心到最远一团 232.6 + 230 ≈ 463 u（给 AI / 别的系统查） | `:158–176, 320–346` [推断：按代码算出] |
| 不刷新区 | 半径 463 + 240 ≈ 703 u，持续 5 s | `:103` |
| 敌方铝热剂 | 范围内敌方的铝热剂火被直接删掉 | `:85–92` [file] |
| AI 危险区 | 半径 = 外半径 375，AI 会躲 | `:196–200` [file] |

**骑在背上的敌方铁驭** [推断]：泰坦盒高 235（P/`titan_base.set:174`），背上的铁驭离伤害中心约 200–250 u，在 320 的内半径里，吃满额。这就是"反骑乘"用途（HUD 提示 `#RODEO_ANTI_RODEO_SMOKE_HINT`，V/`client/cl_main_hud.nut:521–539`）。

### 2.4 自己、队友

- 多人友军保护对电烟**不生效**（`DamageIgnoresFriendlyFire` 把 `mp_titanability_smoke` 列为例外，注释说是为了 FD 的回盾，SV/`mp/_base_gametype.gnut:285–302`），所以同队目标也会收到伤害事件 [file]。
- 但两个伤害回调都把**同队**的伤害设成 0：所有玩家 / NPC（`smokescreen.nut:349–360`）；泰坦（`mp_titanability_smoke.nut:125–175`）[file]。自己算同队 → 自己不掉血 [file]。
- FD：主武器带 `fd_vanguard_utility_1` 时自己在烟里每跳 +35 护盾；带 `_2` 时队友泰坦也加（`mp_titanability_smoke.nut:142–155`）；烟换成治疗特效（`:74–77, 182–193`）[file]。细节见 MONARCH.md `:411, :414`。

### 2.5 次数从哪来

| 项 | 值 | 出处 |
|---|---|---|
| 发放时机 | 核心槽从 < 20 % 涨到 ≥ 20 % 时发一次 | SV/`earn_meter/sv_earn_meter.gnut:454–468`；`CORE_SMOKE_FRAC 0.20`（V/`earn_meter/sh_earn_meter.gnut:29`） [file] |
| 调用处 | 泰坦给出 / 吃到伤害、核心槽涨时 | SV/`titan/_titan_health.gnut:1005–1023` [file] |
| 开关 | `ANTI_RODEO_SMOKE_ENABLED`：多人 true、战役 false | FE/`sh_consts_mp.gnut:8`；SV/`sh_consts_sp.gnut:8` [file] |
| 默认一次给几发 | 1（新给武器时 `ammo_default_total 1`）；已有武器时 +1 | `sv_earn_meter.gnut:474–488` [file] |
| Counter Ready（`pas_anti_rodeo`） | 新给武器时 +1（共 2）；已有时 +2 | `:473–489`；FE/`sh_passives.gnut:232`；名字 / 说明 "Counter Ready" / "1 extra Electric Smoke countermeasure."（FE-R/`r1_english.txt:2707–2709`） [file] |
| 什么时候槽满 20 % 又会再来 | 核心用完后：普通情况核心槽归 0，再涨过 20 % 时又发；`pas_hyper_core` 用完核心后直接设到 20 % 并立刻发一发 | V/`weapons/sh_titancore_utility.gnut:219–240` [file] |
| 用完 | 库存 0 时把 `OFFHAND_INVENTORY` 的武器拿掉 | `mp_titanability_smoke.nut:39–42` [file] |
| Maelstrom | 升级那一刻身上有电烟才加 mod；以后新发电烟时若 `upgradeCount ≥ 2` 且有 core5 再补 | V/`weapons/mp_titancore_upgrade.nut:127–142`；`sv_earn_meter.gnut:490–496` [file] |
| NS 改动 | 进泰坦时把耳计奖励换成 `core_electric_smoke`（20 %），核心已过 20 % 就标记已用 | NS/`earn_meter/sv_earn_meter_mp.gnut:158–166` [file] |

**按键**：`OFFHAND_INVENTORY` 在 HUD 上是 dpad 左那一格（SV/`client/rui/cl_weapon_status.gnut:289, 297, 406–439`）；PC 默认键 **不确定**（`bind` 在引擎配置里，没查）。

---

## 3. 核弹弹射（Nuclear Ejection）

### 3.1 是哪个被动、什么时候生效

- 装备名 "Nuclear Ejection"，说明 "Ejecting while doomed nukes your Titan"（FE-R/`r1_english.txt:2879–2882`）[file]。
- 对应被动 `pas_build_up_nuclear_core` → `PAS_BUILD_UP_NUCLEAR_CORE`（FE/`sh_passives.gnut:56, 158, 251`）[file]。脚本注释 "regular nuke: PAS_BUILD_UP_NUCLEAR_CORE"（V/`titan/sh_titan.gnut:955`）。
- `PAS_NUCLEAR_CORE`（payload +2，"super nuke"）在枚举里有（FE/`sh_passives.gnut:34`），但没有字符串名，玩家装不上 [推断]。
- **只有濒死（doomed）时才是核弹**：`GetNuclearPayload` 不在濒死就返回 0（V/`_utility_shared.nut:1136–1149`）[file]。满血弹射是普通弹射。
- `mp_titanability_nuke_eject`（WT/`mp_titanability_nuke_eject.txt`）不是这个被动：它是一个只在客户端发 `TitanEject 3` 的副手（FE/`burnmeter/sh_burnmeter.gnut:454–464`），文件里伤害全 0 [file]。

### 3.2 时序

时间从"弹射确认"（引擎处理完三连按）算，`L` = 玩家延迟（最多算 0.4）。

| 段 | 时长 | 累计 | 发生什么 | 出处 |
|---|---|---|---|---|
| 0 | — | 0 | 泰坦无敌、冻结操作；站姿播 `at_nuclear_eject_standing`（蹲姿仍用普通蹲姿弹射动作）；蓝色警告光挂在胸口 `CHESTFOCUS`；对别的玩家震屏（750 u 内 5，1500 u 外 0，持续 8.5 s，频率 40）；建 AI 危险区 | V/`titan/sh_titan.gnut:449–450, 471–495, 505–532, 548–564, 387` [file] |
| 1 | 0.15 | 0.15 | 等动作混合 | `:541, 566` [file] |
| 2 | 1.6 − 0.4 = 1.2 | 1.35 | 核弹弹射时长 = 普通 0.8 × 2 | `:317–319, 497–501, 569` [file] |
| 3 | 0.4 − L | ≈ 1.75 − L | 延迟补偿 | `:571–578` [file] |
| 4 | 弹出 | — | 换成自动泰坦（无敌、AI 不当威胁、卡在地形里时临时不挡玩家）；铁驭被抛出 | `:593–711` [file] |
| 5 | 0.15 | ≈ 1.9 − L | 开始 `NuclearCoreExplosion` | `:725–731` [file] |
| 6 | 1.3 | ≈ 3.2 − L | 播爆炸声，泰坦 `Die`，开始连爆 | `:880–891` [file] |
| 7 | 11 次 × 0.1 s | 第 1 次 ≈ 3.2 − L，第 11 次 ≈ 4.2 − L | 见 3.3 | `:954–958, 967, 982–983, 1006–1040` [file] |

普通弹射对照：段 2 = 0.4 s（弹出约 0.95 − L），弹出后 0.15 s 一次爆炸：对人 1、对泰坦 1800、半径 100–300、不伤自己（`SF_ENVEXPLOSION_NO_DAMAGEOWNER`）（`:742–755`）[file]。

**中途被打断**（例如铁驭在动作中死了）：在泰坦当前原点（不加 200）照样起核爆（`:416–425`）[file]。

### 3.3 爆炸伤害

| 项 | 值 | 出处 |
|---|---|---|
| 爆心 | 弹出时自动泰坦的原点 + (0, 0, 200) | `sh_titan.gnut:616, 727` [file] |
| 次数 | 10 次伤害爆炸 + 开头 1 次"额外"的 = **11** | `:956, 982–983` [file] |
| 间隔 | 1.0 / 10 = 0.1 s | `:958, 967, 1039` [file] |
| 第 1 次 | 对人 75、对泰坦 **0**、内 350、外 **600**（注释：给物理物体的） | `:981, 1013–1018` [file] |
| 第 2–11 次 | 对人 **75**、对泰坦 **2500**、内 **350**、外 **750** | `:921–922, 957, 1019–1022` [file] |
| 累计（内半径里） | 对泰坦 25000；对人 825（100 血铁驭两下就死） | [推断] |
| 伤害定义 `damagedef_nuclear_core` | 75 / 2500、内 500、外 750、冲量 0、`DF_RAGDOLL | DF_EXPLOSION`、没写 `explosion_flags` | DD:`39–50` [file] |
| 脚本传 350、定义写 500，哪个生效 | **不确定**；`RadiusDamage_DamageDef` 显式传了内外半径和伤害，估计用传入值 [推断 / 原生] | `sh_titan.gnut:1029–1037` |
| 衰减形状 | [原生]，按 RadiusDamage 惯例内半径满额、到外半径降到 0 [推断] | — |
| 护盾 | 定义里没有 `DF_BYPASS_SHIELD`（对比降落砸人有），应先打护盾 [推断] | DD:`49, 63` |
| 攻击者 | 优先 `soul.nukeAttacker`（被迫弹射时），否则弹射的玩家 | `:370, 1042–1049` [file] |
| 核心能量 | 核弹伤害不给攻击者涨核心槽 | SV/`mp/_codecallbacks.gnut:569–591`（`case damagedef_nuclear_core: return false`，`:587`） [file] |
| 受击方向提示 | 伤害原点随机抖动 300 u + 抬高 128 | SV/`mp/_codecallbacks.gnut:644–650` [file] |
| NS 撤离飞船 | 核弹伤害乘 `EVAC_SHIP_DAMAGE_MULTIPLIER_AGAINST_NUCLEAR_CORE` | NS/`evac/_evac.gnut:277, 634–639` [file] |
| NPC 泰坦核弹（payload 4，对照） | 3 次、1.5 s、每次伤害 × 10/3、内 350，没有额外那一次 | `sh_titan.gnut:926–936` [file] |

### 3.4 弹射本身

| 项 | 值 | 出处 |
|---|---|---|
| 速度 | 1500–1700 随机，核弹 **+400** → 1900–2100；深水再 +1000 | `sh_titan.gnut:660–665` [file] |
| 乘重力系数 | × √gravityscale；铁驭 0.80 → × 0.894 → 核弹 **1699–1878 u/s** | `:698–699`；P/`pilot_mp.set:10` [file] |
| 方向 | 俯仰 270（竖直向上）再合成 −5° → 偏离竖直 5°（向前还是向后 **不确定**）；带 Phase Eject 时 315 且速度减半 | `:656–658, 690–696` |
| 铁驭视角 | 俯仰设 80（几乎向下看） | `:702–704` [file] |
| 空中控制 | 1.5 s 内 airSpeed 200 / airAcceleration 800，之后 airSpeed 100 再 3.5 s | `:1104–1117` [file] |
| 起点 | 安全点，泰坦原点 + 60 附近 | `:653` [file] |
| 骑乘者 | 被甩开：速度 × gravityscale × 0.95，方向再偏 5°；双方临时不碰撞 1.5 s | `:669–685, 825–841` [file] |
| 爆炸时铁驭多高 | 弹出后约 1.45 s：h = v·t − ½·g·t²；g = 750 × 0.8 = 600 [推断：`sv_gravity` 750 没在文件里查到] → 约 1830–2090 u，比爆心高约 1700 u，远在 750 外 | [推断] |

### 3.5 对自己和队友

- **自己**：多人没有"自伤保护"（`IsProtectedFromFriendlyFire_MP` 第一行 `attacker == ent → false`，SV/`mp/_base_gametype.gnut:206–210`），定义里也没写 `NO_DAMAGEOWNER`（DD:`39–50`）→ 铁驭如果被天花板挡住没飞高，会被自己的核弹炸死 [推断]。无敌只到弹射线程结束后 0.35 s（`sh_titan.gnut:397–403, 1058–1074`），赶不到爆炸。正常情况铁驭已经在高空，碰不到。
- **队友**：同队且目标的 owner / boss 不是攻击者 → 受保护（`_base_gametype.gnut:212–219`）；核弹不在 `DamageIgnoresFriendlyFire` 的例外里（`:285–302`）→ **队友免伤** [file]。
- **自己的泰坦**：它本身在 `Die`（`sh_titan.gnut:891`），而且是无敌的（`:622`），不算 [file]。

---

## 4. 要实测的

| # | 项 | 为什么脚本给不了 | 怎么测（Northstar 私服） |
|---|---|---|---|
| 1 | 拳的锥：20° 是半角还是全角；"看得见"按中心 / 包围盒 / hitbox | `PlayerMelee_FindVisibleEntitiesInCone` 是原生 | 1.5 节 B / C / F / H |
| 2 | 冻结步兵打不中的真正原因 | 同上 | 1.5 节 A / B / D / E |
| 3 | 拳的攻击帧时刻、窗口有几帧 | 动作事件来自模型动画 | 服务端日志里 `pressed melee` 到 `calling CodeCallback_OnMeleeAttackAnimEvent()` 的时差和次数 |
| 4 | 俯角多少开始"打地面"（≈ 41°） | 推算 | 1.5 节 G |
| 5 | 电烟每跳实际伤害（4.5 还是 4）、一共几跳（40 还是 41） | `RadiusDamage` 原生 | 铁驭 / 步兵 / 泰坦靶子站在烟中心，记每跳伤害和时刻；靶子血调高 |
| 6 | 电烟 320–375 的衰减形状、是不是 3D 球、高处的目标算不算 | 原生 | 靶子放在中心水平 300 / 330 / 350 / 370 / 380 u；再放在中心正上方 200 / 330 u |
| 7 | 电烟中心是不是真的在前方 140、高 84；前方被挡时是不是跑到身后 100 | 推算 | 对着墙 / 空地各放一次，靶子排一列看谁受伤 |
| 8 | 电烟对自己、队友、骑在背上的敌方铁驭 | 脚本已清零同队；骑乘距离是推算 | 敌方铁驭骑上来放烟；队友站在烟里 |
| 9 | Counter Ready 的总发数、`regen_ammo_refill_rate 5` 会不会让它自己回 | 发放是脚本加减，回充是原生 | 带 / 不带 Counter Ready，看 HUD 段数和库存随时间变化 |
| 10 | 核弹时序：确认弹射 → 弹出 → 第 1 次 / 第 11 次爆炸 | 有延迟补偿和服务器帧 | 濒死后弹射，`NDMG` 记每次 `damagedef_nuclear_core` 的时刻和伤害；靶子泰坦站在 100 / 350 / 500 / 700 / 760 u |
| 11 | 核弹内半径 350 还是 500 | 定义和脚本不一致 | 同上，看 350–500 之间是否满额 2500 |
| 12 | 核弹打护盾还是穿盾 | 定义没有 bypass 标志 | 带满护盾的泰坦靶子 |
| 13 | 弹射高度、偏 5° 的方向、`sv_gravity` | 重力值没在文件里查到 | `hsd` 轨迹记录铁驭位置；顶上加天花板测自伤 |
