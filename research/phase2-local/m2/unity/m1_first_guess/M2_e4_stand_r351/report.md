# R5 replay — M2_e4_stand_r351

Model `ReferenceMotor/m1-first-guess` (not tuned per trial). Trial source `r5flowstate`, experiment `M2_e4_stand`, 361 steps aligned by cmd (54129..54489). Units: Source u, u/s; errors are sim − ref. Reports, does not gate.

Parameters: speed 173.5; moveScale 1.15; maxSpeed 199.525; acceleration 450; deceleration 1250; airSpeed 60; airAcceleration 500; jumpHeight 56; gravityScale 1; svGravity 750; gravity 750; jumpVelocity 289.8275.

## Error, whole trial and per phase

| phase | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | spd2d RMS | spd2d max | grounded mismatch |
|---|---|---|---|---|---|---|---|---|---|---|
| **all** | 361 | 1.24 | 3.75 | 0.00 | 0.00 | 25.79 | 286.52 | 0.00 | 0.00 | 3 |
| idle | 254 | 0.32 | 3.75 | 0.00 | 0.00 | 30.58 | 286.52 | 0.00 | 0.00 | 3 |
| accel | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| cruise | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| decel | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| air | 107 | 2.23 | 3.72 | 0.00 | 0.00 | 4.81 | 5.18 | 0.00 | 0.00 | 0 |

## Events (step index; Δ = sim − ref)

| event | ref | sim | Δ |
|---|---|---|---|
| forward start (spd2d > 1 u/s) | – | – | – |
| release (first step without move input) | – | – | – |
| stop (spd2d < 1 u/s after release) | – | – | – |
| takeoff | 72 | 72 | 0 |
| land | 179 | 182 | +3 |
| apex step | 125 | 126 | +1 |
| peak speed step | 0 | 0 | 0 |

| quantity | ref | sim | Δ |
|---|---|---|---|
| apex height above floor (u) | 53.99 | 56.00 | +2.01 |
| takeoff v_z (u/s, state after takeoff step) | 281.84 | 284.50 | +2.65 |
| peak horizontal speed (u/s) | 0.00 | 0.00 | 0.00 |
| horizontal distance start→end (u) | 0.00 | 0.00 | 0.00 |
| release→stop (steps) | – | – | |
| takeoff→land (steps) | 107 | 110 | |

## All events (paired by order; Δ = sim − ref, steps)

| event | ref steps | sim steps | Δ |
|---|---|---|---|
| takeoff | 72 | 72 | 0 |
| land | 179 | 182 | +3 |
| slide_start |  |  |  |
| slide_end |  |  |  |

## Jumps

| # | takeoff step ref/sim | takeoff vz ref | sim | Δ | apex ref (u) | sim | Δ | takeoff spd2d ref | sim | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 72/72 | 281.84 | 284.50 | +2.651 | 53.99 | 56.00 | +2.009 | 0.00 | 0.00 | 0.000 |

## Ground terminal speed and accel/decel (same estimator on both series)

| quantity | ref | sim | Δ | n ref/sim |
|---|---|---|---|---|
| terminal speed (u/s, 1 s before release) | – | – | – | |

Flag mismatches (steps): grounded 3, sliding 0, sprinting 0, maxspeed 0/361.

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
