# R5 replay — M4_m4_pounce_c0_r1902

Model `R5MotorV2/m4+landing_slowdown,pounce` (not tuned per trial). Trial source `r5flowstate`, experiment `M4_m4_pounce_c0`, 540 steps aligned by cmd (4610..5149). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; lurchClampSprintFraction 0.7; gravity 750; landing_slowdown.a 1.9965; landing_slowdown.b 0; landing_slowdown.duration 1; landing_slowdown.exponent 2; pounce.pullout 0.9; pounce.chargeTime 1.3; pounce.vMin 700; pounce.vMax 1150; pounce.pitchRaise 35; pounce.idealUpLimit -15; pounce.vertLimit -80; pounce.maxDivisor 1.5; pounce.groundCheckPitch 20; pounce.groundCheckReplacePitch 15; pounce.groundCheckDist 200; pounce.maxDownPitch 75; pounce.chargeMoveScale 1; pounce.triggerMask 0x200000.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 540 | 6.88 | 11.64 | 6.53 | 9.56 | 53.28 | 698.21 | 36.49 | 573.41 | 5 |
| idle | 355 | 6.03 | 11.64 | 6.00 | 9.56 | 52.27 | 698.21 | 43.04 | 573.41 | 2 |
| accel | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| cruise | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| decel | 56 | 4.66 | 8.28 | 4.61 | 8.25 | 32.80 | 34.15 | 32.80 | 34.15 | 0 |
| air | 129 | 9.42 | 11.56 | 8.37 | 9.54 | 62.43 | 400.69 | 3.22 | 23.08 | 3 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 169 | 167 | -2 |
| release (first step without move input) | – | – | – |
| stop (spd2d < 1 u/s after release) | – | – | – |
| takeoff | 169 | 167 | -2 |
| land | 298 | 295 | -3 |
| apex step | 233 | 231 | -2 |
| peak speed step | 169 | 167 | -2 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 110.01 | 109.15 | -0.86 |
| takeoff v_z (u/s, state after takeoff step) | 399.96 | 398.38 | -1.58 |
| peak horizontal speed (u/s) | 575.67 | 573.41 | -2.26 |
| horizontal distance start→end (u) | 753.80 | 745.54 | -8.25 |
| release→stop (steps) | – | – | |
| takeoff→land (steps) | 129 | 128 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 169 | 167 | -2 |
| land | 298 | 295 | -3 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 169/167 | 399.96 | 398.38 | -1.584 | 110.01 | 109.15 | -0.856 | 575.67 | 573.41 | -2.259 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| decel_stand (u/s²) | 1250.047 | 1250.000 | -0.047 | 54/53 |

Flag mismatches (steps): grounded 5, sliding 0, sprinting 0, maxspeed 9/540.

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
- M4 abilities (kit landing_slowdown,pounce; move scale modelled: parameter moveScale × ability factors, the recorded movescale column is not used): BeforeMove/AfterMove hooks around each command, parameters from research/phase2-local/m4/*/params.json, nothing fitted per trial.
- M4 landing_slowdown [Movement]: f0 = clamp(1.996467 − 1.6714e-6·vz², 0, 1) on the landing command (v_h ·= f0), then move scale ·= f0 + (1−f0)(t/T)², T = landSlowdownDuration (octane §4; 0 = off)
- M4 pounce [Tactical]: Revenant pounce (valk_rev §3.5): launch at max(release + 1 cmd, press + 0.9 s), v = (700 + 450c)·dir(pitch − 35°) replacing the velocity, c = clamp((release − press − 0.9)/1.3); move scale 1.0 from the press to the landing
- M4 scenario: legend revenant, kit [landing_slowdown, pounce] (scenarios.json schedule 'm4_pounce_c0')

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
