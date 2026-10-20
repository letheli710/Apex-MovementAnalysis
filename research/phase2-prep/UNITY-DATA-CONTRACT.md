# UNITY-DATA-CONTRACT — `hsdmove-trial/1`

**Purpose.** A single file format that lets a future Unity movement controller be checked against telemetry recorded in R5Flowstate. The goal is to *reference* Apex, not reproduce it: the contract carries the data needed to measure how close the Unity controller is, and each tolerance is a design decision, not a promise of parity.

**Status.**
- The reference implementation is `tools/hsdtel/contract.py`, with CLI commands `export-contract`, `check-contract` and `compare-contracts`.
- It is tested on SYNTHETIC data (`tests/test_analysis.py::TestContract`).
- No real R5 trial exists yet; the first ones come from `EXPERIMENTS.md`.
- The Unity side is **not implemented**. This document only fixes the interface it must meet.

## 1. A trial

A trial is one folder holding one experiment run:

```
<trial>/
  trial.json    manifest
  samples.csv   one row per simulation step
```

Recorded trials come from `hsd_tel.py export-contract <logs> --run rN --experiment E1 -o <trial>`. A Unity trial is written by the Unity test harness in the same format. Both pass `hsd_tel.py check-contract <trial>`.

## 2. Space, units, time

| Aspect | Contract (canonical = recording space) | Unity conversion (`contract.py`) |
|---|---|---|
| Axes | Source: +X forward at yaw 0, +Y left, +Z up, right-handed | Unity: +X right, +Y up, +Z forward, left-handed: `unity = (−y, z, x)` |
| Length | Source units `u`; `meters_per_unit = 0.0254` | multiply by 0.0254 |
| Velocity | `u/s` | same mapping and scale |
| Yaw | degrees, positive = turn left (counter-clockwise from above) | `unity_yaw = −source_yaw` |
| Time | seconds; `t` = end of the step, trial-relative; `dt` = step length | unchanged |
| Steps | **variable dt** (one row per client frame in R5 recordings) | the harness must step the controller with the recorded `dt` (see §6) |

## 3. `samples.csv` columns

| column | unit | required | meaning |
|---|---|---|---|
| `step` | – | yes | 0-based, consecutive |
| `t` | s | yes | end of step |
| `dt` | s | yes | step duration (≥ 0) |
| `in_fwd`, `in_right` | –1..1 | for replay | movement input applied during the step |
| `in_yaw`, `in_pitch` | deg | for replay | view angles during the step |
| `in_jump`, `in_duck` | 0/1 | for replay | buttons held during the step (press edges = 0→1 between rows) |
| `pos_x`, `pos_y`, `pos_z` | u | yes | position **after** the step |
| `vel_x`, `vel_y`, `vel_z` | u/s | yes | velocity **after** the step |
| `grounded`, `sliding`, `crouched`, `sprinting` | 0/1 or empty | no | state after the step; empty = unknown |
| `events` | – | no | `|`-joined: `TAKEOFF`, `LAND`, `SLIDE_START`, `SLIDE_END` |

**Step semantics.** Row *k* holds the inputs held during step *k* and the state sampled after it. That matches how HSD.MoveDiag samples (once per `WaitFrame`, after the predicted move). It is an assumption about R5 frame order, recorded in the manifest as `step_semantics`.

**Sprint input is not in v1.** R5 exposes sprint *state* but no sprint *input* the mod can read reliably (`IN_SPEED` has no CLIENT-VM evidence). A replay harness has to infer sprint from `sprinting` or from the experiment description.

## 4. `trial.json` manifest

```json
{
  "contract": "hsdmove-trial/1",
  "trial_id": "r5flowstate_r11",
  "source": "r5flowstate | unity | synthetic",
  "experiment": "E1",
  "recorded_side": "cl",
  "producer": "hsdtel.contract.export_trial from HSD.MoveDiag v0.2 client frames",
  "space": {"axes": "source_zup_righthanded", "length_unit": "u", "meters_per_unit": 0.0254, "angle_unit": "deg", "...": "..."},
  "timing": {"variable_dt": true, "steps": 619, "duration_s": 4.3, "sampling": "..."},
  "step_semantics": "inputs held during the step; state sampled after the step",
  "parameters": {"airAcceleration": {"value": 0.0, "reader": "sv_setting", "experiment": "E0"}},
  "provenance": {"pos_x": "obs", "dt": "drv (difference of observed Time())", "events": "drv (hsdtel edge detection)"},
  "columns": {"pos_x": {"unit": "u", "meaning": "position after the step"}},
  "notes": ""
}
```

**Rules.**
- `source` must say where the numbers came from. A `synthetic` trial is never compared as if it were R5 data. `export-contract` sets `synthetic` automatically when the input logs carry the `# SYNTHETIC` header.
- Every column in `samples.csv` has a `provenance` entry (`check-contract` enforces this). Provenance follows `TELEMETRY-SCHEMA.md` §1: `obs` = read from the game, `drv` = computed offline, `meta` = bookkeeping.
- `parameters` holds the values that were active during the trial: E0 census values plus any class-var or ConVar changes made for an A/B. A Unity trial lists its controller parameters under the same keys, so the two sides can be diffed.

## 5. Parameter mapping (R5 → Unity)

The census (`hsd_tel.py census`) gives R5 key values. A Unity controller exposes **its own** parameter names. The mapping is a table kept next to the controller and versioned with it. Example rows; the R5 keys are from Phase 1 and their values come from E0:

| Unity parameter (example) | R5 key(s) | Conversion | Evidence level of the R5 meaning |
|---|---|---|---|
| `groundMaxSpeed` | `speed` (stand), `sprintspeed` | ×0.0254 → m/s | B |
| `groundAccel` | `acceleration`, `sprintAcceleration` | from the E1 fit shape | B (key), fitted shape (E1) |
| `groundDecel` / `friction` | `deceleration` | from the E1 decel fit | B / E1 |
| `airWishSpeedCap` | `airSpeed` | ×0.0254 | B + E2 fit |
| `airAccel` | `airAcceleration` | per the E2 fit form | C (inferred form) until E2 |
| `gravity` | `sv_gravity` × `gravityScale` | ×0.0254 | B + E2 |
| `jumpHeight` | `jumpHeight` | ×0.0254; `v = √(2·g_sv·h)` uses unscaled `sv_gravity` | B + E2 |
| `slideBoost`, `slideDecel` | `slideSpeedBoost`, `slideDecel` | E5 | B + E5 |

A value only becomes "validated" once the corresponding experiment's M criteria pass (`EXPERIMENTS.md`).

## 6. How a Unity controller is validated against R5 data

1. **Open-loop replay (primary).**
   - A Unity edit-mode test loads a recorded trial.
   - It places the character at `pos(step 0) − vel(step 0)·dt(0)`, roughly the start state, with the initial velocity.
   - For each row it applies `in_*` and advances the controller by exactly `dt`.
   - It writes a Unity trial with the same steps.
   - Requirement: the controller exposes `Step(input, dt)`, deterministic and independent of `Time.deltaTime`. If the game later uses a fixed timestep, the harness sub-steps or resamples, and the trial says so in `notes`.
2. **Compare.**
   - `hsd_tel.py compare-contracts <r5 trial> <unity trial> --json out.json` (exit 3 on failure).
   - Default tolerances (`contract.DEFAULT_TOLERANCES`), meant to be tuned per experiment:

   | check | default | intent |
   |---|---|---|
   | `pos_rms_u` | ≤ 4 u (≈ 10 cm) | trajectory stays close over a few seconds |
   | `vel_rms_ups` | ≤ 10 u/s | speed curves overlap |
   | `spd2d_max_abs_ups` | ≤ 25 u/s | no single large speed excursion |
   | `grounded_mismatch_frac` | ≤ 2 % | the same ground/air timeline |
   | events | same counts, offset ≤ 2 steps | takeoff, landing and slide timing |

3. **Closed-loop / statistical (secondary).** For "feel" metrics that do not need step alignment, compare distributions: E1 `vmax`/`a`/`d`, E2 gravity / take-off vz / air fit, E4 loss against ground time, E5 boost/decel. Use `summary.csv`, `hops.csv` and `slides.csv` from a Unity trial converted with the same tools. Accept when the Unity value lies inside the R5 trial spread, or inside a design-chosen band where High Speed Doom deliberately differs.
4. **Divergence is information, not failure.** Where High Speed Doom intentionally departs from Apex, record the chosen target in the mapping table and loosen or replace that tolerance. The trial data stays the reference.

## 7. Known limitations of v1

- R5 recordings mix S21 client prediction with S3 dedi authority. Export from `--contract-side cl` (the player's view) by default, and check dedi parity with E1/E8-style comparisons before trusting fine details.
- Collisions, slopes and steps are not described in the trial. Replay trials must come from open flat ground, or the Unity harness must load matching geometry.
- `t` is printed with 5 decimals and `Time()` may be float32, so `dt` noise is about 10 µs. That is negligible at 144 fps.
- Variable `dt` per row. A fixed-timestep controller needs resampling, and the comparison then runs on the resampled grid.
