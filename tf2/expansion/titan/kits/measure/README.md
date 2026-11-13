# 泰坦套件补测工具（`measure/`，2026-11-13，`tf2-kits-measure`）

## 先说结论

这一组工具是为补测泰坦套件规格页里"还缺的"弹道和运动曲线写的：每帧记投射物位置、智能弹药的锁定进度、铝热火团、玩家位置，还能让敌方泰坦用脚本开火（不靠它的 AI）。结果写在各泰坦页第 8 节和 [../PROJECTILES.md](../PROJECTILES.md)。

最要紧的一条坑：**不要把 `ProjectileGetWeaponClassName()` 的返回值放进 `format()`**。它对一部分投射物返回坏字符串，`format` 的 `%s` 读到就让 `server.dll` / `client.dll` 直接崩溃（不是脚本错误，进程崩溃）。11-13 因此作废 4 次运行。

## 文件

| 文件 | 作用 |
|---|---|
| `mod/HSD.KitMeasure/` | 探针模组。只在 `kitm_runner.py` 的运行里装进游戏，游戏退出后、放锁前删掉，不影响别的会话 |
| `kitm_runner.py` | `runtime/runner.py` 加装这个模组；Steam 必须已经开着（runner 自己启动的 Steam 起不了游戏，11-12） |
| `plans_km.py` | 实验表：`km_monarch`、`km_proj`、`km_ion`、`km_scorch`、`km_hover`（`--map mp_homestead`）、`km_tether`、`km_shared` |
| `km_tools.py` | 读 `diag.tsv` 的工具（客户端 / 服务端时钟对齐） |
| `an_expand.py` | 张开 / 收拢导弹的弹道（客户端每帧，拼接本地预测和服务端两份实体） |
| `an_lock.py` | 智能弹药锁定进度、发射枚数 |
| `an_proj.py` | 服务端 10 Hz 的投射物：初速、竖直加速度、寿命 |
| `an_ion.py` | 涡旋接住、打回：速度、方向、伤害 |
| `an_scorch.py` | 铝热火团：几个、滑多远、最后的分布、每个伤害源的跳数 |
| `an_hover.py` | 悬停 / 飞行核心的高度曲线 |
| `an_tether.py` | 系留陷阱（敌人被拴，只测到一部分） |
| `an_homing.py`、`an_homing_end.py` | 逐帧转向角速度、反推 `SetHomingSpeeds` 的 H |
| `an_graze.py` | 擦边测试：经过靶子时离中轴多远、有没有直接命中 |

运行：

```bash
py -3 -I kitm_runner.py km_monarch --timeout 600
```

```bash
py -3 -I an_expand.py ../../../../runtime/data/<运行> sv_1
```

## 探针命令（服务端，客户端控制台发）

| 命令 | 作用 |
|---|---|
| `hsd_km_log 0\|1` | 每个服务端帧（10 Hz）记 `TS`（玩家）、`TF`（我放的敌人）、`PSNEW` / `PS`（投射物位置和速度）、`PF`（有主人的 `prop_physics` = 铝热火团）；`TD` 记最终伤害 |
| `hsd_km_foe <setfile> f r yaw [static\|idle\|hostile] [hp]` | 在玩家前方 f、右方 r 放敌方 NPC 泰坦，护盾 0。`idle` 会自己乱走，要固定位置用 `static` |
| `hsd_km_fire <idx> <kind> <n> <gap> [dz]` | 让第 idx 个敌人朝玩家眼睛（+ dz）开 n 发：`40mm`、`meteor`、`sniper`、`salvo`、`tracker`、`leadwall`。照原武器脚本的速度和重力调 `FireWeaponBolt` / `FireWeaponMissile` |
| `hsd_km_walk <idx> dx dy` | 敌人走到出生点 + (dx, dy) |
| `hsd_km_die` | 杀掉铁驭（`mp_homestead` 第一次是运输机出场，之后叫的泰坦会被锁住，要先死一次） |
| `hsd_km_head [x y z]` | 某点头顶泰坦大小的净空 |
| `hsd_km_smoke_give` | 把电烟放进 `OFFHAND_INVENTORY`（配 `+ability 6`） |
| `hsd_km_nukepas` | 把 Nuclear Ejection 被动直接给玩家（`GetNuclearPayload` 读玩家身上的被动） |
| `hsd_km_slide <idx> vx vy dur` | 冻结的敌人按恒定速度平移（每个服务端帧 `SetOrigin`，10 Hz 一跳） |
| `hsd_km_aimfoe <idx>` | 视角对准敌人中心 |
| `hsd_km_fire ... tether ...` | 敌人用 `FireTether` 对玩家扔系留陷阱 |

客户端每帧：`PC`（玩家位置、速度、视角、眼睛）、`PJNEW` / `PJ` / `PJEND`（只限 `rpg_missile`）、`SA`（当前武器和三个副手的 `SmartAmmo_GetTargets()`：目标、`fraction` = 锁的把数）。

## 踩过的坑（11-13）

1. `ProjectileGetWeaponClassName()` / `ProjectileGetDamageSourceID()` / `ProjectileGetMods()`：在服务端对脚本开的弹体、在客户端对部分导弹返回坏值，放进 `format()` 让进程崩溃（`server.dll+0x79fa1` / `client.dll+0x7a011`，都在 Squirrel 的 `format` 里）。现在两边都不调用；武器从时间段和标签判断。
2. 客户端 `GetProjectileArrayEx` 只要场上有 `crossbow_bolt`（40 mm、狙击、铝热、霰弹）就报错（"Failed to CreateScriptInstance for crossbow_bolt"），加类名过滤也一样：现在出错的那一帧跳过、下一帧再试；弹体本身只有服务端 10 Hz 的数据。
3. 客户端实体没有 `GetEncodedEHandle`；客户端按实体自己编号。
4. 本地玩家的导弹在客户端是两份：本地预测的那份活约 0.1 s，然后换成服务端那份。`an_expand.py` 按位置拼接。
5. `format()` 里拼字符串（`"..." + x`）的行偶尔丢掉开头的 `HSDDIAG ...`，被 runner 漏掉；全部改回 `format`，参数先过 `HsdKm_S()`（null 变 "-"）。
6. 敌方泰坦被自己脚本开的 40 mm 打中**玩家**时也崩溃过一次（原因同 1）；涡旋接住时不会碰到玩家。
7. NPC 给第二把主武器会报"No room in inventory"：先收掉原来的。
8. `idle` 的敌人会走动；需要固定靶子用 `static`（冻结的 NPC 仍然能被脚本开火）。
