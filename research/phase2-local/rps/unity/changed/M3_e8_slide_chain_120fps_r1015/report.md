# R5 replay — M3_e8_slide_chain_120fps_r1015

Model `R5MotorV2/m3` (not tuned per trial). Trial source `r5flowstate`, experiment `M3_e8_slide_chain`, 796 steps aligned by cmd (15859..16654). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; sprintspeed 260; acceleration 450; lowSpeed 120; lowAcceleration 2500; sprintAcceleration 100; deceleration 1250; sprintDeceleration 1250; speedScaleBack 1; speedScaleSide 1; gravityScale 1; jumpHeight 56; airSpeed 60; airAcceleration 500; antiMultiJumpHeightFrac 0.3; slideDecel 100; slideVelocityDecay 0.7; slideRequiredStartSpeed 200; slideSpeedBoost 150; slideSpeedBoostCap 400; slideJumpHeight 50; slideMaxJumpSpeed 350; slideStopSpeed 125; svGravity 750; moveScale 1.15; crouchSpeed 80; crouchDeceleration 1500; stopSnapSpeed 1; groundProbe 2; multiJumpHoldT0 0.15; multiJumpRampT 0.6; slideBoostRefundWindow 0.4; sprintButtonMask 0x28000; lurchLamMax 0.7; lurchFullEnd 0.2; lurchZero 0.5; lurchClamp 209.3; groundJumpClampToSprintCap True; slideJumpFloorOnlyAfterBoost True; gravity 750.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 796 | 0.82 | 1.29 | 0.60 | 1.11 | 0.23 | 0.65 | 0.15 | 0.39 | 0 |
| idle | 168 | 1.03 | 1.29 | 0.89 | 1.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| accel | 240 | 0.44 | 0.69 | 0.15 | 0.21 | 0.06 | 0.10 | 0.06 | 0.10 | 0 |
| cruise | 216 | 0.92 | 1.27 | 0.65 | 1.09 | 0.21 | 0.39 | 0.21 | 0.39 | 0 |
| decel | 12 | 1.28 | 1.29 | 1.10 | 1.11 | 0.21 | 0.25 | 0.21 | 0.25 | 0 |
| air | 160 | 0.79 | 1.05 | 0.52 | 0.81 | 0.45 | 0.65 | 0.20 | 0.38 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 60 | 60 | 0 |
| release (first step without move input) | 676 | 676 | 0 |
| stop (spd2d < 1 u/s after release) | 688 | 688 | 0 |
| takeoff | 372 | 372 | 0 |
| land | 457 | 457 | 0 |
| apex step | 414 | 414 | 0 |
| peak speed step | 300 | 300 | 0 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 49.35 | 48.87 | -0.49 |
| takeoff v_z (u/s, state after takeoff step) | 264.18 | 264.51 | +0.33 |
| peak horizontal speed (u/s) | 457.80 | 457.80 | 0.00 |
| horizontal distance start→end (u) | 1447.28 | 1446.16 | -1.11 |
| release→stop (steps) | 12 | 12 | |
| takeoff→land (steps) | 85 | 85 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 372, 524 | 372, 524 | 0, 0 |
| land | 457, 599 | 457, 599 | 0, 0 |
| slide_start | 300, 457, 599 | 300, 457, 599 | 0, 0, 0 |
| slide_end | 372, 524, 676 | 372, 524, 676 | 0, 0, 0 |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 372/372 | 264.18 | 264.51 | +0.335 | 48.70 | 48.87 | +0.166 | 350.01 | 350.00 | -0.006 |
| 2 | 524/524 | 232.22 | 231.93 | -0.288 | 37.87 | 37.82 | -0.051 | 237.92 | 237.79 | -0.125 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |
| accel_low (u/s²) | 2876.035 | 2875.000 | -1.035 | 6/6 |
| accel_mid (u/s²) | 517.554 | 517.500 | -0.054 | 13/13 |
| accel_sprint (u/s²) | 115.050 | 115.000 | -0.050 | 103/103 |
| decel_stand (u/s²) | 1250.687 | 1250.000 | -0.687 | 11/11 |

Flag mismatches (steps): grounded 0, sliding 0, sprinting 0, maxspeed 1/796.

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
- Slide rules (RPS, D-47; they replace the Slide / Slide jump lines above and the slideAccel / slideWantToStopDecel / slideMaxStopSpeed 'not modelled' entry, which are the M2/M3 rules kept by -legacyM2): the native N7 slide rules of the Reference game body: duck released while sliding ends the slide at pre |v_h| <= 350, above it decel 400 in place of 100; a duck-press slide is boosted only >= 2 s after the last slide start (a resumed slide counts); the slide-jump refund needs the 0.4 s window and the 200 ms duck transition (counted from the command after the press); the 350 floor lifts only 297.5 < s < 350; steering at slideAccel 50·msc.

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
