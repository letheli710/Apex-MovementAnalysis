# R5 replay — M2_e5_slidejump06_r282

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e5_slidejump06`, 879 steps aligned by cmd (87354..88232). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 879 | 300.50 | 448.16 | 300.49 | 448.16 | 104.52 | 320.69 | 101.09 | 258.64 | 8 |
| idle | 206 | 333.11 | 416.90 | 333.11 | 416.90 | 15.55 | 104.61 | 15.55 | 104.61 | 0 |
| accel | 288 | 96.32 | 174.53 | 96.32 | 174.53 | 90.57 | 125.89 | 90.57 | 125.89 | 0 |
| cruise | 272 | 383.91 | 448.16 | 383.91 | 448.16 | 131.46 | 320.69 | 123.01 | 258.64 | 8 |
| decel | 10 | 421.01 | 424.41 | 421.01 | 424.41 | 109.46 | 109.60 | 109.46 | 109.60 | 0 |
| air | 103 | 341.08 | 392.91 | 340.99 | 392.69 | 151.71 | 151.74 | 150.58 | 150.68 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | 72 | 72 | 0 |
| release (first step without move input) | 735 | 735 | 0 |
| stop (spd2d < 1 u/s after release) | 745 | 757 | +12 |
| takeoff | 446 | 446 | 0 |
| land | 549 | 557 | +8 |
| apex step | 497 | 501 | +4 |
| peak speed step | 360 | 135 | -225 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 48.92 | 56.00 | +7.08 |
| takeoff v_z (u/s, state after takeoff step) | 265.72 | 284.56 | +18.84 |
| peak horizontal speed (u/s) | 458.17 | 199.53 | -258.64 |
| horizontal distance start→end (u) | 1303.27 | 890.38 | -412.89 |
| release→stop (steps) | 10 | 22 | |
| takeoff→land (steps) | 103 | 111 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 446 | 446 | 0 |
| land | 549 | 557 | +8 |
| slide_start | 360, 549 |  |  |
| slide_end | 446, 728 |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 446/446 | 265.72 | 284.56 | +18.842 | 48.90 | 56.00 | +7.098 | 350.01 | 199.53 | -150.480 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | 199.525 | – | |
| accel_low (u/s²) | 2869.596 | – | – | 7/0 |
| accel_mid (u/s²) | 518.096 | 450.000 | -68.096 | 17/63 |
| accel_sprint (u/s²) | 114.849 | – | – | 123/0 |
| decel_stand (u/s²) | 1254.788 | 1250.000 | -4.788 | 9/23 |
| decel_duck (u/s²) | 1505.891 | – | – | 1/0 |

Flag mismatches (steps): grounded 8, sliding 265, sprinting 287, maxspeed 662/879.

## Model choices

- Units: SOURCE (u, u/s); per-usercmd step with the recorded dt (dt / n_cmds sub-steps); double precision.
- Floor: flat plane at initial_state.pos.z; on ground z is pinned to it and v_z = 0.
- Wish: wishvel = cmd_fwd*F(yaw) + cmd_side*R(yaw), F=(cos,sin,0), R=(sin,-cos,0); wishspeed = speed*moveScale*min(|wishvel|,1).
- Ground: v_h += clamp_len(wishdir*wishspeed - v_h, rate*dt), rate = acceleration when wishspeed>0 else deceleration (vector approach, no separate friction, no lowSpeed/lowAcceleration branch).
- Jump: on the JUMP press edge while grounded, v_z = sqrt(2*sv_gravity*gravityScale*jumpHeight); no ground friction on that command; the air step runs on the same command.
- Air: half-step gravity (v_z -= g*dt/2; move; v_z -= g*dt/2); AirAccelerate with wishspd = min(wishspeed, airSpeed), accelspeed = min(airAcceleration*dt, wishspd - v_h.wishdir) (Phase 1 §3 [C] form, no *wishspeed).
- Land: after an air step, pos.z <= floor and v_z <= 0 -> snap to floor, v_z = 0, grounded.
- Not modelled: sprint, crouch/slide, lowSpeed/lowAcceleration, side/back speed scale, landSlowdown, skip_time/bhop penalties, collisions/slopes/steps.

Files: `steps.csv` (per-step ref/sim/error), `summary.json` (all numbers above).
