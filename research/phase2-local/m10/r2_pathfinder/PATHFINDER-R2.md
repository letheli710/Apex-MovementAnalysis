# M10 track R2: Zipline Gun / Octane gaps (climb fire, grapple onto the own rope, O-5 pad tap strafe)

Status: R2 sessions 1 and 2 (`data/20261023_000555_M10R2_s1` sub-runs `M10R2_path`, `M10R2_path2`, `M10R2_path3`;
`data/20261023_002614_M10R2_s2` sub-runs `M10R2_s2path`, `M10R2_s2path2`) on the R5Flowstate **local hybrid build**, offline,
120 fps, Pathfinder with kit. Nothing is committed. Labels **[meas] [src] [inf]**.

## TL;DR

| Item | Answer | Evidence |
|---|---|---|
| Gun fired from a wall climb | **Not measured — 0 / 12 fired.** Ground control toward the same direction works (2516 u rope, 2/2). With the gun raised the climb on the stacked s950 wall lasts only ~0.2 s (client wr 0.44 → 0.68 s after the jump; without the gun 0.26 → 2.17 s); every turn needed to aim ≥ 700 u away (90° / 135° / 180°, in 0.1 s or 4 frames) ended the climb before the attack; facing the wall the target is < 700 u (dry). Script needs on-ground / wall-run / wall-hang **and a valid ground entity** at the fire [src]. Stop-loss after 2 designs. | [meas 12] [src] |
| Grapple onto the own gun rope | **8 / 8 hooked and handed to the zipline** (aim from 250 u beside the rope at the rope point, ±1.5° pitch all work; rope 112 u up). Hand-off 1.10–1.19 s after the grapple press at a pull speed of 360–371; the ride then **restarts the normal ramp**: ~100 at 0.1 s, 305 at 0.3, 502 at 0.5, 643 at 1.0, 784 at 1.5, 925 at 2.0, **1000 cap** at 2.5 s (= the mount-from-rest ramp, track R). | [meas 8] |
| O-5 tap strafe off a pad (pre-pad jump) | **No lurch after the launch.** Jump 0–1 usercmds before the pad contact, then W press edges every 2 cmds with D held and the view turning 720°/s: heading change ≤ 4° in 0.5 s, largest one-cmd Δv_h 6–8 u/s — the same as the control without a pre-pad jump (≤ 3°, 5–7 u/s); the pad sets (514.3, 0, 1026.1) in every case. Jumping earlier (pads 300 / 310 u ahead) carries the player over the pad: no launch. | [meas 13 + 3 jnots] |
| O-8 pad wallrun | Not run (needs a long wall-floor corner and the "wallbug"; the M3 rock is 240 u wide). | — |

## Data and exclusions

- Session 1 O-5 trials (`m10r2_o5_*`, r18517–18532) are **excluded**: leftover Newcastle castle walls on lane C deflected the
  launches (v_h 499 → 28 in 0.1 s). Re-run in a fresh game (session 2, `m10r2_o5b_*`).
- Excluded by pacing: r18512 grope (+3 frames), r18565 climb_side, r18621 / r18627 / r18629 / r18635 o5b (fps 113–116; re-run).
- Rope-grapple aim is a harness shortcut (server teleport 400 u along the rope, 250 u to its right, eye snapped to the rope
  point); the grapple itself is the real input. `M10R2_zdiag` (lane C fires dry because a leftover interruption rock blocked
  the ray) is flagged explore.

## For HSD

- Grapple → own gun rope: allowed, hands over to the rope ride, ride speed restarts from ~0 (no carry of grapple speed), cap 1000.
- Gun on a wall: keep the [src] rule (ground / climb / hang) but there is no local evidence that a climb fire works.
- Pad + pre-pad jump: no lurch window survives the launch (consistent with the D3 decision; the wiki's "TS off pad" stays Fun).

## Rerun

```
cd research/phase2-local/m10/r2_pathfinder
py -3 pathfinder_analysis.py ../../data/20261023_000555_M10R2_s1 ../../data/20261023_002614_M10R2_s2 \
  --json results.json --params params.json > analysis_output.txt
```

Trials: `tools/hsd_trial.py --legend pathfinder --kit --no-census --state-log --m10-log --fps 120 --geometry s950 --schedule
m10r2_z_ground_m90*2,m10r2_z_climb_t90,m10r2_z_climb_t135,m10r2_z_climb_t0*2,m10r2_z_climb_ctrl*2,m10r2_z_climb_side,
m10r2_z_climb_back,m10r2_z_grope*4,m10r2_z_gup*2,m10r2_z_gdn*2`; session 2 (fresh game, no geometry): `--schedule
m10r2_o5b_ctrl,m10r2_o5b_jnots,m10r2_o5b_j270,m10r2_o5b_j280,m10r2_o5b_j300,m10r2_o5b_j310`.
