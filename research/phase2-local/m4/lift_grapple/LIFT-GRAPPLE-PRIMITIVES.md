# M4: gravity lift, grapple and Horizon passive as movement primitives

Status: offline analysis of four existing sessions (update 2 adds `M4_horizon_lift2` and `M4_pathfinder2`). Nothing was launched, and no file outside this folder was changed.

```
python lift_grapple_analysis.py \
    --horizon ../../data/20261021_003010_M4_horizon ../../data/20261021_010724_M4_horizon_lift2 \
    --pathfinder ../../data/20261021_003330_M4_pathfinder ../../data/20261021_011119_M4_pathfinder2 \
    --ref ../../data/20261020_190759_T0_smoke --json results.json --params params.json > analysis_output.txt
```

- `lg_load.py`: a thin wrapper around the verified M2 loader (`../../m2/air_jump/aj_load.py`). It applies the same runner filter, joins commands to frames with the SAMPLING-PHASE rule, and adds frame pitch.
- `lift_grapple_analysis.py`: computes every number in this file. It uses only the stdlib, takes session folders as arguments, and contains no local paths.
- `--horizon` and `--pathfinder` take one or more folders. The first Horizon folder must hold the census and the e2/e4 controls. The first Pathfinder folder feeds sections 2.1–2.3 (hold, jump, fwd), whose numbers are unchanged from the first pass. With one folder each, the original command line still works.
- `analysis_output.txt`: the console output. `results.json`: per-trial events and per-group statistics. `params.json`: value, unit, source, n and spread for each parameter.

Evidence labels:

- **[obs]**: read directly from client first-time MOVE-TRACE commands (the physics truth).
- **[fit]**: a formula fitted to those commands, with its residual.
- **[src]**: from script constants or the dedi SDK twin. The S21 client lift is native code, and `trigger_gravity.cpp` is a rewrite of it.
- **[inf]**: an interpretation that the data supports but does not prove.

## 0. Data

| Session | Legend | Scored trials (ok, not warm-up) | Join |
|---|---|---|---|
| M4_horizon | Horizon (`mp_ability_space_elevator_tac`, passive equipped) | m4_lift_ride 5, m4_lift_jumpout 5, m4_lift_strafe 5, e4_stand 5, e2_noinput 5 | every command joined except the first of each trial; 0 state mismatches |
| M4_pathfinder | Pathfinder (`mp_ability_grapple`) | m4_grapple_hold 5, m4_grapple_jump 5, m4_grapple_fwd 5 | as above, except m4_grapple_fwd: about 70 commands per trial run in the mantle, which `FullWalkMove` does not log |
| M4_horizon_lift2 (update 2, no census) | Horizon | m4_lift_ride 5, m4_lift_jumpout 5, m4_lift_strafe 5, padded so that lift deployments are more than 10 s apart | as above |
| M4_pathfinder2 (update 2, no census) | Pathfinder | m4_grapple_near 5 (face 244 u), m4_grapple_far 5 (694 u), m4_grapple_p0 5 (394 u, pitch 0), m4_grapple_p20 5 (394 u, pitch −20 = 20° up), all without input | as above; far and p20 end in a mantle onto the wall top (command gap) |

All trials ran at 120 fps (measured 116.6–120.0) with msc 1.15 throughout. The lift is deployed 120 u ahead of the reset point at every reset. The grapple trials use yaw 0 and pitch −10° (frame pitch −9.998 on every fire command), aimed at the rock face at x = −13706. The face is 394 u from the start point.

**Harness artefact found [obs].** In 5 of the 15 lift trials, the previous reset's lift was still alive, so the player stood in two overlapping lift triggers. Those trials are r1607–r1610 (jumpout) and r1611 (strafe), each the trial after a shorter jumpout trial.
- The previous lift's age at entry was 9.09 s in those trials. In the other 10 it was 10.59–10.85 s; the script lifetime is 10 s.
- Two triggers apply the lift pass twice per command. The entry step becomes 40.4 u/s per command instead of 23.36. The hover timer runs twice as fast, so the hover lasts 0.25–0.35 s instead of 0.50 s.
- The dedi twin runs the lift pass once per touched trigger (`trigger_gravity.cpp:1294-1357`), which explains the doubling.
- **All lift parameters below come from the single-lift trials.** The overlap group is reported separately.
- **Update 2:** the detector flags none of the 15 lift2 trials. All have an entry step of 23.25–23.38 u/s, and the previous lift was 14.2–14.6 s old at entry. Section 1 now pools **25 clean trials** (10 from the first session, 15 from lift2).
- [inf] The old lift outlived its 10 s lifetime while it was occupied, which is consistent with `KEEP_ALIVE_MAX_TIME 5`.

## 1. Gravity lift: sustained-thrust / gravity-replacement volume

### 1.1 Measured behaviour (25 clean single-lift trials)

| Item | Result | Label |
|---|---|---|
| Entry | Origin within 83.6–85.9 u (horizontal) of the lift centre on the first lifted command. The command before was at 85.3–87.5 u and not lifted (n = 25). This fits radius 70 + hull half-width 16 = 86 with one command of touch-update jitter. No exact per-command threshold fits every trial (bracket table in the output). | obs |
| Lift centre | (−14680.02, 6800.00), sd 0.05. This is the deploy point. In r2003 the centring step landed exactly on the centre: v_h then stays 0, because at distance 0 there is no direction. | obs |
| Vertical, first lifted command | vz is set to 300 on that command, from 0 on the ground. up_accel 100000·dt is far above 300, so the rise is a step. | obs/src |
| Vertical during the rise | Post vz is exactly 300.000 (n = 6955, sd 0) with no input, and 299.994 with input. **Gravity is replaced, not added.** | obs |
| Horizontal on entry | The carried velocity is **discarded**: 199.5 drops to 23.36 on the first command. | obs |
| Steering with input | v += 2000·dt along the wish direction, then the 3D magnitude is clamped to max(\|v_h\|, 170). The engine AirAccelerate then runs with Horizon's air values (+800·dt up to a cap of 92 = 80·1.15). The residual of this model is **0.012 u/s per command** for the entry ramp (n = 288) and for the strafe at the centre (n = 600). The same model with 4000 leaves 13.2 u/s. | fit |
| Plateau with input | 170.0 u/s, creeping +0.0126 u/s per command. The creep is not modelled; it is engine-side. | obs |
| No input (centring) | v_h is **set**, not accelerated (to-centre accel = 0). The speed is graph(d; 20→25, 70→50) toward the centre. The error is 0.002 ± 0.010 u/s (n = 2667), and the implied inner radius is 19.98 ± 0.05 u. At the centre this gives a ±25 u/s bang-bang that moves the origin ±0.1 u every command. | fit/src |
| Hover band | It starts when the height fraction (z − 294.92)/1200 reaches 0.9 (first hover command at 0.9017). Then vz = 0.5 − (frac − 0.9)/0.1 (error 0.0001 ± 0.0003, n = 963). That is about 0.48 u/s, so the player creeps up slowly. | fit/src |
| Top eject | The hover timer counts commands whose pre-vz < 5. Eject when it exceeds 0.5 s: measured **0.502 ± 0.003 s on every clean trial** (n = 16; session 1 0.504 ± 0.004, lift2 0.5001 ± 0.0002), about 61 commands. The eject velocity is 400.00 along the flat view yaw plus 450.00 up (n = 25). The direction error is 0.00 ± 0.02°. | obs |
| Side exit (strafe 1 s) | The player leaves at 88.0–90.2 u from the centre (n = 9). Eject is 400 horizontal, **radially outward** (travel from the centre > 40 u overrides the view), plus 450 up. Dwell is > 0.5 s in every trial, so the eject scale min(dwell/0.5, 1) = 1 was not exercised. | obs/src |
| After the eject | Plain ballistics: g = 750.07 ± 0.38, horizontal change 0 (n = 6778). Landing at about −1300 u/s, then normal ground decel 1249.9 ± 0.5. | obs |
| Jump inside the lift | **No effect.** Max \|Δv\| against a ride trial over 120 commands after the press is 0.000 (10/10, single and overlap). The S21 lift has no jump-out. You leave by moving out or by the hover timeout. | obs |
| Re-entry block | 2.0 s after an eject (dedi twin `TG_EJECT_DEBOUNCE`). | src, not exercised |

### 1.2 Client and dedi

- The dedi (SDK twin) produces the same per-command values once both sides are in the same state.
- Divergence comes only from touch timing. The dedi enters the lift 4.4 commands later (0–11). Side exits are up to 6 commands later, and the dedi exit distance is 87.3–98.8 u.
- That gives about 9 in-lift commands per trial (0–16) where the dedi differs from the client. They are all at entry and exit. The rise, hover and eject values match.
- [inf] The dedi touch list is refreshed per server tick, not per command.

### 1.3 Algorithm (per command, before the normal air move)

```
touch    = horizontal |p - c| < R + hull_r (70 + 16) and 0 <= z - z0 <= H (1200)
if not touch or hoverTime > maxHover:            # leaving or timed out -> eject (once)
    if active: eject(); active = false; ejectTime = now
    return
if now - ejectTime < 2.0: return                  # re-entry block
if not active: active = true; enterTime = now; hoverTime = 0
frac = (z - z0) / H
vz = clamp(vz + upAccel*dt, 5, upSpeed) if frac < 0.9 else lerp(0.5, -0.5, (frac-0.9)/0.1)
hoverTime = 0 if vz_pre >= 5 else hoverTime + dt
if wish != 0:
    base = 0 if now == enterTime else v_h
    target = max(|v_h|, steerSpeed)
    v = base + wish * steerAccel*dt ; clamp |v| to max(|v_h|, target)
else:
    v_h = toCenterDir * graph(dist; 20 -> 0.5*toCenterSpeed, R -> toCenterSpeed)   # set, accel 0
gravity is not applied this command; then the normal AirAccelerate (legend air values) runs
eject(): s = min((now - enterTime)/0.5, 1)
         dir = flat view; if horizontal travel from c > 40: dir = radial; if dir == 0: dir = move dir
         v = dir * 400*s + up * 450*s
```

### 1.4 Unity primitive: `SustainedThrustVolume` (gravity replacement)

- **Inputs:** body position and velocity, wish direction (2D, unit or 0), view yaw, dt.
- **State:** active, enterTime, hoverTime, lastEjectTime.
- **Parameters (defaults = Apex):** radius 70, height 1200, upSpeed 300, upAccel 1e5, hoverFrac 0.9, hoverVz 0.5→−0.5, maxHover 0.5 s, steerSpeed 170, steerAccel 2000, toCenterSpeed 50 (inner 20 u at half speed), toCenterAccel 0, ejectUp 450, ejectHorizontal 400, maxEjectTime 0.5 s, travelThreshold 40, reentryBlock 2 s.
- **Order:** run before the character's air move. While the volume is active, skip gravity. Overlap is cylinder against capsule radius.
- **Decision for Unity:** apply at most one lift per body per tick. Stacking is an Apex harness artefact and not a design target.

## 2. Grapple: rope-pull primitive

### 2.1 Timeline (15 trials) [obs]

| Event | Time after the fire command | Spread |
|---|---|---|
| Fire (`+offhand1`, bit 0x200000) | 0 | — |
| Hop: vz set to **200** outside the move. All trials started grounded. | **0.200 s** | sd 0.001 |
| Ballistic arc (g = 750), no pull | 0.200 → 0.402 s | — |
| Pull starts | **0.402 s** | sd 0.003 |
| Initial burst, no input: \|a\| = **1662 u/s²** (gravity removed) | first **4 commands** of the pull | sd 1.8 |
| Steady pull | until detach | — |
| Detach, no input: ballistic again **35.9 u** (origin) from the face, at 611.6 u/s, 1.125 s after the pull starts | 3–4 commands before contact | sd 0.8 u |
| Detach, W held: 27.8 u from the face, at 519.7 u/s, 0.751 s after the pull starts | 2–3 commands before contact | sd 1.1 u |
| Impact: horizontal speed drops to 6.3, vz is about 193 | — | — |

After the impact the player rises along the face to z ≈ 449.8 (155 u above the floor), then slides back down; this is wall-hang/climb behaviour. With W held, the player climbs and mantles. That belongs to the M3 wall model and is not refitted here.

Notes on the timeline:
- **Fire→attach latency:** the 0.2 s hop and the 0.4 s pull start are fixed in all 15 trials. One distance could not separate flight from wind-up; **resolved in §2.5**: 0.2 s of hook flight, then a 0.2 s wind-up.
- **Jump during the pull (+0.6 s):** no detectable effect. The max \|Δv\| against a hold trial is 1.5–4.8 u/s, and the same metric between hold trials is 1.8–2.8 u/s. In this build, jump does **not** release the grapple during the pull.
- **Auto-detach:** neither a fixed time (1.125 s vs 0.751 s) nor a fixed gap (35.9 vs 27.8 u) nor a fixed time-to-contact (0.035 vs 0.024 s) fits both conditions. The rule is unidentified, and §2.5 confirms this over five geometries. Range 850 and the 5 s drain thread [src] were not reached.

### 2.2 Pull dynamics: two model rounds [fit]

The speed |v| grows **linearly at 502.1 u/s²** (sd 0.5, n = 10, rms 0.27 u/s) over the steady pull, from about 100 to 612 u/s, with no plateau within 1.1 s. The direction swings from the 73° hop arc to about 10–15°, then rises to about 20° at the end. It does not point at the aim-ray hit point. A fixed-anchor line fit through the acceleration directions fails for every gravity scale (rms ≥ 16 u).

| Model (steady pull, no-input trials, anchor x fixed at the face) | Params | Round 1: one-step rms (u/s per command) | Round 2: open-loop, about 0.95 s |
|---|---|---|---|
| M1: speed ramp plus steering, v′ = (\|v\| + A·dt)·norm(v̂ + k·dt·r̂) | A 503.0, k 0.70 /s, target z 484.7 | 0.355 | max position error **23.4 u**, end \|Δv\| 17.7 |
| M2: constant pull toward the target plus reduced gravity, v′ = v + dt·(A·r̂ − s·g·ẑ) | A **557.3** ± 2.0, s **0.148** ± 0.005, target z **494.2** ± 1.4 | 0.398 | max position error **6.9 u**, end \|Δv\| 8.2 |

Round 1 could not separate the models. Round 2 can: M2 is three times better open-loop, and both models have three parameters. **M2 is chosen.** It is also the simpler mechanism: a constant force toward a point plus scaled gravity.

Neither model reaches the noise floor (about 0.01 u/s). Two things remain unmodelled:
- the first 4 commands (1662 u/s²) and the following phase of about 800 u/s² up to |v| ≈ 92;
- [inf] a slight extra upward curvature near the face.

The fitted target is about 199 u above the floor. The aim ray rises 69.5 u over 394 u. With an assumed eye height of about 60 (not measured), the ray hits at z ≈ 424, so the effective pull target is roughly 70 u above the hit point.

**W held [obs]:**
- The speed ramp is **611.7 u/s²** (sd 0.4), about +110 over no input, until the horizontal speed reaches **483.000 = 420·msc**.
- Horizontal speed is then clamped exactly, while vz keeps rising.
- The initial burst does not appear, because the player is already moving at 199.5 from walking.

### 2.3 Client and dedi (no parity bridge) [obs]

During the pull, the client and dedi post velocities differ by at most **0.21 u/s** (rms 0.037; 0.03–0.21 per trial).
- The client receives 8–21 prediction corrections per pull (its pre-velocity ≠ its previous post-velocity). That is about one every 8 commands.
- So the S3 dedi's native grapple differs slightly from the S21 client's, but the error stays below 0.25 u/s because of the corrections.
- The dedi event timing (hop, pull start, detach) was not compared command by command.

### 2.5 Update 2: distance and pitch series (25 no-input trials) [obs/fit]

All five conditions aim at the same face (x = −13706). The "hook length" is the horizontal distance to the face divided by cos(pitch).

| Condition | Face distance | Pitch up | Hook length | Fire→hop (attach) | Fire→pull | Pull duration | Speed at detach | Detach gap | d\|v\|/dt (> 150 u from face) | Per-trial F1 target H |
|---|---|---|---|---|---|---|---|---|---|---|
| near | 244 | 10° | 247.8 | 0.1249 s | 0.3248 s | 0.850 s | 473.6 | 33.1 u | 503.8 | 113 |
| hold | 394 | 10° | 400.1 | 0.2000 | 0.4017 | 1.125 | 612.0 | 35.6 | 502.1 | 129 |
| far | 694 | 10° | 704.7 | 0.3500 | 0.5503 | 1.546 | 804.4 | 37.6 | 501.3 | 163 |
| p0 | 394 | 0° | 394.0 | 0.1995 | 0.3997 | 1.067 | 729.7 | 33.5 | 551.4 | 49 |
| p20 | 394 | 20° | 419.3 | 0.2116 | 0.4119 | 1.174 | 633.7 | 31.8 | 500.7 | 86 |

Each value is the mean of 5 trials. The spread within a condition is below 0.01 s for times and below 1.5 u/s for speeds.

**Flight vs wind-up (resolved).**
- The hop is the attach. It follows t_hop = 0.004 + hook_length / **2035 u/s** (rms 0.002 s, n = 25).
- The pull then starts **0.2005 ± 0.0017 s** after attach in every condition.
- So the hook flies at about 2035 u/s with no wind-up before it, and a fixed 0.20 s wind-up follows the attach.
- The view ray (pitch) sets the flight length, which supports the hook travelling along the view ray from the eye.

**Pull speed and terminal speed.**
- Away from the wall (> 150 u from the face), the acceleration **along the velocity is 499.8 ± 3.6 u/s²** while moving up. This holds in all 25 trials, for 244–694 u and pitch 0–20°.
- When moving down (p0), the along-path acceleration minus the gravity component is 519.5. That is, gravity speeds the body up on the way down but does not slow it on the way up.
- So speed is a function of time since the pull started, not of distance or pitch.
- There is **no terminal speed**: speed at detach grows with pull duration up to 805 u/s (far).
- Exception: within about 150 u of the face in p0, where the rope swings sharply upward, the along-path acceleration rises to about 1200 u/s².

**Target point.**
- With a free target per trial (F1 = the earlier M2), the target height above the origin at fire, net of the view-ray rise, changes with geometry: 49 (p0), 86 (p20), 113 (near), 129 (hold), 163 (far).
- So F1's target is **not** a fixed offset from the view-ray hit. That earlier per-geometry "+70 u" was a fit artefact.
- Fitted globally (one parameter set for all conditions), R1 puts the target at the view-ray hit + 59 u above the origin. That is close to an eye height of about 60 (assumed, not measured), so R1 is consistent with pulling toward the view-ray hit itself.

**Detach rule.**
- The detach gap to the face is 34.3 ± 2.5 u (30.6–40.6, n = 25), 2–4 commands before contact.
- None of these thresholds fits every trial:
  - a static threshold on the gap (detached max 40.6 ≥ still-pulling min 35.3);
  - a look-ahead gap − 16 − vx·τ for τ in 0–0.1 s;
  - a 3D distance between the target and a point on the body, searched over plausible heights.
- The rule stays unidentified. For a primitive, release at about 34 u before the surface.

**Model choice, round 3 (one parameter set for all five geometries; target = view-ray hit + H).**

| Model | Params | One-step rms (u/s per command) | Open-loop rms / max per condition (u): hold, near, far, p0, p20 |
|---|---|---|---|
| F1: constant pull toward the target plus scaled gravity | A 518.3, s 0.047, H 51.1 | **1.65** | 5.5/20.9, 3.8/12.5, 8.9/30.1, 23.9/46.6, 11.7/28.3 (overall 12.9) |
| R1: along-rope speed +A·dt; the perpendicular part takes s·g and is damped at D | A 509.7, s 0.633, H 59.4, D 19.3 /s | 11.85 | **3.0/8.0, 3.7/7.6, 2.6/9.8, 17.5/44.6, 8.2/13.4** (overall 9.0) |

The two rounds disagree:
- One-step, F1 is 7× better.
- Open-loop, R1 is better in every geometry, but its large one-step error shows that it snaps the velocity onto the rope, which the real body does not do.

On the hold geometry alone (original command line), R1 fits to 0.5 u open-loop and 0.28 u/s one-step. Its parameters do not transfer across geometries, which is another sign that neither model is the mechanism. p0 is poor for both. **F1 is kept, as the simpler model (3 parameters against 4).** The per-geometry M2 fit in §2.2 stays valid for the 394 u / 10° case only.

### 2.6 Unity primitive: `RopePull` (updated with §2.5)

- **Inputs:** fire, aim ray (eye origin, direction), wish axis, dt.
- **State:** phase ∈ {idle, flying, windup, pulling, released}, anchor (view-ray hit), t.
- **Parameters:**
  - range 850
  - hookSpeed 2035 u/s: attach at hookLength/2035
  - hopVz 200 at attach (if grounded)
  - windup 0.20 s after attach
  - burstAccel 1662 for 4 commands (optional)
  - pull (F1, global): pullAccel 518 toward the anchor raised to origin + 51 u, gravity scale 0.047
  - detach about 34 u before the surface
  - W: about +110 u/s² with horizontal cap 420·msc (hold geometry only)
  - jumpRelease = false
- **Check for any implementation:** away from walls, speed should rise about 500 u/s² from the pull start whatever the distance and pitch, with no cap below about 800 u/s. Expect 4–24 u rms path error depending on geometry; horizontal aim (p0) is the worst.

## 3. Horizon passive

| Item | Horizon | Others | Label |
|---|---|---|---|
| airSpeed | **80** | 60 (Pathfinder census, T0 reference) | census |
| airAcceleration | **800** | 500 | census |
| landSlowdownDuration | **0** | 1 | census |
| other 55 class vars | identical | — | census |
| air accel in the data | +800·dt per command up to 92 = 80·1.15 (lift entry ramp, residual 0.012 u/s) | M2: 500·dt up to 69 | fit |
| jump V | 289.822 ± 0.002 (e2), 289.828 (e4) | 289.823 | obs |
| gravity | 749.87 ± 0.25 | 750 | obs |
| no-input air horizontal change | 0.0000 | 0 | obs |
| landing (e2, ~−250 u/s) and hard landing (lift, ~−1300 u/s) | one −1250·dt step, then 1250 decel | same | obs |

The passive changes **air control only**: wish cap 92 instead of 69 and accel 800 instead of 500, so strafing in the air is about 1.6× stronger.
- landSlowdownDuration 0 has no visible effect: no slowdown was seen for other legends either (M3, −585 u/s drop).
- Gravity, jump and landing are unchanged.
- The soft-landing script is visual only [src].

## 4. Open questions

1. The grapple pull mechanism is still open:
   - the initial burst and second phase (1662, then about 800 u/s², up to |v| ≈ 60 / 92);
   - the normal (turning) acceleration law;
   - the near-face acceleration rise when aiming horizontally (p0);
   - the auto-detach rule, which no static, look-ahead or 3D-distance threshold explains (§2.5).
   A dangling anchor (no wall behind the hit point) and a lateral (yaw) offset would separate the rope-direction terms.
2. ~~Grapple attach latency~~: resolved in update 2 (hook 2035 u/s, then a 0.20 s wind-up).
3. Grapple jump-release and swing: is jump ignored only during the pull, or always? Needs a jump after detach and an anchor above the player.
4. Lift eject scaling for dwell < 0.5 s, and the 2 s re-entry block, were not exercised.
5. The exact lift touch rule (radius 86 with ±1 command jitter on the client; the dedi lags 0–11 commands).
6. The extra +110 u/s² with W during the pull (hold geometry only), and the origin of the 420 u/s cap (setfile [?]).
7. ~~Lift overlap in the harness~~: fixed by the padded lift2 schedules (0/15 overlapping, hover 0.500 s in all).
8. The eye height used for the view ray was not measured; the grapple target heights (H) are relative to the origin.
