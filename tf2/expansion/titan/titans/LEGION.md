# Legion（Ogre）

设置文件 `titan_ogre_minigun.set`（底盘 `titan_ogre.set`）。多人：血 12500，护盾上限 2500，每段 2500，濒死 2500。

## HSD 怎么做

- **重机枪 + 姿态**：转管（ADS）后射速和精度更好，但走速 × 0.55。枪盾和强力射击都会强制进入 ADS，所以也都会减速。"开火前要站定"就是 Legion 的机械感来源，HSD 可以照搬：瞄准即减速，升级减轻（× 0.75）。
- 弹药模式切换：近距（散布大）和远距（散布小、伤害距离更远）两种。
- 智能核心：12 s（升级 18 s）主武器自动锁定，伤害 +20 %，不耗弹药。

## 移动和转向

| 项 | 值 | 证据 |
|---|---|---|
| 走 / 后退 / 侧移 / 冲刺跑 | 210 / 210 / 210 / 310 | `t0_move` |
| ADS（转管）走速 | 116（× 0.55；升级 `pas_legion_spinup` × 0.75） | `t0_kit`；`mp_titanweapon_predator_cannon.txt` |
| 枪盾、强力射击期间 | 116（强制 ADS） | `t0_kit` `holdoff1_legion`、`keyoff0_legion` 139（蓄力中） |
| dash | 600，1 次，耗 100，回能 10 /s | `t0_move`；`titan_ogre_minigun.set` |
| 智能核心 | 走速不变 | `t0_kit` `core_legion` |
| 转向 | 和铁驭相同；ADS 时鼠标灵敏度用 `mouse_sensitivity_zoomed`（未实测） | T0-REPORT |

## 套件

| 槽 | 名字 | 怎么用 | 数值 | 出处 |
|---|---|---|---|---|
| 主武器 | 掠食者机枪（`predator_cannon`） | 全自动，ADS 时转管 | 对铁驭 35 → 25，对泰坦 100 → 72（1200 → 1800 u；远距模式 3000 → 3250）；15 发 /s；100 发（升级 140）；换弹 4.6 s | `.txt`（`LongRangeAmmo`、`pas_legion_weapon`） |
| 进攻（Q） | 强力射击（`power_shot`） | 强制 ADS，蓄力 0.75 s 后一发 | 对泰坦 2000（近距模式散布 16、远距模式带爆炸 200 / 1800），击退；冷却 8 s（80 ÷ 10，延迟 1 s） | `.txt`；`mp_titanweapon_predator_cannon.txt` `CloseRangePowerShot` / `LongRangePowerShot` |
| 防御（中键） | 枪盾（`gun_shield`） | 强制 ADS，枪前一个半球盾 | 2500 血（升级 5000），半径 105；6 s；冷却 8 s（200 ÷ 25） | `mp_titanability_gun_shield.nut` 13–15、67 行；`.txt` |
| 战术（G） | 切换弹药模式（`ammo_swap`） | 近距 ↔ 远距 | 冷却 2 s（200 ÷ 100） | `.txt`；`.nut` |
| 核心（V） | 智能核心（`siege_mode`） | 瞬发 | 12 s（升级 18 s）；主武器加 `Smart_Core`：腰射和 ADS 都能自动锁定（最多 6 个目标），不耗弹药；伤害 +20 %（`titan_damage_amp` 0.2）；强力射击和枪盾回能 × 10；充能 150 s | `mp_titancore_siege_mode.nut` 89–165 行；`.txt` |
| 近战 | 拳 | | 500，距离 280 | `melee_titan_punch_legion.txt` |

## 实测

- `20261030_020515_t0_kit`：ADS、枪盾、强力射击减速。
- 未实测：转管时间（`zoom_time_in`），ADS 时的鼠标转速。
