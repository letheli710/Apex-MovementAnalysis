# A · 配件（R5 实测）

会话 `recoil-view`，2026-11-02。本地 R5Flowstate 混合构建。标注：**[实测]** 在 R5 跑到的行为或读回的运行时字段；**[静态]** 只看 `.txt`；**[推断]**。

数据：
- [A-MOD-SWEEP.tsv](A-MOD-SWEEP.tsv)：840 个"枪 + mod"，给上没有、和文件的差别。
- [A-MOD-SUMMARY.tsv](A-MOD-SUMMARY.tsv)：按 mod 汇总。
- [A-MOD-DIFFS.tsv](A-MOD-DIFFS.tsv)：**每个组合实际变了哪些字段、从多少到多少**（客户端读回，1175 个字段；视觉和声音字段省略）。这是配件表的主要来源。
- [A-PLAY.tsv](A-PLAY.tsv)：开枪的行为。
- [GUN-VARS.tsv](GUN-VARS.tsv)：31 把枪的运行时基础字段。

**覆盖**：字段扫描是 31 把枪（30 把 + Sheila）的全部 mod，每个组合 1 次，确定值所以够了。Vantage 的 `mp_ability_sniper_ult` 不是 `mp_weapon_*`，**没扫**。行为测试是下表写明的枪。

## 结论

| # | 结果 |
|---|---|
| 1 | **本地绝大多数配件都生效**：840 个组合里 825 个给上了，文件里写的字段基本按文件变。普通配件（枪管、弹匣、枪托、激光、霰弹栓、瞄具）行为实测也符合 |
| 2 | **Hop-up 的 `hopup_*` 大多只是空标记**，真正改行为的是切换 mod（`altfire_*`、`choke`、`shatter_rounds_hipfire`、`energized`）。切换的按键这里没找到，所以测的是"直接把切换 mod 给上"。**用户手动切换这一步没测到** |
| 3 | Shatter：**标记本身不变成霰弹**，这肯定了 IP2 的结果。给 `shatter_rounds_hipfire` 才是 7 发 × 8。腰射和开镜都如此，说明切换是靠脚本加减这个 mod，而不是枪判断腰射 |
| 4 | **枪托不只是开镜速度**：还改换弹、收枪、掏枪、抬枪、放下时间和开镜 view drift |
| 5 | 瞄具有自己的 FOV 窗口（如 0.1–0.8），ADS 时间也变长 |
| 6 | `hopup_kinetic_loader` 装到 Triple Take 上**服务器直接关掉**（2 次重现），Peacekeeper 上没事 |
| 7 | 15 个组合给了但没有上，见第 5 节 |

## 1. 普通配件（字段 + 行为）

### 枪管（R-301）[实测]

| Mod | `pitch_base` | `pitch_random` | `yaw_base` | `yaw_random` | 实测俯仰后坐比例（3 次平均） | 峰值俯仰 |
|---|---|---|---|---|---|---|
| 无 | 1 | 1 | 1 | 1 | 0.96 | 4.42° |
| L1 | 0.95 | 0.8 | 0.95 | 0.9 | 1.00 | 4.60° |
| L3 | 0.85 | 0.7 | 0.85 | 0.8 | 0.87 | 3.99° |
| L4 | 0.85 | 0.7 | 0.85 | 0.8 | 0.79 | 3.65° |
| `corrupted_barrel` | 见 DIFFS | | | | 0.83 | 3.81° |

L1 看不出差别，因为 3 次的随机差比 5 % 大。L3、L4 明显减小。**字段按乘法作用在表上**。`corrupted_barrel` 还改了很多：爆头倍率 1.3 → 1.56、腰射扩散 3 → 4.2 等。

### 弹匣（R-301）[实测]

`bullets_mag_l1` 21 → 23，`l3` 31，`l4` 31。`corrupted_mag` 37 发，但换弹 2.4 → 3.24 s。其他弹种同规则，见 DIFFS。

### 枪托 [实测]

| Mod（R-301） | ADS 进 / 出（s，实测） | 换弹 | 收枪 | 掏枪 | 抬枪 | 放下 |
|---|---|---|---|---|---|---|
| 无 | 0.270 / 0.230 | 2.40 | 0.55 | 0.60 | 0.50 | 0.40 |
| `stock_tactical_l1` | 0.229 / 0.196 | 2.32 | 0.47 | 0.51 | 0.45 | 0.36 |
| `stock_tactical_l3` | 0.203 / 0.173 | 2.16 | 0.41 | 0.45 | 0.40 | 0.32 |
| `corrupted_tactical_stock` | 0.203 / 0.172 | 2.16 | 0.41 | 0.45 | 0.40 | 0.32，弹匣 21 → 17 |

狙击枪托（G7）：ADS 0.320 / 0.250 → L1 0.256 / 0.200 → L3 0.224 / 0.175。`corrupted_stock_sniper` 0.256 / 0.200，弹匣 10 → 8，射速 4.1 → 4.92。两种枪托都按比例减小 `viewdrift_ads_*`（L3 约 ×0.55，G7 L3 约 ×0.35）。

只有 ADS 时间是跑出来的；换弹等几列是读回字段，**换弹实际时间**见 C。

### 激光（R-99）[实测]

腰射扩散最大值：无 4.0 → L1 3.2 → L3 2.4 → `corrupted_laser` 2.4。字段都乘在腰射扩散上。L4 有负的 kick：越打越准（`spread_kick_on_fire_stand_hip` −0.1），**只读了字段**。`corrupted_laser` 还把换弹 ×0.6。

### 霰弹栓 [字段实测]

EVA-8 射速 2.8 → L1 3.02 → L3 3.36。

## 2. 瞄具 [实测]

R-301 / G7 / R-99 / Longbow / Kraber。FOV 走 smoothstep，窗口是拟合的（基础 89）：

| 枪 + 瞄具 | `zoom_fov` | 实际 FOV | 窗口 | ADS 进 / 出（s） |
|---|---|---|---|---|
| R-301 无 | 55 | 69.97 | 0–1 | 0.27 / 0.23 |
| `optic_cq_hcog_classic`（1×） | 60 | 76.33 | 0–1 | 0.29 / 0.25 |
| `optic_cq_hcog_bruiser`（2×） | 38.59 | 49.09 | 0.1–0.8 | 0.29 / 0.25 |
| `optic_cq_holosight` | 60 | 76.33 | 0–0.66 | 0.29 / 0.25 |
| `optic_cq_holosight_variable` | 60 | 76.33 | 0.1–0.76 | 0.29 / 0.25 |
| `optic_ranged_hcog`（3×） | 26.28 | 33.43 | 0.1–0.65 | 0.34 / 0.29 |
| `optic_ranged_aog_variable` | 38.59 | 49.09 | 0.1–0.66 | 0.36 / 0.30 |
| R-99 `optic_cq_threat` | | 76.33 | 0.1–0.8 | 0.24 / 0.22 |
| Longbow 无 | | 69.97 | 0–1 | 0.31 / 0.28 |
| Longbow `optic_sniper`（6×） | | 16.94 | 0.58–0.86 | 0.48 / 0.42 |
| Longbow `optic_sniper_variable` | | 25.26 | 0.58–0.86 | 0.51 / 0.45 |
| Longbow `optic_sniper_threat` | | 25.26 | 0.58–0.76 | 0.53 / 0.47 |
| Kraber 无（自带镜） | 13.31 | 16.94 | 0.58–0.86 | 0.58 / 0.55 |

可变倍率瞄具的第二档要按键切换，**没测到**（读到的是默认档）。瞄具还改 `zoom_angle_shift_*`、景深、`zoomed_convar_sensitivity_index`（灵敏度档位），**灵敏度本身要鼠标，没测**。

## 3. 改玩法的 Hop-up

"标记"表示只给 `hopup_*` 一个 mod，"生效 mod"是直接给切换 mod。全部 [实测]。

| Hop-up | 枪 | 只给标记 | 给生效 mod | 说明 |
|---|---|---|---|---|
| Turbocharger | Havoc、Devotion | Havoc 按键到第一发 0.434 → 0.024 s；Devotion 起步间隔 0.20 → 0.15 s，后面相同；Nemesis 没变 | 不需要 | **字段本身**生效。`tb_*`，IP2 也这样 |
| Selectfire | Prowler | 不变，点射 0.049 s | `altfire_selectfire`：全自动 0.076 s（13.1/s），伤害 16 → 17 | |
| Selectfire | Charge Rifle | 不变 | `altfire_selectfire`：两发间隔 0.96 s，45 / 74 伤害 | 只有 2 发，不算准 |
| Anvil | R-301 | 不变，15 伤害 | `altfire_highcal`：32 伤害，每发 2 弹，半自动 | Flatline 39 伤害，同样半自动 |
| Base `altfire` | R-301、Flatline | | 半自动，伤害不变 | 这就是单发模式 |
| Double Tap | EVA-8 | 不变 | `altfire_double_tap`：两发间隔 0.149 s | 7 伤害不变 |
| Double Tap | G7 | 不变 | 0.069 s，伤害 33 不变 | |
| Double Tap | Alternator | 不变 | 每次扣 2 弹、2 个命中，伤害 18 → 14 | |
| Hammerpoint | P2020 / RE-45 / Mozambique | 字段就生效：24 → 26、14 → 18、17 → 19 | | 对没盾的假人。**对盾**：P2020 打盾 5 发同样 120，没有加成 |
| Skullpiercer | Longbow / Wingman / 30-30 | 头部 98 → 115、70 → 87、57 → 67 | | 身体没变（Longbow 身 60） |
| Shatter | 30-30 | 不变 | `shatter_rounds_hipfire`：7 × 8，最外约 2.3°（150 u） | 腰射开镜都一样。`hopup_shatter_rounds` 单独 43 |
| Shatter | Bocek | 不变，60 | `altfire_shatter` 不变，**`shatter_rounds_hipfire` 给不上** | 见第 5 节 |
| Choke | Peacekeeper | `hopup_energy_choke`、`hopup_kinetic_choke`、`kinetic_choke` 都不变 | `choke`，按住蓄力：半径 1.28° → **0.72°** | |
| Choke | Triple Take | 同上 | `choke`：0.22° → **0.14°** | |
| Disruptor | Alternator / RE-45 / Peacekeeper | 字段就生效，打盾 5 发：90 → 110、73 → 80、495 → 540 | | 这条数据是盾量差 |
| Energize | Sentinel | | `energized`：70 → 88 | |
| Energize | Rampage | | `energized`：5/s → 6.5/s | 触发入口没找到（IP2 同样） |
| Marksman's Tempo | Sentinel、Bocek | 不变 | Bocek 按住 0.35 s 连放，间隔 0.52 s 没变；Sentinel 给 `marksmans_tempo_active` 没变 | 需要脚本累积，**这里没有测到提速** |
| Boosted、Dual Shell、Kinetic | | 见 [C 第 4 节](C-MOTIONS.md) | | **更正**：这里之前写"`+reload` 不起作用"是错的；当时玩家的弹药池是空的，没有弹药可换。填满弹药池后 `+reload` 正常。所以 `rl_` 这批用例作废，由 C 重测。Boosted Hemlok 弹匣 1–5 时 1.80 s 加到 30 发；Wingman 弹匣 1 时到 7 发；Dual Shell 30-30 一次 2 发；Kinetic 不开滑铲时换弹不变 |
| `hopup_ultimate_accelerator` | 28 把枪 | 没变 | | 大招相关，不影响枪 |
| 金色、补给箱 | `crate` 10 把 | 没有字段变化 | | 补给箱版是另一把枪（`*_crate`），不是 mod |

`elevator_shooter`（30 把枪）：空中扩散 ×0.7，`air_scale_ads` 2 → 1.2。**[字段实测]**，**推断**是 S21 的新机制。

## 4. "刚配的那种配件"

这句话有歧义，两种读法都给：

1. **S21 数据里最新的配件**：`corrupted_*` 系列（barrel、mag、tactical_stock、stock_sniper、laser）在本地都能给上，字段都变（见第 1 节和 DIFFS）。它们是有代价的强化，例如 `corrupted_mag` 多带弹但换弹慢。这组 loot 里是否可得**没查**。
2. **刚装上时有什么效果**：换配件时有没有延迟或动画，**这里没测**，脚本是直接给枪带配件，走不到拾取流程。

要哪一种请用户确认。

## 5. 给了但没上，或关掉服务器的

| 枪 | Mod | 结果 |
|---|---|---|
| Triple Take | `hopup_kinetic_loader` | **服务器关闭**（2 次）。Peacekeeper 正常 |
| Hemlok、Hemlok Elite、Wingman | `fast_reload_mod`、`overloaded_ammo` | 没有报错，`GetMods` 里没有，字段没变 |
| EVA-8 | `shotgun_bolt_l1..l4_double_tap` | 同上 |
| Peacekeeper | `hopup_kinetic_choke`、`kinetic_choke` | 同上 |
| 30-30 | `charged`、`in_ads` | 同上 |
| Bocek | `shatter_rounds_hipfire` | 同上 |

Triple Take 有同名 `fast_reload_mod` 就能上。原因**没查**；这些 mod 都排在 mod 列表后面，**推断**和 mod 个数上限有关。

`optic_cq_threat` 装到没有这个 mod 的枪（R-301）报 `Error calculating bitfield for mods`，这是用法错，不是问题。

## 6. 本地和文件的差别

绝大多数按文件走。差别：

- `amped_damage`（18 把枪）：伤害是 `floor(x × 1.2)`，整数截断。R-99 12 → 14。
- 其余少数"不按文件"都在第 5 节那些没上的 mod 上，或是基础值 −1（未设）乘了没变化。
- **客户端和服务器的对比 [实测]**：25 个字段，21800 次比较，31 次不一致：
  - Nemesis `burst_fire_delay`：服务器 0.21，客户端 0.31（28 次）。IP2 实测点射间隔会从 0.30 降到 0.19，这两个值可能对应热量的两端，**推断**。
  - `energized`：Sentinel 伤害、Rampage 射速只有服务器变（88、6.5），客户端读回还是 70、5；但实际开枪两边都生效（第 3 节）。
  - 其余 1150 个字段只读了客户端。

## 7. 对 Unity

- **按字段做就行**：`A-MOD-DIFFS.tsv` 可以直接当配件表。
- 切换型 Hop-up 要做成"标记 + 切换 mod"两层。
- 枪托要同时改换弹、掏枪收枪和 view drift。
- 瞄具带 FOV 窗口和 ADS 时间，别只改倍率。
