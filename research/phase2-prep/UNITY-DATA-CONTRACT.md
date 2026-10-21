# UNITY-DATA-CONTRACT — `hsdmove-trial/2`

**Purpose.** A single file format that lets a future Unity movement controller be checked against telemetry recorded in R5Flowstate. The goal is to *reference* Apex, not reproduce it: the contract carries the data needed to measure how close the Unity controller is, and each tolerance is a design decision, not a promise of parity.

**Status.**
- The reference implementation is `tools/hsdtel/contract.py`, with CLI commands `export-contract`, `check-contract` and `compare-contracts`.
- It is tested on SYNTHETIC data (`tests/test_contract.py`, `tests/test_analysis.py::TestContract`).
- A first real R5 trial exists locally (T0 smoke, run `r1`; not in the repository). Experiment trials come from `EXPERIMENTS.md`.
- The Unity side is **not implemented**. This document only fixes the interface it must meet.

**Changes from `hsdmove-trial/1`.**
- Added: the usercmd number per step, sprint input, held buttons and usercmd axes, press/release edges, the initial state, a terrain block, and side-explicit parameters.
- Checks are strict: time and usercmd sequences, input completeness, and edge consistency (§7).
- Comparison is aligned by usercmd and fails on any length or sequence mismatch (§8).
- `load_trial` and `check-contract` still accept v1 trials, checked against the v1 column set.

## 1. A trial

A trial is one folder holding one experiment run:

```
<trial>/
  trial.json    manifest
  samples.csv   one row per simulation step
```

Recorded trials come from:

```
hsd_tel.py export-contract <logs> --run rN --experiment E1 --params logs --course-note "flat ground by spawn" -o <trial>
```

A Unity trial is written by the Unity test harness in the same format. Both must pass `hsd_tel.py check-contract <trial>`.

`export-contract` options:

| option | effect |
|---|---|
| `--contract-side cl\|sv` | which frame stream to export; default `cl` |
| `--params <census.csv>\|logs` | fill `parameters` from a census file, or from the census of the input logs |
| `--params-side` | which side's readers to use; default = the trajectory side (§5) |
| `--session <GUID>` | required when the run label occurs in more than one log session |
| `--map` | override `terrain.map` |
| `--course-note` | free text for `terrain.course_note` |

## 2. Space, units, time

| Aspect | Contract (canonical = recording space) | Unity conversion (`contract.py`) |
|---|---|---|
| Axes | Source: +X forward at yaw 0, +Y left, +Z up, right-handed | Unity: +X right, +Y up, +Z forward, left-handed: `unity = (−y, z, x)` |
| Length | Source units `u`; `meters_per_unit = 0.0254` | multiply by 0.0254 |
| Velocity | `u/s` | same mapping and scale |
| Yaw | degrees, positive = turn left (counter-clockwise from above) | `unity_yaw = −source_yaw` |
| Time | seconds; `t` = end of the step, trial-relative; `dt` = step length | unchanged |
| Steps | **variable dt** (one row per client frame that simulated a usercmd) | the harness steps the controller with the recorded `dt` (see §9) |

## 3. `samples.csv` columns

| column | unit | required | meaning |
|---|---|---|---|
| `step` | – | yes | 0-based, consecutive |
| `t` | s | yes | end of step, strictly increasing |
| `dt` | s | yes | step duration; > 0 after step 0 and equal to the `t` difference |
| `cmd` | – | input | usercmd `command_number` of the last command simulated in the step (MOVE-TRACE `cmd=`) |
| `n_cmds` | – | input | usercmds logged in the step. `cmd − previous cmd` must equal it; anything else is a gap |
| `in_fwd`, `in_right` | –1..1 | input | movement axes the script read (`GetInputAxisForward/Right`) |
| `in_yaw`, `in_pitch` | deg | input | view angles during the step |
| `in_jump`, `in_duck` | 0/1 | input | buttons held (`IsInputCommandHeld`) |
| `in_sprint` | 0/1 | input | `IN_SPEED` (bit 17) held in the usercmd |
| `buttons` | – | input | the usercmd's held `m_nButtons` mask (`in_buttons.h` bits), as an integer |
| `cmd_fwd`, `cmd_side` | –1..1 | input | usercmd `forwardmove` / `sidemove` (+ = right) |
| `movescale`, `maxspeed` | –, u/s | state (optional) | `m_cachedMoveScale` and `CMoveData` maxspeed of the step's last usercmd (MOVE-TRACE `msc=`, `ms=`). Optional: readers must accept trials without them |
| `pressed`, `released` | – | input (may be empty) | `\|`-joined inputs that went down / up during the step (§4) |
| `pos_x`, `pos_y`, `pos_z` | u | yes | position **after** the step |
| `vel_x`, `vel_y`, `vel_z` | u/s | yes | velocity **after** the step |
| `grounded`, `sliding`, `crouched`, `sprinting` | 0/1 or empty | no | state after the step; empty = unknown |
| `events` | – | no | `\|`-joined: `TAKEOFF`, `LAND`, `SLIDE_START`, `SLIDE_END` |

**Step semantics.**
- Row *k* holds the inputs held during step *k* and the state sampled after it. That matches how HSD.MoveDiag samples: once per `WaitFrame`, after the predicted move. This is an assumption about R5 frame order, recorded in the manifest as `step_semantics`.
- Usercmds are attached to frames by wall clock: a frame gets every MOVE-TRACE line of the same side and session that was logged at or before it. The client prints MOVE-TRACE during prediction, before the script samples the frame.
- The manifest records how often the command's post-move origin equals the frame's origin (`timing.cmd_association`).
- A frame that simulated no usercmd is not a step: it is dropped, and its time goes into the next step's `dt` (`timing.frames_without_cmd`).
- A frame that simulated several usercmds has `n_cmds > 1` (`timing.steps_with_several_cmds`). The harness should run `n_cmds` controller steps over that `dt`.

**Sprint.** `in_sprint` is the `IN_SPEED` bit the engine received in the usercmd. Whether a held bit means "sprint" depends on the player's toggle/hold setting, so compare it with `sprinting` (state).

## 4. Input edges

Inputs held in one usercmd:
- every set bit of `buttons`, named after `BUTTON_BITS` in `tools/hsdtel/schema.py` (`JUMP`, `DUCK`, `FORWARD`, `SPEED`, …), other bits as `BIT<n>`;
- plus the axis keys `AX_FWD` (`cmd_fwd > 0`), `AX_BACK` (< 0), `AX_RIGHT` (`cmd_side > 0`), `AX_LEFT` (< 0).

How edges are built:
- `pressed` and `released` compare each usercmd with the one before it, and collect the changes over all the usercmds of the step. A tap that starts and ends inside one multi-command step therefore appears in both columns.
- Step 0 compares with `initial_state.inputs_held`, the usercmd before the trial.

`check-contract` rules:
- With one usercmd per step, `pressed`/`released` must equal the change of the held set exactly.
- With several, they must contain the net change.

## 5. `trial.json` manifest

```json
{
  "contract": "hsdmove-trial/2",
  "trial_id": "r5flowstate_r1",
  "source": "r5flowstate | unity | synthetic",
  "experiment": "E1",
  "recorded_side": "cl",
  "session": "<log session GUID of the exported frames>",
  "producer": "hsdtel.contract.export_trial from HSD.MoveDiag v0.2 frames + MOVE-TRACE usercmds",
  "space": {"axes": "source_zup_righthanded", "length_unit": "u", "meters_per_unit": 0.0254, "angle_unit": "deg", "...": "..."},
  "timing": {"variable_dt": true, "steps": 2782, "duration_s": 44.6, "cmd_first": 12, "cmd_last": 2815,
             "frames_without_cmd": 6, "steps_with_several_cmds": 2, "cmd_association": "...", "sampling": "..."},
  "step_semantics": "inputs held during the step; state sampled after the step",
  "initial_state": {"source": "MT pre-move state of the first usercmd of step 0 (...)", "cmd": 6,
                    "pos": [x, y, z], "vel": [vx, vy, vz], "angles": {"pitch": 0.0, "yaw": 0.0},
                    "grounded": 1, "sliding": 0, "sprinting": 0, "duck_state": 0, "stance": "standing",
                    "crouched": 0, "buttons_held": 0, "inputs_held": "", "inputs_source": "..."},
  "terrain": {"map": "mp_rr_canyonlands_staging_mu1", "map_source": "...", "start_origin": [x, y, z],
              "standable": true, "ground_normal": null, "ground_normal_source": "not recorded ...",
              "course_note": "free text"},
  "parameters_side": "cl",
  "parameters": {"airAcceleration": {"value": "500", "side": "cl", "reader": "cl_classvar", "reader_desc": "...",
                 "type": "cvtype2", "same_side_readings": {"cl_setting": "500.000000"},
                 "other_side_readings": {"sv_setting": "500.000000"}, "side_mismatch": false,
                 "differs_between_readers": false, "experiment": "E0"}},
  "parameter_issues": ["speed: no sv reading (other side: cl_classvar=173.5); left out"],
  "provenance": {"pos_x": "obs", "dt": "drv (difference of observed Time(); ...)", "events": "drv (hsdtel edge detection)"},
  "columns": {"pos_x": {"unit": "u", "meaning": "position after the step"}},
  "notes": ""
}
```

**Rules.**
- `source` says where the numbers came from. A `synthetic` trial is never compared as if it were R5 data. `export-contract` sets `synthetic` automatically when the input logs carry the `# SYNTHETIC` header.
- Every column in `samples.csv` has a `provenance` entry (`check-contract` enforces this). Provenance follows `TELEMETRY-SCHEMA.md` §1: `obs` = read from the game, `drv` = computed offline, `meta` = bookkeeping.
- **`initial_state`** is the state *before* step 0, which a replay places the controller in:
  - preferred source: the MOVE-TRACE pre-move values (`o= v= ge= slide= spr= duck=`) of the first usercmd of step 0; `cmd` names that usercmd;
  - fallback: the HSD frame before the trial, else step 0 minus `vel·dt`, with `source` saying so;
  - angles: the HSD frame before step 0;
  - `stance` from `duck=`: 0 `standing`, 2 `crouched`, other values `duck_state_<n>`;
  - `inputs_held` / `buttons_held`: what the usercmd before the trial held (empty when none was logged).
- **`terrain`**:
  - `map` comes from the session's level-load line (`TELEMETRY-SCHEMA.md` §2, source `LOG`);
  - `start_origin` = `initial_state.pos`;
  - `standable` is `true` when the trial starts on the ground, otherwise `null` (unknown);
  - `ground_normal` is `null` because no producer logs a surface normal;
  - `course_note` is the free text from `--course-note`.
  - Slopes, steps and walls are still not described (§10).
- **Parameters are side-explicit.**
  - Each entry names the side (`cl` client, `sv` dedi) and the reader:
    - `cl_classvar`: client class var, `bridge_classvar_get` on the live class-var block;
    - `cl_setting`: client setting, `GetPlayerSetting*` in the client VM;
    - `sv_setting`: server setting, `GetPlayerSetting*` on the dedi.
  - Export uses the trajectory's side unless `--params-side` says otherwise; `parameters_side` records the choice.
  - On the client, the class var wins over the script getter. The other readings are kept in `same_side_readings` and `other_side_readings`.
  - When the client and dedi values differ, the entry is flagged `side_mismatch` and listed in `parameter_issues`. It is reported, not resolved.
  - A key with no reading on the chosen side is left out and listed in `parameter_issues`. It is never filled in from the other side.
  - `export_trial` refuses parameters without a side/reader, or from a side other than `parameters_side`.
- A Unity trial lists its controller parameters under the same keys with `side: "cl"` and `reader: "unity"` (any non-empty reader), so the two sides can be diffed.

## 6. Parameter mapping (R5 → Unity)

The census (`hsd_tel.py census`) gives R5 key values per reader. Its `differs` column compares all readers; `cl_sv_differs` compares only the client readings with the dedi reading. A Unity controller exposes **its own** parameter names. The mapping is a table kept next to the controller and versioned with it. Example rows; the R5 keys are from Phase 1 and their values come from E0:

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

## 7. Conformance (`check-contract`, exit 2 on problems)

Problems are grouped by kind, with a count and the first rows:

- **Manifest.**
  - The contract id and canonical space must be present.
  - v2 also needs: `initial_state` with `pos`/`vel` (three finite numbers), `angles`, `grounded`, `stance`, `buttons_held`, `inputs_held`; `terrain` with `map`, `start_origin`, `standable`, `ground_normal`, `course_note`; every parameter with a side and reader that match `parameters_side`.
- **Columns.** Every required, input and edge column is present, and each has a provenance entry.
- **Time.**
  - `step` is consecutive.
  - `t` is strictly increasing: `duplicate t` and `t goes backwards` are reported separately.
  - `dt > 0` after step 0, and `dt` equals the `t` difference (within 2 µs plus 1 ppm of `t`).
- **Usercmds.**
  - `cmd` is strictly increasing: `duplicate cmd` and `cmd goes backwards` are reported.
  - `cmd − previous cmd = n_cmds`; anything else is a `cmd gap (usercmds missing between steps)`.
  - Step 0 is checked against `initial_state.cmd`.
- **Inputs.**
  - Every sample has a value in every input column of its version (`input missing (...)`).
  - `pressed`/`released` agree with `buttons`/`cmd_fwd`/`cmd_side` (§4): `missing input edge` or `spurious input edge`.
- **State.** The state columns are finite numbers.

## 8. Comparison (`compare-contracts`, exit 3 on failure)

**Alignment comes first.**
- When both trials carry `cmd` on every row, rows are paired by usercmd number, and the two usercmd sequences must be identical.
- Otherwise rows are paired by step index, and the step counts must be equal.
- Any length or sequence difference fails the comparison with an `alignment.message`, for example `usercmd sequences differ: ref 630 steps (cmd 5620..6249), test 625 steps (...); only in ref: 5 [...]`.
- Nothing is truncated to the shorter trial, and no metric is computed on a misaligned pair.
- Both trials are also run through `check_trial` (`checks.conformance`).

The Unity harness therefore copies `cmd` (and `n_cmds`) from the reference row it replays.

Default tolerances (`contract.DEFAULT_TOLERANCES`), meant to be tuned per experiment:

| check | default | intent |
|---|---|---|
| `pos_rms_u` | ≤ 4 u (≈ 10 cm) | trajectory stays close over a few seconds |
| `vel_rms_ups` | ≤ 10 u/s | speed curves overlap |
| `spd2d_max_abs_ups` | ≤ 25 u/s | no single large speed excursion |
| `grounded_mismatch_frac` | ≤ 2 % | the same ground/air timeline |
| events | same counts, offset ≤ 2 steps | takeoff, landing and slide timing |

## 9. How a Unity controller is validated against R5 data

1. **Open-loop replay (primary).**
   - A Unity edit-mode test loads a recorded trial.
   - It loads `terrain.map` geometry, or a flat plane when `course_note` says the course is flat.
   - It places the character at `initial_state.pos` with `initial_state.vel`, `initial_state.angles` and `stance`.
   - For each row it applies the inputs (`cmd_fwd`/`cmd_side` or `in_fwd`/`in_right`, `in_yaw`/`in_pitch`, `buttons`; edges from `pressed`/`released`) and advances the controller by exactly `dt`, split into `n_cmds` sub-steps.
   - It writes a Unity trial with the same `cmd` per row.
   - Requirement: the controller exposes `Step(input, dt)`, deterministic and independent of `Time.deltaTime`. If the game later uses a fixed timestep, the harness sub-steps or resamples, and the trial says so in `notes`.
2. **Compare.** `hsd_tel.py compare-contracts <r5 trial> <unity trial> --json out.json`, with the alignment and tolerances of §8.
3. **Closed-loop / statistical (secondary).** For "feel" metrics that do not need step alignment, compare distributions:
   - E1: `vmax`, `a`, `d`;
   - E2: gravity, take-off vz, the air fit;
   - E4: loss against ground time;
   - E5: boost and decel.

   Use `summary.csv`, `hops.csv` and `slides.csv` from a Unity trial converted with the same tools. Accept when the Unity value lies inside the R5 trial spread, or inside a design-chosen band where High Speed Doom deliberately differs.
4. **Divergence is information, not failure.** Where High Speed Doom intentionally departs from Apex, record the chosen target in the mapping table and loosen or replace that tolerance. The trial data stays the reference.

## 10. Known limitations

- R5 recordings mix S21 client prediction with S3 dedi authority.
  - Export from `--contract-side cl` (the player's view) by default, with client parameters.
  - Check dedi parity (`cl_sv_differs`, E1/E8-style comparisons) before trusting fine details.
- Collisions, slopes and steps are not described beyond `terrain`. Replay trials must come from open flat ground, or the Unity harness must load matching geometry. `ground_normal` stays `null` until a producer logs it.
- `t` is printed with 5 decimals and `Time()` may be float32, so `dt` noise is about 10 µs. That is negligible at 144 fps.
- Variable `dt` per row. A fixed-timestep controller needs resampling, and the comparison then runs on the resampled grid.
- Multi-command steps carry one `dt` and only the last command's axes and buttons. On T0 a 0.24 s script stall put 23 usercmds into one frame whose `Time()` advanced 5.6 ms. Such steps are counted in `timing.steps_with_several_cmds`; treat them with care.
