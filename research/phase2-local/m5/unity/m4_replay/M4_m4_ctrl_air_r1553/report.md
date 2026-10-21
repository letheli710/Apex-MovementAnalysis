# R5 replay — M4_m4_ctrl_air_r1553

Model `R5MotorV2/m4+landing_slowdown,stim,jump_pad` (not tuned per trial). Trial source `r5flowstate`, experiment `M4_m4_ctrl_air`, 640 steps aligned by cmd (5919..6558). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; lurchClampSprintFraction 0.7; gravity 750; landing_slowdown.a 1.9965; landing_slowdown.b 0; landing_slowdown.duration 1; landing_slowdown.exponent 2; stim.onsetDelay 0.16; stim.severity 0.149; stim.extraScale 2; stim.fullDuration 6; stim.fadeDuration 0.5; stim.fadeShape Cosine; stim.sprintspeed 282; stim.sprintAcceleration 120; stim.modDuration 6; stim.triggerMask 0x200000; jump_pad.push 1150; jump_pad.vertOverride 2; jump_pad.duckedVertScale 0.5; jump_pad.radius 32; jump_pad.hullRadius 16; jump_pad.above 32; jump_pad.below 16; jump_pad.slowMoScale 0.8; jump_pad.debounce 1; jump_pad.headingFromVelocity True; jump_pad.triggerMask 0x1000000; jump_pad.deployDistance 300.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 640 | 10.32 | 16.93 | 10.30 | 16.92 | 19.37 | 185.31 | 2.55 | 14.27 | 0 |
| idle | 283 | 15.03 | 16.93 | 15.02 | 16.92 | 0.72 | 12.03 | 0.72 | 12.03 | 0 |
| accel | 66 | 0.21 | 0.48 | 0.21 | 0.48 | 1.08 | 2.23 | 1.08 | 2.23 | 0 |
| cruise | 184 | 1.62 | 9.65 | 1.53 | 9.63 | 31.58 | 185.31 | 1.61 | 14.24 | 0 |
| decel | 17 | 14.65 | 16.88 | 14.64 | 16.87 | 57.60 | 92.66 | 14.25 | 14.27 | 0 |
| air | 90 | 0.93 | 1.03 | 0.70 | 0.86 | 0.59 | 1.02 | 0.13 | 0.25 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 60 | 60 | 0 |
| release (first step without move input) | 400 | 400 | 0 |
| stop (spd2d < 1 u/s after release) | 417 | 419 | +2 |
| takeoff | 300 | 300 | 0 |
| land | 390 | 390 | 0 |
| apex step | 345 | 345 | 0 |
| peak speed step | 129 | 129 | 0 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 55.41 | 54.80 | -0.61 |
| takeoff v_z (u/s, state after takeoff step) | 280.47 | 280.48 | +0.01 |
| peak horizontal speed (u/s) | 320.90 | 322.55 | +1.65 |
| horizontal distance start→end (u) | 752.90 | 739.41 | -13.50 |
| release→stop (steps) | 17 | 19 | |
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
| 1 | 300/300 | 280.47 | 280.48 | +0.010 | 54.75 | 54.80 | +0.048 | 299.01 | 299.00 | -0.008 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 3732.420 | 3731.863 | -0.557 | 6/6 |
| accel_mid (u/s²) | 671.829 | 671.735 | -0.094 | 13/13 |
| accel_sprint (u/s²) | 153.581 | 148.665 | -4.916 | 50/51 |
| decel_stand (u/s²) | 1250.152 | 1250.000 | -0.152 | 17/19 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 60/640.

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
- M4 abilities (kit landing_slowdown,stim,jump_pad; move scale modelled: parameter moveScale × ability factors, the recorded movescale column is not used): BeforeMove/AfterMove hooks around each command, parameters from research/phase2-local/m4/*/params.json, nothing fitted per trial.
- M4 landing_slowdown [Movement]: f0 = clamp(1.996467 − 1.6714e-6·vz², 0, 1) on the landing command (v_h ·= f0), then move scale ·= f0 + (1−f0)(t/T)², T = landSlowdownDuration (octane §4; 0 = off)
- M4 stim [Tactical]: Octane stim (octane §2.4): onset 0.16 s after the press, move scale ×(1 + 2·38/255·g), g = 1 for 6.0 s then 0.5 s cosine fade; sprintspeed 282 / sprintAcceleration 120 for 6.0 s
- M4 jump_pad [Ultimate]: Octane jump pad (octane §3.7): command start within 32+16 u of the pad → v = 1150·normalize(ĥ + 2ẑ) (1ẑ ducked), velocity replaced; flight on dt·0.8 through the landing command; 1 s debounce
- M4 scenario: legend octane, kit [landing_slowdown, stim, jump_pad] (scenarios.json schedule 'm4_ctrl_air')
- M4 scenario: stim at trial start: onset -5.25 s, ready True (stim carried over from the previous trial: msc 1.4927 at step 0, first faded step 90; onset = its start - 6.0 s (octane §1 contamination))

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
