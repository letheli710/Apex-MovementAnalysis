# M9-C (track R ④): Vantage Echo targeting and jet drive

Status: one local session (R5Flowstate **local hybrid build: S21 client + S3 dedicated server + SDK**, offline, 120 fps,
Vantage with kit, geometry m3 for the LOS / wall trials). Nothing is committed. Labels **[meas] [src] [inf] [unknown]**.
Source: `mp_ability_companion_launch.nut` / `sh_vantage_companion.nut` in the local S21 platform scripts. The launch gate
`CanLaunchToCompanion` (60° on-screen + LOS trace, playlist-gated) is the S21 script version (track D: removed in S22,
Aug 2024) and is active in this build. The drive itself is native (`BeginJetDrive`), the double jump is the native jet-drive
window.

## TL;DR

| Question | Answer | Evidence |
|---|---|---|
| Echo placement (tap) | Echo flies along the aim and stops where the aim meets the world or at **1968.5 u horizontal (= 50.0 m)**, hovering ~246 u above the floor (≈ the script's 6 m minimum order height + its bounds). Pitch 10° down: the aim meets the floor at 326 u → Echo there, 246 u up. Pitch 20° up: 1988 u along the ray, 732 u up. 50 m is the script's *buffed* base range (base 40 m, max 55 m); the plain value is not what this build uses [inf: buffs / playlist on] | [meas] 15 + 25 |
| Hold without sending (Echo perched) | Still launches (5/5): Echo is ordered out along the aim (~1185 u, 178 u up) and the player launches 1.66 s after the press | [meas] 5 |
| Hold time | A 0.3 s hold launched 3/5; 0.6 / 1.0 / 2.0 s 5/5. The launch comes **1.81–1.83 s after the hold press** whatever the hold length (a 2.0 s hold launches 0.19 s before the release): a fixed pre-launch, not a charge | [meas] 19 |
| Max distance to Echo | **No distance gate seen:** Echo 2405 u away (player walked back after the send; beyond the 55 m max range) → launch 5/5, same 943 u/s | [meas] 5 + 4 ctrl |
| On-screen gate (R-20a) | View 50° away → launch 4/4; **70° away → no launch 0/5** (script DOT_60DEGREE) | [meas] |
| LOS gate (R-20b) | Rock between the eye and Echo → **no launch 0/5**; same spot without the rock in the line → 5/5 | [meas] |
| Launch speed | 943.5 u/s (= 787 × 1.2, as M8) in every real-tactical launch | [meas] |
| End double jump window (shortcut, 800 u target) | 0.58–0.60 s (310 u before the target): 0/3; 0.67 s (250 u): 0/5; **0.833 s (≈ 121 u): 0/7 but 0.842 s (109–118 u): 3/3** (dj100 and dj100_lurch together) → the window opens at ≈ 0.84 s; 1.083 s (24 u past): 0/4, 1.099 s: 1/1; 1.217 s (59 u past): 4/5; 1.33 s (landed): 1/5. Applied jump: vz 390.9, v_h along the travel 503 → 483 → 469 (later presses lower), as M8. The non-monotonic gaps near 1.08 s are [unknown] | [meas] 33 presses |
| Lurch after the end jump | n = 1 applied jump: \|Δv\| 4.18 on the D press 3 commands later = AirAccelerate (no lurch) [weak, n=1] | [meas] 1 |
| Drive into a wall (shortcut, target behind the rock) | The drive stops at the face: lowest \|v\| 123 at 0.53 s, at x −13718 (face −13706 + hull), z 196 | [meas] 5 |
| Moving Echo, crouch cancel, path speed | Not repeated: M8 shortcut results stand (tracks movers; duck ×0.8; 943 → 787, brake 180 u) | M8 |

## What this means for HSD

- Echo target system: send along the aim to the first hit or 50 m (this build), hover ~6 m above the ground there; holding
  with Echo perched deploys and launches in one go.
- Launch conditions to implement: Echo within 60° of the view and an unblocked eye→Echo trace; no distance limit found; a
  fixed ~1.82 s from the hold press to the lift-off.
- End jump window: starts ≈ 0.84 s into an 800 u drive (~115 u before the target, inside the 180 u brake zone); keep M8's
  vz 394 / ~500 forward; the late edge is unclear.

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_151514_M9R_vantage` | 22 schedules × 5 (real tactical 14, shortcut 8) | r16033 (1442 vs 1441 frames), r16043 (112.3 fps), r16067 (1742 vs 1741 frames), r16071 / r16072 (114.0 / 104.0 fps) |

Server lines are assigned to trials through the `[HSD-RESET]` server time (111 resets, 9979 Echo log lines, 40 drive lines).

## Not measured (and why)

- Zipline / wall-run interactions with the jet drive (time; lowest priority in the plan).
- Echo idle drift beyond ~10 s and the recall timing (the logger runs 14 s; recall only used to reset).
- Exact end-window edges (the presses near 1.08 s give a mixed result; a finer sweep is needed).

## Track D spec check

| Spec | Result |
|---|---|
| R-20 Echo LOS rule (60° on screen + LOS) | **agree** (50° launches, 70° does not; a wall in the line blocks) |

## Rerun

```
cd research/phase2-local/m9/r_vantage
py -3 vantage_analysis.py ../../data/20261022_151514_M9R_vantage --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --label M9R_vantage --trials 5 --run-base 16001 --batch-base 16001 -- --fps 120 --legend vantage
--kit --no-census --state-log --geometry m3 --schedule <22 m9v_* schedules, in runner.json>`. The recall + Echo logger
(`_M9V_PRE`) and the shortcut mover (`_r2_jd_pre`) are `SCHEDULE_PRE` entries in `tools/hsd_trial.py`.
