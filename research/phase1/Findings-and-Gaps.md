# Findings-and-Gaps — Confirmed Findings, Open Questions, Phase 2 Recommendations

> Evidence tags: **[A]** implemented in open-source code · **[B]** SDK reverse-engineering notes about the closed binaries · **[C]** inference · **[D]** unverified.

## 1. Confirmed findings

| # | Finding | Level | Evidence |
|---|---|---|---|
| F1 | R5Flowstate is a **hybrid**: the S21 (2024-06) client predicts and the S3 (2019-10) dedi is authoritative. SDK "twins" patch the dedi toward S21. Observed movement is not any single retail version | A | `s21-r5sdk/README.md:6-11,47-48`; `AGENTS.md:17-24,47-52` |
| F2 | **No movement math is open source.** CGameMovement (FullWalkMove, AirMove, AirAccelerate, Jump, Duck, TryBeginSlide, TraversalMove, JumpOutOfWallRun, SetGroundEntity, …) is located only by byte signature | A (that it is absent) / B (the names) | Architecture §2.1 |
| F3 | **No default parameter values are open source.** Setfiles are rpak assets; the scripts only name them | A | `s21-platform` contains no `.set`; rpak paths are referenced in scripts |
| F4 | Movement simulation is **one usercmd per client frame** with its own `frametime` (clamped 1/350 … 0.1 s); the server runs at 20 Hz and replays command batches | A / B | `game/shared/usercmd.h:106`; `usercmd.cpp:15-16,44-52`; `game/server/player.h:1051-1053`; `s21-platform/cfg/system/autoexec_server_dev.cfg:18-19` |
| F5 | Jump impulse is `√(2·sv_gravity·jumpHeight)` using **unscaled** `sv_gravity` (750). The S21 authored `jumpHeight` is 56 (≈ 289.8 u/s) | B | `game/server/mantle_boost.cpp:108-110,649`; `s21-platform/scripts/vscripts/sh_surf_movement.gnut:54-56` |
| F6 | Jump reacts only to a **press edge**. Jumping on the first grounded command **skips ground friction**. Jumping within `skip_time` of landing costs `skip_speed_reduce` (stock 100) horizontal speed. A quick re-jump is lowered by `antiMultiJumpHeightFrac`. Hard landings slow the player for `landSlowdownDuration` | B | `game/client/autobunnyhop.cpp:3-6`; `game/server/mantle_boost.cpp:56,631-636`; `sh_surf_movement.gnut:51-59,88-89` |
| F7 | Air control goes through `AirAccelerate(wishDir, wishSpeed, accel, dt)`, fed from class `airSpeed`/`airAcceleration`, with a separate `airStrafeEnabled` flag | B | `game/server/wall_launch.cpp:39-44,54,179-187,305-309` |
| F8 | The tap-strafe lurch is triggered by **press edges of the WASD bits (0x618) inside AirMove**. S21 has `AirMove_TapStrafe` and a `jump_grace_cutoff_speed`; the dedi twin defaults its cutoff to 1100 | B / A | `game/server/tapstrafe.cpp:20-41,59-108`; `game/client/mantle_boost.cpp:1261-1264` |
| F9 | Slides start in `Duck → TryBeginSlide(groundNormal, fromAir)`. A slide jump within 0.4 s refunds the slide-boost gain. S21's slide super-jump: 0.3 s window, height 150, cooldown 2.0 | B | `game/server/slide_gate_launch.cpp:229-235`; `game/server/player.h:1085-1090`; `game/server/slide_super_jump.cpp:5-11` |
| F10 | "Wall bounce" = native `JumpOutOfWallRun`, with outward/up/input-direction speed keys. Wallrun and double jump are off in retail playlists | B / A | `game/server/wall_launch.cpp:53,109`; `s21-platform/playlists_r5_patch.txt:5261-5262` |
| F11 | The SDK implements **"superglide" as an explicit mantle-boost FSM** (sweet spot 1.5°, frac > 0.5, exit × 1.3, boost jump h = 90) on both engines. After a boost, tap strafe is suppressed until landing or the next traversal | A | `game/server/mantle_boost.cpp:79-121,473-660,805-835`; `game/client/mantle_boost.cpp:1073-1101` |
| F12 | Grounded velocity stays flat on slopes; the player leaves the ground above 140 u/s upward; standable floor normal z ≥ 0.7 | B | `game/shared/slope_launch_math.h:3-16` |
| F13 | **Parameters can be changed live and per player from script** (`Player_SetClassVar` + `SetLocalClassVar`, or `player.SetClassVar`), with sticky replay after settings rebuilds. Console: `set`/`setall` (cheat-gated); DevMenu **Movement Lab** to view and edit every field | A | `game/server/classvar_natives.cpp:229-362,551-599`; `game/client/classvar_natives.cpp:728-841`; `gameui/IClassVarLab.cpp` |
| F14 | A **per-command movement trace already exists** (`bridge_move_trace`) on both engines, joinable on `cmd=`, with replay tagging on the client. Phase 1 needs no C++ | A | `game/server/move_sim_trace.cpp`; `game/client/move_sim_trace.cpp` |
| F15 | **Deterministic input is possible**: bots with programmed input (`BotCmd_SetMove/SetLook/PressButtons/Strafe`) and record/replay of human input (`CmdRec_*`, `BotCmd_PlayRecording`). Bots measure dedi-only behaviour | A | `game/server/bot_cmd.cpp:1110-1146`; `game/server/cmd_recorder.cpp:24-29,497-502` |
| F16 | Mods are independent folders under `mods/` with strict namespace and file-ownership rules; scripts are added through the mod's own `scripts.rson`; entry points are `CodeCallback_<Id>_ModInit` | A | `pluginsystem/modsystem.cpp`; Modding-Capabilities §4 |

## 2. Contradictions and anomalies in the sources

| # | Issue | Details | How to resolve |
|---|---|---|---|
| X1 | Does the **S3 dedi** have a native lurch? | `tapstrafe.cpp:1-4,31-32` says it has a "native inline lurch" in AirMove with no speed gate. `core/init_server.cpp:664` says "zero trace of the mechanic" and describes a FullWalkMove detour that the current code no longer uses → the registration comment looks stale | E3 with bots and `bridge_lurch_cutoff_speed 0`; or disassemble AirMove |
| X2 | Is the mantle boost native in **retail S21**? | The ConVars are described as "ship-named … S21 default", but the client side is a "client-predicted twin" implemented by the SDK on top of the S21 `TraversalMove` | Check whether the retail S21 binary registers `mantle_boost_*` itself (string search in the user's own install), or run E7 with `mantle_boost_enabled 0` |
| X3 | The registration comment calls SSJ "airborne second press … on the dedi Jump detour", while `slide_super_jump.cpp:9-10` says "The dedi Jump returns 0 for any airborne press" | Consistent: the twin exists *because* the S3 Jump refuses airborne presses for this case. Note it as an S3-vs-S21 Jump difference | — |

## 3. Gaps (not resolvable from the source)

| # | Gap | Impact | Proposed resolution |
|---|---|---|---|
| G1 | Native formulas for ground accel/friction, air accel, lurch, slide accel/decay, wall jump composition | Cannot copy algorithms; can only fit models | E1–E6 model fitting; optional offline disassembly (G-opt below) |
| G2 | Retail values of almost every movement key | No baseline numbers for Unity | E0 runtime dump |
| G3 | `r5flowstate.org` docs (mod guide, tools) unreachable from the VM (proxy 403) | The Modding rules here come from the loader source; the docs may add conventions (e.g. Thunderstore packaging) | Read them from a normal machine and diff against Modding-Capabilities §4 |
| G4 | `GetPlayerSettingFloat` vs. live class vars | E0 server dump may show setfile values, not overrides | E0: set a key with `Player_SetClassVar`, then dump |
| G5 | Movement events may be server-only; client API availability in the CLIENT VM is partly unknown | Client-side event logging relies on polling | Run the mod; watch for `-1` in `ground=`/`slide=` |
| G6 | `MOVE-TRACE` lacks per-command `frametime` and view yaw | Air-strafe and lurch angles are only estimated (`dt_est`) | Phase 2: SDK diag patch (below) |
| G7 | Classic superglide (frame-order exploit) is not in the source | Unknown whether it exists in this hybrid at all | E7 |
| G8 | Hybrid engine: every measurement mixes S21 prediction and S3 authority | Numbers may differ from retail Apex | E8 parity statistics; prefer client-side traces for "S21 feel"; tag each result |
| G9 | `player.h` is a reconstructed layout; only offsets used by working code are effectively verified | A field read from an unused offset may be wrong | Read only fields that existing SDK features already use (the mod does this through script APIs) |
| G10 | The mod and tools have not been executed in the game | Possible Squirrel compile or runtime issues | First step of Phase 2: run it once and fix |
| G11 | `SLIDE_SUPER_JUMP` has no script dispatcher | No event for SSJ | Use `bridge_slide_super_jump_trace` |

## 4. Phase 2 recommendations

1. **Run E0–E2 within one session**, then E4/E5 and E3 (see §5). Commit raw logs and CSVs next to these documents (`research/phase2/data/`).
2. **Minimal SDK diagnostic patch** (local build only, Windows + VS per `AGENTS.md` "Build"). Two changes, both inside hooks that already exist, behind the existing `FCVAR_DEVELOPMENTONLY` ConVar:
   - Add `ft=<frametime>` and `yaw=<viewangles.y>` to `[MOVE-TRACE]`, reading `CUserCmd::frametime` (`usercmd.h:106`) through the current command pointer the trace already reads (`move_sim_trace.cpp:97-108`).
   - Log the `AirAccelerate(wishDir, wishSpeed, accel, dt)` arguments from the **existing** `Hook_GameMovement_AirAccelerate` (`wall_launch.cpp:204-208`); `AGENTS.md:120-127` warns against a second attach. This exposes the air-control inputs exactly, with no disassembly.
3. **Optional, the user's decision: offline static analysis** of the user's own legitimately installed binaries (Ghidra/IDA). Only for the signature-located functions above, with no runtime injection into the retail client and no anti-cheat interaction. Weigh this against the game's terms of service before doing it.
4. **Unity prototype.**
   - Build a parameterised controller whose decomposition mirrors Movement-Analysis §10: per-stance ground params, a Source-style AirAccelerate, a press-edge jump `√(2gh)`, landing rules, a slide with boost/refund/cooldown, an explicit lurch window, and an explicit mantle-boost window.
   - Add a replay harness that feeds R5 usercmd traces (buttons/fwd/side/ft/yaw) into it and compares the output velocity against the R5 `pv` per command.
   - Avoid frame-order-dependent mechanics. Implement superglide and tap strafe as **designed windows** in fixed-timestep logic.
5. **Integration hooks for wallrun / grapple / teleport** (future High Speed Doom features). Keep velocity as the single source of truth, and reuse the R5 pattern of "pre/post the integrator" modifiers (as the SDK twins do) so new abilities stay composable.

## 5. The three most valuable next experiments

| Rank | Experiment | Why |
|---|---|---|
| **1** | **E0 parameter census + E1/E2 ground and air model fitting** | Every other result needs the real parameter values and the base integrator structure. They are the biggest gaps (G1/G2) and the cheapest to close: no special geometry, plus bots with exact input. It also confirms or refutes the key inference that air accel is `airAcceleration·dt` capped at `airSpeed` (Movement-Analysis §3). The output translates directly into the first Unity controller |
| **2** | **E4 + E5 momentum chain (bhop landing window, slide boost/decay, slide-jump 0.4 s refund)** | Apex "speed feel" comes from how momentum survives landings and slides, not from top speed. The source exposes the rule *names* (skip window, friction skip on first-command jump, multi-jump penalty, landing slowdown, slide refund) but not their *values*. These rules determine whether High Speed Doom rewards rhythm, so they must be measured before design |
| **3** | **E3 tap strafe / lurch, with E8 parity** | The most Apex-specific mechanic, and the one with a direct source contradiction (X1) and a known S21/S3 difference (speed cutoff). Measuring the grace window and redirection strength tells us whether to design a lurch on purpose (Reference, not replicate) and how to keep it frame-rate independent |

E7 (superglide) comes next. It matters for design, but it is narrower and depends on frame rate; F11 already gives a usable parametric description of the window.
