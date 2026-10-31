# 公共部件 D：指派目标（准星锥内选一个对象，没有就给自己）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。

来源：Lifeline D.O.C.（`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_lifeline_follow_medic.nut`，FM，**SDK 重写嫌疑**）。对照：Conduit 战术 `mp_ability_conduit_arc_flash.nut` 的 `TargetingThread`（约 430 行）/ `ScoreTarget` / `DoSelfCast`（C0 2.2b 提到，**本批没读**）。

## 0. 概要

- **部件**：常驻扫描线程 + "最佳目标"网络变量 + 下令 / 召回函数（FM:395-548）。
- **一句话**：服务端每 0.1 s 在"距离 ≤ R、和准星夹角 ≤ 50°"的队友里挑夹角最小的一个，写进网络变量；客户端拿它画 HUD；按键时如果最佳目标有效且不是当前对象就改派，没有就派给自己；另一个键召回给自己。
- **分类**：系统。
- **谁能用**：给队友 / 伙伴下指令（跟随谁、治疗谁、去打谁）、锁定类技能（PvE 里换成"选敌人"）。

## 1. 实现手段

| 部分 | 手段 | 来源 |
|---|---|---|
| 扫描 | 服务端线程 `wait 0.1`；拿到武器就开，换主人就停 | FM:256-276、395-436 |
| 结果同步 | 玩家专属网络变量（`SNDC_PLAYER_EXCLUSIVE`）`follow_drone_bestTarget`；当前对象 `lifeline_drone_follow_ent` | FM:200-202 |
| 客户端 HUD | 每个候选身上一个 RUI，读两个网络变量决定"最佳 / 已指派 / 需要" | FM:1265-1325 |
| 下令 | 客户端按键回调同时本地执行 + 发服务端（预测） | FM:1101-1145 |

## 2. 流程

```
常驻：每 0.1 s best = 选（3.1）→ 写网络变量
按"指派"键：
   防抖 0.25 s
   if best 有效 且 best ≠ 当前 且 距离 ≤ R → 当前 = best（播动作 + 语音 + 音效 + 给对方 HUD）
   else → 失败音
按"召回"键：当前 ≠ 自己 → 当前 = 自己
当前对象死亡 / 断线 → 当前 = 自己
```

## 3. 代码

### 3.1 选目标（FM:520-548）

```
best = null; bestDot = CONE_DOT
for ally in 候选（不含自己）:
   跳过：死、非友方、不同 realm、倒地、|主人原点 − ally 原点|² > R²
   dot = normalize( ally.WorldSpaceCenter − 主人眼睛 ) · 主人视线
   if dot ≥ bestDot: best = ally; bestDot = dot
return best
```
- 选"最正"不是"最近"；没有视线检查。
- 部署时（FM:554-556）如果 best 无效就用自己。

### 3.2 下令（FM:438-481）

见第 2 节。下令成功会让主人切到右副手播"下令"动作（`IssueOrderToDrone`，FM:483-491）。

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| R | 45 m = 1771.7 u（升级 ×1.5） | FM:78、358-371 |
| CONE_DOT | cos 50° = 0.643 | FM:79；`sh_utility_all.gnut:27` |
| 扫描间隔 | 0.1 s | FM:116 |
| 防抖 | 0.25 s | FM:80 |
| 被指派方向提示 | 2 s | FM:81 |

## 5. 未解决和要实测的

- 隔墙能否指派（无视线检查）：要两个玩家的环境。
- Conduit 的 `ScoreTarget` 可能是"距离 + 夹角 + 血量"的加权，读完可以和这里合并成一个更通用的打分函数。

## 6. HSD 实现

未实现。建议 `TargetPicker`：输入（眼睛、视线、候选列表、R、锥角、过滤器、可选打分函数），输出最佳对象；默认打分 = 夹角。PvE 里同一个类给"选敌人"用（过滤器换成敌方 + 视线）。
