# TF2 本地服务器：测试靶子（W1）

2026-10-29，W1 交付。用途：给需要目标的道具做实测，比如智能手枪锁定、Tick（frag drone）、哨戒炮。

- 脚本：[../../mod/HSD.TF2Diag/mod/scripts/vscripts/hsd_diag_npc.gnut](../../mod/HSD.TF2Diag/mod/scripts/vscripts/hsd_diag_npc.gnut)，已在 `mod.json` 注册（服务端）。
- 实验表：[../../runtime/plans_w1.py](../../runtime/plans_w1.py)，包括 `w1_targets`、`w1_hostile`、`w1_passive`。
- 本文所有命令都在游戏里跑过，验证数据见第 6 节。

## 1. 结论先说

| 需求 | 做法 | 状态 |
|---|---|---|
| 静止靶（永远不动、不还手） | `hsd_npc soldier static …`：生成后 0.6 s 冻结（`Freeze()`，和战役 Gauntlet 靶子同一做法） | ✓ 已验证 |
| 走动的 AI | `hsd_npc_walk`：AI 寻路，在两点之间来回跑 | ✓ 已验证（需要导航网格） |
| 匀速移动靶 | `hsd_npc_slide`：冻结的 NPC 挂在脚本移动器上，按给定速度来回平移 | ✓ 已验证（不需要导航网格，速度精确） |
| 追玩家的 AI | `hsd_npc_chase` | ✓ 已验证（玩家要站在导航网格上） |
| 会还手的敌人 + 可关掉 | `hsd_npc … hostile …` + `hsd_npc_passive <id> 1/0` | ✓ 已验证（关掉 = 收走枪，见第 4 节） |
| 列出、删除、读血量 | `hsd_npc_list`、`hsd_npc_kill`、`hsd_npc_hp` | ✓ 已验证 |

`mp_lf_stacks`（默认地图）**有** AI 节点图（`hsd_npc_nav` 报 326 个节点），NPC 能寻路。不用换图。

## 2. 命令

所有命令都在实验表里用 `C("…")` 发出，由服务端执行。`<id>` 是生成时分配的编号，从 1 开始，同一局里不会重复（删掉的编号不再复用）。`all` 表示所有活着的靶子。

| 命令 | 参数 | 作用 |
|---|---|---|
| `hsd_npc <种类> <行为> x y z yaw [hp] [阵营]` | 种类：`soldier`（步兵）、`spectre`（幽灵）、`stalker`（潜行者）、`reaper`（死神），或直接写 `npc_xxx` 类名<br>行为：`static`、`idle`、`hostile`（见下表）<br>hp：最大血量，0 或省略 = 默认（步兵 100、幽灵 100、潜行者 150）<br>阵营：`enemy`（默认，玩家的对立阵营）、`friendly`、或阵营编号 | 在 (x, y, z) 生成一个靶子，朝向 yaw |
| `hsd_npc_walk <id> x y z [run]` | run：1 跑，0 或省略走 | 在出生点和 (x y z) 之间来回寻路，每到一端打一行 `NPC leg`。需要导航网格 |
| `hsd_npc_chase <id> [run] [半径]` | 半径默认 150 | 每 0.5 s 把目标点设成玩家位置（先夹到导航网格上），追到半径内停下 |
| `hsd_npc_slide <id> x y z 速度` | 速度：u/s | 冻结后挂到脚本移动器上，在当前位置和 (x y z) 之间匀速来回 |
| `hsd_npc_stop <id\|all>` | | 停止 walk / chase / slide，原地冻结 |
| `hsd_npc_passive <id\|all> <1\|0>` | 1 关火，0 开火 | 1：忽略所有人、清掉敌人、收走枪；0：还枪、恢复感知、直接把玩家设为敌人 |
| `hsd_npc_hp <id\|all> [设定值]` | | 打印血量；带设定值时先设置（超过上限会同时抬高上限） |
| `hsd_npc_track <id\|all> <1\|0>` | | 打开或关闭位置日志（walk / chase / slide 会自动打开） |
| `hsd_npc_list` | | 列出所有活着的靶子 |
| `hsd_npc_kill <id\|all>` | | 直接删除（没有死亡动画，不算击杀） |
| `hsd_npc_nav` | | 打印地图名和 AI 节点数（0 = 没有导航网格） |

三种行为：

| 行为 | 动不动 | 开不开火 | 适合 |
|---|---|---|---|
| `static` | 冻结，连动画都停 | 不开火（没有枪） | 锁定、伤害、命中部位测试 |
| `idle` | 站着，可以接 walk / chase / slide | 不开火（没有枪） | 移动靶 |
| `hostile` | 正常 AI，会自己找掩体、移动 | 开火，生成时直接以玩家为敌 | 需要被打的测试（比如护盾、相位） |

## 3. 日志行

runner 会把这些行收进 `diag.tsv`：

| 行 | 字段 |
|---|---|
| `HSDDIAG NPC spawn <id> <类名> <行为> team=<阵营> x y z yaw=… hp=<血>/<上限> weapon=<武器> <时间>` | 生成。被动靶的武器写成 `xxx(held)`，表示已收走 |
| `HSDDIAG NPC list <id> …  frozen=<0/1>` / `HSDDIAG NPC list end player_team=<n>` | 列表 |
| `HSDDIAG NHP <id> <血> <上限> <时间>` | 血量读数 |
| `HSDDIAG NDMG <时间> <id> <伤害> <受伤前血量> <攻击者类名> <伤害来源 id> <命中点 x y z>` | 靶子每次受伤一行。伤害来源 id 是 `eDamageSourceId` 的数值 |
| `HSDDIAG NPOS <时间> <id> x y z <血>` | 位置，服务端每 0.1 s 一行（只对开了 track 的靶子） |
| `HSDDIAG NDEAD <id> <时间>` | 死亡（被打死，不是 kill 命令删除的） |
| `HSDDIAG PDMG <时间> <伤害> <玩家受伤前血量> <攻击者类名> <攻击者靶子 id>` | 玩家每次受伤一行；id = −1 表示不是靶子打的 |
| `HSDDIAG NPC walk / leg / chase / chasing / slide / stop / passive / kill / err …` | 各命令的回执；`err` 是参数错误或找不到 id |

## 4. 限制和坑

1. **导航网格范围。** `mp_lf_stacks` 的玩家出生点（24, −1864）和 (24, −1700) **不在** AI 网格上；(300, −1400) 一带在。`hsd_npc_chase` 时玩家站在网格外，NPC 只能慢慢挪（6 s 只靠近约 75 u）；玩家站到 (300, −1400) 后，NPC 2 s 内跑到 32 u 处停下。walk 的两端也要选网格上的点。验证过能走的区域：x −300…300，y −1600…−1300，z 1。
2. **`idle` NPC 会漂移。** 生成后会自己挪动：头 1.5 s 约 30–45 u，20 s 里可能挪 140 u（`w1_passive` 的 id 4）。`hostile` 的 NPC 会自己找掩体移动。要位置精确就用 `static`，或者用 `slide`。用完 walk / chase 后，用 `hsd_npc_stop` 原地冻结。
3. **关火要收枪。** 只设 `NPC_IGNORE_ALL` 时，步兵会停火，幽灵却继续开火（`20261029_113018_w1_hostile`）。现在的 `passive 1` 会同时收走枪。所以 `static` / `idle` 靶子手里都没有枪，这对智能手枪锁定没有影响。
4. **静止靶要冻结后才挨打。** 冻结在生成 0.6 s 后发生，实验表里生成后等 ≥ 1 s 再开火。冻结的 NPC 受到致命伤害时，脚本会先解冻，让它能正常死亡（Gauntlet 也是这样做的）。
5. **walk 的速度。** 幽灵跑（run=1）约 217 u/s，到端点后有约 0.5 s 转身停顿。要精确匀速就用 `slide`。实测 slide 150 u/s，误差 < 1 u/s。
6. **伤害数值。** 步兵 / 幽灵用 R-201（`mp_weapon_rspn101`）打玩家每发 10 伤害，约 0.1–1 s 一发。玩家用 R-201 打靶子每发 25（实测 11 发 −275）。
7. **阵营。** 本地私服里玩家的阵营每局不固定（2 或 3），所以默认用"玩家的对立阵营"，不要写死编号。
8. **玩家的血。** 有还手的敌人时先 `hsd_hp 5000`，避免玩家被打死，否则实验表会中断。
9. **slide 时 NPC 被挂在移动器上。** `stop` 会解除挂接并删掉移动器。slide 中靶子是冻结的（不播走路动画）。
10. **runner 并发。** 两个会话的 runner 同时等锁时，可能同时拿到锁，后安装的实验表会覆盖先安装的（2026-10-29 11:34 一次 `w1_passive` 实际跑的是别人的实验表）。跑完先看 `diag.tsv` 里的 `TAG` 是不是自己的。

## 5. 可直接复制的实验表

放进自己的 `plans_xxx.py`（`from plans import C, W, U`）：

```python
def my_target_test():
    """mp_lf_stacks：玩家在出生点 (24, -1864, 1) 朝 +y（yaw 90）。"""
    return [
        C("hsd_hp 5000"),                                   # 有还手的敌人时防止玩家被打死
        C("hsd_npc_nav"),                                   # 记录地图和节点数
        # 静止靶：正前方 264 u，500 血
        C("hsd_npc soldier static 24 -1600 1 -90 500"),     # id 1
        # 匀速移动靶：在 y -1450 左右来回，150 u/s
        C("hsd_npc stalker idle 300 -1450 1 -90"),          # id 2
        W(1.5),                                             # 等冻结（0.6 s）和生成动画
        C("hsd_npc_slide 2 -300 -1450 1 150"),
        C("hsd_npc_list"), C("hsd_npc_hp all"),
        # --- 在这里放要测的道具，比如：
        C("hsd_weapon mp_weapon_rspn101"), W(1.5),
        C("hsd_setup 24 -1864 1 0 0 0 4 90"), W(0.5),      # 瞄准静止靶胸口（pitch 4）
        C("+attack"), W(0.8), C("-attack"), W(0.5),
        C("hsd_npc_hp 1"),
        # 会还手的敌人，然后关火
        C("hsd_npc soldier hostile 300 -1400 1 -135 300"),  # id 3
        W(6.0), C("hsd_npc_passive 3 1"), W(4.0),
        C("hsd_npc_kill all"), C("hsd_npc_list"),
        C("hsd_tag -"),
    ]
```

在 `plans.py` 末尾加一行 import，然后：

```bash
C:/Users/<user>/AppData/Local/Programs/Python/Python311/python.exe -I runner.py my_target_test --timeout 420 --r5-wait 120
```

分析时：

- 伤害：`grep "^HSDDIAG NDMG" diag.tsv`
- 血量：`grep "^HSDDIAG NHP" diag.tsv`
- 移动轨迹：`awk '$2=="NPOS" && $4==2' diag.tsv`

## 6. 验证记录（数据在 `runtime/data/`）

| 运行 | 内容 | 结果 |
|---|---|---|
| `20261029_112659_w1_targets` | 生成步兵（static）、幽灵（idle → walk → chase）、潜行者（idle → slide）、步兵（hostile → passive）；列表、读血、停止、删除 | 都生成成功。static 靶被 R-201 打中 11 次，500 → 225，位置不变（frozen=1）。walk 两端来回 5 次，约 217 u/s。slide 150 u/s 匀速来回。chase 没生效：玩家在出生点，不在网格上，后来修了。删除后列表为空 |
| `20261029_113018_w1_hostile` | 两个 hostile（步兵 + 幽灵）→ passive → 再开火；chase | hostile 生成后 0.9 s 第一发命中玩家，8 s 内 7 发。passive 后步兵停火，幽灵继续开火 10 发（据此改成收枪）。再开火后 6 s 内 13 发。chase：玩家到 (300, −1400) 后 2 s 跑到 32 u |
| `20261029_113421_w1_passive` | **无效**：runner 并发，跑的是别人的实验表 | — |
| `20261029_114130_w1_passive` | 收枪后的 passive 复测：2 幽灵 + 1 步兵 hostile，另有 1 个 idle 幽灵在视野里 | hostile 6 s 内 9 发（id 2、3 都开火）。passive 后 **10 s 内 0 发**。只把 id 1 改回开火，1.1 s 后开始命中，3.7 s 内 8 发，全部来自 id 1。idle 幽灵全程没开火 |
