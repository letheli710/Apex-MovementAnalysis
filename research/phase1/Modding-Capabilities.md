# Modding-Capabilities — What Can Be Read, What Can Be Changed

> Evidence tags: **[A]** implemented in open-source code · **[B]** SDK notes about the closed binaries · **[C]** inference · **[D]** unverified.
> Paths are relative to `s21-r5sdk/src/` unless they start with `s21-platform/`.
> Rule followed throughout: **independent mod first, no edits to original game files.** No anti-cheat bypass and no online servers: R5Flowstate runs its own offline/self-hosted dedi.

## 1. Summary matrix

| Need | Squirrel mod (no compile) | Console (ConVar / command) | SDK C++ (needs a build, Phase 2+) |
|---|---|---|---|
| Position / velocity | ✅ `GetOrigin` / `GetVelocity` on both VMs | ✅ `bridge_move_trace` per-command pre/post origin+velocity | ✅ any field |
| Ground state | ✅ `IsOnGround` (shared code), `GetGroundEntity`; server events `TOUCH_GROUND`/`LEAVE_GROUND` | ✅ trace `ge=` | ✅ |
| Slide / wall / mantle / sprint / crouch flags | ✅ `IsSliding`, `IsWallRunning`, `IsWallHanging`, `IsMantling`, `IsSprinting`, `IsCrouched`, `IsTraversing` (seen in base scripts; per-VM availability partly [D]) | ✅ trace `slide= spr= duck=`; `bridge_mantle_boost_trig_log/apply_log`; `bridge_wallclimb_tap` | ✅ |
| Input (buttons, forward/side move) | ⚠️ client only, coarse (`GetInputAxisForward/Right`, `IsInputCommandHeld`) | ✅ trace `b= fwd= sd=` | ✅ |
| View angles, frametime per command | ❌ | ❌ not in `MOVE-TRACE` | ✅ (CUserCmd has both, `game/shared/usercmd.h:55-106`) |
| Read movement parameters | ✅ server `player.GetPlayerSettingFloat/Int/String(key)` | ✅ client `bridge_classvar_get <key>`; DevMenu Movement Lab table | ✅ |
| Change movement parameters (per player, live) | ✅ `Player_SetClassVar` (server) + `SetLocalClassVar` (client), or `player.SetClassVar` (server, also mirrors to the client) | ✅ `set <key> <value>` (cheat-gated), `setall` (host seat, `FCVAR_CHEAT`); Movement Lab | ✅ |
| Temporary air control / gravity / friction | ✅ `player.kv.airSpeed/airAcceleration/gravity`, `SetGroundFrictionScale` | — | ✅ |
| Speed effects | ✅ status effects `speed_boost`, `move_slow`, `disable_wall_run`, `disable_double_jump`, `disable_automantle_hang` | — | — |
| Bhop / lurch / slide-jump / mantle-boost rules | ⚠️ only through existing ConVars | ✅ `sv_autobunnyhopping`, `skip_speed_reduce`, `bridge_lurch_cutoff_speed`, `mantle_boost_*`, `bridge_slide_super_jump*`, `bridge_dodge_rules`, `sv_slope_launch` | ✅ |
| Change the integrator itself (accel/friction/air formulas) | ❌ | ❌ | ⚠️ only by wrapping native calls (pre/post edits of CMoveData, like the SDK twins); the native math stays closed |
| Deterministic, repeatable input | ✅ bots: `CreateFakePlayer`, `BotCmd_SetMove/SetLook/PressButtons/Strafe`, record/replay `CmdRec_Start/Stop` + `BotCmd_PlayRecording` | — | ✅ |

## 2. Reading data

### 2.1 Squirrel (server VM)

- **Movement events** (best signal for state transitions). `AddPlayerMovementEventCallback( player, ePlayerMovementEvents.X, fn )` turns on `player.SetSendMovementCallbacks( true )` (`s21-platform/scripts/vscripts/_codecallbacks_common.gnut:958-970`). The engine then calls `CodeCallback_OnPlayerJump / DoubleJump / Dodge / LeaveGround / TouchGround / Mantle / Begin/EndWallrun / Begin/EndWallhang / Begin/EndSlide` (`_codecallbacks_common.gnut:1006-1139`). The enum is in `sh_consts.gnut:1000-1015`. **[C]** These callbacks are server-only, because `_codecallbacks_common.gnut` is listed only in a `When: "SERVER"` block (`s21-platform/scripts/vscripts/scripts.rson:630-637`).
- **Settings values.** `player.GetPlayerSettingFloat( "airSpeed" )` etc. (`_script_movers.gnut:2180-2181`; `weapons/_weapon_utility.nut:3861`, inside `#if SERVER`). **[D]** It is not known whether this returns the setfile value or the live class-var block after `Player_SetClassVar`. There is an in-tree warning that "GetPlayerSettingsField isn't working for moddable fields? - Bug 129567" (`weapons/_weapon_utility.nut:7646`).
- **Sampling rate.** A server script thread with `WaitFrame()` runs once per **server frame** (20 Hz at `base_tickinterval_mp 0.05`), while several usercmds may be simulated inside that frame (Architecture §2.3). Script sampling on the server is therefore too coarse for per-command analysis; use `bridge_move_trace` for that.

### 2.2 Squirrel (client VM)

- The local predicted player is `GetLocalClientPlayer()`. `GetVelocity()` is used on the client by the input overlay's speedometer (`s21-platform/scripts/vscripts/client/cl_input_overlay.gnut:580-581`). A client `WaitFrame()` thread samples once per render frame, which is close to one sample per usercmd [C].
- Events are not available on the client [C]; ground edges have to be detected by polling `IsOnGround()`. This is what the HSD.MoveDiag mod does.

### 2.3 Console / SDK diagnostics (no compile needed: they ship in the SDK DLLs)

| ConVar / command | Side | What it gives | Source |
|---|---|---|---|
| `bridge_move_trace 1` (or `2` = state edges plus heartbeat every `bridge_move_trace_heartbeat` commands) | both (must match) | `[MOVE-TRACE] cmd= ent= ms= spr= duck= slide= ge= fwd= sd= b= msc= o= v= po= pv=` per FullWalkMove; join client and dedi on `cmd=` | `game/server/move_sim_trace.cpp:42-48,220-232`; `game/client/move_sim_trace.cpp:47-56,189-198` |
| `bridge_move_trace_replays 1` | client | also logs re-predicted commands (`rp=1`) → prediction-correction analysis | `game/client/move_sim_trace.cpp:54-56,163-168` |
| `bridge_classvar_get <key>` | client | live class-var value, type and offset | `game/client/classvar_natives.cpp:251-293` |
| `bridge_classvar_log 1` / `bridge_classvar_log_cl 1` | dedi / client | every class-var write with readback | `game/server/classvar_natives.cpp:70-71`; `game/client/classvar_natives.cpp:57-58` |
| `bridge_tapstrafe_debug 1` | dedi | each suppressed lurch press and why | `game/server/tapstrafe.cpp:54-55,88-90` |
| `bridge_mantle_boost_trig_log 1`, `bridge_mantle_boost_apply_log 1` | both | mantle-boost decision (`travState raw anim delta gate`) and applied exit velocity | `game/server/mantle_boost.cpp:111-114,512-521,704-712` |
| `bridge_slide_super_jump_trace 1` | dedi | accepted and rejected SSJ presses with reasons | `game/server/slide_super_jump.cpp:49-50,80-81,113-114` |
| `bridge_dodge_diag 1` | dedi | every airborne jump/dodge press | `game/server/dodge_rules.cpp:18-19,45-59` |
| `bridge_wall_launch_diag 1/2`, `bridge_slope_launch_diag 1`, `bridge_source_push_diag 1`, `bridge_wallclimb_tap 1` | dedi + client twins | launches, edge-air frames, wall attach/detach | `wall_launch.cpp:50-51`, `slope_launch.cpp:28-29`, `source_push.cpp:34-35`, `wallclimb.cpp:75-76` |

**Gating [A].** Observe-only ConVars (`*_diag/_trace/_log/_tap/_probe/_debug`) are `FCVAR_DEVELOPMENTONLY`; "`-devsdk` strips the flag at run time" (`AGENTS.md:175-180`). File logs are off by default: stdout is the log, and per-run `.log` files are written to `platform/logs/<client|server>/<GUID>/` only with `-devsdk` / `-dev` / `-developer` / `-logfiles` (`AGENTS.md:301-310`). **Launch both processes with `-devsdk` for every experiment.**

### 2.4 Movement Lab (DevMenu, client)

- **What it is.** An ImGui tab "Movement Lab" in the SDK dev menu (`gameui/IDevMenu.cpp:97`), shown with `ui_devmenu_enable 1` (`gameui/IDevMenu.cpp:15`). It **enumerates every class-var field** of the local player, shows its live value, and lets you edit it (`gameui/IClassVarLab.cpp:116-144`).
- **Edits.** They are sent as `set <key> <value>`, or as `setall` for all players (`IClassVarLab.cpp:146-160`). Edit buttons are disabled without cheats (`IClassVarLab.cpp:471-472`).
- **Profiles.** Profiles save **modified fields only** to `platform/cfg/movementlab/<name>.csv` (`IClassVarLab.cpp:18,191-232`). Note: this is not a full dump; see E0.
- **Presets.** Moon/Low/Normal gravity, Slide Lab, Wallrun Lab, Floaty Air, Long Dodge, and "Titanfall 2 Movement" (`IClassVarLab.cpp:474-519`).

## 3. Changing behaviour

### 3.1 Class vars (the main lever) **[A]**

| Path | Effect | Gate | Source |
|---|---|---|---|
| `Player_SetClassVar( entity player, string key, string value )` → bool (server global) | writes the dedi block, `ClassVar_Apply` (replicated props + dirty-mark), and remembers the write as a **sticky** that is replayed after every settings rebuild, e.g. a legend change (max 128) | none beyond the script running | `game/server/classvar_natives.cpp:229-362` |
| `SetLocalClassVar( string key, string value )` → bool (client global) | writes the local client block; sticky replay | none | `game/client/classvar_natives.cpp:762-841` |
| `player.SetClassVar( key, value )` (server entity method) | sends `SVC_SetClassVar` to that client **and** runs `_setClassVarServer` on the dedi → both sides in one call | none | `game/server/vscript_server.cpp:726-784,2121-2127` |
| `set <key> <value>` (client console) | engine command; wrapped and "cheat-gated" | `sv_cheats` | `game/client/classvar_natives.cpp:728-753` |
| `setall <key> <value>` | every connected human; host seat or dedi console only | `FCVAR_CHEAT` | `game/server/classvar_natives.cpp:551-599` |
| `_setClassVarServer` / `_setClassVarClient` | the engine's own pair; the SDK validates types (bool 0/1, int, 1–3 finite floats, \|x\| ≤ 100000; strings refused from the console) | cheat-gated | `game/server/classvar_natives.cpp:367-430,497-546` |

**Rule [A].** Apply the same value on **both** engines, otherwise prediction diverges. The base mods do exactly that: `Player_SetClassVar` under `#if SERVER` and `SetLocalClassVar` under `#if CLIENT` (`s21-platform/scripts/vscripts/sh_surf_movement.gnut:107-119`; `gamemodes/fs_instagib/sh_gamemode_instagib.nut:272-283`). The surf mode also exposes every key as a playlist var `movement_<key>` (`sh_surf_movement.gnut:4,109`), which is a ready-made, file-only way to A/B test parameters.

**Caveat [B].** A key resolves only if it exists in the engine's primary or secondary settings table (`classvar_natives.cpp:167-185`). The S3 dedi and the S21 client have different layouts (Architecture §3.4). A key accepted on one side may be refused on the other, and the call returns `false` and prints `[CLASSVAR] refused` → always check the return value.

### 3.2 ConVars that change movement rules

| ConVar | Default | Effect | Source |
|---|---|---|---|
| `sv_autobunnyhopping` | 0 (replicated) | holding jump re-jumps on the first grounded command | `game/server/autobunnyhop.cpp:13-15` |
| `skip_speed_reduce` (engine) | 100 | horizontal speed lost when jumping within `skip_time` of landing | `s21-platform/scripts/vscripts/sh_surf_movement.gnut:88-89` |
| `bridge_lurch_cutoff_speed` | 1100 (dedi) | dedi refuses the lurch above this horizontal speed; 0 = never | `game/server/tapstrafe.cpp:33-36` |
| `mantle_boost_enabled`, `mantle_boost_input_setting`, `bridge_mantle_boost_*`, `mantle_boost_disables_tap_strafes`, `mantle_boost_min_valid_traversal_frac`, `mantle_boost_require_*_view_angle` | see the source | the mantle boost / superglide FSM | `game/server/mantle_boost.cpp:79-121`; client `mantle_boost.cpp:41-99` |
| `bridge_slide_super_jump`, `_height`, `_cooldown` | 1 / 150 / 2 | slide super-jump twin | `game/server/slide_super_jump.cpp:43-48` |
| `bridge_dodge_rules` | 1 | airborne dodge rules | `game/server/dodge_rules.cpp:15-17` |
| `sv_slope_launch`, `sv_source_push_boost` | 0 / 1 | Source ramps and trigger_push (community) | `slope_launch.cpp:25-26`; `source_push.cpp:30-32` |
| `sv_gravity` | 750 | gravity and the jump impulse | §Movement-Analysis 4.1 |

Most of these have a client twin and say "Must match the client". Set them on both sides (Experiment-Plan §1.3). The bridge ConVars are also the cleanest **A/B switch between "native S3 behaviour" and "S21-aligned behaviour"** (for example `bridge_lurch_cutoff_speed 0`, `bridge_slide_super_jump 0`, `bridge_dodge_rules 0`, `mantle_boost_enabled 0`).

### 3.3 Script-level temporary modifiers [A]

- `player.kv.airSpeed`, `player.kv.airAcceleration` (`_script_movers.gnut:2191-2192`)
- `player.kv.gravity` (`s21-platform/scripts/vscripts/remap/sv_remap_objects.nut:691,712`)
- `SetGroundFrictionScale` (`weapons/mp_ability_wrecking_ball.nut:1512-1584`)
- `SetVelocity` / `SetOrigin` (`remap/sv_remap_objects.nut:446-448`)
- Status effects (`s21-platform/scripts/status_effect_types.txt:10,15,132-134`)
- Class mods: `GivePlayerSettingsMods` / `TakePlayerSettingsMods` with `enable_doublejump`, `enable_wallrun` (`_utility_shared.nut:6920-7004`)

## 4. Mod packaging rules (from the loader source; the web guide could not be fetched)

| Rule | Source |
|---|---|
| Location: `mods/<folder>/mod.vdf`; only one directory level is scanned | `pluginsystem/modsystem.cpp:9-13,249-265` |
| `mod.vdf` is a KeyValues file (root `"ModSystem"`) with required non-empty `author`, `name`, `id`, `description`, `version`; optional `realm` = `both`/`client`/`server` | `pluginsystem/modsystem.cpp:164,971-1038` |
| `id`: 4–32 chars, must start with a letter, `[A-Za-z0-9._]` only | `pluginsystem/modsystem.cpp:895-965` |
| Namespace = id with `.`→`_`, lowercased; it may not contain `__` | `pluginsystem/modsystem.cpp:1000-1009` |
| **File ownership.** Every shipped file must be a fixed manifest file (`mod.vdf`, `readme.md`, `scripts/vscripts/scripts.rson`, …) or have a path component that is `<namespace>__…` or a folder named `<namespace>` that the base does not have. Otherwise **the whole mod is refused** | `pluginsystem/modsystem.cpp:1357-1555,2144-2145` |
| Scripts are listed in the mod's `scripts/vscripts/scripts.rson`; `When` may use only SERVER CLIENT UI SP MP DEV with `&& \|\| !` and parentheses; unsafe paths are dropped | `vscript/vscript.cpp:401-507` |
| Entry points (optional) are global functions `CodeCallback_<Id_with_underscores>_ModInit` (server), `ClientCodeCallback_…` (client), `UICodeCallback_…` (UI), called from `ModSystem_RunCallbacks()` | `game/shared/pluginsystem/modsystem.cpp:71-105`; `vscript/languages/squirrel_re/vsquirrel.h:100-108`; called from `s21-platform/scripts/vscripts/_sh_init.gnut:91,990` |
| `ConVars` block: per-ConVar `flags`, `helpText`, `Values{default,min,max}`; flags are filtered to ARCHIVE/RELEASE/CHEAT/HIDDEN/DEVELOPMENTONLY/CLIENTDLL (no REPLICATED); a name that already exists is skipped | `pluginsystem/modsystem.cpp:1043-1137` |
| Not in `mods/mods.vdf` → enabled by default | `pluginsystem/modsystem.cpp:544-556` |
| `RequiresFeatures` refuses the mod if the build lacks a feature | `pluginsystem/modsystem.cpp:1195-1230`; `public/sdk_features.h` |
| `ScriptWraps` can wrap or replace a base script function (`<ns>__Function`) | `pluginsystem/modsystem.cpp:1733-1790` |
| Script file dumps: `DevTextBufferDumpToFile` keeps only the base name, allows `.txt/.csv/.log/.json`, and prefixes `scriptdump_` | `vscript/script_convar_guard.cpp:300-341` |

## 5. The prototype: `mod/hsd_movediag` (observe only, **not run**)

| File | Purpose |
|---|---|
| `mod.vdf` | id `HSD.MoveDiag` → namespace `hsd_movediag`; ConVars `hsd_md_enable`, `hsd_md_cl_trace`, `hsd_md_sv_trace` |
| `scripts/vscripts/scripts.rson` | one `When: "SERVER \|\| CLIENT"` block, the same form as the base list's surf block (`s21-platform/scripts/vscripts/scripts.rson:2977-2982`) |
| `scripts/vscripts/hsd_movediag__movediag.gnut` | Server: movement-event logger, optional 20 Hz sampler, `hsd_md_dump` settings dump (+ CSV), `hsd_md_mark <label>`. Client: per-frame takeoff/landing summary (airtime, takeoff/peak/landing speed, hop chain) and an optional per-frame trace |
| `readme.md` | install and usage |

Static verification done:

- `tools/hsd_modlint.py` reproduces the loader rules from §4 and cross-checks every global call and method against the base scripts. The result is **0 errors**; a deliberately broken copy gives 6 errors, as expected.
- `tools/hsd_movelog.py selftest` passes.

Not verified:

- Squirrel compilation.
- Whether `IsOnGround` / `IsSliding` resolve in the client VM. They are wrapped in `try/catch` and report `-1` if they do not.
- Whether `GetPlayerSettingFloat` reflects class-var writes.
- Where the `scriptdump_` file lands.
