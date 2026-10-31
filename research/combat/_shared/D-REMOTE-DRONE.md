# 公共部件 D：可操控的远程载具（玩家"坐进"一个远处的实体）

批次 D 共用，会话 `combat-d`，2026-10-31。只读脚本。

来源：Crypto 无人机（`research-src/s21-platform/scripts/vscripts/weapons/mp_ability_crypto_drone.nut`，CD；Respawn 原版为主）。详细见 [crypto-drone](../crypto-drone/SYSTEM.md)。

## 0. 概要

- **部件**：`CryptoDrone_CreateFlyingCameraVehicle`（CD:1210-1329）+ `SwapToCameraView_Thread`（CD:1663-1901）+ `TransitionOutOfCamera`（CD:1949-2047）+ 召回 / 超距（CD:1061-1127、1427-1436）。
- **一句话**：建一个能受伤的 `player_vehicle`，进视角时把玩家设成它的驾驶员、身体冻结在原地、HUD 换皮、按键重绑；出来时淡出淡入、恢复一切；离太远或被打掉就收回。
- **分类**：系统。
- **谁能用**：遥控无人机、操控炮台、操控伙伴、远程摄像头、"附身"类技能。

## 1. 实现手段

| 部分 | 手段 | 来源 |
|---|---|---|
| 载具 | `player_vehicle` + `VEHICLE_FLYING_CAMERA`（引擎提供飞行控制） | CD:1218、1255 |
| 进入 | `VehicleSetDriver( 玩家 )` + 状态效果 `camera_view` + `ContextAction_SetInVehicle` + 隐藏 HUD | CD:1693-1713 |
| 身体 | 留在原地，可被攻击；头上加 3P 面罩粒子，背上的无人机模型隐藏 | CD:1762、1903-1916 |
| 按键 | `AddButtonPressedPlayerInputCallback` 在进入时注册、出来时注销 | CD:1753-1756、1953-1957 |
| 可见性 | 进入时载具和它的粒子"只对敌我可见"，出来后"所有人可见"（避免主人看到自己的载具外壳） | CD:1716-1732、1979-1996 |
| 出来 | `ScreenFade` 0.2 s 出 / 0.1 s 入，`AnimViewEntity_SetLerpOutTime( 0.3 )` | CD:1959-2026 |
| 防误入 | 状态效果 `script_helper` 0.25 s | CD:2035 |
| 状态管理 | 都用状态效果（`crypto_has_camera`、`camera_view`、`…_is_recalling`、`…_is_emp`）——客户端靠状态效果回调换 HUD | CD:227-232 |

## 2. 流程

```
创建（扔出 / 原地）→ 待机（有 AI 逻辑：扫描）
   ⇄ 进入 / 出去（同一个键）
   → 召回（动画 → 销毁，不扣冷却）/ 被毁（爆炸，扣冷却）/ 超距（自动召回）
打断进入状态：主人死亡、开始相位、倒地、跳伞、载具被毁
```

## 3. 代码要点

- 创建模板：见 crypto-drone 3.2.2（血量、碰撞组、AI 可攻击、登记声呐 / EMP、小地图图标只给本队）。
- 进入 / 出去：见 crypto-drone 3.2.3。
- "主人身体在载具里时干别的"：自动换弹（每 0.4 s，一次一把，用真实换弹时间，CD:1780-1875）——这是"远程操作时本体不闲着"的好例子。
- 被打时：给"再次进入"加 1.4 s 冷却（CD:726）。原版应该会把主人踢出视角，本地版客户端回调是空的（CD:637-643）。

## 4. 参数

| 参数 | 值 | 来源 |
|---|---|---|
| 进入可用延迟 | 1.25 s（出手后） | CD:1418 |
| 过场 | 1.2 s | CD:586 |
| 淡出 / 淡入 / 视角插值 | 0.2 / 0.1 / 0.3 s | CD:1961、2022、2025 |
| 防误入 | 0.25 s | CD:2035 |
| 被打后不能进 | 1.4 s | CD:95 |
| 最远 / 警告 / 自动召回 | 7913 / 5906 / 9496 u | CD:92-93、1430 |
| 载具血量 | 50 | CD:106、205 |
| 自动换弹检查 | 0.4 s | CD:1874 |
| 飞行速度 | **未知（引擎）** | — |

## 5. 未解决和要实测的

飞行速度 / 加速度 / 碰撞尺寸都在引擎：见 crypto-drone 第 5 节。

## 6. HSD 实现

未实现。建议 `RemoteControl` 接口：
```
interface IRemoteControllable {
  Vec3d EyePos; Vec3d EyeAngles;
  void ApplyInput( MovementInput i, double dt );   // 无人机：飞；炮台：只转；伙伴：走
  bool CanEnter( Player p ); void OnEnter(); void OnExit();
}
```
`PracticeSession` 增加"当前被控对象"：非空时相机挂过去、玩家身体不吃输入、战斗键转发给被控对象。进出用 0.2 / 0.1 s 淡出淡入，HUD 换皮。
