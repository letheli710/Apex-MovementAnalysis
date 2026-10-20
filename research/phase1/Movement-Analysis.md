# Movement-Analysis — Mechanics, Algorithms, Parameters and Source Paths

> Evidence tags: **[A]** implemented in open-source code · **[B]** SDK reverse-engineering notes about the closed binaries · **[C]** inference · **[D]** unverified. See [README.md](README.md#evidence-levels-used-in-every-document).
> Paths are relative to `s21-r5sdk/src/` unless they start with `s21-platform/`.

## 0. Two facts that frame everything below

1. **No movement integrator is in the open source.** Ground acceleration, friction, air acceleration, the lurch and jump code are native `CGameMovement` functions inside the closed `r5apex.exe` (S21) and `r5apex_ds.exe` (S3) binaries. The SDK only *finds* them by byte signature, *wraps* them, and in a few places *reimplements* behaviour that one engine lacks (see [Architecture.md §2.1](Architecture.md#21-native-functions-inventory-resolved-by-the-sdk-through-byte-signatures)). So for every mechanic the question "what is the algorithm" has three possible answers: visible only as a signature and offset (B), implemented by the SDK as a twin (A, but it is *R5Flowstate's* code imitating S21), or not visible at all (D).
2. **Default parameter values are not in the repositories.** Player settings (setfiles) are compiled rpak assets, for example `$"settings/player/mp/pilot_survival_stim.rpak"`; s21-platform contains no `.set`/`playersettings` source. The only numbers available are SDK comments that quote S21 authored defaults (B), Titanfall 2 presets (not Apex), and custom gamemode values (surf/instagib). The real Apex values must be **dumped at runtime** (Experiment E0).

## 1. Classification: real Apex logic vs. compatibility layer vs. community additions

| Mechanic / feature | S3 native (dedi) | S21 native (client) | SDK twin (S21 behaviour ported to the dedi) | Community addition (not Apex) | Key evidence |
|---|---|---|---|---|---|
| Ground walk/sprint accel, friction | yes | yes | — | — | no SDK hook; only parameters (§2) |
| Air accel / air strafe | yes (`AirAccelerate`) | yes (inlined) | — | wall-launch edge-air rewrite (Sparrow) | `game/server/wall_launch.cpp:305-309` |
| Tap strafe (lurch) | **disputed** (§4.4) | yes (`AirMove_TapStrafe`) | speed cutoff `bridge_lurch_cutoff_speed` | — | `game/server/tapstrafe.cpp:31-41`, `core/init_server.cpp:664` |
| Jump, double jump | yes | yes | movement-ability input gate, dodge rules | — | `game/shared/jump_input_gate.h`, `game/shared/dodge_rules.h:1-10` |
| Auto bunny hop | no | no | — | `sv_autobunnyhopping` (CS:GO style) | `game/server/autobunnyhop.cpp:1-15` |
| Slide | yes (`TryBeginSlide` from `Duck`) | yes | slide super-jump (`boosted_slide_jump`) | — | `game/server/slide_gate_launch.cpp:229-235`, `game/server/slide_super_jump.cpp:1-11` |
| Climb / wall jump ("wall bounce") | yes (`JumpOutOfWallRun`) | yes | S21 settings-offset remap | Sparrow wall launch | `game/server/wallclimb.cpp:1-6`, `game/server/wall_launch.cpp:1-5` |
| Mantle (TraversalMove) | yes | yes | — | — | `game/server/mantle_boost.cpp:3-5` |
| Superglide / mantle boost | emergent only (§7) | **unclear** (§7) | FSM implemented by the SDK on *both* sides | — | `game/server/mantle_boost.cpp:79-121`, `game/client/mantle_boost.cpp:1-6` |
| Slope launch, Source trigger_push, surf | no | no | — | yes (`sv_slope_launch`, `sv_source_push_boost`, surf maps) | `game/shared/slope_launch_math.h:1-7`, `game/server/source_push.cpp:1-8` |
| JetDrive (Vantage), skydive, glide, jetpack… | no ("zero trace") | yes | yes (from-scratch port) | — | `core/init_server.cpp:619` |

## 2. Ground movement, acceleration, friction

**What can be seen**

- **[B]** The ground speed/accel model is driven by per-stance class vars `speed`, `sprintspeed`, `acceleration`, `deceleration`, `lowSpeed`, `lowAcceleration`, `sprintAcceleration`, `sprintDeceleration`. "The first six are stand-pose fields; -1 is the engine's own fallback to acceleration" (`gameui/IClassVarLab.cpp:27-33`). There is a primary table plus a per-stance secondary table (`poseSettings` row 0 stand, 1 crouch; `game/client/classvar_natives.h:32`, `game/server/classvar_natives.cpp:140-185`). The Movement Lab refuses the TF2 preset unless standing because "speed and acceleration write the current stance" (`IClassVarLab.cpp:507-517`).
- **[C]** Because there are separate `acceleration` and `deceleration` keys (plus `speedScaleSide`, `speedScaleBack`), the ground model is very likely *not* plain Source `Accelerate + Friction(sv_friction)`. No `sv_friction`, `sv_accelerate` or `sv_stopspeed` appears anywhere in either repository. The surf agent search found no hits either.
- **[A/B]** Friction scale hooks exist: `CPlayer::m_groundFrictionScale` and `m_wallrunFrictionScale` (`game/server/player.h:438-439`), and the script API `SetGroundFrictionScale` (`s21-platform/scripts/vscripts/weapons/mp_ability_wrecking_ball.nut:1512`).
- **[B]** `maxspeed` (`CMoveData+212`) and `m_cachedMoveScale` (`CPlayer+24884`) are logged per command by `bridge_move_trace` (`game/server/move_sim_trace.cpp:20,31`). Weapon move-speed modifiers enter in `SetupMove` as `modifier(w)*modifier(w)` (`game/server/movescale_weapon_parity.cpp:1-5`).
- **[B]** Slopes: "Apex keeps grounded velocity flat and only slides the position along the slope" (`game/shared/slope_launch_math.h:3-6`). Standable floor normal z ≥ 0.7 (`slope_launch_math.h:14-16`).
- **[B]** Sprint: airborne sprint grace 0.25 s (`CanSprintNow`; `game/server/mantle_boost_vm_probe.cpp:26`). Sprint start/end timing keys: `sprintStartDelay`, `sprintStartDuration`, `sprintStartFastDuration`, `sprintEndDuration` (`IClassVarLab.cpp:50-51`).
- **[B]** Hard landing slows the player for `landSlowdownDuration`: "Apex slows a player down after a hard landing; Source never does" (`s21-platform/scripts/vscripts/sh_surf_movement.gnut:57-59`).

**Not visible [D]:** the actual accel curve (linear vs. Source-style `accel*wishspeed*dt`), friction formula, stop speed, sprint ramp and side/back scaling math. → Experiment E1.

## 3. Air acceleration and air strafing

- **[B]** Signature `GameMovement_AirAccelerate(ctx, float* wishDir, float wishSpeed, float accel, float dt)`; "called once from the server AirMove", and "the client half inlines its twin" (`game/server/wall_launch.cpp:54,305-309`). This is the Quake/Source shape `AirAccelerate(wishdir, wishspeed, accel)` with an explicit `dt`.
- **[B]** The engine's inputs are scaled from the class `airSpeed` / `airAcceleration` (`game/shared/wall_launch_math.h:141-169`, cached at `CPlayer+0x694C/0x6950`, `game/server/wall_launch.cpp:39-40`). A separate settings boolean `airStrafeEnabled` exists: "Class air strafing replaces the air speed term" (`wall_launch.cpp:44,179-187`).
- Other air keys: `airFriction`, `airDrag` (`s21-platform/scripts/vscripts/sh_surf_movement.gnut:9`).
- **[C] Strong hint about the formula.** The surf mode makes Apex behave like CS:GO surf with `airSpeed = 30` and `airAcceleration = 37500` (`sh_surf_movement.gnut:32-35`). In Source, the air wish speed cap is 30 and CS:GO surf servers commonly run `sv_airaccelerate 150`, with accelspeed = `sv_airaccelerate × wishspeed(250) × dt`. 150 × 250 = 37500. That calibration only makes sense if Apex's `AirAccelerate` uses **accelspeed = airAcceleration × dt** (no extra × wishspeed) with the wish speed clipped to **airSpeed**. This is the surf author's calibration, not a disassembly → must be checked in E2.
- **[A]** Scripts change air control at runtime with `player.kv.airSpeed` / `player.kv.airAcceleration` (wind tunnel sets 80/800, then restores from `GetPlayerSettingFloat`: `s21-platform/scripts/vscripts/_script_movers.gnut:2180-2192`).

## 4. Jump, bunny hop, momentum preservation, tap strafe

### 4.1 Jump

- **[B] Jump velocity formula.** `v_up = sqrt(2 · sv_gravity · jumpHeight)`, read from `sv_gravity` directly ("Real Jump reads sv_gravity directly (JumpHeightToVelocity)", `game/server/mantle_boost.cpp:108-110`). The surf script confirms that the jump uses unscaled `sv_gravity`: "CS:GO jump impulse 301.99 u/s; Apex takes it from sv_gravity 750, not the scaled gravity", so it sets `jumpHeight 60.8` (`sh_surf_movement.gnut:54-56`). Check: √(2·750·60.8) = 301.99. ✔
- **[B]** Defaults quoted by the SDK: `sv_gravity` 750 (fallback in `slide_super_jump.cpp:57`, `wall_launch.cpp:63`), `player_jumpHeight` 56 "authored default" (`mantle_boost.cpp:649`) → √(2·750·56) ≈ **289.8 u/s**.
- **[B]** The native Jump reacts only to a **press edge** (`m_nButtonsPressed`, `CMoveData+0x2C`): "The jump check fires only on the command a jump is pressed" (`game/client/autobunnyhop.cpp:3-6`, `game/server/autobunnyhop.cpp:19-20`).
- **[B]** Airborne jump/dodge decision site: ground → `IN_JUMP`; air → double jump or dodge via `IN_DODGE`, with `super_jump_debounce_time` 0.1 s after the previous jump (`game/shared/jump_input_gate.h:1-11,39-67`). The dedi's Jump "refuses any dodge while ducked" (`game/server/dodge_rules.cpp:3-4`); the SDK NOPs that gate for pilots (`dodge_rules.cpp:61-68,160-178`).
- Double jump keys: `doubleJump`, `superjumpMinHeight`, `superjumpMaxHeight`, `superjumpHorzSpeed`, `superjumpLimit`; state `m_Local.m_superJumpsUsed` (`wall_launch.cpp:36`).

### 4.2 Bunny hop and momentum loss on landing

- **[B]** Anti-bhop "skip window": the native Jump compares against a skip-window timestamp at `CPlayer+25116`, which is the same field as `m_flTimeLastLanded` (`mantle_boost.cpp:56,63`). The SDK pushes it into the past to force a jump through "Jump's anti-bhop gate" (`mantle_boost.cpp:631-636`).
- **[B]** ConVars `skip_time` and `skip_speed_reduce`: "A jump within skip_time of landing normally costs this much horizontal speed (stock 100)" (`sh_surf_movement.gnut:88-89`).
- **[B]** `antiMultiJumpHeightFrac`: "Apex lowers a jump made right after landing from one; Source does not" (`sh_surf_movement.gnut:51-53`), with the `m_bDoMultiJumpPenalty` flag (`player.h:344`).
- **[B]** Auto bhop (community, off by default): on a grounded command with jump held, OR `IN_JUMP` into `m_nButtonsPressed` before `FullWalkMove`, "so the first command on the ground jumps and no ground friction is applied" (`game/client/autobunnyhop.cpp:3-6,58-70`; server `autobunnyhop.cpp:23-35`). This implies that **friction is skipped on the command where the jump happens** (B).
- **[C]** Bhop speed retention in Apex therefore depends on (a) whether you jump on the first grounded command (friction skip), (b) whether you jump inside `skip_time` (−`skip_speed_reduce` horizontal speed), (c) `landSlowdownDuration` after hard landings, and (d) air strafing. The exact window values are unknown → E4.

### 4.3 Momentum through slide jumps

See §5. **[B]** A slide jump within 0.4 s of a slide boost *subtracts* the boost gain (`m_lastSlideBoost`, "the slide speed GAIN in units, which Jump subtracts back out on a slide jump inside 0.4s"; `game/server/player.h:1085-1090`). This is the anti "slide-boost-jump" exploit rule.

### 4.4 Tap strafe (lurch)

- **[B] Input trigger.** The lurch is gated on **press edges** of the direction buttons in `m_nButtonsPressed`: mask `IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT = 0x618`. Clearing those bits inside `AirMove` "suppresses only the lurch" (`game/server/tapstrafe.cpp:20-26,82-100`; button bits in `public/game/shared/in_buttons.h:20-27`).
- **[B] S21 client.** It has a dedicated `C_GameMovement::AirMove_TapStrafe(ctx)` (`game/client/mantle_boost.cpp:1261-1264`), which "skips the lurch above `jump_grace_cutoff_speed`" (`tapstrafe.cpp:31-32`).
- **[A] SDK dedi twin.** `bridge_lurch_cutoff_speed` default **1100** ("matching the S21 client's jump_grace_cutoff_speed"; `tapstrafe.cpp:33-36`). It is also suppressed during gravity-cannon flight and after a mantle boost (state 4) (`tapstrafe.cpp:66-100`).
- **Contradiction (record it, do not resolve it by guessing).**
  - `tapstrafe.cpp:1-4,31-32` says the dedi has a **native inline lurch** in `AirMove` "with no speed gate".
  - The registration comment `core/init_server.cpp:664` says the dedi has "zero trace of the mechanic" and the twin is "ONE detour on CGameMovement::FullWalkMove".
  - The current code hooks `AirMove`, not `FullWalkMove`, so the registration comment looks stale. The truth still needs E3 (or a disassembly of `AirMove` on the dedi).
- **[C]** The ConVar name "jump grace" and the registration comment ("'jump grace'/tap-strafe (lurch) assist") suggest that in S21 the lurch is framed as a short post-jump grace window in which a fresh direction press re-aims velocity. The window length and how much is redirected are **not visible [D]**.

## 5. Sliding

- **[B] Entry.** Slides start inside `Duck`: "Duck's slide-start call: add rdx, m_vPrevGroundNormal; xor r8d, r8d; mov rcx, rdi; call TryBeginSlide" → `TryBeginSlide(ctx, groundNormal, bFromAir)` (`game/server/slide_gate_launch.cpp:55,229-235`). The ground normal is passed in, which suggests slope-dependent slide acceleration [C].
- **[B] State** (`player.h:483-487`): `m_sliding`, `m_slideLongJumpAllowed`, `m_lastSlideWasBoost`, `m_lastSlideTime`, `m_lastSlideBoost`. The `MOVE-TRACE` line logs `slide=` (`CPlayer+26565`; client `+11637`).
- **Keys:**
  - `slideAccel`, `slideDecel`, `slideVelocityDecay`
  - `slideRequiredStartSpeed`, `slideSpeedBoost`, `slideSpeedBoostCap`
  - `slideJumpHeight`, `slideMaxJumpSpeed`
  - `slideStopSpeed`, `slideMaxStopSpeed`, `slideWantToStopDecel`
  - `player_slideBoostCooldown`
  - Sources: `sh_surf_movement.gnut:14-16`, `s21-platform/cfg/speed.cfg:6-9`.
- **[B] Slide boost.** The boost is a speed *gain* stored in `m_lastSlideBoost` and refunded by a slide jump within 0.4 s (§4.3). A boost cooldown key exists (`player_slideBoostCooldown`, `speed.cfg:9`).
- **[B] Slide super-jump (S21, `boosted_slide_jump` class mod).** After a jump taken from a slide, a jump or dodge press within **0.3 s** of leaving the ground adds `up · sqrt(2 · g · slideSuperJumpHeight)` once per `slideSuperJumpCooldown`. The mod authors height **150**; the base setfile authors cooldown **2.0** (`game/server/slide_super_jump.cpp:5-11,29-30,43-48,92-123`). The dedi twin is SDK code (A); the S21 values are B.
- **[A] Scripts.** The `BEGIN_SLIDE` / `END_SLIDE` events exist on the server (`s21-platform/scripts/vscripts/sh_consts.gnut:1012-1013`). `SLIDE_SUPER_JUMP` is in the enum, but no dispatcher handles it.

## 6. Wall jump ("wall bounce"), climb, wallrun

- **[B] Native wall jump.** `GameMovement_JumpOutOfWallRun(ctx)` is the jump taken while on a wall/climb (`game/server/wall_launch.cpp:53,109-133,300-303`). The input direction while hanging: "a short stick is topped up toward the facing direction" (`game/shared/wall_launch_math.h:44-58`).
- **[C]** The community term "wall bounce" in Apex (jump off a wall during a climb) maps to this function. The wallrun code path is reused for climbing (`climbEnabled`, `climbHeight`, `climbSpeedStart`, `climbFinalJumpUpHeight`, `wallrunAllowedWallDistance`… `game/server/wallclimb.cpp:44-65`).
- **Keys:** `wallrunJumpOutwardSpeed`, `wallrunJumpUpSpeed`, `wallrunJumpInputDirSpeed` (`sh_surf_movement.gnut:13`). The TF2 preset values 205 / 230 / 75 (`IClassVarLab.cpp:43-44`) are **not** Apex values.
- **[B] Wall state.** The wall normal is stored at `CPlayer+0x662C` and equals +Z when not on a wall (`wall_launch.cpp:37,219`). Also `m_wallHanging` and the `m_wallDangle*` fields (`player.h:443-470`).
- **[A] Retail Apex wallrun is off.** Wallrun and the double-jump kit are granted only by playlist vars `survival_wallrun_enabled` / `survival_jumpkit_enabled`, default 0 (`s21-platform/playlists_r5_patch.txt:5261-5262`).
- **Community addition.** The Sparrow "climb high jump" (wall launch) is not in either engine ("Neither engine has the climb high jump", `wall_launch.cpp:3-5`). Its constants (max height 300, outward 150–450 u/s, edge air 320/800) come from "Sparrow setfile values" (`wall_launch_math.h:13-25`). It is opt-in per player through `player.SetWallLaunchEnabled( bool )`.

## 7. Mantle and superglide

- **[B] Mantle.** It runs in `TraversalMove(ctx, justStarted)`. "Hook TraversalMove, not TraversalFinished -- its caller overwrites origin and exit velocity after return" (`game/server/mantle_boost.cpp:3-5`). Traversal fields: `m_traversalType` (0 = mantle, non-zero = window vault), `m_traversalState` (11 idle/hang, 12 jump-off), `m_traversalProgress`, `m_traversalForwardDir`, `m_traversalRefPos` (`mantle_boost.cpp:59-60`, `player.h:448-463`).
- **[A] Mantle boost FSM (SDK code on both sides).**
  - States: 0 idle, 1 invalid (hang), 3 failed, 4 boost (`mantle_boost.cpp:181`).
  - Decision on the activation press (`mantle_boost.cpp:473-506`):
    - `|animViewPitch − eyePitch| < bridge_mantle_boost_sweet_spot_angle` (1.5°, "opens about the last 0.10-0.13 s of a mantle")
    - the delta must be settling toward zero (`mantle_boost_require_decreasing_view_angle 1`)
    - traversal fraction > `mantle_boost_min_valid_traversal_frac` (0.5, "for the superglide to be valid")
  - Finish (`mantle_boost.cpp:550-660`):
    - Exit velocity = move dir (reflected off the ledge if it points backwards) × `GetPoseSpeed_Sprint` (falls back to 260).
    - In state 4 the speed is also multiplied by `bridge_mantle_boost_sprint_mult` 1.3.
    - Then one forced native `Jump` with `vz += sqrt(2·g·h)`, where h = 90 for state 4 and 56 for state 3.
    - State 4 also grants slide-chain flags.
  - Input: Jump by default (`mantle_boost_input_setting`: 0 off, 1 jump, 2 crouch, 3 movement ability; `mantle_boost.cpp:82-89`).
  - State 4 suppresses tap strafe until the next traversal or landing (`mantle_boost.cpp:116-121,805-835`).
- **What it means.**
  - The SDK models "superglide" as an explicit, timing-window FSM keyed to the mantle animation camera. The ConVar comments call the names "ship-named … S21 default", which suggests the parameters mirror a retail S21 feature (B).
  - The client file still says "client-predicted twin" and hooks the S21 `TraversalMove` itself (`game/client/mantle_boost.cpp:1-6,1106`). So whether the **retail S21 client natively** contains this FSM is unclear [D].
- **Classic superglide** (jump, then crouch within about one frame at the end of a mantle). It is not implemented anywhere in the open source. If it exists in the native S3/S21 code, it is *emergent* from `TraversalMove` → `Jump` → `Duck`/`TryBeginSlide` ordering within one usercmd [C]. Because usercmds are per frame (Architecture §2.3), it would be frame-rate dependent [C] → E7.

## 8. Movement state, collision, velocity

- **Ground state.**
  - **[B]** `m_hGroundEntity == -1` means airborne (`CPlayer+0x3C4` dedi / `+0x324` client). `SetGroundEntity(ctx, trace)` rewrites `m_groundNormal` (`slope_launch.cpp:22`).
  - **[B]** CategorizePosition leaves the ground when the upward speed is above **140 u/s** "on both engines" (`slope_launch_math.h:12-13`). This is the same constant as Source's `NON_JUMP_VELOCITY`.
- **Stance and hull.**
  - **[B]** `m_duckState`: 0 standing, 2 ducked (`player_stance.cpp:23-25`).
  - **[B]** Stand/duck hulls are cached from the settings `poseSettings` (`player.h:1039-1047`).
  - **[B]** Half-duck exists (`m_doingHalfDuck`, `player.h:417`).
  - **[B]** `stepHeight` is a class var.
- **Velocity and command data.** Velocity lives in `CMoveData` (dedi +304, client +292), and the movement code writes back from there. The per-command trace logs pre- and post-move origin and velocity (`move_sim_trace.cpp:220-232`). `CheckVelocity` exists (`armored_leap.cpp:1451`).
- **[A] Script-level events** (server only): `JUMP, DOUBLE_JUMP, DODGE, LEAVE_GROUND, TOUCH_GROUND, MANTLE, BEGIN/END_WALLRUN, BEGIN/END_WALLHANG, BEGIN/END_SLIDE, SLIDE_SUPER_JUMP` (`s21-platform/scripts/vscripts/sh_consts.gnut:1000-1015`). They are dispatched by the engine through `CodeCallback_OnPlayer*` (`s21-platform/scripts/vscripts/_codecallbacks_common.gnut:958-1139`).

### 8.1 State transition sketch (from the fields and events above; transitions are [C] unless cited)

```
           TOUCH_GROUND                      Duck+speed≥slideRequiredStartSpeed (C)
 AIR  ───────────────────▶ GROUND ───────────────────────────────▶ SLIDE
  ▲  ◀─────────────────── (vz>140 / Jump)        ◀── END_SLIDE ──┘   │ Jump (slide jump, 0.4 s refund rule [B])
  │     LEAVE_GROUND / JUMP                                          ▼
  │                                                                  AIR
  ├── wall contact + climb ──▶ CLIMB/WALLHANG ── JumpOutOfWallRun ──▶ AIR (wall jump)
  └── ledge in reach ───────▶ TRAVERSAL(mantle) ── finish ──▶ GROUND (or AIR via forced Jump in mantle boost)
```

## 9. Known parameter values (and where each number comes from)

| Key / ConVar | Value | Is it a retail Apex value? | Source |
|---|---|---|---|
| `sv_gravity` | 750 | yes, default (B) | `slide_super_jump.cpp:57`; `sh_surf_movement.gnut:41` |
| `jumpHeight` (`player_jumpHeight`) | 56 | S21 authored default (B) | `mantle_boost.cpp:649` |
| jump velocity | ≈ 289.8 u/s | derived: √(2·750·56) | §4.1 |
| `skip_speed_reduce` | 100 | stock (B) | `sh_surf_movement.gnut:88-89` |
| `jump_grace_cutoff_speed` (S21) | 1100? | dedi twin default; S21 value inferred (B/C) | `tapstrafe.cpp:31-36` |
| `super_jump_debounce_time` | 0.1 s | B | `jump_input_gate.h:39-40` |
| slide-jump boost refund window | 0.4 s | B | `player.h:1088-1090` |
| airborne sprint grace | 0.25 s | B | `mantle_boost_vm_probe.cpp:26` |
| ground leave upward speed | 140 u/s | B | `slope_launch_math.h:12-13` |
| standable normal z | 0.7 | B | `slope_launch_math.h:14-15` |
| `slideSuperJumpCooldown` | 2.0 s | S21 base setfile (B) | `slide_super_jump.cpp:47-48` |
| `slideSuperJumpHeight` | 150 | S21 `boosted_slide_jump` mod (B) | `slide_super_jump.cpp:45-46` |
| SSJ press window | 0.3 s | B | `slide_super_jump.cpp:30` |
| mantle boost sweet spot | 1.5°, last ≈ 0.10–0.13 s | SDK default, claimed to match S21 (B) | `mantle_boost.cpp:90-92` |
| mantle boost exit multiplier / jump height | 1.3 / 90 | SDK default (A) | `mantle_boost.cpp:101-107` |
| usercmd frametime clamp | 0.002857–0.1 s | SDK (A) | `game/shared/usercmd.cpp:15-16` |
| server tick / update rate | 0.05 s / 20 | platform cfg (A) | `s21-platform/cfg/system/autoexec_server_dev.cfg:18-19` |
| TF2 pilot preset (`speed` 162.5, `sprintspeed` 243, `acceleration` 2500, `airSpeed` 60, `airAcceleration` 500, `gravityScale` 0.75, `jumpHeight` 60 …) | — | **no, Titanfall 2** | `IClassVarLab.cpp:27-54` |
| surf / instagib values (`airAcceleration` 37500 / 1000 …) | — | **no, custom** | `sh_surf_movement.gnut:28-62`; `s21-platform/scripts/vscripts/gamemodes/fs_instagib/sh_gamemode_instagib.nut:13-43` |

Everything else (`speed`, `sprintspeed`, `acceleration`, `airSpeed`, `airAcceleration`, the `slide*` keys, …) has **no retail value in the repositories** → E0 dumps them.

## 10. What this means for a Unity controller (design notes, not evidence)

- Structure the controller like the observed decomposition: per-stance ground params (`speed`/`accel`/`decel` per stand/crouch/sprint), a Source-style `AirAccelerate(wishDir, wishSpeedCap = airSpeed, accel = airAcceleration, dt)`, an explicit press-edge jump with `v = √(2·g·h)`, and landing rules (skip window, multi-jump penalty, hard-landing slowdown) as *separate, tunable* rules.
- Model tap strafe and superglide as *explicit, designed* windows (like the SDK does) rather than relying on frame-order accidents. That keeps them frame-rate independent.
- Keep the "jump on the first grounded frame skips friction" rule optional. It decides how bhop-friendly the game is.
