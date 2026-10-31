# 批次 A 汇总：轰炸 / 投掷类技能（静态系统记录）

会话 combat-a，2026-10-31。只读脚本和武器 `.txt`（`research-src/s21-platform/scripts/`），没启动游戏、没改 HSD-Unity。每项的数值、行号、伪代码都在各自 `SYSTEM.md`；本页只做索引和结论。

## 1. 每项一行

| # | 记录 | 一句话结论 | 分类 |
|---|---|---|---|
| 1 | [bangalore-rolling-thunder](bangalore-rolling-thunder/SYSTEM.md) | 信号弹落地 2 s 后，6 排 × 6 枚火箭沿扔的方向铺满 2750 × 2750 u，每枚插地 6 s 后炸（40，r350 不衰减，shellshock 6 s）。`rolling_thunder_piece` 是 Maggie 破坏球的、`sonar_dart` 是 Sparrow 的，都和滚雷无关（只是名字 / 模板撞了） | 好技能、系统 |
| 2 | [gibraltar-defensive-bombardment](gibraltar-defensive-bombardment/SYSTEM.md) | 信标落地 2 s 后每秒一波、6 波 36 发落在 256–768 u 的"甜甜圈"里，落地即爆（40，r256，shellshock 4 s）；"范围 +20%"升级在本地脚本里不生效 | 好技能、系统 |
| 3 | [fuse-knuckle-cluster](fuse-knuckle-cluster/SYSTEM.md) | 补 APEX-REPORT 2.7：两波 45 次爆炸、命中计数两波共用（同一人上限约 74）、第 2 波第 1 层延迟 0.4 不是 0.5、第 2 层 yaw 215 疑似 315 笔误、AI 危险区 r187.5 | 好技能、系统 |
| 4 | [fuse-motherlode](fuse-motherlode/SYSTEM.md) | 定速低弧解 + 水平距离到了就空爆，15 颗小炸弹落成毛边环，相邻两颗沿地面连火墙（预燃 1 s + 烧 15 s）；碰一下 75、站着 95 / 4.15 s，减速 0.25，NPC 也吃 | 好技能、系统、可视化 |
| 5 | [fuse-grenadier](fuse-grenadier/SYSTEM.md) | 远投 mod 还换持握模型和声音；mod 挂在玩家上，切换 = 收回再给；抛物线 2 次弹跳只对破片；默认可能是普通投掷 | 系统 |
| 6 | [caustic-nox-gas-trap](caustic-nox-gas-trap/SYSTEM.md) | 投掷 → 展开 → 布防 → 视线触发 → 放毒 11 s → 移除的陷阱状态机；最多 6 个挤掉最旧；打底座（hitbox 0）拆、打罐体放毒；支持 NPC 主人 | 好技能、系统 |
| 7 | [caustic-nox-gas-grenade](caustic-nox-gas-grenade/SYSTEM.md) | 落平地或弹 10 次后 1 s 放大号毒气云（r375，15 s + 2 s）；伤害 / 减速全部走公共毒气云 | 好技能 |
| 8 | [maggie-riot-drill](maggie-riot-drill/SYSTEM.md) | 原生穿墙 trace 求出口，钉墙 1 s 后在墙另一侧沿视线喷 r130 × 224 圆柱火区 8 s（20 DPS），玩家要出口视线，NPC 不要 | 好技能、系统、可视化 |
| 9 | [maggie-wrecking-ball](maggie-wrecking-ball/SYSTEM.md) | 自走物理球 + 路径邻近爆炸 + 每 0.8 s 甩一片 60 s 的加速片（+0.15、滑铲摩擦 −0.5）；**本地服务端滚动代码疑似 SDK 重写，伤害定义 300 和注释 20 不符** | 好技能、系统、可视化 |

## 2. 可拆出的公共部件

单独成文的（`_shared/`）：

| 部件 | 文件 | 用到的技能 | HSD 里能复用的现有类 |
|---|---|---|---|
| 天降炮击调度器（DetCord 线 / Focused 圆 / Creeping / AirBurst + 落点取样） | [_shared/A-bombardment.md](_shared/A-bombardment.md) | 1、2（4、9 借它的副手槽函数） | 新建 `BombardmentScheduler`；弹头用 `ThrownItem`，伤害用 `CombatSim.Explode` |
| Shellshock（减速 0.25 + 模糊 + 调色） | [_shared/A-shellshock.md](_shared/A-shellshock.md) | 1、2、9 | `CombatUnit.slowScale` / `slowUntil` |
| 毒气云（24 采样圆、曝光计时、递增伤害、减速升降、挡视线） | [_shared/A-gas-cloud.md](_shared/A-gas-cloud.md) | 6、7 | 新建 `GasCloud.cs`；减速复用 `slowScale` |
| 只在平地立住的投掷罐 | [_shared/A-ground-canister.md](_shared/A-ground-canister.md) | 1、2、7（4、铝热剂相近） | `ThrownItem.OnBounce`（`Thermite` 已有同样写法） |

写在各自记录里、值得以后拆出来的：

- **抛物线求解 + 准星落点 + 定距空爆**（4 的 3.2.1–3.2.2）→ 放进 `Throw.cs` 的 `Ballistics`。
- **沿地面走线 + 线段胶囊判定 + 燃烧 DoT**（4 的 3.2.5–3.2.7）→ 铝热剂、火墙类通用。
- **递归子弹树 + 每目标命中衰减**（3 的 3.2.1–3.2.2）→ HSD 自创"投掷物发射器"可直接用。
- **陷阱状态机 + 数量上限挤旧**（6 的 3.2.1）→ `Satchel` 已有"挤旧"写法。
- **视线锥触发**（6 的 3.2.2）。
- **穿墙求出口 + 定向圆柱伤害区 + 出口视线**（8 的 3.2.1、3.2.3）。
- **一路投放 + 加速 / 低摩擦区**（9 的 3.2.4–3.2.5）→ 加速片部分可以先做，但要移动电机开"速度倍率 / 摩擦倍率"接口。
- **AI 危险区**（2、3、4、8 都建 `AI_CreateDangerousArea_Static`）→ HSD 敌人 AI 以后要读一张"危险圈"表。

## 3. 最重要的实测项（第二波）

按对 PvE 设计的影响排序。全部在火力训练场用 runner 记录实体 / 血量 / 速度即可，不需要第二个玩家。

1. **毒气对 NPC**：减速有没有、离开再进来伤害倍率是否继续涨、伤害有没有上限 10（`_shared/A-gas-cloud.md` 第 5 节 1–2）。PvE 敌人全是 NPC，本地脚本里 NPC 分支看起来是坏的。
2. **破坏球伤害 300 还是 20、球怎么滚、爆几次**（`maggie-wrecking-ball` 第 5 节 1–3）。
3. **`move_slow` 严重度 → 实际速度倍率**（0.25 到底是 ×0.75 吗；shellshock、毒气、火焰环都用）。
4. **炮击导弹速度（`speed = 1` 是否倍率）和实际发数**：滚雷 36 还是 30、防御轰炸是否 6 波 36 发、甜甜圈分布（`_shared/A-bombardment.md` 第 5 节）。
5. **火焰环燃烧时间线**（75 / 95，站着是否每 4.15 s 重来）和 NPC 减速（`fuse-motherlode` 第 5 节 1）。
6. **Riot Drill 出口区域几何**（墙后 dummy 摆 100 / 200 / 300 u）和失败结果是否在地图原点生成区域（`maggie-riot-drill` 第 5 节 1–2）。
7. **毒罐能不能被 NPC 触发**（`caustic-nox-gas-trap` 第 5 节 1）。
8. 集束弹子弹树俯视图（yaw 215）和同一人 74 上限（`fuse-knuckle-cluster` 第 5 节 1–2）。

## 4. 遇到的问题

- **SDK 重写**：明确有社区痕迹的——`sh_shellshock.gnut`（"Match S21 original"注释，只改客户端健壮性）、`sh_gas.gnut`（`_Copy` 版函数和电桩调试输出）、`mp_weapon_dirty_bomb.nut`（mitosis 咖啡 mod、手写扣血）、`mp_ability_wrecking_ball.nut`（`prop_physics` + 脚本推、`CafeMod_*`、空的 `BeginProjectileFire`）。轰炸两项、集束弹、火焰环、钻头没看到社区注释（推断原版）。
- **疑似 bug / 不生效**（照抄前要决定是否照抄，已在各记录第 6 节给出开关建议）：
  - Gibraltar 范围升级不生效（`GetRadius` 返回常量）；
  - 毒气 NPC 曝光永不清零、伤害无上限（`GAS_CLOUD_DMG_MAX` 未用）；
  - 集束弹 yaw 215；
  - Riot Drill 失败结果出口未赋值、威胁箭头对敌人不显示；
  - 破坏球 shellshock 时长公式反了、两个 playlist 键共用、铝热剂升级空函数、扫描升级只剩喊话；
  - 火焰环揭示扫描调用被注释、威胁箭头 `shouldBeVisible` 不复位；
  - 毒罐 `damagedef_dirty_bomb_explosion`（750）没有调用者。
- **名字误导**：`mp_ability_rolling_thunder_piece` 不是 Bangalore 的（是 Maggie 破坏球内部代号 RollingThunder）；`mp_weapon_sonar_dart.txt` 抄了滚雷的本地化键。
- **共用副手槽**：轰炸两项、火焰环、破坏球都用 `VerifyBombardmentWeapon` 抢 `OFFHAND_RIGHT`，同一玩家同时用两种会互相打断（推断；HSD 不会有这个问题，但实测时注意别连着放）。
- **本地化**：retail 键是哈希，名字能对上（"Rolling Thunder"、"Knuckle Cluster"…），描述文本大多对不上键，引用时只用了能确定的几条。
- 任务里提到的"Fuse 被动"已经大部分在 APEX-REPORT 2.7，补充部分很少，按要求写短。
- 没有写 `DECISIONS.md` / `R5-DIFF-ARCHIVE.md`：本批没有做决定、没改 Unity；各记录第 6 节列了"以后实现时要进 DIFF 档案的差别"。
