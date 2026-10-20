# Architecture — R5Flowstate Movement System Architecture and Client/Server Responsibilities

> For evidence tags, see [README.md](README.md#evidence-levels-used-in-every-document). In short: A = implemented in open-source code, B = SDK reverse-engineering notes about the closed-source binaries, C = inference, D = unverified.

## 1. Three repositories and the game binaries

| Component | Contents | Role in movement research |
|---|---|---|
| **s21-r5sdk** (C++) | Builds `client.dll` and `server.dll`, which are injected into the game process as a "Source-engine detour layer" (`s21-r5sdk/AGENTS.md:13`) | Function signatures, struct offsets and hooks for the native movement functions; S3↔S21 behaviour alignment ("twins"); diagnostic ConVars; class-var natives; Movement Lab |
| **s21-platform** (Squirrel/cfg/datatables) | Files read directly from `platform/`; no compile step (`s21-platform/README.md:3-7,28`) | Movement event callbacks, class-var usage examples (surf/instagib), scripts.rson loading rules |
| **launcher** (.NET 8) | Windows installer/launcher shell; "It is not the game" (`launcher/README.md:1-12`) | Not involved in movement |
| Game binaries + rpak (closed source, ~46 GB) | `r5apex.exe` (S21), `r5apex_ds.exe` (S3), `settings/player/mp/*.rpak` | **The real movement algorithms and the default parameter values (setfiles) live here.** None of it is in the repositories |

### 1.1 Dual-engine bridge (the key structural fact)

**[A]** The same SDK source tree produces two artifacts (`s21-r5sdk/README.md:6-11`, `AGENTS.md:17-24`):

| product | Host process | Game version (`README.md:47-48`) | Macro |
|---|---|---|---|
| `client` | **S21** `r5apex.exe` | `R5pc_r5-211_J12_CL6933961_2024_06_14_13_58` | `CLIENT_DLL` |
| `server` | **S3** `r5apex_ds.exe` | `R5pc_r5launch_N1094_CL456479_2019_10_30_05_20_PM` | `DEDICATED` |

**Consequence:** the client predicts movement with **Season 21 (June 2024)** native code, while the server simulates authoritatively with **Season 3 (October 2019)** native code. Wherever the two versions differ, the SDK adds "twins" (patches) on the S3 dedi side to align it with S21 behaviour. Every movement result observed in R5Flowstate is a mix of "S21 client prediction + S3 server authority + SDK patches", which is not the same as any single retail version of Apex.

**[A]** `AGENTS.md:47-52`: "If a field is **networked**, the fix is on the dedi. The S21 client is a retail build". In other words, the SDK treats the S21 client as the reference behaviour and modifies the dedi.

## 2. Movement call chain

### 2.1 Native functions inventory (resolved by the SDK through byte signatures)

| Native function | Side | Signature location (file:line) | Hooked/called by | Level |
|---|---|---|---|---|
| `CPlayerMove::RunCommand(this, player, ucmd, moveHelper)` | S | `game/server/player_command.h:48,63` | `VPlayerMove` (`core/init_server.cpp:799`) | B |
| `CGameMovement::FullWalkMove(ctx)` | S | `game/server/move_sim_trace.cpp:251-253`, `jetdrive.cpp:1056-1058` | **Only attach is in `jetdrive.cpp:1005-1041,1083`**; all other modules hang off it as sub-steps | B |
| `CGameMovement::FullWalkMove(ctx)` | C | `game/client/move_sim_trace.cpp:215-222` | `game/client/move_sim_trace.cpp:88-118` | B |
| `CGameMovement::AirMove(ctx, float frametime, char)` | S | `game/server/tapstrafe.cpp:116-120` | Lurch masking (`tapstrafe.cpp:59-108`) | B |
| `C_GameMovement::AirMove(ctx, float frametime, char)` | C | `game/client/trigger_cannon.h:19-21`, `trigger_cannon.cpp:238` | Gravity-cannon flight lock | B |
| `C_GameMovement::AirMove_TapStrafe(ctx)` | C (S21 only) | `game/client/mantle_boost.cpp:1261-1264` | Suppresses tap strafe after a mantle boost (`mantle_boost.cpp:1073-1101`) | B |
| `GameMovement_AirAccelerate(ctx, wishDir, wishSpeed, accel, dt)` | S | `game/server/wall_launch.cpp:54,305-309` ("called once from the server AirMove"; "the client half inlines its twin") | Wall-launch edge air control | B |
| `CGameMovement::Jump(ctx)` → `char` | S | `game/server/slide_super_jump.cpp:142`, `dodge_rules.cpp:126`, `mantle_boost.cpp:851` (same signature hit by three modules) | SSJ / Dodge / MantleBoost | B |
| `C_GameMovement::Jump(ctx)` | C | `game/client/mantle_boost.cpp:1250-1253` | Called only | B |
| `CGameMovement::Duck(ctx)` | S/C | `game/server/mantle_boost.cpp:854`; `game/client/mantle_boost.cpp:1256-1259` | Called only | B |
| `CGameMovement::TryBeginSlide(ctx, groundNormal, bFromAir)` | S | `game/server/slide_gate_launch.cpp:55,229-235` ("Duck's slide-start call") | Nitro Gate | B |
| `CGameMovement::TraversalMove(ctx, justStarted)` | S/C | `game/server/mantle_boost.cpp:71,848`; `game/client/mantle_boost.cpp:1246-1248` | Mantle boost FSM | B |
| `GameMovement_JumpOutOfWallRun(ctx)` | S | `game/server/wall_launch.cpp:53,301-303` | Wall launch | B |
| `CGameMovement::SetGroundEntity(ctx, trace*)` | S | `game/server/slope_launch.cpp:31,72-74` | Slope launch / Source push | B |
| `CGameMovement::SetDuckedEyeOffset(ctx, frac)` | S | `game/server/player_stance.cpp:28,70-73` | Instant stance change | B |
| `CPlayer::ApplySettingsChange(player, bForce)` | S | `game/server/classvar_natives.cpp:63,628-630` | Replays class vars after a settings rebuild | B |
| `ClassVar_Find / Write / Apply` | S | `game/server/classvar_natives.cpp:42-50,82-91` | `Player_SetClassVar` | B |

The names `CategorizePosition`, `CheckJumpButton`, `CheckVelocity`, `PlayerMove`, `MeleeWalkMove`, `FullTossMove`, `CanStandOn` and others appear in the SDK as `LogFunAdr` names or comments (for example `armored_leap.cpp:1447-1452`, `player_launch.cpp:509-511`). The table above lists only the core functions involved in the mechanics discussed here.

### 2.2 Call order within one usercmd

```
CUserCmd (with frametime, buttons, forward/sidemove, viewangles)          [A usercmd.h:52-106]
  └─ CPlayerMove::RunCommand                                               [B player_command.h:48]
       └─ (SetupMove: computes maxspeed / moveScale; weapon move_speed_modifier term)  [B movescale_weapon_parity.cpp:1-41]
       └─ CGameMovement::PlayerMove  → by move type ─┐                      [C, Source lineage]
            ├─ TraversalMove (mantle / vault)         │                      [B mantle_boost.cpp:3-5]
            └─ FullWalkMove                           ┘                      [B]
                 ├─ Duck → TryBeginSlide(groundNormal, fromAir)            [B slide_gate_launch.cpp:229]
                 ├─ CheckJumpButton → Jump                                  [B/C]
                 │     └─ JumpOutOfWallRun (jump while on a wall)           [B wall_launch.cpp:3-5,109]
                 ├─ (ground) WalkMove/friction/accel — no SDK hook; algorithm unknown [D]
                 ├─ (air)    AirMove → AirAccelerate (S3) / AirMove_TapStrafe (S21) [B]
                 └─ CategorizePosition / SetGroundEntity (ground check, leaves ground above 140 u/s upward) [B slope_launch_math.h:12]
```

**[A]** What the SDK hangs around FullWalkMove on the dedi (`game/server/jetdrive.cpp:1005-1041`). The diagram is in execution order:

```
Before: MoveSimTrace → AutoBunnyHop → SourcePush → SlipDiag → PlayerLaunch → WallClimb → ArmoredLeap → SlideGateLaunch
        native FullWalkMove
After:  ArmoredLeap/PlayerLaunch end → (JetDrive) → SourcePush → SlopeLaunch → SlipDiag → MoveSimTrace → WallClimb → WallLaunch
```

The client equivalent (`game/client/move_sim_trace.cpp:88-118`):

```
Before: AutoBunnyHop → SourcePush → WallLaunch
        native FullWalkMove
After:  SourcePush → SlopeLaunch → WallClimbTap → WallLaunch
```

**[A]** Tooling constraint: one native function has one entry jmp; within a Detours transaction a later hook on the same address "never runs, with no error". The dedi links shared targets at boot, but client attaches and any attach after boot are not linked (`AGENTS.md:120-127`). This is why `VMoveSimTrace` deliberately attaches nothing (`move_sim_trace.cpp:259-265`) and is called from the JetDrive hook instead. A future diagnostic hook should extend the owning hook rather than add a second attach.

### 2.3 Simulation granularity: per-frame usercmd, not a fixed tick

**[A]** `CUserCmd` carries its own `frametime` (`game/shared/usercmd.h:106`), clamped on the server to `[usercmd_frametime_min, usercmd_frametime_max] = [0.002857, 0.100]` seconds (`usercmd.cpp:15-16,44-52`), i.e. **one command per frame, at most about 350 FPS**.
**[A]** Server snapshot/tick: `base_tickinterval_mp 0.05` and `sv_updaterate_mp 20` (`s21-platform/cfg/system/autoexec_server_dev.cfg:18-19`).
**[C]** So movement is integrated once per client frame. Within one 20 Hz server frame the dedi replays a batch of commands (the comment in `player.h:1051-1053` mentions the "1-2-3 batch"). Mechanics that depend on single-frame inputs (superglide, tap strafe, frame-perfect bhop) are therefore **affected by frame rate**. This matches the community's description of superglide in retail Apex, but the conclusion still has to be confirmed by experiment E7 **[D]**.

## 3. Key data structures (offsets are B-level and differ between the two engines)

### 3.1 CGameMovement ctx

| Offset | Meaning | Evidence |
|---|---|---|
| +0x08 | `CPlayer*` / `C_Player*` | `tapstrafe.cpp:19`, `mantle_boost.h:11-12` |
| +0x10 | `CMoveData*` | same |
| +0x18 | settings block pointer (per-class **shared** data; writing to it corrupts the heap) | `wall_launch.cpp:26`, `mantle_boost.cpp:631` |

### 3.2 CMoveData (important differences between the S3 dedi and the S21 client)

| Field | Dedi (S3) | Client (S21) | Evidence |
|---|---|---|---|
| `m_vecAbsViewAngles` | 0x0C | 0x0C | `mantle_boost.cpp:47-48`; client `mantle_boost.cpp:34` |
| `m_nButtons` (held) | 0x24 | 0x24 | `autobunnyhop.cpp:19` |
| `m_nOldButtons` | 0x28 | 0x28 | client `mantle_boost.cpp:36` |
| `m_nButtonsPressed` (pressed this command) | 0x2C | 0x2C | `tapstrafe.cpp:22-23` |
| forwardmove / sidemove | 48 / 52 | 48 / 52 | `move_sim_trace.cpp:21-22` |
| move direction | 0x78 | — | `wall_launch.cpp:30`, `dodge_rules.cpp:30` |
| `m_moveDirGravity` | 180 | — | `mantle_boost.cpp:52` |
| maxspeed | 212 | 212 | `move_sim_trace.cpp:20` |
| origin | **292 (0x124)** | **280** | server/client `move_sim_trace.cpp` |
| velocity | **304 (0x130)** | **292** | same; client `mantle_boost.cpp:32` |

### 3.3 Movement-related CPlayer fields (dedi side, mainly from `game/server/player.h`)

- Ground: `m_hGroundEntity` @0x3C4 (client @0x324; `autobunnyhop.cpp` S:21 / C:56), `m_groundNormal` @0x5DA4 (`slope_launch.cpp:22`)
- Time stamps: `m_flTimeLastTouchedWall / TouchedGround / LastJumped / LastLanded`, `m_bHasJumpedSinceTouchedGround`, `m_bDoMultiJumpPenalty` (`player.h:336-345`); `m_flTimeLastLanded` @0x621C doubles as the Jump anti-bhop "skip window" timestamp (`mantle_boost.cpp:56,63`)
- Crouch/hull: `m_duckState` @0x65F0, Stand/Duck Hull @0x65FC–0x6620 (`player.h:415-423`, `player_stance.cpp:14-21`)
- Wall: `m_wallrunFrictionScale`, `m_groundFrictionScale`, `m_wallHanging`, the traversal family (`player.h:437-470`)
- Slide: `m_sliding`, `m_slideLongJumpAllowed`, `m_lastSlideWasBoost`, `m_lastSlideTime`, `m_lastSlideBoost` (`player.h:483-487`)
- Cached air parameters: airSpeed @0x694C, airAccel @0x6950 (`wall_launch.cpp:39-40`)
- `m_cachedMoveScale` @24884, `m_playerMoveSpeedScale` @24880 (`mantle_boost.cpp:61-62`)
- Class-var block pointer @0x5F08 (`classvar_natives.cpp:37`)

### 3.4 Parameter (class var / setfile) data path

```
rpak setfile (settings/player/mp/*.rpak, closed-source data)        [B; s21-platform scripts reference only the rpak paths]
   → SettingsLayout (field name → offset; "SettingsFieldFinder" global leaves)  [B snapshot_diag.cpp:647-700, wallclimb.cpp:34-65]
   → per-player class-var block (CPlayer+0x5F08), selected by stance (primary table + secondary table/poseSettings)  [B classvar_natives.cpp:140-185]
   → ClassVar_Apply: copies into replicated player props and dirty-marks them  [B classvar_natives.cpp:49-50]
   → CGameMovement reads them (ctx+0x18 settings block / cached fields)  [B]
```

**[B]** The dedi is an S3 binary, but it uses the S21 setfile layout, so the SDK has to write the S21 offsets back into the S3 finder globals (`wallclimb.cpp:1-6,67-69`; `snapshot_diag.cpp:647`). This is another source of S3/S21 discrepancy.

## 4. Client/Server responsibilities

| Responsibility | S21 client (`client.dll`) | S3 dedi (`server.dll`) |
|---|---|---|
| Movement integration | Local prediction (native C_GameMovement + SDK client twins) | **Authoritative** simulation (native CGameMovement + SDK patches) |
| Feature differences | Natively has S21 mechanics such as `AirMove_TapStrafe` | The SDK "twins" fill in missing S21 mechanics (SSJ, dodge rules, lurch cutoff, wall climb remap, …) |
| Parameters | Its own class-var block; scripts write it with `SetLocalClassVar` | Its own class-var block; `Player_SetClassVar` / `player.SetClassVar` / `setall` |
| Error correction | Compares against snapshots; per-field prediction tolerances (`game/client/pred_authority.h:1-60`, `sdk_pred_tol_*`) | Sends snapshots (20 Hz) |
| Scripts | CLIENT VM (UI is a separate VM) | SERVER VM; **`ePlayerMovementEvents` callbacks fire only here** |
| Bots | — | Server simulation only (`CreateFakePlayer`, `BotCmd_*`) |

**[A]** Almost every bridge ConVar ships with "Must match the client(-side default)" (for example `mantle_boost.cpp:79-121`, `dodge_rules.cpp:15-17`, `wall_launch.cpp:47-48`). Changing only one side causes prediction errors (rubber-banding). **Any parameter experiment must apply the same values on both ends.**

**[A]** Three Squirrel VMs: SERVER (dedi), CLIENT, UI (`AGENTS.md:197`). The same `.gnut` file uses `#if SERVER / CLIENT / UI` to compile the half each VM needs (`s21-platform/README.md:12-15`).

## 5. Position in the overall layering (summary diagram)

```
┌──────────── Windows local ────────────┐
│ r5apex.exe (S21)  ←inject─ client.dll │  CLIENT VM / UI VM  (platform/scripts)
│   C_GameMovement (native, closed)     │    SetLocalClassVar, movement HUD …
│   + SDK client twins (mantle/slope…)  │
└───────────────▲───────────────────────┘
       usercmd  │  snapshot (20 Hz)
┌───────────────┴───────────────────────┐
│ r5apex_ds.exe (S3) ←inject─ server.dll│  SERVER VM
│   CGameMovement (native, closed, 2019)│    ePlayerMovementEvents, Player_SetClassVar,
│   + SDK twins (lurch/SSJ/dodge/…)     │    CreateFakePlayer/BotCmd/CmdRec
│   + SDK diagnostics (bridge_move_trace)│
└───────────────────────────────────────┘
   setfile values: rpak (game data, not in the repositories)
```
