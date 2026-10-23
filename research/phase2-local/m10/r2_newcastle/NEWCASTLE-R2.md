# M10 track R2: Newcastle Castle Wall leap

Status: R2 session 1 (`data/20261023_000555_M10R2_s1`, sub-runs `M10R2_nprobe`, `M10R2_newcastle`, `M10R2_newcastle2`,
`M10R2_newcastle3`) on the R5Flowstate **local hybrid build**, offline, 120 fps, legend newcastle with kit, lane C, **real
ultimate** (tap offhand4, 1.6 s later attack; the view pitch picks the floor target). Nothing is committed. Labels **[meas]
[src] [inf] [sdk]**. The S3 dedi has no native leap: the dedi runs the **SDK twin** (`s21-r5sdk/src/game/server/armored_leap.cpp`,
"follows the S21 client body line for line"); the S21 client predicts its native leap. Phases from the SDK trace
(`bridge_armored_leap_trace 2`).

## TL;DR

| Item | Answer | Evidence |
|---|---|---|
| Triggerable | **Yes**, 33 leaps (n 32 scored). Eye height during the raise ≈ 69 u (targets land 1.13× farther than a 60 u eye predicts). | [meas] |
| Target range | Dash (type 1) up to ≤ 600 u (304 / 576 u seen); jump (type 2) from 604 u; **cap 1575 u = 40 m** (aims at 1611 / 1800 / 2000 u all end at 1575). A target blocked overhead (floating rock) → no leap, ult kept. | [meas] [src 40 m, dash 600] |
| Timing | Attack → leap start **0.52 s** (jump, sd 0.006, n 21) / **0.72 s** (dash, n 4); air **0.19–0.50 s** (grows with distance); hover **0.43 s** (sd 0.015; script const 0.55); slam **0.25–0.31 s**; arrival → control **0.75 s** (script recovery 0.75). | [meas, sdk trace] |
| Jump speeds (max \|v\|) | Launch **1798 (604 u) → 1846 (704) → 2089 (1040) → 2200 (1209) → 2447 (1575)**; hover min 91–126, hover max ~1170–1350 (dive start); slam **2228 → 2471** (|vz| up to 2327). Land v = 0. | [meas] [src 1800–2500 / 2000–2500] |
| Dash | 304 u: 1155 u/s, 0.29 s; 576 u: 1472 u/s, 0.45 s; v = 0 at arrival on the dedi. | [meas 4] [src 800–1500] |
| Client vs dedi | Same velocity on every usercmd except at phase edges; at the dash arrival the S21 client twice predicted a decaying slide (1007 → 965 …) while the dedi stopped at 0 (client corrected). | [meas] [hyb] |
| Interruption | Harness obstacle spawned in the path (shortcut). **Wall ahead:** the collision first clips v_h to ~12, vz 150, then phase "interrupted"; nothing kept. **Ceiling:** v_h **1794 → 491 (27 %)**, vz set to −280, then gravity; kept on landing. The script's "35 % if > 300 u/s" is not seen as 35 % (27 % of v_h, 31 % of \|v\|) [n 3 each]. | [meas] [sdk] |
| Castle Wall | Walls deployed at the landing (9 wall entities). | [meas] |

## For HSD

- Target-point path move: aim = view trace ≤ 40 m; ≤ 600 u dash on the ground at ~1150–1470 u/s; farther: 0.52 s prep, air
  launch 1800–2450 u/s (distance-scaled), 0.43 s hover near ~100 u/s, slam ~2230–2470 u/s, stop dead, 0.75 s locked; inputs
  ignored during the leap (`armored_leap_disable_player_move_input 1`).
- Interruption: keep ~27 % of the horizontal speed (ceiling case); a frontal wall leaves nothing.
- Evidence is the SDK twin + S21 client prediction (agree); no S21 server data. Community value low (only others' "Castle
  boost"), so a Fun/extended item.

## Data and exclusions

No exclusions. `n_d*` = probes with a 60 u eye (n 1 each, kept), `n_fly1300` = blocked target (no leap). `n_int` / `n_ceil`
obstacle: helper spawns the M10 rock 206 u ahead / above once v_x > 1500 (removed at the next reset). A first ceiling attempt
reused the wall pre-code because of a schedule-prefix clash (`m10r2_n_int2` → `m10r2_n_int`); those runs (r18441–18443,
schedule `m10r2_n_int2`) stay in the session but are not reported; the ceiling case was renamed `m10r2_n_ceil` and re-run.

## Rerun

```
cd research/phase2-local/m10/r2_newcastle
py -3 newcastle_analysis.py ../../data/20261023_000555_M10R2_s1 --json results.json --params params.json > analysis_output.txt
```

Trials: `tools/hsd_trial.py --legend newcastle --kit --no-census --state-log --fps 120 --server-cvar bridge_armored_leap_trace=2
--trials 3 --schedule m10r2_n_e300,m10r2_n_e600,m10r2_n_e700,m10r2_n_d900,m10r2_n_e1200,m10r2_n_e1800,m10r2_n_int`, then
`--schedule m10r2_n_ceil`.
