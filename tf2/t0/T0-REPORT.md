# T0 报告：盘点与环境

日期：2026-10-28。按 `TF2-PLAN.md` 第 2、3 节执行。

## 1. 版本

| 项 | 值 |
|---|---|
| 游戏 | Titanfall 2 v2.0.11.0（`gameversion.txt`），Steam |
| Northstar | 1.31.14（`Northstar.dll` 文件版本；三个自带模组 `mod.json` 都是 1.31.14） |
| 安装路径 | `C:\SteamLibrary\steamapps\common\Titanfall2` |

二进制清单（路径、大小、sha256）：[binaries.csv](binaries.csv)。移动研究的主要目标：

| 文件 | 大小 | 用途（预期） |
|---|---|---|
| `server.dll`（根目录） | 13.7 MB | 服务端移动、playersettings 默认值、ConVar |
| `bin\x64_retail\client.dll` | 13.6 MB | 客户端预测移动、镜头（落地踢、晃动、侧倾） |
| `bin\x64_retail\engine.dll` | 9.8 MB | 引擎 ConVar、tick |
| `bin\x64_retail\vstdlib.dll`、`tier0.dll` | — | ConVar 系统 |

## 2. VPK 解包

- **工具**：pg9182/tf2vpk（Northstar 维护者写的 Go 命令行工具，内置 LZHAM 解码 `pg9182/tf2lzham v0.0.8`）。
  - 用户批准方案：从源码编译（GitHub 没有发布包，nightly 构建已过期）。
  - 源码：`https://github.com/pg9182/tf2vpk`，commit `b73c54d8e4245075ea207c7e51a2a86fdb94e4ff`（2025-02-16），克隆在 `C:\Tools\tf2vpk-src`。
  - 编译器：Go 1.27.3 官方 zip（`https://go.dev/dl/go1.27.3.windows-amd64.zip`，79,010,309 字节，sha256 `f26081f4…7885fff` 已校验），解压在 `C:\Tools\go1.27.3`。模块缓存在 `C:\Tools\gopath`。
  - 产物：`C:\Tools\tf2vpk\tf2vpk.exe`（`CGO_ENABLED=0`，纯 Go）。
- **用法**（在 Bash 里跑，PowerShell 管道会破坏二进制流）：

  ```bash
  /c/Tools/tf2vpk/tf2vpk.exe tar --vpk-dir 'C:\SteamLibrary\steamapps\common\Titanfall2\vpk' client_mp_common.bsp.pak000 -e 'scripts/**' | tar -x -C <目标>
  ```

- **已解包**（只取 `scripts/`、`cfg/`、`resource/`）到 `local/vpk/`：`client_mp_common`（855 个文件）、`client_frontend`（462）、`client_sp_training`（857）。
- 全部 38 个 VPK 的文件列表在 `local/vpk-lists/`，统计见 [vpks.csv](vpks.csv)。

## 3. `.set` 和 `.nut` 位置图

完整表：[scripts-map.csv](scripts-map.csv)（1058 个不同路径；列：路径、所在 VPK 数、首个 VPK、是否被 Northstar 模组覆盖）。

- **`.set`（playersettings）**：只在 `scripts/players/mp/`，共 76 个，`client_mp_common` 和每个 `client_sp_*` 里各有一份同样的集合。地图包里没有。
  - 铁驭链：`pilot_base.set` → `pilot_mp.set` → 各职业（`pilot_grapple`、`pilot_stalker`、`pilot_geist`、`pilot_medium`、`pilot_heavy`、`pilot_nomad` 等，含 `_male`/`_female`）。
  - 单人：`pilot_solo_training.set`、`pilot_solo_timeshift.set` 等。
  - 泰坦：`titan_base.set` 和各型号。
- **`.nut`/`.gnut`（Squirrel 脚本）**：`scripts/vscripts/`。`client_mp_common` 363 个，`client_sp_*` 约 425–437 个，`client_frontend` 161 个（UI）。和移动有关的目录：`pilot/`、`rodeo/`、`titan/`、`class/`、`melee/`、`weapons/`（技能如钩爪、兴奋剂、相位都在这里）。
- **Northstar 覆盖**：377 个路径被 `Northstar.CustomServers` / `Northstar.Custom` / `Northstar.Client` 覆盖（主要是服务端游戏模式脚本）。研究时以 VPK 原文为准，模组版只作参考。
- **初看结论**：`pilot_base.set` 里与移动有关的只有少数几项（`slidedecel 50`、`slidevelocitydecay 0.7`、`wallrun_timeLimit 4.0`、`wallrun_hangTimeLimit 4`、钩爪 `grapple_*` 一组、冲刺镜头 `sprint*`）。速度、加速度、跳跃等大多数没写，说明它们用的是 DLL 里的默认值。T1 要从 `server.dll` 读默认值表。

## 4. 测试画面设置

画面配置实际位置：`C:\Users\<user>\OneDrive\Documents\Respawn\Titanfall2\local\`（文档目录被 OneDrive 重定向，不是计划里写的 `Documents\...`）。

**备份**：原文件已复制到 `TF2-Research/local/backup/`：`videoconfig.txt`、`settings.cfg`、`profile.cfg`（后者在 `..\profile\`）。测试版另存为 `videoconfig.test.txt`。

**改动的 `videoconfig.txt` 项**（其余保持原值）：

| 项 | 原值 | 测试值 |
|---|---|---|
| `fullscreen` | 1 | 0（窗口化） |
| `defaultres` × `defaultresheight` | 2560×1440 | 1280×720 |
| `mat_vsync_mode` | 2 | 0（关垂直同步） |
| `dvs_enable` | 1 | 0（关动态分辨率，避免分辨率随帧率浮动） |
| `mat_antialias_mode` | 12 | 0 |
| `shadow_enable` / `csm_enabled` | 1 / 1 | 0 / 0 |
| `r_hbaoenabled` | 1 | 0 |
| `mat_picmip` | 0 | 2（低纹理） |
| `mat_forceaniso` | 16 | 1 |
| 粒子、贴花、布娃娃、gib | 开 | 全关或最低 |

**启动参数**：新建 `Titanfall2\ns_startup_args.txt`（原来没有此文件；文件名已在 `NorthstarLauncher.exe` 字符串里核实）：

```
-windowed -width 1280 -height 720 -novid -multiple +fps_max 144 +mat_vsync_mode 0
```

**补充（2026-10-29）：加了 `-nojoy`。** 2026-10-28 23:56，一次通过 Steam 启动 TF2 后约 15–45 s，机器蓝屏重启：

- 错误码 `0x3B`，出错位置 `vjoy.sys+0x4bc3`。vjoy.sys 是 vJoy 2.1.9 虚拟手柄驱动，2019 年版。
- 2026-09-21 出现过同一错误、同一偏移的蓝屏，那时还没装 TF2。所以这是 vJoy 驱动本身的老问题，TF2 启动枚举输入设备时触发了它。
- 测量只用键盘指令，不需要手柄，所以启动参数加 `-nojoy`（`inputsystem.dll` 支持），不初始化手柄。现在的参数是：`-windowed -width 1280 -height 720 -novid -multiple -nojoy +fps_max 144 +mat_vsync_mode 0`。
- 是否停用或更新 vJoy 驱动由用户决定。这属于系统设置，我们不改。

**帧率**：上限 144。实际帧率还没测，T5 第一次启动时测量并补记在这里。

**恢复方法**：

1. 把 `TF2-Research/local/backup/videoconfig.txt` 复制回 `C:\Users\<user>\OneDrive\Documents\Respawn\Titanfall2\local\`（`settings.cfg`、`profile.cfg` 没改，备份只是保险）。
2. 删掉 `C:\SteamLibrary\steamapps\common\Titanfall2\ns_startup_args.txt`。
3. 也可以直接在游戏里的画面设置调回去，游戏会改写 `videoconfig.txt`。

注意：游戏内改画面设置会覆盖测试配置；测量前确认 `videoconfig.txt` 和 `videoconfig.test.txt` 一致。

## 5. 未解项

- 实际帧率未测（T5）。
- 只解包了 3 个 VPK 的脚本；单人关卡专属脚本在其他 `client_sp_*` 里，需要时再解。
- 模型、动画（如 `.mdl` 里的蹬墙跑动画事件）没解，T3 需要时再看。
