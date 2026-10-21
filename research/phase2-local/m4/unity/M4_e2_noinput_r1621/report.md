# R5 replay — M4_e2_noinput_r1621

Model `R5MotorV2/m4+landing_slowdown,air_profile,gravity_lift` (not tuned per trial). Trial source `r5flowstate`, experiment `M4_e2_noinput`, 544 steps aligned by cmd (22088..22631). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 80; airAcceleration 800; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; lurchClampSprintFraction 0.7; gravity 750; landing_slowdown.a 1.9965; landing_slowdown.b 0; landing_slowdown.duration 0; landing_slowdown.exponent 2; air_profile.legend horizon; air_profile.airSpeed 80; air_profile.airAcceleration 800; air_profile.landSlowdownDuration 0; gravity_lift.radius 70; gravity_lift.hullRadius 16; gravity_lift.height 1200; gravity_lift.hullHeight 72; gravity_lift.upSpeed 300; gravity_lift.upAccel 100000; gravity_lift.minUpSpeed 5; gravity_lift.hoverFrac 0.9; gravity_lift.hoverVz 0.5; gravity_lift.maxHover 0.5; gravity_lift.steerSpeed 170; gravity_lift.steerAccel 2000; gravity_lift.toCenterSpeed 50; gravity_lift.toCenterInnerRadius 20; gravity_lift.toCenterInnerScale 0.5; gravity_lift.ejectUp 450; gravity_lift.ejectHorizontal 400; gravity_lift.maxEjectTime 0.5; gravity_lift.travelThreshold 40; gravity_lift.reentryBlock 2; gravity_lift.lifetime 10; gravity_lift.triggerMask 0x200000; gravity_lift.deployDistance 120.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 544 | 0.29 | 0.43 | 0.29 | 0.42 | 0.09 | 0.32 | 0.04 | 0.10 | 0 |
| idle | 185 | 0.34 | 0.42 | 0.34 | 0.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 119 | 0.09 | 0.16 | 0.09 | 0.16 | 0.07 | 0.09 | 0.07 | 0.09 | 0 |
| cruise | 121 | 0.23 | 0.27 | 0.23 | 0.27 | 0.02 | 0.10 | 0.02 | 0.10 | 0 |
| decel | 29 | 0.42 | 0.43 | 0.42 | 0.42 | 0.03 | 0.05 | 0.03 | 0.05 | 0 |
| air | 90 | 0.35 | 0.43 | 0.34 | 0.41 | 0.20 | 0.32 | 0.03 | 0.03 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 60 | 60 | 0 |
| release (first step without move input) | 304 | 304 | 0 |
| stop (spd2d < 1 u/s after release) | 419 | 419 | 0 |
| takeoff | 300 | 300 | 0 |
| land | 390 | 390 | 0 |
| apex step | 345 | 345 | 0 |
| peak speed step | 303 | 182 | -121 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 54.79 | 54.80 | +0.01 |
| takeoff v_z (u/s, state after takeoff step) | 280.44 | 280.46 | +0.02 |
| peak horizontal speed (u/s) | 299.03 | 299.00 | -0.03 |
| horizontal distance start→end (u) | 793.68 | 793.27 | -0.42 |
| release→stop (steps) | 115 | 115 | |
| takeoff→land (steps) | 90 | 90 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 300 | 300 | 0 |
| land | 390 | 390 | 0 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 300/300 | 280.44 | 280.46 | +0.016 | 54.79 | 54.80 | +0.013 | 299.01 | 299.00 | -0.008 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2875.250 | 2875.000 | -0.250 | 6/6 |
| accel_mid (u/s²) | 517.886 | 517.500 | -0.386 | 13/13 |
| accel_sprint (u/s²) | 115.050 | 115.000 | -0.050 | 103/103 |
| decel_stand (u/s²) | 1250.393 | 1250.000 | -0.393 | 27/27 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 0/544.

## Model choices

- Units: SOURCE (u, u/s); one step per usercmd with the recorded dt (dt / n_cmds sub-steps); double precision; flat floor at initial_state z.
- Parameters: census class vars from the trial's own trial.json parameters; fitted constants (crouch speed 80, crouch decel 1500, stop snap 1, ground probe 2, multi-jump t0 0.15 / T 0.60, refund window 0.4) from the M2 params.json; movescale per step from samples.csv when present.
- Ground (GROUND-MODEL §2): piecewise accel low/mid/sprint by PRE-move speed, sprint edge rule 's + sprintAccel·msc·dt < speed·msc', caps speed/sprintspeed/crouch 80 ×msc, constant decel 1250 standing / 1500 ducked (not ×msc), snap < 1 u/s to 0, v = s·wishdir (instant redirect, diagonal normalized, input magnitude ignored on the ground).
- Sprint flag (GROUND-MODEL §3.3 'spr set one command after the press'; AIR-JUMP §3.1/§4.1): grounded pre-state, sprint held on this AND the previous command, forward > 0, not ducked, not sliding. Sprint button = IN_SPEED (1<<17) or bit 15 (the M2 trials record sprint as bit 15; in_sprint is always 0).
- Ducked state (choice): ducked = IN_DUCK held on the previous command (pre-state flag, mirrors the sprint flag lag); the release command still decelerates at 1500 in e5 data.
- Ground over-speed with input held (choice, not in GROUND-MODEL): s = max(cap, s - D·dt) with D = 1500 ducked (SLIDE-MODEL §4) or deceleration standing.
- speedScaleBack / speedScaleSide (choice, both 1 in every trial): multiply the cap when fwd < 0 / when fwd = 0 and side != 0.
- Jump (AIR-JUMP §2.2, §4.2, §6): press edge while grounded; frac = clamp(f + (1-f)(t-0.15)/0.60, f, 1), f = antiMultiJumpHeightFrac, t = start of the jump command - start of the last landing command (first jump of a trial: no landing yet -> frac 1, the trial reset is not a landing); V = sqrt(2 g H frac); vz = -g dt/2 + V, -g dt/2, move, -g dt/2 (post vz = V - 1.5 g dt); no ground friction; the jump command uses AirAccelerate (choice: 'ground clamp still applies' read as the clamp on ground commands only).
- Air (AIR-JUMP §2.1, §3.2): half-step gravity g = sv_gravity·gravityScale; AirAccelerate accelspeed = airAcceleration·dt, wishcap = airSpeed·msc, wishspeed = min(|wishvel|,1)·maxspeed_air (speed·msc, crouch·msc if duck held), current yaw; no air friction/drag.
- Land (AIR-JUMP §2.3): vz < 0 and floor within 2 u below after the move -> grounded, vz = 0, z kept; the next ground command snaps z to the floor.
- Slide (SLIDE-MODEL §6): duck press edge, grounded, |v| >= slideRequiredStartSpeed (unscaled) -> vPeak = min(|v| + 150·msc, 400·msc) before the move, lastBoost = vPeak - |v|; per command s = (s - 100·dt)·0.7^dt along the current velocity direction (no steering, no slideAccel); ends after the first command with post s < 125; ducked afterwards: over-speed decel 1500 down to 92.
- Slide jump (SLIDE-MODEL §5, H1): now - tBoost < 0.4 s -> s -= lastBoost, else s = max(s, 350); H = slideJumpHeight 50; the multi-jump frac is applied to slide jumps too (choice; frac = 1 in every trial used). Landing with duck held and s >= 200 resumes the slide with no boost and no speed loss.
- Lurch (M3 LURCH-MODEL §8): on an airborne command whose buttons gain a bit of IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT (0x618) vs the previous command, with move input, AFTER AirAccelerate: t = start of the press command - start of the last jump command (time-based window); lam = 0.7·clamp((0.5 - t)/0.3, 0, 1); d = normalize((1-lam)·v̂ + lam·wishdir) (skipped when zero); D = |v|·d - v, |D| <= 209.3; v_xy += D. Every new press edge can lurch (several presses per jump untested). Back = straight 209.3 brake, W re-press = no-op by geometry. No jump since Reset -> no lurch. Not modelled: cutoff speed 1100, mantle-boost suppression, movescale dependence of 209.3.
- Ground jump speed (M3 E8 hop350): a non-slide ground jump sets v_xy = min(|v_xy|, sprintspeed·msc) (299 at msc 1.15) before AirAccelerate, whatever the stance/sprint flag (walk-speed hops untested; min(v, cap) and max(v - 100, cap) only differ above 399).
- Slide chain (M3 E8 slide_chain): a slide resumed by a ducked landing (s >= slideRequiredStartSpeed) is flagged 'not boosted'; its slide jump keeps the horizontal speed (no 350 floor, no refund). A slide started by the duck press (boost) keeps the M2 rule. A trial that starts sliding counts as boosted (M2 behaviour).
- Not modelled: slideAccel / slideWantToStopDecel / slideMaxStopSpeed, landSlowdown, the 1.4e-5·vz² residual air gain, the duck transition (hull/eye offset), sprint timing keys, server corrections, slopes/steps/collisions, walls/climb/mantle in the replay (WallBounce / MantleBoost are separate primitives).
- M4 abilities (kit landing_slowdown,air_profile,gravity_lift; move scale modelled: parameter moveScale × ability factors, the recorded movescale column is not used): BeforeMove/AfterMove hooks around each command, parameters from research/phase2-local/m4/*/params.json, nothing fitted per trial.
- M4 landing_slowdown [Movement]: f0 = clamp(1.996467 − 1.6714e-6·vz², 0, 1) on the landing command (v_h ·= f0), then move scale ·= f0 + (1−f0)(t/T)², T = landSlowdownDuration (octane §4; 0 = off)
- M4 air_profile [Passive]: legend horizon: airSpeed 80, airAcceleration 800, landSlowdownDuration 0 (lift_grapple §3 census)
- M4 gravity_lift [Tactical]: Horizon gravity lift (lift_grapple §1.3): within 70+16 u: vz set 300 (gravity replaced), hover band at 90 % of 1200 u, steer 2000 u/s² to 170 or set toward the axis (50/25 u/s); eject 400 view/radial + 450 up after 0.5 s hover or on leaving
- M4 scenario: legend horizon, kit [landing_slowdown, air_profile, gravity_lift] (scenarios.json schedule 'e2_noinput')
- M4 scenario: horizon air profile 80/800 vs trial census 80/800: identical (the passive changes nothing the census does not already carry)

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
