# Northstar（Stryder）

设置文件 `titan_stryder_sniper.set`（底盘 `titan_stryder.set`）。多人：血 7500，护盾上限 2500，每段 2500，濒死 2500。

## HSD 怎么做

- 远程狙击手 + 空中机动。两项和移动有关：**悬停**（战术）和**飞行核心**。
- 悬停规则（照搬即可）：重力设成 0，竖直速度按时间曲线（0.5 s 内从 225 升到 450，再 0.75 s 降到 70），总共 3 s；水平空速上限 250（被动升级 350），每帧再把水平速度夹到上限 + 50；悬停中不能 dash、不能下机。实测效果：1.8 s 升到离地 340 u，悬停到 3 s，然后自由落下。
- 飞行核心：同一套悬停逻辑，持续 6 s，水平上限 200，主武器换成 12 发 /s 的火箭。
- 狙击炮：按住 ADS 蓄力，5 级，2.25 s 满。

## 移动和转向

| 项 | 值 | 证据 |
|---|---|---|
| 走 / 后退 / 侧移 / 冲刺跑 | 270 / 270 / 270 / 400 | `t0_move` |
| ADS 走速 | 135（× 0.5，狙击炮没写 `ads_move_speed_scale`，用默认） | `t0_kit` |
| dash | 800，2 次，每次耗 50，回能 10 /s | `t0_move`；`titan_stryder_sniper.set` |
| 悬停 | 竖直速度最高 401（0.5 s），1.8 s 到 340 u，3.0 s 开始下落（下落加速度约 750 u/s²），约 4.0 s 落地；水平 271 | `t0_kit` `keyoff2_northstar` |
| 飞行核心 | 0.25 s 起飞，到 340 u 后在 334–340 u 之间以约 1 s 周期起伏，水平上限 250，约 7.0 s 落地 | `t0_kit` `core_northstar` |
| 转向 | 和铁驭相同；手柄 × 0.75 | T0-REPORT 第 2 节 |

## 套件

| 槽 | 名字 | 怎么用 | 数值 | 出处 |
|---|---|---|---|---|
| 主武器 | 电浆狙击炮（`mp_titanweapon_sniper`） | 按住 ADS 蓄力，松开开火；弹道几乎无重力（0.001），速度 10000 | 基础 250，暴击 × 1.5；每级额外伤害 `damage_additional_bullets` 250（对泰坦 300）；5 级，2.25 s 满；6 发，换弹 2 s；`instant_shot` 升级 1200 | `mp_titanweapon_sniper.txt`；`.nut` 17–20、180 行 |
| 进攻（Q） | 集束导弹（`dumbfire_rockets`） | 一发直射火箭，命中后持续子爆炸 | 撞击 300；子爆炸 66 / 150（半径 150–220）；冷却 9 s（180 ÷ 20，延迟 1 s） | `mp_titanweapon_dumbfire_rockets.txt` |
| 防御（中键） | 系留陷阱（`tether_trap`） | 扔出陷阱，靠近的泰坦被绳子拉住 | 一次 1 个（升级 2 个），场上最多 4 个（升级 8）；冷却 20 s（200 ÷ 10） | `mp_titanability_tether_trap.nut` 6、30–39 行；`.txt` |
| 战术（G） | 悬停（`hover`） | 见上 | 3 s；冷却 10 s（200 ÷ 20）；悬停中 `dodge_speed_slow` 0.65 | `mp_titanability_hover.nut`（`FlyerHovers`、`RISE_VEL` 450、`LERP_IN_FLOAT` 0.5） |
| 核心（V） | 飞行核心（`flight_core`） | 起飞 1 s 后可开火，6 s，结束 1 s 落地 | 火箭 300 撞击 + 55 / 300 爆炸（半径 150），12 发 /s；充能 150 s | `mp_titancore_flight_core.nut`；`mp_titancore_flight_core.txt`；`mp_titanweapon_flightcore_rockets.txt` |
| 近战 | 拳 | | 500，距离 280 | `melee_titan_punch_northstar.txt` |

## 实测

- `20261030_020515_t0_kit`：悬停和飞行核心高度曲线（上表）。
- 未实测：蓄力伤害、系留时长。
