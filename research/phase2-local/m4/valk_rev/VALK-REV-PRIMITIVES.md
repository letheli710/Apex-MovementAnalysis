# M4 Valkyrie jets and Revenant pounce: movement primitives

Status: offline analysis of four sessions. Nothing was launched and no existing file was changed. Everything is
in this folder:

```
python valk_rev_analysis.py <session> [<session> ...] [--census-ref <T0 census.csv>] [--json results.json] [--params params.json]
python valk_rev_analysis.py ../../data/20261021_004109_M4_valkyrie ../../data/20261021_011256_M4_valkyrie_rerun \
    ../../data/20261021_004416_M4_revenant ../../data/20261021_011514_M4_revenant_rerun \
    --census-ref ../../data/20261020_190759_T0_smoke/report/census.csv --json results.json --params params.json > analysis_output.txt
```

- `valk_rev_analysis.py` computes every number in this file. It reuses the M2 loader (`../../m2/air_jump/aj_load.py`)
  without changes. The run takes about 3 minutes, most of it the jet fit.
- `analysis_output.txt` is its printed output, `results.json` holds the per-trial rows, and `params.json` lists
  the parameters with value, unit, source, n and spread.

Evidence labels:
- **[obs]** read directly from the logs;
- **[fit]** fitted, with residuals given;
- **[inf]** an interpretation that the data is consistent with but does not prove;
- **[src]** taken from script or SDK source (`P:` = s21-platform/scripts, `SDK:` = s21-r5sdk/src).

Units are Source units (u, u/s). "Per command" means one 120 Hz usercmd (dt ≈ 1/120 s). msc = `m_cachedMoveScale`.

## TL;DR

| Mechanic | Primitive | Model |
|---|---|---|
| Valkyrie jets (hold +jump while airborne) | **sustained thrust with exponential velocity targets** | Engages on the same command as the press. Each command: v_z += g·thrust·s(t)·dt, then v_z ·= 2^(−dt/0.27). thrust = 1.9, or 1.7 with move input. s(t) ramps 1.8 → 1 over 0.5 s. When v_z is above what the thrust can hold, it decays with a 0.4 s half-life instead. Terminal climb is **260 u/s** (202 u/s with W). With W, horizontal speed is pulled toward the input with a 0.14 s half-life plus 1035·1.7 u/s² of push, which tapers to 0 between 300 and 600 u/s. Terminal **336 u/s**. |
| Jet release | **velocity cut + post-effect slow fall** | On the release command (dedi), v_z ·= 0.4. After that, gravity is 0.45·g and there is horizontal drag dv/dt = −1.25e-4·v_h². This lasts until the player is within 50 u of the ground (never timed out in ≤ 2.13 s). |
| Revenant pounce | **charged directional impulse** | Launch at release, or at 0.9 s if released earlier. Velocity is **replaced** by (700 + 450·c)·dir(pitch − 35°), with c = clamp((t_release − t_press − 0.9)/1.3, 0, 1). After that it is plain ballistic: g = 750, no drag, horizontal speed constant. No landing slowdown. |

## 1. Data and method

| Session | Trials used (ok, not warmup) | Schedules |
|---|---|---|
| M4_valkyrie (census) | 12 | valk_ctrl 5, valk_jets 5, valk_jets_fwd 2 |
| M4_valkyrie_rerun | 3 | valk_jets_fwd 3 |
| M4_revenant (census) | 6 | pounce_c0 5, pounce_c06 1 |
| M4_revenant_rerun | 9 | pounce_c06 4, pounce_c13 5 |

Every schedule has n = 5. Three census-session jets_fwd trials and nine pounce trials were not ok (fps 95–113) and
are excluded. Setup: lane C, facing +X, pitch 0 (the HSD frame pitch is 0.0 on every launch command), 120 fps.

**The jetpack runs after the MOVE-TRACE post print [obs].**
- In the jets trials, 242 of 684 client frames per trial do not equal the command's MOVE-TRACE post-state. All of
  them equal the **next command's pre-state** (only 1 frame per trial in two trials matches neither).
- So the jet acceleration is applied after the printed air move and after position integration. It changes
  velocity only, and it shows up as next-pre − post.
- The script therefore uses the pair (post_i → pre_{i+1}) as the jet step. dt is the frame time of the frame
  printed after the command.

**Parity.**
- During the hold, client and dedi agree to ≤ 0.001 on every command (10 trials) [obs].
- At release and after it they differ (§2.4). Where they disagree, the dedi values are the model, because the dedi
  is authoritative and the client snaps to it.

**Census [obs].**
- The Valkyrie census (58 keys) is **identical** to T0. No jetpack, glide or hover key is in the census key list,
  so the setfile jet constants below are **fitted**, not read.
- The dedi log prints `SetGlideMeter first call … value=8.00`, which is `glideDuration` (`P:mp_ability_valk_jets.nut:708`).
- The Revenant census differs from T0 only in `climbHeight` 1250 (instead of 100), which is the wall climb. That
  is not part of this test.

## 2. Valkyrie jets → sustained-thrust primitive

### 2.1 Control jumps [obs]

| Quantity | Value |
|---|---|
| jump vz (post) | 280.39 (sd 0.15) |
| apex | 54.79 u |
| air time | 0.758 s |
| g | 750.07 |

These are the M2 values. The passive changes nothing without the jets.

### 2.2 Activation [obs]

- The hold started 0.208 s after leaving the ground, at vz ≈ 130 (10/10 trials).
- The jet acceleration is present **on the same command** as the first airborne +jump (IN_JUMP|IN_DODGE). The
  activation delay is 0 commands.
- vz is unchanged on that command, so `jetpackVerticalVelocityScaleOnActivation` is 1 (tested only with vz > 0).
- On that same command msc goes 1.15 → 1.0 (maxspeed 199.5 → 173.5), because the jets offhand becomes the active
  weapon. msc returns to 1.15 117–122 commands (≈ 1.0 s) after release.
- Gates from source, not tested here [src]: S21 refuses jets within 0.1 s of the previous jump press
  (`SDK:jetpack.cpp:665`), and there is a 0.25 s reactivation delay after a stop (`P:mp_ability_valk_jets.nut:27,562`).

### 2.3 Flight model [fit + src]

The model is the SDK twin's `Jetpack_Apply` (`SDK:game/server/jetpack.cpp:403-602`), which states that it
reproduces the S21 client math. All setfile constants were left free and fitted over 2400 jet commands
(10 trials × 240). t is the time since the activation command.

```
wish   = min(1, |(fwd, side)|)
thrust = T + (H - T)*wish                    # T = jetpackThrust, H = jetpackHorizontalMoveThrust
s(t)   = s0 + (1 - s0)*t/R  for t <= R, else 1
thrust *= s(t);  strafeThrust = H*s(t)
vin = vz
vz  = (vz + g*thrust*dt) * 2^(-dt/tu)                      # branch A
if vin - Term((thrust-1)*g, tu) > 0.01:                     # branch B: faster than the thrust can hold
    vz = vin * 2^(-dt/0.4) + g*dt
Term(a, tight) = a*dt / (1 - 2^(-dt/tight))
horizontal, per move axis (fwd, side):
    limit = moving ? Term(strafeThrust*strafe, tfb) : 0
    v_axis *= 2^(-dt / (|v_axis| > limit ? 0.4 : tfb))
    acc   = wishdir*strafe * taper(v·wishdir),  taper = 1 below ts, 0 above tf, linear between
    acc_axis = 0 on an over-limit axis
    v += acc*strafeThrust*dt
```

The normal air move (gravity 750 at full scale, M2 AirAccelerate) still runs before this, on the same command.

**Fitted constants.** Free fit, two starts per stage, Nelder–Mead with restarts. The round values are
indistinguishable from the free fit at print precision (0.001 u/s):

| Constant | Free fit | Round value | Setfile field (SDK name) |
|---|---|---|---|
| T | 1.89983 | **1.9** | jetpackThrust |
| H | 1.69992 | **1.7** | jetpackHorizontalMoveThrust |
| tu | 0.27007 s | **0.27** | jetpackTightnessUp (half-life) |
| s0 | 1.80019 | **1.8** | jetpackThrustScaleOnActivation |
| R | 0.49947 s | **0.5** | jetpackThrustScaleTimeOnActivation |
| tfb | 0.13999 s | **0.14** | jetpackTightnessForwardBack |
| strafe | 1035.10 (1034.97 with the others rounded) | **1035** | jetpackStrafe |
| ts / tf | 299.99 / 600.14 | **300 / 600** | jetpackStrafeTaperStart / Finish |

| Residual (next pre-state, u/s per command) | Free | Round |
|---|---|---|
| vz rms (max), all 2400 | 0.0033 (0.014) | 0.0036 (0.018) |
| vx rms (max), W trials 1200 | 0.0028 (0.018) | 0.0034 (0.016) |

- **Branch B** ("decay at 0.4 s half-life") covers 248 commands. Per trial it runs from k = 45/48 to k = 68–72:
  the ramp lifts vz above the post-ramp terminal, which then pulls it back.
- **Round 2 of the horizontal model.** Without the strafe taper, the best fit (tfb 0.062, strafe 2118) leaves
  **5.56 u/s rms**, so the taper is required.
- The W over-limit branch was never reached.

**What a player sees** [fit, model vs. observed at the end of the 2 s hold]:

| | Model | Observed (k > 230, n 45) |
|---|---|---|
| terminal vz, no input | 260.13 | 260.40 (still converging from above) |
| terminal vz, W | 202.32 | 202.27 |
| terminal v_h, W | 335.84 | 335.97 |
| peak vz during the ramp | – | ≈ 366 (no W), ≈ 315 (W) at t ≈ 0.38 s |
| peak v_h during the ramp (W) | – | ≈ 379 at t ≈ 0.3 s |

- **Gravity during the jets [obs]:** the air move still applies full g = 750 (−6.25 per command).
- The net climb comes from thrust·g − g, limited by the tightness.
- There is no glide. Nothing glide-like happens with or without the jets.

### 2.4 Release, post effect and landing [obs]

| Quantity | Value | n |
|---|---|---|
| Stop command, dedi | **the release command** (first command without +jump) | 10/10 |
| Stop command, client prediction | release + 1 | 10/10 |
| vz scale on stop | **0.40000** (sd 0) | 10 |
| Post-effect gravity, dedi | **337.53 u/s² = 0.45005·g** (sd 0.00006) | 10 |
| Post-effect horizontal drag, dedi | **dv_h/dt = −1.2501e-4·v_h²** (se 1.4e-8; rms 0.0004 u/s per command) | 1115 commands |
| Post-effect end | first full-g command at 41.1–45.3 u above the floor; last low-g command at 46.3–49.9 u | 10 |
| Post-effect duration | 2.10–2.13 s (no W), 1.867 s (W). It ends by height, never by time. | 10 |
| Landing vz | −659 to −662 (no W), −600 to −609 (W) | 10 |
| Landing v_h | unchanged (311.7 → 311.6): **no landing slowdown**. The Octane rule gives factor 1. | 5 |

Notes on the table:
- **vz scale on stop:** this is `jetpackVerticalVelocityScaleOnDeactivation`. The SDK applies it only when
  vz ≤ Term((T−1)·g, tu) = 265.75 (`SDK:jetpack.cpp:380-390`). Here vz at the stop was 254 (no W) and 196 (W).
- **Drag model, round 1.** Quadratic drag was chosen. Constant drag (13.09 u/s²) and linear drag (0.0405·v)
  leave a systematic trend between fast and slow samples, ±0.006 and ±0.003 per command. Quadratic leaves 0.00001.
- **Drag axes.** Vertical motion has no drag: gravity stays at 0.45·g at every vz from +200 to −660.
- **Post-effect end.** This is the SDK's 50 u downward probe (`SDK:jetpack.cpp:604-622`).
  `jetpackPostEffectTime` is therefore ≥ 2.13 s, and its value is unknown.

**Client/dedi mismatch after release [obs].**
- **Without W**, the client predicts the post effect: 250 low-g commands, with 3 corrections from its one-command
  late stop.
- **With W held at release**, the client keeps the drag but drops the 0.45 gravity after 3 commands. It is then
  snapped back by the dedi about every 6 commands (40–46 corrections per trial, 20.6–24 u/s in vz each).
- The in-game motion is the dedi's. The client half is a prediction defect of this platform, not a mechanic
  [inf]. The client's drag coefficient is 1.188e-4 (vs 1.250e-4 on the dedi). This is an open question.

### 2.5 Fuel

- The meter starts at **8.0** (`SetGlideMeter(glideDuration)`) [obs].
- No 2.0 s hold ran out [obs]. The drain rate (`jetpackMeterRate`), the activation cost
  (`jetpackMeterOnActivation`) and the recharge rule are **not observed**.
- On empty, the SDK stops the jets through the same path as a release [src]: vz·0.4 if below the terminal, then the
  post effect (`jetpack.cpp:446-448`). After that, `CodeCallback_OnPlayerJetpackStop` holsters the jets
  (`P:mp_ability_valk_jets.nut:715-733`).

### 2.6 Unity primitive: SustainedThrust (+ PostEffect)

```
inputs : jumpHeld (airborne press engages), moveInput (fwd, side), dt
state  : active, tActive, fuel, postFx.active, lastStopTime, lastJumpPressTime
params : thrust 1.9, moveThrust 1.7, tightUp 0.27 s, tightAboveLimit 0.4 s, tightFwdBack 0.14 s
         (tightSide = 0.14, untested), strafe 1035, taper 300..600 u/s, rampScale 1.8, rampTime 0.5 s,
         vzScaleOnStop 0.4, postGravityScale 0.45, postDragQuad 1.25e-4, postProbe 50 u,
         fuelMax 8.0, fuelRate ? (not observed), reactivateDelay 0.25 s, minSinceJump 0.1 s
engage : airborne && jump pressed && fuel > 0 && now - lastStopTime >= 0.25 && now - lastJumpPressTime > 0.1
         -> active = true, tActive = 0, weaponMoveScale = 1.0, cancel postFx
each cmd (after the normal air move; velocity only, position already integrated):
         if !jumpHeld or fuel <= 0: stop()
         else apply the §2.3 step with t = tActive, then tActive += dt
stop() : active = false; if vz <= Term((thrust-1)*g, tightUp): vz *= 0.4
         postFx.active = true
postFx : while airborne && no ground within 50 u below:
            gravityScale = 0.45;  v_h -= 1.25e-4 * |v_h| * v_h * dt   (horizontal only)
         else postFx.active = false (gravityScale 1)
landing: no extra slowdown at these speeds (Octane landing rule gives 1 for |vz| < 772).
weapon : moveScale 1.0 while active and ~1.0 s after stop (weapon swap back), then 1.15.
```

## 3. Revenant pounce → charged directional impulse

### 3.1 Timing [obs + src]

| Schedule | Hold | Press → launch | Release → launch |
|---|---|---|---|
| c0 (tap) | 0.008 s | 0.908–0.917 s (109–110 commands) | 108–109 commands |
| c06 | 0.600 s | 0.908–0.917 s (109–110 commands) | 37–38 commands |
| c13 | 1.300 s | 1.308 s (157 commands) | **1 command** |

- The toss weapon has `toss_pullout_time` 0.9 (`P:weapons/mp_ability_revenant_shadow_pounce_free.txt:33`) [src].
- `startChargeTime = Time() + 0.9` is set at the press (`.nut:OnWeaponTossPrep`) [src].
- **A release before 0.9 s cannot cut the pullout short.** The launch happens at the end of the pullout with
  charge ≈ 0.
- A release after 0.9 s launches on the next command.
- **Full charge therefore needs a 2.2 s hold (0.9 + 1.3), not 1.3 s.** The "max 1.3 s" in
  `../ABILITY-TRIGGERS.md` is the charge window after the pullout. **c13 reached only 31 % charge.**

### 3.2 Launch velocity [obs + src]

The launch vector is measured on the dedi launch command as (v_h, post_vz + ½·g·dt), which removes the half
gravity step:

| Schedule | Speed | Elevation | Charge (obs) | Model, Time at release | Model, Time at launch |
|---|---|---|---|---|---|
| c0 | 701.24 (700.09–702.88) | 34.9999° | 0.0027 | err +1.2 (sd 1.4) | err −2.85 |
| c06 | 702.00 (700.64–702.86) | 35.0000° | 0.0044 | err +2.0 (sd 1.1) | err −2.79 |
| c13 | 839.12 (838.41–839.58) | 34.9999° | 0.3092 | **err +0.72 (sd 0.34)** | err −2.16 |

- **Formula [src, confirmed]:** v = (700 + 450·c) · forward(pitch − 35°, yaw), with
  c = clamp((t_release − startCharge)/1.3, 0, 1) (`.nut:344-394`). The data confirm it at view pitch 0:
  - the elevation is 35.000° to 1e-4;
  - the minimum speed is 700 (the c0/c06 spread of 0–2.9 u/s is the 0–1 command between the pullout end and the
    toss);
  - c13 is within 0.7 u/s.
- **Charge clock, two hypotheses.** Time at release beats time at launch, with an error of +0.7 vs −2.2 u/s. The
  script computes `chargePercentage` in `OnWeaponToss`, which runs at release.
- **Untested, from source only [src]:**
  - the high-angle rules for pitch < −15°: the pitch raise fades to 0 at −80° and the speed is divided by up to 1.5;
  - looking down: pitch ≥ 20° with ground within 200 u is replaced by 15°, and pitch is capped at 75°;
  - 1150 at full charge.
- **The launch replaces the velocity** [src: SDK `player_launch.cpp:350-367` writes mv velocity]. All trials
  started from rest, so this cannot be checked against data. The launch also clears the ground and sets the yaw
  to the launch heading.
- The launch happens from the ground (ground = 1 on the launch command). The position rises 3.35–4.02 u on that
  command.

### 3.3 Charge wind-up [obs]

- From the press, msc is 1.0 and maxspeed 173.5 (instead of 1.15 / 199.5), because the toss weapon is active.
- The trials gave no move input, so speed caps while charging are untested.
- From source, `disable_wall_run` is active while charging, and weapons are disabled during the pounce [src].

### 3.4 Flight and landing [obs]

| Quantity | Value | n |
|---|---|---|
| Gravity, client / dedi | 750.0–750.3 (sd ≤ 0.36) / 750.12 | 15 |
| Horizontal speed in flight | constant to 0.0000 per command (no drag, no input) | 15 |
| Air time | 129–131 commands (c0/c06), 155 (c13) | 15 |
| Landing vz | ≈ −401 (c0/c06), −475 (c13) | 15 |
| Landing | v_h drops only by ground friction (1249–1251 u/s²): **no landing slowdown** (Octane rule factor 1) | 15 |
| msc restored | 6–14 commands after touchdown | 15 |

- Air control with input is untested. Assume the M2 AirAccelerate [inf].

**Parity [obs].**
- The launch command is the same on client and dedi in 14/15 trials. In r2304 the client launched 1 command early.
- The launch velocity is equal to ≤ 0.002 in 12/15 trials; the largest difference is 0.58 u/s.
- In **every** trial the client mispredicts vz 9–11 commands after launch, by +25…+37.6 u/s (= 4–6 commands of
  gravity), and snaps back 6 commands later.
- The cause fits the SDK note that the client enters the launch state only on the snapshot bit, which re-applies
  the launch velocity [inf]. The dedi trajectory is clean ballistic. This is not a mechanic.

### 3.5 Unity primitive: ChargedImpulse

```
inputs : abilityPressed / abilityReleased, view pitch/yaw, grounded
state  : tPress, released, tRelease, charging
params : pullout 0.9 s, chargeTime 1.3 s, vMin 700, vMax 1150, pitchRaise 35 deg, idealUpLimit -15 deg,
         vertLimit -80 deg, maxDivisor 1.5, maxDown 75 deg, groundCheck (>=20 deg, 200 u -> 15 deg),
         chargeMoveScale 1.0
press  : tPress = now; charging = true; weaponMoveScale = 1.0; no wall run
fire   : at max(release, tPress + 0.9) (on the next command when the release is after 0.9 s)
         c = clamp((tFireDecision - tPress - 0.9)/1.3, 0, 1)      # tFireDecision = release time, or pullout end
         p = pitch (down positive); if p >= 20 and ground within 200 u along the view: p = 15
         if -15 <= p <= 75: p' = p - 35;  speedDiv = 1
         elif p < -15:      p' = p - lerpClamped(p, -15..-80, 35..0); speedDiv = lerpClamped(p, -15..-80, 1..1.5)
         v = (700 + 450*c)/speedDiv * forward(p', yaw)
         velocity = v (replace); grounded = false
flight : ordinary air move (g 750, no drag); weapons stowed until landing (+0.2 s minimum)
landing: no slowdown at these speeds; ground friction as usual.
```

## 4. Open questions

1. **Valkyrie fuel.** The drain rate, the activation cost and the recharge are not measured. This needs a hold
   longer than 8 s, or a log line for the meter.
2. **jetpackPostEffectTime.** Only a lower bound (2.13 s) is known, because the probe ended the effect every time.
   This needs a release higher than about 900 u.
3. **Untested jet branches.** Sideways tightness (no strafe input), tightness down (activation while falling),
   `VerticalVelocityScaleOnActivation` for vz < 0, and over-limit horizontal entry (entering the jets faster than
   about 360 u/s).
4. **Client post-effect prediction with W.** It drops the 0.45 gravity and uses a 5 % lower drag. Is the S21
   retail behaviour different from the SDK twin? It makes no difference to the authoritative motion.
5. **Pounce untested ranges.** Pitch other than 0, full charge (2.2 s hold), a moving start (replace vs. add), air
   control in flight, and the wall-climb interaction (`climbHeight` 1250).
6. **Charge clock residual.** c13 is +0.72 u/s (about 0.25 command) above the release-time model. This is
   sub-command timing and is not modelled.
