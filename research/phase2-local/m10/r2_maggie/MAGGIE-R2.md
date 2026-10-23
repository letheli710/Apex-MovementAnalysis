# M10 track R2: Mad Maggie Wrecking Ball speed pads

Status: R2 session 1 (`data/20261023_000555_M10R2_s1`, sub-runs `M10R2_mprobe`, `M10R2_maggie`) on the R5Flowstate **local
hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps, legend madmaggie with kit, lane C. **Real ultimate**
(tap offhand4, the ball is thrown along the view); no EVAL shortcut for the pads. Nothing is committed. Labels **[meas] [src]
[inf]**. Local script `mp_ability_wrecking_ball.nut` (Flowstate copy; contains non-S21 extras such as "mitosis"/big balls,
unused here).

## TL;DR

| Item | Answer | Evidence |
|---|---|---|
| Triggers locally? | **Yes.** Tap ult: the ball rolls along +X; the first piece lands **1.79 s** after the press (sd 0.07, n 14), ~490–690 u ahead, then about one piece per second, **380–720 u apart** (the pads are discrete 88 u discs, not a continuous strip). | [meas] |
| Multiplier | Severity **0.149** (byte of 0.15) → msc 1.15 → **1.4927 (×1.298)**: sprint **388.11**, walk **258.99**. | [meas 16] |
| Sprint required? | **No.** Walking in a pad is boosted (258.99 = 199.5·1.298). Matches S21; sprint-only is the 2026-06 change. | [meas 5] [src] |
| Radius | First boosted command at a 2D centre distance of **62–92 u** (mean 72, n 14) — script trigger 88 u + 16 u hull, reached ~0.1 s late (dedi trigger check + network). | [meas] [src 88 / 16 high] |
| Inside | Endless while touching (standing 3.5 s inside: 0.149 the whole time). | [meas 1] |
| Trailing | After leaving: full boost **~1.95 s**, then a linear fade **0.24 s** (sd 0.004) to 1.15 — the script's `AddTimed( 0.15, 2 s, fade 0.25 )` measured from the geometric edge (the server sees the leave ~0.1–0.2 s later). | [meas 11] [src] |
| Stacking / refresh | Two pads in a row (pass2): the boost is refreshed, never more than 0.149 (max-severity rule, see `../r2_speedboost`). No per-pad re-trigger delay in this script (the 6 s rule is S26.1). | [meas 3] [src] |
| Slide in a pad ("slip slide") | The script sets ground friction **−0.5 while sliding in a pad**, **0.75** for the 2 s after leaving, 1.0 otherwise. Slide deceleration inside a pad **50–71 u/s²** vs **199–222 u/s²** for the same slide age without a pad (n 3 + 2 controls); a small speed bump at entry (+1–4 u/s). | [meas] [src] |
| Stim / phase | Script: the pad still applies 0.15 during Stim or phase (only the FX is skipped); boosts take the max, so Stim (0.149) + pad = no gain. | [src] [inf, not tested] |

## Data and exclusions

Sub-run `M10R2_maggie`: pass ×3, pass2 ×3, walk ×3, slide ×3, stand ×2 (r18323 excluded: +5 frames), ctrl_slide ×2.
`M10R2_mprobe` (r18301–18302) = probes, not in the summary (the second started while the first trial's ball was still rolling).
Every reset destroys balls and clears speed triggers (`DEV_ClearWreckingBallSpeedTriggers`) and resets friction to 1.
Note: `m10r2_m_pass2` shares the `m10r2_m_pass` pre-code (prefix match; only the logger length differs, 12 vs 13 s).

## For HSD

- New "zone" primitive: an 88 u disc (16 u tall); inside → boost 0.15 (×1.298 on the W 1.15 state) endless; on leave →
  2.0 s total (1.75 s hold + 0.25 s linear fade); re-entry refreshes; no stacking; no sprint requirement; sliding inside →
  friction −0.5 (slide almost keeps its speed), 0.75 during the trailing boost.
- Placement for a demo: pieces ~600 u apart along the throw line, first ~500 u ahead, 1.8 s after the press, lasting 60 s [src].

## Rerun

```
cd research/phase2-local/m10/r2_maggie
py -3 maggie_analysis.py ../../data/20261023_000555_M10R2_s1 --json results.json --params params.json > analysis_output.txt
```

Trials: `tools/hsd_trial.py --legend madmaggie --kit --no-census --state-log --fps 120 --trials 3 --schedule
m10r2_m_pass,m10r2_m_pass2,m10r2_m_walk,m10r2_m_slide,m10r2_m_stand,m10r2_m_ctrl_slide*2`.
