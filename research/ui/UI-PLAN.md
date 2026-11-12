# HSD 界面方案（UI-PLAN）：一层界面，按枪和技能用数据驱动

2026-11-07，会话 `ui-inventory`。依据是 [UI-INVENTORY.md](UI-INVENTORY.md)（R5 四层的盘点和 HSD 对照）。只是方案，Unity 没改。〔11-12 你定了 D-130 – D-135：D-130 / D-131 / D-132 / D-133 / D-135 按建议；**D-134 选 B（移动提示默认开）**，不是建议的 A；Unity 的 U1 等战斗那一摞 PR（HSD-Unity #52 – #69）合进 main 以后再开始。没选的选项和数据都留在 §3〕

## 先说结论（给人读的）

现在 HSD 的界面是很多处各画各的 IMGUI 调试文字，没有一处像 R5。方案是把准星、命中反馈、世界标记、状态栏收进**一层界面**，学 R5 的做法：

1. **样子跟数据走，不跟代码走。** 每把枪在 Arsenal 表里多几列"准星类型、base_spread、模式切换、低弹量阈值"，从 S21 字段自动生成，和现在的武器数据一样。每个技能一行"预览类型、圈数、半径、颜色、冷却显示方式"。
2. **逻辑和画分开。** 一个纯 C# 的 `HudModel` 每帧从战斗和移动状态算出"现在该显示什么、参数多少"（可以写测试，不用 Unity）；画的那一层只读它。这就是 R5 的"脚本传参数、RUI 画"。
3. **屏幕上的用 UI Toolkit 画**，世界里的（地面圈、标记）继续用 3D 网格，按 R5 的粒子位置和颜色做。不用加任何包。
4. **旧的 IMGUI 留开关**，默认切到新界面；调试面板和菜单继续用 IMGUI。
5. 〔11-12 定〕HSD 自己加的移动提示（速度条、姿态文字、滑索 / 跳板 / 悬挂提示）**默认继续开**，标成 HSD 设计，能用开关关掉（D-134 B）。

先做准星和命中反馈（每次开枪都看得到，最影响手感），再做状态栏，再做受伤方向和技能预览，最后做开镜瞄具（要和枪模一起做）。

## 1. 结构

```
战斗 / 移动状态（CombatSim、PracticeSession，只读）
        │
        ▼
HudModel（纯 C#，每帧建一次，可测试）
  ├─ Crosshair   形状 id、间隙（度）、透明度、颜色、模式槽
  ├─ HitFeedback X（类型、开始时间、击杀）、数字（累加 / 浮动）、霰弹点（命中时的屏幕位置）、声音事件
  ├─ Incoming    3D 箭头列表（方向、类型、剩余时间）、闪屏、低血量比例
  ├─ Status      两把枪的标签、弹匣 / 备弹、低弹量、换弹比例、蓄力 / 热量 / Energize、技能栏（比例、格数、状态）
  └─ World       技能预览（点、半径、颜色、有效 / 无效）、抛物线（颜色）
        │
        ├──► 屏幕层（UI Toolkit）：准星、X、数字、状态栏、提示
        └──► 世界层（3D 网格）：地面圈、标记、受伤箭头
```

- `HudModel` 的数据来源都是现有状态：扩散角（`ArsenalWeapon.spread.Angle`）、伤害事件（`CombatSim.numbers` 改成事件列表）、冷却（`Charges`）、技能预览（`MissileSwarmCaster.preview` 等）。
- 规则写在 `HudModel` 里，带 R5 的数字和出处：例如累加数字 0.25 s 合并、1.0 s 寿命（`cl_hud.gnut:646-647`）；X 优先级（`cl_player.gnut:631-647`）；护盾命中 = 这一枪后还剩护盾。
- 屏幕层的样子只画一层，霰弹准星和命中点（W-03、H-04）已经由 `shotgun-reticle` 实测过（颜色、大小、0.45 s + 淡出到 0.75 s），直接用。
- 画的一层只管样子。R5 的样子是编译资源，读不到，所以**样子先按截图做，截图之前用干净的几何占位**，参数接口按 R5 RUI 的参数（`adjustedSpread`、`adsFrac`、`isSprinting`、`isReloading`、`hitType`、`isKillShot`、`shieldTier`…）一一对应，以后换样子不改逻辑。

## 2. 数据表

### 2.1 每把枪（加进 Arsenal 表，`gen-weapon-data.mjs` 生成）

| 列 | 来源 | 例子（R-301） |
|---|---|---|
| `crosshair` | `RUI_CrosshairData.Crosshair_N.ui` → HSD 形状 id | `tri` |
| `crosshair_alt` | 第二槽 + 哪个 mod 切过去（`rui_crosshair_index`） | Hemlok `altfire` → 槽 1 |
| `base_spread` | 每槽 `base_spread` | 0（Charge Rifle 10） |
| `crosshair_args` | 额外参数：isFiring、charge、chargeFrac、readyFrac、节奏 | — |
| `red_crosshair_range` | 字段 | 0 |
| `low_ammo_fraction` | 字段 | 0.30 |
| `pellets` | `projectiles_per_shot`（> 1 → 霰弹命中点） | 1（EVA 8） |
| `energize_*`、`heat_*` 颜色 | 字段（Sentinel `energized_ui_color` 等） | — |
| `reticle_iron` / `reticle_optics` | `UiData1` / 各瞄具 `UiData` | `r301_reticle` |

形状 id 的集合就是 INVENTORY W-01 的 14 种。已经有生成好的表：`data/ui-crosshair.tsv`、`ui-reticles.tsv`。

### 2.2 每个技能

| 列 | 例子 |
|---|---|
| `hud_display` | `bar` / `count`（字段 `ammo_display`） |
| `charge_segments` | 弹量 / (每次 × 连发) |
| `preview_kind` | `grid`（Valk）、`ring`（Fuse、Conduit、黑洞）、`pillars`（黑幕）、`ghost`（A 墙、电网）、`reticle`（Newcastle）、`tube`（Seer）、`none` |
| `preview_count` / `radius` | Valk 12（升级 20）、半径 150；Fuse 420；黑洞 400 |
| `colour_valid` / `blocked` / `out_of_range` | Fuse 10 255 0 / 255 125 0 / 255 10 0 |
| `arc_colour` | 红 / 橙 / 蓝 / 浅蓝 / 绿 |
| `threat_radius` | Valk 195、尖刺 440、Bangalore 350 |
| `fail_hint` | 文本键（英文待截图） |

## 3. 决定（11-12 定了）

| # | 定了什么 | 没选的 |
|---|---|---|
| D-130 | A UI Toolkit | B uGUI、C 继续 IMGUI、D 自绘网格 + shader |
| D-131 | A 纯 C# `HudModel` + 屏幕层 + 世界层 | B 每个系统自己画 |
| D-132 | A 世界标记用 3D 网格 / 贴花，在世界相机里（霰弹点例外，在屏幕层） | B 投影到屏幕画 |
| D-133 | 按 R5 玩家默认：X + 护盾图标、累加数字、3D 受伤箭头；准星变红、敌人血条不做 | 其他值都留开关：只有 X / 关、浮动 / 都有 / 关、2D 圆环 / 都有 |
| D-134 | **B 默认开**（速度条、姿态文字、滑索 / 跳板 / 悬挂提示），标 HSD 设计，留开关关掉 | A 默认关、练习模式开（原来的建议）；C 删掉 |
| D-135 | 按 U1 – U9 的顺序；**U1 等战斗那一摞（HSD-Unity #52 – #69）合进 main 以后开始** | 马上开始（没选） |

下面是定之前的选项和数据，原样留着。

### D-130 屏幕界面用什么技术

| 选项 | 数据 / 事实 | 好处 | 坏处 |
|---|---|---|---|
| **A UI Toolkit**（建议） | Unity 6000.6，`com.unity.modules.uielements` 已在 manifest，**不用加包**；`Painter2D` 能每帧画矢量线和弧 | 分辨率无关（准星间隙按度换像素）；USS 管样子，接近"资源管样子"；批处理好；支持数据绑定 | 世界跟随的元素（数字、霰弹点）要每帧自己投影定位；团队没用过 |
| B uGUI Canvas | 要加 `com.unity.ugui`（Unity 6 里是包，manifest 里没有） | 最成熟，例子多，TextMeshPro 字好 | 加依赖；一个元素一个 GameObject；矢量准星要自己写 Graphic |
| C 继续 IMGUI | 现在就是（2 处 `OnGUI`，几百行） | 不用改 | 每帧重建、样式难管、做不出平滑形状和动画；本来就定位成调试 |
| D 自己画网格 + shader（最像 RUI） | — | 每个元素一个 shader 吃参数，最贴 RUI 的思路 | 文字、布局全要自己做，工作量最大 |

建议 A：不加依赖，矢量画准星正合适；IMGUI 留给调试面板和 Esc 菜单（以后要不要换另说）。

### D-131 逻辑和画怎么分

| 选项 | 说明 |
|---|---|
| **A 一个 `HudModel`（纯 C#）+ 两个画层**（建议） | 和 `HsdHud`（"游戏画这些行，测试读它们"）同一个做法；规则可测试；样子以后换不动逻辑 |
| B 每个系统自己画（现在的做法） | `CombatHud`、`ArsenalHud`、`SkillHud`、`PracticeGame` 各画各的；不用改结构，但规则散在画的代码里，没法统一改样式和开关 |

### D-132 世界里的标记怎么画

| 选项 | 说明 |
|---|---|
| **A 3D 网格 / 贴花，在世界相机里**（建议） | R5 也是粒子和模型（`P_valk_rckt_AR_marker`、`damage_arrow.rmdl`）；HSD 现在的 `CombatVisuals` 圆柱已经是这一路，换成按 R5 半径、颜色、贴地法线的圈即可 |
| B 投影到屏幕上画 | 被墙挡、透视都要自己算，和 R5 不一样 |

受伤 3D 箭头用模型（A）。霰弹命中点不是世界标记：〔11-07 改正，`shotgun-reticle` 实测〕R5 在命中那一刻取命中点的屏幕位置放下，之后钉在屏幕上不跟世界（转 4° 世界移 43 px，点不动），所以放在屏幕层，只在命中时投影一次。

### D-133 默认样式跟 R5 的玩家默认设置

| 项 | 建议默认 | 另一个选项（开关） | 数据 |
|---|---|---|---|
| 命中 X | 2 = X + 护盾图标 | 1 只有 X、0 关 | `hud_setting_damageIndicatorStyle` 默认 2 |
| 伤害数字 | 1 = 累加 | 2 浮动（≈ HSD 现在）、3 都有、0 关 | `hud_setting_damageTextStyle` 默认 1 |
| 受伤方向 | 2 = 3D 箭头 | 0 2D 圆环、1 都有 | `damage_indicator_style_pilot` 默认 2 |
| 准星变红 | 不做（玩家枪 `red_crosshair_range` 都是 0） | — | INVENTORY W-01 |
| 敌人血条 | 不做（Flowstate 加的） | 可以以后当 PvE 选项 | H-09 |

### D-134 HSD 加的移动提示怎么办

R5 移动时没有界面（INVENTORY M-00）。HSD 现在有：速度条、姿态文字、滑索"X 上索"、跳板"2J"、悬挂按键提示。

| 选项 | 说明 |
|---|---|
| A 默认关，练习模式开（原来的建议，没选） | 正常玩和 R5 一样干净；练习时有帮助。它们都是 HSD 加的，按"HSD 设计"标（同 D-08） |
| **B 保持现在（默认开）**〔11-12 选了〕 | 用户已经习惯；但和 R5 不一样。标 HSD 设计，留开关关掉 |
| C 删掉 | 不符合留档规则（旧版要留开关） |

### D-135 做的顺序

| 步 | 内容 | 依赖 | 为什么这时候做 |
|---|---|---|---|
| U1 | 屏幕层框架 + `HudModel` + 开关 `hudR5`（关 = 旧 IMGUI） | D-130、D-131 | 后面都要 |
| U2 | 每把枪的准星 + 扩散 | 2.1 表；S-1 截图定系数（先用推断公式） | 每发都看到 |
| U3 | 命中 X（8 种类型、击杀）、累加数字、命中声音事件 | S-2、S-4 | 打中的确认感 |
| U4 | 霰弹准星和命中点：把 `combat/wp5-shotgun-reticle` 的 `ShotgunReticle.cs`（IMGUI，规则按 R5 实测）接到新屏幕层，逻辑沿用 | D-128（`shotgun-reticle`） | 霰弹枪手感 |
| U5 | 右下 HUD、低弹量 / 换弹 / 换枪提示、蓄力 / 热量 / Energize、技能栏 | S-7、S-8、S-10 | 状态 |
| U6 | 受伤 3D 箭头、闪屏、低血量 | S-5、S-6 | PvE 敌人开火以后（`enemyFire` 未实测） |
| U7 | 技能预览按 R5：Valk 4 × 3、Fuse 三色圈、各技能颜色、虚影有效 / 无效 | S-9、S-12 | 现在都有占位，能玩 |
| U8 | 开镜机瞄标记、光学瞄具、枪身弹量屏 | 枪模（#68）上的网格挂点 | 要和枪模一起做 |
| U9 | 移动提示按 D-134 B：默认开，搬到新屏幕层，加关闭开关 | D-134 | 最后 |

〔11-12 定〕U1 在战斗那一摞（HSD-Unity #52 – #69）合进 main 以后开始。

### 已经发现的问题（不在这次改）

- **Valk 圈排法错**：HSD 12 个圈排成 5 + 5 + 2（`MissileSwarm.Targets`，5 列取前 12）；R5 是 3 列 × 4 排（升级 5 列 × 4 排）。改法：列数 = 1 + 2 × (sideSteps − 1)，排数 = forwardSteps。放 U7 一起改，或单独先修。
- `research/combat/valkyrie-missile-swarm/SYSTEM.md` §5.1 / 待查 1 要按 INVENTORY L-01 改正（在 #86 那条分支上）。

## 4. 开关和留档

- `hudR5`（新界面，默认开）；关 = 现在的 IMGUI 全套，一行不删。
- `hudMovementHints`（HSD 加的移动提示，默认开，D-134 B）；关 = 和 R5 一样移动时没有界面。
- 每个 D-133 的设置一个开关，默认按 R5 玩家默认值。
- 和 R5 的差别写进 `R5-DIFF-ARCHIVE.md`：尤其是样子还没截图、按推断做的部分（准星间隙公式、各类型颜色），每项写差在哪、等哪张截图。

## 5. 怎么验收

- `HudModel` 单元测试：累加窗口（0.24 s 合并、0.26 s 分开）、X 优先级、护盾命中定义、技能格数、Valk 圈数和排法。
- 截图对照：S-1 – S-13 拍到以后，同场景拍 HSD，并排放（以前 iron-sights 的做法）。

## 6. 待同步

- 本文件抄送 Drive `设计规范/`（索引 `00-索引.md`），PR 没合并前标"还没合并"。
