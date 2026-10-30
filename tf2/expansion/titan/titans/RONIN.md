# Ronin（Stryder）

设置文件 `titan_stryder_leadwall.set`（底盘 `titan_stryder.set`）。多人：血 7500，护盾上限 2500，每段 2500，濒死 2500。

## HSD 怎么做

- 近身刺客。核心循环：用**相位冲刺**贴脸 → 散弹 + 剑 → 用**剑格挡**扛伤害。机动性是七台里最高（Stryder 底盘 + 两次 dash + 相位冲刺）。
- 相位冲刺：按下瞬间沿移动输入方向给 1000 u/s 水平速度，1 s 相位（不可被打），然后靠地面摩擦衰减。HSD 可以直接照搬"速度冲量 + 无敌窗口"这个规则。
- 剑格挡：按住时正面 150° 锥形内的伤害 × 0.3，近战 / 骑乘不减。剑核心期间 × 0.15。
- 剑核心：12 s 只能用剑（伤害 800 → 2200），冲刺能量立即回满，回能 × 6.5，击杀泰坦每次续 8 s。

## 移动和转向

| 项 | 值 | 证据 |
|---|---|---|
| 走 / 后退 / 侧移 / 冲刺跑 | 270 / 270 / 270 / 400 | `t0_move` `20261030_015751`、`014930` |
| ADS 走速 | 135（× 0.5） | `t0_kit` `20261030_020515`；`mp_titanweapon_leadwall.txt` `ads_move_speed_scale` 0.5 |
| dash | 800 u/s，保持约 0.2 s，2 次，每次耗 50，回能 10 /s | `t0_move`；`titan_stryder_leadwall.set` `dodgePowerDrain` 50、`powerregenrate` 10 |
| 相位冲刺 | 按下当帧 967 u/s，1.3 s 内降回走速（约 590 u/s²） | `t0_kit` `keyoff2_ronin` |
| 转向 | 和铁驭相同；手柄 × 0.75 | [../T0-REPORT.md](../T0-REPORT.md) 第 2 节 |

## 套件

| 槽 | 名字 | 怎么用 | 数值 | 出处 |
|---|---|---|---|---|
| 主武器 | 散弹枪（`mp_titanweapon_leadwall`） | 半自动，每发 8 颗弹丸，弹丸有重力 0.4 | 每颗近 60 / 远 25（对泰坦 100 / 75），600 → 1000 u 衰减；射速 2.5 /s；4 发；换弹 2.25 s | `mp_titanweapon_leadwall.txt`；`.nut` 84 行（重力） |
| 进攻（Q） | 电弧波（`arc_wave`） | 地面向前推进的电弧，打中减速 | 对铁驭 75 / 对泰坦 1000；命中目标 `move_slow` 0.5 + `dodge_speed_slow` 0.5，2 s（淡出 1 s）；冷却 10 s（100 ÷ 10） | `mp_titanweapon_arc_wave.txt`；`.nut` 188–189 行 |
| 防御（中键） | 剑格挡（`basic_block`） | 按住举剑 | 伤害 × 0.3（剑核心 × 0.15）；锥形 150°；近战、骑乘、濒死扣血不减；走速不变 | `mp_titanability_basic_block.nut` 199–200、279 行；`t0_kit` `holdoff1_ronin` 270 |
| 战术（G） | 相位冲刺（`phase_dash`） | 按下沿移动方向冲出并相位 1 s | 速度 1000（+竖直 200，在地上被地面吃掉）；相位 1 s；自身 `move_slow` 0.6，1.5 s；冷却 12.5 s（200 ÷ 16）；升级 `pas_ronin_phase` 8.3 s | `mp_titanability_phase_dash.nut` 8、14–33 行；`.txt` |
| 核心（V） | 剑核心（`shift_core`） | 0.75 s 拔剑，12 s 只能用剑 | 剑 800 → 2200（`super_charged` +1400），范围 325，角度 45；冲刺能量立即回满，回能 × 6.5；击杀泰坦续 8 s；充能 120 s | `mp_titancore_shift_core.nut` 30–40、138–139 行；`melee_titan_sword.txt` |
| 近战 | 剑 | | 800，距离 325 | `melee_titan_sword.txt` |

## 实测

- 7 台共用：召唤、上机、转向、移动见 [../T0-REPORT.md](../T0-REPORT.md)。
- `20261030_020515_t0_kit`：相位冲刺速度曲线、格挡和核心时走速不变（270）。
- 未实测：伤害数值、格挡减伤（需要敌人开火，可用 W1 的 `hsd_npc … hostile`）。
