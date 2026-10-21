# M2 — base movement parameters (walk, run, jump, slide, air control)

Plan M2:

- Using the automated pipeline, measure E0 (runtime parameters), E1 (ground start/stop/turn), E2 (air control), E4 (gravity and jump) and E5 (slide and landing momentum).
- Change one variable at a time, with at least 5 valid trials per condition.
- Deliver a parameter table (value, unit, source) and a model mapped into Unity.
  - Same-condition ground terminal speed must vary ≤ 2 %.
  - Accel/decel parameters must vary ≤ 5 %.

Branch `phase2-local/m2-params` (research) and `m2/r5-motor` (HSD-Unity).

## 1. Acceptance

| # | Criterion | Result |
|---|---|---|
| A1 | E0 census every session | **PASS**: the runner dumps 58 class vars and both sides' settings at session start |
| A2 | ≥ 5 valid trials per condition, one variable changed at a time | **PASS**: 17 conditions, 5–8 valid trials each (§2) |
| A3 | Parameter table with value, unit and source | **PASS**: [PARAMETER-TABLE.md](PARAMETER-TABLE.md) |
| A4 | R5: ground terminal speed spread ≤ 2 %; accel/decel spread ≤ 5 % | **PASS**: terminal speed 0 % in all E1 conditions; worst accel/decel spread 0.10 % (ground), 1.06 % (slide decel) |
| A5 | Unity mapping reproduces the conditions within the same limits | **PASS**: Unity terminal speed equals R5 to 0.000 % in every condition; Unity accel/decel within 0.19 % of R5 (§4) |

## 2. Data

| Session | Content | Valid |
|---|---|---|
| `M2_pilot` | spawn pad, 1× each condition | exposed walls, the `+back`→`+backward` error and falls off the pad; not used |
| `M2_pilot2` | test field, 1× each | clean; not used for fits |
| `M2_main` | 17 × 5 | 32/85. The client sat at about 138 fps for the first ten minutes, and the fps check (±3 %) rejected those trials. Valid: E4 hop3/hop43, E5 (all), part of E4 stand/hop0 |
| `M2_rerun` | E1 (7), E2 (3), e4_stand, e4_hop0 × 5 | 60/60 |

**Test field.** `tools/map_scan.py` traced the map from the dedi and found a flat, hull-clear field at z 294.92 on `mp_rr_canyonlands_staging_mu1` ([map/](map/)).

**Yaw per condition.** Each schedule's yaw makes its motion run along +X.

**Legend caveat.** The firing range assigns a random legend per session: Pathfinder in `M2_main`, Wraith in `M2_rerun`.

- The two class-var censuses differ only in sprintAcceleration (100/102) and dodge.
- The measured sprint acceleration followed each session's census exactly.
- The runner now pins the legend (`--legend`).

## 3. Models (detail in the three sub-reports)

**Ground** — [ground/GROUND-MODEL.md](ground/GROUND-MODEL.md):

- Accel is piecewise by pre-move speed: 2500·msc below 120·msc, then 450·msc, then sprintAcceleration·msc above walk speed while sprinting.
- Speed is capped at speed·msc, sprintspeed·msc or 80·msc (crouch).
- With no input, a constant decel of 1250 standing or 1500 crouched, *not* × msc. Source friction is rejected.
- Velocity = speed × normalized wish direction, redirected instantly.
- One-step error ≤ 0.015 u/s.

**Air and jump** — [air_jump/AIR-JUMP-MODEL.md](air_jump/AIR-JUMP-MODEL.md):

- Gravity: half-step, g = 750.
- Jump: V = √(2·750·56·frac). The jump command removes 1.5·g·dt, which explains the 276.8 u/s seen in M1.
- AirAccelerate: accelspeed = 500·dt, wish cap 60·msc. No air friction or drag.
- Multi-jump height: frac = clamp(0.3 + 0.7·(t − 0.15)/0.60, 0.3, 1).
- Ground friction is skipped on the jump command, so hops keep their speed.

**Slide** — [slide/SLIDE-MODEL.md](slide/SLIDE-MODEL.md):

- Boost to min(v + 150·msc, 400·msc) on the duck press.
- Decay per command: v' = (v − 100·dt)·0.7^dt. The census values reproduce the data to 0.0008 u/s rms.
- The slide ends below 125 u/s.
- Slide jump inside the refund window: the gain is subtracted. Later: speed floors at 350.
- Slide jump height 50.

**Input facts.**

- The first command after a press carries `fwd = 0.5` (kbutton half-press).
- `+speed` sets button **bit 15** in this build, not the SDK header's 1 << 17. The hsdtel schema and the trial export are fixed.
- The `+right` turn key turns at 140.7 °/s.

## 4. Unity mapping

`HSD-Unity`, `Assets/HSD/R5Replay/`:

- `R5MotorV2` sits behind `IMotor`, so the M1 `ReferenceMotor` stays for comparison.
- Class vars come from each trial's own census. Fitted constants come from the M2 `params.json` files.
- The preset is `Presets/R5Reference.asset`.
- EditMode tests: **48/48** (26 old + 22 new, one test per formula plus a synthetic replay regression).
- Open-loop replay of 37 real trials (34 M2 + 3 M1). The lead re-ran it after re-exporting the trials with the sprint-bit fix, and the tables were identical. Full table in [unity/index.md](unity/index.md).

| Condition | Position RMS mean / worst max (u) | Velocity RMS (u/s) | Note |
|---|---|---|---|
| e1 walk / crouch / sprint | 0.03 / 0.04, 0.03 / 0.04, 0.06 / 0.12 | ≤ 0.02 | terminal speed error 0.000 % |
| e1 back / side / diag | 0.14–0.15 / ≤ 0.25 | ≤ 0.02 | |
| e1 turn | 0.66 / 0.97 | 0.11 | |
| e2 noinput / keepfwd | 0.51 / 0.81, 0.65 / 1.14 | ≤ 0.15 | small unexplained in-air speed gain (+0.3 u/s per jump) |
| e2 strafe | 81 / 125 | 60 | **lurch** on the first air strafe press (299 → 253.5 u/s, −44°) is not modelled; that is M3 |
| e4 stand | small, but velocity max 280 | — | the dedi penalised a jump the client did not predict, then corrected the client ~8 cmds later (reset counted as a landing on the dedi only). Harness artefact: leave ≥ 0.75 s between reset and the first jump |
| e4 hop0 / hop3 / hop43 | 1.11 / 1.73, 0.85 / 1.31, 1.72 / 2.73 | ≤ 0.25 | accumulates from the in-air gain |
| e5 slide / slidejump02 / slidejump06 | 0.97 / 1.32, 0.93 / 1.57, 1.29 / 1.81 | 0.16–0.76 | floor seam near 145 u/s; early slide-jump height 50.37 vs 50 |
| M1 loop (spawn pad), before → after | 32.2 → 1.38 RMS | 23.1 → 0.007 | remaining error is a floor bump on the pad (z +2.6); the motor assumes a flat floor |

**Events:**

- Take-off, landing and slide start match to the step everywhere, with two exceptions: e4_stand landing +1/+2 (server correction) and the post-landing slide end in slidejump02 (−1).
- Take-off vz is within ±0.27 u/s, except slidejump02 (−1.0 u/s).

**Ground mapping acceptance:**

- Unity terminal speed equals R5 in every condition, with 0 % spread over the trials.
- Unity accel/decel are within 0.19 % of R5.
- The plan's 2 % and 5 % limits therefore pass.

## 5. Problems found (real data) and how they were handled

| Problem | Handling |
|---|---|
| Client at about 138 fps for 10 min, dips to 77 while the desktop was in use | the fps check rejected those trials; the threshold was not changed; affected conditions re-run 60/60 |
| `+back` is not a command (`+backward`) | fixed after pilot 1 |
| Spawn pad too small and cluttered | map scan → test field |
| Random legend per session | measured its effect, and models read live class vars; runner pins the legend |
| Sprint bit is 15, not 17 | schema fixed; trials re-exported; ground analysis re-run (only a diagnostic field changed) |
| Local user path in a scan JSON before push | tool fixed, commit amended locally, pre-commit hook added |

## 6. Open items carried to M3+

1. **Lurch / tap strafe** (seen once in e2_strafe, identical 5/5) → M3 E3.
2. **Hop speed beyond 299 and hard landings**: `skip_speed_reduce`, `landSlowdownDuration` not yet observed → M3 (landing chains).
3. **Penalty curve between 0.03 and 0.2 s after landing** and the refund-window edge (0.2–0.6 s) → finer schedules.
4. **Duck transition**: R5 keeps the 199.5 cap for about 0.45 s after the duck press, untested while moving; **slopes and steps**; other move scales (weapons); other frame rates → M3 frame-rate tests.
5. Small in-air speed gain (≈ 1.4e-5·vz² u/s²) — ignored; the plan's good-enough rule applies.
6. The legend pin (`--legend`) still needs a live check at the next session.
