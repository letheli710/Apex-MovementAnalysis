# 攻击研究第二波 · R5 本地实测（W2-RUNTIME）

会话 `combat-w2-rt`，2026-11-01。本地 R5Flowstate（S21 客户端 + S3 dedi + SDK 混合构建），火力训练场 `mp_rr_canyonlands_staging_mu1`，离线。工具在 [w2-runtime/](w2-runtime/)；原始记录（每次运行一个 `runs/<时间>_<名字>.txt`）在私有仓库 `HSD-RawData` 的 `apex/research/combat/w2-runtime/runs/`（D-76），公开仓库只放本文和脚本。

标注：**[R5]** = 本地实测值；**[脚本]** = 第一波读脚本得到的值；**差** = 两者不一致的地方。

## 总表

| # | 问题 | 结论 | 和静态结论 |
|---|---|---|---|
| 0 | 本地能不能刷 NPC、走动、开火 | **能刷、能走，不能开火。** `npc_dummie`（`npc_dummie_combat`）、`npc_prowler` 能刷，`SetEnemy(player)` 后会跑过来（dummie 停在 ~268 u，prowler 贴到 50 u），但从不开火 / 近战（`CanSee(player)` 恒 0，补满弹匣也不打）。`CreateSpectre` 一刷 dedi 就卡死（`RandomizeHead` 报错 + 模型缺失）。 | 新信息 |
| 1 | `move_slow` 严重度语义 | **速度 ×(1 − s)**，玩家和 NPC 一样。0.25 → ×0.75，NPC 的 0.8 → ×0.2。s ≥ ~0.06 时玩家**不能冲刺**（按走速乘）。多个同时：**取最大**。 | 0.25 = ×0.75 对；NPC 0.8 是 ×0.2（第一波两种都写了，现在定了） |
| 2 | Horizon 黑洞 | 玩家拉力 ≈ 3.2.2 公式：敌人被拉时速度直接变成 **≈390 u/s 向心**（公式 clamp 400，差 −2.4%），强拉 0.8 s 内按键无效；之后逃跑限速 **127 → 103 u/s**（d = 100 → 300，公式 122.5 → 97.5，高 4–7 u/s）。**NPC 完全不被定身**：触发器碰到了（`IsTouching` = 1），但 `in_black_hole_field` 一直 0、不挂 mover。 | 玩家部分一致（小差见 §2）；NPC 部分**不一致**：本地不生效 |
| 3 | 毒气对 NPC | **不减速**；每 1 s 伤害 **5 + floor(t / 2)**，**没有上限**（25 s 时 17）；离开 10 s 再进来**接着涨**（37 s 回来第一跳 23）。 | 一致（NPC 分支不重置、不减速、无上限） |
| 4 | S3 dedi 有没有暗影状态 | **有。** `EnterShadowForm()` 可用（`IsShadowForm` → true）；Forged Shadows 能放（75 血护盾壳、`shadow_form` 状态）。**Death Totem 本地用不了**：武器 `mp_ability_revenant_death_totem` 没加载（"Can't find weapon … may need to be precached"）。 | "可能没有暗影状态"的担心排除；Death Totem 改成"本地武器缺失" |
| 5 | D.O.C. 无人机轨迹 | **= 公式。** 站立偏移 后 37.3 / 右 62.2 / 高 70.0（0 差）；稳态落后：走 19.9 u（公式 19.9）、冲刺 35–37 u（公式 36.5）；pitch 10° / 15° / 20°（公式 v/400·20°）；转身 roll 封顶 17°。 | 一致 |
| 6 | Ash 拴住 | **本地完全无效。** 命中 10 伤害 + move_slow 0.5（~1.6 s + ~0.9 s 淡出），锚点留在原地 ~7 s；dummie 走到离锚点 **552 u**（半径 210 的 2.6 倍），没有任何拉回或链子伤害。 | 一致（静态："本地被注释掉"） |

## 0. NPC（第 0 项）

[R5]（`npc_one.nut`、`npc_fight.nut`）：

| 类型 | 能刷 | 血 | 武器 | 追玩家 | 开火 / 近战 |
|---|---|---|---|---|---|
| `npc_dummie` + `npc_dummie_combat` | 能 | 120 | `mp_weapon_rspn101`，弹匣 0 | 能，~280 u/s 跑到离玩家 268 u 停 | 不打（补满 21 发，8 s 弹匣不变，玩家血 / 盾不变） |
| `npc_prowler` | 能 | 120 | 无 | 能，贴到 50 u | 不咬（50 u 处停 6 s，无伤害） |
| `npc_spectre`（`CreateSpectre`） | **dedi 卡死** | — | — | — | — |

- 不 `SetEnemy` 时 NPC 只在附近慢走（~25–55 u/s），`GetEnemy()` 为空。`CanSee(player)` 全程 0，推断 AI 视觉 / 开火在这个构建里不工作。玩家本身能受伤（脚本 `TakeDamage` 20 → 盾 50 → 30）。
- spectre：`CommonMinionInit → RandomizeHead` 报 `FindBodyGroup` 不存在，接着 `pilot_medium_loba.rmdl` 和 `error.rmdl` 都加载失败，dedi 不再响应，只能重启。soldier / stalker 走同一个 `CommonMinionInit`，**没敢试**（可能同样卡死）。
- 火力训练场有 realm：自己刷的 NPC 默认不在玩家的 realm，黑洞 / 陷阱这类按 realm 判断的效果要先 `n.RemoveFromAllRealms(); n.AddToOtherEntitysRealms(p)`（之后的测试都这样做了）。NPC 的 `GetVelocity()` 读出来是 0，速度一律用位置差算。

**对后面各项的影响**：NPC 能走 → 减速、黑洞、毒气、拴住都能看 NPC；NPC 不开火 → "被定住时能不能开枪""AI 会不会打分身""AI 绕不绕护罩"这类测不了。

## 1. `move_slow`（第 1 项）

[R5]（`slow_player.nut`、`slow_stack.nut`、`slow_npc.nut`；服务端 `StatusEffect_AddEndless`，客户端按住前进 / 冲刺，取 t > 2 s 的中位数）：

| 严重度 s | 走（按住 W） | 冲刺（W + 冲刺键） | 读回 `GetSeverity` |
|---|---|---|---|
| 0 | 199.52 | 299.00 | 0 |
| 0.01 | — | 296.65（仍冲刺） | 0.008 |
| 0.05 | — | 284.93（仍冲刺，×0.953） | 0.047 |
| 0.06 | — | 187.79（**冲刺被关**，= 走 × 0.941） | 0.059 |
| 0.10 | — | 179.96 | 0.098 |
| 0.25 | 150.23（×0.753） | 150.23 | 0.247 |
| 0.50 | 100.15 | 100.15 | 0.498 |
| 0.75 | 50.08 | 50.08 | 0.749 |
| 0.90 | 20.34 | — | 0.898 |
| 0.25 + 0.25 | 150.23 | — | 0.247 |
| 0.25 + 0.50 | 100.15 | — | 0.498 |

- 公式：**速度 = 基础 × (1 − s)**，s 用读回值（存储有约 1/256 的量化：0.25 → 0.247，0.15 → 0.149）。
- **冲刺门槛**：s = 0.047 还能冲刺，0.059 不能 → 门槛在 0.05 左右（推断 `> 0.05`）。被关冲刺后按走速 199.5 乘。
- **多个 move_slow 取最大**（不相加、不相乘）。和 M10 R2 测的 `speed_boost` 规则一样。
- **NPC**（追玩家时的位置差速度，取 p90 以避开停顿）：prowler 347 → s 0.5：174（×0.50）→ s 0.8：69（×0.20）；dummie 191 → 96 → 30。**NPC 的 0.8 = ×0.2**（只剩 20%）。

## 2. Horizon 黑洞（第 2 项）

真大招：Horizon 套装，客户端点 `offhand4` 举起、0.8 s 后 `attack` 扔（`run_bh.py` + `bh_real.nut`）；仰角 10° 向下，落点在玩家前 ~285 u。服务端每帧（0.1 s）记录。手工照抄 `BLACKHOLE_PullTriggerThread` 建的触发器拉不动人（`IsTouching` 恒 0），所以只用真大招。

**时间线** [R5]：落地后 1.7–1.8 s 开始拉（[脚本] 1.75 s）。

**敌人（落地后玩家换到别的队伍，让黑洞把玩家当敌人）**：

| 情况 | [R5] | [脚本] 3.2.2 | 差 |
|---|---|---|---|
| 不按键，距离 285 → 中心 | 第一帧就是 390.0–391.0 向心，一直保持到冲过中心 | 每 tick +500..600 后 clamp 400 | −9 u/s（−2.4%）；推断 clamp 后同一 tick 地面摩擦又减了一点 |
| 冲过中心后 | 反向 336 → 207 → 89 → 0，停在 ~70 u | 中心 100 内不加力，只 clamp | 一致 |
| 按住后退（从拉开始前 0.3 s 按） | 强拉期照样 390 向心（按键无效） | 强拉期敌人一律走加力分支 | 一致 |
| 强拉结束后按住后退 | 向外速度 d = 98：127.0；d = 206：114.8；d = 304：102.9 | `Graph(d, 0→400, 135→85)`：122.8 / 109.3 / 97.0 | 高 4–6 u/s（推断：限速在 tick 开头，之后本 tick 的加速度又加了一点） |
| 离开范围后后退 | 173.5（正常后退走速） | — | — |
| 离开范围的位置 | 水平距离 ~340 u（以投射物最后位置为中心） | 半径 400 | 中心取的是投射物最后一帧，和无人机实际位置差几十 u，不算差 |

**友军（自己的黑洞，不换队）**：不按键 191 u/s 向心（[脚本] clamp 200，−4.5%），停在 ~60 u。友军那一次，黑洞结束前后服务端位置有一次跳回起点（d 从 95 → 398 → 355），原因没查；敌人那几次没有。

**NPC** [R5]：prowler + dummie 放在离中心 100–260 u（同 realm）。诊断显示黑洞触发器 `IsTouching(npc)` = 1、`DoesShareRealms` = 1，但整个 10 s：`in_black_hole_field` = 0、没有 parent（没挂 mover）、NPC 继续自己走，有一只从 48 u 处走过中心也没被抓。**本地 NPC 定身不生效**，原因没查到（推断 `BLACKHOLE_TriggerEnter` 对 NPC 没被调用）。"定住时能不能开枪"因此测不了（另外本地 NPC 本来就不开火）。

## 3. 毒气对 NPC（第 3 项）

[R5]（`gas_npc.nut`：`CreateGasCloudMediumAtOrigin`，云主 = 玩家，云的 source 是一个临时 script mover；dummie 5000 血，每 0.1 s 放回原位，否则 AI 会自己走出去）：

| 时间 | 每跳伤害 |
|---|---|
| 1–2 s | 5, 5 |
| 3–4 s | 6, 6 |
| … | 每 2 s +1 |
| 25 s | 17 |
| 26–36 s（移到 900 u 外） | 无伤害 |
| 37.1 s（回到云里，第一跳） | **23** |
| 49.1 s | 29 |

- 伤害 = 5 + floor(从**第一次**进入算起的秒数 / 2)，每 1 s 一跳，**没有上限**。NPC 的 `gasEnterTime` 整个过程不重置（脚本里只有玩家分支会退出 `GasExposureUpdate` 并清零）。
- NPC 的 `move_slow` 全程 0：**毒气不减速 NPC**。
- 和传说的"上限 10"不符：25 s 时已经 17。玩家这边本地测不了（只有一个玩家；自己的云不打自己，换队后也不打）。
- 测试中途的教训：`CreateGasCloudMediumAtOrigin` 结束时会 `Destroy()` 它的 source，source 传玩家会让 host 报错关掉；云主必须是玩家（`SetBossPlayer`），不能用 NPC 当云主。

## 4. 暗影状态（第 4 项）

[R5]（`shadow.nut`、`shadow_log.nut`、`shell_regen.nut`）：

- `IsShadowForm()` 存在；`EnterShadowForm()` 不报错，`IsShadowForm` false → **true**；`LeaveShadowForm()` 后 false。
- `EnterShadowFormFortified()` 不报错，但 `IsShadowForm` 仍 **false**。
- **Forged Shadows**（Revenant 套装，按住 `offhand4` 0.8 s 松开）：按下后 ~1.5 s 耗尽充能，生成 `forged_shadows_shield` 壳（75 / 75，parent 在玩家身上），`shadow_form` 状态 = 1，`IsShadowForm` = false。脚本 `TakeDamage`（世界）60 直接扣玩家血 100 → 40，不经过壳（壳挡的是打到壳上的子弹 / 近战，世界伤害不算）。壳被脚本打掉 50 后 9 s 内不回：回复走 `SHADOW_FORM_HEALTH_NETVAR`，由壳的受伤回调启动，脚本伤害触发不到。**壳回复速度没测到**，要有真攻击者（本地 NPC 不开火，只能等两人环境）。
- **Death Totem**：`GiveOffhandWeapon( "mp_ability_revenant_death_totem" )` 报 "Can't find weapon … It may need to be precached"。脚本文件在，但武器没进本地武器表，所以**召回流程本地测不了**；暗影部分本身（`EnterShadowForm`）可用。
- 服务端帧时长 `FrameTime()` = 0.05 s。

## 5. D.O.C. 无人机（第 5 项）

[R5]（Lifeline 套装，满充能时点 `offhand1` 直接放出；`doc_log.nut` 每服务端帧记无人机 `follow_medic` 和玩家；`an_doc.py` 换到玩家朝向坐标系）：

| 阶段 | 玩家速度 | 无人机相对玩家（前 / 右 / 高） | [脚本] 期望 | 前后落后 | pitch / roll |
|---|---|---|---|---|---|
| 站（放出 ~1 s 后） | 0 | −37.3 / 62.2 / 70.0 | −37.3 / 62.2 / 70 | 0.0 | 0 / 0 |
| 走 | 199.5 | −57.2 / 62.2 / 70.0 | 落后 (0.5v − 40)/3 = 19.9 | **19.9** | 10.1° / 0（公式 9.98°） |
| 冲刺 | 299.0 | −72.2 … −74.2 | 落后 36.5 | **34.9–36.8** | 14.2–14.8°（公式 14.95°） |
| 滑铲（440 u/s，蹲） | 440 → 300 | −83.9 / 38.5 / 49.4 | 蹲：−20.6 / 34.3 / 46 | 45–47（还没到稳态） | 20°（封顶） |
| 原地右转 ~210°/s | 0 | 前 +23 / 右 55 | — | — | roll 17°（封顶）；yaw 比玩家晚一个 tick（~20°） |
| 停转后 | 0 | 0.6 s 回到 −37.3 / 62.2 | — | — | 0 |

- 结论：本地 dedi 跑的就是这份重写脚本，行为 = D-FOLLOW-MOTION 公式，没被别的脚本覆盖。
- 没测：断视线 1 s 瞬移、406 u 绳断瞬移、和 S21 正版像不像（要正版录像）。
- 跑道：出生点往 +x 约 1200 u 后是下坡，第一次的长跑段掉到坡下，第二次缩短各段。

## 6. Ash 拴住（第 6 项）

[R5]（Ash 套装，按住 `offhand1` 0.5 s 松开，dummie 在 200 u；命中 1 s 后把玩家移到 dummie 前方 800 u，让 dummie 追过去；`ash_log.nut`）：

- 命中：血 −10（只一次，之后没有链子伤害），`move_slow` 0.5 持续 ~1.6 s，再 ~0.9 s 线性淡到 0（电击路径）。dummie 盾 0。
- 锚点：一个 `prop_physics` 留在命中点，存在约 6.7–7.2 s（每 0.5 s 查一次）。[脚本] 是 5 s 断开 + 收尾。
- dummie 追玩家，离锚点 17 → 40 → 76 → 172 → 299 → 425 → **552 u**，没有被拉回、没有减速、没有伤害。
- 结论：**本地拴住完全无效**，和静态结论（`AddEntityUpdatedTether` 被注释）一致。正版拉回公式本地拿不到，要反编译 S21 客户端（`tether_maxvel`）或看录像。

## 7. 没做的（各汇总第 3 节剩下的项）

这次只做到第 0–6 项。每次脚本运行错误都会让 host 关掉、重启要 1–10 min（本次重启 4 次），剩下的项建议下个会话接着测，按价值：

1. 破坏球伤害 / 滚法 / 爆几次（A #2）——真大招可放（M10 R2 已能放出）。
2. 炮击发数和导弹速度（A #4）、火焰环时间线（A #5）。
3. Whistler 积热（C #1）、Valk 网格（C #2）。
4. Forged Shadows 壳回复（E #2）——要真攻击者，本地 NPC 不开火，可能要两人环境。
5. 黑洞 NPC 不定身的原因（查 `BLACKHOLE_TriggerEnter` 是否对 NPC 调用）。

## 8. 工具和教训

- `rt_probe.py launch|run|stop`：跑一个 Squirrel 片段，收集 `[RT]` 行和 `SCRIPT ERROR`。`run_bh.py`（黑洞：offhand4 + attack）、`run_sched.py`（服务端记录 + 客户端按键时间表）、`legend.py`（换传奇 + 套装，用 `hsd_trial.py` 的 `KIT_SERVER`）、`an_slow.py`、`an_doc.py`。片段在 `w2-runtime/snippets/`。
- **服务端 eval 主体里的运行时错误、或游戏脚本线程里的错误，会让 host 直接关掉**（"There was a problem processing game logic"）。片段一律放进 `try`，并且别把玩家当成会被 `Destroy()` 的参数传进游戏函数。编译错误不会关 host。
- 真技能的按法：战术 `offhand1` 点一下（D.O.C.）或按住松开（Ash）；大招 `offhand4` 举起后要再点 `attack` 才扔（黑洞），Forged Shadows 按住 0.8 s 松开。
- 自己刷的 NPC 要加进玩家的 realm。
