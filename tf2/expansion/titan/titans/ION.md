# Ion（Atlas）

设置文件 `titan_atlas_stickybomb.set`（底盘 `titan_atlas.set`）。多人：血 10000，护盾上限 2500，每段 2500，濒死 2500。

## HSD 怎么做

- **能量泰坦**：进攻、防御、战术和主武器的 ADS 共用一个能量池，总量 1000，用完停 0.2 s 后每秒回 80。这是 Ion 和其他泰坦（各技能独立冷却）最大的区别，HSD 要做 Ion 就要先做这个池。
- 主武器暴击回能：暴击回 30（ADS 分裂射击回 8）。
- 激光核心是七台里唯一**降自己转向**的技能（`turn_slow` 0.25 + `move_slow` 0.25，3.5 s + 2 s 淡出），也就是"开大招时变重"的例子。
- 涡旋护盾：按住时接住飞来的子弹 / 投射物，松开时打回去；按住期间持续耗能。

## 移动和转向

| 项 | 值 | 证据 |
|---|---|---|
| 走 / 后退 / 侧移 / 冲刺跑 | 250 / 250 / 250 / 380 | `t0_move` |
| ADS 走速 | 188（× 0.75） | `t0_kit`；`mp_titanweapon_particle_accelerator.txt` `ads_move_speed_scale` 0.75 |
| dash | 700，1 次，耗 100，回能 16.66 /s（6 s 回满） | `t0_move`；`titan_atlas_stickybomb.set` |
| 激光核心中 | 走速 250 → 188，约 5 s 后 2 s 内恢复 | `t0_kit` `core_ion` |
| 转向 | 和铁驭相同；核心期间 `turn_slow` 0.25：鼠标转速 × 0.506（实测），键盘不受影响 | T0-REPORT 第 2.3、2.5 节；`20261030_023602_t0_mouseslow` |

## 套件

| 槽 | 名字 | 怎么用 | 数值 | 出处 |
|---|---|---|---|---|
| 能量池 | 共享能量 | 进攻、防御、战术、主武器 ADS 都从这里扣 | 1000；停 0.2 s 后每秒回 80（多人） | `titan_atlas_stickybomb.set` `sharedEnergy*` |
| 主武器 | 分裂步枪（`particle_accelerator`） | 全自动；ADS 时一次 3 发（升级 5 发），每次耗能 30 | 对铁驭 25 → 20，对泰坦 80 → 60（1000 → 1700 u）；射速 9 /s；40 发；换弹 4 s；弹速 8000；暴击回能 30 / 8 | `.txt`；`.nut` 17–31 行 |
| 进攻（Q） | 激光射击（`laser_lite`） | 瞬发激光 | 对铁驭 300 / 对泰坦 1200；耗能 550 | `mp_titanweapon_laser_lite.txt` |
| 防御（中键） | 涡旋护盾（`vortex_shield_ion`） | 按住接子弹，松开打回 | 启动耗能 5 %；按住每帧耗能 `shared_energy_charge_cost` 2；打回伤害 35 / 140 每发；走速不变（`t0_kit` 250） | `.txt`；`mp_titanweapon_vortex_shield.nut` 25 行 |
| 战术（G） | 绊线（`laser_trip`） | 扔出 3 个塔，之间连激光，敌人碰到爆炸 | 对铁驭 200 / 对泰坦 1500，半径 400；1 s 展开，存在 12 s，最多 9 个塔，塔血 300；耗能 350，冷却 10 s（200 ÷ 20） | `mp_titanability_laser_trip.nut` 24–38 行 |
| 核心（V） | 激光核心（`laser_cannon`） | 蓄力 1.1 s，然后 3.5 s 持续粗激光 | 每次命中 325，射程 6000；期间不能 dash、不能用技能；自身 `move_slow` 0.25 + `turn_slow` 0.25；充能 150 s | `mp_titancore_lasercannon.nut` 12–13、104–120、186–200 行；`.txt` |
| 近战 | 拳 | | 500，距离 280 | `melee_titan_punch_ion.txt` |

## 实测

- `20261030_020515_t0_kit`：核心期间走速 188（= 250 × 0.75）。
- 未实测：能量消耗曲线（可在 `TT` 日志里加 `GetSharedEnergyCount`）、核心期间鼠标转速。
