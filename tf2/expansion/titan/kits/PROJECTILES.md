# 泰坦投射物通用弹道表（`kits/PROJECTILES.md`，2026-11-13，`tf2-kits-measure`）

给 Unity 共用框架（`titan-kits-core`）照做的总表：每种投射物的发射方式、初速、重力、寿命、追踪、漂移、张开收拢、碰撞尺寸、伤害。脚本和设置里直接写的标 **[file]**，Ghidra 读出的原生规则标 **[原生·Ghidra]**，本地 Northstar 私服实测的标 **[meas]**，按代码推出来的标 **[推断]**。

## 先说结论

- **重力单位已实测确认：** `kv.gravity` / `projectile_gravity_scale` 是 × 750 u/s²。40 mm 的竖直速度每秒掉 37.5（0.05 × 750），狙击弹 0.75（0.001 × 750）[meas]。
- **导弹不受重力**，只有漂移和追踪；转向时速率不变（齐射全程 2200 ± 1 %）[meas]。
- **Ronin 霰弹实际没有重力**：脚本写了 `kv.gravity 0.4`，但设置 `bolt_gravity_enabled 0` 生效，竖直速度一直是 0 [meas]。
- **Monarch 火箭齐射的曲线测到了**：外张 +5° 约 0.17 s → 0.23 s 线性转到 −10° → 保持 0.07 s → 0.12 s 转直 → 0.83 s 起随机漂移（§2.4，详细见 [MONARCH.md](MONARCH.md) §8.4）[meas]。
- **多目标导弹**：0.42 s 第一把锁，之后每 0.15 s 一把（不是设置的 0.3 s），上限 6 / 导弹架 12；没锁时发 5 / 11 枚，走齐射弹道（§2.5）[meas]。
- **电弧波**：贴地每脚本帧（0.1 s）推进 112 u，实测 1.4 s 走了 1568 u（14 段）[meas]。
- **对直接命中的泰坦只有一次伤害事件**：齐射每枚 250、多目标导弹每枚 350，没有另外的爆炸事件 [meas]。设置里的"直击 + 爆炸"不能相加。
- **Ion 涡旋打回**：伤害取原武器的值（40 mm 330、齐射 250、追踪导弹 350、狙击 250、霰弹 90）；弹体 8000 u/s、重力 0.3 × 750 再乘原武器的重力倍数，散布最大约 10°；霰弹 12000；导弹 1800、不加散布（§2.12）[meas]。
- **铝热火团**不弹跳、贴地滑，斜落时顺弹道滑 120 – 390 u；两发叠加、同一发不叠（§2.9）[meas]。
- **导弹远距离漂移**是蛇行：航向 ±15 – 17°、周期约 0.8 – 1 s（§2.4）[meas]。
- 还缺的见最后一节（追踪导弹和飞行核心火箭的逐帧转弯、导弹碰撞尺寸、几种弹体的寿命）。

**实测运行**（原始日志在私有仓库 HSD-RawData，分支 `tf2/titan-kits-measure-raw`；公开仓库 `tf2/runtime/data/` 有 `diag.tsv`、`plan.gnut`）：`20261113_015656_km_monarch`（Monarch）、`020002_km_proj`（Tone / Northstar / Ronin 自己开火，服务端 10 Hz）、`022647_km_ion`（涡旋）、`022352_km_scorch`（铝热）、`022911_km_hover`（`mp_homestead`：悬停、远距离漂移）。作废和部分有效的运行见 [README.md](README.md) 运行表。工具在 [measure/](measure/)：模组 `HSD.KitMeasure`（`hsd_km_*` 命令，每帧记投射物、锁定、铝热火团），实验表 `plans_km.py`，分析 `an_expand.py`、`an_lock.py`、`an_proj.py`。

## 0. 怎么读

**出处缩写**（都在 `TF2-Research/local/vpk/` 下，另有两处单列）：

| 缩写 | 路径 |
|---|---|
| W | `client_mp_common/scripts/vscripts/weapons/` |
| WT | `client_mp_common/scripts/weapons/`（武器设置 .txt） |
| FE | `client_frontend/scripts/vscripts/` |
| SPT | `client_sp_training/scripts/`（单人包里唯一带武器脚本和设置的） |
| SPB | `client_sp_beacon/scripts/vscripts/sp/` |
| RN | `ref-native-tail/REF-NATIVE-1112.md`（分支 `ref/native-tail`，未合并） |
| KIT | 本目录（`tf2/expansion/titan/kits/`） |

**取值规则：** 多人值 = 顶层键 + `MP_BASE` 块 + 对应 mod 块的覆盖；`SP_BASE` 一律丢掉（BT 一节反过来用 `SP_BASE`）。泰坦文件里没有 `[$mp]` / `[$sp]` 行内条件（grep 过，0 处）。`#base` 继承：`mp_titanweapon_tracker_rockets.txt:1` 继承 `mp_titanweapon_salvo_rockets.txt`。

**几条贯穿全表的通则：**

1. **重力单位。** `kv.gravity` 和 `projectile_gravity_scale` 都是 **× sv_gravity** 的倍数 [meas：40 mm 竖直速度 −30.44 → −34.19 u/s / 0.1 s = −37.5 u/s² = 0.05 × 750；狙击弹 −0.8 u/s² ≈ 0.001 × 750，运行 20261113_020002_km_proj]。TF2 `sv_gravity` = 750 u/s²（`TF2-Research/static-values/T1-REPORT.md:46`）。下表"重力"列写倍数，括号里是 ×750 的结果。导弹类（FireWeaponMissile）文件里没有任何重力键 → 写"未找到（推断 0）"。
2. **发射函数第三个参数是绝对速度还是倍率。** 武器设置里有 `projectile_launch_speed` 时，脚本传的是**倍率**：铝热 `speed = 1.0 // 2200.0`（W/`mp_titanweapon_meteor.nut:463`），飞行核心火箭传 `1`（W/`mp_titanweapon_flightcore_rockets.nut:37`），齐射核心传 `0.8–1.1`（W/`mp_titancore_salvo_core.nut:205`）[推断：按注释和用法；原生乘法没读]。没有 `projectile_launch_speed` 时，脚本传的就是 u/s（40 mm 8000、狙击 10000、霰弹 4400 等）。
3. **漂移 6 个键**（RN §4，[原生·Ghidra]）：W = `projectile_drift_windiness`（乘时间，管频率），I = `projectile_drift_intensity`（×dt 后是幅度），`straight_time_min/max`、`straight_radius_min/max`。每帧：t < time_max 时把导弹拉回出膛直线；lerp = 1（t ≤ min）否则 1 − (t − min)/(max − min)；**半径 = rmax + (rmin − rmax)·lerp**，从 rmin 涨到 rmax；`FromWeaponSettings` 版里 radius < 1 按 1。直接传 6 个数的 `InitMissileForRandomDrift`（涡旋打回用）不夹 1。旧脚本版（W/`_weapon_utility.nut:1489–1497`，已注释掉）写着"有目标时不漂移、交给追踪"，原生是否也这样 **不确定**。
4. **追踪 `SetHomingSpeeds(H1, H2)`**（RN §10，[原生·Ghidra]）：每 1/60 s `方向 = normalize(v + 60·dt·H·û)`，**只转向不改速率**；H = 目标是正在 dash 的玩家时用 H2，否则 H1；目标点 ≈ 目标中心 + 2·dt·目标速度；偏出 60° 以上、且转弯半径大于距离时这枚导弹的 H 清零（永久丢追踪）。侧向角速度约 60·H/|v| rad/s。SmartAmmo 默认 H = 300（W/`sh_smart_ammo.gnut:436`），引擎默认 `missile_homing_speed` 150（RN:191）。
5. **脚本帧 = 0.1 s。** 服务端 `WaitFrame()` 是 10 Hz（`script_server_fps` 默认 10，11-08 实测；KIT/`SCORCH.md:11,36`，KIT/`RONIN.md:30`）。追踪、漂移、碰撞是引擎 60 Hz；凡是脚本 `WaitFrame` / `wait` 推进的（电弧波、子爆炸分组、铝热跳伤）按 0.1 s 读。
6. **碰撞尺寸。** 只有 bolt 类有 `bolt_hitsize`（和随时间变大的 `grow1/grow2/growfinal`）。导弹类文件里没有尺寸键 → "未找到"。
7. **伤害两段。** 直击 = `damage_near/far_value`（铁驭）/ `_titanarmor`（泰坦）；爆炸 = `explosion_damage` / `explosion_damage_heavy_armor`，内外半径 `explosion_inner_radius` / `explosionradius`。没写 `_titanarmor` 时对泰坦用哪个值 **不确定**（KIT/`MONARCH.md` 推断同铁驭值）。

---

## 1. 总表（多人值；细节和出处见第 2 节各小节）

| 投射物 | 发射 | 初速 u/s | 重力（× sv_gravity） | 寿命 s | 追踪 | 每次几枚 / 间隔 | 涡旋重发 |
|---|---|---|---|---|---|---|---|
| Tone 40 mm | Bolt | 8000 | 0.05（37.5）[meas] | 未找到 | 无 | 1；射速 1.75 /s | explosive_round |
| ├ mortar_shots | Bolt | 4800（×0.6） | 4.0（3000） | 10 | 无 | 同上 | 同上 |
| └ Burst Loader | Bolt | 8000 | 0.05 | 未找到 | 无 | 1–3 连发，连发内 0.2 s | 同上 |
| Tone 追踪导弹 | Missile（SmartAmmo） | 1800 | 未找到（推断 0） | 10 | 按距离 200→100，每 0.2 s +15 封顶 200 | 每目标 6（Rockets 升级 8），14 /s | rocket |
| Tone 齐射核心 | Missile | 1000 × 0.8–1.1 [推断] | 未找到 | 10 | (100, 0)，跟准星导引点 | 每发 3 枚 × 20 发，12 /s | rocket |
| Monarch 火箭齐射 | Missile（张开收拢，曲线见 §2.4 [meas]） | 2200 | 0 [meas] | 10（到时空爆） | 无 | 6（Racks 12），12 /s | rocket |
| 多目标导弹（Monarch 升级） | Missile（SmartAmmo，张开收拢） | 2200 | 0 [meas] | 10 | (550, 550) | 每把锁 1 枚，12 /s；锁 0.42 s 起每 0.15 s 一把，上限 6（导弹架 12）[meas]；无锁 5（11）枚 [meas] | rocket |
| Northstar 集束导弹 | Missile | 3500 | 未找到 | 未找到 | 无 | 1；射速 1.75 /s | rocket |
| └ 子爆炸 | 脚本 Explosion | — | — | 5（Enhanced 8） | — | 25 次（5 组） | — |
| 飞行核心火箭 | Missile | 2000 × 1 [推断] | 未找到 | 10 | 0.1 s 后 (2000, 0) 飞向开火时准星点 | 1，12 /s | rocket |
| Northstar 狙击弹 | Bolt | 10000 | 0.001（0.75）[meas] | 未找到 | 无 | 1；射速 0.9 /s | explosive_round |
| Scorch 铝热弹 | Bolt（`bolt_gravity_enabled 1`） | 2200 × 1 [推断] | 0.625（468.75） | 未找到 | 无 | 1 | explosive_round |
| Ronin 霰弹 | Bolt × 8 | 4400（+20 % 自身速度） | **0** [meas]（脚本 0.4 不生效） | 0.30–0.35 随机 | 无 | 8 同帧；射速 2.5 /s | bullet |
| Ronin 电弧波 | Grenade（藏起、冻住）+ 脚本贴地推进 | 112 u / 脚本帧 = 1120 u/s [meas] | 不适用 | 15 段 ≈ 1.5 s | 无 | 1 | absorb（且 `projectile_ignores_vortex mirror`） |
| 涡旋打回 explosive_round | Bolt | 8000 | 0.3（225） | 未找到 | 无 | 每个存的 1 发，同帧 | — |
| 涡旋打回 bullet（投射物类） | Bolt | 12000 | 0.0 | 未找到 | 无 | 同上 | — |
| 涡旋打回 rocket | Missile | 1800 | 未找到 | 2.6–3.5 随机 | 无 | 同上 | — |
| BT 多目标导弹（单人） | Missile（SmartAmmo，张开收拢） | 1000 | 未找到 | 10 | (250, 250) | 每把锁 1 枚，30 /s，最多 12 | rocket |
| BT 爆发核心（单人） | **FireWeaponBullet（命中扫描，不是投射物）** | — | — | — | — | 100 发，20 /s | bullet |

---

## 2. 逐项

### 2.1 Tone 40 mm 追踪炮（`mp_titanweapon_sticky_40mm`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponBolt(pos, dir, speed, …)`，单发 | [file] W/`mp_titanweapon_40mm.nut:97` |
| 初速 | `PROJECTILE_SPEED_40MM` = 8000 | [file] W/`mp_titanweapon_40mm.nut:18, 90` |
| 重力 | `bolt.kv.gravity = 0.05`（×750 = 37.5 u/s² [推断]） | [file] 同上 `:110` |
| 寿命 | 脚本和设置都没写 | 未找到 |
| 追踪 / 漂移 | 无 / 无漂移键 | [file] |
| 碰撞尺寸 | `bolt_hitsize` 3.5（没有 grow 键） | [file] WT/`mp_titanweapon_sticky_40mm.txt:29` |
| 直击 | 铁驭 200 / 泰坦 330；近 1500、远 3000 两端同值（不衰减）；暴击 × 1.5 | [file] WT:33–35, 43–46 |
| 爆炸 | 铁驭 75 / 泰坦 200；内 17、外 150；冲击力 20000 | [file] WT:48–51, 94 |
| 弹夹 / 射速 | 12 / 1.75 /s（半自动） | [file] WT:14, 140, 144 |
| 反弹键 | `grenade_bounce_*`、`grenade_roll_*` 写了（0.5/0.3/0.5/0.2/0.2/0.1），对 bolt 是否生效 **不确定** | [file] WT:164–169 |
| 涡旋 | `explosive_round`，`vortex_drain` 0 | [file] WT:119, 157 |
| 标记 | 命中给追踪导弹加标记，寿命 15 s（单人 60 s），满 3 层可发导弹 | [file] W/`mp_titanweapon_40mm.nut:25–29, 197–287` |

**改速 / 改重力的 mod：**

| mod | 改了什么 | 来源 |
|---|---|---|
| `mortar_shots` | 速度 × 0.6 → 4800；`kv.gravity` 4.0（3000 u/s²）；`kv.lifetime` 10；直击和爆炸 × 1.2；内 100 / 外 225；弹夹 10 | [file] W/`mp_titanweapon_40mm.nut:92–107`；WT:439–452 |
| `pas_tone_burst`（Burst Loader） | ADS 蓄力（`charge_is_triggered_by_ADS 1`），2.0 s 3 档；开火时把连发数设成当前档数（最少 1）；连发内射速 5 /s（0.2 s 一发），连发后 0.75 s；弹速和重力不变 | [file] WT:504–534；W/`mp_titanweapon_40mm.nut:70–78` |
| `splasher_rounds` / `fd_splasher_rounds` | 内 100 / 外 225；直击 250 / 600；爆炸 125 / 125（FD 版只改半径） | [file] WT:410–425, 535–540 |
| `burn_mod_titan_40mm` | 全自动 2.0 /s，散布变大 | [file] WT:453–479 |
| `gunship_gunner` | 全自动 3 /s，弹夹 40，内 100 / 外 225 | [file] WT:395–409 |

Burst Loader 每档的时刻：2.0 s / 3 档，是否均分 **不确定** [推断均分 ≈ 0.67 s 一档]。

**实测 [meas]**（`km_proj`，服务端 10 Hz）：出膛 8000 u/s；竖直速度每 0.1 s 掉 3.75（−37.5 u/s²）= 0.05 × 750，重力单位确认。水平开火时出膛方向略朝下（−0.2 … −0.5°），是对准准星落点而不是枪口正前方。

### 2.2 Tone 追踪导弹（`mp_titanweapon_tracker_rockets`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `SmartAmmo_FireWeapon` → `FireWeaponMissile(pos, dir, 1800, …)`，每枚一个已锁目标 | [file] W/`mp_titanweapon_tracker_rockets.nut:50`；W/`sh_smart_ammo.gnut:266–331` |
| 初速 | `SmartAmmo_SetMissileSpeed(weapon, 1800)`；之后 `SetSpeed(1800)` | [file] W/`..._tracker_rockets.nut:32`；W/`sh_smart_ammo.gnut:278, 314` |
| 重力 | 未找到（推断 0） | — |
| 寿命 | `kv.lifetime = 10`（继承的 `projectile_lifetime` 也是 10，寿命到空爆） | [file] W/`sh_smart_ammo.gnut:307`；WT/`mp_titanweapon_salvo_rockets.txt:18–19` |
| 追踪 | 发射时 `SetHomingSpeeds(200, 200)`；思考线程立刻改成 H = GraphCapped(距离, 400→1800, 200→100)；之后每 0.2 s H + 15，封顶 200；两参数相同（目标 dash 也照追） | [file] W/`..._tracker_rockets.nut:33, 91–110` |
| 锁定条件 | 目标身上标记满 3 层（`smart_ammo_max_trackers_per_target 3`，`*_must_be_tracked 1`）；不满按不出（提示音）；搜索角 0.1、距离 15000、最多 20 目标；锁时 0（`targeting_time 0`）；泰坦不挡视线 | [file] WT/`..._tracker_rockets.txt:209–243`；W/`..._tracker_rockets.nut:113–138` |
| 漂移 | W 70、I 10.96、直飞 0–0.1 s、半径 5–10 | [file] WT:61–66 |
| 张开收拢 | 无（`SmartAmmo_SetExpandContract` 没调） | [file] W/`..._tracker_rockets.nut:28–39` |
| 碰撞尺寸 | 未找到 | — |
| 直击 | 350（没写 `_titanarmor`，对泰坦 **不确定**；11-08 实测每发 350，KIT/`TONE.md:477`）；暴击关 | [file] WT:31, 84–85 |
| 爆炸 | 继承齐射：铁驭 100 / 泰坦 250；内 60 / 外 120 [推断：`#base` 合并] | WT/`mp_titanweapon_salvo_rockets.txt:72–73, 109–110` |
| 冲击力 | 40000 | [file] WT:132 |
| 每次几枚 / 间隔 | 每个满标记目标 6 枚（`doBurstPerTarget 1`，`always_do_burst 1`）；`pas_tone_rockets` 8 枚；射速 14 /s；连发后 0.7 s | [file] WT:83, 116–117, 217–218, 241, 261–262；W/`sh_smart_ammo.gnut:142–173` |
| 发后 | 最后一枚清掉目标身上的标记 | [file] W/`sh_smart_ammo.gnut:229–238` |
| 涡旋 | `rocket`（继承） | [file] WT/`mp_titanweapon_salvo_rockets.txt:141` |

### 2.3 Tone 齐射核心（`mp_titancore_salvo_core`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | 每个连发索引 `FireWeaponMissile` **3 枚**（竖直偏移 0、+0.5、−0.5，各再乘随机 0.3–1.5）；横向偏移在 ±0.25 右向量间交替；位置偏 offset × 32 | [file] W/`mp_titancore_salvo_core.nut:157–223` |
| 注意 | 循环里 `attackDir += …`、`attackPos += …` 是**累加**的，3 枚的方向和位置一枚比一枚偏得多 | [file] 同上 `:201–203` |
| 初速 | 设置 `projectile_launch_speed` 1000；脚本传 RandomFloatRange(0.8, 1.1) → [推断] 800–1100 u/s | [file] WT/`mp_titancore_salvo_core.txt:78`；W:205 |
| 继承自身速度 | `projectile_inherit_owner_velocity_scale` 1.0 | [file] WT:187 |
| 重力 | 未找到 | — |
| 寿命 | `MISSILE_LIFETIME` 10 | [file] W:134, 217 |
| 追踪 | `SetHomingSpeeds(100, 0)`：目标在 dash 时完全不追；目标 = 一个导引点 info_target，玩家开火时每脚本帧移到视线落点；视线打到重甲目标就粘在它身上，直到准星偏离 dot ≤ 0.965（约 15°）再换 | [file] W:211, 216, 343–437；[原生·Ghidra] RN:206 |
| 导引线程寿命 | 10 + 5 s，或全部导弹消失 | [file] W:343–356 |
| 漂移 | W 7、I 0.96、直飞 0.6–0.9 s、半径 0–1 | [file] WT:79–84 |
| 张开收拢 | 无 | — |
| 碰撞尺寸 | 未找到；导弹不可被打（`SetTakeDamageType(DAMAGE_NO)`） | [file] W:215 |
| 直击 | 铁驭 60 / 泰坦 140（近 800 远 1200 同值）；类型 burn | [file] WT:124, 143–148 |
| 爆炸 | 铁驭 60 / 泰坦 140；内 150 / 外 150；不伤自己；冲击力 32000 | [file] WT:126, 128, 149–152 |
| 每次几枚 / 间隔 | 连发 20 次 × 3 = 60 枚，射速 12 /s → 约 1.58 s 发完 [推断：首发 t = 0]；FD 升级连发 +10 | [file] WT:190–191, 371 |
| 蓄力 | `charge_time` 0.5、`chargeup_time` 0.5 | [file] WT:37, 51 |
| 涡旋 | `rocket`；`vortex_drain` 0.045 | [file] WT:108, 203 |
| 其他 | `scripted_projectile_max_timestep` 0.1，含义 **不确定** | [file] WT:213 |

**实测 [meas]**（`km_proj` `salvo_core`，服务端 10 Hz）：60 枚，出膛速率 800 – 1094 u/s（和 1000 × 0.8–1.1 相符）；出膛仰角 −14 … +31°、水平偏 −42 … +38°，扇面很宽（累加偏移）；约一半在 0.5 s 内撞地。导弹不受重力（远飞的那些竖直加速度 ±60 以内，是追踪和漂移）。

### 2.4 Monarch 火箭齐射（`mp_titanweapon_salvo_rockets`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireExpandContractMissiles` → 每次 `FireWeaponMissile` 1 枚 + 原生 `InitMissileExpandContract` + 设置漂移 | [file] W/`mp_titanweapon_salvo_rockets.nut:30`；W/`_weapon_utility.nut:1935–1975` |
| 初速 | `VANGUARD_SHOULDER_MISSILE_SPEED` = 2200 | [file] FE/`sh_consts.gnut:459` |
| 重力 | 未找到 | — |
| 寿命 | `projectile_lifetime` 10，`projectile_airburst_on_death 1`（到时空爆） | [file] WT/`mp_titanweapon_salvo_rockets.txt:18–19` |
| 追踪 | 无（没设目标） | [file] |
| 漂移 | W 7、I 0.96、直飞 0.9–1.2 s、半径 0–1（夹成 1） | [file] WT:24–29；[原生·Ghidra] RN:101 |
| 张开收拢参数 | 每次 1 枚、加随机散布 true；张开角 5°、张开 0.20 s；过渡插值 0.2 s；收拢角 −10°、收拢 0.10 s；转直插值 0.1 s；终点 = 眼睛 + 准星 × 5000 | [file] W/`..._salvo_rockets.nut:8–15`；W/`_weapon_utility.nut:1941` |
| 每枚方位 | 第 k 枚绕准星转 a = (360 / 1) / 连发数 × k = 60° × k（Racks 30° × k）；张开向量 = forward·cos5° + (right·cos a + up·sin a)·sin5°；收拢向量 = forward·cos(−10°) + (right·cos a + up·sin a)·sin(−10°)（往对侧） | [file] W/`_weapon_utility.nut:2019–2087` |
| 各段怎么插值 | 原生 `InitMissileExpandContract`，本页没读到 | **不确定**（KIT/`MONARCH.md:126` 也标推断） |
| 碰撞尺寸 | 未找到 | — |
| 直击 | 250（近 800 远 1200 同值）；没写 `_titanarmor` | [file] WT:105–108 |
| 爆炸 | 铁驭 100 / 泰坦 250；内 60 / 外 120；冲击力 1；类型 burn | [file] WT:64, 72–74, 109–110 |
| 每次几枚 / 间隔 | 6 枚（`missile_racks` 12），12 /s；每枚扣 20（Racks 10），能量 120；连发后 0.7 s | [file] WT:79, 103–104, 131–132, 281–282 |
| 涡旋 | `rocket` | [file] WT:141 |
| 其他 mod | `multi_launch_system`：爆炸 150 / 1300、内 250 / 外 400；`scripted_no_damage`、`northstar_prime_execution`：伤害 0、直飞 0、寿命 1.0 | [file] WT:245–277 |

**实测 [meas]**（`km_monarch`，客户端每帧，见 [MONARCH.md](MONARCH.md) §8.4）：

| 时刻（每枚自己出现算起） | 径向角（+ 向外，− 向内） | 说明 |
|---|---|---|
| 0 – 0.17 s | +5.2°（单枚 4.6 – 6.0°） | 外张 |
| 0.17 – 0.40 s | +5° → −10° 线性 | 0.25 s 外偏最大 40 – 55 u（前方约 550 u） |
| 0.40 – 0.47 s | −10° | 0.44 s 穿过准星线（前方约 970 u） |
| 0.47 – 0.59 s | −10° → 0° | 0.58 s 内偏最大 33 – 39 u |
| 0.59 – 0.83 s | +0.6 … +0.8° | 飞向"眼睛 + 准星 × 5000"那一点 |
| 0.83 s 起 | 随机漂移，1.0 s 时 +3 … +9° | 远处的漂移见 §3 |

速率全程 2200（转向时最低 2180）。对直接命中的泰坦每枚只有一个伤害事件 250。

**远距离漂移 [meas]**（`km_hover` `svl_*`，`mp_homestead` 开阔地，客户端每帧）：0.83 – 1.0 s 先被拉回出膛线（径向角 +1 → +10°），之后随机蛇行：航向最大 ±15 – 17°，周期约 0.8 – 1.0 s；3 – 4.5 km 处离准星线 50 – 150 u，飞得最远的一枚 6.4 km 处偏 480 u（右）/ 560 u（上）。速率一直 2200。

### 2.5 多目标导弹（`mp_titanweapon_shoulder_rockets`，多人）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `SmartAmmo_FireWeapon` → 有锁：张开收拢 + 追踪；**没锁**：多人改调齐射函数，枚数 = 剩余格数（张开收拢参数用齐射那套 5° / −10°） | [file] W/`mp_titanweapon_shoulder_rockets.nut:92–111` |
| 初速 | 多人 2200（`VANGUARD_SHOULDER_MISSILE_SPEED`） | [file] W:64；FE/`sh_consts.gnut:459` |
| 追踪 | 多人 H = 2200 / 1000 × 250 = **550**，`SetHomingSpeeds(550, 550)` | [file] W:66–67；W/`sh_smart_ammo.gnut:315` |
| 寿命 | 10 | [file] W/`sh_smart_ammo.gnut:307` |
| 张开收拢参数 | 每次 1 枚、随机散布 true；张开角 多人 5°（单人 10°）、张开 0.2 s；过渡插值 0.0；收拢角 多人 −5°（单人 −10°）、收拢 0.0 s；转直插值 **−0.2**（负数，含义 **不确定**） | [file] W:14–35, 69 |
| 漂移 | W 7、I 0.96、直飞 0.9–1.2 s、半径 0–1 | [file] WT/`mp_titanweapon_shoulder_rockets.txt:33–38` |
| 锁定 | 只在按住时搜（`only_search_on_charge 1`）；搜索角 80（升级版 30）、距离 4000（mod 8000）；每把锁 0.3 s；最多 8 目标；单个重甲最多 12 把（升级版 6）；泰坦挡视线；`alt_lock_style 1`；不锁隐身 | [file] WT:261–293, 315, 332–358 |
| 直击 | 铁驭 250 / 泰坦 350 | [file] WT:80–83 |
| 爆炸 | 铁驭 100 / 泰坦 350；外 120（内半径没写，**未找到**） | [file] WT:84–87 |
| 每次几枚 / 间隔 | 每把锁 1 枚；射速 12 /s；连发后 0.7 s；冷却整条 18 s、延迟 2 s | [file] WT:75, 113–117, 127 |
| 碰撞尺寸 | 未找到 | — |
| 涡旋 | `rocket` | [file] WT:136 |

**实测 [meas]**（`km_monarch`，见 [MONARCH.md](MONARCH.md) §8.5）：第 1 把锁 0.417 s，之后每 0.15 s 一把（锁数连续增长 6.67 /s）；`upgradeCore_Vanguard` 上限 6（1.16 s），导弹架版 12（2.06 s）；900 u 外偏 18.4° 的第二目标锁不上。没锁松手：5 枚（导弹架 11），弹道和火箭齐射相同。有锁：外张 +5.3° 约 0.15 s 后开始追，900 u 0.38 – 0.41 s 命中；每枚对泰坦一个伤害事件 350。

### 2.6 Northstar 集束导弹（`mp_titanweapon_dumbfire_rockets` + 子爆炸）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponMissile(pos, dir, 3500, …)`；玩家瞄向准星落点（`GetVectorFromPositionToCrosshair`） | [file] W/`mp_titanweapon_dumbfire_rockets.nut:68–74, 89–103` |
| 初速 | 3500 | [file] W:91 |
| 重力 / 寿命 | 未找到 / 未找到 | — |
| 追踪 | 无 | — |
| 漂移 | W 2、I 0.4、直飞 0.1–2 s、半径 0–4（夹成 1–4）；`burn_mod` 6 个键全 × 0.2 | [file] WT/`mp_titanweapon_dumbfire_rockets.txt:28–33, 218–223` |
| 碰撞尺寸 | 未找到 | — |
| 直击 | 300（近 800 远 1200 同值）；类型 burn | [file] WT:70–74 |
| 爆炸（撞击那一下和每次子爆炸同值） | 铁驭 66 / 泰坦 150；内 150 / 外 220；冲击力 1 | [file] WT:75–82；W/`_weapon_utility.nut:1610–1621` |
| 射速 / 耗能 | 1.75 /s；每发 180（满 180） | [file] WT:87–89, 104 |
| 涡旋 | `rocket`；而且撞到涡旋球时**当场触发子爆炸** | [file] WT:113；W/`_vortex.nut:1805–1810, 1880–1886` |
| Twin Cluster（`fd_twin_cluster`） | 连发 2，间隔 0.1；各偏 ±(0.25–0.35) × 0.1 右向量；不再瞄准星落点 | [file] W:47–65；WT:197, 251 |

**子爆炸（`ClusterRocket_Detonate` → `StartClusterExplosions` → `ClusterRocketBursts`）：**

| 项 | 值 | 来源 |
|---|---|---|
| 起爆延迟 | `projectile_explosion_delay` 0.5 s | [file] WT:35；W/`_weapon_utility.nut:1623, 1661–1662` |
| 起爆时 | 一次只推不伤的物理爆炸（半径 = 外半径 220） | [file] W/`_weapon_utility.nut:1698–1703` |
| 分组 | 5 个线程（`GROUP_SIZE` 5），每脚本帧开一个 | [file] W:1705–1710；FE/`sh_consts.gnut:484` |
| 每线程次数 | `counter <= count / groupSize` → 20 / 5 = 4 → **5 次**；共 25 次 | [file] W:1758；FE:478 |
| 每次间隔 | burstDelay = duration / (count / groupSize) = 5 / 4 = 1.25 s，再减随机 popDelay（0.5 ± 0.3）→ 每次等 0.45–1.05 s [推断按公式] | [file] W:1738, 1765, 1783；FE:481–482, 486 |
| 落点 | 法线方向半球内随机方向 × 250 × Random(0–1)；被墙挡就截短；一颗物理小弹按"在剩余时间内到达"的速度飞过去（`GetVelocityForDestOverTime`，重力常数 750） | [file] W:1760–1777, 1828–1830；FE:483 |
| 每次伤害 | `Explosion(...)` 用武器的爆炸值 66 / 150、内 150 / 外 220 | [file] W:1785–1798 |
| 总时长 | `CLUSTER_ROCKET_DURATION` 5 s（`ClusterRocketBursts` 末尾 `wait 5`） | [file] W:1712；FE:486 |
| Enhanced Payload（`pas_northstar_cluster`） | 次数 32、时长 8 s、范围 × 1.5（375） | [file] W:1563–1567；FE:479, 487 |
| Twin Cluster | 次数 × 0.7、时长 × 0.7 | [file] W:1576–1580 |
| 碰撞文件 | `OnProjectileCollision_ClusterRocket` 只负责起爆和"禁止出生区" | [file] W/`mp_projectile_cluster_rocket.nut:4–15` |

**实测 [meas]**（`km_proj` `cluster`）：3500 u/s；竖直速度在 121 – 124 之间来回（漂移），没有重力。

### 2.7 飞行核心火箭（`mp_titanweapon_flightcore_rockets`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponMissile(pos, dir, 1, …)`；左右交替（alt fire 索引）偏 ±(0.25–0.45) 右向量，竖直再加 −0.25…+0.55，位置偏 offset × 32 | [file] W/`mp_titanweapon_flightcore_rockets.nut:20–37` |
| 初速 | `projectile_launch_speed` 2000（MP_BASE）× 1 [推断] | [file] WT/`mp_titanweapon_flightcore_rockets.txt:86` |
| 重力 | 未找到 | — |
| 寿命 | `kv.lifetime = 10`，服务端线程到时 Destroy | [file] W:42, 61–76 |
| 追踪 | 开火时从眼睛沿准星打 50000 u 射线取落点；0.1 s 后 `SetHomingSpeeds(2000, 0)`、`SetMissileTargetPosition(落点)`（固定点，不跟人；对 dash 中玩家 H2 = 0 这一条对"位置目标"是否适用 **不确定**） | [file] W:41, 44, 79–85 |
| 漂移 | W 2、I 2.95（MP_BASE）、直飞 0–0.1 s、半径 0–3 | [file] WT:57–60, 87–88 |
| 碰撞尺寸 | 未找到 | — |
| 直击 | 铁驭 300 / 泰坦 300；类型 burn | [file] WT:65–68, 133 |
| 爆炸 | 铁驭 55 / 泰坦 300；内 150 / 外 150；不伤自己；冲击力 32000 | [file] WT:69–70, 82–83, 138–139 |
| 每次几枚 / 间隔 | 1 枚，12 /s；飞行核心 6 s（`sustained_discharge_duration`） | [file] WT:153；WT/`mp_titancore_flight_core.txt:26` |
| 涡旋 | `rocket`；`vortex_drain` 0.066 | [file] WT:53, 165 |

**实测 [meas]**（`km_proj` `fc_rockets`，服务端 10 Hz）：13 枚，全是 2000 u/s；出膛仰角 −10 … +28°、水平偏 ±25°，1.1 – 1.2 s 内飞到 1000 u 外偏右 300 u 的落点附近（航向从 ±20° 收回到 ±5° 以内）。

### 2.8 Northstar 狙击弹（`mp_titanweapon_sniper`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponBolt(pos, dir, 10000, …)` | [file] W/`mp_titanweapon_sniper.nut:20, 177` |
| 重力 | `kv.gravity = 0.001`（0.75 u/s²） | [file] W:180 |
| 寿命 | 未找到 | — |
| 碰撞尺寸 | 0 → 0.035 s 2 → 0.08 s 4 → 0.18 s 插值到 6（MP_BASE） | [file] WT/`mp_titanweapon_sniper.txt:73–78, 93` |
| 穿透 | `pass_through_damage_preserved_scale` 1.0 | [file] WT:79 |
| 直击 | 基础 250 / 250（近 800 远 3000 同值）+ 档数 × 每档额外（铁驭 250 / 泰坦 300）；档 = 1 + 蓄力档；暴击时额外部分也 × `critical_hit_damage_scale` 1.5（FD 升级 × 2）；爆头 1.5、爆头距离 15000 | [file] WT:71–72, 84–89, 64, 168–170；W:56–77, 181–184, 207–224；W/`mp_projectile_titanweapon_sniper.nut:5–28` |
| 爆炸 | 0（半径 0） | [file] WT:94–97 |
| 击退泰坦 | 按伤害和距离（近 1000 × 0.5、远 1500 × 0） | [file] W:79–85 |
| 蓄力 | ADS 触发，2.25 s 5 档；`power_shot` 4.5 s 7 档、`quick_shot` 1.4 s 3 档、`instant_shot` 0.05 s 1 档（对泰坦固定 1200） | [file] WT:176–181, 440–454；W:17, 185–191 |
| 每次几枚 / 间隔 | 1；射速 0.9 /s；弹夹 6 | [file] WT:68, 147 |
| 涡旋 | `explosive_round` | [file] WT:162 |

**实测 [meas]**（`km_proj` `rg_0`、`rg_up3`）：10000 u/s；竖直加速度 −0.8 u/s² ≈ 0.001 × 750。

### 2.9 Scorch 铝热弹（`mp_titanweapon_meteor`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponBolt(pos, dir, 1.0, …)`（注释 `// 2200.0`） | [file] W/`mp_titanweapon_meteor.nut:463–466` |
| 初速 | `projectile_launch_speed` 2200；发射仰角偏移 `projectile_launch_pitch_offset` 2；不继承自身速度（0.0） | [file] WT/`mp_titanweapon_meteor.txt:177, 179, 182` |
| 重力 | `bolt_gravity_enabled 1`，`projectile_gravity_scale` 0.625（468.75 u/s² [推断]） | [file] WT:48, 178 |
| 寿命 | 未找到。脚本有 `METEOR_LIFE_TIME` 1.2 s 的空爆函数 `MeteorAirburst`，但**没有任何调用** | [file] W:43, 151–158（grep 只有定义） |
| 碰撞尺寸 | 0.5 → 0.075 s 16 → 0.18 s 22 → 0.18 s 插值到 24 | [file] WT:39–45 |
| 反弹 | `bolt_bounce_frac` 1.0；但碰撞回调只认第一次碰撞（之后全忽略） | [file] WT:46；W:436–439 |
| 直击 | 铁驭 310 / 泰坦 800（`pas_scorch_weapon` 泰坦 1000）；暴击关 | [file] WT:57–62, 69, 384, 404–405 |
| 爆炸 | 铁驭 50 / 泰坦 200；内 50 / 外 150；冲击力 15000 | [file] WT:66–67, 71–72, 141 |
| 射速 / 弹夹 | 1.7 /s / 1 | [file] WT:149, 153 |
| 涡旋 | `explosive_round` | [file] WT:164 |

**落地火团生成（`Proto_MeteorCreatesThermite`，第一次碰撞时调）：**

| 项 | 值 | 来源 |
|---|---|---|
| 基础速度 | 弹体速度方向 × min(速率, 2500) × 0.25（单人 0.35） | [file] W:162–173 |
| 底座火团 | 1 个 `prop_physics`（碰撞组 debris），寿命 = thermiteLifetimeMax 2.5 s；打在世界上时 `StopPhysics()` 原地不动 | [file] W:195–201, 349–387 |
| 散开的火团 | 4 个（`pas_scorch_weapon` 8 个）；每个速度 = 基础速度 + forward × fireSpeed + up × fireSpeed，方向角在 ±360° 三轴随机；fireSpeed 50（升级 200）；寿命各自随机 2.0–2.5 s（单人 × 1.25） | [file] W:184–193, 203–227 |
| 跳伤 | 每团落下 0.2 s 后开始，每 0.1 s 一次 RadiusDamage：铁驭 20 / 泰坦 100；半径 = max(45, 上一跳以来移动距离) | [file] W:16–17, 255–302 |
| 叠加 | 一发的所有火团共用一个"每脚本帧每目标一次"的伤害源 | [file] W:195；W/`mp_titanweapon_arc_wave.nut:274–282` |

**实测 [meas]**（`km_scorch`，服务端 10 Hz；详见 [SCORCH.md](SCORCH.md) §8.1–8.2）：玩家每发 9 个火团（默认带 Wildfire Launcher），敌方 5 个。底座打在世界上不动；散开的出生 350 – 830 u/s，**不弹跳**、贴地滑：陡落 4 – 80 u，贴地斜落顺弹道 120 – 390 u，打墙 55 – 90 u，打中泰坦被弹开 170 – 230 u；寿命 1.9 – 2.4 s。两发的火各一个伤害源，同一 0.1 s 各 100（叠加）；同一发的火团只算一次。

### 2.10 Ronin 霰弹（`mp_titanweapon_leadwall`）

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponBolt` × 8（`projectiles_per_shot` 8，代码上限 8），同帧 | [file] W/`mp_titanweapon_leadwall.nut:10, 60–93`；WT/`mp_titanweapon_leadwall.txt:120` |
| 图案 | 固定 8 个偏移（上下 ±0.2、横向 ±0.8 / ±0.65 / ±0.2 / ±0.2）× 0.05 × 随机 1.2–1.7；ADS 时 × 0.5 | [file] W:14–24, 61–72 |
| 初速 | 4400；继承自身速度 20 % | [file] W:73；WT:118 |
| 重力 | 脚本 `kv.gravity = 0.4`（注释旧值 0.09）；设置 `bolt_gravity_enabled 0`；哪个生效 **不确定** | [file] W:84；WT:142 |
| 寿命 | 每颗随机 0.30–0.35 s，消失时空爆（爆炸伤害没写 → 等于 0 [推断]） | [file] W:89；WT:78 |
| 碰撞尺寸 | 0.5 → 0.075 s 4 → 0.075 s 4 → 0.18 s 插值到 6 | [file] WT:132–138 |
| 反弹 | `projectile_ricochet_max_count` 0（`pas_ronin_weapon` 1） | [file] WT:54, 417；W:99–110 |
| 直击 | 铁驭 60 → 25 / 泰坦 100 → 75（近 600、远 1000）；暴击 × 1.5 | [file] WT:42–47, 114, 116 |
| 爆炸 | 内 16 / 外 32，但没写爆炸伤害 | [file] WT:110–111 |
| 射速 / 弹夹 | 2.5 /s / 4 | [file] WT:124, 145 |
| 涡旋 | `bullet`（投射物类，被接住后按 2.12 的 bullet 重发） | [file] WT:158 |

**实测 [meas]**（`km_proj` `lw_*`，服务端 10 Hz）：8 颗都是 4400 u/s；**竖直速度 0，没有重力**（`bolt_gravity_enabled 0` 生效，脚本的 0.4 不起作用）。腰射图案：仰角 ±0.7 … ±0.97°，水平 ±0.7 … ±0.9° 和 ±2.5 … ±3.8° 两档，和脚本的固定图案 × 0.05 × 1.2 – 1.7 相符。在 0.2 – 0.3 s 之间消失（≥ 880 u）。

### 2.11 Ronin 电弧波（`mp_titanweapon_arc_wave`）—— 贴地推进波，不是普通弹体

**它怎么推进：**

1. 按键时 `FireWeaponGrenade(pos, dir, 角速度 0, 引信 99, …)` 生成一个手雷实体；服务端立刻把它**冻住、藏起、不可伤、不实体**（`SetVelocity(0)`、`StopPhysics()`、`Hide()`、`NotSolid()`），这个实体只当伤害源和位置标记。[file] W/`mp_titanweapon_arc_wave.nut:69–70, 98–108`
2. 脚本 `WeaponAttackWave` 接管：方向去掉竖直分量后归一化（只在水平面推进）。[file] W/`_weapon_utility.nut:2885–2887`
3. 第 1 段：从发射点水平向前 112 u 打射线；之后每段从上一段地面点 + 80 u 出发，射向前方 112 u、比出发点低 40 u 的点。[file] W/`_weapon_utility.nut:2914–2925`
4. 前方通了：从射线终点往下 1000 u 找地，在地面点放一段（调 `CreateEmpWaveSegment`）；往下 1000 u 都没地 → 波结束。[file] 同上 `:2948–2967`
5. 前方被挡：再试"越过"射线（终点抬高 step × 0.577，约 30° 坡）；越过线也撞到世界 / 玩家 / NPC → 结束；越过通了 → 再往下找地放一段（爬上台阶）。[file] 同上 `:2975–3000`
6. 碰到涡旋：扣对方涡旋能量（Ion 涡旋按"被打中"，涡旋球按泰坦伤害 1000），这一步跳过，继续。碰到 A-Wall 类"放大"墙且方向不对 → 结束。[file] 同上 `:2928–2941, 2971–2972`
7. 每段之间 `WaitFrame()`；最多 15 段（`wave_max_count`），段距 112（`wave_step_dist`，蓄力版同值）。[file] 同上 `:2912, 2966, 3002`；WT/`mp_titanweapon_arc_wave.txt:53–56`
8. 脚本帧 0.1 s → 推进速度 ≈ 1120 u/s、15 段约 1.5 s、最远 1680 u [推断：10 Hz 依据见第 0 节第 5 条]。

| 项 | 值 | 来源 |
|---|---|---|
| 每段伤害 | 在地面点 RadiusDamage：铁驭 75 / 泰坦 1000（MP），内外半径都 112；不伤自己；只算刷子（`MASK_BRUSHONLY`）；同一波每个目标只吃一次（`onlyDamageEntitiesOnce`） | [file] W/`mp_titanweapon_arc_wave.nut:108, 127–162`；WT:93–96 |
| 剑核心中 | 伤害 × 1.5（`isChargedShot`） | [file] W:74–79, 133–142 |
| 命中效果 | `move_slow` 0.5、`dodge_speed_slow` 0.5，2.0 s（淡出 1.0） | [file] W:188–189 |
| 重力 / 寿命 / 尺寸 | 不适用（实体冻住）；引信 99；段的判定 = 半径 112 球 | [file] |
| 漂移键 | 文件写了（W 1、I 0.06、0.7–1.0 s、0–1），但实体冻住后不飞，**用不上** [推断] | [file] WT:36–41 |
| 涡旋 | `vortex_refire_behavior absorb`；`projectile_ignores_vortex mirror` | [file] WT:33, 123 |
| 冷却 | 耗 100（Thunderstorm 50）；`charge_time` 30 | [file] WT:64–66, 74, 216 |
| 相位中 | 不能放 | [file] W:60–61, 303–310 |

**实测 [meas]**（`km_proj` `arcwave`）：服务端看到那颗藏起来的手雷每 0.1 s 往前挪一次，1.4 s 共移动 1568 u（= 14 × 112），推进 1120 u/s 确认。

### 2.12 Ion 涡旋打回（`_vortex.nut`）

打回时机：松手或强制释放时同一帧内，对每条存下的投射物记录按原武器的 `vortex_refire_behavior` 各重发一次（没有间隔）。子弹类另外合成一次霰弹（`ShotgunBlast`）。[file] W/`_vortex.nut:992–1050`

| 类 | 发射 | 初速 | 重力 | 寿命 | 出发点 / 方向 | 漂移 | 来源 |
|---|---|---|---|---|---|---|---|
| `explosive_round`（40 mm、狙击、铝热…） | `FireWeaponBolt` | 8000 | `kv.gravity` 0.3（225） | 未找到 | 收集点 ±3 u 随机；视线向量 + (±0.15, ±0.15, ±0.075) 不归一化 | 无 | [file] W/`_vortex.nut:50–54, 1079–1108, 1142–1165` |
| `bullet`（投射物类，如 Ronin 霰弹、爆发核心） | `FireWeaponBolt` | 12000 | 0.0 | 未找到 | 同上；+ (±0.15, ±0.15, ±0.1) | 无 | [file] W:1110–1140 |
| `rocket`（各种导弹） | `FireWeaponMissile` | 1800 | 未找到 | 随机 2.6–3.5 s | 攻击位置、攻击方向（不加散布） | `InitMissileForRandomDriftForVortexLow`：W 0.3、I 0.085、直飞 0–0 s、半径 0.5–0.5（直接传，不夹 1）→ time_max 0，拉回段不生效，只有随机漂移 | [file] W:1167–1186；W/`_weapon_utility.nut:1427–1430`；[原生·Ghidra] RN:92, 101 |

共同：换成原武器的模型和尾焰，记住原伤害来源（再被接住能还原），`SetVortexRefired(true)`（原生改用 `projectile_vortex_vscript`）。[file] W/`_vortex.nut:1245–1257`

**重发伤害用谁的：** 脚本没写数值，由原生决定，**不确定**（KIT/`ION.md:7` 同样列为要实测）。Vortex Amplifier（`pas_ion_vortex`）把涡旋武器自己的伤害 × 1.35（子弹 35 / 140），投射物是否也乘 **不确定**。[file] WT/`mp_titanweapon_vortex_shield.txt:55–62, 306–311`

另：`grenade` / `grenade_long_fuse` 两类按 1500 u/s ± 0.2 随机、引信 1.25 / 10 s 重发（本表不覆盖泰坦，列出备查）。[file] W/`_vortex.nut:1188–1232`

**实测 [meas]**（`km_ion`，见 [ION.md](ION.md) §8.5）：

| 接住的 | 打回 | 速度 | 竖直加速度 | 散布 | 伤害（打泰坦，每发） |
|---|---|---|---|---|---|
| 40 mm | 弹体 | 8000 | −225（0.3 × 750） | 最大约 10° | 330（原武器值） |
| 铝热 | 弹体 | 8000 | −140.6（0.3 × 0.625 × 750，两个倍数相乘） | 同上 | 没打中 |
| 狙击（不蓄力） | 弹体 | 8000 | — | 同上 | 250（蓄力加成不带过来），暴击 375 |
| 霰弹弹丸 | 弹体（bullet） | 12000 | — | 同上 | 90 |
| 火箭齐射 / 追踪导弹 | 导弹 | 1800 | 0 | 0.1 – 0.2° | 250 / 350（原武器值） |

伤害用原武器的值，每发一个伤害事件；全部在松手后第一个服务端帧出现。

### 2.13 BT-7274 远征装（战役）

**怎么确定远征装是哪几把：** 单人装备表在 `datatable/titan_properties.rpak`（二进制，没解出来；FE/`sp/_sp_sh_weapons.gnut:40`）。旁证：
- 起始装备 `SP_STARTING_TITAN_LOADOUT_KIT = "mp_titanweapon_xo16_shorty"`，菜单注释"Expedition … you start with it"。[file] FE/`sh_consts.gnut:2600`；FE/`ui/menu_sp_loadout_titan.nut:304–306`；SPB/`_sp_loadouts.nut:302, 768–769`
- 爆发核心 = `mp_titancore_amp_core`：图标 `titan_core_burst_core`、语音 `burstCoreOnline` / `burstCoreActivated`。[file] WT/`mp_titancore_amp_core.txt:9–10, 76–77`
- 单人关卡预载 `mp_titanweapon_shoulder_rockets`、`mp_titancore_amp_core`、`mp_titanweapon_xo16_shorty`。[file] `client_sp_beacon/scripts/vscripts/sp/autoprecache/sp_beacon_autoprecache.nut:45, 62, 68`
- [推断] 远征装 = XO-16 短管 + 多目标导弹 + 爆发核心。单人包里没有 `sp_*` 或单独的 BT 武器文件；`client_sp_training` 里这三把的 .txt / .nut 和多人包逐字节相同（`diff -q` 无差别），区别只在 `SP_BASE` 和脚本里的 `IsMultiplayer()` 分支。

**BT 多目标导弹（`mp_titanweapon_shoulder_rockets`，单人分支）：**

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | 有锁：SmartAmmo 张开收拢 + 追踪；**没锁：单发 `FireWeaponMissile(…, 1000, …)`，不调漂移初始化，连发数设 1** | [file] SPT/`vscripts/weapons/mp_titanweapon_shoulder_rockets.nut:96–108` |
| 初速 | `SHOULDERROCKETS_MISSILE_SPEED` 1000 | [file] 同上 `:15, 64` |
| 追踪 | H = 250，`SetHomingSpeeds(250, 250)` | [file] 同上 `:66–67`；W/`sh_smart_ammo.gnut:315` |
| 寿命 | 10 | [file] W/`sh_smart_ammo.gnut:307` |
| 张开收拢 | 张开 10°、0.2 s；过渡 0.0；收拢 −10°、0.0 s；转直 −0.2；随机散布 true | [file] 同上 `:14–28, 69` |
| 漂移 | W 7、I 0.96、直飞 0.9–1.2 s、半径 0–1 | [file] SPT/`weapons/mp_titanweapon_shoulder_rockets.txt:33–38` |
| 锁定 | 同多人键（搜索角 80、4000 u、每把 0.3 s、最多 8 目标、单个重甲 12 把、泰坦挡视线、只在按住时搜） | [file] SPT/…txt:261–293 |
| 直击（SP_BASE） | 铁驭 280 / 泰坦 150（近 800 远 1200） | [file] SPT/…txt:96–101 |
| 爆炸（SP_BASE） | 铁驭 100 / 泰坦 100；外 200（内半径没写） | [file] SPT/…txt:102–105 |
| 射速（SP_BASE） | 30 /s；连发后 0.7 s；冷却 18 s、延迟 2 s | [file] SPT/…txt:93, 113–117, 127 |
| 涡旋 | `rocket` | [file] SPT/…txt:136 |

**BT 爆发核心（`mp_titancore_amp_core`）：**

| 项 | 值 | 来源 |
|---|---|---|
| 发射 | `FireWeaponBullet(pos, dir, 1, largeCaliber | DF_STOPS_TITAN_REGEN)`：**命中扫描子弹，不是投射物** | [file] W/`mp_titancore_amp_core.nut:106` |
| 连发 | 100 发（`burst_fire_count` 100）× 20 /s = 5.0 s；`core_duration` 5.5；起手 `chargeup_time` 1.85 | [file] WT/`mp_titancore_amp_core.txt:33–35, 59–61`；W:108–115 |
| 伤害 | 铁驭 150 / 泰坦 150（近 1800 远 3000 同值）；爆头 1.5、爆头距离 5000；暴击 × 1.1 | [file] WT:131–136, 160, 177–180 |
| 爆炸键 | 内 10 / 外 50，100 / 100；对命中扫描子弹是否生效 **不确定** | [file] WT:139–142 |
| 尺寸键 | `bolt_hitsize` 8.0 写了，但 `FireWeaponBullet` 不生成 bolt，[推断] 用不上 | [file] WT:138 |
| 散布 | 腰射 1.2、ADS 0.7，每发 +0.3，最多 +2 / +1 | [file] WT:144–149, 183–197 |
| 自身 | 期间转向 −25 %、移动 −40 %（核心 + 起手 + 0.5 s 淡出） | [file] W:43–48 |
| 涡旋 | `bullet` | [file] WT:173 |
| 重力 / 寿命 / 追踪 / 漂移 | 不适用 | — |

---

**BT 远征装能不能在私服实测：** 多人模式没有 BT（只有 7 台多人泰坦），这两把武器的文件和多人包逐字节相同，只有 `SP_BASE` 数值和脚本里 `IsMultiplayer()` 分支不同。多人版多目标导弹已实测（§2.5）；单人版的不同点（初速 1000、追踪 250、张开 10°、无锁只发 1 枚）只能照文件 [file]。爆发核心是命中扫描子弹，没有弹道可测。

## 3. 脚本给不了、要实测的（11-13 补测后）

**已补上（[meas]）：** 重力单位 × 750；霰弹实际无重力；火箭齐射 / 多目标导弹的张开收拢曲线、远距离漂移；多目标导弹锁定节奏、无锁枚数；电弧波推进速度；涡旋打回的速度、重力、散布、伤害取值；铝热火团的滑动和叠加；直击泰坦只有一个伤害事件。

**还缺（下表原文保留）：**
- 追踪导弹（Tone）和飞行核心火箭的**逐帧**转弯曲线：客户端只能列 `rpg_missile`，但本地玩家自己的导弹在 10 Hz 服务端数据里能看到大致路径（§2.7 实测）；Tone 追踪导弹这次没发出去（`km_proj` `tr_walk`：标记没满 3 层），用 11-08 的命中时刻（0.58 – 0.94 s）。
- 导弹的碰撞尺寸（文件里没有，测不出来）；40 mm、狙击、铝热、集束导弹的寿命（这次都在 2.3 km 内撞墙）。
- 集束导弹子爆炸的落点分布；齐射核心 3 枚一组的扇形（10 Hz 只有大致范围，§2.3）。
- 弹体类的逐帧曲线（客户端列不出 `crossbow_bolt`）。都是直线加重力，10 Hz 足够核对。



| 投射物 | 只能实测的量 |
|---|---|
| 通用 | ① `kv.gravity` / `projectile_gravity_scale` 是否就是 × 750（打一发记 z(t) 拟合）；② 设置里有 `projectile_launch_speed` 时脚本传的数是不是倍率（铝热、飞行核心、齐射核心记出膛速率）；③ 没写寿命的 bolt / 导弹（40 mm、狙击、铝热、集束、涡旋 bolt）的原生默认寿命或射程上限；④ 导弹的碰撞尺寸（文件里全没有）；⑤ 没写 `_titanarmor` 时对泰坦的直击值（齐射、追踪导弹）；⑥ 直击和爆炸是否都吃 |
| 40 mm | `grenade_bounce_*` 对 bolt 是否生效；Burst Loader 三档的真实时刻；mortar 的实际弹道（4.0 重力、10 s 寿命） |
| 追踪导弹 | 漂移键很大（W 70、I 10.96、半径 5–10）在有目标时是否还生效、实际蛇形幅度；按距离改 H 后的真实转弯半径和命中时刻（KIT 已测 0.58–0.94 s）；有没有冲过头丢追踪 |
| 齐射核心 | 0.8–1.1 的初速分布；累加偏移下 3 枚的真实扇形；导引点粘目标时的转弯；60 枚里有几枚因 60° 规则丢追踪 |
| 火箭齐射 / 多目标导弹 | **张开收拢的真实曲线**（原生 `InitMissileExpandContract`：每段插值方式、负的 straightLerp −0.2 是什么意思）；漂移实际幅度；多目标导弹没锁时的枚数；H 550（多人）/ 250（单人）的实际转弯半径 |
| 集束导弹 | 子爆炸的真实时刻分布（公式给 0.45–1.05 s 间隔）和落点分布；物理小弹飞行是否被地形挡；撞涡旋时当场起爆的伤害 |
| 飞行核心火箭 | H 2000 飞向固定点的转弯半径；左右交替偏移的实际扇形；对 dash 玩家 H2 = 0 对位置目标是否适用 |
| 狙击弹 | 0.001 重力和尺寸增长在远距离的影响（可忽略程度） |
| 铝热 | **火团滚动**：`prop_physics` 的摩擦、弹跳、滚多远；底座打在非世界物体上时会不会跟着滚；火团落地前 0.2 s 的下落；半径随移动距离变大的实际大小 |
| 霰弹 | 0.4 重力和 `bolt_gravity_enabled 0` 哪个生效（打 1000 u 外的墙量落点） |
| 电弧波 | 每段的真实间隔（确认 0.1 s → 1120 u/s）；台阶 / 坡 / 跨坑的推进行为；`MASK_BRUSHONLY` 下能不能隔着物件打中 |
| 涡旋打回 | **重发投射物的伤害用谁的**（原武器的还是涡旋的、是否 × 1.35）；收集点和散布的实际分布；rocket 的随机漂移幅度 |
| BT | 远征装组成要用游戏内菜单或解出 `titan_properties.rpak` 确认；多目标导弹单人版无锁单发的实际表现；爆发核心爆炸键是否生效 |
