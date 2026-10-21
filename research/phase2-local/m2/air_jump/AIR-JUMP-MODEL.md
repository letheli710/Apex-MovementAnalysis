# M2 air control (E2) and jump / landing / hops (E4): model

Status: offline analysis of two sessions. Nothing was launched, and no existing file was changed.
The scripts, outputs and parameters are in this folder:

```
python air_jump_analysis.py <session> [<session> ...] [--json results.json]
python air_jump_analysis.py ../../data/20261020_205712_M2_rerun ../../data/20261020_204723_M2_main --json results.json
```

- `aj_load.py` is the loader and the frame-to-command join.
- `air_jump_analysis.py` runs every number in this file. Its output is in `analysis_output.txt`, and its
  per-jump rows are in `results.json`.
- `params.json` lists the model parameters with their sources, n and spreads.

Evidence labels:
- **[obs]**: read directly from the logs.
- **[fit]**: fitted, with residuals reported.
- **[inf]**: an interpretation the data is consistent with but does not prove.
- **[src]**: from the phase-1 source notes (`research/phase1/Movement-Analysis.md`).

## 1. Data and method

**Trials.** All trials have ok=true and warmup=false. There are 42 trials and 118 jumps.

| schedule | runs |
|---|---|
| e2_strafe | r336–r340 |
| e2_noinput | r341–r345 |
| e2_keepfwd | r346–r350 |
| e4_stand | r351–r355, r251–r253 |
| e4_hop0 | r356–r360, r257–r260 |
| e4_hop3 | r261–r265 |
| e4_hop43 | r266–r270 |

All runs are Gibraltar, empty-handed, movescale 1.15.

**Physics truth.** The model uses client first-time MOVE-TRACE commands (side cl, rp=0). Their pre-state
is (o, v) and their post-state is (po, pv). The MT `ge` flag is the **pre-state** ground flag [obs]: a
landing command has ge=0 and post vz=0, and the next command has ge=1.

**dt and yaw per command (join).** The rule comes from SAMPLING-PHASE.md. An HSD client frame shows the
post-state of the latest first-time command printed before it, ordered by the `[plat]` stamp of the same
process. Each join is validated in two ways:
- The frame's o/vel equals the command's po/pv within 0.0016.
- Exactly one command lies between consecutive frames.

Result: 33 438 of 33 480 commands joined. There were 0 state mismatches and 3 frame intervals without
exactly one command. The 42 unjoined commands are 39 trial-first commands plus those 3, and they get no
dt. Over the joined commands, dt = 0.00696 s (sd 0.00028).

**Dedi.** Dedi MT rows of the same usercmd are used for parity. Dedi HSD events (JUMP, TOUCH_GROUND,
`[HSD-RESET]`) give a second clock: the dedi script `Time()`.

**Event detection.**
- Jump command: ge=1 and post vz > 50.
- Landing command: ge=0, pre vz < 0 and post vz = 0.
- Correction: a command whose pre-state differs from the previous post-state by more than 0.002.

## 2. Gravity, integration and the jump (task 1)

### 2.1 Gravity and integration [fit]

| quantity | value |
|---|---|
| g = (vz − pvz)/dt, airborne commands | **749.907 u/s²** (sd 0.705, n = 10 054) → census 750 × gravityScale 1 |
| Δz residual, half-step (trapezoid) `(vz+pvz)/2·dt` | rms **0.00065 u**, max 0.0022 u |
| Δz residual, explicit `vz·dt` / semi-implicit `pvz·dt` | rms 0.0184 / 0.0184 u (rejected) |
| Δxy residual, post velocity `pv·dt` / pre velocity `v·dt` | rms **0.0011** / 0.0332 u |

The sd of g is print quantisation: z and v are printed %.3f, and dt is about 7 ms.

The scheme is Source's StartGravity/FinishGravity:

```
vz -= g*dt/2;  z += vz*dt;  vz -= g*dt/2
```

Horizontal motion uses the velocity after air acceleration.

### 2.2 Take-off velocity: why post vz is about 282 and not 289.8 [fit]

On the jump command, post vz equals **V − 1.5·g·dt**, where V = √(2·g·jumpHeight·frac).
- Fitted V over the first jumps: **289.823 u/s** (sd 0.005, range 289.815–289.833, n = 42).
- Prediction √(2·750·56): 289.828.
- If the gravity were V − g·dt instead, the fitted V would be 287.216 (sd 0.019). The spread is four times
  larger and the value matches no census number, so that form is rejected.

The jump command's displacement uses V − g·dt. The mean residual of Δz/dt against V − g·dt is −0.020 u/s
(sd 0.122), inside the ±0.072 quantisation of z. This is Source's `CheckJumpButton`:
1. StartGravity runs: −g·dt/2.
2. The jump adds V.
3. The jump runs its own FinishGravity: −g·dt/2. The move uses this value.
4. FullWalkMove's final FinishGravity runs: −g·dt/2.

**[inf]** Gravity is applied 1.5 times on the jump command.

- The observed post vz is **282.003** (sd 0.059). The earlier "take-off vz ≈ 276.8" is the next command's
  post vz, V − 2.5·g·dt.
- No crouch is involved: duck = 0 and IN_DUCK = 0 on all 118 jump commands.
- No multi-jump penalty applies to these first jumps (frac = 1.0000).

### 2.3 Apex and air time [obs]

These are unpenalised jumps with no correction (n = 37).

| quantity | value |
|---|---|
| apex (max post z − take-off z) | **54.951 u** (sd 0.026, 54.920–55.000) |
| closed form of the half-step path, V²/2g − V·dt/2 + g·dt²/8 | 54.996 (the sampled maximum is ≤ this) |
| air time, jump command .. landing command | **0.7631 s** (sd 0.0009); **108.89 commands** (106–109, mode 109) |
| landing command post height above the floor | 0.255–1.982 u (n = 118); the next command snaps onto the floor |
| simulation (fitted V, half-step, 2 u ground probe, recorded dts) | apex error +0.031 u (sd 0.018); landing command exact in 112/113, off by 1 in 1 |

The apex is about 1 u below jumpHeight (56) because of the extra 1.5·g·dt on the jump command:
−V·dt/2 ≈ −1.0 u at 144 fps. It is not a census difference. The apex depends on the frame rate.

The landing rule is **[inf]**, taken from Source's CategorizePosition: grounded when falling and the floor is
within 2 u below. The landing command then zeroes vz. The data support it: every landing height is below
2 u, and the simulation reproduces the landing index.

### 2.4 Parity and server-side corrections [obs]

Client and dedi agree bit for bit in 113 of 118 jumps, including every hop penalty. In five rerun
stand jumps (r351–r355), the client predicted a full jump but the dedi applied a partial multi-jump
penalty:

| run | frac (dedi) | dedi t since [HSD-RESET] | frac predicted by §4.2 model |
|---|---|---|---|
| r351 | 0.9823 | 0.735 s | 0.9822 |
| r352 | 0.9677 | 0.722 s | 0.9677 |
| r353 | 0.9730 | 0.727 s | 0.9731 |
| r354 | 0.9544 | 0.711 s | 0.9544 |
| r355 | 0.9467 | 0.704 s | 0.9467 |
| r251–r253 (main) | 1.0000 | 0.767–0.793 s | 1.0000 |

In each case the client was corrected 6–8 commands later. The corrections have dvz −2.6 to −7.8 and dz
−0.11 to −0.44, with no horizontal part. There are 5 corrections in all the trials used.

**[inf]** The dedi treats the trial-reset teleport as a landing, and the client does not. The penalty
model, fitted on hops, predicts all eight stand jumps to within 0.0001. This is an artefact of the test
harness, not a gameplay rule. For the Unity model it means a teleport or reset must not count as a landing.
The other option is that it does count, and then clients must agree with that.

## 3. Air control (task 2)

### 3.1 No input and forward held [obs]

| case | Δ horizontal speed per airborne command | over the whole jump |
|---|---|---|
| e2_noinput, no keys | **0.0000** (sd 0.0000, n = 524) | +0.025 (only the 4 commands with W still held) |
| e2_keepfwd, W + sprint held at 299 u/s | +0.0028 (0–0.007, n = 545) | **+0.301 u/s** (n = 5, identical) |

- With no input there is no air friction or drag. This matches census airFriction 0 and airDrag 0.
- With W held above the cap, AirAccelerate adds nothing, because add = 69 − 299 < 0. Speed is kept.
  Sprint does not continue in the air: sprint = 0 and maxspeed = 199.525 while airborne.
- A tiny residual gain remains. It is close to 1.39·10⁻⁵·vz² u/s², with rms 0.088 u/s² against 0.30 for a
  constant term. It is largest at high |vz| and zero at the apex. It is **unexplained** and ignored, since
  it is 0.1 % of speed per jump.

### 3.2 AirAccelerate form [fit]

The fit uses 1614 airborne commands of the three E2 schedules. Lurch commands (direction press edges)
and landing commands are excluded. The residual is |Δv_obs − Δv_pred| per command.

| accelspeed | cap | yaw | rms | max | rms on strafe commands only |
|---|---|---|---|---|---|
| **A·dt** | **airSpeed × movescale (69)** | **current** | **0.0039** | **0.0142** | **0.0057** |
| A·dt | 69 | previous frame | 0.207 | 3.50 | 0.366 |
| A·dt | airSpeed (60) | current | 0.279 | 3.56 | 0.493 |
| A·dt | 60 | previous | 0.398 | 3.58 | 0.705 |
| A·wishcap·dt or A·wishspeed·dt (any cap or yaw) | | | 58–65 | 181–194 | 104–115 |

Further checks:
- Unclipped steps (v·wishdir < 60) give a/dt = **499.95 u/s²** (sd 0.26, n = 391). This is census
  airAcceleration 500, applied **without** a wishspeed factor. That confirms the phase-1 surf-calibration
  hypothesis.
- The add-speed-limited commands bracket the cap at **[69.000, 69.000]**, which is 60 × 1.15.
- The wish direction uses the yaw shown by the command's own post frame.

The perpendicular residual is 0.000 with the current yaw and −0.09 with the previous yaw.

The chosen formula has no free parameters. All values are census values except the movescale factor on
the cap:

```
wishvel   = fwd*forward(yaw) + side*right(yaw)        (fwd, side in [-1,1]; right = (sin yaw, -cos yaw))
wishspeed = min(|wishvel|, 1) * maxspeed              (airborne maxspeed = 173.5*1.15 = 199.525)
wishcap   = min(wishspeed, airSpeed*movescale)        (= 69)
add       = wishcap - dot(v_xy, wishdir); if add <= 0: done
v_xy     += min(airAcceleration*dt, add) * wishdir    (airAcceleration*dt = 3.48 u/s at 144 fps)
```

The sustained strafe and turn in e2_strafe follow this model:
1. Speed is flat at 253.5 while v·wishdir > 69.
2. It rises to 263.3 as the turn brings v·wishdir under 69.
3. It falls to about 194 once wishdir points more than 90° from velocity.

The residual stays under 0.015 u/s per command throughout.

## 4. Hops (task 3)

### 4.1 Per-hop summary [obs]

There are 19 hop trials, each with 5 jumps and W + sprint held. The table below shows medians, with the
range in brackets. Per-run rows are in `analysis_output.txt`.

| sched | hop | ground commands | t since landing (s) | V (u/s) | height frac | apex (u) | air commands |
|---|---|---|---|---|---|---|---|
| all | 1 | – | – | 289.82 | 1.000 | 54.93 | 109 (106–109) |
| hop0 | 2 | 1 | 0.007 | 158.74 | **0.300** | 16.24 | 58 |
| hop0 | 3 | 52 | 0.361 | 214.1 (214.0–214.4) | 0.546 | 29.8 | 79–80 |
| hop0 | 4 | 31 (30–31) | 0.215 | 177.7 (175.7–178.0) | 0.376 | 20.4 | 64–65 |
| hop0 | 5 | 45–46 | 0.312 | 202.7 (202.4–204.5) | 0.489 | 26.7 | 75–76 |
| hop3 | 2 | 4 | 0.028 | 158.74 | **0.300** | 16.24 | 58 |
| hop3 | 3 | 55 | 0.38–0.42 | 218.8 (218.5–227.4) | 0.570 | 31.1 | 81–82 |
| hop3 | 4 | 31–32 | 0.22 | 179.5 (176.9–179.7) | 0.384 | 20.8 | 63–66 |
| hop3 | 5 | 47–50 | 0.33–0.37 | 206.7 (205.9–215.6) | 0.509 | 27.7 | 76–79 |
| hop43 | 2 | 44–47 | 0.305–0.326 | 200.9 (200.9–205.9) | 0.481 | 26.2 | 74–76 |
| hop43 | 3 | 77–79 | 0.54–0.60 | 253.4 (251.2–263.4) | 0.764 | 41.9 | 94–96 |
| hop43 | 4 | 57–59 | 0.40 | 223.4 (221.8–224.9) | 0.594 | 32.5 | 82–83 |
| hop43 | 5 | 70–71 | 0.49 | 241.4 (240.7–250.9) | 0.693 | 37.9 | 89–93 |

The schedule presses jump at fixed frame offsets. A penalised hop therefore lands early, and the
following hop gets a longer ground time. That is why hops 3–5 alternate.

Horizontal speed:
- The change on the jump command is +0.003 u/s (sd 0.013, n = 118).
- The change on the landing command is +0.005 (n = 76).
- Take-off speed on hops 2–5 is 298.84 (295.3–299.0).

There is **no horizontal speed loss** at landing or at take-off for any delay from 0.007 to 0.60 s. Friction
is skipped on the jump command: hop0 keeps 298.90 → 298.91 one command after landing. The ground sprint
clamp of 299 still applies.

### 4.2 Multi-jump height penalty [fit]

```
frac(t) = clamp( 0.3 + 0.7 * (t - 0.15) / 0.60 , 0.3 , 1.0 )      V = sqrt(2 * g * jumpHeight * frac)
t = time since the last landing (game clock)
```

| fit | t0 | T | rms (frac) | max abs residual | n |
|---|---|---|---|---|---|
| dedi event clock (JUMP.t − previous TOUCH_GROUND.t) | **0.15002 s** | **0.60001 s** | **0.00002** | 0.00004 | 62 ramp hops |
| client Σdt (landing start → jump start) | 0.1515 | 0.5938 | 0.0073 | 0.056 (r269 hop 5) | 62 |
| rounded model (0.15, 0.60), all 76 re-jumps, dedi clock | | | 0.00003 | 0.00007 | 76 |
| plateau, t < 0.05 s | frac 0.29998 (sd 0.00002) | | | | 14 |

- **Height-linear vs V-linear.** On the dedi clock the V/V0-linear alternative has rms 0.0051, so the
  penalty is linear in **height**, not in V.
- **The 0.3 floor** is census `antiMultiJumpHeightFrac`.
- **t0 = 0.15 s and T = 0.60 s are fitted.** No census key gives them. Full height returns 0.75 s after
  landing.
- **Unobserved region.** The plateau is observed only for t ≤ 0.028 s. The ramp is observed for
  0.208–0.602 s. The hold up to 0.15 s is therefore the line's intercept with 0.3, and the region
  0.03–0.2 s is unobserved.
- **Validation (independent).** The model predicts the eight stand jumps of §2.4 from the dedi reset time.
- **Client clock.** Σ ft on the client agrees with the dedi interval to 0.0005 s (sd 0.0057). The exception
  is one hop (r269 hop 5), where it is 0.050 s short. Client and dedi still computed the same V there, so
  the game clock is right and the ft sum missed time in that interval.

### 4.3 Skip window, skip_speed_reduce, landSlowdownDuration [obs]

- **skip_speed_reduce (stock 100).** No horizontal loss at 295–299 u/s for delays of 1, 4 and 44–79 ground
  commands. Either it does not apply under these conditions (for example below some speed threshold, or
  not at sprint speed), or the S21 value is 0. It is not modelled.
- **The only skip-window behaviour visible is the height penalty in §4.2.** Its 0.75 s window may be the
  `skip_time` that phase 1 refers to. That is **[inf]**: no census or ConVar value confirms it.
- **landSlowdownDuration (census 1).** Not visible after these landings (|vz| ≤ about 282). maxspeed is
  unchanged after landing, and sprint = 1 again on the first grounded command. **[inf]** It applies to hard landings
  only. It is not modelled.

## 5. Lurch (tap-strafe) seen in e2_strafe [obs]

The first `+moveright` command arrives 5 commands after take-off. It is a press edge, has sidemove 0.5, and
its wish direction is 90.7° off the velocity. On that command the velocity is redirected, and this is not
AirAccelerate. All five runs are identical, and the dedi matches:
- Speed: 299.03 → **253.50 (× 0.8477)**.
- Direction: 0° → **−44.22°**, which is 0.4874 of the wish angle.
- Decomposition: **v₁ = 0.6150·v₀ + 0.5913·|v₀|·wishdir**.

This is the lurch from phase 1 §4.4, gated on press edges (mask 0x618). There is only one condition (one
angle, one sidemove, one delay, one speed), so no general formula can be fitted. The Unity model leaves it
out, or adds it as an explicitly empirical one-condition rule. It needs E3: vary angle, sidemove, time
after the jump and speed.

## 6. Chosen model (for Unity, per usercmd, dt = frametime)

```
# airborne command
v_xy = AirAccelerate(v_xy, wish(yaw_cmd, fwd, side), cap = 60*movescale, accel = 500*dt)   # §3.2
vz  -= 750*dt/2;  pos += (v_xy, vz)*dt;  vz -= 750*dt/2                                     # §2.1
if vz < 0 and floor within 2 u below: grounded, vz = 0, last_land_time = now              # §2.3
# jump command (grounded, jump press edge)
frac = clamp(0.3 + 0.7*(now - last_land_time - 0.15)/0.60, 0.3, 1)                         # §4.2
V    = sqrt(2*750*56*frac)
skip ground friction; ground speed clamp still applies                                     # §4.1
vz = -750*dt/2 + V;  vz -= 750*dt/2;  pos += (v_xy, vz)*dt;  vz -= 750*dt/2               # §2.2
```

**Simplicity choices.**
- Rejected: the 0.3 u/s per-jump residual air gain (§3.1), lurch (§5), landing slowdown, skip_speed_reduce.
- Kept as Source does it: the 1.5·g·dt jump-command gravity. A Unity port at another tick rate keeps the
  frame-rate dependence of apex and air time, which is −V·dt/2 on the apex.
- The simpler alternative, post vz = V − 0.5·g·dt, would raise the apex by about 2 u at 144 fps, which a
  player can see. It is not recommended.

## 7. Open questions

1. What do t0 = 0.15 s and T = 0.60 s map to? Neither is in the census. Find the ConVar or setting names,
   and whether `skip_time` is 0.75. Is the time measured from TOUCH_GROUND, as fitted, or from the landing
   command start? The two differ by under 1 command, which is within the fit.
2. Penalty for t between 0.03 and 0.2 s is unobserved. A hop delay of 10–25 frames would close this gap.
3. When does skip_speed_reduce apply? Test a hop above 299 u/s, for example after a slide or slide jump.
4. landSlowdownDuration needs a hard landing (a drop from height) to test.
5. Lurch: the general formula, the time window after the jump, and the dependence on sidemove (E3).
6. The vz-dependent residual air gain of about 1.4·10⁻⁵·vz² u/s² while input is held above the cap.
7. The dedi registers the trial reset as a landing while the client does not (§2.4). Future E4 runs should
   keep ≥ 0.75 s between reset and the first jump. Settle 30 frames + 72 frames = 0.70–0.74 s was just
   short in the rerun.
