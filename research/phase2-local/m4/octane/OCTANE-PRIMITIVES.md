# M4 Octane: movement primitives (stim, jump pad, landing slowdown)

Status: offline analysis of two sessions. Nothing was launched, and no existing file was changed. Everything is
in this folder:

```
python octane_analysis.py <session> [<session> ...] [--json results.json] [--params params.json]
python octane_analysis.py ../../data/20261021_002526_M4_octane ../../data/20261021_003657_M4_octane_rerun \
    --json results.json --params params.json > analysis_output.txt
```

- `octane_analysis.py` computes every number in this file. It reuses the M2 loader and frame join
  (`../../m2/air_jump/aj_load.py`) and the M3 AirAccelerate and lurch functions (`../../m3/lurch/lurch_analysis.py`)
  without changes.
- `analysis_output.txt` is its printed output, `results.json` holds the per-trial rows, and `params.json` lists
  the parameters with value, unit, source, n and spread. The script writes `params.json`.

Evidence labels:
- **[obs]** read directly from the logs;
- **[fit]** fitted, with residuals given;
- **[inf]** an interpretation that the data is consistent with but does not prove;
- **[src]** taken from script or SDK source (paths as in `../ABILITY-TRIGGERS.md`).

Units are Source units (u, u/s). msc = `m_cachedMoveScale`, which is 1.15 empty-handed (M2).

## TL;DR

| Mechanic | Primitive | Model (engine units, per usercmd) |
|---|---|---|
| Stim | **speed multiplier** plus a sprint settings mod | msc = 1.15·(1 + 2·0.14902·g(t)). g = 1 for 6.0 s, then a 0.5 s cosine fade to 0. The boost starts 0.16 s after the tap. For the first 6.0 s, sprintspeed is 282 (instead of 260) and sprintAcceleration is 120 (instead of 100). Every cap and acceleration that scales with msc in M2 scales here too; deceleration does not. |
| Jump pad | **instant impulse** that **replaces** velocity, then a **slow-mo flight** | v = 1150·normalize(ĥ + V·up), with V = 2.0, or 1.0 when ducked. The approach speed is discarded. Until landing, the movement runs on dt·0.8. |
| Hard landing | **speed multiplier with recovery** | On the landing command, v_h ·= f0, where f0 = clamp(1.99647 − 1.6714e-6·vz², 0, 1). After that, msc ·= f0 + (1 − f0)·(t/1.0)² until t = 1 s. |
| (bonus) Lurch | M3 clamp resolved | The clamp is **0.7 × the current sprint cap**: 294.67 with stim, 209.3 without. |

## 1. Data and method

| Session | Trials used (ok, not warmup) | Schedules |
|---|---|---|
| M4_octane (with census) | 30 | ctrl_sprint 5, stim_sprint 5, stim_walk 4, stim_air 4, pad_sprint 5, pad_crouch 5, pad_jumpin 2 |
| M4_octane_rerun | 15 | stim_walk 1, stim_air 1, ctrl_air 5, pad_walk 5, pad_jumpin 3 |

**Setup.** Octane (`character_octane`, kit: `mp_ability_octane_stim`, `mp_weapon_jump_pad`, 1 passive). 120 fps,
lane C, facing +X.

**Join.** The M2 join validated every command except the first of each trial: 0 state mismatches, plus one in
r1506. Only the client first-time MOVE-TRACE rows are used as physics. The dedi rows of the same usercmd are
used for parity and for the authoritative status-effect timing.

**Contamination [obs].**
- **r1517 and r1519 (stim_air)** started with the stim of the previous trial still running. The reset came
  < 6.5 s after that stim. Their own tap gave **no** new stim, so they are excluded from the stim statistics.
- **r1553 (ctrl_air)** also started inside a fading stim. msc was back to 1.15 by its jump, so its air data are
  kept.
- **m4_pad_jumpin never touched the pad** (5/5 trials, §3.6), so jump-in launches are **untested**.

**Census.** Class vars were read only at session start (no reads during a stim). The census matches M2 except
the legend. The stim_sprint mod is therefore inferred from fitted caps and accelerations.

## 2. Stim → speed-multiplier primitive

### 2.1 msc time series [obs/fit]

| Quantity | Value | n |
|---|---|---|
| Tap (+offhand1 edge) → first boosted command | **0.160 s** (0.158–0.167), 19–20 commands | 13 |
| Onset shape | one-command step 1.1500 → 1.4927, no fade-in | 13 |
| Plateau msc (from walk cap 258.991 / 173.5) | **1.492744** (sd 0) | 13 |
| Boost factor msc/1.15 | **1.298038** | 13 |
| Full strength, dedi onset → first faded command | **6.005 s** (sd 0.004) | 10 |
| Fade, dedi | 0.491 s from the first faded command to 1.15, so 0.5 s fade | 5 |
| Onset → back to 1.15, dedi | **6.497 s** (sd 0.005) | 5 |

**Value.** The script severity is 0.15, with `movement_speedboost_extraScale` 2 (`sh_stim.gnut:12`), which would
give a factor of 1.30. The measured factor is **1.298038 = 1 + 2·0.149020**, and 0.149020 = **38/255**. The
severity is evidently stored as a byte [inf], which fits to 1e-6. The walk cap 258.991 (not 258.98) separates
this from 1.298 exactly.

**Timing [src+obs].** `StatusEffect_AddTimed(speed_boost, 0.15, duration + 0.5, fadeOut 0.5)` with duration 6.0
(`sh_stim.gnut:58-64`). The tap → onset delay of 0.16 s matches the offhand deploy_time of 0.15 s plus one
command [inf].

**Fade shape [fit, round 2].** Dedi msc on 309 fade commands, fitting both the time shift and the fade duration:

| Shape g(x), x = (t − 6.0)/T | rms (msc) | max | best T |
|---|---|---|---|
| **cosine 0.5 + 0.5·cos(πx)** | **0.0017** | 0.0035 | **0.500 s** |
| smoothstep 1 − (3x² − 2x³) | 0.0018 | 0.0040 | 0.484 s |
| linear | 0.0198 | 0.038 | 0.452 s |
| 1 − x² | 0.0326 | 0.059 | 0.440 s |

Linear is rejected. Cosine and smoothstep cannot be told apart after two rounds. **Cosine is chosen**: it lands on
the script's 0.5 s with no fitted duration, while smoothstep needs a fitted 0.484 s. The remaining 0.0017 is above
print precision (5e-5). It is ≤ 0.6 u/s on a cap.

**Client/dedi [obs].**
- **Onset.** The dedi onset is on the same command in 11/13 trials. In 2/13 the client is 1 command early.
- **Settings mod glitch.** In 5 trials, the client dropped the settings mod for one command about 3 commands
  after onset (maxspeed/msc = 260 on that command). This leaves a 0.25 u position offset to the dedi. The dedi
  corrected it after 6–32 commands in 2 trials, and it persisted in 3.
- **Fade.** The client starts its predicted fade 0–2 commands before the dedi, then snaps to the dedi values within
  4–58 commands. This is the non-monotonic step seen in 5/5 sprint trials.
- **Model.** Use the dedi timing.

### 2.2 Caps, accelerations and deceleration with and without stim [fit]

All values are per command, ground, W held (`accel_bands`):

| | Control (msc 1.15) | Stim (msc 1.4927) | Base value (÷ msc) |
|---|---|---|---|
| walk cap | 199.525 | **258.991** | 173.5, unchanged |
| sprint cap | 299.000 | **420.954** | **260 → 282** (stim_sprint) |
| low band accel (< 120·msc) | 2500.01·msc | 2500.05·msc | 2500, unchanged |
| walk band accel | 450.03·msc | 449.99·msc | 450, unchanged |
| sprint band accel | 100.01·msc (n 2767) | **120.00·msc** (sd 0.06, n 653) | **100 → 120** (stim_sprint) |
| no-input decel | 1250.1 | 1249.9 | **not** × msc (M2 rule holds) |

- **Acceleration scales with msc exactly as in M2.** The stim changes only msc and the two sprint class vars.
- **The stim_sprint mod contents [fit]** are sprintspeed **282** and sprintAcceleration **120**. Nothing else in
  ground movement changes.
- **Mod duration [obs, carry-over trials].** While the boost fades (6.0–6.5 s), sprint commands show
  maxspeed/msc = **260.00** and accel **100**. The mod therefore ends at 6.0 s, at the start of the fade
  (`RemovePlayerClassModAfterDuration(duration)`) [src]. During the fade the sprint cap is 260·msc. This was seen
  in 3 carry-over trials, 36 commands. It is consistent, but it comes from trials whose reset happened mid-stim.

### 2.3 Jump and air [obs/fit]

| | Control (n 7, incl. carry-over r1517/r1519 at msc 1.15) | Stim (n 3) |
|---|---|---|
| speed on the jump command | 299.000 → 299.008 | **420.954 → 420.959** (no clip: the cap is the stim sprint cap) |
| jump vz (post, 120 fps) | 280.44 | 280.44: **jump height unchanged** |
| first strafe press (k = 4, t = 0.033 s, λ = 0.7), \|D\| | 209.30 | **294.667** |
| landing (vz −276) | no slowdown | no slowdown |

**Lurch clamp under stim (M3 open question 2) [fit].** Three hypotheses were tested on the stim presses, with
the M3 model otherwise unchanged:

| Hypothesis | Error on the stim presses |
|---|---|
| L = 209.3 constant | 85.4 u/s |
| L = 182·msc (sprintspeed 260 × msc × 0.7) | 23.0 u/s |
| **L = 0.7·(sprint cap at the jump) = 0.7·282·msc** | **0.001–0.002 u/s** |

The clamp is **0.7 × the current sprint maxspeed**, and that includes the stim_sprint mod. The control presses
fit all three, because there they coincide.

**Air control.** AirAccelerate never engaged on these airborne commands: wish·v exceeded the wish cap on every
command, max(add) = −160 (stim) and −109 (control). So the **air wish cap 60·msc is not tested** by this
schedule. The M2 model still predicts every other airborne command within 0.014 u/s. Keep `airSpeed·msc` from M2.

### 2.4 Unity primitive: SpeedMultiplier (+ SettingsMod)

```
inputs : trigger (tactical press), now
state  : t0 (activation time), active
params : delay 0.16 s, sev 0.149020 (= 38/255), extraScale 2, full 6.0 s, fade 0.5 s (cosine),
         mod {sprintSpeed: 282, sprintAcceleration: 120} for 6.0 s, reuse lockout >= 6.0 s (see open Q)
on press: t0 = now + 0.16
each cmd: t = now - t0
          g = 1                                  if 0 <= t < 6.0
            = 0.5 + 0.5*cos(pi*(t-6.0)/0.5)      if 6.0 <= t < 6.5
            = 0                                  otherwise (or t < 0)
          boost = 1 + extraScale*sev*g           # 1.298038 at full strength
          moveScale = weaponScale(1.15) * boost * landingFactor(t_land)   # product, §4
          sprintSpeed, sprintAccel = (282, 120) if 0 <= t < 6.0 else (260, 100)
uses    : every msc-scaled quantity of M2/M3: walk/sprint/crouch caps, low/walk/sprint accel,
          slide boost and cap, air wish cap, lurch clamp 0.7*sprintSpeed*moveScale.
          NOT: ground deceleration (1250), slide decel, gravity, jump height.
```

## 3. Jump pad → instant impulse + slow-mo flight

### 3.1 Launch [obs/fit], 15 launches

| Stance | Approach \|h\| | Out \|h\| | Launch vz (vz_out + ½·g·dt) | Formula 1150·normalize(1, V) |
|---|---|---|---|---|
| walk (n 5) | 199.525 | 514.309 | 1028.586 (sd 0.001) | h 514.296, vz 1028.591 (V = 2) |
| sprint (n 5) | 299.000 | 514.309 | 1028.586 | same |
| crouch-walk, duck state 2 (n 5) | 92.000 | 813.181 | 813.165 (sd 0.001) | h 813.173, vz 813.173 (V = 2·0.5 = 1) |

**Horizontal is replaced, not kept or added.** Three approach speeds (92, 199.5, 299) give the same output.
- The remaining +0.013 / +0.008 u/s on |h| is the W-held flight drift of §3.3, applied on the launch command
  itself.
- Launch vz agrees with the formula to −0.005 (standing) and −0.008 (ducked).
- **The native formula [fit + src]** is v = PUSH·normalize(ĥ + V·ẑ), with PUSH = 1150 (`JUMP_PAD_PUSH_VELOCITY`)
  and V = `JUMP_PAD_VERT_OVERRIDE` 2.0, multiplied by `jumppad_vert_override_ducked_scalar` 0.5 at duck state 1
  or 2 (`jumppad_parity.cpp:61-66, 573-643`).
- So "ducked vertical ×0.5" halves V **before** the normalization. The result is a 45° launch with **more**
  horizontal speed (813 vs 514), not half of the vertical velocity.
- ĥ, the horizontal launch direction, is **undetermined**. Approach velocity, view yaw and pad orientation were
  all +X.
- The launch happens on the command whose start is 47.5 u (sd 0.45) before the pad centre, which is radius 32
  plus the 16 u hull (swept touch).
- The dedi rows of the launch command are identical in 15/15 (VJumpPadParity).

### 3.2 Slow-mo flight [obs/fit + src]

From the launch command up to and including the landing command:

| Quantity | Value | n |
|---|---|---|
| Position step / (v·dt), horizontal, summed over the flight | **0.80001** (sd 0.00007) | 15 |
| Gravity in velocity units, Δvz/dt | **600.27** (sd 0.12) = 750 × 0.8004 | 15 |
| Air time standing / ducked | 3.433–3.440 s / 2.693–2.701 s | 10 / 5 |
| Apex rise standing / ducked | 707.8 u / 439–443 u | |

Every movement integral runs on **dt' = 0.8·dt**: gravity, integration and air acceleration.
- This is `m_slowMoEnabled`, which the pad scripts set in `JumpJetsWhileAirborne` (`EnableSlowMo`,
  `sh_jump_pads.gnut:517/549`). Both engines move it onto the launch and landing commands
  (`jumppad_parity.cpp:175-194`, `jumppad_predict.cpp`).
- The 0.8 factor itself is not in readable source (`m_airSlowMoFrac` netvar) [inf].
- The ground commands after landing integrate at 1.00 again.
- **World-space equivalent** (what an observer sees): launch 920 u/s along normalize(ĥ + V·ẑ) (411.4 / 822.9
  standing, 650.5 / 650.5 ducked), gravity 480 u/s². Rise 822.9²/960 = 705 u, air time 3.43 s, range ≈ 1411 u
  (observed 1412).

### 3.3 Air control during the flight [obs]

- **No strafe input was given in flight, so air steering is untested.** [inf]: M2 AirAccelerate on dt'.
- **W held** gives a small unexplained gain: d|h|/dt ≈ −0.19 + 0.00184·vz u/s², about +0.6 to +1.4 u/s over
  the whole flight. The M2 AirAccelerate gives 0 here because v·wish ≫ 69. With no input the gain is exactly 0
  (n ≈ 3970 commands).
- This is the same order as M2's rejected "0.3 u/s per jump residual". It is not modelled (< 0.3 %).

### 3.4 Landing

See §4. A pad landing (|vz| ≈ 1025 standing, ≈ 798 ducked) triggers the landing slowdown. Slow-mo ends on the
landing command.

### 3.5 Not exercised

The following were not tested:
- the relaunch debounce of 1.0 s;
- the double-jump grant after 0.1 s (no jump press in flight);
- air launches;
- launches from a jump.

These values come from source only [src].

### 3.6 m4_pad_jumpin: the pad was never triggered [obs]

The jump at 0.8 s carried the player over the pad. While within 48 u of the pad axis, the feet were **32.6–34.3 u**
above the floor, and the trigger's above-height is 32 (`sh_jump_pads.gnut:346`). So "jump onto the pad" needs a
jump that lands on or just before the pad. This trial set tests the trigger height bound, not the launch.

### 3.7 Unity primitive: InstantImpulse (+ TimeScale flight)

```
inputs : trigger volume (cylinder r 32, +32/-16 u; touch = swept capsule overlap), duck state, horizontal dir h
state  : debounceUntil, slowMo
params : push 1150, vert 2.0, duckedVertScale 0.5, debounce 1.0 s, doubleJumpDelay 0.1 s, slowMoScale 0.8
on touch (now >= debounceUntil, air or ground):
    V = vert * (duckedVertScale if ducking/ducked else 1)
    v = push * normalize(h + V*up)      # replaces the whole velocity (approach speed discarded)
    grounded = false; slowMo = true; debounceUntil = now + 1.0; grant double jump at now + 0.1
each airborne cmd while slowMo:  run the normal air move with dt' = 0.8*dt (gravity 750, AirAccelerate, integration)
on landing cmd: slowMo = false (the landing command still uses dt'), then apply LandingSlowdown (§4.4)
```

Keep v in **engine units** and scale dt. Do not scale v. The landing rule (§4) is defined on the engine vz.

## 4. Landing slowdown

### 4.1 Trigger and instant effect [obs]

- **30 landings.**
  - 15 soft: normal jumps, |vz| ≤ 280. These show no change (ratio 1.00002).
  - 15 hard: pad landings, |vz| 796–1028.
- **On the landing command** (airborne pre-state, post vz = 0), the horizontal velocity is **multiplied by f0**.
  - post|h| / pre|h| equals msc_next/msc_base to 5e-5.
  - The small difference is the recovery of one command.
- **From the next command on**, msc carries the same factor (`landing` term of the move-scale product,
  `melee_lunge_probe.cpp:406-421` [src]).
  - msc_min ≈ 0.276 = 1.15 × 0.2397 for standing pad landings: the pilot's "0.28".
  - Ducked landings dip to ≈ 1.07.

### 4.2 f0 as a function of impact [fit, two rounds]

| Model (15 hard landings) | rms | max | f0 = 1 at | f0 = 0 at |
|---|---|---|---|---|
| f0 = a + b·\|vz\| | 0.00050 | 0.00086 | 775.8 | 1103.7 |
| **f0 = a + b·vz²** (a 1.996467, b −1.6714e-6) | **0.00010** | **0.00034** | **772.1** | **1092.9** |
| f0 = a + b·H (H = apex − landing z) | 0.00351 | 0.0085 | 413 u | 799 u |

The two linear forms are separated **within** the impact clusters, independent of the intercept:

| Cluster | Observed d f0/d\|vz\| | Linear-\|vz\| predicts | vz² predicts |
|---|---|---|---|
| \|vz\| ≈ 798, n 5 | −0.002694 (se 0.000049) | −0.003049 | **−0.002669** |
| \|vz\| ≈ 1026, n 10 | −0.003429 (se 0.000002) | −0.003049 | **−0.003429** |

**The vz² form is chosen.** It has the same number of parameters and is the only form consistent with both
slopes. Measured fall height is rejected.

**Caveats:**
- There are only two impact clusters. The ends (772 / 1093) are extrapolations.
- All hard landings were slow-mo pad landings. vz is the engine velocity, 1.25 × the world speed. Whether a
  normal-gravity fall with the same engine vz gives the same f0 is assumed, not tested.

### 4.3 Recovery [fit]

The model is f(t) = f0 + (1 − f0)·(t/T)^p, with t measured from the start of the landing command:

| Fit | T | rms (in f) | max | n cmds |
|---|---|---|---|---|
| p = 1 | 1.050 | 0.103 | 0.188 | 1804 |
| **p = 2, 12 uncorrected landings** | **0.998** | **0.00028** | 0.0020 | 1439 |
| p free, 12 uncorrected landings | p = 2.00, T 0.998 | 0.00028 | | 1439 |
| p = 2, all 15 (client) | 1.004 | 0.0055 | 0.022 | 1804 |
| p = 3 | 0.950 | 0.042 | 0.10 | 1804 |

- **The recovery is quadratic (ease-in) over T = 1.0 s = census `landSlowdownDuration` 1.** At T it snaps to 1.
  T fitted at 0.998 is within one half-command clock offset of 1.0.
- **Dedi correction.** In 3/15 landings (r1532, r1559, r1562) the dedi ran the recovery about 15 ms later. The
  client snapped onto the dedi between 0.25 and 0.5 s, so the dedi is authoritative.
- **Elsewhere**, client msc and dedi msc differ by ≤ 0.017. This is only the sub-millisecond clock offset on the
  steep part of the curve. Positions and velocities are identical.

**Effect on speed [obs].**
- All pad landings had no movement keys held, so after landing the speed bleeds at 1250 u/s². That rate is not
  scaled by msc, which matches M2.
- With W held, the ground cap would be 173.5·msc·f(t), about 48 u/s just after a standing pad landing. This is
  **untested**.

### 4.4 Why M3's 232 u drop showed no dip

M3's impact was |vz| ≈ 585, well below the f0 = 1 onset at 772. The vz² model gives f0 = 1.43, which clamps to 1,
so there is **no slowdown**. This holds whether or not W is held, because the onset is about impact, not input.
M3's data agree: the speed stayed at 299.000.

### 4.5 Unity primitive: LandingSlowdown

```
params : a 1.996467, b -1.6714e-6 (u/s)^-2, T 1.0 s (landSlowdownDuration), exponent 2
on landing cmd (was airborne, now grounded): vz = pre-move vertical velocity (engine units, negative)
    f0 = clamp(a + b*vz*vz, 0, 1)          # 1 for |vz| <= 772, 0.24 at 1025, 0 at >= 1093
    if f0 < 1: v_xy *= f0; tLand = start time of this cmd; f0Stored = f0
each cmd: landingFactor = 1 if t >= T else f0Stored + (1 - f0Stored) * (t / T)^2      (t = now - tLand)
          moveScale *= landingFactor     # multiplies caps and accels like any msc factor; not decel
```

## 5. Evidence summary

| Claim | Level |
|---|---|
| Stim factor 1.298038 (severity 38/255), 0.16 s delay, 6.0 s full, 0.5 s fade, dedi timing | [obs]/[fit], 13 trials, dedi fade on 5 |
| Cosine fade (vs smoothstep: not separable, chosen by simplicity) | [fit] rms 0.0017 msc |
| stim_sprint = sprintspeed 282, sprintAcceleration 120, both for 6.0 s; other ground values unchanged | [fit] 0.05 % spread; mod end from 3 carry-over trials [obs] |
| Lurch clamp = 0.7·sprint cap | [fit] 3 stim + 7 control presses at print precision |
| Pad launch = 1150·normalize(ĥ + V·ẑ), V = 2 or 1 (ducked), horizontal replaced | [fit] 15 launches, 3 approach speeds, 2 stances; dedi identical |
| Pad flight in slow-mo, dt·0.8 | [obs] 0.80001 ± 0.00007; [src] m_slowMoEnabled |
| Landing: v_h ·= f0(vz²), quadratic recovery over 1.0 s | [fit] 15 hard / 15 soft landings, two impact clusters |

## 6. Open questions

1. **Pad horizontal direction ĥ.** Velocity direction, view yaw or pad yaw? Test by approaching at 45° to the
   view, and by standing still on the pad.
2. **Jump-in, air launch, debounce 1 s, double jump at 0.1 s.** Not exercised. Jump-in needs a jump that lands on
   the pad (feet < 32 u inside 48 u).
3. **Air steering in pad flight**, and the small W-held drift (§3.3).
4. **Landing f0 at other impacts.** Test a third cluster (for example a ducked-launch landing at a different
   height, or a tall drop with |vz| 850–1000). Test a normal-gravity hard landing to confirm that slow-mo engine
   vz is the right variable. Test W held during the recovery, to confirm the cap 173.5·msc·f(t).
5. **Stim air cap 60·msc** (needs a strafe with v·wish < cap) and stim jump/slide interactions (slide boost
   150·msc, cap 400·msc).
6. **Stim re-use.** A tap 6.9 s after a carried-over stim gave nothing. Is that the charge (6 s) plus cooldown
   (0.7 s), or the reset? Is this a lockout rule for Unity?
7. **The 0.8 slow-mo factor.** It is measured, but its source value (`m_airSlowMoFrac` or the setfile) has not
   been read.
8. **Client prediction artefacts** are reported, not modelled: the 1-command early stim onset, the one-command
   mod drop (0.25 u offset), the early predicted fade, and the delayed dedi landing clock.
