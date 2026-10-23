# M10 track R ④: D1 slide re-check (crouch release, slide jump vs slide age)

Status: 1 session (`20261022_212509_M10R_slide`) on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**,
offline, 120 fps, Gibraltar (no kit), lane C. Nothing is committed. Client first-time MOVE-TRACE usercmds; for the slide jumps the
dedi rows agree to 0.01 u/s (checked on 2 trials). Labels **[meas] [src] [inf]**.

## TL;DR

| Question | Answer | Evidence |
|---|---|---|
| Does releasing crouch end the slide? | **Yes, but not instantly while fast.** After the release the slide keeps going with a stronger decel until \|v_h\| ≈ 335 (≤ 350), then ends: release at slide age 0.10 s (434 u/s) → slide ends 19 commands (0.16 s) later at 336; at 0.25 s (397) → 11 commands (0.09 s) later at 335; at 0.50 s (339) and 1.0 s (237) → on the release command. Decel after the release ≈ 620–670 u/s² (slide decel + `slideWantToStopDecel 400`), end threshold consistent with `slideMaxStopSpeed 350` [inf from the class vars]. After the end: sprint 299 with W held, a stop with no keys. | [meas 19] [src] |
| Slide jump exit vs slide age (fresh boost; slide start 457.8 from a 299 sprint) | 0.10 s: pre 434 → **exit 273** (cut); 0.25 s: **397 (kept)**; 0.40 s: 361.5 (kept); 0.60 s: pre 317 → **exit 350.0** (raised, sd 0, n 5); 1.0 s: 236 (kept). Exit vz 264.5 everywhere; heading unchanged. | [meas 24] |
| Re-armed vs not | A second slide 0.6 s after a 0.4 s slide starts **without** the boost (297.3 = sprint speed) and its jump keeps the current speed (0.25 s: 250; 0.60 s: 188), no cut, no raise. | [meas 9] |
| Plain slide (crouch held) | 1.69 s long, ends at 112 u/s. | [meas 5] |

- The M9 "R5 0.25 s → 397" is reproduced (396.8). Unity's 236 at 0.25 s is wrong for a fresh-boost slide; 236 is what R5 gives at
  ~1.0 s.
- Two features are not in the HSD model yet: the **cut at 0.10 s** (434 → 273, a jump in the first ~0.1–0.25 s of a fresh
  slide loses ~160 u/s; consistent with a slide-boost refund window [inf]) and the **raise to 350 at 0.60 s** (only one age
  sampled; `slideMaxJumpSpeed 350` [src] is the number, the rule is not identified).

## Data and exclusions

Session `20261022_212509_M10R_slide`, 5 trials per schedule, 67 scored. Excluded: r16707 `rel_t025` (fps 115.7), r16754 `sj_a100`
(+5 frames), r16761 `sj2_a060` (+5 frames). The first attempt of this session (batch 1) did not start (the dedi exited at launch,
code 274, right after the previous session); it produced no data and was relaunched.

## Open questions

1. The boost refund window edges (between 0.10 and 0.25 s) and the 350 raise (ages 0.45–0.9 s not sampled).
2. Crouch release with W released vs held changes only what happens after the slide ends.

## Rerun

```
cd research/phase2-local/m10/r_slide
py -3 slide_analysis.py ../../data/20261022_212509_M10R_slide --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --label M10R_slide --trials 5 --run-base 16701 --batch-base 16701 -- --fps 120 --legend gibraltar
--no-census --state-log --schedule <the 14 m10_s_* names>`.
