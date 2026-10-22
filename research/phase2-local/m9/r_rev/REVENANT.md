# M9-B (track R ②): Revenant shadow pounce grid, pounce interactions, climb inputs

Status: 2 local sessions (R5Flowstate **local hybrid build: S21 client + S3 dedicated server + SDK**, offline, 120 fps,
Revenant with kit; the pounce weapon is `mp_ability_revenant_shadow_pounce_free` = Revenant Reborn, S18+, so S21-era).
Nothing is committed. Labels **[meas] [fit] [src] [inf] [unknown]**. The pounce launch itself is script (`PlayerLaunch`,
SDK `player_launch.cpp` writes the velocity), the climb is native.

## TL;DR

| Question | Answer | Evidence |
|---|---|---|
| v = (700 + 450c)·dir(pitch − 35°)? | **Yes, exactly, over the whole grid.** Pitch −30/−15/0/+10/+20/+25/+45/+70 × charge tap/mid/full × start stand/sprint/slide: max speed error 1.6 u/s (sub-command charge timing, as M4), elevation exact to 0.005°. c = clamp((t_release − t_press − 0.9)/1.3, 0, 1); full charge needs a 2.2 s hold | [fit] 130 + 85 launches |
| idealUpLimit −15° rule | Looking up beyond −15°: raise fades and speed is divided (pitch −30: 627.6 / 1031.0 u/s at 56.92° = script value exactly; −15: 1150 at 49.996°) | [fit] 40 |
| Looking down | ≥ 20° with ground within 200 u → launch at 20° up (pitch replaced by 15): pitch 25/45/70 all give 20.000°. Pitch 19.995° (just below 20) is not replaced → 15.005°. **Off a ledge** (rock top, view past the edge, the ground trace misses): launch 10° / 35° **down** (horizontal 689 / 574 = 700·cos), the vertical part absorbed by the ledge floor on the launch command | [meas] 70 + 10 |
| Start speed | **Replaced**: sprinting (260 u/s while the toss weapon is out) or sliding (235) gives the same 700 / 1150 launch as standing | [meas] 40 |
| Pull-out 0.9 s, charge 1.3 s | Tap / 0.5 s hold → launch 0.916–0.922 s after the press; a release after 0.9 s launches 0.017 s (2 commands) later; full charge at 2.3 s hold | [meas] |
| Cancel | **Not found:** zoom (ADS), attack and jump pressed 1.2 s into the charge, release at 1.5 s → normal launch (911 u/s) 5/5 each. The script has an `OnWeaponTossCancel` handler; its input was not identified | [meas] 15; [src] |
| Press in the air | The 0.9 s pull-out outlasts a standing jump (air time 0.77 s): the launch came after landing (5/5). An air launch was not reached | [meas] 5 |
| Landing recovery | No slowdown beyond ground friction: e.g. tap at pitch 0: |v_h| 574.9 before touchdown → 564.4 on the first ground command → 245.5 after 0.25 s (≈ 1270 u/s², the normal friction) | [meas] |
| Lurch after a pounce | **No lurch window:** a D press 0.025 s or 0.30 s after the launch gives \|Δv\| 4.17 = AirAccelerate | [meas] 10 + 5 ctrl |
| Tap strafe at 1150 (R-18) | **Works:** W edges every 2 commands while turning 360°/s → heading −95…−99° within 0.25 s (turn only: −7°); every W edge gives \|Δv\| **182.0** (= 0.7 × 260, the lurch clamp at the toss-weapon speed scale 1.0, not 209.3); speed kept ×0.89 (turn only ×0.94). No 1100 u/s cutoff in this build | [meas] 5 + 5 per charge |
| Pounce into a wall | Tap from 150 u: contact 0.26 s after the launch at 81 u; full charge from 300 u: contact 0.317 s at 176 u. The climb starts 0.84–0.89 s after the launch in every case (the 0.75 s `disable_wall_run` from the release + up to one server tick), W held or not | [meas] 15 |
| Jump at the wall inside the climb lock | No wall bounce: jump 0.13 s after contact (0.39 s after the launch) changes nothing (vz follows gravity). The no-pounce control was mistimed (jump 0.14 s **before** contact) and is not a valid comparison; M3/M6 data show the ordinary bounce | [meas] 5; control invalid |
| Climb: sideways key | D held while climbing (W held): drifts sideways at **≈ 161 u/s** (148 u in 0.9 s) and keeps climbing (vz ≈ 215) | [meas] 5 |
| Climb: back key / jump | S (W released) at 150 u: the climb ends at once, the player drops off the face backward at ≈ 70 u/s. Jump with W held at 150 u: **no Sparrow-like launch** — no impulse (0.1 s later vx +17 toward the face, vz 221 → 136, about one gravity step of 75 plus the climb ending); the climb re-attaches 0.9 s later | [meas] 5 + 5 |
| Long climb end rule on a smooth face | **Not measured (stop-loss, 3 designs).** (1) Model probe: the tallest firing-range pillar (2430 u) has steps every 300–400 u on its faces; desert models stalled the precache. (2) Read-only map scan: no smooth face ≥ 800 u in the playable field. (3) The one ≥ 2360 u face (map edge, z 2462) is not standable (5/5 settle timeouts). M8 data stand: climb to ≥ floor+1231, final jump-up at 7.2–7.4 s / floor+1247 | documented |

## What this means for HSD

- The M4 pounce model is complete for Unity: add the off-ledge case (no ground-check hit → launch downward, vertical part
  stopped by the floor), "launch replaces velocity" and the pull-out timing. The lurch clamp during/after a pounce flight
  scales with the speed scale (182 at 1.0); there is no lurch window from the launch itself, but key edges in flight do lurch.
- Climb: sideways drift ~161 u/s while climbing; S detaches; jump does nothing for Revenant (not Sparrow).
- The 0.75 s climb lock also blocks a wall bounce.
- The long-climb end rule stays a design value (M8: ~1250 u gain or ~7.4 s).

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_141811_M9R_revR1` | pitch × charge × start grid, 26 schedules × 5 (lane C) | none (the warm-up hitched, not scored) |
| `20261022_143232_M9R_revR2` | release / cancel / air / lurch / tap strafe / wall / ledge / climb inputs, 23 schedules × 5, geometry h480 | r14311–14315 `m9r_bigwall_climb` (settle timeout: not a standable spot) |

All other trials 118.6–120.0 fps.

## Track D spec check

| Spec | Result |
|---|---|
| R-18 pounce tap strafe at ~1150 | **agree** (works; clamp 182 at speed scale 1.0) |
| R-19 pitch grid | **agree** (ideal −15…0 keeps full speed; ≥ 20° down → 20° up launch with ground below; > 15° up loses speed by the script divisor) |

## Open questions

1. The pounce cancel input (script handler exists).
2. A true air pounce (needs a higher start, e.g. a drop from the rock).
3. The long-climb end rule (needs a smooth face ≥ 1300 u; a custom prop or another map).
4. Wall bounce vs climb lock with a correctly timed control.

## Rerun

```
cd research/phase2-local/m9/r_rev
py -3 rev_analysis.py ../../data/20261022_141811_M9R_revR1 ../../data/20261022_143232_M9R_revR2 \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --label M9R_revR<1|2> --trials 5 --run-base <14001|14201> --batch-base <same> -- --fps 120
--legend revenant --kit --no-census --state-log [--geometry h480] --schedule <list in runner.json>`. Schedules `m9r_*` are in
`tools/hsd_trial.py`.
