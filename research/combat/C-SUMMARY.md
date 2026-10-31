# 批次 C 汇总：投射 / 特殊武器 / 掩体类

会话 `combat-c`，2026-10-31。第一波静态研究：只读 `research-src/s21-platform/scripts/`（脚本、武器 `.txt`、本地化）和 HSD-Unity 战斗层，没启动游戏、没改 Unity。每项按 `SYSTEM-RECORD-TEMPLATE.md` 第 0–6 节写。

## 1. 每项一行

分类：效 = 好技能（效果），视 = 可视化，系 = 系统。

| # | 技能 | 记录 | 一句话结论 | 分类 | HSD |
|---|---|---|---|---|---|
| 1 | Valkyrie 战术 Missile Swarm | [valkyrie-missile-swarm/SYSTEM.md](valkyrie-missile-swarm/SYSTEM.md) | 12 枚（升级 20），先惰性抛射 0.55–0.85 s 再点火弯飞；每枚 15 伤害 / 150 u（内外同），5 s 内同目标后续 ×0.2；晕眩 2 s（move_slow 0.75、turn 0）+ 淡出 1.5 s；飞行时间按距离对数映射 2–4 s，行 / 列错开 0.15 / 0.05 s；冷却 25 s | 效 视 系 | 未实现 |
| 2 | Ballistic 战术 Whistler | [ballistic-whistler/SYSTEM.md](ballistic-whistler/SYSTEM.md) | 5° 锥 3000 u 锁定（0.3 s，4 s 看不见丢锁），锁上 1500 u/s 追踪、否则 3000 u/s 直飞；打中人 → 12 s 过热 debuff（开枪积热，满 100 扣 30 不致死）；打中墙 → 1 s 后 150 u 一次性感应区（10 伤害 + debuff）。积热在引擎里。**对普通 NPC 无效**，建议 AI 版"攻击积热 → 硬直 + 30" | 效 视 系 | 未实现 |
| 3 | Ballistic 大招 Tempest | [ballistic-tempest/SYSTEM.md](ballistic-tempest/SYSTEM.md) | 30 s 光环（半径 3620 u），队友进入就上 buff（时长 = 施法者剩余，离开不掉）：换弹 ×0.6、无限备弹、持枪 speed_boost 0.075；Sling 换成金色版并在结束时换回；击杀 / 击倒全队 +5 s | 视 系 | 未实现 |
| 4 | Vantage 大招 Sniper's Mark | [vantage-snipers-mark/SYSTEM.md](vantage-snipers-mark/SYSTEM.md) | 50 伤害（爆头 ×1.5）、34000 u/s 下坠弹；命中标记 10 s，再打 ×2.5（S25.1 规则，旧 ×2），队友 ×1.15；擦过 120 u 有特效；开枪后 10 s 内开镜才有反光。**本地构建没有禁疗**（死代码）。`bow_ult_missile` = Sparrow 大招，无关 | 效 视 系 | 未实现 |
| 5 | Rampart 大招 Sheila | [rampart-sheila/SYSTEM.md](rampart-sheila/SYSTEM.md) | 手持：开镜 1.25 s 转满才开火（"转速" = 开镜进度，没有射速爬升），20 发/s × 14；扩散 3° 起每发 −0.18° 越打越准；放置：350 血炮台，最多 3 台，EMP 停 15 s，近战两下爆，捡回 +50%；放置部分有 SDK 改动 | 效 系 视 | 未实现（可借 `Boosts.cs` 哨戒炮） |
| 6 | Rampart 战术 Amped Cover | [rampart-amped-cover/SYSTEM.md](rampart-amped-cover/SYSTEM.md) | 底座（120 → 400 血）+ **2 s**（不是 3 s）后升起 175 血的盾；盾单向放行（−0.55）并给子弹加 `amped_damage` ×1.2；同一颗子弹穿第二面盾会打碎它；最多 4 面、3 格 × 20 s。更正 APEX-REPORT 2.9 两处 | 效 系 视 | **已有部分**：`Tacticals.cs` `AWall` Rampart 选项（3 s、无底座） |
| 7 | Gibraltar 战术 Dome of Protection | [gibraltar-dome-of-protection/SYSTEM.md](gibraltar-dome-of-protection/SYSTEM.md) | 投掷落地展开，12 s；碰撞组"挡武器不挡人"，双向挡子弹和爆炸，无血，只被 EMP 摧毁；240 u 触发器给"在罩里"状态（快速救人）；`SPF_BLOCKS_AI_NAVIGATION`。`area_cloak` 只有 `.txt` 没脚本，无关 | 系 视 | 未实现 |
| 8 | Gibraltar 被动 Gun Shield | [gibraltar-gun-shield/SYSTEM.md](gibraltar-gun-shield/SYSTEM.md) | 开镜时前臂护盾（半径 18、高 32、正面 85°），血 = 共享能量；打光碎、溢出伤害（非爆炸）打到本人；10 s 无伤**一次补满**（疑似 SDK 改写） | 系 视 | 未实现 |
| 9 | Seer 战术 Focus of Attention | [seer-focus-of-attention/SYSTEM.md](seer-focus-of-attention/SYSTEM.md) | 胸前到 2362 u 的管子（半径 200，胶囊判定），1 s 预警后引爆：沉默 8 s + 打断 0.25 s + 0.5 s 轻减速 + 扫描 2.5 s；伤害默认关（开时 5）。**对普通 NPC 只扫描** | 效 视 系 | 未实现（可借 `Scan` 的标记字段） |

## 2. 可拆出的公共部件

本批新写（`_shared/C-*`）：

| 部件 | 文件 | 用到的 | HSD 建议落点 |
|---|---|---|---|
| 锁定选目标 + 追踪投射物（+ Valk 弯路径） | [_shared/C-LOCKON-HOMING.md](_shared/C-LOCKON-HOMING.md) | Whistler、Valk | 新 `Combat/Homing.cs`（`LockOnSelector`、`HomingProjectile`、`CurvedMissile`），起点 `SmartPistol` |
| 光环 buff | [_shared/C-AURA-BUFF.md](_shared/C-AURA-BUFF.md) | Tempest、Amped Cover 升级 | 新 `Combat/Buffs.cs` `AuraBuff` |
| 伤害修正链（标记、递减、穿盾、溢出、不致死） | [_shared/C-DAMAGE-MODIFIERS.md](_shared/C-DAMAGE-MODIFIERS.md) | Vantage、Valk、Rampart、枪盾、Whistler | `CombatSim` 伤害结算加 `IDamageModifier` 链 |
| 挡子弹的护盾实体 | [_shared/C-BULLET-BLOCKING-SHIELD.md](_shared/C-BULLET-BLOCKING-SHIELD.md) | 护罩、枪盾、Amped Cover | 扩展 `IWallBlocker` → `IShield` |
| 放置物生命周期 | [_shared/C-PLACEABLE-DEPLOYABLE.md](_shared/C-PLACEABLE-DEPLOYABLE.md) | Amped Cover、Sheila、护罩、Whistler 感应区 | `Deployable` 基类 |

引用其他批次已有的（没重复写）：状态效果框架 `_shared/E-STATUS-EFFECT.md`、EMP 减速 `_shared/B-electric-emp.md`（Valk 晕眩用的是同一个 `GiveEMPStunStatusEffects`）、沉默 / 打断 `revenant-silence/SYSTEM.md` 3.2.2（Seer 用同一个 `SilenceThink`）、设备登记表 `_shared/D-DEVICE-REGISTRY.md`、声呐 `_shared/E-SONAR-HIGHLIGHT.md`。

## 3. 最重要的实测项（第二波）

按对 HSD 的影响排：

1. **Whistler 积热速度 / 降温速度**（引擎实现，只有部分武器写了 `player_overheat_per_bullet`）。不测就没法给 AI 版定"每次攻击加多少热"。测法见 `ballistic-whistler` 第 5 节第 1 条。
2. **Valk 网格到底几行几列**（原生 `GetWeaponMissileMultipleTargets`；脚本算法 5 列取 12，本地化说 4x3 → 3x5）。俯视截图落点即可。
3. **move_slow 严重度语义**（0.75 是 ×0.25 还是 ×0.75），Valk / Seer / Sparrow 都依赖。和批次 E 的同一条一起测。
4. **Amped Cover 两个 playlist 开关在本地是否 true**（2 s 升盾、120 起始血），以及放置距离 128 还是 256。
5. **Gibraltar 护罩半径和是否不可破**、**AI 是否绕开**（`SPF_BLOCKS_AI_NAVIGATION`）——决定 PvE 里罩是不是绝对安全区。
6. **Sheila 扩散收紧曲线**（负 spread kick 的语义）。
7. **Vantage 增伤和爆头的先后**（期望 50 × 1.5 × 2.5 = 187）。

## 4. 遇到的问题

- **R5 的控制效果大多只对玩家**：Whistler（debuff、感应区）、Seer（沉默、打断、硬直、伤害）、Vantage（标记）对普通 NPC 都无效或只剩扫描（训练假人例外）。PvE 版必须重新定义对 AI 的效果，各记录第 6 节给了建议并标"写进 R5-DIFF"。
- **本地脚本比 S21 新**：Vantage 默认开 `vantage_s25_1_buffs_enabled`（S25.1 规则）。客户端和 dedi 是否同一份脚本要核对。
- **SDK 改动（明确有注释的）**：Sheila 放置炮台上炮逻辑（`mp_weapon_mounted_turret_placeable.nut:662`"GetTurretWeaponX doesn't exist in s3"）、炮台弹量继承被注释（`mp_weapon_mounted_turret_weapon.nut:114`）、Sheila 网络函数（`mp_weapon_mobile_hmg.nut:11`、`:386`）、Rampart / Gibraltar 的悬浮载具挂载（`mp_weapon_cover_wall.nut:555`）、穿透回调（`sh_codecallbacks.gnut:860`）、沉默里的 Newcastle 判断（`sh_silence.gnut:201`）、9 个 `.txt` 的"Disabled on dedi"回调。**疑似改写**：枪盾"10 s 一次补满"（`mp_ability_gibraltar_shield.nut:293-302`）；`mp_weapon_bow_ult_missile.nut`（Sparrow）整份像社区复刻。
- **更正已有研究**：APEX-REPORT 2.9 的"升盾 3 s（升级 2 s）"和"底座起始 45"是旧开关值，默认是 2 s / 120（见 `rampart-amped-cover` 第 4 节末）。没有改 APEX-REPORT 本身（不在本批文件夹内），交 Leader 决定。
- **C0 过滤表要改的**：Vantage 行写了"禁疗"，本地构建没有；Gibraltar 护罩的 `area_cloak` 无关。C0 不归本批改，交 Leader。
- 几处数值字段和"正式冷却"对不上（护罩 `ammo_timed` 13 / 13 / 回充 1；Vantage 弹匣 240 / 每发 40），已列为实测。

共享日志（会话 `combat-c`）已写：Valk 数据、Whistler 对 NPC 无效、Vantage 无禁疗 + S25.1、`bow_ult_missile` 归属、APEX 2.9 更正、本汇总。
