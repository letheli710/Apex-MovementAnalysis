# Experiment-Plan — Local Windows Experiments, Measurements and Acceptance Criteria

> Everything here runs on a **local Windows R5Flowstate install against a self-hosted, offline dedi**. No retail client, no online server, no anti-cheat interaction.
> **None of these experiments has been run yet.** They are designed from the static analysis in [Movement-Analysis.md](Movement-Analysis.md).

## 1. Setup

### 1.1 Install and processes

1. Install the R5Flowstate launcher and put the game content in a separate folder (`launcher/README.md:1-12`).
2. Two processes are involved: the **S21 client** (`r5apex.exe` + `client.dll`) and an **S3 dedi** (`r5apex_ds.exe` + `server.dll`) (`s21-r5sdk/README.md:6-11`). For a controlled local dedi, use `r5f-host`:
   - `r5f-host install --path D:\R5FServer`
   - `r5f-host instance add lab --playlist <playlist> --map <map> --extra "-devsdk"`
   - `r5f-host run lab` (`launcher/docs/HOST_TOOL.md`)
   - Connect with `connect 127.0.0.1:37015` (`s21-r5sdk/README.md`, "Spire" section).
   - Keep the instance **hidden/offline** (`r5f-host instance set lab --visibility hidden`).
3. Start the client with `-devsdk` as well. That exposes the `*_trace/_diag/_log` ConVars and writes per-run logs to `platform/logs/<client|server>/<GUID>/` (`s21-r5sdk/AGENTS.md:175-180,301-310`).
4. Copy `research/phase1/mod/hsd_movediag/` to `<game>/mods/hsd_movediag/` on the **client install and the dedi install** (both VMs need the script).

### 1.2 Map and playlist

- **Movement Recorder** (`fs_movement_recorder`, map `mp_rr_canyonlands_hu`, `s21-platform/playlists_r5_patch.txt:5767-5794`): free roam, plus `mrec` record/replay of your own input on bots. This is the best default.
- For each experiment, pick a fixed spot and write it down: flat ground ≥ 60 m, a straight wall ≥ 4 m high, a mantle-height ledge (about 1.2–1.8 m), and a 15–30° slope. Record `GetOrigin` of the start point (`hsd_md_mark start`).
- Parameter A/B tests without touching files: surf maps read playlist vars `movement_<key>` (`s21-platform/scripts/vscripts/sh_surf_movement.gnut:4,109`), and `r5f-host` can set them with `--override movement_airAcceleration=…`. Elsewhere, use `set` (cheat) / `setall`, or a script with `Player_SetClassVar` + `SetLocalClassVar`.

### 1.3 Console recipes (AGENTS.md style: one line per engine, `;` without spaces)

```
DEDI:   sv_cheats 1;bridge_move_trace 1;bridge_classvar_log 1;hsd_md_sv_trace 0
CLIENT: bridge_move_trace 1;bridge_move_trace_replays 1;bridge_classvar_log_cl 1;hsd_md_cl_trace 0;fps_max 144
```

`bridge_move_trace` **must match** on both sides for joinable logs (`s21-r5sdk/src/game/server/move_sim_trace.cpp:42-45`). Use `2` instead of `1` for long runs (edges plus heartbeat).

### 1.4 Data capture and processing

| Data | Source | Rate |
|---|---|---|
| per-command pre/post origin, velocity, ground, slide, sprint, duck, buttons, forward/side move, maxspeed, movescale | `[MOVE-TRACE]` (both engines, joinable on `cmd=`) | one line per usercmd |
| movement events (JUMP, TOUCH_GROUND, BEGIN_SLIDE, MANTLE, …) | `[HSD-MD] side=sv kind=evt` | event |
| takeoff/landing summaries (airtime, takeoff/peak/landing speed, hop chain) | `[HSD-MD] side=cl kind=takeoff/land` | edge |
| live parameter values | `hsd_md_dump` → `[HSD-MD] kind=setting` + `scriptdump_hsd_movediag_settings.csv`; `bridge_classvar_get <key>` | on demand |
| trial labels | `hsd_md_mark <label>` | on demand |
| frame time | `fps_max`; optionally CapFrameX / PresentMon (external) | per frame |
| video (optional) | OBS at a fixed 60 fps, for qualitative review only | — |

Processing:

```
python research/phase1/tools/hsd_movelog.py trace  <client.log> -o cl_trace.csv
python research/phase1/tools/hsd_movelog.py trace  <server.log> -o sv_trace.csv
python research/phase1/tools/hsd_movelog.py air    <client.log> -o cl_air.csv
python research/phase1/tools/hsd_movelog.py hsd    <client.log> -o cl_hsd.csv
```

Derived columns: `spd2d_pre/post`, `dspd2d`, `dheading_deg`, `dt_est`, `pressed_names`, `dir_press_air`. Per-airtime summaries: `takeoff_spd`, `peak_spd`, `land_spd`, `gain`, `dir_presses`, `max_abs_dheading`.

**Known limitation.** `MOVE-TRACE` has **no frametime and no view yaw**. `dt_est` is displacement over mean speed, so it is reliable only above about 50 u/s, and collisions corrupt it. Wish-direction-vs-velocity angles therefore cannot be computed exactly. Phase 2 fix: add `ft=` and `yaw=` to the trace (an SDK build; see Findings-and-Gaps).

### 1.5 General protocol

- At least **10 trials per condition**. Discard trials that collide with geometry (detected by `|po - (o + v·dt)|` jumps or by `hsd_md_mark bad`).
- Fix the frame rate (`fps_max 144`) unless the frame rate is the variable under test.
- Before each A/B, reset parameters (Movement Lab "Reset All" or a respawn, given sticky class vars) and re-dump with `hsd_md_dump`.
- Record the build: SDK DLL version strings from the boot log and the platform commit.

## 2. Experiments

### E0 — Parameter census (prerequisite for everything)

- **Goal.** Get the retail S21 setfile values the client actually uses, and compare them with what the dedi reads.
- **Method.**
  1. As the default legend, run `hsd_md_dump` (server values through `GetPlayerSettingFloat`).
  2. Run `bridge_classvar_get <key>` for the same keys on the client.
  3. Open the Movement Lab and screenshot or export the full field list. "Save" stores only modified fields, so set a no-op edit per field, or copy the table manually.
  4. Repeat for 2–3 legends and for crouch vs. stand (the stance table differs).
- **Record.** key, server value, client value, stance, legend.
- **Accept when:** ≥ 90% of the 58 keys in the mod's list resolve on at least one side; every key that differs between client and server is listed (each one is a prediction-error candidate); the CSV is committed.

### E1 — Ground acceleration, deceleration, friction

- **Goal.** Identify the ground model (linear vs. Source-style), the sprint ramp, and the stop curve.
- **Method.**
  1. From standstill, hold W (walk), then W+sprint, for 3 s; release and coast to a stop.
  2. Repeat crouched and with side/back input (`speedScaleSide/Back`).
  3. A/B: double `acceleration` and `deceleration` (both engines).
- **Record.** Per command: `spd2d_post`, `ground`, `maxspeed`, `movescale`, `fwd`, `sd`, `buttons`.
- **Analysis.**
  - Fit `dv/dt` against `v` for the accel and decel phases.
  - Test the candidate models: constant accel (`dv = a·dt`), Source (`dv = min(accel·wishspeed·dt, wishspeed − v·ŵ)`), and exponential friction (`v' = v·max(0, 1 − k·dt)`).
- **Accept when:** one model fits with R² ≥ 0.98 per phase; the fitted constants scale as expected (±5%) when `acceleration`/`deceleration` are doubled; top speeds equal `maxspeed`·movescale ±1%.

### E2 — Air acceleration and air strafing

- **Goal.** Verify `AirAccelerate(wishDir, wishSpeed = airSpeed, accel = airAcceleration, dt)` with `accelspeed = airAcceleration·dt` (inference §3 in Movement-Analysis).
- **Method.**
  1. Jump from a known speed (about 300 u/s).
  2. Hold A or D only, with a constant mouse turn rate. Use a bot with `BotCmd_SetLook` + `BotCmd_SetMove` for exact inputs: bots run only the dedi, so this measures S3 native air code.
  3. Repeat as a human for S21 client prediction.
  4. Vary the turn rate (0–720°/s) and `airAcceleration` (×0.5, ×2) / `airSpeed`.
- **Record.** `dspd2d` and `dheading_deg` per airborne command; `dt_est`.
- **Analysis.**
  - The Source model predicts `Δv_parallel = clamp(airSpeed − v·ŵ, 0, airAcceleration·dt)`, a speed gain only when the wish direction is nearly perpendicular to velocity, and a maximum gain that depends on the turn rate.
  - Fit the per-command `dspd2d` against the predicted value.
- **Accept when:** the model explains per-command `dspd2d` with median absolute error ≤ 0.5 u/s; changing `airAcceleration` changes the maximum gain proportionally (±10%); client and dedi traces agree within prediction tolerance (no recurring `rp=1` corrections).

### E3 — Tap strafe (lurch)

- **Goal.** Measure how a fresh direction press redirects velocity in the air, as a function of time since the jump, speed, and the S21/S3 split.
- **Method.**
  1. Jump at 300, 600, 900, 1200 and 1500 u/s. To get high speeds, use a temporary `slideSpeedBoost` or `player.SetVelocity` via script on a test map.
  2. Tap W (or A/D) 1–5 times at fixed delays after takeoff (bind with `+forward;wait` macros, or `BotCmd_PressButtons` for the server-only reference).
  3. A/B: `bridge_lurch_cutoff_speed 0` vs 1100 on the dedi, with `bridge_tapstrafe_debug 1`.
- **Record.** Per command: `pressed_names`, `dir_press_air`, `dheading_deg`, `dspd2d`; time since the JUMP event; whether the client predicted a turn that the dedi then corrected (`rp=1` lines following).
- **Analysis.**
  - Heading change and speed loss per press, plotted against time-since-jump and speed.
  - Find the grace window length (where the effect drops to 0).
  - Check whether the dedi lurches at all (this resolves the `tapstrafe.cpp` vs `init_server.cpp:664` contradiction).
- **Accept when:** the window length is measured to ±1 command at 144 fps; the effect vanishes above the cutoff on both sides (or the mismatch is documented); the dedi-native behaviour (a bot with the cutoff at 0) is classified as "lurch present / absent" with ≥ 10 trials.

### E4 — Bunny hop, landing window, momentum

- **Goal.** Measure speed retention per hop as a function of the jump timing after landing.
- **Method.**
  1. Chain jumps at about 600 u/s on flat ground, pressing jump 0, 1, 2, 4 and 8 frames after `TOUCH_GROUND`.
  2. Control: `sv_autobunnyhopping 1` (forces a first-ground-command jump).
  3. A/B: `skip_speed_reduce 0` vs 100; `landSlowdownDuration` 0 vs default; drop heights 0 / 2 / 6 m for hard-landing slowdown.
- **Record.** `[HSD-MD] kind=land/takeoff` (`groundtime`, `gain`, `hop`); trace `ge` edges and `dspd2d` on the ground commands; server `JUMP`/`TOUCH_GROUND` times.
- **Analysis.**
  - Speed loss per hop against ground time.
  - Identify `skip_time` (the step where the loss changes by `skip_speed_reduce`).
  - Confirm that friction is skipped on a first-command jump (the autobhop comment, Movement-Analysis §4.2).
  - Measure the jump height after a quick re-jump to confirm `antiMultiJumpHeightFrac`.
- **Accept when:** the loss-vs-ground-time curve is reproducible (CV ≤ 5%); `skip_time` is bracketed within ±1 command; the 0-frame jump shows zero friction loss within ±1 u/s.

### E5 — Slide, slide boost, slide jump

- **Goal.** Measure the slide entry threshold, the boost and its cap/cooldown, the decay, and the slide-jump refund rule.
- **Method.**
  1. Sprint at fixed speeds (from E1), then crouch. Vary the speed around `slideRequiredStartSpeed`.
  2. Slide on flat ground, then on a 15° and a 30° slope, both up and down.
  3. Slide-jump at 0.1/0.2/0.3/0.5/0.8 s after slide start; repeat slides at intervals shorter than the cooldown.
  4. Turn on `bridge_slide_super_jump_trace 1` and, if the class mod exists, give `boosted_slide_jump`.
- **Record.** Trace `slide` edges, `spd2d`, `dspd2d`; events `BEGIN_SLIDE`/`END_SLIDE`/`JUMP`.
- **Analysis.**
  - Boost gain and cap.
  - Decay model (`slideVelocityDecay`, `slideDecel`).
  - Refund window: does a jump within 0.4 s lose exactly `m_lastSlideBoost`? (Movement-Analysis §4.3)
  - SSJ impulse = √(2·750·150) ≈ 474 u/s.
- **Accept when:** boost and refund are explained within ±2 u/s; the refund boundary is located within ±1 command of 0.4 s; the slope dependence is quantified for 3 angles.

### E6 — Wall jump ("wall bounce") and climb

- **Goal.** Measure the `JumpOutOfWallRun` output velocity against approach angle, input direction and climb state.
- **Method.**
  1. Run into the test wall at 0°, 30° and 60° incidence, then jump while climbing at heights 0.5/1.5/2.5 m.
  2. Vary the input direction (away from the wall, along it, none).
  3. A/B `wallrunJumpOutwardSpeed` / `wallrunJumpUpSpeed` / `wallrunJumpInputDirSpeed` (both sides).
  4. Control: `bridge_wallclimb_tap 1` on the dedi.
- **Record.** Velocity before and after the jump command (trace), wall normal (`[WALLCLIMB]` tap), climb duration.
- **Analysis.** Decompose the output velocity into wall-normal, up and input components. Fit `out = n·outward + up·upSpeed + input·inputDirSpeed (+ kept tangential?)`.
- **Accept when:** the decomposition is stable within ±3 u/s; each parameter changes its own component as expected (±5%).

### E7 — Mantle, superglide, frame-rate dependence

- **Goal.** Decide whether a classic superglide (jump, then crouch within about one frame at the mantle end) exists natively, and characterise the SDK mantle-boost FSM.
- **Method.**
  1. Mantle the test ledge at `fps_max` 60, 144 and 240.
  2. Classic input: jump then crouch at offsets of 0/1/2/3 frames, using macros or a bot program.
  3. Mantle-boost input: jump inside the sweet spot.
  4. A/B: `mantle_boost_enabled 0` vs 1 (both sides).
  5. Turn on `bridge_mantle_boost_trig_log 1` and `bridge_mantle_boost_apply_log 1`.
- **Record.** `[MB-TRIG]` (travState, raw/anim fraction, delta, gate, state), `[MB-APPLY]` (state, speed, velocity), trace origin/velocity around the traversal end, `MANTLE` event time.
- **Analysis.**
  - Exit speed distribution by input offset and fps.
  - Success rate per frame window.
  - Compare against the FSM thresholds (1.5°, frac > 0.5, exit × 1.3, vz = √(2·750·90) ≈ 367 u/s).
- **Accept when:** a boosted vs. normal exit is classified with ≥ 95% agreement against the logs; the success window is measured in ms and in frames for each fps; there is a yes/no answer, with data, on whether the classic input does anything when `mantle_boost_enabled 0`.

### E8 — Client/server parity (cross-cutting)

- **Goal.** Quantify how far S21 prediction and the S3 dedi diverge, per mechanic. This decides which observations reflect "S21 feel" and which reflect the S3 dedi.
- **Method.**
  1. With `bridge_move_trace 1` and `bridge_move_trace_replays 1`, run E1–E7 inputs as a human.
  2. Join client and dedi lines on `cmd=` and compare post-move origin and velocity.
  3. Replay one recorded run on a bot (`mrec` / `CmdRec_Start` → `BotCmd_PlayRecording`) to get dedi-only ground truth.
- **Accept when:** per-mechanic error statistics are reported (median and p95 of `|Δpv|`, count of `rp=1` corrections per 100 commands). Any mechanic with p95 > 5 u/s is flagged as "not representative of a single engine".

## 3. Prioritisation

| Order | Experiment | Why first |
|---|---|---|
| 1 | E0 + E1 + E2 | They provide the numbers and the model structure the Unity controller needs first. They are cheap and need no special geometry |
| 2 | E4 + E5 | Momentum preservation (bhop and slide chain) is the core of the Apex "speed feel" |
| 3 | E3 | Tap strafe is highly distinctive and touches the open S3/S21 contradiction |
| 4 | E7, E6 | Niche and frame-dependent; useful for design decisions, not for the baseline |
| always | E8 | Runs alongside the others; it tells us how far to trust every number |
