# M6 source audit: lurch, climb/mantle, ziplines, slopes, M6-B legends, grapple extras

Read-only source study for M6. Nothing was launched and no game, Unity or runner file was changed.

**Path prefixes** (repo-relative, same convention as `../m4/ABILITY-TRIGGERS.md`):

| Prefix | Meaning |
|---|---|
| `SDK:` | `research-src/s21-r5sdk/src/` (patches the S21 client and the S3 dedi) |
| `P:` | `research-src/s21-platform/scripts/vscripts/` |
| `PW:` | `research-src/s21-platform/scripts/weapons/` |
| `<game root>` | the installed R5Flowstate folder |

The installed copy is `<game root>/platform/scripts`. Every script and weapon file cited here was compared with it after line-ending normalisation, and all of them are identical:

- `loba_tactical_translocation.nut`, `mp_ability_phase_door.nut`, `mp_weapon_phase_breach.nut`, `mp_ability_valk_jets(_upgraded).nut`, `mp_ability_grapple.nut`
- `mp_weapon_zipline.nut`, `_zipline.gnut`, `_utility.gnut`, `remap/sv_remap_ziplines.nut`, `mapeditor/_mapeditor_palette.nut`, `sh_alter.gnut`
- `mp_ability_transport_portal.nut`, `_gamemode_survival.nut`, `agent/sv_agent_api.nut`, `scripts.rson`
- all the matching weapon `.txt` files

**Evidence labels**

| Label | Meaning |
|---|---|
| [src-native-boundary] | Closed engine code. The source shows only a signature, an offset, a call site or a comment. |
| [src-sdk] | Implemented in R5Flowstate SDK code. This is community code, not Respawn code. |
| [src-script] | Implemented in vscripts or a weapon `.txt`. |
| [community] | Community report (`ReApex-MovetionRefer/R5Flowstate_S21_Movement_Report_2026-10-20.md`). |
| [m3]/[m4]/[m55] | Our own measurement (see the cited model file). |
| [unknown] | Not determinable from source. |

---

## 0. Summary for the planner

1. **Lurch.** The lurch is native on both engines.
   - The SDK only *suppresses* it: above 1100 u/s horizontal (dedi only), while a mantle boost is active (state 4), and during gravity-cannon flight.
   - There is no window or strength cvar. The window, strength and clamp are already measured in `m3/lurch/LURCH-MODEL.md`.
   - Open items: per-press stacking, scroll-wheel taps, W while turning, walk-off with no jump, a lurch on the wall-jump command, and the reset/anchor after a mantle, zipline or wall jump.
2. **Climb and mantle.**
   - Climbing, traversal and the jump-off are native.
   - The SDK only remaps the climb setfile offsets on the dedi.
   - The "mantle boost" is a full SDK FSM on both sides, a community reimplementation. It replaces the legacy superglide: while it is enabled, a jump press during the pull-up is latched and the native jump-off is masked.
   - Our M3 "boost window" is the FSM's sweet-spot gate opening: |camera delta| < 1.5° and still decreasing.
3. **Ziplines can be spawned deterministically from server script.**
   - Functions: `CreateZipline(start, end)` in `_utility.gnut`, `MapEditPalette_SpawnZipline(start, end, ents)`, or `ReMap_CreateZipline(...)`. The ReMap one also builds vertical ropes. No model precache is needed.
   - Mount is `+use`. Survival also polls `Zipline_TryUse()` while use is long-held in the air. Nothing in source auto-attaches on touch.
   - Exit rules are native, but the SDK documents them: auto-detach clamps speed to [ziplineSpeed, ziplineDetachSpeed] along the end tangent, and a vertical rope clamps |v| to ziplineMaxVerticalDetachSpeed.
   - The SDK adds a re-mount budget: 3 mounts, +1 per 3 s off the rope, reset on landing or mantle.
   - The runner needs a `use` key to test any of this.
4. **M6-B legends.**
   - All four kits have scripts and `.txt` files in this build.
   - Loba and Valkyrie were equipped in M4.
   - Alter has SDK-side support (phase-door depth patch and dedi object-placement natives). Ash's Phase Breach is the *ultimate* (`+offhand4`).
   - Whether Alter and Ash appear in `GetAllCharacters()` is [unknown]. Check with `Agent_Catalog("legends")`.
   - Key numbers:
     - Alter exit speed = clamp(v·n, 50, 300) along the portal normal.
     - Loba sets velocity to 0. A drop-to-ground needs ≥ 0.24 s of flight and then `+attack`/`+offhand1`. A failed teleport refunds the charge.
     - Breach uses path time clamp(d/1200, 0.3, 1.8) s with prediction off and controls frozen. The exit velocity is probably 0 (inferred).
     - Valkyrie fuel = glideDuration (8.0 measured in M4). The drain and activation cost are class vars that a census can read.
5. **The cheapest high-value step is a class-var and cvar census.** It answers the Valkyrie fuel, the zipline speeds and `jump_grace_cutoff_speed` without any trial (E-A, §7).

---

## A1. Lurch / tap strafe

### Findings

**What `tapstrafe.cpp` implements** [src-sdk]. It does **not** implement the lurch.

- It detours `CGameMovement::AirMove` on the dedi only, found by pattern at `SDK:game/server/tapstrafe.cpp:118`.
- For the duration of that one call it masks the direction press bits `IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT = 0x618` in `m_nButtonsPressed` (`mv+0x2C`) (`tapstrafe.cpp:22-26, 83-98`).
- The comment says masking "suppresses only the lurch" (`:22`). The real press bits are restored after AirMove (`:97-98`).
- It masks in three cases (`:78-83`):
  1. horizontal speed > `bridge_lurch_cutoff_speed` (default **1100**, FCVAR_RELEASE, 0 = never; `:33-46`);
  2. `MantleBoost_ShouldSuppressTapStrafe(player)`, that is, boost state 4;
  3. gravity-cannon flight (`TriggerCannon_BeginFlightLock`).
- Debug cvar: `bridge_tapstrafe_debug` (DEVELOPMENTONLY), which prints `[TAPSTRAFE] lurch press suppressed (...)` (`:53-54, 89-91`).

**Client counterpart** [src-sdk + src-native-boundary].

- The S21 client has its own native `C_GameMovement::AirMove_TapStrafe(ctx)` (`SDK:game/client/mantle_boost.h:18-19`, pattern `SDK:game/client/mantle_boost.cpp:1261-1264`).
- The SDK hooks it and skips the native call entirely while `mantle_boost_enabled && mantle_boost_disables_tap_strafes && state == 4` (`mantle_boost.cpp:1073-1100`). The client trigger-cannon lurch denial also goes through this hook (`SDK:game/client/trigger_cannon.h:5-6, 24-25`).
- The comment at `mantle_boost.cpp:97` says "S21 AirMove_TapStrafe has no native state==4 self-suppress".

**Client vs dedi lurch per the code comments**

- `tapstrafe.cpp:31-32`: "The S21 client skips the lurch above jump_grace_cutoff_speed; the dedi inline lurch has no speed gate". So the client cutoff is native (cvar name `jump_grace_cutoff_speed`, value not in source [unknown]). The dedi mirrors it with the SDK cvar.
- `tapstrafe.cpp:3`: "native inline lurch" on the dedi.
- **Stale contradiction.** `SDK:core/init_server.cpp:664` still calls this a "from-scratch port ... dedi has zero trace of the mechanic ... ONE detour on CGameMovement::FullWalkMove". The code hooks AirMove, and M3 found the dedi reproduces the lurch natively (101/102 identical; `m3/lurch/LURCH-MODEL.md` §6). The registration comment is stale.

**Window, strength, speed and direction rules**

- No cvars exist for these in the SDK or in scripts [src-sdk]. The only related script string is a commented-out `SetConVarToDefault("jump_graceperiod")` (`P:sh_utility_all.gnut:4409`). It hints that an engine cvar `jump_graceperiod` exists [unknown value].
- The measured model is [m3]:

  ```
  λ = 0.7·clamp((0.5 − t)/0.3, 0, 1)
  lerp(vhat, wishdir) at the same speed
  |Δv| clamped to 209.3 u/s
  ```

  It runs after AirAccelerate, on the press-edge command only. The time t is counted from the jump command. Back is a 209.3 brake, and W along the velocity is a no-op.
- The press gate is the press-edge mask 0x618 [src-sdk comment + m3]. A held key does nothing.

**Per-press stacking, scroll-wheel and reset conditions** [unknown in source]

- The gate is "new bit in m_nButtonsPressed", so each new press edge inside the window should lurch again [inference]. This is untested (M3 open question 6).
- Scroll-wheel tap strafe: a wheel bind generates `+forward`/`-forward` with no hold. Whether the press-edge command keeps a non-zero wish direction (kbutton fractional state) decides whether it lurches [unknown].
- Reset or anchor:
  - The window is anchored at the jump command [m3]. Nothing in source states what re-anchors it.
  - Candidate re-anchors are any call of native `CGameMovement::Jump`:
    - the forced exit jump of the mantle-boost FSM, state 3 and state 4 (`SDK:game/server/mantle_boost.cpp:617-650`);
    - the wall jump `JumpOutOfWallRun` (`SDK:game/server/wall_launch.cpp:53`);
    - the zipline jump-off `Zipline_JumpOff` (`SDK:game/server/zipline_exit_parity.cpp:134-136`).
  - M3 saw an unexplained vector (140.9, 177.5) instead of (182.8, 75.1) when moveright was pressed on the wall-jump command (`m3/wall_mantle/WALL-MANTLE-MODEL.md` §3.2). That fits a lurch on the wall-jump command [inference].
- Post-boost suppression ends on landing (time-last-landed advances past the boost time), when a grapple taken during the boost detaches, or at the next traversal start (slot reset) (`SDK:game/server/mantle_boost.cpp:756, 805-835`). A zipline ride does **not** clear it [src-sdk].

### Experiments (E-L)

Shared setup: lane B, Gibraltar, 120/144 fps, `bridge_move_trace 1` on both sides. The analysis is `m3/lurch/lurch_analysis.py` extended to more than one press per jump.

**Runner extension needed.** Add a verb `wheel <key>` that sends `+key` and `-key` in the **same** script frame (no WaitFrame between them). This is the scroll-wheel input. It is a small change to `SCHED_CLIENT` and `parse_schedule`.

| ID | Schedule (our language) | Measures | Control |
|---|---|---|---|
| L1 stack A→D | `wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 3; up forward; up speed; down moveleft; waitf 10; up moveleft; down moveright; wait 0.9s; up moveright; wait 0.5s` | second press edge lurches? Δv on both press commands | e3_right_k3 (single press) |
| L2 re-tap same key | `…tap jump; waitf 3; up forward; up speed; tap moveright; waitf 6; tap moveright; waitf 6; tap moveright; wait 0.9s` | Δv per tap. Prediction: each later tap pulls toward the same wishdir, so it shrinks | L1 |
| L3 wheel W while turning | `wait 72; set cl_yawspeed 360; down speed; down forward; wait 1.0s; tap jump; waitf 2; up forward; up speed; down right; waitf 6; wheel forward; waitf 6; wheel forward; waitf 6; wheel forward; up right; wait 0.9s` | does a same-frame W press lurch toward the new view? Also the forwardmove value on that cmd | same schedule with `tap forward`; same with no W at all |
| L4 back after 0.286 s | `e3_back_k40`, `_k45`, `_k50` (generate like `e3_right_k<N>`) | the abrupt cut of the brake at λ < 0.5 (M3 prediction) | e3_back_k12 |
| L5 diagonal | `…tap jump; waitf 3; up forward; up speed; down moveright; down backward; wait 0.9s; …` | θ ≈ 135° prediction | – |
| L6 walk-off (no jump) | lane with a drop (spawn pad: SPAWN_PAD edge, or sunk wall top as ledge; see E-C): `down speed; down forward; waitair; waitf 3; up forward; down moveright; …` | lurch with no jump anchor? | same with a jump |
| L7 wall-jump command | `e6_bounce_side_15` already exists; add `…tap jump; wait 0.43s; up forward; up speed; down moveright; waitf 2; tap jump; …` (key edge 2 frames before the jump) | separates "lurch on the jump cmd" from the wall-jump input rule | e6_bounce_none_15 |
| L8 after mantle boost | `e7_mb_f205` (120 fps), then `waitf 10; down moveright; wait 0.5s` | press suppressed while state 4: expect `[TAPSTRAFE] lurch press suppressed (mantle boost active)` with `bridge_tapstrafe_debug 1` on the dedi. Client has no log; check MOVE-TRACE Δv = 0 | same after a state-3 exit (`e7_mb_f190`) |
| L9 cutoff 1100 | needs horizontal speed > 1100 in the air. Server thread on the JUMP movement event (`AddPlayerMovementEventCallback(p, ePlayerMovementEvents.JUMP, ...)`, `P:_codecallbacks_common.gnut:958`) does `p.SetVelocity(v*4)`, then the press at k = 5 | dedi suppression vs client native gate (client `jump_grace_cutoff_speed` value from E-A) | same at ×2 (< 1100) |

- **Cost/value.**
  - L1–L5 are cheap (lane B, no geometry, about 20 trials each) and close real gaps in the Unity lurch model.
  - L3 needs the `wheel` verb, but it is the HSD-relevant "tap strafe".
  - L6/L7 need geometry from E-C.
  - L9 is costly and risks a correction artefact (server-set velocity). It is low priority, because HSD speeds above 1100 are rare.

---

## A2. Climb, ledge and mantle

### Findings: who implements what

| Piece | Implementation | Evidence |
|---|---|---|
| Climb (wall contact → vertical climb → final jump-up) | native wallrun code path, both engines | [src-native-boundary] `SDK:game/server/wallclimb.cpp:1-6` (the SDK only rewrites the S3 dedi's SettingsFieldFinder offsets to the live S21 player-settings layout, `:36-64`, cvar `bridge_wallclimb_settings 1`) |
| Wall bounce (jump off the climb) | native `JumpOutOfWallRun` | [src-native-boundary] `SDK:game/server/wall_launch.cpp:53` |
| Mantle / vault (TraversalMove) | native | [src-native-boundary] `SDK:game/server/mantle_boost.cpp:3-5, 722-803`. Traversal fields `m_traversalType` (0 mantle, else window vault) and `m_traversalState` (**11 idle/hang**, **12 jump-off**) (`:57-58`) |
| Mantle boost FSM, the "superglide" | **SDK on both sides** (client "predicted twin", `SDK:game/client/mantle_boost.cpp:1-6`) | [src-sdk] |
| Sparrow wall launch | SDK community addition, opt-in `SetWallLaunchEnabled` | [src-sdk] (phase-1 notes) |
| Retail wallrun | off (playlist `survival_wallrun_enabled` 0) | [src-script] phase-1 `Movement-Analysis.md` §6 |

### Class vars readable at runtime (`bridge_classvar_get <key>`, `SDK:game/client/classvar_natives.cpp:251-293`)

An unknown key prints `[CLASSVAR] unknown key`, which is harmless. Already in our E0 census (`phase2-prep/cfg/hsd_e0_classvars.cfg`):

```
climbEnabled, climbHeight, climbFinalJumpUpHeight, climbSpeedStart, mantleAngleScale
wallrun, wallrun_timeLimit, wallrun_hangTimeLimit
wallrunAccelerateHorizontal/Vertical, wallrunMaxSpeedHorizontal/Vertical
wallrunJumpOutwardSpeed/UpSpeed/InputDirSpeed
```

**Add** these. The names come from the SDK finder list `SDK:game/server/wallclimb.cpp:44-64` and the jump-off code:

```
verticalGainCutoff_wallrun, wallrunDuckCausesFallOff, wallrunAdsType
wallrunAllowedWallDistance, wallrunAllowedWallDistanceWallHang
wallrunCeilingLimit, wallrunSameWallHeight, wallrunSameWallAllowed
wallstickEnabled, wallrunUpWallBoost, wallrunMaxSpeedHorizontalBackward
```

Mantle- and traversal-specific setfile keys other than `mantleAngleScale` are not named anywhere in source [unknown]. Probe candidate names in the census; a miss costs nothing.

### Script and telemetry surface

- **Player methods** (client and server, used in shipped scripts): `IsTraversing()`, `IsMantling()`, `IsWallHanging()`, `IsWallRunning()`, `IsOnGround()`, `IsSliding()` (`P:mp/sh_emotes.nut:1114-1120`, `P:gamemodes/sh_gamemode_survival.nut:506`).
- **Server movement events:** `MANTLE`, `BEGIN/END_WALLRUN`, `BEGIN/END_WALLHANG`, `JUMP`, `TOUCH_GROUND` (`P:sh_consts.gnut:1000-1015`), through `AddPlayerMovementEventCallback` (`P:_codecallbacks_common.gnut:958`).
- **Callback** `CodeCallback_OnPlayerMantleBoosted(player)` on both VMs (`P:server/sv_bridge_mantle_boost.gnut:5-7`, `P:client/cl_bridge_mantle_boost.gnut:6,15`). The dedi fires it on a state-4 finish (`SDK:game/server/mantle_boost.cpp:609-611`).
- **Dedi logs** (DEVELOPMENTONLY):
  - `bridge_mantle_boost_trig_log 1` prints `[MB-TRIG] travState raw anim delta prev gate -> state` and `[MB-CLIMB]` (`mantle_boost.cpp:113-114, 511-520, 691-697`). The same names exist on the client.
  - `bridge_mantle_boost_apply_log 1` prints `[MB-APPLY]` (`:111-112, 698-707`).
  - `bridge_wallclimb_tap 1` prints `[WALLCLIMB] ev=attach|detach|on` with wall up-dir `up=`, predicted up-dir, origin, velocity, **ground normal `gN=`** and settings values (`SDK:game/server/wallclimb.cpp:75-76, 367-447`).
- There is no script getter for the traversal state or the FSM state. Use `[MB-TRIG] travState=` (11/12) only on press edges.

### Hang, cancel and mantle hop

- Community description: release W to hang, press back to cancel, jump to hop [community].
- In source:
  - Native traversalState 11 is idle/hang (`mantle_boost.cpp:57-58`).
  - When a climb settles into the hang, the FSM marks it **INVALID (state 1)**, so a hang can never boost (`:765-768`).
  - A jump press during the pull-up while the FSM is idle (state 0) is *evaluated* and latched to 3 or 4. The FSM then **masks IN_JUMP** for the rest of the traversal, so the native jump-off cannot fire (`:774-785`). It also clears any native jump-off stamp (`:786-793`).
- Consequences [src-sdk]:
  - With the FSM on, a "mantle hop" during the pull-up is replaced by a deferred exit jump (state 3: h = 56, or state 4: boost).
  - A hop from the **hang** (state 1, not evaluated) is the native jump-off.
  - The M3 classes agree: state-3 "exit jump at h 56" (`WALL-MANTLE-MODEL.md` §4.2).
- Mantle resets the zipline re-grab budget (`mantle_boost.cpp:729-733` → `ZipDisc_OnMantle`).

### Is mantle_boost a superglide reimplementation?

**Yes. It is an explicit, community-written FSM** [src-sdk].

- **Gate cascade on the first activation press edge** (`mantle_boost.cpp:435-525`). The default activation is `mantle_boost_input_setting 1` = jump. The input is per-client USERINFO: 2 = crouch, 3 = `bridge_mantle_boost_button_mask`, default IN_DODGE (`:82-89, 123-176`). The gates, in order:
  - no camera sample → 3 (`nocam`);
  - optional "increasing" rule (off);
  - `mantle_boost_require_decreasing_view_angle 1`: |delta| must be settling toward 0 (`dec`);
  - |anim camera pitch − eye pitch| < `bridge_mantle_boost_sweet_spot_angle 1.5`° (`angle`);
  - anim frac > `mantle_boost_min_valid_traversal_frac 0.5` (`frac`);
  - otherwise state 4.
- **Finish when progress reaches 1.0** (`:550-720`):
  - Exit velocity = move dir, reflected if it points backwards, × `GetPoseSpeed_Sprint` (fallback `bridge_mantle_boost_exit_speed 260`). State 4 multiplies this by `bridge_mantle_boost_sprint_mult 1.3`.
  - Then one native `Jump` with vz += √(2·g·h): h = `bridge_mantle_boost_jump_height 90` for state 4, 56 for state 3.
  - State 4 also stamps the slide time and grants a slide (`:608, 688`).
  - Per-player scale: `player.SetMantleBoostProfile(heightScale, sprintScale)`, used by the Sparrow passive (`:885-917`, `P:pilot/sh_pilot_passive_sparrow.gnut:95-101`).
  - Master switch: `mantle_boost_enabled 1`. The client and the dedi must match (`:79-81`; client `SDK:game/client/mantle_boost.cpp:40-42`). The client takes the dedi verdict off the wire by default (`bridge_mantle_boost_authoritative 1`, `:89-95`).
- **Difference from the legacy superglide.**
  - Legacy: jump, then crouch about one frame later, near the end of the mantle. It is emergent in native code and not present in open source (phase-1 `Movement-Analysis.md` §7) [community].
  - The FSM decides on the **press** with a camera-angle gate. Crouch timing is irrelevant (M3: sg = mb at every N), and the outputs are fixed numbers.
  - The cvar comments call the names "ship-named … S21 default". That suggests they copy a Respawn settings name. The community report lists official Mantle Boost as a *later* Apex feature [community], so in S21 terms this is a community feature, not retail S21 physics.
  - While the FSM is on, the legacy path cannot occur, because the first jump press is latched and the IN_JUMP mask removes the native jump-off.
- **What our M3 "boost window" is.** The measured window is the last 0.133 s, anim > 0.777 (`WALL-MANTLE-MODEL.md` §4.3). The fails just before the edge all hit gate `angle`, with delta crossing 1.5°. So the window is the **sweet-spot angle gate** (camera delta < 1.5° and decreasing). It is not the 0.5 frac gate, which is already open by then.

### Experiments (E-C)

**Geometry.** We have one rock model whose face M3 measured (`tools/test_geometry.py`, `M3_WALL_MODEL`, top about 232 u). To get chosen ledge heights H, spawn the same rock **sunk into the floor**: `z = 294.92 − (232 − H)`. Then run `measure` to get the actual top and face profile; the rock is irregular and leans 1.86°.

```
py -3 test_geometry.py clear
py -3 test_geometry.py spawn --model mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl --origin -13600 6500 <z> --yaw 0
py -3 test_geometry.py measure --x0 -13900 --x1 -13300 --y 6500 --z0 300 --z1 700 --dz 4
```

Heights: H = 60, 90, 120, 150, 180, 232 (existing), plus one *taller* wall. Stack two rocks: the second at z + 200, same x/y.

- The climbHeight-100 boundary should show between H ≈ 150 and 232: the climb gained 96 u at 232 in M3.
- A flat alternative: `mdl/city_modern/citymodern_wall_256x384_concrete_dtown_a.rmdl` / `…256x128_concrete_slab_a.rmdl` are in the map-editor catalogue (`P:mapeditor/sh_mapeditor_catalog.gnut`). Whether they load on this map through `MapEdit_PrecacheModel` is [unknown], so let `test_geometry.py spawn` report `precached=`.

Per-session setup: `bridge_mantle_boost_trig_log 1`, `bridge_mantle_boost_apply_log 1` and `bridge_move_trace 1` on both sides, plus `bridge_wallclimb_tap 1` on the dedi.

**Runner addition: a client state logger.** Run it as an EVAL thread started with the schedule. It stops when `hsd_md_run` returns to 0.

```squirrel
entity p = GetLocalClientPlayer()
while ( GetConVarInt( "hsd_md_run" ) != 0 )
{
	printt( "[HSD-STATE] fc=" + FrameCount() + " t=" + Time()
		+ " trav=" + ( p.IsTraversing() ? 1 : 0 ) + " mant=" + ( p.IsMantling() ? 1 : 0 )
		+ " hang=" + ( p.IsWallHanging() ? 1 : 0 ) + " wr=" + ( p.IsWallRunning() ? 1 : 0 )
		+ " zip=" + ( p.IsZiplining() ? 1 : 0 ) + " gr=" + ( p.IsGrappleActive() ? 1 : 0 )
		+ " ph=" + ( p.IsPhaseShifted() ? 1 : 0 ) + " glide=" + p.GetGlideMeter() )
	WaitFrame()
}
```

Wrap each getter in try/catch on first use. `GetGlideMeter` is called in shared scripts but only inside `#if SERVER` blocks, so check that it exists on the client.

| ID | Schedule | Measures | Control |
|---|---|---|---|
| C1 height sweep | `e6_climb` on each H | climb vs instant mantle threshold; Z_end and Z0 relative to the ledge or the floor (M3 open question 3); climbHeight cap | M3 H = 232 data |
| C2 hang | `wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.9s; up forward; up speed; wait 2.0s` (W released before the ledge) | `[HSD-STATE] hang/trav` timeline; `[MB-TRIG] travState=11` on a later press | e6_climb |
| C3 cancel | C2 then `down backward; wait 0.5s; up backward; wait 1.0s` | drop-off velocity from the hang | C2 |
| C4 hop from hang | C2 then `tap jump` (+ variants with moveright / backward held) | native jump-off velocity (no FSM: state 1) | C2 |
| C5 FSM off | `set` is not usable here: `mantle_boost_enabled` is a gameplay cvar, not a VIEW_CVAR. The runner sends `mantle_boost_enabled 0` to the **dedi and client consoles** before the session and restores it after. Rerun `e7_mb_f<N>` and `e7_sg_f<N>` (120 fps, N 185–215) | the **legacy superglide** under native code: does jump + crouch (sg) differ from jump (mb) once the FSM is out? Client/dedi divergence (the S3 dedi traversal may differ) | same N with the FSM on (M3 data) |
| C6 144-fps window | `e7_mb_f230..f260` step 3 at 144 fps | M3 open item 1 | – |
| C7 crouch same frame / first | new steps: `…waitf N; down duck; tap jump; up duck` and `…waitf N; tap duck; tap jump` | FSM says crouch is irrelevant in input mode 1 | e7_mb_fN |

- **Cost/value.**
  - C1–C4 need about one geometry session per H. The rock trick costs nothing to build.
  - They give HSD climb/hang semantics that are currently only community text.
  - C5 is the only way to see what retail-like native code does without the community FSM. Cost is moderate (one session), and its value for the "classic superglide" question is high.

---

## A3. Ziplines

### Creating ziplines from server script (deterministic)

Three ready-made server functions all build a `zipline` + `zipline_end` pair, `LinkToEnt`, `DispatchSpawn`. **No model precache** is needed for the bare rope (material `cable/zipline.vmt`).

| Function | Where | Notes |
|---|---|---|
| `array<entity> CreateZipline( vector startPos, vector endPos, bool disableResting = false, float detatchDistanceOverride = -1, bool skin = false )` | `P:_utility.gnut:4041-4083` (`globalize_all_functions`) | Auto: if \|dir.z\| > 0.7 → `ZiplineVertical = 1`, `ZiplinePreserveVelocity = 1`, auto-detach "0"; else auto-detach "160" (`:4043-4064`). Rest points = start/end (taut rope). |
| `bool MapEditPalette_SpawnZipline( vector start, vector end, array<entity> ents )` | `P:mapeditor/_mapeditor_palette.nut:173-219` (global, server) | Distance 64–8192 (`:14`, `P:mapeditor/sh_mapeditor.gnut:44`). Explicit KVs: auto-detach 100, speed scale 1, `ZiplineVersion 3`, `ZiplineVertical 0`. The comment says this is the form the S21 client understands (`:170-172`). It does not check `MapEditor_IsEnabled`. |
| `ReMap_CreateZipline( start, startAng, end, endAng, startProfile, endProfile, bool vertical, width, speedScale, …, pushOffInDirectionX, …, preserveVelocity, dropToBottom, startAutoDetachDistance, endAutoDetachDistance, … )` | `P:remap/sv_remap_ziplines.nut:60-116` (global; compiled for SERVER, `P:scripts.rson:2999-3004`) | Supports **vertical** (end placed straight above or below the start, push-off angle). Profile `REMAP_ZIPLINE_END_NONE` (0) avoids arm models. Exposes `ZiplineSpeedScale` and per-end auto-detach. |

Shipped examples:

- The Pathfinder ult `CreateGunZipline` (`P:weapons/mp_weapon_zipline.nut:430-486`): auto-detach 100, breakable, realm-limited. Pathfinder-placed ropes give the rider setfile mod `fast_zipline` (`P:pilot/_zipline.gnut:799-806`).
- `BunkerDoor_CreateZipline` for a vertical deploy (`P:_utility.gnut:3989-4039`).
- fs_1v1, fs_scenarios and sv_freelance only **disable or cull** `trigger_no_zipline` / zipline entities (`P:gamemodes/fs_1v1/_gamemode_1v1.nut:2551`, `P:gamemodes/fs_scenarios/_scenarios.nut:179-189, 1584`, `P:freelance/sv_freelance.nut:75-77`). None of them create ropes.
- The Pathfinder kit in this build includes `mp_weapon_zipline` as the ultimate (M4 kit reply), so the natural ult path also exists.

**Safety.** An uncaught server script error shuts the host down (M3). Wrap spawns in try/catch, as `test_geometry.py` does. Never `Destroy()` a rope while the player rides it: call `p.Zipline_Stop()` first (`P:abilities/loba_tactical_translocation.nut:1095-1096` uses it).

### Attach (mount)

- **Input: `+use` (IN_USE)** on the rope entity. It goes through the entity Use handler → native `Zipline_Use(player, forGrappleZipline)` → native `Zipline_Find(player, pos, eyeDir, …)` [src-native-boundary] (`SDK:game/server/zipline_exit_parity.cpp:125-141`). Mount is client-predicted (`SDK:game/client/zipline_disconnect.cpp:1-6`).
- **Survival long-use.** While IN_USE_LONG is held, a thread calls `player.Zipline_TryUse()` every frame, only when **not on the ground** (`P:gamemodes/_gamemode_survival.nut:4494-4515, 4684`). This is the "air grab" path. Whether that callback is registered in our firing-range playlist is [unknown].
- `player.Zipline_TryUse()` is also a **server method we can call from EVAL** for a deterministic mount attempt [src-script].
- **No auto-attach on touch** appears anywhere in source [src-script / unknown for native].
- **Search geometry.**
  - The engine collector searches from origin + 72 u (`ZE_MOUNT_SEARCH_EYE_RAISE`, `zipline_exit_parity.cpp:281`).
  - Rail-candidate radius 120 "matches the engine's own collector radius" (`:218-221`).
  - Find uses the eye direction. The angle tolerance is [unknown]. The use-cone cvars in `extended_range_use.cpp` apply only to script extended-range use entities.
- **Mount side effects (server script):** forced stand stance, a sound, `fast_zipline` on Pathfinder ropes, and the LiveAPI `ziplineUsed` event (`P:pilot/_zipline.gnut:771-814`). Callbacks: `AddCallback_ZiplineMount/Start/Stop` (`:907-932`).

### Ride, detach, exit velocities

- **Ride speed.** Native. Player setting `ziplineSpeed` (resolved at runtime, `zipline_exit_parity.cpp:611-618`) × entity `ZiplineSpeedScale`. Pathfinder ropes add the `fast_zipline` mod.
  - The SDK slows a rider who has another player ahead within 100 u (speed × 0.25, accel × 0.5; `bridge_zip_player_in_front 1`, `:186-188, 769-…`).
  - The ride accel profile is [unknown].
  - Ziprails (curved S21 rails) are a separate SDK model. Defaults: accel 150, path gravity 400, max speed mul 1.2, min speed frac 0.57, detach 450, jump-off 100–550, view influence 0.5, detach dir −10…+26° (`:240-261`).
- **Auto-detach** (end of rope within the entity's `ZiplineAutoDetachDistance`; 350 if unset, `:108-110`). The SDK makes the dedi copy the S21 client rule (`bridge_zip_exit_parity 1`):
  - **Rope:** v_out = d̂_end · clamp(v·d̂_end, `ziplineSpeed`, `ziplineDetachSpeed`), where d̂_end is the last segment direction (`:1962-2005`).
  - **Vertical:** |v| clamped to `ziplineMaxVerticalDetachSpeed` (`:1734-1760`).
  - The detach radius is measured from origin + hull height, not the eye (`:179-181`).
  - The ride stops at the client's detach alpha (`:172-174`).
- **Manual jump-off.** Native `Zipline_JumpOff(zip, player, vel, eyeAngles, forwardMove, sideMove)`. Inputs are the view and the move keys [src-native-boundary].
  - The SDK rewrites the result only for ziprails with a baked path: speed clamp [min, max] JumpOff, direction cone −10°/+26° (`:2212-2330`).
  - Plain ropes keep the native result. Its formula is [unknown]; measure it.
- **Crouch-off.** Native. Entity/setting `ziplinePreventManualDetach` blocks manual detach (`SDK:engine/server/zipline_validation.cpp:635-738`). `sdk_ziprail_duck_detach 0` clamps a ducked *rail* jump-off to the minimum (`:260-261`). Plain-rope crouch-off velocity is [unknown].
- **`halfduck_zip_parity` (which parity fix).** `m_doingHalfDuck` is latched once at duck start and is not networked. Duck is suppressed while ziplining, so after a release the two engines sample it one command apart. Only one of them then applies the `(standHull − duckHull)·0.5` origin step.
  - The fix forces the latch on a duck that starts within a grace window after the release: 3 commands on the dedi, 0.15 s on the client.
  - **Default OFF:** `bridge_halfduck_zip_parity 0` on both sides (`SDK:core/init_server.cpp:645`; `SDK:game/server/halfduck_zip_parity.cpp:74-81`; `SDK:game/client/halfduck_zip_parity.cpp:79-87`).
  - So a crouch-off may show a **client/dedi z divergence of half the hull difference**. Compare both traces.
  - The client also predicts the forced-stand push/pop (`bridge_zip_forcestance_predict 1`, `:100-102`).
- **`c_zipline.cpp`:** a null-pointer guard for zipline validation on converted maps. No movement effect (`SDK:game/client/c_zipline.cpp:1-30`).

### Re-attach budget and cooldown

- **`bridge_zip_disc 1` (both sides, default ON)** [src-sdk]. The comment calls it the "latest zipline hop-regrab count", so it is modelled on current Apex, not S21:
  - 3 successful mounts, then a further mount is refused;
  - +1 back every 3 s off the rope;
  - full reset on landing or mantle (`SDK:game/server/zipline_disconnect.cpp:1-24, 69-144`; client twin `SDK:game/client/zipline_disconnect.cpp:14-21, 232-265`).
  - Diag: `bridge_zip_disc_diag 1` prints `[ZIP-DISC] consume/refuse/reset/+1`, `[ZIP-JUMPOFF]`, `[ZIPRAIL-USE]`.
- **Escalating cooldown ladder** 0.1/0.2/1/3/5 s, which "mirrors client zipline_cooldown_*". On the dedi it is **off** (`bridge_zip_cooldown_enable 0`), because enabling it desyncs with the client (`SDK:game/server/zipline_cooldown.cpp:22-66`). Whether the S21 client enforces its own ladder is [unknown]. Read `zipline_cooldown_*` in E-A.

### Super Jump (ground jump after a zip jump-off)

- Community: a zipline jump-off immediately followed by a grace-period ground jump; Mantle Jump and Float Jump are variants [community].
- No explicit code exists in open source. It must emerge from native `Zipline_JumpOff` + `Jump` + grace logic [unknown].
- Candidate knobs:
  - the engine cvar `jump_graceperiod` (named only in a comment, `P:sh_utility_all.gnut:4409`);
  - the dedi anti-multi-jump timestamp (`MB_PLAYER_OFF_SKIP_TIMESTAMP`, `SDK:game/server/mantle_boost.cpp:51`);
  - the double-jump debounce `super_jump_debounce_time 0.1 s`, which applies to double jumps only (`SDK:game/shared/jump_input_gate.h:39-40`).

### Pathfinder grapple and ziplines

- Native `Zipline_Use(player, bool forGrappleZipline)` exists on both engines (`SDK:game/server/zipline_exit_parity.cpp:125-126`, `SDK:game/client/zipline_disconnect.cpp:55`). So a **grapple → zipline handoff is a native path** [src-native-boundary]. Its trigger (hook hitting the rope?) is [unknown].
- The grapple drain thread **ends when the player becomes ziplining** after the grapple started (`P:weapons/mp_ability_grapple.nut:321-338`). The script expects the transition.
- Gravity lift and hover vehicle refuse entry while `IsGrappleAttached() || IsZiplining()` (`P:mp/sh_space_elevator.gnut:748`, `P:sh_hover_vehicle.gnut:1326`).

### Experiments (E-Z)

**Runner changes.**

- Add `use` (and optionally `attack`) to `KEYS`.
- Spawn the ropes once per session (a new `--geometry m6zip` that calls the snippet below on the dedi), not per reset.
- Add a reset prefix entry that ensures the player is off the rope:

```python
SCHEDULE_PRE["m6_zip"] = 'if ( p.IsZiplining() ) p.Zipline_Stop()\npre = " zip=" + p.IsZiplining()\n'
```

Session spawn snippet (dedi EVAL, lane C at y 6800 is clear from x −14825 to −12475):

```squirrel
string out = ""
try
{
	foreach ( entity e in GetEntArrayByScriptName( "hsd_zip" ) ) e.Destroy()
	array<entity> all
	// Z1 flat, 1600 u long, rope 100 u above the floor (sweep 80/100/120/140 in a pilot)
	all.extend( CreateZipline( <-14600, 6800, 394.92>, <-13000, 6800, 394.92>, false, 100 ) )
	// Z2 sloped down ~10.6 deg (also the reverse direction by mounting at the low end)
	all.extend( CreateZipline( <-14600, 6650, 694.92>, <-13000, 6650, 394.92>, false, 100 ) )
	// Z3 vertical 800 u (|dir.z| > 0.7 -> ZiplineVertical, PreserveVelocity, detach 0)
	all.extend( CreateZipline( <-14700, 6500, 314.92>, <-14700, 6500, 1114.92> ) )
	foreach ( entity e in all ) e.SetScriptName( "hsd_zip" )
	out = "zip_ents=" + all.len()
}
catch ( err ) { out = "error=" + string( err ) }
AgentLink_Reply( out )
```

Check Z3 against the M3 wall (y 6380..6620 at x −13706); x −14700 is clear of it.

**Telemetry.**

- `[HSD-STATE] zip=` (client), MOVE-TRACE (both sides), `bridge_zip_disc_diag 1`, `bridge_zip_exit_debug 1` and `bridge_zip_mount_diag 1` (dedi).
- Server callbacks are available for a printt logger: `AddCallback_ZiplineMount/Stop`.

| ID | Schedule (start pose and yaw per test) | Measures | Control |
|---|---|---|---|
| Z0 mount range | start under or beside Z1 at lateral offsets 0/40/80/120/160 u and rope heights 80–140; `wait 72; tap use; wait 2.0s` | mount yes/no, mount cmd, snap position (`Zipline_Find` radius and height window) | same with no `use` (no auto-attach) |
| Z1 ride | mount, then `wait 3.0s` | speed profile v(t) (accel, cap = ziplineSpeed?), rope-end auto-detach exit vs the SDK rule | E-A census values |
| Z2 jump-off | mount, `wait 0.8s; tap jump; wait 2.0s` × view pitch {−30, 0, +30} × keys {none, forward, back, moveright} | native jump-off velocity law | Z1 |
| Z3 crouch-off | mount, `wait 0.8s; tap duck; wait 2.0s` | crouch-off velocity; client vs dedi z (half-duck parity) | Z2 |
| Z4 budget | `tap use; wait 0.5s; tap jump; waitf 20; tap use; …` ×5 in the air (rope well above the floor), then a variant with a 3.2 s wait | refusal after 3; +1 after 3 s; reset on landing | – |
| Z5 Super Jump | low Z1 (rope 100 u), `tap use; wait 0.5s; tap jump; waitf K; tap jump` for K = 1..12 | second jump applied? vz/vxy vs K → grace window | K = 40 |
| Z6 sloped/vertical | Z2 downhill and uphill; Z3 up to the top auto-detach | slope speed model; vertical exit clamp (ziplineMaxVerticalDetachSpeed) | Z1 |
| Z7 air grab | jump toward Z1 from 200 u, `tap use` at the apex | air mount (`Zipline_Find` in air); also try holding `use` (long-use path) | Z0 |

- **Cost/value.** Ziplines are a core HSD traversal primitive that we have **zero data on**.
  - Z0–Z3 need one session after the runner change (the `use` key plus the spawn snippet).
  - Z4–Z5 decide whether Super Jump belongs in HSD.
  - Priority: high.

---

## A4. Ceilings, slopes, ground normal

- **Apex keeps grounded velocity flat** and slides only the position along a slope. The Source ramp launch is an SDK opt-in (`sv_slope_launch 0`, REPLICATED). Do not enable it for measurements (`SDK:game/shared/slope_launch_math.h:1-33`, `SDK:game/server/slope_launch.cpp:25-29`). The ground leave threshold is 140 u/s upward, and floors with normal.z ≥ 0.7 are standable (`slope_launch_math.h:12-15`) [src-sdk citing native].
- **Slide on slope:** fully native. No SDK twin and no class-var names in source [unknown]. Candidates for the census are slide keys already present (slideAccel, slideDecel, slideVelocityDecay …). Downhill-specific keys are unknown.
- `m_onSlopeTime` exists on the player (`SDK:game/server/player.h:517`). It is used as the "airborne sprint grace anchor 0.25 s" (`SDK:game/server/mantle_boost_vm_probe.cpp:26`).
- **Ground normal telemetry.**
  - `m_groundNormal` (CPlayer+0x5DA4 dedi, written by every SetGroundEntity; `slope_launch.cpp:22`) is a predicted field. It is not exposed to script [src-sdk].
  - It *is* printed as `gN=` in `[WALLCLIMB]` lines (`bridge_wallclimb_tap 1`), but only on wall attach/detach/on-wall events.
  - For per-frame values, trace in the logger:
    ```
    TraceHull( o, o - <0,0,4>, p.GetPlayerMins(), p.GetPlayerMaxs(), [p], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER ).surfaceNormal
    ```
- **Ceilings:** `wallrunCeilingLimit` is a class var (census). Ceiling bonk is native [unknown law].

### Experiments (E-S)

- **Ramps:** spawn a slab prop pitched by α ∈ {10, 20, 30, 40}°, for example the catalogue `citymodern_wall_512x128_concrete_slab_a.rmdl` with angles `<α, 0, 0>`.
  - Verify with a **vertical** trace profile. `test_geometry.py measure` traces horizontally, so add a `--vertical` mode (z top → bottom along x).
  - Schedules:
    - downhill slide: `wait 72; down speed; down forward; wait 1.0s; down duck; wait 2.0s; up duck; up forward; up speed`;
    - uphill: the same with yaw 180;
    - slide jump on the ramp.
  - Measure: slide acceleration vs α (fit dv/dt = −(100 + 0.357 v) + g_eff·sin α?), slide-stop speed, launch at the crest, and the trace normal.
- **Ceiling:** a horizontal slab at floor + 90/110 u above lane B; `e4_stand` and the slide jump. Measure vz on contact (zeroed or reflected) and the ceiling-climb limit.
- **Cost/value.** Medium cost: the prop pitch and the collision of a rotated slab must be verified. Value is medium, since HSD levels have ramps. Run it after E-Z.

---

## M6-B: legend abilities in this build

Kit equip uses `KIT_SERVER` in `tools/hsd_trial.py` (from the M4 notes). **Run `Agent_Catalog( "legends" )` first** (`P:agent/sv_agent_api.nut:952-957`) to confirm that `character_alter` and `character_ash` exist. Then `--legend alter|ash --kit`. The kit reply prints the resolved tactical, ultimate and passive classnames.

### Alter, Void Passage (`mp_ability_phase_door`, tactical)

- **Presence.**
  - Script and `.txt` are present and registered (`P:scripts.rson:914-917`).
  - The SDK patches the client max wall depth 20 m → 30 m to match "the dedi placement and the Void Passage range" (`SDK:game/client/phase_door_depth.cpp:1-10`).
  - The dedi object-placement natives are an **SDK reimplementation**: phase-door placement distance defaults to 1750 when unset (`SDK:game/server/vscript_server_placement.cpp:1119-1146`).
  - `character_alter` appears only in an easter-egg list (`P:mp/_staging_area_ee.gnut:1101`).
  - Equippable: probably yes [src-sdk]; runtime [unknown].
  - `sh_alter.gnut` is cosmetic (kill animation modifier).
- **Trigger.**
  - `fire_mode offhand`, `object_placement_run_mode offhandHold`, `object_placement_special 1`, `object_placement_distance_max 1750` (`PW:mp_ability_phase_door.txt:44-75`).
  - Hold `+offhand1` (placement preview), release to place. Placement fails without a valid spot (`P:weapons/mp_ability_phase_door.nut:627-641`).
  - Charges: clip 50, 25 per use, regen 1/s (`.txt:76-86`).
- **Tuning** (playlist-overridable, `:114-131, 308-342`):
  - wall thickness max 30 m;
  - portal life 15 s;
  - **plant delay 0.7 s**;
  - re-enter debounce 1.35 s;
  - **exit velocity min 50 / max 300**;
  - post-portal phase shift 1.0 s with weapons taken;
  - extension (rope) travel 400 u/s.
- **Teleport** (`:1291-1489`, server only, not predicted):
  - Instant `TeleportPlayerNoInterp` + `PutPlayerInSafeSpot` (`:1435-1436`).
  - Exit position = portal centre + outDir × 10, minus 32 z for a wall portal. Ceiling/floor-down portals use 82 (`:1403-1406`).
  - **Exit velocity = outDir × clamp(v·outDir, 50, 300)** (`:1476-1479`).
  - A floor or ceiling portal forces outDir to ±Z (`:1408-1413`).
  - Travel via the vertical "portal extension" keeps only vz (`:1438-1444`).
- **Telemetry:** dedi MOVE-TRACE (velocity before and after), the server script printf `ALTER: Teleporting … from … to …` (`:1433`), `IsPhaseShifted()`.
- **Experiment AL1** (lane A, M3 rock wall; it must have open ground behind it: check the thickness with `measure`):

  ```
  "m6_alter_sprint": "wait 72; down speed; down forward; down offhand1; wait 0.4s; up offhand1; wait 3.0s; up forward; up speed; wait 2.0s"
  ```

  Pitch 0, starting 600 u from the face so the placement happens before contact. Variants: walk (no `speed`); standing still with `down forward` starting after 1.0 s from 150 u; slide-jump approach (350); stim approach on Octane is a separate legend, so skip it.
  - Prediction: exit speed = min(max(v·n, 50), 300) along the far-side normal, with 1 s of phase.
  - **Value:** high for HSD ("speed through a portal" is a design question). Cost: one session if the wall is thin enough.

### Loba, Translocation (`mp_ability_translocation`, tactical)

- **Presence:** equipped and used in M4 (`m4/p3_transitions/P3-TRANSITIONS.md`).
- **Throw.** Toss weapon, pull-out 0.6 s. Launch 1815 u/s (1390 above 50° pitch), staged gravity scales 0.5975 → 0.48 → 0.68, inherits owner velocity, hull ±3, fuse/timeout 5.7 s (`PW:mp_ability_translocation.txt:9-68`).
- **Second press (early drop).**
  - `fire_to_redirect_projectile_mid_flight 1` (`.txt:71`). The weapon callback is **disabled on the dedi** (`.txt:114`).
  - Instead the server toss thread polls `owner.IsInputCommandPressed( IN_ATTACK ) || …( IN_OFFHAND1 )` and calls the redirect itself (`P:abilities/loba_tactical_translocation.nut:716-724`).
  - This works because the SDK latches those press bits ("drop-click latch", `SDK:game/server/translocation.cpp:61-66, 604-612, 1405-1441`).
  - The drop is allowed only ≥ `loba_tactical_drop_minimum_time` **0.24 s** after projectile creation, and only once (`nut:468-487`).
  - It re-throws straight down (`attackParams.dir = <0,0,-1>`, drop velocity 1650, `.txt:58`).
- **Destination validation.**
  - Candidates: the plant point + up to 2 backup points along the throw path (`nut:966-971, 1155-…`).
  - `IsLandingPositionValid`: there must be ground within 1000 u below; no slip/OOB trigger at the hull; no kill trigger between (`nut:754-836`).
  - Then `CanPutPlayerInSafeSpot` again after the delay (`nut:1061-1075`).
  - Pre-teleport delay 0.4 s (`nut:1010`). The teleport aborts if the player enters a disallowed state.
- **Teleport.** Stops any zipline. Angles face the travel direction, **velocity = 0**, `TeleportPlayerNoInterp` (`nut:1095-1105`). On failure the original angles and velocity are restored (`nut:1108-1115`).
- **Failure and refund.** If the teleport never succeeds (no valid spot, timeout, destroyed projectile), one charge (25 of 50) is refunded and the next attack time is reset (`nut:595-607`). Timeout = fuse 5.7 s (+2 s once planted) (`nut:672, 711-713`).
- **Experiment LO1** (fixes the M4 "lands off the field" problem):

  ```
  "m6_loba_drop_t07": "wait 72; tap offhand1; wait 0.7s; tap offhand1; wait 3.0s"
  ```

  Also t = 0.9, 1.2, 1.5 s, on lane P3 (start x −14900, y 6650, pitch −15), plus standing vs sprinting.
  - Measure: landing distance vs drop time; velocity after = 0 (confirm); pre-teleport delay 0.4 s (MOVE-TRACE origin jump time − plant time).
  - Refund check: throw toward the map void (yaw away from the field, pitch −30 at the field edge) and read the clip in the reset line (add `tac_clip=` to the RESET string).
  - **Value:** low to medium (velocity zeroing is already known). Cost: low.

### Ash, Phase Breach (`mp_weapon_phase_breach`, **ultimate**)

- **Presence.** Present and registered (`P:scripts.rson:880`). It is logged as `ABILITY_TYPE.ULTIMATE` (`nut:331`), and the S21 Ash ult is Phase Breach.
  - `fire_mode offhandHybrid`, clip 150 per use, regen 1/s after a 1 s delay (`PW:mp_weapon_phase_breach.txt:9, 45-53`). So the trigger is **`+offhand4`**.
  - The community says S21 Ash has no dash. `mp_ability_ash_dash.nut` exists but is a later feature [community].
- **Targeting.**
  - Max 2D distance 75 m = 2953 u (100 m upgraded), full distance only within 45° of view, minimum 200 u from the player.
  - Movers are allowed at start and end if they move slower than 12 u/s, never out of bounds.
  - The end must pass `PhaseTunnel_IsPortalExitPointValid` (`nut:36-64, 202-215, 1588-1636`).
  - The path is straight steps from start to end (`GenerateBreachPathInfo`).
- **Travel.**
  - Speed 1200 u/s. Path time = clamp(distance/1200, **0.3, 1.8**) s, 1.4 upgraded (`nut:36-47, 355`; `P:weapons/mp_weapon_phase_tunnel.nut:2183-2184`).
  - The player is phase-shifted, **prediction disabled**, **controls frozen on the server** (`mp_weapon_phase_tunnel.nut:1576-1577`), and moved by a mover with `NonPhysicsMoveTo`. The velocity is set to each node's velocity (`:1520-1522`).
  - The breach path nodes are built without a velocity (`nut:341-352` sets origin and angles only). So the node velocity is the zero vector and the **exit velocity is ≈ 0** [src-script inference, verify].
  - Revert: prediction on, controls unfrozen immediately (`controlRestoreDelay` defaults to 0), weapons back after 0.4 s (`nut:408-409`; tunnel `:1636-1653`). The portal stays 15 s.
- **Telemetry.** The client trace is not physics truth (prediction off). Use a **server per-tick logger** (origin, velocity, `IsPhaseShifted()`) or dedi MOVE-TRACE, which may not run while the player is parented to the mover [unknown].
- **Experiment AS1:**

  ```
  "m6_ash_breach": "wait 72; tap offhand4; wait 3.0s"
  ```

  Also a hold variant: `down offhand4; wait 0.5s; up offhand4`. Aim along lane P3 at pitch +5 so the target is ground at 600/1200/2400 u.
  - Measure: travel time vs distance (expect clamp(d/1200, 0.3, 1.8)), exit velocity (expect 0), control return time.
  - **Value:** low (exit velocity likely 0, which is already the M4 design reading). Cost: low once Ash is confirmed.

### Valkyrie, VTOL jets (`mp_ability_valk_jets`, passive equipment)

- **Presence:** equipped in M4 (`m4/valk_rev/VALK-REV-PRIMITIVES.md`).
  - `PAS_VALK` → equipment in OFFHAND_EQUIPMENT.
  - `SetGlideMeter(glideDuration)` when the passive is gained (`P:weapons/mp_ability_valk_jets.nut:689-712`). M4 measured 8.0.
- **Activation:**
  - jets on/off via `SetActivateJetpack` (`:606-611, 676-684`);
  - reactivation delay **0.25 s** (`:27, 562`);
  - refused while healing or during a tactical burst (`:554-559`);
  - native `CanUseJetpack(vel)`, which returns `JETPACK_ENGAGE_FAILED_OUT_OF_FUEL` when the meter is empty (`:565-572`).
  - `.txt`: `offhand_deactivate_on_jump_toggle_or_release 1`, `offhand_holds_on_tactical 1` (`PW:mp_ability_valk_jets.txt:15-16`). Hold `+jump` in the air (M4).
- **Fuel model.** Native meter shared with glide and hover, `m_glideMeter`. The dedi uses an SDK twin of the S21 flight model, `bridge_jetpack 1` (`SDK:game/server/jetpack.cpp:1-5, 136-144`). The settings keys it reads (`:191-223`):

  ```
  jetpackThrust, jetpackHorizontalMoveThrust, jetpackAfterburnerThrust
  jetpackThrustScaleOnActivation, jetpackThrustScaleTimeOnActivation
  jetpackVerticalVelocityScaleOnActivation/Deactivation
  jetpackTightnessUp/Down/Sideways/ForwardBack
  jetpackStrafe(+TaperStart/Finish), jetpackPitchMovement
  jetpackMeterRate (drain), jetpackMeterOnActivation (startup cost), jetpackTacticalMeterRate
  jetpackPostEffectTime/Gravity/Drag
  glideDuration, glideRechargeOnlyInGroundedState, glideRechargeOnlyWhenFeetOnGround
  jetpackJumpsToActivate, boostRepeatedBoostsAreShort
  ```

  - Holding the tactical in the alt hand drains at `jetpackTacticalMeterRate` (`:745-767`).
  - Jets stop on death, on a move parent, on hover, or when a grapple attaches (`:413-420`).
  - The refill helper tops up the meter **only on the ground** (`P:weapons/_weapon_utility.nut` around 3860).
- **Upgrades:** `PAS_BOOSTED_JETPACK` → mod `valk_jetpack_manuverability`; `PAS_EXTRA_JETPACK_FUEL` → mod `valk_jetpack_increased_duration` (`P:weapons/mp_ability_valk_jets_upgraded.nut:1-40`).
- **Why M4 saw no drain:** the holds were 2 s against an 8 s meter. The drain rate and activation cost were never in the census.
- **Telemetry:**
  - census of the keys above (E-A);
  - `[JETPACK] start … meter a -> b` and `stop` lines with `bridge_jetpack_diag N` (DEVELOPMENTONLY; `jetpack.cpp:142-143, 397, 710`);
  - `GetGlideMeter()` per frame (server; verify on the client).
- **Experiment VK1:**

  ```
  "m6_valk_hold10": "wait 72; tap jump; waitair; wait 0.2s; down jump; wait 10.0s; up jump; waitland; wait 6.0s"
  "m6_valk_pulse":  "wait 72; tap jump; waitair; wait 0.2s; down jump; wait 0.3s; up jump; wait 0.35s; down jump; wait 0.3s; up jump; wait 0.35s; down jump; wait 0.3s; up jump; wait 0.35s; down jump; wait 0.3s; up jump; waitland; wait 3.0s"
  ```

  Add a server logger of `GetGlideMeter()` at 10 Hz.
  - Measure: drain rate (slope while held), activation cost (step at each start in the pulse run), the time at which the meter runs out, and ground recharge (slope after landing; air recharge blocked?).
  - Repeat with `GivePassive(p, ePassives.PAS_EXTRA_JETPACK_FUEL)` and a census.
  - **Value:** high for completing the M4 Jetpack primitive. Cost: low.

### Grapple extras

- **Release inputs** [src-script + src-native-boundary]:
  - Jump releases (M4 data).
  - A second `+offhand1` while grappling: `OnWeaponAttemptOffhandSwitch` sees suit grapple power < 100 and calls `Grapple(<0,0,1>)` (`P:weapons/mp_ability_grapple.nut:140-161`). This is probably the native release/retract request [inference].
  - The server forced detach is `player.Grapple( <0,0,0> )`, used on bleedout (`:453-459`). That is a **deterministic release for experiments** from server EVAL.
  - Native struct fields: `m_grappleRetracting`, `m_grappleForcedRetracting`, `m_grappleSwingDetachLowSpeed`, `m_grappleSwingHoldTime` (`SDK:game/shared/r1/grapple.h:6-31`, dt schema `SDK:game/shared/s21_dt_schema.h:3202-3214`).
- **Players and NPCs.**
  - Auto-aim can bend the direction toward a target (`GrappleAutoAim_FindTarget`, native; `nut:107-125`). The struct carries `m_grappleAutoAimTarget` and `m_grappleMeleeTarget` (grapple-to-melee is native).
  - An enemy player hit only adds an assist (`nut:520-524`).
  - The NPC flinch/damage callback is commented out (`nut:54-57`). `CodeCallback_GrappleDetachFromNPC` detaches from a prowler above 400 u/s (`nut:409-421`).
- **Moving entities and deployables.** Per-entity callbacks `AddEntityCallback_OnGrappled` (used only by grapple-switch levers, `P:_script_movers.gnut:474, 875-895`). The hit entity and normal arrive in `CodeCallback_OnGrappleAttach(player, hitent, hitpos, normal)` (`nut:201-263`). Behaviour on movers is native [unknown].
- **Interactions:**
  - jets stop (`SDK:game/server/jetpack.cpp:419-420`) and glide stops (`SDK:game/server/glide.cpp:494`) when the grapple attaches;
  - a grapple detach ends mantle-boost state 4 (`SDK:game/server/mantle_boost.cpp:818-831`);
  - a jump pad launches grappled players (`SDK:game/server/jumppad_parity.cpp:96-99`: S3 launched only "on ground or grappled", and the SDK lifts the ground gate);
  - lift and Trident entry are refused while grappled;
  - the zipline handoff (A3).

| ID | Schedule | Measures |
|---|---|---|
| G1 second-press release | `m55_nomod_hold` start; `wait 72; tap offhand1; wait 0.6s; tap offhand1; wait 3.0s` (also 0.3 / 1.0 s) | release yes/no, release velocity vs the jump release (`m4_grapple_jump`) |
| G2 server release | reset prefix `m6_grel` starts a server thread `wait 0.6; p.Grapple( <0,0,0> )` | forced-detach velocity (control for G1) |
| G3 grapple → zipline | Z1 rope crossing lane A at 150 u height, 400 u ahead, aim pitch so the ray hits the rope: `wait 72; tap offhand1; wait 3.0s` | `[HSD-STATE] zip=1` after a grapple? `[ZIPRAIL-USE] grapple=1` on the client (`bridge_zip_disc_diag 1`) |
| G4 grapple + pad | pad (`JumpPad_CreateAtLocation`) under the pull path | launch while attached |
| G5 dummy target | `Agent_SpawnDummy` 600 u ahead, aim 10° off it | auto-aim bend, pull toward a player-sized target |

- **Cost/value.** G1/G2 are cheap and fill the "release" gap in the M5.5 grapple. G3 is novel but uncertain. G4/G5 are low priority.

---

## 7. Cross-cutting cheap step: E-A census (no trials)

Run this once per legend: Gibraltar, Pathfinder, Valkyrie (with and without `PAS_EXTRA_JETPACK_FUEL`) and Alter. On the **client** console:

```
bridge_classvar_get ziplineSpeed / ziplineDetachSpeed / ziplineMaxVerticalDetachSpeed / ziplinePreventManualDetach / ziplineViewOffset
bridge_classvar_get ziprailAcceleration / ziprailDetachSpeed / ziprailMountReverseDistance / pathGravityAcceleration / maxSpeedMultiplier / minSpeedFraction / maxJumpOffSpeed / minJumpOffSpeed / viewInfluenceOnJumpDirection / detachDirMaxDownAngle / detachDirMaxUpAngle
bridge_classvar_get jetpackEnabled / jetpackThrust / jetpackMeterRate / jetpackMeterOnActivation / jetpackTacticalMeterRate / jetpackThrustScaleOnActivation / jetpackThrustScaleTimeOnActivation / jetpackPostEffectTime / jetpackPostEffectGravity / jetpackPostEffectDrag / jetpackTightnessUp / jetpackTightnessDown / jetpackTightnessSideways / jetpackTightnessForwardBack / glideDuration / glideEnabled / hoverEnabled / glideRechargeOnlyInGroundedState / glideRechargeOnlyWhenFeetOnGround
bridge_classvar_get verticalGainCutoff_wallrun / wallrunAllowedWallDistance / wallrunAllowedWallDistanceWallHang / wallrunCeilingLimit / wallrunSameWallHeight / wallrunSameWallAllowed / wallstickEnabled / wallrunUpWallBoost / wallrunDuckCausesFallOff
```

(One key per command. The slashes only list the keys.)

Then cvars, on **both** consoles:

- `find jump_grace` (client `jump_grace_cutoff_speed`, `jump_graceperiod`);
- `find zipline_cooldown`;
- `find mantle_boost`;
- `bridge_lurch_cutoff_speed`.

Append the keys to `hsd_e0_classvars.cfg` (or a new `hsd_m6_classvars.cfg`, copied to `<game root>/platform/cfg/user/`).

- **Cost:** minutes. **Value:** it answers the Valkyrie fuel drain and startup cost, the zipline speeds and exit clamps, and the client lurch cutoff before any trial is designed in detail.

---

## 8. Recommended order

| # | Experiment | Why | Cost | Runner changes |
|---|---|---|---|---|
| 1 | **E-A census** (§7) | Several open numbers become readable (Valkyrie fuel, zipline speeds, jump grace) | very low | cfg file only |
| 2 | **E-Z ziplines Z0–Z5** | Core traversal, no data at all; Super Jump decision | medium | `use` key, rope spawn geometry, `m6_zip` reset prefix |
| 3 | **E-L lurch L1–L5, L8** | Completes the Unity lurch model (stacking, wheel, back cut-off, post-boost) | low | `wheel` verb |
| 4 | **VK1 Valkyrie fuel** | Closes the M4 Jetpack gap | low | server meter logger |
| 5 | **AL1 Alter exit speed** | HSD design question (speed through portals); cheap if Alter is in the catalogue | low to medium | Alter in catalogue; wall thickness check |
| 6 | **E-C climb heights, hang, hop, C5 FSM-off** | Ledge reference, hang semantics, legacy superglide under native code | medium | geometry heights, `[HSD-STATE]` logger, cvar toggle both sides |
| 7 | **G1/G2 grapple release**, G3 grapple → zipline | Fills the M5.5 grapple gaps | low | – |
| 8 | **LO1 Loba drop**, **AS1 Ash breach** | Confirm "velocity zeroed / exit ≈ 0"; low new information | low | server logger for breach |
| 9 | **E-S slopes and ceilings** | Ramps in HSD levels; needs rotated-prop validation | medium | vertical measure mode |
| 10 | L6/L7/L9 lurch edge cases | Only after E-C geometry; L9 has a correction artefact risk | medium to high | – |

## 9. Unknowns that stay open after this audit

- **Native, no source:**
  - plain-rope jump-off and crouch-off velocity laws;
  - zipline mount angle tolerance;
  - zipline ride acceleration;
  - slide-on-slope law and ceiling bonk;
  - grapple pull/swing law (M4 fits exist);
  - client lurch cutoff value;
  - `jump_graceperiod` value.
- **Runtime:**
  - whether Alter and Ash are in `GetAllCharacters()`;
  - whether the survival IN_USE_LONG air-grab callback is registered in our playlist;
  - whether `GetGlideMeter` exists on the client VM;
  - whether the catalogue slab models load on this map.
- **Inference only:**
  - the Ash breach exit velocity is 0 (nodes have no velocity);
  - the second tactical press releases the grapple;
  - each new direction press edge lurches again;
  - native `Jump` calls (wall jump, forced mantle exit, zip jump-off) re-anchor the lurch window.
