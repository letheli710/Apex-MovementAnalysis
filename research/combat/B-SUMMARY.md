# 批次 B 汇总：陷阱 / 区域控制（静态研究）

会话 `combat-b`，2026-10-31。第一波：只读 `research-src/s21-platform/scripts/`（另读了 SDK `research-src/s21-r5sdk/src/` 里和黑洞、拴住有关的两处），没开游戏、没改 HSD-Unity、没 commit。模板：`SYSTEM-RECORD-TEMPLATE.md`；过滤表：`C0-ABILITY-FILTER.md`。HSD 侧 10 项**全部未实现**，每份记录第 6 节写了建议做法和能复用的类。

## 1. 每项一行

| # | 技能 | 记录 | 一句话结论 | 分类 |
|---|---|---|---|---|
| 1 | Wattson 战术 Perimeter Security | [wattson-perimeter-security](wattson-perimeter-security/SYSTEM.md) | 桩链：≤ 768 u 自动连、每桩 2 条、4 层 × 24 u；敌人穿线 20 伤害 + 电击 3 s（减速 0.5 / 转向 0.7），每人每秒一次（全局表，不分电线）；队友穿过关 0.4 s；被挡关 1.1 s。穿越判定在引擎（`TT_TESLA_TRAP`）。脚本被 SDK 为 S3 dedi 改过（载具击晕删了）；`.txt` 回充 4 s 一次，可疑 | 好技能、系统 |
| 2 | Wattson 大招 Interception Pylon | [wattson-interception-pylon](wattson-interception-pylon/SYSTEM.md) | 512 u vortex 球，只拦"0.2 s 内会落进 512"的投射物，按 `.txt` 字段 `trophy_system_ignores` 白名单（默认连友军也拦）；有视线的队友每 0.2 s +1 盾（池 250）；电网回充 ×5（给武器挂 mod）；**本地没有持续时间**（计时自毁函数未调用） | 待定；系统（反制投掷物、区域回资源） |
| 3 | Ash 战术 Arc Snare | [ash-arc-snare](ash-arc-snare/SYSTEM.md) | 1200 u/s 无重力飞，范围 0.5 s 内按 1.5 次方长到 160，10 伤害并拴住 5 s。**拴住是引擎 tether，本地被注释掉了**（`tetherId = 1//victim.AddEntityUpdatedTether(…)`），只剩绳子特效。按留下的参数还原：半径 210 内自由、出圈拉回 ≤ 100 u/s、链血 1000 每秒掉 200 + 拉扯掉血 | 好技能、系统、可视化 |
| 4 | Catalyst 战术 Piercing Spikes | [catalyst-piercing-spikes](catalyst-piercing-spikes/SYSTEM.md) | 落平地后贴地铺 9×3 网格（47 × 30 u），2 s 后待机；440 内有"看得见核心"的敌人才竖起；踩上减速 0.5（NPC 0.8，Endless）、竖起时每秒 15；无持续时间，最多 2 块 | 好技能、系统 |
| 5 | Catalyst 大招 Dark Veil | [catalyst-dark-veil](catalyst-dark-veil/SYSTEM.md) | 20 根柱子每 0.05 s 一根、间隔 88，按头顶净空选 120/240/360 高，等 1.2 s 再 0.6 s 放大、立 15 s；挡视线不挡子弹；墙里减速 0.5，穿过致盲 7 s（只看清 200 u）；NPC 出墙再减速 2 s；"在墙里 / 穿过"用线段近邻 + 侧翻转判；**队友也被减速**（脚本没判队伍，待测） | 好技能、可视化 |
| 6 | Conduit 大招 Energy Barricade | [conduit-energy-barricade](conduit-energy-barricade/SYSTEM.md) | 两发弹各自空爆（目标上 4 m），把 7 个干扰器撒成垂直瞄准方向的一条线（间距 380、半径 200）；3 s 激活；每人每秒 10 伤害 + 减速 0.25 1 s；寿命常量 `45//5`（注释残留，待测） | 好技能、系统 |
| 7 | Conduit 战术 Radiant Transfer | [conduit-radiant-transfer](conduit-radiant-transfer/SYSTEM.md) | **指派目标 = 每帧打分**：缺盾 0–25 + 贴准星 0–35（50° 锥、50 m，5 m 内不看朝向），距离权重 0，分 > 0 的最高者；拿出就先给自己 0.67 倍；临时护盾 15/s × 9 s（上限 125）→ 保持 20 s → 20/s 衰减；只认玩家，不认 NPC | 参考（系统） |
| 8 | Newcastle 大招 Castle Wall | [newcastle-castle-wall](newcastle-castle-wall/SYSTEM.md) | 跳跃运动在引擎（三种：冲刺 / 跳 / 空中俯冲，参数齐）；落地击退只遍历**玩家**（350 u、450→250），伤害常量 0；中间高墙 + 两侧蛇形贴地铺低墙；3 s 后通电 120 s：每 2.5 s（NPC 3 s）20 + 减速 / 转向 0.75；墙拦截 200 内投射物 | 好技能、系统、可视化 |
| 9 | Newcastle 战术 Mobile Shield | [newcastle-mobile-shield](newcastle-mobile-shield/SYSTEM.md) | 一个"给目的地就自己走"的 script_mover：引擎非物理导航（前瞻 75、贴墙滑 400、跨台阶 40、悬崖 200、离地 40），160 u/s，20 s；再按 = 准星点为新目的地；玩家在盾后同向时盾面跟视线 | 待定；系统（可做 PvE 伙伴 / 护送） |
| 10 | Horizon 大招 Black Hole | [horizon-black-hole](horizon-black-hole/SYSTEM.md) | 玩家拉力在 SDK `trigger_gravity.cpp`（按 S21 客户端常量还原）：不按键 / 前 0.8 s 强拉 → 每 tick 速度 += 指向中心 300–400（强拉 +200），上限 400；按键逃 → 外向水平速度压到 85–135；友军减半；11 点视线门。**NPC：脚本直接挂 mover，1.2 s 拖到离中心 40 u 并定住到结束（~10.8 s）**。不造成伤害 | 好技能（PvE 聚怪最强）、系统 |

## 2. 可拆出的公共部件（`_shared/`）

| 文件 | 部件 | 来源技能 | 谁能复用 |
|---|---|---|---|
| [B-electric-emp](_shared/B-electric-emp.md) | 电击：减速 0.5 + 转向 0.7 + 屏幕 0.4、固定时长分支、NPC 3 s 击晕免疫窗（免疫期整次伤害 ×0） | 电网、城墙、屏障、电弧陷阱 | 所有电系伤害；HSD 现有 `CombatSim.Emp` 可直接扩展 |
| [B-move-slow](_shared/B-move-slow.md) | 区域减速三种写法（在里面 Endless + 引用计数 / 碰一下 Timed / 电击）+ "空中或滑铲进入砍一半水平速度" | 尖刺、黑幕、屏障、城墙 | 所有区域控制；HSD `slowScale` 要改成多来源 |
| [B-placement](_shared/B-placement.md) | 引擎放置器字段、粘附落地（含墙面弹开）、贴地铺开（网格 / 直线 / 蛇形）、每人数量上限 | 全部 10 项 | 所有部署类道具；和铝热剂火墙同一类 |
| [B-targeting](_shared/B-targeting.md) | 指派目标的**打分版**，和 D 批的"最小夹角版"对照，给出统一的 `TargetPicker` | Radiant Transfer | 给友方 / 敌方选目标 |

另外几个没单独成文、写在各自记录里的部件：投射物拦截球（拦截塔 3.2.2–3.2.3，城墙 3.2.6 同写法）、可指挥移动体（移动盾 3.2.2–3.2.3）、NPC 定身拉拽（黑洞 3.2.3）、精确落点弹道 + 空爆分撒（屏障 3.2.1–3.2.2）、柱子依次生长的墙（黑幕 3.2.1–3.2.2）、线段穿越触发器（电网 3.2.3）。

和别的批次的交叉：状态效果框架见 `_shared/E-STATUS-EFFECT.md`；D 批 `D-TARGET-ASSIGN.md` 写"Conduit 没读"，本批 `B-targeting.md` 补上。

## 3. 最重要的实测项（第二波，按价值排）

1. **黑洞对玩家的拉力和对 NPC 的定身**（PvE 价值最高）：R5 runner 逐帧记录站在黑洞边缘不按键 / 按后退的速度，对照 3.2.2 公式；dedi 上刷 spectre 看是否被搬到 40 u 圈定 10 s、是否还能开枪。
2. **Ash 拴住在本地是否完全无效**：dedi 上打中 dummie，看它能否走出 210。若无效，正版拉回公式需要 REA 反编译 S21 客户端（搜 `tether_maxvel`）。
3. **NPC 的 move_slow 0.8 含义**（尖刺、黑幕共用）：spectre 走过尖刺量速度。
4. **电击类对 NPC 的频率**：电网放 spectre 来回穿，看伤害是每 1 s 还是每 3 s（免疫窗）。
5. **Conduit 屏障寿命**（`45//5`）和 **电网回充**（4 s 一次）：计时。
6. **Newcastle 跳跃轨迹**：逐帧记录一次跳跃，拆出蹲伏 / 上升 / 悬停 / 俯冲四段。
7. **黑幕是否减速队友**、**拦截塔是否拦友军投射物**：需要两名同队。

## 4. 遇到的问题

- **SDK 改写的证据**（服务端行为可能和正式服不同）：
  - 电网：两处注释"HoverVehicle_StunBegin is not registered on the S3 dedi entity VM"。
  - Ash：引擎 tether 调用被注释、链血写死 10.0、6 个 tether ConVar 注释掉 → 拴住无效。
  - 黑洞：玩家拉力整段由 SDK `trigger_gravity.cpp` 重写（有 `bridge_trigger_blackhole` 开关）。
  - 拦截塔、黑幕：残留调试 `printt`。
  - `_utility_shared.nut` 有"S21 CLIENT: no int→bool"注释，共用代码也改过。
- **常量和正式服记忆不符**：Newcastle 落地伤害 `0 //25`；Conduit 屏障寿命 `45//5`；电网回充 4 s；拦截塔无持续时间。都已列入实测。
- **引擎黑盒**：电网穿越判定（`TT_TESLA_TRAP`）、Newcastle 跳跃（`StartArmoredLeap*`）、移动盾导航（`EnableNonPhysicsTraversal`）、tether 都在 C++，脚本只给参数。HSD 实现时这几处要自己写近似，写进 `R5-DIFF-ARCHIVE.md`。
- **本地化缺失**：`localization_english.txt` 里没有 Catalyst / Conduit / Wattson / Horizon 的升级说明，几条升级（尖刺检测半径 440→330、Radiant 充能 ×0.5）的意图无法从文字核对。
- 共享日志已写 8 条（`2026-10-31-combat-b-*`）。
