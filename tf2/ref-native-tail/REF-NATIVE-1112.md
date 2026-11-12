# 小尾巴里标"原生"的 13 项：从 TF2 的 dll 里读出来的规则（ref-native-tail，2026-11-12）

会话 `ref-native-tail`，补测清单 `TF2-Research/REF-TESTS-1112.md`（本地文件，不在仓库里）第 1 节最后一张表。只用 Ghidra 读 TF2 的 `server.dll` / `client.dll`，没有开 TF2，没有改 Unity。这里只写规则、数值和函数地址；反编译原文在私有仓库 HSD-RawData 的 `tf2/local/nattail/`（分支 `ref/native-tail-raw`）。

## 先说结论

13 项里 11 项读到了规则，2 项只读到一部分（N7 的冷却键、N11 的搜索循环），1 项的一个开关没读出（N5 用哪条积分路径）。对手感影响最大的几条：

1. **墙跳排斥在 TF2 里根本不运行（N1）。** 削速度的函数在两个 dll 里都没有任何调用者，是死代码。实测"排斥没效果"就是这个原因。HSD 的 `repelTime` 没有 TF2 依据。
2. **腰射散布不是原生，是脚本（N3）。** 每个轴是两个均匀分布之和（三角分布），截在单位圆里，最远偏散布角的一半。SMR / Flak 的"散布 − 1°"变成负数后只是翻个方向，**实际散布还是 0.5°，不是 0**，SMR 页原来的推断不对。
3. **泰坦踩人一次给 5000，不按秒（N6）。** 每走 100 u（NPC 150 u）、速度 ≥ 50 判一次，脚下 15 % 高度内碰到的小目标都挨一下。dash 也算。
4. **Ronin 相位冲刺中不和泰坦、玩家、NPC 碰撞，只和世界碰撞（N7）。** `move_slow` 这类减速叠加时**取最大值**，不相加。
5. **导弹追踪只转方向、不改速率（N10）。** 每 1/60 s 朝目标加 H 的速度再归一化；目标偏出 60° 又转不过来时，这枚导弹永久丢掉追踪。第二个参数是"对正在 dash 的玩家用的 H"。
6. **视角 punch 弹簧是 x'' = −k·x − c·x'（N5）**，有固定步长 0.0166 s 的半隐式欧拉和按帧长的解析解两条路，由引擎一个开关选；两者在 60 Hz 下几乎一样。

## 0. 清单（开始前列出）

| # | 要找的 | 结果 | 发给谁核对 | 节 |
|---|---|---|---|---|
| N1 | 墙跳排斥：调用它的地方 | ☑ 没有调用者，死代码 | `ref-pilot-ai` | §1 |
| N2 | 敌人发现进度的函数（多 0.25–0.6 s） | ☑ 规则全；扫描量化解释了偏移，没解释斜率 | `ref-pilot-ai` | §2 |
| N3 | `ApplyVectorSpread` 分布公式 | ☑ 是脚本函数，公式全 | `ref-weapons-tail` | §3 |
| N4 | 导弹漂移 6 个键的位置 | ☑ 槽位确定 | `ref-weapons-tail` | §4 |
| N5 | 视角 punch 弹簧怎么积分 | ◐ 两条路径都读到；选哪条的引擎开关没读 | `ref-weapons-tail` | §5 |
| N6 | 泰坦踩人的伤害公式和判定盒 | ☑ | `ref-titan-tail-a` | §6 |
| N7 | Ronin 相位碰撞；`move_slow` 叠加；冷却延迟和 `fire_duration` | ◐ 前两项 ☑；第三项没找到原生读取点 | `ref-titan-tail-a` | §7 |
| N8 | Northstar 系留的拉力和断开 | ☑ | `ref-titan-tail-a` | §8 |
| N9 | Ion 涡旋霰弹锥角 `GetAttackSpreadAngle` | ☑ | `ref-titan-tail-a` | §9 |
| N10 | Tone 导弹追踪 `SetHomingSpeeds` | ☑ | `ref-titan-tail-b` | §10 |
| N11 | Legion 智能核心：搜索角含义、子弹导向 | ◐ 导向 ☑；搜索角按校验范围推断是半角 | `ref-titan-tail-b` | §11 |
| N12 | 舱框俯仰晃动对应的设置键 | ◐ 推断：和转身共用 Turn 键 | 只写进 `T-f` | §12 |
| N13 | 暴击判定 `IsCriticalHit` | ☑ | 只写进原页 | §13 |

## 方法

- 工程：`ghidra-projects/tf2/`（Ghidra 12.1.4），全程 `-readOnly -noanalysis`。`server.dll` sha256 `a5ca3a25c8ae5695…`，`client.dll` sha256 `002b36487fec7c98…`（和 `ref-titan-native` 同一份）。
- 工具：本目录 `AiDig.java`（在 `pve/live/ghidra/AiDig.java` 上加了两条命令：`nat:`/`find:` 按脚本函数名找原生绑定，`vslot:` 读命名虚表的某一格）；`ConVarReadersTF2.java`（`ledger/ghidra/`）列 ConVar 读取点；`vastr.py` 按虚拟地址从 dll 读字符串和浮点常数；`ImmScan.java`（`expansion/titan/anim/ref-native/`）按立即数找指令。
- 脚本函数（`IsCriticalHit` 等）的原生实现：找到函数名字符串的引用，引用后面第一个 `LEA` 到函数的就是绑定，绑定里调用的是实现。
- 设置键（武器 / 玩家 / aisettings）的偏移从各自的键表读（每项 0x20 或 0x30 字节：名字指针、默认值、偏移）。

## 1. N1 墙跳排斥（`runtime/GAPS-1108.md` §1.5）

| 作用 | server.dll | client.dll |
|---|---|---|
| 记录（墙跳 0x180173a00、脱墙 0x180186d60 调用） | `0x1801603d0` | `0x1801f0c60` |
| 削速度（读 `wallrun_repelTimeMin/Max`） | `0x18017eb80` | `0x1802072d0` |

- 记录函数照常运行：`wallrun_repelEnable`（默认 "1"）开着时，把墙的水平法线存进玩家 +0x18cc，时间存 +0x18e4，条数 +0x18e8 = 1。
- **削速度的函数没有任何调用者**：没有 CALL / JMP，没有 8 字节指针（虚表）指向它；只有 `.pdata` 和 `.rdata` 里的展开表引用。客户端那一份也一样。所以排斥在 TF2 MP 里从不运行。
- 它本来要做的（留档）：对每条存下的法线 n，如果向量 v 朝墙（−v·n > 0），去掉朝墙的分量，再减去一个"按输入放宽"的量（−(输入·n)·`repelSoftness` 5 · 放宽系数，放宽系数 0.2 s 前为 0、之后线性增加）；权重 0.2 s 内为 1，0.2 → 0.4 s 线性降到 0。
- **规则：** TF2 没有墙跳排斥。实测"0.28 s 贴回同一面墙、速度不被削"和这一点一致。

## 2. N2 敌人发现进度（`pve/AI-LIVE.md`）

函数：发现判定 `0x1803b5b70`；玩家扫描 `0x1803b4a80`（先过 `0x1803b3a70`：视野 vfunc 0x8a0 + 视线追踪 mask 0x84081）；清理 `0x1803b38f0`。aisettings 偏移：`NoticeForgetPreTime` +0xa3c（默认 0.3）、`NoticeForgetPostTime` +0xa40（5.0）、`NoticeDistNear/Far` +0xa44 / +0xa50、`NoticeTimeNear/Far` +0xa5c / +0xa68、`NoticeTimePeripheral` +0xa74，每项 Idle / Alert / Combat 三列，按 NPC 当前警觉状态取。

```
每次玩家扫描（距上次 > 0.15 s，常量 0x18089f31c）:
  对每个看得见的玩家 p（过了视野和视线）:
    if NPC 记得 p 且 now − 上次见到 < ForgetPostTime(5 s): 立刻发现
    找 / 建"正在发现"条目 {p, start, lastSeen}（新建时 start = now）
    d = |p.origin − npc.origin|（三维）
    T = d ≤ Near ? TimeNear : d ≥ Far ? TimeFar : lerp
    if T < TimePeripheral and p 偏离 NPC 前方 > 30°（dot < 0.866）: T = TimePeripheral
    if now − start < T: lastSeen = now; NPC 转头看（vfunc 0xd18）; 还没发现
    else: 发现，删条目
  扫描后: lastSeen 距今 ≥ ForgetPreTime(0.3 s) 的条目删掉（下次从 0 算）
```

NPC 打 NPC 用 `ai_sight_npc_search_time`（NPC 状态 > 2 时再加 0.1 s）当扫描间隔。

**和实测的关系：** 发现只在扫描时推进，开始和结束各被量化一次，比设置值多约 0.15–0.35 s，解释了"多出来的"偏移。但实测的斜率（0.00072 s/u）比 Idle 设置的斜率（0.9 / 1850 = 0.00049 s/u）大，这一点原生规则解释不了。可能是 NPC 当时在 Alert / Combat 列、该 NPC 的 aisettings 覆盖了默认值，或者远距离视线时断时续触发了 0.3 s 重置。已请 `ref-pilot-ai` 核对。

## 3. N3 `ApplyVectorSpread`（`weapons/README.md`、`SIDEWINDER-SMR.md`、`DOUBLE-TAKE.md`）

**不是原生。** 两个 dll 里都没有这个名字；它是脚本函数 `scripts/vscripts/weapons/_weapon_utility.nut:430`。

```
s = sin(spreadDegrees / 2)
shotBias = 2·bias − 1（bias 默认 1 → 1）；flatness = |shotBias|·0.5 = 0.5
重复: x = 0.5·U(−1,1) + 0.5·U(−1,1)；y 同理；直到 x² + y² ≤ 1
结果 = dir + right·x·s + up·y·s        （不再归一化）
```

- 每个轴是三角分布，截在单位圆里；最远偏离 = 散布角的一半（`GetAttackSpreadAngle` 的说明是"从锥的一边到另一边的度数"，见 §9）。
- 按公式模拟 20 万次（单位：最大偏离）：每轴 |x| 平均 0.32；半径中位数 0.50、平均 0.51、90 % 分位 0.83、99 % 分位 0.97。
- **负散布：** SMR / Flak 用 `GetAttackSpreadAngle() − 1`。腰射 0.5° → −0.5°，s 变负，只是偏移翻个方向，分布对称，所以**实际散布 = |角度 − 1| = 0.5°**。`SIDEWINDER-SMR.md` §3 "推断负值按 0"不对。开镜 0° → −1° → 实际 1°。
- 即时命中子弹（`FireWeaponBullet`）的散布在引擎里。脚本注释说代码用同一算法，bias 取自 `ai_shot_bias`（server 默认 "1.0"）。引擎这一条没有反编译核对 `[推断]`。

## 4. N4 导弹漂移 6 个键（`SIDEWINDER-SMR.md` §1.4）

原生 `InitMissileForRandomDrift(pos, dir, a, b, c, d, e, f)`（绑定 `0x1806724f0`）把 6 个参数按顺序写进导弹 +0x1d00…+0x1d14；被注释掉的旧脚本版（`_weapon_utility.nut:1433–1545`）给出了名字和顺序，涡旋打回用的两组固定值（8, 2.5, 0, 0, 100, 100）/（0.3, 0.085, 0, 0, 0.5, 0.5）也对得上：

| 偏移 | 键 | 备注 |
|---|---|---|
| +0x1cfc | 随机相位 r | RandomFloat(0, 1) |
| +0x1d00 | `projectile_drift_windiness` W | 乘时间，管频率 |
| +0x1d04 | `projectile_drift_intensity` I | ×dt 后是幅度 |
| +0x1d08 | `projectile_straight_time_min` | |
| +0x1d0c | `projectile_straight_time_max` | |
| +0x1d10 | `projectile_straight_radius_min` | FromWeaponSettings 版 `0x180675690` 里 < 1 按 1 |
| +0x1d14 | `projectile_straight_radius_max` | 同上 |

每帧 `0x1806758b0`（先调漂移 `0x180675ce0`）和旧脚本 `MissileControlledDrift` 一致：t < time_max 时，lerp = 1（t ≤ time_min）否则 1 − (t − min)/(max − min)；**半径 = rmax + (rmin − rmax)·lerp，从 radius_min 开始、到 time_max 时涨到 radius_max**（"从小到大"）。拉回速度 = −偏离·速率 / max(距离, 半径)，在半径内再加 startDir·速率·(1 − 距离/半径)，乘 I·dt 加上后保持速率。

## 5. N5 视角 punch 弹簧（`weapons/README.md`，也是 W9）

client.dll。每次移动更新 `0x1802041c0` → `0x1801f5210`，推两个弹簧：

| 弹簧 | 状态（角度 / 角速度） | 常数来源 |
|---|---|---|
| punch | 玩家 +0x1e1c / +0x1e28 | 玩家设置 `viewpunchspring`（springs.txt 一项），没有就用 `viewpunch_base_springConstantX/Y/Z` 65、`DampingX/Y/Z` 9 |
| 武器后坐 | 玩家 +0x1e34 / +0x1e40 | 当前武器的 `viewkick_spring`（springs.txt），没有就用同上的基础值 |

每轴（俯仰、偏航、滚转）的 k、c = lerp(hipfire_*, ADS_*, 开镜比例)（`0x1801fd600` / `0x1805a9380`，开镜比例 `0x1802c8440`）。

方程：x'' = −k·x − c·x'（springs.txt 开头的注释和这个一致：f = √(4k − c²)/(4π)，振幅半衰期 1.386 / c）。

两条积分路径，由 `VEngineClient013` 第 383 格（vtable +0xbf8）的返回值选：

- **A `0x1801efdd0`，固定步长 h = 0.0166 s（常数，不看帧长）：** 若 |x|² > 0.001 或 |v|² > 0.001：x += v·h；俯仰、滚转夹在 ±89，偏航 ±179；v = v·exp(−c·h) − k·x·h（用更新后的 x）。否则 x = v = 0。
- **B `0x1801f5100` → `0x180625bb0`，按帧长 dt 的解析解：** 判别式 c² − 4k > 1e-6 用过阻尼闭式（`0x180625ed0`），< −1e-6 用欠阻尼闭式（`0x180626240`，e^(−c·dt/2)·(cos/sin ω·dt)，ω = √(4k − c²)/2），否则临界阻尼：y = x·c/2 + v；x' = (x + y·dt)·e^(−c·dt/2)；v' = (y − x'·c/2)·e^(−c·dt/2)。同样有 0.001 的归零。

**没读出的：** 第 383 格是哪个引擎函数（在 engine.dll 里，这次没分析）。60 Hz 下 A、B 几乎一样；HSD 用 B（和帧率无关）即可。`ref-weapons-tail` 的 W1 实测曲线可以分辨：A 是半隐式欧拉，会有一点额外滞后。

## 6. N6 泰坦踩人（`kits/T-b-TITAN-VS-INFANTRY.md`）

每次泰坦移动 `0x180661360`，对每个候选目标 `0x180660c80`（`DoTitanStepDamage`）。设置键偏移：玩家设置 +0x21b0 伤害、+0x21b4 最低速度、+0x21b8 高度比例、+0x21bc 间隔、+0x21c0 距离间隔；aisettings +0x1ae8…+0x1af8 同一组（`set-schema-server.tsv`）。

```
if 泰坦离上次判定位置 < dist_interval（玩家 100，NPC 150）: 不判
if min_speed > 0 and 速度 < min_speed（50）: 不判
记下这次的位置
盒 = 泰坦碰撞盒（底面下移 1 u）；列出盒里的实体
对每个实体 e:
  跳过：泰坦、友军；NPC 要 aisettings +0x1893 标志；玩家 +0x4f1 时跳过
  跳过：玩家从 rodeo 跳下 0.1 s 内（titan_step_damage_rodeo_immunity_time）
  e 的盒要和泰坦盒相交，并且和"泰坦盒的下部"相交：mins.z … mins.z + 0.15·高度
  每个 e 单独计时：now − e 上次被踩 > interval（玩家泰坦 −1 → 总是过；NPC 泰坦 1.0 s）
  从泰坦盒中心到 e 盒中心做一次盒追踪（半尺寸 0.125·较小的盒尺寸，mask 0x200420b），要畅通
  → 一次伤害 = titan_footstep_damage（5000），伤害源 DF_TITAN_STEP
```

**规则：** 一次给 5000，不是"每秒"（设置键说明里的"每秒"和用法不符）。dash 不被排除，满足速度和距离就会踩。对 100 血的铁驭、50 血的步兵就是碰到即死。

## 7. N7 Ronin（`kits/RONIN.md`）

**`move_slow` / `dodge_speed_slow` 叠加：取最大值。** 状态效果查询 `0x180221c50` 遍历实体自己和父链（泰坦的 soul）上所有计时和无限的同类效果，取强度最大的那个。强度按字节存（值 / 255）；计时效果在最后的淡出时间里按曲线降（`0x1802219e0`）。

- 最大速度 = 基础 × 缩放 × (1 − move_slow) × speed_boost（`0x1805d2510`）。
- dodge 速度 = dodge 设置值 × (1 − dodge_speed_slow)（`0x1805d2210`）。

**相位期间的碰撞：** 玩家移动的追踪过滤 `0x18017e970`：自己处于相位（vfunc 0x658）时，不和泰坦、玩家、NPC 碰撞（NPC 只有带 +0x4f2 标志的才碰），世界和道具照常碰；没相位的玩家也穿过相位中的玩家。所以 Ronin 相位冲刺能穿过泰坦；出相位时重叠怎么办由脚本处理（`sh_phase_shift.gnut`：和泰坦重叠时自杀或互相推开 600，和人形重叠时把对方杀死）。另外：AI 的玩家扫描跳过相位中的玩家（§2 的 `0x1803b4a80`），系留遇到相位直接断（§8）。

**相位中能不能开枪：** dll 里没有和相位有关的开火键或开火判定（字符串全列过）。由脚本决定，原生没找到 `[要实测]`。

**`charge_cooldown_delay`、`fire_duration`：** 武器键表给出偏移（`charge_cooldown_delay` +0x324、`charge_cooldown_time` +0x320、`charge_time` +0x31c、`fire_duration` +0x30），但按偏移和按武器实体偏移（+0x1288 + 键偏移）都没找到运行时读取点。脚本里：`fire_duration` 只给 HUD 的反向充能条用（`cl_weapon_status.gnut:732`），另外有几个技能自己读它当持续时间；相位冲刺用脚本常量，不读它。`charge_cooldown_delay` 只有三个核心的脚本读。**结论：没找到原生含义** `[还缺]`。

## 8. N8 Northstar 系留（`kits/NORTHSTAR.md`）

`AddTether`（绑定 `0x1800cb6d0` → `0x1800dc820`）在玩家身上占一个槽（最多 2 个，每个 0x28 字节，玩家 +0x1368 起），绳子血 1000。每次移动更新 `0x18017f640`：

```
if 玩家在相位: 删掉这条绳
health −= tether_healthDrain(200)·dt                      # NPC 用 tether_healthDrainNPC 200
dz: 锚点在脚和脚 + 身高之间时 dz = 0；锚点在上方时竖直分量丢掉（只往下拉）
d = |(dx, dy, dz)|
if d ≤ tether_radius(250): 不拉
Δv = (d − 250)·tether_strength(25)·dt
朝锚点的速度 vt = v·dir；新 = min(vt + Δv, tether_maxvel(200))；补 max(新 − vt, 0)
health −= Δv·tether_damageScale(0.00)                     # 默认不扣
```

- 1000 / 200 = **5.0 s 后绳子断**，和 `tethered` 状态 5 s 一致。`tether_dodge_damage` 默认 0。所以默认设置下绳子只会按时间断或遇相位断，拉扯不扣血。
- NPC 被拴时用 `tether_npc_strength` 5（"每单位距离的速度"），读取点 `0x1803163f0`、`0x180318140`、`0x180318c80`、`0x1803192f0`，没逐行读。
- 注意拉的半径是 250，比陷阱的检测距离（玩家泰坦 350）小。

## 9. N9 `GetAttackSpreadAngle`（`kits/ION.md`）

绑定 `0x1800ca280` → 实体 vfunc +0x900。

- 玩家（`CPlayer::vftable` +0x900 = `0x1805dd680`）：当前武器 `0x1806907e0` = lerp(bloom 腰射 +0x1000, bloom 开镜 +0x1004, 开镜比例) + 当前散布 +0xff0。
- 当前散布在 `0x1806ab320` 里更新：按姿态（站 / 蹲 × 腰射 / 开镜双线性，移动、空中、冲刺、滑铲另算）得到目标值，每次最多变化一个武器自己的速率。
- NPC（`CAI_BaseNPC::vftable` +0x900 = `0x180307a10`）：武器 +0x1944（< 0 时 +0x1918）+ +0xff0。
- 返回值是整个锥角（引擎说明 "from one side of the cone to the other"）。

**Ion 涡旋：** `spread_stand_hip` = `spread_stand_ads` = 7，`ShotgunBlast` 用 × 0.5 → **半角 3.5°**，搜索 × 1.1。涡旋文件没写其他姿态的散布键（用默认值），空中等姿态可能不同，`ref-titan-tail-a` TA3 可以顺带看。

## 10. N10 `SetHomingSpeeds`（`kits/TONE.md`）

绑定 `0x1806721a0`：导弹 +0x1cbc = 第一个参数，+0x1cc0 = 第二个参数。`mp_weapon_yh803.nut` 的注释说明了含义："speed, speed for dodging player"。默认 `missile_homing_speed` 150。

每帧（有目标时）`0x180673770` → 转向 `0x1806718a0`：

```
H = 目标是正在 dash 的玩家（+0x2599）? 第二个参数 : 第一个参数
目标点（0x180673270）≈ 目标中心 + 2·dt·目标速度（提前量），可加每枚导弹自己的偏移（目标坐标系 +0x1cd4…dc）
u = 指向目标点的单位向量；s = dt·60
方向 = normalize(v + s·H·u)；速度 = 方向·|v|        # 只转向，速率不变
if min(旧, 新 的 v̂·u) < 0.5（偏 60° 以上）and 60·H·距离 < |v|²（转弯半径大于距离）and 距离 > 一个小半径:
    H ← max((1 − s)·H, 0)                          # 60 Hz 下 s = 1，H 立刻变 0
```

- 侧向时转向角速度约 60·H / |v| rad/s。
- **冲过头就永久丢追踪**（这枚导弹的 H 被清零）。
- Tone 追踪导弹（`mp_titanweapon_tracker_rockets.nut:91–110`）：起始 H = GraphCapped(距离, 400 → 1800, 200 → 100)，之后每 0.2 s +15，封顶 200，两个参数相同。齐射核心 `SetHomingSpeeds(100, 0)`：目标 dash 时完全不追。

## 11. N11 Legion 智能核心（`kits/LEGION.md`）

- **子弹怎么导向：** 没有飞行中的导向。智能弹药开火时用即时命中的"特殊子弹"，无散布，直接射向 `SmartAmmo_GetFirePosition(目标)`（`sh_smart_ammo.gnut:248–255`）。开火点 `0x18065b0a0`：目标模型有锁定附着点 / 命中盒时用它（+0xde4），否则用中心（某些类用接近眼睛的点）。
- **搜索角的含义：** 武器数据加载时拒绝 ≤ 0 或 ≥ 90 的值（提示"needs to be greater than 0 and less than 90 … Forcing it to 0.1 / 89"）。如果是整个锥角，上限应该是 180，所以是**半角** `[推断，按校验范围]`。Legion 60 → 偏离准星 ±60°（共 120°），距离 3000。每帧的搜索循环本身没找到（键表偏移 +0x850 没有运行时读取点，按索引 0x1ff 查也没命中）。
- **有效目标过滤**（`0x18065d140`）：不是自己、不在相位、活着、没有"不当目标"标志；带 NPC 标志的同队排除；最后由目标类自己的 vfunc 决定。

## 12. N12 舱框俯仰晃动的键（`kits/T-f-COCKPIT-RELOAD.md`）

client.dll `0x1804e7cf0` 每帧从玩家设置读 `cockpitSway*`（客户端设置偏移 +0x3f4…+0x43c，`local/set-schema-client.tsv`），填一张"输入 → 舱框位移 / 角度"的映射表，交给 `0x1805939c0` 推进，最后过 `cockpit_spring_*`（俯仰 65 / 9）。

表里 `cockpitSwayTurnAngleFactor`（−4）、`TurnOriginFactor`（−1）、`TurnAngleRollFactor`（0）各被写进 4 格（带正负号），`Move*` 三个键也各 4–6 格。一个键出现在两组格子里，说明它管两个输入轴：转身（偏航角速度）和俯仰角速度。**推断：俯仰晃动没有单独的键，和转身共用 `cockpitSwayTurnAngleFactor` / `TurnOriginFactor`，经 `cockpit_spring_pitch*` 平滑。** 映射表每格对应哪个输入、哪个输出没有逐格对上 `[推断]`。

## 13. N13 `IsCriticalHit`（`kits/NORTHSTAR.md`）

绑定 `0x18029d480` → `0x180600fa0`，参数（攻击者、受害者、命中盒、伤害、伤害类型）：

```
攻击者、受害者都不为空，伤害 > 1，伤害类型不带 0x20
攻击者通过一个类检查（vfunc 0x298），且攻击者 ≠ 受害者
受害者没有标志 0xd8 & 0x800；是泰坦类时它的 soul 也没有
受害者（或它的 soul）+0x7b4 > 0 且 +0x7b0 > 0 → 不算暴击      # 推断是护盾值和护盾上限：有盾不暴击
命中盒 ≥ 0：在受害者模型的命中盒集里，这个命中盒的标志位 1 → 暴击
```

- 伤害类型 0x20：按脚本 `DF_*` 的顺序（`DF_GIB` 是第 1 位）是 `DF_BYPASS_SHIELD` `[推断]`。
- 哪些命中盒算暴击由模型决定（MDL 命中盒的标志位），不是代码里的部位表。
- vfunc 0x298 是哪个类检查、0x800 是哪个标志，没追到名字。

## 14. 发出去核对的

| 项 | 发给 | 时间 |
|---|---|---|
| N1、N2 | `ref-pilot-ai` | 11-12 |
| N3、N4、N5（N3 另发一次统计值更正） | `ref-weapons-tail` | 11-12 |
| N6–N9 | `ref-titan-tail-a` | 11-12 |
| N10、N11 | `ref-titan-tail-b` | 11-12 |

**回复（11-12）：** `ref-weapons-tail` 独立核对了 N3、N4，结果一致（同一份被注释的脚本；SMR 的散布按 |角度 − 1| 算）。它用 `wp_e` 的 SMR 弹道做自由漂移拟合：按本页槽位，误差 5–20 u rms；把 W 和 I 对调，误差 48–135 u。N5 纠正了它读错的 punch 偏移：武器弹簧的角度在 +0x1e34，角速度在 +0x1e40。A / B 两条积分路径用哪条，等 TF2 再开时用实测曲线区分。

## 15. 文件

| 文件 | 放在哪 |
|---|---|
| 本报告、`AiDig.java`（加了 `nat:` / `find:` / `vslot:`）、`vastr.py` | 研究仓库 `tf2/ref-native-tail/` |
| 各出处页的"11-12 原生"一段 | 研究仓库各页"还缺"后面 |
| 反编译原文 `t*.txt`、`n*.txt`、`dec-server/`、`dec-client/`、`readers-*.tsv`、`obj-*.tsv`、`imm-n11.txt`、`dig.sh` | HSD-RawData `tf2/local/nattail/`（分支 `ref/native-tail-raw`；本地原件 `TF2-Research/local/nattail/`；D-76，不进公开仓库） |
