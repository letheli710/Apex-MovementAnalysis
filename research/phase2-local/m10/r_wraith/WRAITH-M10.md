# M10 track R ⑤: Wraith feasibility (Into the Void, Dimensional Rift)

Status: 2 sessions on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps, Wraith
with kit (tactical `mp_ability_phase_walk`, ultimate `mp_weapon_phase_tunnel`). Real inputs only (no EVAL shortcut for the
abilities). Nothing is committed. Labels **[meas] [src] [inf]**. Spec = track D §6 W-1..W-3. The local `mp_weapon_phase_tunnel.nut`
is the Flowstate copy (a comment marks "post s15" tuning); script presence is not proof of S21 values.

## TL;DR

| Item | Answer | Evidence | Spec |
|---|---|---|---|
| Triggers locally? | **Yes, both.** Tactical: tap. Portal: tap ultimate to start placing (the start portal appears at once), move, tap ultimate again to drop the end portal; both portals exist (2 trace blockers). Holding the ultimate instead of tapping kept placing until ~8.6 s (no clean result, 3 trials). | [meas] | — |
| Into the Void | msc 0.80 for 1.175 s (deploy), then 1.5961 (= 1.15 × 1.388) for 2.80 s, then a fade; sprint v_h 414.98. Same as M4 P3. | [meas 5] | W-1 agree |
| Placement speed | During placement the dedi `speed_boost` severity is 0.2 and the sprint runs at **364** (vs 299). The script's distance steps (+0.1 per 20 % of 6000 u) were not visible in the severity read (it stayed 0.2 up to 1500 u of placement). | [meas 15] [src] | W-2 not resolved (field ≤ 2300 u long) |
| Travel | Entering the end portal replays the recorded path back to the start: 0.6 s for ~400 u, 1.1 s for ~760 u, 1.7–1.8 s for ~1480 u; the replay speed equals the recorded placement speed (364; the slid part 516–525). | [meas 15] | W-2/W-3 partly |
| Exit speed | The replay **decelerates to ~0 at the exit** (…338 → 296 → 254 → 177 → 0); the first free state has v ≈ 0 (dedi) / ≤ 24 (client), for entry speeds 173–535 (walk, sprint, run-in). | [meas 15] | W-3 contradicted ("exit = placement speed") |
| Who / cooldown | Only Wraith tested; ult clip 90 refills at 1/s after a 1 s delay [src] (no refill during the trials; the kit refills at every reset). Lifetime 45 s [src, not measured]. | [src] | not tested |

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_211317_M10R_wraith` | portal: sprint 2 s / 5 s, walk 3 s, slide at the end, sprint run-in, hold | all 6 tactical trials (`m10_w_void`, `m10_w_ctrl`: fps 104–114 at the session start) |
| `20261022_213615_M10R_wraith2` | 2 portal warm-ups, tactical 5 + control 5 | r17011 `ctrl` (+3 frames) |

Logger: dedi `[M10-WR]` 10 Hz (speed_boost / placing severities, phase flag, ult clip, portal blockers). The start position is x
−14700 (from −14900 an exploration exit dropped the player off the field edge).

## For HSD (recommendation; user approved the portal for M10 as an extension)

- Portal = path recorder + replay: replay at the recorded speeds, end at ~0 speed at the exit (not a velocity-preserving
  teleport); placement grants a speed boost (364 sprint). A Unity version can reuse the existing path-drive code; exit velocity 0.
- Into the Void: existing `StimAbility` preset is correct.

## Open questions

1. The distance-based placement speed steps (need a ≥ 6000 u run).
2. Portal use by other players, re-entry rules (debounce 0.5 s [src]), lifetime.

## Rerun

```
cd research/phase2-local/m10/r_wraith
py -3 wraith_analysis.py ../../data/20261022_211317_M10R_wraith ../../data/20261022_213615_M10R_wraith2 \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --label M10R_wraith --trials 3 --run-base 16801 --batch-base 16801 -- --fps 120 --legend wraith --kit
--no-census --state-log --m10-log --schedule <8 m10_w_* names>`; `--label M10R_wraith2 --trials 5 --run-base 17001 --batch-base 17001 --
... --warmup 2 --schedule m10_w_portal_d2*2,m10_w_void*5,m10_w_ctrl*5`.
