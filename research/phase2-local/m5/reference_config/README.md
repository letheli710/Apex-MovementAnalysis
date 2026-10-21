# M5 part B: reference calibration config — short-range accuracy

Plan acceptance: the **reference calibration config** reproduces R5 base movement with **short-range position RMS ≤ 4 u and
velocity RMS ≤ 10 u/s**. This folder defines "short range", measures it on every base-movement trial, and reports the full
distribution for the default replay motor (before) and the reference config (after).

Code: HSD-Unity branch `m5/skill-slots` — `Runtime/ShortRangeEval.cs` (harness), `Editor/ShortRangeBatch.cs` (batch entry),
`Runtime/MovementConfig.cs` (the two configs), `Runtime/R5MotorV2.cs` (the two model options). Results: [RESULTS.md](RESULTS.md)
(generated), `windows_baseline.csv`, `windows_reference.csv` (one row per window).

## 1. Definition of "short range"

| Item | Choice | Why |
|---|---|---|
| Window | **1.0 s of recorded time**, consecutive and non-overlapping (rows whose start time lies in [k, k+1) s). The last window of a trial may be shorter. **Every row of every trial is in exactly one window; no window is dropped.** | 1 s spans one complete movement event of the trials (a jump ≈ 0.6 s air time, a landing + redirect ≈ 0.3 s, a slide ≈ 1 s, a lurch window 0.5 s) but not a whole multi-event trial, so it tests the model and not the accumulation of earlier errors. |
| Start state | Window 0 starts from `initial_state` (the plain replay). Every later window restarts the motor from the **recorded state after the previous row**: position, velocity, grounded, sliding; a grounded restart also takes the recorded floor height. The clocks the inputs do not fix come from the recorded history: last landing, last jump press on the ground, last takeoff; with the duck-hull option, the recorded `crouched` flag. | "Restarted from the recorded state" (plan). Everything else (duck/sprint history, slide-boost bookkeeping, ability states and timers) continues from the sim's own run, which is driven by the same recorded inputs. |
| Inputs | The recorded usercmd inputs, open loop, exactly as `BatchReplay` (same input decoding; `Replayer.Replay` with a per-row hook). | Same harness as every earlier replay. |
| Metric | Per window: RMS over its rows of the 3D position error and of the 3D velocity error (sim − ref, Source units). | Same error definitions as the replay reports. |
| Pass | pos RMS ≤ 4 u **and** vel RMS ≤ 10 u/s. Family verdict: the p90 of both is within the limits. The pass fraction and the median / p90 / max are reported for every family. | Thresholds from the plan, unchanged. |
| Trials | All of `../../m1/trials` (3), `../../m2/trials` (34), `../../m3/trials` (30) and the M4 trials that are neither grapple nor rejected (34): **101 trials, 633 windows**. M4 trials run with their legend kit from `../../m4/unity/scenarios.json`, as in the M4 replay. | The plan's base-movement set. The grapple trials are excluded by the plan (their pull law is the M4b RF fit, compared in `../unity/grapple_compare.md`). |
| Census | Class variables always come from the trial's own `trial.json` (as in every replay); the config contributes its model options. | Trials differ (legend, session); nothing is set per trial. |

Nothing is tuned per trial or per window. The two model options below have one global value each.

## 2. What changed in the reference model (options of `R5MotorV2Params`, off in the default replay motor)

| Option | Value | Measured basis | Effect |
|---|---|---|---|
| `lurchClampSprintFraction` | 0.7 | M4 octane: lurch clamp = 0.7 × sprintspeed·msc (209.3 at msc 1.15, same as M3) | none on these trials (same number); scales with stim in the game |
| `groundVectorRedirect` | on | M3 e3 / M4 ctrl_air / stim_air landings: after a lurched landing R5 does **not** redirect the velocity instantly (M2 model). The per-command change is a friction vector of **1250 u/s²** (\|f\| = 1246.8–1255.7 over 31 commands of 4 trials, below the cap) plus the band acceleration along the wish direction (517.5 = 450·1.15). Model: the cross-wish component decays at the deceleration (1250 standing, 1500 ducked), the band acceleration adds along the wish up to cap − \|v\|, \|v\| ≤ max(cap, \|v\| − 1250·dt). Aligned with the wish it is the M2 rule exactly (unit test). | e3 lurch family 78.0 → 92.7 %, controls / stim 96.6 / 95.5 → 100 % |
| `airUnduckDrop` (+ `airUnduckMinAfterTakeoff` 0.08 s, `hullCrouchTime` 0.2 s) | 16.5 u | M3 e8 hops / e3 slide350 (8 trials): releasing duck in the air with a crouched hull lowers the origin by **16.50 u** on one command, 0.076–0.083 s after the takeoff; M4 pad_crouch: 12.5 u, immediately. The 16.5 u / 0.08 s pair is used for all. | e8 family 85.2 → 96.3 % (window pos 12.9–14.5 u → 0.4–1.9 u), pad crouch window 5 12.6 u → passes |

Development order (same harness): baseline 580 → +redirect 596 → +duck hull 604 windows passing (of 633).

**Not exact (residuals reported, not tuned away):** in the first commands after a landing the measured friction vector leans
up to 16° toward −ŵ (it also brakes the along-wish component), and while \|v\| > cap the vector is 1267–1282 u/s², not 1250. The
direction law of that lean was not identified (it depends on the history since the landing). It leaves 4.4–4.7 u / 13 u/s in the
three hardest e3 windows.

## 3. Results (full tables: [RESULTS.md](RESULTS.md))

| family | windows | pass before → after | pos RMS p90 (u) | vel RMS p90 (u/s) | verdict (after) |
|---|---|---|---|---|---|
| M1 ground | 27 | 100 → 100 % | 3.04 → 3.04 | 0.01 → 0.01 | PASS |
| M2 e1 ground | 89 | 100 → 100 % | 0.10 → 0.10 | 0.03 → 0.03 | PASS |
| M2 e2 release / air strafe | 34 | 100 → 100 % | 0.16 → 0.16 | 0.14 → 0.14 | PASS |
| M2 e4 jumps | 52 | 100 → 100 % | 0.24 → 0.24 | 0.22 → 0.22 | PASS |
| M2 e5 slide / slide jump | 40 | 100 → 100 % | 0.29 → 0.29 | 0.32 → 0.32 | PASS |
| M3 e3 lurch | 82 | 78.0 → **92.7 %** | 13.63 → 2.21 | 76.06 → 7.87 | PASS |
| M3 e8 hops / slide chain | 54 | 85.2 → **96.3 %** | 12.90 → 0.36 | 62.85 → 0.54 | PASS |
| M4 controls | 58 | 96.6 → **100 %** | 0.33 → 0.33 | 0.28 → 0.28 | PASS |
| M4 stim | 44 | 95.5 → **100 %** | 0.33 → 0.33 | 0.32 → 0.32 | PASS |
| M4 jump pad | 45 | 93.3 → **97.8 %** | 0.69 → 0.69 | 0.50 → 0.50 | PASS |
| M4 gravity lift | 74 | 78.4 → 78.4 % | 5.58 → 5.58 | 53.27 → 53.27 | **FAIL** |
| M4 jets | 12 | 83.3 → 83.3 % | 0.28 → 0.28 | 14.44 → 14.44 | **FAIL** |
| M4 pounce | 22 | 90.9 → 90.9 % | 0.64 → 0.64 | 8.47 → 8.47 | PASS |
| **all** | **633** | **91.6 → 95.4 %** | 0.62 → 0.53 | 0.60 → 0.53 | PASS |

Medians are ≤ 0.13 u and ≤ 0.11 u/s in every family (RESULTS.md).

### Failing windows of the reference config (29 of 633) and their causes

| Windows | Family | Error | Cause |
|---|---|---|---|
| e3 k42 r1029, k50 r623/r624, window 2 | e3 lurch | 4.4–4.7 u, 13.0–13.6 u/s | Post-landing redirect residual (§2: friction direction lean not modelled). |
| e3 slide350 r650/r651, window 3 | e3 lurch | 1.3–1.9 u, 10.25 u/s | Just over the velocity limit; the landing after the slide jump (duck-hull drop, then the redirect) is within one command — not separated further. |
| e3 walk r648, window 2 | e3 lurch | 0.49 u, 24.3 u/s | Landing one command late: a single-command vz spike (281 u/s). |
| e8 slide_chain r1015/r1016, window 5 | e8 | 3.6 u, 19.4 u/s | Slide end 6 commands off (M2 slide-end rule; known since M3, `../../m3/unity/index_notes.md`). |
| lift ride/jumpout/strafe, window 0 (6) | lift | 3.8–5.7 u, 4.9–33.8 u/s | Lift entry: no exact per-command touch threshold fits every trial (LIFT-GRAPPLE §1). |
| lift ride/jumpout, window 4 (4) | lift | 1.7–3.5 u, 53–77 u/s | Eject one command off (a single-command velocity spike of 580–620 u/s). |
| lift strafe, window 2 (2) | lift | 7.0–8.0 u, 33–43 u/s | Strafing inside the lift (steer law approximate, M4). |
| lift strafe, windows 4–5 (4) | lift | up to 425 u, 675 u/s | **Terrain**: the body drifts off the test plateau and lands 414 u lower; the replay has no map (flat floor). Not a motor error. |
| valk jets r1806/r1807, window 2 | jets | 0.28 u, 14.4–14.6 u/s | Jets stop one command off (`JETS_OFF_RELEASE`, vz ×0.4): a single 158 u/s spike. |
| pad crouch r1536, window 6 | pad | 1.0 u, 73.3 u/s | Landing one command off (single spike). |
| pounce c0 r1901/r1902, window 1 | pounce | 7.4 u, 91.5 u/s | The known 2-command pull-out latency (M4). |

So: **11 of 13 families pass at p90 (95.4 % of all windows)**. The **gravity lift** (entry threshold, eject timing, and 4 windows
that are a terrain artefact) and the **jets** (2 single-command stop-timing windows out of 12) fail the family p90. Single-command
event offsets dominate the remaining failures: one command at 120 fps moves a 600 u/s event by 5 u, and the RMS over a 1 s window
is sensitive to a single large velocity spike (158 u/s in one of 120 rows = 14.4 u/s RMS).

## 4. Re-run

```
python run_eval.py                 # Unity batch (both configs) + summarize.py → windows_*.csv, RESULTS.md
python run_eval.py --skip-unity    # only the tables
```

`run_eval.py` finds Unity 6000.6.5f1 in the standard Hub folder (or `$UNITY_EXE`) and the HSD-Unity project next to this repository
(or `$HSD_UNITY`); it hands absolute paths to Unity and keeps the Unity log in the system temp folder.
